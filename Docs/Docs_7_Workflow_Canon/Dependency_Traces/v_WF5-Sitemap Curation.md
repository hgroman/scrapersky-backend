# Workflow Trace: Sitemap Curation "Selected" Status to Deep Scrape Queueing

**Version:** 1.0
**Date:** 2025-05-02

This document traces the full dependency chain for the user workflow where items (sitemap files) are marked with `deep_scrape_curation_status` = 'Selected' in the "Sitemap Curation" UI tab, resulting in them being queued for deep scrape processing (extracting URLs and processing pages) in the backend.

**Note:** This trace identifies a gap where the background scheduler currently does not pick up these queued items.

## Table of Contents

- [1. Involved Files & Components](#1-involved-files--components)
  - [1.1. Frontend (Layer 6: UI Components & JS)](#11-frontend-ui--js)
  - [1.2. Backend (API Layer 3: Routers)](#12-backend-api-router)
  - [1.3. Backend (Layer 4: Services & Background Jobs)](#13-backend-services--background-jobs)
  - [1.4. Database (Layer 1: Models & ENUMs)](#14-database-models--enums)
  - [1.5. Background Scheduling Layer 5: Configuration](#15-background-scheduling-config)
  - [1.6. Layer 7: Testing](#16-testing)
- [2. Workflow Summary](#2-workflow-summary)
- [3. Key Logic Points & Missing Steps](#3-key-logic-points--missing-steps)
- [4. Potential Generalization / Modularization](#4-potential-generalization--modularization)

---

## 1. Involved Files & Components

### 1.1. Frontend (Layer 6: UI Components & JS)

1.  **File:** `static/scraper-sky-mvp.html`
    - **Role:** Contains the HTML structure for the "Sitemap Curation" tab, including the table, checkboxes, status dropdown (`sitemapBatchStatusSelect`), and update button (`sitemapBatchUpdateBtn`).
2.  **File:** `static/js/sitemap-curation-tab.js`
    - **Role:** Handles user interactions within the Sitemap Curation tab.
    - **Function:** (Likely) `sitemapBatchUpdate()` or similar function attached to the update button.
      - Triggered when the "Update X Selected" button is clicked.
      - Collects `sitemap_file_ids` (primary keys) from selected checkboxes.
      - Gets the target `deep_scrape_curation_status` ("Selected") from the dropdown.
      - Sends a `PUT` request to `/api/v3/sitemap-files/status` with IDs and `status` in the request body (`SitemapFileBatchUpdate` Layer 2: Schema).

### 1.2. Backend (API Layer 3: Routers)

1.  **File:** `src/routers/sitemap_files.py`
    - **Role:** Defines API endpoints for managing `SitemapFile` entities.
    - **Function:** `update_sitemap_files_status_batch(...)`, handling `PUT /api/v3/sitemap-files/status`.
      - Receives `sitemap_file_ids` and `deep_scrape_curation_status` ("Selected") from the `update_request` (`SitemapFileBatchUpdate`).
      - **Delegates** the core update and queueing logic to Layer 4: Services.
      - Calls `sitemap_files_service.update_curation_status_batch(...)`.
      - Depends on `get_db_session`, `get_current_user`, `SitemapFileBatchUpdate`, `SitemapFilesService`.

### 1.3. Backend (Layer 4: Services & Background Jobs)

1.  **File:** `src/services/sitemap_files_service.py`
    - **Role:** Contains the business logic for managing `SitemapFile` records, including the dual-status update.
    - **Function:** `update_curation_status_batch(...)`
      - Receives `sitemap_file_ids` and the target `new_curation_status` (enum member `SitemapDeepCurationStatusEnum.Selected`).
      - **Key Logic (Dual-Status Update Verified):**
        - Updates `sitemap_files.deep_scrape_curation_status` to `Selected` for the given IDs.
        - **If** `new_curation_status` is `Selected`, it issues a _second_ update:
          - Sets `sitemap_files.deep_scrape_process_status` to `SitemapDeepProcessStatusEnum.Queued`.
          - Condition: Only updates if the current `deep_scrape_process_status` is `None` or not equal to `Processing`.
      - Uses `session.begin()` for transaction management.
      - Depends on `SitemapFile`, `SitemapDeepCurationStatusEnum`, `SitemapDeepProcessStatusEnum`.
2.  **File:** `src/services/sitemap_scheduler.py`
    - **Role:** Contains the currently implemented background job polling mechanism.
    - **Function:** `process_pending_jobs()`
      - **Missing Logic:** This function currently polls for legacy sitemap jobs, `Place` deep scans, and `LocalBusiness` domain extractions. It **does not** contain logic to query the `sitemap_files` table for `deep_scrape_process_status == 'Queued'`.
3.  **File:** `src/services/page_scraper/processing_service.py` (or similar)
    - **Role:** **(Intended Target - Not Called)** This Layer 4: Service likely contains the logic required to process a `SitemapFile` marked as `Queued`. It would fetch the sitemap, parse URLs, and potentially queue individual page scraping jobs. This Layer 4: Service **is not currently being triggered** by the scheduler for this workflow.
4.  **File:** `src/scheduler_instance.py`
    - **Role:** Defines the shared `AsyncIOScheduler` instance.
5.  **File:** `src/main.py`
    - **Role:** FastAPI application entry point.
    - **Function:** `@app.on_event("startup")` handler
      - Initializes scheduled jobs (currently including `sitemap_scheduler`).

### 1.4. Database (Layer 1: Models & ENUMs)

1.  **File:** `src/models/sitemap.py`
    - **Role:** Defines the primary data model for this stage.
    - **Class:** `SitemapFile`
      - Mapped to the `sitemap_files` table.
      - **Fields Updated:** `deep_scrape_curation_status`, `deep_scrape_process_status`, `updated_at`, `updated_by`.
      - **Fields Read (by missing scheduler):** `id`, `url`, `domain_id`, `deep_scrape_process_status`.
    - Layer 1: ENUM: `SitemapDeepCurationStatusEnum`
      - Defines values for the main curation status field (e.g., `Selected`). Used by router and service.
    - Layer 1: ENUM: `SitemapDeepProcessStatusEnum`
      - Defines values for the processing status field (e.g., `Queued`, `Processing`, `Completed`, `Error`). Used by service and (should be used by) scheduler.
2.  **File:** `src/schemas/sitemap_file.py`
    - **Role:** Defines Pydantic Layer 2: Schemas for API interaction.
    - **Class:** `SitemapFileBatchUpdate`
      - Used by the router to validate the incoming request body. Includes `sitemap_file_ids` and `deep_scrape_curation_status`.

### 1.5. Background Scheduling Layer 5: Configuration

_(Same as previous workflows, as `sitemap_scheduler.py` is involved, even if incompletely)_

1.  **File:** `docker-compose.yml`
    - **Variables:** `SITEMAP_SCHEDULER_INTERVAL_MINUTES`, `SITEMAP_SCHEDULER_BATCH_SIZE`, `SITEMAP_SCHEDULER_MAX_INSTANCES`.
2.  **File:** `src/config/settings.py` (Implied)
    - **Role:** Loads scheduler environment variables.

### 1.6. Layer 7: Testing

_(Requires confirmation via codebase search)_

1.  **File:** `tests/routers/test_sitemap_files.py` (Likely location)
    - **Potential Test Functions:**
      - `test_update_sitemap_files_status_batch_selected_queues`: Verify calling the endpoint with status 'Selected' results in `deep_scrape_process_status` being set to `Queued` in the DB (via Layer 4: Service call).
2.  **File:** `tests/services/test_sitemap_files_service.py` (Likely location)
    - **Potential Test Functions:**
      - `test_update_curation_status_batch_selected`: Verify Layer 4: Service function updates curation status to 'Selected' AND process status to 'Queued'.
      - `test_update_curation_status_batch_selected_already_processing`: Verify Layer 4: Service function updates curation status but does _not_ update process status if it's already 'Processing'.
      - `test_update_curation_status_batch_other_status`: Verify Layer 4: Service function only updates curation status and does _not_ touch process status for non-'Selected' inputs.
3.  **File:** `tests/services/test_sitemap_scheduler.py` (Likely location)
    - **Potential Test Functions:**
      - **(Missing Test):** There should ideally be a test like `test_process_pending_jobs_picks_up_queued_sitemap_files` which verifies the scheduler queries `sitemap_files` and calls the appropriate processing Layer 4: Service. This test would currently fail or be absent.

---

## 2. Workflow Summary

1.  User selects sitemaps and "Selected" status in Sitemap Curation UI.
2.  Frontend JS calls `PUT /api/v3/sitemap-files/status` with IDs and status="Selected".
3.  Backend Layer 3: Router (`sitemap_files.py`) receives the call and delegates to the Layer 4: Service.
4.  Backend Layer 4: Service (`sitemap_files_service.update_curation_status_batch`) implements **Dual-Status Update Logic**: updates `sitemap_files.deep_scrape_curation_status` to `Selected` and sets `sitemap_files.deep_scrape_process_status` to `Queued` (if not already processing).
5.  Database `sitemap_files` table is updated accordingly.
6.  **(BROKEN STEP):** The background job (`sitemap_scheduler.process_pending_jobs`) runs periodically **but does not currently query** for `sitemap_files` with `deep_scrape_process_status == 'Queued'`.
7.  **(NOT REACHED):** Consequently, the intended next step service (likely `page_scraper.processing_service`) is never called for these queued sitemap files.

---

## 3. Key Logic Points & Missing Steps

- **Dual-Status Update Logic:** Correctly implemented in Layer 4: Services (`sitemap_files_service.py`). Setting curation status to `Selected` correctly queues the item by setting the process status.
- **No Unused Parameters:** No unused trigger parameters were identified in the relevant Layer 3: Router/Layer 4: Service functions.
- **MISSING SCHEDULER LOGIC:** The primary issue is that the existing background job (`sitemap_scheduler.py::process_pending_jobs`) **lacks the necessary query and logic** to detect and process `SitemapFile` records queued for deep scraping (`deep_scrape_process_status == 'Queued'`).

---

## 4. Potential Generalization / Modularization

- The "Dual-Status Update Logic" is again present in Layer 4: Services and could potentially be generalized.
- The lack of scheduler logic for this specific queue highlights the potential benefit of either adding a dedicated section to `sitemap_scheduler.py` or creating separate, more focused scheduler functions/jobs (e.g., one for deep scans, one for domain extraction, one for sitemap processing) instead of bundling them all into `process_pending_jobs`. This could make it easier to track which queues are actively being polled.
