"""
Middleware to handle custom exceptions and convert them to JSON responses.
"""
import json
import traceback
from django.http import JsonResponse
from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareMixin
from .exceptions import CustomException
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

        