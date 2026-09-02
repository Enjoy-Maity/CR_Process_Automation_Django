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
        CRWiseStatus.objects.filter(execution_date=parsed_date, is_active=True).values(*settings.CR_WISE_STATUS_FIELDS)
    )
    print(result)

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

