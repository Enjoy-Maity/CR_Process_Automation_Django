import pandas as pd
from typing import Any
from collections import defaultdict



def run_task(request, task, runtime, GLOBAL_LOGS=None, timestamp_fn=None, selected_date=None, user_email=None, user_name=None):
    global relationship_nodes_queue
    global cr_to_relationship_node_count_dictionary
    global cr_itsm_details_dictionary
    global work_details_cr_hygiene_dictionary
    global nodes_count_remarks_dictionary
    global interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary
    global cr_to_circle_checker_dictionary
    
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

    cr_itsm_details_dictionary = defaultdict[Any, dict](dict)
    cr_to_relationship_node_count_dictionary = defaultdict[Any, int](int)
    work_details_cr_hygiene_dictionary = defaultdict[Any, dict](dict)
    nodes_count_remarks_dictionary = defaultdict[Any, bool](bool)
    interdomain_kpi_activity_name_interdomain_kpi_required_check_dictionary = defaultdict[Any, dict](dict)
    cr_to_circle_checker_dictionary = defaultdict[Any, bool](bool)


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
                timestamp_fn,
                user_email,
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
            
            except Exception:
                pass

    return {
        "status": "Completed",
        "message": f"{task['name']} completed successfully.",
        "download_ready": True,
        "download_name": report_file,
        "counts": {},
    }
