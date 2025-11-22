# Documentation Manifest (The Code Truth)

**Generated:** 2025-11-22
**Purpose:** This document lists the *actual* files present in the codebase at the time of the "Great Cleanup". Any documentation that references files NOT on this list is considered "Stale" or "Fiction".

## 1. Active Routers (The API Surface)
*Verified `src/routers/` contents:*

*   `copilot.py`
*   `db_portal.py`
*   `dev_tools.py`
*   `profile.py`
*   `vector_db_ui.py`
*   `wf1_google_maps_api_router.py`
*   `wf1_place_staging_router.py`
*   `wf3_domains_csv_import_router.py`
*   `wf3_domains_direct_submission_router.py`
*   `wf3_local_business_router.py`
*   `wf4_domain_router.py`
*   `wf5_sitemap_batch_router.py`
*   `wf5_sitemap_csv_import_router.py`
*   `wf5_sitemap_direct_submission_router.py`
*   `wf5_sitemap_file_router.py`
*   `wf5_sitemap_modernized_router.py`
*   `wf7_contacts_router.py`
*   `wf7_contacts_validation_router.py`
*   `wf7_email_scanner_router.py`
*   `wf7_n8n_webhook_router.py`
*   `wf7_page_batch_scraper_router.py`
*   `wf7_page_csv_import_router.py`
*   `wf7_page_direct_submission_router.py`
*   `wf7_page_modernized_scraper_router.py`
*   `wf7_pages_router.py`

## 2. Active Services (The Business Logic)
*Verified `src/services/` contents:*

### Background Schedulers
*   `wf2_deep_scan_scheduler.py`
*   `wf3_domain_extraction_scheduler.py`
*   `wf4_domain_monitor_scheduler.py`
*   `wf4_sitemap_discovery_scheduler.py`
*   `wf5_sitemap_import_scheduler.py`
*   `wf7_crm_brevo_sync_scheduler.py`
*   `wf7_crm_debounce_scheduler.py`
*   `wf7_crm_hubspot_sync_scheduler.py`
*   `wf7_crm_n8n_sync_scheduler.py`
*   `wf7_page_curation_scheduler.py`

### Core Services
*   `places/wf1_places_search_service.py`
*   `places/wf1_places_service.py`
*   `sitemap/wf5_sitemap_service.py`
*   `page_scraper/wf7_processing_service.py`
*   `crm/wf7_brevo_sync_service.py`
*   `crm/wf7_hubspot_sync_service.py`
*   `crm/wf7_n8n_sync_service.py`
*   `email_validation/wf7_debounce_service.py`

## 3. Active Models (The Data Structure)
*Verified `src/models/` contents:*

*   `wf1_place_search.py`
*   `wf1_place_staging.py`
*   `wf3_local_business.py`
*   `wf4_domain.py`
*   `wf5_sitemap_file.py`
*   `wf7_contact.py`
*   `wf7_page.py`
*   `tenant.py` (CRITICAL)
*   `enums.py`

---

**Audit Rule:** If a document references `v2/` routers or `old_enum_names`, it does NOT belong in this folder until updated.
