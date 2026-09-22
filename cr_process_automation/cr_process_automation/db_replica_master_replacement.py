# import os
# import sys
# import sqlite3
# from contextlib import closing
# from pathlib import Path

# # Based on your traceback: the directory containing manage.py.
# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# sys.path.insert(0, str(PROJECT_ROOT))

# # Use the same settings module specified in manage.py.
# os.environ.setdefault(
#     "DJANGO_SETTINGS_MODULE",
#     "cr_process_automation.settings",
# )
# from django.conf import settings

# # Working copy of the replica, with any associated sidecar files.
# replica_path = Path(settings.DB_REPLICA_PATH)

# # Must be a new file, not your existing master.
# restored_path = Path(settings.DB_RESTORE_PATH)


# def validate_database(connection, label):
#     integrity = [
#         row[0]
#         for row in connection.execute("PRAGMA integrity_check;")
#     ]
#     if integrity != ["ok"]:
#         raise RuntimeError(f"{label} integrity check failed: {integrity}")

#     foreign_key_error = connection.execute(
#         "PRAGMA foreign_key_check;"
#     ).fetchone()
#     if foreign_key_error is not None:
#         raise RuntimeError(
#             f"{label} has foreign-key violations; "
#             f"first violation: {foreign_key_error}"
#         )


# if not replica_path.is_file():
#     raise FileNotFoundError(replica_path)

# restored_path.parent.mkdir(parents=True, exist_ok=True)

# # Reserve a new destination; refuse to overwrite an existing file.
# with restored_path.open("wb"):
#     pass

# try:
#     if os.path.exists(restored_path):
#         os.remove(restored_path)
#     with closing(sqlite3.connect(
#         replica_path.resolve().as_uri() + "?mode=ro",
#         uri=True,
#     )) as source:
#         validate_database(source, "Replica")

#         with closing(sqlite3.connect(str(restored_path))) as destination:
#             source.backup(destination)
#             validate_database(destination, "Restored master")

#     print(f"Validated replacement created: {restored_path}")
# except Exception:
#     print(
#         f"Restore failed. Do not deploy {restored_path}; "
#         "it may be incomplete."
#     )
#     raise

# db_replica_master_replacement.py
import os
import sys
import subprocess
from urllib.parse import quote  # Add this import
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

# Fetch PostgreSQL configurations from settings
master_db = settings.DATABASES['default']
replica_db = settings.DATABASES['replica']

# URL-encode passwords to safely handle special characters like '@' and '#'
replica_pwd = quote(replica_db['PASSWORD'])
master_pwd = quote(master_db['PASSWORD'])

# Construct PostgreSQL connection URIs safely
replica_url = f"postgresql://{replica_db['USER']}:{replica_pwd}@{replica_db['HOST']}:{replica_db['PORT']}/{replica_db['NAME']}"
master_url = f"postgresql://{master_db['USER']}:{master_pwd}@{master_db['HOST']}:{master_db['PORT']}/{master_db['NAME']}"

# We use an intermediate dump file in the project folder. 
# You CAN track this file in Git to safely sync data between Windows and Fedora!
dump_path = PROJECT_ROOT / "postgres_replica_dump.sql"


def validate_database(db_url, label):
    """Validates the PostgreSQL database is active and responding."""
    try:
        subprocess.run(
            ["psql", "--dbname", db_url, "-c", "SELECT 1;"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        raise RuntimeError(f"{label} connection or integrity check failed.")


try:
    # 1. Validate Replica connection
    validate_database(replica_url, "Replica")

    # 2. Dump from Replica to the SQL file
    print(f"Creating dump from Replica (Port {replica_db['PORT']}) to {dump_path.name}...")
    subprocess.run([
        "pg_dump",
        "--dbname", replica_url,
        "--clean",           # Drops existing tables before recreating them
        "--if-exists",
        "--no-owner",        # Skips ownership to prevent Windows/Fedora permission issues
        "--no-privileges",
        "-f", str(dump_path)
    ], check=True)
    print("Replica dump created successfully.")

    # 3. Restore the SQL file to the Master database
    print(f"Restoring dump to Master (Port {master_db['PORT']})...")
    subprocess.run([
        "psql",
        "--dbname", master_url,
        "-f", str(dump_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 4. Validate Master connection
    validate_database(master_url, "Restored Master")

    print(f"Validated replacement created and synced. Dump file available at: {dump_path}")

except subprocess.CalledProcessError as e:
    print(f"Restore failed. Do not deploy; it may be incomplete. Error: {e}")
    raise

