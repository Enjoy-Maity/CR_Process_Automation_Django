"""
Middleware to handle custom exceptions and convert them to JSON responses.
"""
import json
import traceback
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareMixin

from .exceptions import CustomException
from .utils.task_runtime import RUN_REGISTRY
import logging

logger = logging.getLogger(__name__)


class CustomExceptionMiddleware(MiddlewareMixin):
    """
    Middleware to catch CustomException and other exceptions,
    and convert them to appropriate JSON responses.
    """
    
    def process_exception(self, request, exception):
        # Log the exception
        logger.error(f"Exception: {type(exception).__name__}", exc_info=True)
        
        # Handle CustomException
        if isinstance(exception, CustomException):
            return JsonResponse(
                exception.to_dict(),
                status=exception.status_code
            )
        
        # Handle other exceptions
        return JsonResponse(
            {
                'ok': False,
                'title': 'Server Error',
                'message': 'An unexpected error occurred. Please try again later.',
                'status_code': 500
            },
            status=500
        )


class SessionIdleTimeoutMiddleware:
    """
    Expire a login after a period of real inactivity.

    Dashboard polling must NOT refresh the idle clock, otherwise an open tab
    keeps the session alive forever. Only non-polling requests do.
    """

    # These endpoints are polled by the browser; they must not keep a session alive.
    NON_ACTIVITY_PATHS = {
        '/api/task/dashboard-data/',
        '/api/task-dashboard-data/',
        '/health',
        '/health/',
        '/night-execution/status-result/',
        '/api/replica-sync-status/',
        '/api/region-locks/status/',
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self.idle_seconds = int(
            getattr(settings, 'USER_IDLE_TIMEOUT_SECONDS', 30 * 60)
        )

    def __call__(self, request):
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            now = timezone.now()
            raw_last = request.session.get('last_activity')
            last = parse_datetime(raw_last) if raw_last else None

            if last and now - last > timedelta(seconds=self.idle_seconds):
                RUN_REGISTRY.clear_all_for_user(user.id)
                # Idle expiry must clear the same state as explicit logout:
                # persisted region selections (in the session) and region locks.
                try:
                    from .models import RegionLock

                    RegionLock.objects.using("default").filter(
                        locked_by_id=user.id
                    ).delete()
                except Exception:
                    logger.exception("Failed to release region locks on idle timeout")
                logout(request)  # flushes the session and logs the user out

            # logout() makes request.user anonymous, so refresh only if still
            # authenticated. Otherwise an expired session would immediately
            # create a fresh anonymous one with a last_activity stamp.
            if (
                request.user.is_authenticated
                and request.path not in self.NON_ACTIVITY_PATHS
            ):
                request.session['last_activity'] = now.isoformat()
                request.session.set_expiry(self.idle_seconds)

        return self.get_response(request)
