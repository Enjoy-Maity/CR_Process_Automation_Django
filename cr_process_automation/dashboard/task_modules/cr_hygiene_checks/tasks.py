import os
import traceback
import pandas as pd
import numpy as np
import dateutil.parser as dp
import dashboard.task_modules.dependencies.playwright_common_methods_ as pcm
import dashboard.task_modules.dependencies.extra_dependencies as ed
from dashboard.task_modules.dependencies.excel_modifier import ExcelModifier
from queue import Queue
from threading import Thread
from typing import List, Callable, AnyStr, Dict
from dashboard.exceptions import CustomException
from typing import Any, AnyStr
from numpy.typing import ArrayLike
from collections import defaultdict
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.db.models import QuerySet
from django.http import JsonResponse
from django_pandas.io import read_frame
from dashboard.models import MasterCRDatabase, SelectedDateTable, CRWiseStatus
import dashboard.task_modules.dependencies.batch_methods as bm
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from playwright.sync_api import sync_playwright

glogs = None
relationship_nodes_queue = None
work_detail_queue = None
cr_itsm_details_dictionary = None
cr_to_circle_checker_dictionary = None
work_details_cr_hygiene_dictionary = None
interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary = None


def cr_wise_status_modifier_update_func(
    cr: str,
    status: str = "Success"
):
    with transaction.atomic(using='default'):
        cr_wise_status = CRWiseStatus.objects.using('default').get(cr_no=cr)
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


def validation_file_colorizer(
    df: pd.DataFrame, 
    excel_modifier_obj: ExcelModifier,
    interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary_local: Dict[Dict[AnyStr, AnyStr]],
    logs: list
) -> list:
    unique_crs = df["CR No"].astype(str).str.strip().unique()
    red_color = "FF5050"
    
    col_loc_dict = {
        "Circle": excel_modifier_obj.column_index("Circle"),
        "Node Details": excel_modifier_obj.column_index("Node Details"),
        "Node Count Remarks": excel_modifier_obj.column_index("Node Count Remarks"),
        "Manual DLD Name Status": excel_modifier_obj.column_index("Manual DLD Name Status") if "Manual DLD Name Status" in df.columns else 0,
        "Manual DLD File Name Status": excel_modifier_obj.column_index("Manual DLD File Name Status") if "Manual DLD File Name Status" in df.columns else 0,
        "All Applicable Task Status": excel_modifier_obj.column_index("All Applicable Task Status") if "All Applicable Task Status" in df.columns else 0,
        "Install Plan Attachment Name": excel_modifier_obj.column_index("Install Plan Attachment Name") if "Install Plan Attachment Name" in df.columns else 0,
        "Install Plan Type": excel_modifier_obj.column_index("Install Plan Type") if "Install Plan Type" in df.columns else 0,
        "Install Plan Attached": excel_modifier_obj.column_index("Install Plan Attached") if "Install Plan Attached" in df.columns else 0,
        "Test Plan Attached": excel_modifier_obj.column_index("Test Plan Attached"),
        "Backout Plan Attached": excel_modifier_obj.column_index("Backout Plan Attached"),
        "Risk Remarks": excel_modifier_obj.column_index("Risk Remarks")
        }
    
    interdomain_kpi_required_column_index = excel_modifier_obj.column_index("Inter-Domain KPI Required")
    interdomain_measuring_kpis_column_index = excel_modifier_obj.column_index("Inter-Domain Measuring KPIs")
    
    wrong_value_list = ["invalid", "not mentioned", "no", "tempna", "none", "na", "n/a", "", "file not found"]
    
    columns_to_check_for_in_loop = [
        "Circle",
        "Install Plan Attached",
        "Backout Plan Attached",
        "Node Count Remarks",
        "Node Details",
        "Test Plan Attached",
        "Risk Remarks",
        "All Applicable Task Status",
        "Install Plan Attachment Name"
    ]
    
    i = 0
    while i < unique_crs.size:
        cr = unique_crs[i]
        error_found = False
        cr_row, cr_column = excel_modifier_obj.get_cell_based_on_value("CR No", cr)
        
        j = 0
        while j < len(columns_to_check_for_in_loop):
            column = columns_to_check_for_in_loop[j]
            column_loc = col_loc_dict[column]
            if column in df.columns:
                # Debug: Check if cr_row or column_loc is None
                # if cr_row is None:
                #     print(f"DEBUG: cr_row is None for CR: {cr}")
                # if column_loc is None:
                #     print(f"DEBUG: column_loc is None for column: {column}")
                raw_data = excel_modifier_obj.get_data(cr_row, column)
                # print(f"DEBUG: Raw cell value at ({cr_row}, {column_loc}) for column '{column}': {raw_data}")
                data = str(raw_data)
                if data.strip().lower() in wrong_value_list:
                    error_found = True
                    excel_modifier_obj.colorizer_based_on_cell_value(cr_row, column_loc, red_color)
            j += 1
            
        if ("Manual DLD Name Status" in df.columns and "Manual DLD File Name Status" in df.columns) and ("Install Plan Type" in df.columns):
            if excel_modifier_obj.get_data(cr_row, "Install Plan Type").strip().lower() == "manual":
                if excel_modifier_obj.get_data(cr_row, "Manual DLD Name Status").lower() in wrong_value_list:
                    error_found = True
                    excel_modifier_obj.colorizer_based_on_cell_value(cr_row, col_loc_dict["Manual DLD Name Status"], red_color)
                if excel_modifier_obj.get_data(cr_row, "Manual DLD File Name Status").strip().lower() in wrong_value_list:
                    error_found = True
                    excel_modifier_obj.colorizer_based_on_cell_value(cr_row, col_loc_dict["Manual DLD File Name Status"], red_color)
                    
        if cr in interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary_local:
            if not interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary_local[cr]["Inter-Domain KPI Required"]:
                excel_modifier_obj.colorizer_based_on_cell_value(cr_row, interdomain_kpi_required_column_index, red_color)
                error_found = True
            
            if not interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary_local[cr]["Inter-Domain Measuring KPIs"]:
                excel_modifier_obj.colorizer_based_on_cell_value(cr_row, interdomain_measuring_kpis_column_index, red_color)
                error_found = True
        
        if error_found:
            excel_modifier_obj.colorizer_based_on_cell_value(cr_row, cr_column, red_color)
            cr_wise_status_modifier_update_func(cr, "Unsuccess")
        i += 1
    
    logs.append(
            "Validation File Colorized Successfully"
        )
    
    return logs


def interdomain_measuring_kpis_remarks_lambda_func(x:str) -> str:   
    return "Not Mentioned" if pd.isna(x) or str(x).strip().lower().__contains__('none|na|n/a') else str(x).strip()


def validation_summary_writer_and_planning_sheet_updater(filtered_df: pd.DataFrame, logs: list, date_: datetime) -> list:
    global interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary
    global cr_itsm_details_dictionary
    global work_details_cr_hygiene_dictionary
    global cr_to_circle_checker_dictionary
    global nodes_count_remarks_dictionary
    
    workbook = os.path.join(os.getenv("PLANNING_SHEET_DOWNLOAD_FOLDER").format(date_.strftime('%d-%b-%y')), os.getenv("PLANNING_SHEET_WORKBOOK_NAME"))
    summary_excel_file_path = os.getenv("CR_HYGIENE_CHECKS_FILE").format(date_.strftime('%d-%b-%y'))

    summary_excel_folder = os.path.dirname(summary_excel_file_path)

    if not os.path.exists(summary_excel_folder):
        os.makedirs(summary_excel_folder, exist_ok=True)

    sheet_name = "Non_BPMS CR Validation Summary"
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
        
    excel_modifier_obj = ExcelModifier(workbook, "Planning_Sheet", wrap_text=True)
    
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
        
        dictionary_for_df["Install Plan Attached"].append(
            "Yes" 
            if cr in work_details_cr_hygiene_dictionary and work_details_cr_hygiene_dictionary[cr]["Install_plan_availability"] 
            else "No"
        )
        
        dictionary_for_df["Test Plan Attached"].append(
            "Yes" 
            if cr in work_details_cr_hygiene_dictionary and work_details_cr_hygiene_dictionary[cr]["Test_plan_availability"] 
            else "No"
        )
        
        dictionary_for_df["Backout Plan Attached"].append(
            "Yes" 
            if cr in work_details_cr_hygiene_dictionary and work_details_cr_hygiene_dictionary[cr]["Backout_plan_availability"] 
            else "No"
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
        
        row, _ =excel_modifier_obj.get_cell_based_on_value("CR No", cr)
        excel_modifier_obj.value_adder("Node Details", value=dictionary_for_df["Node Details"][-1], row=row)
        excel_modifier_obj.value_adder("Impact", value=dictionary_for_df["Impact"][-1], row=row)
        excel_modifier_obj.value_adder("Test Cases", value=dictionary_for_df["Test Plan Notes"][-1], row=row)

        # updating the CR wise data
        cr_wise_status_modifier_update_func(cr, "Success")
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
    ed.workbook_styling(workbook)
    
    
    logs = validation_file_colorizer(
        df, 
        neo_excel_modifier_obj, 
        interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary, 
        logs
    )
    neo_excel_modifier_obj.normal_styler()
    
    
    return logs


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


def plan_files_cr_hygiene():
    global work_details_cr_hygiene_dictionary
    global cr_itsm_details_dictionary
        
    if cr_itsm_details_dictionary:
        cr_list = list(cr_itsm_details_dictionary.keys())
        i = 0
        while i < len(cr_list):
            cr = cr_list[i]
            cr_df = cr_itsm_details_dictionary[cr]["work_details"]
            
            cr_df["Files"] = pd.to_numeric(cr_df["Files"], errors="coerce").fillna(0).astype(int)
            cr_df["Notes"] = cr_df["Notes"].fillna("").astype(str) # NA, N/A, NaN, naN, etc.
            type_values = cr_df["Type"].astype(str).str.strip().values.tolist()
            
            work_details_cr_hygiene_dictionary[cr]["Test_plan_availability"] = False
            work_details_cr_hygiene_dictionary[cr]["Test_plan_notes"] = ""
            work_details_cr_hygiene_dictionary[cr]["Service_impact_assessment_notes"] = ""
            work_details_cr_hygiene_dictionary[cr]["Backout_plan_availability"] = False
            work_details_cr_hygiene_dictionary[cr]["Install_plan_availability"] = False
            
            # if "Test Plan" in type_values:
            if any(x.strip().lower().startswith("test") for x in type_values):
                test_plan_df = cr_df.loc[cr_df["Type"].astype(str).str.strip().str.lower().str.startswith("test")]
                test_plan_files_attached_in_latest_entry = test_plan_df.iloc[0, test_plan_df.columns.get_loc("Files")]
                test_plan_notes_in_latest_entry = str(test_plan_df.iloc[0, test_plan_df.columns.get_loc("Notes")])
                
                if test_plan_files_attached_in_latest_entry > 0:
                    work_details_cr_hygiene_dictionary[cr]["Test_plan_availability"] = True
                
                if len(test_plan_notes_in_latest_entry) > 0:
                    work_details_cr_hygiene_dictionary[cr]["Test_plan_notes"] = test_plan_notes_in_latest_entry
            
            # if "Backout Plan" in type_values:
            if any(x.strip().lower().startswith("backout") for x in type_values):
                backout_plan_df = cr_df.loc[cr_df["Type"].astype(str).str.strip().str.lower().str.startswith("backout")]
                backout_plan_files_attached_in_latest_entry = backout_plan_df.iloc[0, backout_plan_df.columns.get_loc("Files")]
                
                if backout_plan_files_attached_in_latest_entry > 0:
                    work_details_cr_hygiene_dictionary[cr]["Backout_plan_availability"] = True
                
            # if "Install Plan" in type_values:
            if any(x.strip().lower().startswith("install") for x in type_values):
                install_plan_df = cr_df.loc[cr_df["Type"].astype(str).str.strip().str.lower().str.startswith("install")]
                install_plan_attached_in_latest_entry = install_plan_df.iloc[0, install_plan_df.columns.get_loc("Files")]
                
                if install_plan_attached_in_latest_entry > 0:
                    work_details_cr_hygiene_dictionary[cr]["Install_plan_availability"] = True
            
            # if 'Service Impact Assessment' in type_values:
            if any(x.strip().lower().startswith("service impact") for x in type_values):
                service_impact_assessment_df = cr_df.loc[cr_df["Type"].astype(str).str.strip().str.lower().str.startswith("service impact")]
                service_impact_assessment_notes_in_latest_entry = str(service_impact_assessment_df.iloc[0, service_impact_assessment_df.columns.get_loc("Notes")])
                
                if len(service_impact_assessment_notes_in_latest_entry) > 0:
                    work_details_cr_hygiene_dictionary[cr]["Service_impact_assessment_notes"] = service_impact_assessment_notes_in_latest_entry
            
            i += 1


def interdomain_kpi_activity_name_interdomain_kpi_required_check(df: pd.DataFrame):
    global interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary
    
    if interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary is not None and df is not None:
        crs = df["CR No"].astype(str).str.strip().unique()
        i = 0
        while i < len(crs):
            cr = crs[i]
            # print(f"\n{cr= }")
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
                # print(f"Inter-Domain KPI Required: {required_value=}")
                # print(f"Inter-Domain Activity: {required_interdomain_activity_value=}")
                # print(f"Inter-Domain Measuring KPIs: {required_interdomain_measuring_kpi_value=}\n\n")
                
                if required_value == "yes":
                    if required_interdomain_measuring_kpi_value not in ["no", "none", "na", "n/a",  "", "tempna", "nan"]:
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


def itsm_thread_task(cr_batch: List[AnyStr]):
    global glogs
    global relationship_nodes_queue
    global work_detail_queue
    stop_Event = Event()
    text_contents = None
    with sync_playwright() as thread_playwright_instance:
        browser = thread_playwright_instance.chromium.launch(
            headless=False,
            executable_path=pcm.get_browser(),
        )
        thread_context = browser.new_context(storage_state=os.getenv("ITSM_SESSION_FILE"))
        logs = []
        try:
            thread_page, logs = pcm.new_page_opener(thread_context, logs)

            if text_contents is None:
                text_contents = pcm.get_service_plus_list(thread_page)
            i = 0
            while i < len(cr_batch):
                cr = cr_batch[i]
                logs = pcm.search_for_cr(thread_page, cr, logs)
                
                work_detail_queue.put(
                    pcm.work_detail_table_reader(thread_page, cr)
                )
                
                relationship_nodes_queue.put(
                    pcm.relationship_nodes_handler(thread_page, cr, text_contents)
                )
        
                i += 1
            glogs.put(
                element for element in logs
            )

        except Exception as e:
            glogs.put(
                f"Exception Occurred ({e.__class__.__name__})",
                f"{traceback.format_exc()}\n\n{e}",
            )
            raise

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


# def itsm_job_starter(df: pd.DataFrame, runtime:dict, logs: list, timestamp_fn: Callable, user_email: str, task:dict) -> list:
def itsm_job_starter(df: pd.DataFrame, runtime, logs, timestamp_fn, user_email, task):
    unique_crs_in_df = df["CR No"].astype(str).str.strip().unique()

    if unique_crs_in_df.size == 0:
        return logs

    batch_creation_success, batches, logs = bm.main_method(unique_crs_in_df.tolist(), logs)

    if not batch_creation_success:
        logs.append("Batch creation failed; aborting ITSM job.")
        return logs

    logs.append(f"Created {len(batches)} batches from {unique_crs_in_df.size} CRs")

    session_created = False
    max_attempts = 3
    attempt = 0

    while not session_created and attempt < max_attempts:
        attempt += 1
        logs.append(f"Session creation attempt {attempt}/{max_attempts} ---- {timestamp_fn()}")
        session_created, logs = pcm.session_maker(
            logs, task, False, runtime, timestamp_fn, user_email
        )

    if not session_created:
        logs.append(f"Failed to create ITSM session after {max_attempts} attempts.")
        # Reset flags so the iframe closes
        runtime["password_required"] = False
        runtime["otp_required"] = False
        runtime["status"] = "Failed"
        raise CustomException(
            "ITSM Session Creation Failed",
            f"Could not create session after {max_attempts} attempts."
        )

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(itsm_thread_task, batch) for batch in batches]
        for future in futures:
            future.result()

    pcm.session_breaker()

    # Drain glogs (your original code has a bug: while glogs.is_empty() is wrong)
    while not glogs.empty():
        logs.append(glogs.get())

    return logs


def circle_checker(df: pd.DataFrame):
    global cr_to_circle_checker_dictionary
    # df["Circle"] = df["Circle"].where(df["Circle"].notna(), "TempNA")
    # print(f"{df.columns.to_list() = }")
    # print(f"{df.columns.get_loc("Circle") = }")
    # df["Circle"] = df["Circle"].fillna("TempNA")
    
    cr_to_circle_checker_dictionary = {
        cr: (circle != "TempNA") for cr, circle in df.set_index("CR No")["Circle"].to_dict().items()
    }


def cr_pre_hygiene_dictionary_maker():
    global relationship_nodes_queue, work_detail_queue
    global cr_itsm_details_dictionary, cr_to_relationship_node_count_dictionary
    
    relationship_nodes_list = []
    work_detail_list = []
    
    while relationship_nodes_queue.qsize() > 0:
        relationship_nodes_list.append(relationship_nodes_queue.get())
    
    while work_detail_queue.qsize() > 0:
        work_detail_list.append(work_detail_queue.get())
    
    if len(relationship_nodes_list) == len(work_detail_list):
        i = 0
        while i < len(relationship_nodes_list):
            cr, relationship_nodes = relationship_nodes_list[i]
            if isinstance(relationship_nodes, (list, np.ndarray, tuple)):
                cr_itsm_details_dictionary[cr]["relationship_nodes"] = relationship_nodes
                cr_to_relationship_node_count_dictionary[cr] = len(relationship_nodes)
            else:
                cr_itsm_details_dictionary[cr]["relationship_nodes"] = []
                cr_to_relationship_node_count_dictionary[cr] = 0
            i += 1
        
        i = 0
        while i < len(work_detail_list):
            cr, work_details = work_detail_list[i]
            cr_itsm_details_dictionary[cr]["work_details"] = work_details
            i += 1
            
    
    else:
        raise CustomException(
            " CR Work Details and CR Relationship Details length Mismatch!!",
            "Relationship Nodes and Work Details are not equal in number!!",
        )


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


def selected_date_df_maker(selected_date_data: QuerySet) -> pd.DataFrame:
    """
    This function creates a pandas DataFrame from the selected_date_data.
   
    Parameters:
        selected_date_data (QuerySet): A queryset of objects, object representing a row of data.    
        The keys of the queryset should match the field names in the settings file.
    Returns:
        pd.DataFrame: A pandas DataFrame with the selected_date_data.
    """
    # selected_date_data = pd.DataFrame(selected_date_data)
    # print(selected_date_data.columns)
    df = read_frame(selected_date_data).rename(columns=settings.DB_TO_PL_COLUMNS_MAPPING)

    # Normalize datetime columns to naive IST wall-clock for consistent comparisons
    for col in ["Scheduled Start Date+", "Scheduled End Date+"]:
        if col in df.columns:
            s = pd.to_datetime(df[col], errors="coerce")
            if getattr(s.dt, "tz", None) is not None:
                s = s.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
            df[col] = s

    return df


def datetime_check(row: pd.Series, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp):
    """
    This function checks the given row of a dataframe for validity of a date-time value.
   
    Parameters:
        row (pd.Series): A row from a dataframe.
        start_datetime (pd.Timestamp): The start datetime for the date-time value.
        end_datetime (pd.Timestamp): The end datetime for the date-time value.
        
    Returns:
        bool: True if the row contains a valid date-time value, False otherwise.    
    """
    # print(f"{row['CR No'] = }")
    ts = row["Scheduled Start Date+"]
    if pd.isna(ts):
        return False
    ts = pd.Timestamp(ts)
    return start_datetime < ts < end_datetime


def file_reader_and_checker(
    raw_planning_sheet_df: pd.DataFrame, 
    runtime: dict, 
    logs: list, 
    selected_date:datetime 
) -> Tuple[pd.DataFrame, ArrayLike[AnyStr]|None, list]:
    runtime["status"] = "Performing pre-checks"
    try:
        # raw_planning_sheet_df = raw_planning_sheet_df.loc[
        #     raw_planning_sheet_df["Planning Status"].astype(str).str.strip().str.lower().isin(['planned'])
        # ]
        
        print(f"{raw_planning_sheet_df = }")

        start_datetime = pd.Timestamp(selected_date.replace(hour=21, minute=0, second=0, microsecond=0))
        end_datetime = pd.Timestamp((selected_date + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0))
        print(f"{start_datetime = }")
        print(f"{end_datetime = }")
        df_with_datatime_problem = raw_planning_sheet_df.loc[
            ~raw_planning_sheet_df.apply(lambda row: datetime_check(row, start_datetime, end_datetime), axis=1)
        ]

        print(f"{df_with_datatime_problem =}")
        
        cr_array_with_problem = np.array([], dtype=str)
        
        if df_with_datatime_problem.shape[0] > 0:
            cr_arrays_with_problem = df_with_datatime_problem["CR No"].astype(str).str.strip().unique()
            raw_planning_sheet_df = raw_planning_sheet_df.loc[
            (
                ~raw_planning_sheet_df["CR No"].astype(str).str.strip().isin(cr_arrays_with_problem)
            )]

        # print(f'{bpms_planning_sheet_df = }')
    
    except Exception as e:
        logs.append(
            (   
                f"Exception: {e.__class__.__name__}\n"
                f"{traceback.format_exc()}\n"
                f"{e}"
            )
        )
        raise 
    
    runtime["status"] = "Pre-checks completed"
    
    return raw_planning_sheet_df, cr_array_with_problem, logs


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

    relationship_nodes_queue = Queue()
    work_detail_queue = Queue()
    glogs=Queue()

    cr_itsm_details_dictionary = defaultdict[Any, dict](dict)
    cr_to_relationship_node_count_dictionary = defaultdict[Any, int](int)
    work_details_cr_hygiene_dictionary = defaultdict[Any, dict](dict)
    nodes_count_remarks_dictionary = defaultdict[Any, bool](bool)
    interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary = defaultdict[Any, dict](dict)
    cr_to_circle_checker_dictionary = defaultdict[Any, bool](bool)
    glogs=Queue()


    playwright = None
    browser=None
    context = None
    page = None

    parsed_date = dp.parse(selected_date)

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

            print(f"{model_instances = }")

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
    # print(f"\n\n{cr_wise_status_df = }\n")
    # print(f"{selected_data_df.columns = }\n\n")
    # print(f"{selected_data_df['Planning Status'].unique()}")
    # print(f"{cr_wise_status_df["cr_no"].astype(str).str.strip().tolist() = }")
    # print(f"{selected_data_df.loc[selected_data_df['Planning Status'].astype(str).str.strip().astype(str).str.lower() == 'planned']["CR No"].tolist() = }\n")
    # print(f"{selected_data_df.loc[selected_data_df['Planning Status'].astype(str).str.strip().astype(str).str.lower() == 'planned']["BPMS CR (Yes/No)"].tolist() = }\n")
    # print(f"{selected_data_df.loc[selected_data_df['CR No'].astype(str).str.strip().isin(cr_wise_status_df['cr_no'].astype(str).str.strip().tolist())]["CR No"].tolist() =  }\n\n")
    selected_data_df = selected_data_df.loc[
        (
            (
                selected_data_df["Planning Status"].astype(str).str.strip().astype(str).str.lower() == 'planned'
            )
            & 
            (
                selected_data_df["BPMS CR (Yes/No)"].astype(str).str.strip().astype(str).str.lower() == 'no'
            )
        )
    ]

    selected_data_df = selected_data_df.loc[
        selected_data_df["CR No"].astype(str).str.strip().isin(cr_wise_status_df["cr_no"].astype(str).str.strip().tolist())
    ]

    # print(f"{selected_data_df = }\n\n")

    filtered_df, crs_with_problem, GLOBAL_LOGS = file_reader_and_checker(selected_data_df, runtime, GLOBAL_LOGS, parsed_date)

    print(f"{filtered_df = }")
    

    if len(crs_with_problem) > 0:
        for cr in crs_with_problem:
            cr_wise_status_modifier_update_func(cr, "Failed")
    
    if filtered_df.shape[0] > 0:
        runtime["status"] = "Running"

        filtered_df["Circle"] = filtered_df["Circle"].fillna("TempNA")
        filtered_df["Node Count"] = filtered_df["Node Count"].fillna(0)    
        
        GLOBAL_LOGS=itsm_job_starter(filtered_df, runtime, GLOBAL_LOGS, timestamp_fn, user_email, task)
        cr_pre_hygiene_dictionary_maker()

        inter_domain_checks_thread = Thread(
            target = interdomain_kpi_activity_name_interdomain_kpi_required_check, 
            args=(filtered_df,)
        )

        inter_domain_checks_thread.start()            

        circle_checker_thread = Thread(
            target=circle_checker,
            args=(filtered_df,)
        )

        circle_checker_thread.start()            

        node_count_mismatch_thread = Thread(
            target= node_count_mismatch_checker,
            args=(filtered_df,)
        )

        node_count_mismatch_thread.start()            

        plan_files_cr_hygiene_thread = Thread(
            target=plan_files_cr_hygiene,
        )
        
        plan_files_cr_hygiene_thread.start()
        
        
        # kpi_and_test_plan_thread.join()
        inter_domain_checks_thread.join()
        circle_checker_thread.join()
        node_count_mismatch_thread.join()
        plan_files_cr_hygiene_thread.join()

        GLOBAL_LOGS = validation_summary_writer_and_planning_sheet_updater(filtered_df, GLOBAL_LOGS, parsed_date)

    return {
        "status": "Completed",
        "message": f"{task['name']} completed successfully.",
        "download_ready": True,
        "download_name": str(os.getenv("CR_HYGIENE_CHECKS_FILE")).format(parsed_date.strftime("%d-%b-%y")),
        "counts": {},
    }
