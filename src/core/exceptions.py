"""
Core Exceptions

This module defines core exceptions used throughout the application.
"""

from typing import Optional


class BaseError(Exception):
    """Base class for all custom exceptions."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(BaseError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ValidationError(BaseError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class AuthenticationError(BaseError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(BaseError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)


class DatabaseError(BaseError):
    """Raised when a database operation fails."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, status_code=500)
        self.original_error = original_error
