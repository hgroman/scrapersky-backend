# ScraperSky Files by Layer and Workflow

**Date:** 2025-05-19
**Version:** 2.0
**Last Updated By:** Claude

## Introduction: The 7-Layer Architecture

ScraperSky follows a strict 7-layer architectural pattern, where each layer has specific responsibilities:

1. **Layer 1: Models & ENUMs** - Database models and status enums (SQLAlchemy ORM)
2. **Layer 2: Schemas** - API request/response schemas (Pydantic models)
3. **Layer 3: Routers** - API endpoints (FastAPI routers)
4. **Layer 4: Services** - Business logic and background processing
5. **Layer 5: Configuration** - Application settings and environment configuration
6. **Layer 6: UI Components** - Frontend components and user interfaces
7. **Layer 7: Testing** - Unit, integration, and workflow tests

All workflows follow the **Producer-Consumer pattern**, where:
- A user action triggers a status update via an API endpoint (Producer)
- A background scheduler polls for records with specific status values (Consumer)
- Standardized status transitions (Queued → Processing → Complete/Error) track progress

## File Mapping Matrix

| Layer | WF1-SingleSearch | WF2-StagingEditor | WF3-LocalBusinessCuration | WF4-DomainCuration | WF5-SitemapCuration | WF6-SitemapImport | WF7-PageCuration |
|-------|------------------|-------------------|---------------------------|-------------------|---------------------|-------------------|------------------|
| **Layer 1: Models & ENUMs** | `src/models/place_search.py` [SHARED]<br>`src/models/place.py` [SHARED]<br>Enum: `PlaceSearchStatusEnum`<br>Enum: `PlaceStatusEnum` | `src/models/place.py` [SHARED]<br>Enum: `PlaceStatusEnum`<br>Enum: `DeepScanStatusEnum` | `src/models/local_business.py` [SHARED]<br>Enum: `PlaceStatusEnum` (reused)<br>Enum: `DomainExtractionStatusEnum` | `src/models/domain.py` [SHARED]<br>Enum: `SitemapCurationStatusEnum`<br>Enum: `SitemapAnalysisStatusEnum` | `src/models/sitemap.py` [SHARED]<br>Enum: `SitemapImportCurationStatusEnum`<br>Enum: `SitemapImportProcessStatusEnum` | `src/models/sitemap.py` [SHARED]<br>`src/models/page.py` [SHARED]<br>Enum: `SitemapImportProcessStatusEnum`<br>Enum: `PageStatusEnum` | `src/models/page.py` [SHARED]<br>Enum: `PageCurationStatus` |
| **Layer 2: Schemas** | `src/models/api_models.py::PlacesSearchRequest` [SHARED] ⚠️ | `src/models/api_models.py::PlaceBatchStatusUpdateRequest` [SHARED]<br>`src/models/api_models.py::PlaceStagingStatusEnum` [SHARED] | `src/models/api_models.py::LocalBusinessBatchStatusUpdateRequest` [SHARED] ⚠️ | `src/models/api_models.py::DomainBatchCurationStatusUpdateRequest` [SHARED]<br>`src/models/api_models.py::SitemapCurationStatusApiEnum` [SHARED] | `src/models/sitemap_file.py::SitemapFileBatchUpdate` [SHARED] ⚠️ | N/A (Triggered by WF5 DB state) | `src/models/api_models.py::PageBatchStatusUpdateRequest` [SHARED] ⚠️ |
| **Layer 3: Routers** | `src/routers/google_maps_api.py` [NOVEL] | `src/routers/places_staging.py` [NOVEL] | `src/routers/local_businesses.py` [NOVEL] | `src/routers/domains.py` [NOVEL] | `src/routers/sitemap_files.py` [NOVEL] | `src/routers/dev_tools.py` [SHARED] | `src/routers/pages.py` [NOVEL] |
| **Layer 4: Services** | `src/services/places/places_search_service.py` [NOVEL]<br>`src/services/places/places_service.py` [NOVEL]<br>`src/services/places/places_storage_service.py` [NOVEL] | `src/services/sitemap_scheduler.py` [SHARED] ⚠️<br>`src/services/places/places_deep_service.py` [SHARED] | `src/services/sitemap_scheduler.py` [SHARED] ⚠️<br>`src/services/business_to_domain_service.py` [SHARED] | `src/services/domain_sitemap_submission_scheduler.py` [NOVEL]<br>`src/services/domain_to_sitemap_adapter_service.py` [NOVEL] | `src/services/sitemap_files_service.py` [NOVEL] | `src/services/sitemap_import_scheduler.py` [SHARED]<br>`src/services/sitemap_import_service.py` [SHARED] | `src/services/page_curation_service.py` [NOVEL]<br>`src/services/page_curation_scheduler.py` [NOVEL] ✓ |
| **Layer 5: Configuration** | `.env`/`docker-compose.yml`: `GOOGLE_MAPS_API_KEY` | `.env`/`docker-compose.yml`:<br>`SITEMAP_SCHEDULER_INTERVAL_MINUTES`<br>`SITEMAP_SCHEDULER_BATCH_SIZE`<br>`SITEMAP_SCHEDULER_MAX_INSTANCES` | `.env`/`docker-compose.yml`<br>(Reuses scheduler config from WF2) ⚠️ | `.env`/`docker-compose.yml`:<br>`DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES`<br>`DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE`<br>`DOMAIN_SITEMAP_SCHEDULER_MAX_INSTANCES` ✓ | `.env`/`docker-compose.yml`<br>(Reuses scheduler config from WF2) ⚠️ | `.env`/`docker-compose.yml`:<br>`SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES`<br>`SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE`<br>`SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES` ✓ | `.env`/`docker-compose.yml`:<br>`PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES`<br>`PAGE_CURATION_SCHEDULER_BATCH_SIZE` ✓ |
| **Layer 6: UI Components** | `static/js/single-search-tab.js` [NOVEL]<br>HTML Tab ID: `singleSearch` | `static/js/staging-editor-tab.js` [NOVEL]<br>HTML Tab ID: `stagingEditor` | `static/js/local-business-curation-tab.js` [NOVEL]<br>HTML Tab ID: `localBusinessCuration` | `static/js/domain-curation-tab.js` [NOVEL]<br>HTML Tab ID: `domainCurationPanel` ✓ | `static/js/sitemap-curation-tab.js` [NOVEL]<br>HTML Tab ID: `sitemapCurationPanel` ✓ | N/A (Background Process) | `static/js/page-curation-tab.js` [NOVEL]<br>HTML Tab ID: `pageCurationPanel` ✓ |
| **Layer 7: Testing** | `tests/routers/test_google_maps_api.py` [NOVEL]<br>`tests/services/places/test_places_search_service.py` [NOVEL]<br>`tests/services/places/test_places_service.py` [NOVEL]<br>`tests/services/places/test_places_storage_service.py` [NOVEL] | `tests/routers/test_places_staging.py` [NOVEL]<br>`tests/services/places/test_places_deep_service.py` [NOVEL]<br>`tests/services/test_sitemap_scheduler.py` [SHARED] | `tests/routers/test_local_businesses.py` [NOVEL]<br>`tests/services/test_sitemap_scheduler.py` [SHARED] | `tests/routers/test_domains.py` [NOVEL]<br>`tests/services/test_domain_sitemap_submission_scheduler.py` [NOVEL] | `tests/routers/test_sitemap_files.py` [NOVEL]<br>`tests/services/test_sitemap_files_service.py` [NOVEL]<br>`tests/services/test_sitemap_scheduler.py` [SHARED] | `tests/services/test_sitemap_import_service.py` [NOVEL]<br>`tests/services/test_sitemap_import_scheduler.py` [NOVEL] | `tests/routers/test_pages.py` [NOVEL]<br>`tests/services/test_page_curation_service.py` [NOVEL]<br>`tests/services/test_page_curation_scheduler.py` [NOVEL] |

**Legend:**
✓ - Follows current naming conventions perfectly
⚠️ - Technical debt/deviation from conventions

## Standardized Status Fields by Workflow

According to the `CONVENTIONS_AND_PATTERNS_GUIDE.md`, each workflow should have consistent status field naming:

| Workflow | Correct Curation Status Field | Correct Processing Status Field | Current Implementation | Compliance |
|----------|------------------------------|--------------------------------|------------------------|------------|
| WF1-SingleSearch | `business_search_curation_status` | `business_search_processing_status` | Uses direct API calls | ⚠️ Non-compliant |
| WF2-StagingEditor | `staging_curation_status` | `staging_processing_status` | `status`, `deep_scan_status` | ⚠️ Non-compliant |
| WF3-LocalBusinessCuration | `local_business_curation_status` | `local_business_processing_status` | `status`, `domain_extraction_status` | ⚠️ Non-compliant |
| WF4-DomainCuration | `domain_curation_status` | `domain_curation_processing_status` | `sitemap_curation_status`, `sitemap_analysis_status` | ⚠️ Non-compliant |
| WF5-SitemapCuration | `sitemap_curation_status` | `sitemap_curation_processing_status` | `deep_scrape_curation_status`, `sitemap_import_status` | ⚠️ Non-compliant |
| WF6-SitemapImport | `sitemap_import_curation_status` | `sitemap_import_processing_status` | `sitemap_import_status` | ⚠️ Partially compliant |
| WF7-PageCuration | `page_curation_status` | `page_curation_processing_status` | `page_curation_status`, `page_curation_processing_status` | ✓ Compliant |

## Producer-Consumer Workflow Connections

| Producer Workflow | Consumer Workflow | Interface Table | Handoff Field | Handoff Value | Compliant with Pattern |
|-------------------|-------------------|-----------------|---------------|---------------|------------------------|
| WF1-SingleSearch | WF2-StagingEditor | `places` | `status` | `PlaceStatusEnum.New` | ✓ |
| WF2-StagingEditor | WF3-LocalBusinessCuration | `local_businesses` | `status` | `PlaceStatusEnum.Selected` | ✓ |
| WF3-LocalBusinessCuration | WF4-DomainCuration | `domains` | `sitemap_curation_status` | `SitemapCurationStatusEnum.New` | ✓ |
| WF4-DomainCuration | WF5-SitemapCuration | `domains` | `sitemap_analysis_status` | `SitemapAnalysisStatusEnum.Queued` | ✓ |
| WF5-SitemapCuration | WF6-SitemapImport | `sitemap_files` | `sitemap_import_status` | `SitemapImportProcessStatusEnum.Queued` | ✓ |
| WF6-SitemapImport | WF7-PageCuration | `pages` | `status` | `PageStatusEnum.New` | ✓ |

## Architectural Compliance Summary

| Architectural Principle | Description | Overall Compliance |
|------------------------|-------------|-------------------|
| **Layer 1: ORM Usage** | All database access must use SQLAlchemy ORM | Mostly compliant, with exceptions in WF2 (raw SQL in places_staging.py) |
| **Layer 3: Transaction Boundaries** | Routers own transaction boundaries | Generally compliant, with some issues in dev_tools.py (WF6) |
| **Layer 4: Background Services** | Each workflow should have a dedicated scheduler | Partially compliant - WF2 and WF3 share sitemap_scheduler.py |
| **Layer 5: Configuration** | Settings should follow workflow-specific naming | Partially compliant - newer workflows follow conventions |
| **Layer 6: UI Component IDs** | UI components should follow standard ID patterns | Mixed compliance - newer UIs follow conventions |
| **Status Field Naming** | Status fields should follow `{workflow_name}_{type}_status` pattern | Only newest workflow (WF7) fully compliant |

## Technical Debt Analysis

1. **Layer 2: Schemas Location:** Schemas should be in `src/schemas/{workflow_name}.py` but are mostly in `src/models/api_models.py`
2. **Shared Scheduler:** WF2 and WF3 both use `sitemap_scheduler.py` when each should have dedicated schedulers
3. **Non-standard Status Fields:** Most workflows don't follow the current naming conventions for status fields
4. **Raw SQL Usage:** Found in places_staging.py, violating the ORM requirement
5. **Schema Naming:** Batch update request schemas don't follow current naming conventions

## Path to Standardization

Based on the `CONVENTIONS_AND_PATTERNS_GUIDE.md`, future development and refactoring should:

1. Move schemas to dedicated `src/schemas/{workflow_name}.py` files
2. Rename status fields to follow `{workflow_name}_{type}_status` pattern
3. Create dedicated schedulers for each workflow
4. Update environment variable names to follow workflow-specific naming
5. Refactor raw SQL to use SQLAlchemy ORM
6. Update UI component IDs to follow standard patterns

WF7-PageCuration appears to be the most compliant workflow and should serve as a reference model for future development and refactoring efforts.
