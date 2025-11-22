# System Architecture Scan (2025-11-21)

## Overview
This document provides a deep scan of the ScraperSky backend architecture as of November 21, 2025. It maps the relationships between Routers, Services, Schedulers, and Models, with a specific focus on identifying "dual purpose" adapters and critical dependencies.

## 1. Entry Point: `src/main.py`

### Active Schedulers (Background Services)
These schedulers are initialized in the `lifespan` event handler.

| Scheduler Name | Setup Function | Workflow | Purpose |
|----------------|----------------|----------|---------|
| `wf5_sitemap_import_scheduler` | `setup_sitemap_import_scheduler` | WF5 | Processes pending sitemap imports. |
| `wf7_page_curation_scheduler` | `setup_page_curation_scheduler` | WF7 | Curates pages for scraping/contact extraction. |
| `wf7_crm_brevo_sync_scheduler` | `setup_brevo_sync_scheduler` | WF7 | Syncs contacts to Brevo CRM. |
| `wf7_crm_hubspot_sync_scheduler` | `setup_hubspot_sync_scheduler` | WF7 | Syncs contacts to HubSpot CRM. |
| `wf7_crm_n8n_sync_scheduler` | `setup_n8n_sync_scheduler` | WF7 | Syncs contacts to n8n webhooks. |
| `wf7_crm_debounce_scheduler` | `setup_debounce_validation_scheduler` | WF7 | Validates emails via DeBounce. |
| `wf4_domain_monitor_scheduler` | `setup_domain_scheduler` | WF4 | Monitors domain status (legacy?). |
| `wf4_sitemap_discovery_scheduler` | `setup_sitemap_discovery_scheduler` | WF4 | Discovers sitemaps for domains. **CRITICAL LINK** |
| `wf2_deep_scan_scheduler` | `setup_deep_scan_scheduler` | WF2 | Performs deep scans of Places. |
| `wf3_domain_extraction_scheduler` | `setup_domain_extraction_scheduler` | WF3 | Extracts domains from Places. |

## 2. Data Flow & Trigger Map (The "Kinetic" View)

This section maps exactly how data moves from one stage to the next.

### WF1 → WF2: Place Enrichment
*   **Source:** `places` table
*   **Trigger Field:** `deep_scan_status`
*   **Trigger Value:** `Queued` (Enum: `GcpApiDeepScanStatusEnum.Queued`)
*   **Detector:** `wf2_deep_scan_scheduler.py`
    *   *Query:* `SELECT * FROM places WHERE deep_scan_status = 'Queued'`
*   **Processor:** `PlacesDeepService.process_single_deep_scan()`
*   **Action:** Calls Google Places API (Details)
*   **Output:**
    1.  Updates `places.raw_data` (Enrichment)
    2.  Sets `places.deep_scan_status` → `Completed`
    3.  **HANDOFF:** Creates `LocalBusiness` record (if valid)

### WF2 → WF3: Domain Extraction
*   **Source:** `local_businesses` table
*   **Trigger Field:** `domain_extraction_status`
*   **Trigger Value:** `Queued` (Enum: `DomainExtractionStatusEnum.Queued`)
    *   *Note:* Often auto-set to `Queued` upon creation in WF2.
*   **Detector:** `wf3_domain_extraction_scheduler.py`
    *   *Query:* `SELECT * FROM local_businesses WHERE domain_extraction_status = 'Queued'`
*   **Processor:** `LocalBusinessToDomainService.create_pending_domain_from_local_business()`
*   **Action:** Extracts website URL from business data
*   **Output:**
    1.  Sets `local_businesses.domain_extraction_status` → `Completed`
    2.  **HANDOFF:** Creates `Domain` record (if website exists)

### WF3 → WF4: Domain Curation (The "Gap")
*   **Source:** `domains` table
*   **Trigger Field:** `sitemap_analysis_status`
*   **Trigger Value:** `queued` (Enum: `SitemapAnalysisStatusEnum.queued` - **LOWERCASE**)
    *   *Note:* User manually selects "Select" in UI -> API sets this to `queued`.
*   **Detector:** `wf4_sitemap_discovery_scheduler.py`
    *   *Query:* `SELECT * FROM domains WHERE sitemap_analysis_status = 'queued'`
*   **Processor:** `wf4_domain_to_sitemap_adapter_service.py` (**CRITICAL ADAPTER**)
*   **Action:**
    1.  Creates `Job` record (type='sitemap')
    2.  Triggers `wf5_processing_service` (Async Task)
*   **Output:**
    1.  Sets `domains.sitemap_analysis_status` → `submitted`
    2.  **HANDOFF:** `wf5_processing_service` discovers sitemaps and creates `SitemapFile` records.

### WF4 → WF5: Sitemap Import
*   **Source:** `sitemap_files` table
*   **Trigger Field:** `sitemap_import_status` (or similar, needs verification)
*   **Trigger Value:** `Queued`
*   **Detector:** `wf5_sitemap_import_scheduler.py`
*   **Processor:** `wf5_sitemap_import_service.py`
*   **Action:** Downloads XML, extracts URLs, runs Honeybee categorization
*   **Output:**
    1.  Sets `sitemap_files.status` → `Completed`
    2.  **HANDOFF:** Creates `Page` records.
    3.  **AUTO-SELECTION:** If Honeybee confidence high, sets `Page.page_curation_status` → `Selected`.

**FAILURE MODE: Sitemap Index (Known Issue)**
*   **Condition:** Target is a Sitemap Index (contains other sitemaps, not pages).
*   **Symptom:** `SitemapFile` created with `sitemap_type='index'` and `url_count=0`.
*   **Result:** Pipeline halts. No pages created. No child sitemaps recursively fetched as new `SitemapFile` records.
*   **Example:** `mikesbikes.com/sitemap.xml` (Index) -> 0 URLs.

### WF5 → WF7: Page Curation (Contact Extraction)
*   **Source:** `pages` table
*   **Trigger Field:** `page_curation_status` AND `page_processing_status`
*   **Trigger Value:** `page_curation_status='Selected'` AND `page_processing_status='Queued'`
*   **Detector:** `wf7_page_curation_scheduler.py`
*   **Processor:** `wf7_page_curation_service.py`
*   **Action:** Scrapes HTML (ScraperAPI), extracts emails/phones
*   **Output:**
    1.  Updates `pages.scraped_content` (JSONB)
    2.  Sets `pages.page_processing_status` → `Complete`
    3.  **HANDOFF:** Creates `Contact` records (if found).

## 3. Critical Adapters & Bridges

### `wf4_domain_to_sitemap_adapter_service.py`
*   **Role:** Bridge between WF4 (Domain Curation) and WF5 (Sitemap Discovery).
*   **Input:** `Domain` records with `sitemap_analysis_status='queued'`.
*   **Action:**
    1.  Creates a `Job` record (type='sitemap').
    2.  Initializes job status in memory (`_job_statuses`).
    3.  Triggers `process_domain_with_own_session` (WF5 logic) as an asyncio task.
    4.  Updates `Domain.sitemap_analysis_status` to 'submitted' or 'failed'.
*   **Criticality:** HIGH. Removal breaks the pipeline.

## 4. Enum & Model Inventory (Enum Hell)

### `Place` (WF1)
*   **Status:** `PlaceStatusEnum` (New, Selected, Maybe, Not a Fit, Archived) - **Title Case**
*   **Deep Scan:** `GcpApiDeepScanStatusEnum` (Queued, Processing, Completed, Error) - **Title Case**

### `LocalBusiness` (WF3)
*   **Status:** `PlaceStatusEnum` (Shared) - **Title Case**
*   **Domain Extraction:** `DomainExtractionStatusEnum` (Queued, Processing, Completed, Error) - **Title Case**

### `Domain` (WF4)
*   **Sitemap Analysis:** `SitemapAnalysisStatusEnum` (pending, queued, processing, submitted, failed) - **LOWERCASE** (Inconsistent!)
*   **Suration:** `SitemapCurationStatusEnum` (New, Selected, Maybe, Not a Fit, Archived, Completed) - **Title Case**

**Conclusion:**
The system has a mix of standardized SDK-based workflows (WF2, WF3) and legacy custom loops (WF4). The "Enum Hell" issue is confirmed with `SitemapAnalysisStatusEnum` using lowercase values while others use Title Case.
