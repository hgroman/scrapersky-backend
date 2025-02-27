"""
Tenant Isolation Module

This module provides functions for tenant isolation in the multi-tenant system.
It ensures that users can only access data for their tenant.
"""

from fastapi import HTTPException, Header
from typing import Dict, Optional
import logging
import uuid

# Configure logging
logger = logging.getLogger(__name__)

# Default tenant ID used as fallback
DEFAULT_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

def is_valid_uuid(val: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, AttributeError, TypeError):
        return False

def validate_tenant_id(tenant_id: Optional[str], current_user: Dict) -> str:
    """
    Validate and normalize a tenant ID.

    Args:
        tenant_id: The tenant ID to validate (can be None)
        current_user: The current user information

    Returns:
        The validated tenant ID

    Raises:
        HTTPException: If the tenant ID is invalid or the user doesn't have access
    """
    # If no tenant ID is provided, use the user's tenant ID
    if not tenant_id:
        return current_user.get("tenant_id", DEFAULT_TENANT_ID)

    # Check if the tenant ID is valid
    if not is_valid_uuid(tenant_id):
        logger.warning(f"Invalid tenant ID format: {tenant_id}")
        raise HTTPException(status_code=400, detail="Invalid tenant ID format")

    # Check if the user has access to the tenant
    user_tenant_id = current_user.get("tenant_id")
    user_role = current_user.get("role", "User")

    # Super admins and API key users can access any tenant
    if user_role == "SUPER_ADMIN" or current_user.get("auth_method") == "api_key":
        logger.info(f"User with role {user_role} accessing tenant {tenant_id}")
        return tenant_id

    # Regular users can only access their own tenant
    if user_tenant_id != tenant_id:
        logger.warning(f"User with tenant {user_tenant_id} attempted to access tenant {tenant_id}")
        raise HTTPException(status_code=403, detail="You don't have access to this tenant")

    return tenant_id

def get_tenant_filter_sql(tenant_id_column: str = "tenant_id") -> str:
    """
    Get the SQL fragment for filtering by tenant ID.

    Args:
        tenant_id_column: The name of the tenant ID column

    Returns:
        SQL fragment for filtering by tenant ID
    """
    return f"{tenant_id_column} = %s"

def apply_tenant_filter(query: str, tenant_id: str, tenant_id_column: str = "tenant_id") -> tuple:
    """
    Apply tenant filtering to a SQL query.

    Args:
        query: The SQL query
        tenant_id: The tenant ID to filter by
        tenant_id_column: The name of the tenant ID column

    Returns:
        Tuple of (modified query, parameters)
    """
    import re
    
    # Use regex to find the position to insert the tenant filter
    # This is safer than string replacement for SQL
    
    # Define regex patterns for SQL clauses
    where_pattern = re.compile(r"\bWHERE\b", re.IGNORECASE)
    group_pattern = re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE)
    order_pattern = re.compile(r"\bORDER\s+BY\b", re.IGNORECASE)
    limit_pattern = re.compile(r"\bLIMIT\b", re.IGNORECASE)
    
    # Check if query already has a WHERE clause
    where_match = where_pattern.search(query)
    if where_match:
        # Insert tenant filter after WHERE
        position = where_match.end()
        modified_query = f"{query[:position]} {tenant_id_column} = %s AND {query[position:]}".strip()
        return (modified_query, [tenant_id])
    
    # Find the first clause after FROM
    group_match = group_pattern.search(query)
    order_match = order_pattern.search(query)
    limit_match = limit_pattern.search(query)
    
    # Find the earliest clause
    matches = [(m.start(), m.group()) for m in [group_match, order_match, limit_match] if m]
    if matches:
        # Sort by position in the query
        matches.sort()
        position, clause = matches[0]
        # Insert WHERE clause before the earliest clause
        modified_query = f"{query[:position]}WHERE {tenant_id_column} = %s {query[position:]}".strip()
        return (modified_query, [tenant_id])
    
    # If no clause is found, add WHERE clause at the end
    modified_query = f"{query} WHERE {tenant_id_column} = %s".strip()
    return (modified_query, [tenant_id])
