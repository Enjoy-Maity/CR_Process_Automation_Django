"""
Per-user, per-task execution contexts.

Historically the dashboard kept ONE global runtime dict per task id
(``TASK_RUNTIME``) plus module-level globals inside each task module. That made
two users running the same task clobber each other. This module gives every
(user, task) pair its own isolated runtime context with its own log buffer and
its own OTP/password events, and can load a *fresh* copy of a task module so the
module-level globals inside it are private to a single run.

Nothing here touches the database; callers decide what to persist.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import threading
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dateutil import parser as date_parser
from django.conf import settings

from .region_paths import format_env_path, primary_region, task_date_label

# Tasks that authenticate against ITSM (password + OTP iframes).
TASK_REQUIRES_AUTH = {1, 2, 3, 4, 5}


def requires_auth(task_id: int) -> bool:
    return task_id in TASK_REQUIRES_AUTH


def _empty_counts() -> Dict[str, int]:
    return {
        "total_crs": 0,
        "north_crs": 0,
        "west_crs": 0,
        "east_crs": 0,
        "south_crs": 0,
    }


def make_runtime(task_id: int) -> Dict[str, Any]:
    """Build a brand-new runtime context (fresh events, fresh log buffer)."""
    return {
        "task_id": task_id,
        "run_key": uuid.uuid4().hex,
        "status": "Pending",
        "download_ready": False,
        "download_name": "",
        "download_url": "",
        "logs": [],
        "run_dir": "",
        "requires_auth": requires_auth(task_id),
        # Password fields
        "password_required": False,
        "password": None,
        "pwd_event": threading.Event(),
        # OTP fields
        "otp_required": False,
        "otp": None,
        "otp_event": threading.Event(),
        # Read-only notice fields (e.g. Microsoft Authenticator sign-in code)
        "notice_required": False,
        "notice_text": "",
        # Blocking dialog fields (e.g. missing/wrong NIAM credentials)
        "alert_required": False,
        "alert_title": "",
        "alert_text": "",
        "alert_seq": 0,
        **_empty_counts(),
    }


class _RuntimeRegistry:
    """Thread-safe map of (user_id, task_id) -> runtime context."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._contexts: Dict[Any, Dict[str, Any]] = {}

    def begin(self, user_id: Any, task_id: int) -> Dict[str, Any]:
        ctx = make_runtime(task_id)
        with self._lock:
            self._contexts[(user_id, task_id)] = ctx
        return ctx

    def peek(self, user_id: Any, task_id: int) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._contexts.get((user_id, task_id))

    def get(
        self, user_id: Any, task_id: int, run_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Return the current context, optionally requiring an exact run key.

        Auth submissions must use ``run_key`` so a stale iframe/form cannot set
        the event of a newer run for the same (user, task).
        """
        ctx = self.peek(user_id, task_id)
        if ctx is None:
            return None
        if run_key is None:
            return ctx
        return ctx if str(ctx.get("run_key", "")) == str(run_key) else None

    def all_for_user(self, user_id: Any) -> Dict[int, Dict[str, Any]]:
        with self._lock:
            return {
                task_id: ctx
                for (uid, task_id), ctx in self._contexts.items()
                if uid == user_id
            }

    def set(self, user_id: Any, task_id: int, ctx: Dict[str, Any]) -> None:
        with self._lock:
            self._contexts[(user_id, task_id)] = ctx

    def clear(self, user_id: Any, task_id: int) -> None:
        with self._lock:
            self._contexts.pop((user_id, task_id), None)

    def clear_all_for_user(self, user_id: Any) -> None:
        """Drop every live run context owned by a user (logout / idle expiry)."""
        with self._lock:
            for key in [k for k in self._contexts if k[0] == user_id]:
                self._contexts.pop(key, None)


def load_fresh_module(module_path: str):
    """
    Import *module_path* and return a fresh module object whose globals are
    private to this run. The module body is re-executed onto a new module
    instance, so module-level state (``glogs`` etc.) used by the automation code
    is no longer shared between concurrent runs of the same task.

    Falls back to the shared cached module if a file path cannot be resolved.
    """
    base = importlib.import_module(module_path)
    module_file = getattr(base, "__file__", None)
    if not module_file:
        return base

    unique_name = f"_cr_run_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(unique_name, module_file)
    if spec is None or spec.loader is None:
        return base

    module = importlib.util.module_from_spec(spec)
    sys.modules[unique_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(unique_name, None)
        raise
    return module


# Shared, process-wide registry instance.
RUN_REGISTRY = _RuntimeRegistry()


def run_output_dir(run_key: str) -> Path:
    """Per-run directory used to keep each run's downloadable files separate."""
    root = Path(settings.MEDIA_ROOT) / "task_runs" / run_key
    root.mkdir(parents=True, exist_ok=True)
    return root


def _as_datetime(selected_date: Any) -> datetime:
    if selected_date is None or selected_date == "":
        return datetime.now()
    if hasattr(selected_date, "strftime"):
        return selected_date
    return date_parser.parse(str(selected_date))


def shared_input_paths(selected_date: Any = None, regions=None) -> Dict[str, str]:
    """
    Canonical paths of the two shared input files for one night and region.

    The files are shared between users (protected by the task-module file
    locks); the region folder is the isolation boundary.  When several regions
    are selected, the primary (first) region is the one recorded here and the
    finished artefact is copied to every selected region by the caller.
    """
    parsed = _as_datetime(selected_date)
    folder_date = task_date_label(1, parsed)
    region = primary_region(regions)

    raw_report_file = ""
    if os.getenv("RAW_REPORT_DOWNLOAD_FOLDER", ""):
        raw_report_file = str(
            format_env_path("RAW_REPORT_DOWNLOAD_FOLDER", folder_date, region)
            / f"PS_Core_Raw_Report_{parsed.strftime('%Y-%m-%d')}.csv"
        )

    planning_sheet = ""
    if os.getenv("PLANNING_SHEET_DOWNLOAD_FOLDER", ""):
        planning_sheet = str(
            format_env_path("PLANNING_SHEET_DOWNLOAD_FOLDER", folder_date, region)
            / os.getenv("PLANNING_SHEET_WORKBOOK_NAME", "Standard_Planning_Sheet.xlsx")
        )

    return {
        "raw_report_file": raw_report_file,
        "planning_sheet": planning_sheet,
    }


def isolate_output(runtime: Dict[str, Any], source) -> Optional[str]:
    """
    Copy a completed run's output file into its private run directory so users
    downloading the same task never overwrite each other. Returns the new path
    (or None when there is nothing to copy).
    """
    if not source:
        return None
    src = Path(str(source))
    if not src.is_file():
        return None

    run_dir = Path(runtime.get("run_dir") or run_output_dir(runtime["run_key"]))
    run_dir.mkdir(parents=True, exist_ok=True)
    dest = run_dir / src.name
    try:
        if src.resolve() == dest.resolve():
            return str(dest)
    except OSError:
        pass

    import shutil

    shutil.copy2(src, dest)
    return str(dest)
