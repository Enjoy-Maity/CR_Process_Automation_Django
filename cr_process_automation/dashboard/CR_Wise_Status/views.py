from django.core.serializers.json import DjangoJSONEncoder
from pathlib import Path
from datetime import datetime
import sqlite3
import sys
import traceback
import threading
from importlib import import_module
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_GET, require_POST
from dashboard.models import MasterCRDatabase
from dashboard.views import _common_context
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from io import BytesIO
from django.utils import timezone
from dashboard.models import CRWiseStatus
from django.conf import settings
from django.forms.models import model_to_dict

CR_WISE_STATUS_EXCLUDED_FIELDS = ("id",)


def _cr_wise_status_columns():
    columns = []
    for field in CRWiseStatus._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue
        if field.name in CR_WISE_STATUS_EXCLUDED_FIELDS:
            continue
        label = field.verbose_name if field.verbose_name else field.name
        columns.append({"name": field.name, "label": str(label)})
    return columns


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

    columns_meta = _cr_wise_status_columns()
    columns = [c["name"] for c in columns_meta]
    field_list = columns if columns else settings.CR_WISE_STATUS_FIELDS

    result = list(
        CRWiseStatus.objects.filter(execution_date=parsed_date, is_active=True).values(*field_list)
    )

    return JsonResponse({
        "ok": True,
        "date": date_str,
        "fields": field_list,
        "columns": columns,
        "column_labels": {c["name"]: c["label"] for c in columns_meta},
        "rows": result,
    }, encoder=DjangoJSONEncoder)

@login_required(login_url="login")
def cr_wise_status(request):
    ctx = _common_context(request)
    ctx["selected_option"] = "cr_wise_status"
    ctx["cr_wise_status_columns"] = _cr_wise_status_columns()
    return render(request, "dashboard/cr_wise_status.html", ctx)

