import os
import platform
import ctypes
from playwright.sync_api import sync_playwright
from dashboard.views import _timestamp

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

def chrome_path_returner() -> str:
    if platform.system() == "Windows":
        return common_paths_for_browser_method()
    return None

def run_task(request, task, runtime, GLOBAL_LOGS=None, timestamp_fn=None):
    GLOBAL_LOGS = GLOBAL_LOGS or []
    timestamp_fn = timestamp_fn or _timestamp

    runtime["status"] = "Running"
    runtime["download_ready"] = False
    runtime["otp_required"] = False
    runtime["otp"] = None

    chrome_path = chrome_path_returner()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome_path if chrome_path else None,
            headless=False,
        )
        context = browser.new_context()
        page = context.new_page()

        url = "https://ticketing-in.managed-services.prod.sdt.ericsson.net/arsys/"
        GLOBAL_LOGS.append(f"{task['name']}: opening {url} ---- {timestamp_fn()}")
        page.goto(url, wait_until="load")

        # TODO: adjust these steps to your actual login/2FA flow.
        # Example: wait until the OTP page / OTP input becomes visible.
        runtime["status"] = "Waiting for OTP"
        runtime["otp_required"] = True
        GLOBAL_LOGS.append(f"{task['name']}: waiting for OTP ---- {timestamp_fn()}")

        otp_event = runtime.get("otp_event")
        if otp_event:
            otp_event.wait(timeout=300)

        otp = runtime.get("otp")
        if not otp:
            runtime["status"] = "Failed"
            msg = "OTP not received in time."
            GLOBAL_LOGS.append(f"{task['name']}: {msg} ---- {timestamp_fn()}")
            browser.close()
            return {
                "status": "Failed",
                "message": msg,
                "download_ready": False,
                "download_name": runtime.get("download_name", ""),
                "counts": {},
            }

        # Replace selector with the real OTP field on your page.
        page.fill("input[name='otp']", otp)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        runtime["status"] = "Completed"
        GLOBAL_LOGS.append(f"{task['name']}: completed successfully ---- {timestamp_fn()}")

        browser.close()

        return {
            "status": "Completed",
            "message": f"{task['name']} completed successfully.",
            "download_ready": False,
            "download_name": runtime.get("download_name", ""),
            "counts": {},
        }