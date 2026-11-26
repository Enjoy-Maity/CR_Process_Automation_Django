import os
import sys
import rootutils
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from django.conf import settings

# print("loaded all dotenv and rootutils")

# print("\n\n\n\n", os.path.dirname(os.path.dirname(__file__)), "\n\n\n\n\n\n")

default_app_config = "dashboard.DashboardConfig"

# This finds the root, sets PROJECT_ROOT env var, loads .env, and adds root to PYTHONPATH
root = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True, dotenv=True)

os.environ["PROJECT_ROOT"] = str(root)
os.environ["ITSM_SESSION_FILE"] = os.path.join(
    str(root), 
    "dashboard", 
    "task_modules", 
    "dependencies", 
    "Session_store_files", 
    "itsm_session_file.json"
)
os.environ["PLAYWRIGHT_BROWSERS_PATH"]=os.path.join(str(root), "pw-browsers")
# Assume 'root' is already defined
base_dir = Path(root).joinpath("pw-browsers")
# print(f"{base_dir = }")
# 1. Set platform-specific variables
if sys.platform == "win32":
    os_folder = "chrome-win64"
    exe_name = "chrome.exe"
else:
    os_folder = "chrome-linux64"  # Playwright's default Linux subfolder
    exe_name = "chrome"

# 2. Search for the dynamic "chromium-xxxx" folder
chromium_dirs = list(base_dir.glob("chromium-*"))
# print(chromium_dirs)

if chromium_dirs:
    # 3. Take the first match and construct the full path
    # Sort them if you want to ensure you get the latest version: sorted(chromium_dirs)[-1]
    browser_path = chromium_dirs[0] / os_folder / exe_name
    
    # 4. Set the environment variable as a string
    os.environ["BROWSER_PATH"] = str(browser_path)
else:
    raise FileNotFoundError(f"No 'chromium-*' folder found in {base_dir}")

# # Adding the path for task_wise_output
# os.environ.setdefault(
#     "DJANGO_DOWNLOAD_DIR", 
#     r"C:\Users\username\Desktop\my_files"
# )

# Generated task files use named placeholders so every caller supplies the
# task-owned date label and the selected region explicitly:
#   HOST_DOWNLOAD_FOLDER/{date}/{Task-Wise folder}/{Region-name}
os.environ["RAW_REPORT_DOWNLOAD_FOLDER"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "{date}", "Raw_Report_to_Template", "{region}")

os.environ["PLANNING_SHEET_DOWNLOAD_FOLDER"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "{date}", "Planning_Sheet", "{region}")
os.environ["CR_HYGIENE_CHECKS_FILE"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "{date}", "CR_Hygiene_Checks", "{region}", "CR_Hygiene_Checks.xlsx")
os.environ["BPMS_CR_HYGIENE_CHECKS_FILE"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "{date}", "BPMS_CR_Hygiene_Checks", "{region}", "BPMS_CR_Hygiene_Checks.xlsx")
os.environ["BPMS_DB"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "BPMS_DB", "BPMS DATA.xlsx")
os.environ["PLAN_FILES_DOWNLOAD_FOLDER"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "{date}", "Plan_Files_Download", "{region}")
os.environ["PLAN_FILES_ZIP_FILE"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "{date}", "Plan_Files_Download", "{region}", "Plan_Files_Download_{label}.zip")
os.environ["MOP_ATTACHMENT_INVENTORY_SHEET"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "MOP_ATTACHMENT_INVENTORY", "PS_Core_MOP link with Protocol.xlsx")
os.environ["MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE"]=os.path.join(settings.HOST_DOWNLOAD_FOLDER, "{date}", "Mop_Attachment_Approval", "{region}", "MOP_Attachment_Approval_status.xlsx")
os.environ["PLANNING_SHEET_WORKBOOK_NAME"]= "Standard_Planning_Sheet.xlsx"
# Load variables from .env into the system environment
load_dotenv()
