from pathlib import Path
from dateutil import parser
from datetime import datetime, timedelta
import sqlite3
import sys
import traceback
import threading
from importlib import import_module
import pandas as pd
# from django.core.cache import cache
from django.db import connection
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_GET, require_POST
from .forms import LoginForm, TwoFactorAuthForm, PasswordAuthForm
from .models import MasterCRDatabase, SelectedDateTable
from django.contrib import messages
from dashboard.services import update_cr_flag_atomic
import uuid

TASKS = [
    {"id": 1, "sequence_no": 1, "name": "RAW Report to Template", "download_required": True},
    {"id": 2, "sequence_no": 2, "name": "CR Hygiene Checks", "download_required": True},
    {"id": 3, "sequence_no": 3, "name": "Install/Test Plan Downloads", "download_required": True},
    {"id": 4, "sequence_no": 4, "name": "BPMS CR Hygiene Checks", "download_required": True},
    {"id": 5, "sequence_no": 5, "name": "MOP Attachment & Approvals", "download_required": False},
    {"id": 6, "sequence_no": 6, "name": "Final Email Package", "download_required": True},
    {"id": 7, "sequence_no": 7, "name": "NIAM Ticket Generation", "download_required": False},
]

TASKS_REQUIRING_AUTH = {1, 3, 5}

def _requires_auth(task_id):
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
        # Whether this task uses the ITSM login flow at all
        "requires_auth": _requires_auth(task["id"]),
        # OTP fields
        "otp_required": False,
        "otp": None,
        "otp_event": threading.Event(),
        # Password fields
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
                return redirect("cr_planning")
            message = "invalid user"
    else:
        form = LoginForm()
    return render(request, "dashboard/login.html", {"form": form, "message": message})


def logout_view(request):
    logout(request)
    return redirect("login")


def _task_by_id(task_id):
    return next((task for task in TASKS if task["id"] == task_id), None)


def _downloads_root():
    root = Path(settings.MEDIA_ROOT) / "task_downloads"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _database_root():
    root = Path(settings.MEDIA_ROOT) / "generated_databases" / datetime.now().strftime("%Y-%m-%d")
    root.mkdir(parents=True, exist_ok=True)
    return root


def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _count_rows_in_sqlite(db_path):
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
    counts = {"north_crs": 0, "west_crs": 0, "east_crs": 0, "south_crs": 0}
    db_root = _database_root()
    for field_name, file_name in REGION_DATABASES.items():
        counts[field_name] = _count_rows_in_sqlite(db_root / file_name)
    counts["total_crs"] = (counts["north_crs"] + counts["west_crs"] + counts["east_crs"] + counts["south_crs"])
    return counts


def _apply_counts_to_tasks():
    counts = _load_regional_counts()
    for task in TASKS:
        runtime = TASK_RUNTIME[task["id"]]
        runtime.update(counts)


def _build_tasks_for_ui():
    return [{**task, **TASK_RUNTIME[task["id"]]} for task in TASKS]


def _split_log(entry):
    if "----" in entry:
        message, ts = entry.rsplit("----", 1)
        return {"message": message.strip(), "timestamp": ts.strip()}
    return {"message": entry, "timestamp": ""}


def _common_context(request):
    if request.user.is_authenticated:
        user_name = request.user.get_full_name() or request.user.username
        user_role = request.user.role
    else:
        user_name = "Karan Loomba"
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
    return render(request, "dashboard/home.html", _common_context(request))


@login_required(login_url="login")
def night_execution_view(request):
    ctx = _common_context(request)
    ctx["selected_option"] = "night_execution"
    return render(request, "dashboard/night_execution.html", ctx)


@login_required(login_url="login")
def night_spoc_view(request):
    ctx = _common_context(request)
    ctx["selected_option"] = "night_spoc"
    return render(request, "dashboard/night_spoc.html", ctx)


# @login_required(login_url="login")
# def region_crs_view(request):
#     ctx = _common_context(request)
#     ctx["selected_option"] = "region_crs"
#     return render(request, "dashboard/region_crs.html", ctx)

# @login_required(login_url="login")
# def cr_history_view(request):
#     ctx = _common_context(request)
#     ctx["selected_option"] = "cr_history"
#     return render(request, "dashboard/cr_history.html", ctx)

@require_POST
@login_required(login_url="login")
def start_task(request, task_id):
    global CURRENT_RUNNING_TASK

    task = _task_by_id(task_id)
    if not task:
        return JsonResponse({"ok": False, "message": "Invalid task id."}, status=404)

    selected_date = request.POST.get('date', '').strip()

    if task_id == 1 and not selected_date:
        return JsonResponse({
            "ok": False,
            "message": "Please select a Date before starting this task."
        }, status=400)

    try:
        parsed_date = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else None
    except ValueError:
        return JsonResponse({"ok": False, "message": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    user_email = request.user.email if request.user.is_authenticated else None
    user_name = request.user.employee_name if request.user.is_authenticated else None

    task_module_path = TASK_MODULE_MAP.get(task_id)
    if not task_module_path:
        msg = f"Module not found for '{task['name']}'."
        GLOBAL_LOGS.append(f"{msg} ---- {_timestamp()}")
        return JsonResponse({"ok": False, "message": msg}, status=404)

    try:
        task_module = import_module(task_module_path)
    except Exception as exc:
        msg = f"Import failed for '{task_module_path}': {exc}"
        GLOBAL_LOGS.append(f"{msg} ---- {_timestamp()}")
        GLOBAL_LOGS.append(traceback.format_exc())
        return JsonResponse({"ok": False, "message": msg}, status=500)

    if not hasattr(task_module, "run_task"):
        msg = f"run_task() missing in module '{task_module_path}'."
        GLOBAL_LOGS.append(f"{msg} ---- {_timestamp()}")
        return JsonResponse({"ok": False, "message": msg}, status=404)

    runtime = TASK_RUNTIME[task_id]
    runtime["status"] = "Running"
    runtime["requires_auth"] = _requires_auth(task_id)
    # OTP fields (reset each run)
    runtime["otp_required"] = False
    runtime["otp"] = None
    runtime["otp_event"] = threading.Event()
    
    # Password fields (reset each run)
    runtime["password_required"] = False
    runtime["password"] = None
    runtime["pwd_event"] = threading.Event()

    CURRENT_RUNNING_TASK = task["name"]
    GLOBAL_LOGS.append(f"{task['name']}: task started ---- {_timestamp()}")

    def _runner():
        global CURRENT_RUNNING_TASK
        try:
            result = task_module.run_task(
                request=request,
                task=task,
                runtime=runtime,
                GLOBAL_LOGS=GLOBAL_LOGS,
                timestamp_fn=_timestamp,
                selected_date = selected_date,
                user_email = user_email,
                user_name = user_name
            )
            runtime["status"] = result.get("status", runtime["status"])
            runtime["download_ready"] = result.get("download_ready", False)
            runtime["download_name"] = result.get("download_name", runtime["download_name"])
            if result.get("counts"):
                runtime.update(result["counts"])
            CURRENT_RUNNING_TASK = result.get("message", f"{task['name']} completed successfully.")
            GLOBAL_LOGS.append(f"{task['name']}: {CURRENT_RUNNING_TASK} ---- {_timestamp()}")
        except Exception as exc:
            runtime["status"] = "Failed"
            msg = f"{task['name']} failed: {exc}"
            GLOBAL_LOGS.append(f"{msg} ---- {_timestamp()}")
            GLOBAL_LOGS.append(traceback.format_exc())
            CURRENT_RUNNING_TASK = msg
        finally:
            # Safety: never leave stale flags that would keep the iframe open
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
def submit_otp(request, task_id):
    task = _task_by_id(task_id)
    if not task:
        return JsonResponse({"ok": False, "message": "Invalid task id."}, status=404)

    # Guard: reject OTP submissions for tasks that don't use auth
    if not _requires_auth(task_id):
        return JsonResponse(
            {"ok": False, "message": "This task does not require OTP."}, status=400
        )
    
    runtime = TASK_RUNTIME[task_id]
    otp = request.POST.get("otp", "").strip()
    if not otp:
        return JsonResponse({"ok": False, "message": "OTP is required."}, status=400)
    runtime["otp"] = otp
    runtime["otp_required"] = False
    otp_event = runtime.get("otp_event")
    if otp_event:
        otp_event.set()
    GLOBAL_LOGS.append(f"{task['name']}: OTP received from user ---- {_timestamp()}")
    return JsonResponse({"ok": True, "message": "OTP submitted successfully."})

@require_POST
@login_required(login_url="login")
def submit_password(request, task_id):
    task = _task_by_id(task_id)
    if not task:
        return JsonResponse({"ok": False, "message": "Invalid task id."}, status=404)

    # Guard: reject password submissions for tasks that don't use auth
    if not _requires_auth(task_id):
        return JsonResponse(
            {"ok": False, "message": "This task does not require a password."}, status=400
        )

    runtime = TASK_RUNTIME[task_id]
    password = request.POST.get("password", "").strip()
    if not password:
        return JsonResponse({"ok": False, "message": "Password is required."}, status=400)

    runtime["password"] = password
    runtime["password_required"] = False

    pwd_event = runtime.get("pwd_event")
    if pwd_event:
        pwd_event.set()

    GLOBAL_LOGS.append(f"{task['name']}: Password received from user ---- {_timestamp()}")

    return JsonResponse({"ok": True, "message": "Password submitted successfully."})

@require_GET
@login_required(login_url="login")
def task_dashboard_data(request):
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
            # Only auth-requiring tasks can flip these true.
            # For non-auth tasks force False so the iframe never opens for them.
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
def download_task_output(request, task_id):
    task = _task_by_id(task_id)
    if not task:
        raise Http404("Invalid task id.")

    runtime = TASK_RUNTIME[task_id]
    file_path = runtime.get("download_name")

    if not file_path or not runtime.get("download_ready"):
        raise Http404("No file is available for download yet.")

    path_obj = Path(file_path)
    if not path_obj.exists():
        raise Http404("The requested file could not be found on the server.")

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
def filter_region_crs(request):
    date_str = request.GET.get("date", "").strip()
    selected_regions = request.GET.get("regions", "").strip()
    selected_regions = [r.strip().lower() for r in selected_regions.split(",") if r.strip()]

    # Two count sets:
    # - counts_all: execution_date only (for task_id 1)
    # - counts_planned: execution_date + planning_status="planned" (for other tasks)
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
        return JsonResponse(
            {"ok": False, "message": "Invalid date format. Use YYYY-MM-DD."},
            status=400,
        )

    # Per-region counts for both sets
    for region_key in selected_regions:
        field_name = REGION_FIELD_MAP.get(region_key)
        if not field_name:
            continue

        # 1) Execution date only (task_id 1)
        count_all = MasterCRDatabase.objects.filter(
            execution_date=filter_date,
            region__iexact=region_key,
        ).count()
        counts_all[field_name] = count_all

        # 2) Execution date + planning_status="planned" (tasks 2–7)
        count_planned = MasterCRDatabase.objects.filter(
            execution_date=filter_date,
            region__iexact=region_key,
            planning_status__iexact="planned",
        ).count()
        counts_planned[field_name] = count_planned

    counts_all["total_crs"] = (
        counts_all["north_crs"]
        + counts_all["west_crs"]
        + counts_all["east_crs"]
        + counts_all["south_crs"]
    )
    counts_planned["total_crs"] = (
        counts_planned["north_crs"]
        + counts_planned["west_crs"]
        + counts_planned["east_crs"]
        + counts_planned["south_crs"]
    )

    return JsonResponse({
        "ok": True,
        "date": date_str,
        "regions": selected_regions,
        "counts_all": counts_all,
        "counts_planned": counts_planned,
    })

@xframe_options_sameorigin
def playwright_auth_iframe(request):
    print(f"🟢 playwright_auth_iframe CALLED, method={request.method}")

    if request.method == 'POST':
        print(f"🟢 POST data: {dict(request.POST)}")
        form = TwoFactorAuthForm(request.POST)

        if form.is_valid():
            task_id = int(form.cleaned_data['task_id'])
            two_factor_code = form.cleaned_data['two_factor_code']
            print(f"🟢 Valid form. task_id={task_id}, code={two_factor_code}")

            # Guard: ignore submissions for tasks that don't use auth
            if not _requires_auth(task_id):
                print(f"🔴 task_id={task_id} does not require auth; ignoring OTP.")
                return render(request, 'dashboard/iframe_form.html', {'form': form})

            runtime = TASK_RUNTIME.get(task_id)
            print(f"🟢 runtime found: {runtime is not None}")

            if runtime is None:
                print(f"🔴 No runtime found for task_id={task_id}! "
                      f"Available keys: {list(TASK_RUNTIME.keys())}")
                return render(request, 'dashboard/iframe_form.html', {'form': form})

            runtime["otp"] = two_factor_code
            runtime["otp_required"] = False

            otp_event = runtime.get("otp_event")
            print(f"🟢 Setting event id={id(otp_event)} for runtime id={id(runtime)}")

            if otp_event is not None:
                otp_event.set()
                print("🟢 Event SET! Playwright thread should resume now.")
            else:
                print("🔴 otp_event is None! Nothing to set — thread will stay stuck.")

            GLOBAL_LOGS.append(f"Task ID {task_id}: OTP received via Iframe ---- {_timestamp()}")

            return render(request, 'dashboard/iframe_success.html')

        else:
            print(f"🔴 FORM INVALID: {form.errors.as_json()}")
            return render(request, 'dashboard/iframe_form.html', {'form': form})

    else:
        task_id = request.GET.get('task_id', '')
        print(f"🟢 GET request, pre-filling task_id={task_id}")
        form = TwoFactorAuthForm(initial={'task_id': task_id})

    return render(request, 'dashboard/iframe_form.html', {'form': form})


@xframe_options_sameorigin
def playwright_password_iframe(request):
    print(f"🔵 playwright_password_iframe CALLED, method={request.method}")

    if request.method == 'POST':
        print(f"🔵 POST data keys: {list(request.POST.keys())}")  # never log the password value
        form = PasswordAuthForm(request.POST)

        if form.is_valid():
            task_id = int(form.cleaned_data['task_id'])
            password = form.cleaned_data['password']
            print(f"🔵 Valid form. task_id={task_id}")

            # Guard: ignore submissions for tasks that don't use auth
            if not _requires_auth(task_id):
                print(f"🔴 task_id={task_id} does not require auth; ignoring password.")
                return render(request, 'dashboard/password_form.html', {'form': form})

            runtime = TASK_RUNTIME.get(task_id)
            print(f"🔵 runtime found: {runtime is not None}")

            if runtime is None:
                print(f"🔴 No runtime found for task_id={task_id}! "
                      f"Available keys: {list(TASK_RUNTIME.keys())}")
                return render(request, 'dashboard/password_form.html', {'form': form})

            runtime["password"] = password
            runtime["password_required"] = False

            pwd_event = runtime.get("pwd_event")
            print(f"🔵 Setting pwd_event id={id(pwd_event)} for runtime id={id(runtime)}")

            if pwd_event is not None:
                pwd_event.set()
                print("🔵 pwd_event SET! Playwright thread should resume now.")
            else:
                print("🔴 pwd_event is None! Nothing to set — thread will stay stuck.")

            GLOBAL_LOGS.append(f"Task ID {task_id}: Password received via Iframe ---- {_timestamp()}")

            return render(request, 'dashboard/iframe_success.html')

        else:
            print(f"🔴 FORM INVALID: {form.errors.as_json()}")
            return render(request, 'dashboard/password_form.html', {'form': form})

    else:
        task_id = request.GET.get('task_id', '')
        print(f"🔵 GET request, pre-filling task_id={task_id}")
        form = PasswordAuthForm(initial={'task_id': task_id})

    return render(request, 'dashboard/password_form.html', {'form': form})


@require_GET
@login_required(login_url="login")
def fetch_current_date_crs(request):
    try:
        date_str = request.GET.get("date", "").strip()
        if not date_str:
            return JsonResponse({"ok": False, "message": "Date is required."}, status=400)
        parsed_date = parser.parse(date_str).date()

        result = list(
            SelectedDateTable.objects.filter(execution_date=parsed_date).values(*settings.CR_WISE_STATUS_FIELDS)
        )

        if result:
            return JsonResponse({
                "ok": True,
                "date": date_str,
                "fields": settings.SELECTED_DATE_TABLE_FIELDS,
                "rows": result,
            }, encoder=DjangoJSONEncoder)
        else:
            SelectedDateTable.objects.all().delete()
            objects = MasterCRDatabase.objects.filter(execution_date=parsed_date).values(*settings.SELECTED_DATE_TABLE_FIELDS)
            
            if len(objects) == 0:
                return JsonResponse({"ok": False, "message": "No CR found for the selected date."}, status=400)

            else:
                SelectedDateTable.objects.bulk_create(objects)
                return JsonResponse({
                    "ok": True,
                    "date": date_str,
                    "fields": settings.SELECTED_DATE_TABLE_FIELDS,
                    "rows": list(objects),
                }, encoder=DjangoJSONEncoder)

    except Exception:
        raise


def update_hygiene_check(request, cr_no):
    # This forces a write to 'default' and locks the row
    try:
        update_cr_flag_atomic(cr_no, "CR_Hygiene_Checks", "Passed")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_replica_sync_status(request, sync_id):
    # status = cache.get(f'replica_sync_{sync_id}_status', 'unknown')
    return JsonResponse({
        'sync_id': sync_id,
        'status': status,
        'ready': status == 'complete'
    })

