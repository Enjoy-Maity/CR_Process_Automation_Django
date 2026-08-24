"""
Custom exception classes for the CR Process Automation application.
"""

class CustomException(Exception):
    """
    Base custom exception class for application-specific errors.
    Stores both title and message for better error reporting.
    """
    def __init__(self, title: str, message: str, status_code: int = 400):
        self.title = title
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.title}: {self.message}"

    def to_dict(self):
        """Convert exception to dictionary for JSON response."""
        return {
            'ok': False,
            'title': self.title,
            'message': self.message,
            'status_code': self.status_code
        }


class ValidationException(CustomException):
    """Raised when data validation fails."""
    def __init__(self, message: str, title: str = "Validation Error"):
        super().__init__(title, message, status_code=400)


class NotFoundException(CustomException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str, title: str = "Not Found"):
        super().__init__(title, message, status_code=404)


class TaskExecutionException(CustomException):
    """Raised when task execution fails."""
    def __init__(self, message: str, title: str = "Task Execution Error"):
        super().__init__(title, message, status_code=500)


class AuthenticationException(CustomException):
    """Raised when authentication fails."""
    def __init__(self, message: str, title: str = "Authentication Error"):
        super().__init__(title, message, status_code=401)


class PermissionException(CustomException):
    """Raised when user doesn't have permission."""
    def __init__(self, message: str, title: str = "Permission Denied"):
        super().__init__(title, message, status_code=403)


class DatabaseException(CustomException):
    """Raised when database operations fail."""
    def __init__(self, message: str, title: str = "Database Error"):
        super().__init__(title, message, status_code=500)


class DuplicateRecordException(CustomException):
    """Raised when trying to create a duplicate record."""
    def __init__(self, message: str, title: str = "Duplicate Record"):
        super().__init__(title, message, status_code=409)
        