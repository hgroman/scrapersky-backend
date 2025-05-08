# STRUCTURAL CHANGES SUMMARY

This document provides a comprehensive summary of major structural changes made to the ScraperSky codebase. If you encounter code patterns or references that don't match this summary, they are likely outdated and should be reported to the project maintainer.

## 1. AUTHENTICATION SYSTEM CHANGES

### RBAC System: COMPLETELY REMOVED

- **Previous Implementation**: Three-layer RBAC system (Roles → Permissions → Features)
- **Current Status**: RBAC system entirely removed
- **What Was Removed**:
  - All permission checking functions (`require_permission`, `has_permission`)
  - All feature flag checks (`require_feature_enabled`)
  - All role level checks (`require_role_level`)
  - RBAC constants file and utilities
  - RBAC models and database tables are no longer referenced
- **Current Implementation**: Simple JWT authentication only (validates user identity)

### Tenant Isolation: COMPLETELY REMOVED

- **Previous Implementation**: Multi-tenancy with tenant_id filtering throughout the application
- **Current Status**: Tenant isolation entirely removed
- **What Was Removed**:
  - Tenant middleware
  - Tenant context functions
  - Tenant validation in endpoints
  - Tenant_id filtering in database queries
  - Tenant_id fields in model creation
- **Current Implementation**: No multi-tenancy; all users access the same data

## 2. DATABASE CONNECTION STANDARDIZATION

### Direct Database Connections: PROHIBITED

- **Previous Implementation**: Mix of direct psycopg2/asyncpg connections and SQLAlchemy ORM
- **Current Status**: SQLAlchemy ORM connections only
- **What Was Removed**:
  - Direct psycopg2/asyncpg imports
  - Manual connection string construction
  - Custom connection handlers
- **Current Implementation**:
  - Supavisor connection pooling with proper configuration
  - Standardized session factory approach
  - Strict transaction boundaries

### Transaction Management: STANDARDIZED

- **Current Patterns**:
  - **Routers**: Own transaction boundaries with `async with session.begin()`
  - **Services**: Transaction-aware but never create their own transactions
  - **Background Tasks**: Create and manage their own transactions

## 3. FILE STRUCTURE REORGANIZATION

- Legacy routers have been removed or modernized
- New standardized services structure implemented
- Database connection handling consolidated
- Authentication simplified to JWT-only
- RBAC and tenant isolation code completely removed

## 4. WHAT TO DO IF YOU ENCOUNTER LEGACY CODE

If you find any of the following in the codebase:

### RBAC-Related Code
- Permission checks (`require_permission`, `has_permission`)
- Feature flag checks (`require_feature_enabled`)
- Role level checks (`require_role_level`)
- The constants file `src.constants.rbac`
- The utils file `src.utils.permissions`

### Tenant Isolation Code
- References to `tenant_id` in database queries
- References to `tenant_id` in model creation
- References to `tenant_context` or tenant middleware
- References to `validate_tenant_access` or tenant validation
- Use of `X-Tenant-ID` headers

### Direct Database Connections
- Direct imports of psycopg2 or asyncpg
- Manual connection string construction
- Custom connection handlers
- Direct connection objects
- PgBouncer-specific configurations

**STOP IMMEDIATELY** and:
1. Note the location of the code
2. Report it to the project maintainer
3. Do not modify the code until receiving guidance

## 5. CODE MIGRATION REFERENCE

Use this table to check if you're working with up-to-date patterns:

| Legacy Pattern | Current Pattern |
|----------------|-----------------|
| `require_permission(user, "permission")` | ❌ REMOVED - Use JWT auth only |
| `require_feature_enabled(tenant_id, "feature")` | ❌ REMOVED - Features available to all |
| `Model.tenant_id == tenant_id` in queries | ❌ REMOVED - No tenant filtering |
| Direct psycopg2/asyncpg connection | ✅ Use `get_db_session()` dependency |
| Service creating and committing transactions | ✅ Routers own transactions |
| Authentication logic in services | ✅ Move to router level |
| Transaction handling in services | ✅ Move to router level |
| Feature flag checking middleware | ❌ REMOVED - No feature flags |

## 6. CONCLUSION

The project has been significantly simplified by:
1. Removing the RBAC system entirely
2. Removing tenant isolation completely
3. Standardizing database connections
4. Enforcing proper transaction boundaries
5. Simplifying authentication to JWT-only

These changes have reduced complexity, improved maintainability, and resolved numerous transaction and authentication issues that were previously causing problems in the system.
