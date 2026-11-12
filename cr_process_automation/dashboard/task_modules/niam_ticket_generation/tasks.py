import os
import queue
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
from dashboard.models import (
    SelectedDateTable,
    MasterCRDatabase,
    NIAMTicketGenerationTable,
)
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from dashboard.utils.file_locks import file_lock
from dashboard.task_modules.dependencies.excel_modifier import ExcelModifier
from dashboard.task_modules.dependencies.extra_dependencies import (
    selected_date_df_maker, 
    cr_wise_status_df_maker,
    _norm_series,
    niam_circle_df_maker,
    mail_id_worksheet_df_maker,
    niam_data_updater,
    renumber_niam_sno,
    NIAM_DROPDOWN_SOURCES,
    NIAM_FIELD_TO_COLUMN,
    NIAM_COLUMN_TO_FIELD_MAPPING,
    NIAM_DATETIME_FIELDS,
)


# Base location under which generated NIAM workbooks are written
# (HOST_DOWNLOAD_DIR/NIAM_Excel_files/<date>/RITM Input_...xlsx).
workbook_path = os.path.join(settings.HOST_DOWNLOAD_DIR, "NIAM_Excel_files")


def niam_workbook_path_for(date_: datetime) -> Path:
    """Canonical output path of the RITM workbook for a given date."""
    return Path(workbook_path).joinpath(
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


def _cell_text(value) -> str:
    """Return a cell value as text, mapping None/NaN/NaT to an empty string."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    text = str(value)
    return "" if text.strip().lower() in ("nan", "nat", "none") else text


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
        "F4B084": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "Y"],
        "92D050": ["T", "U", "V", "W", "X"]
    }
    excel_modifier_obj.special_styler(column_index_color_dict)
    del excel_modifier_obj

    return str(niam_workbook_path)
 


def niam_input_initiator(
    filtered_df: pd.DataFrame, 
    mail_id_worksheet_df: pd.DataFrame, 
    niam_circle_df: pd.DataFrame, 
    date_: datetime,
    include_all_crs: bool = False):
    """
    Build the 24-column RITM input frame from the (already filtered) CR frame.

    ``include_all_crs`` keeps CRs whose NIAM fields are still blank: instead of
    skipping a CR with no Node Type / Node Details, one placeholder row is
    emitted with a blank NIAM Node Name so the user can fill the row in on the
    NIAM Template Database page. Strict ticket generation leaves it False so
    only fully-specified CRs produce rows.
    """
    
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
            
            node_type_var = _cell_text(selected_cr_df.iloc[0, niam_node_type_index])
            
            node_type_var_list = [element.strip() for element in node_type_var.split(",")]
            node_details_value = _cell_text(
                selected_cr_df.iloc[0, node_details_index]
            )
            node_names = re.sub(r",", "", node_details_value)
            node_names = [str(element).strip() for element in re.split("\n", node_names) if len(str(element).strip())> 0]
            # print(f"{cr = }\n{node_type_var = }\n{node_type_var_list = }\n{node_names = }\n")
            
            bool_result, node_names_list = node_names_checker(node_type_var_list, node_names)
            # print(f"\n{bool_result = }\n{node_names_list = }")
            
            if not bool_result and include_all_crs:
                # Keep the CR in the template even though its NIAM fields are
                # still blank; the blank node name marks it as a placeholder.
                node_names_list = [""]
                bool_result = True
            
            if bool_result:
                try:
                    j = 0
                    while j < len(node_names_list):
                        selected_node_name_list = node_names_list[j]
                        
                        # Entry for NIAM Node Name
                        node_name.append(selected_node_name_list)
                        
                        # Entry for Total Node Details
                        node_details.append(
                            node_details_value
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
#   id 7 = full NIAM Ticket Generation (strict eligibility)
#   id 8 = Fetch CRs — validate/rebuild SelectedDateTable for the selected
#          night's execution date and then add NIAM template rows for CRs whose
#          NIAM Ticket Required = Yes (include_all_crs=True). Existing NIAM rows
#          are always kept.
NIAM_GENERATE_TASK_ID = 7
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

    # If the CR tables have no rows for that execution date but NIAM rows were
    # already generated, there is nothing to rebuild: the page can still show
    # the existing NIAM rows.
    in_selected = SelectedDateTable.objects.filter(
        execution_date=execution_date, is_active=True
    ).exists()
    in_master = MasterCRDatabase.objects.filter(
        execution_date=execution_date, is_active=True
    ).exists()

    if not (in_selected or in_master):
        niam_count = NIAMTicketGenerationTable.objects.filter(
            execution_date=execution_date
        ).count()
        if niam_count:
            message = (
                f"{niam_count} existing NIAM row(s) found for {picked_date} "
                f"(execute {execution_date}); reusing them."
            )
            GLOBAL_LOGS.append(f"Fetch CRs: {message} ---- {timestamp_fn()}")
            if runtime is not None:
                runtime["total_crs"] = niam_count
            return {
                "status": "Completed",
                "download_ready": False,
                "message": message,
                "counts": {
                    "total_crs": niam_count,
                    "execution_date": execution_date.isoformat(),
                },
            }

        # Help the user when they picked the execution date instead of the
        # night date: the rows exist, just under a different (earlier) picker
        # value.
        picked_has_crs = (
            SelectedDateTable.objects.using("default").filter(
                execution_date=picked_date, is_active=True
            ).exists()
            or MasterCRDatabase.objects.using("default").filter(
                execution_date=picked_date, is_active=True
            ).exists()
            or NIAMTicketGenerationTable.objects.using("default").filter(
                execution_date=picked_date
            ).exists()
        )
        hint = (
            f" CRs exist for {picked_date} itself; select "
            f"{picked_date - timedelta(days=1)} as the night date to work on "
            f"that night."
            if picked_has_crs
            else ""
        )
        raise NotFoundException(
            f"No CR found for the night of {picked_date} (they execute on "
            f"{execution_date}).{hint}",
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


def _niam_template_df_from_rows(rows):
    """Convert NIAMTicketGenerationTable rows into the 24-column RITM frame."""
    df = pd.DataFrame(
        {
            column: [row.get(field) for row in rows]
            for column, field in NIAM_COLUMN_TO_FIELD_MAPPING.items()
        },
        columns=list(NIAM_COLUMN_TO_FIELD_MAPPING.keys()),
    )

    # Excel cannot store timezone-aware datetimes. Render the stored datetimes
    # in the app's local timezone (Asia/Kolkata) as naive wall-clock values,
    # matching the strings written by niam_input_initiator().
    for field in NIAM_DATETIME_FIELDS:
        column = NIAM_FIELD_TO_COLUMN.get(field)
        if column not in df.columns:
            continue
        series = pd.to_datetime(df[column], errors="coerce")
        if getattr(series.dt, "tz", None) is not None:
            series = series.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
        df[column] = series

    return df


def _reuse_existing_niam_rows(rows, parsed_date, label, GLOBAL_LOGS, timestamp_fn):
    """
    Rebuild the dated workbook from NIAM rows that were generated previously.

    Existing NIAM rows are authoritative: they may contain values a user edited
    on the NIAM Template Database page, so they are never re-derived from the
    CR tables (which would overwrite those edits).
    """
    execution_date = (parsed_date + timedelta(days=1)).date()
    GLOBAL_LOGS.append(
        f"NIAM: {len(rows)} existing row(s) found in NIAMTicketGenerationTable "
        f"for execution {execution_date}; reusing them ---- {timestamp_fn()}"
    )

    try:
        with file_lock(niam_workbook_path_for(parsed_date)):
            workbook_file = niam_workbook_template_maker(
                _niam_template_df_from_rows(rows),
                mail_id_worksheet_df_maker(),
                parsed_date,
            )
    except Exception as exc:  # workbook is optional; the page data is already there
        GLOBAL_LOGS.append(
            f"NIAM: could not rewrite the workbook from existing rows: {exc} "
            f"---- {timestamp_fn()}"
        )
        return {
            "status": "Completed",
            "download_ready": False,
            "message": (
                f"{len(rows)} existing NIAM row(s) found for {label}; "
                "the workbook could not be rewritten."
            ),
        }

    GLOBAL_LOGS.append(
        f"NIAM ticket workbook rebuilt from existing rows: {workbook_file} "
        f"---- {timestamp_fn()}"
    )
    return {
        "status": "Completed",
        "download_ready": True,
        "download_name": str(workbook_file),
        "message": f"{len(rows)} existing NIAM row(s) reused for {label}.",
    }


def _niam_cr_source_candidates(execution_date):
    """Yield ("SelectedDateTable"|"MasterCRDatabase", rows) for the date.

    Reads go to the master DB: this runs in the same pipeline that has just
    rebuilt SelectedDateTable, so it must not race replication lag.
    """
    fields = settings.SELECTED_DATE_TABLE_FIELDS

    selected_rows = list(
        SelectedDateTable.objects.using("default").filter(
            execution_date=execution_date, is_active=True
        ).values(*fields)
    )
    if selected_rows:
        yield "SelectedDateTable", selected_rows

    # Always keep MasterCRDatabase as a fallback: SelectedDateTable may be
    # missing or stale for a date even when the master rows exist.
    master_rows = list(
        MasterCRDatabase.objects.using("default").filter(
            execution_date=execution_date, is_active=True
        ).values(*fields)
    )
    if master_rows:
        yield "MasterCRDatabase", master_rows


def _filter_niam_eligible(df, cr_whitelist, include_all=False):
    """Apply the NIAM eligibility rules to a SelectedDate-shaped DataFrame.

    With ``include_all=True`` only CRs flagged ``NIAM Ticket Required = Yes``
    are kept (used by "Fetch CRs" so the NIAM Template Database page is scoped
    to CRs that need a ticket, even when their node details are still blank).
    Strict ticket generation keeps ``include_all=False``.
    """
    if df is None or df.empty:
        return df

    if include_all:
        column = "NIAM Ticket Required (Yes/No)"
        if column not in df.columns:
            return df.iloc[0:0]
        return df.loc[_norm_series(df[column]).eq("yes")]

    required_columns = {
        "CR No",
        "Planning Status",
        "NIAM Ticket Required (Yes/No)",
        "NIAM Node Type",
    }
    if not required_columns.issubset(df.columns):
        return df.iloc[0:0]

    planning_status_norm = _norm_series(df["Planning Status"])
    niam_cr_norm = _norm_series(df["NIAM Ticket Required (Yes/No)"])
    niam_node_type = _norm_series(df["NIAM Node Type"])

    filtered = df.loc[
        (planning_status_norm.eq("planned") & niam_cr_norm.eq("yes"))
        & (niam_node_type.astype(str).str.strip().map(len) > 0)
        & (
            ~niam_node_type.astype(str)
            .str.strip()
            .str.lower()
            .isin(["nan", "tempna", "na"])
        )
    ]

    if cr_whitelist:
        filtered = filtered.loc[
            filtered["CR No"].astype(str).str.strip().isin(cr_whitelist)
        ]

    return filtered


def _placeholder_node_rows(execution_date):
    """Rows for the date that were created with a blank NIAM node name."""
    return NIAMTicketGenerationTable.objects.filter(
        execution_date=execution_date
    ).filter(
        Q(node_name__isnull=True)
        | Q(node_name__exact="")
        | Q(node_name__iexact="nan")
        | Q(node_name__iexact="none")
    )


def _remove_placeholder_niam_rows(execution_date, cr_numbers=None):
    """Delete blank-node placeholder rows for the date (optionally per CR)."""
    qs = _placeholder_node_rows(execution_date)
    if cr_numbers is not None:
        normalized = {str(cr).strip() for cr in cr_numbers if str(cr).strip()}
        if not normalized:
            return 0
        qs = qs.filter(sr_or_change_number__in=normalized)
    with transaction.atomic(using="default"):
        count, _ = qs.delete()
        if count:
            renumber_niam_sno(execution_date, using="default", compact=True)
    return count


def generate_niam_input(
    night_date,
    GLOBAL_LOGS=None,
    timestamp_fn=None,
    runtime=None,
    include_all_crs=False,
):
    """
    Build the NIAM input template for the night date ``night_date`` and:

      * upsert one row per CR per node into NIAMTicketGenerationTable, and
      * (re)write the dated RITM workbook
        (RITM Input_PS_Core_<night_date>.xlsx).

    Source priority (execution date = ``night_date`` + 1):

      1. NIAMTicketGenerationTable rows already generated for that date: reuse
         them as-is (including any user edits) and only rebuild the workbook.
      2. SelectedDateTable rows for that execution date.
      3. MasterCRDatabase rows for that execution date.

    This is the single implementation shared by the "NIAM Ticket Generator"
    task (id 7) and the NIAM page's "Fetch CR" task (id 8).

    ``include_all_crs=True`` is the "Fetch CR" flow: only CRs flagged
    ``NIAM Ticket Required = Yes`` are considered, existing NIAM rows are kept
    as-is (including rows whose ticket was never raised), and template rows are
    added only for Yes CRs that do not have a row yet. Strict generation (id 7)
    keeps the full eligibility gate (planned + Yes + node details).

    Returns a dict in the same shape the task runner expects
    (``status`` / ``download_ready`` / ``message`` / optional ``download_name``).
    """
    if GLOBAL_LOGS is None:
        GLOBAL_LOGS = []
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
        "message": (
            f"No CRs found for {label}."
            if include_all_crs
            else f"No NIAM tickets were required for {label}."
        ),
    }

    # Strict generation must not treat template placeholders (blank node name)
    # as already-raised tickets. They are kept for CRs that stay ineligible and
    # are removed per CR below once real node rows replace them.
    placeholder_q = (
        Q(node_name__isnull=True)
        | Q(node_name__exact="")
        | Q(node_name__iexact="nan")
        | Q(node_name__iexact="none")
    )

    # 1) Existing NIAM rows are authoritative and are always shown on the page,
    #    whether the ticket was raised or not, because they may contain manual
    #    edits. Strict generation ignores blank-node placeholders here so it can
    #    still generate the real node rows for a date that only has a template.
    existing_qs = NIAMTicketGenerationTable.objects.using("default").filter(
        execution_date=execution_date
    )
    if not include_all_crs:
        existing_qs = existing_qs.exclude(placeholder_q)
    existing_niam_rows = list(existing_qs.values())
    existing_cr_numbers = {
        str(row.get("sr_or_change_number") or "").strip()
        for row in existing_niam_rows
        if str(row.get("sr_or_change_number") or "").strip()
    }
    if existing_niam_rows and not include_all_crs:
        return _reuse_existing_niam_rows(
            existing_niam_rows, parsed_date, label, GLOBAL_LOGS, timestamp_fn
        )

    cr_wise_status_df = cr_wise_status_df_maker(parsed_date)
    if cr_wise_status_df is None or cr_wise_status_df.empty:
        GLOBAL_LOGS.append(
            f"NIAM: no CRWiseStatus rows for execution {execution_date} "
            f"---- {timestamp_fn()}"
        )
        if not include_all_crs:
            return empty_result
        to_be_filter_crs = []
    else:
        # NIAM_Ticket column removed; treat all as not success
        if "NIAM_Ticket" in cr_wise_status_df.columns:
            cr_wise_status_df["NIAM_Ticket"] = (
                cr_wise_status_df["NIAM_Ticket"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.lower()
            )
            cr_wise_status_df = cr_wise_status_df.loc[
                cr_wise_status_df["NIAM_Ticket"] != "success"
            ]
        # else include all CRs from cr_wise_status_df

        to_be_filter_crs = list(
            cr_wise_status_df["cr_no"].astype(str).str.strip().unique()
        )

    # 2) SelectedDateTable first, 3) MasterCRDatabase as the fallback.
    selected_data_df = None
    used_source = None
    for source_name, rows in _niam_cr_source_candidates(execution_date):
        candidate_df = selected_date_df_maker(rows)
        if candidate_df is None or candidate_df.empty:
            continue

        filtered_df = _filter_niam_eligible(
            candidate_df, to_be_filter_crs, include_all=include_all_crs
        )
        if include_all_crs:
            GLOBAL_LOGS.append(
                f"NIAM: {source_name} has {len(rows)} CR(s) for execution "
                f"{execution_date}; {len(filtered_df)} have NIAM Ticket "
                f"Required=Yes ---- {timestamp_fn()}"
            )
        else:
            GLOBAL_LOGS.append(
                f"NIAM: {source_name} has {len(rows)} CR(s) for execution "
                f"{execution_date}; {len(filtered_df)} pass the NIAM filters "
                f"(planned + NIAM Ticket Required=yes + NIAM Node Type set) "
                f"---- {timestamp_fn()}"
            )
        if not filtered_df.empty:
            selected_data_df = filtered_df
            used_source = source_name
            break

    if selected_data_df is None or selected_data_df.empty:
        if include_all_crs:
            GLOBAL_LOGS.append(
                f"NIAM: no CRs with NIAM Ticket Required=Yes in "
                f"SelectedDateTable or MasterCRDatabase for execution "
                f"{execution_date} ---- {timestamp_fn()}"
            )
            empty_result["message"] = (
                f"No CRs with NIAM Ticket Required=Yes found for {label}."
            )
            if existing_niam_rows:
                return _reuse_existing_niam_rows(
                    existing_niam_rows, parsed_date, label, GLOBAL_LOGS, timestamp_fn
                )
            return empty_result

        GLOBAL_LOGS.append(
            f"NIAM: no CRs eligible for the template in SelectedDateTable or "
            f"MasterCRDatabase for execution {execution_date} "
            f"---- {timestamp_fn()}"
        )
        return empty_result

    if include_all_crs:
        # Keep every existing NIAM row untouched; add rows only for Yes CRs
        # that are not represented in NIAMTicketGenerationTable yet.
        already_present = (
            selected_data_df["CR No"].astype(str).str.strip().isin(existing_cr_numbers)
        )
        selected_data_df = selected_data_df.loc[~already_present]
        if selected_data_df.empty:
            GLOBAL_LOGS.append(
                f"NIAM: all {len(existing_cr_numbers)} NIAM CR(s) for execution "
                f"{execution_date} already have template rows; nothing to add "
                f"---- {timestamp_fn()}"
            )
            if existing_niam_rows:
                return _reuse_existing_niam_rows(
                    existing_niam_rows, parsed_date, label, GLOBAL_LOGS, timestamp_fn
                )
            return empty_result

    if runtime is not None:
        runtime["total_crs"] = len(selected_data_df)

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
                include_all_crs=include_all_crs,
            )
    except TimeoutError as exc:
        return {
            "status": "Failed",
            "download_ready": False,
            "message": f"Could not lock the NIAM workbook for {label}: {exc}",
        }

    if workbook_file and Path(workbook_file).exists():
        # Real node rows now exist for these CRs, so drop their blank-node
        # placeholders (placeholder rows for ineligible CRs are kept).
        if not include_all_crs and "CR No" in selected_data_df.columns:
            removed = _remove_placeholder_niam_rows(
                execution_date,
                selected_data_df["CR No"].astype(str).str.strip().unique(),
            )
            if removed:
                GLOBAL_LOGS.append(
                    f"NIAM: removed {removed} placeholder row(s) replaced by "
                    f"real node rows ---- {timestamp_fn()}"
                )

        if include_all_crs:
            # The workbook was just written from the *newly added* rows only.
            # Rewrite it from every NIAM row for the date so the download keeps
            # the existing rows (and their manual edits) too.
            all_rows = list(
                NIAMTicketGenerationTable.objects.using("default").filter(
                    execution_date=execution_date
                ).values()
            )
            try:
                with file_lock(niam_workbook_path_for(parsed_date)):
                    rebuilt_file = niam_workbook_template_maker(
                        _niam_template_df_from_rows(all_rows),
                        mail_id_df,
                        parsed_date,
                    )
                if rebuilt_file:
                    workbook_file = rebuilt_file
            except Exception as exc:
                GLOBAL_LOGS.append(
                    f"NIAM: could not rebuild the workbook from all rows: {exc} "
                    f"---- {timestamp_fn()}"
                )

        GLOBAL_LOGS.append(
            f"NIAM ticket workbook generated from {used_source}: "
            f"{workbook_file} ---- {timestamp_fn()}"
        )
        if include_all_crs:
            message = (
                f"Added {len(selected_data_df)} NIAM CR(s) with NIAM Ticket "
                f"Required=Yes for {label} ({used_source})."
            )
        else:
            message = f"NIAM ticket generated for {label} ({used_source})."
        return {
            "status": "Completed",
            "download_ready": True,
            "download_name": str(workbook_file),
            "message": message,
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
    if GLOBAL_LOGS is None:
        GLOBAL_LOGS = []
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

    # "Fetch CR" (task id 8, NIAM Template Database page): fetch the selected
    # night's CRs, then add template rows for the CRs flagged
    # "NIAM Ticket Required = Yes". Existing NIAM rows are always kept.
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
            include_all_crs=True,
        )
        gen_result["counts"] = fetch_result.get("counts", {})
        return gen_result

    # Task id 7: strict NIAM Ticket Generation on its own. Only CRs that are
    # planned, require a NIAM ticket, and have a node type/node list produce
    # rows; each CR's blank-node placeholder is replaced by its real node rows.
    if task.get("id") == NIAM_GENERATE_TASK_ID:
        return generate_niam_input(
            selected_date,
            GLOBAL_LOGS=GLOBAL_LOGS,
            timestamp_fn=timestamp_fn,
            runtime=runtime,
        )

    # Any other id must not silently change NIAM data: run the safe strict path
    # and make the unexpected dispatch visible in the task log.
    GLOBAL_LOGS.append(
        f"NIAM: unexpected task id {task.get('id')!r}; running strict "
        f"generation ---- {timestamp_fn()}"
    )
    return generate_niam_input(
        selected_date,
        GLOBAL_LOGS=GLOBAL_LOGS,
        timestamp_fn=timestamp_fn,
        runtime=runtime,
    )
