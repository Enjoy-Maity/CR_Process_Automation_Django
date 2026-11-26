"""Shared run status per (task, night, region).

Dashboard badges must reflect what any user has done for the selected regions,
not which user happens to be looking at the page. A run publishes one marker per
selected region; the UI reduces those markers with boolean AND:

* ``Completed`` only when *every* selected region is Completed;
* ``Failed`` when *any* selected region is Failed;
* ``Pending`` otherwise (a region is still running or has no marker yet).

Markers live outside the artefact folders, so they never interfere with task
outputs or downloads, and no database schema change is required.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable, List, Optional

from django.conf import settings

from .region_paths import all_region_files_ready, safe_region, task_date_label

logger = logging.getLogger(__name__)

COMPLETED = "Completed"
FAILED = "Failed"
PENDING = "Pending"
RUNNING = "Running"

STATUS_ROOT = ".task_status"


def status_path(task_id: int, selected_date: Any, region: Any = None) -> Path:
    """Marker file for one task, night and region."""
    return (
        Path(settings.HOST_DOWNLOAD_FOLDER)
        / STATUS_ROOT
        / str(int(task_id))
        / task_date_label(task_id, selected_date)
        / f"{safe_region(region)}.json"
    )


def publish(
    task_id: int,
    selected_date: Any,
    regions: Optional[Iterable[Any]],
    status: str,
) -> List[Path]:
    """Write *status* into the marker for every selected region."""
    written: List[Path] = []
    for region in regions or []:
        path = status_path(task_id, selected_date, region)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"status": status}, separators=(",", ":")),
                encoding="utf-8",
            )
            written.append(path)
        except OSError:
            logger.exception("Could not write region status marker %s", path)
    return written


def _read_status(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return str(data.get("status", "")).strip()
    except (OSError, ValueError, TypeError, AttributeError):
        return ""


def combined_status(
    task_id: int,
    selected_date: Any,
    regions: Optional[Iterable[Any]],
) -> str:
    """Reduce per-region markers to one badge status (boolean AND)."""
    region_names = list(regions or [])
    if not region_names:
        return PENDING

    statuses = [
        _read_status(status_path(task_id, selected_date, region))
        for region in region_names
    ]
    if any(status == FAILED for status in statuses):
        return FAILED
    if all(status == COMPLETED for status in statuses):
        return COMPLETED
    # Older artefacts have no marker; existing files for every region still
    # mean the work was completed before shared status tracking existed.
    if all_region_files_ready(task_id, selected_date, region_names):
        return COMPLETED
    return PENDING
