import os
import traceback
import numpy as np
import pandas as pd
import dateutil.parser as dp
from collections import defaultdict
from queue import Queue
from threading import Thread, Event
from concurrent.futures import ThreadPoolExecutor
from dashboard.task_modules.dependencies import batch_methods as bm
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta, date
from typing import Dict, AnyStr, Tuple, List
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction
from dashboard.views import _timestamp, _make_serializable
from dashboard.task_modules.dependencies import playwright_common_methods_ as pcm
from dashboard.task_modules.dependencies.extra_dependencies import (
    # sync_replica_task, 
    selected_date_df_maker,
    cr_wise_status_df_maker
    )
from dashboard.task_modules.dependencies.excel_modifier import ExcelModifier
from dashboard.models import CRWiseStatus, SelectedDateTable, MasterCRDatabase, UserManagement



glogs = None
cr_approval_queue = None
mop_attachment_queue = None
cr_to_circle_dict = None
cr_to_risk_dict = None
cr_to_region_dict = None
cr_to_activity_description_dict = None


def mop_attachment_and_cr_approval_sheet_maker(validation_file_path: AnyStr, required_sheet_name: AnyStr, dictionary: Dict[AnyStr, AnyStr]) -> None:
    global cr_to_circle_dict, cr_to_risk_dict, cr_to_region_dict
    global cr_to_activity_description_dict
    
    keys = list(dictionary.keys())
    
    # required_columns
    #     "CR No",
    #     "Risk",
    #     "Region",
    #     "Circle",
    #     "Activity Description"
    
    required_crs = list(dictionary)
    
    summary_df_dict = defaultdict(list)
    
    for cr in required_crs:
        summary_df_dict["CR No"].append(cr)
        summary_df_dict["Circle"].append(cr_to_circle_dict.get(cr, ""))
        summary_df_dict["Risk"].append(cr_to_risk_dict.get(cr, ""))
        summary_df_dict["Region"].append(cr_to_region_dict.get(cr, ""))
        summary_df_dict["Activity Description"].append(cr_to_activity_description_dict.get(cr, ""))
        summary_df_dict["MOP Attachment Status"].append("Not Initiated")
        summary_df_dict["CR Approval Status"].append("Not Initiated")
    
    summary_df = pd.DataFrame(summary_df_dict)
    
    writer = pd.ExcelWriter(validation_file_path, engine="openpyxl", mode="a", if_sheet_exists='replace')
    summary_df.to_excel(writer, index=False, sheet_name=required_sheet_name)
    writer.close()
    del writer



def attachment_queue_writer( 
    dict_: Dict[AnyStr, AnyStr], 
    mop_attachment_task: bool, 
    cr_approval_task: bool,
    logs: list,
    date_: datetime
) -> List[AnyStr]:            
    validation_file_path = os.environ["MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE"].format(date_.strftime("%d-%b-%y"))
    
    os.makedirs(
        os.path.dirname(validation_file_path),
        exist_ok=True
    )

    required_sheetname = "MOP Attachment and CR Approval"
    sheet_names = []
    excel_file = pd.ExcelFile(validation_file_path, engine="openpyxl")
    # validation_summary_df = pd.read_excel(excel_file, sheet_name="Summary")
    sheet_names = excel_file.sheet_names
    excel_file.close()
    del excel_file
    red_color = "FF5050"
    wrong_value_list = ["faliure", "not approved", "tempna", "none", "na", "n/a", ""]
    
    if required_sheetname not in sheet_names:
        mop_attachment_and_cr_approval_sheet_maker(validation_file_path, required_sheetname, dict_)
    
    
    # crs = validation_summary_df["CR No"].astype(str).str.strip().unique()
    crs = list(dict_.keys())
    
    items_dict = {}
    
    if mop_attachment_task:
        while not mop_attachment_queue.empty():
            item = mop_attachment_queue.get()
            items_dict[item[0]] = item[1]
    
    if cr_approval_task:
        while not cr_approval_queue.empty():
            item = cr_approval_queue.get()
            items_dict[item[0]] = item[1]
    
    crs_in_queue = list(items_dict.keys())
    
    # print(f"{crs = }")
    excel_modifier_obj = ExcelModifier(validation_file_path, required_sheetname)
    

    i = 0
    while i < len(crs_in_queue):
        cr = crs_in_queue[i]
        row_index = None
        # print(f"{cr = }")
        dimension = excel_modifier_obj.worksheet.calculate_dimension()
        
        if dimension == 'A1:A1':
            excel_modifier_obj.value_adder("CR No", value=cr, row=row_index)
            row_index = excel_modifier_obj.get_row_based_on_value("CR No", cr)
            excel_modifier_obj.value_adder("Risk", value=cr_to_risk_dict.get(cr, ""), row=row_index)
            excel_modifier_obj.value_adder("Region", value=cr_to_region_dict.get(cr, ""), row=row_index)
            excel_modifier_obj.value_adder("Circle", value=cr_to_circle_dict.get(cr, ""), row=row_index)
            excel_modifier_obj.value_adder("Activity Description", value=cr_to_activity_description_dict.get(cr, ""), row=row_index)
        
        column_name = ""
        if mop_attachment_task:
                # validation_summary_df.loc[validation_summary_df["CR No"].astype(str) == cr, validation_summary_df.columns.get_loc("MOP Attachment Status")] = items_dict[cr]
                column_name = "MOP Attachment Status"
        
        if cr_approval_task:
            # validation_summary_df.loc[validation_summary_df["CR No"].astype(str) == cr, validation_summary_df.columns.get_loc("CR Approval Status")] = items_dict[cr]
            column_name = "CR Approval Status"
        
            
        if cr not in crs:
            # validation_summary_df.iloc[len(crs)+i, validation_summary_df.columns.get_loc("CR No")].value = cr
            excel_modifier_obj.value_adder("CR No", value=cr)
            
            # print(f"CR {cr} not found in validation summary\n",excel_modifier_obj.to_markdown())
            # if mop_attachment_task:
            #     # print(f"MOP Attachment Status for CR {cr}\n",validation_summary_df.iloc[len(crs) + i, validation_summary_df.columns.get_loc("MOP Attachment Status")])
            #     # validation_summary_df.iloc[len(crs) + i, validation_summary_df.columns.get_loc("MOP Attachment Status")].value = items_dict[cr]
            #     column_name = "MOP Attachment Status"
            # if cr_approval_task:
            #     # print(f"CR Approval Status for CR {cr}\n",validation_summary_df.iloc[len(crs) + i, validation_summary_df.columns.get_loc("CR Approval Status")])
            #     # validation_summary_df.iloc[len(crs) + i, validation_summary_df.columns.get_loc("CR Approval Status")].value = items_dict[cr]
            #     column_name = "CR Approval Status"
        if row_index is not None:
            row_index = excel_modifier_obj.get_row_based_on_value("CR No", cr)
        
        if cr not in crs:
            excel_modifier_obj.value_adder("Risk", value=cr_to_risk_dict.get(cr, ""), row=row_index)
            excel_modifier_obj.value_adder("Region", value=cr_to_region_dict.get(cr, ""), row=row_index)
            excel_modifier_obj.value_adder("Circle", value=cr_to_circle_dict.get(cr, ""), row=row_index)
            excel_modifier_obj.value_adder("Activity Description", value=cr_to_activity_description_dict.get(cr, ""), row=row_index)
        excel_modifier_obj.value_adder(column_name, value=items_dict[cr], row=row_index)


        with transaction.atomic(using='default'):
            cr_row = CRWiseStatus.objects.using('default').get(cr_no=cr, is_active=True)
            value = str(items_dict[cr]).strip().lower()
            if mop_attachment_task:
                if value in wrong_value_list:
                    cr_row.MOP_Attachment = _make_serializable("Failed")
                else:
                    cr_row.MOP_Attachment = _make_serializable("Success")
            
            elif cr_approval_task:
                if value in wrong_value_list:
                    cr_row.CR_Approval = _make_serializable("Failed")
                else:
                    cr_row.CR_Approval = _make_serializable("Success")
            
            cr_row.save()
            # transaction.on_commit(lambda: sync_replica_task(), using='default')
        
        if str(items_dict[cr]).strip().lower() in wrong_value_list:
            excel_modifier_obj.colorizer_based_on_value_and_header(header=column_name, value=items_dict[cr], color=red_color)
            excel_modifier_obj.colorizer_based_on_value_and_header(header="CR No", value=cr, color=red_color)
        
        i += 1
    
    # print(excel_modifier_obj.to_markdown())
    
    excel_modifier_obj.normal_styler()
    logs.append(
        f"Validation file {os.path.basename(validation_file_path)} updated successfully"
    )
    return logs


def blank_error_protocol_db_updater(list_of_crs: List[AnyStr]):
    with transaction.atomic(using='default'):
        for cr in list_of_crs:
            cr_row = CRWiseStatus.objects.using('default').get(cr_no=cr, is_active=True)
            cr_row.status = _make_serializable("Failed")
            cr_row.save()
        # transaction.on_commit(lambda: sync_replica_task(), using='default')


def planning_cr_mop_attachment_dict_maker(
    mop_attachment_dict: Dict[AnyStr, AnyStr], planning_sheet_df: pd.DataFrame
) -> Dict[AnyStr, AnyStr]:
    result_dict = {}
    Planning_sheet_protocol_column_name = "Protocol"
    unique_crs_in_planning_sheet = planning_sheet_df['CR No'].astype(str).str.strip().unique()
    
    i = 0
    while i < unique_crs_in_planning_sheet.size:
        selected_cr = unique_crs_in_planning_sheet[i]
        temporary_dataframe = planning_sheet_df.loc[planning_sheet_df["CR No"] == selected_cr]
        mop_links_to_be_attached: list = []
        if temporary_dataframe.shape[0] > 1:
            j = 0
            while j < temporary_dataframe.shape[0]:
                protocols = (
                    str(temporary_dataframe.iloc[j][Planning_sheet_protocol_column_name]).strip().split(",")
                )
                protocols = [
                    str(protocol).strip().lower()
                    for protocol in protocols
                    if str(protocol).strip().lower() != "TempNA"
                ]
                protocols = list(set(protocols))
                mop_links_to_be_attached.extend(protocols)
                mop_links_to_be_attached = list(set(mop_links_to_be_attached))
                j += 1

        if temporary_dataframe.shape[0] == 1:
            protocols = str(temporary_dataframe.iloc[0][Planning_sheet_protocol_column_name]).strip().split(",")
            protocols = [str(protocol).strip().lower() for protocol in protocols]
            protocols = list(set(protocols))
            mop_links_to_be_attached.extend(protocols)
            mop_links_to_be_attached = list(set(mop_links_to_be_attached))

        temp_string_to_fill = "MOP Links:\n"

        temp_string_to_fill = temp_string_to_fill + "\n".join(
            [
                str(mop_attachment_dict[mop_link.lower()])
                for mop_link in [
                    str(protocol)
                    for protocol in mop_links_to_be_attached
                    if protocol in mop_attachment_dict.keys()
                ]
            ]
        )
        result_dict[selected_cr] = temp_string_to_fill
        i += 1

    return result_dict


def cr_protocol_to_mop_attachment_dict_maker(logs: List[AnyStr]) -> Tuple[Dict[AnyStr, AnyStr], pd.DataFrame, List[AnyStr]]:
    result = {}

    sheet_name = "MOP_Link"
    Mop_column_name = "MOP Link"
    Protocol_column_name = "Protocol"
    
    inventory_workbook_name = os.getenv("MOP_ATTACHMENT_INVENTORY_SHEET")

    if os.path.exists(inventory_workbook_name) and inventory_workbook_name.endswith(
        (".xlsx", ".xls", ".xlsm")
    ):
        # Code for reading the excel file containing inventory database
        logs.append(
            (    
                _timestamp(),
                f"\nReading the excel file containing inventory database: {os.path.basename(inventory_workbook_name)}\n",
            )
        )

        excel_file = pd.ExcelFile(inventory_workbook_name, engine="openpyxl")
        try:
            inventory_sheet_df = pd.read_excel(excel_file, sheet_name=sheet_name)
            inventory_sheet_df = inventory_sheet_df.where(
                ~pd.isna(inventory_sheet_df), "TempNA"
            )
            inventory_sheet_df = inventory_sheet_df.loc[
                ~inventory_sheet_df[Protocol_column_name].astype(str).str.strip().isin(["", "TempNA"])
                ]
        except Exception as e:
            logs.append(
                (    
                    _timestamp(),
                    f"\nException Occured ({e.__class__.__name__})\n",
                    f"{traceback.format_exc()}\n{e}",
                )
            )
            raise e
        
        excel_file.close()
        del excel_file
        
        if not inventory_sheet_df.empty:
            result = dict(
                zip(
                    inventory_sheet_df[Protocol_column_name].astype(str).str.strip().str.lower(),
                    inventory_sheet_df[Mop_column_name].astype(str).str.strip()
                )
            )

    return result, inventory_sheet_df, logs


def crs_with_blank_or_wrong_protocols_finder(
    inventory_sheet_df: pd.DataFrame, 
    df: pd.DataFrame,
    logs: List[AnyStr]
) -> Tuple[List[AnyStr], bool, List[AnyStr]]:
    result_list = []
    temp_flag = False
    
    Protocol_column_name = "Protocol"
    # Mop_column_name = "MOP_Link"
    Planning_sheet_protocol_column_name = "Protocol"
    
    # Getting the array of all the mentioned protocols in the inventory sheet
    unique_acceptable_protocols_from_mop_links = inventory_sheet_df[
        Protocol_column_name
    ].astype(str).str.strip().str.lower().unique()
    
    cr_to_protocol_mapping: dict = {}
    unique_crs_in_planning_sheet = (
        df["CR No"].dropna().unique().astype(str)
    )

    logs.append("Finding CRs with blank or wrong protocols...")
    i = 0
    while i < unique_crs_in_planning_sheet.size:
        selected_cr = unique_crs_in_planning_sheet[i]
        cr_protocols: list = []
        temp_df = df.loc[df["CR No"] == selected_cr]
        if temp_df.shape[0] > 0:
            j = 0
            while j < temp_df.shape[0]:
                protocols = str(temp_df.iloc[j][Planning_sheet_protocol_column_name]).strip().lower()
                if protocols != "TempNA":
                    cr_protocols.extend(protocols.split(","))
                else:
                    cr_protocols.append(protocols)
                j += 1

            cr_to_protocol_mapping[selected_cr] = cr_protocols
        i += 1

    unique_crs_in_cr_to_protocol_mapping = list(cr_to_protocol_mapping.keys())
    # print(f"{unique_crs_in_cr_to_protocol_mapping = }")

    error_dictionary: dict = {}

    # print(f"{unique_crs_in_cr_to_protocol_mapping = }")
    i = 0
    while i < len(unique_crs_in_cr_to_protocol_mapping):
        selected_cr = unique_crs_in_cr_to_protocol_mapping[i]
        protocols = cr_to_protocol_mapping[selected_cr]
        j = 0
        while j < len(protocols):
            protocol = str(protocols[j]).strip()
            if protocol not in unique_acceptable_protocols_from_mop_links:
                if (protocol == "TempNA") or (protocol == "tempna"):
                    protocol = "Blank Entry"
                if selected_cr not in error_dictionary.keys():
                    error_dictionary[selected_cr] = [protocol]
                else:
                    error_dictionary[selected_cr].append(protocol)

                error_dictionary[selected_cr] = list(
                    set(error_dictionary[selected_cr])
                )

            j += 1
        i += 1
    unique_error_protocols_in_error_dictionary = []
    if len(error_dictionary) > 0:
        unique_error_protocols_in_error_dictionary = list(
            set(
                [
                    str(error_protocol).lower().strip()
                    for error_cr in error_dictionary.keys()
                    for error_protocol in error_dictionary[error_cr]
                ]
            )
        )
        
    if len(unique_error_protocols_in_error_dictionary) > 0:
        if len(unique_error_protocols_in_error_dictionary) == 1:
            if (
                unique_error_protocols_in_error_dictionary[0]
                == "blank entry"
            ):
                planned_crs_with_blank_protocols = []
                # unplanned_crs_with_blank_protocols = []
                error_dictionary_crs = list(error_dictionary.keys())
                planned_crs = (
                    df.loc[
                        df["Planning Status"].astype(str).str.strip().str.lower().isin(['planned'])
                    ]["CR No"]
                    .astype(str)
                    .unique()
                )

                if len(planned_crs) > 0:
                    p = 0
                    while p < len(error_dictionary_crs):
                        if error_dictionary_crs[p] in planned_crs:
                            planned_crs_with_blank_protocols.append(
                                error_dictionary_crs[p]
                            )
                        # else:
                        #     unplanned_crs_with_blank_protocols.append(
                        #         error_dictionary_crs[p]
                        #     )
                        p += 1
                
                if (
                    len(planned_crs_with_blank_protocols) > 0
                ):
                    logs.append(
                        f"CRs with blank entry in protocols: \n{'\n\t'.join(planned_crs_with_blank_protocols)}"
                    )

                    thread = Thread(target=blank_error_protocol_db_updater, args=(planned_crs_with_blank_protocols,),)

                    thread.start()
                    thread.join()
                
                temp_flag = True
                result_list = list(error_dictionary.keys())
                
            else:
                logs.append(
                    (
                        "Errors in Protocols Entries found:\n\n",
                        "\n".join(
                            [
                                f"{cr} : {', '.join(protocols)}"
                                for cr, protocols in error_dictionary.items()
                            ]
                        )
                    )
                )
                thread = Thread(target=blank_error_protocol_db_updater, args=(list(error_dictionary.keys()),),)
                thread.start()
                thread.join()
                temp_flag = False
                
        else:
            logs.append(
                (
                    "Errors in Protocols Entries found:\n\n",
                    "\n".join(
                        [
                            f"{cr} : {', '.join(protocols)}"
                            for cr, protocols in error_dictionary.items()
                        ]
                    )
                )
            )

            thread = Thread(target=blank_error_protocol_db_updater, args=(list(error_dictionary.keys()),),)
            thread.start()
            thread.join()
            temp_flag = False
    
    else:
        logs.append("No errors in Protocols Entries found.")
        # print(temp_flag)
        temp_flag = True
    
    return result_list, temp_flag, logs


def thread_task(
    cr_batch: List[AnyStr],
    cr_approval: bool,
    mop_attachment_string_dict: Optional[Dict[AnyStr, AnyStr], None] = None,
    username: str = "",
):
    global glogs
    stop_event = Event()
    logs = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            executable_path=pcm.get_browser(),
            timeout=15000,
        )
        context = browser.new_context(storage_state=os.getenv("ITSM_SESSION_FILE"))
        page, logs = pcm.new_page_opener(context, logs)

        try:
            pass
            i = 0
            while i < len(cr_batch):
                cr = cr_batch[i]

                message_string = (
                    f"Attaching MOP Link for CR : {cr}..."
                    if not cr_approval
                    else f"Approving CR : {cr}..."
                )

                # Process the current CR here
                if logs:
                    logs.append(_make_serializable(message_string))

                match cr_approval:
                    case True:
                        cr_approval_queue.put(
                            (cr, pcm.cr_approval_func(cr, page, username))
                        )
                    case False:
                        mop_attachment_queue.put(
                            (cr, pcm.mop_attachment_func(cr, mop_attachment_string_dict[cr], page, True))
                        )
                i += 1

        except Exception as e:
            logs.append(
                    (   
                        _timestamp(),
                        f"Exception occurred ({e.__class__.__name__})!!",
                        f"{traceback.format_exc()}\n\n{e}",)
                )

        finally:
            if glogs:
                for elem in logs:
                    glogs.put(_make_serializable(elem))
            
            if page:
                page.close()

            if context:
                context.close()

            if browser:
                browser.close()

            if playwright:
                playwright.stop()
                del playwright

            stop_event.set()


def mop_attachment_func(
    df: pd.DataFrame,
    task:dict,
    runtime: dict,
    timestamp_fn: Callable,
    user_email: str, 
    logs: List[AnyStr],
    date_: datetime,
    username: str = "",
) -> List[AnyStr]:
    global mop_attachment_queue
    try:
        full_df = df.copy(deep=True)
        Planning_sheet_protocol_column_name = "Protocol"
        
        df = df.loc[(df["CR No"] != "TempNA") & (df[Planning_sheet_protocol_column_name] != "TempNA")]

        unique_crs_in_planning_sheet = df["CR No"].unique().astype(str)

        mop_attachment_dict, inventory_sheet_df, logs = cr_protocol_to_mop_attachment_dict_maker(logs)

        crs_with_blank_protocols, token_for_mop_attachment_trigger, logs = crs_with_blank_or_wrong_protocols_finder(inventory_sheet_df, full_df, logs)

        if token_for_mop_attachment_trigger:
            if len(crs_with_blank_protocols) > 0:
                unique_crs_in_planning_sheet = np.setdiff1d(
                    unique_crs_in_planning_sheet, np.array(crs_with_blank_protocols)
                )
                df = df.loc[
                    df["CR No"].astype(str).str.strip().isin(unique_crs_in_planning_sheet)
                ]

            planning_cr_mop_attachment_dict = planning_cr_mop_attachment_dict_maker(
                mop_attachment_dict, df
            )
            
            if unique_crs_in_planning_sheet.size > 0:
                batch_creation_success, batches, logs = bm.main_method(
                    unique_crs_in_planning_sheet.tolist(), logs
                )
                
                if batch_creation_success:
                    session_created = None
                    # print(batches)

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
                                thread_task, batch, False, planning_cr_mop_attachment_dict, username
                            )
                            for batch in batches
                        ]

                    for future in futures:
                        future.result()
                    
                    pcm.session_breaker()
        
                if mop_attachment_queue:
                    logs = attachment_queue_writer(planning_cr_mop_attachment_dict, True, False, logs, date_)
    
    except Exception as e:
        logs.append((
            "Error in mop_attachment_func",
            traceback.format_exc()
        ))
    
    finally:
        if glogs:
            while not glogs.empty():
                logs.append(glogs.get())
    
    return logs


def cr_approval_func(
    df: pd.DataFrame,
    task:dict,
    runtime: dict,
    timestamp_fn: Callable,
    user_email: str, 
    logs: List[AnyStr],
    date_: datetime,
    username:str=""
) -> List[AnyStr]:
    try:
        cr_approval_task_status_dict = {}
        df_for_blank_or_discussed_or_swapped = df.loc[
            (df["CR No"] != "TempNA") & (df["Planning Status"] != "Planned")
        ]

        if df_for_blank_or_discussed_or_swapped.shape[0] > 0:
            i = 0
            while i < df_for_blank_or_discussed_or_swapped.shape[0]:
                cr = df_for_blank_or_discussed_or_swapped.iloc[i]["CR No"]
                cr_approval_task_status_dict[cr] = "CR is not in Planned State"
                i += 1

        df = df.loc[(df["CR No"] != "TempNA") & (df["Planning Status"].astype(str).str.lower().isin(['planned']))]
        planned_df_dict = dict(
            zip(
                df["CR No"].astype(str).str.strip(),
                df["Planning Status"].astype(str).str.strip()
            )
        )

        # df = df.loc[~df["CR No"].astype(str).str.upper().str.contains("FNI")]
        df = df.loc[df["CR No"].astype(str).str.upper().map(len) > 10]
        if df.shape[0] > 0:
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
                
            batch_creation_success, batches, logs = bm.main_method(df['CR No'].astype(str).str.strip().unique().tolist(), logs)
            if batch_creation_success:
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [
                        executor.submit(
                            thread_task, batch, True, None, username
                        )
                        for batch in batches
                    ]

                    for future in futures:
                        future.result()
            pcm.session_breaker()
            
            if cr_approval_queue:
                logs = attachment_queue_writer(planned_df_dict, False, True, logs, date_)
   
    except Exception as e:
        logs.append((
                f"  Exception Occurred: {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            ))
    
    finally:
        if glogs:
            while not glogs.empty():
                logs.append(glogs.get())
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
    global cr_approval_queue
    global mop_attachment_queue
    global cr_to_circle_dict
    global cr_to_risk_dict
    global cr_to_region_dict
    global cr_to_activity_description_dict

    glogs = Queue()
    cr_approval_queue = Queue()
    mop_attachment_queue = Queue()
    
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

    
    try:
        parsed_date = dp.parse(selected_date)
        date_ = parsed_date

        os.makedirs(os.path.dirname(os.getenv("MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE").format(date_.strftime("%d-%b-%y"))), exist_ok=True)
        if not os.path.exists(os.getenv("MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE").format(date_.strftime("%d-%b-%y"))):
            GLOBAL_LOGS.append("No MOP Attachment and CR Approval file found, Creating one.")
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "MOP Attachment and CR Approval"
            wb.save(os.getenv("MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE").format(date_.strftime("%d-%b-%y")))
            wb.close()
            del wb

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
                    # transaction.on_commit(lambda: sync_replica_task(), using='default')

                selected_date_data = SelectedDateTable.objects.filter(execution_date=parsed_date + timedelta(days=1), is_active=True).values(*settings.SELECTED_DATE_TABLE_FIELDS)
                # print(f"{selected_date_data = }")
            selected_data_df = selected_date_df_maker(selected_date_data)
        
        # print(selected_data_df.columns)
        
        cr_wise_status_df = cr_wise_status_df_maker(parsed_date)
        # cr_wise_status_df = cr_wise_status_df.where(~pd.notna(cr_wise_status_df["CR_Hygiene_Checks"]), "")
        cr_wise_status_df["Install_Test_Plan_Downloads"].fillna("", inplace=True)
        cr_wise_status_df = cr_wise_status_df.loc[
            cr_wise_status_df["Install_Test_Plan_Downloads"].astype(str).str.lower().str.strip() != 'success'
        ]

        selected_data_df = selected_data_df.loc[
            (
                selected_data_df["Planning Status"].astype(str).str.strip().astype(str).str.lower() == 'planned'
            )
        ]

        to_be_filter_crs = list(cr_wise_status_df["cr_no"].astype(str).str.strip())
        selected_data_df = selected_data_df.loc[
            selected_data_df["CR No"].astype(str).str.strip().isin(to_be_filter_crs)
        ]

        planning_sheet_df = selected_data_df
        # Filling NA values with "TempNA"
        planning_sheet_df = planning_sheet_df.where(
            ~pd.isna(planning_sheet_df), "TempNA"
        )

        # removing rows with TempNA CR values
        planning_sheet_df = planning_sheet_df.loc[
            ~(
                (
                    planning_sheet_df["CR No"]
                    .astype(str)
                    .str.lower()
                    .isin(["tempna", "nan", "na"])
                )
                | (planning_sheet_df["CR No"].astype(str).str.strip().map(len) == 0)
            )
        ]
        planning_sheet_df = planning_sheet_df.loc[
            planning_sheet_df["Planning Status"].astype(str).str.strip().str.lower().isin(['planned'])
        ]

        if planning_sheet_df.shape[0] > 0:
            cr_to_circle_dict = dict(
                zip(
                    planning_sheet_df["CR No"].astype(str).str.strip(),
                    planning_sheet_df["Circle"].astype(str).str.strip()
                )
            )
            
            cr_to_risk_dict = dict(
                zip(
                    planning_sheet_df["CR No"].astype(str).str.strip(),
                    planning_sheet_df["Risk"].astype(str).str.strip()
                )
            )
            
            cr_to_region_dict = dict(
                zip(
                    planning_sheet_df["CR No"].astype(str).str.strip(),
                    planning_sheet_df["Region"].astype(str).str.strip()
                )
            )
            
            cr_to_activity_description_dict = dict(
                zip(
                    planning_sheet_df["CR No"].astype(str).str.strip(),
                    planning_sheet_df["Activity Description"].astype(str).str.strip()
                )
            )

            username = str(UserManagement.objects.using('default').get(email=user_email).employee_signum).lower()
            GLOBAL_LOGS = mop_attachment_func(
                planning_sheet_df,
                task,
                runtime,
                timestamp_fn, 
                user_email,
                GLOBAL_LOGS,
                date_,
                username
            )
            # GLOBAL_LOGS = cr_approval_func(
            #     planning_sheet_df,
            #     task,
            #     runtime,
            #     timestamp_fn, 
            #     user_email,
            #     GLOBAL_LOGS,
            #     date_,
            #     username
            # )

    except Exception as e:
        GLOBAL_LOGS.append(
            f"{traceback.format_exc()}\n{e.__class__.__name__}\n{e}"
        )
        raise e
        # return {
        #     "status": "Failed",
        #     "message": f"{task['name']} fail",
        #     "download_ready": False,
        # }
    
    else:
        return {
            "status": "Completed",
            "message": f"{task['name']} completed successfully.",
            "download_ready": True,
            "download_name": str(os.getenv("MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE")).format(date_.strftime("%d-%b-%y"), date_.strftime("%d-%B-%Y")),
            "counts": {},
        }

