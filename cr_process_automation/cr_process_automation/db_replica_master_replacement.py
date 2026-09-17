import os
import sys
import sqlite3
from contextlib import closing
from pathlib import Path

# Based on your traceback: the directory containing manage.py.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Use the same settings module specified in manage.py.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "cr_process_automation.settings",
)
from django.conf import settings

# Working copy of the replica, with any associated sidecar files.
replica_path = Path(settings.DB_REPLICA_PATH)

# Must be a new file, not your existing master.
restored_path = Path(settings.DB_RESTORE_PATH)


def validate_database(connection, label):
    integrity = [
        row[0]
        for row in connection.execute("PRAGMA integrity_check;")
    ]
    if integrity != ["ok"]:
        raise RuntimeError(f"{label} integrity check failed: {integrity}")

    foreign_key_error = connection.execute(
        "PRAGMA foreign_key_check;"
    ).fetchone()
    if foreign_key_error is not None:
        raise RuntimeError(
            f"{label} has foreign-key violations; "
            f"first violation: {foreign_key_error}"
        )


if not replica_path.is_file():
    raise FileNotFoundError(replica_path)

restored_path.parent.mkdir(parents=True, exist_ok=True)

# Reserve a new destination; refuse to overwrite an existing file.
with restored_path.open("wb"):
    pass

try:
    if os.path.exists(restored_path):
        os.remove(restored_path)
    with closing(sqlite3.connect(
        replica_path.resolve().as_uri() + "?mode=ro",
        uri=True,
    )) as source:
        validate_database(source, "Replica")

        with closing(sqlite3.connect(str(restored_path))) as destination:
            source.backup(destination)
            validate_database(destination, "Restored master")

    print(f"Validated replacement created: {restored_path}")
except Exception:
    print(
        f"Restore failed. Do not deploy {restored_path}; "
        "it may be incomplete."
    )
    raise
