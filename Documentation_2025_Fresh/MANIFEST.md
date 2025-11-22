# Codebase Manifest
**Generated:** 2025-11-22
**Status:** VERIFIED TRUTH

This document lists every active file in the `src/` directory. If a file is NOT on this list, it is either:
1.  **Dead Code** (Delete it)
2.  **New & Unverified** (Audit it)

## The Source of Truth (`src/`)

### Auth
- `src/auth/jwt_auth.py`: JWT authentication logic

### Common
- `src/common/crud_base.py`: Universal CRUD base class (Tier 3)
- `src/common/curation_sdk/scheduler_loop.py`: The "Brain" of background processing
- `src/common/sitemap_parser.py`: XML sitemap parsing logic

### Config
- `src/config/settings.py`: Environment variables and configuration
- `src/config/logging_config.py`: Centralized logging setup
- `src/config/runtime_tracer.py`: Debugging tool

### Core
- `src/core/exceptions.py`: Custom exception classes
- `src/core/response.py`: Standardized API response wrappers

### Database
- `src/db/engine.py`: SQLAlchemy async engine configuration (Supavisor settings)
- `src/db/session.py`: Session management
- `src/db/sitemap_handler.py`: Database-specific sitemap operations

### Models (The Schema Truth)
- `src/models/base.py`: SQLAlchemy Base and Mixins
- `src/models/enums.py`: **Centralized Enums (Tier 1 Rule)**
- `src/models/job.py`: Job tracking model
- `src/models/wf1_place_search.py`: Google Maps API results
- `src/models/wf1_place_staging.py`: Staging area for places
- `src/models/wf3_local_business.py`: Local Business entity
- `src/models/wf4_domain.py`: Domain entity
- `src/models/wf5_sitemap_file.py`: Sitemap file entity
- `src/models/wf7_page.py`: Page entity (Scraped content)
- `src/models/wf7_contact.py`: Contact entity (Extracted emails)

### Routers (The API Surface)
- `src/routers/wf1_google_maps_api_router.py`
- `src/routers/wf1_place_staging_router.py`
- `src/routers/wf3_local_business_router.py`
- `src/routers/wf4_domain_router.py`
- `src/routers/wf5_sitemap_file_router.py`
- `src/routers/wf5_sitemap_modernized_router.py`
- `src/routers/wf5_sitemap_batch_router.py`
- `src/routers/wf7_pages_router.py`
- `src/routers/wf7_page_modernized_scraper_router.py`
- `src/routers/wf7_page_batch_scraper_router.py`
- `src/routers/wf7_contacts_router.py`
- `src/routers/wf9_copilot_router.py`

### Services (The Business Logic)
- `src/services/wf3_business_to_domain_service.py`: Logic for extracting domains from businesses
- `src/services/wf4_domain_to_sitemap_adapter_service.py`: Logic for finding sitemaps
- `src/services/wf5_sitemap_import_service.py`: Logic for importing pages from sitemaps
- `src/services/wf7_page_curation_service.py`: Logic for scraping pages
- `src/services/crm/wf7_brevo_sync_service.py`: Brevo integration
- `src/services/crm/wf7_hubspot_sync_service.py`: HubSpot integration

### Schedulers (The Heartbeat)
- `src/services/background/wf3_domain_extraction_scheduler.py`
- `src/services/background/wf4_sitemap_discovery_scheduler.py`
- `src/services/background/wf5_sitemap_import_scheduler.py`
- `src/services/background/wf7_page_curation_scheduler.py`
- `src/services/background/wf7_crm_brevo_sync_scheduler.py`

### Utils
- `src/utils/honeybee_categorizer.py`: AI categorization logic
- `src/utils/scraper_api.py`: ScraperAPI client
- `src/utils/simple_scraper.py`: Fallback scraper

---
**Note:** This list is auto-generated. Always check `src/` for the absolute latest state, but treat this as the "Expected State".
