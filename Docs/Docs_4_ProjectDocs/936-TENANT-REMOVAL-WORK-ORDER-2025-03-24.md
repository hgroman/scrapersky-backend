# TENANT CODE REMOVAL WORK ORDER

## SCOPE: TOTAL FILES WITH TENANT CODE: 57

**OBJECTIVE: COMPLETELY DELETE ALL TENANT CODE, RBAC, AND FEATURE FLAGS - NO DEPRECATION COMMENTS**

## FILES TO DELETE COMPLETELY

1. `/src/auth/tenant_isolation.py` - DELETE THIS FILE
2. `/src/middleware/tenant_middleware.py` - DELETE THIS FILE
3. `/src/services/core/tenant_service.py` - DELETE THIS FILE 
4. `/src/middleware/__init__.py` - DELETE IF ONLY CONTAINING TENANT IMPORTS

## FILES TO PURGE OF ALL TENANT CODE

### Core/Highest Impact (9 files)

1. `/src/auth/dependencies.py` - PURGE all tenant references, replace with DEFAULT_TENANT_ID
2. `/src/auth/jwt_auth.py` - PURGE all tenant validation, keep JWT auth only
3. `/src/db/session.py` - PURGE tenant_context and all tenant-related code
4. `/src/main.py` - PURGE all tenant middleware registration
5. `/src/models/tenant.py` - PURGE functionality, remove from imports
6. `/src/services/sqlalchemy_service.py` - PURGE all tenant_context usage
7. `/src/models/user.py` - PURGE tenant relationship
8. `/src/models/profile.py` - PURGE tenant relationship
9. `/src/config/settings.py` - PURGE tenant configuration

### Router Files (11 files) 

1. `/src/routers/modernized_sitemap.py` - PURGE tenant validations, RBAC checks
2. `/src/routers/batch_page_scraper.py` - PURGE tenant validations, RBAC checks
3. `/src/routers/google_maps_api.py` - PURGE tenant validations, RBAC checks
4. `/src/routers/dev_tools.py` - PURGE tenant validations, RBAC checks
5. `/src/routers/profile.py` - PURGE tenant validations, RBAC checks
6. `/src/routers/sitemap_analyzer.py` - PURGE tenant validations, RBAC checks
7. `/src/routers/db_portal.py` - PURGE tenant validations, RBAC checks
8. `/src/routers/chat.py` - PURGE tenant validations, RBAC checks
9. `/src/routers/places_scraper.py` - PURGE tenant validations, RBAC checks
10. `/src/routers/sitemap_scraper.py` - PURGE tenant validations, RBAC checks
11. `/src/routers/email_scanner.py` - PURGE tenant validations, RBAC checks

### Service Files (25 files)

1. `/src/services/sitemap/processing_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
2. `/src/services/places/places_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
3. `/src/services/places/places_search_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
4. `/src/services/places/places_storage_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
5. `/src/services/scraping/scrape_executor_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
6. `/src/services/page_scraper/processing_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
7. `/src/services/batch/batch_processor_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
8. `/src/services/job_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
9. `/src/services/domain_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
10. `/src/services/profile_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
11. `/src/services/storage/storage_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
12. `/src/services/core/user_context_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
13. `/src/services/core/auth_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
14. `/src/services/core/validation_service.py` - PURGE tenant validations
15. `/src/services/core/db_service.py` - PURGE tenant context handling
16. `/src/services/sitemap_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
17. `/src/services/error/error_service.py` - PURGE tenant references in errors
18. `/src/services/new/error_service.py` - PURGE tenant references in errors
19. `/src/services/core/error_service.py` - PURGE tenant references in errors
20. `/src/services/db_inspector.py` - PURGE tenant filtering
21. `/src/services/sitemap/analyzer_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
22. `/src/services/sitemap/sitemap_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
23. `/src/services/sitemap/background_service.py` - PURGE tenant DB checks, use DEFAULT_TENANT_ID
24. `/src/services/email_service.py` - PURGE tenant references
25. `/src/services/places_search_service.py` - PURGE tenant references

### Model Files (10 files)

1. `/src/models/__init__.py` - PURGE tenant model imports
2. `/src/models/api_models.py` - PURGE tenant fields
3. `/src/models/domain.py` - KEEP tenant_id field, PURGE validation
4. `/src/models/job.py` - KEEP tenant_id field, PURGE validation
5. `/src/models/place.py` - KEEP tenant_id field, PURGE validation 
6. `/src/models/place_search.py` - KEEP tenant_id field, PURGE validation
7. `/src/models/sidebar.py` - REMOVE feature flag relationship
8. `/src/models/sitemap.py` - KEEP tenant_id field, PURGE validation
9. `/src/models/base.py` - REMOVE tenant/RBAC fields
10. `/src/models/batch_job.py` - KEEP tenant_id field, PURGE validation

### Other Files (2)

1. `/src/db/domain_handler.py` - PURGE tenant checks
2. `/src/db/sitemap_handler.py` - PURGE tenant checks

## IMPLEMENTATION GUIDELINES

1. **Keep Column References**: Keep tenant_id columns in models but REMOVE all validation
2. **Use DEFAULT_TENANT_ID**: Always use `DEFAULT_TENANT_ID` from jwt_auth.py (UUID format)
3. **Remove DB Checks**: Remove `SELECT FROM tenant` or `if tenant not exist` checks
4. **Remove RBAC**: Delete all `require_permission`, `require_role`, feature flag checks
5. **NO COMMENTS**: Don't add "# Tenant code removed" comments - remove code completely
6. **Security**: Remove code so service layer is security-unaware - keep JWT in routers only
7. **Hard-code tenant_id**: Use `tenant_id="550e8400-e29b-41d4-a716-446655440000"` for any DB creation

## VERIFICATION POINTS

After each file update, verify:

1. File compiles with no errors
2. No references to tenant existence checking
3. No RBAC or feature flag checks
4. Domain/job creation uses DEFAULT_TENANT_ID
5. All tenant relationships are removed from User/Profile models
6. Only the JWT part of auth remains (no tenant or role validation)

## TIMING GUIDANCE

Estimated 6-8 hours of work for all files.

**Priority order:**
1. Core files - especially auth/jwt_auth.py
2. Router files - start with modernized_sitemap.py
3. Service files - start with processing_service.py
4. Model files - start with tenant.py

## REPORT COMPLETION

Create completion report showing:
1. Deleted files
2. Purged files with line count delta
3. Verification all code runs with proper tenant as default