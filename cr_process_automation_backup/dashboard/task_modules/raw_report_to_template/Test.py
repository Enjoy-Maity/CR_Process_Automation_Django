import pandas as pd
from pathlib import Path
import traceback
from datetime import datetime, timedelta


try:
    print("inside try block")
    Project_Folder_Path = Path(__file__).resolve().parents[3]
    workbook_path = Project_Folder_Path / "cr_process_automation" / "Standard_Template" / "PS-Core daily planning sheet.xlsx"
    intended_raw_report_path = Project_Folder_Path.joinpath(f"/ cr_process_automation / Task_Wise_Output / PS_Core_Raw_Report_{datetime.now().strftime('%Y-%m-%d')}.csv")  
    print(workbook_path)
    print(intended_raw_report_path)
    df = pd.read_excel(workbook_path)
    # print(df)

except Exception as e:
    print(f"Exception occurred: {e.__class__.__name__}")
    print(f"{traceback.format_exc()}\n\n {str(e)}","error",)

