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
import threading
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings

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
