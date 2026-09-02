import os
import time
import pandas as pd
from io import StringIO
import traceback
import pythoncom
import rootutils
import inspect
from bs4 import BeautifulSoup as beautifulsoup
from dashboard.views import _timestamp
from django.conf import settings
from playwright.sync_api import (
    Page,
    expect,
    sync_playwright,
    Playwright,
    BrowserContext,
    Browser,
    TimeoutError,
    Frame,
    FrameLocator,
    Locator,
)
from collections.abc import Callable
from django.conf import settings
from datetime import datetime, timedelta, date
from dateutil import parser
from pathlib import Path
from typing import Union, Tuple, List, Literal, AnyStr
import threading
import  dateutil.parser as dp

def request_password_from_user(runtime, task, logs, timestamp_fn, timeout=300):
    """
    Pauses the Playwright thread until the user submits a password
    via the Django iframe form, then returns the password.
    Uses separate pwd_event / pwd fields so it doesn't clash with OTP.
    """
    print("Inside request_password_from_user")
    if runtime is None:
        raise Exception("runtime not provided; cannot request password from user")

    task_name = task["name"] if task else "Task"

    # 1. Reset the event and flag so the frontend opens the iframe
    pwd_event = runtime.get("pwd_event")
    if pwd_event is None:
        pwd_event = threading.Event()
        runtime["pwd_event"] = pwd_event

    pwd_event.clear()                  # ensure not pre-set from a previous run
    runtime["password"] = None
    runtime["password_required"] = True   # <-- dashboard.js polling opens the iframe
    runtime["status"] = "Waiting for Password"

    logs.append(f"{task_name}: waiting for password from user ---- {timestamp_fn()}")
    print("🔑 Waiting for user to submit password via iframe...")
    print(f"🔎 [Playwright] Waiting on pwd_event id={id(pwd_event)}, runtime id={id(runtime)}")

    # 2. BLOCK this thread until the view calls pwd_event.set()
    got_it = pwd_event.wait(timeout=timeout)
    print("🔑 Password received")
    # 3. Reset flag so the iframe closes / stops re-opening
    runtime["password_required"] = False
    runtime["status"] = "Running"

    password = runtime.get("password")
    if not got_it or not password:
        logs.append(f"{task_name}: password not received in time ---- {timestamp_fn()}")
        raise Exception("Timed out waiting for password from user")

    print("🔑 Password received")
    logs.append(f"{task_name}: password received ---- {timestamp_fn()}")
    return str(password).strip()


def request_2fa_code_from_user(runtime, task, logs, timestamp_fn, timeout=300):
    if runtime is None:
        raise Exception("runtime not provided; cannot request 2FA from user")

    task_name = task["name"] if task else "Task"

    otp_event = runtime.get("otp_event")
    if otp_event is None:
        otp_event = threading.Event()
        runtime["otp_event"] = otp_event

    print(f"🔎 [Playwright] Waiting on event id={id(otp_event)}, runtime id={id(runtime)}")

    otp_event.clear()
    runtime["otp"] = None
    runtime["otp_required"] = True

    logs.append(f"{task_name}: waiting for 2FA code from user ---- {timestamp_fn()}")
    print("🔐 Waiting for user to submit 2FA code via iframe...")

    got_it = otp_event.wait(timeout=timeout)

    runtime["otp_required"] = False

    code = runtime.get("otp")
    if not got_it or not code:
        logs.append(f"{task_name}: 2FA code not received in time ---- {timestamp_fn()}")
        raise Exception("Timed out waiting for 2FA verification code from user")

    print(f"🔐 2FA code received: {code}")
    logs.append(f"{task_name}: 2FA code received ---- {timestamp_fn()}")
    return str(code).strip()


def get_browser() -> str:
    print("Inside get browser")
    
    print("Browser path ", os.path.join(str(os.environ["PROJECT_ROOT"]) , str(os.getenv("BROWSER_PATH"))))
    return os.path.join(str(os.environ["PROJECT_ROOT"]) , str(os.getenv("BROWSER_PATH")))

def get_itsm_session_file_path() -> str:
    return os.path.join(str(os.environ["PROJECT_ROOT"]) , str(os.getenv("ITSM_SESSION_FILE")))


def call_with_modal_ack(func, *args, max_retries=3, **kwargs):
    """
    Calls a function that may trigger a popup iframe.
    Detects popup, mutates args, retries, and returns updated args.
    """
    print("inside call_with_modal_ack\n")
    try:
        sig = inspect.signature(func)
        print(f"{sig =}\n\n")
        bound = sig.bind(*args, **kwargs)
        print(f"{bound =}\n\n")
        bound.apply_defaults()
    except TypeError as e:
        print(f"BINDING FAILED: {e}")
        raise
    except Exception as e:
        print(f"CALLING FAILED: {e}")
        raise
    else:
        print(f"{bound.arguments=}\n")
        earlier_value_of_token_for_locking = bound.arguments["token_for_locking"]
        availability_list = updated_token = updated_logs = None
        for attempt in range(1, max_retries + 1):
            result = func(*bound.args, **bound.kwargs)
            availability_list, updated_token, updated_logs = result
            print(f"{result=}\n")

            # allow iframe watcher to act
            # page.wait_for_timeout(300)

            # popup = read_and_reset_popup_state(page)

            # if not popup["handled"]:
            #     return result, dict(bound.arguments)["token_for_locking"]

            # print(f"⚠️ Popup handled ({popup['type']}) in {func.__name__}, retry {attempt}")

            # # 🔁 mutate arguments ONLY when required
            # if popup["type"] == "confirm_save":
            #     if "token_for_locking" in bound.arguments:
            #         bound.arguments["token_for_locking"] = False
            #         print("🔁 token_for_locking → False")

            # retry with mutated args
            result_value_for_locking = result[1]
            # print(f"{attempt =}")
            if result_value_for_locking != earlier_value_of_token_for_locking:
                # print("increasing the value attempt variable")
                attempt += 1
                continue
                
        return availability_list, updated_token, updated_logs



def backout_plan_downloader(
    page: Page,
    folder_location: str,
    cr: str,
    cr_circle: str,
    token_for_locking: bool,
    date_: datetime,
    logs: List[str],
) -> Tuple[List[str], bool, List[str]]:
    try:
        test_plan_download_folder = os.path.join(
            folder_location,
            "Install_and_Backout_Plan_Files",
            f"{cr}_{cr_circle}",
            "Backout Plans",
        )

        text_attachment_locators = [
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[3]/fieldset/div/div[4]/textarea",
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[1]/textarea",
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[2]/textarea",
        ]

        Path.mkdir(Path(test_plan_download_folder), parents=True, exist_ok=True)

        wait_var = True
        # Waiting for the table to load
        while wait_var:
            if (
                page.locator(
                    "//div[@class='PageBody pbChrome']/div[@id='WIN_3_301389923']/div[@class='TableHdr']/table[@class='TableHdr']/tbody/tr/td[@class='TableHdrL']"
                ).text_content()
                == "Table has Not been Loaded"
            ):
                page.wait_for_timeout(1000)
            else:
                wait_var = False

        page.wait_for_load_state("load")
        page.wait_for_load_state("domcontentloaded")
        # page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)
        
        logs.append(
            f"Downloading and locking the Backout plans for cr: {cr}"
        )

        cr_wise_test_plan_availability_list = []

        if page.locator(
            "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Backout Plan']"
        ).first.is_visible():
            try:
                # Searching for the CR Test Plan details
                page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Backout Plan']"
                ).first.dblclick()

            except Exception as e:
                page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Backout Plan']"
                ).nth(0).dblclick()

            # page.wait_for_timeout(1000)
            if (
                page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Backout Plan']"
                )
                .nth(0)
                .is_visible()
            ):
                page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Backout Plan']"
                ).nth(0).dblclick()
            # Checking if Test Plan is attached or not
            # text_attachment = page.locator(
            #     "//fieldset/div/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/div[@arid='304247090']/textarea[@class='text sr ']"
            # ).input_value()
            # # print(f"CR: {text_attachment}")
            # if text_attachment == "<File Name>":
            #     cr_wise_test_plan_availability_list = [
            #         "Not Available",
            #         "Not Available",
            #     ]

            # else:
            #     # Downloading the attachment
            #     with page.expect_download() as neo_neo_popup_info:
            #         page.locator(
            #             "//fieldset/div/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/a/div[@class='btnimgdiv']/img[@id='reg_img_304252650']"
            #         ).click(timeout=5000)

            #     # page.wait_for_timeout(5000)

            #     download = neo_neo_popup_info.value

            #     if not os.path.exists(test_plan_download_folder):
            #         os.mkdir(test_plan_download_folder)

            #     cr_wise_test_plan_availability_list = [
            #         "Available",
            #         f"{text_attachment}",
            #     ]

            #     # print(f"downloading {text_attachment}")
            #     if os.path.exists(
            #         os.path.join(
            #             test_plan_download_folder,
            #             f"{text_attachment}",
            #         )
            #     ):
            #         os.remove(
            #             os.path.join(
            #                 test_plan_download_folder,
            #                 f"{text_attachment}",
            #             )
            #         )
            #     download.save_as(
            #         os.path.join(
            #             test_plan_download_folder,
            #             f"{text_attachment}",
            #         )
            #     )
            j = 0
            while j < len(text_attachment_locators):
                # print(f"value of iterator value {j = }")
                # text_attachment = page.locator(
                #     "//fieldset/div/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/div[@arid='304247090']/textarea[@class='text sr ']"
                # ).input_value()
                text_attachment = page.locator(text_attachment_locators[j]).input_value()
                # print(f"got the text attachment value {text_attachment}")
                if text_attachment == "<File Name>":
                    j += 1
                    continue

                else:
                    # Downloading the attachment
                    test_plan_found_attached = True
                    with page.expect_download() as neo_neo_popup_info:
                        page.locator(
                            "//fieldset/div/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/a/div[@class='btnimgdiv']/img[@id='reg_img_304252650']"
                        ).click()

                    # page.wait_for_timeout(5000)

                    download = neo_neo_popup_info.value

                    if not os.path.exists(test_plan_download_folder):
                        os.mkdir(test_plan_download_folder)

                    cr_wise_test_plan_availability_list = [
                        "Available",
                        f"{text_attachment}",
                    ]

                    # print(f"downloading {text_attachment}")
                    if os.path.exists(
                        os.path.join(
                            test_plan_download_folder,
                            f"{text_attachment}",
                        )
                    ):
                        os.remove(
                            os.path.join(
                                test_plan_download_folder,
                                f"{text_attachment}",
                            )
                        )
                    download.save_as(
                        os.path.join(
                            test_plan_download_folder,
                            f"{text_attachment}",
                        )
                    )
                    # print("test_plan downloaded")
                    # # Locking the test plan
                # print(f"{j = }")
                # print(f"{test_plan_found_attached =}")
                j += 1
                # # Locking the test plan

        else:
            cr_wise_test_plan_availability_list = [
                "Not Available (Backout Plan Entry Not Available)",
                "KPI Not Required",
            ]

        if token_for_locking:
            test_plan_to_be_locked = False
            test_plan_lock_button = page.locator(
                "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
            ).all()
            i = 0
            while i < len(test_plan_lock_button):
                if (
                    page.locator(
                        "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                    )
                    .nth(i)
                    .is_visible()
                ):
                    # CRQ000004668101
                    # print(
                    #     "{} page.locator(\"//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']\").is_disabled(){}".format(cr, page.locator("//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']").is_disabled())
                    # )
                    if (
                        not page.locator(
                            "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                        )
                        .nth(i)
                        .is_disabled()
                    ):
                        test_plan_to_be_locked = True
                        
                        # Locking the Backout Plan
                        # page.locator(
                        #     "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                        # ).nth(i).click(timeout=60000)
                        break
                i += 1

            # Saving the test plan
            if (
                test_plan_to_be_locked
                and page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Backout Plan']"
                ).first.is_visible()
            ):
                # print(f"cr test_plan_to_be_locked : {cr}")
                save_button_locators_for_test_plan = page.locator(
                    "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                ).all()
                i = 0
                while i < len(save_button_locators_for_test_plan):
                    if (
                        page.locator(
                            "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                        )
                        .nth(i)
                        .is_visible()
                    ):
                        # Saving the changes
                        # page.locator(
                        #     "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                        # ).nth(i).click(timeout=60000)
                        token_for_locking, logs = iframe_message_handler(
                            page, token_for_locking, logs
                        )
                        break
                    i += 1

    except Exception as e:
        logs.append(
            f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
        )

    
    return cr_wise_test_plan_availability_list, token_for_locking, logs


def install_plan_downloader(
    page: Page,
    folder_location: str,
    cr: str,
    cr_circle: str,
    need_install_plan: bool,
    token_for_locking: bool,
    date_: datetime,
    logs: List[str],
) -> Literal["Available", "Not Available"]:
    try:
        # print(f"Inside install_plan_downloader for cr {cr}")
        install_plan_attached_to_cr = "Not Available"
        page.wait_for_timeout(1000)
        page.wait_for_load_state("domcontentloaded")

        list_of_downloads_button = [
            "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[3]/fieldset/div/a[2]/div[@class='btnimgdiv']",
            "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[4]/fieldset/div/a[2]/div[@class='btnimgdiv']",
            "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[4]/fieldset/div/a[5]/div[@class='btnimgdiv']",
        ]

        install_plan_download_folder = os.path.join(
            folder_location,
            "Install_and_Backout_Plan_Files",
            f"{cr}_{cr_circle}",
            "Install Plans",
        )

        Path.mkdir(Path(install_plan_download_folder), parents=True, exist_ok=True)

        """
            Locking the install plans
        """

        # install_plan_locators = page.locator(
        #     "//div[@id='WIN_3_301389923' and @arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Install Plan']"
        # ).all()
        text_attachment_locators = [
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[3]/fieldset/div/div[4]/textarea",
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[1]/textarea",
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[2]/textarea",
        ]

        install_plan_found = False

        logs.append(
            f"Downloading and locking the Install plans for cr: {cr}"
        )

        # print(install_plan_locators)

        # i = 0
        # while i < len(install_plan_locators):
        #     page.locator(
        #         "//div[@id='WIN_3_301389923' and @arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Install Plan']"
        #     ).nth(i).dblclick()
            # print("Install Plan clicked")
            # text_attachment_locators = page.locator("//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@id='WIN_3_304247060' and @arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/div[@id='WIN_3_304247090' and @arid='304247090']/textarea[@class='text sr ']").all()
        
        page.locator(
                "//div[@id='WIN_3_301389923' and @arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Install Plan']"
            ).first.dblclick()
        
        j = 0
        while j < len(text_attachment_locators):
            # if page.locator("//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@id='WIN_3_304247060' and @arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/div[@id='WIN_3_304247090' and @arid='304247090']/textarea[@class='text sr ']").nth(l).is_visible():
            if page.locator(text_attachment_locators[j]).is_visible(timeout=10000):
                # text_attachment = page.locator("//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@id='WIN_3_304247060' and @arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/div[@id='WIN_3_304247090' and @arid='304247090']/textarea[@class='text sr ']").nth(l).input_value()
                text_attachment = page.locator(
                    text_attachment_locators[j]
                ).input_value()
                if text_attachment != "<File Name>":
                    install_plan_found = True

                    if need_install_plan:
                        with page.expect_download(timeout=60000) as download_info:
                            page.bring_to_front()
                            page.locator(list_of_downloads_button[j]).click()

                        download = download_info.value

                        if not os.path.exists(install_plan_download_folder):
                            os.mkdir(install_plan_download_folder)

                        if os.path.exists(
                            os.path.join(
                                install_plan_download_folder,
                                f"{text_attachment}",
                            )
                        ):
                            os.remove(
                                os.path.join(
                                    install_plan_download_folder,
                                    f"{text_attachment}",
                                )
                            )

                        download.save_as(
                            os.path.join(
                                install_plan_download_folder,
                                f"{text_attachment}",
                            )
                        )
                    install_plan_attached_to_cr = "Available"
            j += 1

        if install_plan_found and token_for_locking:
            install_plan_lock_locators = page.locator(
                "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
            ).all()

            j = 0
            while j < len(install_plan_lock_locators):
                if (
                    page.locator(
                        "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                    )
                    .nth(j)
                    .is_visible()
                ):
                    if (
                        not page.locator(
                            "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                        )
                        .nth(j)
                        .is_disabled()
                    ):
                        # locking the files
                        # page.locator(
                        #     "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                        # ).nth(j).click(timeout=60000)
                        break
                j += 1

            save_button_locators = page.locator(
                "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
            ).all()

            j = 0
            while j < len(save_button_locators):
                if (
                    page.locator(
                        "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                    )
                    .nth(j)
                    .is_visible()
                ):
                    # Saving the changes
                    # page.locator(
                    #     "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                    # ).nth(j).click(timeout=60000)
                    token_for_locking, logs = iframe_message_handler(
                        page, token_for_locking, logs 
                    )
                    break
                j += 1
            # i += 1

    except Exception as e:
        logs.append(
            f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
        )

    return install_plan_attached_to_cr, token_for_locking, logs



def test_plan_downloader(
    page: Page,
    folder_location: str,
    cr: str,
    cr_circle: str,
    token_for_locking: bool,
    date_: datetime,
    logs:list
) -> Tuple[List[AnyStr], bool, list]:
    try:
        test_plan_download_folder = os.path.join(
            folder_location,
            "Install_and_Backout_Plan_Files",
            f"{cr}_{cr_circle}",
            "Test Plans",
        )

        text_attachment_locators = [
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[3]/fieldset/div/div[4]/textarea",
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[1]/textarea",
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[2]/textarea",
        ]

        Path.mkdir(Path(test_plan_download_folder), parents=True, exist_ok=True)

        wait_var = True
        # Waiting for the table to load
        while wait_var:
            if (
                page.locator(
                    "//div[@class='PageBody pbChrome']/div[@id='WIN_3_301389923']/div[@class='TableHdr']/table[@class='TableHdr']/tbody/tr/td[@class='TableHdrL']"
                ).text_content()
                == "Table has Not been Loaded"
            ):
                page.wait_for_timeout(1000)
            else:
                wait_var = False

        page.wait_for_load_state("load")
        page.wait_for_load_state("domcontentloaded")
        # page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)
        
        logs.append(
            f"Downloading and locking the Test plans for cr: {cr}"
        )

        cr_wise_test_plan_availability_list = []

        if page.locator(
            "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Test Plan']"
        ).first.is_visible():
            try:
                # Searching for the CR Test Plan details
                page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Test Plan']"
                ).first.dblclick()

            except Exception as e:
                page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Test Plan']"
                ).nth(0).dblclick()

            page.wait_for_timeout(1000)
            if (
                page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Test Plan']"
                )
                .nth(0)
                .is_visible()
            ):
                page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Test Plan']"
                ).nth(0).dblclick()
            
            # print("Line 2170")
            # Checking if Test Plan is attached or not
            test_plan_found_attached = False
            j = 0
            while j < len(text_attachment_locators):
                # print(f"value of iterator value {j = }")
                # text_attachment = page.locator(
                #     "//fieldset/div/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/div[@arid='304247090']/textarea[@class='text sr ']"
                # ).input_value()
                text_attachment = page.locator(text_attachment_locators[j]).input_value()
                # print(f"got the text attachment value {text_attachment}")
                if text_attachment == "<File Name>":
                    j += 1
                    continue

                else:
                    # Downloading the attachment
                    test_plan_found_attached = True
                    with page.expect_download() as neo_neo_popup_info:
                        page.locator(
                            "//fieldset/div/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/a/div[@class='btnimgdiv']/img[@id='reg_img_304252650']"
                        ).click()

                    # page.wait_for_timeout(5000)

                    download = neo_neo_popup_info.value

                    if not os.path.exists(test_plan_download_folder):
                        os.mkdir(test_plan_download_folder)

                    cr_wise_test_plan_availability_list = [
                        "Available",
                        f"{text_attachment}",
                    ]

                    # print(f"downloading {text_attachment}")
                    if os.path.exists(
                        os.path.join(
                            test_plan_download_folder,
                            f"{text_attachment}",
                        )
                    ):
                        os.remove(
                            os.path.join(
                                test_plan_download_folder,
                                f"{text_attachment}",
                            )
                        )
                    download.save_as(
                        os.path.join(
                            test_plan_download_folder,
                            f"{text_attachment}",
                        )
                    )
                    # print("test_plan downloaded")
                    # # Locking the test plan
                # print(f"{j = }")
                # print(f"{test_plan_found_attached =}")
                j += 1
                # print(f"incrememnted value of {j = }")

            if not test_plan_found_attached:
                cr_wise_test_plan_availability_list = [
                        "Not Available",
                        "Not Available",
                    ]
            # print("broke the loop")
        else:
            cr_wise_test_plan_availability_list = [
                "Not Available (Test Plan Entry Not Available)",
                "KPI Not Required",
            ]

        if token_for_locking:
            test_plan_to_be_locked = False
            test_plan_lock_button = page.locator(
                "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
            ).all()
            i = 0
            while i < len(test_plan_lock_button):
                if (
                    page.locator(
                        "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                    )
                    .nth(i)
                    .is_visible()
                ):
                    # CRQ000004668101
                    # print(
                    #     "{} page.locator(\"//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']\").is_disabled(){}".format(cr, page.locator("//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']").is_disabled())
                    # )
                    if (
                        not page.locator(
                            "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                        )
                        .nth(i)
                        .is_disabled()
                    ):
                        test_plan_to_be_locked = True
                        # page.locator(
                        #     "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                        # ).nth(i).click(timeout=60000)
                        break
                i += 1

            # Saving the test plan
            if (
                test_plan_to_be_locked
                and page.locator(
                    "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Test Plan']"
                ).first.is_visible()
            ):
                # print(f"cr test_plan_to_be_locked : {cr}")
                save_button_locators_for_test_plan = page.locator(
                    "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                ).all()
                i = 0
                while i < len(save_button_locators_for_test_plan):
                    if (
                        page.locator(
                            "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                        )
                        .nth(i)
                        .is_visible()
                    ):
                        # page.locator(
                        #     "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                        # ).nth(i).click(timeout=60000)
                        token_for_locking, logs = iframe_message_handler(
                            page, token_for_locking, logs
                        )
                        break
                    i += 1

    except Exception as e:
        logs.append(
            f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
        )

    
    # print(f"returning values =>{cr_wise_test_plan_availability_list = }, {token_for_locking = }")
    return cr_wise_test_plan_availability_list, token_for_locking, logs

def bpms_tasks_tab_getter(
    cr: str, 
    page: Page, 
) -> Tuple[AnyStr, pd.DataFrame]:
    page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")
    
    first_table_df = pd.DataFrame()
    
    page.locator(
        "//div[@class='TabsViewPort']/div/dl[@class='OuterOuterTab']/dd[@class='OuterTab']/span[@class='Tab']/a[text()='Tasks']"
    ).click(modifiers=["Control"], button="left", delay=1000)
    
    page.wait_for_load_state(state="domcontentloaded")
    page.wait_for_load_state(state="load")
    
    # first_table_xpath = "//fieldset[@arwindowid='3']/div[@arwindowid='3']/div/div/div[@arwindowid='3']/fieldset/div/div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']"
    # first_table_xpath = "//fieldset/div/div/div/div/fieldset/div/div/div[@class='TableInner']/div[@class='BaseTableOuter']"
    # first_table_xpath = "//fieldset/div/div/div/div/div[3]/fieldset/div/div/fieldset[1]/div[2]/div/div/div[2]/fieldset/div/div/div[2]/div"
    lld_locator = "//fieldset/div/div/div/div/fieldset/div/div/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table/tbody/tr/td/nobr/span[contains(.,'LLD Automation')]"
    # logs.append(
    #     f"Getting the bpms technical design attachment name for cr: {cr}"
    # )
    
    page.wait_for_load_state(state="domcontentloaded")
    page.wait_for_load_state(state="load")
    
    count = 0
    while count < 3:
        # if page.locator(first_table_xpath).is_visible():
        if page.locator(lld_locator).is_visible():
            break
        else:
            page.wait_for_timeout(1000)
        count += 1
    
    # print(f"{page.locator(first_table_xpath).first.is_visible() = }")
    # if page.locator(first_table_xpath).is_visible():
    if page.locator(lld_locator).is_visible():
        elements_locator = page.locator(
            lld_locator
        ).locator("xpath=../..").locator("xpath=../..").locator("xpath=../..").locator("xpath=..").inner_html()
        
        df_list = pd.read_html(StringIO(elements_locator))
        # pprint(df_list)
        first_table_df = df_list[0]
        
        if len(df_list) == 0:
            _, first_table_df = bpms_tasks_tab_getter(cr, page)
            
        elif len(df_list) > 0:
            first_table_df = df_list[0]
        
    return cr, first_table_df


def bpms_auto_crs_tasks_lld_automation_handler(
    cr: str,
    page: Page,
    folder_location: str,
    cr_circle: str,
    date_: datetime,
    logs: list
) -> Tuple[AnyStr, AnyStr, list]:
    
    page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")
    
    page.locator(
        "//div[@class='TabsViewPort']/div/dl[@class='OuterOuterTab']/dd[@class='OuterTab']/span[@class='Tab']/a[text()='Tasks']"
    ).click(modifiers=["Control"], button="left", delay=1000)
    
    page.wait_for_load_state(state="domcontentloaded")
    page.wait_for_load_state(state="load")
    
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_load_state('load')
    page.wait_for_timeout(1000)
    attachment_ = ""
    lld_locator = "//fieldset/div/div/div/div/fieldset/div/div/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table/tbody/tr/td/nobr/span[contains(.,'LLD Automation')]"

    lld_design_download_path = os.path.join(
        folder_location,
        "Install_and_Backout_Plan_Files",
        f"{cr}_{cr_circle}",
        "Auto_Technical_Design"
    )

    Path(lld_design_download_path).mkdir(parents=True, exist_ok=True)
    
    if page.locator(lld_locator).first.is_visible():
        # print("locator_found")
        page.locator(lld_locator).first.hover()
        page.locator(lld_locator).first.click()
        # page.locator(lld_locator).first.click(modifiers=['Control'], button='left', delay=1000)
        # page.wait_for_timeout(1000)
        # general_information_entries_locator = "//fieldset[3]/div/div/div/div[4]/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/div/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table/tbody/tr/td[@title='General Information']/nobr/span[normalize-space()='General Information']"
        general_information_entries_locator = "//fieldset[3]/div[2]/div/div/div[4]/fieldset/div/div/div[2]/div/div[2]/table/tbody/tr/td[1]/nobr/span[text()='General Information']"
        
        # page.wait_for_load_state('load')
        # page.wait_for_load_state('domcontentloaded')
        # page.wait_for_timeout(1000)
        # all_general_insurance_entries = page.locator(general_information_entries_locator).all()
        # print("Line 806")
        # print(page.locator(general_information_entries_locator).count())
        
        target_entries = page.locator(general_information_entries_locator)
    
        # 2. THE FIX: Wait specifically for the first element to attach to the DOM.
        # It will poll the DOM dynamically and proceed the millisecond it appears.
        # try:
        #     target_entries.first.wait_for(state="attached", timeout=10000) # Waits up to 10 seconds
        # except Exception as e:
        #     print(f"Failed to find elements within 10 seconds. Error: {e}")
        
        # print(page.locator(general_information_entries_locator).count())
        # page.locator(general_information_entries_locator).last.hover()
        
        if page.locator(general_information_entries_locator).last.is_visible():
            # print("Line Number 821")
            page.locator(general_information_entries_locator).last.dblclick()
            
            # iframe_element = page.wait_for_selector("//iframe[@src='/arsys/forms/helixitsm-01/TMS%3AWorkInfo/Default+User+View/?cacheid=43b69c09&format=html']")
            page.wait_for_selector("//table[@id='DivTable']//iframe")
            frame = page.frame_locator("//table[@id='DivTable']//iframe")
            
            
            # frame = iframe_element.content_frame()
            locator_for_attachment = "//div[1]/div[5]/div[11]/div[2]/div/div[2]/table/tbody/tr[2]/td[1]/nobr/span"
            
            count = 0
            while count < 3:
                if frame.locator(locator_for_attachment).is_visible():
                    break
                else:
                    try:
                        page.wait_for_timeout(1000)
                    except:
                        count+= 1
                        continue
                count += 1
            
            if frame.locator(locator_for_attachment).is_visible():
                # print("Line Number 833")
                attachment_ = frame.locator(locator_for_attachment).inner_text()
                
                if len(str(attachment_).strip()) > 0:
                    # print("Line Number 837")
                    frame.locator(locator_for_attachment).click()
                    
                    save_to_disk_button_locator = "//div/div/div/div/table/tbody/tr/td/a[text()='Save to Disk']"
                    
                    if not os.path.exists(lld_design_download_path):
                        os.makedirs(lld_design_download_path, exist_ok=True)
                    
                    if frame.locator(save_to_disk_button_locator).is_visible():
                        with page.expect_download(timeout=60000) as download_info:
                            # frame.bring_to_front()
                            frame.locator(save_to_disk_button_locator).click()
                        download = download_info.value
                        
                        if os.path.exists(
                            os.path.join(
                                lld_design_download_path,
                                f"{attachment_}"
                            )
                        ):
                            os.remove(
                                os.path.join(
                                    lld_design_download_path,
                                    f"{attachment_}"
                                )
                            )
                        download.save_as(
                            os.path.join(
                                lld_design_download_path,
                                f"{attachment_}"
                            )
                        )
                            
            if frame is not None:
                frame.locator("//div/div/a/div/div[normalize-space()='Close']").click()
                            
    return cr, attachment_, logs


def bpms_crs_attachment_name_getter(
    cr: str,
    page: Page,
    logs:list
) -> Tuple[AnyStr, AnyStr, list]:
    attachment_name = ""
    try:
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_load_state('load')
        
        list_of_downloads_button = [
                "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[3]/fieldset/div/a[2]/div[@class='btnimgdiv']",
                # "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[4]/fieldset/div/a[2]/div[@class='btnimgdiv']",
                # "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[4]/fieldset/div/a[5]/div[@class='btnimgdiv']",
            ]
        
        text_attachment_locators = [
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[3]/fieldset/div/div[4]/textarea",
            # "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[1]/textarea",
            # "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[2]/textarea",
        ]
        
        logs.append(
            f"Getting the bpms technical design attachment name for cr: {cr}"
        )
        
        page.locator(
                "//div[@id='WIN_3_301389923' and @arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Technical Design']"
            ).first.dblclick()
        
        j = 0
        while j < len(text_attachment_locators):
            if page.locator(text_attachment_locators[j]).is_visible():
                text_attachment = page.locator(
                    text_attachment_locators[j]
                ).input_value()
                if text_attachment != "<File Name>":
                    attachment_name = text_attachment
            j += 1
    
    except Exception as e:
        logs.append(
            f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
        )
    
    return cr, attachment_name, logs
            

def bpms_manual_crs_attachment_downloader(
    cr: str,
    folder_location: str,
    cr_circle: str,
    page: Page,
    date_:datetime, 
    logs:list
) -> Tuple[AnyStr, AnyStr, list]:
    attachment_name = ""
    try:
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_load_state('load')
        
        lld_design_download_path = os.path.join(
            folder_location,
            "Install_and_Backout_Plan_Files",
            f"{cr}_{cr_circle}",
            "Manual_Technical_Design"
        )

        Path(lld_design_download_path).mkdir(parents=True, exist_ok=True)
        
        list_of_downloads_button = [
                "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[3]/fieldset/div/a[2]/div[@class='btnimgdiv']",
                # "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[4]/fieldset/div/a[2]/div[@class='btnimgdiv']",
                # "//fieldset/div/div/fieldset[1]/div[2]/div/div/div[4]/fieldset/div/a[5]/div[@class='btnimgdiv']",
            ]
        
        text_attachment_locators = [
            "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[3]/fieldset/div/div[4]/textarea",
            # "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[1]/textarea",
            # "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[2]/textarea",
        ]
        
        logs.append(
            f"Getting the bpms technical design attachment name for cr: {cr}"
        )
        
        page.locator(
                "//div[@id='WIN_3_301389923' and @arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'Technical Design']"
            ).first.dblclick()
        
        j = 0
        while j < len(text_attachment_locators):
            # if page.locator("//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@id='WIN_3_304247060' and @arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/div[@id='WIN_3_304247090' and @arid='304247090']/textarea[@class='text sr ']").nth(l).is_visible():
            if page.locator(text_attachment_locators[j]).is_visible(timeout=10000):
                # text_attachment = page.locator("//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div[@class='PageHolderStackViewResizable']/div[@class='PageHolderStackViewFixedCV']/div[@id='WIN_3_304247060' and @arid='304247060']/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome' ]/div[@id='WIN_3_304247090' and @arid='304247090']/textarea[@class='text sr ']").nth(l).input_value()
                text_attachment = page.locator(
                    text_attachment_locators[j]
                ).input_value()
                
                if text_attachment != "<File Name>":
                    attachment_name = text_attachment
                    with page.expect_download(timeout=60000) as download_info:
                        page.bring_to_front()
                        page.locator(list_of_downloads_button[j]).click()
                        
                    download = download_info.value
                    
                    if not os.path.exists(lld_design_download_path):
                        os.makedirs(lld_design_download_path, exist_ok=True)
                    
                    # print(f"{os.path.exists(lld_design_download_path) =}")
                    
                    if os.path.exists(
                        os.path.join(
                            lld_design_download_path,
                            f"{text_attachment}",
                        )
                    ):
                        os.remove(
                            os.path.join(
                                lld_design_download_path,
                                f"{text_attachment}",
                            )
                        )

                    download.save_as(
                        os.path.join(
                            lld_design_download_path,
                            f"{text_attachment}",
                        )
                    )
            j += 1

        
    except Exception as e:
        logs.append(
            f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
        )
    
    return cr, attachment_name, logs


def bpms_file_correction_file_upload(
    cr: str, 
    corrected_file_path: str,
    page: Page,
    runtime: dict,
    logs: list
) -> Tuple[AnyStr, AnyStr, list]:
    result = "Failure"
    page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")
    
    runtime["status"] = "Starting to upload the corrected file"
    logs.append(
        f"Starting to upload the corrected file for cr: {cr}"
    )
    logs = search_for_cr(cr, page, logs)

    try:
        wait_var = True

        # Waiting for the table to load
        while wait_var:
            if (
                page.locator(
                    "//div[@class='PageBody pbChrome']/div[@id='WIN_3_301389923']/div[@class='TableHdr']/table[@class='TableHdr']/tbody/tr/td[@class='TableHdrL']"
                ).text_content()
                == "Table has Not been Loaded"
            ):
                page.wait_for_timeout(1000)
            else:
                wait_var = False

        # Clicking on More Info
        page.wait_for_selector('//textarea[@id="arid_WIN_3_304247080"]')
        
        page.locator(
            '//textarea[@id="arid_WIN_3_304247080"]'
        ).fill('Updated Manual DLD/Design')
        
        # page.wait_for_selector(
        #     '//div/a[@id="WIN_3_304247100"]/div'
        # )
        
        page.wait_for_selector(
            '//img[@id="reg_img_304247100"]'
        )
        
        page.locator(
            '//img[@id="reg_img_304247100"]'
        ).click()
        
        page.wait_for_selector("//table[@id='DivTable']//iframe")
        frame = page.frame_locator("//table[@id='DivTable']//iframe")
        locator_for_choosing_the_file = '//table/tbody/tr/td/form/table/tbody/tr/td[2]/input[@id="PopupAttInput"]'
        
        ok_button_locator = '//div[@id="PopupAttFooter"]/a[text()="OK"]'
        
        count = 0
        while count < 3:
            if frame.locator(locator_for_choosing_the_file).is_visible():
                break
            else:
                try:
                    page.wait_for_timeout(1000)
                except:
                    count+= 1
                    continue
            count += 1
        # print(f"\n{frame.locator(locator_for_choosing_the_file).is_visible() = }\n")
        if frame.locator(locator_for_choosing_the_file).is_visible():
            # print(f"\n{frame.locator(locator_for_choosing_the_file) = }")
            # with page.expect_file_chooser(timeout=60000) as fc_info:
            #     frame.locator(locator_for_choosing_the_file).hover()
            #     frame.locator(locator_for_choosing_the_file).click(button='left', click_count=2, force=True)
            # print("Line 1153")
            # file_chooser = fc_info.value
            # file_chooser.set_files(corrected_file_path)
            frame.locator(locator_for_choosing_the_file).set_input_files(corrected_file_path)
        
        if frame is not None:
            frame.locator(ok_button_locator).click()
        
        result = "Success"

        # Clicking on More Info
        page.locator(
            "//div/fieldset[@class='PageBodyHorizontal']/div[@class='PageBody pbChrome']/div/fieldset/div[@arid='304196500']/div/div/div/div/a[@class='pagebtn ']/span[@class='Twisty Tsize']"
        ).click()

        # Selecting Info
        page.locator(
            "//div/fieldset/div[@class='PageBody pbChrome']/div[@arid='304247210']/div[@class='selection']/a[@class='btn btn3d selectionbtn']"
        ).click()
        
        page.wait_for_selector(
            "//div[@class='MenuOuter']/div[@class='MenuTableContainer']/table[@class='MenuTable']/tbody/tr/td"
        )
        page.locator(
            "//div[@class='MenuOuter']/div[@class='MenuTableContainer']/table[@class='MenuTable']/tbody/tr/td",
            has_text="Technical Design",
        ).click()
        
        # Locking the Design
        # page.locator(
        #     "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
        # ).click()
        
        # Setting View Access Public
        page.locator(
            '//fieldset/div/div/fieldset/div[@class="radio "]/span[2]/input[@value="1" and @id="WIN_3_rc1id1000000761"]'
        ).click()
        
        # Clicking on 'Add' button
        page.locator(
            "//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/a[@arid='304247110']/div[@class='btntextdiv']"
        ).click()
    
    except Exception as e:
        result = "Failure"
        # print(f"Error occurred while filling MOP attachment for CR {cr}: {e}")
        logs.append(
            f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
        )
        raise
    return cr, result, logs


def raw_report_downloader(
    context: BrowserContext,
    page: Page,
    logs: list,
    task:dict|None=None,
    runtime:dict|None=None,
    timestamp_fn:Callable=_timestamp,
    date_: datetime|date|str|None = None,
) -> list:
    # date_1 = ""
    # date_2 = ""
    runtime["status"] = "Running"
    task_name = task["name"] if task else "Task"
    
    if date_ is None:
        # print(datetime.now())
        date_1 = f"{((datetime.now()).replace(hour=20, minute=0, second=0)).strftime('%m/%d/%Y %H:%M:%S')}"
        date_2 = f"{((datetime.now() + timedelta(days=1)).replace(hour=8, minute=0, second=0)).strftime('%m/%d/%Y %H:%M:%S')}"

    else:
        if isinstance(date_, datetime):
            pass
        elif isinstance(date_, date):
            date_ = datetime(date_.year, date_.month, date_.day)
        elif isinstance(date_, str):
            date_ = parser.parse(date_)

        date_1 = f"{date_.replace(hour=20, minute=0, second=0).strftime('%m/%d/%Y %H:%M:%S')}"
        date_2 = f"{(date_ + timedelta(days=1)).replace(hour=8, minute=0, second=0).strftime('%m/%d/%Y %H:%M:%S')}"


    folder_date = (dp.parse(date_1)).strftime("%d-%b-%y")

    folder = str(os.getenv("RAW_REPORT_DOWNLOAD_FOLDER")).format(folder_date)
    
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    
    advanced_search_query = f"""('Scheduled Start Date+' >= "{date_1}" AND 'Scheduled End Date+' <= "{date_2}") AND ('Coordinator Group*+' = "SRF-Packet Core CM Delhi" OR 'Coordinator Group*+' = "SRF-VAS CM Delhi")"""
    # print("\n\n", advanced_search_query, end="\n\n")
    counter = 0
    # clicking the advanced search button
    while not page.locator(
        "//fieldset/div/div/div/div/table/tbody/tr/td/a[@class='advancedsearch btn btn3d tbbtn' and @arwindowid='3']/div[@id='TBadvancedsearch']"
    ).is_visible() and counter < 10:
        page.wait_for_timeout(1000)
        counter += 1
    
    page.locator(
        "//fieldset/div/div/div/div/table/tbody/tr/td/a[@class='advancedsearch btn btn3d tbbtn' and @arwindowid='3']/div[@id='TBadvancedsearch']"
    ).click()

    page.wait_for_selector(
        '//fieldset/div/div/div/div[@id="QueryBar" and @arwindowid="3"]/table/tbody/tr/td/textarea[@id="arid1005"]'
    )
    page.locator(
        '//fieldset/div/div/div/div[@id="QueryBar" and @arwindowid="3"]/table/tbody/tr/td/textarea[@id="arid1005"]'
    ).fill(advanced_search_query)

    page.locator(
        "//table/tbody/tr/td[@class='TBGroup TBGroup0']/a[@arwindowid = '3']/div[@id='TBsearchsavechanges']",
        has_text="Search",
    ).click()
    page.locator(
        "//div[@class='TableFtr']/table[@class='TableFtr']/tbody/tr/td[@class='TableFtrL']/a[@class='SelAll btn btn3d TableBtn' and text()='Select All']"
    ).click()

    with context.expect_page() as popup_info:
        page.locator(
            "//div[@class='TableFtr']/table[@class='TableFtr']/tbody/tr/td[@class='TableFtrL']/a[@class= 'Rep btn btn3d TableBtn']",
            has_text="Report",
        ).click()

    popup = popup_info.value
    popup.wait_for_load_state()

    popup.locator(
        "//table[@id='T93250']/tbody/tr/td/nobr[@class='dp ']/span[text()='SRF-PS_Core']",
        has_text="SRF-PS_Core",
    ).click()

    popup.locator(
        "//div[@arid='2000053' and @id='WIN_0_2000053']/div[@class='selection']/input[@id = 'arid_WIN_0_2000053']"
    ).click()
    popup.locator(
        "//div[@class='MenuOuter']/div[@class='MenuTableContainer']/table[@class='MenuTable']/tbody[@class='MenuTableBody']/tr[@class='MenuTableRow']/td[@class='MenuEntryName' or @class='MenuEntryNameHover']",
        has_text="File",
    ).hover()
    popup.locator(
        "//div[@class='MenuOuter']/div[@class='MenuTableContainer']/table[@class='MenuTable']/tbody[@class='MenuTableBody']/tr[@class='MenuTableRow']/td[@class='MenuEntryName' or @class='MenuEntryNameHover']",
        has_text="File",
    ).click()

    popup.locator(
        "//div[@arid='2000056' and @id='WIN_0_2000056']/div[@class='selection']/input[@id = 'arid_WIN_0_2000056']"
    ).click()
    popup.locator(
        "//div[@class='MenuOuter']/div[@class='MenuTableContainer']/table[@class='MenuTable']/tbody[@class='MenuTableBody']/tr[@class='MenuTableRow']/td[@class='MenuEntryName' or @class='MenuEntryNameHover']",
        has_text="CSV",
    ).hover()
    popup.locator(
        "//div[@class='MenuOuter']/div[@class='MenuTableContainer']/table[@class='MenuTable']/tbody[@class='MenuTableBody']/tr[@class='MenuTableRow']/td[@class='MenuEntryName' or @class='MenuEntryNameHover']",
        has_text="CSV",
    ).click()

    popup.locator(
        '//fieldset/div/div/fieldset/div[@id="WIN_0_2000054"]/a[@class="btn btn3d menu"]'
    ).click()
    popup.locator(
        '//div/div[@class="MenuTableContainer"]/table[@class="MenuTable"]/tbody/tr/td[text()="Unicode (UTF-8)"]'
    ).click()

    with popup.expect_download() as neo_popup_info:
        popup.locator(
            "//a[@artype='Control']/div[@class='btnimgdiv']/img[@id='reg_img_93272']"
        ).click()

    download = neo_popup_info.value
    
    runtime["status"]="Dowloading the Raw Report"

    logs.append(f"{task_name}: [{timestamp_fn}] :: Downloading the Raw Report")

    report_file_date = (dp.parse(date_1))

    if os.path.exists(
        os.path.join(folder, f"PS_Core_Raw_Report_{report_file_date.strftime('%Y-%m-%d')}.csv")
    ):
        os.remove(
            os.path.join(folder, f"PS_Core_Raw_Report_{report_file_date.strftime('%Y-%m-%d')}.csv")
        )
    download.save_as(
        os.path.join(folder, f"PS_Core_Raw_Report_{report_file_date.strftime('%Y-%m-%d')}.csv")
    )

    # time.sleep(2)
    logs.append(f"{task_name}: [{timestamp_fn}] :: Downloaded the Raw Report")
    runtime["status"]="Dowloaded the Raw Report"

    popup.close(run_before_unload=True)

    return logs


def login_to_itsm(
    page: Page, logs: list, runtime: dict, task: dict, timestamp_fn: Callable, user_email: str = None
):
    # if folder is None:
    #     folder = str(Path(__file__).parent.parent)
    # username = os.getlogin().upper().strip()
    # __itsm_data = ITSM_Password_Fetcher().fetch
    # username = __itsm_data["username"]
    # password = __itsm_data["password"]
    # page.locator("//input[@id='login']").fill(username)
    # password = str(os.getenv("PASSWORD")) if str(os.getenv("PASSWORD")) else ""
    # if password is None and folder is not None:
    #     with open(os.path.join(folder, "planning.txt"), "r") as f:
    #         password = f.readline().strip()
    # page.locator("//input[@id='passwd']").fill(str(password).strip())

    # clicking the logon button
    # page.locator("//a[@id='loginBtn']", has_text="Log On").click()

    resolved_user_email = user_email or str(os.getenv('EMAIL_USERNAME'))
    
    if not user_email:
        logs.append(f"Warning: no user email provided, falling back to EMAIL_USERNAME env var ---- {timestamp_fn()}")

    # Filling the user name
    page.locator('//div/input[@id="i0116"]').fill(resolved_user_email)
    page.locator('//div/input[@id="idSIButton9"]').click()
    
    page.wait_for_load_state("load", timeout=60000)
    page.wait_for_selector('//div/input[@id="i0118"]', state="visible", timeout=10000)
    # if page.locator('//div/input[@id="i0118"]').is_visible():
    #     page.locator('//div/input[@id="i0118"]').fill(str(password).strip())
    #     page.locator('//div/input[@id="idSIButton9"]').click()
    #     page.wait_for_load_state("load", timeout=60000)
    return request_password_from_user(runtime, task, logs, timestamp_fn)


def iframe_message_handler(
    page: Page,
    token_for_locking: bool,
    logs: list,
) -> Tuple[bool, list]:
    result = token_for_locking
    try:
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_load_state("load")

        # print("\n\n Inside Iframe Handler")
        page_iframe = page.frame_locator(
            "iframe[src='https://ticketing-in.managed-services.prod.sdt.ericsson.net/arsys/resources/html/MessagePopup.html']"
        )
        if page_iframe is not None:
            if page_iframe.locator(
                "//a[contains(@class,'PopupBtn') and normalize-space()='No']|//a[contains(@class,'PopupBtn') and normalize-space()='OK']|//a[contains(@class,'PopupBtn') and normalize-space()='Ok']"
            ).is_visible():
                if page_iframe.locator(
                    "//a[@class='btn btn3d PopupBtn' and normalize-space()='No']"
                ).is_visible():
                    # print("Found No Button in Popup")
                    page_iframe.locator(
                        "//a[@class='btn btn3d PopupBtn' and text()='No']"
                    ).click(timeout=15000)
                elif page_iframe.locator(
                    "//a[@class='btn btn3d PopupBtn' and normalize-space()='Ok']"
                ).is_visible():
                    page_iframe.locator(
                        "//a[@class='btn btn3d PopupBtn' and normalize-space()='Ok']"
                    ).click(timeout=15000)
                    logs.append("Can't Lock the plan")

                elif page_iframe.locator(
                    "//a[contains(@class,'PopupBtn') and normalize-space()='Ok']"
                ).is_visible():
                    result = False

    except TimeoutError:
        result = False

    return result, logs

def handle_authenticator(
    page: Page,
    password: str,
    context: BrowserContext,
    playwright: Playwright,
    logs: list,
    runtime:dict,
    task:dict,
    timestamp_fn:Callable|None
):
    pythoncom.PumpWaitingMessages()
    
    """Handle MFA / 2FA authentication flow."""
    logs = logs if logs is not None else []
    timestamp_fn = timestamp_fn or (lambda: "")
    task_name = task["name"] if task else "Task"

    try:
        page.bring_to_front()
        # Wait for either the password field or the security key prompt to be visible
        page.wait_for_selector(
            "//*[text()='Enter password']",
            state="visible",
            timeout=20000,
        )

    except Exception as e:
        print(f"Password prompt not found (may already be past it): {e}")
        # Optional: alternative sign-in path
        # try:
        #     page.wait_for_selector(
        #         "//*[text()='We couldn't sign you in']",
        #         state="visible",
        #         timeout=10000,
        #     )

        #     page.locator("//*[text()='Sign in another way']").click(button="left")

        #     page.wait_for_load_state("load")
        #     page.wait_for_load_state("domcontentloaded")

        #     page.wait_for_selector(
        #         "//*[text()='Use my password']", state="visible", timeout=10000
        #     )

        #     page.locator("//*[text()='Use my password']").click(button="left")

        # except Exception as e:
        #     page.wait_for_timeout(30000)

        try:
            if page.get_by_text("We couldn't sign you in").is_visible():
                page.locator("//*[text()='Sign in another way']").click(button="left")
                page.wait_for_load_state("load")
                page.wait_for_selector(
                    "//*[text()='Use my password']", state="visible", timeout=10000
                )
                page.locator("//*[text()='Use my password']").click(button="left")
        except Exception as inner:
            print(f"Alternative auth flow skipped: {inner}")
    
    try:
        password_string_locator = page.locator("//*[text()='Enter password']")
        password_input_locator = page.locator('//div/input[@id="i0118"]')

        if password_string_locator.is_visible():
            password_input_locator.fill(str(password).strip())
            page.wait_for_selector(
                '//div/input[@id="i0118"]', state="visible", timeout=15000
            )
            page.locator('//div/input[@id="i0118"]').fill(str(password).strip())
            page.locator('//div/input[@id="idSIButton9"]').click()

        page.wait_for_load_state("load", timeout=2000)

        neo_mfa_prompt_locator = page.locator("//*[text()='Approve sign in request']")
        
        if neo_mfa_prompt_locator.is_visible():
            page.get_by_text("Approve sign in request").wait_for(
                    state="hidden", timeout=60000
                )
    
    except Exception:
        pass


    mfa_prompt_locator = page.locator(
            "//*[text()='Approve sign in request' or text()='Verify your identity' or text()='Face, fingerprint, PIN, or security key']"
        )
    
    
    try:
        # Wait for either prompt to appear
        mfa_prompt_locator.first.wait_for(state="visible", timeout=15000)

        prompt_text = mfa_prompt_locator.first.text_content()

        # Now check which one it is
        if "Approve sign in request" in prompt_text:
            try:
                # Wait for the prompt to disappear
                # page.get_by_text("Approve sign in request").wait_for(
                #     state="hidden", timeout=60000
                # )
                if page.get_by_text("I can't use my Microsoft Authenticator app right now").is_visible():
                    page.get_by_text("I can't use my Microsoft Authenticator app right now").click()

                page.wait_for_selector("//*[text() = 'Use a verification code']")

                # if page.get_by_text("Use a verification code").is_visible():
                #     page.get_by_text("Use a verification code").click()

                print("\"Use a verification code\" is visible =>", page.locator('//*[@id="idDiv_SAOTCS_Proofs"]/div[2]/div/div/div[2]/div[text()="Use a verification code"]').is_visible())
                if page.locator('//*[@id="idDiv_SAOTCS_Proofs"]/div[2]/div/div/div[2]/div[text()="Use a verification code"]').is_visible():
                    page.locator('//*[@id="idDiv_SAOTCS_Proofs"]/div[2]/div/div/div[2]/div[text()="Use a verification code"]').click()
                
                 # ===== Get the code from the user via iframe form =====
                code = request_2fa_code_from_user(runtime, task, logs, timestamp_fn)

                # Fill the code into the MS verification input (adjust selector if needed)
                otp_input = page.locator('#idTxtBx_SAOTCC_OTC')
                otp_input.wait_for(state="visible", timeout=15000)
                otp_input.fill(code)

                # Click "Verify" / "Sign in"
                # After clicking Verify/Continue on OTP
                page.locator('#idSubmit_SAOTCC_Continue').click()

                # Handle the "Stay signed in?" prompt that often appears after MFA
                try:
                    stay_signed_in = page.locator("//*[text()='Stay signed in?']")
                    stay_signed_in.wait_for(state="visible", timeout=15000)
                    # Click "Yes" to persist the session (important for storage_state!)
                    page.locator('#idSIButton9').click()   # "Yes" button
                except Exception:
                    pass

                page.wait_for_load_state("load", timeout=60000)   # not 2000
                logs.append(f"{task_name}: 2FA code submitted ---- {timestamp_fn()}")
                # ======================================================

            except Exception as e:
                print(f"OTP handling error: {e}")
                logs.append(f"{task_name}: OTP handling error: {e} ---- {timestamp_fn()}")
                raise

        elif "Verify your identity" in prompt_text:
            while page.get_by_text(
                "Approve a request on my Microsoft Authenticator app"
            ).is_visible():
                page.get_by_text(
                    "Approve a request on my Microsoft Authenticator app"
                ).click(button="left")
                page.wait_for_timeout(1000)

            try:
                approve_prompt = page.get_by_text("Approve sign in request")
                while True:
                    if approve_prompt.is_visible():
                        break
                    else:
                        
                        approve_prompt_failed_prompt = page.get_by_text(
                            "Approve a request on my Microsoft Authenticator app"
                        )
                        while not approve_prompt_failed_prompt.is_visible():
                            approve_prompt_failed_prompt.click(button="left")
                            page.wait_for_timeout(1000)
                        approve_prompt.wait_for(state="visible", timeout=10000)
                # print("Waiting for sign in approval after verification step.")
                approve_prompt.wait_for(state="hidden", timeout=60000)
                # print("Sign in approved by user after verification.")

            except Exception as e:
                pass
        
        elif "Face, fingerprint, PIN, or security key" in prompt_text:
            try:
                approve_prompt = page.get_by_text(
                    "Face, fingerprint, PIN, or security key"
                )
                while True:
                    if not approve_prompt.is_visible():
                        break
                    else:
                        approve_prompt.wait_for(state="hidden", timeout=10000)
            except Exception as e:
                pass
    
    except Exception:
        pass


def search_for_cr(page: Page, cr: str, logs: list):
    logs.append(f"{_timestamp()} -- Starting the Search for the CR: '{cr}'")
    page.locator(
        "//div[@arid='304255502']/div/div/table[@class='Toolbar']/tbody/tr/td[@class='TBGroup TBGroup1']/a[@class='newsearch btn btn3d tbbtn']/span"
    ).click()

    # Adding the CR to the search field
    page.locator(
        "//div[@class='PageBody pbChrome']/div[@id='WIN_3_303683700']/fieldset[@class=' pnl ']/div[@arwindowid='3']/textarea[@class='text sr ' and @id= 'arid_WIN_3_1000000182']"
    ).fill(cr)

    page.locator(
        "//div[@id='WIN_0_304255502' and @arid='304255502']/div[@id='FormApp']/div[@id='Toolbar' and @arwindowid='3']/table[@class='Toolbar']/tbody/tr/td[@class='TBGroup TBGroup0']/a[@arwindowid='3']/div[@id = 'TBsearchsavechanges' and text()='Search']"
    ).click()

    return logs


def work_detail_table_reader(page: Page, 
    cr: str,
) -> Tuple[AnyStr, pd.DataFrame|None]:
    result = None
    
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_load_state('load')
    
    wait_var = True
    # Waiting for the table to load
    while wait_var:
        if (
            page.locator(
                "//div[@class='PageBody pbChrome']/div[@id='WIN_3_301389923']/div[@class='TableHdr']/table[@class='TableHdr']/tbody/tr/td[@class='TableHdrL']"
            ).text_content()
            == "Table has Not been Loaded"
        ):
            page.wait_for_timeout(1000)
        else:
            wait_var = False
    
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_load_state('load')
    
    # print(f"\n\n{cr=}")
    # print(f"{page.locator(
    #     '//fieldset/div/div[@id="WIN_3_301389923"]/div[2]/div'
    # ).is_visible() = }\n\n")

    if page.locator(
        '//fieldset/div/div[@id="WIN_3_301389923"]/div[2]/div'
    ).is_visible():
        table = page.locator(
            '//fieldset/div/div[@id="WIN_3_301389923"]/div[2]/div'
        ).inner_html()
        # print(f"{table = }\n\n")
        df_list = pd.read_html(StringIO(table))
        df = df_list[0]
        print(f"df =\n{df}\n\n")
        result = df
        # writer = pd.ExcelWriter(f"C:/Users/emaienj/Downloads/Work_Details/Work Detail Table_{cr}.xlsx", engine="openpyxl")
        # result.to_excel(writer, sheet_name="Work Detail Table")
        # # writer.save()
        # writer.close()
        # del writer
    
    return cr, result


def get_service_plus_list(
    page: Page,
) -> Tuple[str]:
    result = []
    non_services_plus_entry = (
        "(2G /3G )",
    )
    
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("load")
    page.wait_for_timeout(1000)

    page.locator(
        "//fieldset/div/div/div/div/div[3]/fieldset/div/div/div/div[4]/div[16]/div/div/div[3]/fieldset/div/div/div/div/div[2]/fieldset/div/div[2]/fieldset/div[1]/a"
    ).click()

    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("load")
    
    while len(result) == 0 or result == ('Loading...',):
        table = page.locator(
            "//div[@class='MenuOuter']/div[@class='MenuTableContainer']"
        ).inner_html()
        # print(table, "\n\n")
        parsed_table = beautifulsoup(table, "html.parser")
        # from pprint import pprint
        # pprint(parsed_table)
        # print("\n\n\n")

        result = tuple(
            [
                str(cell.get_text())
                for cell in parsed_table.find_all("td")
                if len(str(cell.get_text())) > 0
            ]
        )
    result = result + non_services_plus_entry
    # print("Service Plus List")
    # print(f"{result = }\n")
    
    return result


def relationship_nodes_handler(
    page: Page,
    cr: str,
    text_contents: List[str]|None = None
) -> Tuple[AnyStr,List[AnyStr]]:
    relationship_nodes = []
    
    page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")
    # print(f"{cr = }\n{text_contents = }\n\n")
    
    if text_contents is None:
        text_contents = [
            "2G",
            "3G",
            "4G",
            "5G",
            "IMS",
            "(2G /3G )",
        ]
    
    page.wait_for_load_state(state="domcontentloaded")
    page.wait_for_load_state(state="load")
    
    page.locator(
        "//div[@class='TabsViewPort']/div/dl[@class='OuterOuterTab']/dd[@class='OuterTab']/span[@class='Tab']/a[text()='Relationships']"
    ).click(modifiers=["Control"], button="left", delay=1000)

    page.wait_for_load_state(state="domcontentloaded")
    page.wait_for_load_state(state="load")
    # page.wait_for_timeout(1500)
    
    var = True
    while var:
        if page.locator(
            "//fieldset/div/div/div/div/div[3]/fieldset/div/div/div/div[4]/div[16]/div/div/div[3]/fieldset/div/div/div/div/div[3]/fieldset/div/div/fieldset[4]/div[2]/div/div/div[2]/fieldset/div/div/div[2]/div/div[2]"
        ).is_visible():
            break
        else:
            page.wait_for_timeout(1000)
    
    if page.locator(
        "//fieldset/div/div/div/div/div[3]/fieldset/div/div/div/div[4]/div[16]/div/div/div[3]/fieldset/div/div/div/div/div[3]/fieldset/div/div/fieldset[4]/div[2]/div/div/div[2]/fieldset/div/div/div[2]/div/div[2]"
    ).is_visible():
        elements_locator = page.locator(
            "//fieldset/div/div/div/div/div[3]/fieldset/div/div/div/div[4]/div[16]/div/div/div[3]/fieldset/div/div/div/div/div[3]/fieldset/div/div/fieldset[4]/div[2]/div/div/div[2]/fieldset/div/div/div[2]/div/div[2]"
        ).inner_html()

        # texts = elements_locator.evaluate_all("elements => elements.map(el => el.textContent.trim())")
        # data = elements_locator.all_inner_texts()
        # df = pd.DataFrame(data)
        # print(StringIO(elements_locator))
        # print("\n\n")
        df_list = pd.read_html(StringIO(elements_locator))

        # df = pd.DataFrame(texts, columns=["Text"])
        df = pd.DataFrame()

        # print(f"{cr = },")
        # print(f"{search_field_value = },\n")

        if len(df_list) == 0:
            _, relationship_nodes = relationship_nodes_handler(page, cr)
        
        elif len(df_list) > 0:
            df = df_list[0]

            if not df.empty:
                if {"Relationship Type", "Request Type", "Request Summary"}.issubset(
                    set(df.columns)
                ):
                    df = df.loc[
                        (
                            (
                                df["Relationship Type"].astype(str).str.strip()
                                == "Related to"
                            )
                            & (
                                df["Request Type"].astype(str).str.strip()
                                == "Configuration Item"
                            )
                        )
                    ]
                    
                    df = df.loc[
                            ~df["Request Summary"]
                            .astype(str)
                            .str.strip()
                            .str.startswith(tuple(text_contents))
                    ]

                    # print(df)
                    # print("\n\n")
                    if df.shape[0] > 0:
                        relationship_nodes = df["Request Summary"].astype(str).str.strip().tolist()
    
    return cr, relationship_nodes


def navigate_to_change_management(page:Page):
    page.wait_for_load_state("load")

    page.locator(
        '//div/img[@id="reg_img_304316340" and @artxt="Show Application List"]'
    ).click()

    while True:
        if page.locator(
            "//div[@class='root root_menu' and @arid='app1600']",
            has_text="Change Management",
        ).is_visible():
            break
        else:
            page.wait_for_timeout(1000)

    page.locator(
        "//div[@class='root root_menu' and @arid='app1600']",
        has_text="Change Management",
    ).hover()

    page.locator("//a[@class='btn']", has_text="Search Change").click()


def itsm_logout(
    page: Page, task:dict, runtime:dict, logs:list, timestamp_fn:Callable|None=_timestamp
) -> list:

    task_name=task["name"] if task else "Task"
    page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")

    logout_locator_path = "//div[@class='f9' and text() = 'Logout']"
    logout_locator = page.locator(logout_locator_path)

    if logout_locator.is_visible():
        logout_locator.click()
        page.wait_for_timeout(2000)

    logs.append(
        f"{task_name}: [{timestamp_fn}]:: Logged out of ITSM"
    )
    runtime["status"] = "ITSM Logout"

    return logs


def itsm_logger(
    logs: list, 
    playwright: Playwright, 
    headless_arg: bool, 
    task: dict, 
    runtime:dict|None=None, 
    timestamp_fn:Callable|None=None,
    user_email: str = None
) -> Tuple[Browser|None, BrowserContext | None, Page | None, list]:
    
    # print("inside itsm logger")

    logs.append(f"🔬 [itsm_logger] runtime is None? {runtime is None}")
    if runtime is not None:
        logs.append(f"🔬 [itsm_logger] runtime id = {id(runtime)}")

    task_name = task["name"] if task else "Task"
    try:
        browser_path = get_browser()
        browser = playwright.chromium.launch(
            headless=headless_arg,
            executable_path=browser_path,
            args=[
                    "--disable-blink-features=AutomationControlled",
                ]
            )
        # methods = [m for m in dir(browser) if not m.startswith('_')]
        # print("\n\n", methods, "\n\n")
        logs.append("✓ Browser launched successfully")
        # ✅ Check connection
        logs.append(f"Browser is connected: {browser.is_connected()}")
        
        logs.append("Step 2: Creating context...")
        context = browser.new_context()
        logs.append("✓ Context created")
        
        logs.append("Step 3: Creating page...")
        page = context.new_page()
        logs.append("✓ Page created")
        # Add close listeners to detect crashes
        def on_close():
            logs.append("⚠️ BROWSER CLOSED UNEXPECTEDLY!")
        
        browser.on("disconnected", on_close)

        logs.append(f"{task['name']}: opening {str(os.getenv('ITSM_URL'))} ---- {_timestamp()}")
        page.goto( str(os.getenv("ITSM_URL")), wait_until="load")

        password = login_to_itsm(page, logs, runtime, task, timestamp_fn, user_email)
        # password = str(os.getenv("PASSWORD"))

        # Ask the user for their password instead of hardcoding it
        # password = request_password_from_user(runtime, task, logs, timestamp_fn)

        page.wait_for_load_state("load")

        expect(
            page.get_by_text("Try again after some time or contact your help desk")
        ).to_be_hidden()

        handle_authenticator(page, password, context, playwright, logs, runtime, task, timestamp_fn)

        # while not page.locator(
        # '//div/img[@id="reg_img_304316340" and @artxt="Show Application List"]').is_visible():
        #     page.wait_for_timeout(1000)
        #     page.wait_for_load_state("domcontentloaded")

        deadline = time.time() + 120  # 2 minutes max
        while not page.locator(
            '//div/img[@id="reg_img_304316340" and @artxt="Show Application List"]'
        ).is_visible():
            if time.time() > deadline:
                raise TimeoutError("ITSM did not reach the application list within 120s")
            page.wait_for_timeout(1000)
            page.wait_for_load_state("domcontentloaded")

        navigate_to_change_management(page)

        logs.append(f"{task_name}: logged in successfully ---- {timestamp_fn()}")
        logs.append("✓ All steps completed successfully")

    except Exception as e:
        import traceback
        traceback.print_exc()
        logs.append(f"Error in itsm_logger: {type(e).__name__}: {str(e)} ---- {timestamp_fn()}")

        # for obj in (page, context, browser):
        #     if obj:
        #         try:
        #             obj.close()
        #         except Exception:
        #             pass
        raise

    return browser, context, page, logs


def safe_evaluate(page, script, timeout=5000):
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
        page.evaluate(script)
    except TimeoutError:
        # Page never stabilized
        pass
    except Exception:
        # Execution context was destroyed or page closed
        pass


def new_page_opener(context: BrowserContext, logs: list) -> Tuple[Page|None, List[AnyStr]]:
    result = None
    try:
        page = context.new_page()
        page.goto(
            str(os.getenv("LOGGED_ITSM_URL")),
            wait_until="load",
        )

        page.wait_for_load_state("domcontentloaded")
        page.wait_for_load_state("load")
        page.on("dialog", lambda dialog: dialog.dismiss())
        # attach_iframe_popup_watcher(page)
        # page.on(
        #     "frameattached",
        #     on_frame_attached,
        # )
        # page = context.new_page()

        safe_evaluate(page, settings.BMC_REMEDY_IFRAME_MODAL_WATCHER_JS)

        navigate_to_change_management(page)

        result = page
    
    except Exception as e:
        print(f"✗ Exception in new_page_opener: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        logs.append(f"{_timestamp()} --- Exception in new_page_opener: {type(e).__name__}: {traceback.format_exc()}\n{str(e)}")
    
    return result, logs



def session_maker(
    logs: list, 
    task:dict, 
    headless_arg: bool=False, 
    runtime: dict=None, 
    timestamp_fn:Callable=None, 
    user_email: str=""
) -> Tuple[bool, list]:
    assert runtime is not None, "runtime must be passed through unchanged"
    print(f"🔎 [session_maker] runtime id = {id(runtime)}")
    print(f"🔬 [session_maker] runtime is None? {runtime is None}")
    if runtime is not None:
        print(f"🔬 [session_maker] runtime id = {id(runtime)}")
    
    browser = None
    main_context = None
    login_page = None
    playwright = None
    session_made = False
    try:
        with sync_playwright() as playwright:
            # print("inside try block session maker")
            browser, main_context, login_page, logs = itsm_logger(
                logs, playwright, headless_arg, task, runtime, timestamp_fn, user_email
            )
            main_context.storage_state(path=get_itsm_session_file_path())
            session_made = True
            # if main_context:
            #     main_context.close()
            #     del main_context

            # if browser:
            #     browser.close()
            #     del browser

            # if playwright:
            #     playwright.stop()
            #     # keyboard.press_and_release("ctrl+c")
            #     del playwright

    except Exception as e:
        print(f"✗ Exception in session_maker: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        logs.append(f"Exception in session_maker: {type(e).__name__}: {str(e)}")
        session_made = False
        raise

    finally:
        for obj in (login_page, main_context, browser):
            if obj:
                try:
                    obj.close()
                except Exception:
                    pass
        if playwright:
            playwright.stop()
        logs.append("✓ Cleanup complete")

    return session_made, logs



def session_breaker():
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True, executable_path=get_browser()
            )

            main_context = browser.new_context(storage_state=get_itsm_session_file_path())
            login_page = main_context.new_page()
            login_page.goto(
                str(os.getenv("LOGGED_ITSM_URL"))
            )

            if login_page.locator("//div[@class='f9' and text() = 'Logout']").is_visible():
                login_page.locator("//div[@class='f9' and text() = 'Logout']").click()
                login_page.wait_for_timeout(2000)

                login_page.close()

            if main_context:
                main_context.close()

            if playwright:
                playwright.stop()
                del playwright
        
        if Path(get_itsm_session_file_path()).exists():
            Path(get_itsm_session_file_path()).unlink()
    
    except Exception:
        pass