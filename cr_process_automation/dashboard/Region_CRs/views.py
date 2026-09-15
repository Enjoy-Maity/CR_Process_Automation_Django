import logging
import copy
from collections import defaultdict
from django.core.serializers.json import DjangoJSONEncoder
from pathlib import Path
from datetime import datetime
import sqlite3
import sys
import traceback
import threading
from importlib import import_module
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_GET, require_POST
from dashboard.models import MasterCRDatabase, SelectedDateTable, CRWiseStatus,UserManagement  # CHANGED: added CRWiseStatus
from dashboard.views import _common_context
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
import json
from datetime import datetime, timedelta
from io import BytesIO
from django.utils import timezone
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

# CHANGED: define module logger (used by bootstrap_selected_date_table,
# _trigger_replica_sync_on_commit, and save_region_cr_details).
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────
# Database Alias Constants
# ────────────────────────────────────────────────────────────────
DB_MASTER  = 'default'   # All writes go here
DB_REPLICA = 'replica'   # All reads go here

# CHANGED: define _COW_BOOKKEEPING (referenced by _sync_fields but never defined).
# These are pk + CoW columns that must NOT be copied when mirroring master rows.
# _COW_BOOKKEEPING = {"id", "is_active", "version", "parent_reference"}

# ────────────────────────────────────────────────────────────────
# Field Definitions
# ────────────────────────────────────────────────────────────────
MASTER_CR_FIELDS = [
    "id", "sno", "ms_project", "execution_date", "maintenance_window", "cr_no",
    "priority", "risk", "region", "circle", "activity_description", "node_details", "node_count",
    "bpms_cr_yes_no", "planning_status", "activity_executor",
    "auditor_name", "activity_status", "reason_for_rollback_cancel", "technical_validator",
    "service_affecting", "impact", "test_cases", "kpi_name", "kpi_spoc_night",
    "kpi_spoc_morning", "inter_domain_activity", "inter_domain_kpi_required",
    "inter_domain_measuring_kpis", "activity_type", "vendor", "protocol",
    "execution_type", "cli_availability", "team", "scheduled_start_date",
    "scheduled_end_date", "niam_ticket_required", "niam_node_type", "additional_info",
    # CoW metadata fields for context
    "is_active", "version", "parent_reference_id",
]

EDITABLE_REGION_CR_FIELDS = [
    "node_details",
    "region",
    "circle",
    "node_count",
    "planning_status",
    "activity_executor",
    "auditor_name",
    "activity_status",
    "technical_validator",
    "reason_for_rollback_cancel",
    "test_cases",
    "kpi_spoc_night",
    "kpi_spoc_morning",
    "activity_type",
    "vendor",
    "protocol",
    "execution_type",
    "cli_availability",
    "niam_ticket_required",
    "niam_node_type",
    "additional_info",
]

CR_HISTORY_EXPORT_FIELDS = [
    "ms_project",
    "execution_date",
    "maintenance_window",
    "cr_no",
    "priority",
    "risk",
    "region",
    "circle",
    "activity_description",
    "node_details",
    "node_count",
    "bpms_cr_yes_no",
    "planning_status",
    "activity_executor",
    "auditor_name",
    "activity_status",
    "reason_for_rollback_cancel",
    "technical_validator",
    "service_affecting",
    "impact",
    "test_cases",
    "kpi_name",
    "kpi_spoc_night",
    "kpi_spoc_morning",
    "inter_domain_activity",
    "inter_domain_kpi_required",
    "inter_domain_measuring_kpis",
    "activity_type",
    "vendor",
    "protocol",
    "execution_type",
    "cli_availability",
    "team",
    "scheduled_start_date",
    "scheduled_end_date",
    "niam_ticket_required",
    "niam_node_type",
    "additional_info",
    # CoW metadata fields included in export for audit trail
    "version",
    "parent_reference_id",
]

CR_HISTORY_EXPORT_FIELDS_VIEW = [
    "ms_project",
    "execution_date",
    "maintenance_window",
    "cr_no",
    "priority",
    "risk",
    "region",
    "circle",
    "activity_description",
    "node_details",
    "node_count",
    "bpms_cr_yes_no",
    "planning_status",
    "activity_executor",
    "auditor_name",
    "activity_status",
    "reason_for_rollback_cancel",
    "technical_validator",
    "service_affecting",
    "impact",
    "test_cases",
    "kpi_name",
    "kpi_spoc_night",
    "kpi_spoc_morning",
    "inter_domain_activity",
    "inter_domain_kpi_required",
    "inter_domain_measuring_kpis",
    "activity_type",
    "vendor",
    "protocol",
    "execution_type",
    "cli_availability",
    "team",
    "scheduled_start_date",
    "scheduled_end_date",
    "niam_ticket_required",
    "niam_node_type",
    "additional_info",
]

ALLOWED_REGION_CR_EDIT_ROLES = {"Admin", "Validator", "Night-SPOC"}
# Must match the exact values stored in the DB / model choices.
PLANNING_STATUS_ALLOWED = {"planned", "unplanned", "discussed"}
USER_EDITABLE_FIELDS = {"activity_executor", "auditor_name", "kpi_spoc_night", "kpi_spoc_morning", }  # add more if needed


_COW_BOOKKEEPING = {"id", "is_active", "version", "parent_reference", "parent_reference_id"}


def _sync_fields():
    def concrete_names(model):
        names = set()
        for f in model._meta.get_fields():
            # Skip reverse relations (e.g. historical_versions) and m2m.
            if f.auto_created and not f.concrete:
                continue
            if getattr(f, "many_to_many", False):
                continue
            if not getattr(f, "concrete", False):
                continue
            # Use the DB attribute name for FKs (…_id), plain name otherwise.
            names.add(f.attname if hasattr(f, "attname") else f.name)
        return names

    master_fields = concrete_names(MasterCRDatabase)
    sel_fields = concrete_names(SelectedDateTable)
    return (master_fields & sel_fields) - _COW_BOOKKEEPING


def sync_selected_date_table(execution_date):
    """
    Rebuild SelectedDateTable for a single execution_date to mirror the
    currently-active MasterCRDatabase rows for that date.

    Behavior:
      - If SelectedDateTable has rows for this date, they are deleted and
        rebuilt from active master rows (self-healing).
      - If SelectedDateTable has NO rows for this date ("not available"),
        they are simply created from active master rows.

    Call this AFTER MasterCRDatabase has committed for `execution_date`
    (i.e. from a transaction.on_commit hook). Scoped to one date so other
    dates are never touched. bulk_create intentionally bypasses
    SelectedDateTable.save()/CoW: a rebuild is a full mirror, not a versioned edit.
    """
    copy_fields = _sync_fields()  # concrete, assignable columns only

    with transaction.atomic(using=DB_MASTER):
        # Delete existing rows for this execution_date to avoid unique constraint violations
        table_with_current_selected_date = SelectedDateTable.objects.using(DB_MASTER).filter(
            execution_date=execution_date
        )
        if table_with_current_selected_date.exists():
            table_with_current_selected_date.delete()

        master_rows = list(  # CHANGED: materialise once (needed for drift guard + build)
            MasterCRDatabase.objects.using(DB_MASTER).filter(
                execution_date=execution_date, is_active=True
            ).values(*copy_fields)
        )

        # Drift guard: active master must be unique per cr_no.
        seen = set()
        for row in master_rows:
            cr = row.get("cr_no")
            if cr in seen:
                raise ValueError(
                    f"Duplicate active master row for cr_no={cr} on "
                    f"{execution_date}; fix master drift before rebuild."
                )
            seen.add(cr)

        # copy_fields already excludes pk/CoW/reverse fields, so this is safe.
        # Set is_active=True explicitly to avoid any default value issues
        model_instances = []
        for row in master_rows:
            row_data = row.copy()
            row_data['is_active'] = True
            model_instances.append(SelectedDateTable(**row_data))

        if model_instances:
            # Use bulk_create with ignore_conflicts to handle any remaining unique constraint issues
            SelectedDateTable.objects.using(DB_MASTER).bulk_create(
                model_instances, 
                ignore_conflicts=True
            )

    logger.info(
        "sync_selected_date_table: rebuilt %d rows for %s",
        len(model_instances), execution_date,
    )
    return len(model_instances)


# ────────────────────────────────────────────────────────────────
# Helper: Sync replica after master commit
# ────────────────────────────────────────────────────────────────
def _trigger_replica_sync_on_commit(affected_dates):
    """
    Registers a post-commit hook to sync the master DB
    to the replica after the current transaction commits.
    No Redis or Celery required: runs synchronously via call_command.
    """
    def _run_sync():
        try:
            # Sync SelectedDateTable for affected dates
            for d in affected_dates:
                sync_selected_date_table(d)
            # Then sync replica
            from django.core.management import call_command
            call_command("sync_replica")
        except Exception:
            logger.exception("Replica sync failed after commit")
    
    if affected_dates:
        transaction.on_commit(_run_sync, using=DB_MASTER)


# ────────────────────────────────────────────────────────────────
# Views: Render Pages
# ────────────────────────────────────────────────────────────────
@login_required(login_url="login")
def region_crs_view(request):
    ctx = _common_context(request)
    ctx["selected_option"] = "region_crs"
    ctx["field_labels"] = MASTER_CR_FIELDS
    ctx["editable_region_cr_fields"] = EDITABLE_REGION_CR_FIELDS
    ctx["can_edit_region_crs"] = getattr(request.user, "role", "") in ALLOWED_REGION_CR_EDIT_ROLES
    return render(request, "dashboard/region_crs.html", ctx)


@login_required(login_url="login")
def cr_history_view(request):
    ctx = _common_context(request)
    ctx["selected_option"] = "cr_history"
    return render(request, "dashboard/cr_history.html", ctx)



# ────────────────────────────────────────────────────────────────
# View: Fetch Region CR Details (READ → replica)
# ────────────────────────────────────────────────────────────────
@require_GET
@login_required(login_url="login")
def fetch_region_cr_details(request):
    date_str = request.GET.get("date", "").strip()
    if not date_str:
        return JsonResponse({"ok": False, "message": "Date is required."}, status=400)

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()  # noqa: DTZ007
    except ValueError:
        return JsonResponse({"ok": False, "message": "Invalid date format."}, status=400)

    # Read explicitly from replica and only return active (latest CoW) records
    result = list(
        MasterCRDatabase.objects
        .using(DB_REPLICA)
        .filter(execution_date=parsed_date, is_active=True)
        .values(*MASTER_CR_FIELDS)
    )

    for row in result:
        if row.get("execution_date"):
            row["execution_date"] = row["execution_date"].strftime("%d-%m-%Y")
        if row.get("scheduled_start_date"):
            row["scheduled_start_date"] = timezone.localtime(row["scheduled_start_date"]).strftime("%d-%m-%Y %H:%M:%S")
        if row.get("scheduled_end_date"):
            row["scheduled_end_date"] = timezone.localtime(row["scheduled_end_date"]).strftime("%d-%m-%Y %H:%M:%S")

    return JsonResponse({
        "ok": True,
        "date": date_str,
        "fields": MASTER_CR_FIELDS,
        "rows": result,
    })


# ────────────────────────────────────────────────────────────────
# View: Save Region CR Details (WRITE → CoW on master)
# ────────────────────────────────────────────────────────────────
# @require_POST
# @login_required(login_url="login")
# def save_region_cr_details(request):
#     user_role = getattr(request.user, "role", "")
#     if user_role not in ALLOWED_REGION_CR_EDIT_ROLES:
#         return JsonResponse({
#             "ok": False,
#             "message": "You are not authorized to modify Region CR records."
#         }, status=403)

#     try:
#         payload = json.loads(request.body.decode("utf-8"))
#     except Exception:
#         return JsonResponse({
#             "ok": False,
#             "message": "Invalid JSON payload."
#         }, status=400)

#     changes = payload.get("changes", [])
#     print(f"changes=\n{changes}")
#     if not isinstance(changes, list) or not changes:
#         return JsonResponse({
#             "ok": False,
#             "message": "No changes were submitted."
#         }, status=400)

#     updated_rows = []
#     errors = []
#     did_write = False

#     with transaction.atomic(using=DB_MASTER):
#         for item in changes:
#             row_id = item.get("id")
#             field_values = item.get("fields", {})

#             if not row_id:
#                 errors.append({"id": None, "message": "Missing row id."})
#                 continue

#             if not isinstance(field_values, dict):
#                 errors.append({"id": row_id, "message": "Invalid fields payload."})
#                 continue

#             invalid_fields = [f for f in field_values.keys() if f not in EDITABLE_REGION_CR_FIELDS]
#             if invalid_fields:
#                 errors.append({
#                     "id": row_id,
#                     "message": f"Invalid editable fields: {', '.join(invalid_fields)}"
#                 })
#                 continue

#             try:
#                 active_obj = MasterCRDatabase.objects.using(DB_MASTER).get(id=row_id, is_active=True)
#             except MasterCRDatabase.DoesNotExist:
#                 errors.append({"id": row_id, "message": "Active record not found. It may have already been updated."})
#                 continue

#             # sanitise and validate input values (same handling as views1.py)
#             sanitised_fields = {}
#             field_error = None
#             for field_name, raw_value in field_values.items():
#                 value = raw_value
#                 if isinstance(value, str):
#                     value = value.strip()
#                     if value.lower() in {"nan", "na", "n/a", "n.a.", "n.a", "none", "null", "nat"}:
#                         value = ""
#                 if field_name == "node_count":
#                     if value in ("", None):
#                         value = None
#                     else:
#                         try:
#                             value = int(value)
#                         except (TypeError, ValueError):
#                             field_error = {"id": row_id, "message": "node_count must be a valid integer."}
#                             break
#                 sanitised_fields[field_name] = value

#             if field_error:
#                 errors.append(field_error)
#                 continue

#             if not sanitised_fields:
#                 continue

#             # CoW step: deactivate current active record
#             MasterCRDatabase.objects.using(DB_MASTER).filter(pk=active_obj.pk).update(is_active=False)

#             # Build new record dictionary by copying fields from the active object
#             new_record_data = {}
#             for field in active_obj._meta.get_fields():
#                 # skip reverse relations and non-concrete fields
#                 if getattr(field, "many_to_many", False):
#                     continue
#                 if not getattr(field, "concrete", True):
#                     continue
#                 fname = field.name
#                 if fname == "id":
#                     continue
#                 new_record_data[fname] = getattr(active_obj, fname)

#             # Apply incoming changes
#             new_record_data.update(sanitised_fields)

#             # Set CoW metadata
#             new_record_data["is_active"] = True
#             new_record_data["version"] = (active_obj.version or 0) + 1
#             new_record_data["parent_reference_id"] = active_obj.pk

#             # Create new instance using setattr pattern (so behaviour mirrors views1.py)
#             new_obj = MasterCRDatabase()
#             row_updated_fields = []
#             for k, v in new_record_data.items():
#                 # skip id if present
#                 if k == "id":
#                     continue
#                 setattr(new_obj, k, v)
#                 # record which user-submitted editable fields changed
#                 if k in sanitised_fields:
#                     row_updated_fields.append(k)

#             # Save new version to master
#             # new_obj.save(using=DB_MASTER, force_insert=True)
#             try:
#                 new_obj.save(using=DB_MASTER, force_insert=True)
#             except Exception as exc:
#                 logging.getLogger(__name__).exception(
#                     "CoW insert failed for row %s", row_id
#                 )
#                 errors.append({"id": row_id, "message": str(exc)})
#                 # roll back the deactivation of this row within the atomic block
#                 MasterCRDatabase.objects.using(DB_MASTER).filter(
#                     pk=active_obj.pk
#                 ).update(is_active=True)
#                 continue

#             updated_rows.append({
#                 "old_id": active_obj.pk,
#                 "new_id": new_obj.pk,
#                 "cr_no": new_obj.cr_no,
#                 "new_version": new_obj.version,
#                 "updated_fields": row_updated_fields,
#             })
#             # did_write = True


#         # Register master->replica sync after commit (runs synchronously here)
#         if did_write:
#             _trigger_replica_sync_on_commit()
#         # transaction.on_commit(lambda: _trigger_replica_sync_on_commit(), using=DB_MASTER)

#     if errors and not updated_rows:
#         return JsonResponse({
#             "ok": False,
#             "message": "No records were updated.",
#             "errors": errors,
#         }, status=400)

#     return JsonResponse({
#         "ok": True,
#         "message": f"{len(updated_rows)} record(s) updated successfully (new CoW versions created).",
#         "updated_rows": updated_rows,
#         "errors": errors,
#     })


def _user_can_edit_region_crs(user):
    return user.is_authenticated and user.role in ("Admin", "Validator")


def bootstrap_selected_date_table():
    """
    Full bootstrap: if SelectedDateTable is entirely empty (table not populated),
    build it from ALL active MasterCRDatabase rows across every execution_date.
    Safe to call on startup or via a management command. No-op if rows exist.
    """
    if SelectedDateTable.objects.using(DB_MASTER).exists():
        return 0

    copy_fields = _sync_fields()
    with transaction.atomic(using=DB_MASTER):
        master_rows = list(
            MasterCRDatabase.objects.using(DB_MASTER)
            .filter(is_active=True)
            .values(*copy_fields)
        )
        
        # Group by execution_date to handle unique constraints properly
        rows_by_date = defaultdict(list)
        for row in master_rows:
            exec_date = row.get('execution_date')
            if exec_date:
                rows_by_date[exec_date].append(row)
        
        # Process each date separately to avoid unique constraint violations
        total_created = 0
        for exec_date, rows in rows_by_date.items():
            # Ensure no existing records for this date
            SelectedDateTable.objects.using(DB_MASTER).filter(
                execution_date=exec_date
            ).delete()
            
            # Create instances with explicit is_active=True
            instances = []
            for row in rows:
                row_data = row.copy()
                row_data['is_active'] = True
                instances.append(SelectedDateTable(**row_data))
            
            if instances:
                SelectedDateTable.objects.using(DB_MASTER).bulk_create(
                    instances, 
                    ignore_conflicts=True
                )
                total_created += len(instances)

    logger.info("bootstrap_selected_date_table: created %d rows", total_created)
    return total_created


@require_POST
@login_required(login_url="login")
def save_region_cr_details(request):
    if not _user_can_edit_region_crs(request.user):  # your existing auth check
        return JsonResponse(
            {"ok": False, "message": "Not authorized.", "errors": []},
            status=403,
        )

    # --- Parse payload ---
    try:
        payload = json.loads(request.body.decode("utf-8"))
        changes = payload.get("changes", [])
        print(f'\n\n{changes = }')
    except (ValueError, KeyError):
        return JsonResponse(
            {"ok": False, "message": "Invalid request body.", "errors": []},
            status=400,
        )

    if not isinstance(changes, list) or not changes:
        return JsonResponse(
            {"ok": False, "message": "No changes to save.", "errors": []},
            status=400,
        )

    errors = []
    updated_rows = []
    did_write = False
    affected_dates = set()  # CHANGED: track dates to rebuild in SelectedDateTable

    try:
        with transaction.atomic(using=DB_MASTER):
            for item in changes:
                row_id = item.get("id")
                raw_fields = item.get("fields", {}) or {}
                print(f'\n\n{raw_fields = }\n\n')

                if row_id is None:
                    errors.append({"id": None, "message": "Missing row id."})
                    continue

                # --- Validate field allowlist ---
                invalid_fields = [
                    f for f in raw_fields.keys()
                    if f not in EDITABLE_REGION_CR_FIELDS
                ]
                if invalid_fields:
                    errors.append({
                        "id": row_id,
                        "message": f"Non-editable field(s): {', '.join(invalid_fields)}",
                    })
                    continue

                # --- Sanitise / normalise values ---
                sanitised_fields = {}
                field_error = None

                for field_name, value in raw_fields.items():
                    # Trim strings; treat blanks as empty
                    if isinstance(value, str):
                        value = value.strip()

                    if field_name == "node_count":
                        if value in ("", None):
                            value = None
                        else:
                            try:
                                value = int(value)
                            except (TypeError, ValueError):
                                field_error = {
                                    "id": row_id,
                                    "message": "node_count must be a valid integer.",
                                }
                                break

                    if field_name == "planning_status" and value not in ("", None):
                        normalized = str(value).strip().lower()
                        if normalized not in PLANNING_STATUS_ALLOWED:
                            field_error = {
                                "id": row_id,
                                "message": f"Invalid planning_status: {value}",
                            }
                            break
                        value = normalized  # store canonical form

                    if field_name in USER_EDITABLE_FIELDS and value not in ("", None):
                        # User = get_user_model()
                        if not UserManagement.objects.filter(
                            is_active=True, employee_name=value
                        ).exists():
                            field_error = {
                                "id": row_id,
                                "message": f"Invalid user for {field_name}: {value}",
                            }
                            break

                    sanitised_fields[field_name] = value

                if field_error:
                    errors.append(field_error)
                    continue

                if not sanitised_fields:
                    continue  # nothing to change for this row

                # --- Load the current active row ---
                active_obj = (
                    MasterCRDatabase.objects.using(DB_MASTER)
                    .filter(pk=row_id, is_active=True)
                    .first()
                )
                # print(f"{row_id = }")
                if active_obj is None:
                    errors.append({
                        "id": row_id,
                        "message": "Active record not found (may have been modified).",
                    })
                    continue

                # --- CoW step 1: deactivate current active row (guarded) ---
                deactivated = (
                    MasterCRDatabase.objects.using(DB_MASTER)
                    .filter(pk=active_obj.pk, is_active=True)
                    .update(is_active=False)
                )
                if deactivated != 1:
                    errors.append({
                        "id": row_id,
                        "message": "Record was modified concurrently. Please re-fetch and retry.",
                    })
                    continue

                # --- CoW step 2: build the new active row ---
                # Deep-copy the existing row so ALL NOT NULL columns carry over,
                # then overlay only the edited fields. This prevents the
                # NOT NULL constraint failure from hand-picking fields.
                new_obj = copy.deepcopy(active_obj)
                new_obj.pk = None
                new_obj.id = None          # adjust if your PK isn't 'id'
                new_obj.is_active = True

                # print(f'{new_obj = }')
                for field_name, value in sanitised_fields.items():
                    # print(f'{field_name = }')
                    # print(f'{value =}\n')
                    setattr(new_obj, field_name, value)

                # No-op unless MasterCRDatabase gains updated_at; kept for future-proofing.
                if hasattr(new_obj, "updated_at"):
                    new_obj.updated_at = timezone.now()

                # --- CoW step 3: insert new row (single CoW path) ---
                try:
                    # skip_cow=True: only if MasterCRDatabase.save() supports it.
                    # Drop skip_cow if your model has no CoW override.
                    # new_obj.save(using=DB_MASTER, force_insert=True, skip_cow=True)
                    new_obj.save(using=DB_MASTER, force_insert=True)
                except Exception as exc:
                    logger.exception("CoW insert failed for row %s", row_id)
                    errors.append({"id": row_id, "message": str(exc)})
                    # Roll back the deactivation of this specific row.
                    MasterCRDatabase.objects.using(DB_MASTER).filter(
                        pk=active_obj.pk
                    ).update(is_active=True)
                    continue

                updated_rows.append(new_obj.pk)
                did_write = True

                # CHANGED: record the execution_date so SelectedDateTable can be
                # rebuilt for it post-commit ("create from master if not available").
                if new_obj.execution_date is not None:
                    affected_dates.add(new_obj.execution_date)

            # Register replica sync exactly once, only if we wrote something.
            if did_write:
                _trigger_replica_sync_on_commit(affected_dates)

                # CHANGED: rebuild SelectedDateTable per affected date AFTER commit.
                # sync_selected_date_table opens its own atomic() and must run post-commit;
                # it self-heals (creates rows if the date has none).
                # for d in affected_dates:
                #     transaction.on_commit(
                #         lambda d=d: sync_selected_date_table(d),
                #         using=DB_MASTER,
                #     )
                

    except Exception:
        logger.exception("save_region_cr_details failed")
        return JsonResponse(
            {"ok": False, "message": "Internal error while saving.", "errors": errors},
            status=500,
        )

    ok = len(updated_rows) > 0
    status_code = 200 if ok else 400
    return JsonResponse(
        {
            "ok": ok,
            "updated_rows": updated_rows,
            "errors": errors,
        },
        status=status_code,
    )


# ────────────────────────────────────────────────────────────────
# Helpers: CR History Querysets (READ → replica)
# ────────────────────────────────────────────────────────────────
def _get_history_start_date(range_key):
    today = timezone.localdate()

    if range_key == "1m":
        return today - timedelta(days=30), today
    if range_key == "3m":
        return today - timedelta(days=90), today
    if range_key == "6m":
        return today - timedelta(days=180), today
    if range_key == "12m":
        return today - timedelta(days=365), today

    return None, None


def _get_cr_history_queryset(date_str=None, range_key=None):
    """
    Returns queryset routed to replica.
    Only returns is_active=True records (latest CoW versions).
    """
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None, None, None, "Invalid date format."

        qs = (
            MasterCRDatabase.objects
            .using(DB_REPLICA)
            .filter(execution_date=selected_date, is_active=True)
            .order_by("cr_no")
        )
        return qs, selected_date, selected_date, None

    start_date, end_date = _get_history_start_date(range_key)
    if not start_date:
        return None, None, None, "Invalid history period selected."

    qs = (
        MasterCRDatabase.objects
        .using(DB_REPLICA)
        .filter(
            execution_date__isnull=False,
            execution_date__gte=start_date,
            execution_date__lte=end_date,
            is_active=True,     # Only show latest CoW versions
        )
        .order_by("-execution_date", "cr_no")
    )
    return qs, start_date, end_date, None


# ────────────────────────────────────────────────────────────────
# View: Fetch CR History (READ → replica)
# ────────────────────────────────────────────────────────────────
@require_GET
@login_required(login_url="login")
def fetch_cr_history(request):
    date_str  = request.GET.get("date", "").strip()
    range_key = request.GET.get("range", "").strip()

    qs, start_date, end_date, err = _get_cr_history_queryset(date_str, range_key)
    if err:
        return JsonResponse({"ok": False, "message": err}, status=400)

    rows = list(qs.values(*CR_HISTORY_EXPORT_FIELDS_VIEW))

    for row in rows:
        if row.get("execution_date"):
            row["execution_date"] = row["execution_date"].strftime("%d-%m-%Y")

        if row.get("scheduled_start_date"):
            row["scheduled_start_date"] = timezone.localtime(
                row["scheduled_start_date"]
            ).strftime("%d-%m-%Y %H:%M:%S")

        if row.get("scheduled_end_date"):
            row["scheduled_end_date"] = timezone.localtime(
                row["scheduled_end_date"]
            ).strftime("%d-%m-%Y %H:%M:%S")

    numbered_rows = []
    for idx, row in enumerate(rows, start=1):
        numbered_row = {"sno": idx}
        numbered_row.update(row)
        numbered_rows.append(numbered_row)

    if date_str:
        message = (
            f"Showing {len(numbered_rows)} record(s) "
            f"for {start_date.strftime('%d-%m-%Y')}."
        )
    else:
        range_label_map = {
            "1m":  "Last Month CR",
            "3m":  "Last 3-Months CR",
            "6m":  "Last 6-Months CR",
            "12m": "Last Year CR",
        }
        message = (
            f"Showing {len(numbered_rows)} record(s) for "
            f"{range_label_map.get(range_key, 'selected period')} "
            f"from {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}."
        )

    return JsonResponse({
        "ok": True,
        "rows": numbered_rows,
        "message": message,
    })


# ────────────────────────────────────────────────────────────────
# View: Download CR History (READ → replica)
# ────────────────────────────────────────────────────────────────
@require_GET
@login_required(login_url="login")
def download_cr_history(request):
    date_str  = request.GET.get("date", "").strip()
    range_key = request.GET.get("range", "").strip()

    qs, start_date, end_date, err = _get_cr_history_queryset(date_str, range_key)
    if err:
        return JsonResponse({"ok": False, "message": err}, status=400)

    rows = list(qs.values(*CR_HISTORY_EXPORT_FIELDS))

    numbered_rows = []
    for idx, row in enumerate(rows, start=1):
        numbered_row = {"sno": idx}
        numbered_row.update(row)
        numbered_rows.append(numbered_row)

    df = pd.DataFrame(numbered_rows)

    if not df.empty and "execution_date" in df.columns:
        df["execution_date"] = pd.to_datetime(
            df["execution_date"]
        ).dt.strftime("%d-%m-%Y")

    if not df.empty and "scheduled_start_date" in df.columns:
        df["scheduled_start_date"] = (
            pd.to_datetime(df["scheduled_start_date"], utc=True, errors="coerce")
            .dt.tz_convert(timezone.get_current_timezone())
            .dt.strftime("%d-%m-%Y %H:%M:%S")
        )

    if not df.empty and "scheduled_end_date" in df.columns:
        df["scheduled_end_date"] = (
            pd.to_datetime(df["scheduled_end_date"], utc=True, errors="coerce")
            .dt.tz_convert(timezone.get_current_timezone())
            .dt.strftime("%d-%m-%Y %H:%M:%S")
        )

    header_label_map = {
        "sno":                          "S.No",
        "cr_no":                        "CR No",
        "ms_project":                   "MS Project",
        "execution_date":               "Execution Date",
        "maintenance_window":           "Maintenance Window",
        "region":                       "Region",
        "circle":                       "Circle",
        "priority":                     "Priority",
        "risk":                         "Risk",
        "planning_status":              "Planning Status",
        "activity_status":              "Activity Status",
        "vendor":                       "Vendor",
        "team":                         "Team",
        "activity_description":         "Activity Description",
        "node_details":                 "Node Details",
        "node_count":                   "Node Count",
        "bpms_cr_yes_no":               "BPMS CR (Yes/No)",
        "activity_executor":            "Activity Executor",
        "auditor_name":                 "Auditor Name",
        "reason_for_rollback_cancel":   "Reason For Rollback/Cancel",
        "technical_validator":          "Technical Validator",
        "service_affecting":            "Service Affecting",
        "impact":                       "Impact",
        "test_cases":                   "Test Cases",
        "kpi_name":                     "KPI Name",
        "kpi_spoc_night":               "KPI SPOC Night",
        "kpi_spoc_morning":             "KPI SPOC Morning",
        "inter_domain_activity":        "Inter Domain Activity",
        "inter_domain_kpi_required":    "Inter Domain KPI Required",
        "inter_domain_measuring_kpis":  "Inter Domain Measuring KPIs",
        "activity_type":                "Activity Type",
        "scheduled_start_date":         "Scheduled Start Date",
        "scheduled_end_date":           "Scheduled End Date",
        "protocol":                     "Protocol",
        "execution_type":               "Execution Type",
        "cli_availability":             "CLI Availability",
        "niam_ticket_required":         "NIAM Ticket Required",
        "niam_node_type":               "NIAM Node Type",
        "additional_info":              "Additional Info",
        # CoW metadata columns in export
        # "version":                      "Version",
        # "parent_reference_id":          "Parent Reference ID",
    }

    df = df.rename(columns=header_label_map)

    range_label_map = {
        "1m":  "last_month",
        "3m":  "last_3_months",
        "6m":  "last_6_months",
        "12m": "last_year",
    }

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="CR History")
        worksheet = writer.sheets["CR History"]

        thin_side   = Side(style="thin", color="000000")
        cell_border = Border(
            left=thin_side, right=thin_side,
            top=thin_side, bottom=thin_side
        )
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(
            start_color="0A5EA8", end_color="0A5EA8", fill_type="solid"
        )
        center_align = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )

        max_col = worksheet.max_column
        max_row = worksheet.max_row

        for col_idx in range(1, max_col + 1):
            header_cell = worksheet.cell(row=1, column=col_idx)
            header_cell.font      = header_font
            header_cell.fill      = header_fill
            header_cell.alignment = center_align
            header_cell.border    = cell_border

        for row_idx in range(2, max_row + 1):
            for col_idx in range(1, max_col + 1):
                body_cell = worksheet.cell(row=row_idx, column=col_idx)
                body_cell.alignment = center_align
                body_cell.border    = cell_border

        for col_idx in range(1, max_col + 1):
            column_letter = worksheet.cell(row=1, column=col_idx).column_letter
            max_length = max(
                len(str(worksheet.cell(row=r, column=col_idx).value or ""))
                for r in range(1, max_row + 1)
            )
            worksheet.column_dimensions[column_letter].width = min(
                max(max_length + 4, 12), 40
            )

        worksheet.freeze_panes = "A2"

    output.seek(0)

    if date_str:
        filename = f"Final_Planning_Sheet_{start_date.strftime('%Y%m%d')}.xlsx"
    else:
        filename = (
            f"cr_history_{range_label_map.get(range_key, 'history')}"
            f"_{timezone.localdate().strftime('%Y%m%d')}.xlsx"
        )

    return FileResponse(
        output,
        as_attachment=True,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@require_GET
@login_required(login_url="login")
def fetch_cr_wise_status(request):
    date_str = request.GET.get("date", "").strip()

    if not date_str:
        return JsonResponse({"ok": False, "message": "Date is required."}, status=400)

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"ok": False, "message": "Invalid date format."}, status=400)

    result = list(
        CRWiseStatus.objects.filter(
            execution_date=parsed_date, is_active=True
        ).values(*settings.CR_WISE_STATUS_FIELDS)
    )

    return JsonResponse({
        "ok": True,
        "date": date_str,
        "fields": settings.CR_WISE_STATUS_FIELDS,
        "rows": result,
    }, encoder=DjangoJSONEncoder)


@login_required(login_url="login")
def cr_wise_status(request):
    ctx = _common_context(request)
    ctx["selected_option"] = "cr_wise_status"
    return render(request, "dashboard/cr_wise_status.html", ctx)