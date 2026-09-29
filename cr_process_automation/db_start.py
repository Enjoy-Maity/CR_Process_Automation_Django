#!/usr/bin/env python3
"""
db_start.py — Cross-platform startup script for CR Process Automation PostgreSQL cluster.

Works on: Linux (rootless Docker / Podman), Windows (Docker Desktop + WSL2)

Usage:
    python db_start.py            # Start containers only (no Django migration)
    python db_start.py --migrate  # Start + run Django migrations on master
    python db_start.py --fresh    # Destroy volumes, start clean, migrate, load fixture
    python db_start.py --status   # Show replication health and row counts

What this script does:
    1. Detects the OS and the correct docker / docker-compose binary.
    2. Starts docker-compose with the streaming replication configuration.
    3. Waits for db-master to pass its healthcheck (pg_isready).
    4. Waits for db-replica to connect to db-master as a streaming standby.
    5. Optionally runs Django migrations on master only (replica gets them via replication).
    6. Optionally loads sync_data.json fixture into master.
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
SCRIPT_DIR   = Path(__file__).resolve().parent          # cr_process_automation/
PROJECT_ROOT = SCRIPT_DIR                               # docker-compose.yml lives here
MANAGE_PY    = SCRIPT_DIR / "manage.py"
FIXTURE      = SCRIPT_DIR / "sync_data.json"

# ---------------------------------------------------------------------------
# Colours (disabled on Windows unless ANSI is available)
# ---------------------------------------------------------------------------
_USE_COLOUR = sys.stdout.isatty() and platform.system() != "Windows"

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text

def info(msg):  print(_c("36", f"[INFO]  {msg}"))
def ok(msg):    print(_c("32", f"[OK]    {msg}"))
def warn(msg):  print(_c("33", f"[WARN]  {msg}"))
def error(msg): print(_c("31", f"[ERROR] {msg}"), file=sys.stderr)
def step(msg):  print(_c("1;35", f"\n>>> {msg}"))


# ---------------------------------------------------------------------------
# Docker binary detection
# ---------------------------------------------------------------------------
def _find_docker_compose() -> list[str]:
    """
    Returns the docker-compose command as a list, e.g.:
      ['docker', 'compose']  — modern Docker (v2 plugin, Linux/Mac/Windows)
      ['docker-compose']     — legacy standalone binary
    Raises SystemExit if neither is available.
    """
    # Prefer 'docker compose' (plugin, v2) if available
    if shutil.which("docker"):
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return ["docker", "compose"]

    # Fall back to legacy binary
    if shutil.which("docker-compose"):
        return ["docker-compose"]

    error("Neither 'docker compose' nor 'docker-compose' was found in PATH.")
    error("Please install Docker Desktop (Windows) or Docker / Podman (Linux).")
    sys.exit(1)


def _find_python() -> str:
    """Return the path to the current Python interpreter."""
    return sys.executable


def run(cmd: list[str], *, check=True, capture=False, cwd=None) -> subprocess.CompletedProcess:
    """Thin wrapper around subprocess.run with consistent error handling."""
    cwd = cwd or PROJECT_ROOT
    return subprocess.run(
        cmd, check=check, cwd=str(cwd),
        capture_output=capture, text=capture
    )


# ---------------------------------------------------------------------------
# Health-wait helpers
# ---------------------------------------------------------------------------
def _wait_for_master(dc: list[str], timeout: int = 90) -> None:
    """Poll until db-master is healthy (pg_isready passes)."""
    step("Waiting for db-master to become healthy...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = subprocess.run(
            dc + ["exec", "-T", "db-master",
                  "pg_isready", "-U", "admin", "-d", "master_db"],
            capture_output=True, cwd=str(PROJECT_ROOT)
        )
        if r.returncode == 0:
            ok("db-master is ready.")
            return
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(3)
    print()
    error(f"db-master did not become healthy within {timeout}s.")
    sys.exit(1)


def _wait_for_replica(dc: list[str], timeout: int = 120) -> None:
    """Poll until db-replica appears as a streaming standby on db-master."""
    step("Waiting for db-replica to connect to db-master as a streaming standby...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = subprocess.run(
            dc + ["exec", "-T", "db-master",
                  "psql", "-U", "admin", "-d", "master_db",
                  "-tAc",
                  "SELECT count(*) FROM pg_stat_replication WHERE state='streaming';"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )
        if r.returncode == 0 and r.stdout.strip() == "1":
            ok("db-replica is streaming from db-master.")
            return
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(3)
    print()
    warn("db-replica did not appear as a streaming standby within the timeout.")
    warn("It may still be cloning via pg_basebackup (large dataset). Check logs:")
    warn("  docker compose logs db-replica")


# ---------------------------------------------------------------------------
# Core actions
# ---------------------------------------------------------------------------
def start(dc: list[str], *, destroy_volumes: bool = False) -> None:
    """Start the docker-compose stack."""
    if destroy_volumes:
        step("Destroying existing volumes for a clean start...")
        run(dc + ["down", "--volumes", "--remove-orphans"], check=False)
    else:
        step("Starting PostgreSQL containers (keeping existing data)...")
        run(dc + ["down", "--remove-orphans"], check=False)   # clean stale state

    run(dc + ["up", "-d"])
    ok("Containers started.")


def migrate(python: str) -> None:
    """Run Django migrations on master only."""
    step("Running Django migrations on db-master...")
    run([python, str(MANAGE_PY), "migrate", "--database", "default"])
    ok("Migrations applied to db-master. Replica inherits via streaming replication.")


def load_fixture(python: str) -> None:
    """Load sync_data.json into master if it exists."""
    if not FIXTURE.exists():
        warn(f"Fixture not found: {FIXTURE} — skipping loaddata.")
        return
    step(f"Loading fixture '{FIXTURE.name}' into db-master...")
    run([python, str(MANAGE_PY), "loaddata",
         "--database", "default", str(FIXTURE)])
    ok("Fixture loaded. Replica receives data via streaming replication.")


def show_status(dc: list[str], python: str) -> None:
    """Print replication status and row counts."""
    step("Replication status (pg_stat_replication on db-master):")
    run(dc + ["exec", "-T", "db-master",
              "psql", "-U", "admin", "-d", "master_db",
              "-c",
              "SELECT application_name, state, sent_lsn, write_lsn, flush_lsn, "
              "replay_lsn, sync_state FROM pg_stat_replication;"],
        check=False)

    step("Django model row counts (master vs replica):")
    script = (
        "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE',"
        "'cr_process_automation.settings'); django.setup();"
        "from dashboard.models import MasterCRDatabase;"
        "m = MasterCRDatabase.objects.using('default').count();"
        "r = MasterCRDatabase.objects.using('replica').count();"
        "print(f'  master  MasterCRDatabase rows: {m}');"
        "print(f'  replica MasterCRDatabase rows: {r}');"
        "print('  STATUS: OK' if m == r else '  STATUS: MISMATCH — replica may still be syncing');"
    )
    run([python, "-c", script], check=False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Start the CR Process Automation PostgreSQL streaming-replication cluster."
    )
    parser.add_argument(
        "--migrate", action="store_true",
        help="Apply Django migrations to db-master after startup."
    )
    parser.add_argument(
        "--load-fixture", action="store_true",
        help="Load sync_data.json fixture into db-master after startup."
    )
    parser.add_argument(
        "--fresh", action="store_true",
        help="DANGER: Destroy volumes, start clean, apply migrations and load fixture."
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show replication health and row counts (containers must already be running)."
    )
    args = parser.parse_args()

    dc     = _find_docker_compose()
    python = _find_python()

    info(f"OS           : {platform.system()} {platform.release()}")
    info(f"Docker cmd   : {' '.join(dc)}")
    info(f"Python       : {python}")
    info(f"Project root : {PROJECT_ROOT}")

    if args.status:
        show_status(dc, python)
        return

    # Start containers
    start(dc, destroy_volumes=args.fresh)

    # Health checks
    _wait_for_master(dc)
    _wait_for_replica(dc)

    # Optional: migrations
    if args.migrate or args.fresh:
        migrate(python)

    # Optional: load fixture
    if args.load_fixture or args.fresh:
        load_fixture(python)

    print()
    ok("=" * 60)
    ok("  PostgreSQL cluster is ready.")
    ok(f"  Master  → 127.0.0.1:5432  (master_db)")
    ok(f"  Replica → 127.0.0.1:5433  (master_db, read-only standby)")
    ok("  All writes to master are streamed to replica in real-time.")
    ok("  Run your Django app:  python manage.py runserver 9000")
    ok("=" * 60)


if __name__ == "__main__":
    main()
