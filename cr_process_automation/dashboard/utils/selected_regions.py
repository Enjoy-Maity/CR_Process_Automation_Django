"""Persistent per-session region selection helpers.

The CR Planning checkboxes are the only place a user changes their region
selection.  Their authoritative value lives in the Django session so it
survives page reloads and navigation between tabs, but is removed by explicit
logout or by the idle-timeout middleware flushing the session.

Region locks remain a separate, short-lived concurrency mechanism; holding a
lock is not what makes a region "selected".
"""
from dashboard.utils.region_paths import REGION_KEYS

SESSION_KEY = "selected_regions"


def parse_regions(raw):
    """Normalise a list/comma string to known region keys, preserving order."""
    if raw is None:
        return []
    items = raw if isinstance(raw, (list, tuple, set)) else str(raw).split(",")
    result = []
    for item in items:
        key = str(item).strip().lower()
        if key in REGION_KEYS and key not in result:
            result.append(key)
    return result


def get_selected_regions(request):
    """Return the regions persisted for the current login session."""
    session = getattr(request, "session", None)
    if session is None:
        return []
    return parse_regions(session.get(SESSION_KEY, []))


def set_selected_regions(request, regions):
    """Replace the persisted selection. An empty list clears it."""
    values = parse_regions(regions)
    session = getattr(request, "session", None)
    if session is None:
        return []
    session[SESSION_KEY] = values
    modified = getattr(session, "modified", None)
    if isinstance(modified, bool):
        session.modified = True
    return values


def effective_regions(request, requested=None):
    """Intersect requested regions with the persisted selection.

    When ``requested`` is omitted, the persisted selection itself is returned.
    Callers that enforce editability must treat an empty result as "no regions
    may be edited", not as "all regions".
    """
    selected = get_selected_regions(request)
    if requested is None:
        return selected
    allowed = set(selected)
    return [region for region in parse_regions(requested) if region in allowed]


def region_is_selected(request, region):
    """True only when *region* is an explicit persisted selection."""
    key = str(region or "").strip().lower()
    return bool(key) and key in get_selected_regions(request)
