# Updated Auth Service Consolidation Plan

## Current Implementation Decision

After evaluating both implementations and the recent work to remove RBAC throughout the codebase, we have decided to standardize on **auth/jwt_auth.py** for these reasons:

1. **Simplified Authentication**: The `jwt_auth.py` implementation focuses on basic JWT validation without complex RBAC structures, aligning with our recent RBAC removal work.

2. **Consistent Tenant Handling**: `jwt_auth.py` uses `DEFAULT_TENANT_ID` consistently, simplifying multi-tenancy without complex isolation logic.

3. **Recent Implementation**: Significant recent work has been done implementing `jwt_auth.py` across multiple routers, making it the most up-to-date auth implementation.

## Current Usage Status

We have two auth service implementations:

1. **auth/jwt_auth.py** - Our target standard, used by:
   - profile.py
   - dev_tools.py
   - sitemap_analyzer.py (already updated)
   - Several other routers already standardized

2. **services/core/auth_service.py** - To be deprecated, used by:
   - modernized_page_scraper.py
   - batch_page_scraper.py
   - google_maps_api.py
   - modernized_sitemap.py
   - modernized_sitemap.bak.3.21.25.py

## Preserved Information from Deprecated Implementation

While standardizing on `jwt_auth.py`, we should preserve these valuable aspects of `auth_service.py` for future reference:

1. **Multiple JWT Library Fallbacks**: The approach to handle various JWT libraries with fallback mechanisms.
2. **User Model Integration**: How it integrates with the User model.
3. **Dependency Injection Pattern**: The clean dependency pattern (although more complex than needed).

## Implementation Plan

### 1. First Update Remaining Routers Using jwt_auth.py:
- We have completed this for `sitemap_analyzer.py`
- ~~Next update `profile.py`~~ (Already using jwt_auth.py)
- ~~Next update `dev_tools.py`~~ (Already using jwt_auth.py)

### 2. Then Update Routers Using services/core/auth_service.py:
- modernized_page_scraper.py
- batch_page_scraper.py
- google_maps_api.py
- modernized_sitemap.py
- modernized_sitemap.bak.3.21.25.py

### 3. Route-by-Route Approach:

For each router using auth_service.py:
1. Change imports to use `from ..auth.jwt_auth import get_current_user, DEFAULT_TENANT_ID`
2. Update dependency injection pattern if needed
3. Ensure any User objects are handled properly (jwt_auth returns Dict instead of User objects)
4. Update tenant handling to use DEFAULT_TENANT_ID
5. Test to ensure auth still works

### 4. Key Implementation Challenges

The main challenge is that the two implementations have different return types:

**jwt_auth.py:**
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    # Returns a dictionary with user information
```

**auth_service.py:**
```python
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    # Returns a User object
```

We need to ensure routers expecting a User object can work with a Dict returned by jwt_auth.py.

## Implementation Tracking

| Router | Current Auth | Status | Notes |
|--------|--------------|--------|-------|
| profile.py | jwt_auth.py | ✅ Done | Already using target implementation |
| dev_tools.py | jwt_auth.py | ✅ Done | Already using target implementation |
| sitemap_analyzer.py | jwt_auth.py | ✅ Done | Updated to import from jwt_auth |
| modernized_page_scraper.py | auth_service.py | 🔄 Pending | |
| batch_page_scraper.py | auth_service.py | 🔄 Pending | |
| google_maps_api.py | auth_service.py | 🔄 Pending | |
| modernized_sitemap.py | auth_service.py | 🔄 Pending | |
| modernized_sitemap.bak.3.21.25.py | auth_service.py | 🔄 Pending | Consider archiving instead |

## Development Environment Settings

For testing, ensure these environment variables are set:
- `DEV_TOKEN=scraper_sky_2024`
- `DEFAULT_TENANT_ID=550e8400-e29b-41d4-a716-446655440000`
- `ENVIRONMENT=development`
