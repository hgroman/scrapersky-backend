"""
Health Check Package

This package provides health check functions for various components of the application.
"""

from .db_health import check_database_connection

__all__ = ["check_database_connection"]
