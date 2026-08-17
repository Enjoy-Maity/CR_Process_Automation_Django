import os
import uuid
import platform
import ctypes
import traceback
import threading
import numpy as np
import charset_normalizer as cn
import pandas as pd
from datetime import datetime, timedelta
from django.core.management import call_command
# from celery import shared_task
from playwright.sync_api import sync_playwright
from dashboard.views import _timestamp
from dashboard.task_modules.dependencies.extra_dependencies import CustomThread
import dashboard.task_modules.dependencies.playwright_common_methods_ as pcm
from typing import List, AnyStr
from pandas import DataFrame
from os import PathLike
import  dateutil.parser as dp
from django.db import transaction
# from django.core.cache import cache
from dashboard.models import MasterCRDatabase, CRWiseStatus

def check_admin_status():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def common_paths_for_browser_method():
    admin_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser("~/AppData/Local/BraveSoftware/Brave-Browser/Application/brave.exe"),
    ]

    user_paths = [
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        os.path.expanduser("~/AppData/Local/BraveSoftware/Brave-Browser/Application/brave.exe"),
    ]

    paths = admin_paths if check_admin_status() else user_paths

    for path in paths:
        if os.path.exists(path):
            return path
    return None


def encoding_fetcher(csv_file: str) -> str:
    return cn.from_path(csv_file).best().encoding


def chrome_path_returner() -> str:
    if platform.system() == "Windows":
        return common_paths_for_browser_method()
    return None


def raw_report_to_planning_sheet_converter(
    raw_report_file_content: DataFrame, workbook: str | PathLike, logs:List[AnyStr], runtime:dict, selected_date=None, user_name: str = "") -> None:
    
    runtime["status"] = "Creating Planning Sheet"
    try:
        raw_report_file_content["Scheduled Start Date+"] = pd.to_datetime(
            raw_report_file_content["Scheduled Start Date+"],
            format="%m/%d/%Y %I:%M:%S %p",
        )

        new_temp_df = pd.DataFrame()
        new_temp_df.insert(loc=0, column="S.No.", value="")
        new_temp_df.insert(loc=1, column="MS/Project", value="")
        new_temp_df.insert(loc=2, column="Execution Date", value="")
        new_temp_df.insert(loc=3, column="Maintainence Window", value="")
        new_temp_df.insert(loc=4, column="CR No", value="")
        new_temp_df.insert(loc=5, column="Priority", value="")
        new_temp_df.insert(loc=6, column="Risk", value="")
        new_temp_df.insert(loc=7, column="Region", value="")
        new_temp_df.insert(loc=8, column="Circle", value="")
        new_temp_df.insert(loc=9, column="Node Details", value="")
        new_temp_df.insert(loc=10, column="Node Count", value="")
        new_temp_df.insert(loc=11, column="Activity Description", value="")
        new_temp_df.insert(loc=12, column="BPMS CR (Yes/No)", value="")
        new_temp_df.insert(loc=13, column="Planning Status", value="")
        new_temp_df.insert(loc=14, column="Activity Executor", value="")
        new_temp_df.insert(loc=15, column="Auditor Name", value="")
        new_temp_df.insert(loc=16, column="Activity Status", value="")
        new_temp_df.insert(loc=17, column="Reason For Rollback/Cancel", value="")
        new_temp_df.insert(loc=18, column="Technical Validator", value="")
        new_temp_df.insert(loc=19, column="Service Affecting", value="")
        new_temp_df.insert(loc=20, column="Impact", value="")
        new_temp_df.insert(loc=21, column="Test Cases", value="")
        new_temp_df.insert(loc=22, column="KPI Name", value="")   
        new_temp_df.insert(loc=23, column="KPI SPOC (Night)", value="")
        new_temp_df.insert(loc=24, column="KPI SPOC (Morning)", value="")
        new_temp_df.insert(loc=25, column="Inter-Domain Activity", value="")
        new_temp_df.insert(loc=26, column="Inter-Domain KPI Required", value="")
        new_temp_df.insert(loc=27, column="Inter-Domain Measuring KPIs", value="")
        new_temp_df.insert(loc=28, column="Activity Type", value="")
        new_temp_df.insert(loc=29, column="Vendor", value="")
        new_temp_df.insert(loc=30, column="Protocol", value="")
        new_temp_df.insert(loc=31, column="Execution Type", value="")
        new_temp_df.insert(loc=32, column="CLI Availability", value="")
        new_temp_df.insert(loc=33, column="Team", value="")
        new_temp_df.insert(loc=34, column="Scheduled Start Date+", value="")
        new_temp_df.insert(loc=35, column="Scheduled End Date+", value="")

        temp_df = raw_report_file_content.copy()

        new_temp_df["CR No"] = temp_df.loc[:, "Change ID*+"]

        new_temp_df["S.No."] = range(1, len(new_temp_df) + 1)
        
        selected_date = dp.parse(selected_date)           
        new_temp_df["Execution Date"] = (selected_date + timedelta(days=1)).strftime("%d-%m-%Y")


        new_temp_df["Maintainence Window"] = (
            pd.to_datetime(temp_df["Scheduled Start Date+"]).dt.strftime(
                "%H:%M:%S"
            )
            + " - " 
            + pd.to_datetime(temp_df["Scheduled End Date+"]).dt.strftime(
                "%H:%M:%S"
            )
        )
        new_temp_df["MS/Project"] = "MS"
        new_temp_df["Priority"] = temp_df.loc[:, "Priority"]
        new_temp_df["Risk"] = temp_df.loc[:, "Impact*"]
        new_temp_df["Region"] = temp_df.loc[:, "Region"]
        new_temp_df.loc[new_temp_df["Region"].fillna("").str.contains("Upper North Region", case=False, na=False), "Region"] = "North"
        new_temp_df.loc[new_temp_df["Region"].fillna("").str.contains("North Region", case=False, na=False), "Region"] = "North"
        new_temp_df.loc[new_temp_df["Region"].fillna("").str.contains("South Region", case=False, na=False), "Region"] = "South"
        new_temp_df.loc[new_temp_df["Region"].fillna("").str.contains("West Region", case=False, na=False), "Region"] = "West"
        new_temp_df.loc[new_temp_df["Region"].fillna("").str.contains("East Region", case=False, na=False), "Region"] = "East"

        new_temp_df["Circle"] = temp_df.loc[:, "Site Group"]
        new_temp_df["Node Count"] = temp_df.loc[:, "Custom_Field2"]

        new_temp_df["Activity Description"] = temp_df.loc[:, "Summary*"]
        new_temp_df["Service Affecting"] = temp_df.loc[:, "Service Affecting"]

        new_temp_df["Inter-Domain Activity"] = temp_df.loc[:, "Custom_Field13"]
        new_temp_df["Inter-Domain KPI Required"] = temp_df.loc[:, "Custom_Field14"]
        new_temp_df["Inter-Domain Measuring KPIs"] = temp_df.loc[:, "Custom_Field15"]

        new_temp_df["Vendor"] = temp_df.loc[:, "Custom_Field10"]

        new_temp_df["Team"] = temp_df.loc[:, "Coordinator Group*+"]
        new_temp_df.loc[new_temp_df["Team"].str.contains("SRF-Packet Core CM Delhi"), "Team"] = "PS-CORE"
        new_temp_df.loc[new_temp_df["Team"].str.contains("SRF-VAS CM Delhi"), "Team"] = "VAS"

        new_temp_df["Activity Type"] = temp_df.loc[:, "Operational Categorization Tier 3"]
        new_temp_df["Scheduled Start Date+"] = temp_df.loc[:, "Scheduled Start Date+"]
        new_temp_df["Scheduled End Date+"] = temp_df.loc[:, "Scheduled End Date+"]

        new_temp_df["BPMS CR (Yes/No)"] = np.where(
                                                temp_df["Summary*"].str.startswith("BPMS", na=False) |
                                                temp_df["Summary*"].str.contains("BPMS", na=False),
                                                "Yes",
                                                "No"
                                                )
                                                
        new_temp_df["Technical Validator"] = str(user_name)
        new_temp_df["NIAM Ticket Required (Yes/No)"] = ""
        new_temp_df["NIAM Node Type"] = ""
        new_temp_df["Additional Info"] = ""
        
        writer = pd.ExcelWriter(workbook, engine="openpyxl", mode="w")
        
        new_temp_df.to_excel(writer, sheet_name="Planning_Sheet", index=False)
        writer.close()
        del writer

    except Exception as e:
        logs.append(
            (   
                f"Exception: {e.__class__.__name__}\n"
                f"{traceback.format_exc()}\n"
                f"{e}"
            )
        )

        raise

    return logs

def _clean_nan_like_values(df: DataFrame) -> DataFrame:
    cleaned_df = df.copy()

    nan_like_tokens = {
        "nan", "na", "n/a", "n.a.", "n.a", "none", "null", "nat",
        "-", "--", "<na>", "NaN", "None", "NULL"
    }

    def _clean_value(value):
        if value is None:
            return ""
        if pd.isna(value):
            return ""
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.lower() in nan_like_tokens:
                return ""
            return stripped
        return value

    for col in cleaned_df.columns:
        cleaned_df[col] = cleaned_df[col].apply(_clean_value)

    return cleaned_df

def _prepare_master_fields_from_planning_sheet(planning_df: DataFrame) -> DataFrame:
    column_map = {
        "S.No.": "sno", "MS/Project": "ms_project", "Execution Date": "execution_date",
        "Maintainence Window": "maintenance_window", "CR No": "cr_no", "Priority": "priority",
        "Risk": "risk", "Region": "region", "Circle": "circle", "Node Details": "node_details",
        "Node Count": "node_count", "Activity Description": "activity_description",
        "BPMS CR (Yes/No)": "bpms_cr_yes_no", "Planning Status": "planning_status",
        "Activity Executor": "activity_executor", "Auditor Name": "auditor_name",
        "Activity Status": "activity_status", "Reason For Rollback/Cancel": "reason_for_rollback_cancel",
        "Technical Validator": "technical_validator", "Service Affecting": "service_affecting",
        "Impact": "impact", "Test Cases": "test_cases", "KPI Name": "kpi_name",
        "KPI SPOC (Night)": "kpi_spoc_night", "KPI SPOC (Morning)": "kpi_spoc_morning",
        "Inter-Domain Activity": "inter_domain_activity",
        "Inter-Domain KPI Required": "inter_domain_kpi_required",
        "Inter-Domain Measuring KPIs": "inter_domain_measuring_kpis",
        "Activity Type": "activity_type", "Vendor": "vendor", "Protocol": "protocol",
        "Execution Type": "execution_type", "CLI Availability": "cli_availability", "Team": "team",
        "Scheduled Start Date+": "scheduled_start_date", "Scheduled End Date+": "scheduled_end_date",
        "NIAM Ticket Required (Yes/No)": "niam_ticket_required", "NIAM Node Type": "niam_node_type",
        "Additional Info": "additional_info",
    }

    df = planning_df.rename(columns=column_map)
    df = df[[c for c in column_map.values() if c in df.columns]].copy()
    df = _clean_nan_like_values(df)

    df["cr_no"] = df["cr_no"].fillna("").replace("nan", "").replace("NaN", "")
    df["cr_no"] = df["cr_no"].astype(str).str.strip()

    df["execution_date"] = pd.to_datetime(df["execution_date"], format="%d-%m-%Y", errors="coerce").dt.date
    df["scheduled_start_date"] = pd.to_datetime(df.get("scheduled_start_date"), errors="coerce")
    df["scheduled_end_date"] = pd.to_datetime(df.get("scheduled_end_date"), errors="coerce")
    df["sno"] = pd.to_numeric(df.get("sno"), errors="coerce")
    df["node_count"] = pd.to_numeric(df.get("node_count"), errors="coerce")

    df = df.drop_duplicates(subset=["cr_no"]).reset_index(drop=True)

    return df


def sync_cr_databases(planning_workbook_df: DataFrame, logs: List[AnyStr], runtime: dict) -> List[AnyStr]:
    runtime["status"] = "Syncing CR Databases"
    try:
        mapped_df = _prepare_master_fields_from_planning_sheet(planning_workbook_df)
        print(f"Mapped dataframe: {mapped_df}")

        total_inserted = 0
        total_updated_cow = 0

        unique_exec_dates = sorted(mapped_df["execution_date"].dropna().unique())
        print(f"Unique Execution Date: {unique_exec_dates}")

        if not unique_exec_dates:
            logs.append("No execution dates found; nothing to sync.")
            return logs

        last_index = len(unique_exec_dates) - 1
        # one sync_id to track the whole run
        # sync_id = str(uuid.uuid4())
        # cache_key = f'replica_sync_{sync_id}_status'
        # cache.set(cache_key, 'in_progress', None)

        # Iterate through the dates and rows to apply CoW insertions manually targeting master DB ('default')
        for exec_date in unique_exec_dates:
            date_group_df = mapped_df[mapped_df["execution_date"] == exec_date]

            # Explicitly wrap transaction on the master database connection
            with transaction.atomic(using='default'):
                for row in date_group_df.itertuples(index=False):
                    cr_number = str(row.cr_no)

                    # Explicitly use .using('default') for queries during write/sync phases
                    active_master = MasterCRDatabase.objects.using('default').filter(cr_no=cr_number, is_active=True).first()
                    active_status = CRWiseStatus.objects.using('default').filter(cr_no=cr_number, is_active=True).first()

                    if active_master:
                        # 1. Deactivate old records on master database
                        MasterCRDatabase.objects.using('default').filter(pk=active_master.pk).update(is_active=False)
                        if active_status:
                            CRWiseStatus.objects.using('default').filter(pk=active_status.pk).update(is_active=False)

                        # 2. Insert new CoW versions explicitly into master database
                        MasterCRDatabase.objects.using('default').create(
                            sno=row.sno if pd.notna(row.sno) else None,
                            ms_project=row.ms_project, execution_date=row.execution_date,
                            maintenance_window=row.maintenance_window, cr_no=row.cr_no, priority=row.priority,
                            risk=row.risk, region=row.region, circle=row.circle, node_details=row.node_details,
                            node_count=row.node_count if pd.notna(row.node_count) else None,
                            activity_description=row.activity_description, bpms_cr_yes_no=row.bpms_cr_yes_no,
                            planning_status=row.planning_status, activity_executor=row.activity_executor,
                            auditor_name=row.auditor_name, activity_status=row.activity_status,
                            reason_for_rollback_cancel=row.reason_for_rollback_cancel,
                            technical_validator=row.technical_validator, service_affecting=row.service_affecting,
                            impact=row.impact, test_cases=row.test_cases, kpi_name=row.kpi_name,
                            kpi_spoc_night=row.kpi_spoc_night, kpi_spoc_morning=row.kpi_spoc_morning,
                            inter_domain_activity=row.inter_domain_activity,
                            inter_domain_kpi_required=row.inter_domain_kpi_required,
                            inter_domain_measuring_kpis=row.inter_domain_measuring_kpis,
                            activity_type=row.activity_type, vendor=row.vendor, protocol=row.protocol,
                            execution_type=row.execution_type, cli_availability=row.cli_availability, team=row.team,
                            scheduled_start_date=row.scheduled_start_date if pd.notna(row.scheduled_start_date) else None,
                            scheduled_end_date=row.scheduled_end_date if pd.notna(row.scheduled_end_date) else None,
                            niam_ticket_required=row.niam_ticket_required, niam_node_type=row.niam_node_type,
                            additional_info=row.additional_info,
                            # CoW Fields
                            is_active=True,
                            version=active_master.version + 1,
                            parent_reference_id=active_master.pk
                        )

                        CRWiseStatus.objects.using('default').create(
                            sno=row.sno if pd.notna(row.sno) else None,
                            execution_date=row.execution_date, maintenance_window=row.maintenance_window,
                            cr_no=row.cr_no, risk=row.risk, activity_description=row.activity_description,
                            bpms_cr_yes_no=row.bpms_cr_yes_no, circle=row.circle, region=row.region,
                            technical_validator=row.technical_validator,
                            CR_Hygiene_Checks="Pending", Install_Test_Plan_Downloads="Pending",
                            MOP_Attachment="Pending", CR_Approvals="Pending", NIAM_Ticket=" ",
                            # CoW Fields
                            is_active=True,
                            version=(active_status.version + 1) if active_status else 1,
                            parent_reference_id=active_status.pk if active_status else None
                        )
                        total_updated_cow += 1

                    else:
                        # 3. Handle brand new insertions explicitly on master database
                        MasterCRDatabase.objects.using('default').create(
                            sno=row.sno if pd.notna(row.sno) else None,
                            ms_project=row.ms_project, execution_date=row.execution_date,
                            maintenance_window=row.maintenance_window, cr_no=row.cr_no, priority=row.priority,
                            risk=row.risk, region=row.region, circle=row.circle, node_details=row.node_details,
                            node_count=row.node_count if pd.notna(row.node_count) else None,
                            activity_description=row.activity_description, bpms_cr_yes_no=row.bpms_cr_yes_no,
                            planning_status=row.planning_status, activity_executor=row.activity_executor,
                            auditor_name=row.auditor_name, activity_status=row.activity_status,
                            reason_for_rollback_cancel=row.reason_for_rollback_cancel,
                            technical_validator=row.technical_validator, service_affecting=row.service_affecting,
                            impact=row.impact, test_cases=row.test_cases, kpi_name=row.kpi_name,
                            kpi_spoc_night=row.kpi_spoc_night, kpi_spoc_morning=row.kpi_spoc_morning,
                            inter_domain_activity=row.inter_domain_activity,
                            inter_domain_kpi_required=row.inter_domain_kpi_required,
                            inter_domain_measuring_kpis=row.inter_domain_measuring_kpis,
                            activity_type=row.activity_type, vendor=row.vendor, protocol=row.protocol,
                            execution_type=row.execution_type, cli_availability=row.cli_availability, team=row.team,
                            scheduled_start_date=row.scheduled_start_date if pd.notna(row.scheduled_start_date) else None,
                            scheduled_end_date=row.scheduled_end_date if pd.notna(row.scheduled_end_date) else None,
                            niam_ticket_required=row.niam_ticket_required, niam_node_type=row.niam_node_type,
                            additional_info=row.additional_info,
                            is_active=True,
                            version=1
                        )

                        CRWiseStatus.objects.using('default').create(
                            sno=row.sno if pd.notna(row.sno) else None,
                            execution_date=row.execution_date, maintenance_window=row.maintenance_window,
                            cr_no=row.cr_no, risk=row.risk, activity_description=row.activity_description,
                            bpms_cr_yes_no=row.bpms_cr_yes_no, circle=row.circle, region=row.region,
                            technical_validator=row.technical_validator,
                            CR_Hygiene_Checks="Pending", Install_Test_Plan_Downloads="Pending",
                            MOP_Attachment="Pending", CR_Approvals="Pending", NIAM_Ticket=" ",
                            is_active=True,
                            version=1
                        )
                        total_inserted += 1

                # Register the replica sync to run only after the DB transaction commits
                transaction.on_commit(lambda: sync_replica_task(), using='default')

        logs.append(f"Sync complete: {total_inserted} new CR(s) inserted, {total_updated_cow} existing CR(s) updated to new versions.")

    except Exception as e:
        # cache.set(f'replica_sync_{sync_id}_status', 'failed', None)
        logs.append(f"Exception: {e.__class__.__name__}\n{traceback.format_exc()}\n{e}")
        runtime["status"] = "Failed"
        raise

    return logs


# @shared_task(bind=True)
# def sync_replica_task(self):
def sync_replica_task():
    # self.update_state(state='RUNNING')
    # sync_id = self.request.id
    try:
        call_command('sync_replica')
        # cache.set(f'replica_sync_{sync_id}_status', 'complete', None)
    except Exception as e:
        # cache.set(f'replica_sync_{sync_id}_status', 'failed', None)
        raise


def run_task(request, task, runtime, GLOBAL_LOGS=None, timestamp_fn=None, selected_date=None, user_email=None, user_name=None):
    GLOBAL_LOGS = GLOBAL_LOGS or []
    timestamp_fn = timestamp_fn or _timestamp

    runtime["status"] = "Running"
    runtime["download_ready"] = False
    
    # Password fields (new)
    runtime["password_required"] = False
    runtime["password"] = None
    runtime["pwd_event"] = threading.Event()

    # OTP fields (existing)
    runtime["otp_required"] = False
    runtime["otp"] = None
    runtime["otp_event"] = threading.Event()

    playwright = None
    browser=None
    context = None
    page = None

    with sync_playwright() as playwright:
        try:
            browser, context, page, GLOBAL_LOGS = pcm.itsm_logger(
                GLOBAL_LOGS,
                playwright,
                False,
                task,
                runtime,
                timestamp_fn,
                user_email,
                )

            GLOBAL_LOGS=pcm.raw_report_downloader(
                context, 
                page, 
                GLOBAL_LOGS, 
                task,
                runtime,
                timestamp_fn,
                date_=selected_date,
            )

            if page:
                GLOBAL_LOGS = pcm.itsm_logout(
                    page, 
                    task,
                    runtime,
                    GLOBAL_LOGS,
                    timestamp_fn
                    )

        except Exception as e:
            GLOBAL_LOGS.append(
                (   
                    f"Exception Occurred: {e.__class__.__name__}\n "
                    f"{traceback.format_exc()}\n "
                    f"{e}"
                )
            )
            raise

        finally:
            try:
                if playwright:
                    for obj_ in (browser, context, page):
                        if obj_:
                            obj_.close()
                            del obj_
                    
                        playwright.stop()
            
            except Exception:
                pass


    folder_date = (dp.parse(selected_date)).strftime("%d-%b-%y")
    report_file_date = (dp.parse(selected_date))

    report_file = os.path.join(str(os.getenv("RAW_REPORT_DOWNLOAD_FOLDER").format(folder_date)), f"PS_Core_Raw_Report_{report_file_date.strftime('%Y-%m-%d')}.csv")
    encoding_thread = CustomThread(target=encoding_fetcher, args=(report_file,))
    encoding_thread.start()
    encoding = encoding_thread.join()

    report_df = pd.read_csv(report_file, encoding=encoding)

    report_df_filtered = report_df[report_df["Status*"].str.contains("Request For Authorization", case=False)]
    valid_status= "|".join(["Request For Authorization", "Scheduled For Approval", "Request For Change"])
    report_df_filtered = report_df[report_df["Status*"].str.contains(valid_status, regex= True, case= False)]

    planning_workbook = str(os.getenv("PLANNING_SHEET_WORKBOOK_PATH"))

    if report_df_filtered.shape[0]>0:
        GLOBAL_LOGS = raw_report_to_planning_sheet_converter(
            report_df_filtered, planning_workbook, GLOBAL_LOGS, runtime, selected_date = selected_date, user_name = user_name
            )

        planning_workbook_df = pd.read_excel(planning_workbook)
        GLOBAL_LOGS = sync_cr_databases(planning_workbook_df, GLOBAL_LOGS, runtime)

    else:
        GLOBAL_LOGS.append(f"No CR found having status 'Request For Authorization' for {selected_date}")
        
    return {
        "status": "Completed",
        "message": f"{task['name']} completed successfully.",
        "download_ready": True,
        "download_name": report_file,
        "counts": {},
    }