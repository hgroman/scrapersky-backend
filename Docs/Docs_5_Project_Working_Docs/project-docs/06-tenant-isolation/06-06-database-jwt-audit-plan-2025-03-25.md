# DATABASE JWT AUDIT PLAN

## Purpose

This document outlines the specific steps to audit and fix the improper JWT/tenant authentication in database operations throughout the ScraperSky backend codebase.

## Audit Steps

### 1. Database Connection Files

| File | Status | Action Required |
|------|--------|----------------|
| `src/db/session.py` | ✅ Fixed | Removed JWT/tenant authentication from database connection |
| `src/db/engine.py` | 🔍 Needs Audit | Check for JWT/tenant authentication in connection settings |
| `scripts/db/*.py` | 🔍 Needs Audit | Check all database scripts for JWT/tenant authentication |

### 2. API Gateway Endpoints

Verify that JWT authentication is correctly implemented at the API gateway level:

| Endpoint | HTTP Method | Authentication Required | Status |
|----------|-------------|-------------------------|--------|
| `/api/v3/sitemap/scan` | POST | Yes | 🔍 Needs Audit |
| `/api/v3/sitemap/status/{job_id}` | GET | Yes | 🔍 Needs Audit |
| All other `/api/v3/*` endpoints | Various | Yes | 🔍 Needs Audit |

### 3. Background Tasks

Verify that background tasks are not implementing redundant JWT authentication:

| Task | File | Status | Action Required |
|------|------|--------|----------------|
| Sitemap Scanning | `src/services/sitemap/*.py` | 🔍 Needs Audit | Remove any JWT/tenant authentication |
| Data Processing | `src/services/data/*.py` | 🔍 Needs Audit | Remove any JWT/tenant authentication |
| All other background tasks | Various | 🔍 Needs Audit | Remove any JWT/tenant authentication |

### 4. Service Modules

Audit all service modules that interact with the database:

| Service | Files | Status | Action Required |
|---------|-------|--------|----------------|
| User Service | `src/services/user/*.py` | 🔍 Needs Audit | Remove any JWT/tenant authentication in DB operations |
| Sitemap Service | `src/services/sitemap/*.py` | 🔍 Needs Audit | Remove any JWT/tenant authentication in DB operations |
| All other services | Various | 🔍 Needs Audit | Remove any JWT/tenant authentication in DB operations |

## Implementation Plan

### Phase 1: Critical Fixes (Immediate)

1. ✅ Fix `src/db/session.py` to remove JWT/tenant authentication
2. Test the sitemap scan endpoint to verify it works with the simplified database connection
3. Document the architectural principle in `docs/DATABASE_JWT_SEPARATION_MANDATE.md`

### Phase 2: Systematic Audit (1-2 days)

1. Audit all files listed in the tables above
2. For each file:
   - Remove any JWT/tenant authentication from database operations
   - Ensure JWT authentication is only happening at API gateway endpoints
   - Update to use the simplified database connection approach

### Phase 3: Testing and Verification (1 day)

1. Test all endpoints to verify they work with the simplified database connections
2. Verify that JWT authentication is correctly implemented at the API gateway level
3. Update documentation to reflect the architectural changes

## Reporting

For each file audited, update this document with:

```
| File | Status | Changes Made |
|------|--------|--------------|
| `path/to/file.py` | ✅ Fixed | Removed JWT claims from database connection |
```

## Completion Criteria

The audit is complete when:

1. All database operations use simple pooled connections without JWT/tenant authentication
2. All JWT authentication happens only at the API gateway level
3. All tests pass with the simplified database connections
4. Documentation is updated to reflect the architectural changes
