# CR Process Automation Django

This is a Django-based web application for automating Change Request (CR) processes.

The app runs as a standard **WSGI** application on Windows and Linux (including a
Linux VM or WSL2 guest running inside a Windows host). A single launcher
(`wsgi_app.py`) picks the right server for the host platform:

| Platform | WSGI server | Notes |
| --- | --- | --- |
| Linux / macOS (incl. Linux VM, WSL2) | **Gunicorn** (`gthread`) | falls back to Waitress if Gunicorn is absent |
| Windows | **Waitress** (threaded) | pure-Python, no build tools needed |

Static files are served by **WhiteNoise** from Django itself, so the app is
self-contained and an external reverse proxy (nginx) is optional — though it is
recommended in production for TLS and caching.

## Quick start

```bash
# 1. Create an environment and install dependencies
python -m venv .venv
. .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Download the Playwright browser used by the automation tasks
python setup_browsers.py

# 3. Configure the environment (see below), then start the server
./start.sh                           # Linux / macOS / Linux VM
start.bat                            # Windows
```

`start.sh` / `start.bat` run migrations + `collectstatic` and then bind
`0.0.0.0:8000`. Open `http://<server-ip>:8000/` from a client; the launcher
prints the reachable URL(s) on startup.

> **Headless Linux:** the automation launches a *non-headless* Chromium, so a
> virtual display is required when there is no desktop session. `start.sh`
> automatically wraps the server in `xvfb-run` when `DISPLAY` is unset. Install
> it with `sudo apt-get install xvfb` (disable the wrapper with `NO_XVFB=1`).

## Configuration

Environment variables are read from `cr_process_automation/dashboard/.env` or
the process environment. Common variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | insecure dev key | set a unique value in production |
| `DJANGO_DEBUG` | `True` | set `False` for production |
| `DJANGO_ALLOWED_HOSTS` | `*` | comma/space separated hosts; restrict in production |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | *(empty)* | e.g. `https://cr-app.internal` when behind TLS |
| `DJANGO_BEHIND_PROXY` | `False` | trust `X-Forwarded-Proto`/`X-Forwarded-Host` from nginx |
| `DJANGO_SECURE_COOKIES` | `False` | mark session/CSRF cookies `Secure` (HTTPS only) |
| `USER_IDLE_TIMEOUT_SECONDS` | `1800` (30 min) | logout after this period of real inactivity; polling does not extend it |
| `DJANGO_DOWNLOAD_DIR` | `~/Automation/PS_Core_Automation/Task_Wise_Automation` | root folder for generated task output files |
| `DB_*` / master-replica settings | local docker | PostgreSQL connection settings |

WSGI launcher options (also settable via `WSGI_*` env vars):

```bash
python wsgi_app.py --help
python wsgi_app.py --migrate --collectstatic --host 0.0.0.0 --port 8000
python wsgi_app.py --host 127.0.0.1 --port 9000 --threads 8   # behind nginx
python wsgi_app.py --server waitress                           # force a server
```

> **Keep a single worker.** The dashboard keeps per-user task state in memory
> and runs automation in background threads, so run **one process with many
> threads** (`WSGI_WORKERS=1`, the default). Multiple worker *processes* would
> split that state and break status polling.

### Database

The app expects a PostgreSQL master (and an optional read replica). With the
bundled Docker Compose setup:

```bash
cd cr_process_automation
./setup.sh              # or: docker compose up -d
python db_start.py      # migrate + load base data
```

Otherwise point the `DB_*` settings at your own PostgreSQL instance, then:

```bash
python manage.py migrate
python manage.py loaddata cr_process_automation/sync_data.json
```

## Login sessions and result isolation

Sessions are stored in the database and expire after `USER_IDLE_TIMEOUT_SECONDS`
of real inactivity. Browser polling endpoints do not reset the idle clock, so an
open tab cannot keep a session alive forever. Log out (or idle expiry) clears
the user's in-memory run state immediately.

Every task start creates a `TaskRun` owned by `request.user` and the current
`session_key`. Logs are written as `TaskLog` rows against that run, and the UI
only reads logs through that owner/session filter. Downloads still require the
same ownership check; path traversal outside the allowed roots is rejected.

Generated task files are region-based:

```
settings.HOST_DOWNLOAD_FOLDER/{date}/{Task-Wise folder}/{Region-name}/
```

Tasks 1-5 use the task's existing `%d-%b-%y` date label and write their artefact
into every selected region folder. The CR Planning download button is shown
only when that artefact exists for **all** selected regions, independent of the
task status badge. Older runs' private `MEDIA_ROOT/task_runs/<run_key>/` copies
remain downloadable.

`raw_report_file` and `planning_sheet` are shared per night/region and remain
guarded by the task modules' file locks. The `region` column already present on
`MasterCRDatabase` and `SelectedDateTable` is reused for the backend CR filter;
no new schema is required. Selecting a date and regions on CR Planning refreshes
both the counts and the CR row table from `MasterCRDatabase` via
`/filter-region-crs/`.

NIAM workbooks follow the same hierarchy:

```
settings.HOST_DOWNLOAD_FOLDER/<night>/NIAM_Excel_files/<region>/RITM Input_PS_Core_<night>.xlsx
settings.HOST_DOWNLOAD_FOLDER/<night>/NIAM_Excel_files/<region>/RITM Output_PS_Core_<night>.xlsx
```

"Save Changes" writes back to the region workbook(s) matching the saved rows.
Per-user isolation is retained for browser sessions and logs, not for the shared
region artefacts.

No schema change is required: region handling reuses the existing `region`
columns on `MasterCRDatabase` and `SelectedDateTable`. Restart the WSGI server
after deploying — Waitress/Gunicorn do not auto-reload code.

## Production behind nginx

Run the WSGI server on loopback and let nginx terminate TLS and serve static
files:

```bash
./start.sh --host 127.0.0.1 --port 8000      # Linux
start.bat  --host 127.0.0.1 --port 8000      # Windows
```

Use `deploy/nginx.conf` as a starting point and set on the app side:

```env
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=cr-app.internal
DJANGO_CSRF_TRUSTED_ORIGINS=https://cr-app.internal
DJANGO_BEHIND_PROXY=True
DJANGO_SECURE_COOKIES=True
```

### Running inside a Linux VM on a Windows host

The guest reports Linux, so the launcher selects Gunicorn automatically. Make
sure the guest is reachable from the client / Windows host:

- Bind to `0.0.0.0` (default) or the VM's bridged IP, not just `127.0.0.1`.
- For NAT networking, forward a host port to the guest (e.g. VirtualBox
  "Port Forwarding": host `8080` → guest `8000`), or run nginx on the Windows
  host with `upstream cr_app { server <guest-ip>:8000; }`.
- Allow the port through the guest and host firewalls.

## Cross-platform notes

- The app is WSGI-compatible and works on both Windows and Linux.
- Use Gunicorn on Linux / Waitress on Windows — `wsgi_app.py` does this for you.
- File paths use `pathlib.Path`; cross-process file locking uses `fcntl` on
  Linux and `msvcrt` on Windows.
- All deployment-specific settings are environment variables.
