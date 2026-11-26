# CR Process Automation — Project Documentation

This is the consolidated project reference. It describes **this repository only**:
its files, features, user-facing tabs, exceptions, runtime/data flow, deployment
inputs, and known limitations. Django concepts are abstracted where the project's
own behaviour is what matters.

Related documents:

| Document | Use it for |
| --- | --- |
| [`PROJECT_DOCUMENTATION.md`](PROJECT_DOCUMENTATION.md) | This consolidated module/file/feature map. |
| [`TEAM_HANDOVER.md`](TEAM_HANDOVER.md) | Day-to-day operations, region locks, NIAM MFA, troubleshooting. |
| [`TECHNICAL_BACKEND.md`](TECHNICAL_BACKEND.md) | Backend internals: endpoints, runtime isolation, models, routing, concurrency. |

## 1. Scope and source of truth

- Application code: `cr_process_automation/dashboard/`.
- Project configuration: `cr_process_automation/cr_process_automation/`.
- Browser automation implementations: `cr_process_automation/dashboard/task_modules/`.
- Frontend: `cr_process_automation/dashboard/templates/` and `static/dashboard/`.
- Operational entry points: `wsgi_app.py`, `start.sh`, `start.bat`, `db_start.py`,
  `scripts/`, `deploy/`.
- Routes are registered in `cr_process_automation/dashboard/urls.py` and mounted at
  `/` by `cr_process_automation/cr_process_automation/urls.py`.

## 2. Feature catalogue

### 2.1 User-facing tabs and pages

| Route | View function | Template | Purpose |
|---|---|---|---|
| `/`, `/login/` | `views.login_view` | `dashboard/login.html` | Login landing and form handling. |
| `/logout/` | `views.logout_view` | redirect to login | Logs out, clears that user's runtime state and releases their `RegionLock` rows. |
| `/health`, `/health/` | `views.health_check` | JSON | Unauthenticated liveness/DB probe. |
| `/home/` | `views.cr_planning_view` | `dashboard/home.html` | **CR Planning**: select night date and regions, run tasks 1–5, view logs/status, download shared artefacts. |
| `/dashboard/` | `views.dashboard_view` | `dashboard/dashboard.html` | **Dashboard**: landing page linking to the four analysis pages. |
| `/night-spoc/` | `views.night_spoc_view` | `dashboard/night_spoc.html` | **Night-SPOC** page. |
| `/region-crs/` | `Region_views.region_crs_view` | `dashboard/region_crs.html` | **Region CRs**: view/edit CR rows by execution date and region. |
| `/cr_history/` | `Region_views.cr_history_view` | `dashboard/cr_history.html` | **CR History**: date/range filtering and export. |
| `/cr_wise_status/` | `CR_Wise_Status_views.cr_wise_status` | `dashboard/cr_wise_status.html` | **CR-Wise Status**: hygiene/download/MOP/approval status table. |
| `/night-execution/` | `NightExecution_views.night_execution` | `dashboard/night_execution.html` | **Night Execution**: fetch and act on CRs assigned to the logged-in executor. |
| `/vendor-wise-analysis/` | `views.vendor_wise_analysis_view` | `dashboard/vendor_wise_analysis.html` | **Vendor-Wise Analysis** page. |
| `/cr-success-rate-analysis/` | `views.cr_success_rate_analysis_view` | `dashboard/cr_success_rate_analysis.html` | **CR Success Rate Analysis** page. |
| `/team-performance-analysis/` | `views.team_performance_analysis_view` | `dashboard/team_performance_analysis.html` | **Team Performance Analysis** page. |
| `/automation-cr-analysis/` | `views.automation_cr_analysis_view` | `dashboard/automation_cr_analysis.html` | **Automation CR Analysis** page. |
| `/niam-template-db/` | `views.niam_template_db_view` | `dashboard/niam_template_db.html` | **NIAM Template Database**: fetch, view/edit, save, download, and raise tickets. |
| `/niam-credentials/` | `views.niam_credentials_view` | `dashboard/niam_credentials.html` | **NIAM Credentials**: self-service OLM ID/password update. |

### 2.2 APIs, downloads, auth dialogs and iframes

| Route | View function | Purpose |
|---|---|---|
| `POST /api/task/start/<int:task_id>/` | `views.start_task` | Validates date/regions/locks and starts an isolated background run. |
| `GET /api/task/dashboard-data/` | `views.task_dashboard_data` | Polls status, logs, auth flags, shared region status, readiness and download links. |
| `POST /api/task/submit-otp/<int:task_id>/` | `views.submit_otp` | Supplies OTP to an active run; requires matching `run_key`. |
| `POST /api/task/submit-password/<int:task_id>/` | `views.submit_password` | Supplies password to an active run; requires matching `run_key`. |
| `GET /download/task/<int:task_id>/` | `views.download_task_output` | Streams an authorised shared region artefact or private run copy. |
| `POST /api/region-locks/acquire/` | `views.acquire_region_locks` | Acquires/renews DB-backed region locks. |
| `POST /api/region-locks/release/` | `views.release_region_locks` | Releases the current user's locks. |
| `GET /api/region-locks/status/` | `views.region_lock_status` | Returns lock state for frontend polling. |
| `GET /filter-region-crs/` | `views.filter_region_crs` | Returns CR counts/rows for a night date and selected regions. |
| `GET /region-crs/fetch-region-cr-details/`, `/cr_history/fetch-region-cr-details/` | `Region_views.fetch_region_cr_details` | Fetches editable region CR rows. |
| `POST /region-crs/save-region-cr-details` | `Region_views.save_region_cr_details` | Saves edited region CR rows with CoW handling. |
| `GET /fetch-cr-history/` | `Region_views.fetch_cr_history` | Fetches CR history rows. |
| `GET /download-cr-history/` | `Region_views.download_cr_history` | Exports CR history. |
| `GET /playwright-auth-iframe/` | `views.playwright_auth_iframe` | OTP input iframe; bound to `task_id` + `run_key`. |
| `GET /playwright-password-iframe/` | `views.playwright_password_iframe` | Password input iframe; bound to `task_id` + `run_key`. |
| `GET /playwright-notice-iframe/` | `views.playwright_notice_iframe` | Read-only Authenticator sign-in code/notice iframe; bound to `task_id` + `run_key`. |
| `GET /playwright-alert-iframe/` | `views.playwright_alert_iframe` | Blocking alert iframe for missing/rejected credentials; bound to `task_id` + `run_key`. |
| `GET /fetch-cr-wise-status/` | `CR_Wise_Status_views.fetch_cr_wise_status` | Fetches CR-wise status rows. |
| `GET /fetch-user-options/` | `views.fetch_user_options` | Active employee options. |
| `GET /api/replica-sync-status/<str:sync_id>/` | `views.check_replica_sync_status` | Placeholder sync poll. |
| `GET /night-execution/fetch-crs/` | `NightExecution_views.fetch_night_execution_crs` | Fetches executor CRs. |
| `GET /night-execution/fetch-cr-status/` | `NightExecution_views.fetch_night_cr_status` | Starts/fetches night CR status execution. |
| `POST /night-execution/start-task/` | `NightExecution_views.start_night_execution_task` | Placeholder night task starter. |
| `GET /night-execution/status-result/` | `NightExecution_views.night_cr_status_result` | Polls night status job result. |
| `POST /night-execution/submit-password/`, `/submit-otp/` | `submit_night_password`, `submit_night_otp` | Night-execution auth input. |
| `GET /night-execution/password-iframe/`, `/otp-iframe/` | `night_password_iframe`, `night_otp_iframe` | Night-execution auth iframes. |
| `GET /fetch-vendor-wise-analysis/` | `views.fetch_vendor_wise_analysis` | Vendor-wise analysis data. |
| `GET /fetch-cr-success-rate-analysis/` | `views.fetch_cr_success_rate_analysis` | CR success-rate data. |
| `GET /fetch-team-performance-analysis/` | `views.fetch_team_performance_analysis` | Team performance data. |
| `GET /fetch-automation-cr-analysis/` | `views.fetch_automation_cr_analysis` | Automation CR analysis data. |
| `GET /fetch-niam-template-data/` | `views.fetch_niam_template_data` | NIAM rows, columns, options and edit permission. |
| `GET /download-niam-template/` | `views.download_niam_template` | Exports `NIAM_Template*.xlsx`. |
| `POST /api/niam/fetch-crs/` | `views.start_niam_fetch_crs` | Starts task 8 after date validation. |
| `POST /api/niam/generate-ticket/` | `views.start_niam_ticket_generation` | Starts task 9 after NIAM row checks. |
| `POST /api/niam/save-changes/` | `views.save_niam_template_changes` | Saves editable NIAM fields to DB and workbook. |
| `POST /api/user/update-niam-credentials/` | `views.update_niam_credentials` | Updates the current user's NIAM credentials. |

### 2.3 Task catalogue

| ID | Exact name | Started from | Auth group | Artefact/result |
|---|---|---|---|---|
| 1 | RAW Report to Template | CR Planning | ITSM | Shared raw report and planning sheet per night/region. |
| 2 | CR Hygiene Checks | CR Planning | ITSM | `CR_Hygiene_Checks.xlsx` per night/region. |
| 3 | Install/Test Plan Downloads | CR Planning | ITSM | `Plan_Files_Download_<label>.zip` per night/region. |
| 4 | BPMS CR Hygiene Checks | CR Planning | ITSM | `BPMS_CR_Hygiene_Checks.xlsx` per night/region. |
| 5 | MOP Attachment & Approvals | CR Planning | ITSM | `MOP_Attachment_Approval_status.xlsx` per night/region. |
| 6 | Final Email Package | CR Planning table only | — | Declared but module is absent; starting it fails at import. |
| 7 | NIAM Ticket Generation | generic task API | NIAM | Strict NIAM input generation. |
| 8 | Fetch CRs | NIAM Template Database | NIAM | Rebuilds selected-date rows, adds eligible NIAM rows. |
| 9 | Raise NIAM Tickets | NIAM Template Database | NIAM | Writes `RITM Output_PS_Core_<night>.xlsx`. |

`TASKS_REQUIRING_AUTH = {1, 2, 3, 4, 5}`. `REGION_TASK_IDS = (1, 2, 3, 4, 5, 9)`.

### 2.4 Cross-cutting behaviour

- **Auth/session:** `UserManagement` is the auth model; DB-backed sessions;
  `SessionIdleTimeoutMiddleware` expires real inactivity and clears the user's
  in-memory runs. Polling endpoints do not extend the idle clock.
- **Copy-on-write data:** CR rows are versioned by `CoWModel`/custom `save()`
  overrides and written to `default`; reads normally use `replica`.
- **Task execution:** each start creates a per-user runtime via `RUN_REGISTRY`,
  a `TaskRun`, a background thread, a fresh copy of the task module, and persisted
  `TaskLog` rows.
- **Region locks:** `RegionLock` with a 120-second TTL and heartbeat prevents two
  users running the same region.
- **Region outputs:** shared artefacts live at
  `settings.HOST_DOWNLOAD_FOLDER/{date}/{Task-Wise folder}/{Region-name}/`.
  A download button appears only when the artefact exists for **all** selected
  regions, independent of status. Shared artefacts can be downloaded by any
  logged-in user.
- **Shared status:** `.task_status/<task>/<date>/<region>.json` markers are reduced
  with AND: Completed only if all selected regions are Completed, Failed if any
  is Failed, otherwise Pending. Older artefacts without markers fall back to
  Completed when present for every region.
- **NIAM:** per-user credentials, per-run browser session files, Microsoft MFA
  variants, iframe prompts/alerts, and output-only workbook for task 9.
- **Error contract:** custom exceptions become
  `{"ok": false, "title": ..., "message": ..., "status_code": ...}`.

## 3. Core module/file map

| File | Abstract responsibility | Key symbols/features | Notes |
|---|---|---|---|
| `cr_process_automation/dashboard/views.py` | HTTP layer for pages, JSON APIs, task orchestration, region locks, NIAM workflows, downloads and auth iframes. | `TASKS`, `ALL_TASKS`, `TASK_MODULE_MAP`, `RUN_REGISTRY`, `login_view`, `logout_view`, `health_check`, `cr_planning_view`, `dashboard_view`, `night_spoc_view`, `start_task`, `submit_otp`, `submit_password`, `task_dashboard_data`, `download_task_output`, lock APIs, analysis APIs, NIAM APIs, iframe views. | Largest core file. `fetch_current_date_crs` and `update_hygiene_check` have no active URL entry. |
| `cr_process_automation/dashboard/urls.py` | Active URLconf for dashboard pages/APIs. | `urlpatterns` for all routes in §2. | Commented-out entries include vendor dashboard, import-master-cr, task upload, duplicate night-execution route. |
| `cr_process_automation/dashboard/models.py` | ORM schema, CoW versioning, custom user, task runs/logs, NIAM lookup/template tables. | `CoWModel`, `MasterCRDatabase`, `SelectedDateTable`, `UserManagement`, `CRWiseStatus`, `FlagTable`, `AutomationTask`, `TaskRun`, `TaskLog`, `RegionLock`, `NIAMTicketGenerationTable`, lookup models. | Unique active-row constraints exist for CR status models. |
| `cr_process_automation/dashboard/forms.py` | Form validation for login, interactive auth and NIAM credentials. | `LoginForm`, `TwoFactorAuthForm`, `PasswordAuthForm`, `NiamCredentialsForm`. | NIAM form enforces OLM-ID pattern, password complexity and confirmation. |
| `cr_process_automation/dashboard/middleware.py` | Exception-to-JSON conversion and real inactivity expiry. | `CustomExceptionMiddleware.process_exception`, `SessionIdleTimeoutMiddleware`, `NON_ACTIVITY_PATHS`. | On expiry, clears runs then logs out. |
| `cr_process_automation/dashboard/services.py` | Reusable CR data services with locking and custom exceptions. | `update_cr_flag_atomic`, `update_cr_flags_batch`, `sync_selected_date_to_master`, `get_active_cr`, `get_cr_history`, `bulk_update_activity_status`, `validate_cr_exists`, `get_crs_by_region`, `get_crs_by_planning_status`, `get_cr_count_by_region`, `revert_cr_to_version`. | Uses `transaction.atomic(using="default")` and `select_for_update()`. |
| `cr_process_automation/dashboard/exceptions.py` | Application exception hierarchy and JSON error payload. | `CustomException` and subclasses; `to_dict()`. | Shared by views, services and exception handler. |
| `cr_process_automation/dashboard/apps.py` | Startup config; registers signals and lazy NIAM seeding. | `DashboardConfig.ready`, `_SEED_LOCK`, `_seed_niam_reference_tables`. | Seed failures are logged, not fatal. |
| `cr_process_automation/dashboard/signals.py` | Replica sync after master CR writes. | `on_master_cr_save`, `on_master_cr_delete`, `on_cr_status_save`, `on_cr_status_delete`, `async_sync_master_to_replica`. | Generic `_trigger_replica_sync` helper is not signal-registered. |
| `cr_process_automation/dashboard/admin.py` | Admin registrations and list/search/filter configuration. | `AutomationTaskAdmin`, `TaskRunAdmin`, `TaskLogAdmin`, `MasterCRDatabaseAdmin`, `CRWiseStatusAdmin`, `SelectedDateTableAdmin`, `UserManagementAdmin`. | History models show all versions by default. |
| `cr_process_automation/dashboard/niam_seed.py` | Idempotent seed data for NIAM lookup tables. | `NIAM_ACCESS_TYPE_SEED`, `NIAM_REQUEST_FOR_SEED`, `NIAM_PROJECT_NAME_SEED`, `NIAM_DOMAIN_SEED`, `NIAM_ACTIVITY_NAME_SEED`, `NIAM_CIRCLE_SEED`, `seed_niam_reference_tables`. | Skips populated/missing tables. |
| `cr_process_automation/dashboard/tests.py` | Placeholder test module. | imports `django.test.TestCase`. | No tests defined. |
| `cr_process_automation/cr_process_automation/settings.py` | Project configuration: env loading, apps/middleware, DBs, sessions, logging, static/media and column maps. | `DATABASES`, `AUTH_USER_MODEL`, `HOST_DOWNLOAD_FOLDER`, `CR_WISE_STATUS_FIELDS`, `PLANNING_SHEET_COLUMNS`, mapping constants. | Env-driven; no credentials hard-coded. |
| `cr_process_automation/cr_process_automation/urls.py` | Root URLconf. | `admin/`, `include('dashboard.urls')`, debug media serving. | Dashboard routes are at `/` with no prefix. |
| `cr_process_automation/cr_process_automation/routers.py` | Copy-on-write DB router. | `CoWRouter.db_for_read`, `db_for_write`, `allow_relation`, `allow_migrate`. | Auth/session/contenttypes/admin and users read `default`; other reads `replica`; all writes/migrations `default`. |
| `cr_process_automation/cr_process_automation/wsgi.py` | WSGI entry point. | `application`, `gc.freeze()`, `gc.collect()`. | Intended for preloaded Gunicorn workers. |

### 3.1 Utility modules (`dashboard/utils/`)

| File | Abstract responsibility | Key symbols/contracts |
|---|---|---|
| `utils/task_runtime.py` | Per-user, per-task in-memory run contexts and fresh module loading. | `TASK_REQUIRES_AUTH`, `requires_auth`, `make_runtime`, `RUN_REGISTRY`, `load_fresh_module`, `run_output_dir`, `shared_input_paths`, `isolate_output`. Runtime is keyed by `(user_id, task_id)` and includes `run_key`, status, logs, auth/notice/alert fields and counts. |
| `utils/region_paths.py` | Region-safe artefact paths, date labels, readiness and fan-out. | `REGION_KEYS`, `DEFAULT_REGION`, `REGION_TASK_IDS`, `TASK_FOLDER_ENV`, `safe_region`, `primary_region`, `task_date_label`, `format_env_path`, `task_output_path`, `all_region_files_ready`, `publish_region_output`. |
| `utils/region_status.py` | Shared per-region status markers and AND reduction. | `status_path`, `publish`, `combined_status`; markers under `HOST_DOWNLOAD_FOLDER/.task_status/<task>/<date>/<region>.json`. `Failed` wins, then all `Completed`, then legacy artefact fallback, otherwise `Pending`. |
| `utils/niam_paths.py` | Region-scoped NIAM workbook paths. | `niam_date_folder`, `niam_region_root`, `niam_template_path_for`, `niam_output_path_for`; `<root>/<night>/NIAM_Excel_files/<region>/`. |
| `utils/file_locks.py` | Cross-platform advisory file lock with a per-path thread lock. | `file_lock(path, timeout=300.0, poll=0.1)` creates `<path>.lock`, yields the resolved path, raises `TimeoutError` on timeout. Used by tasks 1, 2, 4, 7, 8. |
| `utils/exception_handler.py` | Decorator/model lookup helpers for JSON errors. | `handle_exceptions`, `get_or_404`. `get_or_404` raises `NotFoundException` on `DoesNotExist`. |
| `utils/cow_helpers.py` | Copy-on-write deactivation helper. | `deactivate_record(queryset, db_alias="default")`; triggers `async_sync_master_to_replica()` when rows change. |
| `utils/replica_sync.py` | Legacy SQLite master→replica backup helper. | `sync_master_to_replica`, `async_sync_master_to_replica`, `_sync_lock`. Uses `db.master.sqlite3`/`db.replica.sqlite3`; needs review under PostgreSQL settings. |

### 3.2 Task implementation files (`dashboard/task_modules/`)

| File | Abstract responsibility | Key symbols / task output |
|---|---|---|
| `task_modules/__init__.py`, `*/__init__.py` | Package markers. | No runtime behaviour. |
| `raw_report_to_template/Test.py` | Empty script with no entry point. | None. |
| `raw_report_to_template/tasks.py` | Task 1 entry point. Downloads raw report, converts to planning sheet under `file_lock`, syncs regional SQLite DBs. | `run_task`, `raw_report_to_planning_sheet_converter`, `sync_cr_databases`. |
| `cr_hygiene_checks/tasks.py` | Task 2 entry point. CR hygiene workbook plus planning-sheet updates. | `run_task`, `file_reader_and_checker`, `itsm_job_starter`, `validation_summary_writer_and_planning_sheet_updater`. |
| `install_test_plan_downloads/tasks.py` | Task 3 entry point. Downloads install/backout/test-plan files and zips them. | `run_task`, `plan_files_downloader`, `zip_maker`, `cr_wise_status_modifier_update_func`. |
| `bpms_cr_hygiene_checks/tasks.py` | Task 4 entry point. BPMS validation workbook; reuses hygiene helpers. | `run_task`, `bpms_manual_cr_design_handler`, `bpms_auto_cr_design_handler`, `first_itsm_job_starter`, `second_itsm_job_starter`. |
| `mop_attachment_approvals/tasks.py` | Task 5 entry point. MOP attachment/approval validation workbook. | `run_task`, `mop_attachment_func`, `cr_protocol_to_mop_attachment_dict_maker`; `cr_approval_func` exists but its call in `run_task` is commented out. |
| `niam_ticket_generation/tasks.py` | Tasks 7 and 8. Strict NIAM input generation and Fetch CRs rebuild. | `run_task`, `generate_niam_input`, `fetch_crs_for_date`, `niam_input_initiator`, `niam_workbook_template_maker`, `_reuse_existing_niam_rows`, `_remove_placeholder_niam_rows`, `niam_workbook_path_for`. |
| `niam_ticket_generation/niam_ticket_generation_tasks.py` | Task 9. Playwright NIAM ticket raising, DB status/failure updates, output workbook. | `run_task`, `pre_checks`, `thread_task`, `niam_database_updater`, `output_niam_file_maker`, `get_niam_output_path_for`. Uses per-run `NIAM_SESSION_FILE`. |

### 3.3 Shared task dependencies

| File | Abstract responsibility |
|---|---|
| `dependencies/playwright_common_methods_.py` | Active browser automation layer for ITSM and NIAM: session create/close, ITSM login, raw/install/test/backout downloads, approval/MOP/BPMS helpers, NIAM login/ticket raise, runtime password/OTP/notice/alert helpers, and NIAM-specific exceptions. Imported by task modules and `Night_Execution/services.py`. |
| `dependencies/playwright_common_methods_-E-5CG23509H9.py` | Older host-suffixed duplicate with fewer symbols; no imports found, appears stale. |
| `dependencies/extra_dependencies.py` | Shared dataframe/NIAM contract: column↔field mappings, dropdown sources, editable-field rules, `CustomThread`, `selected_date_df_maker`, `cr_wise_status_df_maker`, `niam_data_updater`, `renumber_niam_sno`, `niam_ticket_generation_df_maker`. |
| `dependencies/excel_modifier.py` | Shared `openpyxl` workbook wrapper (`ExcelModifier`) for headers, rows, styling and save. |
| `dependencies/batch_methods.py` | Batching helper: CR/list inputs in batches of 10, integer ranges in batches of 3. |

### 3.4 Task entry and utility contracts

- `views.start_task()` loads `TASK_MODULE_MAP[task_id]` via
  `task_runtime.load_fresh_module()` and calls:
  `run_task(request, task, runtime, GLOBAL_LOGS=None, timestamp_fn=None,
  selected_date=None, user_email=None, user_name=None, regions=None)`.
  Expected result keys: `status`, `message`, `download_ready`, usually
  `download_name`, and optional `counts`. Non-dict results are coerced to
  `{"status": "Completed", "download_ready": False}`.
- `task_runtime.RUN_REGISTRY` keeps runtime state private per user/task;
  `TASK_RUNTIME` remains a legacy display default.
- `region_paths.task_date_label()` uses `%d_%b_%Y` for tasks 7–9 and
  `%d-%b-%y` otherwise. `TASK_FOLDER_ENV` maps tasks 1–5; task 9 delegates to
  `niam_paths.niam_output_path_for()`.
- `all_region_files_ready()` is the download AND-gate;
  `publish_region_output()` copies the primary artefact into all selected
  region folders.
- Auth dialog contract: tasks 1–5 set `password_required`/`otp_required` and
  wait on `pwd_event`/`otp_event`. Every iframe URL and hidden auth form carries
  `run_key`, and submissions must match the live `(user_id, task_id, run_key)`
  context; stale forms are rejected. ITSM storage-state files are also per run
  (`itsm_session_<run_key>.json`). NIAM uses notice/alert fields and its own
  per-run session files instead.

### 3.5 Task/utility limitations

- Task 6 is mapped to `dashboard.task_modules.final_email_package.tasks`, but no
  such module exists; starting it fails before the thread starts.
- `REGION_TASK_IDS` includes 9 but excludes 7 and 8, even though tasks 7/8 use
  region-based NIAM paths.
- `views.py` has its own `TASKS_REQUIRING_AUTH = {1, 2, 3, 4, 5}` alongside
  `task_runtime.TASK_REQUIRES_AUTH`/`requires_auth()`.
- `start_task()` requires a date for tasks 1, 2, 7, 8, 9 but not 3, 4, 5, while
  tasks 2–5 parse a date immediately.
- Tasks 2–5 call `SelectedDateTable.objects.all().delete()` when the selected
  execution date has no rows; task 8 uses a scoped date filter.
- Tasks 2–5 can return a `JsonResponse` for “No CR found”; the runner treats any
  non-dict result as Completed and may publish a Completed marker.
- Task 5 defines `cr_approval_func`, but its call is commented out.
- `batch_methods.main_method()` references an undefined `e` in its `except`
  block; an exception there becomes `UnboundLocalError`.
- `format_env_path()` returns `Path()` when an env var is unset, so missing path
  configuration can silently become a relative/empty path.
- `RUN_REGISTRY` and `TASK_RUNTIME` are process-local and not durable across
  restarts or multiple workers.
- `file_lock()` is advisory and only serializes cooperating code.
- `replica_sync.py` is SQLite-specific and may skip a sync when one is running.
- The host-suffixed Playwright duplicate is stale; `get_or_404()` and
  `deactivate_record()` have no in-repo callers found.

## 4. Exceptions and error contract

All custom exceptions inherit `CustomException`, store `title`, `message` and
`status_code`, and expose `to_dict()`:

```json
{"ok": false, "title": "...", "message": "...", "status_code": 400}
```

| Class | Purpose | Default title / status | Typical source |
|---|---|---|---|
| `CustomException` | Base class; stores the error fields. | no default title / `400` | Raised directly in some task modules with explicit titles. |
| `ValidationException` | Bad or missing input/data. | `Validation Error` / `400` | `views.py`, `services.py`, NIAM generation. |
| `NotFoundException` | Missing resource/data. | `Not Found` / `404` | `views.py`, `services.py`, `utils/exception_handler.get_or_404`. |
| `TaskExecutionException` | Task module/import/runner failure. | `Task Execution Error` / `500` | `views.py:start_task`. |
| `AuthenticationException` | Authentication failure. | `Authentication Error` / `401` | Imported in `views.py`; no explicit raise found in scanned dashboard Python. |
| `PermissionException` | Authorization failure. | `Permission Denied` / `403` | No explicit raise found; some NIAM endpoints return ad-hoc 403 JSON. |
| `DatabaseException` | Database operation failure. | `Database Error` / `500` | `services.py`, `views.py:update_hygiene_check`. |
| `DuplicateRecordException` | Duplicate record creation. | `Duplicate Record` / `409` | No explicit raise found in scanned dashboard Python. |

`CustomExceptionMiddleware` and `utils.exception_handler.handle_exceptions` turn
these into the JSON shape above. Some NIAM endpoints instead return ad-hoc
`{"ok": false, "message": ...}` payloads.

## 5. Runtime and data flow

### 5.1 Start-to-finish task flow

1. `start_task()` validates task id, date and regions, enforces region locks,
   pre-imports the mapped module and checks for `run_task`.
2. `RUN_REGISTRY.begin()` creates a fresh per-user runtime; `TaskRun` records
   owner, session and run key.
3. Region tasks publish a `Running` status marker for each selected region.
4. A daemon thread calls `run_task(request, task, runtime, GLOBAL_LOGS, timestamp_fn,
   selected_date, user_email, user_name, regions)` on a freshly loaded module.
5. The result updates runtime status, logs, counts and download metadata.
6. Region artefacts are copied to every selected region folder by
   `publish_region_output()`; final status markers are published; private outputs
   use `task_runtime.isolate_output()`.
7. `TaskRun` is closed out with `Successful`/`Unsuccessful`; auth/notice flags are
   cleared; the temporary module is removed from `sys.modules`.

### 5.2 Dashboard polling payload

`task_dashboard_data()` returns `running_task`, `logs`, `tasks`, `user_name`,
`user_role` and `user_email`. Each task includes status, download fields, CR
counts, auth flags, notice/alert fields and `run_key`. For region tasks with date
and regions, readiness and badge status are derived from shared artefacts and
markers rather than the viewing user's own run.

### 5.3 Persistence and routing

- CR models use copy-on-write: writes create a new active version, reads normally
  target `replica`.
- `CoWRouter` sends `default` for auth/session/contenttypes/admin/users and all
  writes/migrations; other reads go to `replica`.
- `TaskRun`/`TaskLog` persist run ownership and logs; NIAM tables persist
  template rows and lookup values.
- Shared artefacts, private run copies, NIAM sessions, status markers and logs
  live on the filesystem under the configured download/media roots.

## 6. Sub-apps, management commands, and project bootstrap

### 6.1 Dashboard sub-apps

| File | Abstract responsibility | Used by / notes |
|---|---|---|
| `dashboard/__init__.py` | Import-time bootstrap: loads `.env`, sets `PLAYWRIGHT_BROWSERS_PATH` to `cr_process_automation/pw-browsers`, validates a `chromium-*` build exists. | Required before Playwright tasks start. |
| `dashboard/Region_CRs/views.py` | Region CR table, CR history, fetch/save APIs, CoW edits, replica reads, scoped selected-date rebuild, and NIAM-row removal. | Active routes: `region_crs`, `cr_history`, `fetch_region_cr_details`, `save_region_cr_details`, `fetch_cr_history`, `download_cr_history`. |
| `dashboard/CR_Wise_Status/views.py` | Renders the PAN-India CR status page and returns active `CRWiseStatus` rows for a date. | Active routes: `cr_wise_status`, `fetch_cr_wise_status`. |
| `dashboard/Night_Execution/views.py` | Night Execution page, CR fetch by executor/date, status job start/poll, and auth iframes. | `_JOBS` is process-local; needs a shared store for multi-worker use. |
| `dashboard/Night_Execution/services.py` | ITSM status-fetch service: `NIGHT_EXECUTION_TASKS`, `STATUS_BATCH_SIZE = 3`, `build_cr_status_payload*`. | Used by the background status thread. |
| `dashboard/Night_Execution/views copy.py` | Legacy duplicate of an earlier implementation. | Not imported by `urls.py`. |
| `dashboard/vendor_dashboard/views.py` | Dormant vendor analytics helpers and views after a large commented legacy block. | Active routes are commented out; `dashboard.views` serves the current analysis pages. |

### 6.2 Management commands and project scripts

| File | Abstract responsibility |
|---|---|
| `cr_process_automation/manage.py` | Standard Django management command entry point. |
| `dashboard/management/commands/runserver.py` | Starts PostgreSQL Compose services, waits for master/replica, runs Django, then stops containers. |
| `dashboard/management/commands/sync_replica.py` | Prints replication status/row counts; `--resync` wipes and re-clones the replica volume. |
| `dashboard/management/commands/import_master_cr.py` | Imports the daily planning sheet into `MasterCRDatabase` using CoW versioning. |
| `cr_process_automation/extra_depency_module.py` | Empty placeholder; filename spelling is intentional as found in the repo. |
| `cr_process_automation/db_start.py` | Starts PostgreSQL, waits for master/replica, migrates, loads `sync_data.json`, waits for replay unless `--no-sync`. Flags: `--fresh`, `--status`, `--no-sync`. |
| `cr_process_automation/db_stop.py` | Optionally dumps/writes fixtures, cleans temp/log artefacts, stops containers. Flags: `--backup`, `--no-sync`, `--wipe`. |
| `cr_process_automation/docker-compose.yml` | Master/replica PostgreSQL services with health checks and ports `5432`/`5433`. |
| `cr_process_automation/setup.sh`, `pre-start.sh` | Prepare DB volume directories and start Compose services. |
| `cr_process_automation/pre-stop.sh` | Placeholder container cleanup script. |

## 7. Frontend/template map

All templates extending `dashboard/base_main.html` inherit `dashboard/css/style.css` and `dashboard/js/dashboard.js`. Templates extending `base_module.html` inherit them through `base_main.html`.

| Template | Abstract responsibility | Assets / API contract |
|---|---|---|
| `base_main.html` | Shared app shell, navigation, footer panels, auth/notice/alert overlay. | Loads `style.css`, `dashboard.js`; overlay driven by task payload flags. |
| `base_module.html` | Adds left module menu and `module_content` block. | Extends `base_main.html`; builds links from `menu_items`. |
| `home.html` | CR Planning task table, date/region filters, counts, downloads, locks. | Loads `region_locks.js`; calls `/filter-region-crs/` and `download_task_output`. |
| `dashboard.html` | Analytics workspace cards. | Links to four active analysis routes. |
| `dashboard_copy.html` | Older copy of analytics workspace. | Dormant; references commented `vendor_dashboard_view`. |
| `automation_cr_analysis.html` | Automation CR filters, tables, charts. | Chart.js CDN; `fetch-automation-cr-analysis`. |
| `cr_success_rate_analysis.html` | Success-rate KPIs, tables, charts. | Chart.js CDN; `fetch-cr-success-rate-analysis`. |
| `team_performance_analysis.html` | Team/executor performance tables and heatmaps. | Chart.js CDN; `fetch-team-performance-analysis`. |
| `vendor_wise_analysis.html` | Vendor-wise tables and charts. | Chart.js CDN; `fetch-vendor-wise-analysis`. |
| `vendor_dashboard.html` | Dormant vendor dashboard with heatmap/monthly series. | Uses `vendor_dashboard_data`; route commented out. |
| `region_crs.html` | Editable Region CR table. | `fetch_region_cr_details`, `fetch_user_options`, `save_region_cr_details`. |
| `cr_history.html` | PAN-India CR history with date/range filters and download. | `fetch_cr_history`, `download_cr_history`. |
| `cr_wise_status.html` | PAN-India CR Wise Status table. | `fetch_cr_wise_status`. |
| `niam_template_db.html` | NIAM fetch/edit/save/download/generate UI. | NIAM APIs plus task dashboard polling. |
| `niam_credentials.html` | Self-service OLM ID/password form. | `update-niam-credentials`. |
| `night_execution.html` | Night Execution date picker, CR table, task buttons. | Injects `window.USER_EMAIL`; loads `night_execution.js`. |
| `night_spoc.html` | Intentional placeholder page. | No API. |
| `iframe_alert.html` | Blocking backend alert iframe. | Polls dashboard data every 2s; posts close message. |
| `iframe_form.html` | Shared password/OTP iframe. | Posts to current iframe URL; posts close message. |
| `iframe_notice.html` | Read-only sign-in-code iframe. | Polls dashboard data every 1s; posts close message. |
| `iframe_success.html` | Success confirmation iframe. | Posts close message after 1s. |
| `login.html` | Standalone login page. | Standard form POST. |
| `password_form.html` | Legacy standalone ITSM password form. | Standard form POST with hidden task id. |
| `import_master_cr.html` | Empty dormant template. | Route commented out. |

### Static assets

| File | Responsibility |
|---|---|
| `static/dashboard/js/dashboard.js` | Global polling, status/download rendering, auth overlay, task start, replica-sync polling. |
| `static/dashboard/js/region_locks.js` | CR Planning region lock heartbeat. |
| `static/dashboard/js/night_execution.js` | Night Execution fetch/status/auth flow. |
| `static/dashboard/css/style.css` | Shared dashboard styling. |
| `static/dashboard/images/automation-tool-brand.png`, `automation-tool-login.png` | Login page branding. |

## 8. JavaScript contracts

### `dashboard.js`

- Loaded globally by `base_main.html`.
- `refreshTaskPanels()` polls `/api/task/dashboard-data/` on load and every **500 ms**. CR Planning adds `cr_planning=1`, `date`, and comma-separated `regions`.
- Consumes `running_task`, `logs`, `tasks`, `user_name`, `user_role`, `user_email`.
- Each task uses `id`, `status`, `download_ready`, `download_name`, `download_url`, CR counts, auth flags, notice/alert fields, and `run_key`.
- Auth overlay routes (all include `&run_key=<run_key>`):
  - password → `/playwright-password-iframe/?task_id=<id>`
  - notice → `/playwright-notice-iframe/?task_id=<id>`
  - alert → `/playwright-alert-iframe/?task_id=<id>`
  - OTP/default → `/playwright-auth-iframe/?task_id=<id>`
- Alert dedupe key: `<task.id>:<task.run_key>:<task.alert_seq>`.
- Task start: `POST /api/task/start/<task_id>/` with `X-CSRFToken` and `FormData(date, region)`.
- `waitForReplicaSync(syncId)` polls `/api/replica-sync-status/<sync_id>/` every 500 ms.

### `region_locks.js`

- Loaded only by `home.html`; keys are `north`, `west`, `east`, `south`.
- `POST /api/region-locks/acquire/`, `POST /api/region-locks/release/`, `GET /api/region-locks/status/`.
- Heartbeat is **3000 ms**; releases via `navigator.sendBeacon` on unload/pagehide.
- Exposes `window.RegionLocks = {refreshStatus, acquire, release}`.

### `night_execution.js`

- Loaded only by `night_execution.html`; reads `window.USER_EMAIL`.
- Constants: `POLL_INTERVAL_MS = 2000`, `MAX_POLL_ATTEMPTS = 150`.
- Task keys: `automation_template`, `activity_hc`, `activity_cli`, `cr_implementation`, `cr_closure`.
- APIs: `fetch-crs`, `start-task`, `fetch-cr-status`, `status-result`, password/OTP iframes.
- Final status payload: `{ok, statuses: {<cr_no>: <status>}}`.
- `start_night_execution_task()` is currently a backend placeholder.

## 9. Root launchers and operational scripts

| File | Abstract responsibility |
|---|---|
| `wsgi_app.py` | Cross-platform WSGI launcher: Gunicorn `gthread` on Linux/macOS, Waitress on Windows/fallback; optional `--migrate`/`--collectstatic`; default `0.0.0.0:9000`, one worker. |
| `start.sh` | Linux/macOS wrapper; prefers `.venv`; wraps with `xvfb-run` when `DISPLAY` is unset unless `NO_XVFB=1`. |
| `start.bat` | Windows wrapper for the same launcher. |
| `deploy.py` | Management-command passthrough that adds `cr_process_automation/` to `sys.path`. |
| `setup_browsers.py` | Installs Playwright Chromium into `cr_process_automation/pw-browsers`. |
| `Dockerfile` | Python slim image, port `9000`; CMD uses Windows-style path syntax and needs review for Linux containers. |
| `compose.yaml` | App service on `9000:9000`; DB block commented out. |
| `pyproject.toml`, `requirements.txt` | Project metadata and runtime dependency declarations, including Windows-only `pywin32`. |
| `deploy/nginx.conf` | Sample reverse proxy to `127.0.0.1:8000`, static/media aliases, proxy headers, 600s timeouts, optional TLS. |
| `scripts/watch_niam_timing.sh`, `.ps1` | Tail `notice_timing.log`, `errors.log`, and optionally the service journal/stdout. |

## 10. Known limitations and TODOs

| Area | Limitation |
|---|---|
| Task 6 | `final_email_package.tasks` is mapped but absent; starting it fails before the thread starts. |
| Task 7 UI | Startable via generic API but has no dedicated NIAM page button. |
| Region fan-out | Only tasks 1–5 and 9 are in `REGION_TASK_IDS`; NIAM input workbooks for tasks 7/8 are not fanned out. |
| NIAM metadata | `NIAMTicketGenerationTable` has no `region` field; workbook write-back targets `all`. |
| Status markers | Stale markers and the legacy artefact fallback can show Completed after older runs. |
| Process-local state | `RUN_REGISTRY`, `TASK_RUNTIME`, and Night Execution `_JOBS` do not survive restarts or multiple workers. The launcher now forces `WSGI_WORKERS=1`; scale with threads only. |
| Date validation | `start_task()` requires a date for tasks 1, 2, 7, 8, 9 but not 3, 4, 5, although tasks 2–5 parse a date immediately. |
| CR deletion scope | Tasks 2–5 call `SelectedDateTable.objects.all().delete()` when the execution date has no rows. |
| Non-dict task results | Tasks 2–5 can return a `JsonResponse`; the runner treats any non-dict result as Completed and may publish a Completed marker. |
| Task 5 | `cr_approval_func` is defined but its call is commented out. |
| Batching | `batch_methods.main_method()` references undefined `e` in its `except` block. |
| Path config | `format_env_path()` returns `Path()` when an env var is unset, silently becoming a relative/empty path. |
| File locks | Advisory; only cooperating code is serialized. |
| Replica sync | `replica_sync.py` is SQLite-specific while settings use PostgreSQL; `check_replica_sync_status()` is a placeholder. |
| Duplicate code | `playwright_common_methods_-E-5CG23509H9.py`, `Night_Execution/views copy.py`, `dashboard_copy.html`, and dormant vendor routes/templates remain. |
| Deployment | `deploy/nginx.conf` targets port `8000`; `wsgi_app.py` defaults to `9000`. Pass `--port` explicitly. |
| Dockerfile | CMD uses Windows-style backslashes inside a Linux image. |
| Tests | `dashboard/tests.py` is an empty placeholder. |
| Idle locks | Idle timeout clears run contexts but does not delete `RegionLock` rows; expiry relies on TTL/heartbeat lapse. |
| Frontend timing | `dashboard.js` comment says 3 seconds but task polling uses 500 ms. |
| NIAM validation | `NIAM_EDITABLE_FIELDS` comment says all seven must be filled, but `save_niam_template_changes()` accepts blanks. |
| Dormant endpoints | `fetch_current_date_crs`, `update_hygiene_check`, upload/import routes, and vendor dashboard routes have no active URL entry. |

## 11. Documentation touchpoints

- `README.md` links all three docs and uses launcher port `9000`.
- `deploy/nginx.conf` still documents `8000`; keep that aligned when changing deployment examples.
- `TEAM_HANDOVER.md` is the operational companion: workflows, locks, MFA, troubleshooting.
- `TECHNICAL_BACKEND.md` is the backend companion: endpoints, runtime isolation, models, routing, concurrency.
- Update this file when adding task modules, routes, templates, status markers, or operational scripts.
