# Complete Tenant Isolation and RBAC Removal Plan

## Target Areas for Removal

1. **Core Tenant Files**
   - `/src/auth/tenant_isolation.py` (Complete removal)
   - `/src/middleware/tenant_middleware.py` (Complete removal)
   - `/src/models/tenant.py` (Keep DB schema but remove functionality)
   - `/src/services/core/tenant_service.py` (Complete removal)

2. **RBAC & Feature Flag Components**
   - All imports and usage of RBAC constants, permissions
   - Remove all feature flag checks and custom permissions
   - Remove role hierarchy and access level checks 

3. **Authentication Components to Modify**
   - `/src/auth/dependencies.py` (Remove tenant validation, keep JWT)
   - `/src/auth/jwt_auth.py` (Remove tenant checks, keep auth)
   - `/src/auth/auth_service.py` (Remove tenant validation)

4. **Router Changes**
   - Remove tenant validations from all endpoint handlers
   - Replace tenant dependency checks with minimal implementation
   - Replace tenant validations with DEFAULT_TENANT_ID

5. **Model & Schema Changes**
   - Maintain `tenant_id` columns in database schemas but ignore
   - Remove tenant validation from Pydantic models
   - Replace tenant references with DEFAULT_TENANT_ID

6. **Session & DB Changes**
   - Remove tenant context from session management
   - Remove Row-Level Security (RLS) tenant filters

## Implementation Steps

### 1. Baseline Setup 

1. Create a DEFAULT_TENANT_ID constant in a central location
2. Ensure all JWT auth continues to work without tenant validation

### 2. Purge Core Tenant Implementation

1. Remove tenant middleware registration from main.py
2. Disable all tenant validation code
3. Remove tenant context managers from database code
4. Create placeholder tenant_id parameter handlers 

### 3. Modify All Router Files

1. Replace tenant validation with DEFAULT_TENANT_ID
2. Remove feature flag and permission checks
3. Keep JWT auth but remove tenant validation

### 4. Update Session Management

1. Remove tenant context from session creation
2. Remove Row-Level Security (RLS) filters
3. Simplify session initialization 

### 5. Update DB Services

1. Remove tenant filtering from SQL queries
2. Default all tenant_id fields to DEFAULT_TENANT_ID
3. Eliminate RLS policy enforcement

### 6. Check Database Compatibility

1. Keep all tenant_id columns for compatibility
2. Default tenant_id values to DEFAULT_TENANT_ID
3. Remove foreign key constraints to tenant table if possible

## Files to Modify

### High Priority
1. `/src/auth/tenant_isolation.py` - Complete removal or replacement with dummy functions
2. `/src/middleware/tenant_middleware.py` - Complete removal
3. `/src/auth/dependencies.py` - Remove tenant checks, keep JWT auth
4. `/src/main.py` - Remove tenant middleware registration
5. `/src/session/async_session.py` - Remove tenant context
6. `/src/routers/modernized_sitemap.py` - Replace tenant validation with default
7. `/src/routers/batch_page_scraper.py` - Replace tenant validation with default
8. `/src/routers/google_maps_api.py` - Replace tenant validation with default

### Secondary Priority
1. `/src/models/tenant.py` - Disable functionality, keep schema
2. `/src/models/user.py` - Remove tenant relationship 
3. `/src/models/profile.py` - Remove tenant relationship
4. `/src/services/core/tenant_service.py` - Replace with dummy service
5. All remaining service files with tenant references

### Final Cleanup
1. Update all imports to remove unused tenant modules
2. Remove commented tenant code
3. Update documentation to remove tenant references

## Implementation Approach

For each file:
1. Create a backup of the original file
2. Remove all tenant-related imports
3. Replace tenant validation with DEFAULT_TENANT_ID
4. Remove tenant filtering from DB queries
5. Remove RBAC and feature flag checks
6. Test functionality after changes

## Expected Outcome

1. System operates with a single default tenant behind the scenes
2. All authentication works via JWT without tenant isolation
3. All tenant_id fields are set to DEFAULT_TENANT_ID
4. All RBAC and permission checks are removed
5. Feature flags are disabled/removed