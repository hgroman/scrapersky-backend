# ScraperSky RBAC Implementation Guide & Developer Setup

**Version 2.0 — 2025-03-21**

This document serves as the authoritative guide for ScraperSky's Role-Based Access Control (RBAC) implementation and developer environment setup. It combines all essential information from the RBAC Implementation Guide, Dev-Admin Setup & Feature-Flag Verification Guide, and Production RBAC Enforcement Summary.

## 1. Overview & Background

This guide details our unified Role-Based Access Control (RBAC) strategy across all ScraperSky API routes. It captures our successful refactor efforts where we:
- Eliminated obsolete sitemap modules
- Consolidated multiple permission checks into a single dependency
- Removed development-only mocks and bypasses
- Implemented production-grade security using live database state

The ScraperSky backend now enforces proper RBAC for all API routes using only database-driven configuration, with no environment toggles or development shortcuts.

## 2. Purpose & Scope

This guide serves as the single source of truth for:

- **Security Enforcement:** Consistent, live permission checks for every API route
- **Developer Reference:** Clear documentation of required roles, permissions, and feature flags
- **Environment Setup:** Complete instructions for configuring a working dev environment
- **Audit & Testing:** A comprehensive reference to grant, audit, and test access both in local development and production

## 3. Key Improvements

- **Unified Dependency:** A single dependency (`check_sitemap_access` or similar) replaces four separate permission checks
- **Router-Level Security:** Every route is now protected by default—there's no chance to forget a permission check
- **Reduced Boilerplate:** Shared error handling and simplified legacy adapters eliminate duplicate code
- **Centralized Constants:** All permission, feature, and tab names are defined in constants, removing magic strings
- **Consistent Response Models:** Modern endpoints now use uniform response structures
- **Cleaner Background Tasks:** Background operations now use isolated sessions with proper transaction boundaries
- **Structured Logging:** Error contexts are logged clearly for easier troubleshooting

## 4. Environment Cleanup

The following environment variables were removed to enforce proper RBAC checks:

| Environment Variable        | Previous Purpose                      | File(s) Changed                                       |
| --------------------------- | ------------------------------------- | ----------------------------------------------------- |
| `SCRAPER_SKY_DEV_MODE`      | Bypassed auth checks, used mock users | `docker-compose.yml`, `.env`, `modernized_sitemap.py` |
| `ENABLE_FEATURE_CONTENTMAP` | Forced feature enablement             | `docker-compose.yml`, `.env`, `modernized_sitemap.py` |
| `DISABLE_PERMISSION_CHECKS` | Skipped permission verification       | `docker-compose.yml`, `.env`, `modernized_sitemap.py` |
| `ENABLE_ALL_FEATURES`       | Bypassed feature flag checks          | `docker-compose.yml`, `.env`, `modernized_sitemap.py` |

Specific code changes:

- Removed the check for these environment variables in router files
- Eliminated conditional logic that would bypass database checks when variables were set
- Ensured all permission checks now use real database tables
- Deleted the `is_feature_check_disabled()` function that bypassed feature checks
- Removed use of development mock users and data

## 5. Role Hierarchy

| Role Name    | Numeric Level | Description             |
| ------------ | ------------- | ----------------------- |
| USER         | 1             | Basic access            |
| ADMIN        | 2             | Elevated capabilities   |
| SUPER_ADMIN  | 3             | Org‑wide administration |
| GLOBAL_ADMIN | 4             | System‑wide admin       |

Defined in `src/constants/rbac.py:ROLE_HIERARCHY`.

## 6. Feature Flags

Feature flags control high‑level functionality and are managed in the database.

- **Backend Source:** The `feature_flags` table
- **Mapping:** `FEATURE_MAP` (in code) maps backend names to frontend identifiers

| Backend Key    | Frontend Key   | Default Enabled? |
| -------------- | -------------- | ---------------- |
| contentmap     | deep-analysis  | ❌               |
| discovery-scan | discovery-scan | ✅               |
| localminer     | localminer     | ✅               |

Tenant-specific enablement is controlled via the `tenant_features` table.

## 7. Tab Permissions

Tabs (UI modules) are secured using both role and feature flag checks.

- Each tab's required role is defined in `TAB_ROLE_REQUIREMENTS`
- Both the feature enablement (via `tenant_features`) and the user's role are verified before granting access

| Tab Name       | Required Role | Feature Flag |
| -------------- | ------------- | ------------ |
| discovery-scan | USER (1)      | contentmap   |
| deep-analysis  | ADMIN (2)     | contentmap   |

## 8. Endpoint Permissions Matrix

| HTTP Method | Path                            | Permission             | Feature Flag | Required Role | Tab            |
| ----------- | ------------------------------- | ---------------------- | ------------ | ------------- | -------------- |
| POST        | /api/v3/sitemap/scan            | access_sitemap_scanner | contentmap   | USER (1)      | discovery-scan |
| GET         | /api/v3/sitemap/status/{job_id} | access_sitemap_scanner | contentmap   | USER (1)      | discovery-scan |

_Add new routes as they are implemented._

## 9. Development vs Production Approach

Our earlier development environment relied on environment‑variable toggles (e.g., `SCRAPER_SKY_DEV_MODE`, `ENABLE_ALL_FEATURES`) to bypass permission checks and use mock data. **These have now been removed.**

- **Development:** Uses live database data for all permission checks. No bypasses or mocks remain.
- **Production:** All endpoints enforce strict permissions based solely on the live database state.

## 10. Four-Layer RBAC Integration

```
1. Basic Permission Check (synchronous)
   require_permission(current_user, "permission:name")
   |
2. Feature Enablement Check (async)
   await require_feature_enabled(...)
   |
3. Role Level Check (async)
   await require_role_level(...)
   |
4. Tab Permission Check (async)
   await require_tab_permission(...)
   |
Business Logic / Data Access
```

Example implementation:

```python
async def check_sitemap_access(user: dict = Depends(user_dependency), session: AsyncSession = Depends(get_db_session)):
    tenant_id = auth_service.validate_tenant_id(None, user) or DEFAULT_TENANT_ID
    require_permission(user, PERM_ACCESS_SITEMAP)

    # Real DB access - no development mode bypassing
    await require_feature_enabled(tenant_id, FEATURE_CONTENTMAP, session, user.get("permissions", []))
    await require_role_level(user, ROLE_HIERARCHY["USER"], session)
    await require_tab_permission(user, TAB_DISCOVERY, FEATURE_CONTENTMAP, session)
    return tenant_id
```

## 11. Developer Database Setup

### 11.1 Relevant Tables & Columns

| Table                | PK / Composite PK       | Key Columns                       | Purpose                    |
| -------------------- | ----------------------- | --------------------------------- | -------------------------- |
| **auth.users**       | id (UUID)               | email                             | Base user record           |
| **profiles**         | id (UUID)               | tenant_id, role_id, role, active  | Links user → tenant → role |
| **feature_flags**    | id (UUID)               | name, default_enabled             | Master feature list        |
| **tenant_features**  | (tenant_id, feature_id) | is_enabled                        | Tenant's enabled features  |
| **sidebar_features** | id (UUID)               | requires_feature, minimum_role_id | UI tab access control      |

### 11.2 Create & Elevate Dev Admin

#### 11.2.1 Insert user into `auth.users`

```sql
INSERT INTO auth.users (id, email, created_at)
VALUES (
  '88f53cfa-9a35-439b-9e06-2b62d9603572',
  'dev@example.com',
  NOW()
)
ON CONFLICT (id) DO NOTHING;
```

#### 11.2.2 Update `profiles` to GLOBAL_ADMIN

```sql
UPDATE profiles
SET role_id = 4, role = 'GLOBAL_ADMIN', active = TRUE
WHERE id = '88f53cfa-9a35-439b-9e06-2b62d9603572';
```

### 11.3 Enable ContentMap Feature

#### 11.3.1 Ensure `deep-analysis` exists

```sql
SELECT id FROM feature_flags WHERE name = 'deep-analysis';
```

If empty, create it:

```sql
INSERT INTO feature_flags (id, name, description, default_enabled)
VALUES (uuid_generate_v4(), 'deep-analysis', 'Advanced content mapping', TRUE)
ON CONFLICT (name) DO NOTHING;
```

#### 11.3.2 Enable for your tenant

```sql
INSERT INTO tenant_features (tenant_id, feature_id, is_enabled)
VALUES (
  '550e8400-e29b-41d4-a716-446655440000',
  (SELECT id FROM feature_flags WHERE name = 'deep-analysis'),
  TRUE
)
ON CONFLICT (tenant_id, feature_id) DO UPDATE SET is_enabled = TRUE;
```

## 12. Verification Queries

Run each query and confirm output exactly matches expectations:

### 12.1 Dev Admin Profile

```sql
SELECT id, tenant_id, role_id, role, active
FROM profiles
WHERE id = '88f53cfa-9a35-439b-9e06-2b62d9603572';
```

▶️ Expect GLOBAL_ADMIN, active = true.

### 12.2 Tenant Features

```sql
SELECT ff.name, tf.is_enabled
FROM tenant_features tf
JOIN feature_flags ff ON tf.feature_id = ff.id
WHERE tf.tenant_id = '550e8400-e29b-41d4-a716-446655440000';
```

▶️ Expect row: `deep-analysis | true`.

## 13. Troubleshooting Checklist

| Symptom                           | Check                                               | Fix                                   |
| --------------------------------- | --------------------------------------------------- | ------------------------------------- |
| "Feature not enabled: contentmap" | Does SELECT in Step 11.3.2 return `deep-analysis,true`? | Re‑run Step 11.3.2                    |
| 403 on scan endpoint              | JWT's tenant_id matches profiles.tenant_id?         | Decode JWT; confirm `tenant_id` claim |
| 403 on status endpoint            | profile.role_id ≥ USER (1)?                         | Update profile role as in Step 11.2.2 |
| Missing feature in DB             | SELECT name FROM feature_flags                      | Insert missing feature (Step 11.3.1)  |

## 14. API Smoke Tests

### 14.1 Scan Endpoint

```bash
curl -s -X POST http://localhost:8000/api/v3/sitemap/scan \
  -H "Authorization: Bearer 123" \
  -H "Content-Type: application/json" \
  -d '{"base_url":"https://www.guthrie.org","tenant_id":"550e8400-e29b-41d4-a716-446655440000","max_pages":10}'
```

▶️ Expected response (202 Accepted):

```json
{
  "job_id": "job_add7d3e1",
  "status_url": "/api/v1/status/job_add7d3e1"
}
```

### 14.2 Status Endpoint

```bash
curl -s -X GET http://localhost:8000/api/v3/sitemap/status/job_add7d3e1 \
  -H "Authorization: Bearer 123"
```

▶️ Expected response (200 OK):

```json
{
  "job_id": "job_add7d3e1",
  "status": "running",
  "domain": null,
  "progress": 0.0,
  "created_at": null,
  "updated_at": null,
  "result": null,
  "error": null,
  "metadata": null
}
```

## 15. CI Test Example (pytest + httpx)

```python
import httpx

def test_sitemap_scan_authorization(httpx_client):
    # Test without a token returns 403
    r = httpx_client.post("/api/v3/sitemap/scan")
    assert r.status_code == 403

    # Test with a valid token returns 202
    token = get_jwt_for_role("GLOBAL_ADMIN")
    r = httpx_client.post(
        "/api/v3/sitemap/scan",
        headers={"Authorization": f"Bearer {token}"},
        json={"base_url": "https://www.guthrie.org", "max_pages": 10}
    )
    assert r.status_code == 202
```

## 16. Template for New Routes

Follow this checklist for implementing RBAC on any new API route:

| Step                         | Description                    | Implementation                                                 |
| ---------------------------- | ------------------------------ | -------------------------------------------------------------- |
| **1. Environment Cleanup**   | Remove any environment toggles | Delete env var checks from the router                          |
| **2. DB Feature Toggle**     | Use feature_flags table        | Ensure the feature exists in feature_flags table               |
| **3. Permission Dependency** | Create unified dependency      | Model after check_sitemap_access pattern                       |
| **4. Smoke Tests**           | Verify with curl               | Test with and without valid token, verify 403 for unauthorized |

### New Route Implementation Pattern

```python
# 1. Define constants
FEATURE_NAME = "your-feature"
PERM_ACCESS = "access_your_feature"
TAB_NAME = "your-tab"

# 2. Create unified permission dependency
async def check_feature_access(user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
    tenant_id = auth_service.validate_tenant_id(None, user)
    require_permission(user, PERM_ACCESS)
    await require_feature_enabled(tenant_id, FEATURE_NAME, session, user.get("permissions", []))
    await require_role_level(user, ROLE_HIERARCHY["USER"], session)
    await require_tab_permission(user, TAB_NAME, FEATURE_NAME, session)
    return tenant_id

# 3. Apply to router
router = APIRouter(prefix="/api/v3/your-feature", dependencies=[Depends(check_feature_access)])

# 4. Create endpoints that inherit the dependency
@router.post("/your-endpoint")
async def your_function(...):
    # Implementation
```

## 17. Next Steps

- **Review & Extend:** Add any new routes to the Endpoint Permissions Matrix as they are built
- **Integrate Tests:** Incorporate the tests from Section 15 into your CI pipeline
- **Document Setup:** For new developers, point them to this guide for proper database setup
- **Monitor:** Keep this document updated with any changes in RBAC requirements

---

This document now fully reflects our current implementation, including the removal of legacy development-only shortcuts and the consolidation of all permission checks into a live, database‑driven system.
