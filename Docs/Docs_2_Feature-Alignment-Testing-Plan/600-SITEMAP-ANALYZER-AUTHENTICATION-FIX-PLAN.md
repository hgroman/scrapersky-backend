# Sitemap Analyzer Authentication Fix Plan

## Issue Identification

The sitemap analyzer page (`sitemap-analyzer.html`) is not working because of authentication issues with the compatibility endpoints. The root cause is that the compatibility router (`compat_router`) in `modernized_sitemap.py` does not implement the standardized RBAC pattern that has been applied to the modern endpoints.

### Key Problems:

1. **Missing Development Mode Support**: The compatibility endpoints do not have the same development mode support that's documented in the Authentication Standardization (400-AUTHENTICATION-STANDARDIZATION.md).

2. **Incomplete RBAC Integration**: The compatibility endpoints don't implement all four layers of RBAC checks (basic permission, feature enablement, role level, tab permission) as outlined in the RBAC Integration Guide (013-RBAC-INTEGRATION-GUIDE.md).

3. **Inconsistent User Context**: There's no fallback for development environments or standardized way to handle the development token "scraper_sky_2024".

## Solution Overview

We need to modify the compatibility router in `modernized_sitemap.py` to implement the standardized authentication pattern used in other routers, particularly `google_maps_api.py` which is referenced as the exemplary implementation.

### Implementation Steps:

1. **Add Development Mode Support**:
   - Add `is_development_mode()` function to detect development environment
   - Add `get_development_user()` function to provide a mock user with necessary permissions
   - Use conditional dependency selection based on development mode

2. **Implement Full RBAC Pattern in Compatibility Endpoints**:
   - Add all four layers of permission checks to each compatibility endpoint
   - Ensure proper transaction boundaries after permission checks
   - Use constants from `rbac.py` instead of hardcoded values

3. **Standardize Error Handling**:
   - Ensure consistent error response format
   - Add proper logging for authentication and permission errors
   - Return appropriate HTTP status codes

## Detailed Implementation

### Step 1: Add Development Mode Support

Add these imports and functions at the top of `modernized_sitemap.py`:

```python
import os
from ..config.settings import settings

# Function to check if running in development mode
def is_development_mode() -> bool:
    """
    Checks if the application is running in development mode.
    Requires explicit opt-in through environment variable.
    """
    dev_mode = os.getenv("SCRAPER_SKY_DEV_MODE", "").lower() == "true"
    if dev_mode:
        logger.warning("⚠️ Running in DEVELOPMENT mode - ALL AUTH CHECKS BYPASSED ⚠️")
    return dev_mode or settings.environment.lower() in ["development", "dev"]

# Development user for local testing
async def get_development_user():
    """
    Provide a mock user for local development with full sitemap analyzer access.
    This is only used when SCRAPER_SKY_DEV_MODE=true is set.
    """
    logger.info("Using development user with full access to sitemap analyzer")
    return {
        "id": "dev-admin-id",
        "user_id": "dev-admin-id",
        "email": "dev@example.com",
        "tenant_id": DEFAULT_TENANT_ID,
        "roles": ["admin"],
        "permissions": ["access_sitemap_scanner", "*"],
        "auth_method": "dev_mode",
        "is_admin": True
    }

# Choose the appropriate user dependency based on explicit development mode
user_dependency = get_development_user if is_development_mode() else get_current_user
```

### Step 2: Update Compatibility Endpoints

Replace all instances of `Depends(get_current_user)` in the compatibility endpoints with `Depends(user_dependency)` and implement the full RBAC pattern. Here's an example for the `/analyze` endpoint:

```python
@compat_router.post("/analyze")
async def legacy_analyze_domain(
    request: LegacySitemapAnalyzeRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(user_dependency)  # Use user_dependency instead
):
    """
    Compatibility endpoint for the legacy frontend.
    Maps the legacy frontend request format to the modern v3 API.

    Required Permissions:
    - Basic permission: "access_sitemap_scanner"
    - Feature flag: "sitemap_analyzer"
    - Minimum role: "USER"
    - Tab permission: "discovery-scan"
    """
    logger.info(f"Received legacy analyze request for domain: {request.domain}")

    # Get tenant ID with proper fallbacks
    tenant_id = request.tenant_id or current_user.get("tenant_id", "")
    if not tenant_id:
        tenant_id = DEFAULT_TENANT_ID

    # 1. Basic permission check
    require_permission(current_user, "access_sitemap_scanner")

    # 2. Feature enablement check
    user_permissions = current_user.get("permissions", [])
    await require_feature_enabled(
        tenant_id=tenant_id,
        feature_name="sitemap_analyzer",
        session=session,
        user_permissions=user_permissions
    )

    # 3. Role level check
    await require_role_level(
        user=current_user,
        required_role_id=ROLE_HIERARCHY["USER"],
        session=session
    )

    # 4. Tab permission check
    await require_tab_permission(
        user=current_user,
        tab_name="discovery-scan",
        feature_name="sitemap_analyzer",
        session=session
    )

    # Map legacy request to modern request
    modern_request = SitemapScrapingRequest(
        base_url=request.domain,
        tenant_id=tenant_id,
        max_pages=request.max_urls_per_sitemap or 10000
    )

    try:
        # Call the modern implementation with proper transaction boundaries
        async with session.begin():
            response = await sitemap_processing_service.initiate_domain_scan(
                request=ServiceRequest(
                    base_url=modern_request.base_url,
                    tenant_id=tenant_id,
                    max_pages=modern_request.max_pages
                ),
                session=session,
                background_tasks=background_tasks,
                tenant_id=tenant_id
            )

        # Map response to format expected by legacy frontend
        return {
            "job_id": response.job_id,
            "status": "started",
            "status_url": f"/api/v1/sitemap-analyzer/status/{response.job_id}"
        }
    except Exception as e:
        logger.error(f"Error in legacy_analyze_domain: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
```

### Step 3: Update All Other Compatibility Endpoints

Apply the same pattern to the remaining compatibility endpoints:
- `/status/{job_id}`
- `/batch`
- `/batch-status/{batch_id}`

## Testing Procedure

After implementing the fixes:

1. **Basic Authentication Test**:
   - Test with development token "scraper_sky_2024"
   - Test with invalid token
   - Test with no token

2. **Permission Boundary Tests**:
   - Test with user having insufficient permissions
   - Test with admin user
   - Test with development user

3. **End-to-End Testing**:
   - Run the complete test script from 512-SITEMAP-ANALYZER-TEST-INSTRUCTIONS.md
   - Verify the frontend works with the updated authentication

## Monitoring and Verification

Use these techniques to verify the fix:

1. **Enable Verbose Logging**:
   ```
   LOGLEVEL=DEBUG SCRAPER_SKY_DEV_MODE=true python -m src.main
   ```

2. **Monitor Authentication Logs**:
   - Look for "Using development user" messages
   - Check for any permission check failures

3. **Frontend Console Monitoring**:
   - Check browser console for request/response errors
   - Verify the Authorization header is set correctly in requests

## Implementation Progress Tracking

- [x] Added development mode support functions
- [x] Updated `/analyze` endpoint with full RBAC pattern
- [x] Updated `/status/{job_id}` endpoint with full RBAC pattern
- [x] Updated `/batch` endpoint with full RBAC pattern
- [x] Updated `/batch-status/{batch_id}` endpoint with full RBAC pattern
- [ ] Tested with development token
- [ ] Verified frontend functionality
- [x] Documented changes

## Conclusion

This plan addresses the authentication issues with the sitemap analyzer by implementing the standardized RBAC pattern and development mode support in the compatibility router. Once implemented, the frontend should work correctly with the expected authentication flow, especially in development environments.

This fix aligns with the broader standardization efforts and ensures that the sitemap analyzer adheres to the same authentication patterns as the rest of the application.
