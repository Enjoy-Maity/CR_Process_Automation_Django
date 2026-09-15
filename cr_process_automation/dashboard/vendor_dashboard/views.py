# # dashboard/vendor_dashboard/views.py
# # CHANGED: New module for vendor-wise analytics dashboard.

# import logging
# from django.http import JsonResponse
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_GET
# from django.db.models import Count, Q

# from dashboard.models import MasterCRDatabase
# from dashboard.views import _common_context

# logger = logging.getLogger(__name__)

# # CHANGED: read from replica to match your CoW pattern (see Region_CRs/views.py)
# DB_REPLICA = "replica"

# # ─────────────────────────────────────────────────────────────
# # CONFIG — CONFIRM THESE MATCH YOUR ACTUAL DB VALUES
# # If your DB stores e.g. "Successful" instead of "Completed",
# # change the right-hand lists here. Values are matched case-insensitively.
# # ─────────────────────────────────────────────────────────────
# ACTIVITY_STATUS_MAP = {
#     "completed":  ["completed", "success", "successful"],
#     "rollback":   ["rollback", "rolled back", "rolledback"],
#     "cancelled":  ["cancelled", "canceled"],
# }

# EXECUTION_TYPE_MAP = {
#     "automation":         ["automation", "automated", "auto"],
#     "partial_automation": ["partial automation", "partial", "semi-automation"],
#     "manual":             ["manual"],
# }


# def _norm_in(field, values):
#     """Build a case-insensitive OR filter for a field over a list of values."""
#     q = Q()
#     for v in values:
#         q |= Q(**{f"{field}__iexact": v})
#     return q


# def _base_queryset():
#     return MasterCRDatabase.objects.using(DB_REPLICA).filter(is_active=True)


# @login_required(login_url="login")
# def vendor_dashboard_view(request):
#     """Render the vendor-wise analytics dashboard page."""
#     ctx = _common_context(request)
#     ctx["selected_option"] = "dashboard"
#     ctx["page_title"] = "Vendor Wise Dashboard"
#     return render(request, "dashboard/vendor_dashboard.html", ctx)


# @require_GET
# @login_required(login_url="login")
# def vendor_dashboard_data(request):
#     """
#     Return aggregated vendor-wise data as JSON.

#     Optional filters:
#       ?circle=PB        (single circle; blank = all)
#       ?date=YYYY-MM-DD  (single execution date; blank = all)
#     """
#     circle = request.GET.get("circle", "").strip()
#     date_str = request.GET.get("date", "").strip()

#     qs = _base_queryset()

#     if circle:
#         qs = qs.filter(circle__iexact=circle)

#     if date_str:
#         from datetime import datetime
#         try:
#             parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
#             qs = qs.filter(execution_date=parsed)
#         except ValueError:
#             return JsonResponse(
#                 {"ok": False, "message": "Invalid date format. Use YYYY-MM-DD."},
#                 status=400,
#             )

#     # ── Aggregate per (circle, vendor) row (mirrors your sample table) ──
#     rows = []
#     grouped = (
#         qs.values("circle", "vendor")
#         .annotate(total_count=Count("id"))
#         .order_by("circle", "vendor")
#     )

#     for g in grouped:
#         c = g["circle"]
#         v = g["vendor"]
#         row_qs = qs.filter(circle__iexact=c or "", vendor__iexact=v or "")

#         row = {
#             "circle": c or "Unknown",
#             "vendor": v or "Unknown",
#             "total_count": g["total_count"],
#             "completed":  row_qs.filter(_norm_in("activity_status", ACTIVITY_STATUS_MAP["completed"])).count(),
#             "rollback":   row_qs.filter(_norm_in("activity_status", ACTIVITY_STATUS_MAP["rollback"])).count(),
#             "cancelled":  row_qs.filter(_norm_in("activity_status", ACTIVITY_STATUS_MAP["cancelled"])).count(),
#             "automation":         row_qs.filter(_norm_in("execution_type", EXECUTION_TYPE_MAP["automation"])).count(),
#             "partial_automation": row_qs.filter(_norm_in("execution_type", EXECUTION_TYPE_MAP["partial_automation"])).count(),
#             "manual":             row_qs.filter(_norm_in("execution_type", EXECUTION_TYPE_MAP["manual"])).count(),
#         }
#         rows.append(row)

#     # ── Vendor-level totals (for the donut charts) ──
#     vendor_totals = {}
#     for r in rows:
#         vt = vendor_totals.setdefault(r["vendor"], {
#             "vendor": r["vendor"], "total_count": 0,
#             "completed": 0, "rollback": 0, "cancelled": 0,
#             "automation": 0, "partial_automation": 0, "manual": 0,
#         })
#         for k in ("total_count", "completed", "rollback", "cancelled",
#                   "automation", "partial_automation", "manual"):
#             vt[k] += r[k]

#     # ── Overall totals (for KPI cards / top donut) ──
#     overall = {
#         "total_count": sum(r["total_count"] for r in rows),
#         "completed":   sum(r["completed"] for r in rows),
#         "rollback":    sum(r["rollback"] for r in rows),
#         "cancelled":   sum(r["cancelled"] for r in rows),
#         "automation":  sum(r["automation"] for r in rows),
#         "partial_automation": sum(r["partial_automation"] for r in rows),
#         "manual":      sum(r["manual"] for r in rows),
#     }

#     # ── Filter option lists ──
#     circles = list(
#         _base_queryset().exclude(circle__isnull=True).exclude(circle__exact="")
#         .values_list("circle", flat=True).distinct().order_by("circle")
#     )

#     logger.info("vendor_dashboard_data: %d rows (circle=%s, date=%s)",
#                 len(rows), circle or "ALL", date_str or "ALL")

#     return JsonResponse({
#         "ok": True,
#         "rows": rows,
#         "vendor_totals": list(vendor_totals.values()),
#         "overall": overall,
#         "circles": circles,
#         "filters": {"circle": circle, "date": date_str},
#     })

# dashboard/vendor_dashboard/views.py
# Vendor-wise analytics dashboard with date-range filtering & "Combined" vendor bucket.

import logging
from datetime import datetime, timedelta, date

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.db.models import Count, Q

from dashboard.models import MasterCRDatabase
from dashboard.views import _common_context

logger = logging.getLogger(__name__)

# Data source database alias.
#   "default" → master CR database (source of truth, per requirement)
#   "replica" → read-only mirror kept in sync via sqlite backup
DB_SOURCE = "default"

# ── Status / execution-type value mapping (case-insensitive) ──────────
ACTIVITY_STATUS_MAP = {
    "completed":  ["completed", "success", "successful"],
    "rollback":   ["rollback", "rolled back", "rolledback"],
    "cancelled":  ["cancelled", "canceled"],
}

EXECUTION_TYPE_MAP = {
    "automation":         ["automation", "automated", "auto"],
    "partial_automation": ["partial automation", "partial", "semi-automation"],
    "manual":             ["manual"],
}

# ── Known single-vendor names (lowercase). Anything else → "Combined" ─
# Any value that is blank, contains a multi-vendor separator, or is not in
# this known set is rolled into the single "Combined" bucket.
KNOWN_VENDORS = {
    "ericsson", "cisco", "nokia", "huawei",
    "zte", "juniper", "samsung", "alcatel", "alcatel-lucent", "lucent",
    "ciena", "adtran", "fiberhome", "nuage", "ribbon",
}

# Multi-vendor separator characters
_MULTI_VENDOR_SEPS = (",", "/", "&", "+")

# Range keys mirror the CR History page: 1m | 3m | 6m | 12m
RANGE_LABELS = {
    "1m":  "Last Month CR",
    "3m":  "Last 3-Months CR",
    "6m":  "Last 6-Months CR",
    "12m": "Last Year CR",
}


# ── Helpers ───────────────────────────────────────────────────────────
def _ci_in(field: str, values: list[str]) -> Q:
    """Case-insensitive OR filter."""
    q = Q()
    for v in values:
        q |= Q(**{f"{field}__iexact": v})
    return q


def _base_queryset():
    return MasterCRDatabase.objects.using(DB_SOURCE).filter(is_active=True)


def _lookup_keyword(value, mapping):
    """
    Return the mapping key whose keyword list contains the lowered value,
    or None when the value matches no known keyword.
    """
    v = (value or "").strip().lower()
    for key, words in mapping.items():
        if v in words:
            return key
    return None


def _period_label(date_str: str = "", range_key: str = "") -> str:
    """Human-readable label for the active filter period."""
    if date_str:
        return f"Specific date: {date_str}"
    if range_key:
        return f"{RANGE_LABELS.get(range_key, range_key)}"
    return "All time"


def _classify_vendor(raw_vendor: str) -> str:
    """
    Return a display-friendly vendor name.
    If the value contains multiple vendors (separators like , / & +)
    or is not in the KNOWN_VENDORS set, return 'Combined'.
    """
    v = (raw_vendor or "").strip()
    v_lower = v.lower()

    if not v:
        return "Combined"

    # Check for multi-vendor separators
    for sep in _MULTI_VENDOR_SEPS:
        if sep in v:
            return "Combined"

    if " and " in v_lower:
        return "Combined"

    if v_lower not in KNOWN_VENDORS:
        return "Combined"

    return v.title()  # e.g. "ericsson" → "Ericsson"


def _parse_date_filter(date_str: str = "", range_key: str = ""):
    """
    Return (start_date, end_date, error_message).
    Supports:
      date=YYYY-MM-DD          → single-day filter
      range=1m | 3m | 6m | 12m → rolling window ending today
    If neither supplied → (None, None, None) meaning "all time".
    """
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            return dt, dt, None
        except ValueError:
            return None, None, "Invalid date format. Use YYYY-MM-DD."

    if range_key:
        today = date.today()
        mapping = {"1m": 30, "3m": 90, "6m": 180, "12m": 365}
        days = mapping.get(range_key)
        if not days:
            return None, None, "Invalid range. Use 1m, 3m, 6m, or 12m."
        return today - timedelta(days=days), today, None

    return None, None, None  # all time


def _apply_date_filter(qs, date_str: str = "", range_key: str = ""):
    """Apply date / range filter to a queryset. Returns (qs, error_or_None)."""
    start, end, err = _parse_date_filter(date_str, range_key)
    if err:
        return qs.none(), err
    if start and end:
        if start == end:
            return qs.filter(execution_date=start), None
        return qs.filter(execution_date__gte=start, execution_date__lte=end), None
    return qs, None  # all time


def transform_to_vendor_rows(qs):
    """
    Transform raw MasterCRDatabase rows (active CoW versions) from the master
    CR database into the vendor-wise dashboard *data template*.

    Output contract — one row per (circle, display-vendor):

        {
            "circle": str,                # circle code, "Unknown" if blank
            "vendor": str,                # "Ericsson" | "Cisco" | ... | "Combined"
            "total_count": int,           # total CRs for this group
            "completed": int,             # activity_status → completed/success
            "rollback": int,              # activity_status → rollback/rolled back
            "cancelled": int,             # activity_status → cancelled/canceled
            "automation": int,            # execution_type → automation/automated/auto
            "partial_automation": int,    # execution_type → partial/semi-automation
            "manual": int,                # execution_type → manual
        }

    Vendor bucketing:
      - blank vendor                     → "Combined"
      - multi-vendor values (have any of
        `,` `/` `&` `+` or " and ")       → "Combined"
      - single vendor names NOT in
        KNOWN_VENDORS set                 → "Combined"
      - otherwise the single, known
        vendor (title-cased)              → e.g. "Ericsson"

    Returns list[dict] of per-(circle, display_vendor) rows.
    """
    # First pass: get raw (circle, vendor) groups
    raw_groups = (
        qs.values("circle", "vendor")
          .annotate(total_count=Count("id"))
          .order_by("circle", "vendor")
    )

    # Accumulator keyed by (circle, display_vendor)
    buckets: dict[tuple[str, str], dict] = {}

    STATUS_Q = {k: _ci_in("activity_status", v) for k, v in ACTIVITY_STATUS_MAP.items()}
    EXEC_Q   = {k: _ci_in("execution_type", v) for k, v in EXECUTION_TYPE_MAP.items()}

    for g in raw_groups:
        raw_circle = (g["circle"] or "").strip() or "Unknown"
        raw_vendor = (g["vendor"] or "").strip()
        display_vendor = _classify_vendor(raw_vendor)

        if raw_circle == "Unknown":
            circle_filter = Q(circle__isnull=True) | Q(circle="")
        else:
            circle_filter = Q(circle__iexact=raw_circle)

        row_qs = qs.filter(circle_filter, vendor__iexact=raw_vendor)

        counts = {
            "completed":          row_qs.filter(STATUS_Q["completed"]).count(),
            "rollback":           row_qs.filter(STATUS_Q["rollback"]).count(),
            "cancelled":          row_qs.filter(STATUS_Q["cancelled"]).count(),
            "automation":         row_qs.filter(EXEC_Q["automation"]).count(),
            "partial_automation": row_qs.filter(EXEC_Q["partial_automation"]).count(),
            "manual":             row_qs.filter(EXEC_Q["manual"]).count(),
        }

        key = (raw_circle, display_vendor)
        if key not in buckets:
            buckets[key] = {
                "circle": raw_circle,
                "vendor": display_vendor,
                "total_count": 0,
                "completed": 0, "rollback": 0, "cancelled": 0,
                "automation": 0, "partial_automation": 0, "manual": 0,
            }

        buckets[key]["total_count"] += g["total_count"]
        for k, v in counts.items():
            buckets[key][k] += v

    return list(buckets.values())


def vendor_circle_heatmap(qs):
    """
    Build a vendor × circle CR-count matrix for a heatmap.

    Returns:
        {
            "vendors":  [display_vendor, ...],          # matrix rows
            "circles":  [circle_code, ...],             # matrix columns
            "data":     [[count, ...], ...],            # data[v][c]
            "max_count": int,                           # colour-scaling ceiling
        }
    """
    from collections import defaultdict

    buckets: dict[tuple[str, str], int] = defaultdict(int)
    raw_groups = (
        qs.values("circle", "vendor").annotate(total_count=Count("id"))
    )

    for g in raw_groups:
        circle = (g["circle"] or "").strip() or "Unknown"
        vendor = _classify_vendor(g["vendor"])
        buckets[(vendor, circle)] += g["total_count"]

    vendors = sorted({v for v, _ in buckets})
    circles = sorted({c for _, c in buckets})
    data = [
        [buckets.get((v, c), 0) for c in circles]
        for v in vendors
    ]

    return {
        "vendors": vendors,
        "circles": circles,
        "data": data,
        "max_count": max((buckets.get((v, c), 0) for v in vendors for c in circles), default=0),
    }


def monthly_cr_series(qs):
    """
    Aggregate the filtered queryset by calendar month (execution_date).

    Used as the histogram input:

        [{"label": "Jan 2026", "total_count": int,
          "completed": int, "rollback": int, "cancelled": int}, ...]

    Missing months between the first and last CR date are filled with zero
    counts so the histogram renders a continuous timeline.
    """
    from collections import defaultdict

    buckets: dict[tuple[int, int], dict] = defaultdict(lambda: {
        "label": "",
        "total_count": 0, "completed": 0, "rollback": 0, "cancelled": 0,
    })

    for rec in qs.values("execution_date", "activity_status"):
        d = rec.get("execution_date")
        if not d:
            continue
        key = (d.year, d.month)
        b = buckets[key]
        if not b["label"]:
            b["label"] = d.strftime("%b %Y")
        b["total_count"] += 1
        bucket = _lookup_keyword(rec.get("activity_status"), ACTIVITY_STATUS_MAP)
        if bucket:
            b[bucket] += 1

    if not buckets:
        return []

    # Fill gaps so the histogram timeline is continuous.
    first_y, first_m = min(buckets)
    last_y, last_m = max(buckets)

    series = []
    y, m = first_y, first_m
    while (y, m) <= (last_y, last_m):
        entry = buckets[(y, m)]
        entry["year"], entry["month"] = y, m
        series.append(entry)
        m += 1
        if m == 13:
            m = 1
            y += 1

    return series


# ── Views ─────────────────────────────────────────────────────────────
@login_required(login_url="login")
def vendor_dashboard_view(request):
    """Render the vendor-wise analytics dashboard page."""
    ctx = _common_context(request)
    ctx["selected_option"] = "dashboard"
    ctx["page_title"] = "Vendor Wise Dashboard"
    return render(request, "dashboard/vendor_dashboard.html", ctx)


@require_GET
@login_required(login_url="login")
def vendor_dashboard_data(request):
    """
    GET /api/dashboard/vendor-wise-data/

    Query params (all optional, mutually-exclusive date vs range):
      circle  = <circle_code>            (filter by circle)
      date    = YYYY-MM-DD               (single execution date)
      range   = 1m | 3m | 6m | 12m      (rolling window)
    """
    circle    = request.GET.get("circle", "").strip()
    date_str  = request.GET.get("date", "").strip()
    range_key = request.GET.get("range", "").strip()

    qs = _base_queryset()

    # ── Date / range filter ───────────────────────────────────────
    qs, err = _apply_date_filter(qs, date_str=date_str, range_key=range_key)
    if err:
        return JsonResponse({"ok": False, "message": err}, status=400)

    # ── Circle filter ─────────────────────────────────────────────
    if circle:
        qs = qs.filter(circle__iexact=circle)

    # ── Transform to sample-table rows (with Combined bucket) ─────
    rows = transform_to_vendor_rows(qs)
    heatmap = vendor_circle_heatmap(qs)
    monthly_series = monthly_cr_series(qs)

    # ── Vendor-level totals (for donut charts) ────────────────────
    vendor_totals: dict[str, dict] = {}
    overall = {
        "total_count": 0, "completed": 0, "rollback": 0, "cancelled": 0,
        "automation": 0, "partial_automation": 0, "manual": 0,
    }

    SUM_KEYS = tuple(overall.keys())

    for r in rows:
        vt = vendor_totals.setdefault(r["vendor"], {
            "vendor": r["vendor"],
            **{k: 0 for k in SUM_KEYS},
        })
        for k in SUM_KEYS:
            vt[k] += r[k]
            overall[k] += r[k]

    # ── Circle list for dropdown ──────────────────────────────────
    circles = list(
        _base_queryset()
        .exclude(circle__isnull=True).exclude(circle__exact="")
        .values_list("circle", flat=True).distinct().order_by("circle")
    )

    logger.info(
        "vendor_dashboard_data: %d rows (circle=%s, date=%s, range=%s)",
        len(rows), circle or "ALL", date_str or "ALL", range_key or "ALL",
    )

    return JsonResponse({
        "ok": True,
        "rows": rows,
        "vendor_totals": list(vendor_totals.values()),
        "overall": overall,
        "circles": circles,
        "heatmap": heatmap,
        "monthly_series": monthly_series,
        "filters": {"circle": circle, "date": date_str, "range": range_key},
        "filter_label": _period_label(date_str, range_key),
    })

