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

import argparse
import datetime
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
BACKUP_DIR   = PROJECT_ROOT / "db_backups"

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
_USE_COLOUR = sys.stdout.isatty() and platform.system() != "Windows"

def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text

def info(msg):  print(_c("36", f"[INFO]  {msg}"))
def ok(msg):    print(_c("32", f"[OK]    {msg}"))
def warn(msg):  print(_c("33", f"[WARN]  {msg}"))
def error(msg): print(_c("31", f"[ERROR] {msg}"), file=sys.stderr)
def step(msg):  print(_c("1;35", f"\n>>> {msg}"))


def _find_docker_compose() -> list[str]:
    if shutil.which("docker"):
        r = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    error("Neither 'docker compose' nor 'docker-compose' was found in PATH.")
    sys.exit(1)


def run(cmd, *, check=True, capture=False, cwd=None):
    cwd = cwd or PROJECT_ROOT
    return subprocess.run(
        cmd, check=check, cwd=str(cwd),
        capture_output=capture, text=capture
    )


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------
def backup_master(dc: list[str]) -> Path:
    """pg_dump master_db to a timestamped SQL file in db_backups/."""
    BACKUP_DIR.mkdir(exist_ok=True)
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"master_db_backup_{ts}.sql"

    step(f"Dumping master_db to '{dest.name}'...")
    with open(dest, "wb") as fh:
        subprocess.run(
            dc + [
                "exec", "-T", "db-master",
                "pg_dump", "-U", "admin",
                "--clean", "--if-exists",
                "--no-owner", "--no-privileges",
                "master_db"
            ],
            stdout=fh,
            check=True,
            cwd=str(PROJECT_ROOT)
        )
    ok(f"Backup saved → {dest}")
    return dest


# ---------------------------------------------------------------------------
# Stop
# ---------------------------------------------------------------------------
def stop(dc: list[str], *, wipe: bool = False) -> None:
    if wipe:
        step("Stopping containers AND deleting named volumes (all data will be lost)...")
        warn("THIS CANNOT BE UNDONE. You will need 'python db_start.py --fresh' next time.")
        run(dc + ["down", "--volumes", "--remove-orphans"])
        ok("Containers and volumes removed.")
    else:
        step("Stopping containers (named volumes are PRESERVED — data is safe)...")
        run(dc + ["down", "--remove-orphans"])
        ok("Containers stopped. Named volumes retained.")
        info("Next startup: 'python db_start.py'   — data resumes instantly.")
        info("Fresh start : 'python db_start.py --fresh'  — wipes everything.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gracefully stop the CR Process Automation PostgreSQL cluster."
    )
    parser.add_argument(
        "--wipe", action="store_true",
        help="DANGER: Delete named volumes. All database data will be permanently lost."
    )
    parser.add_argument(
        "--backup", action="store_true",
        help="Dump master_db to a .sql file in ./db_backups/ before stopping."
    )
    args = parser.parse_args()

    dc = _find_docker_compose()

    info(f"OS           : {platform.system()} {platform.release()}")
    info(f"Docker cmd   : {' '.join(dc)}")
    info(f"Project root : {PROJECT_ROOT}")

    if args.wipe and not args.backup:
        # Prompt for confirmation when wiping without backup
        ans = input("\n⚠️  --wipe will permanently delete ALL database data. Type 'yes' to continue: ")
        if ans.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    if args.backup:
        try:
            backup_master(dc)
        except subprocess.CalledProcessError as exc:
            error(f"Backup failed: {exc}")
            error("Containers may not be running. Skipping backup.")

    stop(dc, wipe=args.wipe)

    print()
    ok("=" * 60)
    ok("  Shutdown complete.")
    if not args.wipe:
        ok("  Data is preserved in Docker named volumes:")
        ok("    cr_process_automation_db_master_volume")
        ok("    cr_process_automation_db_replica_volume")
        ok("  Restart anytime with: python db_start.py")
    else:
        ok("  Volumes wiped. Restart from scratch with:")
        ok("    python db_start.py --fresh")
    ok("=" * 60)


if __name__ == "__main__":
    main()
