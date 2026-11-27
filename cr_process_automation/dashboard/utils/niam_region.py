"""Derive a display region for NIAM template rows.

``NIAMTicketGenerationTable`` deliberately has no ``region`` column: its rows
are populated from the RITM input workbook, whose "Total Node Details" column
contains the real node names.  This module maps those node-name prefixes to the
same four region keys used by CR Planning, so the NIAM page can mark rows
read-only without a schema change.  The CR number is used as a fallback when
node text is absent or spans several regions.
"""
import re
from collections import Counter

from dashboard.utils.region_paths import REGION_KEYS

# Prefixes seen in "Total Node Details" / "NIAM Node Name" values, grouped by
# the region of the CR that carried them. Longest prefixes win below, so e.g.
# MAH is matched before MHNA2 and UWN before UW.
NODE_PREFIX_TO_REGION = {
    # South
    "AP": "south", "APU": "south", "APV": "south",
    "CH": "south", "CHN": "south", "CHS": "south",
    "KK": "south", "KL": "south", "KER": "south",
    "TN": "south", "TNS": "south", "TNI": "south",
    "SMPC": "south", "GMPC": "south",
    # East
    "AS": "east", "BH": "east", "BIH": "east", "BHP": "east",
    "NE": "east", "OR": "east", "WB": "east", "KO": "east",
    "KOL": "east", "SIL": "east", "BGR": "east", "INTR": "east",
    # North
    "DL": "north", "NCR": "north", "GGN": "north", "NDL": "north",
    "HR": "north", "HP": "north", "JK": "north", "PB": "north",
    "UPW": "north", "UPE": "north", "UWN": "north", "UWM": "north",
    "UWG": "north", "UEG": "north", "UEV": "north", "UEN": "north",
    "MAN": "north",
    # West
    "GJ": "west", "GUJ": "west", "MH": "west", "MAH": "west",
    "MHNA": "west", "MU": "west", "MUM": "west", "MUS": "west",
    "MUC": "west", "MP": "west", "MPJ": "west", "MPG": "west",
    "RJ": "west",
}

_SORTED_PREFIXES = tuple(
    sorted(NODE_PREFIX_TO_REGION.items(), key=lambda item: len(item[0]), reverse=True)
)
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def normalise_region(value):
    """Return one of the four region keys, or an empty string."""
    key = str(value or "").strip().lower()
    return key if key in REGION_KEYS else ""


def region_from_node_text(*values):
    """Infer a region from node-name text; return '' when ambiguous/unknown."""
    votes = Counter()
    for value in values:
        text = str(value or "").upper()
        for token in _TOKEN_RE.findall(text):
            for prefix, region in _SORTED_PREFIXES:
                if token.startswith(prefix):
                    votes[region] += 1
                    break
    if not votes:
        return ""
    # Only accept a clear winner. Mixed-region node lists are resolved from
    # the CR number instead of guessing.
    winner, count = votes.most_common(1)[0]
    tied = [region for region, votes_for_region in votes.items()
            if votes_for_region == count]
    return winner if len(tied) == 1 else ""


def region_for_niam_row(obj):
    """Return the derived region key for a NIAMTicketGenerationTable row."""
    region = region_from_node_text(
        getattr(obj, "node_details", None),
        getattr(obj, "node_name", None),
    )
    if region:
        return region

    cr_no = str(getattr(obj, "sr_or_change_number", "") or "").strip()
    if not cr_no:
        return ""

    try:
        from dashboard.models import MasterCRDatabase, SelectedDateTable

        region_value = (
            MasterCRDatabase.objects.using("default")
            .filter(cr_no__iexact=cr_no, is_active=True)
            .values_list("region", flat=True)
            .first()
        )
        if not region_value:
            region_value = (
                SelectedDateTable.objects.using("default")
                .filter(cr_no__iexact=cr_no, is_active=True)
                .values_list("region", flat=True)
                .first()
            )
        return normalise_region(region_value)
    except Exception:
        # A missing/unreachable CR record means the row stays read-only.
        return ""
