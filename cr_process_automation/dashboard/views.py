from pathlib import Path
from dateutil import parser
from datetime import datetime, timedelta
import sqlite3
import sys
import re
import traceback
import threading
from importlib import import_module
import pandas as pd
from django.db import connection
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_GET, require_POST
from django.core.serializers.json import DjangoJSONEncoder
from .forms import LoginForm, TwoFactorAuthForm, PasswordAuthForm
# from django.contrib.auth import get_user_model
from .models import MasterCRDatabase, SelectedDateTable, UserManagement
from .exceptions import (
    ValidationException,
    NotFoundException,
    TaskExecutionException,
    AuthenticationException,
    DatabaseException
)
from .utils.exception_handler import handle_exceptions
from dashboard.services import (
    update_cr_flag_atomic,
    get_crs_by_region,
    get_cr_count_by_region,
    validate_cr_exists
)
import uuid
import logging

logger = logging.getLogger(__name__)

TASKS = [
    {"id": 1, "sequence_no": 1, "name": "RAW Report to Template", "download_required": True},
    {"id": 2, "sequence_no": 2, "name": "CR Hygiene Checks", "download_required": True},
    {"id": 3, "sequence_no": 3, "name": "Install/Test Plan Downloads", "download_required": True},
    {"id": 4, "sequence_no": 4, "name": "BPMS CR Hygiene Checks", "download_required": True},
    {"id": 5, "sequence_no": 5, "name": "MOP Attachment & Approvals", "download_required": True},
    {"id": 6, "sequence_no": 6, "name": "Final Email Package", "download_required": True},
    {"id": 7, "sequence_no": 7, "name": "NIAM Ticket Generation", "download_required": True},
]

TASKS_REQUIRING_AUTH = {1, 2, 3, 4, 5, 7}

def _requires_auth(task_id):
    """Check if a task requires authentication."""
    return task_id in TASKS_REQUIRING_AUTH

TASK_RUNTIME = {
    task["id"]: {
        "status": "Pending",
        "download_ready": False,
        "download_name": "",
        "total_crs": 0,
        "north_crs": 0,
        "west_crs": 0,
        "east_crs": 0,
        "south_crs": 0,
        "logs": [f"{task['name']} is waiting for execution."],
        "requires_auth": _requires_auth(task["id"]),
        "otp_required": False,
        "otp": None,
        "otp_event": threading.Event(),
        "password_required": False,
        "password": None,
        "pwd_event": threading.Event(),
    }
    for task in TASKS
}

GLOBAL_LOGS = ["Dashboard loaded successfully.", "Waiting for task execution."]
CURRENT_RUNNING_TASK = "No task is running currently."

REGION_DATABASES = {
    "north_crs": "North.db",
    "west_crs": "West.db",
    "east_crs": "East.db",
    "south_crs": "South.db",
}

TASK_MODULE_MAP = {
    1: "dashboard.task_modules.raw_report_to_template.tasks",
    2: "dashboard.task_modules.cr_hygiene_checks.tasks",
    3: "dashboard.task_modules.install_test_plan_downloads.tasks",
    4: "dashboard.task_modules.bpms_cr_hygiene_checks.tasks",
    5: "dashboard.task_modules.mop_attachment_approvals.tasks",
    6: "dashboard.task_modules.final_email_package.tasks",
    7: "dashboard.task_modules.niam_ticket_generation.tasks",
}


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect("cr_planning")
    message = ""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"User {username} logged in successfully")
                return redirect("cr_planning")
            message = "Invalid username or password"
            logger.warning(f"Failed login attempt for user {username}")
    else:
        form = LoginForm()
    return render(request, "dashboard/login.html", {"form": form, "message": message})


def logout_view(request):
    """Handle user logout."""
    user = request.user.username if request.user.is_authenticated else "Unknown"
    logout(request)
    logger.info(f"User {user} logged out")
    return redirect("login")


def _task_by_id(task_id):
    """Get task by ID."""
    try:
        return next((task for task in TASKS if task["id"] == task_id), None)
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        return None


def _downloads_root():
    """Get or create downloads directory."""
    root = Path(settings.MEDIA_ROOT) / "task_downloads"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _database_root():
    """Get or create database directory."""
    root = Path(settings.MEDIA_ROOT) / "generated_databases" / datetime.now().strftime("%Y-%m-%d")
    root.mkdir(parents=True, exist_ok=True)
    return root


def _timestamp():
    """Get current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _count_rows_in_sqlite(db_path):
    """Count rows in SQLite database."""
    if not db_path.exists():
        return 0
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        if not tables:
            return 0
        table_name = tables[0][0]
        row = cur.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def _load_regional_counts():
    """Load CR counts by region."""
    counts = {"north_crs": 0, "west_crs": 0, "east_crs": 0, "south_crs": 0}
    db_root = _database_root()
    for field_name, file_name in REGION_DATABASES.items():
        counts[field_name] = _count_rows_in_sqlite(db_root / file_name)
    counts["total_crs"] = sum([counts["north_crs"], counts["west_crs"], counts["east_crs"], counts["south_crs"]])
    return counts


def _apply_counts_to_tasks():
    """Apply counts to task runtime."""
    counts = _load_regional_counts()
    for task in TASKS:
        runtime = TASK_RUNTIME[task["id"]]
        runtime.update(counts)


def _build_tasks_for_ui():
    """Build task data for UI."""
    return [{**task, **TASK_RUNTIME[task["id"]]} for task in TASKS]


def _split_log(entry):
    """Split log entry into message and timestamp."""
    if "----" in entry:
        message, ts = entry.rsplit("----", 1)
        return {"message": message.strip(), "timestamp": ts.strip()}
    return {"message": entry, "timestamp": ""}


def _common_context(request):
    """Build common context for templates."""
    if request.user.is_authenticated:
        user_name = request.user.get_full_name() or request.user.username
        user_role = getattr(request.user, 'role', 'User')
    else:
        user_name = "Guest"
        user_role = "Standard User"
    
    return {
        "page_title": "CR Process Automation",
        "selected_option": "cr_planning",
        "user_name": user_name,
        "user_role": user_role,
        "running_task": CURRENT_RUNNING_TASK,
        "task_logs": [_split_log(x) for x in GLOBAL_LOGS[-20:]],
        "tasks": _build_tasks_for_ui(),
        "menu_items": [
            {"key": "cr_planning", "label": "CR Planning", "url_name": "cr_planning"},
            {"key": "night_execution", "label": "Night Execution", "url_name": "night_execution"},
            {"key": "night_spoc", "label": "Night-SPOC", "url_name": "night_spoc"},
            {"key": "region_crs", "label": "Region CRs", "url_name": "region_crs"},
            {"key": "cr_wise_status", "label": "CR-Wise Status", "url_name": "cr_wise_status"},
            {"key": "cr_history", "label": "CR History", "url_name": "cr_history"},
        ]
    }


@login_required(login_url="login")
def cr_planning_view(request):
    """Render CR planning page."""
    return render(request, "dashboard/home.html", _common_context(request))


# @login_required(login_url="login")
# def night_execution_view(request):
#     """Render night execution page."""
#     ctx = _common_context(request)
#     ctx["selected_option"] = "night_execution"
#     return render(request, "dashboard/night_execution.html", ctx)


@login_required(login_url="login")
def night_spoc_view(request):
    """Render night SPOC page."""
    ctx = _common_context(request)
    ctx["selected_option"] = "night_spoc"
    return render(request, "dashboard/night_spoc.html", ctx)


@require_POST
@login_required(login_url="login")
@handle_exceptions
def start_task(request, task_id):
    """Start a task with validation and exception handling."""
    global CURRENT_RUNNING_TASK

    try:
        task_id = int(task_id)
    except (ValueError, TypeError):
        raise ValidationException(
            "Task ID must be a valid integer.",
            title="Invalid Task ID"
        )

    task = _task_by_id(task_id)
    if not task:
        raise NotFoundException(
            f"Task with ID {task_id} not found.",
            title="Invalid Task"
        )

    # Parse date input
    selected_date = request.POST.get('date', '').strip()
    
    # Validate date for task_id 1
    if task_id in [1, 2] and not selected_date:
        raise ValidationException(
            "Please select a Date before starting this task.",
            title="Missing Date"
        )

    try:
        parsed_date = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else None
    except ValueError:
        raise ValidationException(
            "Invalid date format. Use YYYY-MM-DD.",
            title="Invalid Date Format"
        )

    # Parse region input
    region_values = request.POST.get('region', '')
    region_values = [r.strip().lower() for r in region_values.split(',') if r.strip()]
    
    logger.info(f"Starting task {task_id} with regions: {region_values}, date: {selected_date}")

    # Get user information
    user_email = request.user.email if request.user.is_authenticated else None
    user_name = getattr(request.user, 'employee_name', request.user.username if request.user.is_authenticated else None)

    # Load task module
    task_module_path = TASK_MODULE_MAP.get(task_id)
    if not task_module_path:
        raise TaskExecutionException(
            f"Module not found for '{task['name']}'.",
            title="Module Not Found"
        )

    try:
        task_module = import_module(task_module_path)
    except Exception as exc:
        logger.error(f"Import failed for module {task_module_path}: {str(exc)}", exc_info=True)
        raise TaskExecutionException(
            f"Import failed for '{task_module_path}': {str(exc)}",
            title="Module Import Failed"
        )

    if not hasattr(task_module, "run_task"):
        raise TaskExecutionException(
            f"run_task() function missing in module '{task_module_path}'.",
            title="Missing Task Function"
        )

    # Initialize runtime
    runtime = TASK_RUNTIME[task_id]
    runtime["status"] = "Running"
    runtime["requires_auth"] = _requires_auth(task_id)
    runtime["otp_required"] = False
    runtime["otp"] = None
    runtime["otp_event"] = threading.Event()
    runtime["password_required"] = False
    runtime["password"] = None
    runtime["pwd_event"] = threading.Event()

    CURRENT_RUNNING_TASK = task["name"]
    GLOBAL_LOGS.append(f"{task['name']}: task started ---- {_timestamp()}")

    def _runner():
        """Run task in background thread."""
        global CURRENT_RUNNING_TASK
        try:
            result = task_module.run_task(
                request=request,
                task=task,
                runtime=runtime,
                GLOBAL_LOGS=GLOBAL_LOGS,
                timestamp_fn=_timestamp,
                selected_date=selected_date,
                user_email=user_email,
                user_name=user_name,
                regions=region_values,
            )

            runtime["status"] = result.get("status", "Completed")
            runtime["download_ready"] = result.get("download_ready", False)
            runtime["download_name"] = result.get("download_name", "")
            if result.get("counts"):
                runtime.update(result["counts"])
            CURRENT_RUNNING_TASK = result.get("message", f"{task['name']} completed successfully.")
            GLOBAL_LOGS.append(f"{task['name']}: {CURRENT_RUNNING_TASK} ---- {_timestamp()}")
            logger.info(f"Task {task_id} completed: {CURRENT_RUNNING_TASK}")
            
        except Exception as exc:
            runtime["status"] = "Failed"
            msg = f"{task['name']} failed: {str(exc)}"
            GLOBAL_LOGS.append(f"{msg} ---- {_timestamp()}")
            GLOBAL_LOGS.append(traceback.format_exc())
            CURRENT_RUNNING_TASK = msg
            logger.error(f"Task {task_id} failed: {str(exc)}", exc_info=True)
            
        finally:
            # Safety: clear authentication flags
            runtime["otp_required"] = False
            runtime["password_required"] = False

    threading.Thread(target=_runner, daemon=True).start()

    return JsonResponse({
        "ok": True,
        "task_id": task_id,
        "message": f"{task['name']} started successfully.",
        "status": runtime["status"],
        "requires_auth": runtime["requires_auth"],
        "otp_required": runtime["otp_required"],
        "password_required": runtime["password_required"],
    })


@require_POST
@login_required(login_url="login")
@handle_exceptions
def submit_otp(request, task_id):
    """Submit OTP for authentication."""
    try:
        task_id = int(task_id)
    except (ValueError, TypeError):
        raise ValidationException("Task ID must be a valid integer.")

    task = _task_by_id(task_id)
    if not task:
        raise NotFoundException(f"Task with ID {task_id} not found.")

    if not _requires_auth(task_id):
        raise ValidationException(
            "This task does not require OTP.",
            title="Invalid Task"
        )
    
    otp = request.POST.get("otp", "").strip()
    if not otp:
        raise ValidationException(
            "OTP is required.",
            title="Missing OTP"
        )

    runtime = TASK_RUNTIME[task_id]
    runtime["otp"] = otp
    runtime["otp_required"] = False
    
    otp_event = runtime.get("otp_event")
    if otp_event:
        otp_event.set()
    
    GLOBAL_LOGS.append(f"{task['name']}: OTP received from user ---- {_timestamp()}")
    logger.info(f"OTP received for task {task_id}")
    
    return JsonResponse({
        "ok": True,
        "message": "OTP submitted successfully."
    })


@require_POST
@login_required(login_url="login")
@handle_exceptions
def submit_password(request, task_id):
    """Submit password for authentication."""
    try:
        task_id = int(task_id)
    except (ValueError, TypeError):
        raise ValidationException("Task ID must be a valid integer.")

    task = _task_by_id(task_id)
    if not task:
        raise NotFoundException(f"Task with ID {task_id} not found.")

    if not _requires_auth(task_id):
        raise ValidationException(
            "This task does not require a password.",
            title="Invalid Task"
        )

    password = request.POST.get("password", "").strip()
    if not password:
        raise ValidationException(
            "Password is required.",
            title="Missing Password"
        )

    runtime = TASK_RUNTIME[task_id]
    runtime["password"] = password
    runtime["password_required"] = False

    pwd_event = runtime.get("pwd_event")
    if pwd_event:
        pwd_event.set()

    GLOBAL_LOGS.append(f"{task['name']}: Password received from user ---- {_timestamp()}")
    logger.info(f"Password received for task {task_id}")

    return JsonResponse({
        "ok": True,
        "message": "Password submitted successfully."
    })


@require_GET
@login_required(login_url="login")
def task_dashboard_data(request):
    """Get dashboard data for all tasks."""
    tasks = []
    for task in _build_tasks_for_ui():
        task_id = task["id"]
        requires_auth = _requires_auth(task_id)
        tasks.append({
            "id": task_id,
            "status": task["status"],
            "download_ready": task["download_ready"],
            "download_name": task["download_name"],
            "download_url": f"/download/task/{task_id}/" if task["download_ready"] else "",
            "total_crs": task["total_crs"],
            "north_crs": task["north_crs"],
            "west_crs": task["west_crs"],
            "east_crs": task["east_crs"],
            "south_crs": task["south_crs"],
            "requires_auth": requires_auth,
            "otp_required": bool(task.get("otp_required", False)) if requires_auth else False,
            "password_required": bool(task.get("password_required", False)) if requires_auth else False,
        })
    
    return JsonResponse({
        "running_task": CURRENT_RUNNING_TASK,
        "logs": [_split_log(x) for x in GLOBAL_LOGS[-20:]],
        "tasks": tasks,
        "user_name": request.user.get_full_name() or request.user.username,
        "user_role": getattr(request.user, "role", ""),
        "user_email": request.user.email,
    })


@require_GET
@login_required(login_url='login')
@handle_exceptions
def download_task_output(request, task_id):
    """Download task output file."""
    try:
        task_id = int(task_id)
    except (ValueError, TypeError):
        raise ValidationException("Task ID must be a valid integer.")

    task = _task_by_id(task_id)
    if not task:
        raise NotFoundException(f"Task with ID {task_id} not found.")

    runtime = TASK_RUNTIME[task_id]
    file_path = runtime.get("download_name")

    if not file_path or not runtime.get("download_ready"):
        raise NotFoundException(
            "No file is available for download yet.",
            title="File Not Ready"
        )

    path_obj = Path(file_path)
    if not path_obj.exists():
        raise NotFoundException(
            "The requested file could not be found on the server.",
            title="File Not Found"
        )

    logger.info(f"Downloading task {task_id} output: {path_obj.name}")
    
    return FileResponse(
        open(path_obj, "rb"),
        as_attachment=True,
        filename=path_obj.name,
    )


REGION_FIELD_MAP = {
    "north": "north_crs",
    "west": "west_crs",
    "east": "east_crs",
    "south": "south_crs",
}


@require_GET
@login_required(login_url="login")
@handle_exceptions
def filter_region_crs(request):
    """Filter CRs by region and date."""
    date_str = request.GET.get("date", "").strip()
    selected_regions = request.GET.get("regions", "").strip()
    selected_regions = [r.strip().lower() for r in selected_regions.split(",") if r.strip()]

    empty_counts = {
        "total_crs": 0,
        "north_crs": 0,
        "west_crs": 0,
        "east_crs": 0,
        "south_crs": 0,
    }
    counts_all = empty_counts.copy()
    counts_planned = empty_counts.copy()

    if not date_str or not selected_regions:
        return JsonResponse({
            "ok": True,
            "counts_all": counts_all,
            "counts_planned": counts_planned,
        })

    try:
        filter_date = datetime.strptime(date_str, "%Y-%m-%d").date() + timedelta(days=1)
    except ValueError:
        raise ValidationException(
            "Invalid date format. Use YYYY-MM-DD.",
            title="Invalid Date"
        )

    # Get counts for each region
    for region_key in selected_regions:
        field_name = REGION_FIELD_MAP.get(region_key)
        if not field_name:
            continue

        # Count all CRs by execution date
        count_all = MasterCRDatabase.objects.filter(
            execution_date=filter_date,
            region__iexact=region_key,
            is_active=True,
        ).count()
        counts_all[field_name] = count_all

        # Count planned CRs
        count_planned = MasterCRDatabase.objects.filter(
            execution_date=filter_date,
            region__iexact=region_key,
            planning_status__iexact="planned",
            is_active=True,
        ).count()
        counts_planned[field_name] = count_planned

    counts_all["total_crs"] = sum([
        counts_all["north_crs"],
        counts_all["west_crs"],
        counts_all["east_crs"],
        counts_all["south_crs"]
    ])

    counts_planned["total_crs"] = sum([
        counts_planned["north_crs"],
        counts_planned["west_crs"],
        counts_planned["east_crs"],
        counts_planned["south_crs"]
    ])

    logger.info(f"Filtered CRs for date {date_str}, regions {selected_regions}")

    return JsonResponse({
        "ok": True,
        "date": date_str,
        "regions": selected_regions,
        "counts_all": counts_all,
        "counts_planned": counts_planned,
    })


@xframe_options_sameorigin
def playwright_auth_iframe(request):
    """Handle OTP authentication via iframe."""
    logger.debug(f"playwright_auth_iframe called with method={request.method}")

    if request.method == 'POST':
        form = TwoFactorAuthForm(request.POST)

        if form.is_valid():
            try:
                task_id = int(form.cleaned_data['task_id'])
                two_factor_code = form.cleaned_data['two_factor_code']

                if not _requires_auth(task_id):
                    logger.warning(f"Task {task_id} does not require auth")
                    return render(request, 'dashboard/iframe_form.html', {'form': form})

                runtime = TASK_RUNTIME.get(task_id)

                if runtime is None:
                    logger.error(f"No runtime found for task {task_id}")
                    return render(request, 'dashboard/iframe_form.html', {'form': form})

                runtime["otp"] = two_factor_code
                runtime["otp_required"] = False

                otp_event = runtime.get("otp_event")
                if otp_event:
                    otp_event.set()
                    logger.info(f"OTP event set for task {task_id}")

                GLOBAL_LOGS.append(f"Task ID {task_id}: OTP received via Iframe ---- {_timestamp()}")

                return render(request, 'dashboard/iframe_success.html')

            except ValueError as e:
                logger.error(f"Invalid task_id: {str(e)}")
                return render(request, 'dashboard/iframe_form.html', {'form': form})
        else:
            logger.warning(f"Invalid form submission: {form.errors.as_json()}")
            return render(request, 'dashboard/iframe_form.html', {'form': form})

    else:
        task_id = request.GET.get('task_id', '')
        form = TwoFactorAuthForm(initial={'task_id': task_id})

    return render(request, 'dashboard/iframe_form.html', {'form': form})


@xframe_options_sameorigin
def playwright_password_iframe(request):
    """Handle password authentication via iframe."""
    logger.debug(f"playwright_password_iframe called with method={request.method}")

    if request.method == 'POST':
        form = PasswordAuthForm(request.POST)

        if form.is_valid():
            try:
                task_id = int(form.cleaned_data['task_id'])
                password = form.cleaned_data['password']

                if not _requires_auth(task_id):
                    logger.warning(f"Task {task_id} does not require auth")
                    return render(request, 'dashboard/password_form.html', {'form': form})

                runtime = TASK_RUNTIME.get(task_id)

                if runtime is None:
                    logger.error(f"No runtime found for task {task_id}")
                    return render(request, 'dashboard/password_form.html', {'form': form})

                runtime["password"] = password
                runtime["password_required"] = False

                pwd_event = runtime.get("pwd_event")
                if pwd_event:
                    pwd_event.set()
                    logger.info(f"Password event set for task {task_id}")

                GLOBAL_LOGS.append(f"Task ID {task_id}: Password received via Iframe ---- {_timestamp()}")

                return render(request, 'dashboard/iframe_success.html')

            except ValueError as e:
                logger.error(f"Invalid task_id: {str(e)}")
                return render(request, 'dashboard/password_form.html', {'form': form})
        else:
            logger.warning(f"Invalid form submission: {form.errors.as_json()}")
            return render(request, 'dashboard/password_form.html', {'form': form})

    else:
        task_id = request.GET.get('task_id', '')
        form = PasswordAuthForm(initial={'task_id': task_id})

    return render(request, 'dashboard/password_form.html', {'form': form})


@require_GET
@login_required(login_url="login")
@handle_exceptions
def fetch_current_date_crs(request):
    """Fetch CRs for a specific date."""
    date_str = request.GET.get("date", "").strip()
    if not date_str:
        raise ValidationException(
            "Date is required.",
            title="Missing Date"
        )

    try:
        parsed_date = parser.parse(date_str).date()
    except (ValueError, TypeError):
        raise ValidationException(
            "Invalid date format.",
            title="Invalid Date"
        )

    # Try to get from SelectedDateTable first
    result = list(
        SelectedDateTable.objects.filter(
            execution_date=parsed_date,
            is_active=True
        ).values(*settings.SELECTED_DATE_TABLE_FIELDS)
    )

    if result:
        logger.info(f"Found {len(result)} CRs in SelectedDateTable for {parsed_date}")
        return JsonResponse({
            "ok": True,
            "date": date_str,
            "fields": settings.SELECTED_DATE_TABLE_FIELDS,
            "rows": result,
        }, encoder=DjangoJSONEncoder)
    else:
        # Clear and repopulate from MasterCRDatabase
        SelectedDateTable.objects.all().delete()
        objects = list(
            MasterCRDatabase.objects.filter(
                execution_date=parsed_date,
                is_active=True
            ).values(*settings.SELECTED_DATE_TABLE_FIELDS)
        )
        
        if not objects:
            raise NotFoundException(
                f"No CR found for the selected date {date_str}.",
                title="No Data"
            )

        # Bulk create in SelectedDateTable
        SelectedDateTable.objects.bulk_create([
            SelectedDateTable(**obj) for obj in objects
        ])
        
        logger.info(f"Created {len(objects)} CRs in SelectedDateTable for {parsed_date}")
        
        return JsonResponse({
            "ok": True,
            "date": date_str,
            "fields": settings.SELECTED_DATE_TABLE_FIELDS,
            "rows": objects,
        }, encoder=DjangoJSONEncoder)


@handle_exceptions
def update_hygiene_check(cr_no):
    """Update hygiene check status for a CR."""
    if not cr_no:
        raise ValidationException(
            "CR number is required.",
            title="Missing CR"
        )

    try:
        validate_cr_exists(cr_no)
        result = update_cr_flag_atomic(cr_no, "CR_Hygiene_Checks", "Passed")
        logger.info(f"Updated hygiene check for CR {cr_no}")
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to update hygiene check for CR {cr_no}: {str(e)}", exc_info=True)
        raise DatabaseException(
            f"Failed to update hygiene check: {str(e)}",
            title="Update Failed"
        )


@require_GET
@login_required(login_url="login")
def check_replica_sync_status(request, sync_id):
    """Check replica sync status (placeholder implementation)."""
    try:
        sync_id = str(sync_id).strip()
        if not sync_id:
            raise ValidationException("Sync ID is required.")
        
        logger.debug(f"Checking sync status for {sync_id}")
        
        # Placeholder: sync not implemented yet, always return complete
        # so the frontend polling loop doesn't hang forever
        return JsonResponse({
            'ok': True,
            'sync_id': sync_id,
            'status': 'complete',
            'ready': True,
            'progress_percentage': 100,
        })
        
    except ValidationException as e:
        return JsonResponse(e.to_dict(), status=e.status_code)
    except Exception as e:
        logger.error(f"Error checking sync status: {str(e)}")
        return JsonResponse({
            'ok': False,
            'message': 'Failed to check sync status'
        }, status=500)


import types

def _make_serializable(obj):
    if isinstance(obj, (types.GeneratorType, map, filter, zip)):
        return list(obj)
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_make_serializable(v) for v in obj]
    return obj


@login_required(login_url="login")
def dashboard_view(request):
    ctx = _common_context(request)
    ctx["selected_option"] = "dashboard"

    # ctx["dashboard_options"] = [
    #     {
    #         "key": "vendor_wise",
    #         "label": "Vendor Wise",
    #         "description": "Review Vendor wise CR distribution and planning analysis.",
    #     },
    #     {
    #         "key": "cr_success_rate",
    #         "label": "CR Success Rate",
    #         "description": "Review Successful, Cancelled and Rollback CR outcomes.",
    #     },
    #     {
    #         "key": "team_performance",
    #         "label": "Team Performance",
    #         "description": "Review CR workload and execution performance by team.",
    #     },
    #     {
    #         "key": "automation_cr",
    #         "label": "Automation CR",
    #         "description": "Review Automation coverage and CR analysis.",
    #     },
    # ]

    ctx["dashboard_options"] = [
        {
            "key": "vendor_wise_analysis",
            "label": "Vendor Wise",
            "description": "Review Vendor wise CR distribution and planning analysis.",
            "url_name": "vendor_wise_analysis",
        },
        {
            "key": "cr_success_rate_analysis",
            "label": "CR Success Rate",
            "description": "Review Successful, Cancelled and Rollback CR outcomes.",
            "url_name": "cr_success_rate_analysis",
        },
        {
            "key": "team_performance_analysis",
            "label": "Team Performance",
            "description": "Review CR workload and execution performance by team.",
            "url_name": "team_performance_analysis"
        },
        {
            "key": "automation_cr_analysis",
            "label": "Automation CR",
            "description": "Review Automation coverage and CR analysis.",
            "url_name": "automation_cr_analysis"
        },
    ]

    return render(request, "dashboard/dashboard.html", ctx)


# ────────────────────────────────────────────────────────────────
# View: Get the Employee List
# ────────────────────────────────────────────────────────────────
@require_GET
@login_required(login_url="login")
def fetch_user_options(request):
    # User = UserManagement()
    users = list(
        UserManagement.objects.filter(is_active=True)
        .order_by("employee_name")
        .values("id", "employee_name")   # adjust fields to what you store/display
    )
    return JsonResponse({"ok": True, "users": users})


VENDOR_ANALYSIS_FIELDS = [
    "circle",
    "region",
    "cr_no",
    "activity_status",
    "vendor",
    "execution_type",
    "planning_status",
]

def _vendor_analysis_dates(date_str="", range_key=""):
    """
    Return (start_date, end_date, error_message).

    A user may choose:
      - one exact date: YYYY-MM-DD;
      - Last One Month: 30 calendar days including today;
      - Last Three Months: 90 calendar days including today;
      - Last Six Months: 180 calendar days including today.
    """
    date_str = (date_str or "").strip()
    range_key = (range_key or "").strip()

    if date_str:
        try:
            selected_date = datetime.strptime(
                date_str,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            return None, None, "Invalid date format. Use YYYY-MM-DD."

        return selected_date, selected_date, None

    today = datetime.today().date()

    range_days = {
        "1m": 30,
        "3m": 90,
        "6m": 180,
    }

    if range_key not in range_days:
        return (
            None,
            None,
            "Select one date or choose Last One Month, "
            "Last Three Months, or Last Six Months.",
        )

    return (
        today - timedelta(days=range_days[range_key]),
        today,
        None,
    )

def _vendor_analysis_text(value, fallback="Not Mentioned"):
    """
    Normalize blank, null, pandas-like, and inconsistent text values.
    """
    if value is None:
        return fallback

    text = str(value).strip()

    if text.lower() in {
        "",
        "nan",
        "na",
        "n/a",
        "n.a",
        "n.a.",
        "none",
        "null",
        "nat",
        "<na>",
    }:
        return fallback

    return text

def _analysis_status_key(value):
    """
    Convert Activity Status variants into the three displayed buckets.
    """
    status = _vendor_analysis_text(
        value,
        fallback="",
    ).lower()

    if status == "completed":
        return "completed"

    if status in {
        "rollback",
        "rolled back",
        "rolled-back",
    }:
        return "rollback"

    if status in {
        "cancelled",
        "canceled",
        "cancel",
    }:
        return "cancelled"

    return "other"

def _analysis_execution_type_key(value):
    """
    Convert Execution Type variants into the three displayed buckets.
    """
    execution_type = _vendor_analysis_text(
        value,
        fallback="",
    ).lower()

    if execution_type in {
        "partial automation",
        "partial_automation",
        "partial-automation",
        "partialautomation",
    }:
        return "partial_automation"

    if execution_type == "automation":
        return "automation"

    if execution_type == "manual":
        return "manual"

    return "other"

def _vendor_analysis_vendor_bucket(value):
    """
    Normalize the vendor value.

    If the raw vendor text contains more than one vendor separated
    by "/" or ",", the row is grouped under a single "Combination"
    bucket. Otherwise the cleaned single vendor name is returned.
    """
    vendor_text = _vendor_analysis_text(value)

    # Split on "/" or "," (any surrounding spaces are ignored).
    parts = [
        part.strip()
        for part in re.split(r"[/,]", vendor_text)
        if part.strip()
    ]

    # More than one distinct vendor -> Combination bucket.
    if len(parts) > 1:
        return "Combination"

    # Single vendor (or fallback text) returned as-is.
    return parts[0] if parts else vendor_text

@login_required(login_url="login")
def vendor_wise_analysis_view(request):
    """
    Render Vendor Wise Analysis page.
    """
    ctx = _common_context(request)
    ctx["selected_option"] = "vendor_wise_analysis"

    return render(
        request,
        "dashboard/vendor_wise_analysis.html",
        ctx,
    )

@require_GET
@login_required(login_url="login")
def fetch_vendor_wise_analysis(request):
    """
    Return table and chart-ready Vendor Wise Analysis data.

    The summary grouping is:
        Circle + Vendor

    Only active master records are included, preventing historical
    Copy-on-Write versions from being counted.
    """
    date_str = request.GET.get("date", "")
    range_key = request.GET.get("range", "")

    start_date, end_date, error_message = _vendor_analysis_dates(
        date_str=date_str,
        range_key=range_key,
    )

    if error_message:
        return JsonResponse(
            {
                "ok": False,
                "message": error_message,
            },
            status=400,
        )

    # Requirement: query master_cr_database.
    #
    # If your project requires report reads to occur through replica,
    # change only "default" to "replica" below.
    raw_rows = list(
        MasterCRDatabase.objects
        .using("default")
        .filter(
            execution_date__isnull=False,
            execution_date__gte=start_date,
            execution_date__lte=end_date,
            is_active=True,
            planning_status__iexact="planned",
        )
        .values(*VENDOR_ANALYSIS_FIELDS)
        .order_by(
            "circle",
            "vendor",
            "cr_no",
        )
    )

    grouped = {}
    vendor_totals = {}
    heatmap = {}

    totals = {
        "total_cr": 0,
        "completed": 0,
        "rollback": 0,
        "cancelled": 0,
        "automation": 0,
        "partial_automation": 0,
        "manual": 0,
    }

    for raw_row in raw_rows:

        planning_status = _vendor_analysis_text(
                    raw_row.get("planning_status"),
                    fallback="",
                ).lower()

        if planning_status != "planned":
            continue

        circle = _vendor_analysis_text(
            raw_row.get("circle"),
        )
        vendor = _vendor_analysis_vendor_bucket(
            raw_row.get("vendor"),
        )
        region = _vendor_analysis_text(
            raw_row.get("region"),
        )

        activity_status_key = _analysis_status_key(
            raw_row.get("activity_status"),
        )
        execution_type_key = _analysis_execution_type_key(
            raw_row.get("execution_type"),
        )

        circle_vendor_key = (circle, vendor)

        if circle_vendor_key not in grouped:
            grouped[circle_vendor_key] = {
                "circle": circle,
                "vendor": vendor,
                "regions": set(),
                "total_count": 0,
                "completed": 0,
                "rollback": 0,
                "cancelled": 0,
                "automation": 0,
                "partial_automation": 0,
                "manual": 0,
            }

        summary = grouped[circle_vendor_key]
        summary["regions"].add(region)
        summary["total_count"] += 1

        totals["total_cr"] += 1

        if activity_status_key == "completed":
            summary["completed"] += 1
            totals["completed"] += 1

        elif activity_status_key == "rollback":
            summary["rollback"] += 1
            totals["rollback"] += 1

        elif activity_status_key == "cancelled":
            summary["cancelled"] += 1
            totals["cancelled"] += 1

        if execution_type_key == "automation":
            summary["automation"] += 1
            totals["automation"] += 1

        elif execution_type_key == "partial_automation":
            summary["partial_automation"] += 1
            totals["partial_automation"] += 1

        elif execution_type_key == "manual":
            summary["manual"] += 1
            totals["manual"] += 1

        if vendor not in vendor_totals:
            vendor_totals[vendor] = {
                "vendor": vendor,
                "total_count": 0,
                "completed": 0,
                "rollback": 0,
                "cancelled": 0,
                "automation": 0,
                "partial_automation": 0,
                "manual": 0,
            }

        vendor_summary = vendor_totals[vendor]
        vendor_summary["total_count"] += 1

        if activity_status_key == "completed":
            vendor_summary["completed"] += 1

        elif activity_status_key == "rollback":
            vendor_summary["rollback"] += 1

        elif activity_status_key == "cancelled":
            vendor_summary["cancelled"] += 1

        if execution_type_key == "automation":
            vendor_summary["automation"] += 1

        elif execution_type_key == "partial_automation":
            vendor_summary["partial_automation"] += 1

        elif execution_type_key == "manual":
            vendor_summary["manual"] += 1

        if vendor not in heatmap:
            heatmap[vendor] = {}

        if circle not in heatmap[vendor]:
            heatmap[vendor][circle] = {
                "total_count": 0,
                "completed": 0,
            }

        heatmap[vendor][circle]["total_count"] += 1

        if activity_status_key == "completed":
            heatmap[vendor][circle]["completed"] += 1

    summary_rows = []

    for value in grouped.values():
        summary_rows.append({
            "circle": value["circle"],
            "region": ", ".join(sorted(value["regions"])),
            "vendor": value["vendor"],
            "total_count": value["total_count"],
            "completed": value["completed"],
            "rollback": value["rollback"],
            "cancelled": value["cancelled"],
            "automation": value["automation"],
            "partial_automation": value["partial_automation"],
            "manual": value["manual"],
        })

    summary_rows.sort(
        key=lambda row: (
            row["circle"].lower(),
            row["vendor"].lower() == "combination",  # False sorts before True
            row["vendor"].lower(),
        )
    )

    vendor_rows = list(vendor_totals.values())
    vendor_rows.sort(
        key=lambda row: row["vendor"].lower()
    )

    circles = sorted({
        row["circle"]
        for row in summary_rows
    }, key=str.lower)

    vendors = sorted(
        {row["vendor"] for row in summary_rows},
        key=lambda v: (v.lower() == "combination", v.lower()),
    )

    heatmap_rows = []

    for vendor in vendors:
        values = []

        for circle in circles:
            counts = heatmap.get(vendor, {}).get(
                circle,
                {
                    "total_count": 0,
                    "completed": 0,
                },
            )

            total_count = counts["total_count"]
            completed_count = counts["completed"]

            completion_rate = (
                round((completed_count / total_count) * 100, 1)
                if total_count
                else None
            )

            values.append({
                "circle": circle,
                "total_count": total_count,
                "completed": completed_count,
                "completion_rate": completion_rate,
            })

        heatmap_rows.append({
            "vendor": vendor,
            "values": values,
        })

    total_cr = totals["total_cr"]

    completion_rate = (
        round((totals["completed"] / total_cr) * 100, 1)
        if total_cr
        else 0
    )

    automation_rate = (
        round((totals["automation"] / total_cr) * 100, 1)
        if total_cr
        else 0
    )

    if date_str:
        period_label = start_date.strftime("%d-%m-%Y")
    else:
        range_labels = {
            "1m": "Last One Month",
            "3m": "Last Three Months",
            "6m": "Last Six Months",
        }

        period_label = (
            f"{range_labels.get(range_key, 'Selected Period')} "
            f"({start_date.strftime('%d-%m-%Y')} to "
            f"{end_date.strftime('%d-%m-%Y')})"
        )

    return JsonResponse({
        "ok": True,
        "message": (
            f"Analysis generated for {total_cr} active planned CR(s), "
            f"with {len(summary_rows)} Circle/Vendor group(s)."
        ),
        "period_label": period_label,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),

        "kpis": {
            "total_cr": total_cr,
            "completed": totals["completed"],
            "rollback": totals["rollback"],
            "cancelled": totals["cancelled"],
            "completion_rate": completion_rate,
            "automation_rate": automation_rate,
        },

        "rows": summary_rows,

        "charts": {
            "vendor_status": vendor_rows,
            "vendor_execution_type": vendor_rows,
            "heatmap": {
                "circles": circles,
                "vendors": heatmap_rows,
            },
        },
    })


CR_SUCCESS_ANALYSIS_FIELDS = [
    "circle",
    "region",
    "cr_no",
    "activity_description",
    "activity_status",
    "planning_status",
]


@login_required(login_url="login")
def cr_success_rate_analysis_view(request):
    """
    Render the CR Success Rate Analysis page.
    """
    context = _common_context(request)
    context["selected_option"] = "cr_success_rate_analysis"

    return render(
        request,
        "dashboard/cr_success_rate_analysis.html",
        context,
    )


@require_GET
@login_required(login_url="login")
def fetch_cr_success_rate_analysis(request):
    """
    Build CR Success Rate analysis from active, planned MasterCRDatabase
    records for one selected execution date or one selected date range.

    Summary outputs:
    - Circle + Region status counts and total CR count.
    - Circle-only status counts for the Circle chart.
    - Region-only status counts and total CR count.
    - Overall KPI values and chart-ready status counts.
    """
    date_str = request.GET.get("date", "")
    range_key = request.GET.get("range", "")

    start_date, end_date, error_message = _vendor_analysis_dates(
        date_str=date_str,
        range_key=range_key,
    )

    if error_message:
        return JsonResponse(
            {
                "ok": False,
                "message": error_message,
            },
            status=400,
        )

    raw_rows = list(
        MasterCRDatabase.objects
        .using("default")
        .filter(
            execution_date__isnull=False,
            execution_date__gte=start_date,
            execution_date__lte=end_date,
            is_active=True,
            planning_status__iexact="planned",
        )
        .values(*CR_SUCCESS_ANALYSIS_FIELDS)
        .order_by(
            "region",
            "circle",
            "cr_no",
        )
    )

    circle_summary = {}
    circle_region_summary = {}
    region_summary = {}

    total_cr = 0
    total_completed = 0
    total_rollback = 0
    total_cancelled = 0

    for raw_row in raw_rows:
        planning_status = _vendor_analysis_text(
                    raw_row.get("planning_status"),
                    fallback="",
                ).lower()

        if planning_status != "planned":
            continue
        circle = _vendor_analysis_text(
            raw_row.get("circle"),
            fallback="Not Mentioned",
        )
        region = _vendor_analysis_text(
            raw_row.get("region"),
            fallback="Not Mentioned",
        )
        status_key = _analysis_status_key(
            raw_row.get("activity_status"),
        )

        total_cr += 1

        if circle not in circle_summary:
            circle_summary[circle] = {
                "circle": circle,
                "total_count": 0,
                "completed": 0,
                "rollback": 0,
                "cancelled": 0,
            }

        circle_region_key = (circle, region)

        if circle_region_key not in circle_region_summary:
            circle_region_summary[circle_region_key] = {
                "circle": circle,
                "region": region,
                "total_count": 0,
                "completed": 0,
                "rollback": 0,
                "cancelled": 0,
            }

        if region not in region_summary:
            region_summary[region] = {
                "region": region,
                "total_count": 0,
                "completed": 0,
                "rollback": 0,
                "cancelled": 0,
            }

        circle_row = circle_summary[circle]
        circle_region_row = circle_region_summary[circle_region_key]
        region_row = region_summary[region]

        circle_row["total_count"] += 1
        circle_region_row["total_count"] += 1
        region_row["total_count"] += 1

        if status_key == "completed":
            circle_row["completed"] += 1
            circle_region_row["completed"] += 1
            region_row["completed"] += 1
            total_completed += 1

        elif status_key == "rollback":
            circle_row["rollback"] += 1
            circle_region_row["rollback"] += 1
            region_row["rollback"] += 1
            total_rollback += 1

        elif status_key == "cancelled":
            circle_row["cancelled"] += 1
            circle_region_row["cancelled"] += 1
            region_row["cancelled"] += 1
            total_cancelled += 1

    circle_rows = list(circle_summary.values())
    circle_rows.sort(
        key=lambda row: row["circle"].lower()
    )

    circle_region_rows = list(circle_region_summary.values())
    circle_region_rows.sort(
        key=lambda row: (
            row["region"].lower(),
            row["circle"].lower(),
        )
    )

    region_rows = list(region_summary.values())
    region_rows.sort(
        key=lambda row: row["region"].lower()
    )

    completion_rate = (
        round((total_completed / total_cr) * 100, 1)
        if total_cr
        else 0
    )

    if date_str:
        period_label = start_date.strftime("%d-%m-%Y")
    else:
        range_labels = {
            "1m": "Last One Month",
            "3m": "Last Three Months",
            "6m": "Last Six Months",
        }
        period_label = (
            f"{range_labels.get(range_key, 'Selected Period')} "
            f"({start_date.strftime('%d-%m-%Y')} to "
            f"{end_date.strftime('%d-%m-%Y')})"
        )

    return JsonResponse({
        "ok": True,
        "message": (
            f"CR Success Rate Analysis generated for {total_cr} "
            f"active planned CR(s)."
        ),
        "period_label": period_label,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "kpis": {
            "total_cr": total_cr,
            "completed": total_completed,
            "completion_rate": completion_rate,
            "rollback": total_rollback,
            "cancelled": total_cancelled,
        },
        "circle_region_rows": circle_region_rows,
        "region_rows": region_rows,
        "charts": {
            "by_circle": circle_rows,
            "by_region": region_rows,
        },
    })

TEAM_PERFORMANCE_FIELDS = [
    "circle",
    "region",
    "cr_no",
    "activity_executor",
    "risk",
    "vendor",
    "execution_type",
    "activity_status",
]

def _team_risk_level(value):
    """
    Map MasterCRDatabase risk values into requested risk buckets.

    Level-1:
        1-Extensive/Widespread

    Level-2:
        2-Significant/Large

    Values outside these definitions are excluded from Level-1/Level-2
    counts but remain included in Total CRs.
    """
    risk_value = _vendor_analysis_text(
        value,
        fallback="",
    ).lower()

    if risk_value in {
        "1-extensive/widespread",
        "1 - extensive/widespread",
        "1-extensive / widespread",
        "1 - extensive / widespread",
        "level-1",
        "level 1",
        "l1",
    }:
        return "level_1"

    if risk_value in {
        "2-significant/large",
        "2 - significant/large",
        "2-significant / large",
        "2 - significant / large",
        "level-2",
        "level 2",
        "l2",
    }:
        return "level_2"

    return "other"

def _empty_team_status_summary():
    """
    Standard count structure for Circle/Region team summaries.
    """
    return {
        "total_count": 0,
        "level_1": 0,
        "level_2": 0,
        "completed": 0,
        "rollback": 0,
        "cancelled": 0,
    }

def _empty_team_execution_summary():
    """
    Standard count structure for Activity Executor + Execution Type summary.
    """
    return {
        "total_count": 0,
        "level_1": 0,
        "level_2": 0,
        "completed": 0,
        "automation": 0,
        "partial_automation": 0,
        "manual": 0,
    }


def _empty_team_vendor_summary():
    """
    Standard count structure for Activity Executor + Vendor summary.
    """
    return {
        "total_count": 0,
        "ericsson": 0,
        "nokia": 0,
        "cisco": 0,
        "huawei": 0,
        "combination": 0,
        "completed": 0,
        "rollback": 0,
        "cancelled": 0,
    }

@login_required(login_url="login")
def team_performance_analysis_view(request):
    """
    Render Team Performance Analysis page.
    """
    context = _common_context(request)
    context["selected_option"] = "team_performance_analysis"

    return render(
        request,
        "dashboard/team_performance_analysis.html",
        context,
    )

@require_GET
@login_required(login_url="login")
def fetch_team_performance_analysis(request):
    """
    Build Team Performance Analysis from active planned MasterCRDatabase
    records for one selected date or selected date range.

    Returned summaries:
    - Activity Executor consolidated summary.
    - Region + Activity Executor summary.
    - Activity Executor + Execution Type summary.
    - Activity Executor + Vendor summary.
    - Activity Executor × Circle completion-rate heatmap.
    - Activity Executor × Region completion-rate heatmap.
    """
    date_str = request.GET.get("date", "")
    range_key = request.GET.get("range", "")

    start_date, end_date, error_message = _vendor_analysis_dates(
        date_str=date_str,
        range_key=range_key,
    )

    if error_message:
        return JsonResponse(
            {
                "ok": False,
                "message": error_message,
            },
            status=400,
        )

    raw_rows = list(
        MasterCRDatabase.objects
        .using("default")
        .filter(
            execution_date__isnull=False,
            execution_date__gte=start_date,
            execution_date__lte=end_date,
            is_active=True,
            planning_status__iexact="planned",
        )
        .values(*TEAM_PERFORMANCE_FIELDS)
        .order_by(
            "activity_executor",
            "region",
            "circle",
            "cr_no",
        )
    )

    executor_summary = {}
    region_executor_summary = {}
    executor_execution_summary = {}
    executor_vendor_summary = {}
    executor_totals = {}

    executor_risk_heatmap = {}
    region_executor_heatmap = {}

    total_cr = 0
    total_completed = 0
    total_rollback = 0
    total_cancelled = 0
    total_automation = 0

    for raw_row in raw_rows:
        circle = _vendor_analysis_text(
            raw_row.get("circle"),
            fallback="Not Mentioned",
        )
        region = _vendor_analysis_text(
            raw_row.get("region"),
            fallback="Not Mentioned",
        )
        executor = _vendor_analysis_text(
            raw_row.get("activity_executor"),
            fallback="Not Mentioned",
        )

        risk_level = _team_risk_level(
            raw_row.get("risk"),
        )
        status_key = _analysis_status_key(
            raw_row.get("activity_status"),
        )
        execution_key = _analysis_execution_type_key(
            raw_row.get("execution_type"),
        )
        vendor_bucket = _vendor_analysis_vendor_bucket(
            raw_row.get("vendor"),
        )

        total_cr += 1

        # ------------------------------------------------------------
        # 1. Consolidated Activity Executor Summary
        # ------------------------------------------------------------
        if executor not in executor_summary:
            executor_summary[executor] = {
                "activity_executor": executor,
                "total_count": 0,
                "level_1": 0,
                "level_2": 0,
                "completed": 0,
                "rollback": 0,
                "cancelled": 0,
            }

        executor_summary_row = executor_summary[executor]
        executor_summary_row["total_count"] += 1

        # ------------------------------------------------------------
        # 2. Region + Activity Executor Summary
        # ------------------------------------------------------------
        region_executor_key = (region, executor)

        if region_executor_key not in region_executor_summary:
            region_executor_summary[region_executor_key] = {
                "region": region,
                "activity_executor": executor,
                **_empty_team_status_summary(),
            }

        region_executor_row = region_executor_summary[
            region_executor_key
        ]
        region_executor_row["total_count"] += 1

        # ------------------------------------------------------------
        # 3. Activity Executor + Execution Type Summary
        # ------------------------------------------------------------
        if executor not in executor_execution_summary:
            executor_execution_summary[executor] = {
                "activity_executor": executor,
                **_empty_team_execution_summary(),
            }

        executor_execution_row = executor_execution_summary[
            executor
        ]
        executor_execution_row["total_count"] += 1

        # ------------------------------------------------------------
        # 4. Activity Executor + Vendor Summary
        # ------------------------------------------------------------
        if executor not in executor_vendor_summary:
            executor_vendor_summary[executor] = {
                "activity_executor": executor,
                **_empty_team_vendor_summary(),
            }

        executor_vendor_row = executor_vendor_summary[
            executor
        ]
        executor_vendor_row["total_count"] += 1

        # ------------------------------------------------------------
        # 5. Executor totals for stacked status/execution charts
        # ------------------------------------------------------------
        if executor not in executor_totals:
            executor_totals[executor] = {
                "activity_executor": executor,
                "total_count": 0,
                "completed": 0,
                "rollback": 0,
                "cancelled": 0,
                "automation": 0,
                "partial_automation": 0,
                "manual": 0,
            }

        executor_total_row = executor_totals[executor]
        executor_total_row["total_count"] += 1

        # ------------------------------------------------------------
        # 6. Activity Executor × Risk heatmap aggregation.
        #
        # Rows: Level-1, Level-2
        # Columns: Activity Executor
        # Values: completion percentage
        # ------------------------------------------------------------
        if risk_level in {"level_1", "level_2"}:
            if risk_level not in executor_risk_heatmap:
                executor_risk_heatmap[risk_level] = {}

            if executor not in executor_risk_heatmap[risk_level]:
                executor_risk_heatmap[risk_level][executor] = {
                    "total_count": 0,
                    "completed": 0,
                }

            executor_risk_heatmap[risk_level][executor][
                "total_count"
            ] += 1

        # ------------------------------------------------------------
        # 7. Region × Activity Executor heatmap aggregation.
        #
        # Rows: Region
        # Columns: Activity Executor
        # Values: completion percentage
        # ------------------------------------------------------------
        if region not in region_executor_heatmap:
            region_executor_heatmap[region] = {}

        if executor not in region_executor_heatmap[region]:
            region_executor_heatmap[region][executor] = {
                "total_count": 0,
                "completed": 0,
            }

        region_executor_heatmap[region][executor][
            "total_count"
        ] += 1

        # ------------------------------------------------------------
        # Risk-level counts
        # ------------------------------------------------------------
        if risk_level == "level_1":
            executor_summary_row["level_1"] += 1
            region_executor_row["level_1"] += 1
            executor_execution_row["level_1"] += 1

        elif risk_level == "level_2":
            executor_summary_row["level_2"] += 1
            region_executor_row["level_2"] += 1
            executor_execution_row["level_2"] += 1

        # ------------------------------------------------------------
        # Activity-status counts
        # ------------------------------------------------------------
        if status_key == "completed":
            executor_summary_row["completed"] += 1
            region_executor_row["completed"] += 1
            executor_execution_row["completed"] += 1
            executor_vendor_row["completed"] += 1
            executor_total_row["completed"] += 1

            if risk_level in {"level_1", "level_2"}:
                executor_risk_heatmap[risk_level][executor][
                    "completed"
                ] += 1

            region_executor_heatmap[region][executor][
                "completed"
            ] += 1


            total_completed += 1

        elif status_key == "rollback":
            executor_summary_row["rollback"] += 1
            region_executor_row["rollback"] += 1
            executor_vendor_row["rollback"] += 1
            executor_total_row["rollback"] += 1
            total_rollback += 1

        elif status_key == "cancelled":
            executor_summary_row["cancelled"] += 1
            region_executor_row["cancelled"] += 1
            executor_vendor_row["cancelled"] += 1
            executor_total_row["cancelled"] += 1
            total_cancelled += 1

        # ------------------------------------------------------------
        # Execution-type counts
        # ------------------------------------------------------------
        if execution_key == "automation":
            executor_execution_row["automation"] += 1
            executor_total_row["automation"] += 1
            total_automation += 1

        elif execution_key == "partial_automation":
            executor_execution_row["partial_automation"] += 1
            executor_total_row["partial_automation"] += 1

        elif execution_key == "manual":
            executor_execution_row["manual"] += 1
            executor_total_row["manual"] += 1

        # ------------------------------------------------------------
        # Vendor-bucket counts
        # ------------------------------------------------------------

        vendor_bucket_key = vendor_bucket.strip().lower()

        if vendor_bucket_key == "ericsson":
            executor_vendor_row["ericsson"] += 1

        elif vendor_bucket_key == "nokia":
            executor_vendor_row["nokia"] += 1
        
        elif vendor_bucket_key == "cisco":
            executor_vendor_row["cisco"] += 1
        
        elif vendor_bucket_key == "huawei":
            executor_vendor_row["huawei"] += 1

        elif vendor_bucket == "combination":
            executor_vendor_row["combination"] += 1

    # ------------------------------------------------------------
    # Build sorted output tables
    # ------------------------------------------------------------
    executor_summary_rows = list(executor_summary.values())
    executor_summary_rows.sort(
        key=lambda row: row["activity_executor"].lower()
    )

    region_executor_rows = list(region_executor_summary.values())
    region_executor_rows.sort(
        key=lambda row: (
            row["region"].lower(),
            row["activity_executor"].lower(),
        )
    )

    executor_execution_rows = list(
        executor_execution_summary.values()
    )
    executor_execution_rows.sort(
        key=lambda row: row["activity_executor"].lower()
    )

    executor_vendor_rows = list(executor_vendor_summary.values())
    executor_vendor_rows.sort(
        key=lambda row: row["activity_executor"].lower()
    )

    executor_total_rows = list(executor_totals.values())
    executor_total_rows.sort(
        key=lambda row: row["activity_executor"].lower()
    )

    executor_labels = sorted(
        executor_summary.keys(),
        key=str.lower,
    )

    executor_labels = sorted(
        executor_summary.keys(),
        key=str.lower,
    )

    risk_labels = ["level_1", "level_2"]

    risk_label_map = {
        "level_1": "Level-1",
        "level_2": "Level-2",
    }

    region_labels = sorted(
        region_executor_heatmap.keys(),
        key=str.lower,
    )

    # ------------------------------------------------------------
    # Build Risk × Activity Executor heatmap:
    # rows = risk levels; columns = executors.
    # ------------------------------------------------------------
    risk_heatmap_rows = []

    for risk_key in risk_labels:
        values = []

        for executor in executor_labels:
            counts = executor_risk_heatmap.get(
                risk_key,
                {},
            ).get(
                executor,
                {
                    "total_count": 0,
                    "completed": 0,
                },
            )

            total_count = counts["total_count"]
            completed = counts["completed"]

            completion_rate = (
                round((completed / total_count) * 100, 1)
                if total_count
                else None
            )

            values.append({
                "activity_executor": executor,
                "total_count": total_count,
                "completed": completed,
                "completion_rate": completion_rate,
            })

        risk_heatmap_rows.append({
            "risk_key": risk_key,
            "risk_label": risk_label_map[risk_key],
            "values": values,
        })

    # ------------------------------------------------------------
    # Build Region × Activity Executor heatmap:
    # rows = regions; columns = executors.
    # ------------------------------------------------------------
    region_executor_heatmap_rows = []

    for region in region_labels:
        values = []

        for executor in executor_labels:
            counts = region_executor_heatmap.get(
                region,
                {},
            ).get(
                executor,
                {
                    "total_count": 0,
                    "completed": 0,
                },
            )

            total_count = counts["total_count"]
            completed = counts["completed"]

            completion_rate = (
                round((completed / total_count) * 100, 1)
                if total_count
                else None
            )

            values.append({
                "activity_executor": executor,
                "total_count": total_count,
                "completed": completed,
                "completion_rate": completion_rate,
            })

        region_executor_heatmap_rows.append({
            "region": region,
            "values": values,
        })

    completion_rate = (
        round((total_completed / total_cr) * 100, 1)
        if total_cr
        else 0
    )

    automation_rate = (
        round((total_automation / total_cr) * 100, 1)
        if total_cr
        else 0
    )

    if date_str:
        period_label = start_date.strftime("%d-%m-%Y")
    else:
        range_labels = {
            "1m": "Last One Month",
            "3m": "Last Three Months",
            "6m": "Last Six Months",
        }

        period_label = (
            f"{range_labels.get(range_key, 'Selected Period')} "
            f"({start_date.strftime('%d-%m-%Y')} to "
            f"{end_date.strftime('%d-%m-%Y')})"
        )

    return JsonResponse({
        "ok": True,
        "message": (
            f"Team Performance Analysis generated for {total_cr} "
            f"active planned CR(s)."
        ),
        "period_label": period_label,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),

        "kpis": {
            "total_cr": total_cr,
            "completed": total_completed,
            "completion_rate": completion_rate,
            "automation_rate": automation_rate,
            "rollback": total_rollback,
            "cancelled": total_cancelled,
        },

        "executor_summary_rows": executor_summary_rows,
        "region_executor_rows": region_executor_rows,
        "executor_execution_rows": executor_execution_rows,
        "executor_vendor_rows": executor_vendor_rows,

        "charts": {
            "executor_status": executor_total_rows,

            # Use execution-specific rows. This guarantees all executors,
            # including those without a completed/rollback/cancelled record,
            # are represented with their execution-type counters.
            "executor_execution": executor_total_rows,

            "risk_executor_heatmap": {
                "executors": executor_labels,
                "risks": risk_heatmap_rows,
            },

            "region_executor_heatmap": {
                "executors": executor_labels,
                "regions": region_executor_heatmap_rows,
            },
        },
    })


AUTOMATION_CR_FIELDS = [
    "region",
    "cr_no",
    "bpms_cr_yes_no",
    "activity_type",
    "vendor",
    "execution_type",
    "activity_status",
    "planning_status",
]


def _automation_bpms_key(value):
    """Normalize BPMS CR Yes/No text into 'yes' / 'no' / 'other'."""
    bpms = _vendor_analysis_text(value, fallback="").lower()

    if bpms in {"yes", "y", "true", "1"}:
        return "bpms"

    if bpms in {"no", "n", "false", "0"}:
        return "non_bpms"

    return "other"

def _automation_activity_identity(value):
    """
    Create a normalized identity for Activity Type grouping.

    Handles differences in:
    - letter case
    - leading/trailing spaces
    - multiple spaces between words
    """
    text = _vendor_analysis_text(
        value,
        fallback="Not Mentioned",
    )

    return re.sub(r"\s+", " ", text).strip().lower()


@login_required(login_url="login")
def automation_cr_analysis_view(request):
    """Render Automation CR Analysis page."""
    ctx = _common_context(request)
    ctx["selected_option"] = "automation_cr_analysis"

    return render(
        request,
        "dashboard/automation_cr_analysis.html",
        ctx,
    )



@require_GET
@login_required(login_url="login")
def fetch_automation_cr_analysis(request):
    """
    Return chart-ready Automation CR Analysis data.

    Filters:
        - One selected execution date or a date range.
        - planning_status = planned.
        - activity_status = completed.
        - is_active = True.

    Summary:
        - One unique row per Activity Type.
        - Duplicate Activity Type records are merged.
        - Counts are aggregated for BPMS, Non-BPMS, Automation,
          Partial Automation and Manual.

    Charts:
        - Vendor Execution Type chart.
        - Vendor versus Region Automation Rate heatmap.
        - Activity Type versus Execution Type Automation Rate heatmap.
    """
    date_str = request.GET.get("date", "").strip()
    range_key = request.GET.get("range", "").strip()

    start_date, end_date, error_message = _vendor_analysis_dates(
        date_str=date_str,
        range_key=range_key,
    )

    if error_message:
        return JsonResponse(
            {
                "ok": False,
                "message": error_message,
            },
            status=400,
        )

    raw_rows = list(
        MasterCRDatabase.objects
        .using("default")
        .filter(
            execution_date__isnull=False,
            execution_date__gte=start_date,
            execution_date__lte=end_date,
            is_active=True,
            planning_status__iexact="planned",
            activity_status__iexact="completed",
        )
        .values(*AUTOMATION_CR_FIELDS)
        .order_by(
            "region",
            "activity_type",
            "vendor",
            "cr_no",
        )
    )

    activity_summary = {}
    vendor_totals = {}
    vendor_region_heatmap = {}
    activity_execution_heatmap = {}

    totals = {
        "total_cr": 0,
        "bpms": 0,
        "non_bpms": 0,
        "automation": 0,
        "partial_automation": 0,
        "manual": 0,
    }

    for raw_row in raw_rows:
        # Defensive validation even though the queryset already filters
        # these values.
        planning_status = _vendor_analysis_text(
            raw_row.get("planning_status"),
            fallback="",
        ).lower()

        activity_status = _vendor_analysis_text(
            raw_row.get("activity_status"),
            fallback="",
        ).lower()

        if planning_status != "planned":
            continue

        if activity_status != "completed":
            continue

        # Display value and normalized grouping key.
        activity_type_label = _vendor_analysis_text(
            raw_row.get("activity_type"),
            fallback="Not Mentioned",
        )

        activity_type_key = _automation_activity_identity(
            activity_type_label
        )

        region = _vendor_analysis_text(
            raw_row.get("region"),
            fallback="Not Mentioned",
        )

        vendor = _vendor_analysis_vendor_bucket(
            raw_row.get("vendor")
        )

        bpms_key = _automation_bpms_key(
            raw_row.get("bpms_cr_yes_no")
        )

        execution_type_key = _analysis_execution_type_key(
            raw_row.get("execution_type")
        )

        # ------------------------------------------------------------
        # 1. Activity Type summary
        #
        # One row is created for each normalized Activity Type.
        # Duplicate Activity Type rows are merged here.
        # ------------------------------------------------------------
        if activity_type_key not in activity_summary:
            activity_summary[activity_type_key] = {
                "activity_type": activity_type_label,
                "total_count": 0,
                "bpms": 0,
                "non_bpms": 0,
                "automation": 0,
                "partial_automation": 0,
                "manual": 0,
            }

        activity_summary_row = activity_summary[activity_type_key]

        activity_summary_row["total_count"] += 1
        totals["total_cr"] += 1

        if bpms_key == "bpms":
            activity_summary_row["bpms"] += 1
            totals["bpms"] += 1

        elif bpms_key == "non_bpms":
            activity_summary_row["non_bpms"] += 1
            totals["non_bpms"] += 1

        if execution_type_key == "automation":
            activity_summary_row["automation"] += 1
            totals["automation"] += 1

        elif execution_type_key == "partial_automation":
            activity_summary_row["partial_automation"] += 1
            totals["partial_automation"] += 1

        elif execution_type_key == "manual":
            activity_summary_row["manual"] += 1
            totals["manual"] += 1

        # ------------------------------------------------------------
        # 2. Vendor execution-type chart
        # ------------------------------------------------------------
        if vendor not in vendor_totals:
            vendor_totals[vendor] = {
                "vendor": vendor,
                "total_count": 0,
                "automation": 0,
                "partial_automation": 0,
                "manual": 0,
            }

        vendor_summary = vendor_totals[vendor]
        vendor_summary["total_count"] += 1

        if execution_type_key == "automation":
            vendor_summary["automation"] += 1

        elif execution_type_key == "partial_automation":
            vendor_summary["partial_automation"] += 1

        elif execution_type_key == "manual":
            vendor_summary["manual"] += 1

        # ------------------------------------------------------------
        # 3. Vendor versus Region automation heatmap
        # ------------------------------------------------------------
        if vendor not in vendor_region_heatmap:
            vendor_region_heatmap[vendor] = {}

        if region not in vendor_region_heatmap[vendor]:
            vendor_region_heatmap[vendor][region] = {
                "total_count": 0,
                "automation": 0,
            }

        vendor_region_cell = vendor_region_heatmap[vendor][region]
        vendor_region_cell["total_count"] += 1

        if execution_type_key == "automation":
            vendor_region_cell["automation"] += 1

        # ------------------------------------------------------------
        # 4. Activity Type versus Execution Type heatmap
        # ------------------------------------------------------------
        if activity_type_key not in activity_execution_heatmap:
            activity_execution_heatmap[activity_type_key] = {
                "activity_type": activity_type_label,
                "total_count": 0,
                "automation": 0,
                "partial_automation": 0,
                "manual": 0,
            }

        activity_heatmap_summary = (
            activity_execution_heatmap[activity_type_key]
        )

        activity_heatmap_summary["total_count"] += 1

        if execution_type_key in {
            "automation",
            "partial_automation",
            "manual",
        }:
            activity_heatmap_summary[execution_type_key] += 1

    # ------------------------------------------------------------
    # Activity Type summary rows
    # ------------------------------------------------------------
    summary_rows = list(activity_summary.values())

    summary_rows.sort(
        key=lambda row: row["activity_type"].lower()
    )

    # ------------------------------------------------------------
    # Vendor execution-type chart rows
    # ------------------------------------------------------------
    vendor_rows = list(vendor_totals.values())

    vendor_rows.sort(
        key=lambda row: (
            row["vendor"].lower() == "combination",
            row["vendor"].lower(),
        )
    )

    # ------------------------------------------------------------
    # Vendor versus Region heatmap
    # ------------------------------------------------------------
    regions = sorted(
        {
            region_name
            for vendor_data in vendor_region_heatmap.values()
            for region_name in vendor_data.keys()
        },
        key=str.lower,
    )

    vendors = sorted(
        vendor_region_heatmap.keys(),
        key=lambda value: (
            value.lower() == "combination",
            value.lower(),
        ),
    )

    vendor_region_heatmap_rows = []

    for vendor_name in vendors:
        values = []

        for region_name in regions:
            counts = vendor_region_heatmap.get(
                vendor_name,
                {},
            ).get(
                region_name,
                {
                    "total_count": 0,
                    "automation": 0,
                },
            )

            total_count = counts["total_count"]
            automation_count = counts["automation"]

            automation_rate = (
                round(
                    (automation_count / total_count) * 100,
                    1,
                )
                if total_count
                else None
            )

            values.append({
                "region": region_name,
                "total_count": total_count,
                "automation": automation_count,
                "automation_rate": automation_rate,
            })

        vendor_region_heatmap_rows.append({
            "vendor": vendor_name,
            "values": values,
        })

    # ------------------------------------------------------------
    # Activity Type versus Execution Type heatmap
    # ------------------------------------------------------------
    execution_labels = [
        "automation",
        "partial_automation",
        "manual",
    ]

    execution_label_map = {
        "automation": "Automation",
        "partial_automation": "Partial Automation",
        "manual": "Manual",
    }

    activity_execution_heatmap_rows = []

    sorted_activity_keys = sorted(
        activity_execution_heatmap.keys(),
        key=lambda activity_key: (
            activity_execution_heatmap[activity_key][
                "activity_type"
            ].lower()
        ),
    )

    for activity_type_key in sorted_activity_keys:
        activity_counts = activity_execution_heatmap[
            activity_type_key
        ]

        total_count = activity_counts["total_count"]
        values = []

        for execution_key in execution_labels:
            execution_count = activity_counts[execution_key]

            execution_rate = (
                round(
                    (execution_count / total_count) * 100,
                    1,
                )
                if total_count
                else None
            )

            values.append({
                "execution_type": execution_key,
                "execution_label": execution_label_map[
                    execution_key
                ],
                "count": execution_count,
                "total_count": total_count,
                "execution_rate": execution_rate,
            })

        activity_execution_heatmap_rows.append({
            "activity_type": activity_counts["activity_type"],
            "values": values,
        })

    # ------------------------------------------------------------
    # KPI calculations
    # ------------------------------------------------------------
    total_cr = totals["total_cr"]

    automation_rate = (
        round(
            (totals["automation"] / total_cr) * 100,
            1,
        )
        if total_cr
        else 0
    )

    partial_automation_rate = (
        round(
            (totals["partial_automation"] / total_cr) * 100,
            1,
        )
        if total_cr
        else 0
    )

    manual_rate = (
        round(
            (totals["manual"] / total_cr) * 100,
            1,
        )
        if total_cr
        else 0
    )

    if date_str:
        period_label = start_date.strftime("%d-%m-%Y")

    else:
        range_labels = {
            "1m": "Last One Month",
            "3m": "Last Three Months",
            "6m": "Last Six Months",
        }

        period_label = (
            f"{range_labels.get(range_key, 'Selected Period')} "
            f"({start_date.strftime('%d-%m-%Y')} to "
            f"{end_date.strftime('%d-%m-%Y')})"
        )

    return JsonResponse({
        "ok": True,
        "message": (
            f"Automation analysis generated for {total_cr} "
            f"active planned and completed CR(s), with "
            f"{len(summary_rows)} unique Activity Type group(s)."
        ),
        "period_label": period_label,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),

        "kpis": {
            "total_cr": total_cr,
            "bpms": totals["bpms"],
            "non_bpms": totals["non_bpms"],
            "automation": totals["automation"],
            "partial_automation": totals[
                "partial_automation"
            ],
            "manual": totals["manual"],
            "automation_rate": automation_rate,
        },

        "rows": summary_rows,

        "charts": {
            "vendor_execution_type": vendor_rows,

            "heatmap": {
                "regions": regions,
                "vendors": vendor_region_heatmap_rows,
            },

            "activity_execution_heatmap": {
                "execution_types": [
                    {
                        "key": "automation",
                        "label": "Automation",
                    },
                    {
                        "key": "partial_automation",
                        "label": "Partial Automation",
                    },
                    {
                        "key": "manual",
                        "label": "Manual",
                    },
                ],
                "activities": activity_execution_heatmap_rows,
            },
        },
    })
