# dashboard/Night_Execution/services.py
"""
Night Execution business logic.

Kept separate from views so the status source can be swapped later
(DB, ServiceNow API, Playwright automation, etc.) without touching views.

Responsibilities:
    - Declare the task columns rendered as Start buttons per CR.
    - Log in to ITSM once (interactive OTP/password via iframe) and fetch
      each assigned CR's status in batches of <= STATUS_BATCH_SIZE.
    - Shape the CR -> status mapping into a JSON-ready payload for the frontend.
"""

import os
import traceback
import numpy as np
from queue import Queue
from threading import Event
import dashboard.task_modules.dependencies.playwright_common_methods_ as pcm
import dashboard.task_modules.dependencies.batch_methods as bm
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from playwright.sync_api import sync_playwright

from dashboard.views import _timestamp, _make_serializable


# ── Task columns config ──────────────────────────────────────────────────────
# Each task renders a Start button per CR row.
# `key` must be unique; `label` is the col_fetch_status_for_one_crumn header shown in the table.
NIGHT_EXECUTION_TASKS = [
    {"key": "automation_template", "label": "Automation Template"},
    {"key": "activity_hc",         "label": "Activity HC"},
    {"key": "activity_cli",        "label": "Activity CLI"},
    {"key": "cr_implementation",   "label": "CR Implementation Task"},
    {"key": "cr_closure",          "label": "CR Closure"},
]


# ── Batch config ─────────────────────────────────────────────────────────────
STATUS_BATCH_SIZE = 3   # keep <= 3 concurrent pages


# ── Global variables ──────────────────────────────────────────────────────────
glogs = None 
queue_ = None



# ── ITSM Thread Task ────────────────────────────────────────────────────────────
def itsm_thread_task(batch: list):
    global glogs, queue_

    stop_Event = Event()
    with sync_playwright() as thread_playwright_instance:
        browser = thread_playwright_instance.chromium.launch(
            headless=False,
            executable_path=pcm.get_browser()
        )
        logs = []
        thread_context = browser.new_context(storage_state=os.getenv("ITSM_SESSION_FILE"))
        try:
            thread_page, logs =pcm.new_page_opener(thread_context, logs)
            for cr in batch:
                retry = 0
                status = None
                while retry < 3:
                    try:
                        cr_, status, logs = cr_status_fetch_try(cr, thread_page, logs)
                        if cr == cr_:
                            if queue_:
                                queue_.put(
                                    (
                                        _make_serializable(cr),
                                        _make_serializable(status)
                                    )
                                )    
                            break
                        else:
                            retry += 1
                    except Exception as e:
                        logs.append(
                            f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
                        )
                        queue_.put(
                            _make_serializable(cr),
                            _make_serializable("Error")
                        )
                        continue
                
                if status is None:
                    queue_.put(
                            _make_serializable(cr),
                            _make_serializable("Error")
                        )
        
        except Exception as e:
            logs.append(
                f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
            )
            raise
                
        finally:
            if glogs:
                for element in logs:
                    glogs.put(_make_serializable(element))

            if thread_page:
                thread_page.close()
                del thread_page
            
            if thread_context:
                thread_context.close()
                del thread_context
            
            if browser:
                browser.close()
                del browser
            
            if thread_playwright_instance:
                thread_playwright_instance.stop()
                del thread_playwright_instance
            
            stop_Event.set()


def cr_status_fetch_try(cr, page, logs):
    try:
        return pcm.fetch_status_for_one_cr(cr, page, logs)
    except Exception as e:
        logs.append(
            f"{str(e.__class__.__name__)}\n{traceback.format_exc()}\n\n{e}"
        )
        return cr, "Error", logs



# ── ITSM status fetcher (login once, batch reads) ────────────────────────────
def fetch_cr_status_dict_from_itsm(
    cr_numbers,
    logs,
    task,
    runtime,
    headless_arg=False,
    timestamp_fn=_timestamp,
    user_email="",
):
    """
    Logs in to ITSM ONCE (interactive OTP/password via iframe), then fetches the
    status of each assigned CR in batches of <= STATUS_BATCH_SIZE using a
    ThreadPoolExecutor over pages within the same authenticated context.

    IMPORTANT: The single interactive login (OTP/password) happens once via
    itsm_logger. Do NOT run itsm_logger concurrently per CR — the user can only
    satisfy one OTP/password prompt at a time.

    Args:
        cr_numbers:   iterable of CR numbers assigned to the user.
        logs:         mutable list used for append-style logging.
        task:         task dict (must contain "name").
        runtime:      shared runtime dict (drives the password/OTP iframes).
        headless_arg: whether to run the browser headless.
        timestamp_fn: callable returning a timestamp string.
        user_email:   email used to log in to ITSM.

    Returns:
        (status_dict, logs) where status_dict = {cr_no: status_string}
    """
    assert runtime is not None, "runtime must be passed through unchanged"
    global glogs, queue_
    status_dict = {}
    cr_numbers = list(cr_numbers)
    if not cr_numbers:
        return status_dict, logs

    browser = context = login_page = playwright = None

    glogs = Queue()
    queue_ = Queue()
    unique_crs_in_df = np.array(cr_numbers)
    
    if unique_crs_in_df.size > 0:
        batch_creation_success, batches, logs = bm.main_method(
                unique_crs_in_df.tolist(),
                logs
            )

        if batch_creation_success:
            logs.append(
                f"Created {len(batches)} batches from {unique_crs_in_df.size} CRs"
            )
        
            session_created = None
        
            while not session_created:
                session_created, logs = pcm.session_maker(
                    logs,
                    task,
                    False,
                    runtime,
                    timestamp_fn,
                    user_email
                )
                
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(
                        itsm_thread_task, batch,
                    )
                    for batch in batches
                ]

                for future in futures:
                    future.result()
            
            pcm.session_breaker()

            if glogs:
                while not glogs.empty():
                    logs.append(glogs.get())
            
            if queue_:
                while not queue_.empty():
                    cr, status = queue_.get()
                    status_dict[cr] = status

    return status_dict, logs


# ── JSON payload wrappers for the website ────────────────────────────────────
def build_cr_status_payload(status_dict):
    """
    Shapes a CR -> status dict into a JSON-ready payload for the frontend
    (returned via JsonResponse in the view).

    Args:
        status_dict: {"CR12345": "Completed", "CR12346": "Pending", ...}

    Returns:
        {
            "ok": True,
            "statuses": { ... }
        }
    """
    return {"ok": True, "statuses": status_dict or {}}


def build_cr_status_payload_from_itsm(
    cr_numbers,
    logs,
    task,
    runtime,
    headless_arg=False,
    timestamp_fn=_timestamp,
    user_email="",
):
    """
    Convenience wrapper: fetch statuses from ITSM and return the JSON payload.

    Returns:
        (payload, logs) where payload has the shape produced by
        build_cr_status_payload(). On failure the payload still contains
        whatever statuses were collected (with the rest marked "Error").
    """
    try:
        status_dict, logs = fetch_cr_status_dict_from_itsm(
            cr_numbers, logs, task, runtime,
            headless_arg, timestamp_fn, user_email,
        )
        return build_cr_status_payload(status_dict), logs
    except Exception as exc:  # keep the endpoint resilient
        logs.append(
            f"{timestamp_fn()} -- build_cr_status_payload_from_itsm failed: "
            f"{type(exc).__name__}: {exc}"
        )
        return {
            "ok": False,
            "statuses": {},
            "message": f"Failed to fetch CR statuses: {exc}",
        }, logs
