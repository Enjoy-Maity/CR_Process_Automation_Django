#!/usr/bin/env python3
"""
db_start.py — Cross-platform startup script for CR Process Automation PostgreSQL cluster.

Works on: Linux (rootless Docker / Podman), Windows (Docker Desktop + WSL2)

Usage:
    python db_start.py             # Start containers, migrate, load sync_data.json, confirm replica synced
    python db_start.py --no-sync   # Start containers, migrate, but skip loading sync_data.json
    python db_start.py --fresh     # DANGER: destroy volumes, start clean, migrate, load sync_data.json
    python db_start.py --status    # Show replication status and exit (containers must already be running)

What this script does:
    1. Detects the OS and the correct docker / docker-compose binary.
    2. Starts docker-compose with the streaming replication configuration.
    3. Waits for db-master to pass its healthcheck (pg_isready).
    4. Waits for db-replica to connect to db-master as a streaming standby.
    5. Optionally runs Django migrations on master only (replica gets them via replication).
    6. Optionally loads sync_data.json fixture into master.
"""

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
# SCRIPT_DIR   = Path(__file__).resolve().parent          # cr_process_automation/
# PROJECT_ROOT = SCRIPT_DIR                               # docker-compose.yml lives here
# MANAGE_PY    = SCRIPT_DIR / "manage.py"
# FIXTURE      = SCRIPT_DIR / "sync_data.json"

# # ---------------------------------------------------------------------------
# # Colours (disabled on Windows unless ANSI is available)
# # ---------------------------------------------------------------------------
# _USE_COLOUR = sys.stdout.isatty() and platform.system() != "Windows"

# def _c(code: str, text: str) -> str:
#     return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text

# def info(msg):  print(_c("36", f"[INFO]  {msg}"))
# def ok(msg):    print(_c("32", f"[OK]    {msg}"))
# def warn(msg):  print(_c("33", f"[WARN]  {msg}"))
# def error(msg): print(_c("31", f"[ERROR] {msg}"), file=sys.stderr)
# def step(msg):  print(_c("1;35", f"\n>>> {msg}"))


# # ---------------------------------------------------------------------------
# # Docker binary detection
# # ---------------------------------------------------------------------------
# def _find_docker_compose() -> list[str]:
#     """
#     Returns the docker-compose command as a list, e.g.:
#       ['docker', 'compose']  — modern Docker (v2 plugin, Linux/Mac/Windows)
#       ['docker-compose']     — legacy standalone binary
#     Raises SystemExit if neither is available.
#     """
#     # Prefer 'docker compose' (plugin, v2) if available
#     if shutil.which("docker"):
#         result = subprocess.run(
#             ["docker", "compose", "version"],
#             capture_output=True, text=True
#         )
#         if result.returncode == 0:
#             return ["docker", "compose"]

#     # Fall back to legacy binary
#     if shutil.which("docker-compose"):
#         return ["docker-compose"]

#     error("Neither 'docker compose' nor 'docker-compose' was found in PATH.")
#     error("Please install Docker Desktop (Windows) or Docker / Podman (Linux).")
#     sys.exit(1)


# def _find_python() -> str:
#     """Return the path to the current Python interpreter."""
#     return sys.executable


# def run(cmd: list[str], *, check=True, capture=False, cwd=None) -> subprocess.CompletedProcess:
#     """Thin wrapper around subprocess.run with consistent error handling."""
#     cwd = cwd or PROJECT_ROOT
#     return subprocess.run(
#         cmd, check=check, cwd=str(cwd),
#         capture_output=capture, text=capture
#     )


# # ---------------------------------------------------------------------------
# # Health-wait helpers
# # ---------------------------------------------------------------------------
# def _wait_for_master(dc: list[str], timeout: int = 90) -> None:
#     """Poll until db-master is healthy (pg_isready passes)."""
#     step("Waiting for db-master to become healthy...")
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         r = subprocess.run(
#             dc + ["exec", "-T", "db-master",
#                   "pg_isready", "-U", "admin", "-d", "master_db"],
#             capture_output=True, cwd=str(PROJECT_ROOT)
#         )
#         if r.returncode == 0:
#             ok("db-master is ready.")
#             return
#         sys.stdout.write(".")
#         sys.stdout.flush()
#         time.sleep(3)
#     print()
#     error(f"db-master did not become healthy within {timeout}s.")
#     sys.exit(1)


# def _wait_for_replica(dc: list[str], timeout: int = 120) -> None:
#     """Poll until db-replica appears as a streaming standby on db-master."""
#     step("Waiting for db-replica to connect to db-master as a streaming standby...")
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         r = subprocess.run(
#             dc + ["exec", "-T", "db-master",
#                   "psql", "-U", "admin", "-d", "master_db",
#                   "-tAc",
#                   "SELECT count(*) FROM pg_stat_replication WHERE state='streaming';"],
#             capture_output=True, text=True, cwd=str(PROJECT_ROOT)
#         )
#         if r.returncode == 0 and r.stdout.strip() == "1":
#             ok("db-replica is streaming from db-master.")
#             return
#         sys.stdout.write(".")
#         sys.stdout.flush()
#         time.sleep(3)
#     print()
#     warn("db-replica did not appear as a streaming standby within the timeout.")
#     warn("It may still be cloning via pg_basebackup (large dataset). Check logs:")
#     warn("  docker compose logs db-replica")


# # ---------------------------------------------------------------------------
# # Core actions
# # ---------------------------------------------------------------------------
# def start(dc: list[str], *, destroy_volumes: bool = False) -> None:
#     """Start the docker-compose stack."""
#     if destroy_volumes:
#         step("Destroying existing volumes for a clean start...")
#         run(dc + ["down", "--volumes", "--remove-orphans"], check=False)
#     else:
#         step("Starting PostgreSQL containers (keeping existing data)...")
#         run(dc + ["down", "--remove-orphans"], check=False)   # clean stale state

#     run(dc + ["up", "-d"])
#     ok("Containers started.")


# def migrate(python: str) -> None:
#     """Run Django migrations on master only."""
#     step("Running Django migrations on db-master...")
#     run([python, str(MANAGE_PY), "migrate", "--database", "default"])
#     ok("Migrations applied to db-master. Replica inherits via streaming replication.")


# def load_fixture(python: str) -> None:
#     """Load sync_data.json into master if it exists."""
#     if not FIXTURE.exists():
#         warn(f"Fixture not found: {FIXTURE} — skipping loaddata.")
#         return
#     step(f"Loading fixture '{FIXTURE.name}' into db-master...")
#     run([python, str(MANAGE_PY), "loaddata",
#          "--database", "default", str(FIXTURE)])
#     ok("Fixture loaded. Replica receives data via streaming replication.")


# def show_status(dc: list[str], python: str) -> None:
#     """Print replication status and row counts."""
#     step("Replication status (pg_stat_replication on db-master):")
#     run(dc + ["exec", "-T", "db-master",
#               "psql", "-U", "admin", "-d", "master_db",
#               "-c",
#               "SELECT application_name, state, sent_lsn, write_lsn, flush_lsn, "
#               "replay_lsn, sync_state FROM pg_stat_replication;"],
#         check=False)

#     step("Django model row counts (master vs replica):")
#     script = (
#         "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE',"
#         "'cr_process_automation.settings'); django.setup();"
#         "from dashboard.models import MasterCRDatabase;"
#         "m = MasterCRDatabase.objects.using('default').count();"
#         "r = MasterCRDatabase.objects.using('replica').count();"
#         "print(f'  master  MasterCRDatabase rows: {m}');"
#         "print(f'  replica MasterCRDatabase rows: {r}');"
#         "print('  STATUS: OK' if m == r else '  STATUS: MISMATCH — replica may still be syncing');"
#     )
#     run([python, "-c", script], check=False)


# # ---------------------------------------------------------------------------
# # Entry point
# # ---------------------------------------------------------------------------
# def main() -> None:
#     parser = argparse.ArgumentParser(
#         description="Start the CR Process Automation PostgreSQL streaming-replication cluster."
#     )
#     parser.add_argument(
#         "--migrate", action="store_true",
#         help="Apply Django migrations to db-master after startup."
#     )
#     parser.add_argument(
#         "--load-fixture", action="store_true",
#         help="Load sync_data.json fixture into db-master after startup."
#     )
#     parser.add_argument(
#         "--fresh", action="store_true",
#         help="DANGER: Destroy volumes, start clean, apply migrations and load fixture."
#     )
#     parser.add_argument(
#         "--status", action="store_true",
#         help="Show replication health and row counts (containers must already be running)."
#     )
#     args = parser.parse_args()

#     dc     = _find_docker_compose()
#     python = _find_python()

#     info(f"OS           : {platform.system()} {platform.release()}")
#     info(f"Docker cmd   : {' '.join(dc)}")
#     info(f"Python       : {python}")
#     info(f"Project root : {PROJECT_ROOT}")

#     if args.status:
#         show_status(dc, python)
#         return

#     # Start containers
#     start(dc, destroy_volumes=args.fresh)

#     # Health checks
#     _wait_for_master(dc)
#     _wait_for_replica(dc)

#     # Optional: migrations
#     if args.migrate or args.fresh:
#         migrate(python)

#     # Optional: load fixture
#     if args.load_fixture or args.fresh:
#         load_fixture(python)

#     print()
#     ok("=" * 60)
#     ok("  PostgreSQL cluster is ready.")
#     ok(f"  Master  → 127.0.0.1:5432  (master_db)")
#     ok(f"  Replica → 127.0.0.1:5433  (master_db, read-only standby)")
#     ok("  All writes to master are streamed to replica in real-time.")
#     ok("  Run your Django app:  python manage.py runserver 9000")
#     ok("=" * 60)


# if __name__ == "__main__":
#     main()


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
MANAGE_PY    = SCRIPT_DIR / "manage.py"
FIXTURE      = SCRIPT_DIR / "sync_data.json"

# Local volume directories
VOLUMES_DIR  = PROJECT_ROOT / "volumes"
MASTER_VOL   = VOLUMES_DIR / "db_master_volume"
REPLICA_VOL  = VOLUMES_DIR / "db_replica_volume"

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
# Docker binary detection & Execution
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

def _find_python() -> str:
    return sys.executable

def run(cmd: list[str], *, check=True, capture=False, cwd=None) -> subprocess.CompletedProcess:
    cwd = cwd or PROJECT_ROOT
    env = os.environ.copy()
    # Explicitly pass PWD so docker-compose.yml resolves ${PWD} correctly on Windows
    env["PWD"] = str(cwd)
    return subprocess.run(
        cmd, check=check, cwd=str(cwd),
        capture_output=capture, text=capture, env=env
    )

# ---------------------------------------------------------------------------
# Health-wait helpers & Utils
# ---------------------------------------------------------------------------
def normalize_line_endings() -> None:
    """
    Converts .sh files to appropriate line endings.
    - Host scripts get LF on Linux/Mac, CRLF on Windows.
    - Container scripts ALWAYS get LF, because the container runs Linux.
    """
    step("Normalizing shell script line endings...")
    
    # These files are mounted into the Linux container and must NEVER be CRLF
    container_scripts = {"init-primary.sh", "init-replica.sh", "create-replicator.sh"}
    host_newline = b'\r\n' if platform.system() == "Windows" else b'\n'
    
    sh_files = list(PROJECT_ROOT.glob("*.sh"))
    if not sh_files:
        ok("No .sh files found to normalize.")
        return

    for sh_file in sh_files:
        with open(sh_file, 'rb') as f:
            content = f.read()
            
        # Normalize everything to LF first
        content = content.replace(b'\r\n', b'\n')
        
        # Apply platform CRLF only if it's a host script and platform is Windows
        if sh_file.name not in container_scripts and host_newline == b'\r\n':
            content = content.replace(b'\n', b'\r\n')
            
        with open(sh_file, 'wb') as f:
            f.write(content)
            
    ok("Shell scripts normalized.")

def _wait_for_master(dc: list[str], timeout: int = 90) -> None:
    step("Waiting for db-master to become healthy...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = run(dc + ["exec", "-T", "db-master", "pg_isready", "-U", "admin", "-d", "master_db"], check=False, capture=True)
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
    step("Waiting for db-replica to connect to db-master as a streaming standby...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = run(dc + ["exec", "-T", "db-master", "psql", "-U", "admin", "-d", "master_db", "-tAc", 
                      "SELECT count(*) FROM pg_stat_replication WHERE state='streaming';"], check=False, capture=True)
        if r.returncode == 0 and r.stdout.strip() == "1":
            ok("db-replica is streaming from db-master.")
            return
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(3)
    print()
    warn("db-replica did not appear as a streaming standby within the timeout.")


def _wait_for_sync(dc: list[str], timeout: int = 60) -> None:
    """
    After loading data into master, poll until the replica's replay position
    matches master's current WAL position — confirms the replica actually has
    the loaded data, not just that it's connected and streaming.
    """
    step("Waiting for db-replica to fully replay loaded data...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = run(dc + ["exec", "-T", "db-master", "psql", "-U", "admin", "-d", "master_db", "-tAc",
                      "SELECT COALESCE(bool_and(replay_lsn = pg_current_wal_lsn()), false) "
                      "FROM pg_stat_replication;"], check=False, capture=True)
        if r.returncode == 0 and r.stdout.strip() == "t":
            ok("db-replica is fully synced with db-master.")
            return
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(2)
    print()
    warn("db-replica did not catch up within the timeout — check `docker compose logs db-replica`.")

# ---------------------------------------------------------------------------
# Core actions
# ---------------------------------------------------------------------------
# def start(dc: list[str], *, destroy_volumes: bool = False) -> None:
#     # Ensure all bash scripts have correct line endings before Docker tries to run them
#     normalize_line_endings()

#     if destroy_volumes:
#         step("Destroying existing volumes for a clean start...")
#         run(dc + ["down", "--volumes", "--remove-orphans"], check=False)
#     else:
#         step("Ensuring pre-start volume directories exist...")
#         MASTER_VOL.mkdir(parents=True, exist_ok=True)
#         REPLICA_VOL.mkdir(parents=True, exist_ok=True)
        
#         step("Starting PostgreSQL containers...")
#         run(dc + ["down", "--remove-orphans"], check=False)

#     run(dc + ["up", "-d"])
#     ok("Containers started.")


# def start(dc: list[str], *, destroy_volumes: bool = False) -> None:
#     # Ensure all bash scripts have correct line endings before Docker tries to run them
#     normalize_line_endings()

#     if destroy_volumes:
#         step("Destroying existing volumes for a clean start...")
#         run(dc + ["down", "--volumes", "--remove-orphans"], check=False)
        
#         # Docker does not delete bind-mounted host files, so we must delete them natively
#         if MASTER_VOL.exists():
#             shutil.rmtree(MASTER_VOL, ignore_errors=True)
#         if REPLICA_VOL.exists():
#             shutil.rmtree(REPLICA_VOL, ignore_errors=True)
#         ok("Host volume directories physically wiped.")
#     else:
#         step("Starting PostgreSQL containers...")
#         run(dc + ["down", "--remove-orphans"], check=False)

#     # Recreate the host directories cleanly before Docker boots
#     step("Ensuring pre-start volume directories exist...")
#     MASTER_VOL.mkdir(parents=True, exist_ok=True)
#     REPLICA_VOL.mkdir(parents=True, exist_ok=True)

#     run(dc + ["up", "-d"])
#     ok("Containers started.")


def start(dc: list[str], *, destroy_volumes: bool = False) -> None:
    if destroy_volumes:
        step("Destroying existing volumes for a clean start...")
        run(dc + ["down", "--volumes", "--remove-orphans"], check=False)
        ok("Named Docker volumes removed.")
    else:
        step("Starting PostgreSQL containers...")
        run(dc + ["down", "--remove-orphans"], check=False)

    # Containers are stopped now, so it's safe to touch the mounted .sh files
    normalize_line_endings()

    run(dc + ["up", "-d"])
    ok("Containers started.")

def migrate(python: str) -> None:
    step("Running Django migrations on db-master...")
    run([python, str(MANAGE_PY), "migrate", "--database", "default"])
    ok("Migrations applied.")

def load_fixture(python: str) -> None:
    if not FIXTURE.exists():
        warn(f"Fixture not found: {FIXTURE} — skipping.")
        return
    step(f"Loading fixture '{FIXTURE.name}' into db-master...")
    run([python, str(MANAGE_PY), "loaddata", "--database", "default", str(FIXTURE)])
    ok("Fixture loaded.")

def show_status(dc: list[str], python: str) -> None:
    step("Replication status:")
    run(dc + ["exec", "-T", "db-master", "psql", "-U", "admin", "-d", "master_db", "-c",
              "SELECT application_name, state, sync_state FROM pg_stat_replication;"], check=False)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
# def main() -> None:
#     parser = argparse.ArgumentParser(description="Start the PostgreSQL cluster.")
#     parser.add_argument("--migrate", action="store_true")
#     parser.add_argument("--load-fixture", action="store_true")
#     parser.add_argument("--fresh", action="store_true")
#     parser.add_argument("--status", action="store_true")
#     args = parser.parse_args()

#     dc = _find_docker_compose()
#     python = _find_python()

#     info(f"OS           : {platform.system()} {platform.release()}")
#     info(f"Project root : {PROJECT_ROOT}")

#     if args.status:
#         show_status(dc, python)
#         return

#     start(dc, destroy_volumes=args.fresh)
#     _wait_for_master(dc)
#     _wait_for_replica(dc)

#     if args.migrate or args.fresh:
#         migrate(python)
#     if args.load_fixture or args.fresh:
#         load_fixture(python)

#     ok("Cluster ready.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the PostgreSQL cluster.")
    parser.add_argument("--fresh", action="store_true", help="DANGER: wipe volumes and start clean.")
    parser.add_argument("--status", action="store_true", help="Show replication status and exit.")
    parser.add_argument("--no-sync", action="store_true", help="Skip loading sync_data.json this run.")
    args = parser.parse_args()

    dc = _find_docker_compose()
    python = _find_python()

    info(f"OS           : {platform.system()} {platform.release()}")
    info(f"Project root : {PROJECT_ROOT}")

    if args.status:
        show_status(dc, python)
        return

    start(dc, destroy_volumes=args.fresh)
    _wait_for_master(dc)
    _wait_for_replica(dc)

    # Idempotent — safe to run every time so tables exist before the fixture load.
    migrate(python)

    if not args.no_sync:
        load_fixture(python)
        _wait_for_sync(dc)
    else:
        info("Skipping sync_data.json load (--no-sync).")

    ok("Cluster ready.")

if __name__ == "__main__":
    main()


