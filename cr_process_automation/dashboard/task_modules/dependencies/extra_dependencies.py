import time
import logging
import pandas as pd
from threading import Thread
from zoneinfo import ZoneInfo
from django.conf import settings
from django.db import transaction
from dashboard.models import (
    CRWiseStatus, 
    UserManagement, 
    NIAMCircleTable,
    NIAMProjectNameTable,
    NIAMRequestForTable,
    NIAMAccessTypeTable,
    NIAMActivityNameTable,
    NiamDomainsTable,
    NIAMTicketGenerationTable,
)
from rest_framework.exceptions import APIException
from rest_framework import status
from django_pandas.io import read_frame
from django.utils import timezone
from django.core.management import call_command
from datetime import timedelta
from openpyxl import load_workbook
from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    PatternFill,
    Side,
)
from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


logger = logging.getLogger(__name__)

# Database aliases used for explicit master/replica routing.
DB_MASTER = "default"
DB_REPLICA = "replica"

# Maps the columns produced by the NIAM input template to the fields of
# NIAMTicketGenerationTable.
NIAM_COLUMN_TO_FIELD_MAPPING = {
    "SL. No": "sno",
    "Request Type": "request_type",
    "Node Managed By": "node_managed_by",
    "Subtype": "subtype",
    "UID Type": "uid_type",
    "Policy period": "policy_period",
    "User Type": "user_type",
    "Request IP>10 ?": "request_ip",
    "Business Justification": "business_justification",
    "SR_CR_Start Date-Time": "sr_cr_start_date_time",
    "SR_CR_End Date-Time": "sr_cr_end_date_time",
    "NIAM Access Start Date": "niam_access_start_date_time",
    "NIAM Access END Date": "niam_access_end_date_time",
    "Execution Location": "execution_location",
    "SR OR CHANGE NO": "sr_or_change_number",
    "Activity Title": "activity_title",
    "NIAM Node Name": "node_name",
    "Total Node Details": "node_details",
    "Requested For(email)": "requested_for_email",
    "Activity Name": "activity_name",
    "Project Name": "project_name",
    "Request For": "request_for",
    "Domain": "domain",
    "Access Type": "access_type",
}

# Fields stored as DateTimeField on the model.
NIAM_DATETIME_FIELDS = {
    "sr_cr_start_date_time",
    "sr_cr_end_date_time",
    "niam_access_start_date_time",
    "niam_access_end_date_time",
}

# Duplicate-prevention / update key for a NIAM input template row. A single CR
# produces one row per node, so (execution_date, CR number, node name) is unique.
NIAM_UPSERT_KEY_FIELDS = ("execution_date", "sr_or_change_number", "node_name")

# ---------------------------------------------------------------------------
# NIAM Template Database editable columns
# ---------------------------------------------------------------------------
# The seven RITM_INPUT columns a user fills in on the NIAM Template Database
# page. Each renders as a dropdown; on Save the chosen values are written back
# to both NIAMTicketGenerationTable and the dated RITM workbook. All seven must
# be filled before a row can be saved.
NIAM_EDITABLE_FIELDS = (
    "request_ip",
    "requested_for_email",
    "activity_name",
    "project_name",
    "request_for",
    "domain",
    "access_type",
)

# Reference table/field that supplies the allowed values for the five "list"
# editable columns (the ones the generated workbook validates with Excel
# data-validation dropdowns).
NIAM_DROPDOWN_SOURCES = {
    "project_name": (NIAMProjectNameTable, "project_name"),
    "activity_name": (NIAMActivityNameTable, "activity_name"),
    "access_type": (NIAMAccessTypeTable, "access_type"),
    "request_for": (NIAMRequestForTable, "request_for"),
    "domain": (NiamDomainsTable, "domain"),
}

# Editable columns whose options are fixed rather than table-driven.
NIAM_STATIC_DROPDOWN_OPTIONS = {
    "request_ip": ("Yes", "No"),
}

# Reverse of NIAM_COLUMN_TO_FIELD_MAPPING: model field -> RITM workbook header.
NIAM_FIELD_TO_COLUMN = {
    field: column for column, field in NIAM_COLUMN_TO_FIELD_MAPPING.items()
}


class CustomThread(Thread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None
    ) -> None:
        Thread.__init__(self, group, target, name, args, kwargs)
        self._returnvalue=None

    def run(self):
        if self._target is not None:
            self._returnvalue = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._returnvalue


def cr_wise_status_df_maker(date_: datetime) -> pd.DataFrame:
    # cr_wise_status_df = read_frame( 
    #         CRWiseStatus.objects.filter(execution_date=date_+timedelta(days=1), is_active=True).values(*settings.CR_WISE_STATUS_FIELDS)
    #     )

    query_result = list(
        CRWiseStatus.objects.filter(execution_date=date_+timedelta(days=1), is_active=True).values(*settings.CR_WISE_STATUS_FIELDS)
    )
    cr_wise_status_df = pd.DataFrame(query_result)
    print(f"cr_wise_status_df = \n{cr_wise_status_df}")
    return cr_wise_status_df


def _ts_or_none(value):
    if pd.isna(value):
        return None
    ts = pd.Timestamp(value)
    return ts.to_pydatetime()  # tz-aware datetime, cleanly accepted by Django


def workbook_styling(workbook: str):
    wb = load_workbook(workbook)
    if "Planning_Sheet" in wb.sheetnames:
        ws = wb["Planning_Sheet"]
    
    elif "Planning Sheet" in wb.sheetnames:
        ws = wb["Planning Sheet"]
        
    mail_id_sheet_name = ""
    
    if "Mail Id" in wb.sheetnames:
        mail_id_sheet = wb["Mail Id"]
        mail_id_sheet_name = "Mail Id"
    
    elif "Mail_Id" in wb.sheetnames:
        mail_id_sheet = wb["Mail_Id"]
        mail_id_sheet_name = "Mail_Id"
    
        if mail_id_sheet.sheet_state != 'hidden':
            mail_id_sheet.sheet_state = 'hidden'
    
    planning_status_list = ["Planned", "Discussed", "Swapped"]

    # if "Mail Id" in wb.sheetnames:
    #     cs_core_team_list =

    # cs_core_team_list = ["Mandeep", "Parveen", "Rahul"]
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    header_fill = PatternFill(
        start_color="1F4E79", end_color="1F4E79", fill_type="solid"
    )  # Blue
    header_font = Font(color="FFFFFF", bold=True)  # White bold text

    for cell in ws[1]:  # Row 1 (headers)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = header_font

    for row in ws.iter_rows(
        min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column
    ):
        for cell in row:
            cell.border = thin_border
            cell.alignment = center_align

    for col_num, col in enumerate(ws.columns, 1):
        max_length = 0
        column_letter = get_column_letter(col_num)

        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                continue

        # Set width with 2 pixels padding
        adjusted_width = min(max_length + 2, 50)  # Cap at 50 for readability
        ws.column_dimensions[column_letter].width = adjusted_width

    # ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"

    ws.sheet_view.zoomScale = 80

    helper_col_letter_1 = "ZZ"

    # range_str_1 = (
    #     f"'{mail_id_sheet_name}'!$J$2:$J${get_max_row_in_column(mail_id_sheet, column_index_from_string('J'))}"
    # )
    # range_str_2 =(
    #     f"'{mail_id_sheet_name}'!$M$2:$M${get_max_row_in_column(mail_id_sheet, column_index_from_string('M'))}"
    # )
    # range_str_3 = (
    #     f"'{mail_id_sheet_name}'!$P$2:$P${get_max_row_in_column(mail_id_sheet, column_index_from_string('P'))}"
    # )
    
    
    
    # dv_1 = DataValidation(
    #     type="list",
    #     formula1=range_str_1,
    #     allow_blank=True,
    #     error="Select from list only",
    #     errorTitle="Invalid Executor",
    # )
    # dv_2 = DataValidation(
    #     type="list",
    #     formula1=range_str_2,
    #     allow_blank=True,
    #     error="Select from list only",
    #     errorTitle="Invalid KPI SPOC",
    # )
    # dv_3 = DataValidation(
    #     type="list",
    #     formula1=range_str_3,
    #     allow_blank = True,
    #     error="Select from list only",
    #     errorTitle="Invalid Activity Status"
    # )
    # ws.add_data_validation(dv_1)
    # ws.add_data_validation(dv_2)
    # ws.add_data_validation(dv_3)

    max_row = ws.max_row
    # dv_1.add(f"O2:O{max_row}")
    # dv_2.add(f"Y2:Y{max_row}")
    # dv_2.add(f"X2:X{max_row}")
    # dv_3.add(f"Q2:Q{max_row}")
    
    formula_string_for_planning_status = f'\"{", ".join(planning_status_list)}\"'

    dv_4 = DataValidation(
        type="list",
        formula1=formula_string_for_planning_status,
        allow_blank=True,
        error="Select from list only",
        errorTitle="Invalid Status",
    )
    ws.add_data_validation(dv_4)

    max_row = ws.max_row
    dv_4.add(f"N2:N{max_row}")
    
    dv5 = DataValidation(
        type="list",
        formula1='\"Yes, No\"',
        allow_blank= True,
        error="Select from list only",
        errorTitle="Invalid Input"
    )
    ws.add_data_validation(dv5)
    
    dv5.add(f"AK2:AK{max_row}")
    
    
    
    # node_type_list = f"'{mail_id_sheet_name}'!$P$2:$P${get_max_row_in_column(mail_id_sheet, column_index_from_string('P'))}"
    
    # dv6= DataValidation(
    #     type="list",
    #     formula1=node_type_list,
    #     allow_blank=True,
    #     error="Select from the list only",
    #     errorTitle="Invalid Input"
    #     )
    # ws.add_data_validation(dv6)
    
    # dv6.add(f"AL2:AL{max_row}")
    # ws.column_dimensions[helper_col_letter_2].hidden = True

    wb.save(workbook)
    wb.close()


# def sync_replica_task():
#     # self.update_state(state='RUNNING')
#     # sync_id = self.request.id
#     try:
#         call_command('sync_replica')
#         # cache.set(f'replica_sync_{sync_id}_status', 'complete', None)
#     except Exception as e:
#         # cache.set(f'replica_sync_{sync_id}_status', 'failed', None)
#         raise


def selected_date_df_maker(selected_date_data: QuerySet) -> pd.DataFrame:
    """
    This function creates a pandas DataFrame from the selected_date_data.
   
    Parameters:
        selected_date_data (QuerySet): A queryset of objects, object representing a row of data.    
        The keys of the queryset should match the field names in the settings file.
    Returns:
        pd.DataFrame: A pandas DataFrame with the selected_date_data.
    """
    # selected_date_data = pd.DataFrame(selected_date_data)
    # print(selected_date_data.columns)
    if not isinstance(selected_date_data, list):
        selected_date_data = list(selected_date_data)
    df = pd.DataFrame(selected_date_data)
    df = df.rename(columns=settings.DB_TO_PL_COLUMNS_MAPPING)
    # df = read_frame(selected_date_data).rename(columns=settings.DB_TO_PL_COLUMNS_MAPPING)

    # Normalize datetime columns to naive IST wall-clock for consistent comparisons
    for col in ["Scheduled Start Date+", "Scheduled End Date+"]:
        if col in df.columns:
            s = pd.to_datetime(df[col], errors="coerce")
            if getattr(s.dt, "tz", None) is not None:
                s = s.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
            df[col] = s
    # print(f"selected_date_df = \n{df}")
    return df


def niam_circle_df_maker() -> pd.DataFrame:
    """
    This function creates a pandas DataFrame from the niam_circle_data.
   
    Parameters:
        niam_circle_data (QuerySet): A queryset of objects, object representing a row of data.    
        The keys of the queryset should match the field names in the settings file.
    Returns:
        pd.DataFrame: A pandas DataFrame with the niam_circle_data.
    """
    # niam_circle_data = pd.DataFrame(niam_circle_data)
    # print(niam_circle_data.columns)
    niam_circle_records = list(NIAMCircleTable.objects.all().values())
    df = pd.DataFrame(niam_circle_records)
    df = df.rename(columns=settings.DB_TO_NIAM_CIRCLE_COLUMNS_MAPPING)
    # df = read_frame(niam_circle_data).rename(columns=settings.DB_TO_PL_COLUMNS_MAPPING)

    return df


def _norm_series(series: pd.Series) -> pd.Series:
    """Normalize text for exact-match filters: strip hidden chars + casefold."""
    return (
        series.astype("string")
        .str.replace("\xa0", " ", regex=False)   # non-breaking space
        .str.replace("\u200b", "", regex=False)  # zero-width space
        .str.strip()
        .str.casefold()
    )


def user_email_df_maker() -> pd.DataFrame:
    """
    This function creates a pandas DataFrame from the user_email_data.
   
    Parameters:
        user_email_data (QuerySet): A queryset of objects, object representing a row of data.    
        The keys of the queryset should match the field names in the settings file.
    Returns:
        pd.DataFrame: A pandas DataFrame with the user_email_data.
    """
    # pandas >= 3 no longer expands a QuerySet of model instances into columns,
    # so materialise the row dicts explicitly.
    user_email_data = UserManagement.objects.all()
    df = pd.DataFrame(list(user_email_data.values()))
    # df = df.rename(columns=settings.DB_TO_PL_COLUMNS_MAPPING)
    return df


def _clean_option_values(values) -> list:
    """Normalise a column of option values: strip, drop blanks/NaN, de-dupe."""
    options = []
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text or text.lower() in ("nan", "none"):
            continue
        if text not in options:
            options.append(text)
    return options


def niam_dropdown_options() -> dict:
    """
    Allowed values for every editable NIAM column, keyed by model field.

    Used both to populate the page dropdowns and to validate saved values.
    """
    options = {}
    for field, (model, source_field) in NIAM_DROPDOWN_SOURCES.items():
        options[field] = _clean_option_values(
            model.objects.values_list(source_field, flat=True)
        )
    for field, values in NIAM_STATIC_DROPDOWN_OPTIONS.items():
        options[field] = list(values)
    options["requested_for_email"] = _clean_option_values(
        UserManagement.objects.filter(is_active=True)
        .exclude(email__isnull=True)
        .exclude(email__exact="")
        .values_list("email", flat=True)
    )
    return options


def mail_id_worksheet_df_maker() -> pd.DataFrame:
    """
    Build the hidden "Mail_ID_Worksheet" source frame for a RITM workbook.

    It backs (a) the Change Responsible -> Mail ID lookup used for the requester
    email, (b) the Circle -> NIAM Circle -> NIAM Circle Name mapping used for the
    "User Type" column, and (c) the five dropdown lists the RITM_INPUT sheet
    validates against. The columns have different lengths, so shorter ones are
    padded with None to keep the sheet rectangular.
    """
    change_responsible, mail_ids = [], []
    for name, email in (
        UserManagement.objects.filter(is_active=True)
        .exclude(email__isnull=True)
        .exclude(email__exact="")
        .values_list("employee_name", "email")
        .order_by("employee_name")
    ):
        name = (name or "").strip()
        email = (email or "").strip()
        if name and email:
            change_responsible.append(name)
            mail_ids.append(email)

    circle, niam_circles, circle_names = [], [], []
    for circ, niam_circ, circ_name in (
        NIAMCircleTable.objects.values_list("circle", "niam_circles", "circle_name")
        .order_by("sno")
    ):
        circle.append((circ or "").strip())
        niam_circles.append((niam_circ or "").strip())
        circle_names.append((circ_name or "").strip())

    columns = {
        "Change Responsible": change_responsible,
        "Mail ID": mail_ids,
        "Circle": circle,
        "NIAM Circles": niam_circles,
        "NIAM Circle Name": circle_names,
    }
    for field, (model, source_field) in NIAM_DROPDOWN_SOURCES.items():
        columns[NIAM_FIELD_TO_COLUMN[field]] = _clean_option_values(
            model.objects.values_list(source_field, flat=True)
        )

    height = max((len(values) for values in columns.values()), default=0)
    framed = {
        name: values + [None] * (height - len(values))
        for name, values in columns.items()
    }
    return pd.DataFrame(framed, columns=list(columns.keys()))

def _niam_clean_value(field_name: str, value):
    """
    Normalize a raw DataFrame cell into a value Django can persist on the given
    model field. Empty/NaN cells become None and datetime fields are parsed into
    tz-aware (Asia/Kolkata) datetimes.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if field_name in NIAM_DATETIME_FIELDS:
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return None
        dt = ts.to_pydatetime()
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, ZoneInfo("Asia/Kolkata"))
        return dt

    # Convert numpy scalar types to native Python types for safe persistence.
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            value = value.item()
        except (TypeError, ValueError):
            pass

    if isinstance(value, str):
        value = value.strip()
        if value == "" or value.lower() in ("nan", "nat", "none"):
            return None

    return value


def _niam_key(value) -> str:
    """Build a normalized lookup key component (blank-safe, case-insensitive)."""
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip().casefold()


def _verify_niam_replication(execution_date, timeout: int = 15, interval: float = 1.0):
    """
    Confirm the master rows for the given execution date have streamed to the
    replica. Polls the replica until it matches master or the timeout elapses.

    Returns:
        Tuple[bool, str]: (replicated, message)
    """
    master_count = (
        NIAMTicketGenerationTable.objects.using(DB_MASTER)
        .filter(execution_date=execution_date)
        .count()
    )

    replica_count = None
    last_error = ""
    deadline = time.monotonic() + timeout

    while True:
        try:
            replica_count = (
                NIAMTicketGenerationTable.objects.using(DB_REPLICA)
                .filter(execution_date=execution_date)
                .count()
            )
            if replica_count == master_count:
                return (
                    True,
                    f"Replication in sync (master={master_count}, replica={replica_count}).",
                )
        except Exception as exc:  # replica may be unreachable / read-only not ready
            last_error = str(exc)

        if time.monotonic() >= deadline:
            break
        time.sleep(interval)

    if replica_count is None:
        return False, f"Replica not reachable for verification: {last_error}"
    return (
        False,
        f"Replication lag detected (master={master_count}, replica={replica_count}).",
    )


def niam_data_updater(df: pd.DataFrame, execution_date=None):
    """
    Push the NIAM input template DataFrame into NIAMTicketGenerationTable.

    Behaviour:
        * Prevents duplicate rows by upserting on
          (execution_date, sr_or_change_number, node_name): a CR can produce one
          row per node name.
        * Updates existing rows in place instead of inserting copies.
        * Removes any pre-existing duplicate rows for the same key on master.
        * Verifies PostgreSQL streaming replication after the commit.

    Args:
        df (pd.DataFrame): The NIAM input template DataFrame produced by
            niam_input_initiator.
        execution_date (date | datetime | None): The CR execution date. When
            omitted it is derived from the template's SR/CR start date-time.

    Returns:
        dict: Summary with inserted/updated/skipped counts and replication status.
    """
    summary = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "replicated": None,
        "message": "",
    }

    if df is None or len(df) == 0:
        summary["message"] = "Empty NIAM input template; nothing to push."
        logger.info(summary["message"])
        return summary

    if execution_date is not None:
        execution_date = pd.to_datetime(execution_date).date()
    else:
        start_col = NIAM_COLUMN_TO_FIELD_MAPPING.get("SR_CR_Start Date-Time")
        if start_col in df.columns:
            derived = pd.to_datetime(df[start_col].iloc[0], errors="coerce")
            execution_date = derived.date() if pd.notna(derived) else None

    if execution_date is None:
        summary["message"] = "Execution date unavailable; NIAM rows not pushed."
        logger.warning(summary["message"])
        return summary

    mapped_df = df.rename(columns=NIAM_COLUMN_TO_FIELD_MAPPING)

    valid_fields = {
        field.name
        for field in NIAMTicketGenerationTable._meta.get_fields()
        if getattr(field, "concrete", False) and field.name != "id"
    }

    for key_field in ("sr_or_change_number", "node_name"):
        if key_field not in mapped_df.columns:
            mapped_df[key_field] = None

    value_fields = [
        col
        for col in mapped_df.columns
        if col in valid_fields and col not in NIAM_UPSERT_KEY_FIELDS
    ]

    # Drop duplicate rows inside the incoming dataframe, keeping the last entry.
    mapped_df = mapped_df.drop_duplicates(
        subset=["sr_or_change_number", "node_name"], keep="last"
    )

    try:
        with transaction.atomic(using=DB_MASTER):
            # Clean up any existing duplicate rows for this execution date so the
            # upsert key stays unique (defensive against earlier buggy inserts).
            existing_map = {}
            duplicate_ids = []
            existing_rows = (
                NIAMTicketGenerationTable.objects.using(DB_MASTER)
                .select_for_update()
                .filter(execution_date=execution_date)
                .order_by("id")
            )
            for obj in existing_rows:
                key = (_niam_key(obj.sr_or_change_number), _niam_key(obj.node_name))
                if key in existing_map:
                    duplicate_ids.append(obj.pk)
                else:
                    existing_map[key] = obj

            if duplicate_ids:
                NIAMTicketGenerationTable.objects.using(DB_MASTER).filter(
                    pk__in=duplicate_ids
                ).delete()
                logger.info(
                    "Removed %d duplicate NIAM row(s) for execution_date=%s",
                    len(duplicate_ids),
                    execution_date,
                )

            for row in mapped_df.to_dict(orient="records"):
                key = (
                    _niam_key(row.get("sr_or_change_number")),
                    _niam_key(row.get("node_name")),
                )

                defaults = {
                    field: _niam_clean_value(field, row.get(field))
                    for field in value_fields
                }

                obj = existing_map.get(key)
                if obj is None:
                    NIAMTicketGenerationTable.objects.using(DB_MASTER).create(
                        execution_date=execution_date,
                        sr_or_change_number=row.get("sr_or_change_number"),
                        node_name=row.get("node_name"),
                        **defaults,
                    )
                    summary["inserted"] += 1
                    continue

                changed_fields = []
                for field, value in defaults.items():
                    if getattr(obj, field) != value:
                        setattr(obj, field, value)
                        changed_fields.append(field)

                if changed_fields:
                    obj.save(using=DB_MASTER, update_fields=changed_fields)
                    summary["updated"] += 1
                else:
                    summary["skipped"] += 1

    except Exception as exc:
        logger.exception("Failed to push NIAM input template into the database.")
        summary["message"] = f"Database update failed: {exc}"
        raise

    replicated, replication_message = _verify_niam_replication(execution_date)
    summary["replicated"] = replicated
    summary["message"] = (
        f"NIAM rows pushed for {execution_date}: "
        f"{summary['inserted']} inserted, {summary['updated']} updated, "
        f"{summary['skipped']} unchanged. {replication_message}"
    )
    logger.info(summary["message"])
    return summary

