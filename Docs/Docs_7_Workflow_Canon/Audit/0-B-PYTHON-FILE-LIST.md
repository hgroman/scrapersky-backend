# Python Files in ScraperSky Project

This is a comprehensive list of all Python files in the ScraperSky project, aligned with the 7-layer architectural standard, superseding previous categorizations such as:

- System Infrastructure Layer (`1.0-System-Infrastructure-Layer.md`) (Note: This document describes foundational components not directly mapped to a single one of the 7 application layers and has been flagged for review)
- API Router Layer (now Layer 3: Routers, see `1.1-API-Router-Layer.md` - proposed rename `Layer-3_Routers_Audit-and-Dependencies.md`)
- Background Processing Layer (now primarily Layer 4: Services, see `1.2-Background Processing Layer.md` - proposed rename `Layer-4_Services_Background-Processing_Audit-and-Dependencies.md`)
  Files are documented in workflow documentation (`workflows/*.yaml`) and should be mapped to one of the 7 layers.

All files are properly documented, with no orphaned files remaining.

## Layer 1: Core Models & ENUMs (and Base Files)

- src/models/api_models.py
- src/models/base.py
- src/models/batch_job.py
- src/models/contact.py
- src/models/domain.py
- src/models/enums.py
- src/models/job.py
- src/models/local_business.py
- src/models/page.py
- src/models/place.py
- src/models/place_search.py
- src/models/profile.py
- src/models/sitemap.py
- src/models/sitemap_file.py
- src/models/tenant.py
- src/models/**init**.py

## Layer 3: Routers

- src/routers/batch_page_scraper.py
- src/routers/batch_sitemap.py
- src/routers/db_portal.py
- src/routers/dev_tools.py
- src/routers/domains.py
- src/routers/email_scanner.py
- src/routers/google_maps_api.py
- src/routers/local_businesses.py
- src/routers/modernized_page_scraper.py
- src/routers/modernized_sitemap.py
- src/routers/places_staging.py
- src/routers/profile.py
- src/routers/sitemap_files.py
- src/routers/sqlalchemy/**init**.py

## Layer 4: Services

- src/services/batch/batch_functions.py
- src/services/batch/batch_processor_service.py
- src/services/batch/types.py
- src/services/business_to_domain_service.py
- src/services/core/user_context_service.py
- src/services/core/validation_service.py
- src/services/db_inspector.py
- src/services/domain_scheduler.py
- src/services/domain_sitemap_submission_scheduler.py
- src/services/domain_to_sitemap_adapter_service.py
- src/services/job_service.py
- src/services/page_scraper/**init**.py
- src/services/page_scraper/domain_processor.py
- src/services/page_scraper/processing_service.py
- src/services/places/places_deep_service.py
- src/services/places/places_search_service.py
- src/services/places/places_service.py
- src/services/places/places_storage_service.py
- src/services/profile_service.py
- src/services/sitemap/processing_service.py
- src/services/sitemap/sitemap_service.py
- src/services/sitemap_files_service.py
- src/services/sitemap_import_scheduler.py
- src/services/sitemap_import_service.py
- src/services/sitemap_scheduler.py

## Layer 5: Configuration (and Utilities)

- src/auth/jwt_auth.py
- src/common/curation_sdk/scheduler_loop.py
- src/common/sitemap_parser.py
- src/config/settings.py
- src/core/**init**.py
- src/core/exceptions.py
- src/core/response.py
- src/db/session.py
- src/db/sitemap_handler.py
- src/scheduler_instance.py
- src/scraper/domain_utils.py
- src/scraper/metadata_extractor.py
- src/scraper/sitemap_analyzer.py
- src/scraper/utils.py
- src/session/async_session.py
- src/utils/db_helpers.py
- src/utils/scraper_api.py

## System Infrastructure Files (Cross-Cutting Concerns)

- src/**init**.py
- src/auth/**init**.py
- src/common/**init**.py
- src/config/logging_config.py
- src/config/runtime_tracer.py
- src/db/**init**.py
- src/db/engine.py
- src/health/**init**.py
- src/health/db_health.py
- src/main.py
- src/routers/**init**.py
- src/scraper/**init**.py
- src/services/**init**.py
- src/services/batch/**init**.py
- src/services/core/**init**.py
- src/services/places/**init**.py
- src/services/sitemap/**init**.py
- src/services/storage/**init**.py

## Layer 4: Tasks (Typically run by Services)

- src/tasks/email_scraper.py

## Layer 2: Schemas

- src/schemas/email_scan.py
- src/schemas/job.py
- src/schemas/sitemap_file.py
