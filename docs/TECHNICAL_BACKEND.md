# Technical Backend Reference

Scope: backend structure and control flow of **this** Django project. Paths are repository-relative. This document describes code as implemented; it does not prescribe a redesign. Secrets and credential values are intentionally omitted.

Related documentation: [`PROJECT_DOCUMENTATION.md`](PROJECT_DOCUMENTATION.md) for the consolidated module/file and feature map, and [`TEAM_HANDOVER.md`](TEAM_HANDOVER.md) for operational workflows.

## 1. Repository map

| Area | Path | Contents |
|---|---|---|
| Django project | `cr_process_automation/cr_process_automation/settings.py` | Env loading, PostgreSQL aliases, sessions, middleware, static/media, logging, app field constants. |
|  | `cr_process_automation/cr_process_automation/urls.py` | Mounts `admin/` and `include('dashboard.urls')`; serves `MEDIA_URL` in debug. |
|  | `cr_process_automation/cr_process_automation/routers.py` | `CoWRouter`: master/replica routing. |
|  | `cr_process_automation/cr_process_automation/wsgi.py` | WSGI entry point used by `wsgi_app.py`. |
| Main app | `cr_process_automation/dashboard/urls.py` | All dashboard routes listed in §2. |
|  | `cr_process_automation/dashboard/views.py` | Auth, task start/run/orchestration, downloads, region locks, NIAM APIs, analysis APIs, iframes. |
|  | `cr_process_automation/dashboard/models.py` | `CoWModel`, CR/selected-date models, task run/log models, NIAM models, `RegionLock`. |
|  | `cr_process_automation/dashboard/middleware.py` | `CustomExceptionMiddleware`, `SessionIdleTimeoutMiddleware`. |
|  | `cr_process_automation/dashboard/exceptions.py` | `CustomException` subclasses and JSON shape. |
|  | `cr_process_automation/dashboard/services.py` | Atomic CR flag/update helpers imported by `views.py`. |
|  | `cr_process_automation/dashboard/apps.py` | Registers signals; lazily seeds NIAM reference tables. |
|  | `cr_process_automation/dashboard/signals.py` | Post-save/post-delete hooks for `MasterCRDatabase` and `CRWiseStatus`. |
|  | `cr_process_automation/dashboard/niam_seed.py` | Seed data used by `DashboardConfig._seed_niam_reference_tables`. |
| Runtime utilities | `cr_process_automation/dashboard/utils/task_runtime.py` | Per-user runtime map, fresh module loading, private output copy, shared input paths. |
|  | `cr_process_automation/dashboard/utils/region_paths.py` | Region-safe paths, date labels, artefact discovery, region fan-out. |
|  | `cr_process_automation/dashboard/utils/region_status.py` | Per-region status marker files and combined status. |
|  | `cr_process_automation/dashboard/utils/niam_paths.py` | NIAM input/output workbook paths. |
|  | `cr_process_automation/dashboard/utils/file_locks.py` | Cross-platform advisory file lock. |
|  | `cr_process_automation/dashboard/utils/replica_sync.py` | Legacy SQLite master→replica copy helper. |
|  | `cr_process_automation/dashboard/utils/exception_handler.py` | `handle_exceptions` decorator. |
| Task implementations | `cr_process_automation/dashboard/task_modules/<module>/tasks.py` | Task IDs 1–5, 7, 8; task 9 lives in `niam_ticket_generation/niam_ticket_generation_tasks.py`. |
|  | `cr_process_automation/dashboard/task_modules/dependencies/extra_dependencies.py` | Shared NIAM/CR DataFrame, workbook, dropdown, and renumbering helpers. |
| Sub-apps | `cr_process_automation/dashboard/Region_CRs/` | Region CR table, history, save/edit, CoW sync helpers. |
|  | `cr_process_automation/dashboard/CR_Wise_Status/` | CR-wise status view and fetch API. |
|  | `cr_process_automation/dashboard/Night_Execution/` | Separate job-based night-execution flow. |
|  | `cr_process_automation/dashboard/vendor_dashboard/` | Present in tree; routes are commented out in `urls.py`. |
| Frontend | `cr_process_automation/dashboard/static/dashboard/js/dashboard.js` | Task polling/start/auth overlay. |
|  | `cr_process_automation/dashboard/static/dashboard/js/region_locks.js` | Region lock heartbeat. |
|  | `cr_process_automation/dashboard/static/dashboard/js/night_execution.js` | Night Execution polling/auth. |
|  | `cr_process_automation/dashboard/templates/dashboard/` | Pages and iframe templates, including `niam_template_db.html`. |
| Operations | `wsgi_app.py`, `start.sh`, `start.bat`, `compose.yaml`, `Dockerfile` | Cross-platform launcher and container entry points. |
|  | `cr_process_automation/docker-compose.yml` | Local PostgreSQL master/replica services. Do not reuse checked-in credentials in production. |
|  | `deploy/nginx.conf`, `scripts/watch_niam_timing.sh`, `scripts/watch_niam_timing.ps1` | Sample reverse proxy and NIAM timing log watchers. |
| Docs | `docs/TEAM_HANDOVER.md` | Existing operational handover; this file is a separate backend reference. |

## 2. Request/response architecture

### Middleware and error shape

- Settings installs `whitenoise.middleware.WhiteNoiseMiddleware` when available, then session/common/CSRF/auth, `dashboard.middleware.SessionIdleTimeoutMiddleware`, messages, clickjacking, and `dashboard.middleware.CustomExceptionMiddleware`.
- Most JSON endpoints use `@require_GET` / `@require_POST`, `@login_required(login_url="login")`, and `@handle_exceptions`.
- `CustomException.to_dict()` and `handle_exceptions` return `{"ok": false, "title": ..., "message": ..., "status_code": ...}` with statuses from `ValidationException` (400), `NotFoundException` (404), `PermissionException` (403), `AuthenticationException` (401), `TaskExecutionException`/`DatabaseException` (500).
- `/health` and `/health/` call `health_check` without auth; they check `connections["default"]` and return `{"status": "ok"|"degraded", "database": bool}` with 200/503.
- `X_FRAME_OPTIONS = 'SAMEORIGIN'`; auth iframes use `@xframe_options_sameorigin`.

### Endpoint map

| Path | View | Method/purpose |
|---|---|---|
| `/`, `/login/` | `views.login_view` | GET/POST login via `LoginForm`; success redirects to `cr_planning`. |
| `/logout/` | `views.logout_view` | Clears `RUN_REGISTRY`, deletes user `RegionLock` rows, logs out. |
| `/health`, `/health/` | `views.health_check` | Liveness/DB probe. |
| `/home/` | `views.cr_planning_view` | CR Planning page. |
| `/dashboard/` | `views.dashboard_view` | Analysis dashboard page. |
| `/night-spoc/` | `views.night_spoc_view` | Night SPOC page. |
| `/region-crs/`, `/cr_history/` | `Region_views.region_crs_view`, `Region_views.cr_history_view` | Region CR pages. |
| `/cr_wise_status/` | `CR_Wise_Status_views.cr_wise_status` | CR status page. |
| `/api/task/start/<int:task_id>/` | `views.start_task` | POST `date`, `region`; starts isolated background run. |
| `/api/task/dashboard-data/` | `views.task_dashboard_data` | GET polling payload; optional `date`, `regions`, `cr_planning=1`. |
| `/download/task/<int:task_id>/` | `views.download_task_output` | GET shared region artefact or private run copy. |
| `/api/task/submit-otp/<int:task_id>/` | `views.submit_otp` | POST `otp` + `run_key`; sets runtime OTP event only on an exact match. |
| `/api/task/submit-password/<int:task_id>/` | `views.submit_password` | POST `password` + `run_key`; sets runtime password event only on an exact match. |
| `/playwright-auth-iframe/`, `/playwright-password-iframe/` | `views.playwright_auth_iframe`, `views.playwright_password_iframe` | OTP/password form iframes bound to `task_id` + `run_key`; stale submissions are rejected. |
| `/playwright-notice-iframe/`, `/playwright-alert-iframe/` | `views.playwright_notice_iframe`, `views.playwright_alert_iframe` | Read-only sign-in notice / blocking alert iframes, also bound to `task_id` + `run_key`. |
| `/api/region-locks/acquire/`, `/api/region-locks/release/`, `/api/region-locks/status/` | `views.acquire_region_locks`, `views.release_region_locks`, `views.region_lock_status` | Region lock heartbeat endpoints. |
| `/filter-region-crs/` | `views.filter_region_crs` | GET `date`, `regions`; returns `counts_all`, `counts_planned`, `rows`, `cr_rows`. Selected night maps to `execution_date = date + 1`. |
| `/region-crs/fetch-region-cr-details/`, `/cr_history/fetch-region-cr-details/` | `Region_views.fetch_region_cr_details` | Fetch region CR rows. |
| `/region-crs/save-region-cr-details` | `Region_views.save_region_cr_details` | Save edits (no trailing slash in route). |
| `/fetch-cr-history/`, `/download-cr-history/` | `Region_views.fetch_cr_history`, `Region_views.download_cr_history` | History query/export. |
| `/fetch-cr-wise-status/` | `CR_Wise_Status_views.fetch_cr_wise_status` | CR status data. |
| `/fetch-user-options/` | `views.fetch_user_options` | Active `UserManagement` employee options. |
| `/api/replica-sync-status/<str:sync_id>/` | `views.check_replica_sync_status` | Placeholder polling endpoint. |
| `/night-execution/` | `NightExecution_views.night_execution` | Page. |
| `/night-execution/fetch-crs/`, `/night-execution/fetch-cr-status/`, `/night-execution/start-task/`, `/night-execution/status-result/` | `fetch_night_execution_crs`, `fetch_night_cr_status`, `start_night_execution_task`, `night_cr_status_result` | Separate job-based flow. |
| `/night-execution/submit-password/`, `/night-execution/submit-otp/`, `/night-execution/password-iframe/`, `/night-execution/otp-iframe/` | `submit_night_password`, `submit_night_otp`, `night_password_iframe`, `night_otp_iframe` | Night Execution auth; job-scoped, owner-checked, with `run_key = job_id`. |
| `/vendor-wise-analysis/`, `/fetch-vendor-wise-analysis/` | `views.vendor_wise_analysis_view`, `views.fetch_vendor_wise_analysis` | Analysis page/API. |
| `/cr-success-rate-analysis/`, `/fetch-cr-success-rate-analysis/` | `views.cr_success_rate_analysis_view`, `views.fetch_cr_success_rate_analysis` | Analysis page/API. |
| `/team-performance-analysis/`, `/fetch-team-performance-analysis/` | `views.team_performance_analysis_view`, `views.fetch_team_performance_analysis` | Analysis page/API. |
| `/automation-cr-analysis/`, `/fetch-automation-cr-analysis/` | `views.automation_cr_analysis_view`, `views.fetch_automation_cr_analysis` | Analysis page/API. |
| `/niam-template-db/` | `views.niam_template_db_view` | NIAM Template Database page. |
| `/fetch-niam-template-data/` | `views.fetch_niam_template_data` | GET NIAM rows. |
| `/download-niam-template/` | `views.download_niam_template` | GET in-memory Excel export. |
| `/api/niam/fetch-crs/` | `views.start_niam_fetch_crs` | POST `date`; delegates to `start_task(8)`. |
| `/api/niam/generate-ticket/` | `views.start_niam_ticket_generation` | POST `date`; delegates to `start_task(9)`. |
| `/api/niam/save-changes/` | `views.save_niam_template_changes` | POST JSON `{date, rows}`. |
| `/niam-credentials/`, `/api/user/update-niam-credentials/` | `views.niam_credentials_view`, `views.update_niam_credentials` | Self-service NIAM OLM ID/password update. |

### Page context

`_common_context()` builds `page_title`, selected menu option, `user_name`/`user_role`, `running_task`, `task_logs`, and `tasks` via `_build_tasks_for_ui()`. `menu_items` includes CR Planning, Night Execution, Night-SPOC, Region CRs, CR-Wise Status, CR History, NIAM Template Database, and NIAM Credentials.

## 3. Runtime model

### Task IDs and maps (`cr_process_automation/dashboard/views.py`)

| Constant | Value |
|---|---|
| `TASKS` | IDs 1–6 shown on CR Planning. |
| `NIAM_TASK_ID`, `NIAM_TASK` | 7, NIAM Ticket Generation. |
| `FETCH_CRS_TASK_ID`, `FETCH_CRS_TASK` | 8, Fetch CRs. |
| `RAISE_NIAM_TICKET_TASK_ID`, `RAISE_NIAM_TICKET_TASK` | 9, Raise NIAM Tickets. |
| `ALL_TASKS` | `TASKS + [NIAM_TASK, FETCH_CRS_TASK, RAISE_NIAM_TICKET_TASK]`. |
| `TASKS_REQUIRING_AUTH` / `task_runtime.TASK_REQUIRES_AUTH` | `{1, 2, 3, 4, 5}`. |
| `REGION_LOCK_TTL_SECONDS` | `120`. |
| `REGION_KEYS` | `("north", "west", "east", "south")`. |

`TASK_MODULE_MAP` maps task IDs to module paths verbatim:

| ID | `TASK_MODULE_MAP` value |
|---|---|
| 1 | `dashboard.task_modules.raw_report_to_template.tasks` |
| 2 | `dashboard.task_modules.cr_hygiene_checks.tasks` |
| 3 | `dashboard.task_modules.install_test_plan_downloads.tasks` |
| 4 | `dashboard.task_modules.bpms_cr_hygiene_checks.tasks` |
| 5 | `dashboard.task_modules.mop_attachment_approvals.tasks` |
| 6 | `dashboard.task_modules.final_email_package.tasks` |
| 7 | `dashboard.task_modules.niam_ticket_generation.tasks` |
| 8 | `dashboard.task_modules.niam_ticket_generation.tasks` |
| 9 | `dashboard.task_modules.niam_ticket_generation.niam_ticket_generation_tasks` |

### Runtime state

- `TASK_RUNTIME` is a process-global default per task (counts, status, download fields, auth fields, log seed). It is not per-user state.
- `task_runtime.make_runtime(task_id)` creates a fresh context: `task_id`, `run_key` (`uuid4().hex`), `status`, `download_ready`, `download_name`, `download_url`, `logs`, `run_dir`, `requires_auth`, `password`/`pwd_event`, `otp`/`otp_event`, notice/alert fields, and count fields.
- `task_runtime.RUN_REGISTRY` is a thread-safe `(user_id, task_id) -> runtime` map with `begin`, `peek`, `all_for_user`, `set`, `clear`, and `clear_all_for_user`.
- `_merge_runtime_for_request(user_id, task_id)` overlays the per-user context onto the legacy `TASK_RUNTIME` defaults. Users never see each other's status, logs, or auth prompts.
- `task_runtime.run_output_dir(run_key)` creates `settings.MEDIA_ROOT/task_runs/<run_key>`.
- `task_runtime.shared_input_paths(selected_date, regions)` records canonical `raw_report_file` and `planning_sheet` paths using `RAW_REPORT_DOWNLOAD_FOLDER`, `PLANNING_SHEET_DOWNLOAD_FOLDER`, and `PLANNING_SHEET_WORKBOOK_NAME`.

### `start_task()` flow

1. Validate integer `task_id`, resolve task via `_task_by_id()`, parse `date` (`%Y-%m-%d`) and `region` via `_parse_regions()`.
2. Tasks 1, 2, 7, 8, 9 require a date. Task 8 additionally calls `_validate_fetch_crs_date()` synchronously.
3. `_locked_by_others()` rejects regions held by another user.
4. Pre-import `TASK_MODULE_MAP[task_id]` and verify `run_task` exists.
5. `RUN_REGISTRY.begin(user_id, task_id)`; set `status = "Running"`, `_timing_start`, `run_dir`, `username`, `selected_date`, `regions`, `shared_inputs`, raw/planning paths, and NIAM template/output paths.
6. `AutomationTask.objects.get_or_create(sequence_no=task_id)` and `TaskRun.objects.create(...)` record ownership (`triggered_by`, `session_key`, `run_key`).
7. publish `region_status.RUNNING` for region tasks; log "task started" via `log_user()`.
8. Start daemon thread named `task-{task_id}-user-{user_id}-{run_key[:8]}` targeting nested `_runner()`.
9. Return JSON with `ok`, `task_id`, `run_key`, `message`, `status`, `requires_auth`, `otp_required`, `password_required`.

### `_runner()` flow

- Loads an isolated module copy via `task_runtime.load_fresh_module()` (module name `_cr_run_<uuid>`) and calls:
  `run_task(request, task, runtime, GLOBAL_LOGS=runtime["logs"], timestamp_fn=_timestamp, selected_date, user_email, user_name, regions)`.
- Interprets returned keys: `status`, `download_ready`, `download_name`, `message`, `counts`.
- Publishes final `region_status.COMPLETED`/`FAILED` markers for region tasks.
- For `REGION_TASK_IDS`, calls `region_paths.publish_region_output(...)`; otherwise calls `task_runtime.isolate_output(...)`.
- Sets `runtime["download_ready"]` only when the module says ready **and** a path exists; sets `download_url = "/download/task/<id>/"` when ready.
- On exception: sets `status = "Failed"`, logs message and traceback, publishes `FAILED`.
- In `finally`, updates `TaskRun.status` to `Successful`/`Unsuccessful`, stores the output basename in `output_file`, sets `completed_at`, closes the DB connection, clears auth/notice flags, and removes the `_cr_run_` module from `sys.modules`.

### Auth and logs

- Task modules set `runtime["otp_required"]` / `runtime["password_required"]` and wait on `otp_event` / `pwd_event`. Events are created once by `make_runtime()`; task modules no longer recreate them.
- `submit_otp()` and `submit_password()` require `run_key`, resolve the context with `RUN_REGISTRY.get(user_id, task_id, run_key)`, reject stale/missing states, then write the secret, clear the flag, set the event, and log receipt with `user_id`, `run_key` and `event_id`. The iframe views perform the same guarded update and render `iframe_success.html`.
- `start_task()` refuses a second start while the same `(user_id, task_id)` is in an active auth/running state, so a new thread cannot replace the runtime an old thread is waiting on.
- `UserLogList.append/extend/__iadd__/__add__` persists each line through `_persist_user_log()` as a `TaskLog` row linked to `runtime["task_run_id"]`.
- `log_user()` wraps older plain lists in `UserLogList` so later appends persist. `_user_logs()` filters by `run__triggered_by=request.user` and `run__session_key=request.session.session_key`.

### Dashboard payload

`task_dashboard_data()` returns:

```text
running_task, logs[{message, timestamp}], tasks[], user_name, user_role, user_email
```

Each `tasks[]` item includes:

```text
id, status, download_ready, download_name, download_url,
total_crs, north_crs, west_crs, east_crs, south_crs,
requires_auth, otp_required, password_required,
notice_required, notice_text, alert_required, alert_title, alert_text, alert_seq, run_key
```

For region tasks with `date` + `regions`, `download_ready` comes from `region_paths.all_region_files_ready()` and `status` from `region_status.combined_status()` rather than the viewing user's runtime flag. Ready region downloads get `?date=...&regions=...` appended to `download_url`.

### Downloads

`download_task_output()` allows two paths:

- Shared region artefacts: requires `date` and `regions` query parameters, task in `REGION_TASK_IDS`, and `all_region_files_ready()` for every selected region. Any logged-in user can download.
- Private/legacy `task_runs` copies: requires the requesting user's own `TaskRun` matching `triggered_by`, `session_key`, and `run_key`.

Resolved files must be under `settings.HOST_DOWNLOAD_FOLDER` or the user's private `MEDIA_ROOT/task_runs/<run_key>` directory.

## 4. Persistence

### Models (`cr_process_automation/dashboard/models.py`)

| Model | Role |
|---|---|
| `CoWModel` | Abstract copy-on-write base: `is_active`, `version`, `parent_reference`; `save()` pins reads/writes to `default` and wraps updates in `transaction.atomic(using="default")`. |
| `AutomationTask` | Unique `sequence_no`, display `name`, flags, status, active flag. Tasks 7–9 may be created on demand by `start_task()`. |
| `TaskRun` | Per-run ownership: `task`, `triggered_by`, `session_key`, `run_key`, `status`, `output_file`, `started_at`, `completed_at`, `message`. |
| `TaskLog` | Log lines linked to `TaskRun` via `run`; filtered per user/session for the UI. |
| `MasterCRDatabase` | CoW master CR rows. `save()` has an override; `_after_cow_save()` is a no-op. |
| `SelectedDateTable` | CoW selected-night CR rows. `_after_cow_save()` calls `_sync_to_master_cr_database()`. |
| `CRWiseStatus` | Status flags keyed by `cr_no`; custom CoW `save()` with a unique active-row constraint. |
| `FlagTable` | Simple `source_id`/`status`/`version` table. |
| `UserManagement` | `AbstractUser` subclass; `AUTH_USER_MODEL`. Adds role/employee/NIAM credential fields. |
| `NIAMTicketGenerationTable` | One row per CR per NIAM node; 24 displayed columns plus internal `execution_date`. |
| `NiamDomainsTable`, `NIAMCircleTable`, `NIAMProjectNameTable`, `NIAMRequestForTable`, `NIAMAccessTypeTable`, `NIAMActivityNameTable` | Admin-editable lookup data for NIAM dropdowns. |
| `RegionLock` | Unique `region`, `locked_by`, `session_key`, `locked_at`, `expires_at`; `is_expired()`. |

### Copy-on-write behavior

- `CoWModel.save()` locks the existing row with `select_for_update()`, deactivates it, sets `parent_reference_id` to the old PK, increments `version`, clears `pk`, and inserts a new active row.
- New/stale PKs are inserted as active `version=1`. `skip_cow=True` bypasses this path.
- `SelectedDateTable.save()` mirrors CoW and calls `_sync_to_master_cr_database()`, which locks active `MasterCRDatabase` rows for the same `cr_no`, deactivates them, and inserts a new active version.
- `CRWiseStatus.save()` implements the same versioning locally and is constrained to one active row per `cr_no`.

### Routing and sync

- `CoWRouter.db_for_read()` sends `auth`, `sessions`, `contenttypes`, `admin`, and `usermanagement` to `default`; all other models route to `replica`.
- `db_for_write()` always returns `default`; `allow_migrate()` only allows `default`.
- CoW saves explicitly use `.using("default")`, bypassing replica reads during version creation.
- `dashboard/signals.py` triggers `async_sync_master_to_replica()` after `MasterCRDatabase` and `CRWiseStatus` writes.
- `utils/replica_sync.py` still uses `sqlite3` paths (`db.master.sqlite3`, `db.replica.sqlite3`); verify it against the active PostgreSQL setup before relying on it.
- `DashboardConfig.ready()` registers `connection_created`; `_seed_niam_reference_tables()` seeds NIAM lookup tables lazily on the first `default` connection under `_SEED_LOCK`.

### Filesystem outputs

- Shared artefacts: `settings.HOST_DOWNLOAD_FOLDER/{date}/{task folder}/{region}/`.
- Private copies: `settings.MEDIA_ROOT/task_runs/<run_key>/`.
- NIAM sessions: `settings.MEDIA_ROOT/niam_sessions/niam_session_<run_key>.json`.
- Status markers: `settings.HOST_DOWNLOAD_FOLDER/.task_status/<task_id>/<date>/<region>.json`.
- Logs: `<HOST_DOWNLOAD_DIR>/logs/errors.log` and `notice_timing.log`.

## 5. Region subsystem

### Keys and paths

- Keys: `north`, `west`, `east`, `south`; default when absent: `all`.
- `region_paths.REGION_TASK_IDS = (1, 2, 3, 4, 5, 9)`; task 6 is deliberately excluded.
- `region_paths.task_date_label()` uses `%d_%b_%Y` for tasks 7/8/9 and `%d-%b-%y` for the others.
- `region_paths.TASK_FOLDER_ENV`:

| Task | Env template |
|---|---|
| 1 | `RAW_REPORT_DOWNLOAD_FOLDER` |
| 2 | `CR_HYGIENE_CHECKS_FILE` |
| 3 | `PLAN_FILES_ZIP_FILE` |
| 4 | `BPMS_CR_HYGIENE_CHECKS_FILE` |
| 5 | `MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE` |

- `format_env_path(env_name, date_label, region, **extra)` formats `{date}` and `{region}` placeholders; task 3 also passes `label`.

### Readiness and status

- `all_region_files_ready(task_id, date, regions)` returns true only when the expected artefact exists for **every** selected region.
- `publish_region_output(task_id, date, regions, source)` copies the completed artefact to every selected region folder and returns the primary (first) path.
- `region_status.publish()` writes `{"status": "<value>"}` JSON per region. Values are `Running`, `Completed`, `Failed`.
- `region_status.combined_status()` returns `Failed` if any marker failed, `Completed` if all markers are completed, falls back to `Completed` when all artefacts exist (legacy compatibility), otherwise `Pending`.

### Locks

- `_parse_regions()` normalizes list/comma input to known keys.
- `_purge_expired_region_locks()` deletes rows with `expires_at <= now`.
- `_acquire_single_region_lock()` uses `transaction.atomic(using="default")`, `select_for_update()`, and an `IntegrityError` savepoint retry to handle concurrent inserts; the owner refreshes `expires_at` and `session_key`.
- `acquire_region_locks()` returns `ok`, `acquired`, `conflicts`, `locks`, `ttl`.
- `release_region_locks()` releases all user locks or a subset.
- `region_lock_status()` returns `ok`, `locks`, `ttl`.
- `logout_view()` deletes the user's `RegionLock` rows. Idle timeout only clears runtimes/logs out, so locks then expire by TTL.

## 6. Task modules

Every implementation exposes:

```text
run_task(request, task, runtime, GLOBAL_LOGS=None, timestamp_fn=None,
         selected_date=None, user_email=None, user_name=None, regions=None)
```

It returns a dict with `status`, `message`, `download_ready`, usually `download_name`, and optional `counts`. Auth-requiring modules set/clear OTP and password fields on `runtime`.

| ID | Module | Backend behavior / returned artefact |
|---|---|---|
| 1 | `dashboard.task_modules.raw_report_to_template.tasks` | ITSM auth; reads shared raw report and planning sheet; syncs regional SQLite DBs; returns `report_file`. |
| 2 | `dashboard.task_modules.cr_hygiene_checks.tasks` | ITSM auth; runs hygiene checks; writes `CR_HYGIENE_CHECKS_FILE`; returns `counts: {}`. |
| 3 | `dashboard.task_modules.install_test_plan_downloads.tasks` | ITSM auth; filters planned CRs; writes `PLAN_FILES_ZIP_FILE` with `label`; returns `counts: {}`. |
| 4 | `dashboard.task_modules.bpms_cr_hygiene_checks.tasks` | ITSM auth; BPMS CR hygiene checks; writes `BPMS_CR_HYGIENE_CHECKS_FILE`; returns `counts: {}`. |
| 5 | `dashboard.task_modules.mop_attachment_approvals.tasks` | ITSM auth; MOP attachment/approval validation; writes `MOP_ATTACHMENT_CR_APPROVAL_VALIDATION_FILE`; returns `counts: {}`. |
| 6 | `dashboard.task_modules.final_email_package.tasks` | Declared in `TASKS`/`TASK_MODULE_MAP` but absent from the repository; `start_task()` fails at import. |
| 7 | `dashboard.task_modules.niam_ticket_generation.tasks` | Strict NIAM input generation; upserts `NIAMTicketGenerationTable`, writes RITM Input workbook. |
| 8 | `dashboard.task_modules.niam_ticket_generation.tasks` | Fetch CRs for night; rebuilds scoped `SelectedDateTable`; adds eligible NIAM rows; writes RITM Input workbook. |
| 9 | `dashboard.task_modules.niam_ticket_generation.niam_ticket_generation_tasks` | Playwright NIAM ticket raising; updates statuses/failure reasons; writes RITM Output workbook. |

Notes for maintainers:

- Task modules still declare module-level globals (`glogs`, queues, dictionaries). Isolation depends on `load_fresh_module()` and the per-run cleanup in `_runner()`.
- Only `REGION_TASK_IDS` artefacts are fanned out to all selected region folders; other outputs use the private `task_runs` copy.
- Task status strings consumed by the UI include `Running`, `Completed`, `Failed`, `Waiting for OTP`, `Waiting for Password`, and `Waiting for Sign-in Approval`.

## 7. NIAM subsystem

### Date convention

The picker value is the **night** date `D`; CRs execute on `D + 1`. This is enforced in `_validate_fetch_crs_date()`, `fetch_crs_for_date()`, `_niam_period_query()`, `generate_niam_input()`, and the note in `templates/dashboard/niam_template_db.html`. `_niam_period_query()` matches `sr_cr_start_date_time__date` in the `D+1` range and falls back to `execution_date` when the start datetime is null.

### Paths

`utils/niam_paths.py` uses folder `NIAM_Excel_files` and date `%d_%b_%Y`:

```text
{HOST_DOWNLOAD_FOLDER}/{night}/NIAM_Excel_files/{region}/RITM Input_PS_Core_{night}.xlsx
{HOST_DOWNLOAD_FOLDER}/{night}/NIAM_Excel_files/{region}/RITM Output_PS_Core_{night}.xlsx
```

Functions: `niam_region_root()`, `niam_template_path_for()`, `niam_output_path_for()`, `niam_date_folder()`.

### Fetch and generation

- `fetch_crs_for_date()` reuses existing NIAM rows when present; otherwise rebuilds only that execution date's `SelectedDateTable` from active `MasterCRDatabase` rows in `transaction.atomic(using="default")`, deliberately excluding master `id` values.
- `generate_niam_input()` source priority: existing `NIAMTicketGenerationTable` rows (edits authoritative) → `SelectedDateTable` → `MasterCRDatabase`.
- `include_all_crs=True` (task 8) considers CRs flagged `NIAM Ticket Required = Yes`, keeps existing rows, and adds placeholders for missing rows. Strict generation (task 7) requires planned + Yes + node details and removes replaced blank-node placeholders.
- Workbook writes are serialized with `file_lock(niam_workbook_path_for(date))`.
- Task 9 uses `NIAM_SESSION_FILE` (`MEDIA_ROOT/niam_sessions/niam_session_<run_key>.json`), retries NIAM login, sets notice/alert runtime flags, and returns `RITM Output_PS_Core_<night>.xlsx` when available.

### Column/edit contract

Defined in `task_modules/dependencies/extra_dependencies.py`:

| Symbol | Meaning |
|---|---|
| `NIAM_COLUMN_TO_FIELD_MAPPING` | 24 RITM column labels → `NIAMTicketGenerationTable` fields. |
| `NIAM_FIELD_TO_COLUMN` | Reverse mapping used by workbook write-back. |
| `NIAM_DATETIME_FIELDS` | Four `DateTimeField`s rendered as naive Asia/Kolkata wall-clock strings. |
| `NIAM_UPSERT_KEY_FIELDS` | `("execution_date", "sr_or_change_number", "node_name")`. |
| `NIAM_EDITABLE_FIELDS` | `request_ip`, `requested_for_email`, `activity_name`, `project_name`, `request_for`, `domain`, `access_type`. |
| `NIAM_DROPDOWN_SOURCES`, `NIAM_STATIC_DROPDOWN_OPTIONS` | Allowed values from lookup tables plus fixed `request_ip` options. |
| `niam_dropdown_options()`, `_niam_key()`, `renumber_niam_sno()` | Options payload, normalized match key, and S.No compaction after splits/merges. |

### NIAM endpoints in detail

- `fetch_niam_template_data()`: GET `date` or `range` (`1w`/`1m`/`1y` from `NIAM_RANGE_DAYS`); limit `1000`. Returns `ok`, `columns`, `column_labels`, `editable_columns`, `options`, `can_edit`, `rows`, `count`, `range`, `period_label`, `from_date`, `to_date`.
- `download_niam_template()`: same period inputs; limit `5000`; builds an in-memory `NIAM_Template` sheet and names it `NIAM_Template_<date>.xlsx` or `NIAM_Template_<label>_<from>_<to>.xlsx`.
- `start_niam_fetch_crs()`: validates POST `date`, returns errors via `handle_exceptions`, then calls `start_task(FETCH_CRS_TASK_ID)`.
- `start_niam_ticket_generation()`: validates POST `date`, requires NIAM rows for the night, then calls `start_task(RAISE_NIAM_TICKET_TASK_ID)`.
- `save_niam_template_changes()`: requires `_user_can_edit_region_crs()` (roles `Admin`, `Validator`, `Night-SPOC`), validates editable values, saves in `transaction.atomic(using="default")`, handles `ADMIN AND READWRITE` split/merge, calls `renumber_niam_sno(..., compact=True)`, then writes edited values to `RITM_INPUT` via `_write_niam_edits_to_workbook()`. Rows are matched on `(_niam_key("SR OR CHANGE NO"), _niam_key("NIAM Node Name"))`. Workbook failures return `warning` but do not roll back the DB save.
- `update_niam_credentials()`: JSON body `{niam_olm_id, niam_password, confirm_niam_password}`; updates only `request.user` after `NiamCredentialsForm` validation.

## 8. Concurrency and isolation

| Concern | Mechanism in this project |
|---|---|
| Per-user run state | `RUN_REGISTRY` keyed by `(user_id, task_id)`; private logs, OTP/password events, status, and run key. Auth submissions are routed by exact `run_key`. |
| Per-user module globals | `load_fresh_module()` re-executes task modules as `_cr_run_<uuid>`; removed from `sys.modules` in `finally`. |
| User identity on persisted data | `TaskRun.triggered_by` + `session_key` + `run_key`; `_user_logs()` and download ownership queries use them. |
| Shared workbook/file writes | `utils/file_locks.file_lock(path, timeout=300.0, poll=0.1)` uses `<path>.lock`, a per-path `threading.Lock`, and OS advisory locking (`msvcrt` on Windows, `fcntl` on POSIX). Used by tasks 1, 2, 4, and 7/8. |
| Shared artefacts by region | `publish_region_output()` copies final artefacts into every selected region folder. |
| Region selection conflicts | DB-backed `RegionLock` with TTL, heartbeat, `select_for_update()`, and `IntegrityError` race handling. |
| DB consistency | `transaction.atomic(using="default")` in CoW saves, NIAM save, region lock acquisition, and scoped selected-date rebuild. |
| NIAM browser sessions | One storage file per `run_key`; credentials stored per Django user. |
| ITSM browser sessions | `get_itsm_session_file_path(runtime)` writes `itsm_session_<run_key>.json`; `session_breaker(runtime=...)` logs out/deletes only that file. Threads inherit the same per-run path. |
| ITSM MFA | All three Microsoft prompts try verification-code entry; push approval shows the sign-in code and detects rejection/timeout. Visible prompts are selected per variant so hidden Microsoft templates cannot stall one run. OTP is requested only when `#idTxtBx_SAOTCC_OTC` is visible. The notice is cleared only on a real approval signal (ServiceNow app list, "Stay signed in?", or leaving the Microsoft login domain with no MFA prompt), never on a transient hidden template. |
| Idle sessions | `SessionIdleTimeoutMiddleware` logs out after `USER_IDLE_TIMEOUT_SECONDS` and excludes polling URLs in `NON_ACTIVITY_PATHS`. |
| Process model | One WSGI process with many threads is required; multiple worker processes split `RUN_REGISTRY`. `wsgi_app.py` now forces `WSGI_WORKERS=1` when a larger value is configured. |

## 9. Frontend integration contract

| Client file | Contract |
|---|---|
| `static/dashboard/js/dashboard.js` | Polls `/api/task/dashboard-data/` every `500` ms (comment says 3 s). On CR Planning, sends `cr_planning=1`, `date`, and comma-separated `regions`. Starts tasks via POST `/api/task/start/<id>/` with `FormData` `date`/`region` and `X-CSRFToken`. Shows download when `download_ready`; uses `download_url` verbatim. Opens `/playwright-*-iframe/?task_id=<id>&run_key=<run_key>` for password/OTP/notice/alert and keeps the iframe bound to that exact run. |
| Alert dedupe | Key is `${task.id}:${task.run_key || ''}:${task.alert_seq || 0}`; a modal is reopened only for a new run/sequence. |
| `static/dashboard/js/region_locks.js` | `REGION_KEYS` north/west/east/south; polls `/api/region-locks/status/` every `3000` ms; posts `regions` to acquire/release; reacquires selected regions on each heartbeat; releases via `navigator.sendBeacon` on unload/pagehide. |
| `static/dashboard/js/night_execution.js` | Polls `/night-execution/status-result/` every `2000` ms for up to `150` attempts; uses `job_id` for password/OTP iframes. |
| `templates/dashboard/niam_template_db.html` | `FETCH_NIAM_URL`, `DOWNLOAD_NIAM_URL`, `SAVE_NIAM_URL`, `CAN_EDIT_NIAM`. Fetches rows with `date` or `range`; posts `api/niam/fetch-crs/` and starts task 8, polling `/api/task/dashboard-data/` every `3000` ms until task 8 completes; save posts JSON `{date, rows}`; generator starts task 9 and polls until `download_ready`. |
| CSRF | Browser reads `csrftoken` cookie and sends `X-CSRFToken`; JSON endpoints also set `Content-Type: application/json`. |
| Response handling | JSON errors use `{ok:false,title,message,status_code}`; successful task starts return `ok/task_id/run_key/message/status/requires_auth/otp_required/password_required`. |

## 10. Deployment/config

### Settings and env

`cr_process_automation/cr_process_automation/settings.py` loads `cr_process_automation/dashboard/.env`, then process env. Relevant names (values omitted):

| Group | Names |
|---|---|
| Django | `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_BEHIND_PROXY`, `DJANGO_SECURE_COOKIES`. |
| Paths | `DJANGO_DOWNLOAD_DIR` → `HOST_DOWNLOAD_DIR` / `HOST_DOWNLOAD_FOLDER`; `MEDIA_ROOT = <HOST_DOWNLOAD_DIR>/media`; `STATIC_ROOT = <BASE_DIR>/staticfiles`. |
| Sessions | `USER_IDLE_TIMEOUT_SECONDS` feeds `SESSION_COOKIE_AGE` and `USER_IDLE_TIMEOUT_SECONDS`. |
| Databases | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`; replica equivalents `DB_NAME_REPLICA`, `DB_USER_REPLICA`, `DB_PASSWORD_REPLICA`, `DB_HOST_REPLICA`, `DB_PORT_REPLICA`. |
| WSGI launcher | `WSGI_HOST`, `WSGI_PORT`, `WSGI_WORKERS`, `WSGI_THREADS`, `WSGI_TIMEOUT`, `WSGI_SERVER`, `WSGI_RUN_MIGRATE`, `WSGI_RUN_COLLECTSTATIC`, `WSGI_LOG_LEVEL`. |

Other settings: `AUTH_USER_MODEL = "dashboard.UserManagement"`, DB-backed sessions, `USE_TZ=True`, `TIME_ZONE='Asia/Kolkata'`, `X_FRAME_OPTIONS='SAMEORIGIN'`, WhiteNoise static storage when installed, and `dashboard`/`dashboard.notice` loggers.

### Launch paths

- `wsgi_app.py`: auto-selects Gunicorn `gthread` on Linux/macOS and Waitress on Windows; optional `--migrate`/`--collectstatic`; default bind `0.0.0.0:9000`; `WSGI_WORKERS` defaults to `1`.
- `start.sh`: prefers `.venv/bin/python` or `venv/bin/python`, runs `wsgi_app.py --migrate --collectstatic`, wraps in `xvfb-run -a` when `DISPLAY` is unset and Xvfb exists (`NO_XVFB=1` disables).
- `start.bat`: same launcher on Windows via Waitress.
- `compose.yaml`: app service mapping `9000:9000`.
- `cr_process_automation/docker-compose.yml`: local PostgreSQL master (`5432`) and replica (`5433`) services; configure credentials externally for non-local use.
- `deploy/nginx.conf`: sample proxy to `127.0.0.1:8000`, static/media aliases, CSRF/proxy headers, `600s` proxy timeouts, optional TLS block. Set `DJANGO_BEHIND_PROXY`, `DJANGO_SECURE_COOKIES`, `DJANGO_CSRF_TRUSTED_ORIGINS`, and `DJANGO_ALLOWED_HOSTS` when behind TLS/proxy.
- `requirements.txt`: Django, psycopg2-binary, pandas/openpyxl, Playwright, WhiteNoise, Waitress, and Gunicorn on non-Windows. Run `playwright install chromium` during provisioning.
- `scripts/watch_niam_timing.sh` / `.ps1`: tail `notice_timing.log` and `errors.log` with optional journal/server output capture.

**Deployment rule:** keep `WSGI_WORKERS=1`; the launcher forces it to one worker and logs a warning if a larger value is set. Scale with threads only until in-memory state is moved to a shared store.

## 11. Known limitations / TODOs

| Area | Limitation |
|---|---|
| Task 6 | `final_email_package.tasks` does not exist; starting task 6 fails before thread start. |
| NIAM region metadata | `NIAMTicketGenerationTable` has no `region` field, although `save_niam_template_changes()` reads `obj.region`; workbook write-back therefore targets `all` unless a region is supplied elsewhere. |
| NIAM fan-out | Only task 9 (`RITM Output`) is in `REGION_TASK_IDS`; task 7/8 input workbooks are not fanned out by `publish_region_output()`. |
| Replica sync | `check_replica_sync_status()` always returns `complete`/`ready`; `utils/replica_sync.py` is still SQLite-oriented while settings use PostgreSQL. |
| Process-local state | `RUN_REGISTRY` and fresh module objects do not survive worker restarts; daemon threads are not resumed. Multiple WSGI workers break polling and iframe submission. |
| Idle locks | Idle timeout clears run contexts but does not delete `RegionLock` rows; expiry relies on TTL/heartbeat lapse. |
| Status markers | Stale `.task_status` markers and the legacy `all_region_files_ready()` fallback can make a badge show `Completed` after older runs. |
| Frontend timing | `dashboard.js` comment says a 3-second poll but the code uses `500` ms; NIAM task polling uses `3000` ms. |
| Task 7 UI | NIAM task 7 is startable via the generic `/api/task/start/7/` route but has no dedicated button on the NIAM page (the page starts tasks 8 and 9). |
| NIAM edit validation | `NIAM_EDITABLE_FIELDS` comment says all seven must be filled, but `save_niam_template_changes()` accepts blank values. |
| Dockerfile | `Dockerfile` `CMD` uses Windows-style backslashes inside a Linux container; verify or replace for container deployments. |
| Port mismatch | README/nginx examples use `8000`; `wsgi_app.py` defaults to `9000`. Pass `--port` explicitly. |
| Disabled module | `vendor_dashboard` routes are commented out in `cr_process_automation/dashboard/urls.py`. |
