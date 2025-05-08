# Supabase Connection Issue Documentation

## Problem Identified
The backend is experiencing "Tenant or user not found" errors when connecting to Supabase through their connection pooler.

## Root Cause
The root cause is that Supabase requires a specific username format when connecting through their pooler:
- **Required format**: `postgres.[project-ref]` (e.g., postgres.ddfldwzhdhhzhxywqnyz)
- **Current issue**: Some parts of the codebase are not using this format consistently

## Final Assessment
After reviewing the code, we've found that:

1. The `/src/session/async_session.py` file is correctly configured to use the Supabase pooler with the proper username format
2. The `/src/db/direct_session.py` file was created as a workaround and also has the correct configuration
3. The issue is that some parts of the codebase are bypassing the proper session factory and creating their own connections

## Working Solution
The solution that works is:
1. Username format: `postgres.[project-ref]` (e.g., postgres.ddfldwzhdhhzhxywqnyz)
2. SSL context configuration with certificate verification disabled
3. Statement cache disabled for pgbouncer compatibility

## Comprehensive Approach to Fix All Database Connections

### Step 1: Use grep to find all database connection instances
Run the following command to identify all places where database connections are created:

```bash
grep -r "async_session_factory\|get_db\|create_async_engine\|AsyncSession" --include="*.py" ./src
```

### Step 2: Verify session.py is correctly configured
Ensure that `src/db/session.py` uses the correct username format for Supabase pooler. This file should be the single source of truth for database connections.

### Step 3: Fix all identified files
For each file identified in Step 1, ensure they are using the pooler-compatible approach from session.py instead of creating their own connections.

### Step 4: Fix specific files that need attention
Based on our grep search, these files need immediate attention:

1. `/src/session/async_session.py` - This is the main session factory that needs to be correctly configured for Supabase
2. `/src/services/sitemap/processing_service.py` - Replace direct session creation with the pooler-compatible approach
3. `/src/routers/google_maps_api.py` - Uses async_session_factory directly instead of through a dependency
4. `/src/routers/batch_page_scraper.py` - Uses async_session_factory directly
5. `/debug_sitemap_flow.py` - Ensure it uses the pooler-compatible approach

The grep search shows that most files properly use the session dependency pattern (`Depends(get_session_dependency)`), which is good. We need to focus on fixing the files that create sessions directly.

### Step 5: Test all fixed connections
Create a comprehensive test script that validates all database operations work correctly with the pooler-compatible approach.

## Important Notes
1. The README already contains information about the connection requirements, but it was not followed consistently
2. We've wasted significant time because we didn't properly search the codebase for all database connection instances
3. The test script we created (`test_supabase_connection.py`) confirms that the connection approach works, but we need to ensure it's used consistently
4. The core issue is in `/src/session/async_session.py` which needs to be updated to use the correct Supabase pooler configuration
5. Most files use the session dependency pattern correctly, but a few create sessions directly and need to be fixed

## Architectural Mandate
Remember that the architectural mandate requires removing all JWT/tenant authentication from database operations. This should be done while fixing the connection issues.

## Action Plan

1. **Fix `/src/services/sitemap/processing_service.py`**:
   - Ensure it uses the proper session factory from async_session.py
   - Remove any direct session creation that bypasses the factory

2. **Fix `/debug_sitemap_flow.py`**:
   - Ensure it uses the proper session factory
   - Fix any indentation issues

3. **Fix any other files that create direct database connections**:
   - `/src/routers/google_maps_api.py`
   - `/src/routers/batch_page_scraper.py`

4. **Verify that all connections use the correct format**:
   - Username: `postgres.[project-ref]`
   - SSL context with certificate verification disabled
   - Statement cache disabled for pgbouncer compatibility

5. **Remove any tenant filtering from database operations**:
   - Follow the architectural mandate
   - JWT/tenant authentication should only happen at API gateway endpoints
