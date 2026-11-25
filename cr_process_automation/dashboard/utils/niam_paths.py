"""
Per-user filesystem locations for NIAM template and result workbooks.

The CR source files (``raw_report_file`` / ``planning_sheet``) remain shared,
but the two NIAM workbooks are user-owned: one user must never overwrite or
download another user's template or RITM output.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from django.conf import settings


def niam_user_root(user=None) -> Path:
    """Stable root directory for a user's NIAM files."""
    if user is None or not getattr(user, "is_authenticated", False):
        return Path(settings.MEDIA_ROOT) / "niam" / "anonymous"

    user_id = getattr(user, "id", None) or "unknown"
    raw_name = getattr(user, "username", "") or "user"
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", str(raw_name))[:40]
    return Path(settings.MEDIA_ROOT) / "niam" / f"user_{user_id}_{safe_name}"


def niam_date_folder(date_: datetime) -> str:
    """Night label used by both NIAM workbook file names."""
    if isinstance(date_, datetime):
        return date_.strftime("%d_%b_%Y")
    return str(date_)


def niam_template_path_for(
    date_: datetime, user=None, base: Optional[str] = None
) -> Path:
    """RITM Input (template) workbook for one user and night."""
    root = Path(base) if base else niam_user_root(user) / "templates"
    return root.joinpath(
        niam_date_folder(date_),
        f"RITM Input_PS_Core_{niam_date_folder(date_)}.xlsx",
    )


def niam_output_path_for(
    date_: datetime, user=None, base: Optional[str] = None
) -> Path:
    """RITM Output (result) workbook for one user and night."""
    root = Path(base) if base else niam_user_root(user) / "outputs"
    return root.joinpath(
        niam_date_folder(date_),
        f"RITM Output_PS_Core_{niam_date_folder(date_)}.xlsx",
    )
