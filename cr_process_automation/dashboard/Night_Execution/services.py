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
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from playwright.sync_api import sync_playwright

from dashboard.views import _timestamp

# NOTE: adjust this import path module location/filename module location/filename.
from dashboard.task_modules.dependencies.playwright_common_methods_ import (
    itsm_logger,
    search_for_cr,
    fetch_cr_status,
    get_itsm_session_file_path,
    navigate_to_change_management,
    safe_evaluate,
)


# ── Task columns config ──────────────────────────────────────────────────────
# Each task renders a Start button per CR row.
# `key` must be unique; `label` is the column header shown in the table.
NIGHT_EXECUTION_TASKS = [
    {"key": "cr_implementation", "label": "CR Implementation Task"},
    {"key": "cr_closure",        "label": "CR Closure"},
    # add more as needed, e.g.:
    # {"key": "kpi_validation",  "label": "KPI Validation"},
]


# ── Batch config ─────────────────────────────────────────────────────────────
STATUS_BATCH_SIZE = 3   # keep <= 3 concurrent pages


# ── Per-CR worker ────────────────────────────────────────────────────────────
def _fetch_status_for_one_cr(context, cr, logs):
    """
    Runs on ONE CR using its OWN page inside the shared authenticated context.
    Returns (cr, status).

    WARNING: Playwright's sync API is not guaranteed thread-safe. If you hit
    greenlet / event-loop errors when running this under ThreadPoolExecutor,
    switch to the sequential loop (set STATUS_BATCH_SIZE = 1) or migrate to the
    async Playwright API with an asyncio.Semaphore(3).
    """
    page = None
    try:
        page = context.new_page()
        page.goto(str(os.getenv("LOGGED_ITSM_URL")), wait_until="load")
        safe_evaluate(page, settings.BMC_REMEDY_IFRAME_MODAL_WATCHER_JS)
        navigate_to_change_management(page)

        search_for_cr(page, cr, logs)
        status = fetch_cr_status(page, cr, logs)
        return cr, status
    except Exception as e:
        logs.append(
            f"{_timestamp()} -- Error processing CR '{cr}': "
            f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        )
        return cr, "Error"
    finally:
        if page is not None:
            try:
                page.close()
            except Exception:
                pass


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

    status_dict = {}
    cr_numbers = list(cr_numbers)
    if not cr_numbers:
        return status_dict, logs

    browser = context = login_page = playwright = None
    try:
        with sync_playwright() as playwright:
            # 1) Single interactive login (raises password/OTP iframes).
            browser, context, login_page, logs = itsm_logger(
                logs, playwright, headless_arg, task, runtime,
                timestamp_fn, user_email,
            )
            context.storage_state(path=get_itsm_session_file_path())
            runtime["status"] = "Fetching CR statuses"

            # 2) Batch the status reads (<= STATUS_BATCH_SIZE concurrent pages).
            for start in range(0, len(cr_numbers), STATUS_BATCH_SIZE):
                batch = cr_numbers[start:start + STATUS_BATCH_SIZE]
                logs.append(f"{timestamp_fn()} -- Processing batch: {batch}")

                with ThreadPoolExecutor(max_workers=STATUS_BATCH_SIZE) as pool:
                    futures = {
                        pool.submit(_fetch_status_for_one_cr, context, cr, logs): cr
                        for cr in batch
                    }
                    for fut in as_completed(futures):
                        cr, status = fut.result()
                        status_dict[cr] = status

    except Exception as e:
        logs.append(
            f"{timestamp_fn()} -- fetch_cr_status_dict_from_itsm failed: "
            f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        )
        # Preserve any statuses already collected; mark the rest as Error.
        for cr in cr_numbers:
            status_dict.setdefault(cr, "Error")
    finally:
        for obj in (login_page, context, browser):
            if obj:
                try:
                    obj.close()
                except Exception:
                    pass
        if playwright:
            try:
                playwright.stop()
            except Exception:
                pass
        logs.append(f"{timestamp_fn()} -- CR status fetch cleanup complete")

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
