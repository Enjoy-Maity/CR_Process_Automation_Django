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
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.clickjacking import xframe_options_sameorigin

import dashboard.views
from dashboard.views import _timestamp, GLOBAL_LOGS, CURRENT_RUNNING_TASK
from dashboard.Night_Execution.services import (
    NIGHT_EXECUTION_TASKS,
    build_cr_status_payload_from_itsm,
)
from dashboard.models import MasterCRDatabase
from django import forms

# Custom forms for Night Execution (using job_id instead of task_id)
class NightOTPForm(forms.Form):
    two_factor_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit 2FA'}),
        required=True,
        label="2FA Code"
    )
    job_id = forms.CharField(widget=forms.HiddenInput(), required=False)

class NightPasswordForm(forms.Form):
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        }),
        required=True,
        label="Password"
    )
    job_id = forms.CharField(widget=forms.HiddenInput(), required=False)


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
        "password": None,
        "otp": None,
        "pwd_event": threading.Event(),
        "otp_event": threading.Event(),
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
@login_required(login_url="login")
@require_GET
def night_execution(request):
    """
    Renders the Night Execution table.

    Task columns render Start buttons; the CR Status column is filled
    client-side from the fetch-status endpoint's JSON.
    """
    context = {
        "page_title": "Night Execution",
        "selected_option": "night_execution",
        "task_columns": NIGHT_EXECUTION_TASKS,
        "cr_rows": [],
        "user_name": (request.user.get_full_name() or request.user.username)
                     if request.user.is_authenticated else "Guest",
        "user_role": getattr(request.user, "role", "") if request.user.is_authenticated else "",
        "running_task": "",
        "task_logs": [],
        "user_email": request.user.email if request.user.is_authenticated else "",
        "menu_items": [
            {"key": "cr_planning", "label": "CR Planning", "url_name": "cr_planning"},
            {"key": "night_execution", "label": "Night Execution", "url_name": "night_execution"},
            {"key": "night_spoc", "label": "Night-SPOC", "url_name": "night_spoc"},
            {"key": "region_crs", "label": "Region CRs", "url_name": "region_crs"},
            {"key": "cr_wise_status", "label": "CR-Wise Status", "url_name": "cr_wise_status"},
            {"key": "cr_history", "label": "CR History", "url_name": "cr_history"},
        ]
    }
    return render(request, "dashboard/night_execution.html", context)


# ── Fetch CRs by date for current user ─────────────────────────────────────
@login_required(login_url="login")
@require_POST
def fetch_night_execution_crs(request):
    """
    Fetches CRs for the selected date for the current logged-in user.
    
    Body:
        { "date": "YYYY-MM-DD" }
    Returns:
        { "ok": true, "crs": [...] }
    """
    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "message": "Invalid JSON body"}, status=400
        )

    date_str = body.get("date", "").strip()
    if not date_str:
        return JsonResponse(
            {"ok": False, "message": "Date is required"}, status=400
        )

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse(
            {"ok": False, "message": "Invalid date format. Use YYYY-MM-DD."}, status=400
        )

    # Get current user information
    user_email = request.user.email if request.user.is_authenticated else None
    user_name = getattr(request.user, 'employee_name', request.user.username if request.user.is_authenticated else None)

    # Fetch CRs from MasterCRDatabase for the selected date AND current user
    # Filter by activity_executor to only show CRs assigned to the logged-in user
    # Try multiple possible user name formats
    possible_names = []
    if user_name:
        possible_names.append(user_name)
    if request.user.username:
        possible_names.append(request.user.username)
    if request.user.get_full_name():
        possible_names.append(request.user.get_full_name())
    
    # Remove duplicates and empty values
    possible_names = list(set([name for name in possible_names if name]))
    
    # Build query with OR condition for multiple possible name matches
    name_query = Q()
    for name in possible_names:
        name_query |= Q(activity_executor__icontains=name)
    
    crs = MasterCRDatabase.objects.filter(
        execution_date=selected_date,
        is_active=True
    ).filter(name_query).values(
        'cr_no', 
        'circle', 
        'activity_description',
        'activity_executor'
    )

    # Convert to list of dicts for JSON response
    cr_list = []
    for cr in crs:
        cr_list.append({
            'cr_no': cr['cr_no'],
            'circle': cr['circle'] or '',
            'activity_title': cr['activity_description'] or '',
            'change_responsible': cr['activity_executor'] or '',
            'cr_status': '',  # Will be populated by fetch status endpoint
        })

    return JsonResponse({
        "ok": True,
        "crs": cr_list,
        "message": f"Found {len(cr_list)} CRs for {date_str}"
    })


# ── Start a task for a specific CR ─────────────────────────────────────────
@login_required(login_url="login")
@require_POST
def start_night_execution_task(request):
    """
    Starts a specific task (CR Implementation or CR Closure) for a specific CR.
    
    Body:
        { "cr_no": "CR001", "task_key": "cr_implementation" }
    Returns:
        { "ok": true, "status": "success" }
    """
    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "message": "Invalid JSON body"}, status=400
        )

    cr_no = body.get("cr_no", "").strip()
    task_key = body.get("task_key", "").strip()

    if not cr_no or not task_key:
        return JsonResponse(
            {"ok": False, "message": "cr_no and task_key are required"}, status=400
        )

    # Validate task_key
    valid_tasks = {task["key"] for task in NIGHT_EXECUTION_TASKS}
    if task_key not in valid_tasks:
        return JsonResponse(
            {"ok": False, "message": f"Invalid task_key: {task_key}"}, status=400
        )

    # This is a placeholder for actual task execution logic
    # You should implement the actual task execution here based on your requirements
    # For now, we'll just return a success response
    
    # TODO: Implement actual task execution logic
    # This could involve:
    # 1. Running a background task
    # 2. Updating database records
    # 3. Calling external services
    # 4. Logging the task execution
    
    return JsonResponse({
        "ok": True,
        "status": "success",
        "message": f"Task {task_key} started for CR {cr_no}"
    })


# ── Start a status-fetch job (background thread) ────────────────────────────
class DualLogList(list):
    def __init__(self, job_logs, global_logs):
        super().__init__()
        self.job_logs = job_logs
        self.global_logs = global_logs

    def append(self, item):
        self.job_logs.append(item)
        self.global_logs.append(item)
        
    def extend(self, items):
        self.job_logs.extend(items)
        self.global_logs.extend(items)

    def __iter__(self):
        return iter(self.job_logs)
        
    def __len__(self):
        return len(self.job_logs)

@login_required(login_url="login")
@require_POST
def fetch_night_cr_status(request):
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
        dashboard.views.CURRENT_RUNNING_TASK = task["name"]
        payload, logs = build_cr_status_payload_from_itsm(
            cr_numbers=cr_numbers,
            logs=DualLogList(job["logs"], GLOBAL_LOGS),          # dual list -> live log updates
            task=task,
            runtime=job["runtime"],    # SAME dict polled by dashboard.js
            headless_arg=False,        # OTP/password iframes need a visible browser
            timestamp_fn=_timestamp,
            user_email=user_email,
        )
        job["payload"] = payload
        job["done"] = True
        job["runtime"]["status"] = "Completed"
        dashboard.views.CURRENT_RUNNING_TASK = "No task is running currently."

    threading.Thread(target=_worker, name=f"cr-status-{job_id}", daemon=True).start()
    return JsonResponse({"ok": True, "job_id": job_id})


# ── Poll job status / result ────────────────────────────────────────────────
@login_required(login_url="login")
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
@login_required(login_url="login")
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


@login_required(login_url="login")
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


# ── Iframe views for password/OTP input ────────────────────────────────────
@xframe_options_sameorigin
def night_password_iframe(request):
    """Handle password authentication via iframe for Night Execution."""
    job_id = request.GET.get("job_id")
    if not job_id:
        return render(request, 'dashboard/iframe_form.html', {
            'form': NightPasswordForm(),
            'error': 'Missing job_id'
        })

    job = _get_job(job_id)
    if not job:
        return render(request, 'dashboard/iframe_form.html', {
            'form': NightPasswordForm(),
            'error': 'Unknown job_id'
        })

    if request.method == 'POST':
        form = NightPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            runtime = job["runtime"]
            runtime["password"] = password
            runtime["password_required"] = False

            pwd_event = runtime.get("pwd_event")
            if pwd_event:
                pwd_event.set()

            return render(request, 'dashboard/iframe_form.html', {
                'form': NightPasswordForm(),
                'success': True,
                'message': 'Password submitted successfully'
            })
    else:
        form = NightPasswordForm(initial={'job_id': job_id})

    return render(request, 'dashboard/iframe_form.html', {
        'form': form,
        'job_id': job_id
    })


@xframe_options_sameorigin
def night_otp_iframe(request):
    """Handle OTP authentication via iframe for Night Execution."""
    job_id = request.GET.get("job_id")
    if not job_id:
        return render(request, 'dashboard/iframe_form.html', {
            'form': NightOTPForm(),
            'error': 'Missing job_id'
        })

    job = _get_job(job_id)
    if not job:
        return render(request, 'dashboard/iframe_form.html', {
            'form': NightOTPForm(),
            'error': 'Unknown job_id'
        })

    if request.method == 'POST':
        form = NightOTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['two_factor_code']
            runtime = job["runtime"]
            runtime["otp"] = otp
            runtime["otp_required"] = False

            otp_event = runtime.get("otp_event")
            if otp_event:
                otp_event.set()

            return render(request, 'dashboard/iframe_form.html', {
                'form': NightOTPForm(),
                'success': True,
                'message': 'OTP submitted successfully'
            })
    else:
        form = NightOTPForm(initial={'job_id': job_id})

    return render(request, 'dashboard/iframe_form.html', {
        'form': form,
        'job_id': job_id
    })
