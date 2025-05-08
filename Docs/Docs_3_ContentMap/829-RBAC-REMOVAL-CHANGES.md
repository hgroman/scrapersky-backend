# RBAC Removal Changes Documentation

This document details the specific changes needed to remove RBAC from the ScraperSky backend.

## Overview

After analyzing the codebase, we've identified the key components that need to be modified:

1. The RBAC files have been backed up to `backup/rbac_backup/20250323/`
2. Core RBAC files have been removed from the codebase
3. JWT authentication remains intact
4. Router files need to be updated to bypass RBAC checks

## Authentication Dependencies

The existing authentication flow uses several dependencies:

1. `get_current_user` in src/auth/jwt_auth.py
2. `get_current_user` in src/services/core/auth_service.py
3. Router-specific auth checks like `check_sitemap_access` in src/routers/modernized_sitemap.py

## Implementation Details

### 1. JWT Authentication Updates

Instead of creating a new JWT authentication function, we'll modify each router to use the existing JWT validation but skip RBAC checks.

For each router that uses RBAC checks (like `check_sitemap_access`), we'll keep the basic JWT validation but bypass RBAC checks:

```python
# BEFORE:
async def check_sitemap_access(user: dict = Depends(user_dependency), session: AsyncSession = Depends(get_db_session)):
    tenant_id = auth_service.validate_tenant_id(None, user) or DEFAULT_TENANT_ID
    require_permission(user, PERM_ACCESS_SITEMAP)

    # Skip feature check in development mode
    if not is_development_mode() and not is_feature_check_disabled():
        logger.debug(f"Checking feature enablement for {FEATURE_CONTENTMAP}")
        await require_feature_enabled(tenant_id, FEATURE_CONTENTMAP, session, user.get("permissions", []))
    else:
        logger.warning(f"⚠️ Bypassing feature check for {FEATURE_CONTENTMAP} in development/testing mode")

    # Skip role check in development mode
    if not is_development_mode() and not is_feature_check_disabled():
        await require_role_level(user, ROLE_HIERARCHY["USER"], session)

    return tenant_id

# AFTER:
async def check_sitemap_access(user: dict = Depends(user_dependency), session: AsyncSession = Depends(get_db_session)):
    tenant_id = auth_service.validate_tenant_id(None, user) or DEFAULT_TENANT_ID
    # RBAC checks have been removed
    # require_permission(user, PERM_ACCESS_SITEMAP)
    # if not is_development_mode() and not is_feature_check_disabled():
    #     logger.debug(f"Checking feature enablement for {FEATURE_CONTENTMAP}")
    #     await require_feature_enabled(tenant_id, FEATURE_CONTENTMAP, session, user.get("permissions", []))
    # else:
    #     logger.warning(f"⚠️ Bypassing feature check for {FEATURE_CONTENTMAP} in development/testing mode")
    # if not is_development_mode() and not is_feature_check_disabled():
    #     await require_role_level(user, ROLE_HIERARCHY["USER"], session)

    return tenant_id
```

### 2. Endpoint Updates

For each API endpoint using RBAC checks, we'll update the endpoint to use JWT-only validation:

```python
# BEFORE:
@router.post("/scan", response_model=ScanResponse)
async def scan_endpoint(
    request: ScanRequest,
    tenant_id: str = Depends(check_some_rbac_feature),
    current_user: dict = Depends(user_dependency)
):
    # Function body...

# AFTER:
@router.post("/scan", response_model=ScanResponse)
async def scan_endpoint(
    request: ScanRequest,
    # tenant_id: str = Depends(check_some_rbac_feature),
    current_user: dict = Depends(user_dependency)
):
    # Extract tenant_id from request or user
    tenant_id = request.tenant_id or current_user.get("tenant_id") or DEFAULT_TENANT_ID
    # Function body continues...
```

## Specific Files to Update

Based on our analysis, these are the specific files that need to be updated:

1. src/routers/modernized_sitemap.py
2. src/routers/google_maps_api.py
3. src/routers/batch_page_scraper.py
4. src/routers/modernized_page_scraper.py
5. src/routers/profile.py
6. src/routers/dev_tools.py

## Next Steps

1. For each router file, modify any RBAC-specific checks to use simple JWT validation
2. Test each endpoint to ensure it works with basic JWT validation
3. Document any issues that arise when running the application

## Testing Process

For each modified endpoint, we'll test:

```bash
# Test with valid JWT
curl -X POST "http://localhost:8000/api/v3/sitemap/scan" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'

# Test with invalid JWT
curl -X POST "http://localhost:8000/api/v3/sitemap/scan" \
  -H "Authorization: Bearer invalid_token" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'

# Test with no JWT
curl -X POST "http://localhost:8000/api/v3/sitemap/scan" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'
```
