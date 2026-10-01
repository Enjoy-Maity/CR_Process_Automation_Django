#!/usr/bin/env python3
"""
db_stop.py — Cross-platform graceful shutdown script for CR Process Automation.

Works on: Linux (rootless Docker / Podman), Windows (Docker Desktop + WSL2)

Usage:
    python db_stop.py              # Stop containers, keep named volumes (DATA IS PRESERVED)
    python db_stop.py --wipe       # Stop containers AND delete volumes (DATA IS LOST — fresh start)
    python db_stop.py --backup     # Dump master_db to a .sql file before stopping

What this script does on a normal stop (no flags):
    1. Optionally dumps master_db to a timestamped SQL file (--backup flag).
    2. Runs 'docker compose down' — containers are stopped and removed.
    3. Named Docker volumes are KEPT — all your PostgreSQL data survives.

What survives after 'docker compose down' (no --wipe):
    - Named volume 'cr_process_automation_db_master_volume' → all master_db data
    - Named volume 'cr_process_automation_db_replica_volume' → replica's copy
    The next 'docker compose up' (or db_start.py) will mount the same volumes and
    PostgreSQL will resume exactly where it left off, including the replication slot.

What is LOST if you pass --wipe:
    - All database data is permanently deleted from the named volumes.
    - You must run 'python db_start.py --fresh' next time to re-initialise everything.
"""

# import argparse
# import datetime
# import os
# import platform
# import shutil
# import subprocess
# import sys
# from pathlib import Path

# # ---------------------------------------------------------------------------
# # Paths
# # ---------------------------------------------------------------------------
# SCRIPT_DIR   = Path(__file__).resolve().parent
# PROJECT_ROOT = SCRIPT_DIR
# BACKUP_DIR   = PROJECT_ROOT / "db_backups"

# # ---------------------------------------------------------------------------
# # Colours
# # ---------------------------------------------------------------------------
# _USE_COLOUR = sys.stdout.isatty() and platform.system() != "Windows"

# def _c(code, text):
#     return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text

# def info(msg):  print(_c("36", f"[INFO]  {msg}"))
# def ok(msg):    print(_c("32", f"[OK]    {msg}"))
# def warn(msg):  print(_c("33", f"[WARN]  {msg}"))
# def error(msg): print(_c("31", f"[ERROR] {msg}"), file=sys.stderr)
# def step(msg):  print(_c("1;35", f"\n>>> {msg}"))


# def _find_docker_compose() -> list[str]:
#     if shutil.which("docker"):
#         r = subprocess.run(
#             ["docker", "compose", "version"],
#             capture_output=True, text=True
#         )
#         if r.returncode == 0:
#             return ["docker", "compose"]
#     if shutil.which("docker-compose"):
#         return ["docker-compose"]
#     error("Neither 'docker compose' nor 'docker-compose' was found in PATH.")
#     sys.exit(1)


# def run(cmd, *, check=True, capture=False, cwd=None):
#     cwd = cwd or PROJECT_ROOT
#     return subprocess.run(
#         cmd, check=check, cwd=str(cwd),
#         capture_output=capture, text=capture
#     )


# # ---------------------------------------------------------------------------
# # Backup
# # ---------------------------------------------------------------------------
# def backup_master(dc: list[str]) -> Path:
#     """pg_dump master_db to a timestamped SQL file in db_backups/."""
#     BACKUP_DIR.mkdir(exist_ok=True)
#     ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     dest = BACKUP_DIR / f"master_db_backup_{ts}.sql"

#     step(f"Dumping master_db to '{dest.name}'...")
#     with open(dest, "wb") as fh:
#         subprocess.run(
#             dc + [
#                 "exec", "-T", "db-master",
#                 "pg_dump", "-U", "admin",
#                 "--clean", "--if-exists",
#                 "--no-owner", "--no-privileges",
#                 "master_db"
#             ],
#             stdout=fh,
#             check=True,
#             cwd=str(PROJECT_ROOT)
#         )
#     ok(f"Backup saved → {dest}")
#     return dest


# # ---------------------------------------------------------------------------
# # Stop
# # ---------------------------------------------------------------------------
# def stop(dc: list[str], *, wipe: bool = False) -> None:
#     if wipe:
#         step("Stopping containers AND deleting named volumes (all data will be lost)...")
#         warn("THIS CANNOT BE UNDONE. You will need 'python db_start.py --fresh' next time.")
#         run(dc + ["down", "--volumes", "--remove-orphans"])
#         ok("Containers and volumes removed.")
#     else:
#         step("Stopping containers (named volumes are PRESERVED — data is safe)...")
#         run(dc + ["down", "--remove-orphans"])
#         ok("Containers stopped. Named volumes retained.")
#         info("Next startup: 'python db_start.py'   — data resumes instantly.")
#         info("Fresh start : 'python db_start.py --fresh'  — wipes everything.")


# # ---------------------------------------------------------------------------
# # Entry point
# # ---------------------------------------------------------------------------
# def main() -> None:
#     parser = argparse.ArgumentParser(
#         description="Gracefully stop the CR Process Automation PostgreSQL cluster."
#     )
#     parser.add_argument(
#         "--wipe", action="store_true",
#         help="DANGER: Delete named volumes. All database data will be permanently lost."
#     )
#     parser.add_argument(
#         "--backup", action="store_true",
#         help="Dump master_db to a .sql file in ./db_backups/ before stopping."
#     )
#     args = parser.parse_args()

#     dc = _find_docker_compose()

#     info(f"OS           : {platform.system()} {platform.release()}")
#     info(f"Docker cmd   : {' '.join(dc)}")
#     info(f"Project root : {PROJECT_ROOT}")

#     if args.wipe and not args.backup:
#         # Prompt for confirmation when wiping without backup
#         ans = input("\n⚠️  --wipe will permanently delete ALL database data. Type 'yes' to continue: ")
#         if ans.strip().lower() != "yes":
#             print("Aborted.")
#             sys.exit(0)

#     if args.backup:
#         try:
#             backup_master(dc)
#         except subprocess.CalledProcessError as exc:
#             error(f"Backup failed: {exc}")
#             error("Containers may not be running. Skipping backup.")

#     stop(dc, wipe=args.wipe)

#     print()
#     ok("=" * 60)
#     ok("  Shutdown complete.")
#     if not args.wipe:
#         ok("  Data is preserved in Docker named volumes:")
#         ok("    cr_process_automation_db_master_volume")
#         ok("    cr_process_automation_db_replica_volume")
#         ok("  Restart anytime with: python db_start.py")
#     else:
#         ok("  Volumes wiped. Restart from scratch with:")
#         ok("    python db_start.py --fresh")
#     ok("=" * 60)


# if __name__ == "__main__":
#     main()


# import argparse
# import os
# import platform
# import shutil
# import subprocess
# import sys
# import time
# from pathlib import Path

# # ---------------------------------------------------------------------------
# # Paths
# # ---------------------------------------------------------------------------
# SCRIPT_DIR   = Path(__file__).resolve().parent
# PROJECT_ROOT = SCRIPT_DIR

# # App artifacts
# TEMP_DIR = PROJECT_ROOT / "app" / "temp"
# LOGS_DIR = PROJECT_ROOT / "app" / "logs"

# # Database sync/backup artifacts
# VOLUMES_DIR  = PROJECT_ROOT / "volumes"
# BACKUP_DIR   = PROJECT_ROOT / "backups"
# MANAGE_PY    = PROJECT_ROOT / "manage.py"
# FIXTURE      = PROJECT_ROOT / "sync_data.json"

# # ---------------------------------------------------------------------------
# # Colours
# # ---------------------------------------------------------------------------
# _USE_COLOUR = sys.stdout.isatty() and platform.system() != "Windows"

# def _c(code: str, text: str) -> str: return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text
# def info(msg):  print(_c("36", f"[INFO]  {msg}"))
# def ok(msg):    print(_c("32", f"[OK]    {msg}"))
# def error(msg): print(_c("31", f"[ERROR] {msg}"), file=sys.stderr)
# def step(msg):  print(_c("1;35", f"\n>>> {msg}"))

# # ---------------------------------------------------------------------------
# # Tooling Execution
# # ---------------------------------------------------------------------------
# def _find_docker_compose() -> list[str]:
#     if shutil.which("docker"):
#         result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
#         if result.returncode == 0:
#             return ["docker", "compose"]
#     if shutil.which("docker-compose"):
#         return ["docker-compose"]
#     error("Neither 'docker compose' nor 'docker-compose' was found in PATH.")
#     sys.exit(1)

# def run(cmd: list[str], *, check=True) -> subprocess.CompletedProcess:
#     env = os.environ.copy()
#     env["PWD"] = str(PROJECT_ROOT)
#     return subprocess.run(cmd, check=check, cwd=str(PROJECT_ROOT), env=env)

# # ---------------------------------------------------------------------------
# # Actions
# # ---------------------------------------------------------------------------
# def perform_backup(dc: list[str]) -> None:
#     step("Creating database backup before shutdown...")
#     BACKUP_DIR.mkdir(exist_ok=True)
#     timestamp = time.strftime("%Y%m%d-%H%M%S")
#     backup_file = BACKUP_DIR / f"master_db_{timestamp}.sql"
    
#     env = os.environ.copy()
#     env["PWD"] = str(PROJECT_ROOT)
    
#     # Run pg_dump inside db-master and pipe the output to a local file
#     try:
#         with open(backup_file, "w") as f:
#             subprocess.run(
#                 dc + ["exec", "-T", "db-master", "pg_dump", "-U", "admin", "master_db"],
#                 stdout=f, check=True, env=env, cwd=str(PROJECT_ROOT)
#             )
#         ok(f"Backup saved to {backup_file}")
#     except subprocess.CalledProcessError:
#         error("Backup failed. Is the container running?")

# def perform_sync(python: str) -> None:
#     step("Syncing database state to Django fixture...")
#     if not MANAGE_PY.exists():
#         error(f"{MANAGE_PY.name} not found. Skipping sync.")
#         return
        
#     try:
#         with open(FIXTURE, "w") as f:
#             subprocess.run(
#                 [python, str(MANAGE_PY), "dumpdata", "--database", "default", "--indent", "2"],
#                 stdout=f, check=True, cwd=str(PROJECT_ROOT)
#             )
#         ok(f"Data synchronized to {FIXTURE.name}")
#     except subprocess.CalledProcessError:
#         error("Sync failed. Check your Django configuration.")

# def cleanup_artifacts() -> None:
#     step("Performing pre-stop cleanup actions...")
#     if TEMP_DIR.exists():
#         shutil.rmtree(TEMP_DIR, ignore_errors=True)
#         info(f"Removed: {TEMP_DIR}")
    
#     if LOGS_DIR.exists():
#         shutil.rmtree(LOGS_DIR, ignore_errors=True)
#         info(f"Removed: {LOGS_DIR}")

# def stop_containers(dc: list[str], wipe: bool) -> None:
#     step("Stopping Docker Compose containers...")
#     try:
#         if wipe:
#             run(dc + ["down", "--volumes", "--remove-orphans"])
#             ok("Containers and Docker volumes removed.")
            
#             if VOLUMES_DIR.exists():
#                 shutil.rmtree(VOLUMES_DIR, ignore_errors=True)
#                 ok(f"Host volume directory deleted: {VOLUMES_DIR}")
#         else:
#             run(dc + ["down"])
#             ok("Containers stopped successfully.")
#     except subprocess.CalledProcessError as e:
#         error(f"Failed to stop containers. Exit code: {e.returncode}")
#         sys.exit(1)

# # ---------------------------------------------------------------------------
# # Entry point
# # ---------------------------------------------------------------------------
# def main() -> None:
#     parser = argparse.ArgumentParser(description="Stop and optionally clean/backup the PostgreSQL cluster.")
#     parser.add_argument("--backup", action="store_true", help="Dump the master_db to a .sql file in the backups directory.")
#     parser.add_argument("--sync", action="store_true", help="Run Django dumpdata to update sync_data.json.")
#     parser.add_argument("--wipe", action="store_true", help="DANGER: Destroy containers, volumes, and local volume directories.")
#     args = parser.parse_args()

#     dc = _find_docker_compose()
#     python = sys.executable
    
#     # Process commands requiring the database to be online first
#     if args.backup:
#         perform_backup(dc)
    
#     if args.sync:
#         perform_sync(python)

#     # Standard cleanups and teardown
#     cleanup_artifacts()
#     stop_containers(dc, wipe=args.wipe)

# if __name__ == "__main__":
#     main()

"""
db_stop.py — Cross-platform graceful shutdown script for CR Process Automation.

Usage:
    python db_stop.py              # Dump sync_data.json, stop containers, keep volumes
    python db_stop.py --no-sync    # Skip the dump this run
    python db_stop.py --backup     # Also pg_dump master_db to a timestamped .sql file
    python db_stop.py --wipe       # Dump, then stop AND delete volumes (fresh start next time)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR

TEMP_DIR = PROJECT_ROOT / "app" / "temp"
LOGS_DIR = PROJECT_ROOT / "app" / "logs"

VOLUMES_DIR  = PROJECT_ROOT / "volumes"
BACKUP_DIR   = PROJECT_ROOT / "backups"
MANAGE_PY    = PROJECT_ROOT / "manage.py"
FIXTURE      = PROJECT_ROOT / "sync_data.json"

# System tables that shouldn't go in a portable data fixture — their IDs
# shift across a fresh `migrate` and break FKs on reload.
EXCLUDE_APPS = ["contenttypes", "auth.permission", "sessions.session", "admin.logentry"]

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
_USE_COLOUR = sys.stdout.isatty() and platform.system() != "Windows"

def _c(code: str, text: str) -> str: return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text
def info(msg):  print(_c("36", f"[INFO]  {msg}"))
def ok(msg):    print(_c("32", f"[OK]    {msg}"))
def warn(msg):  print(_c("33", f"[WARN]  {msg}"))
def error(msg): print(_c("31", f"[ERROR] {msg}"), file=sys.stderr)
def step(msg):  print(_c("1;35", f"\n>>> {msg}"))

# ---------------------------------------------------------------------------
# Tooling Execution
# ---------------------------------------------------------------------------
def _find_docker_compose() -> list[str]:
    if shutil.which("docker"):
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    error("Neither 'docker compose' nor 'docker-compose' was found in PATH.")
    sys.exit(1)

def run(cmd: list[str], *, check=True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PWD"] = str(PROJECT_ROOT)
    return subprocess.run(cmd, check=check, cwd=str(PROJECT_ROOT), env=env)

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
def perform_backup(dc: list[str]) -> None:
    step("Creating database backup before shutdown...")
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    backup_file = BACKUP_DIR / f"master_db_{timestamp}.sql"

    env = os.environ.copy()
    env["PWD"] = str(PROJECT_ROOT)

    try:
        with open(backup_file, "w") as f:
            subprocess.run(
                dc + ["exec", "-T", "db-master", "pg_dump", "-U", "admin", "master_db"],
                stdout=f, check=True, env=env, cwd=str(PROJECT_ROOT)
            )
        ok(f"Backup saved to {backup_file}")
    except subprocess.CalledProcessError:
        error("Backup failed. Is the container running?")

def perform_sync(python: str) -> bool:
    """Dump db-master to sync_data.json via an atomic write. Returns True on success."""
    step(f"Dumping current database state to '{FIXTURE.name}'...")
    if not MANAGE_PY.exists():
        error(f"{MANAGE_PY.name} not found. Skipping sync.")
        return False

    tmp = FIXTURE.with_suffix(".json.tmp")
    cmd = [python, str(MANAGE_PY), "dumpdata", "--database", "default",
           "--natural-foreign", "--natural-primary", "--indent", "2"]
    for app in EXCLUDE_APPS:
        cmd += ["--exclude", app]

    try:
        with open(tmp, "w") as f:
            subprocess.run(cmd, stdout=f, check=True, cwd=str(PROJECT_ROOT))
        tmp.replace(FIXTURE)  # atomic swap — a failed dump never corrupts the last good fixture
        ok(f"Data synchronized to {FIXTURE.name}")
        return True
    except subprocess.CalledProcessError:
        error("Sync failed (is db-master running?). Previous sync_data.json left untouched.")
        tmp.unlink(missing_ok=True)
        return False

def cleanup_artifacts() -> None:
    step("Performing pre-stop cleanup actions...")
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        info(f"Removed: {TEMP_DIR}")
    if LOGS_DIR.exists():
        shutil.rmtree(LOGS_DIR, ignore_errors=True)
        info(f"Removed: {LOGS_DIR}")

def stop_containers(dc: list[str], wipe: bool) -> None:
    step("Stopping Docker Compose containers...")
    try:
        if wipe:
            run(dc + ["down", "--volumes", "--remove-orphans"])
            ok("Containers and Docker volumes removed.")
            if VOLUMES_DIR.exists():
                shutil.rmtree(VOLUMES_DIR, ignore_errors=True)
                ok(f"Host volume directory deleted: {VOLUMES_DIR}")
        else:
            run(dc + ["down"])
            ok("Containers stopped successfully.")
    except subprocess.CalledProcessError as e:
        error(f"Failed to stop containers. Exit code: {e.returncode}")
        sys.exit(1)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Stop and optionally clean/backup the PostgreSQL cluster.")
    parser.add_argument("--backup", action="store_true", help="Dump master_db to a .sql file in the backups directory.")
    parser.add_argument("--no-sync", action="store_true", help="Skip writing sync_data.json this run.")
    parser.add_argument("--wipe", action="store_true", help="DANGER: Destroy containers, volumes, and local volume directories.")
    args = parser.parse_args()

    dc = _find_docker_compose()
    python = sys.executable

    if args.backup:
        perform_backup(dc)

    if not args.no_sync:
        perform_sync(python)
    else:
        info("Skipping sync_data.json update (--no-sync).")

    cleanup_artifacts()
    stop_containers(dc, wipe=args.wipe)

if __name__ == "__main__":
    main()


