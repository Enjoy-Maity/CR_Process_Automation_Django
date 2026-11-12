import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue
from threading import Event
from typing import AnyStr, List, Optional, Tuple, Union

import dateutil.parser as dp
import pandas as pd
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from playwright.sync_api import sync_playwright

import dashboard.task_modules.dependencies.batch_methods as cbm
from dashboard.models import NIAMTicketGenerationTable
from dashboard.task_modules.dependencies import playwright_common_methods_ as pcm
from dashboard.task_modules.dependencies.extra_dependencies import (
    NIAM_COLUMN_TO_FIELD_MAPPING,
    NIAM_DATETIME_FIELDS,
    niam_ticket_generation_df_maker,
)
from dashboard.views import _timestamp

glogs = Queue()
queue_ = Queue()
sr_or_change_index = 0
GENERATE_NIAM_TICKET_TASK_ID = 9

# Field name -> display column, used to normalise DB rows before writing the
# RITM Output workbook.
_FIELD_TO_NIAM_COLUMN = {v: k for k, v in NIAM_COLUMN_TO_FIELD_MAPPING.items()}

# The output workbook keeps the same RITM columns as the input template plus
# the raising result columns.
NIAM_OUTPUT_COLUMNS = list(NIAM_COLUMN_TO_FIELD_MAPPING) + ["Failure Reason"]

workbook_path = ""


def get_niam_workbook_path_for(date_: datetime) -> Path:
    """Canonical input-template workbook for a date (written by Fetch CR)."""
    global workbook_path
    return Path(workbook_path).joinpath(
        date_.strftime("%d_%b_%Y"),
        f"RITM Input_PS_Core_{date_.strftime('%d_%b_%Y')}.xlsx",
    )


def get_niam_output_path_for(date_: datetime) -> Path:
    """Result workbook holding the NIAM ticket statuses / failure reasons."""
    global workbook_path
    return Path(workbook_path).joinpath(
        date_.strftime("%d_%b_%Y"),
        f"RITM Output_PS_Core_{date_.strftime('%d_%b_%Y')}.xlsx",
    )


def thread_task(
    index_batch: List[AnyStr],
    df: pd.DataFrame,
    session_file: Union[str, os.PathLike, None] = None,
    headless_var: bool = False,
    ):
    global queue_, sr_or_change_index, glogs

    stop_event = Event()
    session_file = session_file or os.getenv("NIAM_SESSION_FILE")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=headless_var,
            executable_path=pcm.get_browser(),
            timeout=15000
        )

        logs = []

        context = browser.new_context(
            storage_state=str(session_file)
            )
        
        page, logs = pcm.niam_new_page_opener(context, logs)

        try:
            i = 0
            while i < len(index_batch):
                # niam_node_names = []
                # output_dict = {}
                index = index_batch[i]
                cr = df.iloc[index, sr_or_change_index]
                access_type = ""
                try:
                    
                    df_dict = df.iloc[index].to_dict()
                    # output_dict = {
                    #     "Activity Title": str(row_dict["Activity Title"]),
                    #     "Circle": User_Type,
                    #     "Change Responsible": Requested_For_email,
                    #     "Request For": Request_For,
                    #     "Activity Name": NIAM_Activity_Name,
                    #     "Project Name": NIAM_Project_Name,
                    #     "Execution Location": Execution_Location,
                    #     "Execution Date": str(SR_CR_Start_Date_Time)
                    # }
                    # niam_node_names = df_dict["NIAM Node Name"]
                    access_type = str(df_dict.get('Access Type', '') or '').strip()

                    message_string = (
                        f"Working on raising ticket for {df.iloc[index, sr_or_change_index]}"
                    )

                    queue_.put(pcm.niam_tt_raiser(df_dict, page))

                    logs.append(
                        message_string
                    )
                except Exception as e:
                    queue_.put(
                        (
                            cr,
                            # niam_node_names,
                            {(access_type or "Unknown"): "Failure",
                             "Failure Reason": f"{e.__str__().strip()}",
                            },
                            # output_dict
                        )
                    )
                    logs.append(
                        f"Exception occurred ({e.__class__.__name__})!!\n"
                        f"{traceback.format_exc()}\n\n{e}"
                    )
                i += 1
        
        except Exception as e:
            logs.append(
                f"Exception occurred ({e.__class__.__name__})!!\n"
                f"{traceback.format_exc()}\n\n{e}"
            )

        finally:
            if glogs:
                while len(logs) > 0:
                    glogs.put(logs.pop(0))

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


def niam_database_updater(results_list: List[Tuple[str, dict]], _date: datetime = datetime.now()):
    """
    Write the raising results back to NIAMTicketGenerationTable.

    ``results_list`` holds ``(cr, {access_type: status, "Failure Reason": ...})``
    tuples produced by ``thread_task``. A CR may have been raised for more than
    one access type, so every access type in the dict is applied.
    """
    day = _date.date() if isinstance(_date, datetime) else _date

    for cr, access_type_dict in results_list:
        failure_reason = str(access_type_dict.get("Failure Reason", "") or "")

        base = NIAMTicketGenerationTable.objects.using("default").filter(
            sr_or_change_number__iexact=str(cr).strip()
        )
        if day:
            # Scope to this night's rows: they either carry the 22:00 access
            # start of the night, or execute the following day.
            base = base.filter(
                Q(niam_access_start_date_time__date=day)
                | Q(execution_date=day + timedelta(days=1))
            )

        with transaction.atomic():
            for access_type, status in access_type_dict.items():
                if str(access_type).strip().lower() == "failure reason":
                    continue
                access_key = str(access_type).strip()
                if not access_key:
                    continue

                # Match a split ("ADMIN", "READWRITE") row exactly, and also a
                # combined ("ADMIN and READWRITE") row via containment.
                base.filter(
                    Q(access_type__iexact=access_key)
                    | Q(access_type__icontains=access_key)
                ).update(
                    niam_ticket_status=str(status or "").strip(),
                    failure_reason=failure_reason,
                )


def _niam_output_dataframe(_date: datetime) -> pd.DataFrame:
    """DB rows for the night, in RITM column order, with result columns."""
    df = niam_ticket_generation_df_maker(_date=_date)
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame(columns=NIAM_OUTPUT_COLUMNS)

    df = df.rename(columns={"failure_reason": "Failure Reason"})

    # Normalise datetime columns for Excel (aware -> naive IST wall clock,
    # otherwise openpyxl refuses to write timezone-aware values).
    for field_name in NIAM_DATETIME_FIELDS:
        column = _FIELD_TO_NIAM_COLUMN.get(field_name)
        if not column or column not in df.columns:
            continue
        series = pd.to_datetime(df[column], errors="coerce")
        if getattr(series.dt, "tz", None) is not None:
            series = series.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
        df[column] = series

    for column in NIAM_OUTPUT_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[NIAM_OUTPUT_COLUMNS]

    if "SL. No" in df.columns:
        df = df.sort_values(
            "SL. No",
            key=lambda s: pd.to_numeric(s, errors="coerce"),
            na_position="last",
        )
    return df.reset_index(drop=True)


def output_df_maker(_date: datetime = datetime.now()):
    global queue_
    all_results = []
    
    while not queue_.empty():
        all_results.append(queue_.get())

    if all_results:
        niam_database_updater(all_results, _date)

    output_df = _niam_output_dataframe(_date)

    # if all_results:
        
    #     for cr, node_names, access_type_dict, col_dict in all_results:
    #         # Process each result here
    #         for access_type, element in access_type_dict.items():
    #             cr_list.append(cr)
    #             node_names_list.append(node_names)
    #             niam_ticket_status_list.append(element)
    #             access_type_list.append(access_type)
    #             execution_date_list.append((lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').strftime("%d-%b-%Y") if len(x) > 0 else "")(col_dict.get('Execution Date', '')))
    #             circle_list.append(col_dict.get('Circle', ''))
    #             change_responsible_list.append(col_dict.get('Change Responsible', ''))
    #             request_for_list.append(col_dict.get('Request For', ''))
    #             project_name_list.append(col_dict.get('Project Name', ''))
    #             execution_location_list.append(col_dict.get('Execution Location', ''))
            
        
            
    #     output_df = pd.DataFrame(
    #         {   
    #             "S.No": range(1, len(cr_list) + 1),             # A
    #             "Execution Date": execution_date_list,          # B
    #             "CR No": cr_list,                               # C
    #             "Node Names": node_names_list,                  # D
    #             "Access Type": access_type_list,                # E
    #             "NIAM Ticket Status": niam_ticket_status_list,  # F
    #             "Circle": circle_list,                          # G
    #             "Change Responsible": change_responsible_list,  # H
    #             "Request_For": request_for_list,                # I
    #             "Project Name": project_name_list,              # J
    #             "Execution Location": execution_location_list   # K
    #         }
    #     )
    return output_df
    


# def niam_tt_raised_failure_reattempt_row_maker(
#     result_df: pd.DataFrame, 
#     required_input_from_main_input_df: pd.DataFrame,
#     selected_cr_df_from_failed_tt_raised_df: pd.DataFrame
# ) -> pd.DataFrame:
#     selected_cr_failed_tt_raised_df_node_names_column_index = selected_cr_df_from_failed_tt_raised_df.columns.get_loc('Node Names')
#     selected_cr_failed_tt_raised_df_access_type_column_index = selected_cr_df_from_failed_tt_raised_df.columns.get_loc('Access Type')
#     selected_cr_failed_tt_raised_df_request_for_column_index = selected_cr_df_from_failed_tt_raised_df.columns.get_loc('Request For')
    
#     i = 0
#     while i < selected_cr_df_from_failed_tt_raised_df.shape[0]:
                
#         access_type_of_the_selected_row = str(selected_cr_df_from_failed_tt_raised_df.iloc[
#             i, selected_cr_failed_tt_raised_df_access_type_column_index
#         ]).lower()
        
#         request_for_for_selected_row = str(selected_cr_df_from_failed_tt_raised_df.iloc[
#                 i, selected_cr_failed_tt_raised_df_request_for_column_index
#             ])
        
#         selected_input_from_input_df = required_input_from_main_input_df.loc[
#             required_input_from_main_input_df['Access Type'].astype(str).str.lower().str.contains(
#                 access_type_of_the_selected_row
#             )
#         ]
        
#         if selected_input_from_input_df.shape[0] > 0:
#             request_type_filtered_df = selected_input_from_input_df.loc[
#                 selected_input_from_input_df["Request For"].astype(str).str.strip() == request_for_for_selected_row
#             ]
            
#             if request_type_filtered_df.shape[0] > 0:
#                 # Process the filtered data
#                 required_row = request_type_filtered_df.iloc[0].to_dict()

#                 required_row["Access Type"] = access_type_of_the_selected_row.upper()
                
#                 result_df = pd.concat(
#                     [
#                         result_df,
#                         pd.DataFrame([required_row])
#                     ],
#                     ignore_index=True
#                 )
#         i += 1
    
#     return result_df
            

# def output_niam_file_maker(df: pd.DataFrame, _date: datetime, logs: List[AnyStr]=[]):
#     global queue_, workbook_path
#     global flag
#     excel_modifier_obj = None
#     try:
#         niam_ticket_output_excel = get_niam_workbook_path_for(_date)
        
#         color_dict = {
#             "F0D807": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
#         }
        
#         # output_file_check = output_file_checker()
        
#         if output_file_check:
#             output_file_reader = pd.ExcelFile(str(niam_ticket_output_excel), engine="openpyxl")
#             output_excel_df = output_file_reader.parse("RITM Data Table")
#             del output_file_reader
            
#             output_excel_df = output_excel_df.loc[
#                 ~(   
#                     output_excel_df['NIAM Ticket Status'].astype(str).str.strip().str.lower().isin(
#                         [   
#                             'failure',
#                             'failed',
#                             '',
#                             'na',
#                             'nan',
#                             'n/a',
#                             'none'
#                         ]
#                     )
#                 )
#             ]
#             required_columns = list(output_excel_df.columns)
#             # print(f'{required_columns = }')
#             if "S.No" in required_columns:
#                 required_columns.remove("S.No")
#             output_excel_df = output_excel_df[required_columns]
            
#             output_df = output_df_maker()
            
#             list_of_output_df_columns = list(output_df.columns)
#             if "S.No" in list_of_output_df_columns:
#                 list_of_output_df_columns.remove("S.No")
            
#             output_df = output_df[list_of_output_df_columns]
            
#             if output_df.shape[0] > 0 and output_excel_df.shape[0] > 0:
#                 writer = pd.ExcelWriter(niam_ticket_output_excel, engine="openpyxl", mode="w")
                
#                 output_df = pd.concat(
#                     [
#                         output_excel_df,
#                         output_df
#                     ]
#                 )
                
#                 output_df.insert(0, "S.No", range(1, len(output_df) + 1))
#                 output_df.to_excel(writer, sheet_name="RITM Data Table", index=False)
#                 writer.close()
#                 del writer
                
#                 excel_modifier_obj = ExcelModifier(
#                     str(niam_ticket_output_excel),
#                     sheet_name="RITM Data Table"
#                 )
#                 excel_modifier_obj.special_styler(color_dict, True)
#                 # del excel_modifier_obj
            
        
#         else:
#             output_df = output_df_maker()
            
#             if output_df.shape[0] > 0:
#                 writer = pd.ExcelWriter(niam_ticket_output_excel, engine="openpyxl", mode="w")
#                 output_df.to_excel(writer, sheet_name="RITM Data Table", index=False)
#                 writer.close()
#                 del writer
                
#                 excel_modifier_obj = ExcelModifier(
#                     str(niam_ticket_output_excel),
#                     sheet_name="RITM Data Table"
#                 )
#                 excel_modifier_obj.special_styler(color_dict, True)
#                 # del excel_modifier_obj
        
#         if excel_modifier_obj:
#             max_row = excel_modifier_obj.total_rows
#             column_value = excel_modifier_obj.column_index("NIAM Ticket Status")
#             for row in range(excel_modifier_obj.header_row+1, max_row+1):
#                 # cell_value = str(excel_modifier_obj.get_data(row, column_value)).strip().lower()
#                 cell_value = str(excel_modifier_obj.get_data(row, "NIAM Ticket Status")).strip().lower()
#                 # print(cell_value)
#                 if cell_value in [
#                     'failure',
#                     'failed',
#                     '',
#                     'na',
#                     'nan',
#                     'n/a',
#                     'none']:
#                     excel_modifier_obj.colorizer_based_on_cell_value(row, column_value, "FF0000")
            
#             excel_modifier_obj.save()
#             del excel_modifier_obj
    
#     except Exception as e:
#         flag = "Unsuccessful"
        
#         if manager:
#             manager.show_info_signal.emit(
#                 f"{e.__title__()}",
#                 f"{traceback.format_exc()}\n\n{e}",
#                 "error"
#             )
#         else:
#             messagebox = Messagebox()
            
#             messagebox.showerror(
#                 f"{e.__title__()}",
#                 f"{traceback.format_exc()}\n\n{e}"
#             )


def output_file_checker(_date: Optional[datetime] = None) -> bool:
    """True when this date's RITM Output workbook has already been written."""
    return get_niam_output_path_for(_date or datetime.now()).exists()


def niam_ticket_raise_using_thread(
    df: pd.DataFrame,
    user_name: str,
    _date: datetime,
    logs: Optional[List[AnyStr]] = None,
    headless_mode: bool = False,
    session_file: Union[str, os.PathLike, None] = None,
    runtime: Optional[dict] = None,
    task: Optional[dict] = None,
    timestamp_fn=None,
) -> List[AnyStr]:
    """Raise the NIAM tickets for ``df``, with one browser batch per thread."""
    global glogs, sr_or_change_index

    logs = logs if logs is not None else []
    timestamp_fn = timestamp_fn or _timestamp

    if df is None or df.shape[0] == 0:
        logs.append("No NIAM rows need a ticket; nothing to raise.")
        return output_niam_file_maker(_date, logs)

    # Resolve the CR column by name; the DB-derived frame's column order differs
    # from the old hard-coded workbook layout.
    if "SR OR CHANGE NO" in df.columns:
        sr_or_change_index = df.columns.get_loc("SR OR CHANGE NO")

    batch_creation_success, batches, logs = cbm.main_method(df.shape[0], logs)
    if not batch_creation_success or not batches:
        logs.append("Could not create NIAM batches; nothing was raised.")
        return output_niam_file_maker(_date, logs)

    logs.append(f"Created {len(batches)} batches from {df.shape[0]} NIAM TT Entries")

    session_path = session_file or os.getenv("NIAM_SESSION_FILE")
    if not session_path:
        raise RuntimeError(
            "NIAM session file path is not configured. Set NIAM_SESSION_FILE or "
            "run the task from the dashboard."
        )

    # A login can legitimately fail (bad/expired credentials, MFA not approved).
    # Retry a couple of times, then fail the task instead of looping forever.
    session_created = False
    last_error = ""
    for attempt in range(3):
        if attempt:
            logs.append(
                f"Retrying NIAM login ({attempt + 1}/3) ---- {timestamp_fn()}"
            )
        attempt_start = len(logs)
        session_created, created_file, logs = pcm.niam_session_maker(
            user_name,
            logs,
            session_file=session_path,
            runtime=runtime,
            task=task,
            timestamp_fn=timestamp_fn,
        )
        if session_created:
            session_path = str(created_file or session_path)
            break

        # Keep the first line of the latest exception so the final error tells
        # the user why login failed instead of only saying "Could not log in".
        fatal_login_error = False
        for entry in reversed(logs[attempt_start:]):
            text = str(entry or "").strip()
            if (
                "Could not load NIAM credentials" in text
                or "NiamAuthenticationError" in text
                or "NiamCredentialsError" in text
            ):
                fatal_login_error = True
            if "Exception Occurred" in text or "Could not load NIAM" in text:
                last_error = text.splitlines()[0].strip()
                break
        if fatal_login_error:
            # Wrong/missing credentials will not fix themselves on retry.
            break

    if not session_created:
        # Do not leave the sign-in notice iframe open after a failed login.
        try:
            pcm.clear_user_notice(runtime, status=None)
        except Exception:
            pass
        # The login helpers normally raise an alert themselves. Only add a
        # fallback when nothing was surfaced (e.g. an unexpected early return).
        if runtime is not None and not runtime.get("alert_required"):
            try:
                pcm.show_user_alert(
                    runtime,
                    task,
                    logs,
                    timestamp_fn,
                    title="NIAM login failed",
                    text=(
                        "Could not log in to NIAM. Check the NIAM OLM ID / "
                        "password saved in NIAM Credentials and try again."
                        + (f"\n\nDetails: {last_error}" if last_error else "")
                    ),
                )
            except Exception:
                pass
        detail = f" Last error: {last_error}" if last_error else ""
        raise RuntimeError(
            "Could not log in to NIAM. Check the NIAM OLM ID / password saved on "
            f"the user profile.{detail}"
        )

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(thread_task, batch, df, session_path, headless_mode)
            for batch in batches
        ]
        for future in futures:
            future.result()

    try:
        pcm.niam_session_breaker(session_file=session_path)
    except Exception:
        logs.append(
            "Could not close the NIAM session cleanly.\n"
            f"{traceback.format_exc()}"
        )

    if glogs:
        while not glogs.empty():
            logs.append(glogs.get())

    return output_niam_file_maker(_date, logs)


# def niam_ticket_raiser(df: pd.DataFrame, user_name: str, _date: datetime, logs: List[AnyStr] = [], headless_mode: bool = False) -> List[AnyStr]:
    
#     # global request_type_index
#     # global node_managed_by_index
#     # global subtype_index
#     # global uid_type_index
#     # global policy_period_index
#     # global user_type_index
#     # global request_ip_greater_than_10_index
#     # global business_justification_index
#     # global sr_cr_start_date_time_index
#     # global sr_cr_end_date_time_index
#     # global niam_access_start_date_index
#     # global niam_access_end_date_index
#     # global execution_location_index
#     global sr_or_change_index
#     # global activity_title_index
#     # global niam_node_name_index
#     # global requested_for_email_index
#     # global activity_name_index
#     # global project_name_index
#     # global request_for_index
#     # global domain_index
#     # global access_type_index
    
#     # crs = df['SR OR CHANGE NO'].astype(str).str.strip().tolist()
#     # sr_nos = df['SL. No'].astype(str).str.strip().astype(float).astype(int).astype(str).tolist()
    
#     # request_type_index = df.columns.get_loc('Request Type')
#     # node_managed_by_index = df.columns.get_loc('Node Managed By')
#     # subtype_index = df.columns.get_loc('Subtype')
#     # uid_type_index = df.columns.get_Loc('UID Type')
#     # policy_period_index = df.columns.get_loc('Policy period')
#     # user_type_index = df.columns.get_loc('User Type')
#     # request_ip_greater_than_10_index = df.columns.get_loc('Request IP>10 ?')
#     # business_justification_index = df.columns.get_loc('Business Justification')
#     # sr_cr_start_date_time_index = df.columns.get_loc('SR_CR_Start Date-Time')
#     # sr_cr_start_date_time_index = df.columns.get_loc('SR_CR_End Date-Time')
#     # niam_access_start_date_index = df.columns.get_loc('NIAM Access Start Date')
#     # niam_access_end_date_index = df.columns.get_loc('NIAM Access End Date')
#     # execution_location_index = df.columns.get_loc('Execution Location')
#     sr_or_change_index = df.columns.get_loc('SR OR CHANGE NO')
#     # activity_title_index = df.columns.get_loc('Activity Title')
#     # niam_node_name_index = df.columns.get_loc('NIAM Node Name')
#     # requested_for_email_index = df.columns.get_loc('Requested For(email)')
#     # activity_name_index = df.columns.get_loc('Activity Name')
#     # project_name_index = df.columns.get_loc('Project Name')
#     # request_for_index = df.columns.get_loc('Request For')
#     # domain_index = df.columns.get_loc('Domain')
#     # access_type_index = df.columns.get_loc('Access Type')
    
#     output_file_check = output_file_checker()
    
#     if output_file_check:
#         niam_ticket_output_excel = niam_workbook_path_for(_date)
        
#         output_file_reader = pd.ExcelFile(str(niam_ticket_output_excel), engine="openpyxl")
#         output_excel_df = output_file_reader.parse("RITM Data Table")
#         del output_file_reader
        
#         failed_raised_tt_df = output_excel_df.loc[
#             output_excel_df["NIAM Ticket Status"].astype(str).str.strip().str.lower().isin(
#                 [   
#                     'failure',
#                     'failed',
#                     '',
#                     'na',
#                     'nan',
#                     'n/a',
#                     'none'
#                 ]
#             )
#         ]
        
#         # print(f"From OutPut Excel failed_raised_tt_df.to_markdown()\n{failed_raised_tt_df[["S.No", "CR No", "Access Type"]]}")
        
#         new_cr_entry_df = df.loc[
#             ~(
#                 df['SR OR CHANGE NO'].astype(str).str.strip().str.lower().isin(
#                     np.append(
#                         output_excel_df['CR No'].astype(str).str.strip().str.lower().unique(),
#                         np.array([
#                             'nan',
#                             'na',
#                             'none',
#                             ''
#                         ])
#                     )
#                 )
#             )
#         ]
#         required_columns = list(df.columns)
#         required_columns.remove("SL. No")
#         result_df = pd.DataFrame(columns=required_columns)
        
#         if failed_raised_tt_df.shape[0] > 0:         
#             failed_filter_df_intersection_main_df = df.loc[
#                 df['SR OR CHANGE NO'].astype(str).str.strip().str.lower().isin(
#                     failed_raised_tt_df['CR No'].astype(str).str.strip().str.lower().unique().tolist()
#                 )
#             ]
#             # print(
#             #     f"failed_filter_df_intersection_main_df.to_markdown()\n{failed_filter_df_intersection_main_df[["SL. No", "SR OR CHANGE NO", "Access Type"]]}"
#             # )
            
#             # Remove SL. No column from failed_filter_df_intersection_main_df
#             required_columns = list(failed_filter_df_intersection_main_df.columns)
#             required_columns.remove("SL. No")
#             failed_filter_df_intersection_main_df = failed_filter_df_intersection_main_df[
#                 required_columns
#             ]
            
#             for cr in failed_filter_df_intersection_main_df['SR OR CHANGE NO'].astype(str).str.strip().unique():
#                 # print(f"\n{cr = }")
#                 # Add logic to handle failed CRs here
#                 selected_cr_df_from_failed_tt_raised_df = failed_raised_tt_df.loc[
#                     failed_raised_tt_df['CR No'].astype(str).str.strip() == cr
#                 ]
                
#                 # print(f"\nselected_cr_df_from_failed_tt_raised_df\n{selected_cr_df_from_failed_tt_raised_df[["S.No", "CR No", "Access Type"]]}")
                
#                 unique_access_types_in_failed_raised_tt_df = selected_cr_df_from_failed_tt_raised_df['Access Type'].astype(str).str.strip().str.lower().unique()
                
#                 required_input_from_main_input_df = df.loc[
#                         (
#                             df['SR OR CHANGE NO'].astype(str).str.strip() == cr
#                         )
#                     ]
                
#                 # print(f"\nrequired_input_from_main_input_df\n{required_input_from_main_input_df[['SR OR CHANGE NO', 'NIAM Node Name', 'Access Type']]}")
                
#                 if required_input_from_main_input_df.shape[0] > 0 and selected_cr_df_from_failed_tt_raised_df.shape[0] > 0:
#                     result_df = niam_tt_raised_failure_reattempt_row_maker(
#                         result_df,
#                         required_input_from_main_input_df,
#                         selected_cr_df_from_failed_tt_raised_df
#                     )
                
#                 # unique_access_type_in_main_input_df = required_input_from_main_input_df[
#                 #     'Access Type'
#                 # ].astype(str).str.strip().str.lower().unique()
                
#                 # print(f"\nunique_access_type_in_main_input_df\n{list(unique_access_type_in_main_input_df)}")
                
#                 # if len(unique_access_type_in_main_input_df) > 0:
#                 #     temp_var= list(unique_access_type_in_main_input_df)[0].split('and')
#                 #     print(f"\ntemp_var\n{temp_var}")
#                 #     unique_access_intersection = set(temp_var).intersection(unique_access_types_in_failed_raised_tt_df)
                    
#                 #     print(f"\nunique_access_intersection\n{unique_access_intersection}")
#                 #     if len(unique_access_intersection) > 0:
#                 #         for selected_access_type in unique_access_intersection:
#                 #             # Add logic to handle each access type here
                            
#                 #             required_row = required_input_from_main_input_df.loc[
#                 #                 required_input_from_main_input_df['SR OR CHANGE NO'].astype(str).str.strip() == cr
#                 #             ].iloc[0].to_dict()
                            
#                 #             required_row["Access Type"] = selected_access_type
                            
#                 #             result_df = pd.concat(
#                 #                 [
#                 #                     result_df,
#                 #                     pd.DataFrame([required_row])
#                 #                 ],
#                 #                 ignore_index=True
#                 #             )    
            
#         if new_cr_entry_df.shape[0] > 0:
#             required_columns = list(new_cr_entry_df.columns)
#             required_columns.remove("SL. No")
#             # print(f"{list(new_cr_entry_df.columns) = }")
#             # print(f"{required_columns = }")
#             new_cr_entry_df = new_cr_entry_df[
#                 required_columns
#             ]
            
#             result_df = pd.concat(
#                 [
#                     result_df,
#                     new_cr_entry_df
#                 ]
#             )
#         if "SL. No" in result_df.columns:
#             required_columns = list(result_df.columns)
#             required_columns.remove("SL. No")
#             result_df = result_df[required_columns]
            
#         result_df.insert(0, "SL. No", range(1, len(result_df) + 1))
        
#         result_df["Access Type"] = result_df["Access Type"].astype(str).str.strip().str.upper()
        
#         # print(f"result_df\n{result_df[["SL. No", "SR OR CHANGE NO", "Access Type"]]}")
        
#         logs = niam_ticket_raise_using_thread(result_df, user_name, logs, headless_mode)        
    
#     elif df.shape[0] > 0:
#         logs = niam_ticket_raise_using_thread(df, user_name, logs, headless_mode)

#     df = niam_ticket_generation_df_maker(_date)
#     df = df[df['NIAM Ticket Status'].astype(str).str.strip().str.lower().isin(
#         [
#             'failure',
#             'failed',
#             '',
#             'na',
#             'nan',
#             'n/a',
#             'none'
#         ]
#     )]
#       
#    output_niam_file_maker()


# def pre_checks(_date: datetime, logs: List[AnyStr]=[]) -> Tuple[bool, Union[pd.DataFrame, None]]:
#     global workbook_path, flag
    
#     niam_input_workbook_path = get_niam_workbook_path_for(_date)
#     # print(f"NIAM Input Workbook Path: {niam_input_workbook_path}")
#     # print(f"{niam_input_workbook_path.exists() = }")
#     if not niam_input_workbook_path.exists():
#         flag = "Unsuccessful"
#         logs.append(
#             "NIAM Input Excel file not found",
#         )
        
#         logs.append(
#                 "NIAM File not found",
#                 "error"
#             )
        
            
#         return False, None, logs
    
#     else:
#         excel_file = pd.ExcelFile(str(niam_input_workbook_path), engine='openpyxl')
#         if "RITM_INPUT" not in excel_file.sheet_names:
#             flag = "Unsuccessful"
            
#             excel_file.close()
#             del excel_file
            
#             logs.append(
#                     "Worksheet named 'RITM_INPUT' not found in the 'NIAM Input_PS_Core' Workbook"
#             )
                
#             if manager:
#                 manager.show_info_signal.emit(
#                     "Worksheet Not Found",
#                     "Worksheet named 'RITM_INPUT' not found in the 'NIAM Input_PS_Core' Workbook",
#                     "error"
#                 )
            
#             return False, None, logs
        
#         else:
#             niam_input_file_df = excel_file.parse("RITM_INPUT")
#             excel_file.close()
#             del excel_file
            
#             if niam_input_file_df.shape[0] > 0:                
#                 return True, niam_input_file_df
            
#             else:
#                 flag = "Unsuccessful"
                
#                 if live_feed:
#                     live_feed.emit(
#                         "Worksheet Data for 'NIAM Input_PS_Core' Workbook is empty"
#                     )
                    
#                 if manager:
#                     manager.show_info_signal.emit(
#                         "NIAM Input Data Not Missing",
#                         "Worksheet Data for 'NIAM Input_PS_Core' Workbook is empty",
#                         "error"
#                     )
                
#                 else:
#                     messagebox = Messagebox()
#                     messagebox.showerror(
#                         "NIAM Input Data Not Missing",
#                         "Worksheet Data for 'NIAM Input_PS_Core' Workbook is empty",
#                     )
                
#                 return False, None


# def niam_input_file_maker(result_df: pd.DataFrame, _date: datetime, logs: List[AnyStr]=[]):
#     niam_workbook_path = get_niam_workbook_path_for(_date)


def output_niam_file_maker(
    _date: datetime, logs: Optional[List[AnyStr]] = None
) -> List[AnyStr]:
    """
    Write the NIAM ticket results to this date's RITM Output workbook.

    The input template (RITM Input) is never overwritten: the output workbook
    is a separate file next to it, containing the same RITM rows plus the
    raising status and failure reason.

    :param _date: The (night) date for which the results are generated.
    :param logs: A list of logs to append to.
    :return: A list of logs.
    """
    logs = logs if logs is not None else []

    df = output_df_maker(_date)
    output_path = get_niam_output_path_for(_date)

    if df.shape[0] > 0:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(str(output_path), sheet_name="RITM Data Table", index=False)
        logs.append(
            f"NIAM ticket result workbook saved and ready for download: "
            f"{output_path.name}"
        )
    else:
        logs.append(
            "NIAM ticket result workbook was not saved because it has no rows."
        )

    return logs


def pre_checks(
    _date: datetime, logs: Optional[List[AnyStr]] = None
) -> Tuple[bool, Union[pd.DataFrame, None], List[AnyStr]]:
    """
    Load this night's NIAM rows and keep only the ones still needing a ticket.

    A row needs raising when its NIAM Ticket Status is empty or a previous
    failure. Successful rows (which carry the raised RITM number) are skipped.
    """
    logs = logs if logs is not None else []

    result_df = niam_ticket_generation_df_maker(_date=_date)

    if not isinstance(result_df, pd.DataFrame):
        logs.append("NIAM Ticket Generation: no dataframe returned from the database.")
        return False, None, logs

    logs.append(f"NIAM Ticket Generation DataFrame Shape: {result_df.shape}")
    if result_df.empty:
        return True, result_df, logs

    if "NIAM Ticket Status" not in result_df.columns:
        logs.append(
            "NIAM Ticket Generation: the rows have no 'NIAM Ticket Status' column."
        )
        return False, None, logs

    status = (
        result_df["NIAM Ticket Status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )
    needs_ticket = status.isna() | status.isin(
        ["failure", "failed", "", "na", "nan", "n/a", "none"]
    )
    pending_df = result_df[needs_ticket].reset_index(drop=True)
    logs.append(
        f"NIAM Ticket Generation: {pending_df.shape[0]} of "
        f"{result_df.shape[0]} row(s) still need a ticket."
    )
    return True, pending_df, logs




def _parse_selected_date(value) -> datetime:
    """Accept the dashboard's YYYY-MM-DD string, a date or a datetime."""
    if value is None or value == "":
        return datetime.now()
    if isinstance(value, datetime):
        return value
    try:
        return dp.parse(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid date format: {value}") from exc


def run_task(
    request,
    task,
    runtime,
    GLOBAL_LOGS=None,
    timestamp_fn=None,
    selected_date=None,
    user_email=None,
    user_name=None,
    regions=None,
):
    """
    Raise the NIAM tickets for the selected night (task 9).

    ``selected_date`` is the page's night date: the NIAM access window starts at
    22:00 that night and the CRs execute the following day. The task updates
    NIAMTicketGenerationTable with each row's RITM number / failure reason and
    writes ``RITM Output_PS_Core_<night>.xlsx`` for download.
    """
    global glogs, sr_or_change_index, queue_, workbook_path

    logs = GLOBAL_LOGS if GLOBAL_LOGS is not None else []
    # Respect the dashboard's timestamp helper when one is supplied.
    timestamp_fn = timestamp_fn or _timestamp
    task = task or {}
    runtime = runtime if runtime is not None else {}

    runtime["status"] = "Running"
    runtime["download_ready"] = False

    runtime["password_required"] = False
    runtime["password"] = None
    runtime["pwd_event"] = None

    runtime["otp_required"] = False
    runtime["otp"] = None
    runtime["otp_event"] = Event()

    # Read-only notice shown during the Microsoft Authenticator sign-in.
    runtime["notice_required"] = False
    runtime["notice_text"] = ""

    # Blocking alert dialog (missing/wrong NIAM credentials).
    runtime["alert_required"] = False
    runtime["alert_title"] = ""
    runtime["alert_text"] = ""
    runtime["alert_seq"] = 0

    queue_ = Queue()
    glogs = Queue()
    sr_or_change_index = 0
    workbook_path = os.path.join(settings.HOST_DOWNLOAD_DIR, "NIAM_Excel_files")
    night = _parse_selected_date(selected_date)

    # Each run gets its own NIAM browser session storage file so concurrent
    # users never overwrite each other's cookies.
    session_dir = Path(settings.MEDIA_ROOT) / "niam_sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    run_key = runtime.get("run_key") or datetime.now().strftime("%Y%m%d%H%M%S")
    session_file = session_dir / f"niam_session_{run_key}.json"
    os.environ["NIAM_SESSION_FILE"] = str(session_file)

    if task.get("id") != GENERATE_NIAM_TICKET_TASK_ID:
        return {
            "status": "Completed",
            "download_ready": False,
            "message": "Nothing to do for this task id.",
        }

    # NIAM credentials are stored against the Django username.
    niam_user = getattr(getattr(request, "user", None), "username", None) or user_name
    execution_day = night + timedelta(days=1)
    logs.append(
        f"Raising NIAM tickets for the night of {night:%d-%m-%Y} "
        f"(CRs execute {execution_day:%d-%m-%Y})."
    )

    success, result_df, logs = pre_checks(night, logs)

    if success and result_df is not None and result_df.shape[0] > 0:
        logs = niam_ticket_raise_using_thread(
            result_df,
            niam_user,
            night,
            logs,
            False,
            session_file=str(session_file),
            runtime=runtime,
            task=task,
            timestamp_fn=timestamp_fn,
        )
        message = (
            f"NIAM ticket raising finished for {result_df.shape[0]} row(s). "
            "Download the RITM Output workbook."
        )
    else:
        logs.append("No NIAM rows need a ticket; exporting the current statuses.")
        logs = output_niam_file_maker(night, logs)
        message = "No NIAM rows needed a ticket; the current statuses were exported."

    output_path = get_niam_output_path_for(night)
    download_ready = output_path.is_file()

    if download_ready:
        logs.append(f"Output workbook ready: {output_path}")
    else:
        logs.append("No output workbook was produced for this run.")

    return {
        "status": "Completed",
        "download_ready": download_ready,
        "download_name": str(output_path) if download_ready else "",
        "message": message,
    }
