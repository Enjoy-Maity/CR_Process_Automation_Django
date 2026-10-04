import os
import queue
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
from dashboard.views import _timestamp
from dashboard.models import SelectedDateTable, MasterCRDatabase
from dashboard.utils import settings
from django.http import JsonResponse
from django.db import transaction
from dashboard.task_modules.dependencies.extra_dependencies import (
    selected_date_df_maker, 
    cr_wise_status_df_maker,
    _norm_series
)


def niam_workbook_template_maker(df: pd.DataFrame, mail_id_worksheet_df: pd.DataFrame):
    global workbook_path
    
    niam_workbook_path = Path(
        workbook_path
    ).parent.joinpath(
        "NIAM_Excel_files",
        datetime.now().strftime("%d_%b_%Y"),
        f"RITM Input_PS_Core_{datetime.now().strftime('%d_%b_%Y')}.xlsx"
    )
    
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
    
    project_name_range = f"'{mail_id_sheetname}'!$R$2:$R${get_max_row_in_column(mail_id_worksheet, column_index_from_string('R'))}"
    activity_name_range = f"'{mail_id_sheetname}'!$S$2:$S${get_max_row_in_column(mail_id_worksheet, column_index_from_string('S'))}"
    access_type_range = f"'{mail_id_sheetname}'!$T$2:$T${get_max_row_in_column(mail_id_worksheet, column_index_from_string('T'))}"
    request_for_range = f"'{mail_id_sheetname}'!$U$2:$U${get_max_row_in_column(mail_id_worksheet, column_index_from_string('U'))}"
    domain_range = f"'{mail_id_sheetname}'!$V$2:$V${get_max_row_in_column(mail_id_worksheet, column_index_from_string('V'))}"
    
    dv1=DataValidation(
        type="list",
        formula1=project_name_range,
        allow_blank=True,
        error="Select from list only",
        errorTitle="Invalid Option"
    )
    
    dv2=DataValidation(
        type="list",
        formula1=activity_name_range,
        allow_blank=True,
        error="Select from list only",
        errorTitle="Invalid Option"
    )
    
    dv3=DataValidation(
        type="list",
        formula1=access_type_range,
        allow_blank=True,
        error="Select from list only",
        errorTitle="Invalid Option"
    )
    
    dv4=DataValidation(
        type="list",
        formula1=request_for_range,
        allow_blank=True,
        error="Select from list only",
        errorTitle="Invalid Option"
    )
    
    dv5=DataValidation(
        type="list",
        formula1=domain_range,
        allow_blank=True,
        error="Select from list only",
        errorTitle="Invalid Option"
    )
    
    input_worksheet.add_data_validation(dv1)
    input_worksheet.add_data_validation(dv2)
    input_worksheet.add_data_validation(dv3)
    input_worksheet.add_data_validation(dv4)
    input_worksheet.add_data_validation(dv5)
    
    max_row = input_worksheet.max_row
    
    dv1.add(f"U2:U{max_row}")
    dv2.add(f"T2:T{max_row}")
    dv3.add(f"X2:X{max_row}")
    dv4.add(f"V2:V{max_row}")
    dv5.add(f"W2:W{max_row}")
    
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
 


def niam_input_initiator(filtered_df: pd.DataFrame, mail_id_worksheet_df: pd.DataFrame):
    
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
                mail_id_worksheet_df["NIAM Circle"].astype(str).str.strip(),
                mail_id_worksheet_df["Circle Name"].astype(str).str.strip()
            )
        )
        
        cr_circle_to_niam_circle_mapping = dict(
            zip(
                mail_id_worksheet_df["Circle"].astype(str).str.strip(),
                mail_id_worksheet_df["NIAM Circle"].astype(str).str.strip()
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
        
        today_date = datetime.now()
        today_date = today_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # today_date = today_date.strftime('%d-%m-%Y %H:%M:%S')

        tomorrow_date = datetime.now() + timedelta(days=1)
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
            selected_cr_df = niam_filtered_df.loc[niam_filtered_df["CR No"] == cr]
            
            node_type_var = selected_cr_df.iloc[0, niam_node_type_index]
            
            node_type_var_list = [str(element).strip() for element in node_type_var.split(",")]
            node_names = re.sub(r",", "", selected_cr_df.iloc[0, node_details_index])
            node_names = [str(element).strip() for element in re.split("\n", node_names)]
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
        
        niam_workbook_template_maker(niam_input_template_df, mail_id_worksheet_df)



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
    runtime["pwd_event"] = Event()

    # OTP fields (existing)
    runtime["otp_required"] = False
    runtime["otp"] = None
    runtime["otp_event"] = Event()

    parsed_date = dp.parse(selected_date)

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

            # print(f"{model_instances = }")

            with transaction.atomic(using='default'):
                SelectedDateTable.objects.using('default').bulk_create(model_instances)
                # transaction.on_commit(lambda: sync_replica_task(), using='default')

            selected_date_data = SelectedDateTable.objects.filter(execution_date=parsed_date + timedelta(days=1), is_active=True).values(*settings.SELECTED_DATE_TABLE_FIELDS)
            # print(f"{selected_date_data = }")
        selected_data_df = selected_date_df_maker(selected_date_data)
    
    cr_wise_status_df = cr_wise_status_df_maker(parsed_date)
    # cr_wise_status_df = cr_wise_status_df.where(~pd.notna(cr_wise_status_df["CR_Hygiene_Checks"]), "")
    cr_wise_status_df["NIAM_Ticket"].fillna("", inplace=True)

    cr_wise_status_df = cr_wise_status_df.loc[
        cr_wise_status_df["NIAM_Ticket"].astype(str).str.lower().str.strip() != 'success'
    ]

    planning_status_norm = _norm_series(selected_data_df["Planning Status"])
    niam_cr_norm = _norm_series(selected_data_df["NIAM Ticket Required (Yes/No)"])
    niam_node_type = _norm_series(selected_data_df["NIAM Node Type"])

    selected_data_df = selected_data_df.loc[
        (
            planning_status_norm.eq("planned") & niam_cr_norm.eq("yes")
        )
        &
        (
            (
                niam_node_type.astype(str).str.strip().map(len) > 0
            )
            &
            (
                ~niam_node_type.astype(str).str.strip().str.lower().isin(
                    [
                        "nan",
                        "tempna",
                        "na",
                    ]
                )
            )
        )
    ]

    to_be_filter_crs = list(cr_wise_status_df["cr_no"].astype(str).str.strip().unique())
    # print(f"\n\nto_be_filter_crs = \n{to_be_filter_crs}\n")
    # print(f"selected_data_df_crs=\n{selected_data_df['CR No'].tolist()}\n")

    selected_data_df = selected_data_df.loc[
        selected_data_df["CR No"].astype(str).str.strip().isin(to_be_filter_crs)
    ]
