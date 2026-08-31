import os
import regex as re
import traceback
import pandas as pd
import numpy as np
import zipfile
import dateutil.parser as dp
import dashboard.task_modules.dependencies.batch_methods as bm
import dashboard.task_modules.dependencies.playwright_common_methods_ as pcm
from pathlib import Path
from dashboard.task_modules.dependencies.extra_dependencies import workbook_styling, ExcelModifier
from playwright.sync_api import sync_playwright, Page
from typing import AnyStr, List, Tuple, Literal, Callable
from numpy.typing import ArrayLike
from threading import Event
from datetime import datetime, timedelta, date
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from collections import defaultdict
from dashboard.views import _make_serializable
from dashboard.models import MasterCRDatabase, SelectedDateTable, CRWiseStatus
from dashboard.task_modules.cr_hygiene_checks.tasks import (
    validation_file_colorizer,
    file_reader_and_checker
)


glogs = Queue()
session_file = None
work_detail_queue = Queue()
text_contents = None
cr_itsm_details_dictionary = None
manual_crs = []
auto_crs = []
manual_crs_attachment_dict = {}
auto_crs_attachment_dict = {}
interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary = None
work_details_cr_hygiene_dictionary = None
task_table_status_dict = None
manual_crs_file_name_status_dict = None
manual_crs_attachment_extension_dict = None
manual_crs_file_content_status_dict = None
manual_crs_attachment_file_content_count_dict = None
manual_crs_attachment_zip_validity_status = None
relationship_nodes_queue = Queue()
tasks_queue = Queue()
queue_ = Queue()
cr_to_circle_dict = {}


def cr_wise_status_modifier_update_func(
    cr: str,
    status: str = "Success"
):
    with transaction.atomic(using='default'):
        cr_wise_status = CRWiseStatus.objects.using('default').get(cr_no=cr, is_active=True)
        cr_wise_status.CR_Hygiene_Checks = status
        cr_wise_status.save()
        transaction.on_commit(lambda: sync_replica_task(), using='default')


def sync_replica_task():
    # self.update_state(state='RUNNING')
    # sync_id = self.request.id
    try:
        call_command('sync_replica')
        # cache.set(f'replica_sync_{sync_id}_status', 'complete', None)
    except Exception as e:
        # cache.set(f'replica_sync_{sync_id}_status', 'failed', None)
        raise


def bpms_manual_cr_design_handler(cr: str, page: Page, date_: datetime, logs: list):
    global manual_crs, cr_to_circle_dict
    manual_crs.append(cr)
    # folder = os.path.dirname(str(workbook_file_path))
    folder = os.path.dirname(os.getenv("BPMS_CR_HYGIENE_CHECKS_FILE").format(date_.strftime('%d-%b-%y')))
    # print(f"{folder=}")
    
    _, attachment_name = pcm.bpms_crs_attachment_name_getter(cr, page, logs)
    manual_crs_attachment_dict[cr] = attachment_name
    
    _, attachment_name, logs = pcm.bpms_manual_crs_attachment_downloader(cr, folder, cr_to_circle_dict[cr], page, date_, logs)

    return logs
    

def bpms_auto_cr_design_handler(cr: str, page: Page, date_: datetime, logs: list):
    global auto_crs, cr_to_circle_dict, auto_crs_attachment_dict
    global tasks_queue
    auto_crs.append(cr)

    # folder = os.path.dirname(str(workbook_file_path))
    folder = os.path.dirname(os.getenv("BPMS_CR_HYGIENE_CHECKS_FILE").format(date_.strftime('%d-%b-%y')))
    
    _, attachment, logs = pcm.bpms_auto_crs_tasks_lld_automation_handler(cr, page, folder, cr_to_circle_dict[cr], date_, logs)
    auto_crs_attachment_dict[cr] = attachment
    return logs


def design_type_identifier(design_type: str):
    if "manual" in design_type:
        return "manual"
    else:
        return "auto"


def first_download_itsm_thread_task(cr_batch: List[AnyStr], date_: datetime):
    global glogs, queue_
    global work_detail_queue
    
    stop_Event = Event()
    with sync_playwright() as thread_playwright_instance:
        browser = thread_playwright_instance.chromium.launch(
            headless=False,
            executable_path=pcm.get_browser()
        )
        logs = []
        thread_context = browser.new_context(storage_state=os.getenv("ITSM_SESSION_FILE"))
        try:
            thread_page, logs =pcm.new_page_opener(thread_context, logs)
            token_for_locking = True
            # workbook_parent = os.path.dirname(str(workbook_file_path))
            workbook_parent = os.path.dirname(str(os.getenv("BPMS_CR_HYGIENE_CHECKS_FILE")).format(date_.strftime("%d-%b-%y")))
            i = 0
            while i < len(cr_batch):
                cr = cr_batch[i]
                logs = pcm.search_for_cr(cr, thread_page, logs)
                _, work_details_table = pcm.work_detail_table_reader(thread_page, cr, manager, live_feed)
                
                work_details_table["Files"] = pd.to_numeric(work_details_table["Files"], errors="coerce").fillna(0).astype(int)
                work_details_table["Notes"] = work_details_table["Notes"].fillna("").astype(str) # NA, N/A, NaN, naN, etc.
                type_values = work_details_table["Type"].astype(str).str.strip().values.tolist()
                
                work_detail_queue.put((cr, work_details_table))
                
                backout_plan_found = False
                    
                backout_plan_df = work_details_table[
                    (work_details_table['Type'].astype(str).str.strip() == 'Backout Plan')
                    ]

                if not backout_plan_df.empty:
                    backout_plan_found = True if backout_plan_df.iloc[0]['Files'] > 0 else False
                
                backout_plan_availability_list = ["Not Available", "Not Available"]
                if backout_plan_found:
                    # ---Backout plan (may trigger modal) ---
                    backout_plan_availability_list, token_for_locking, logs = (
                        pcm.call_with_modal_ack(
                            thread_page,
                            pcm.backout_plan_downloader,
                            thread_page,
                            workbook_parent,
                            cr,
                            cr_to_circle_dict[cr],
                            token_for_locking,
                            date_,
                            logs,
                            max_retries=2,
                        )
                    )
                    
                test_plan_found = False
                
                test_plan_df = work_details_table[
                    (work_details_table['Type'].astype(str).str.strip() == 'Test Plan')
                    ]
                
                if not test_plan_df.empty:
                    test_plan_found = True if test_plan_df.iloc[0]['Files'] > 0 else False

                test_plan_availability_list = ["Not Available", "Not Available"]
                if test_plan_found:
                    # --- Test plan (may trigger modal) ---
                    test_plan_availability_list, token_for_locking, logs = (
                        pcm.call_with_modal_ack(
                            thread_page,
                            pcm.test_plan_downloader,
                            thread_page,
                            workbook_parent,
                            cr,
                            cr_to_circle_dict[cr],
                            token_for_locking,
                            date_,
                            logs,
                            max_retries=2,
                        )
                    )
                    # print(f"{cr = }, test_plan_downloaded = {test_plan_availability_list}")
                
                if queue_:
                        queue_.put(
                            (
                                cr,
                                backout_plan_availability_list,
                                test_plan_availability_list,
                            )
                        )
                
                
                if any(x.strip().lower().startswith("technical") and x.strip().lower().endswith("design") for x in type_values):
                    temp_df = work_details_table[
                        (
                            work_details_table["Type"].astype(str).str.strip().str.lower().str.startswith('technical')
                        )
                        &
                        (
                            work_details_table["Type"].astype(str).str.strip().str.lower().str.endswith('design')
                        )
                    ]
                    design_type = str(temp_df.iloc[0, temp_df.columns.get_loc("Notes")]).strip()
                    
                    match(design_type_identifier(design_type.lower())):
                        case "manual":
                            logs = bpms_manual_cr_design_handler(cr, thread_page, date_, logs)
                        
                        case "auto":
                            logs = bpms_auto_cr_design_handler(cr, thread_page, date_, logs)
                        
                            
                else:
                    logs = bpms_auto_cr_design_handler(cr, thread_page, date_, logs)
                
                
                i += 1

            if glogs:
                for element in logs:
                    glogs.put(_make_serializable(element))
        
        except Exception as e:
            if glogs:
                glogs.put(
                    f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
                )
                
        finally:
            if thread_page:
                thread_page.close()
                del thread_page
            
            if thread_context:
                thread_context.close()
                del thread_context
            
            if browser:
                browser.close()
                del browser
            
            if thread_playwright_instance:
                thread_playwright_instance.stop()
                del thread_playwright_instance
            
            stop_Event.set()


def second_cr_hygiene_itsm_thread_task(cr_batch: List[AnyStr], logs: list):
    global relationship_nodes_queue, text_contents
    global tasks_queue
    global glogs
    
    stop_Event = Event()
    with sync_playwright() as thread_playwright_instance:
        browser = thread_playwright_instance.chromium.launch(
            headless=False,
            executable_path=extra.common_paths_for_browser_method()
        )
        thread_context = browser.new_context(storage_state=os.getenv("ITSM_SESSION_FILE"))
        logs = []
        try:
            thread_page, logs =pcm.new_page_opener(thread_context, logs)
            if text_contents is None:
                text_contents = pcm.get_service_plus_list(thread_page)
                
            i = 0
            while i < len(cr_batch):
                cr = cr_batch[i]
                logs = pcm.search_for_cr(cr, thread_page, logs)
                
                relationship_nodes_queue.put(
                    pcm.relationship_nodes_handler(thread_page, cr, text_contents, manager, live_feed)
                )
                
                tasks_queue.put(
                    pcm.bpms_tasks_tab_getter(cr, thread_page)
                )
        
                i += 1
        
        except Exception as e:
            logs.append(
                f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
            )
                
        finally:
            if glogs:
                for element in logs:
                    glogs.put(_make_serializable(element))
            
            if thread_page:
                thread_page.close()
                del thread_page
            
            if thread_context:
                thread_context.close()
                del thread_context
            
            if browser:
                browser.close()
                del browser
            
            if thread_playwright_instance:
                thread_playwright_instance.stop()
                del thread_playwright_instance
            
            stop_Event.set()


def first_itsm_job_starter(
    df: pd.DataFrame, 
    logs: list, 
    task:dict, 
    runtime:dict, 
    timestamp_fn: Callable, 
    user_email:str,
    date_: datetime
):
    global glogs 
    unique_crs_in_df = df["CR No"].fillna("TempNA").astype(str).str.strip().unique()
    unique_crs_in_df = unique_crs_in_df[unique_crs_in_df != "TempNA"]
    
    if unique_crs_in_df.size > 0:
        batch_creation_success, batches, logs = bm.main_method(
                unique_crs_in_df.tolist()
            )

        if batch_creation_success:
            logs.append(
                f"Created {len(batches)} batches from {unique_crs_in_df.size} CRs"
            )
        
            session_created = None
        
            while not session_created:
                session_created, logs = pcm.session_maker(
                    logs,
                    task,
                    False,
                    runtime,
                    timestamp_fn,
                    user_email
                )
                
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(
                        first_download_itsm_thread_task, batch, date_
                    )
                    for batch in batches
                ]

                for future in futures:
                    future.result()
            
            pcm.session_breaker()

            if glogs:
                while not glogs.empty():
                    logs.append(glogs.get())
    return logs


def second_itsm_job_starter(
    df: pd.DataFrame,
    logs: list, 
    task:dict, 
    runtime:dict, 
    timestamp_fn: Callable, 
    user_email:str,
    date_: datetime
):    
    global glogs
    unique_crs_in_df = df["CR No"].fillna("TempNA").astype(str).str.strip().unique()
    unique_crs_in_df = unique_crs_in_df[unique_crs_in_df != "TempNA"]
    
    if unique_crs_in_df.size > 0:
        batch_creation_success, batches, logs = bm.main_method(
            unique_crs_in_df.tolist(),
            logs
        )

        if batch_creation_success:
            logs.append(
                f"Created {len(batches)} batches from {unique_crs_in_df.size} CRs"
            )
        
            session_created = None
        
            while not session_created:
                session_created, logs = pcm.session_maker(
                    logs,
                    task,
                    False,
                    runtime,
                    timestamp_fn,
                    user_email
                )
                
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(
                        second_cr_hygiene_itsm_thread_task, batch, logs
                    )
                    for batch in batches
                ]

                for future in futures:
                    future.result()
            
            while not glogs.empty():
                logs.append(
                    glogs.get()
                )
    return logs


def plan_files_cr_hygiene():
    global work_details_cr_hygiene_dictionary
    global cr_itsm_details_dictionary
    global glogs
    
    if glogs:
        glogs.put(_make_serializable("Checking Plan Files CR hygiene..."))
        
    if cr_itsm_details_dictionary:
        cr_list = list(cr_itsm_details_dictionary.keys())
        i = 0
        while i < len(cr_list):
            cr = cr_list[i]
            cr_df = cr_itsm_details_dictionary[cr]["work_details"]
            
            cr_df["Files"] = pd.to_numeric(cr_df["Files"], errors="coerce").fillna(0).astype(int)
            cr_df["Notes"] = cr_df["Notes"].fillna("").astype(str) # NA, N/A, NaN, naN, etc.
            type_values = cr_df["Type"].astype(str).str.strip().values.tolist()
            
            work_details_cr_hygiene_dictionary[cr]["Test_plan_notes"] = ""
            work_details_cr_hygiene_dictionary[cr]["Service_impact_assessment_notes"] = ""
            
            # if "Test Plan" in type_values:
            if any(x.strip().lower().startswith("test") for x in type_values):
                test_plan_df = cr_df.loc[cr_df["Type"].astype(str).str.strip().str.lower().str.startswith("test")]
                test_plan_notes_in_latest_entry = str(test_plan_df.iloc[0, test_plan_df.columns.get_loc("Notes")])
                
                if len(test_plan_notes_in_latest_entry) > 0:
                    work_details_cr_hygiene_dictionary[cr]["Test_plan_notes"] = test_plan_notes_in_latest_entry
            
                
            
            # if 'Service Impact Assessment' in type_values:
            if any(x.strip().lower().startswith("service impact") for x in type_values):
                service_impact_assessment_df = cr_df.loc[cr_df["Type"].astype(str).str.strip().str.lower().str.startswith("service impact")]
                service_impact_assessment_notes_in_latest_entry = str(service_impact_assessment_df.iloc[0, service_impact_assessment_df.columns.get_loc("Notes")])
                
                if len(service_impact_assessment_notes_in_latest_entry) > 0:
                    work_details_cr_hygiene_dictionary[cr]["Service_impact_assessment_notes"] = service_impact_assessment_notes_in_latest_entry
            
            i += 1
            
            
def cr_pre_hygiene_dictionary_maker():
    global glogs, relationship_nodes_queue, work_detail_queue
    global cr_itsm_details_dictionary, cr_to_relationship_node_count_dictionary
    if glogs:
        glogs.put(orange_text("Compiling Data from ITSM..."))
        
    relationship_nodes_list = []
    work_detail_list = []
    tasks_details_list = []
    items = []
    
    while queue_.qsize() > 0:
        items.append(queue_.get())
    
    while relationship_nodes_queue.qsize() > 0:
        relationship_nodes_list.append(relationship_nodes_queue.get())
    
    while work_detail_queue.qsize() > 0:
        work_detail_list.append(work_detail_queue.get())
        
    while tasks_queue.qsize() > 0:
        tasks_details_list.append(tasks_queue.get())
    
    if len(relationship_nodes_list) == len(work_detail_list) == len(tasks_details_list) == len(items):
        i = 0
        while i < len(relationship_nodes_list):
            cr, relationship_nodes = relationship_nodes_list[i]
            if isinstance(relationship_nodes, (list, np.ndarray, tuple)):
                cr_itsm_details_dictionary[cr]["relationship_nodes"] = relationship_nodes
                cr_to_relationship_node_count_dictionary[cr] = len(relationship_nodes)
            else:
                cr_itsm_details_dictionary[cr]["relationship_nodes"] = []
                cr_to_relationship_node_count_dictionary[cr] = 0
            
            neo_cr, work_details = work_detail_list[i]
            neo_neo_cr, tasks_details = tasks_details_list[i]
            cr_itsm_details_dictionary[neo_cr]["work_details"] = work_details
            cr_itsm_details_dictionary[neo_neo_cr]["tasks_details"] = tasks_details
            
            neo_neo_neo_cr = items[i][0]
            cr_itsm_details_dictionary[neo_neo_neo_cr]["backout_plan_details"] = items[i][1][0][0]
            cr_itsm_details_dictionary[neo_neo_neo_cr]["test_plan_details"] = items[i][2][0][0]
            
            i += 1
            
    else:
        raise CustomException(
            " CR Work Details, CR Relationship Details, and Tasks Details length Mismatch!!",
            "Relationship Nodes, Work Details, and Tasks Details are not equal in number!!",
        )


def tasks_tables_checker(df: pd.DataFrame):
    global task_table_status_dict, cr_itsm_details_dictionary
    required_tasks_dict = {
        "LLD Automation": "closed",
        "Design Validation": "closed",
        "Design Check": "closed",
        "Buffer_Task": "assigned"
    }
    
    unique_crs = df["CR No"].fillna("TempNA").astype(str).str.strip().unique()
    unique_crs = unique_crs[unique_crs != "TempNA"]
    required_tasks_entries = list(required_tasks_dict.keys())
    
    i = 0
    while i < unique_crs.size:
        cr = unique_crs[i]
        result = "Invalid"
        if cr in cr_itsm_details_dictionary:
            task_table = cr_itsm_details_dictionary[cr]["tasks_details"]
            
            if isinstance(task_table, pd.DataFrame):
                if not task_table.empty:
                    task_table["Name"] = task_table["Name"].fillna("TempNA").astype(str).str.strip().str.lower()
                    task_table["Status"] = task_table["Status"].fillna("TempNA").astype(str).str.strip().str.lower()
                    
                    names_array = task_table["Name"].unique()
                    names_array = names_array[names_array != "TempNA"]
                    
                    if all(
                        map(
                            lambda entry: any(
                                entry.lower() in name for name in names_array
                            ),
                            required_tasks_entries
                        )
                    ):
                        if all(
                            map(lambda entry: required_tasks_dict[entry] == (task_table[task_table["Name"].str.contains(entry.lower())]).iloc[0, task_table.columns.get_loc("Status")],
                                required_tasks_entries)
                        ):
                            result = "Valid"
        
        task_table_status_dict[cr] = result
        
        i += 1
        
        
def zipfile_checker(path: str):
    # print(f"zipfile_checker {path = }")
    try:
        return zipfile.is_zipfile(str(path))
    
    except zipfile.BadZipFile:
        return False
        
        
def manual_installed_files_checker(
    df: pd.DataFrame, 
    date_: datetime
):
    # dictionaries to be filled here
    global manual_crs_file_name_status_dict
    global manual_crs_file_content_status_dict
    global manual_crs_attachment_zip_validity_status
    global manual_crs_attachment_extension_dict
    global manual_crs_attachment_file_content_count_dict
    
    # dictionaries got filled from main method
    global manual_crs_attachment_dict
    # global workbook_file_path
    global cr_to_circle_dict
    
    unique_crs = df['CR No'].astype(str).str.strip().unique()
    
    # wkbk = pd.ExcelFile(workbook_file_path, engine='openpyxl')
    wkbk = pd.ExcelFile(os.getenv('BPMS_DB'), engine='openpyxl')
    bpms_db_df = wkbk.parse('BPMS_DB')
    wkbk.close()
    del wkbk
    
    # print(bpms_db_df, "\n\n")
    
    # print(f'{manual_crs_attachment_dict = }\n\n')
    
    bpms_activity_name_to_folder_name_dict = dict(
        zip(
            bpms_db_df["ACTIVITY NAME"].astype(str).str.strip(),
            bpms_db_df["FOLDER NAME"].astype(str).str.strip()
        )
    )
    # print(f"{bpms_activity_name_to_folder_name_dict = }", "\n\n")
    
    bpms_activity_name_to_file_contents_dict = dict(
        zip(
            bpms_db_df["ACTIVITY NAME"].astype(str).str.strip(),
            bpms_db_df["FILE NAME"].astype(str).str.strip().str.split(',')
        )
    )
    # print(f"{bpms_activity_name_to_file_contents_dict =}", "\n\n")
    
    bpms_activity_name_list = list(bpms_activity_name_to_folder_name_dict.keys())
    # workbook_folder = os.path.dirname(str(workbook_file_path))
    # install_plan_and_test_plan_folder = Path(workbook_folder).joinpath(str(TODAY_CR_DATE_FOLDER))
    install_plan_and_test_plan_folder = Path(
        os.path.dirname(str(os.getenv("BPMS_CR_HYGIENE_CHECKS_FILE")).format(date_.strftime("%d-%b-%y")))
    ).joinpath(
        "Install_and_Backout_Plan_Files",
        f"{date_.strftime('%d-%b-%Y')}"
    )
    
    i = 0
    while i < unique_crs.size:
        cr = unique_crs[i]
        temp_df = df[df["CR No"].astype(str).str.strip() == cr]
        activity_description = str(temp_df.iloc[0, temp_df.columns.get_loc('Activity Description')]).strip()
        
        # print(f"{activity_description = }\n\n")
        
        if activity_description in bpms_activity_name_list:
            extension_check = (Path(manual_crs_attachment_dict[cr]).suffix == ".zip")
            
            manual_crs_attachment_extension_dict[cr] = extension_check
             
            cr_folder_content = install_plan_and_test_plan_folder.joinpath(
                f"{cr}_{cr_to_circle_dict[cr]}",
                "Manual_Technical_Design",
                manual_crs_attachment_dict[cr]
            )
            
            # print(f"{cr_folder_content = }")
            
            if extension_check:
                file_type_check = zipfile_checker(str(cr_folder_content))
                manual_crs_attachment_zip_validity_status[cr] = file_type_check
                
                if file_type_check:
                    required_file_name = bpms_activity_name_to_folder_name_dict[activity_description]
                    
                    file_name_check = (required_file_name == (str(manual_crs_attachment_dict[cr]).split('.')[0]))
                    manual_crs_file_name_status_dict[cr] = file_name_check
                    
                    with zipfile.ZipFile(str(cr_folder_content), 'r') as zip_ref:
                        zip_file_contents = zip_ref.namelist()
                        zip_file_contents = [str(element).split('.')[0] for element in zip_file_contents]
                        
                        # print(f"{zip_file_contents = }\n\n")
                        
                        file_content_count = (len(zip_file_contents) == len(bpms_activity_name_to_file_contents_dict[activity_description]))
                        manual_crs_attachment_file_content_count_dict[cr] = file_content_count
                        
                        if file_content_count:
                            require_file_content_filenames = bpms_activity_name_to_file_contents_dict[activity_description]
                            file_content_filename_check = True if len(set(require_file_content_filenames) - set(zip_file_contents)) == 0 else False
                            
                            manual_crs_file_content_status_dict[cr] = file_content_filename_check
                        
                        else:
                            manual_crs_file_content_status_dict[cr] = False
                
                else:
                    manual_crs_file_name_status_dict[cr] = False
                    manual_crs_attachment_file_content_count_dict[cr] = False
                    manual_crs_file_content_status_dict[cr] = False
            
            else:              
                file_type_check = zipfile_checker(str(cr_folder_content))
                manual_crs_attachment_zip_validity_status[cr] = file_type_check
                
                if file_type_check:
                    required_file_name = bpms_activity_name_to_folder_name_dict[activity_description]
                    
                    file_name_check = (required_file_name == (str(manual_crs_attachment_dict[cr]).split('.')[0]))
                    manual_crs_file_name_status_dict[cr] = file_name_check
                    
                    with zipfile.ZipFile(str(cr_folder_content), 'r') as zip_ref:
                        zip_file_contents = zip_ref.namelist()
                        
                        file_content_count = (len(zip_file_contents) == len(bpms_activity_name_to_file_contents_dict[activity_description]))
                        manual_crs_attachment_file_content_count_dict[cr] = file_content_count
                        
                        if file_content_count:
                            manual_crs_file_content_status_dict[cr]
                        
                        else:
                            manual_crs_file_content_status_dict[cr] = False
                
                else:
                    manual_crs_file_name_status_dict[cr] = False
                    manual_crs_attachment_file_content_count_dict[cr] = False
                    manual_crs_file_content_status_dict[cr] = False
        
        else:
            manual_crs_attachment_extension_dict[cr] = False
            manual_crs_attachment_zip_validity_status[cr] = False
            manual_crs_file_name_status_dict[cr] = False
            manual_crs_attachment_file_content_count_dict[cr] = False
            manual_crs_file_content_status_dict[cr] = False
        i += 1


def circle_checker(df: pd.DataFrame):
    global cr_to_circle_checker_dictionary
    # df["Circle"] = df["Circle"].where(df["Circle"].notna(), "TempNA")
    # print(f"{df.columns.to_list() = }")
    # print(f"{df.columns.get_loc("Circle") = }")
    # df["Circle"] = df["Circle"].fillna("TempNA")
    
    cr_to_circle_checker_dictionary = {
        cr: (circle != "TempNA") for cr, circle in df.set_index("CR No")["Circle"].to_dict().items()
    }
    
    
def interdomain_kpi_activity_name_interdomain_kpi_required_check(
    df: pd.DataFrame
):
    global interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary
    
    if interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary is not None and df is not None:
        crs = df["CR No"].astype(str).str.strip().unique()
        i = 0
        while i < len(crs):
            cr = crs[i]
            temp_df = df.loc[df["CR No"].astype(str).str.strip() == cr]
            # print(temp_df[["CR No", "Inter-Domain KPI Required", "Inter-Domain Activity", "Inter-Domain Measuring KPIs"]])
            # print(f"{temp_df.columns = }")
            if temp_df.shape[0] > 0:
                required_value = str(temp_df["Inter-Domain KPI Required"].iloc[0]).strip().lower()
                required_interdomain_activity_value = str(temp_df["Inter-Domain Activity"].iloc[0]).strip().lower()
                required_interdomain_measuring_kpi_value = str(temp_df["Inter-Domain Measuring KPIs"].iloc[0]).strip().lower()
                
                # if required_value == "yes":
                # TODO: Add logic to handle the case when CR is in the dictionary
                # if str(temp_df.iloc[0, temp_df.columns.get_loc("Inter-Domain KPI Required")]).strip().lower() == "yes":
                
                if required_value == "yes":
                    if required_interdomain_measuring_kpi_value not in ["no", "none", "na", "n/a", "", "tempna", "nan"]:
                        interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary[cr]["Inter-Domain Measuring KPIs"] = True
                    else:
                        interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary[cr]["Inter-Domain Measuring KPIs"] = False
                else:
                    interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary[cr]["Inter-Domain Measuring KPIs"] = True
                    
                if required_interdomain_activity_value == "yes":
                    if required_value == "yes":
                        interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary[cr]["Inter-Domain KPI Required"] = True
                    
                    else:
                        interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary[cr]["Inter-Domain KPI Required"] = False
                        
                    if required_interdomain_measuring_kpi_value in ["no", "none", "na", "n/a", "", "tempna", "nan"]:
                        interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary[cr]["Inter-Domain Measuring KPIs"] = False
                else:
                    interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary[cr]["Inter-Domain KPI Required"] = True
            i += 1

    
    
def interdomain_measuring_kpis_remarks_lambda_func(x:str) -> str:   
    return "Not Mentioned" if pd.isna(x) or str(x).strip().lower().__contains__('none|na|n/a') else str(x).strip()

            
def risk_remarks_func(row: pd.Series) -> str:
    impact_value = ""
    risk_value = ""
    result = ""
    
    if row.isna()['Impact']:
        impact_value = "NA"
        
    else:
        impact_value = str(row['Impact']).strip()
    
    if row.isna()['Risk']:
        risk_value = "NA"
    
    else:
        risk_value = str(row['Risk']).strip()
    
    # Now making the if else ladder for giving out risk remarks
    if impact_value in ["", "NA"] or risk_value in ["", "NA"]:
        result = "Invalid"
    
    if risk_value.lower() == "1-extensive/widespread" and impact_value.lower().startswith(("nsa", "non-service", "not service", "non service")):
        result = "Invalid"
    
    else:
        result = "Valid"
    
    return result


def manual_dld_name_status_remarks_maker_func(cr: str) -> Literal["Valid", "Invalid", "Corrupt", ""]:
    global manual_crs_attachment_zip_validity_status
    global manual_crs_attachment_extension_dict
    global manual_crs_file_name_status_dict
    
    if cr in manual_crs_attachment_zip_validity_status:
        zip_validity_status = manual_crs_attachment_zip_validity_status[cr]
        
        if zip_validity_status:
            if cr in manual_crs_attachment_extension_dict:
                file_extension_status = manual_crs_attachment_extension_dict[cr]
                
                if file_extension_status:
                    if cr in manual_crs_file_name_status_dict:
                        file_name_status = manual_crs_file_name_status_dict[cr]
                        if file_name_status:
                            return "Valid"
                        
                        else:
                            return "Invalid"
                    else:
                        return "Invalid"
                else:
                    return "Invalid"
            else:
                return "Invalid"
        else:
            return "Corrupt"
    else:
        return ""
    
    
def manual_dld_file_name_status_remarks_maker_func(cr: str) -> Literal["Valid", "Invalid", "Count Mismatch", ""]:
    global manual_crs_file_content_status_dict
    global manual_crs_attachment_file_content_count_dict
    
    if cr in manual_crs_file_content_status_dict:
        file_content_count_status = manual_crs_attachment_file_content_count_dict[cr]
        if file_content_count_status:
            file_content_status = manual_crs_file_content_status_dict[cr]
            
            if file_content_status:
                return "Valid"
            
            else:
                return "Invalid"
        
        else:
            return "Count Mismatch"
    else:
        return ""
    

def test_plan_attached_remarks_maker(cr: str) -> Literal["Valid", "Invalid"]:
    global cr_itsm_details_dictionary
    
    if cr in cr_itsm_details_dictionary:
        test_plan_attached = cr_itsm_details_dictionary[cr]["test_plan_details"]
        if test_plan_attached == "Available":
            return "Valid"
        else:
            return "Invalid"
    else:
        return "Invalid"
    
    
def backout_plan_attached_remarks_maker(cr: str) -> Literal["Valid", "Invalid"]:
    global cr_itsm_details_dictionary
    
    if cr in cr_itsm_details_dictionary:
        backout_plan_attached = cr_itsm_details_dictionary[cr]["backout_plan_details"]
        if backout_plan_attached == "Available":
            return "Valid"
        else:
            return "Invalid"
    else:
        return "Invalid"
    

def install_plan_attachment_name_remarks_maker(cr: str) -> AnyStr|Literal["Invalid"]:
    global manual_crs, auto_crs
    global manual_crs_attachment_dict, auto_crs_attachment_dict
    
    if cr in manual_crs:
        if cr in manual_crs_attachment_dict:
            if str(manual_crs_attachment_dict[cr]).strip().lower() in ['tempna', 'na', '', 'n/a', 'none']:
                return "File not Found"
            else:
                return manual_crs_attachment_dict[cr]
        else:
            return "Invalid"
        
    elif cr in auto_crs:
        if cr in auto_crs_attachment_dict:
            return auto_crs_attachment_dict[cr]
        
        else:
            return "Invalid"
    
    else:
        return "Invalid"
    

def node_count_mismatch_checker(df: pd.DataFrame):
    global nodes_count_remarks_dictionary
    global cr_to_relationship_node_count_dictionary
    
    # df["Node Count"] = df['Node Count'].where(df['Node Count'].notna(), 0)
    # df["Node Count"] = df['Node Count'].fillna(0)
    
    cr_to_node_count_dictionary = dict(
        zip(
            df["CR No"].astype(str).str.strip(),
            df["Node Count"].astype(float).astype(int)
        )
    )
    
    nodes_count_remarks_dictionary = {
        cr: (cr_to_node_count_dictionary[cr] == cr_to_relationship_node_count_dictionary[cr]) 
        if cr in cr_to_relationship_node_count_dictionary 
        else False 
        for cr in cr_to_node_count_dictionary.keys()
    }   


def node_counts_remarks_maker(cr: str):
    global nodes_count_remarks_dictionary
    
    if cr in nodes_count_remarks_dictionary:
        return "Valid" if nodes_count_remarks_dictionary[cr] else "Invalid"
    else:
        return "Cannot Determine"


def validation_summary_writer_and_planning_sheet_updater(filtered_df: pd.DataFrame, logs: list) -> list:
    global manual_crs
    global auto_crs
    global cr_itsm_details_dictionary
    global work_details_cr_hygiene_dictionary
    global cr_to_circle_checker_dictionary
    global task_table_status_dict
    global nodes_count_remarks_dictionary
    global manual_crs_attachment_extension_dict
    global manual_crs_attachment_zip_validity_status
    global manual_crs_file_name_status_dict
    global manual_crs_attachment_file_content_count_dict
    global manual_crs_file_content_status_dict
    
    summary_excel_file_path = str(os.getenv("BPMS_CR_HYGIENE_CHECKS_FILE")).format(date_.strftime("%d-%b-%y"))
    workbook_file_path = os.path.join(os.getenv("PLANNING_SHEET_DOWNLOAD_FOLDER").format(date_.strftime('%d-%b-%y')), os.getenv("PLANNING_SHEET_WORKBOOK_NAME"))
    sheet_name = "BPMS CR Validation Summary"
    df = pd.DataFrame()
    
    dictionary_for_df = defaultdict(list)

    if os.path.exists(summary_excel_file_path):
        excel_file = pd.ExcelWriter(
            summary_excel_file_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace",
        )
        
    else:
        excel_file = pd.ExcelWriter(
            summary_excel_file_path, engine="openpyxl", mode="w"
        )
        
    excel_modifier_obj = ExcelModifier(workbook_file_path, "Planning_Sheet", wrap_text=True)

    activity_description_column = filtered_df.columns.get_loc("Activity Description")
    circle_column = filtered_df.columns.get_loc('Circle')
    # impact_column = filtered_df.columns.get_loc('Impact')
    risk_column = filtered_df.columns.get_loc('Risk')
    interdomain_activity_column = filtered_df.columns.get_loc('Inter-Domain Activity')
    interdomain_kpi_required_column = filtered_df.columns.get_loc('Inter-Domain KPI Required')
    interdomain_measuring_kpis_column = filtered_df.columns.get_loc('Inter-Domain Measuring KPIs')
    node_count_column = filtered_df.columns.get_loc("Node Count")
    cr_column = filtered_df.columns.get_loc("CR No")
    
    unique_crs = filtered_df['CR No'].astype(str).unique()
    
    i = 0
    while i < unique_crs.size:
        cr = filtered_df.iloc[i, cr_column]
        temp_df = filtered_df.loc[filtered_df['CR No'].astype(str).str.strip() == cr]
        
        dictionary_for_df["CR No"].append(cr)
        
        dictionary_for_df["Circle"].append(
            str(temp_df.iloc[0, circle_column]).strip()
        )
        
        dictionary_for_df["Risk"].append(
            str(temp_df.iloc[0, risk_column]).strip()
        )
                
        dictionary_for_df["Activity Description"].append(
            str(temp_df.iloc[0, activity_description_column]).strip())
        
        dictionary_for_df["Impact"].append(
            work_details_cr_hygiene_dictionary[cr]["Service_impact_assessment_notes"]
        )
        
        dictionary_for_df["Test Plan Notes"].append(
            work_details_cr_hygiene_dictionary[cr]["Test_plan_notes"]
        )
        
        dictionary_for_df["Node Details"].append(
            ',\n'.join(cr_itsm_details_dictionary[cr]["relationship_nodes"])
            if cr in cr_itsm_details_dictionary 
            else ""
        )

        dictionary_for_df["Node Count"].append(
            temp_df.iloc[0, node_count_column]
        )
        
        dictionary_for_df["Node Count Remarks"].append(
            node_counts_remarks_maker(cr)
        )
        
        dictionary_for_df["Install Plan Type"].append(
            "Manual"
            if cr in manual_crs
            else 
            "Automation" 
            if cr in auto_crs
            else
            "Invalid"
        )
        
        dictionary_for_df["Manual DLD Name Status"].append(
            manual_dld_name_status_remarks_maker_func(cr)
        )
        
        dictionary_for_df["Manual DLD File Name Status"].append(
            manual_dld_file_name_status_remarks_maker_func(cr)
        )
        
        dictionary_for_df["All Applicable Task Status"].append(
            task_table_status_dict[cr] 
            if cr in task_table_status_dict
            else "Invalid"
        )
        
        # dictionary_for_df["Test Plan Attached"].append(
        #     "Yes" 
        #     if cr in work_details_cr_hygiene_dictionary and work_details_cr_hygiene_dictionary[cr]["Test_plan_availability"] 
        #     else "No"
        # )
        
        # dictionary_for_df["Backout Plan Attached"].append(
        #     "Yes" 
        #     if cr in work_details_cr_hygiene_dictionary and work_details_cr_hygiene_dictionary[cr]["Backout_plan_availability"] 
        #     else "No"
        # )
        
        dictionary_for_df["Test Plan Attached"].append(
            test_plan_attached_remarks_maker(cr)
        )
        
        dictionary_for_df["Backout Plan Attached"].append(
            backout_plan_attached_remarks_maker(cr)
        )
        
        dictionary_for_df["Inter-Domain Activity"].append(
            str(temp_df.iloc[0, interdomain_activity_column]).strip()
        )        

        dictionary_for_df["Inter-Domain KPI Required"].append(
            str(temp_df.iloc[0, interdomain_kpi_required_column]).strip()
        )
        
        dictionary_for_df["Inter-Domain Measuring KPIs"].append(
            interdomain_measuring_kpis_remarks_lambda_func(
                str(temp_df.iloc[0, interdomain_measuring_kpis_column]).strip()
            )    
        )
        
        dictionary_for_df["Risk Remarks"].append(
            risk_remarks_func(temp_df.iloc[0])
        )
        
        dictionary_for_df["Install Plan Attachment Name"].append(
            install_plan_attachment_name_remarks_maker(cr)
        )
        
        row, _ =excel_modifier_obj.get_cell_based_on_value("CR No", cr)
        excel_modifier_obj.value_adder("Node Details", value=dictionary_for_df["Node Details"][-1], row=row)
        excel_modifier_obj.value_adder("Impact", value=dictionary_for_df["Impact"][-1], row=row)
        excel_modifier_obj.value_adder("Test Cases", value=dictionary_for_df["Test Plan Notes"][-1], row=row)
        
        i += 1
    
    df = pd.DataFrame(dictionary_for_df)
    df = df.where(pd.notna(df), "NA")
    df = df.replace(to_replace=r"(?i)^nan$", value='NA', regex=True)
    df = df.where(df != "TempNA", "")
    df.to_excel(excel_file, sheet_name=sheet_name, index=False)

    if excel_file:
        excel_file.close()
        del excel_file    

    neo_excel_modifier_obj = ExcelModifier(
        summary_excel_file_path, sheet_name, wrap_text=True
    )
    
    excel_modifier_obj.save()
    workbook_styling(os.path.join(os.getenv("PLANNING_SHEET_DOWNLOAD_FOLDER").format(date_.strftime('%d-%b-%y')), os.getenv("PLANNING_SHEET_WORKBOOK_NAME")))
    
    
    logs = validation_file_colorizer(
        df, 
        neo_excel_modifier_obj,
        interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary,
        logs
    )

    neo_excel_modifier_obj.normal_styler()
    
    logs.append(f"Summary Excel saved at {summary_excel_file_path}")

    return logs


def run_task(
    request, 
    task, 
    runtime, 
    GLOBAL_LOGS=None, 
    timestamp_fn=None, 
    selected_date=None, 
    user_email=None, 
    user_name=None, 
    regions=None
):
    global glogs
    global relationship_nodes_queue
    global work_detail_queue
    
    global cr_to_relationship_node_count_dictionary
    global cr_itsm_details_dictionary
    global work_details_cr_hygiene_dictionary
    global nodes_count_remarks_dictionary
    global interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary
    
    global cr_to_circle_checker_dictionary
    global manual_crs
    global manual_crs_attachment_dict
    global auto_crs_attachment_dict
    global cr_to_circle_dict
    global text_contents
    global tasks_queue
    global queue_
    global work_details_cr_hygiene_dictionary
    global task_table_status_dict
    global manual_crs_file_name_status_dict
    global manual_crs_file_content_status_dict
    global manual_crs_attachment_extension_dict
    global manual_crs_attachment_zip_validity_status
    global manual_crs_attachment_file_content_count_dict

    GLOBAL_LOGS = GLOBAL_LOGS or []
    timestamp_fn = timestamp_fn or _timestamp

    runtime["status"] = "Running"
    runtime["download_ready"] = False
    
    # Password fields (new)
    runtime["password_required"] = False
    runtime["password"] = None
    runtime["pwd_event"] = Event()

    # OTP fields (existing)
    runtime["otp_required"] = False
    runtime["otp"] = None
    runtime["otp_event"] = Event()

    text_contents = None
    manual_crs_attachment_dict = defaultdict(str)
    auto_crs_attachment_dict = defaultdict(str)
    manual_crs = []

    relationship_nodes_queue = Queue()
    work_detail_queue = Queue()
    glogs=Queue()

    tasks_queue = Queue()
    queue_ = Queue()
    cr_itsm_details_dictionary = defaultdict(dict)
    task_table_status_dict = defaultdict(str)
    cr_to_relationship_node_count_dictionary = defaultdict(int)
    cr_to_circle_checker_dictionary = defaultdict(bool)
    manual_crs_file_name_status_dict = defaultdict(bool)
    manual_crs_attachment_zip_validity_status = defaultdict(bool)
    manual_crs_file_content_status_dict = defaultdict(bool)
    manual_crs_attachment_extension_dict = defaultdict(bool)
    manual_crs_attachment_file_content_count_dict = defaultdict(bool)
    interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary = defaultdict(dict)

    playwright = None
    browser=None
    context = None
    page = None

    parsed_date = dp.parse(selected_date)
    date_ = parsed_date

    if regions is not None:
        regions = [str(region).upper() for region in regions]

    else:
        regions = ["NORTH", "SOUTH", "EAST", "WEST"]

    selected_data_df = pd.DataFrame()

    selected_date_data = SelectedDateTable.objects.filter(execution_date=parsed_date + timedelta(days=1), is_active=True).values(*settings.SELECTED_DATE_TABLE_FIELDS)
    
    # print(selected_date_data)
    
    if selected_date_data:
        selected_data_df = selected_date_df_maker(selected_date_data)
    
    else:
        # print("Line No. 793")
        SelectedDateTable.objects.all().delete()
        objects = MasterCRDatabase.objects.filter(execution_date=parsed_date + timedelta(days=1), is_active=True).values(*settings.SELECTED_DATE_TABLE_FIELDS)
        # print(f"{objects = }")
        if len(objects) == 0:
            return JsonResponse({"ok": False, "message": "No CR found for the selected date."}, status=400)

        else:
            valid_fields = {f.name for f in SelectedDateTable._meta.get_fields()}

            model_instances = [
                SelectedDateTable(**{k: v for k, v in data.items() if k in valid_fields})
                for data in objects
            ]

            with transaction.atomic(using='default'):
                SelectedDateTable.objects.using('default').bulk_create(model_instances)
                transaction.on_commit(lambda: sync_replica_task(), using='default')

            selected_date_data = SelectedDateTable.objects.filter(execution_date=parsed_date + timedelta(days=1), is_active=True).values(*settings.SELECTED_DATE_TABLE_FIELDS)
            # print(f"{selected_date_data = }")
        selected_data_df = selected_date_df_maker(selected_date_data)
    
    # print(selected_data_df.columns)
    
    cr_wise_status_df = ed.cr_wise_status_df_maker(parsed_date)
    # cr_wise_status_df = cr_wise_status_df.where(~pd.notna(cr_wise_status_df["CR_Hygiene_Checks"]), "")
    cr_wise_status_df["CR_Hygiene_Checks"].fillna("", inplace=True)
    cr_wise_status_df = cr_wise_status_df.loc[
        cr_wise_status_df["CR_Hygiene_Checks"].astype(str).str.lower().str.strip() != 'success'
    ]

    selected_data_df = selected_data_df.loc[
        (
            (
                selected_data_df["Planning Status"].astype(str).str.strip().astype(str).str.lower() == 'planned'
            )
            & 
            (
                selected_data_df["BPMS CR (Yes/No)"].astype(str).str.strip().astype(str).str.lower() == 'yes'
            )
        )
    ]

    selected_data_df = selected_data_df.loc[
        selected_data_df["CR No"].astype(str).str.strip().isin(cr_wise_status_df["cr_no"].astype(str).str.strip().tolist())
    ]

    bpms_filtered_df, crs_with_problem, GLOBAL_LOGS = file_reader_and_checker(selected_data_df, runtime, GLOBAL_LOGS, parsed_date)
    
    if len(crs_with_problem) > 0:
        for cr in crs_with_problem:
            cr_wise_status_modifier_update_func(cr, "Failed")
    
    if bpms_filtered_df.shape[0] > 0:
        runtime["status"] = "Running"

        bpms_filtered_df["Circle"] = bpms_filtered_df["Circle"].fillna("TempNA")
        bpms_filtered_df["Node Count"] = bpms_filtered_df["Node Count"].fillna(0)

        cr_to_circle_dict = dict(
            zip(
                bpms_filtered_df["CR No"].astype(str),
                bpms_filtered_df["Circle"].astype(str)
            )
        )

        GLOBAL_LOGS.append("Logging to ITSM to perform ITSM Checks for BPMS CRs...")

        GLOBAL_LOGS=first_itsm_job_starter(
            bpms_filtered_df,
            GLOBAL_LOGS,
            task,
            runtime,
            timestamp_fn,
            user_email,
            date_
        )  
            
        GLOBAL_LOGS=second_itsm_job_starter(
            bpms_filtered_df,
            GLOBAL_LOGS,
            task,
            runtime,
            timestamp_fn,
            user_email,
            date_
        )
        cr_pre_hygiene_dictionary_maker()
        
        inter_domain_checks_thread = Thread(
            target=interdomain_kpi_activity_name_interdomain_kpi_required_check,
            args=(bpms_filtered_df,)
        )
        inter_domain_checks_thread.start()
            
        circle_checker_thread = Thread(
            target=circle_checker,
            args=(bpms_filtered_df,)
        )

        circle_checker_thread.start()            

        node_count_mismatch_thread = Thread(
            target= node_count_mismatch_checker,
            args=(bpms_filtered_df,)
        )

        node_count_mismatch_thread.start()
        
        tasks_table_checker_thread = Thread(
            target= tasks_tables_checker,
            args=(bpms_filtered_df, )
        )
        tasks_table_checker_thread.start()
        
        plan_files_cr_hygiene_thread = Thread(
            target=plan_files_cr_hygiene,
        )
        
        plan_files_cr_hygiene_thread.start()
        
        
        inter_domain_checks_thread.join()
        circle_checker_thread.join()
        node_count_mismatch_thread.join()
        tasks_table_checker_thread.join()
        plan_files_cr_hygiene_thread.join()
        
        if manual_crs:
            manual_installed_file_checker_thread = Thread(
                target=manual_installed_files_checker,
                args=(bpms_filtered_df[bpms_filtered_df['CR No'].astype(str).str.strip().isin(manual_crs)], date_)
            )
            manual_installed_file_checker_thread.start()
            manual_installed_file_checker_thread.join()
        
        GLOBAL_LOGS = validation_summary_writer_and_planning_sheet_updater(bpms_filtered_df, GLOBAL_LOGS)
    
    return {
        "status": "Completed",
        "message": f"{task['name']} completed successfully.",
        "download_ready": True,
        "download_name": str(os.getenv("CR_HYGIENE_CHECKS_FILE")).format(parsed_date.strftime("%d-%b-%y")),
        "counts": {},
    }
