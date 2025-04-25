"""
Core Package

This package contains core functionality used throughout the application.
"""

from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    BaseError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    'BaseError',
    'NotFoundError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'DatabaseError'
]
