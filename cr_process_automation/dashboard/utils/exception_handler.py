"""
Exception handling utilities for views and services.
"""
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..exceptions import CustomException
import logging
import traceback

logger = logging.getLogger(__name__)


def handle_exceptions(view_func):
    """
    Decorator to handle exceptions in view functions.
    Catches CustomException and general exceptions.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except CustomException as e:
            logger.warning(f"Custom Exception in {view_func.__name__}: {str(e)}")
            return JsonResponse(e.to_dict(), status=e.status_code)
        except Exception as e:
            logger.error(f"Unexpected error in {view_func.__name__}: {str(e)}", exc_info=True)
            return JsonResponse(
                {
                    'ok': False,
                    'title': 'Server Error',
                    'message': str(e),
                    'status_code': 500
                },
                status=500
            )
    return wrapper


def get_or_404(model, **kwargs):
    """
    Wrapper around Django's get_object_or_404 that raises NotFoundException.
    """
    from ..exceptions import NotFoundException
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise NotFoundException(
            f"{model.__name__} not found with parameters: {kwargs}"
        )
        