"""
Region-scoped filesystem locations for the two NIAM workbooks.

The RITM template and result workbooks follow the same hierarchy as the other
task artefacts::

    settings.HOST_DOWNLOAD_FOLDER/{night}/{NIAM_Excel_files}/{Region-name}/

The night date is the date shown in the UI (``%d_%b_%Y``).  Credentials and
browser session files stay per user/run; only the workbooks are region-based.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from django.conf import settings

from .region_paths import DEFAULT_REGION, safe_region, task_date_label


NIAM_TASK_FOLDER = "NIAM_Excel_files"


def niam_date_folder(date_: datetime) -> str:
    """Night label used by both NIAM workbook file names."""
    return task_date_label(9, date_)


def niam_region_root(date_: datetime, region: Optional[str] = None) -> Path:
    """Root folder holding one night's NIAM workbooks for one region."""
    return (
        Path(settings.HOST_DOWNLOAD_FOLDER)
        / niam_date_folder(date_)
        / NIAM_TASK_FOLDER
        / safe_region(region or DEFAULT_REGION)
    )


def niam_template_path_for(
    date_: datetime,
    region: Optional[str] = None,
) -> Path:
    """RITM Input (template) workbook for one night and region."""
    return (
        niam_region_root(date_, region)
        / f"RITM Input_PS_Core_{niam_date_folder(date_)}.xlsx"
    )


def niam_output_path_for(
    date_: datetime,
    region: Optional[str] = None,
) -> Path:
    """RITM Output (result) workbook for one night and region."""
    return (
        niam_region_root(date_, region)
        / f"RITM Output_PS_Core_{niam_date_folder(date_)}.xlsx"
    )
