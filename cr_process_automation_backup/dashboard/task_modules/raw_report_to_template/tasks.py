
import os
from dashboard.views import _timestamp
from django.http import JsonResponse
from playwright.sync_api import sync_playwright
import platform
import ctypes

# def run_task(request, task, runtime, GLOBAL_LOGS = None, timestamp_fn=None):
#     cwd = os.getcwd()
#     file_path = os.path.join(cwd, "new_file.txt")
#     GLOBAL_LOGS.append (f"{task['name']}: Creating the text file ---- {_timestamp()}")
#     with open(file_path, "w") as f:
#         f.write("Hello from current directory.\n")
    
#     GLOBAL_LOGS.append (f"{task['name']}: text file created successfully ---- {_timestamp()}")

#     runtime["status"] = "Completed"
#     runtime["download_ready"] = True
#     runtime["download_name"] = f"{task['name'].lower().replace(' ', '_')}_output.txt"

#     counts = {
#         "total_crs": 0,
#         "north_crs": 0,
#         "west_crs": 0,
#         "east_crs": 0,
#         "south_crs": 0,
#     }

#     return {
#         "status": "Completed",
#         "download_ready": True,
#         "download_name": runtime["download_name"],
#         "message": f"{task['name']} completed successfully.",
#         "counts": counts,
#     }

def check_admin_status():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            # print("✓ Script is running with Administrator privileges")
            return True
        else:
            # print("✗ Script is running in User mode")
            return False
    except Exception as e:
        # print(f"Error checking admin status: {e}")
        return False

def common_paths_for_browser_method():
    admin_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(
            "~/AppData/Local/BraveSoftware/Brave-Browser/Application/brave.exe"
        ),
    ]

    user_path = [
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        os.path.expanduser(
            "~/AppData/Local/BraveSoftware/Brave-Browser/Application/brave.exe"
        ),
    ]

    is_admin = check_admin_status()
    if is_admin:
        paths = admin_paths
    else:
        paths = user_path

    for path in paths:
        if os.path.exists(path):
            return path

    return None

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

def run_task(request, task, runtime, GLOBAL_LOGS = None, timestamp_fn=None):
    with sync_playwright() as p:
        selected_path_for_browser = ""
        selected_path_for_browser = chrome_path_returner()

        browser = p.chromium.launch(executable_path=selected_path_for_browser, headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://ticketing-in.managed-services.prod.sdt.ericsson.net/arsys/", wait_until="load",)
        title = page.title
        # browser.close()

    return JsonResponse({"ok": True, "title": title})