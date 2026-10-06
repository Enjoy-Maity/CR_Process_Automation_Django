"""Seed NIAM reference/lookup tables on application startup.

Checks NIAMAccessTypeTable, NIAMRequestForTable, NIAMProjectNameTable and
NiamDomainsTable; if any of them is empty, it is filled from the admin-editable
lists defined below. NIAMCircleTable is seeded from NIAM_CIRCLE_SEED, where
the dict key is the circle column value and the value is
(niam_circles, circle_name). Both are maintained by the admin in this module.
"""

import logging

from django.db import connection, transaction

from dashboard.models import (
    NiamDomainsTable,
    NIAMAccessTypeTable,
    NIAMCircleTable,
    NIAMProjectNameTable,
    NIAMRequestForTable,
    NIAMActivityNameTable,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Admin-maintained seed data — edit the lists/dict below as needed.
# ---------------------------------------------------------------------------

# Lists -> NIAMAccessTypeTable.access_type
NIAM_ACCESS_TYPE_SEED = [
    # "ReadOnly",
    # "ReadWrite",
    "ADMIN",
    "READWRITE",
    "ADMIN and READWRITE"
]

# Lists -> NIAMRequestForTable.request_for
NIAM_REQUEST_FOR_SEED = [
    # "NIAM Access",
    "ID Modification",
    "ID Creation",
    "Glass_break"
]

# Lists -> NIAMProjectNameTable.project_name
NIAM_PROJECT_NAME_SEED = [
    # "NIAM",
    "CORE",
    "RAN/MW",
    "Transport"
]

# Lists -> NiamDomainsTable.domain
NIAM_DOMAIN_SEED = [
    # "Transport",
    "RAN",
    "PBN-SDN",
    "PACO"
]

# Lists -> NIAMActivityNameTable.activity_name
NIAM_ACTIVITY_NAME_SEED = [
    # "NIAM Access",
    "Configural-Change: Addition or Creation | Modification | Deletion | Definition",
    "Traffic-Optimization / Shifting / Migration / Offloading",
    "Node-Go Live / Launch / Readiness / Installation / AT",
    "Test-Case Scenarios",
    "Upgrade: Hardware / Software",
    "Health-CheckUp / Backup",
    "Monitoring/Others"
]

# Dict -> NIAMCircleTable
# key   = circle column value (Circle)
# value = (niam_circles, circle_name)
NIAM_CIRCLE_SEED = {
    # "Kolkata": ("NIAM Kolkata", "Kolkata Circle"),
    "BH":  ("BH", "Bihar"),
    "GJ": ("GJ", "Gujarat"),
    "KO": ("WB", "West Bengal"),
    "MH": ("MH", "Maharashtra"),
    "MP": ("MP", "Madhya Pradesh"),
    "MU": ("MUM", "Mumbai"),
    "WB": ("WB", "West Bengal"),
    "OR": ("OR", "Orrisa"),
    "AP": ("AP", "Andhra Pradesh"),
    "AS": ("AS", "Assam"),
    "CH": ("CH", "Chennai"),
    "DL": ("DL", "Delhi"),
    "HP": ("HP", "Himachal Pradesh"),
    "HR": ("HR", "Haryana"),
    "KK": ("KK", "Kerala"),
    "JK": ("JK", "Jammu and Kashmir"),
    "KL": ("Others", "Others"),
    "NE": ("NESA", "North East & Sikkim"),
    "PB": ("PB", "Punjab"),
    "RJ": ("RJ", "Rajasthan"),
    "TN": ("TN", "Tamil Nadu"),
    "UPE": ("UPE", "UP East"),
    "UPW": ("UPW", "UP West"),
}


def _field_max_length(model, field_name):
    try:
        return model._meta.get_field(field_name).max_length
    except Exception:
        return None


def _seed_list_table(model, values, field_name):
    """Bulk-insert `values` into `model` only when the table is empty."""
    if model.objects.exists():
        logger.info("%s already populated; skipping seed.", model.__name__)
        return 0

    max_length = _field_max_length(model, field_name)
    rows = []
    for index, value in enumerate(values):
        value = (value or "").strip()
        if not value:
            continue
        if max_length and len(value) > max_length:
            logger.warning(
                "%s: skipping seed value longer than %s chars: %r",
                model.__name__,
                max_length,
                value[:80],
            )
            continue
        rows.append(model(sno=index + 1, **{field_name: value}))

    if not rows:
        logger.info("%s seed list is empty; nothing to insert.", model.__name__)
        return 0

    model.objects.bulk_create(rows)
    logger.info("Seeded %s row(s) into %s.", len(rows), model.__name__)
    return len(rows)


def _seed_circle_table():
    """Bulk-insert NIAM_CIRCLE_SEED into NIAMCircleTable only when empty."""
    if NIAMCircleTable.objects.exists():
        logger.info("NIAMCircleTable already populated; skipping seed.")
        return 0

    max_circle = _field_max_length(NIAMCircleTable, "circle")
    max_niam = _field_max_length(NIAMCircleTable, "niam_circles")
    max_name = _field_max_length(NIAMCircleTable, "circle_name")

    rows = []
    for index, (circle, (niam_circles, circle_name)) in enumerate(
        NIAM_CIRCLE_SEED.items()
    ):
        circle = (circle or "").strip()
        niam_circles = (niam_circles or "").strip()
        circle_name = (circle_name or "").strip()
        if not circle:
            continue
        too_long = (
            (max_circle and len(circle) > max_circle)
            or (max_niam and len(niam_circles) > max_niam)
            or (max_name and len(circle_name) > max_name)
        )
        if too_long:
            logger.warning(
                "NIAMCircleTable: skipping seed value exceeding field limits: %r",
                circle,
            )
            continue
        rows.append(
            NIAMCircleTable(
                sno=index + 1,
                circle=circle,
                niam_circles=niam_circles,
                circle_name=circle_name,
            )
        )

    if not rows:
        logger.info("NIAM_CIRCLE_SEED is empty; nothing to insert.")
        return 0

    NIAMCircleTable.objects.bulk_create(rows)
    logger.info("Seeded %s row(s) into NIAMCircleTable.", len(rows))
    return len(rows)


def seed_niam_reference_tables():
    """Populate NIAM reference tables when empty. Safe to call on startup."""
    required_tables = [
        NiamDomainsTable._meta.db_table,
        NIAMAccessTypeTable._meta.db_table,
        NIAMCircleTable._meta.db_table,
        NIAMProjectNameTable._meta.db_table,
        NIAMRequestForTable._meta.db_table,
        NIAMActivityNameTable._meta.db_table,
    ]
    existing_tables = connection.introspection.table_names()
    missing = [table for table in required_tables if table not in existing_tables]
    if missing:
        logger.warning(
            "Skipping NIAM reference seed; missing tables: %s", ", ".join(missing)
        )
        return

    seed_jobs = [
        (NIAMAccessTypeTable, NIAM_ACCESS_TYPE_SEED, "access_type"),
        (NIAMRequestForTable, NIAM_REQUEST_FOR_SEED, "request_for"),
        (NIAMProjectNameTable, NIAM_PROJECT_NAME_SEED, "project_name"),
        (NIAMActivityNameTable, NIAM_ACTIVITY_NAME_SEED, "activity_name"),
        (NiamDomainsTable, NIAM_DOMAIN_SEED, "domain"),
    ]
    for model, values, field_name in seed_jobs:
        try:
            with transaction.atomic():
                _seed_list_table(model, values, field_name)
        except Exception:
            logger.exception("Failed to seed %s.", model.__name__)

    try:
        with transaction.atomic():
            _seed_circle_table()
    except Exception:
        logger.exception("Failed to seed NIAMCircleTable.")
