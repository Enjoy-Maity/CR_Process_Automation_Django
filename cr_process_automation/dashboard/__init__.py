import os
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
os.environ["ITSM_SESSION_FILE"] = os.path.join(str(root), "dashboard", "task_modules", "dependencies", "Session_store_files", "itsm_session_file.json")
os.environ["PLAYWRIGHT_BROWSERS_PATH"]=os.path.join(str(root), "pw-browsers")

# # Adding the path for task_wise_output
# os.environ.setdefault(
#     "DJANGO_DOWNLOAD_DIR", 
#     r"C:\Users\username\Desktop\my_files"
# )

os.environ["RAW_REPORT_DOWNLOAD_FOLDER"]=os.path.join(settings.HOST_DOWNLOAD_DIR, "{}",  "Raw_Report_to_Template", )

# if not os.path.exists(os.path.join(settings.HOST_DOWNLOAD_DIR, "Planning_Sheet",)):
#     Path(os.path.join(settings.HOST_DOWNLOAD_DIR, "Planning_Sheet")).mkdir(parents=True)
os.environ["PLANNING_SHEET_DOWNLOAD_FOLDER"]=os.path.join(settings.HOST_DOWNLOAD_DIR, "{}", "Planning_Sheet")
os.environ["CR_HYGIENE_CHECKS_FILE"]=os.path.join(settings.HOST_DOWNLOAD_DIR, "{}", "CR_Hygiene_Checks", "CR_Hygiene_Checks.xlsx")
os.environ["BPMS_CR_HYGIENE_CHECKS_FILE"]=os.path.join(settings.HOST_DOWNLOAD_DIR, "{}", "BPMS_CR_Hygiene_Checks", "BPMS_CR_Hygiene_Checks.xlsx")
os.environ["BPMS_DB"]=os.path.join(settings.HOST_DOWNLOAD_DIR, "BPMS_DB", "BPMS DATA.xlsx")
os.environ["PLAN_FILES_DOWNLOAD_FOLDER"]=os.path.join(settings.HOST_DOWNLOAD_DIR, "{}", "Plan_Files_Download")
os.environ["PLAN_FILES_ZIP_FILE"]=os.path.join(settings.HOST_DOWNLOAD_DIR, os.environ["PLAN_FILES_DOWNLOAD_FOLDER"], "Plan_Files_Download_{}.zip")

os.environ["PLANNING_SHEET_WORKBOOK_NAME"]= "Standard_Planning_Sheet.xlsx"
# Load variables from .env into the system environment
load_dotenv()

