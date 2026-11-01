import os
import re
import time
import traceback
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from playwright.sync_api import sync_playwright
from typing import AnyStr, List, Union, Tuple
from queue import Queue
import dateutil.parser as dp
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import column_index_from_string, get_column_letter
from dashboard.views import _timestamp
from dashboard.exceptions import NotFoundException, ValidationException
from dashboard.models import SelectedDateTable, MasterCRDatabase
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction
from dashboard.utils.file_locks import file_lock
from dashboard.task_modules.dependencies.excel_modifier import ExcelModifier
from dashboard.task_modules.dependencies.extra_dependencies import (
    selected_date_df_maker, 
    cr_wise_status_df_maker,
    _norm_series,
    niam_circle_df_maker,
    mail_id_worksheet_df_maker,
    niam_data_updater,
    NIAM_DROPDOWN_SOURCES,
    NIAM_FIELD_TO_COLUMN,
)


# Base location under which generated NIAM workbooks are written
# (HOST_DOWNLOAD_DIR/NIAM_Excel_files/<date>/RITM Input_...xlsx).
workbook_path = os.path.join(settings.HOST_DOWNLOAD_DIR, "NIAM_Excel_files", "base.xlsx")


def niam_workbook_path_for(date_: datetime) -> Path:
    """Canonical output path of the RITM workbook for a given date."""
    return Path(workbook_path).parent.joinpath(
        "NIAM_Excel_files",
        date_.strftime("%d_%b_%Y"),
        f"RITM Input_PS_Core_{date_.strftime('%d_%b_%Y')}.xlsx",
    )


def get_max_row_in_column(worksheet, column_index: int) -> int:
    """Return the last row holding a value in the given 1-based column."""
    last_row = 1
    for row in range(1, worksheet.max_row + 1):
        if worksheet.cell(row=row, column=column_index).value not in (None, ""):
            last_row = row
    return last_row


def node_names_checker(node_type_var_list, node_names):
    """
    Decide which NIAM node rows to create for a single CR.

    The helper used by the legacy automation script was never committed to this
    repository, so this is a faithful-contract stand-in: it returns
    ``(ok, node_names)`` where ``node_names`` is the list of individual node
    names to raise a NIAM row for, applying the safest defensible behaviour:

      * a CR is only eligible when a NIAM Node Type is present, and
      * every non-empty entry of "Node Details" becomes one node row,
        de-duplicated while preserving order.

    Swap in the canonical implementation if/when it becomes available.
    """
    types = [
        str(t).strip()
        for t in (node_type_var_list or [])
        if str(t).strip() and str(t).strip().lower() not in ("nan", "none")
    ]
    if not types:
        return False, []

    cleaned = []
    for name in node_names or []:
        text = str(name).strip()
        if not text or text.lower() in ("nan", "none"):
            continue
        if text not in cleaned:
            cleaned.append(text)

    if not cleaned:
        return False, []
    return True, cleaned


def niam_workbook_template_maker(df: pd.DataFrame, mail_id_worksheet_df: pd.DataFrame, date_: datetime):
    niam_workbook_path = niam_workbook_path_for(date_)

    niam_workbook_path.parent.mkdir(parents=True, exist_ok=True)
    
    niam_workbook_path.unlink(missing_ok=True)
    
    mail_id_sheetname = "Mail_ID_Worksheet"
    
    # print(df)
    
    writer = pd.ExcelWriter(niam_workbook_path, engine='openpyxl')
    df.to_excel(writer, sheet_name="RITM_INPUT", index=False)
    mail_id_worksheet_df.to_excel(writer, sheet_name=mail_id_sheetname, index=False)
    writer.close()
    del writer
    
    wkbk = load_workbook(str(niam_workbook_path))
    input_worksheet = wkbk["RITM_INPUT"]
    mail_id_worksheet = wkbk[mail_id_sheetname]
    mail_id_worksheet.sheet_state = "hidden"
    
    project_name_range = None  # placeholder replaced below by dynamic ranges

    # The five dropdown lists live in the hidden Mail_ID_Worksheet sheet. Build
    # each validation range from the actual position of its list column in the
    # sheet (and target the matching RITM_INPUT column), so the layout of the
    # generated sheet is free to change without silently breaking the dropdowns.
    max_row = input_worksheet.max_row
    input_columns = list(df.columns)
    list_columns = list(mail_id_worksheet_df.columns)

    for field in NIAM_DROPDOWN_SOURCES:
        col_name = NIAM_FIELD_TO_COLUMN[field]
        if col_name not in input_columns or col_name not in list_columns:
            continue

        target_letter = get_column_letter(input_columns.index(col_name) + 1)
        source_letter = get_column_letter(list_columns.index(col_name) + 1)
        source_last_row = get_max_row_in_column(
            mail_id_worksheet, column_index_from_string(source_letter)
        )
        if source_last_row < 2:
            continue

        dv = DataValidation(
            type="list",
            formula1=(
                f"'{mail_id_sheetname}'!"
                f"${source_letter}$2:${source_letter}${source_last_row}"
            ),
            allow_blank=True,
            error="Select from list only",
            errorTitle="Invalid Option",
        )
        input_worksheet.add_data_validation(dv)
        dv.add(f"{target_letter}2:{target_letter}{max_row}")

    wkbk.save(str(niam_workbook_path))
    wkbk.close()
    del wkbk
    
    excel_modifier_obj = ExcelModifier(
        str(niam_workbook_path),
        "RITM_INPUT",
        wrap_text=True
    )
    
    column_index_color_dict = {
        "F4B084": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S"],
        "92D050": ["T", "U", "V", "W", "X"]
    }
    excel_modifier_obj.special_styler(column_index_color_dict)
    del excel_modifier_obj

    return str(niam_workbook_path)
 


def niam_input_initiator(
    filtered_df: pd.DataFrame, 
    mail_id_worksheet_df: pd.DataFrame, 
    niam_circle_df: pd.DataFrame, 
    date_: datetime):
    
    if filtered_df.shape[0] > 0:
        unique_crs = filtered_df["CR No"].astype(str).str.strip().unique()
        
        change_responsible_mail_ids = dict(
            zip(
                mail_id_worksheet_df["Change Responsible"], 
                mail_id_worksheet_df["Mail ID"]
            )
        )
        
        cr_niam_circle_to_niam_circle_name_mapping = dict(
            zip(
                mail_id_worksheet_df["NIAM Circles"].astype(str).str.strip(),
                mail_id_worksheet_df["NIAM Circle Name"].astype(str).str.strip()
            )
        )
        
        cr_circle_to_niam_circle_mapping = dict(
            zip(
                mail_id_worksheet_df["Circle"].astype(str).str.strip(),
                mail_id_worksheet_df["NIAM Circles"].astype(str).str.strip()
            )
        )
        
        # from pprint import pprint
        # print("cr_niam_circle_to_niam_circle_name_mapping =")
        # pprint(cr_niam_circle_to_niam_circle_name_mapping)
        # print("\ncr_circle_to_niam_circle_mapping =")
        # pprint(cr_circle_to_niam_circle_mapping)
        
        niam_input_template_df = pd.DataFrame()
        
        requested_for_email = []
        request_type = []
        request_for = []
        node_managed_by = []
        subtype = []
        domain = []
        access_type = []
        uid_type = []
        policy_period = []
        user_type = []
        request_ip = []
        sr_or_change_number = []
        activity_title = []
        sr_cr_start_date_time = []
        sr_cr_end_date_time = []
        niam_access_start_date = []
        niam_access_end_date = []
        business_justification = []
        node_name = []
        node_details = []
        activity_name = []
        project_name = []
        execution_location = []
        
        
        activity_executor_index = filtered_df.columns.get_loc("Activity Executor")
        circle_index = filtered_df.columns.get_loc("Circle")
        activity_type_index = filtered_df.columns.get_loc("Activity Type")
        niam_node_type_index = filtered_df.columns.get_loc("NIAM Node Type")
        node_details_index = filtered_df.columns.get_loc("Node Details")
        
        # today_date = datetime.now()
        # today_date = today_date.replace(hour=0, minute=0, second=0, microsecond=0)
        today_date = date_.replace(hour=0, minute=0, second=0, microsecond=0)

        # today_date = today_date.strftime('%d-%m-%Y %H:%M:%S')

        # tomorrow_date = datetime.now() + timedelta(days=1)
        tomorrow_date = date_ + timedelta(days=1)
        tomorrow_date = tomorrow_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        cr_start_date_time = tomorrow_date
        cr_start_date_time = cr_start_date_time.strftime("%Y-%m-%d %H:%M:%S")

        cr_end_date_time = tomorrow_date + timedelta(hours=6)
        cr_end_date_time = cr_end_date_time.strftime("%Y-%m-%d %H:%M:%S")

        niam_access_start_date_var = today_date.replace(hour=22)
        niam_access_start_date_var = niam_access_start_date_var.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        niam_access_end_date_var = tomorrow_date + timedelta(hours=8)
        niam_access_end_date_var = niam_access_end_date_var.strftime("%Y-%m-%d %H:%M:%S")

        business_justification_var = "Access required for CR execution ({} circle).\nRemark :- Please provide access from 10PM to 08AM as requested to ensure pre-post backup and for rollback scenario in worst case."
        
        i = 0
        while i < unique_crs.size:
            # print(f"{i =}")
            cr = unique_crs[i]
            selected_cr_df = filtered_df.loc[filtered_df["CR No"] == cr]
            
            node_type_var = selected_cr_df.iloc[0, niam_node_type_index]
            
            node_type_var_list = [str(element).strip() for element in node_type_var.split(",")]
            node_names = re.sub(r",", "", selected_cr_df.iloc[0, node_details_index])
            node_names = [str(element).strip() for element in re.split("\n", node_names) if len(str(element).strip())> 0]
            # print(f"{cr = }\n{node_type_var = }\n{node_type_var_list = }\n{node_names = }\n")
            
            bool_result, node_names_list = node_names_checker(node_type_var_list, node_names)
            # print(f"\n{bool_result = }\n{node_names_list = }")
            
            if bool_result:
                try:
                    j = 0
                    while j < len(node_names_list):
                        selected_node_name_list = node_names_list[j]
                        
                        # Entry for NIAM Node Name
                        node_name.append(selected_node_name_list)
                        
                        # Entry for Total Node Details
                        node_details.append(
                            selected_cr_df.iloc[0, node_details_index]
                        )
                        
                        # Entry for Request for (email)
                        requested_for_email.append(
                            change_responsible_mail_ids.get(
                                str(selected_cr_df.iloc[0, activity_executor_index]), 
                                ""
                            )
                        )
                        
                        # Entry for Request Type Column
                        request_type.append(
                            "NIAM"
                        )
                        
                        # Entry for Request For Column
                        request_for.append(
                            ""
                        )
                        
                        # Entry for Node Managed By Column
                        node_managed_by.append(
                            "Ericsson"
                        )
                        
                        # Entry for Subtype Column
                        subtype.append(
                            "Bharti Airtel"
                        )
                        
                        # Entry for Domain Column
                        domain.append(
                            ""
                        )
                        
                        # Entry for Access Type Column
                        access_type.append(
                            ""
                        )
                        
                        # Entry for UID Type
                        uid_type.append(
                            "OLMID"
                        )
                        
                        # Entry for Policy Period
                        policy_period.append(
                            "TEMPORARY"
                        ) 
                        
                        # Entry for User Type Column
                        user_type.append(
                            cr_niam_circle_to_niam_circle_name_mapping.get(
                                        cr_circle_to_niam_circle_mapping.get(
                                            str(selected_cr_df.iloc[0, circle_index]), 
                                            ""
                                        ), 
                                    "")
                        )
                        
                        # Entry for Request IP column
                        request_ip.append(
                            "No"
                        )
                        
                        # Entry for SR or Change No Column
                        sr_or_change_number.append(
                            cr
                        )
                        
                        # Entry for Activity Title Column
                        activity_title.append(
                            selected_cr_df.iloc[0, activity_type_index]
                        )
                        
                        # Entry for SR CR Start Date Time Column
                        sr_cr_start_date_time.append(
                            cr_start_date_time
                        )
                        
                        # Entry for SR CR End Date Time Column
                        sr_cr_end_date_time.append(
                            cr_end_date_time
                        )
                        
                        # Entry for NIAM Access Start Date Column
                        niam_access_start_date.append(
                            niam_access_start_date_var
                        )
                        
                        # Entry for NIAM Access End Date Column
                        niam_access_end_date.append(
                            niam_access_end_date_var
                        )
                        
                        # Entry for Business Justification Column
                        # print(f"{str(selected_cr_df.iloc[0, circle_index]) = }")
                        # print(f"{cr_niam_circle_to_niam_circle_name_mapping.get(
                        #                 cr_circle_to_niam_circle_mapping.get(
                        #                     str(selected_cr_df.iloc[0, circle_index]), 
                        #                     ""
                        #                 ), 
                        #             "") =}")
                        business_justification.append(
                            business_justification_var.format(
                                    cr_niam_circle_to_niam_circle_name_mapping.get(
                                        cr_circle_to_niam_circle_mapping.get(
                                            str(selected_cr_df.iloc[0, circle_index]), 
                                            ""
                                        ), 
                                    "")
                            )
                        )
                        
                    
                        
                        # Entry for Activity Name Column
                        activity_name.append("")
                        
                        # Entry for Project Name Column
                        project_name.append("")
                        
                        # Entry for Execution Location Column
                        execution_location.append("Partner Office")
                        
                        j += 1
                
                except Exception:
                    i += 1
                    continue   
            i += 1
        
        niam_input_template_df = pd.DataFrame(
            {
                "SL. No": range(1, len(requested_for_email) + 1),   # A
                "Request Type": request_type,                       # B
                "Node Managed By": node_managed_by,                 # C
                "Subtype": subtype,                                 # D
                "UID Type": uid_type,                               # E
                "Policy period": policy_period,                     # F
                "User Type": user_type,                             # G
                "Request IP>10 ?": request_ip,                      # H
                "Business Justification": business_justification,   # I
                "SR_CR_Start Date-Time": sr_cr_start_date_time,     # J
                "SR_CR_End Date-Time": sr_cr_end_date_time,         # K
                "NIAM Access Start Date": niam_access_start_date,   # L
                "NIAM Access END Date": niam_access_end_date,       # M
                "Execution Location": execution_location,           # N
                "SR OR CHANGE NO": sr_or_change_number,             # O 
                "Activity Title": activity_title,                   # P
                "NIAM Node Name": node_name,                        # Q
                "Total Node Details": node_details,                 # R
                "Requested For(email)": requested_for_email,        # S
                "Activity Name": activity_name,                     # T
                "Project Name": project_name,                       # U
                "Request For": request_for,                         # V
                "Domain": domain,                                   # W
                "Access Type": access_type,                         # X
            }
        )
        
        niam_data_updater(
            niam_input_template_df,
            execution_date=date_ + timedelta(days=1)
        )
        
        niam_workbook_template_maker(niam_input_template_df, mail_id_worksheet_df, date_)
        return niam_workbook_path_for(date_)

        

# The "Fetch CRs" task (NIAM Template Database "Fetch CR" button). Kept aligned
# with views.FETCH_CRS_TASK_ID so this module can serve both NIAM flows:
#   id 7 = full NIAM Ticket Generation (run_task below)
#   id 8 = Fetch CRs — validate/rebuild SelectedDateTable for the selected
#          night's execution date and then build the NIAM input (generate_niam_input)
#          so the page can display the Input sheet straight away.
FETCH_CRS_TASK_ID = 8


def fetch_crs_for_date(selected_date, GLOBAL_LOGS, timestamp_fn, runtime=None):
    """Validate the selected (night) date and (re)build that night's CRs.

    The app-wide convention is that the date picked in the UI is the *night*
    date: the CRs execute on the following day (execution_date = picked + 1),
    which is the window the NIAM access (22:00 -> 08:00) belongs to. This
    matches every other task module and ``filter_region_crs``.

    - No date           -> ValidationException ("Missing Date")
    - No CRs that night -> NotFoundException ("No Data")
    - Otherwise         -> scoped rebuild of SelectedDateTable for the execution
                           date from the active MasterCRDatabase rows.

    The synchronous presence gate in start_task surfaces those errors to the
    page as dialogs before this runs; this function is the task-side job.
    """
    if not selected_date:
        raise ValidationException(
            "Please select a Date before fetching CRs.",
            title="Missing Date",
        )

    try:
        picked_date = dp.parse(selected_date).date()
    except (ValueError, TypeError):
        raise ValidationException(
            "Invalid date format. Use YYYY-MM-DD.",
            title="Invalid Date Format",
        )

    execution_date = picked_date + timedelta(days=1)

    GLOBAL_LOGS.append(
        f"Fetch CRs: night {picked_date.isoformat()} -> execution "
        f"{execution_date.isoformat()} ---- {timestamp_fn()}"
    )

    in_selected = SelectedDateTable.objects.filter(
        execution_date=execution_date, is_active=True
    ).exists()
    in_master = MasterCRDatabase.objects.filter(
        execution_date=execution_date, is_active=True
    ).exists()

    if not (in_selected or in_master):
        raise NotFoundException(
            f"No CR found for the selected date {picked_date} (CRs execute on "
            f"{execution_date}).",
            title="No Data",
        )

    fields = settings.SELECTED_DATE_TABLE_FIELDS
    source = list(
        MasterCRDatabase.objects.filter(
            execution_date=execution_date, is_active=True
        ).values(*fields)
    )

    # Scoped rebuild: only the execution date's rows are replaced; every other
    # date's SelectedDateTable data is left untouched. The date's existing rows
    # (active + legacy CoW versions) are replaced atomically with fresh rows
    # built from the active MasterCRDatabase versions.
    #
    # NOTE: "id" is deliberately NOT copied from MasterCRDatabase — those ids
    # are the *master* table's keys and are not free in SelectedDateTable
    # (rows for other dates may already hold them). Letting the auto-pk assign
    # fresh ids avoids primary-key collisions (selected_date_table_pkey).
    with transaction.atomic(using="default"):
        SelectedDateTable.objects.using("default").filter(
            execution_date=execution_date
        ).delete()
        if source:
            valid_fields = {f.name for f in SelectedDateTable._meta.get_fields()}
            instances = [
                SelectedDateTable(
                    **{k: v for k, v in row.items() if k in valid_fields and k != "id"}
                )
                for row in source
            ]
            SelectedDateTable.objects.using("default").bulk_create(instances)

    if runtime is not None:
        runtime["total_crs"] = len(source)

    message = (
        f"{len(source)} CR(s) found for {picked_date} (execute {execution_date})."
    )
    GLOBAL_LOGS.append(f"Fetch CRs: {message} ---- {timestamp_fn()}")
    return {
        "status": "Completed",
        "download_ready": False,
        "message": message,
        "counts": {"total_crs": len(source), "execution_date": execution_date.isoformat()},
    }


def generate_niam_input(night_date, GLOBAL_LOGS=None, timestamp_fn=None, runtime=None):
    """
    Build the NIAM input template for the night date ``night_date`` and:

      * upsert one row per CR per node into NIAMTicketGenerationTable, and
      * (re)write the dated RITM workbook
        (RITM Input_PS_Core_<night_date>.xlsx).

    The CRs are read from SelectedDateTable for the execution date
    (``night_date`` + 1), matching the rest of the app. This is the single
    implementation shared by the "NIAM Ticket Generator" task (id 7) and the
    NIAM page's "Fetch CR" task (id 8), so both produce an identical Input
    sheet.

    Returns a dict in the same shape the task runner expects
    (``status`` / ``download_ready`` / ``message`` / optional ``download_name``).
    """
    GLOBAL_LOGS = GLOBAL_LOGS or []
    timestamp_fn = timestamp_fn or _timestamp

    parsed_date = night_date
    if isinstance(parsed_date, str):
        parsed_date = dp.parse(parsed_date)
    if not isinstance(parsed_date, datetime):
        parsed_date = datetime.combine(parsed_date, datetime.min.time())

    execution_date = (parsed_date + timedelta(days=1)).date()
    label = f"{parsed_date.date()}"

    empty_result = {
        "status": "Completed",
        "download_ready": False,
        "message": f"No NIAM tickets were required for {label}.",
    }

    selected_date_data = list(
        SelectedDateTable.objects.filter(
            execution_date=execution_date, is_active=True
        ).values(*settings.SELECTED_DATE_TABLE_FIELDS)
    )

    if not selected_date_data:
        GLOBAL_LOGS.append(
            f"NIAM: no CRs in SelectedDateTable for execution {execution_date} "
            f"---- {timestamp_fn()}"
        )
        return empty_result

    selected_data_df = selected_date_df_maker(selected_date_data)
    if selected_data_df is None or selected_data_df.empty:
        return empty_result

    cr_wise_status_df = cr_wise_status_df_maker(parsed_date)
    if cr_wise_status_df is None or cr_wise_status_df.empty:
        return empty_result

    # Added (not inplace) to stay copy-on-write safe and avoid chained-assignment.
    cr_wise_status_df["NIAM_Ticket"] = (
        cr_wise_status_df["NIAM_Ticket"].fillna("").astype(str).str.strip().str.lower()
    )

    cr_wise_status_df = cr_wise_status_df.loc[
        cr_wise_status_df["NIAM_Ticket"] != "success"
    ]

    planning_status_norm = _norm_series(selected_data_df["Planning Status"])
    niam_cr_norm = _norm_series(selected_data_df["NIAM Ticket Required (Yes/No)"])
    niam_node_type = _norm_series(selected_data_df["NIAM Node Type"])

    selected_data_df = selected_data_df.loc[
        (planning_status_norm.eq("planned") & niam_cr_norm.eq("yes"))
        & (niam_node_type.astype(str).str.strip().map(len) > 0)
        & (
            ~niam_node_type.astype(str)
            .str.strip()
            .str.lower()
            .isin(["nan", "tempna", "na"])
        )
    ]

    to_be_filter_crs = list(cr_wise_status_df["cr_no"].astype(str).str.strip().unique())
    selected_data_df = selected_data_df.loc[
        selected_data_df["CR No"].astype(str).str.strip().isin(to_be_filter_crs)
    ]

    if selected_data_df.empty:
        return empty_result

    # The hidden "Mail_ID_Worksheet" frame supplies the Change Responsible ->
    # Mail ID lookup, the Circle -> NIAM Circle mapping, and the five dropdown
    # lists used by the generated workbook.
    mail_id_df = mail_id_worksheet_df_maker()
    niam_circle_df = niam_circle_df_maker()

    # Serialise generation for the same execution date: the workbook path is
    # shared by date, so two users generating for the same day must not write
    # it at the same time.
    workbook_file = None
    try:
        with file_lock(niam_workbook_path_for(parsed_date)):
            workbook_file = niam_input_initiator(
                selected_data_df,
                mail_id_df,
                niam_circle_df,
                parsed_date,
            )
    except TimeoutError as exc:
        return {
            "status": "Failed",
            "download_ready": False,
            "message": f"Could not lock the NIAM workbook for {label}: {exc}",
        }

    if workbook_file and Path(workbook_file).exists():
        GLOBAL_LOGS.append(
            f"NIAM ticket workbook generated: {workbook_file} ---- {timestamp_fn()}"
        )
        return {
            "status": "Completed",
            "download_ready": True,
            "download_name": str(workbook_file),
            "message": f"NIAM ticket generated for {label}.",
        }

    return empty_result


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
    GLOBAL_LOGS = GLOBAL_LOGS or []
    timestamp_fn = timestamp_fn or _timestamp

    runtime["status"] = "Running"
    runtime["download_ready"] = False

    # Password fields (new)
    runtime["password_required"] = False
    runtime["password"] = None
    runtime["pwd_event"] = None

    # OTP fields (existing)
    runtime["otp_required"] = False
    runtime["otp"] = None
    runtime["otp_event"] = Event()

    # "Fetch CR" (task id 8, NIAM Template Database page): fetch the selected
    # night's CRs, then immediately build the NIAM input (same work the "NIAM
    # Ticket Generator" button does) so the Input sheet is ready to display.
    if task.get("id") == FETCH_CRS_TASK_ID:
        fetch_result = fetch_crs_for_date(
            selected_date=selected_date,
            GLOBAL_LOGS=GLOBAL_LOGS,
            timestamp_fn=timestamp_fn,
            runtime=runtime,
        )
        if fetch_result.get("status") != "Completed":
            return fetch_result

        gen_result = generate_niam_input(
            selected_date,
            GLOBAL_LOGS=GLOBAL_LOGS,
            timestamp_fn=timestamp_fn,
            runtime=runtime,
        )
        gen_result["counts"] = fetch_result.get("counts", {})
        return gen_result

    # Task id 7: NIAM Ticket Generation on its own.
    return generate_niam_input(
        selected_date,
        GLOBAL_LOGS=GLOBAL_LOGS,
        timestamp_fn=timestamp_fn,
        runtime=runtime,
    )
