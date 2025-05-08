# RBAC SYSTEM REMOVED

This document outlines the authentication system in ScraperSky after the complete removal of Role-Based Access Control (RBAC). Understanding this change is crucial for all authentication-related work on the project.

## 1. AUTHENTICATION SYSTEM ARCHITECTURE

### Current Authentication Architecture

```
+----------------+    
|     JWT        |    
| AUTHENTICATION |    
+----------------+    
  Validates user
  identity only
```

The system now has **JWT authentication only**:

- JWT tokens validate user identity
- No role checks
- No permission checks
- No feature flags tied to permissions
- No tenant isolation

### Previous RBAC Architecture (REMOVED)

```
+----------------+    +----------------+    +----------------+
|     ROLES      | -> |  PERMISSIONS   | -> |    FEATURES    |
+----------------+    +----------------+    +----------------+
  e.g. "admin"         e.g. "access_        e.g. "contentmap"
       "user"          sitemap_scanner"
```

The **entire RBAC system** has been completely removed from the codebase.

## 2. AUTHENTICATION METHODS

### Current Authentication Methods

```python
# In route handlers - only authentication, no permission checking
current_user = Depends(get_current_user)

# JWT validation only
# No permission checking
# No feature flag checking
```

### Removed RBAC Methods

The following methods have been removed and should NOT be used:

```python
# DO NOT USE - These methods no longer exist
require_permission()      # REMOVED
has_permission()          # REMOVED
require_feature_enabled() # REMOVED
require_role_level()      # REMOVED
check_tab_permission()    # REMOVED
require_tab_permission()  # REMOVED
has_tab_permission()      # REMOVED
```

## 3. AUTHENTICATION IN ROUTERS

### Correct Implementation Example

```python
@router.post("/scan", response_model=SitemapScrapingResponse)
async def scan_domain(
    request: SitemapScanRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    # No permission checks - only JWT authentication
    
    # Route implementation...
    result = await sitemap_service.scan_domain(
        session=session,
        domain=request.domain,
        # No tenant_id needed
    )
    
    return result
```

## 4. DATABASE QUERIES WITHOUT TENANT ISOLATION

```python
# No tenant filtering in queries
result = await session.execute(
    select(Model).where(
        Model.id == model_id
        # No tenant_id filter
    )
)

# Model creation without tenant_id
new_item = Model(
    id=str(uuid.uuid4()),
    name="Example",
    # No tenant_id field
)
session.add(new_item)
```

## 5. JWT AUTHENTICATION LOCATION

JWT authentication is defined in:

```python
from src.auth.jwt_auth import (
    get_current_user,       # FastAPI dependency for verifying JWT
    create_access_token,    # Create JWT token
)
```

## 6. WHAT TO DO IF YOU ENCOUNTER RBAC CODE

If you encounter any of the following in the codebase:

- Permission checks (`require_permission`, `has_permission`)
- Feature flag checks (`require_feature_enabled`)
- Role level checks (`require_role_level`)
- Tab permission checks
- Tenant isolation code
- The constants file `src.constants.rbac`
- The utils file `src.utils.permissions`

**STOP IMMEDIATELY** and:

1. Note the location of the code
2. Report it to the project maintainer
3. Do not modify the code until receiving guidance

## 7. QUICK REFERENCE FOR API ACCESS CHECKS

Use this pattern for checking authentication:

```python
# JWT Authentication Only
@router.post("/endpoint")
async def example_endpoint(
    request: RequestModel,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    # Use current_user for identity only
    # No permission or role checks
    
    # Implementation...
```

## 8. TEST USERS

For testing, you can still use the test users documented in the test user information guide, but note that all users have equal access since RBAC has been removed.