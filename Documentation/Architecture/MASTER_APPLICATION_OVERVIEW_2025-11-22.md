# MASTER APPLICATION OVERVIEW – 2025-11-22
## The Single Source of Truth (finally)

### 1. main.py Router Registration Order (exact lines 38-88)
```python
app.include_router(google_maps_api.router, prefix="/api/v3/google-maps")
app.include_router(places_staging.router, prefix="/api/v3/places-staging")
app.include_router(local_businesses.router, prefix="/api/v3/local-businesses")
app.include_router(domains_router.router, prefix="/api/v3/domains")
app.include_router(sitemap_files_router.router, prefix="/api/v3/sitemap-files")
app.include_router(pages_router.router, prefix="/api/v3/pages")           # ← ONLY v3, this is the modern one
app.include_router(contacts_router.router, prefix="/api/v3/contacts")
```

**DEPRECATED / DELETE THESE (they are still imported but dead):**
*   `WF7_V2_L3_1of1_PagesRouter.py`
*   any router in `src/routers/v2/` that is duplicated in v3
*   all `*_direct_submission_router.py` files (legacy)

### 2. Complete Dual-Status Adapter Map (every single one, file + line)

| Workflow | Router File | Curation Field → Processing Field Trigger | Line Numbers |
|----------|-------------|-------------------------------------------|--------------|
| WF1 | `wf1_place_staging_router.py` | `status='Selected'` → `deep_scan_status='Queued'` | 317, 266 |
| WF3 | `wf3_local_business_router.py` | `status='Selected'` → `domain_extraction_status='Queued'` | 261, 209 |
| WF4 | `wf4_domain_router.py` | `sitemap_curation_status='Selected'` → `sitemap_analysis_status='queued'` | 364, 232-233 |
| WF5 | `wf5_sitemap_file_router.py` | `deep_scrape_curation_status='Selected'` → `sitemap_import_status='Queued'` | 53-54 |
| WF7 | `WF7_V3_L3_1of1_PagesRouter.py` | `page_curation_status='Selected'` → `page_processing_status='Queued'` | 145-146 |

### 3. Background Schedulers (exact intervals + purpose)

| Scheduler | Interval | Purpose |
|-----------|----------|---------|
| WF2 Deep Scan | 1 min | Enrich Place data |
| WF3 Domain Extraction | 2 min | Extract domain from Place |
| WF4 Sitemap Discovery | 1 min | `wf4_sitemap_discovery_scheduler.py` – the FIXED one |
| WF5 Sitemap Import | 1 min | Import URLs from sitemaps |
| WF7 Page Curation | 1 min | Scrape pages for contacts |
| CRM syncs | 1 min | Sync to Brevo/HubSpot/n8n |

### 4. CRUD Standardization Matrix (current state)

| Table | Modern CRUD? | Sortable Headers? | Filters? | Notes |
|-------|--------------|-------------------|----------|-------|
| Pages | Yes (v3) | Yes | Yes | Gold standard |
| SitemapFiles | Yes (v3) | Partial | Yes | Needs full sort |
| Domains | Yes (v3) | No | Yes | Needs sort + filter love |
| LocalBusiness | Yes | No | Yes | Same |
| Contacts | Yes | No | No | Next target |

### 5. Remaining ENUM Cleanup Hit-List (only 4 left)

*   `SitemapImportProcessingStatusEnum` → merge into unified `ProcessingStatusEnum`
*   `DomainExtractionStatusEnum` → same
*   `PageProcessingStatusEnum` → same
*   `DeepScanStatusEnum` → same

**Target:** one single `ProcessingStatusEnum` used everywhere.
