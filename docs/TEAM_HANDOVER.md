# Team handover: running CR Process Automation

This document explains how to operate this repository. It is based only on files in the repository; it does not describe the VM or any external system state.

The app is a small internal automation dashboard. It shows CR work, starts browser automations, collects interactive login input, and exposes generated files for download. The framework is deliberately kept in the background here: what matters operationally is the task IDs, date convention, region locks, shared files, and login flow described below.

Related documentation: [`PROJECT_DOCUMENTATION.md`](PROJECT_DOCUMENTATION.md) for the full module/file/feature map, and [`TECHNICAL_BACKEND.md`](TECHNICAL_BACKEND.md) for backend internals.

## 1. What is deployed

- Cross-platform WSGI launcher: `wsgi_app.py`
  - Linux / macOS / Linux VM / WSL2: Gunicorn with `gthread` workers (falls back to Waitress).
  - Windows: Waitress with threads.
  - Static files are served by WhiteNoise when installed, so nginx is optional.
- Launchers:
  - `start.sh` runs `python wsgi_app.py --migrate --collectstatic ...`.
  - `start.bat` runs `python wsgi_app.py --migrate --collectstatic ...`.
- **Keep one worker process.** Per-user run state and background task threads live in process memory (`WSGI_WORKERS=1`, the default). Multiple workers split that state and break status polling; `wsgi_app.py` now forces one worker even if `WSGI_WORKERS` is set higher.
- Playwright launches a **non-headless** Chromium. On a headless Linux host, `start.sh` wraps the server in `xvfb-run` when `DISPLAY` is unset. Install Xvfb with `sudo apt-get install xvfb`; use `NO_XVFB=1` to disable the wrapper.
- Browser binary path is resolved in `dashboard/__init__.py` from `cr_process_automation/pw-browsers/chromium-*`; missing folders raise `FileNotFoundError` at startup.
- Important port mismatch: the README examples and nginx sample use port **8000**, but the current `wsgi_app.py` default is **9000**. Pass `--port` explicitly to avoid surprises.
- Database sessions are stored in the database and idle out after `USER_IDLE_TIMEOUT_SECONDS` (default `1800` seconds). Browser polling does not extend the idle timer. The selected-region list lives in the session, so logout/idle expiry clears it.
- Generated files and logs live under `DJANGO_DOWNLOAD_DIR` (`HOST_DOWNLOAD_FOLDER` is the same path). Logs are in `<download-root>/logs/errors.log` and `<download-root>/logs/notice_timing.log`; private media is under `<download-root>/media/`.

## 2. Main pages

All routes are registered in `dashboard/urls.py`; the menu labels come from `dashboard/views.py`.

| Route | Menu label | What an operator does there |
| --- | --- | --- |
| `/login/`, `/` | Login | Log in to the app. |
| `/home/` | CR Planning | Select a **night date** and one or more regions; run tasks 1–5, watch status/logs, and download shared artefacts. |
| `/night-execution/` | Night Execution | Select the **execution date**, fetch CRs assigned to the logged-in user, and start per-CR buttons: Automation Template, Activity HC, Activity CLI, CR Implementation Task, CR Closure. |
| `/night-spoc/` | Night-SPOC | Intentionally blank for now. |
| `/region-crs/` | Region CRs | Fetch/save CR rows by **execution date** and region. Save permission is limited to Admin, Validator, and Night-SPOC roles. |
| `/cr_wise_status/` | CR-Wise Status | Fetch a status table by **execution date** (PAN-INDIA). |
| `/cr_history/` | CR History | Fetch by execution date or 1/3/6-month ranges (PAN-INDIA); supports download. |
| `/niam-template-db/` | NIAM Template Database | Fetch CRs (task 8), view/edit NIAM rows, download the RITM Input template, and raise NIAM tickets (task 9). |
| `/niam-credentials/` | NIAM Credentials | Update your own NIAM OLM ID and password. |
| `/dashboard/` | — | Dashboard route also exists; the CR Planning page is `/home/`. |
| `/health`, `/health/` | — | Unauthenticated liveness/readiness probe. |

Useful API routes:

- `/api/task/start/<task_id>/`, `/api/task/dashboard-data/`, `/download/task/<task_id>/`
- `/api/region-locks/acquire/`, `/api/region-locks/release/`, `/api/region-locks/status/`
- `/api/region-selection/` — GET reads, POST replaces the persisted selected-region list. Unchecking a region removes it immediately; unload/lock release does not.
- `/filter-region-crs/` — refreshes per-region CR counts from `MasterCRDatabase`, narrowed to the persisted selection.
- `/api/niam/fetch-crs/`, `/api/niam/generate-ticket/`, `/api/niam/save-changes/`
- `/api/user/update-niam-credentials/`
- Login-support iframes: `/playwright-auth-iframe/`, `/playwright-password-iframe/`, `/playwright-notice-iframe/`, `/playwright-alert-iframe/`

## 3. Dates, nights, and access windows

This is the most common source of operator error.

- The UI date input is `YYYY-MM-DD`.
- **CR Planning and NIAM pages use the night date.** The selected night date `D` owns CRs that execute on `D + 1`.
  - `filter_region_crs()` adds one day before querying `MasterCRDatabase`.
  - `_validate_fetch_crs_date()` checks `D + 1` in `NIAMTicketGenerationTable`, `SelectedDateTable`, and `MasterCRDatabase`.
  - `_niam_period_query()` matches rows whose `sr_cr_start_date_time` date is `D + 1` (falling back to `execution_date` if the start time is null).
  - The NIAM page states the rule explicitly: to work on CRs executing `13-11-2026`, select `12-11-2026`.
- **Region CRs, CR-Wise Status, CR History, and Night Execution use the execution date directly**; they query `execution_date=<selected date>`.
- Access windows are not the same thing as the UI date:
  - NIAM access is documented in code as **22:00 on the night date → 08:00 the next day**. The NIAM fetch helper selects rows with `niam_access_start_date_time` on the selected date at hour `22`.
  - CR hygiene pre-checks use **21:00 on the selected date → 06:00 the next day**.
  - Fixture data commonly shows CR maintenance windows such as `00:00:00 - 06:00:00`, and sometimes `23:00:00 - 06:00:00`. Use the data already in `MasterCRDatabase`; do not rewrite the date/window logic when an operator sees a different window.
- Folder labels are task-owned:
  - Tasks 1–5 use `%d-%b-%y` (for example `12-Nov-26`).
  - Tasks 7–9 use `%d_%b_%Y` (for example `12_Nov_2026`).
  - NIAM workbook filenames use the `%d_%b_%Y` label: `RITM Input_PS_Core_<night>.xlsx` and `RITM Output_PS_Core_<night>.xlsx`.

If Fetch CRs says "No Data" but CRs exist on the picked date, select the previous date as the night date. The backend includes this hint in its error message.

## 4. Task catalogue (IDs 1–9)

Defined in `dashboard/views.py`.

| ID | Exact name | Where started | Auth group | Artefact behaviour |
| --- | --- | --- | --- | --- |
| 1 | RAW Report to Template | CR Planning | ITSM (`TASKS_REQUIRING_AUTH`) | Shared raw report and planning sheet per night/region. |
| 2 | CR Hygiene Checks | CR Planning | ITSM | `CR_Hygiene_Checks.xlsx` per night/region. |
| 3 | Install/Test Plan Downloads | CR Planning | ITSM | `Plan_Files_Download_<label>.zip` per night/region. |
| 4 | BPMS CR Hygiene Checks | CR Planning | ITSM | `BPMS_CR_Hygiene_Checks.xlsx` per night/region. |
| 5 | MOP Attachment & Approvals | CR Planning | ITSM | `MOP_Attachment_Approval_status.xlsx` per night/region. |
| 6 | Final Email Package | CR Planning table only | — | **Not implemented in this repository.** `TASK_MODULE_MAP` points at `dashboard.task_modules.final_email_package.tasks`, but that directory/module does not exist. Starting it produces a module import error. |
| 7 | NIAM Ticket Generation | NIAM Template Database | NIAM | Strict-eligibility generation flow; uses `dashboard.task_modules.niam_ticket_generation.tasks`. |
| 8 | Fetch CRs | NIAM Template Database "Fetch CR" | NIAM | No download of its own. Validates the night, rebuilds `SelectedDateTable` for `D + 1`, and adds NIAM template rows for `NIAM Ticket Required = Yes`; existing rows are kept. |
| 9 | Raise NIAM Tickets | NIAM Template Database "NIAM Ticket Generator" | NIAM | Updates `NIAMTicketGenerationTable` with RITM number / `Failure Reason` and writes `RITM Output_PS_Core_<night>.xlsx`. |

`TASKS_REQUIRING_AUTH = {1, 2, 3, 4, 5}`. Tasks 7–9 are NIAM work and are intentionally absent from the CR Planning task table. Task 8 has `download_required: False`; tasks 1–7 and 9 have downloads enabled.

## 5. Day-to-day workflows

### CR Planning (tasks 1–5)

1. Open `/home/`.
2. Select the night date and at least one region. The exact checked set is saved to the Django session; it stays selected across page navigation and reloads until you uncheck it or the session ends.
3. Selecting a region also acquires a DB-backed lock; other users see it disabled with the holder's name. A lock held by someone else never silently clears your saved selection. The `/filter-region-crs/` call refreshes all/planned CR counts for the selected regions.
4. Start tasks in sequence. A task runs in a background thread with an isolated runtime, logs, and `TaskRun` owned by the current user/session.
5. Watch the status cell and log panel; `dashboard.js` polls the dashboard API every 500 ms and includes `run_key` in every auth iframe URL. Statuses include `Running`, `Completed`, `Failed`, `Waiting for Password`, `Waiting for OTP`, and `Waiting for Sign-in Approval`. A second start is rejected while the same user/task is still active.
6. Download becomes available when the expected artefact exists for **all** selected regions, independent of the badge status. Older private `MEDIA_ROOT/task_runs/<run_key>/` copies remain owner/session scoped.

### NIAM Template Database

1. Open `/niam-template-db/` and select the **night** date (or a range shortcut).
2. Click **Fetch CR** (task 8). The backend refuses dates without CRs for `D + 1` and tells you if you picked the execution date by mistake.
3. Edit allowed NIAM columns where permitted, then **Save Changes**. Only rows whose derived region is in the persisted selection are editable. Blank values are allowed for placeholders; list columns must use allowed options. Saves write to both `NIAMTicketGenerationTable` and the derived regional workbook.
4. Click **Download Template** for `RITM Input_PS_Core_<night>.xlsx`.
5. Click **NIAM Ticket Generator** (task 9). When it finishes, the page offers the `RITM Output` workbook download.
6. If Microsoft sign-in needs attention, use the iframe prompt described in section 7. Do not restart the task while the prompt is open.

### Night Execution, Region CRs, CR History, CR-Wise Status

- These pages use the **execution date** directly.
- Night Execution filters active `MasterCRDatabase` rows by `activity_executor` matching the logged-in user's employee name, username, or full name **and** by the persisted region selection. Statuses/task buttons reject CRs outside that selection.
- CR-Wise Status and CR History are read-only but also filter rows server-side to the persisted selection, including exports.
- Region CRs and NIAM Template Database share the same edit-role check (`Admin`, `Validator`, `Night-SPOC`) and additionally mark unselected-region rows read-only.
- Region CR saves can rebuild `SelectedDateTable` for affected execution dates and renumber NIAM rows.

## 6. Region locks and shared artefacts

### Locks

- Region keys: `north`, `west`, `east`, `south`.
- Lock records are in the `RegionLock` table on the default database.
- TTL is `REGION_LOCK_TTL_SECONDS = 120`.
- `region_locks.js` polls status every `3000` ms and renews the selected regions on each heartbeat. Locks are released on uncheck, page unload, or logout; expired rows are purged lazily. Heartbeats are real activity and keep the session alive.
- Another user's region checkbox is disabled and shows the holder's full name or username. If the region is still in your saved selection it remains checked, so losing a lock does not silently clear the selection.
- `start_task()` rechecks conflicts and rejects the start with title `Region Locked` if any selected region is held by someone else.
- Acquire is transactional (`select_for_update` plus an `IntegrityError` retry) so simultaneous selections of the same region cannot both win.

### Shared artefact paths

Root pattern:

```text
settings.HOST_DOWNLOAD_FOLDER/{date}/{Task-Wise folder}/{Region-name}/
```

Central templates are set in `dashboard/__init__.py`:

```text
<root>/{date}/Raw_Report_to_Template/{region}/
<root>/{date}/Planning_Sheet/{region}/
<root>/{date}/CR_Hygiene_Checks/{region}/CR_Hygiene_Checks.xlsx
<root>/{date}/Plan_Files_Download/{region}/Plan_Files_Download_{label}.zip
<root>/{date}/BPMS_CR_Hygiene_Checks/{region}/BPMS_CR_Hygiene_Checks.xlsx
<root>/{date}/Mop_Attachment_Approval/{region}/MOP_Attachment_Approval_status.xlsx
<root>/<night>/NIAM_Excel_files/<region>/... (see below)
```

The path templates above are defined as environment variables in `dashboard/__init__.py`. `BPMS_CR_HYGIENE_CHECKS_FILE` is the variable name for the `BPMS_CR_Hygiene_Checks.xlsx` path.

NIAM workbooks:

```text
<root>/<night>/NIAM_Excel_files/<region>/RITM Input_PS_Core_<night>.xlsx
<root>/<night>/NIAM_Excel_files/<region>/RITM Output_PS_Core_<night>.xlsx
```

`REGION_TASK_IDS = (1, 2, 3, 4, 5, 9)`. A run of one of these tasks publishes its artefact into every selected region folder. Shared outputs may be downloaded by any logged-in user once all selected regions have the file; private/legacy run copies still require ownership. Path traversal outside allowed roots is rejected.

`raw_report_file` and `planning_sheet` remain guarded by the task modules' own file locks.

### Shared status markers and AND logic

Markers are kept outside artefact folders:

```text
<root>/.task_status/<task_id>/<date-label>/<region>.json
```

Each file contains `{"status":"..."}`. The CR Planning badge reduces the selected regions as follows:

- `Failed` if **any** selected region marker is `Failed`.
- `Completed` only if **every** selected region marker is `Completed`.
- If no markers exist but the expected artefact exists for every selected region, the badge is `Completed` (legacy compatibility).
- Otherwise `Pending`. A `Running` marker therefore still displays as `Pending` until all selected regions finish.

No schema change was needed for this: status is stored in marker files under the download root, not in database tables. The existing `region` columns on `MasterCRDatabase` and `SelectedDateTable` are used only for CR data.

## 7. NIAM credentials, MFA, and iframe alerts

### Credentials

- Page: `/niam-credentials/`; endpoint: `/api/user/update-niam-credentials/` (POST JSON).
- Fields: `niam_olm_id`, `niam_password`, `confirm_niam_password`.
- Any logged-in user can update only their own credentials. Password minimum: 8 characters with at least one letter and one digit.
- The page shows the saved OLM ID and whether a password is set; it does not display the stored password.
- Credentials are stored against the Django username and used by the NIAM Playwright flow.

### Login and MFA behaviour

- Each NIAM ticket run writes a private browser storage file at `MEDIA_ROOT/niam_sessions/niam_session_<run_key>.json`, so concurrent users do not overwrite cookies.
- The login helper handles Microsoft's `Choose a way to sign in` chooser: it looks for a visible `Use my password` or `Approve a request` option rather than a hidden DOM template.
- After a password it detects visible `Approve sign in`, `Verify your identity`, or `Face, fingerprint, PIN, or security key` prompts. On the verification path it can click `Approve a request on my Microsoft Authenticator app`.
- The Microsoft Authenticator sign-in code is displayed in a **read-only notice iframe** with status `Waiting for Sign-in Approval`; it is cleared once the sign-in prompt disappears.
- Wrong OLM ID / password produces a blocking alert in the alert iframe, with messages pointing to `NIAM Credentials`. Alerts stay until acknowledged or replaced by a new run; the frontend remembers them by `task.id`, `run_key`, and `alert_seq` so the 3-second poll does not reopen them.
- `Waiting for Password` and `Waiting for OTP` states open the corresponding interactive iframe. Interactive prompts and the time-sensitive notice take priority over alerts.
- Timing checkpoints are logged by `dashboard.notice` to `<download-root>/logs/notice_timing.log`; errors go to `<download-root>/logs/errors.log`.

Live tail on Linux (from the repository root):

```bash
chmod +x scripts/watch_niam_timing.sh
./scripts/watch_niam_timing.sh                 # timing + errors + journal
./scripts/watch_niam_timing.sh --no-journal    # files only
./scripts/watch_niam_timing.sh --reset         # clear timing log first
SERVICE=cr-app ./scripts/watch_niam_timing.sh  # choose the systemd unit
```

The script also writes a timestamped capture under `cr_process_automation/logs/`.

## 8. Local setup and run

From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python setup_browsers.py

# Linux/macOS/VM
./start.sh                           # or: ./start.sh --host 127.0.0.1 --port 8000

# Windows
start.bat                            # or: start.bat --host 127.0.0.1 --port 8000
```

`start.sh` / `start.bat` already run migrations and `collectstatic`.

Database bootstrap with the bundled Docker Compose setup:

```bash
cd cr_process_automation
./setup.sh              # or: docker compose up -d
python db_start.py      # migrate + load sync_data.json + wait for replica replay
```

When you want migrations but want to **keep the existing database contents**, run:

```bash
cd cr_process_automation
python db_start.py --no-sync
```

`--no-sync` starts/recreates the containers, waits for master health and replica streaming, and runs migrations on the master. It skips loading `sync_data.json` and skips the replica replay-position check for that load. `--fresh` destroys volumes and must not be used for routine restarts; `--status` only prints replication status. `db_start.py` normalizes shell-script line endings before starting containers.

For an external PostgreSQL instance, point the `DB_*` settings at it and run:

```bash
python manage.py migrate
python manage.py loaddata cr_process_automation/sync_data.json
```

Configuration is read from the process environment or `cr_process_automation/dashboard/.env`. Production should set `DJANGO_DEBUG=False`, a unique `DJANGO_SECRET_KEY`, restricted `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, and, behind TLS, `DJANGO_BEHIND_PROXY=True` and `DJANGO_SECURE_COOKIES=True`. Do not commit credentials, tokens, or keys.

## 9. Deployment and operations facts

- `deploy/nginx.conf` is a sample reverse proxy: app on `127.0.0.1:8000`, keepalive upstream, and optional static-file alias and TLS blocks. Replace hostnames, alias paths, and certificates for your site.
- Behind nginx on the same machine: `./start.sh --host 127.0.0.1 --port 8000` or `start.bat --host 127.0.0.1 --port 8000`.
- In a Linux VM on a Windows host, either bind to `0.0.0.0`/the bridged IP and open firewalls, or forward a host port (example: host `8080` → guest `8000`), or run nginx on the Windows host with `upstream cr_app { server <guest-ip>:8000; }`.
- Restart the WSGI server after deploying code. Waitress/Gunicorn do not auto-reload; database sessions survive a restart, in-memory task state does not.
- `deploy.py` is a thin wrapper that puts `cr_process_automation/` on `sys.path` and forwards arguments to Django management commands.
- `README.Docker.md` mentions `docker compose up --build` with the app at `http://localhost:9000`; the primary operational path in `README.md` is the WSGI launcher.
- Use `python wsgi_app.py --help` to see launcher options (`WSGI_HOST`, `WSGI_PORT`, `WSGI_WORKERS`, `WSGI_THREADS`, `WSGI_SERVER`, timeout).

## 10. Troubleshooting

| Symptom | Check |
| --- | --- |
| Region checkbox disabled with another user's name | The holder owns the lock. Wait for the 120 s TTL to expire or ask the holder to uncheck/close the page/log out. Your saved selection is not cleared by this. |
| Save Changes disabled / rows read-only | The row's region is not in your persisted selection. Return to CR Planning and check that region; an empty selection means no region is editable. |
| Task start fails with `Region Locked` | A selected region was acquired by someone else between selection and start. Refresh and reselect. |
| Status stays `Pending` but files exist | The selected regions must all have the expected artefact. Check the per-region folder and `.task_status/<task>/<date>/<region>.json`. A `Running` marker reduces to `Pending`. |
| Download button hidden | Download requires the artefact in **every** selected region folder, not just one. Verify the task-owned date label (`%d-%b-%y` vs `%d_%b_%Y`). |
| Task 6 fails with module import error | Expected in this repository: `final_email_package.tasks` does not exist. Do not treat it as a deployment regression. |
| `No Data` from Fetch CRs | The date is probably the execution date. Select the previous night date. The backend error may suggest the exact date. |
| NIAM template shows no rows for a selected night | The page matches `D + 1` on `sr_cr_start_date_time` (or `execution_date` when the start is null). Confirm the CRs execute on the following day. |
| NIAM sign-in alert iframe appears | Check the saved OLM ID/password in NIAM Credentials, acknowledge the alert, and retry. Wrong ID and wrong password have distinct log messages. |
| Sign-in code iframe is open | This is normal during Authenticator approval. Match the code on the phone, approve, and wait for the notice to clear. |
| Password/OTP iframe does not respond | The runtime is process-local and each submission must carry the current `run_key`. Confirm a single WSGI worker, hard-refresh the page so the iframe has the new `run_key`, keep the tab on the same app process, and check `errors.log` for `Stale Run` / `Stale OTP` / `Stale Password`. |
| Browser task fails on headless Linux | Install Xvfb or provide a `DISPLAY`; verify the Chromium folder under `pw-browsers` and run `python setup_browsers.py`. |
| Stale UI after deployment | Restart the WSGI server and hard-refresh the browser to bypass cached static files. |
| DB startup fails on Windows line endings | `db_start.py` normalizes `.sh` files; container scripts are forced to LF, host scripts to CRLF on Windows. |
| Replica appears behind | Check `python db_start.py --status` and `docker compose logs db-replica`. A plain `db_start.py` waits for replay; `--no-sync` deliberately skips that load-specific wait. |
| Polling appears to keep sessions alive | It does not. Idle timeout is based on real activity; users will be logged out after `USER_IDLE_TIMEOUT_SECONDS`. |

## 11. Recent region-based changes

Current committed HEAD is `5564b1d Fix concurrent ITSM authentication`. Relevant recent history:

- `a5485c2` — user-scoped sessions and NIAM file isolation.
- `d49a4c6` — NIAM login timing diagnostics and robust MFA handling.
- `62216d6` — handle `Approve a request` on the Microsoft sign-in chooser.
- `2c33eb9` — region-based task outputs and backend CR refresh.
- `6ba8c55` — shared task outputs downloadable by any logged-in user.
- `1bbf8e7` — remove the `MasterCRDatabase` detail table from the CR Planning UI.
- `cefe5dc` — shared per-region status markers with boolean AND reduction.

These changes reused existing `region` columns and did not require a schema migration.

## 12. Source files used

- `README.md`, `README.Docker.md`, `start.sh`, `start.bat`, `wsgi_app.py`, `deploy.py`, `deploy/nginx.conf`
- `cr_process_automation/db_start.py`, `cr_process_automation/cr_process_automation/settings.py`, `cr_process_automation/cr_process_automation/urls.py`
- `cr_process_automation/dashboard/views.py`, `urls.py`, `models.py`, `services.py`, `__init__.py`
- `cr_process_automation/dashboard/utils/region_paths.py`, `region_status.py`, `niam_paths.py`, `task_runtime.py`
- `cr_process_automation/dashboard/Region_CRs/views.py`, `Night_Execution/views.py`, `Night_Execution/services.py`, `CR_Wise_Status/views.py`
- `cr_process_automation/dashboard/task_modules/` (NIAM, ITSM tasks, `dependencies/playwright_common_methods_.py`, `dependencies/extra_dependencies.py`)
- `cr_process_automation/dashboard/templates/dashboard/` and `static/dashboard/js/` (`home.html`, `niam_template_db.html`, `niam_credentials.html`, `region_crs.html`, `cr_history.html`, `cr_wise_status.html`, `night_execution.html`, `night_spoc.html`, `dashboard.js`, `region_locks.js`)
- `scripts/watch_niam_timing.sh` and local `git log --oneline`
