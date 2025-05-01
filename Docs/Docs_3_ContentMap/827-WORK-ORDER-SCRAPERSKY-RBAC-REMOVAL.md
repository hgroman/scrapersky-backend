I understand completely. Let's focus purely on RBAC removal and nothing else. Here's a focused work order just for gutting the RBAC system:

# WORK ORDER: ScraperSky RBAC Removal

## 1. Executive Summary

This work order outlines the process to completely remove the over-engineered Role-Based Access Control (RBAC) system from the ScraperSky backend. The goal is to simplify the codebase by maintaining only basic JWT authentication while removing all RBAC-specific permissions, feature flags, role levels, and tab-based permissions.

## 2. RBAC Removal Process

### PHASE 1: Identify All RBAC Components (Estimated Time: 1 hour)

#### 1.1 Core RBAC Files

Locate and document all files specifically related to RBAC:

```bash
# Core RBAC implementation files
src/constants/rbac.py                # RBAC constants and mappings
src/utils/permissions.py             # Permission utility functions
src/services/rbac/                   # RBAC service implementations
src/routers/rbac_admin.py            # RBAC admin endpoints
src/routers/rbac_features.py         # Feature flag endpoints
```

#### 1.2 RBAC Dependencies in Endpoints

Identify all API routes that use RBAC checks:

```bash
# Find all RBAC check functions in routers
grep -r "Depends(check_" --include="*.py" src/routers/
grep -r "require_permission" --include="*.py" src/routers/
grep -r "require_feature_enabled" --include="*.py" src/routers/
grep -r "require_role_level" --include="*.py" src/routers/
```

### PHASE 2: Create Backup of RBAC Code (Estimated Time: 30 minutes)

#### 2.1 Backup All RBAC Files

```bash
# Create backup directory
mkdir -p backup/rbac_backup/$(date +%Y%m%d)

# Copy RBAC files to backup
cp src/constants/rbac.py backup/rbac_backup/$(date +%Y%m%d)/
cp src/utils/permissions.py backup/rbac_backup/$(date +%Y%m%d)/
cp -r src/services/rbac/ backup/rbac_backup/$(date +%Y%m%d)/
cp src/routers/rbac_admin.py backup/rbac_backup/$(date +%Y%m%d)/
cp src/routers/rbac_features.py backup/rbac_backup/$(date +%Y%m%d)/
```

#### 2.2 Document Current RBAC Checks

For each router file using RBAC, document the original implementation before changes:

```bash
# Example for one router
mkdir -p backup/rbac_backup/$(date +%Y%m%d)/routers
cp src/routers/modernized_sitemap.py backup/rbac_backup/$(date +%Y%m%d)/routers/
```

### PHASE 3: Remove RBAC Check Dependencies (Estimated Time: 2 hours)

#### 3.1 Create JWT-Only Authentication Function

Add a simplified authentication function that only checks JWT validity:

```python
# Add to src/auth/dependencies.py

async def verify_jwt_only(
    authorization: Optional[str] = Header(None),
    request: Request = None
) -> dict:
    """
    Simple JWT validation without RBAC checks.
    Returns the decoded JWT payload if valid.
    """
    if not authorization:
        raise HTTPException(status_code=403, detail="Not authenticated")

    # Handle development token if needed
    if authorization == "Bearer scraper_sky_2024":
        return {"id": "dev-user-id", "tenant_id": "550e8400-e29b-41d4-a716-446655440000"}

    # Extract token
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme")

    try:
        # Decode JWT token (using your existing JWT verification logic)
        from ..utils.jwt import verify_token
        payload = verify_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Invalid token: {str(e)}")
```

#### 3.2 Replace RBAC Checks in Router Files

For each router file, replace RBAC dependencies with the simple JWT check:

```python
# BEFORE:
@router.post("/scan")
async def scan_domain(
    request: ScanRequest,
    tenant_id: str = Depends(check_sitemap_access),  # RBAC check
    current_user: dict = Depends(user_dependency)
):

# AFTER:
@router.post("/scan")
async def scan_domain(
    request: ScanRequest,
    current_user: dict = Depends(verify_jwt_only)  # JWT-only check
):
    # Extract tenant_id from user if needed
    tenant_id = request.tenant_id or current_user.get("tenant_id")
```

#### 3.3 Remove RBAC Code from Router Initialization

Find and remove RBAC dependencies at router initialization:

```python
# BEFORE:
router = APIRouter(
    prefix="/api/v3/sitemap",
    tags=["sitemap"],
    dependencies=[Depends(some_rbac_check)]
)

# AFTER:
router = APIRouter(
    prefix="/api/v3/sitemap",
    tags=["sitemap"]
)
```

### PHASE 4: Update Each API Endpoint (Estimated Time: 3 hours)

Go through each API endpoint one by one and update them:

#### 4.1 ContentMap (Sitemap) Endpoints

Update `src/routers/modernized_sitemap.py`:

- Remove `check_sitemap_access` dependency
- Replace with `verify_jwt_only`
- Comment out any internal RBAC checks

#### 4.2 Google Maps API Endpoints

Update `src/routers/google_maps_api.py`:

- Remove RBAC checks like `check_google_maps_access`
- Replace with `verify_jwt_only`
- Comment out any internal RBAC checks

#### 4.3 Batch Page Scraper Endpoints

Update `src/routers/batch_page_scraper.py`:

- Remove RBAC dependencies
- Replace with `verify_jwt_only`
- Comment out any internal RBAC checks

#### 4.4 All Other API Endpoints

Repeat the same process for each remaining router file

### PHASE 5: Comment Out RBAC Service Calls (Estimated Time: 1 hour)

For any service methods that call RBAC functions internally:

```python
# BEFORE:
async def process_domain(self, domain: str, tenant_id: str, user_id: str):
    # Check if feature is enabled
    is_enabled = await rbac_service.is_feature_enabled(
        tenant_id, "contentmap", session
    )
    if not is_enabled:
        raise ValueError("Feature not enabled")

    # Rest of the function

# AFTER:
async def process_domain(self, domain: str, tenant_id: str, user_id: str):
    # RBAC check removed
    # is_enabled = await rbac_service.is_feature_enabled(
    #     tenant_id, "contentmap", session
    # )
    # if not is_enabled:
    #     raise ValueError("Feature not enabled")

    # Rest of the function
```

### PHASE 6: Testing JWT-Only Authentication (Estimated Time: 1 hour)

#### 6.1 Test API Endpoints with Valid JWT

```bash
# Test with valid JWT or development token
curl -X POST "http://localhost:8000/api/v3/sitemap/scan" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'
```

#### 6.2 Test API Endpoints with Invalid JWT

```bash
# Test with invalid JWT
curl -X POST "http://localhost:8000/api/v3/sitemap/scan" \
  -H "Authorization: Bearer invalid_token" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'
```

#### 6.3 Test API Endpoints with No JWT

```bash
# Test with no JWT
curl -X POST "http://localhost:8000/api/v3/sitemap/scan" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'
```

## 3. Endpoint Checklist

Track the status of each endpoint as you remove RBAC:

| Router File                     | Endpoint                                   | RBAC Removed | JWT-Only Implemented | Tested |
| ------------------------------- | ------------------------------------------ | ------------ | -------------------- | ------ |
| modernized_sitemap.py           | /api/v3/sitemap/scan                       | □            | □                    | □      |
| modernized_sitemap.py           | /api/v3/sitemap/status/{job_id}            | □            | □                    | □      |
| google_maps_api.py              | /api/v3/google_maps_api/search             | □            | □                    | □      |
| google_maps_api.py              | /api/v3/google_maps_api/status/{job_id}    | □            | □                    | □      |
| batch_page_scraper.py           | /api/v3/batch_page_scraper/scan            | □            | □                    | □      |
| batch_page_scraper.py           | /api/v3/batch_page_scraper/status/{job_id} | □            | □                    | □      |
| rbac_admin.py                   | /api/v3/rbac-admin/\*                      | □            | □                    | □      |
| rbac_features.py                | /api/v3/rbac-features/\*                   | □            | □                    | □      |
| [Add other endpoints as needed] |                                            | □            | □                    | □      |

## 4. Common RBAC Check Patterns to Remove

Look for these RBAC check patterns in all files:

1. Router-level dependencies:

   ```python
   @router.get("/endpoint", dependencies=[Depends(check_some_access)])
   ```

2. Endpoint parameter dependencies:

   ```python
   async def endpoint(tenant_id: str = Depends(check_some_access))
   ```

3. Internal RBAC service calls:

   ```python
   await require_feature_enabled(tenant_id, feature_name, session)
   await require_role_level(user, role_level, session)
   await require_tab_permission(user, tab_name, feature_name, session)
   ```

4. RBAC utility function calls:

   ```python
   require_permission(user, permission_name)
   ```

5. Router initialization with RBAC dependencies:
   ```python
   router = APIRouter(dependencies=[Depends(check_some_access)])
   ```

## 5. Success Criteria

The RBAC removal is considered successful when:

1. All RBAC-specific checks are removed or commented out
2. Basic JWT authentication works correctly
3. All API endpoints can be accessed with a valid JWT
4. Invalid or missing JWTs are properly rejected
5. No RBAC-related errors appear in the logs

## 6. Reporting Requirements

After completing the work, provide a detailed report including:

1. List of all files modified
2. Summary of changes made to each file
3. List of removed RBAC checks
4. Results of endpoint testing
5. Any challenges encountered
6. Recommendations for future RBAC reimplementation

## Conclusion

This work order provides a focused plan for completely removing the RBAC system from the ScraperSky backend while maintaining basic JWT authentication. By following these steps, you should be able to achieve a simplified codebase that's easier to maintain and debug.
