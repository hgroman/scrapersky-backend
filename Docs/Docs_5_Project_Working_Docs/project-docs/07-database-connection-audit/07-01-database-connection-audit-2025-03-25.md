# Database Connection Audit - MANDATORY COMPLIANCE REQUIRED

**Date:** 2025-03-25  
**Author:** System Audit  
**Status:** CRITICAL - In Progress
**Enforcement:** MANDATORY

## Purpose

This document establishes the ONE AND ONLY ONE acceptable method for database connections in the ScraperSky backend. **NO EXCEPTIONS WILL BE PERMITTED**. This is a comprehensive audit of all database connection points in the codebase with the goal of identifying and eliminating any non-compliant connection methods.

## CRITICAL MANDATE

**THERE IS ONLY ONE ACCEPTABLE WAY TO CONNECT TO THE DATABASE:**

```python
# In FastAPI route handlers:
async def your_endpoint(
    session: AsyncSession = Depends(get_session_dependency),
    # other dependencies...
):
    # Use the session here
    # NO MANUAL SESSION CREATION ALLOWED

# In services that receive a session parameter:
async def your_service_function(data: Dict, session: AsyncSession):
    # Use the provided session
    # NEVER CREATE YOUR OWN SESSION
```

**ANY OTHER METHOD OF DATABASE CONNECTION IS STRICTLY FORBIDDEN AND WILL BE ELIMINATED.**

## Connection Requirements - ZERO TOLERANCE FOR NON-COMPLIANCE

All database connections to Supabase MUST:

1. Use the correct username format: `postgres.[project-ref]` (e.g., postgres.ddfldwzhdhhzhxywqnyz)
2. Configure SSL context with certificate verification disabled
3. Disable statement cache for pgbouncer compatibility
4. Use the pooler approach for compatibility with Render.com in production
5. Follow the architectural mandate to remove tenant filtering from database operations

**THESE REQUIREMENTS ARE IMPLEMENTED IN THE CENTRALIZED SESSION FACTORY AND DEPENDENCY.**

**DIRECT DATABASE CONNECTIONS THAT BYPASS THIS CENTRALIZED APPROACH ARE STRICTLY FORBIDDEN.**

## Connection Points Audit

| Module | File | Line | Connection Method | Status | Notes |
|--------|------|------|-------------------|--------|-------|
| Session | `/src/session/async_session.py` | 149-154 | `async_session_factory` | ✅ Correct | Main session factory, properly configured |
| Session | `/src/db/direct_session.py` | 131-136 | `direct_session_factory` | ⚠️ Review | Temporary workaround, should be consolidated |
| Sitemap | `/src/services/sitemap/processing_service.py` | ~654 | Direct session creation | ❌ Fix Required | Should use proper session factory |
| Debug | `/debug_sitemap_flow.py` | Multiple | Direct connection | ❌ Fix Required | Should use proper session factory |
| Google Maps | `/src/routers/google_maps_api.py` | Multiple | Direct `async_session_factory()` | ❌ Fix Required | Should use dependency injection |
| Batch Scraper | `/src/routers/batch_page_scraper.py` | Multiple | Direct `async_session_factory()` | ❌ Fix Required | Should use dependency injection |

## Dependency Injection Usage Audit

Most files correctly use dependency injection with `Depends(get_session_dependency)`:

| Module | File | Status | Notes |
|--------|------|--------|-------|
| Page Scraper | `/src/routers/modernized_page_scraper.py` | ✅ Correct | Uses dependency injection |
| Dev Tools | `/src/routers/dev_tools.py` | ✅ Correct | Uses dependency injection |
| Profile | `/src/routers/profile.py` | ✅ Correct | Uses dependency injection |
| DB Inspector | `/src/services/db_inspector.py` | ✅ Correct | Uses session parameter |
| Job Service | `/src/services/job_service.py` | ✅ Correct | Uses session parameter |
| Batch Processor | `/src/services/batch/batch_processor_service.py` | ✅ Correct | Uses session parameter |
| Profile Service | `/src/services/profile_service.py` | ✅ Correct | Uses session parameter |
| Page Scraper | `/src/services/page_scraper/processing_service.py` | ✅ Correct | Uses session parameter |

## Action Items - MANDATORY ENFORCEMENT PLAN

1. **ELIMINATE direct session creation in sitemap processing service**
   - REPLACE ALL direct session creation with FastAPI dependency injection
   - ENFORCE architectural mandate with zero exceptions

2. **ELIMINATE non-compliant code in debug_sitemap_flow.py**
   - ENFORCE use of proper session dependency
   - FIX ALL indentation issues

3. **ELIMINATE direct session creation in Google Maps API router**
   - REPLACE ALL direct `async_session_factory()` calls with dependency injection
   - NO EXCEPTIONS PERMITTED

4. **ELIMINATE direct session creation in Batch Page Scraper router**
   - REPLACE ALL direct `async_session_factory()` calls with dependency injection
   - ZERO TOLERANCE for non-compliance

5. **ENFORCE single session factory standard**
   - CONSOLIDATE `direct_session_factory` and `async_session_factory`
   - MANDATE use of a single, properly configured session factory

6. **IMPLEMENT automated compliance verification**
   - DEVELOP tests that FAIL if non-compliant connections are detected
   - INCLUDE comprehensive tests for Supabase pooler connection

7. **ESTABLISH clear documentation and enforcement**
   - DOCUMENT the ONE AND ONLY ONE acceptable connection method in the README
   - CREATE mandatory developer guidelines with zero tolerance for violations
   - ADD pre-commit hooks to detect and reject non-compliant code

8. **CONDUCT comprehensive codebase audit**
   - USE automated tools to find ALL instances of database connections
   - VERIFY 100% compliance with no exceptions
   - IMPLEMENT continuous monitoring for future compliance

## Verification Process - ZERO EXCEPTIONS

For each connection point:

1. VERIFY it uses ONLY the FastAPI dependency injection pattern
2. VERIFY it NEVER creates its own database sessions
3. VERIFY it uses the correct username format
4. VERIFY SSL context is properly configured
5. VERIFY statement cache is disabled
6. VERIFY it follows the architectural mandate with NO JWT/tenant logic
7. TEST the connection with actual database operations

**ANY CODE THAT FAILS VERIFICATION WILL BE IMMEDIATELY FIXED OR REMOVED.**

**NO EXCEPTIONS, NO SPECIAL CASES, NO WORKAROUNDS PERMITTED.**

## Progress Tracking

| Action Item | Status | Assigned To | Due Date | Notes |
|-------------|--------|-------------|----------|-------|
| Fix sitemap processing service | Not Started | | 2025-03-26 | |
| Fix debug_sitemap_flow.py | Not Started | | 2025-03-26 | |
| Fix Google Maps API router | Not Started | | 2025-03-27 | |
| Fix Batch Page Scraper router | Not Started | | 2025-03-27 | |
| Consolidate session factories | Not Started | | 2025-03-28 | |
| Create automated tests | Not Started | | 2025-03-29 | |
| Update documentation | Not Started | | 2025-03-30 | |
