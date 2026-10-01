import os
import queue
import time
import traceback
import pythoncom
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
from dashboard.models import SelectedDateTable
from dashboard.settings import settings
from dashboard.tasks_modules.dependencies.extra_dependencies import (
    selected_date_df_maker, 
    cr_wise_status_df_maker,
    _norm_series)



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
