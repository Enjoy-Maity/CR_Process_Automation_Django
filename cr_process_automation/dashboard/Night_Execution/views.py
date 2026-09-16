# dashboard/Night_Execution/views.py
"""
Night Execution views.

Renders the CR table (Start buttons per task column + a CR Status column that
is populated client-side) and exposes an endpoint that fetches ITSM CR statuses
in batches of <= 3.
"""

import json
import threading
import uuid

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
# from django.contrib.auth.decorators import login_required  # if you use auth

from dashboard.views import _timestamp
from dashboard.Night_Execution.services import (
    NIGHT_EXECUTION_TASKS,
    build_cr_status_payload_from_itsm,
)


# ── Shared runtime registry ─────────────────────────────────────────────────
# The Playwright thread and dashboard.js polling MUST see the SAME runtime dict,
# otherwise the password/OTP iframe flow deadlocks. Keyed by job_id.
# NOTE: process-local only. If you run multiple workers, use a shared store.
_JOBS = {}
_JOBS_LOCK = threading.Lock()


def _new_job():
    job_id = uuid.uuid4().hex
    runtime = {
        "status": "Starting",
        "password_required": False,
        "otp_required": False,
    }
    with _JOBS_LOCK:
        _JOBS[job_id] = {
            "runtime": runtime,
            "logs": [],
            "payload": None,   # filled when the fetch completes
            "done": False,
        }
    return job_id


def _get_job(job_id):
    with _JOBS_LOCK:
        return _JOBS.get(job_id)


# ── Page render ─────────────────────────────────────────────────────────────
# @login_required
@require_GET
def night_execution(request):
    """
    Renders the Night Execution table.

    Task columns render Start buttons; the CR Status column is filled
    client-side from the fetch-status endpoint's JSON.
    """
    # Replace with however you resolve the CRs assigned to the user.
    cr_numbers = request.session.get("assigned_crs", [])

    context = {
        "tasks": NIGHT_EXECUTION_TASKS,
        "crs": cr_numbers,
    }
    return render(request, "nightexecution.html", context)


# ── Start a status-fetch job (background thread) ────────────────────────────
# @login_required
@require_POST
def start_night_cr_status(request):
    """
    Starts a background ITSM status fetch and returns a job_id immediately.

    Body:
        { "cr_numbers": [...], "user_email": "..." }
    Returns:
        { "ok": true, "job_id": "<hex>" }
    """
    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "message": "Invalid JSON body"}, status=400
        )

    cr_numbers = body.get("cr_numbers") or []
    if not isinstance(cr_numbers, list) or not cr_numbers:
        return JsonResponse(
            {"ok": False, "message": "cr_numbers must be a non-empty list"},
            status=400,
        )

    user_email = body.get("user_email") or ""
    job_id = _new_job()
    job = _get_job(job_id)

    task = {"name": "Night Execution CR Status Fetch"}

    def _worker():
        payload, logs = build_cr_status_payload_from_itsm(
            cr_numbers=cr_numbers,
            logs=job["logs"],          # same list -> live log updates
            task=task,
            runtime=job["runtime"],    # SAME dict polled by dashboard.js
            headless_arg=False,        # OTP/password iframes need a visible browser
            timestamp_fn=_timestamp,
            user_email=user_email,
        )
        job["payload"] = payload
        job["done"] = True
        job["runtime"]["status"] = "Completed"

    threading.Thread(target=_worker, name=f"cr-status-{job_id}", daemon=True).start()
    return JsonResponse({"ok": True, "job_id": job_id})


# ── Poll job status / result ────────────────────────────────────────────────
# @login_required
@require_GET
def night_cr_status_result(request):
    """
    Polled by dashboard.js.

    Query params: ?job_id=<hex>

    Returns runtime flags (so the frontend can raise password/OTP iframes),
    plus the final statuses payload once done.
    """
    job_id = request.GET.get("job_id")
    job = _get_job(job_id)
    if not job:
        return JsonResponse({"ok": False, "message": "Unknown job_id"}, status=404)

    runtime = job["runtime"]
    resp = {
        "ok": True,
        "done": job["done"],
        "status": runtime.get("status"),
        "password_required": runtime.get("password_required", False),
        "otp_required": runtime.get("otp_required", False),
        "logs": job["logs"],
    }
    if job["done"] and job["payload"] is not None:
        resp["payload"] = job["payload"]   # {"ok":..., "statuses": {...}}
    return JsonResponse(resp)


# ── Receive password / OTP from the iframe forms ────────────────────────────
# @login_required
@require_POST
def submit_night_password(request):
    """
    Called by the password iframe. Sets runtime["password"] and fires the event
    that unblocks request_password_from_user() in the Playwright thread.
    """
    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "message": "Invalid JSON body"}, status=400)

    job = _get_job(body.get("job_id"))
    if not job:
        return JsonResponse({"ok": False, "message": "Unknown job_id"}, status=404)

    runtime = job["runtime"]
    runtime["password"] = body.get("password", "")
    runtime["password_required"] = False

    pwd_event = runtime.get("pwd_event")
    if pwd_event is not None:
        pwd_event.set()
    return JsonResponse({"ok": True})


# @login_required
@require_POST
def submit_night_otp(request):
    """
    Called by the OTP iframe. Sets runtime["otp"] and fires the event
    that unblocks request_2fa_code_from_user() in the Playwright thread.
    """
    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "message": "Invalid JSON body"}, status=400)

    job = _get_job(body.get("job_id"))
    if not job:
        return JsonResponse({"ok": False, "message": "Unknown job_id"}, status=404)

    runtime = job["runtime"]
    runtime["otp"] = body.get("otp", "")
    runtime["otp_required"] = False

    otp_event = runtime.get("otp_event")
    if otp_event is not None:
        otp_event.set()
    return JsonResponse({"ok": True})
    