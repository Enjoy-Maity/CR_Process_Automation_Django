import os
import traceback
import pythoncom
import rootutils
import threading
from pathlib import Path
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
from typing import Union, Tuple
from collections.abc import Callable
from datetime import datetime, timedelta, date
from dateutil import parser


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
        print(datetime.now())
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


    folder = str(os.getenv("RAW_REPORT_DOWNLOAD_FOLDER"))
    
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
    
    if os.path.exists(
        os.path.join(folder, f"PS_Core_Raw_Report_{datetime.now().strftime('%Y-%m-%d')}.csv")
    ):
        os.remove(
            os.path.join(folder, f"PS_Core_Raw_Report_{datetime.now().strftime('%Y-%m-%d')}.csv")
        )
    download.save_as(
        os.path.join(folder, f"PS_Core_Raw_Report_{datetime.now().strftime('%Y-%m-%d')}.csv")
    )

    # time.sleep(2)
    logs.append(f"{task_name}: [{timestamp_fn}] :: Downloaded the Raw Report")
    runtime["status"]="Dowloaded the Raw Report"

    popup.close(run_before_unload=True)

    return logs


def login_to_itsm(
    page: Page, logs: list, runtime: dict, task: dict, timestamp_fn: Callable
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

    username = str(os.getenv("EMAIL_USERNAME"))

    # Filling the user name
    page.locator('//div/input[@id="i0116"]').fill(username)
    page.locator('//div/input[@id="idSIButton9"]').click()
    
    page.wait_for_load_state("load", timeout=60000)
    page.wait_for_selector('//div/input[@id="i0118"]', state="visible", timeout=10000)
    # if page.locator('//div/input[@id="i0118"]').is_visible():
    #     page.locator('//div/input[@id="i0118"]').fill(str(password).strip())
    #     page.locator('//div/input[@id="idSIButton9"]').click()
    #     page.wait_for_load_state("load", timeout=60000)
    return request_password_from_user(runtime, task, logs, timestamp_fn)



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
                page.locator('#idSubmit_SAOTCC_Continue').click()
                page.wait_for_load_state("load")
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



def navigate_to_change_management(page:Page, logs:list):
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
    timestamp_fn:Callable|None=None) -> Tuple[Browser|None, BrowserContext | None, Page | None, list]:
    
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

        password = login_to_itsm(page, logs, runtime, task, timestamp_fn)
        # password = str(os.getenv("PASSWORD"))

        # Ask the user for their password instead of hardcoding it
        # password = request_password_from_user(runtime, task, logs, timestamp_fn)

        page.wait_for_load_state("load")

        expect(
            page.get_by_text("Try again after some time or contact your help desk")
        ).to_be_hidden()

        handle_authenticator(page, password, context, playwright, logs, runtime, task, timestamp_fn)

        while not page.locator(
        '//div/img[@id="reg_img_304316340" and @artxt="Show Application List"]').is_visible():
            page.wait_for_timeout(1000)
            page.wait_for_load_state("domcontentloaded")

        navigate_to_change_management(page, logs)

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


def session_maker(logs: list, task:dict, headless_arg: bool=False, runtime: dict=None, timestamp_fn:Callable=None) -> list:
    print(f"🔬 [session_maker] runtime is None? {runtime is None}")
    if runtime is not None:
        print(f"🔬 [session_maker] runtime id = {id(runtime)}")
    
    browser = None
    main_context = None
    login_page = None
    playwright = None
    try:
        with sync_playwright() as playwright:
            # print("inside try block session maker")
            browser, main_context, login_page, logs = itsm_logger(
                logs, playwright, headless_arg, task, runtime, timestamp_fn
            )
            session_file = main_context.storage_state(path=get_itsm_session_file_path())
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

    return logs



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