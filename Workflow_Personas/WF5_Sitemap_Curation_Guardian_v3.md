# WF5 Sitemap Curation Guardian v3 - TRUTH DOCUMENT

**MISSION CRITICAL REFERENCE - OXYGEN SYSTEM LEVEL IMPORTANCE**

**Version:** 3.0 (Code Truth Authority)  
**Created:** 2025-01-28  
**Purpose:** Complete operational authority for WF5 Sitemap Curation workflow  
**Audience:** Future AI partners who need to understand and fix WF5 quickly  

---

## CRITICAL CONTEXT

**⚠️ WARNING: THIS WORKFLOW IS BROKEN ⚠️**

You are reading this because WF5 needs to be fixed. This workflow has a **critical gap** - user selections are queued but never processed by the background scheduler. This document contains the complete truth about the broken state and what needs to be implemented to fix it.

---

## WHAT WF5 IS (CODE REALITY)

WF5 is a **PARTIALLY IMPLEMENTED** dual-status automation system intended to transform user sitemap selections into queued deep scrape jobs. When users mark sitemap files as "Selected", the system queues them for background processing - **but the background processor never picks them up**.

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

**THE BROKEN LINK:** The scheduler (`/src/services/sitemap_scheduler.py`) does NOT import `SitemapFile` or query for queued sitemap processing.

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

5. **`/src/services/sitemap_scheduler.py`** (**BROKEN - MISSING LOGIC**)
   - Contains `process_pending_jobs()` function
   - **CRITICAL GAP:** Does NOT import `SitemapFile`
   - **MISSING QUERY:** No logic to find `sitemap_import_status == 'Queued'`
   - **MISSING PROCESSING:** No calls to sitemap processing service
   - **Current imports:** Only handles `LocalBusiness`, `Place`, and legacy `Job` models

6. **`/src/services/page_scraper/processing_service.py`** (**INTENDED TARGET - NOT CALLED**)
   - **Role:** Likely contains logic to process queued sitemap files
   - **Function:** Would fetch sitemap, parse URLs, queue page scraping jobs
   - **Status:** NOT currently triggered by scheduler

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

## WORKFLOW DATA FLOW (BROKEN EXECUTION SEQUENCE)

### Stage 1: User Trigger (WORKING)
**Location:** Browser → `/static/scraper-sky-mvp.html`
1. User selects sitemap file checkboxes in curation tab
2. User sets dropdown to "Selected"
3. User clicks "Update X Selected" button
4. JavaScript sends PUT request to `/api/v3/sitemap-files/status`

### Stage 2: API Processing (WORKING)
**Location:** `/src/routers/sitemap_files.py`
1. Router receives `SitemapFileBatchUpdate` request
2. Calls `sitemap_files_service.update_curation_status_batch()`
3. Service executes dual-status update logic
4. Sets `sitemap_import_status = SitemapImportProcessStatusEnum.Queued`
5. Commits transaction and returns counts

### Stage 3: Background Processing (**BROKEN**)
**Location:** `/src/services/sitemap_scheduler.py`
1. **Scheduler runs:** `process_pending_jobs()` executes periodically
2. **MISSING:** No query for `SitemapFile` where `sitemap_import_status = 'Queued'`
3. **MISSING:** No processing of queued sitemap files
4. **RESULT:** Sitemap files remain stuck in 'Queued' status forever

### Stage 4: Actual Work (**NEVER REACHED**)
**Location:** `/src/services/page_scraper/processing_service.py` (presumed)
1. **INTENDED:** Process queued sitemap files
2. **INTENDED:** Parse sitemaps and extract URLs
3. **INTENDED:** Queue individual page scraping jobs
4. **REALITY:** Never executed because scheduler doesn't call it

---

## PRODUCER-CONSUMER CHAIN (BROKEN ECOSYSTEM)

### WF5 AS CONSUMER (What Triggers WF5)
**Consumes From:** WF4 (Domain Curation)
**Input Signal:** SitemapFile records with various curation statuses
**Source Table:** `sitemap_files` table
**Trigger:** User action in Sitemap Curation UI

### WF5 AS PRODUCER (**BROKEN** - What WF5 Should Create)
**Should Produce For:** WF6 (Page Curation)  
**Intended Output Signal:** Individual page records queued for scraping
**Target Table:** Would create page/URL records (not implemented)
**Consumer:** WF6 Page Curation workflow

### **BROKEN** Chain
```
WF4 → sitemap_files with various curation statuses
WF5 → User selection → sitemap_import_status = 'Queued' → **STOPS HERE**
WF6 → **NEVER RECEIVES INPUT** because WF5 processing never happens
```

---

## STATUS FIELD TRANSITIONS (BROKEN STATE MACHINE)

### Curation Status Flow (WORKING)
```
Any Status → User selects → 'Selected' → (triggers process status queueing)
```

### Process Status Flow (**BROKEN**)  
```
null → 'Queued' → **STUCK FOREVER** (no background processing)
```

**INTENDED Process Status Flow:**
```
null → 'Queued' → 'Processing' → 'Completed'/'Error'
```

### Critical State Transitions (Line References)
- **Service:** Sets `sitemap_import_status = SitemapImportProcessStatusEnum.Queued`
- **Service:** Sets `sitemap_import_error = None`
- **MISSING:** Scheduler should query for 'Queued' status
- **MISSING:** Scheduler should update to 'Processing' during execution
- **MISSING:** Scheduler should update to 'Completed'/'Error' based on results

---

## CRITICAL DEPENDENCIES (FAILURE POINTS)

### Working Dependencies
- **Primary Table:** `sitemap_files` with dual status fields (WORKS)
- **API Layer:** Router and service logic (WORKS)
- **Session Management:** Both sync sessions work (WORKS)
- **Transaction Boundaries:** Router owns API transactions (WORKS)

### **BROKEN** Dependencies  
- **Background Processing:** Scheduler doesn't process sitemap queues (BROKEN)
- **Service Integration:** Missing calls to page scraper service (BROKEN)
- **Status Updates:** No progression beyond 'Queued' (BROKEN)

### Configuration Dependencies
- **Scheduler Interval:** Polling frequency works but processes wrong queues
- **Database Connection:** Background sessions would work if scheduler used them

---

## WHAT NEEDS TO BE IMPLEMENTED

### **CRITICAL FIX REQUIRED:** Scheduler Integration

**File:** `/src/services/sitemap_scheduler.py`  
**Missing imports:**
```python
from ..models.sitemap import SitemapFile, SitemapImportProcessStatusEnum
```

**Missing query logic:**
```python
# Query for queued sitemap files
stmt_select_sitemap = (
    select(SitemapFile)
    .where(SitemapFile.sitemap_import_status == SitemapImportProcessStatusEnum.Queued)
    .order_by(SitemapFile.updated_at.asc())
    .limit(limit)
    .with_for_update(skip_locked=True)
)
```

**Missing processing logic:**
```python
# Process each queued sitemap file
for sitemap_file in queued_sitemap_files:
    # Update status to Processing
    sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Processing
    
    # Call processing service (needs to be implemented)
    processing_service = PageScraperProcessingService()
    result = await processing_service.process_sitemap_file(sitemap_file.id)
    
    # Update final status based on result
    if result.success:
        sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Completed
    else:
        sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Error
        sitemap_file.sitemap_import_error = result.error_message
```

---

## WHERE TO GET MORE INFORMATION

### Architecture References (AUTHORITATIVE SOURCES)
1. **`/Docs/Docs_7_Workflow_Canon/Dependency_Traces/WF5-Sitemap Curation.md`**
   - Documents the broken state and missing scheduler logic
   - Complete file dependency map
   - Identifies the gap explicitly

2. **`/Docs/Docs_7_Workflow_Canon/workflows/v_11_WF5_CANONICAL.yaml`**
   - Business workflow definition (intended, not actual)
   - What the workflow should accomplish when fixed

3. **`/Docs/Docs_7_Workflow_Canon/Linear-Steps/WF5-SitemapCuration_linear_steps.md`**
   - Step-by-step execution sequence (shows where it breaks)

### Code Investigation Paths
- **API Issues:** `/src/routers/sitemap_files.py` (works correctly)
- **Service Issues:** `/src/services/sitemap_files_service.py` (works correctly)
- **BROKEN Scheduler:** `/src/services/sitemap_scheduler.py` (missing sitemap processing)
- **Data Issues:** `/src/models/sitemap.py` enum definitions (work correctly)

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

### Current **BROKEN** State
- **Infinite Queue Growth:** All selected sitemap files accumulate in 'Queued' status
- **No Processing:** Background scheduler never picks up queued items
- **Silent Failure:** Users see successful API responses but nothing happens
- **Resource Waste:** Database fills with permanently queued records

### **Future** Implementation Risks (When Fixed)
- **Service Integration Failures:** If page scraper service doesn't exist or fails
- **Processing Timeouts:** If sitemap parsing takes too long
- **Memory Issues:** If large sitemaps consume too much memory during processing

### API Layer Issues (Currently Working)
- **Frontend sends wrong payload:** API returns 400 errors (works correctly)
- **Authentication failures:** 401/403 responses (works correctly)
- **Database constraint violations:** Service handles gracefully (works correctly)

---

## EMERGENCY PROCEDURES

### **IMMEDIATE ACTION REQUIRED:** Fix the Broken Pipeline

1. **Verify the broken state:**
   ```sql
   -- This query will likely return many results
   SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued';
   ```

2. **Check scheduler is running but not processing sitemaps:**
   ```bash
   docker-compose logs scrapersky | grep "sitemap_scheduler"
   # Will show scheduler running but no sitemap processing logs
   ```

3. **Implement the missing scheduler logic:**
   - Add imports for `SitemapFile` and `SitemapImportProcessStatusEnum`
   - Add query logic for queued sitemap files
   - Add processing service calls
   - Add status update logic

### **Temporary Workaround** (Until Fixed)
- **Reset stuck records:** Manually update queued items back to a processable state
- **Monitor queue growth:** Alert when too many items are stuck
- **User communication:** Inform users that sitemap processing is temporarily disabled

### If Implementation Goes Wrong
1. **Rollback strategy:** Keep the working API layer, remove scheduler changes
2. **Gradual deployment:** Process small batches first to test integration
3. **Monitoring:** Watch for memory usage and processing times during implementation

---

## FINAL WARNING

**THIS WORKFLOW IS CURRENTLY BROKEN AND NEEDS IMPLEMENTATION TO FUNCTION.**

**The API layer works correctly and will continue to queue sitemap files for processing. However, NO BACKGROUND PROCESSING OCCURS. This creates a growing queue of permanently stuck records.**

**Priority Fix:** Implement missing scheduler logic to process queued sitemap files before the queue becomes unmanageably large.

**DO NOT** attempt to "fix" the working API layer or service layer. The break is specifically in the scheduler's missing logic.

**This document reflects the broken state as of 2025-01-28. When the scheduler logic is implemented, UPDATE THIS DOCUMENT to reflect the working state.**

**The fate of WF5 operations depends on implementing the missing scheduler logic. This is not a documentation problem - it's a missing implementation problem.**