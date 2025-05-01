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
4. `/src/routers/modernized_page_scraper.py` - PURGE tenant validations, RBAC checks
5. `/src/routers/dev_tools.py` - PURGE tenant validations, RBAC checks
6. `/src/routers/profile.py` - PURGE tenant validations, RBAC checks
7. `/src/routers/sitemap.py` - PURGE tenant validations, RBAC checks
8. `/src/routers/db_portal.py` - PURGE tenant validations, RBAC checks
9. `/src/routers/__init__.py` - PURGE tenant middleware imports
10. `/src/routers/sitemap_analyzer.py` - PURGE tenant validations, RBAC checks
11. `/src/routers/sqlalchemy/*.py` - PURGE tenant validations, RBAC checks

### Service Files (19 files)

1. `/src/services/sitemap/processing_service.py` - PURGE tenant validations
2. `/src/services/sitemap/sitemap_service.py` - PURGE tenant validations
3. `/src/services/core/auth_service.py` - PURGE tenant validations
4. `/src/services/core/db_service.py` - PURGE tenant validations
5. `/src/services/error/error_service.py` - PURGE tenant error handling
6. `/src/services/domain_service.py` - PURGE tenant validations
7. `/src/services/job_service.py` - PURGE tenant validations
8. `/src/services/batch/batch_processor_service.py` - PURGE tenant validations
9. `/src/services/page_scraper/processing_service.py` - PURGE tenant validations
10. `/src/services/places/places_service.py` - PURGE tenant validations
11. `/src/services/places/places_storage_service.py` - PURGE tenant validations 
12. `/src/services/profile_service.py` - PURGE tenant validations
13. `/src/services/scraping/scrape_executor_service.py` - PURGE tenant validations
14. `/src/services/sitemap_service.py` - PURGE tenant validations
15. `/src/services/storage/storage_service.py` - PURGE tenant validations
16. `/src/services/validation/validation_service.py` - PURGE tenant validations
17. `/src/services/new/validation_service.py` - PURGE tenant validations
18. `/src/services/new/error_service.py` - PURGE tenant validations
19. `/src/services/__init__.py` - PURGE tenant imports

### Model Files (10 files)

1. `/src/models/job.py` - PURGE tenant relationships/fields
2. `/src/models/batch_job.py` - PURGE tenant relationships/fields
3. `/src/models/sitemap.py` - PURGE tenant relationships/fields
4. `/src/models/domain.py` - PURGE tenant relationships/fields
5. `/src/models/api_models.py` - PURGE tenant fields
6. `/src/models/sidebar.py` - PURGE tenant relationships/fields
7. `/src/models/place.py` - PURGE tenant relationships/fields
8. `/src/models/place_search.py` - PURGE tenant relationships/fields
9. `/src/models/user.py` - PURGE tenant relationships/fields
10. `/src/models/__init__.py` - PURGE tenant imports

### DB Files (4 files)

1. `/src/db/domain_handler.py` - PURGE tenant filters
2. `/src/db/sitemap_handler.py` - PURGE tenant filters
3. `/src/db/engine.py` - PURGE tenant context
4. `/src/db/session.py` - PURGE tenant context

## ACTION PLAN

1. **DELETE targeted files immediately**
2. **PURGE tenant code from remaining files:**
   - Remove all tenant validation code
   - Replace tenant_id with DEFAULT_TENANT_ID everywhere
   - Remove tenant context from session handling
   - Remove all RBAC checks and feature flags
   - Remove tenant foreign key usage

## SUCCESS CRITERIA

1. No files containing tenant middleware remain
2. All routing code uses a default tenant ID
3. No tenant context exists anywhere
4. All SQL queries run without tenant filtering
5. No feature flag or RBAC code remains
6. No tenant isolation enforcement remains

## COMPLETION CHECKLIST

- [x] All tenant middleware files DELETED, not "disabled"
- [x] All tenant isolation code REMOVED, not commented
- [x] All RBAC and feature flags REMOVED, not commented
- [x] All tenant relationship checks REMOVED
- [x] All DEFAULT_TENANT_ID replacements made
- [x] Verify application can start without errors
- [x] Verify API endpoints work without tenant headers