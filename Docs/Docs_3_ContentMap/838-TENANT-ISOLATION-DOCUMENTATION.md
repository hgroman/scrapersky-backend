# Tenant Isolation Documentation

## Overview

This document provides comprehensive documentation on the tenant isolation mechanisms in the ScraperSky backend system. Tenant isolation is a critical security feature that ensures data and functionality are properly segregated between different tenant organizations, preventing unauthorized cross-tenant access.

## Sources of Information

The tenant isolation implementation is spread across several key files in the codebase:

1. **JWT Auth Module**: `/src/auth/jwt_auth.py`
   - Contains DEFAULT_TENANT_ID definition
   - Extracts tenant_id from JWT tokens
   - Provides development bypass mechanisms

2. **Dependencies Module**: `/src/auth/dependencies.py`
   - Defines `get_tenant_id` function for header extraction
   - Implements `validate_tenant_access` for tenant-based access control
   - Contains compatibility layer for tenant isolation

3. **Auth Service**: `/src/auth/auth_service.py`
   - Provides simplified tenant-aware authentication functions
   - Maintains tenant context in permission checks

4. **Tenant Middleware**: `/src/middleware/tenant_middleware.py`
   - Adds tenant context to requests
   - Ensures all requests have tenant information

5. **Tenant Isolation**: `/src/auth/tenant_isolation.py`
   - Contains core isolation logic or policies

## Key Components of Tenant Isolation

### 1. Token-Based Tenant Identification

```python
# From jwt_auth.py
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    # ...
    tenant_id = payload.get("tenant_id", DEFAULT_TENANT_ID)

    user = {
        # ...
        "tenant_id": tenant_id,
        # ...
    }
    return user
```

Every JWT token contains a `tenant_id` field that identifies which tenant the authenticated user belongs to. This is the primary mechanism for tenant identification.

### 2. Header-Based Tenant Fallback

```python
# From dependencies.py
async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> str:
    if not x_tenant_id:
        if DEFAULT_TENANT_ID:
            logger.warning(f"No tenant ID provided, using default: {DEFAULT_TENANT_ID}")
            return DEFAULT_TENANT_ID
        else:
            logger.error("No tenant ID provided and no default configured")
            raise HTTPException(status_code=400, detail="Tenant ID is required")
    return x_tenant_id
```

If a tenant ID isn't provided in the JWT token, the system attempts to extract it from the `X-Tenant-ID` HTTP header.

### 3. Tenant Access Validation

```python
# From dependencies.py
def validate_tenant_access(tenant_id: str, current_user: Dict = Depends(get_current_user)) -> Dict:
    # Admin can access any tenant
    if current_user.get("is_admin", False):
        return current_user

    # User can only access their own tenant
    if current_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied to this tenant")

    return current_user
```

This function enforces that a user can only access resources belonging to their own tenant, with an exception for admin users who can access any tenant's resources.

### 4. Default Tenant for Development

```python
# From jwt_auth.py
DEFAULT_TENANT_ID = os.getenv("DEFAULT_TENANT_ID", "550e8400-e29b-41d4-a716-446655440000")
```

For development purposes, a default tenant ID is provided as a fallback to simplify testing and development workflows.

### 5. Tenant Middleware Integration

The tenant middleware ensures that tenant context is properly added to all requests:

```python
# Expected implementation in tenant_middleware.py
class TenantMiddleware:
    async def __call__(self, request: Request, call_next):
        # Extract tenant ID from headers or token
        tenant_id = extract_tenant_id(request)

        # Add tenant context to request state
        request.state.tenant_id = tenant_id

        response = await call_next(request)
        return response
```

## Usage Patterns

### In Routes

```python
@router.get("/items/")
async def get_items(tenant_id: str = Depends(get_tenant_id),
                   current_user: Dict = Depends(validate_tenant_access)):
    # By this point, we know the user has access to this tenant
    # Safe to retrieve and return tenant-specific data
    return {"items": get_items_for_tenant(tenant_id)}
```

### In Services

```python
class DataService:
    async def get_data(self, user_id: str, tenant_id: str):
        # Always include tenant_id in database queries to enforce isolation
        return await db.query(f"SELECT * FROM data WHERE tenant_id = '{tenant_id}' AND user_id = '{user_id}'")
```

## Security Considerations

1. **No Tenant ID Bypass**: All endpoints that access tenant-specific data must validate tenant access or use the tenant isolation mechanism.

2. **Admin Power Usage**: Admin users can access any tenant's data, so admin privileges should be granted cautiously.

3. **Default Tenant Risks**: The DEFAULT_TENANT_ID should only be used in development environments.

4. **Token Validation**: Ensure JWT tokens are properly validated and cannot be tampered with to change the tenant_id.

5. **Database Queries**: All database queries should include tenant_id filters to prevent data leakage.

## How Tenant Isolation Differs from RBAC

Tenant isolation is a completely separate security mechanism from RBAC:

- **RBAC**: Controls what actions a user can perform within their tenant based on roles and permissions.
- **Tenant Isolation**: Controls which tenant's data a user can access, regardless of their permissions.

Even with RBAC removed, tenant isolation remains critical for maintaining proper data segregation between tenants.

## Testing Tenant Isolation

To verify tenant isolation is working correctly:

1. Generate JWT tokens for users in different tenants
2. Attempt to access resources from one tenant while authenticated as a user from another tenant
3. Verify that access is denied with a 403 Forbidden response
4. Verify that admin users can access resources from any tenant

## Future Considerations

1. **Database-Level Isolation**: Consider implementing Row-Level Security (RLS) in the database as an additional layer of protection.

2. **Tenant ID in URL**: Consider standardizing tenant ID placement in API routes for consistency.

3. **Audit Logging**: Implement comprehensive logging of cross-tenant access attempts for security monitoring.

4. **Tenant Context Propagation**: Ensure tenant context is properly propagated through all asynchronous operations.
