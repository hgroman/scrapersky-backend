# WF5 - The Flight Planner Guardian v3 - TRUTH DOCUMENT

**MISSION CRITICAL REFERENCE - OXYGEN SYSTEM LEVEL IMPORTANCE**

**Version:** 3.1 (Corrected after background service discovery)  
**Created:** 2025-01-28  
**Updated:** 2025-01-28 - Corrected broken status after discovering working implementation  
**Purpose:** Complete operational authority for WF5 - The Flight Planner workflow  
**Audience:** Future AI partners who need to understand WF5 operations  

---

## CRITICAL CONTEXT

**✅ UPDATE: THIS WORKFLOW IS WORKING ✅**

**Previous incorrect assessment:** This document originally claimed WF5 was broken due to missing scheduler logic. A comprehensive review of background services revealed that WF5 processing is handled by a separate dedicated scheduler: `sitemap_import_scheduler.py`.

**Current status:** WF5 is fully operational through the SDK-based implementation in the sitemap import scheduler.

---

## WHAT WF5 IS (CODE REALITY)

WF5 is a **FULLY IMPLEMENTED** dual-status automation system that transforms user sitemap selections into queued import jobs. When users mark sitemap files as "Selected", the system queues them for background processing, which is handled by the dedicated sitemap import scheduler.

**Core Business Logic (Service function in `/src/services/sitemap_files_service.py`):**
```python
queue_for_processing = (
    new_curation_status == SitemapImportCurationStatusEnum.Selected
)
if queue_for_processing:
    # Use renamed Enum for process status
    update_values[SitemapFile.sitemap_import_status] = (
        SitemapImportProcessStatusEnum.Queued
    )
    # Clear any previous error when re-queuing
    update_values[SitemapFile.sitemap_import_error] = None
```

**THE WORKING ARCHITECTURE:** WF5 processing is handled by a dedicated scheduler (`/src/services/sitemap_import_scheduler.py`) that uses the SDK pattern to process queued sitemap files.

---

## COMPLETE FILE DEPENDENCY MAP

### Layer 6: User Interface (WORKING)
1. **`/static/scraper-sky-mvp.html`** (Sitemap Curation tab)
   - Contains HTML structure for Sitemap Curation tab
   - Table with checkboxes and status dropdown (`sitemapBatchStatusSelect`)
   - Update button (`sitemapBatchUpdateBtn`)

2. **`/static/js/sitemap-curation-tab.js`** 
   - Handles user interactions within the Sitemap Curation tab
   - Function: `sitemapBatchUpdate()` (likely name)
   - Sends PUT requests to `/api/v3/sitemap-files/status`
   - Collects selected IDs and target status from UI

### Layer 3: API Router (WORKING)
3. **`/src/routers/sitemap_files.py`** (FUNCTIONAL API)
   - **Router function:** `update_sitemap_import_curation_status_batch()`
   - **Endpoint:** `PUT /api/v3/sitemap-files/status`
   - **Delegation:** Calls `sitemap_files_service.update_curation_status_batch()`
   - **Transaction management:** Uses `session` for database operations

### Layer 4: Services (PARTIALLY WORKING)
4. **`/src/services/sitemap_files_service.py`** (BUSINESS LOGIC WORKS)
   - Contains `SitemapFilesService` class
   - **Function:** `update_curation_status_batch()` (IMPLEMENTED)
   - **Dual-status update:** Sets both curation and process status when "Selected"
   - **Process status:** `SitemapFile.sitemap_import_status = SitemapImportProcessStatusEnum.Queued`
   - **Error clearing:** `SitemapFile.sitemap_import_error = None`

5. **`/src/services/sitemap_scheduler.py`** (MULTI-PURPOSE SCHEDULER)
   - Contains `process_pending_jobs()` function
   - Handles legacy sitemap jobs, deep scans, and domain extractions
   - **NOT responsible for WF5** - This is handled by sitemap_import_scheduler
   - Processes `LocalBusiness`, `Place`, and legacy `Job` models

6. **`/src/services/sitemap_import_scheduler.py`** (**THE ACTUAL WF5 PROCESSOR**)
   - **Function:** `process_pending_sitemap_imports()`
   - **SDK Pattern:** Uses `run_job_loop()` from curation SDK
   - **Queries:** `SitemapFile.sitemap_import_status == SitemapImportProcessStatusEnum.Queued`
   - **Service:** Calls `SitemapImportService.process_single_sitemap_file()`
   - **Schedule:** Runs every `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES`

7. **`/src/services/sitemap_import_service.py`** (WF5 BUSINESS LOGIC)
   - Contains `SitemapImportService` class
   - **Function:** `process_single_sitemap_file()` 
   - Downloads sitemap XML, parses URLs, creates Page records
   - Updates status from Queued → Processing → Complete/Error

### Layer 5: Configuration & Infrastructure
7. **`/src/scheduler_instance.py`**
   - Provides shared AsyncIOScheduler instance
   - Used by sitemap_scheduler for background processing

8. **`/src/main.py`**
   - Application startup
   - Initializes sitemap_scheduler (which doesn't process sitemaps!)

### Layer 1: Data Models (WORKING)
9. **`/src/models/sitemap.py`** (DATA AUTHORITY)
   - `SitemapFile` SQLAlchemy model class
   - **Curation status field:** `deep_scrape_curation_status` using `SitemapImportCurationStatusEnum`
   - **Process status field:** `sitemap_import_status` using `SitemapImportProcessStatusEnum`
   - **Key values:** `Queued`, `Processing`, `Completed`, `Error`

10. **`/src/schemas/sitemap_file.py`**
    - Contains `SitemapFileBatchUpdate` Pydantic schema
    - Defines API request structure for batch updates

### Layer 2: Database Session
11. **`/src/db/session.py`**
    - Provides `get_db_session()` for API routes
    - Would provide `get_background_session()` for scheduler (if it worked)

---

## WORKFLOW DATA FLOW (WORKING EXECUTION SEQUENCE)

### Stage 1: User Trigger ✅
**Location:** Browser → `/static/scraper-sky-mvp.html`
1. User selects sitemap file checkboxes in curation tab
2. User sets dropdown to "Selected"
3. User clicks "Update X Selected" button
4. JavaScript sends PUT request to `/api/v3/sitemap-files/status`

### Stage 2: API Processing ✅
**Location:** `/src/routers/sitemap_files.py`
1. Router receives `SitemapFileBatchUpdate` request
2. Calls `sitemap_files_service.update_curation_status_batch()`
3. Service executes dual-status update logic
4. Sets `sitemap_import_status = SitemapImportProcessStatusEnum.Queued`
5. Commits transaction and returns counts

### Stage 3: Background Processing ✅
**Location:** `/src/services/sitemap_import_scheduler.py`
1. **Scheduler runs:** `process_pending_sitemap_imports()` executes periodically
2. **SDK queries:** Uses `run_job_loop()` to find `sitemap_import_status = 'Queued'`
3. **Processing:** Calls `SitemapImportService.process_single_sitemap_file()`
4. **Status updates:** Queued → Processing → Complete/Error

### Stage 4: Actual Work ✅
**Location:** `/src/services/sitemap_import_service.py`
1. **Downloads:** Fetches sitemap XML from URL
2. **Parses:** Uses `SitemapParser` to extract all URLs
3. **Creates:** Generates Page records for each URL found
4. **Links:** Associates pages with domain and sitemap file

---

## PRODUCER-CONSUMER CHAIN (WORKING ECOSYSTEM)

### WF5 AS CONSUMER (What Triggers WF5)
**Consumes From:** WF4 (Domain Curation)
**Input Signal:** SitemapFile records with various curation statuses
**Source Table:** `sitemap_files` table
**Trigger:** User action in Sitemap Curation UI

### WF5 AS PRODUCER (What WF5 Creates)
**Produces For:** WF6 (Page Curation)  
**Output Signal:** Individual Page records ready for processing
**Target Table:** `pages` table with `lead_source = 'sitemap_import'`
**Consumer:** WF6 Page Curation workflow

### Working Chain
```
WF4 → Creates sitemap_files records
WF5 → User selection → sitemap_import_status = 'Queued' → Background processing → Creates Page records
WF6 → Processes Page records for content extraction
```

---

## STATUS FIELD TRANSITIONS (WORKING STATE MACHINE)

### Curation Status Flow ✅
```
Any Status → User selects → 'Selected' → (triggers process status queueing)
```

### Process Status Flow ✅
```
null → 'Queued' → 'Processing' → 'Complete'/'Error'
```

### Critical State Transitions (Line References)
- **Service:** Sets `sitemap_import_status = SitemapImportProcessStatusEnum.Queued`
- **Service:** Sets `sitemap_import_error = None`  
- **Scheduler:** Queries for 'Queued' status via SDK `run_job_loop()`
- **Scheduler:** Updates to 'Processing' during execution
- **Service:** Updates to 'Complete'/'Error' based on results

---

## CRITICAL DEPENDENCIES

### Working Dependencies ✅
- **Primary Table:** `sitemap_files` with dual status fields
- **API Layer:** Router and service logic for batch updates
- **Session Management:** API and background sessions
- **Transaction Boundaries:** Router owns API transactions
- **Background Processing:** Dedicated sitemap import scheduler
- **Service Integration:** SitemapImportService handles processing
- **Status Updates:** Full progression through state machine

### Configuration Dependencies
- **Scheduler Settings:** 
  - `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES`
  - `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE`
  - `SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES`
- **Database Connection:** Background sessions via SDK pattern

---

## BACKGROUND PROCESSING ARCHITECTURE

### The SDK Pattern Implementation

WF5 uses the curation SDK's `run_job_loop()` helper function, which provides:
- Automatic status field querying and updates
- Batch processing with configurable limits
- Error handling and status transitions
- Transaction management

### How the SDK Processes Jobs

```python
# From sitemap_import_scheduler.py
await run_job_loop(
    model=SitemapFile,
    status_enum=SitemapImportProcessStatusEnum,
    queued_status=SitemapImportProcessStatusEnum.Queued,
    processing_status=SitemapImportProcessStatusEnum.Processing,
    completed_status=SitemapImportProcessStatusEnum.Complete,
    failed_status=SitemapImportProcessStatusEnum.Error,
    processing_function=service.process_single_sitemap_file,
    batch_size=settings.SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE,
    order_by_column=asc(SitemapFile.updated_at),
    status_field_name="sitemap_import_status",
    error_field_name="sitemap_import_error",
)
```

---

## WHERE TO GET MORE INFORMATION

### Architecture References (AUTHORITATIVE SOURCES)
1. **`/Docs/Docs_7_Workflow_Canon/Dependency_Traces/v_WF5-Sitemap Curation.md`**
   - Complete file dependency map
   - May need updating to reflect working scheduler

2. **`/Docs/Docs_7_Workflow_Canon/workflows/v_11_WF5_CANONICAL.yaml`**
   - Business workflow definition
   - Accurately describes the workflow's purpose

3. **`/Docs/Docs_7_Workflow_Canon/Linear-Steps/v_WF5-SitemapCuration_linear_steps.md`**
   - Step-by-step execution sequence
   - Should be updated to include sitemap_import_scheduler

### Code Investigation Paths
- **API Layer:** `/src/routers/sitemap_files.py` ✅
- **Service Layer:** `/src/services/sitemap_files_service.py` ✅
- **Background Scheduler:** `/src/services/sitemap_import_scheduler.py` ✅
- **Processing Service:** `/src/services/sitemap_import_service.py` ✅
- **Data Models:** `/src/models/sitemap.py` enum definitions ✅
- **SDK Pattern:** `/src/common/curation_sdk/scheduler_loop.py` ✅

### Database Queries for Debugging
```sql
-- Check how many sitemap files are stuck in Queued status
SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued';

-- See the distribution of process statuses
SELECT sitemap_import_status, COUNT(*) 
FROM sitemap_files 
WHERE sitemap_import_status IS NOT NULL
GROUP BY sitemap_import_status;

-- Find oldest queued items (these will never be processed)
SELECT id, url, sitemap_import_status, updated_at 
FROM sitemap_files 
WHERE sitemap_import_status = 'Queued'
ORDER BY updated_at ASC
LIMIT 10;
```

---

## WHAT CAN GO WRONG (ERROR SCENARIOS)

### Processing Failures
- **Sitemap Download Failures:** Network timeouts, 404s, or access denied
- **Parsing Errors:** Malformed XML, encoding issues, or unexpected formats
- **Memory Issues:** Very large sitemaps (>100MB) may cause OOM errors
- **Database Constraints:** Duplicate URL insertions handled with individual retry logic

### Status Tracking Issues
- **Stuck in Processing:** If service crashes mid-process, status remains 'Processing'
- **Error Without Details:** Generic errors may not provide enough debugging info
- **Queue Starvation:** If batch size too small and interval too long

### API Layer Issues
- **Frontend sends wrong payload:** API returns 400 errors with validation details
- **Authentication failures:** 401/403 responses properly handled
- **Concurrent updates:** Race conditions prevented by `with_for_update(skip_locked=True)`

---

## EMERGENCY PROCEDURES

### Monitoring the Pipeline

1. **Check queue health:**
   ```sql
   -- Monitor queue depth
   SELECT sitemap_import_status, COUNT(*) 
   FROM sitemap_files 
   WHERE sitemap_import_status IS NOT NULL
   GROUP BY sitemap_import_status;
   ```

2. **Check scheduler logs:**
   ```bash
   # Look for sitemap import processing
   docker-compose logs scrapersky | grep "process_pending_sitemap_imports"
   ```

3. **Verify Page creation:**
   ```sql
   -- Check if Pages are being created
   SELECT COUNT(*), DATE(created_at) 
   FROM pages 
   WHERE lead_source = 'sitemap_import'
   GROUP BY DATE(created_at)
   ORDER BY DATE(created_at) DESC;
   ```

### If Processing Stops
1. **Check scheduler status:** Ensure sitemap_import_scheduler job is running
2. **Look for stuck items:** Find sitemaps stuck in 'Processing' status
3. **Reset stuck records:** Update old 'Processing' back to 'Queued'
4. **Check service logs:** Look for repeated errors in sitemap_import_service

### Performance Issues
1. **Adjust batch size:** Modify `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE`
2. **Increase interval:** If CPU/memory constrained
3. **Add monitoring:** Track processing time per sitemap

---

## CRITICAL UPDATE HISTORY

**2025-01-28 (v3.0):** Original document incorrectly identified WF5 as broken with missing scheduler logic.

**2025-01-28 (v3.1):** Comprehensive review of background services revealed:
- WF5 processing is handled by dedicated `sitemap_import_scheduler.py`
- The workflow is fully operational using SDK pattern
- A duplicate implementation was mistakenly added to `sitemap_scheduler.py` and has been reverted
- This document has been updated to reflect the working state

## ARCHITECTURE SUMMARY

**WF5 Sitemap Curation is a fully functional workflow** that:
1. Accepts user selections via the API layer
2. Queues sitemap files for background processing
3. Processes queued files via dedicated sitemap import scheduler
4. Downloads and parses sitemap XML
5. Creates Page records for downstream processing by WF6

**The workflow uses the SDK pattern** (`run_job_loop`) which provides robust error handling, status management, and batch processing capabilities.

**For future debugging:** Always check for dedicated schedulers before assuming functionality is missing. The ScraperSky architecture separates concerns with specialized schedulers for different workflow types.