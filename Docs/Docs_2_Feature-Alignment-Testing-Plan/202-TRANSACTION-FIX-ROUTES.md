# 1.4: Routes Requiring Transaction Management Fixes

This document provides a prioritized list of routes that need transaction management fixes applied following the pattern established in the Transaction Management Guide and demonstrated in the Google Maps API case study.

## Overview of Issue

The core issue is routers wrapping service calls in transaction contexts (`async with session.begin()`) while also passing the session to services that might initiate their own transactions. This leads to the error:

```
'_AsyncGeneratorContextManager' object has no attribute 'begin'
```

## Routes Requiring Fixes

Based on the codebase analysis, the following routes contain transaction management anti-patterns and need to be fixed:

### 1. RBAC Features Router

- **File**: `src/routers/rbac_features.py`
- **Endpoints**:
  - `GET /api/v3/features/` - Get all features
  - `POST /api/v3/features/` - Create a feature
  - `GET /api/v3/features/tenant` - Get tenant features
  - `POST /api/v3/features/tenant` - Update tenant feature

### 2. RBAC Admin Router

- **File**: `src/routers/rbac_admin.py`
- **Endpoints**:
  - `GET /api/v3/rbac-admin/roles` - Get roles
  - `POST /api/v3/rbac-admin/roles` - Create role
  - `PUT /api/v3/rbac-admin/roles/{role_id}` - Update role
  - `DELETE /api/v3/rbac-admin/roles/{role_id}` - Delete role

### 3. RBAC Permissions Router

- **File**: `src/routers/rbac_permissions.py`
- **Endpoints**:
  - `GET /api/v3/rbac-permissions/` - Get permissions
  - `POST /api/v3/rbac-permissions/` - Create permission
  - `GET /api/v3/rbac-permissions/{permission_id}` - Get permission
  - `PUT /api/v3/rbac-permissions/{permission_id}` - Update permission
  - `DELETE /api/v3/rbac-permissions/{permission_id}` - Delete permission
  - `POST /api/v3/rbac-permissions/role/{role_id}` - Assign permission to role
  - `DELETE /api/v3/rbac-permissions/role/{role_id}/permission/{permission_id}` - Remove permission from role

### 4. Batch Page Scraper Router

- **File**: `src/routers/batch_page_scraper.py`
- **Endpoints**:
  - `POST /api/v3/batch-page-scraper/scan` - Scan domain
  - `GET /api/v3/batch-page-scraper/status/{job_id}` - Get job status
  - `POST /api/v3/batch-page-scraper/batch` - Batch scan domains

### 5. Dev Tools Router

- **File**: `src/routers/dev_tools.py`
- **Endpoints**:
  - `GET /api/v3/dev-tools/db-tables` - Get database tables
  - Various other development endpoints

## Fix Implementation Instructions

For each router, apply the following fixes:

1. **Remove Transaction Contexts**: Remove all `async with session.begin():` wrappers around service calls

2. **Add Documentation Comments**: Add clear comments explaining the architectural pattern:

   ```python
   # IMPORTANT: Do not wrap in session.begin() - service handles sessions properly
   ```

3. **Test Each Endpoint**: After fixing, test the endpoints to verify they work correctly

## Example Fix Pattern

```python
# BEFORE
@router.get("/endpoint")
async def endpoint(session: AsyncSession):
    async with session.begin():  # REMOVE THIS
        result = await service.do_something(session)
    return result

# AFTER
@router.get("/endpoint")
async def endpoint(session: AsyncSession):
    # IMPORTANT: Do not wrap in session.begin() - service handles sessions properly
    result = await service.do_something(session)
    return result
```

## Verification Process

For each fixed router:

1. Run targeted tests against the endpoints
2. Verify no transaction-related errors occur
3. Check that the endpoints function correctly

## Priority Order

Fix the routers in this order:

1. RBAC Features Router - High usage, impacts feature enablement checks
2. RBAC Permissions Router - Critical for permission management
3. RBAC Admin Router - Administrative functionality
4. Batch Page Scraper Router - Core business functionality
5. Dev Tools Router - Lower priority as it's development-only functionality

# Transaction Fix Routes

This document identifies routes in the ScraperSky backend that need to be updated to follow the standardized transaction management pattern documented in `TRANSACTION_MANAGEMENT_PATTERN.md` and `GOOGLE_MAPS_API_ARCHITECTURAL_PATTERNS.md`.

## Priority Routes for Transaction Pattern Fixes

| Router File                      | Endpoints               | Current Pattern                       | Needed Fix                               |
| -------------------------------- | ----------------------- | ------------------------------------- | ---------------------------------------- |
| `src/routers/batch_scraper.py`   | `/batch/*` endpoints    | Mixed transaction handling            | Apply router transaction boundaries      |
| `src/routers/data_processor.py`  | `/process/*` endpoints  | Services creating transactions        | Remove service transactions              |
| `src/routers/feature_service.py` | `/features/*` endpoints | Inconsistent session handling         | Use managed_transaction decorator        |
| `src/routers/import_api.py`      | `/import/*` endpoints   | Background tasks with request session | Create new sessions for background tasks |
| `src/routers/search_api.py`      | `/search/*` endpoints   | Nested transactions                   | Remove nested transactions               |

## Common Issues Identified

1. **Nested Transactions**:

   - Router creates transaction
   - Service also creates transaction
   - Results in SQLAlchemy errors

2. **Session Leaks in Background Tasks**:

   - Background task uses request session
   - Request completes while background task still running
   - Results in "Session closed" errors

3. **Inconsistent Transaction Handling**:

   - Some endpoints manage transactions
   - Others rely on services
   - Results in inconsistent error handling

4. **Missing Error Propagation**:
   - Exceptions caught without proper logging
   - Job status not updated on errors
   - Results in silent failures

## Implementation Plan

1. **Phase 1 (Completed)**:

   - [x] Google Maps API router - FIXED
   - [x] Job Service - FIXED
   - [x] Places Storage Service - FIXED

2. **Phase 2 (Next)**:

   - [ ] Batch Scraper router
   - [ ] Data Processor router

3. **Phase 3 (Later)**:

   - [ ] Feature Service router
   - [ ] Import API router
   - [ ] Search API router

4. **Phase 4 (Final)**:
   - [ ] Remaining routers
   - [ ] Create standardized base classes

## Testing Strategy

Each fixed router should be tested with:

1. **Transaction Boundary Tests**:

   - Verify router establishes transaction
   - Confirm service uses provided session
   - Test transaction rollback on error

2. **Background Task Tests**:

   - Verify background task creates new session
   - Test job status updates
   - Confirm error handling

3. **Duplicate Entity Tests** (if applicable):
   - Test handling of existing entities
   - Verify constraint violations are prevented
   - Confirm batch operation error handling
