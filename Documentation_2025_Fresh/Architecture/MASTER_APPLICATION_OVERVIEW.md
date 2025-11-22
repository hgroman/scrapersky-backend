# MASTER APPLICATION OVERVIEW

**Date:** 2025-11-22
**Status:** Verified against Codebase
**Source of Truth:** `Documentation_2025_Fresh/MANIFEST.md`

## 1. The Router Map (Verified)

The application is structured around **Workflow-Specific Routers** (WF*) and **Core Utilities**. All routers are flattened under `src/routers/` and use the `/api/v3/` prefix.

| Workflow | Router File | Prefix | Purpose |
|----------|-------------|--------|---------|
| **WF1** | `wf1_google_maps_api_router.py` | `/api/v3/localminer-discoveryscan` | Google Maps Discovery |
| **WF1** | `wf1_place_staging_router.py` | `/api/v3/places-staging` | Place Staging & Selection |
| **WF3** | `wf3_local_business_router.py` | `/api/v3/local-businesses` | Business Data Management |
| **WF3** | `wf3_domains_direct_submission_router.py` | `/api/v3/domains` | Direct Domain Submission |
| **WF3** | `wf3_domains_csv_import_router.py` | `/api/v3/domains` | Bulk Domain CSV Import |
| **WF4** | `wf4_domain_router.py` | `/api/v3/domains` | Domain Management |
| **WF5** | `wf5_sitemap_file_router.py` | `/api/v3/sitemap-files` | Sitemap CRUD |
| **WF5** | `wf5_sitemap_modernized_router.py` | `/api/v3/sitemap` | Sitemap Scanning |
| **WF7** | `wf7_pages_router.py` | `/api/v3/pages` | Page Curation (The Gold Standard) |
| **WF7** | `wf7_contacts_router.py` | `/api/v3/contacts` | Contact Management |
| **Co-Pilot** | `copilot.py` | `/api/v3/copilot` | AI Semantic Search & Stats |

## 2. Dual-Status Adapter Map (The "Engine")

The system uses a **Dual-Status Pattern** to coordinate User Intent (`Curation Status`) with System Action (`Processing Status`).

| Workflow | Router File | Trigger Logic |
|----------|-------------|---------------|
| **WF1** | `wf1_place_staging_router.py` | `status='Selected'` → `deep_scan_status='Queued'` |
| **WF3** | `wf3_local_business_router.py` | `status='Selected'` → `domain_extraction_status='Queued'` |
| **WF4** | `wf4_domain_router.py` | `sitemap_curation_status='Selected'` → `sitemap_analysis_status='queued'` |
| **WF5** | `wf5_sitemap_file_router.py` | `deep_scrape_curation_status='Selected'` → `sitemap_import_status='Queued'` |
| **WF7** | `wf7_pages_router.py` | `page_curation_status='Selected'` → `page_processing_status='Queued'` |

## 3. Background Schedulers

Background tasks are handled by dedicated scheduler services in `src/services/background/`.

| Scheduler File | Interval | Purpose |
|----------------|----------|---------|
| `wf2_deep_scan_scheduler.py` | 1 min | Enriches Place data (Google Maps details) |
| `wf3_domain_extraction_scheduler.py` | 2 min | Extracts Domain URL from Place data |
| `wf4_sitemap_discovery_scheduler.py` | 1 min | Discovers sitemaps for Domains |
| `wf5_sitemap_import_scheduler.py` | 1 min | Imports URLs from Sitemaps to Pages |
| `wf7_page_curation_scheduler.py` | 1 min | Scrapes Pages for Contacts |
| `wf7_crm_*_scheduler.py` | 1 min | Syncs Contacts to Brevo/HubSpot/n8n |

## 4. CRUD Standardization Status

| Entity | Modern CRUD? | Sortable? | Filters? | Notes |
|--------|--------------|-----------|----------|-------|
| **Pages** | ✅ Yes | ✅ Yes | ✅ Yes | The Gold Standard Implementation |
| **SitemapFiles** | ✅ Yes | ⚠️ Partial | ✅ Yes | Needs full sort implementation |
| **Domains** | ✅ Yes | ❌ No | ✅ Yes | Needs sort/filter upgrade |
| **LocalBusiness** | ✅ Yes | ❌ No | ✅ Yes | Needs sort/filter upgrade |
| **Contacts** | ✅ Yes | ❌ No | ❌ No | **Next Priority Target** |

## 5. Future Cleanup Targets (Enums)

*   `SitemapImportProcessingStatusEnum`
*   `DomainExtractionStatusEnum`
*   `PageProcessingStatusEnum`
*   `DeepScanStatusEnum`

**Goal:** Merge all into a single unified `ProcessingStatusEnum`.
