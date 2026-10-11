#!/usr/bin/env python3
"""Install the Chromium build used by the automation into ``cr_process_automation/pw-browsers``.

``dashboard/__init__.py`` forces ``PLAYWRIGHT_BROWSERS_PATH`` to that folder and
raises at import time when no ``chromium-*`` build is present. Running
``playwright install chromium`` on its own would download into the OS user
cache instead, leaving the app unable to start - so this helper pins the path.

Usage (from the repository root, with the project environment active):

    python setup_browsers.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PROJECT_DIR = REPO_ROOT / "cr_process_automation"
BROWSERS_DIR = PROJECT_DIR / "pw-browsers"


def main() -> int:
    BROWSERS_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSERS_DIR)
    print(f"Installing Chromium into {BROWSERS_DIR} ...", flush=True)
    return subprocess.call(
        [sys.executable, "-m", "playwright", "install", "chromium"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
