# All Python Files in src/ Directory

This is a complete inventory of all Python files in the ScraperSky backend project as of the current date. The files are organized alphabetically by path.

```
src/__init__.py
src/auth/__init__.py
src/auth/jwt_auth.py
src/common/__init__.py
src/common/curation_sdk/scheduler_loop.py
src/common/sitemap_parser.py
src/config/logging_config.py (Layer 5: Configuration)
src/config/runtime_tracer.py (Layer 5: Configuration)
src/config/settings.py (Layer 5: Configuration)
src/core/__init__.py
src/core/exceptions.py
src/core/response.py
src/db/__init__.py
src/db/engine.py
src/db/session.py
src/db/sitemap_handler.py
src/health/__init__.py
src/health/db_health.py
src/main.py
src/models/__init__.py (Layer 1: Models & ENUMs)
src/models/api_models.py (Layer 1: Models & ENUMs)
src/models/base.py (Layer 1: Models & ENUMs)
src/models/batch_job.py (Layer 1: Models & ENUMs)
src/models/contact.py (Layer 1: Models & ENUMs)
src/models/domain.py (Layer 1: Models & ENUMs)
src/models/enums.py (Layer 1: Models & ENUMs)
src/models/job.py (Layer 1: Models & ENUMs)
src/models/local_business.py (Layer 1: Models & ENUMs)
src/models/page.py (Layer 1: Models & ENUMs)
src/models/place_search.py (Layer 1: Models & ENUMs)
src/models/place.py (Layer 1: Models & ENUMs)
src/models/profile.py (Layer 1: Models & ENUMs)
src/models/sitemap_file.py (Layer 1: Models & ENUMs)
src/models/sitemap.py (Layer 1: Models & ENUMs)
src/models/tenant.py (Layer 1: Models & ENUMs)
src/routers/__init__.py (Layer 3: Routers)
src/routers/batch_page_scraper.py (Layer 3: Routers)
src/routers/batch_sitemap.py (Layer 3: Routers)
src/routers/db_portal.py (Layer 3: Routers)
src/routers/dev_tools.py (Layer 3: Routers)
src/routers/domains.py (Layer 3: Routers)
src/routers/email_scanner.py (Layer 3: Routers)
src/routers/google_maps_api.py (Layer 3: Routers)
src/routers/local_businesses.py (Layer 3: Routers)
src/routers/modernized_page_scraper.py (Layer 3: Routers)
src/routers/modernized_sitemap.py (Layer 3: Routers)
src/routers/places_staging.py (Layer 3: Routers)
src/routers/profile.py (Layer 3: Routers)
src/routers/sitemap_files.py (Layer 3: Routers)
src/routers/sqlalchemy/__init__.py (Layer 3: Routers)
src/scheduler_instance.py
src/schemas/email_scan.py (Layer 2: Schemas)
src/schemas/job.py (Layer 2: Schemas)
src/schemas/sitemap_file.py (Layer 2: Schemas)
src/scraper/__init__.py
src/scraper/domain_utils.py
src/scraper/metadata_extractor.py
src/scraper/sitemap_analyzer.py
src/scraper/utils.py
src/services/__init__.py (Layer 4: Services)
src/services/batch/__init__.py (Layer 4: Services)
src/services/batch/batch_functions.py (Layer 4: Services)
src/services/batch/batch_processor_service.py (Layer 4: Services)
src/services/batch/types.py (Layer 4: Services)
src/services/business_to_domain_service.py (Layer 4: Services)
src/services/core/__init__.py (Layer 4: Services)
src/services/core/user_context_service.py (Layer 4: Services)
src/services/core/validation_service.py (Layer 4: Services)
src/services/db_inspector.py (Layer 4: Services)
src/services/domain_scheduler.py (Layer 4: Services)
src/services/domain_sitemap_submission_scheduler.py (Layer 4: Services)
src/services/domain_to_sitemap_adapter_service.py (Layer 4: Services)
src/services/job_service.py (Layer 4: Services)
src/services/page_scraper/__init__.py (Layer 4: Services)
src/services/page_scraper/domain_processor.py (Layer 4: Services)
src/services/page_scraper/processing_service.py (Layer 4: Services)
src/services/places/__init__.py (Layer 4: Services)
src/services/places/places_deep_service.py (Layer 4: Services)
src/services/places/places_search_service.py (Layer 4: Services)
src/services/places/places_service.py (Layer 4: Services)
src/services/places/places_storage_service.py (Layer 4: Services)
src/services/profile_service.py (Layer 4: Services)
src/services/sitemap_files_service.py (Layer 4: Services)
src/services/sitemap_import_scheduler.py (Layer 4: Services)
src/services/sitemap_import_service.py (Layer 4: Services)
src/services/sitemap_scheduler.py (Layer 4: Services)
src/services/sitemap/__init__.py (Layer 4: Services)
src/services/sitemap/processing_service.py (Layer 4: Services)
src/services/sitemap/sitemap_service.py (Layer 4: Services)
src/services/storage/__init__.py (Layer 4: Services)
src/session/async_session.py
src/tasks/email_scraper.py
src/utils/db_helpers.py
src/utils/scraper_api.py
```

There are 94 Python files in total in the src directory.

## Comparison with Workflow Documentation

This list shows the actual source code files in the project. It can be used to validate that all workflow documentation correctly references the files they depend on.

Key observations:

- Three previously identified orphaned files have been properly handled:
  - `src/common/curation_sdk/router_base.py` has been moved to the archive directory
  - `src/common/curation_sdk/status_queue_helper.py` has been moved to the archive directory
  - `src/services/batch/simple_task_test.py` has been moved to the Layer 7: Tests directory
- The file previously referenced as `src/services/page_scraper/page_scraper_service.py` is actually named `processing_service.py` (Layer 4: Services)
- All essential infrastructure files are now documented in `1.0-System-Infrastructure-Layer.md`
- All Layer 4: Service packages have proper `__init__.py` files for Python package structure
- There are no longer any orphaned files in the codebase
