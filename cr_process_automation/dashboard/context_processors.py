"""Template context shared by every authenticated page."""
import json

from dashboard.utils.region_paths import REGION_KEYS
from dashboard.utils.selected_regions import get_selected_regions


def selected_regions(request):
    """Expose the persisted region selection to templates and inline JS."""
    regions = get_selected_regions(request)
    return {
        "selected_regions": regions,
        "selected_regions_json": json.dumps(regions),
        "all_regions": REGION_KEYS,
    }
