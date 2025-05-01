# Functional Dependency Map (Reverse Engineered from UI)

This report maps used Python files (`src/`) back to the business functions identified via UI tabs and API calls.
**Note:** This is based on tracing dependencies from specific router entry points identified from UI interactions. 'Core/Shared' indicates files used by multiple functions or matching common patterns.

| File Path | Mapped Business Function(s) | Entry Point(s) | Notes |
|---|---|---|---|
| `src/auth/jwt_auth.py` | Core/Shared | src/routers/google_maps_api.py |  |
| `src/config/logging_config.py` | Core/Shared | N/A |  |
| `src/config/settings.py` | Core/Shared | src/routers/google_maps_api.py |  |
| `src/db/engine.py` | Core/Shared | N/A |  |
| `src/db/session.py` | Core/Shared | src/routers/google_maps_api.py |  |
| `src/db/sitemap_handler.py` | Core/Shared | N/A |  |
| `src/models.py` | Core/Shared | src/routers/google_maps_api.py |  |
| `src/models/api_models.py` | Core/Shared | N/A |  |
| `src/models/base.py` | Core/Shared | src/routers/google_maps_api.py |  |
| `src/models/enums.py` | Core/Shared | N/A |  |
| `src/models/job.py` | Core/Shared | N/A |  |
| `src/models/user.py` | Core/Shared | N/A |  |
| `src/schemas/job.py` | Core/Shared | N/A |  |
| `src/session/async_session.py` | Core/Shared | src/routers/google_maps_api.py |  |
| `src/routers/dev_tools.py` | DevTool | N/A |  |
| `src/models/place.py` | LocalMiner | src/routers/google_maps_api.py |  |
| `src/models/place_search.py` | LocalMiner | src/routers/google_maps_api.py |  |
| `src/models/tenant.py` | LocalMiner | src/routers/google_maps_api.py |  |
| `src/routers/google_maps_api.py` | LocalMiner | src/routers/google_maps_api.py |  |
| `src/services/job_service.py` | LocalMiner | src/routers/google_maps_api.py |  |
| `src/services/places/places_search_service.py` | LocalMiner | src/routers/google_maps_api.py |  |
| `src/services/places/places_service.py` | LocalMiner | src/routers/google_maps_api.py |  |
| `src/services/places/places_storage_service.py` | LocalMiner | src/routers/google_maps_api.py |  |
| `src/core/exceptions.py` | Unmapped | N/A |  |
| `src/core/response.py` | Unmapped | N/A |  |
| `src/health/db_health.py` | Unmapped | N/A |  |
| `src/main.py` | Unmapped | N/A |  |
| `src/models/batch_job.py` | Unmapped | N/A |  |
| `src/models/contact.py` | Unmapped | N/A |  |
| `src/models/domain.py` | Unmapped | N/A |  |
| `src/models/local_business.py` | Unmapped | N/A |  |
| `src/models/page.py` | Unmapped | N/A |  |
| `src/models/profile.py` | Unmapped | N/A |  |
| `src/models/sitemap.py` | Unmapped | N/A |  |
| `src/routers/batch_page_scraper.py` | Unmapped | N/A |  |
| `src/routers/batch_sitemap.py` | Unmapped | N/A |  |
| `src/routers/db_portal.py` | Unmapped | N/A |  |
| `src/routers/domains.py` | Unmapped | N/A |  |
| `src/routers/email_scanner.py` | Unmapped | N/A |  |
| `src/routers/local_businesses.py` | Unmapped | N/A |  |
| `src/routers/modernized_page_scraper.py` | Unmapped | N/A |  |
| `src/routers/modernized_sitemap.py` | Unmapped | N/A |  |
| `src/routers/places_staging.py` | Unmapped | N/A |  |
| `src/routers/profile.py` | Unmapped | N/A |  |
| `src/routers/sitemap_files.py` | Unmapped | N/A |  |
| `src/scheduler_instance.py` | Unmapped | N/A |  |
| `src/schemas/email_scan.py` | Unmapped | N/A |  |
| `src/schemas/sitemap_file.py` | Unmapped | N/A |  |
| `src/scraper/domain_utils.py` | Unmapped | N/A |  |
| `src/scraper/metadata_extractor.py` | Unmapped | N/A |  |
| `src/scraper/sitemap_analyzer.py` | Unmapped | N/A |  |
| `src/scraper/utils.py` | Unmapped | N/A |  |
| `src/services/batch/batch_functions.py` | Unmapped | N/A |  |
| `src/services/batch/batch_processor_service.py` | Unmapped | N/A |  |
| `src/services/batch/simple_task_test.py` | Unmapped | N/A |  |
| `src/services/batch/types.py` | Unmapped | N/A |  |
| `src/services/business_to_domain_service.py` | Unmapped | N/A |  |
| `src/services/core/db_service.py` | Unmapped | N/A |  |
| `src/services/core/user_context_service.py` | Unmapped | N/A |  |
| `src/services/core/validation_service.py` | Unmapped | N/A |  |
| `src/services/db_inspector.py` | Unmapped | N/A |  |
| `src/services/domain_scheduler.py` | Unmapped | N/A |  |
| `src/services/domain_sitemap_submission_scheduler.py` | Unmapped | N/A |  |
| `src/services/domain_to_sitemap_adapter_service.py` | Unmapped | N/A |  |
| `src/services/page_scraper/domain_processor.py` | Unmapped | N/A |  |
| `src/services/page_scraper/processing_service.py` | Unmapped | N/A |  |
| `src/services/places/places_deep_service.py` | Unmapped | N/A |  |
| `src/services/profile_service.py` | Unmapped | N/A |  |
| `src/services/sitemap/processing_service.py` | Unmapped | N/A |  |
| `src/services/sitemap_files_service.py` | Unmapped | N/A |  |
| `src/services/sitemap_scheduler.py` | Unmapped | N/A |  |
| `src/tasks/email_scraper.py` | Unmapped | N/A |  |
| `src/utils/db_helpers.py` | Unmapped | N/A |  |
| `src/utils/scraper_api.py` | Unmapped | N/A |  |

## Summary
- **Total Used Files Analyzed:** 74
- **Files Primarily Mapped to LocalMiner:** 8
- **Files Categorized as Core/Shared:** 14
- **Files Categorized as DevTool:** 1
- **Unmapped Files:** 51

### Unmapped Files:
- `src/core/exceptions.py`
- `src/core/response.py`
- `src/health/db_health.py`
- `src/main.py`
- `src/models/batch_job.py`
- `src/models/contact.py`
- `src/models/domain.py`
- `src/models/local_business.py`
- `src/models/page.py`
- `src/models/profile.py`
- `src/models/sitemap.py`
- `src/routers/batch_page_scraper.py`
- `src/routers/batch_sitemap.py`
- `src/routers/db_portal.py`
- `src/routers/domains.py`
- `src/routers/email_scanner.py`
- `src/routers/local_businesses.py`
- `src/routers/modernized_page_scraper.py`
- `src/routers/modernized_sitemap.py`
- `src/routers/places_staging.py`
- `src/routers/profile.py`
- `src/routers/sitemap_files.py`
- `src/scheduler_instance.py`
- `src/schemas/email_scan.py`
- `src/schemas/sitemap_file.py`
- `src/scraper/domain_utils.py`
- `src/scraper/metadata_extractor.py`
- `src/scraper/sitemap_analyzer.py`
- `src/scraper/utils.py`
- `src/services/batch/batch_functions.py`
- `src/services/batch/batch_processor_service.py`
- `src/services/batch/simple_task_test.py`
- `src/services/batch/types.py`
- `src/services/business_to_domain_service.py`
- `src/services/core/db_service.py`
- `src/services/core/user_context_service.py`
- `src/services/core/validation_service.py`
- `src/services/db_inspector.py`
- `src/services/domain_scheduler.py`
- `src/services/domain_sitemap_submission_scheduler.py`
- `src/services/domain_to_sitemap_adapter_service.py`
- `src/services/page_scraper/domain_processor.py`
- `src/services/page_scraper/processing_service.py`
- `src/services/places/places_deep_service.py`
- `src/services/profile_service.py`
- `src/services/sitemap/processing_service.py`
- `src/services/sitemap_files_service.py`
- `src/services/sitemap_scheduler.py`
- `src/tasks/email_scraper.py`
- `src/utils/db_helpers.py`
- `src/utils/scraper_api.py`
