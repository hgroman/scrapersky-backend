# SCRAPERSKY UNUSED FILES

This document lists files that are not directly referenced by any active route handlers. These files may be candidates for archiving or removal.

## OBSOLETE ROUTER FILES
- src/routers/page_scraper.py 
- src/routers/sitemap.py
- src/routers/modernized_sitemap.bak.3.21.25.py

## DUPLICATE SERVICE IMPLEMENTATIONS
- src/services/core/error_service.py (duplicate of services/error/error_service.py)
- src/services/new/error_service.py (duplicate of services/error/error_service.py)
- src/services/core/validation_service.py (duplicate of services/validation/validation_service.py)
- src/services/new/validation_service.py (duplicate of services/validation/validation_service.py)
- src/services/db_service.py (duplicate of services/core/db_service.py)
- src/services/sitemap_service.py (duplicate of services/sitemap/sitemap_service.py)
- src/auth/auth_service.py (duplicate of services/core/auth_service.py)

## ABANDONED DATABASE CONNECTION FILES
- src/db/async_sb_connection.py (should use engine.py or session.py instead)
- src/db/sb_connection.py (should use engine.py or session.py instead)
- src/db/sb_connection copy.py (obvious duplicate)

## UNUSED UTILITY FILES
- src/utils/db_schema_helper.py (not imported anywhere)
- src/utils/db_utils.py (not imported anywhere)
- src/utils/scraper_api.py (not imported anywhere)
- src/utils/sidebar.py (not imported anywhere)

## UNUSED TASK FILES
- src/tasks/email_scraper.py (router has been deleted)

## UNUSED TEST FILES
- src/test_domain_scrape.py (should be moved to tests directory)

## OBSOLETE TENANT ISOLATION CODE
- src/middleware/tenant_middleware.py (tenant isolation was removed)
- src/auth/tenant_isolation.py (tenant isolation was removed)

## UNUSED MODEL FILES 
- src/models/sidebar.py (sidebar functionality is limited)

## SUMMARY
- 7 duplicate service implementations
- 3 obsolete router files
- 3 abandoned database connection files
- 4 unused utility files
- 1 unused task file
- 1 unused test file
- 2 obsolete tenant isolation files
- 1 unused model file

Total files that can be removed or archived: 22