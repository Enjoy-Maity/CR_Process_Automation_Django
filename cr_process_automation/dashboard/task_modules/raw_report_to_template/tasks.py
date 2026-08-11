import os
import platform
import ctypes
import traceback
import threading
import numpy as np
import charset_normalizer as cn
import pandas as pd
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from dashboard.views import _timestamp
from dashboard.task_modules.dependencies.extra_dependencies import CustomThread
import dashboard.task_modules.dependencies.playwright_common_methods_ as pcm
from typing import List, AnyStr

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
    raw_report_file_content: DataFrame, workbook: str | PathLike, logs:List[AnyStr], runtime:dict, user_name: str = "") -> None:
    

    # Process the raw report data to create a planning sheet
    # ...
    runtime["status"] = "Creating Planning Sheet"
    try:
        raw_report_file_content["Scheduled Start Date+"] = pd.to_datetime(
            raw_report_file_content["Scheduled Start Date+"],
            format="%m/%d/%Y %I:%M:%S %p",
        )
        date1 = pd.Timestamp(
            datetime.now()
            .replace(hour=20, minute=0, second=0)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
        date2 = pd.Timestamp(
            (
                (datetime.now() + timedelta(days=1)).replace(hour=8, minute=0, second=0)
            ).strftime("%Y-%m-%d %H:%M:%S")
        )
        # print(f"{date1 = } , {date2 = }")
        # print(raw_report_file_content["Scheduled Start Date+"])

        outside_date_df = raw_report_file_content.loc[
            ~raw_report_file_content["Scheduled Start Date+"].between(date1, date2)
            | raw_report_file_content["Scheduled Start Date+"].isna()
        ]


        if outside_date_df.empty or outside_date_df.shape[0] == 0:

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
            # new_temp_df.insert(loc=36, column="Additional Info", value="")

            temp_df = raw_report_file_content.copy()

            new_temp_df["CR No"] = temp_df.loc[:, "Change ID*+"]

            new_temp_df["S.No."] = range(1, len(new_temp_df) + 1)
            
            new_temp_df["Execution Date"] = pd.to_datetime(
                temp_df["Scheduled Start Date+"]
            ).dt.date
            
            # new_temp_df["Execution Date"] = datetime.now().strftime("%d-%m-%Y")            
            new_temp_df["Execution Date"] = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")


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

            # runtime["status"]=""

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


def run_task(request, task, runtime, GLOBAL_LOGS=None, timestamp_fn=None):
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

    # chrome_path = chrome_path_returner()

    # with sync_playwright() as p:
    #     browser = p.chromium.launch(
    #         executable_path=chrome_path if chrome_path else None,
    #         headless=False,
    #     )
    #     context = browser.new_context()
    #     page = context.new_page()

        # url = "https://ticketing-in.managed-services.prod.sdt.ericsson.net/arsys/"
        # GLOBAL_LOGS.append(f"{task['name']}: opening {url} ---- {timestamp_fn()}")
        # page.goto(url, wait_until="load")

        # # TODO: adjust these steps to your actual login/2FA flow.
        # # Example: wait until the OTP page / OTP input becomes visible.
        # runtime["status"] = "Waiting for OTP"
        # runtime["otp_required"] = True
        # GLOBAL_LOGS.append(f"{task['name']}: waiting for OTP ---- {timestamp_fn()}")

        # otp_event = runtime.get("otp_event")
        # if otp_event:
        #     otp_event.wait(timeout=300)

        # otp = runtime.get("otp")
        # if not otp:
        #     runtime["status"] = "Failed" 
        #     msg = "OTP not received in time."
        #     GLOBAL_LOGS.append(f"{task['name']}: {msg} ---- {timestamp_fn()}")
        #     browser.close()
        #     return {
        #         "status": "Failed",
        #         "message": msg,
        #         "download_ready": False,
        #         "download_name": runtime.get("download_name", ""),
        #         "counts": {},
        #     }

        # # Replace selector with the real OTP field on your page.
        # page.fill("input[name='otp']", otp)
        # page.click("button[type='submit']")
        # page.wait_for_load_state("networkidle")

        # runtime["status"] = "Completed"
        # GLOBAL_LOGS.append(f"{task['name']}: completed successfully ---- {timestamp_fn()}")

        # browser.close()

    # GLOBAL_LOGS = pcm.session_maker(
    #     GLOBAL_LOGS, 
    #     task, 
    #     False,
    #     runtime, 
    #     timestamp_fn)
    # print("inside run task function")
    # import time
    # time.sleep(10)

    playwright = None
    browser=None
    context = None
    page = None

    with sync_playwright() as playwright:
        # pcm.session_breaker()
        try:
            browser, context, page, GLOBAL_LOGS = pcm.itsm_logger(
                GLOBAL_LOGS,
                playwright,
                False,
                task,
                runtime,
                timestamp_fn
                )

            GLOBAL_LOGS=pcm.raw_report_downloader(
                context, 
                page, 
                GLOBAL_LOGS, 
                task,
                runtime,
                timestamp_fn,
                None
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
            
            except:
                pass

    report_file = os.path.join(str(os.getenv("RAW_REPORT_DOWNLOAD_FOLDER")), f"PS_Core_Raw_Report_{datetime.now().strftime('%Y-%m-%d')}.csv")
    encoding_thread = CustomThread(target=encoding_fetcher, args=(report_file,))
    # encoding_thread.daemon = True
    encoding_thread.start()
    encoding = encoding_thread.join()

    report_df = pd.read_csv(report_file, encoding=encoding)

    planning_workbook = str(os.getenv("PLANNING_SHEET_WORKBOOK_PATH"))

    GLOBAL_LOGS = raw_report_to_planning_sheet_converter(report_df, planning_workbook, GLOBAL_LOGS, runtime, "Karan Loomba")
    
    return {
        "status": "Completed",
        "message": f"{task['name']} completed successfully.",
        "download_ready": False,
        "download_name": runtime.get("download_name", ""),
        "counts": {},
    }