"""
Region-scoped task output paths.

Every generated artefact now lives under::

    settings.HOST_DOWNLOAD_FOLDER/{date}/{Task-Wise folder}/{Region-name}/

The date label is owned by the calling task: tasks 1-5 keep the existing
``%d-%b-%y`` label while the NIAM workbooks keep ``%d_%b_%Y``.  When more than
one region is selected, a task writes its artefact into each selected region
folder.  That makes "the file is ready for every selected region" a simple,
checkable filesystem condition instead of a task-status guess.
"""

from __future__ import annotations

import os
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, List, Optional

from dateutil import parser as date_parser
from django.conf import settings

REGION_KEYS = ("north", "west", "east", "south")
DEFAULT_REGION = "all"

# Tasks whose artefacts are written into a region folder.  Task 6 has no
# implementation in this repository yet, so it deliberately stays out.
REGION_TASK_IDS = (1, 2, 3, 4, 5, 9)

TASK_FOLDER_ENV = {
    1: "RAW_REPORT_DOWNLOAD_FOLDER",
    2: "CR_HYGIENE_CHECKS_FILE",
    3: "PLAN_FILES_ZIP_FILE",
    4: "BPMS_CR_HYGIENE_CHECKS_FILE",
    5: "MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE",
}


def safe_region(region: Any = None) -> str:
    """Return a filesystem-safe, lowercase region folder name."""
    if region is None:
        return DEFAULT_REGION
    text = str(region).strip().lower()
    if not text:
        return DEFAULT_REGION
    text = re.sub(r"[^a-z0-9_-]+", "_", text).strip("_")
    return text or DEFAULT_REGION


def primary_region(regions: Optional[Iterable[Any]]) -> str:
    """Region a task writes first when the run has one or more regions."""
    if not regions:
        return DEFAULT_REGION
    if isinstance(regions, str):
        return safe_region(regions)
    for region in regions:
        return safe_region(region)
    return DEFAULT_REGION


def as_datetime(selected_date: Any) -> datetime:
    if selected_date is None or selected_date == "":
        return datetime.now()
    if isinstance(selected_date, datetime):
        return selected_date
    if isinstance(selected_date, date):
        return datetime(selected_date.year, selected_date.month, selected_date.day)
    return date_parser.parse(str(selected_date))


def task_date_label(task_id: int, selected_date: Any) -> str:
    """Date folder name owned by *task_id*."""
    parsed = as_datetime(selected_date)
    if task_id in (7, 8, 9):
        return parsed.strftime("%d_%b_%Y")
    return parsed.strftime("%d-%b-%y")


def format_env_path(
    env_name: str,
    date_label: str,
    region: Any = None,
    **extra: Any,
) -> Path:
    """Format one of the central path templates with named placeholders."""
    template = os.getenv(env_name, "")
    if not template:
        return Path()
    return Path(
        template.format(
            date=date_label,
            region=safe_region(region),
            **extra,
        )
    )


def task_output_path(
    task_id: int,
    selected_date: Any,
    region: Any = None,
) -> Optional[Path]:
    """Expected artefact path for one task, night and region."""
    parsed = as_datetime(selected_date)
    date_label = task_date_label(task_id, parsed)
    region_name = safe_region(region)

    if task_id == 1:
        return (
            format_env_path(
                "RAW_REPORT_DOWNLOAD_FOLDER", date_label, region_name
            )
            / f"PS_Core_Raw_Report_{parsed.strftime('%Y-%m-%d')}.csv"
        )
    if task_id == 2:
        return format_env_path("CR_HYGIENE_CHECKS_FILE", date_label, region_name)
    if task_id == 3:
        return format_env_path(
            "PLAN_FILES_ZIP_FILE",
            date_label,
            region_name,
            label=parsed.strftime("%d-%B-%Y"),
        )
    if task_id == 4:
        return format_env_path("BPMS_CR_HYGIENE_CHECKS_FILE", date_label, region_name)
    if task_id == 5:
        return format_env_path(
            "MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE", date_label, region_name
        )
    if task_id == 9:
        # Imported lazily so this module stays free of a dependency cycle.
        from .niam_paths import niam_output_path_for

        return niam_output_path_for(parsed, region=region_name)
    return None


def all_region_files_ready(
    task_id: int,
    selected_date: Any,
    regions: Optional[Iterable[Any]],
) -> bool:
    """True only when the artefact exists for *every* selected region (AND)."""
    if task_id not in REGION_TASK_IDS:
        return False
    if not regions:
        return False

    paths: List[Path] = []
    for region in regions:
        path = task_output_path(task_id, selected_date, region)
        if path is None:
            return False
        paths.append(path)
    return bool(paths) and all(path.is_file() for path in paths)


def publish_region_output(
    task_id: int,
    selected_date: Any,
    regions: Optional[Iterable[Any]],
    source: Any,
) -> Optional[str]:
    """Copy a completed artefact into every selected region folder.

    Tasks write their artefact into the *primary* region folder while running.
    This finishes the region fan-out after the task completes and returns the
    primary region path so callers can keep using ``download_name``.
    """
    if not source:
        return None
    src = Path(str(source))
    if not src.is_file():
        return None

    region_names = [safe_region(region) for region in (regions or [])]
    if not region_names:
        region_names = [DEFAULT_REGION]

    primary_path: Optional[Path] = None
    for index, region_name in enumerate(region_names):
        target = task_output_path(task_id, selected_date, region_name)
        if target is None:
            continue
        if index == 0:
            primary_path = target
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            if src.resolve() == target.resolve():
                continue
        except OSError:
            pass
        shutil.copy2(src, target)

    return str(primary_path or src)
