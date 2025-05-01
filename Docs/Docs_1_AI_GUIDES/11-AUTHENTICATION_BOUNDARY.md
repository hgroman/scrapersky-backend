# Authentication Boundary Guide

## Critical Principle

JWT authentication must ONLY happen at the API router level. This is a STRICT boundary that must never be crossed.

## Why This Matters

Authentication boundary violations are a common cause of security issues, technical debt, and code complexity. By maintaining a strict authentication boundary, we achieve:

1. **Clear Security Model**: Authentication is handled consistently in one place
2. **Separation of Concerns**: Services focus on business logic without authentication concerns
3. **Testability**: Services can be tested independently of authentication
4. **Maintainability**: Authentication changes only affect routers, not the entire codebase
5. **Performance**: Prevents redundant authentication checks deep in the call stack

## Current Authentication System

The ScraperSky backend now uses:

- **JWT authentication only** - validates user identity
- **No RBAC system** - the entire RBAC system has been removed
- **No tenant isolation** - tenant isolation has been completely removed
- **No permission checks** - no permission or feature checks exist

## Correct Implementation

### Router Layer (JWT-aware)

```python
@router.post("/resource", response_model=ResourceResponse)
async def create_resource(
    request: ResourceRequest,
    current_user: dict = Depends(get_current_user),  # JWT validation only
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new resource."""
    try:
        # 1. Router extracts user_id from the JWT token (via dependency)
        user_id = current_user.get("id")

        # 2. Router owns the transaction
        async with session.begin():
            # 3. Router passes user_id (not the token) to the service
            result = await resource_service.create_resource(
                session=session,
                data=request.dict(),
                user_id=user_id  # Only pass the ID, not the token
            )

            return ResourceResponse(**result)
    except Exception as e:
        handle_error(e)
```

### Service Layer (Authentication-agnostic)

```python
async def create_resource(
    session: AsyncSession,
    data: dict,
    user_id: str
) -> dict:
    """Create a resource - NO authentication here!"""
    # Service uses the user_id but has no knowledge of JWT
    # Service is authentication-agnostic
    resource = Resource(
        **data,
        created_by=user_id  # Uses ID directly, no JWT validation
    )
    session.add(resource)
    # Use session but don't commit (router owns transaction)
    return resource.to_dict()
```

## Common Anti-patterns to Avoid

### ❌ Accessing JWT in Services

```python
# BAD - Service should not access JWT
async def create_resource(session: AsyncSession, data: dict, token: str):
    # Decoding JWT in a service violates the boundary
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_id = payload.get("sub")
    # ...
```

### ❌ Passing Authentication State Through Multiple Layers

```python
# BAD - Propagating auth state through many layers
async def complex_operation(session: AsyncSession, user: dict):
    # Passing complete user dict with auth info violates boundary
    result_a = await subsystem_a.process(session, user)
    result_b = await subsystem_b.process(session, user)
    # ...
```

### ❌ Authentication Logic in Database Models

```python
# BAD - Model should not contain auth logic
class Resource(Base):
    # ...
    def is_accessible_by(self, token: str) -> bool:
        # Models should never verify tokens or contain auth logic
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        # ...
```

## WHAT TO DO IF YOU ENCOUNTER RBAC OR TENANT CODE

If you encounter any of the following in the codebase:

- Permission checks (`require_permission`, `has_permission`)
- Feature flag checks (`require_feature_enabled`)
- Role level checks (`require_role_level`)
- Tenant isolation code (tenant_id filtering, etc.)
- The constants file `src.constants.rbac`
- The utils file `src.utils.permissions`

**STOP IMMEDIATELY** and:

1. Note the location of the code
2. Report it to the project maintainer
3. Do not modify the code until receiving guidance

## Testing Implications

When following this boundary:

1. **Service tests don't need JWT tokens** - just pass a user ID
2. **Router tests must include authentication** - test with real tokens
3. **Use test_user information** from our [Test User Guide](/AI_GUIDES/10-TEST_USER_INFORMATION.md)

## Migration Path

If you find authentication logic outside routers:

1. Move JWT validation to the router level
2. Pass only user IDs to services
3. Remove any JWT dependencies from services and models
4. Update tests to reflect the new boundary

## Additional Resources

- [10-TEST_USER_INFORMATION.md](/AI_GUIDES/10-TEST_USER_INFORMATION.md) - For testing with real credentials
- [07-DATABASE_CONNECTION_STANDARDS.md](/AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md) - For database connection patterns
- [08-RBAC_SYSTEM_REMOVED.md](/AI_GUIDES/08-RBAC_SYSTEM_REMOVED.md) - For details on RBAC removal
- [09-TENANT_ISOLATION_REMOVED.md](/AI_GUIDES/09-TENANT_ISOLATION_REMOVED.md) - For details on tenant isolation removal

## Critical Standardization: UUID Format in Authentication

### UUID Standards for Authentication Boundaries

When implementing the authentication boundary, it is **critical** that all user identifiers returned from authentication functions use proper UUID formats, even for development or test tokens. This ensures consistency across system boundaries and prevents type errors when these identifiers are used in database operations.

### Recent Change: Development Admin ID (2025-03-26)

A significant change was made on March 26, 2025 that developers should be aware of:

**Change made**: The hardcoded development token authentication in `src/auth/jwt_auth.py` was modified to return a standard UUID format ('00000000-0000-0000-0000-000000000000') instead of the previous string format ('dev-admin-id').

**Reason for change**: The string 'dev-admin-id' was causing database errors when used with tables that have UUID-typed columns. This violated our UUID standardization principles and created inconsistency between authentication and data persistence layers.

**Previous implementation**:

```python
# Old implementation (before 2025-03-26)
if token == "scraper_sky_2024":
    # Special case for development - hardcoded token
    return {
        "user_id": "dev-admin-id",  # String ID, not a UUID
        "id": "dev-admin-id",
        "tenant_id": DEFAULT_TENANT_ID,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
```

**New implementation**:

```python
# New implementation (after 2025-03-26)
if token == "scraper_sky_2024":
    # Special case for development - hardcoded token with proper UUID
    return {
        "user_id": "00000000-0000-0000-0000-000000000000",  # Standard UUID format
        "id": "00000000-0000-0000-0000-000000000000",
        "tenant_id": DEFAULT_TENANT_ID,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
```

### Potential Impact

Any code that specifically relied on or checked for the string 'dev-admin-id' will need to be updated. This includes:

- Tests that assert the specific ID value
- Frontend code that might have hardcoded expectations
- Logging or analytics that filtered for this specific ID
- Authorization rules that treated this ID specially

### Transitional Approach (If Needed)

If your component relies on the previous behavior, consider:

1. Update your code to work with the UUID format (preferred approach)
2. Implement detection of both formats during a transition period
3. For critical cases where changes cannot be immediate, discuss with the architecture team about potential workarounds

### Verification

Verify your authentication boundary implementation by checking that:

1. All user IDs returned from authentication functions are valid UUID strings
2. Development/test tokens return proper UUIDs, not string identifiers
3. Your database properly accepts these UUIDs in UUID-typed columns
