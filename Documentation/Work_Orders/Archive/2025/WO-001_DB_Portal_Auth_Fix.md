# Work Order 001: DB Portal Authentication Fix

**ID:** WO-001
**Created:** 2025-11-16
**Priority:** 🔴 CATASTROPHIC
**Status:** OPEN
**Estimated Time:** 5 minutes
**Assignee:** TBD

---

## Issue Summary

**CATASTROPHIC SECURITY VULNERABILITY:** The database portal router at `src/routers/db_portal.py` has ZERO authentication on all endpoints, allowing anyone to execute arbitrary SQL queries against the production database.

---

## Severity Classification

**Level:** 🔴 CATASTROPHIC

**Risk:** Anyone with network access to the API can:
- Execute arbitrary SQL SELECT queries
- Read all database tables (users, domains, contacts, API keys, etc.)
- Extract sensitive business data
- Discover database schema
- Potentially escalate to data modification via SQL injection

**Verification:**
```bash
grep -n "get_current_user" src/routers/db_portal.py
# Returns: NO MATCHES
```

---

## Current State (Vulnerable Code)

**File:** `src/routers/db_portal.py`

### Affected Endpoints

All endpoints in the db_portal router are missing authentication:

| Line | Endpoint | Method | Status |
|------|----------|--------|--------|
| 107 | `/api/v3/db-portal/tables` | GET | ❌ No auth |
| 119 | `/api/v3/db-portal/tables/{table_name}` | GET | ❌ No auth |
| 141 | `/api/v3/db-portal/tables/{table_name}/sample` | GET | ❌ No auth |
| 160 | `/api/v3/db-portal/query` | POST | ❌ No auth |
| 180 | `/api/v3/db-portal/tables/{table_name}/validate` | POST | ❌ No auth |
| 204 | `/api/v3/db-portal/tables/{table_name}/model` | GET | ❌ No auth |
| 219 | `/api/v3/db-portal/health` | GET | ❌ No auth |

### Example Vulnerable Code (Line 160-163)

```python
@router.post("/query", response_model=QueryResult, summary="Execute SQL Query")
async def execute_query(
    request: SqlQueryRequest, session: AsyncSession = Depends(get_session_dependency)
):
    """
    Execute a safe, read-only SQL query for database inspection.
    """
    # ⚠️ MISSING: current_user: Dict = Depends(get_current_user)
```

---

## Required Fix

### Solution

Add authentication dependency to all public endpoints in `src/routers/db_portal.py`.

### Required Import

Add to top of file (after existing imports):

```python
from src.auth.jwt_auth import get_current_user
```

### Code Changes Required

For each endpoint function, add the authentication parameter:

```python
current_user: Dict = Depends(get_current_user)
```

### Specific Example (Line 161)

**BEFORE:**
```python
async def execute_query(
    request: SqlQueryRequest,
    session: AsyncSession = Depends(get_session_dependency)
):
```

**AFTER:**
```python
async def execute_query(
    request: SqlQueryRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user)  # ADD THIS LINE
):
```

---

## Implementation Checklist

### Step 1: Add Import
- [ ] Add `from src.auth.jwt_auth import get_current_user` to imports section

### Step 2: Add Authentication to All Endpoints

- [ ] **Line 108** - `list_tables()` - Add auth parameter
- [ ] **Line 122** - `get_table_schema()` - Add auth parameter
- [ ] **Line 142** - `get_sample_data()` - Add auth parameter
- [ ] **Line 161** - `execute_query()` - Add auth parameter
- [ ] **Line 186** - `validate_schema()` - Add auth parameter
- [ ] **Line 206** - `generate_model()` - Add auth parameter
- [ ] **Line 220** - `health_check()` - Add auth parameter

### Step 3: Verification

- [ ] Run tests: `pytest src/routers/test_db_portal.py -v` (if tests exist)
- [ ] Manual verification:
  ```bash
  # Should FAIL without auth token
  curl -X POST http://localhost:8000/api/v3/db-portal/query \
    -H "Content-Type: application/json" \
    -d '{"query": "SELECT 1"}'

  # Should SUCCEED with valid auth token
  curl -X POST http://localhost:8000/api/v3/db-portal/query \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -d '{"query": "SELECT 1"}'
  ```
- [ ] Verify all 7 endpoints require authentication
- [ ] Check Swagger UI shows lock icon on all endpoints

### Step 4: Documentation

- [ ] Update endpoint documentation if needed
- [ ] Add security note to docstrings
- [ ] Update API documentation

---

## Testing Strategy

### Unit Tests

Create/update `tests/routers/test_db_portal.py`:

```python
async def test_db_portal_requires_authentication():
    """Verify all db_portal endpoints require authentication"""

    endpoints = [
        ("GET", "/api/v3/db-portal/tables"),
        ("GET", "/api/v3/db-portal/tables/domains"),
        ("POST", "/api/v3/db-portal/query"),
    ]

    for method, endpoint in endpoints:
        response = await client.request(method, endpoint)
        assert response.status_code == 401  # Unauthorized
```

### Integration Tests

```python
async def test_db_portal_with_valid_token():
    """Verify authenticated requests succeed"""

    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    response = await client.get("/api/v3/db-portal/tables", headers=headers)
    assert response.status_code == 200
```

---

## Risk Assessment

### Before Fix
- **Exploit Difficulty:** Trivial (no authentication required)
- **Data Exposure:** Complete database read access
- **Impact:** CATASTROPHIC

### After Fix
- **Exploit Difficulty:** Requires valid JWT token
- **Data Exposure:** Limited to authenticated users
- **Impact:** Mitigated

---

## Dependencies

**Required:**
- JWT authentication system (already exists at `src/auth/jwt_auth.py`)
- `get_current_user` dependency function (already implemented)

**No external dependencies required.**

---

## Rollback Plan

If issues arise after deployment:

1. **Immediate:** Revert commit
2. **Alternative:** Temporarily disable db_portal router in `src/main.py`:
   ```python
   # Comment out this line:
   # app.include_router(db_portal_api_router, prefix="/api/v3", tags=["DB Portal"])
   ```
3. **Investigation:** Fix any authentication integration issues
4. **Redeploy:** Re-enable with fixes

---

## Success Criteria

- ✅ All 7 db_portal endpoints require authentication
- ✅ Unauthenticated requests return HTTP 401
- ✅ Authenticated requests with valid JWT succeed
- ✅ Swagger UI shows lock icon on all endpoints
- ✅ No functionality regression for authenticated users
- ✅ Tests pass

---

## Related Documents

- **STATE_OF_THE_NATION_2025-11-16.md** - Issue identification
- **ADR-004-Transaction-Boundaries.md** - Authentication patterns
- **src/auth/jwt_auth.py** - Authentication implementation
- **CLAUDE.md** - Dependency-based authentication pattern

---

## Notes

- This fix follows the existing authentication pattern used throughout the codebase
- The `get_current_user` dependency is already used in other routers
- No changes to business logic required - only adding auth dependency
- The db_portal was likely created as a development tool and accidentally exposed
- After this fix, consider adding additional rate limiting to db_portal endpoints

---

**Created by:** Claude (AI Assistant)
**Validation Date:** 2025-11-16
**Related Issue:** CATASTROPHIC security vulnerability - DB Portal exposure
