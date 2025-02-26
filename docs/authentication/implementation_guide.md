# Authentication Implementation Guide for Developers

## Overview

This guide explains how to implement authentication and authorization in new routes and features. It provides step-by-step instructions, code examples, and best practices for using the authentication module.

## Authentication Module

The authentication module is located in `src/auth/jwt_auth.py` and `src/auth/auth_service.py`. These modules provide the following functionality:

- JWT token validation
- API key fallback authentication
- Tenant ID validation
- Permission checking
- Role-based access control

## Basic Authentication

### Adding Authentication to a Route

To add basic authentication to a route, use the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from ..auth.jwt_auth import get_current_user

router = APIRouter(prefix="/api/v1/your-feature", tags=["your-feature"])

@router.get("/")
async def get_your_feature(
    current_user: dict = Depends(get_current_user)
):
    """Get your feature data."""
    # Access user information
    user_id = current_user["user_id"]
    tenant_id = current_user["tenant_id"]

    # Your implementation here

    return {"message": "Your feature data"}
```

### Tenant ID Validation

To validate and normalize a tenant ID from a request parameter, use the `validate_tenant_id` function:

```python
from fastapi import APIRouter, Depends
from typing import Optional
from ..auth.jwt_auth import get_current_user, validate_tenant_id

@router.get("/your-data")
async def get_your_data(
    tenant_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get your data with tenant isolation."""
    # Validate and normalize tenant ID
    tenant_id = validate_tenant_id(tenant_id, current_user)

    # Use tenant_id for data isolation
    # Your implementation here

    return {"message": "Your data"}
```

## Permission-Based Authorization

### Requiring a Permission

To require a specific permission for a route, use the `require_permission` dependency:

```python
from fastapi import APIRouter, Depends
from ..auth.auth_service import AuthService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/users")
async def get_users(
    user: dict = Depends(AuthService.require_permission("manage_users"))
):
    """Get all users (requires manage_users permission)."""
    # This route will only be accessible to users with the manage_users permission

    # Your implementation here

    return {"message": "Users data"}
```

### Checking Permissions in Code

To check permissions within a route function:

```python
from fastapi import APIRouter, Depends, HTTPException
from ..auth.jwt_auth import get_current_user
from ..auth.auth_service import AuthService

@router.get("/sensitive-data")
async def get_sensitive_data(
    current_user: dict = Depends(get_current_user)
):
    """Get sensitive data with permission check."""
    # Check if user has the required permission
    if not AuthService.has_permission(current_user, "view_reports"):
        raise HTTPException(
            status_code=403,
            detail="Permission denied: view_reports required"
        )

    # Your implementation here

    return {"message": "Sensitive data"}
```

## Multi-Tenant Data Access

### Filtering Data by Tenant

Always filter data by tenant_id to ensure proper tenant isolation:

```python
from fastapi import APIRouter, Depends
from ..auth.jwt_auth import get_current_user, validate_tenant_id
from ..db.sb_connection import db

@router.get("/your-data")
async def get_your_data(
    tenant_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get your data with tenant isolation."""
    # Validate and normalize tenant ID
    tenant_id = validate_tenant_id(tenant_id, current_user)

    # Query data with tenant isolation
    with db.get_cursor() as cur:
        cur.execute("""
            SELECT * FROM your_table
            WHERE tenant_id = %s
        """, (tenant_id,))

        results = cur.fetchall()

    return {"data": results}
```

### Creating Data with Tenant ID

When creating new data, always include the tenant_id:

```python
from fastapi import APIRouter, Depends
from ..auth.jwt_auth import get_current_user, validate_tenant_id
from ..db.sb_connection import db

@router.post("/your-data")
async def create_your_data(
    data: YourDataModel,
    tenant_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create your data with tenant association."""
    # Validate and normalize tenant ID
    tenant_id = validate_tenant_id(tenant_id, current_user)

    # Insert data with tenant association
    with db.get_cursor() as cur:
        cur.execute("""
            INSERT INTO your_table (name, description, tenant_id, created_by)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (data.name, data.description, tenant_id, current_user["user_id"]))

        result = cur.fetchone()
        new_id = result[0] if isinstance(result, tuple) else result.get("id")

    return {"id": new_id, "message": "Data created successfully"}
```

## User and Tenant Management

### Getting User Tenants

To get all tenants a user has access to:

```python
from fastapi import APIRouter, Depends
from ..auth.jwt_auth import get_current_user
from ..auth.auth_service import AuthService

@router.get("/my-tenants")
async def get_my_tenants(
    current_user: dict = Depends(get_current_user)
):
    """Get tenants the current user has access to."""
    tenants = AuthService.get_user_tenants(current_user["user_id"])
    return tenants
```

### Assigning a User to a Tenant

To assign a user to a tenant with a role:

```python
from fastapi import APIRouter, Depends, HTTPException
from ..auth.auth_service import AuthService
from ..models import UserTenantAssign

@router.post("/assign-tenant")
async def assign_user_to_tenant(
    assignment: UserTenantAssign,
    user: dict = Depends(AuthService.require_permission("manage_users"))
):
    """Assign a user to a tenant with a role (requires manage_users permission)."""
    try:
        # Implementation in auth_service.py
        result = await AuthService.assign_user_to_tenant(
            assignment.user_id,
            assignment.tenant_id,
            assignment.role_id
        )
        return {"message": "User assigned to tenant successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Error Handling

### Authentication Errors

Handle authentication errors gracefully:

```python
from fastapi import APIRouter, Depends, HTTPException
from ..auth.jwt_auth import get_current_user

@router.get("/your-data")
async def get_your_data(
    current_user: dict = Depends(get_current_user)
):
    """Get your data with error handling."""
    try:
        # Your implementation here
        return {"message": "Your data"}
    except Exception as e:
        # Log the error
        logging.error(f"Error in get_your_data: {str(e)}")

        # Return appropriate error response
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving data: {str(e)}"
        )
```

### Permission Errors

Handle permission errors with clear messages:

```python
from fastapi import APIRouter, Depends, HTTPException
from ..auth.jwt_auth import get_current_user
from ..auth.auth_service import AuthService

@router.get("/admin-data")
async def get_admin_data(
    current_user: dict = Depends(get_current_user)
):
    """Get admin data with permission check."""
    # Check if user has the required permission
    if not AuthService.has_permission(current_user, "manage_users"):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access admin data. The 'manage_users' permission is required."
        )

    # Your implementation here

    return {"message": "Admin data"}
```

## Testing

### Testing with API Key

For testing endpoints with authentication, use the API key:

```python
def test_your_endpoint():
    """Test your endpoint with API key authentication."""
    headers = {
        "Authorization": "Bearer scraper_sky_2024",
        "Content-Type": "application/json"
    }

    response = client.get("/api/v1/your-feature", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
```

### Mocking Authentication in Tests

For unit tests, mock the authentication dependencies:

```python
from unittest.mock import patch

def test_your_endpoint_with_mock_auth():
    """Test your endpoint with mocked authentication."""
    # Mock the get_current_user dependency
    with patch("src.auth.jwt_auth.get_current_user") as mock_auth:
        # Set up the mock to return a test user
        mock_auth.return_value = {
            "user_id": "test-user-id",
            "tenant_id": "test-tenant-id",
            "name": "Test User",
            "role": "admin"
        }

        # Test the endpoint
        response = client.get("/api/v1/your-feature")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
```

## Best Practices

### 1. Always Use the Authentication Module

All routes should use the authentication module for consistent security:

```python
# ✅ CORRECT: Use the authentication module
from ..auth.jwt_auth import get_current_user

@router.get("/your-data")
async def get_your_data(
    current_user: dict = Depends(get_current_user)
):
    # Implementation
```

```python
# ❌ INCORRECT: Custom authentication logic
@router.get("/your-data")
async def get_your_data(
    authorization: str = Header(None)
):
    # Custom authentication logic
    if authorization != "Bearer my-secret-key":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Implementation
```

### 2. Always Filter Data by Tenant ID

All data access should be filtered by tenant_id:

```python
# ✅ CORRECT: Filter by tenant_id
tenant_id = validate_tenant_id(tenant_id, current_user)
cur.execute("SELECT * FROM your_table WHERE tenant_id = %s", (tenant_id,))
```

```python
# ❌ INCORRECT: No tenant filtering
cur.execute("SELECT * FROM your_table")
```

### 3. Use Permission-Based Authorization

Use permission checks for sensitive operations:

```python
# ✅ CORRECT: Check permissions
if not AuthService.has_permission(current_user, "manage_users"):
    raise HTTPException(status_code=403, detail="Permission denied")
```

```python
# ❌ INCORRECT: No permission check
# Directly perform sensitive operation without checking permissions
```

### 4. Proper Error Handling

Handle authentication and authorization errors gracefully:

```python
# ✅ CORRECT: Proper error handling
try:
    # Implementation
except Exception as e:
    logging.error(f"Error: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
```

```python
# ❌ INCORRECT: No error handling
# Implementation without try/except
```

## Conclusion

By following this guide, you can implement consistent authentication and authorization in all new routes and features. The authentication module provides a robust foundation for secure, multi-tenant operations with proper role-based access control.
