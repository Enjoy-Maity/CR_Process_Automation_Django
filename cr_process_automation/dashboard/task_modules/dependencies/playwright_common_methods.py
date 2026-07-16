# import winreg
import time
import inspect
import traceback
import pythoncom
import platform
import re
import keyboard
import os
import pandas as pd
from os import PathLike
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
from io import StringIO
from pprint import pprint
# from sqlalchemy.util.preloaded import engine_reflection
from .extra import common_paths_for_browser_method
from pathlib import Path
from typing import Tuple, Literal, List, AnyStr, Dict, Union
from .password_checker import ITSM_Password_Fetcher, NIAM_Password_Fetcher
from datetime import datetime, timedelta
from .constants import BMC_REMEDY_IFRAME_MODAL_WATCHER_JS, ITSM_SESSION_FILE, NIAM_SESSION_FILE

# from winreg import KEY_READ
from PySide6.QtCore import Signal
from PS_Core_Process_Automation.dialog_manager import DialogManager
from PS_Core_Process_Automation.messages import Messagebox
from bs4 import BeautifulSoup as beautifulsoup
from PS_Core_Process_Automation.live_feed_text_colorizer import orange_text, red_text

def new_testing_method():
    print("Hello Testing of Playwright Common Methods")


def read_and_reset_modal_ack(page):
    # return page.evaluate("""
    #     () => {
    #         const s = window.__remedyModalState || {};
    #         const result = {
    #             handled: !!s.handled,
    #             type: s.type,
    #             message: s.message
    #         };

    #         if (s.handled) {
    #             s.handled = false;
    #             s.type = null;
    #             s.message = null;
    #         }
    #         return result;
    #     }
    # """)
    return page.evaluate("""
            () => {
                const s = window.__remedyModalState || {};
                window.__remedyModalState = { handled:false, type:null };
                return s;
            }
        """)


def on_frame_attached(frame: Frame | FrameLocator):
    try:
        url = frame.url or ""

        if "MessagePopup.html" not in url:
            return
        # content = frame.content()

        frame.wait_for_load_state("domcontentloaded", timeout=3000)

        # Confirm Save → YES
        # yes_xpath = "//a[contains(@class,'PopupBtn') and normalize-space()='Yes']"
        # if frame.locator(f"xpath={yes_xpath}").count():
        #     frame.locator(f"xpath={yes_xpath}").click()
        #     page._popup_state = {
        #         "handled": True,
        #         "type": "confirm_save",
        #     }
        #     return

        # Confirm Save -> YES
        # yes_xpath = "//a[contains(@class,'PopupBtn') and normalize-space()='Yes']"
        # if frame.locator(yes_xpath).is_visible():
        #     frame.locator(yes_xpath).click()
        #     page._popup_state = {
        #         "handled": True,
        #         "type": "confirm_save",
        #     }
        #     return

        # Confirm Save -> NO
        no_xpath = "//a[contains(@class,'PopupBtn') and normalize-space()='No']"
        if frame.locator(no_xpath).is_visible():
            # print("\n\n\nfound no button in the popup")
            frame.locator(no_xpath).click()
            # page._popup_state = {
            #     "handled": True,
            #     "type": "confirm_save",
            # }
            return

        # Error / Info → OK
        ok_xpath = "//a[contains(@class,'PopupBtn') and normalize-space()='OK']"
        if frame.locator(f"xpath={ok_xpath}").count():
            frame.locator(f"xpath={ok_xpath}").click()
            # page._popup_state = {
            #     "handled": True,
            #     "type": "ok",
            # }
            return

    except Exception as e:
        print("iframe popup handler error:", e)


def attach_iframe_popup_watcher(page: Page):
    """
    Watches for dynamically created popup iframes and
    records popup type after clicking via XPath.
    """

    page._popup_state = {"handled": False, "type": None}

    def on_frame_attached(frame):
        try:
            url = frame.url or ""

            if "MessagePopup.html" not in url:
                return
            # content = frame.content()

            frame.wait_for_load_state("domcontentloaded", timeout=3000)

            # Confirm Save → YES
            # yes_xpath = "//a[contains(@class,'PopupBtn') and normalize-space()='Yes']"
            # if frame.locator(f"xpath={yes_xpath}").count():
            #     frame.locator(f"xpath={yes_xpath}").click()
            #     page._popup_state = {
            #         "handled": True,
            #         "type": "confirm_save",
            #     }
            #     return

            # Confirm Save -> YES
            # yes_xpath = "//a[contains(@class,'PopupBtn') and normalize-space()='Yes']"
            # if frame.locator(yes_xpath).is_visible():
            #     frame.locator(yes_xpath).click()
            #     page._popup_state = {
            #         "handled": True,
            #         "type": "confirm_save",
            #     }
            #     return

            # Confirm Save -> NO
            no_xpath = "//a[contains(@class,'PopupBtn') and normalize-space()='No']"
            if frame.locator(no_xpath).is_visible():
                # print("\n\n\nfound no button in the popup")
                frame.locator(no_xpath).click()
                page._popup_state = {
                    "handled": True,
                    "type": "confirm_save",
                }
                return

            # Error / Info → OK
            ok_xpath = "//a[contains(@class,'PopupBtn') and normalize-space()='OK']"
            if frame.locator(f"xpath={ok_xpath}").count():
                frame.locator(f"xpath={ok_xpath}").click()
                page._popup_state = {
                    "handled": True,
                    "type": "ok",
                }
                return

        except Exception as e:
            print("iframe popup handler error:", e)

    page.on("frameattached", on_frame_attached)


def read_and_reset_popup_state(page):
    state = getattr(page, "_popup_state", {"handled": False, "type": None})
    page._popup_state = {"handled": False, "type": None}
    return state


# def handle_remedy_message_popup(page, timeout=1000):
#     """
#     Handles Remedy MessagePopup iframe.
#     Returns:
#         "confirm_save" | "ok" | None
#     """
#     # for frame in page.frames:
#     #     if "MessagePopup.html" in (frame.url or ""):
#     #         try:
#     #             frame.wait_for_selector("a.PopupBtn", timeout=1000)

#     #             # Read popup text
#     #             msg = frame.locator("#PopupMsgBox").inner_text().lower()

#     #             # CONFIRM SAVE → YES
#     #             if "do you want to save the current request" in msg:
#     #                 frame.locator("a.PopupBtn", has_text="Yes").click()
#     #                 return "confirm_save"

#     #             # All other popups → OK or Yes fallback
#     #             if frame.locator("a.PopupBtn", has_text="OK").count():
#     #                 frame.locator("a.PopupBtn", has_text="OK").click()
#     #                 return "ok"

#     #             # Some popups only have Yes
#     #             if frame.locator("a.PopupBtn", has_text="Yes").count():
#     #                 frame.locator("a.PopupBtn", has_text="Yes").click()
#     #                 return "ok"

#     #         except Exception:
#     #             pass

#     # return None
#     deadline = page.context._loop.time() + (timeout / 1000)

#     while page.context._loop.time() < deadline:
#         for frame in page.frames:
#             if frame.url and "MessagePopup.html" in frame.url:
#                 try:
#                     frame.wait_for_selector("#PopupMsgBox", timeout=500)

#                     message = frame.evaluate(
#                         "document.getElementById('PopupMsgBox').innerText"
#                     ).lower()

#                     # 🔑 EXECUTE Remedy's own JS (not DOM click)
#                     if "do you want to save the current request" in message:
#                         frame.evaluate("""
#                             (() => {
#                                 const yes = [...document.querySelectorAll('a.PopupBtn')]
#                                     .find(a => a.innerText.trim() === 'Yes');
#                                 if (yes) yes.click();
#                             })();
#                         """)
#                         return "confirm_save"

#                     # Other popups → OK / Yes
#                     frame.evaluate("""
#                         (() => {
#                             const ok = [...document.querySelectorAll('a.PopupBtn')]
#                                 .find(a => ['ok','yes'].includes(a.innerText.trim().toLowerCase()));
#                             if (ok) ok.click();
#                         })();
#                     """)
#                     return "ok"

#                 except Exception:
#                     pass

#         page.wait_for_timeout(200)

#     return None


# def handle_remedy_message_popup(page, timeout=5000):
#     """
#     HARD Remedy fix.
#     Directly calls weCloseDialogue inside MessagePopup iframe.
#     Returns:
#         "confirm_save" | "ok" | None
#     """
#     end = page.timeouts().timeout + timeout if hasattr(page, "timeouts") else None

#     while True:
#         for frame in page.frames:
#             if frame.url and "MessagePopup.html" in frame.url:
#                 try:
#                     # Ensure popup fully initialized
#                     frame.wait_for_function(
#                         "() => typeof weCloseDialogue === 'function' && typeof windowID !== 'undefined'",
#                         timeout=1000,
#                     )

#                     message = frame.evaluate(
#                         "document.getElementById('PopupMsgBox').innerText"
#                     ).lower()

#                     if "do you want to save the current request" in message:
#                         # YES → v:1
#                         frame.evaluate("weCloseDialogue(windowID, {v: 1})")
#                         return "confirm_save"

#                     # All other popups → OK / Yes
#                     frame.evaluate("weCloseDialogue(windowID, {v: 1})")
#                     return "ok"

#                 except Exception:
#                     pass

#         page.wait_for_timeout(200)

#         if timeout <= 0:
#             break
#         timeout -= 200

#     return None


# def handle_remedy_message_popup(page, timeout_ms=5000):
#     """
#     FINAL, GUARANTEED Remedy popup handler.
#     Uses keyboard events ONLY.
#     Returns:
#         "confirm_save" | "ok" | None
#     """
#     deadline = time.time() + timeout_ms / 1000

#     while time.time() < deadline:
#         for frame in page.frames:
#             if frame.url and "MessagePopup.html" in frame.url:
#                 try:
#                     # Read message text (best effort)
#                     msg = frame.evaluate("""
#                         () => document.getElementById('PopupMsgBox')?.innerText || ''
#                     """).lower()

#                     # 🔑 UNIVERSAL FIX: press Enter
#                     page.keyboard.press("Enter")

#                     if "do you want to save the current request" in msg:
#                         return "confirm_save"

#                     return "ok"

#                 except Exception:
#                     # Even if JS access fails, Enter still works
#                     page.keyboard.press("Enter")
#                     return "ok"

#         page.wait_for_timeout(200)

#     return None


def handle_remedy_message_popup(page: Page, timeout_ms: int = 6000):
    """
    FINAL focus-safe Remedy popup handler.
    """
    # import time

    deadline = time.time() + timeout_ms / 1000

    # 🔑 ensure browser is foreground
    page.bring_to_front()

    while time.time() < deadline:
        for frame in page.frames:
            if frame.url and "MessagePopup.html" in frame.url:
                try:
                    # 1️⃣ focus iframe window
                    frame.evaluate("""
                        () => {
                            window.focus();
                            document.body.focus();
                            document.getElementById('PopupMsgBox')?.focus();
                        }
                    """)

                    # 2️⃣ read message (best effort)
                    msg = frame.evaluate("""
                        document.getElementById('PopupMsgBox')?.innerText || ''
                    """).lower()

                    # 3️⃣ HARD ACCEPT via keyboard at page level
                    page.keyboard.press("Enter")

                    if "do you want to save the current request" in msg:
                        return "confirm_save"

                    return "ok"

                except Exception:
                    # even if JS fails, keyboard still works once focused
                    page.keyboard.press("Enter")
                    return "ok"

        page.wait_for_timeout(200)

    return None


# def call_with_modal_ack(page, func, *args, max_retries=2, **kwargs):
#     """
#     Executes a function that may trigger Remedy HTML modals.
#     Retries if a modal was handled.

#     Returns:
#         result
#     """
#     for attempt in range(1, max_retries + 1):
#         # --- Bind args to parameter names ---
#         sig = inspect.signature(func)
#         bound = sig.bind(*args, **kwargs)
#         bound.apply_defaults()

#         # --- Call function ---
#         result = func(*bound.args, **bound.kwargs)

#         # let DOM settle & observer react
#         page.wait_for_timeout(300)

#         #     # ack = read_and_reset_modal_ack(page)
#         #     popup_type = handle_remedy_message_popup(page)

#         #     # --- No modal → success ---
#         #     if not popup_type:
#         #         ack = read_and_reset_modal_ack(page)
#         #         popup_type = ack["type"] if ack["handled"] else None

#         #     if not popup_type:
#         #         return result, dict(bound.arguments)["token_for_locking"]

#         #     # print(
#         #     #     f"⚠️ Modal handled during {func.__name__} "
#         #     #     f"(type={ack['type']}) → retry {attempt}"
#         #     # )

#         #     print(
#         #         f"⚠️ Remedy popup handled ({popup_type}) "
#         #         f"in {func.__name__}, attempt {attempt}"
#         #     )

#         #     # # --- ONLY for Confirm Save Request ---
#         #     # if ack["type"] == "confirm_save":
#         #     #     # 🔑 Update argument safely by name
#         #     #     if "token_for_locking" in bound.arguments:
#         #     #         print("🔁 Disabling install plan and retrying")
#         #     #         bound.arguments["token_for_locking"] = False

#         #     #     # rebuild args / kwargs for retry
#         #     #     args = bound.args
#         #     #     kwargs = bound.kwargs
#         #     #     continue

#         #     # 🔁 mutate argument ONLY for Confirm Save
#         #     if popup_type == "confirm_save":
#         #         if "token_for_locking" in bound.arguments:
#         #             bound.arguments["token_for_locking"] = False
#         #             print("🔁 token_for_locking set to False")

#         #     # --- Other popups: retry without mutation ---
#         #     continue

#         # return result, dict(bound.arguments)["token_for_locking"]
#         popup_type = handle_remedy_message_popup(page)

#         if not popup_type:
#             ack = read_and_reset_modal_ack(page)
#             popup_type = ack["type"] if ack["handled"] else None

#         if not popup_type:
#             return result, dict(bound.arguments)["token_for_locking"]

#         print(
#             f"⚠️ Remedy popup '{popup_type}' handled "
#             f"in {func.__name__} (attempt {attempt})"
#         )

#         # 🔁 Disable install plan ONLY on Confirm Save
#         if popup_type == "confirm_save":
#             if "token_for_locking" in bound.arguments:
#                 bound.arguments["token_for_locking"] = False
#                 print("🔁 token_for_locking → False")

#     return result, dict(bound.arguments)["token_for_locking"]


# def call_with_modal_ack(page, func, *args, max_retries=3, **kwargs):
#     """
#     Executes a function that may trigger Remedy popups.
#     Adapts arguments and retries safely.
#     """
#     sig = inspect.signature(func)
#     bound = sig.bind(*args, **kwargs)
#     bound.apply_defaults()

#     for attempt in range(1, max_retries + 1):
#         result = func(*bound.args, **bound.kwargs)

#         popup_type = handle_remedy_message_popup(page)

#         if not popup_type:
#             return result, dict(bound.arguments)["token_for_locking"]

#         print(
#             f"⚠️ Remedy popup '{popup_type}' handled "
#             f"in {func.__name__} (attempt {attempt})"
#         )

#         # 🔁 Only Confirm Save affects logic
#         if popup_type == "confirm_save":
#             if "token_for_locking" in bound.arguments:
#                 bound.arguments["token_for_locking"] = False
#                 print("🔁 token_for_locking set to False")

#     return result, dict(bound.arguments)["token_for_locking"]


def call_with_modal_ack(page, func, *args, max_retries=3, **kwargs):
    """
    Calls a function that may trigger a popup iframe.
    Detects popup, mutates args, retries, and returns updated args.
    """
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    earlier_value_of_token_for_locking = bound.arguments["token_for_locking"]

    for attempt in range(1, max_retries + 1):
        result = func(*bound.args, **bound.kwargs)

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
            
    return result, dict(bound.arguments)["token_for_locking"]


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


def page_deleter(
    page: Page,
    browser,
    context: BrowserContext,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
):
    if page:
        page.wait_for_timeout(1000)
        if page.locator("//div[@class='f9' and text() = 'Logout']").is_visible():
            page.locator("//div[@class='f9' and text() = 'Logout']").click()
            page.wait_for_timeout(2000)
        page.close()

    if context:
        context.close()

    if browser:
        browser.close()

    if live_feed:
        live_feed.emit(orange_text("Logged out of ITSM and closed the browser"))


def raw_report_downloader(
    context: BrowserContext,
    page: Page,
    folder: None,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
):
    if not folder:
        folder = os.path.dirname(__file__)

    date_1 = f"{((datetime.now()).replace(hour=20, minute=0, second=0)).strftime('%m/%d/%Y %H:%M:%S')}"
    date_2 = f"{((datetime.now() + timedelta(days=1)).replace(hour=8, minute=0, second=0)).strftime('%m/%d/%Y %H:%M:%S')}"

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
    
    # with popup.expect_popup() as nav_popup_info:
    #     popup.locator(
    #         '//div/table/tbody/tr/td/input[@class="birtviewer_clickable" and @title="Export report"]'
    #     ).click()

    # nav_popup = nav_popup_info.value
    
    # nav_popup.locator(
    #     '//div/table[@class="birtviewer_dialog_body"]/tbody/tr/td/select[@id="exportFormat"]'
    # ).click()
    
    # nav_popup.get_by_text("Spudsoft Excel").click()
    
    # with nav_popup.expect_download() as neo_popup_info:
    #     nav_popup.locator(
    #         '//div[@id="exportReportDialogokButton"]/input[@class="dialogBtnBarButtonText dialogBtnBarButtonEnabled" and @type="button" and @value="OK"]'
    #     ).click()
    
    with popup.expect_download() as neo_popup_info:
        popup.locator(
            "//a[@artype='Control']/div[@class='btnimgdiv']/img[@id='reg_img_93272']"
        ).click()

    download = neo_popup_info.value
    # download.wait_for_load_state()
    # if os.path.exists(
    #     os.path.join(folder, f"Report_{datetime.now().strftime('%Y-%m-%d')}.xls")
    # ):
    #     os.remove(
    #         os.path.join(folder, f"Report_{datetime.now().strftime('%Y-%m-%d')}.xls")
    #     )
    # download.save_as(
    #     os.path.join(folder, f"Report_{datetime.now().strftime('%Y-%m-%d')}.xls")
    # )
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

    popup.close(run_before_unload=True)


def bpms_tasks_tab_getter(
    cr: str, 
    page: Page, 
    manager: DialogManager | None = None, 
    live_feed: Signal | None = None
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
            _, first_table_df = bpms_tasks_tab_getter(cr, page, manager, live_feed)
            
        elif len(df_list) > 0:
            first_table_df = df_list[0]
        
    return cr, first_table_df


def bpms_auto_crs_tasks_lld_automation_handler(
    cr: str,
    page: Page,
    folder_location: str,
    cr_circle: str,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Tuple[AnyStr, AnyStr]:
    
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
        f"{datetime.now().strftime('%d-%b-%Y')}",
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
                            
    return cr, attachment_


def bpms_crs_attachment_name_getter(
    cr: str,
    page: Page,
    manager: DialogManager | None,
    live_feed: Signal | None
) -> Tuple[AnyStr, AnyStr]:
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
        
        if live_feed:
            live_feed.emit(
                orange_text(
                    f"Getting the bpms technical design attachment name for cr: {cr}"
                )
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
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )
    
    return cr, attachment_name
        
    


def bpms_manual_crs_attachment_downloader(
    cr: str,
    folder_location: str,
    cr_circle: str,
    page: Page,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Tuple[AnyStr, AnyStr]:
    attachment_name = ""
    try:
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_load_state('load')
        
        lld_design_download_path = os.path.join(
            folder_location,
            "Install_and_Backout_Plan_Files",
            f"{datetime.now().strftime('%d-%b-%Y')}",
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
        
        if live_feed:
            live_feed.emit(
                orange_text(
                    f"Getting the bpms technical design attachment name for cr: {cr}"
                )
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
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )
    
    return cr, attachment_name


def bpms_file_correction_file_upload(
    cr: str, 
    corrected_file_path: str,
    page: Page,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None
) -> Tuple[AnyStr, AnyStr]:
    result = "Failure"
    page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")
    
    search_for_cr(cr, page, manager, live_feed)

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
        if manager:
            manager.show_info_signal.emit(
                f"Exception occurred ({e.__class__.__name__})!!",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )

        else:
            messagebox = Messagebox()
            messagebox.showerror(
                f"Exception occurred ({e.__class__.__name__})!!",
                f"{traceback.format_exc()}\n\n{e}",
            )
            
    
    return cr, result
                    

def context_playwright_deleter(
    # context: BrowserContext,
    playwright: Playwright,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
):
    # if context:
    #     context.close()

    if playwright:
        playwright.stop()
        keyboard.press_and_release("ctrl+c")
        del playwright

    if live_feed:
        live_feed.emit(orange_text("Closed the Browser Context and Playwright"))


def exception_returner(
    playwright: Playwright,
    context: BrowserContext,
    browser: Browser,
    page: Page,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
):
    page_deleter(page, browser, context, manager, live_feed)
    context_playwright_deleter(playwright, manager, live_feed)

    return None, None, None


def chrome_path_returner() -> str:
    _chrom_path = None
    if platform.system() == "Windows":
        # key = winreg.OpenKey(
        #     key=winreg.HKEY_CLASSES_ROOT,
        #     sub_key=r"\ChromeHTML\shell\open\command",
        #     reserved=0,
        #     access=KEY_READ,
        # )
        # command_tuple = winreg.QueryValueEx(key, "")
        # command = command_tuple[0]
        # _chrome_path = re.findall(r"\"(.*)\"", command)[0]
        # winreg.CloseKey(key)
        _chrom_path = common_paths_for_browser_method()

    if platform.system() == "Linux":
        pass

    return _chrom_path


def login_to_itsm(
    page: Page, manager: DialogManager | None = None, live_feed: Signal | None = None
):
    # if folder is None:
    #     folder = str(Path(__file__).parent.parent)
    # username = os.getlogin().upper().strip()
    __itsm_data = ITSM_Password_Fetcher().fetch
    username = __itsm_data["username"]
    password = __itsm_data["password"]
    # page.locator("//input[@id='login']").fill(username)
    # password = ""
    # if password is None and folder is not None:
    #     with open(os.path.join(folder, "planning.txt"), "r") as f:
    #         password = f.readline().strip()
    # page.locator("//input[@id='passwd']").fill(str(password).strip())

    # clicking the logon button
    # page.locator("//a[@id='loginBtn']", has_text="Log On").click()

    # Filling the user name
    page.locator('//div/input[@id="i0116"]').fill(username)
    page.locator('//div/input[@id="idSIButton9"]').click()
    if live_feed:
        live_feed.emit(orange_text("Entered the username"))
    page.wait_for_load_state("load", timeout=60000)
    page.wait_for_selector('//div/input[@id="i0118"]', state="visible", timeout=10000)
    # if page.locator('//div/input[@id="i0118"]').is_visible():
    #     page.locator('//div/input[@id="i0118"]').fill(str(password).strip())
    #     page.locator('//div/input[@id="idSIButton9"]').click()
    #     page.wait_for_load_state("load", timeout=60000)
    return password


def handle_authenticator(
    page: Page,
    password: str,
    context: BrowserContext,
    playwright: Playwright,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
):
    # page.locator("//input[@id='response']").focus()
    # page.wait_for_timeout(5000)
    # while len(page.locator("//input[@id='response']").input_value()) < 6:
    #     if len(page.locator("//input[@id='response']").input_value()) == 0:
    #         # from tkinter import messagebox
    #         messagebox = Messagebox()
    #         messagebox.showwarning(
    #             "    Authentication Error!", "Please enter the authenticator code"
    #         )
    #     page.wait_for_timeout(5000)
    # if page.locator("//a[@id= 'ns-dialogue-submit']", has_text="Submit").is_visible():
    #     page.locator("//a[@id= 'ns-dialogue-submit']", has_text="Submit").click()

    pythoncom.PumpWaitingMessages()

    try:
        page.bring_to_front()
        # Wait for either the password field or the security key prompt to be visible
        page.wait_for_selector(
            "//*[text()='Enter password']",
            state="visible",
            timeout=20000,
        )

    except Exception as e:
        try:
            page.wait_for_selector(
                "//*[text()='We couldn't sign you in']",
                state="visible",
                timeout=10000,
            )

            page.locator("//*[text()='Sign in another way']").click(button="left")

            page.wait_for_load_state("load")
            page.wait_for_load_state("domcontentloaded")

            page.wait_for_selector(
                "//*[text()='Use my password']", state="visible", timeout=10000
            )

            page.locator("//*[text()='Use my password']").click(button="left")

            if manager:
                manager.show_info_signal.emit(
                    "  Work In Progress!!!",
                    "Please Wait! We are working on it.",
                    "info",
                )

            else:
                # from tkinter import messagebox
                from messages import Messagebox

                messagebox = Messagebox()
                messagebox.showinfo(
                    "  Work In Progress!!!", "Please Wait! We are working on it."
                )

        except Exception as e:
            # Master block to handle any any errors of any kind in microsoft login

            if manager:
                manager.show_info_signal.emit(
                    "  Work In Progress!!!",
                    "Please Wait! We are working on it.",
                    "info",
                )

            else:
                from messages import Messagebox

                messagebox = Messagebox()
                messagebox.showinfo(
                    "  Work In Progress!!!", "Please Wait! We are working on it."
                )
            page.wait_for_timeout(30000)

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
    
    
    # Define a single locator for either of the MFA prompts
    
    mfa_prompt_locator = page.locator(
            "//*[text()='Approve sign in request' or text()='Verify your identity' or text()='Face, fingerprint, PIN, or security key']"
        )
    
    
    try:
        # Wait for either prompt to appear
        mfa_prompt_locator.first.wait_for(state="visible", timeout=15000)

        prompt_text = mfa_prompt_locator.first.text_content()

        # Now check which one it is
        if "Approve sign in request" in prompt_text:
            # print("Line No. 356 - Waiting for sign in approval.")
            try:
                # Wait for the prompt to disappear
                page.get_by_text("Approve sign in request").wait_for(
                    state="hidden", timeout=60000
                )
                if live_feed:
                    live_feed.emit("Waiting for sign in approval.")
                # print("Sign in approved by user.")
            except Exception as e:
                if manager:
                    # manager.show_info_signal.emit(
                    #     "  Timeout Error!",
                    #     "Timed out waiting for sign-in approval. Please try again.",
                    #     "error"
                    # )
                    pass

                else:
                    # from tkinter import messagebox
                    # from messages import Messagebox
                    # messagebox = Messagebox()
                    # messagebox.showerror(
                    #     "Timeout",
                    #     "Timed out waiting for sign-in approval. Please try again.",
                    # )
                    pass
                # raise e

        elif "Verify your identity" in prompt_text:
            # print("Line No. 367 - Verifying identity.")
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
                if manager:
                    # manager.show_info_signal.emit(
                    #     "   Timeout",
                    #     "Timed out waiting for sign-in approval after verification. Please try again.",
                    #     "error"
                    # )
                    pass

                else:
                    # from tkinter import messagebox
                    # from messages import Messagebox
                    # messagebox = Messagebox()
                    # messagebox.showerror(
                    #     "Timeout",
                    #     "Timed out waiting for sign-in approval after verification. Please try again.",
                    # )
                    pass
                # context_playwright_deleter(context, playwright)

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
                if manager:
                    # manager.show_info_signal.emit(
                    #     "   Timeout",
                    #     "Timed out waiting for sign-in approval after verification. Please try again.",
                    #     "error"
                    # )
                    pass
                else:
                    # from tkinter import messagebox
                    # from messages import Messagebox
                    # messagebox = Messagebox()
                    # messagebox.showerror(
                    #     "   Timeout",
                    #     "Timed out waiting for sign-in approval after verification. Please try again.",
                    # )
                    pass
                # context_playwright_deleter(context, playwright)

    except Exception:
        # If neither prompt appeared after waiting
        if manager:
            # manager.show_info_signal.emit(
            #     "  Timeout Error!",
            #     "MFA prompt not detected within the timeout. Assuming no MFA is required or page is different than expected.",
            #     "error"
            # )
            pass
        else:
            # from tkinter import messagebox
            # from messages import Messagebox
            # messagebox = Messagebox()
            # messagebox.showerror(
            #     "  Timeout Error!",
            #     "MFA prompt not detected within the timeout. Assuming no MFA is required or page is different than expected.",
            # )
            pass
        # context_playwright_deleter(context, playwright)


def navigate_to_change_management(
    page: Page, manager: DialogManager | None = None, live_feed: Signal | None = None
):
    page.wait_for_load_state("load")
    # scroll_to_bottom(page)

    # page.locator("//img[@alt='Show Application List']").click()
    page.locator(
        '//div/img[@id="reg_img_304316340" and @artxt="Show Application List"]'
    ).click()
    # time.sleep(2)
    # page.locator(
    #     '//div/fieldset/div/div/div/div/a/span/*[text()="Change Management"]',
    # ).hover()

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
    # time.sleep(2)

    # scroll_to_bottom(page)

    page.locator("//a[@class='btn']", has_text="Search Change").click()


def itsm_logger(
    playwright: Playwright,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Tuple[Playwright | None, Page | None]:
    # sourcery skip: extract-method
    selected_path_for_browser = ""

    selected_path_for_browser = chrome_path_returner()

    browser = playwright.chromium.launch(
        executable_path=selected_path_for_browser, headless=False
    )

    # context = browser.new_context(viewport={"width": 1920, "height": 1080})
    context = browser.new_context()
    page = context.new_page()

    try:
        # page.goto("https://nextgentm-in.sdt.ericsson.net/arsys", wait_until="load")
        page.goto(
            "https://ticketing-in.managed-services.prod.sdt.ericsson.net/arsys/",
            wait_until="load",
        )

        # finding the id 'domain' and 'Employee' in the option value
        # select_element = page.locator("select#domain")
        # select_element.select_option("Employee")
        # page.wait_for_selector("//a[@id='loginBtn']")
        # page.locator(selector="//a[@id='loginBtn']", has_text="Log On").click()

        password = login_to_itsm(page, manager, live_feed)

        page.wait_for_load_state("load")

        # if page.locator("//span[@class='detail-text error' and text()='Try again after some time or contact your help desk']").is_visible():
        #     # from tkinter import messagebox
        #     messagebox.showerror("Error", "Please enter the correct password")
        #     main_func(workbook=workbook)

        expect(
            page.get_by_text("Try again after some time or contact your help desk")
        ).to_be_hidden()

        handle_authenticator(page, password, context, playwright, manager, live_feed)
        
        while not page.locator(
        '//div/img[@id="reg_img_304316340" and @artxt="Show Application List"]').is_visible():
            page.wait_for_timeout(1000)
            page.wait_for_load_state("domcontentloaded")

        navigate_to_change_management(page, manager, live_feed)

    except TimeoutError:
        exception_returner(playwright, context, browser, page, manager, live_feed)

    except Exception as e:
        # from tkinter import messagebox

        if manager:
            manager.show_info_signal.emit(
                f"   Exception Occurred ({e.__class__.__name__})",
                f"{traceback.format_exc()}\n\n{str(e)}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.showerror(
                f"   Exception Occurred ({e.__class__.__name__})",
                f"{traceback.format_exc()}\n\n{str(e)}",
            )
        exception_returner(playwright, context, browser, page, manager, live_feed)

    return browser, context, page


def search_for_cr(
    cr: str,
    page: Page,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Page:
    if live_feed:
        live_feed.emit(orange_text(f"Starting the Search for the CR: '{cr}'"))

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

    if live_feed:
        live_feed.emit(orange_text(f"Finished the Search for the CR: '{cr}'"))

    # return page


def itsm_logout(
    page: Page, manager: DialogManager | None = None, live_feed: Signal | None = None
) -> None:
    page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")

    logout_locator_path = "//div[@class='f9' and text() = 'Logout']"
    logout_locator = page.locator(logout_locator_path)

    if logout_locator.is_visible():
        logout_locator.click()
        page.wait_for_timeout(2000)

    if live_feed:
        live_feed.emit("Logged out of ITSM")


def iframe_message_handler(
    page: Page,
    token_for_locking: bool,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> bool:
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
                    if live_feed:
                        live_feed.emit(red_text("Can't Lock the plan"))

                elif page_iframe.locator(
                    "//a[contains(@class,'PopupBtn') and normalize-space()='Ok']"
                ).is_visible():
                    result = False

    except TimeoutError:
        result = False

    finally:
        return result



def work_detail_table_reader(page: Page, 
    cr: str,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None
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
    
    if page.locator(
        '//fieldset/div/div[@id="WIN_3_301389923"]/div[2]/div'
    ).is_visible():
        table = page.locator(
            '//fieldset/div/div[@id="WIN_3_301389923"]/div[2]/div'
        ).inner_html()
        df_list = pd.read_html(StringIO(table))
        df = df_list[0]
        result = df
        # writer = pd.ExcelWriter(f"C:/Users/emaienj/Downloads/Work_Details/Work Detail Table_{cr}.xlsx", engine="openpyxl")
        # result.to_excel(writer, sheet_name="Work Detail Table")
        # # writer.save()
        # writer.close()
        # del writer
    
    return cr, result
    


def test_plan_text_hanlder(
    page: Page,
    cr: str,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Tuple[AnyStr, AnyStr]:
    result = ""
    
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

    test_plan_attachment_found = False
    
    text_attachment_locators = [
        "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[3]/fieldset/div/div[4]/textarea",
        "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[1]/textarea",
        "//fieldset[@id='WIN_3_303868700']/div[@id='WIN_3_304196500']/div/div/div[4]/fieldset/div/div[2]/textarea",
    ]

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
        
        # Opening the test plan notes    
        notes_activator_button = page.locator(
            '//fieldset/div/div/div/div/fieldset/div/div[@id="WIN_3_304247080"]/a'
        )
        
        while True:
            if notes_activator_button.is_visible():
                notes_activator_button.click()
                break
        
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_load_state("load")
        
        # Getting the test plan notes
        result = page.locator(
            '//html/body/div/table/tbody/tr[2]/td/table/tbody/tr/td/div/textarea[@id="editor"]'
        ).input_value()
        
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_load_state("load")
        
        # Closing the test plan notes
        try:
            page.locator(
                '/html/body/div/table/tbody/tr[1]/td/button[@id="ardivpcl"]'
            ).click()
        except Exception as e:
            page.locator(
                '/html/body/div/table/tbody/tr[3]/td/table/tbody/tr[1]/td[1]/button[@id="ardivpcancel"]/div'
            ).click()
        
        # Checking for the test plan attachment
        i = 0
        while i < len(text_attachment_locators):
            if page.locator(text_attachment_locators[i]).is_visible():
                test_plan_attachment = page.locator(text_attachment_locators[i]).input_value()
                if test_plan_attachment != "<File Name>":
                    test_plan_attachment_found = True
                    break
            i+=1
    
    return cr, result, test_plan_attachment_found


def get_service_plus_list(
    page: Page,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
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
    text_contents: List[str]|None = None,
    manager: DialogManager | None = None ,
    live_feed: Signal | None = None,
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
            _, relationship_nodes = relationship_nodes_handler(page, cr, manager, live_feed)
        
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


def install_plan_downloader(
    page: Page,
    folder_location: str,
    cr: str,
    cr_circle: str,
    need_install_plan: bool,
    token_for_locking: bool,
    manager: DialogManager | None,
    live_feed: Signal | None,
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
            f"{datetime.now().strftime('%d-%b-%Y')}",
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

        if live_feed:
            live_feed.emit(
                orange_text(
                    f"Downloading and locking the Install plans for cr: {cr}"
                )
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
                    token_for_locking = iframe_message_handler(
                        page, token_for_locking, manager, live_feed
                    )
                    break
                j += 1
            # i += 1

    except Exception as e:
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )

    finally:
        return install_plan_attached_to_cr, token_for_locking
    
    
def test_plan_downloader(
    page: Page,
    folder_location: str,
    cr: str,
    cr_circle: str,
    token_for_locking: bool,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Tuple[List[AnyStr], bool]:
    try:
        test_plan_download_folder = os.path.join(
            folder_location,
            "Install_and_Backout_Plan_Files",
            f"{datetime.now().strftime('%d-%b-%Y')}",
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
        
        if live_feed:
            live_feed.emit(
                orange_text(
                    f"Downloading and locking the Test plans for cr: {cr}"
                )
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
                        token_for_locking = iframe_message_handler(
                            page, token_for_locking, manager, live_feed
                        )
                        break
                    i += 1

    except Exception as e:
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )

    finally:
        # print(f"returning values =>{cr_wise_test_plan_availability_list = }, {token_for_locking = }")
        return cr_wise_test_plan_availability_list, token_for_locking


def backout_plan_downloader(
    page: Page,
    folder_location: str,
    cr: str,
    cr_circle: str,
    token_for_locking: bool,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> List[str]:
    try:
        test_plan_download_folder = os.path.join(
            folder_location,
            "Install_and_Backout_Plan_Files",
            f"{datetime.now().strftime('%d-%b-%Y')}",
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
        
        if live_feed:
            live_feed.emit(
                orange_text(
                    f"Downloading and locking the Backout plans for cr: {cr}"
                )
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
                        token_for_locking = iframe_message_handler(
                            page, token_for_locking, manager, live_feed
                        )
                        break
                    i += 1

    except Exception as e:
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )

    finally:
        return cr_wise_test_plan_availability_list, token_for_locking



def cr_approval_func(
    cr: str,
    page: Page,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Literal["Approved", "Not Approved"]:
    result = "Not Approved"
    search_for_cr(cr, page, manager, live_feed)

    try:
        wait_var = True
        username = str(os.getlogin()).strip()

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

        list_of_locators = page.locator(
            f"//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/div[@arid='301320700']/div[@class='TableInner']/div[@class='BaseTableOuter']/div/table/tbody/tr/td/nobr/span[text()='{str(username).lower()}']"
        ).all()
        # list_of_locators = page.locator(f"//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/div[@arid='301320700']/div[@class='TableInner']/div[@class='BaseTableOuter']/div/table/tbody/tr/td/nobr/span[text()='emudrup']").all()

        if len(list_of_locators) > 0:
            i = 0
            while i < len(list_of_locators):
                # print(i)
                if (
                    page.locator(
                        f"//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/div[@arid='301320700']/div[@class='TableInner']/div[@class='BaseTableOuter']/div/table/tbody/tr/td/nobr/span[text()='{str(username).lower()}']"
                    )
                    .nth(i)
                    .is_visible()
                ):
                    page.locator(
                        f"//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/div[@arid='301320700']/div[@class='TableInner']/div[@class='BaseTableOuter']/div/table/tbody/tr/td/nobr/span[text()='{str(username).lower()}']"
                    ).nth(i).click()

                    if (
                        page.locator(
                            "//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/div[@arid='304198500']/fieldset[@class=' pnl ']/a[@title='Approve']"
                        )
                        .nth(i)
                        .is_visible()
                    ):
                        # print("Approve button found")
                        page.locator(
                            "//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/div[@arid='304198500']/fieldset[@class=' pnl ']/a[@title='Approve']"
                        ).nth(i).dblclick()
                        result = "Approved"
                i += 1

    except Exception as e:
        # print(f"Error occurred while filling MOP attachment for CR {cr}: {e}")
        if manager:
            manager.show_info_signal.emit(
                f"Exception occurred ({e.__class__.__name__})!!",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )

        else:
            messagebox = Messagebox()
            messagebox.showerror(
                f"Exception occurred ({e.__class__.__name__})!!",
                f"{traceback.format_exc()}\n\n{e}",
            )

    finally:
        return result


def mop_attachment_func(
    cr: str,
    mop_attachment_string_for_notes: str,
    page: Page,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
    token_for_locking: bool = True,
) -> Literal["Success", "Failure"]:
    result = "Failure"
    search_for_cr(cr, page, manager, live_feed)

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
        page.locator(
            "//div/fieldset[@class='PageBodyHorizontal']/div[@class='PageBody pbChrome']/div/fieldset/div[@arid='304196500']/div/div/div/div/a[@class='pagebtn ']/span[@class='Twisty Tsize']"
        ).click()

        # Selecting Info
        page.locator(
            "//div/fieldset/div[@class='PageBody pbChrome']/div[@arid='304247210']/div[@class='selection']/a[@class='btn btn3d selectionbtn']"
        ).click()
        page.locator(
            "//div[@class='MenuOuter']/div[@class='MenuTableContainer']/table[@class='MenuTable']/tbody/tr/td",
            has_text="MOP",
        ).click()

        if (
            re.fullmatch(
                pattern="MOP Links:\n",
                string=mop_attachment_string_for_notes,
            )
            is None
        ):
            # Filling the Mop link attachments
            page.locator(
                "//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/div[@arwindowid='3' and @arid='304247080']/textarea[@class='text ']"
            ).fill(mop_attachment_string_for_notes)
            
            # Clicking on 'Add' button
            page.locator(
                "//div/fieldset[@class='PageBodyVertical']/div[@class='PageBody pbChrome']/a[@arid='304247110']/div[@class='btntextdiv']"
            ).click()
            
            # Clicking on the MOP links to lock them
            page.locator(
               "//div[@id='WIN_3_301389923' and @arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'MOP']" 
            ).first.dblclick()
            
            if token_for_locking:
                mop_to_be_locked = False
                mop_lock_button = page.locator(
                    "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                ).all()
                i = 0
                while i < len(mop_lock_button):
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
                            mop_to_be_locked = True
                            page.locator(
                                "//div[@arid='304247260']/fieldset[@class='fieldSetRadio']/div/span/input[@value='0']"
                            ).nth(i).click(timeout=60000)
                            break
                    i += 1
            
                if (
                    mop_to_be_locked
                    and page.locator(
                        "//div[@arid='301389923']/div[@class='TableInner']/div[@class='BaseTableOuter']/div[@class='BaseTableInner']/table[@id='T301389923']/tbody/tr/td/nobr/span[text() = 'MOP']"
                    ).first.is_visible()
                ):
                    # print(f"cr test_plan_to_be_locked : {cr}")
                    save_button_locators_for_mop = page.locator(
                        "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                    ).all()
                    i = 0
                    while i < len(save_button_locators_for_mop):
                        if (
                            page.locator(
                                "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                            )
                            .nth(i)
                            .is_visible()
                        ):
                            page.locator(
                                "//div/fieldset/div[@class='PageBody pbChrome']/a[@arid='301402700']/div[@class='btntextdiv']/div[@class='f1' and text()='Save']"
                            ).nth(i).click(timeout=60000)
                            token_for_locking = iframe_message_handler(
                                page, token_for_locking, manager, live_feed
                            )
                            break
                        i += 1 
        
            result = "Success"

    except Exception as e:
        # print(f"Error occurred while filling MOP attachment for CR {cr}: {e}")
        if manager:
            manager.show_info_signal.emit(
                f"Exception occurred ({e.__class__.__name__})!!",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )

        else:
            messagebox = Messagebox()
            messagebox.showerror(
                f"Exception occurred ({e.__class__.__name__})!!",
                f"{traceback.format_exc()}\n\n{e}",
            )

    finally:
        return result


def new_page_opener(
    context: BrowserContext,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Page | None:
    result = None
    try:
        if live_feed:
            live_feed.emit(orange_text("Opening a new page...."))

        page = context.new_page()
        page.goto(
            "https://ticketing-in.managed-services.prod.sdt.ericsson.net/arsys/forms/helixitsm-01/SHR%3ALandingConsole/Default+Administrator+View/?cacheid=45821ded",
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

        safe_evaluate(page, BMC_REMEDY_IFRAME_MODAL_WATCHER_JS)

        navigate_to_change_management(page, manager, live_feed)

        result = page

    except Exception as e:
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )

    finally:
        return result


def session_maker(
    manager: DialogManager | None = None, live_feed: Signal | None = None
) -> Tuple[bool, None | PathLike]:
    try:
        with sync_playwright() as playwright:
            browser, main_context, login_page = itsm_logger(
                playwright, manager, live_feed
            )
            session_file = main_context.storage_state(path=str(ITSM_SESSION_FILE))
            if main_context:
                main_context.close()
                del main_context

            if browser:
                browser.close()
                del browser

            if playwright:
                playwright.stop()
                # keyboard.press_and_release("ctrl+c")
                del playwright

            return True, session_file

    except Exception as e:
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )
        return False, None


def session_breaker(
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
    session_file: str | PathLike = None,
) -> None:
    """
    Breaks the already created ITSM session
    Args:
        manager: DialogManager instance
        live_feed: Signal instance
        session_file: Path to the session file
    returns:
        None
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True, executable_path=common_paths_for_browser_method()
        )
        main_context = browser.new_context(storage_state=ITSM_SESSION_FILE)
        login_page = main_context.new_page()
        login_page.goto(
            "https://ticketing-in.managed-services.prod.sdt.ericsson.net/arsys/forms/helixitsm-01/SHR%3ALandingConsole/Default+Administrator+View/?cacheid=45821ded"
        )
        # page_deleter(login_page, browser, main_context, manager, live_feed)
        # context_playwright_deleter(main_context, playwright, manager, live_feed)
        login_page.wait_for_timeout(1000)

        if login_page.locator("//div[@class='f9' and text() = 'Logout']").is_visible():
            login_page.locator("//div[@class='f9' and text() = 'Logout']").click()
            login_page.wait_for_timeout(2000)

        login_page.close()

        if main_context:
            main_context.close()

        if playwright:
            playwright.stop()
            # keyboard.press_and_release("ctrl+c")
            del playwright

    if ITSM_SESSION_FILE.exists():
        ITSM_SESSION_FILE.unlink()


def handle_niam_login(
    page: Page,
    context: BrowserContext,
    password: str,
    playwright: Playwright,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None    
):
    # password = ""

    page.wait_for_load_state("load")
    page.wait_for_timeout(500)
    while True:
        page.wait_for_timeout(500)
        try:
            # if page.locator('//div/form/div/div/div/span[text()="Bharti Airtel"]').is_visible():
            #     break
            if page.locator('//div[text()="Enter password"]').is_visible():
                break
        except:
            pass
    
    # Enter the password
    # page.locator('[id="passwordInput"]').fill(self.password)
    page.locator('//input[@id="i0118"]').fill(password)

    # Clicking on Sign in
    # page.locator('[id="submitButton"]').click()
    page.locator('//input[@id="idSIButton9"]').click()
    
    page.wait_for_load_state("load")
    
    mfa_prompt_locator = page.locator(
        "//*[text()='Approve sign in request' or text()='Verify your identity' or text()='Face, fingerprint, PIN, or security key']"
    )
    
    try:
        # Wait for either prompt to appear
        mfa_prompt_locator.first.wait_for(state="visible", timeout=15000)

        prompt_text = mfa_prompt_locator.first.text_content()
        
        # Now check which one it is
        if "Approve sign in request" in prompt_text:
            # print("Line No. 356 - Waiting for sign in approval.")
            try:
                # Wait for the prompt to disappear
                page.get_by_text("Approve sign in request").wait_for(
                    state="hidden", timeout=60000
                )
                if live_feed:
                    live_feed.emit("Waiting for sign in approval.")
                # print("Sign in approved by user.")
            except Exception as e:
                if manager:
                    # manager.show_info_signal.emit(
                    #     "  Timeout Error!",
                    #     "Timed out waiting for sign-in approval. Please try again.",
                    #     "error"
                    # )
                    pass

                else:
                    # from tkinter import messagebox
                    # from messages import Messagebox
                    # messagebox = Messagebox()
                    # messagebox.showerror(
                    #     "Timeout",
                    #     "Timed out waiting for sign-in approval. Please try again.",
                    # )
                    pass
                # raise e

        elif "Verify your identity" in prompt_text:
            # print("Line No. 367 - Verifying identity.")
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
                if manager:
                    # manager.show_info_signal.emit(
                    #     "   Timeout",
                    #     "Timed out waiting for sign-in approval after verification. Please try again.",
                    #     "error"
                    # )
                    pass

                else:
                    # from tkinter import messagebox
                    # from messages import Messagebox
                    # messagebox = Messagebox()
                    # messagebox.showerror(
                    #     "Timeout",
                    #     "Timed out waiting for sign-in approval after verification. Please try again.",
                    # )
                    pass
                # context_playwright_deleter(context, playwright)

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
                if manager:
                    # manager.show_info_signal.emit(
                    #     "   Timeout",
                    #     "Timed out waiting for sign-in approval after verification. Please try again.",
                    #     "error"
                    # )
                    pass
                else:
                    # from tkinter import messagebox
                    # from messages import Messagebox
                    # messagebox = Messagebox()
                    # messagebox.showerror(
                    #     "   Timeout",
                    #     "Timed out waiting for sign-in approval after verification. Please try again.",
                    # )
                    pass
                # context_playwright_deleter(context, playwright)

    except Exception:
        # If neither prompt appeared after waiting
        if manager:
            # manager.show_info_signal.emit(
            #     "  Timeout Error!",
            #     "MFA prompt not detected within the timeout. Assuming no MFA is required or page is different than expected.",
            #     "error"
            # )
            pass
        else:
            # from tkinter import messagebox
            # from messages import Messagebox
            # messagebox = Messagebox()
            # messagebox.showerror(
            #     "  Timeout Error!",
            #     "MFA prompt not detected within the timeout. Assuming no MFA is required or page is different than expected.",
            # )
            pass
    
    

def login_to_niam(
    page: Page, manager: DialogManager | None = None, live_feed: Signal | None = None
):
    __niam_data = NIAM_Password_Fetcher().fetch
    username = f"{str(__niam_data['username']).strip().upper()}@airtel.com"
    password = __niam_data['password']
    
    while True:
        pythoncom.PumpWaitingMessages()
        page.wait_for_timeout(500)
        try:
            # print("page.locator('//input[@id=\"username\"]').is_visible() = {}".format(page.locator('//input[@id=\"username\"]').is_visible()))
            # if page.locator('//input[@id="username"]').is_visible():
            #     break
            if page.locator('//div[text()="Sign in"]').is_visible():
                break
        except:
            pass
    # print(f"{self.olmid = }")
    page.wait_for_timeout(500)
    # page.locator('//input[@id="username"]').fill(self.olmid)
    page.locator('//input[@id="i0116"]').fill(username)

    # Clicking the Next Button
    # page.locator('[name="login"]').click()
    page.locator('//input[@id="idSIButton9"]').click()
    
    return password


def niam_logger(
    playwright: Playwright,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Tuple[Browser, BrowserContext, Page]:
    selected_path_for_browser = ""

    selected_path_for_browser = chrome_path_returner()

    browser = playwright.chromium.launch(
        executable_path=selected_path_for_browser, headless=False
    )

    # context = browser.new_context(viewport={"width": 1920, "height": 1080})
    context = browser.new_context()
    page = context.new_page()

    try:
        # page.goto("https://nextgentm-in.sdt.ericsson.net/arsys", wait_until="load")
        page.goto(
            "https://airtel.service-now.com/",
            wait_until="load",
        )

        # finding the id 'domain' and 'Employee' in the option value
        # select_element = page.locator("select#domain")
        # select_element.select_option("Employee")
        # page.wait_for_selector("//a[@id='loginBtn']")
        # page.locator(selector="//a[@id='loginBtn']", has_text="Log On").click()

        password = login_to_niam(page, manager, live_feed)

        page.wait_for_load_state("load")

        # if page.locator("//span[@class='detail-text error' and text()='Try again after some time or contact your help desk']").is_visible():
        #     # from tkinter import messagebox
        #     messagebox.showerror("Error", "Please enter the correct password")
        #     main_func(workbook=workbook)

        expect(
            page.get_by_text("Try again after some time or contact your help desk")
        ).to_be_hidden()

        handle_niam_login(page, context, password, playwright, manager, live_feed)
        
        page.wait_for_timeout(500)
        page.wait_for_load_state("networkidle")

        while True:
            page.wait_for_timeout(500)
            page.wait_for_load_state("networkidle")
            try:
                if page.locator(
                    '//div[@class="row text-title" and text()="Stay signed in?"]'
                ).is_visible(timeout=3000):
                    page.locator('//input[@id="idBtn_Back"]').click()
                    continue

                if page.locator(
                    '//*[@id="homepage-search"]/div/h2',
                    has_text="We're Here to Help You.",
                ).is_visible():
                    break
            except:
                pass

        page.wait_for_timeout(500)
        page.wait_for_load_state("networkidle")
        
    except TimeoutError:
        exception_returner(playwright, context, browser, page, manager, live_feed)

    except Exception as e:
        # from tkinter import messagebox

        if manager:
            manager.show_info_signal.emit(
                f"   Exception Occurred ({e.__class__.__name__})",
                f"{traceback.format_exc()}\n\n{str(e)}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.showerror(
                f"   Exception Occurred ({e.__class__.__name__})",
                f"{traceback.format_exc()}\n\n{str(e)}",
            )
        exception_returner(playwright, context, browser, page, manager, live_feed)

    return browser, context, page



def niam_session_maker(
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
) -> Tuple[bool, None | PathLike]:
    try:
        with sync_playwright() as playwright:
            browser, main_context, login_page = niam_logger(
                playwright, manager, live_feed
            )
            session_file = main_context.storage_state(path=str(NIAM_SESSION_FILE))
            if main_context:
                main_context.close()
                del main_context
                
            if browser:
                browser.close()
                del browser

            if playwright:
                playwright.stop()
                # keyboard.press_and_release("ctrl+c")
                del playwright

            return True, session_file
    
    except Exception as e:
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )
        return False, None


def niam_session_breaker(
    manager: DialogManager | None = None,
    live_feed: Signal | None = None
):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True, executable_path=common_paths_for_browser_method()
        )
        main_context = browser.new_context(storage_state=NIAM_SESSION_FILE)
        login_page = main_context.new_page()
        login_page.goto(
            "https://airtel.service-now.com/airtel?id=sc_cat_item&sys_id=01caf3ecdbaac30018af9ea3db9619f0",
            wait_until="load"
        )
        login_page.wait_for_timeout(1000)
        if login_page.locator(
            "//div/div/nav/div/ul/li/a[@id='profile-dropdown']"
        ).is_visible():
            login_page.locator(
                "//div/div/nav/div/ul/li/a[@id='profile-dropdown']"
            ).click()
            login_page.wait_for_timeout(1000)
        login_page.close()

        if main_context:
            main_context.close()

        if playwright:
            playwright.stop()
            # keyboard.press_and_release("ctrl+c")
            del playwright

    if NIAM_SESSION_FILE.exists():
        NIAM_SESSION_FILE.unlink()


def niam_new_page_opener(
    context: BrowserContext,
    manager: DialogManager | None = None,
    live_feed: Signal | None = None,
):
    result = None
    try:
        if live_feed:
            live_feed.emit(orange_text("Opening a new page...."))

        page = context.new_page()
        
        result = page

    except Exception as e:
        if manager:
            manager.show_info_signal.emit(
                f"  Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
                "error",
            )
        else:
            messagebox = Messagebox()
            messagebox.show_error(
                f"Exception Occurred {str(e.__class__.__name__)}",
                f"{traceback.format_exc()}\n\n{e}",
            )

    finally:
        return result
    
    
def send_input_wait_for_result_and_click(page, input_data):
    page.wait_for_load_state("networkidle")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("load")
    # page.wait_for_timeout(500)

    page.wait_for_selector(
        "//div[contains(@id, 'select2-drop')]//input[contains(@id, 's2id_autogen')]"
    )
    if page.locator(
        "//div[contains(@id, 'select2-drop')]//input[contains(@id, 's2id_autogen')]"
    ).is_visible():
        page.locator(
            "//div[contains(@id, 'select2-drop')]//input[contains(@id, 's2id_autogen')]"
        ).fill(input_data)

    start = time.time()
    while True:
        if page.locator(
            "//ul[@class='select2-results']/li/div", has_text=input_data
        ).first.is_visible():
            page.wait_for_timeout(200)
            break
        if time.time() - start > 5:
            if (
                page.locator(
                    "//div[contains(@id, 'select2-drop')]//input[contains(@id, 's2id_autogen')]"
                ).first.is_visible()
                and not page.locator(
                    "//ul[@class='select2-results']/li/div", has_text=input_data
                ).first.is_visible()
            ):
                raise Exception("Time Out")
    try:
        # options = page.locator("//ul[@class='select2-results']/li/div")
        # target_option = options.filter(has_text=re.compile(f"^{re.escape(input_data)}$"))
        # target_option.first.click()
        # page.get_by_text(input_data, exact=True).click()
        page.get_by_role("option", name=input_data, exact=True).click()
    except Exception:
        # print(f"Error clicking on input: {e}")
        try:
            page.locator(
            "//ul[@class='select2-results']/li/div", has_text=input_data
            ).first.click()
        
        except Exception as e:
            raise Exception(
                "Error clicking on input"
            )
    

def niam_locator_finder_and_input_provider(locator_list: List[AnyStr], variable_list: List[AnyStr], page: Page):
    j = 0
    while j < len(locator_list):
        locator = locator_list[j]
        var = variable_list[j]

        page.wait_for_timeout(800)
        page.locator(locator).click()
        page.wait_for_timeout(600)
        send_input_wait_for_result_and_click(page, var)
        j += 1
        
        
def wait_for_niam_ne_search_results(page: Page, results_list: Locator, timeout_ms: int = 15000) -> list:
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        items = results_list.all()
        if items:
            first_text = items[0].inner_text().strip()
            # Skip transient states
            if first_text and first_text not in ('Searching...', 'Searching…', 'Loading...'):
                return items
        page.wait_for_timeout(200)
    # timeout — return whatever we have (may be empty / still searching)
    return results_list.all()


def search_niam_ne_node(page: Page, search_input: Locator, results_list: Locator, query: str) -> list:
    search_input.fill(query)
    return wait_for_niam_ne_search_results(page, results_list)  # ← UNCOMMENT THIS


# ✅ SAFE — reads all text in a single JS call, no stale refs
def get_dropdown_texts(results_list) -> list[str]:
    try:
        texts = results_list.evaluate_all(
            "items => items.map(el => el.innerText.trim()).filter(t => t.length > 0)"
        )
        return texts
    except Exception:
        return []


def niam_tt_raiser(
    row_dict: Dict[AnyStr, AnyStr],
    page: Page,
    manager: DialogManager|None = None,
    live_feed: Signal|None = None
) -> Tuple[AnyStr, AnyStr, Union[List[AnyStr], None], Dict[AnyStr, AnyStr]]:
    cr = row_dict['SR OR CHANGE NO']
    node_names = row_dict['NIAM Node Name']
    
    result = {}
    
    Requested_For_email = row_dict["Requested For(email)"]
    Request_Type = row_dict["Request Type"]

    Request_For = row_dict["Request For"]
    Node_Managed_By = row_dict["Node Managed By"]
    Subtype = row_dict["Subtype"]

    Domain = row_dict["Domain"]

    Access_Type = str(row_dict["Access Type"])

    UID_Type = row_dict["UID Type"]

    Policy_period = row_dict["Policy period"]

    User_Type = row_dict["User Type"]

    Request_IP_10 = row_dict["Request IP>10 ?"]

    SR_CR_Start_Date_Time = str(
        row_dict["SR_CR_Start Date-Time"]
    )
    SR_CR_End_Date_Time = str(row_dict["SR_CR_End Date-Time"])

    # NIAM_Access_Start_Date_Time = str(
    #     row_dict["NIAM Access Start Date"]
    # )
    # NIAM_Access_End_Date_Time = str(
    #     row_dict["NIAM Access END Date"]
    # )
    
    Business_Justification = row_dict["Business Justification"]
    NIAM_Activity_Name = row_dict["Activity Name"]
    NIAM_Project_Name = row_dict["Project Name"]
    Execution_Location = row_dict["Execution Location"]
    
    loop_break = False
    
    first_locator_batch = [
        "//div[@id='s2id_sp_formfield_v_request_type']/a",  # Request Type
        "//div[@id='s2id_sp_formfield_node_managed_by']/a",  # Node Managed By
        "//div[@id='s2id_sp_formfield_niam_domain']/a",  # Domain
    ]
    
    second_locator_batch = [
        "//div[@id='s2id_sp_formfield_access_type']/a",  # Access Type
        "//div[@id='s2id_sp_formfield_request_ip_more_than']/a",  # Request IP > 10?
    ]
    
    first_locator_batch_variable_list = [
        Request_Type,
        Node_Managed_By,
        Domain,
    ]
    
    third_locator_batch =[
        "//div[@id='s2id_sp_formfield_v_request_for']/a",  # Request For
        "//div[@id='s2id_sp_formfield_v_subtype']/a",  # Subtype
        "//div[@id='s2id_sp_formfield_v_uid_type']/a",  # UID Type
        "//div[@id='s2id_sp_formfield_execution_location']/a",  # Execution Location
        "//div[@id='s2id_sp_formfield_policy_period']/a",  # Policy period
        "//div[@id='s2id_sp_formfield_project_name']/a",  # Project Name
        "//div[@id='s2id_sp_formfield_user_type']/a",  # User Type
        "//div[@id='s2id_sp_formfield_activity_name']/a",  # Activity Name
    ]
    
    third_locator_batch_variable_list = [
        Request_For,
        Subtype,
        UID_Type,
        Execution_Location,
        Policy_period,
        NIAM_Project_Name,
        User_Type,
        NIAM_Activity_Name,
    ]
    
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
    
    Access_Type_List = [str(element).strip() for element in Access_Type.split('and')]
    
    i = 0
    while i < len(Access_Type_List):
        try:
            if not loop_break:
                # Login to the NIAM TT Page
                page.goto(
                    "https://airtel.service-now.com/airtel?id=sc_cat_item&sys_id=01caf3ecdbaac30018af9ea3db9619f0",
                        wait_until="load",
                )
                
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_load_state("load")
                page.on("dialog", lambda dialog: dialog.dismiss())
                
                # Request For (Email)
                page.locator(
                    "//div[@id='s2id_sp_formfield_requested_for']/a"
                ).click()
                
                page.locator(
                            "//div[contains(@id, 'select2-drop')]//input[contains(@id, 's2id_autogen')]"
                        ).fill(Requested_For_email)
                
                while (
                        len(
                            page.locator("//ul[@class='select2-results']/li/div").all()
                        )
                        > 1
                    ):
                        page.wait_for_timeout(1000)
                page.wait_for_timeout(1000)

                page.locator("//ul[@class='select2-results']/li/div").click()
                
                # if condition for M2M 4G Network Optimization to add location
                if (
                    str(Requested_For_email).strip()
                    == "M2M 4G Network Optimization"
                ):
                    page.locator(
                        "//div[@id='s2id_sp_formfield_current_location']/a"
                    ).click()

                    # page.wait_for_timeout(1000)
                    page.wait_for_timeout(500)
                    page.locator(
                        "//div[contains(@id, 'select2-drop')]//input[contains(@id, 's2id_autogen')]"
                    ).fill("Noida")
                    page.wait_for_timeout(500)

                    if (
                        len(
                            page.locator(
                                "//ul[@class='select2-results']/li/div"
                            ).all()
                        )
                        > 0
                    ):
                        if (
                            len(
                                page.locator(
                                    "//ul[@class='select2-results']/li/div/*[text()='Noida']"
                                ).all()
                            )
                            > 0
                        ):
                            for element in page.locator(
                                "//ul[@class='select2-results']/li/div/*[text()='Noida']"
                            ).all():
                                element.click()
                                break
                
                niam_locator_finder_and_input_provider(
                    first_locator_batch, 
                    first_locator_batch_variable_list, 
                    page
                )
                
                niam_locator_finder_and_input_provider(
                    second_locator_batch, 
                    [
                        Access_Type_List[i],
                        Request_IP_10,
                    ],
                    page
                )
                
                node_names_list = [str(element).strip() for element in str(node_names).split('\n')]
                
                ne_field_opener = page.locator('//div[@id="select2-drop"]/ul')  # ← adjust if needed
                search_input = page.locator('//input[@id="s2id_autogen34"]')
                results_list = page.locator('//ul[@id="s2id_autogen34_results"]/li')

                loop_break = False

                for name in node_names_list:
                    selected_node = f"*{name}"
                    clicked_texts = set()
                    consecutive_failures = 0
                    MAX_FAILURES = 3
                    iteration = 0
                    MAX_ITERATIONS = 50  # hard cap — never loop more than 50 times per node

                    while iteration < MAX_ITERATIONS:
                        iteration += 1
                        # print(f"\n--- [{name}] iteration {iteration} ---")

                        # ===== STEP 1: Open the dropdown =====
                        try:
                            if not search_input.is_visible(timeout=1000):
                                ne_field_opener.click()
                                page.wait_for_timeout(400)
                        except Exception:
                            try:
                                ne_field_opener.click()
                                page.wait_for_timeout(400)
                            except Exception as e:
                                # print(f"[{name}] cannot open dropdown: {e}")
                                consecutive_failures += 1
                                if consecutive_failures >= MAX_FAILURES:
                                    break
                                continue

                        # ===== STEP 2: Type the search query =====
                        try:
                            search_input.fill("")
                            page.wait_for_timeout(150)
                            search_input.fill(selected_node)
                        except Exception as e:
                            # print(f"[{name}] cannot fill search: {e}")
                            consecutive_failures += 1
                            if consecutive_failures >= MAX_FAILURES:
                                break
                            continue

                        # ===== STEP 3: Wait for AJAX to settle =====
                        ajax_done = False
                        ajax_deadline = time.monotonic() + 10  # 10s max
                        while time.monotonic() < ajax_deadline:
                            page.wait_for_timeout(200)
                            texts = get_dropdown_texts(results_list)
                            if not texts:
                                continue
                            first_text = texts[0]
                            if first_text and first_text not in ('Searching...', 'Searching…', 'Loading...'):
                                ajax_done = True
                                break

                        if not ajax_done:
                            # print(f"[{name}] AJAX never settled")
                            consecutive_failures += 1
                            if consecutive_failures >= MAX_FAILURES:
                                break
                            continue

                        # ===== STEP 4: Read all options IN ONE JS CALL =====
                        all_texts = get_dropdown_texts(results_list)
                        # print(f"[{name}] options visible: {all_texts}")

                        # ===== STEP 5: Decide what to do =====
                        # Case A: dropdown shows "No matches found"
                        if all_texts == ['No matches found']:
                            if not clicked_texts:
                                # Never clicked anything → node truly missing
                                # print(f"[{name}] NOT FOUND in DB")
                                loop_break = True
                            # else:
                            #     # Already clicked some → exhausted matches
                            #     print(f"[{name}] all {len(clicked_texts)} matches clicked")
                            break

                        # Case B: find first option not yet clicked
                        target = None
                        for t in all_texts:
                            if t == 'No matches found':
                                continue
                            if t not in clicked_texts:
                                target = t
                                break

                        if target is None:
                            # Every visible option already clicked → done
                            # print(f"[{name}] no new options ({len(clicked_texts)} clicked total)")
                            break

                        # ===== STEP 6: Click it =====
                        try:
                            page.get_by_role('option', name=target, exact=True).click(timeout=5000)
                            clicked_texts.add(target)
                            consecutive_failures = 0
                            page.wait_for_timeout(400)
                            # print(f"[{name}] ✓ clicked: {target}")
                        except Exception as e:
                            # print(f"[{name}] click failed for {target!r}: {e}")
                            consecutive_failures += 1
                            if consecutive_failures >= MAX_FAILURES:
                                break

                    if iteration >= MAX_ITERATIONS:
                        # print(f"[{name}] hit iteration cap — bailing")
                        loop_break = True

                    if loop_break:
                        break

                if loop_break:
                    raise Exception(f"Node selection failed for: {name}")
                
                # === END OF NODE SELECTION LOOP ===

                # 1. Close dropdown
                try:
                    search_input.press("Escape")
                    page.wait_for_timeout(200)
                except Exception:
                    # 2. Tab away from the field
                    try:
                        search_input.press("Tab")
                        page.wait_for_timeout(300)
                    except Exception:
                        # 3. Click neutral area to fully defocus
                        try:
                            page.locator("//body").click(position={"x": 10, "y": 10})
                            page.wait_for_timeout(300)
                        except Exception:
                            pass

                # print("[node select] \u2705 Select2 field released. Proceeding to next field.")

                
                niam_locator_finder_and_input_provider(
                    third_locator_batch, 
                    third_locator_batch_variable_list, 
                    page
                )
                
                # CR No
                # page.locator('/html/body/div[1]/section/main/div[1]/div/sp-page-row/div/div/span[1]/div/div/div/div[2]/div/div[3]/sp-cat-item/form/div[1]/div/sp-variable-layout/div[4]/div/div[1]/div[25]/div/span/span/input').fill(cr)
                page.locator('[id="sp_formfield_sr_or_change_no"]').fill(cr)
                # page.wait_for_timeout(1000)

                # Start Date-Time
                page.locator('[id="sp_formfield_sr_cr_start_date"]').fill(
                    SR_CR_Start_Date_Time
                )
                page.keyboard.press("Enter")
                
                # End Date-Time
                page.locator('[id="sp_formfield_sr_cr_end_date"]').fill(
                    SR_CR_End_Date_Time
                )
                
                # Business Justification
                page.locator('[id="sp_formfield_v_business_justification"]').fill(
                    Business_Justification
                )
                
                # Submitting the Ticket
                
                # page.wait_for_timeout(1000)
                # page.locator('//*[text()="Submit"]').click()
                # while True:
                #     page.wait_for_timeout(500)
                #     page.wait_for_load_state("networkidle")
                #     try:
                #         if page.locator('//*[text()="Submitted"]').is_visible():
                #             # print("NIAM_Playwright Line 466")
                #             break
                #     except Exception:
                #         pass
                    
                # page.wait_for_timeout(1000)

                # page.goto(
                #     "https://airtel.service-now.com/airtel?id=requests_lists&table=sc_req_item"
                # )
                # page.wait_for_load_state("networkidle")
                # page.wait_for_timeout(500)

                # table = page.locator(
                #     '//section/main/div/div/sp-page-row/div/div/div/sp-page-row/div/div/span/div/div/div/div/div/div[2]/table/tbody/tr/td[@role="text"]'
                # ).all()
                # ritm = ""
                # if len(table) > 0:
                #     ritm = table[0].text_content().strip()
                #     result.append(ritm)
                result[Access_Type_List[i]] = "Success"
            else:
                result[Access_Type_List[i]] = "Failure"
                break
        
        except Exception:
            result[Access_Type_List[i]] = "Failure"
        i += 1
    
    return cr,node_names,result, output_dict

