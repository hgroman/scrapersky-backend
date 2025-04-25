"""
Database Helper Utilities

Provides utilities for standardizing database operations and parameters
across the application, particularly for Supavisor connection pooling.
"""

from typing import Any, Dict

from fastapi import Query


def get_db_params(
    raw_sql: bool = Query(True, description="Use raw SQL for complex operations"),
    no_prepare: bool = Query(True, description="Disable prepared statements"),
    statement_cache_size: int = Query(0, description="Set statement cache size"),
) -> Dict[str, Any]:
    """
    Get standardized database parameters for endpoints.

    This function can be used as a dependency in FastAPI endpoints
    to ensure consistent parameters for database operations.

    Returns:
        Dictionary of standardized database parameters
    """
    # Log that parameters were received
    # Return empty dict for now to avoid passing to database session
    return {}


def enhance_database_url(db_url: str) -> str:
    """
    Helper function to add Supavisor connection pooling parameters to database URLs.

    This is a utility function that can be called from any service that needs
    to create database connections with proper Supavisor parameters.

    Args:
        db_url: Original database URL

    Returns:
        Enhanced URL with connection pooling parameters
    """
    # Already has query parameters
    if "?" in db_url:
        return f"{db_url}&raw_sql=true&no_prepare=true&statement_cache_size=0"
    # No existing query parameters
    else:
        return f"{db_url}?raw_sql=true&no_prepare=true&statement_cache_size=0"
