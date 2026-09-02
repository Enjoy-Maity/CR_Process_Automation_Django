import os
import traceback
import pandas as pd
import dateutil.parser as dp
import dashboard.task_modules.dependencies.batch_methods as bm
import dashboard.task_modules.dependencies.playwright_common_methods_ as pcm
from django.http import JsonResponse
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from playwright.sync_api import sync_playwright, Page
from typing import AnyStr, List, Callable, Dict, Any
from threading import Event, Thread
from datetime import datetime, timedelta
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from dashboard.views import _make_serializable
from dashboard.models import MasterCRDatabase, SelectedDateTable, CRWiseStatus
from dashboard.task_modules.cr_hygiene_checks.tasks import selected_date_df_maker
from dashboard.task_modules.dependencies.extra_dependencies import cr_wise_status_df_maker


queue_ = Queue()
glogs = Queue()
workbook_parent = ""



def cr_wise_status_modifier_update_func(
    cr: str,
    status: str = "Success"
):
    with transaction.atomic(using='default'):
        cr_wise_status = CRWiseStatus.objects.using('default').get(cr_no=cr, is_active=True)
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


def page_tasks(
    batch_number,
    cr_batch: List[str],
    cr_to_circle_dict: Dict[str, str],
    date_: datetime
):
    global glogs
    stop_event = Event()
    with sync_playwright() as thread_playwright_instance:
        browser = thread_playwright_instance.chromium.launch(
            headless=False,
            executable_path=pcm.get_browser(),
            timeout=15000,
        )
        logs = []
        thread_context = browser.new_context(storage_state=os.getenv("ITSM_SESSION_FILE"))
        page, logs = pcm.new_page_opener(thread_context, logs)
        page.on("dialog", lambda d: d.accept())
        
        try:
            if (thread_context is not None) and (page is not None):
                logs.append(f"Batch {batch_number} started")

                token_for_locking = True

                i = 0
                while i < len(cr_batch):
                    cr = cr_batch[i]
                    try:
                        cr_work_table = None
                        # print(cr)
                        logs = pcm.search_for_cr(page, cr, logs)

                        wait_var = True
                        # Waiting for the table to load
                        while wait_var:
                            try:
                                if (
                                    page.locator(
                                        "//div[@class='PageBody pbChrome']/div[@id='WIN_3_301389923']/div[@class='TableHdr']/table[@class='TableHdr']/tbody/tr/td[@class='TableHdrL']"
                                    ).text_content()
                                    == "Table has Not been Loaded"
                                ):
                                    page.wait_for_timeout(1000)
                                else:
                                    wait_var = False
                            except:
                                continue
                    
                        page.wait_for_load_state("domcontentloaded")
                        # page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(1000)

                        page.wait_for_load_state("domcontentloaded")
                        # page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(1000)

                        _, cr_work_table = pcm.work_detail_table_reader(page, cr)
                            
                        # cr_work_table["Files"] = cr_work_table["Files"].apply(lambda x: int(x) if pd.notna(x) else 0)
                        cr_work_table["Files"] = pd.to_numeric(cr_work_table["Files"], errors="coerce").fillna(0).astype(int)
                        cr_work_table = cr_work_table.where(pd.notna(cr_work_table), "TempNA")
                        
                        install_plan_found = False
                        
                        install_plan_attached_to_cr = ["Not Available", "Not Available"]
                        
                        install_plan_df = cr_work_table[
                            (cr_work_table['Type'].astype(str).str.strip() == 'Install Plan')
                            ]

                        if not install_plan_df.empty:
                            install_plan_found = True if install_plan_df.iloc[0]['Files'] > 0 else False

                        if install_plan_found:
                            install_plan_attached_to_cr, token_for_locking, logs = (
                                pcm.call_with_modal_ack(
                                    pcm.install_plan_downloader,
                                    page,
                                    workbook_parent,
                                    cr,
                                    cr_to_circle_dict[cr],
                                    True,
                                    token_for_locking,
                                    date_,
                                    logs,
                                    max_retries=2,
                                )
                            )
                            
                        backout_plan_found = False
                        
                        backout_plan_df = cr_work_table[
                            (cr_work_table['Type'].astype(str).str.strip() == 'Backout Plan')
                            ]

                        if not backout_plan_df.empty:
                            backout_plan_found = True if backout_plan_df.iloc[0]['Files'] > 0 else False
                        
                        backout_plan_availability_list = ["Not Available", "Not Available"]
                        if backout_plan_found:
                            # ---Backout plan (may trigger modal) ---
                            backout_plan_availability_list, token_for_locking, logs = (
                                pcm.call_with_modal_ack(
                                    pcm.backout_plan_downloader,
                                    page,
                                    workbook_parent,
                                    cr,
                                    cr_to_circle_dict[cr],
                                    token_for_locking,
                                    date_,
                                    logs,
                                    max_retries=2,
                                )
                            )
                            
                        test_plan_found = False
                        
                        test_plan_df = cr_work_table[
                            (cr_work_table['Type'].astype(str).str.strip() == 'Test Plan')
                            ]
                        
                        if not test_plan_df.empty:
                            test_plan_found = True if test_plan_df.iloc[0]['Files'] > 0 else False

                        test_plan_availability_list = ["Not Available", "Not Available"]
                        if test_plan_found:
                            # --- Test plan (may trigger modal) ---
                            test_plan_availability_list, token_for_locking, logs = (
                                pcm.call_with_modal_ack(
                                    pcm.test_plan_downloader,
                                    page,
                                    workbook_parent,
                                    cr,
                                    cr_to_circle_dict[cr],
                                    token_for_locking,
                                    date_,
                                    logs,
                                    max_retries=2,
                                )
                            )
                        
                        
                        if queue_:
                            queue_.put(
                                (
                                    cr,
                                    install_plan_attached_to_cr,
                                    backout_plan_availability_list,
                                    test_plan_availability_list,
                                )
                            )

                        thread = Thread(target=cr_wise_status_modifier_update_func, args=(
                            cr,
                            "Success"
                        ))
                        thread.start()
                        thread.join()

                    except:
                        thread = Thread(target=cr_wise_status_modifier_update_func, args=(
                            cr,
                            "Failed"
                        ))
                        thread.start()
                        thread.join()
                    i += 1
        
        except Exception as e:
            logs.append(
                f"Exception Occurred ({e.__class__.__name__})",
                f"{traceback.format_exc()}\n\n{e}",
            )
            raise

        finally:
            if glogs:
                for element in logs:
                    glogs.put(
                        _make_serializable(element)
                    )

            if page:
                page.close()

            if thread_context:
                thread_context.close()

            if thread_playwright_instance:
                thread_playwright_instance.stop()
                # keyboard.press_and_release("ctrl+c")
                del thread_playwright_instance

            # print(f"Batch {batch_number} finished and thread closing.")
            # 🔑 signal background threads to stop
            stop_event.set()


def run_download_tasks(
    batches: List[List[str|AnyStr]],
    cr_to_circle_dict: Dict[AnyStr, AnyStr],
    logs: List[AnyStr],
    user_email: AnyStr,
    runtime: Dict[Any, Any],
    task: Dict[Any, Any],
    timestamp_fn: Callable,
    date_: datetime
):
    global glogs

    session_created = False
    while not session_created:
        session_created, logs = pcm.session_maker(
            logs,
            task,
            False,
            runtime,
            timestamp_fn,
            user_email
        )
    if batches:
        batch_dict = {
            f"batch_{i}": batches[i] for i in range(len(batches))
        }

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    page_tasks,
                    i,
                    batch_dict[f"batch_{i}"],
                    cr_to_circle_dict,
                    date_
                )
                for i, batch in enumerate(batches)
            ]
        for future in futures:
                future.result()

    pcm.session_breaker()

    if glogs:
        while not glogs.empty():
            logs.append(glogs.get())

    return logs


def plan_files_downloader(
    unique_crs: List[str], 
    cr_to_circle_dict: Dict[str, str], 
    logs: List[str], 
    user_email: AnyStr,
    runtime: Dict[Any, Any],
    task: Dict[Any, Any],
    timestamp_fn: Callable,
    date_: datetime
) -> List[str]:
    assert isinstance(unique_crs, list)
    # print(f"{unique_crs = }")
    batch_creation_status, batches,logs = bm.main_method(unique_crs, logs)

    if batch_creation_status:
        logs.append("Batch creation successful")

    if batch_creation_status:
        number_of_batches = len(batches)
        logs.append(f"Got {number_of_batches} batches and now downloading the backout plans and install plans in batches")

    logs = run_download_tasks(batches, cr_to_circle_dict, logs, user_email, runtime, task, timestamp_fn, date_)
    
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
    global workbook_parent
    global queue_

    queue_ = Queue()
    glogs = Queue()

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
                    transaction.on_commit(lambda: sync_replica_task(), using='default')

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

        selected_data_df = selected_data_df.loc[
            selected_data_df["CR No"].astype(str).str.strip().isin(cr_wise_status_df["cr_no"].astype(str).str.strip().tolist())
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
        unique_crs = list(
            planning_sheet_df["CR No"].astype(str).str.strip().unique()
        )

        cr_to_circle_dict = dict(
            zip(
                planning_sheet_df["CR No"].astype(str).str.strip(),
                planning_sheet_df["Circle"].astype(str).str.strip(),
            )
        )

        workbook_parent = os.getenv("PLAN_FILES_DOWNLOAD_FOLDER").format(date_.strftime("%d-%b-%y"))
        os.makedirs(workbook_parent,exist_ok=True)
        
        GLOBAL_LOGS = plan_files_downloader(
            unique_crs, cr_to_circle_dict, GLOBAL_LOGS, user_email, runtime, task, timestamp_fn, date_
        )

    except Exception as e:
        GLOBAL_LOGS.append(
            f"{traceback.format_exc()}\n{e.__class__.__name__}\n{e}"
        )
        raise
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
            "download_name": str(os.getenv("CR_HYGIENE_CHECKS_FILE")).format(parsed_date.strftime("%d-%b-%y")),
            "counts": {},
        }
