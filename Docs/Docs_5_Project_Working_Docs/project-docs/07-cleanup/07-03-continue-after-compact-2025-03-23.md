# CONTINUATION NOTES FOR SERVICE CONSOLIDATION

## CURRENT STATE (2025-03-23)
1. COMPLETED: Auth service consolidation
   - Standardized on jwt_auth.py across all routers
   - Removed tenant validation complexity, using DEFAULT_TENANT_ID consistently
   - Completed detailed tracking in AUTH_CONSOLIDATION_PROGRESS.md

2. COMPLETED: Error service consolidation
   - Standardized on services/error/error_service.py
   - Added ErrorService.route_error_handler to all router registrations in main.py

## NEXT PHASE: DATABASE SERVICE CONSOLIDATION
1. Goal: Standardize on services/core/db_service.py
2. Target files:
   - Check all routers for different database access patterns
   - Especially examine: db_portal.py, sitemap_analyzer.py, modernized_page_scraper.py
3. Approach:
   - Update imports to use db_service consistently
   - Ensure routers own transaction boundaries (async with session.begin())
   - Services should be transaction-aware but not create transactions
   - Replace direct SQL with db_service methods where possible

## IMPORTANT NOTES
1. Don't waste time on backup (.bak) files - they're not part of the active codebase
2. Skip tenant isolation code - we're drastically simplifying by using DEFAULT_TENANT_ID
3. Avoid changing the transaction pattern - transactions belong to routers, not services
4. Check for comments in the code about database connection handling - they might provide context

## FILES TO EXAMINE FOR DATABASE PATTERNS
1. src/services/core/db_service.py (this is our target standard)
2. src/routers/db_portal.py (likely has db access patterns)
3. src/db/session.py (likely has the session factory)
4. src/db/engine.py (database connection configuration)

## FOLLOW-UP VERIFICATION
After consolidating database services:
1. Run any database tests available (look in tests-for-transactions/ directory)
2. Check for SQL statements that might need updates
3. Verify remaining tenant_id handling is consistent

Reference the AUTH_CONSOLIDATION_PROGRESS.md file for the approach to tracking progress.