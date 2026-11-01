import os
import traceback
import pandas as pd
import numpy as np
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from playwright.sync_api import sync_playwright
from django.conf import settings
from django.db import transaction
from typing import List, AnyStr, Optional
from dashboard.task_modules.dependencies import playwright_common_methods_ as pcm
from dashboard.models import UserManagement, NIAMTicketGenerationTable
from dashboard.views import _timestamp


glogs = []
queue_ = Queue()
sr_or_change_index = None
GENERATE_NIAM_TICKET_TASK_ID = 9

def thread_task(
    index_batch: List[AnyStr], 
    df: pd.DataFrame,
    headless_var: bool = true
    ):
    global queue_, sr_or_change_index

    stop_event = Event()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=headless_var,
            executable_path=pcm.get_browser(),
            timeout=15000
        )

        logs = []

        context = browser.new_context(
            storage_state=str(os.getenv("NIAM_SESSION_FILE"))
            )
        
        logs, page = pcm.niam_new_page_opener(context, logs)

        try:
            i = 0
            while i < len(index_batch):
                niam_node_names = []
                output_dict = {}
                index = index_batch[i]
                cr = df.iloc[index, sr_or_change_index]
                try:
                    
                    df_dict = df.iloc[index].to_dict()
                    output_dict = {
                        "Activity Title": str(row_dict["Activity Title"]),
                        "Circle": User_Type,
                        "Change Responsible": Requested_For_email,
                        "Request For": Request_For,
                        "Activity Name": NIAM_Activity_Name,
                        "Project Name": NIAM_Project_Name,
                        "Execution Location": Execution_Location,
                        "Execution Date": str(SR_CR_Start_Date_Time)
                    }
                    niam_node_names = df_dict["NIAM Node Name"]

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
                            niam_node_names,
                            {},
                            output_dict
                        )
                    )
                    logs.append(
                        f"Exception occurred ({e.__class__.__name__})!!",
                        f"{traceback.format_exc()}\n\n{e}",
                        "error",
                    )
                i += 1
        
        except Exception as e:
            logs.append(
                f"Exception occurred ({e.__class__.__name__})!!",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )

        finally:
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


def output_df_maker():
    global queue_
    all_results = []
            
    while not queue_.empty():
        all_results.append(queue_.get())
    
    output_df = pd.DataFrame()
        
    if all_results:
        cr_list = []
        node_names_list = []
        access_type_list = []
        execution_date_list = []
        niam_ticket_status_list = []
        circle_list = []
        change_responsible_list = []
        request_for_list = []
        project_name_list = []
        execution_location_list = []
        node_names_list = []
        
        for cr, node_names, access_type_dict, col_dict in all_results:
            
            # Process each result here
            for access_type, element in access_type_dict.items():
                cr_list.append(cr)
                node_names_list.append(node_names)
                niam_ticket_status_list.append(element)
                access_type_list.append(access_type)
                execution_date_list.append((lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').strftime("%d-%b-%Y") if len(x) > 0 else "")(col_dict.get('Execution Date', '')))
                circle_list.append(col_dict.get('Circle', ''))
                change_responsible_list.append(col_dict.get('Change Responsible', ''))
                request_for_list.append(col_dict.get('Request For', ''))
                project_name_list.append(col_dict.get('Project Name', ''))
                execution_location_list.append(col_dict.get('Execution Location', ''))
        
            
        output_df = pd.DataFrame(
            {   
                "S.No": range(1, len(cr_list) + 1),             # A
                "Execution Date": execution_date_list,          # B
                "CR No": cr_list,                               # C
                "Node Names": node_names_list,                  # D
                "Access Type": access_type_list,                # E
                "NIAM Ticket Status": niam_ticket_status_list,  # F
                "Circle": circle_list,                          # G
                "Change Responsible": change_responsible_list,  # H
                "Request_For": request_for_list,                # I
                "Project Name": project_name_list,              # J
                "Execution Location": execution_location_list   # K
            }
        )
    
    return output_df


def niam_tt_raised_failure_reattempt_row_maker(
    result_df: pd.DataFrame, 
    required_input_from_main_input_df: pd.DataFrame,
    selected_cr_df_from_failed_tt_raised_df: pd.DataFrame
) -> pd.DataFrame:
    selected_cr_failed_tt_raised_df_node_names_column_index = selected_cr_df_from_failed_tt_raised_df.columns.get_loc('Node Names')
    selected_cr_failed_tt_raised_df_access_type_column_index = selected_cr_df_from_failed_tt_raised_df.columns.get_loc('Access Type')
    selected_cr_failed_tt_raised_df_request_for_column_index = selected_cr_df_from_failed_tt_raised_df.columns.get_loc('Request For')
    
    i = 0
    while i < selected_cr_df_from_failed_tt_raised_df.shape[0]:
                
        access_type_of_the_selected_row = str(selected_cr_df_from_failed_tt_raised_df.iloc[
            i, selected_cr_failed_tt_raised_df_access_type_column_index
        ]).lower()
        
        request_for_for_selected_row = str(selected_cr_df_from_failed_tt_raised_df.iloc[
                i, selected_cr_failed_tt_raised_df_request_for_column_index
            ])
        
        selected_input_from_input_df = required_input_from_main_input_df.loc[
            required_input_from_main_input_df['Access Type'].astype(str).str.lower().str.contains(
                access_type_of_the_selected_row
            )
        ]
        
        if selected_input_from_input_df.shape[0] > 0:
            request_type_filtered_df = selected_input_from_input_df.loc[
                selected_input_from_input_df["Request For"].astype(str).str.strip() == request_for_for_selected_row
            ]
            
            if request_type_filtered_df.shape[0] > 0:
                # Process the filtered data
                required_row = request_type_filtered_df.iloc[0].to_dict()

                required_row["Access Type"] = access_type_of_the_selected_row.upper()
                
                result_df = pd.concat(
                    [
                        result_df,
                        pd.DataFrame([required_row])
                    ],
                    ignore_index=True
                )
        i += 1
    
    return result_df
            

def output_niam_file_maker():
    global live_feed, manager, queue_, workbook_path
    global flag
    excel_modifier_obj = None
    try:
        niam_ticket_output_excel = Path(
            workbook_path
        ).parent.joinpath(
            "NIAM_Excel_files",
            datetime.now().strftime("%d_%b_%Y"),
            f"RITM Output_PS_Core_{datetime.now().strftime('%d_%b_%Y')}.xlsx"
        )
        
        color_dict = {
            "F0D807": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
        }
        
        output_file_check = output_file_checker()
        
        if output_file_check:
            output_file_reader = pd.ExcelFile(str(niam_ticket_output_excel), engine="openpyxl")
            output_excel_df = output_file_reader.parse("RITM Data Table")
            del output_file_reader
            
            output_excel_df = output_excel_df.loc[
                ~(   
                    output_excel_df['NIAM Ticket Status'].astype(str).str.strip().str.lower().isin(
                        [   
                            'failure',
                            'failed',
                            '',
                            'na',
                            'nan',
                            'n/a',
                            'none'
                        ]
                    )
                )
            ]
            required_columns = list(output_excel_df.columns)
            # print(f'{required_columns = }')
            if "S.No" in required_columns:
                required_columns.remove("S.No")
            output_excel_df = output_excel_df[required_columns]
            
            output_df = output_df_maker()
            
            list_of_output_df_columns = list(output_df.columns)
            if "S.No" in list_of_output_df_columns:
                list_of_output_df_columns.remove("S.No")
            
            output_df = output_df[list_of_output_df_columns]
            
            if output_df.shape[0] > 0 and output_excel_df.shape[0] > 0:
                writer = pd.ExcelWriter(niam_ticket_output_excel, engine="openpyxl", mode="w")
                
                output_df = pd.concat(
                    [
                        output_excel_df,
                        output_df
                    ]
                )
                
                output_df.insert(0, "S.No", range(1, len(output_df) + 1))
                output_df.to_excel(writer, sheet_name="RITM Data Table", index=False)
                writer.close()
                del writer
                
                excel_modifier_obj = ExcelModifier(
                    str(niam_ticket_output_excel),
                    sheet_name="RITM Data Table"
                )
                excel_modifier_obj.special_styler(color_dict, True)
                # del excel_modifier_obj
            
        
        else:
            output_df = output_df_maker()
            
            if output_df.shape[0] > 0:
                writer = pd.ExcelWriter(niam_ticket_output_excel, engine="openpyxl", mode="w")
                output_df.to_excel(writer, sheet_name="RITM Data Table", index=False)
                writer.close()
                del writer
                
                excel_modifier_obj = ExcelModifier(
                    str(niam_ticket_output_excel),
                    sheet_name="RITM Data Table"
                )
                excel_modifier_obj.special_styler(color_dict, True)
                # del excel_modifier_obj
        
        if excel_modifier_obj:
            max_row = excel_modifier_obj.total_rows
            column_value = excel_modifier_obj.column_index("NIAM Ticket Status")
            for row in range(excel_modifier_obj.header_row+1, max_row+1):
                # cell_value = str(excel_modifier_obj.get_data(row, column_value)).strip().lower()
                cell_value = str(excel_modifier_obj.get_data(row, "NIAM Ticket Status")).strip().lower()
                # print(cell_value)
                if cell_value in [
                    'failure',
                    'failed',
                    '',
                    'na',
                    'nan',
                    'n/a',
                    'none']:
                    excel_modifier_obj.colorizer_based_on_cell_value(row, column_value, "FF0000")
            
            excel_modifier_obj.save()
            del excel_modifier_obj
    
    except Exception as e:
        flag = "Unsuccessful"
        
        if manager:
            manager.show_info_signal.emit(
                f"{e.__title__()}",
                f"{traceback.format_exc()}\n\n{e}",
                "error"
            )
        else:
            messagebox = Messagebox()
            
            messagebox.showerror(
                f"{e.__title__()}",
                f"{traceback.format_exc()}\n\n{e}"
            )


def output_file_checker():
    global workbook_path
    
    niam_ticket_output_excel = Path(
            workbook_path
        ).parent.joinpath(
            "NIAM_Excel_files",
            datetime.now().strftime("%d_%b_%Y"),
            f"RITM Output_PS_Core_{datetime.now().strftime('%d_%b_%Y')}.xlsx"
        )
    # print(f"{niam_ticket_output_excel.exists() =}")
    return niam_ticket_output_excel.exists()


def niam_ticket_raise_using_thread(df: pd.DataFrame):
    batch_creation_success, batches = cbm.main_method(
                    manager, live_feed, df.shape[0]
                )

    if batch_creation_success:
        if live_feed:
            live_feed.emit(
                orange_text(
                    f"Created {len(batches)} batches from {df.shape[0]} NIAM TT Entries"
                )
            )
    
        session_created = None
        # print(batches)

        while not session_created:
            session_created, session_file = pcm.niam_session_maker(manager, live_feed)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(
                    thread_task, batch, df
                )
                for batch in batches
            ]

            for future in futures:
                future.result()
        
        pcm.niam_session_breaker(manager, live_feed)


def niam_ticket_raiser(df: pd.DataFrame):
    global flag
    global manager, live_feed
    
    # global request_type_index
    # global node_managed_by_index
    # global subtype_index
    # global uid_type_index
    # global policy_period_index
    # global user_type_index
    # global request_ip_greater_than_10_index
    # global business_justification_index
    # global sr_cr_start_date_time_index
    # global sr_cr_end_date_time_index
    # global niam_access_start_date_index
    # global niam_access_end_date_index
    # global execution_location_index
    global sr_or_change_index
    # global activity_title_index
    # global niam_node_name_index
    # global requested_for_email_index
    # global activity_name_index
    # global project_name_index
    # global request_for_index
    # global domain_index
    # global access_type_index
    
    # crs = df['SR OR CHANGE NO'].astype(str).str.strip().tolist()
    # sr_nos = df['SL. No'].astype(str).str.strip().astype(float).astype(int).astype(str).tolist()
    
    # request_type_index = df.columns.get_loc('Request Type')
    # node_managed_by_index = df.columns.get_loc('Node Managed By')
    # subtype_index = df.columns.get_loc('Subtype')
    # uid_type_index = df.columns.get_Loc('UID Type')
    # policy_period_index = df.columns.get_loc('Policy period')
    # user_type_index = df.columns.get_loc('User Type')
    # request_ip_greater_than_10_index = df.columns.get_loc('Request IP>10 ?')
    # business_justification_index = df.columns.get_loc('Business Justification')
    # sr_cr_start_date_time_index = df.columns.get_loc('SR_CR_Start Date-Time')
    # sr_cr_start_date_time_index = df.columns.get_loc('SR_CR_End Date-Time')
    # niam_access_start_date_index = df.columns.get_loc('NIAM Access Start Date')
    # niam_access_end_date_index = df.columns.get_loc('NIAM Access End Date')
    # execution_location_index = df.columns.get_loc('Execution Location')
    sr_or_change_index = df.columns.get_loc('SR OR CHANGE NO')
    # activity_title_index = df.columns.get_loc('Activity Title')
    # niam_node_name_index = df.columns.get_loc('NIAM Node Name')
    # requested_for_email_index = df.columns.get_loc('Requested For(email)')
    # activity_name_index = df.columns.get_loc('Activity Name')
    # project_name_index = df.columns.get_loc('Project Name')
    # request_for_index = df.columns.get_loc('Request For')
    # domain_index = df.columns.get_loc('Domain')
    # access_type_index = df.columns.get_loc('Access Type')
    
    output_file_check = output_file_checker()
    
    if output_file_check:
        niam_ticket_output_excel = Path(
            workbook_path
        ).parent.joinpath(
            "NIAM_Excel_files",
            datetime.now().strftime("%d_%b_%Y"),
            f"RITM Output_PS_Core_{datetime.now().strftime('%d_%b_%Y')}.xlsx"
        )
        
        output_file_reader = pd.ExcelFile(str(niam_ticket_output_excel), engine="openpyxl")
        output_excel_df = output_file_reader.parse("RITM Data Table")
        del output_file_reader
        
        failed_raised_tt_df = output_excel_df.loc[
            output_excel_df["NIAM Ticket Status"].astype(str).str.strip().str.lower().isin(
                [   
                    'failure',
                    'failed',
                    '',
                    'na',
                    'nan',
                    'n/a',
                    'none'
                ]
            )
        ]
        
        # print(f"From OutPut Excel failed_raised_tt_df.to_markdown()\n{failed_raised_tt_df[["S.No", "CR No", "Access Type"]]}")
        
        new_cr_entry_df = df.loc[
            ~(
                df['SR OR CHANGE NO'].astype(str).str.strip().str.lower().isin(
                    np.append(
                        output_excel_df['CR No'].astype(str).str.strip().str.lower().unique(),
                        np.array([
                            'nan',
                            'na',
                            'none',
                            ''
                        ])
                    )
                )
            )
        ]
        required_columns = list(df.columns)
        required_columns.remove("SL. No")
        result_df = pd.DataFrame(columns=required_columns)
        
        if failed_raised_tt_df.shape[0] > 0:         
            failed_filter_df_intersection_main_df = df.loc[
                df['SR OR CHANGE NO'].astype(str).str.strip().str.lower().isin(
                    failed_raised_tt_df['CR No'].astype(str).str.strip().str.lower().unique().tolist()
                )
            ]
            # print(
            #     f"failed_filter_df_intersection_main_df.to_markdown()\n{failed_filter_df_intersection_main_df[["SL. No", "SR OR CHANGE NO", "Access Type"]]}"
            # )
            
            # Remove SL. No column from failed_filter_df_intersection_main_df
            required_columns = list(failed_filter_df_intersection_main_df.columns)
            required_columns.remove("SL. No")
            failed_filter_df_intersection_main_df = failed_filter_df_intersection_main_df[
                required_columns
            ]
            
            for cr in failed_filter_df_intersection_main_df['SR OR CHANGE NO'].astype(str).str.strip().unique():
                # print(f"\n{cr = }")
                # Add logic to handle failed CRs here
                selected_cr_df_from_failed_tt_raised_df = failed_raised_tt_df.loc[
                    failed_raised_tt_df['CR No'].astype(str).str.strip() == cr
                ]
                
                # print(f"\nselected_cr_df_from_failed_tt_raised_df\n{selected_cr_df_from_failed_tt_raised_df[["S.No", "CR No", "Access Type"]]}")
                
                unique_access_types_in_failed_raised_tt_df = selected_cr_df_from_failed_tt_raised_df['Access Type'].astype(str).str.strip().str.lower().unique()
                
                required_input_from_main_input_df = df.loc[
                        (
                            df['SR OR CHANGE NO'].astype(str).str.strip() == cr
                        )
                    ]
                
                # print(f"\nrequired_input_from_main_input_df\n{required_input_from_main_input_df[['SR OR CHANGE NO', 'NIAM Node Name', 'Access Type']]}")
                
                if required_input_from_main_input_df.shape[0] > 0 and selected_cr_df_from_failed_tt_raised_df.shape[0] > 0:
                    result_df = niam_tt_raised_failure_reattempt_row_maker(
                        result_df,
                        required_input_from_main_input_df,
                        selected_cr_df_from_failed_tt_raised_df
                    )
                
                # unique_access_type_in_main_input_df = required_input_from_main_input_df[
                #     'Access Type'
                # ].astype(str).str.strip().str.lower().unique()
                
                # print(f"\nunique_access_type_in_main_input_df\n{list(unique_access_type_in_main_input_df)}")
                
                # if len(unique_access_type_in_main_input_df) > 0:
                #     temp_var= list(unique_access_type_in_main_input_df)[0].split('and')
                #     print(f"\ntemp_var\n{temp_var}")
                #     unique_access_intersection = set(temp_var).intersection(unique_access_types_in_failed_raised_tt_df)
                    
                #     print(f"\nunique_access_intersection\n{unique_access_intersection}")
                #     if len(unique_access_intersection) > 0:
                #         for selected_access_type in unique_access_intersection:
                #             # Add logic to handle each access type here
                            
                #             required_row = required_input_from_main_input_df.loc[
                #                 required_input_from_main_input_df['SR OR CHANGE NO'].astype(str).str.strip() == cr
                #             ].iloc[0].to_dict()
                            
                #             required_row["Access Type"] = selected_access_type
                            
                #             result_df = pd.concat(
                #                 [
                #                     result_df,
                #                     pd.DataFrame([required_row])
                #                 ],
                #                 ignore_index=True
                #             )    
            
        if new_cr_entry_df.shape[0] > 0:
            required_columns = list(new_cr_entry_df.columns)
            required_columns.remove("SL. No")
            # print(f"{list(new_cr_entry_df.columns) = }")
            # print(f"{required_columns = }")
            new_cr_entry_df = new_cr_entry_df[
                required_columns
            ]
            
            result_df = pd.concat(
                [
                    result_df,
                    new_cr_entry_df
                ]
            )
        if "SL. No" in result_df.columns:
            required_columns = list(result_df.columns)
            required_columns.remove("SL. No")
            result_df = result_df[required_columns]
            
        result_df.insert(0, "SL. No", range(1, len(result_df) + 1))
        
        result_df["Access Type"] = result_df["Access Type"].astype(str).str.strip().str.upper()
        
        # print(f"result_df\n{result_df[["SL. No", "SR OR CHANGE NO", "Access Type"]]}")
        
        niam_ticket_raise_using_thread(result_df)        
    
    elif df.shape[0] > 0:
        niam_ticket_raise_using_thread(df)
        
    output_niam_file_maker()


def pre_checks() -> Tuple[bool, Union[pd.DataFrame, None]]:
    global workbook_path, flag
    global live_feed, manager
    
    niam_input_workbook_path = Path(
            workbook_path
        ).parent.joinpath(
            "NIAM_Excel_files",
            datetime.now().strftime("%d_%b_%Y"),
            f"RITM Input_PS_Core_{datetime.now().strftime('%d_%b_%Y')}.xlsx"
        )
    # print(f"NIAM Input Workbook Path: {niam_input_workbook_path}")
    # print(f"{niam_input_workbook_path.exists() = }")
    if not niam_input_workbook_path.exists():
        flag = "Unsuccessful"
        if live_feed:
            live_feed.emit("NIAM Input Excel file not found")
        
        if manager:
            manager.show_info_signal.emit(
                "File Not Found",
                "NIAM File not found",
                "error"
            )
        
        else:
            messagebox = Messagebox()
            messagebox.showerror(
                "File Not Found",
                "NIAM File not found",
            )
            
        return False, None
    
    else:
        excel_file = pd.ExcelFile(str(niam_input_workbook_path), engine='openpyxl')
        if "RITM_INPUT" not in excel_file.sheet_names:
            flag = "Unsuccessful"
            
            excel_file.close()
            del excel_file
            
            if live_feed:
                live_feed.emit(
                    "Worksheet named 'RITM_INPUT' not found in the 'NIAM Input_PS_Core' Workbook"
                )
                
            if manager:
                manager.show_info_signal.emit(
                    "Worksheet Not Found",
                    "Worksheet named 'RITM_INPUT' not found in the 'NIAM Input_PS_Core' Workbook",
                    "error"
                )
            
            else:
                messagebox = Messagebox()
                messagebox.showerror(
                    "Worksheet Not Found",
                    "Worksheet named 'RITM_INPUT' not found in the 'NIAM Input_PS_Core' Workbook",
                )
                
            return False, None
        
        else:
            niam_input_file_df = excel_file.parse("RITM_INPUT")
            excel_file.close()
            del excel_file
            
            if niam_input_file_df.shape[0] > 0:                
                return True, niam_input_file_df
            
            else:
                flag = "Unsuccessful"
                
                if live_feed:
                    live_feed.emit(
                        "Worksheet Data for 'NIAM Input_PS_Core' Workbook is empty"
                    )
                    
                if manager:
                    manager.show_info_signal.emit(
                        "NIAM Input Data Not Missing",
                        "Worksheet Data for 'NIAM Input_PS_Core' Workbook is empty",
                        "error"
                    )
                
                else:
                    messagebox = Messagebox()
                    messagebox.showerror(
                        "NIAM Input Data Not Missing",
                        "Worksheet Data for 'NIAM Input_PS_Core' Workbook is empty",
                    )
                
                return False, None


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
    global glogs, sr_or_change_index, queue_

    GLOBAL_LOGS = GLOBAL_LOGS or []
    timestamp_fn = _timestamp

    runtime["status"] = "Running"
    runtime["download_ready"] = False

    runtime["password_required"] = False
    runtime["password"] = None
    runtime["pwd_event"] = None

    runtime["otp_required"] = False
    runtime["otp"] = None
    runtime["otp_event"] = Event()

    queue_ = Queue()
    glogs = []

    if task.get("id") == GENERATE_NIAM_TICKET_TASK_ID:
        pass