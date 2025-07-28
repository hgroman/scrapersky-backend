# WF6 Sitemap Import Guardian v3 - TRUTH DOCUMENT

**MISSION CRITICAL REFERENCE - OXYGEN SYSTEM LEVEL IMPORTANCE**

**Version:** 3.0 (Code Truth Authority)  
**Created:** 2025-01-28  
**Purpose:** Complete operational authority for WF6 Sitemap Import workflow  
**Audience:** Future AI partners who need to understand and fix WF6 quickly  

---

## CRITICAL CONTEXT

You are reading this because something in WF6 needs to be understood or fixed. **GOOD NEWS:** This workflow is FULLY FUNCTIONAL and properly implemented. This document contains the complete truth about how WF6 works based on actual code analysis. Every statement is traceable to specific code lines.

---

## WHAT WF6 IS (CODE REALITY)

WF6 is a **WORKING** background processing system that automatically processes queued sitemap files, extracts URLs from their XML content, and creates Page records in the database. Unlike WF5 (which is broken), WF6 has a complete pipeline from queue detection to URL extraction.

**Core Processing Logic (Lines 29-44 in `/src/services/sitemap_import_scheduler.py`):**
```python
await run_job_loop(
    model=SitemapFile,
    status_enum=SitemapImportProcessStatusEnum,
    queued_status=SitemapImportProcessStatusEnum.Queued,
    processing_status=SitemapImportProcessStatusEnum.Processing,
    completed_status=SitemapImportProcessStatusEnum.Complete,
    failed_status=SitemapImportProcessStatusEnum.Error,
    # Pass the service method as the processing function
    processing_function=service.process_single_sitemap_file,
    batch_size=settings.SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE,
    order_by_column=asc(SitemapFile.updated_at),
    status_field_name="sitemap_import_status",
    error_field_name="sitemap_import_error",
)
```

This is the heart of WF6 - a standardized job processing loop that actually works.

---

## COMPLETE FILE DEPENDENCY MAP

### Layer 6: User Interface (DEVELOPMENT ONLY)
1. **`/src/routers/dev_tools.py`** (Manual Testing)
   - Provides development endpoints for manual sitemap import triggering
   - **Endpoint:** `POST /api/v3/dev/import-sitemap/{sitemap_file_id}`
   - Used for testing and troubleshooting individual sitemap files

### Layer 4: Background Services (WORKING PIPELINE)
2. **`/src/services/sitemap_import_scheduler.py`** (SCHEDULER ENGINE)
   - **Function:** `process_pending_sitemap_imports()` (line 20)
   - **Imports:** `SitemapFile, SitemapImportProcessStatusEnum` (line 11) ✅
   - **Processing:** Uses `run_job_loop` from curation SDK (line 29)
   - **Service Integration:** Calls `SitemapImportService.process_single_sitemap_file()` (line 37)
   - **Configuration:** Uses `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE` (line 39)

3. **`/src/services/sitemap_import_service.py`** (ACTUAL WORK ENGINE)
   - Contains `SitemapImportService` class
   - **Function:** `process_single_sitemap_file(sitemap_file_id: uuid.UUID, session: AsyncSession)` (line 24)
   - **HTTP Fetching:** Uses `httpx.AsyncClient` with 60s timeout (lines 67-74)
   - **XML Parsing:** Uses `SitemapParser.parse()` to extract URLs (lines 78-80)
   - **Page Creation:** Creates `Page` records for each extracted URL
   - **Status Updates:** Sets `sitemap_import_status` to `Complete` or `Error`

4. **`/src/common/curation_sdk/scheduler_loop.py`** (SHARED PROCESSING)
   - **Function:** `run_job_loop()` - standardized batch processing
   - Handles status transitions from Queued → Processing → Complete/Error
   - Provides transaction management and error isolation
   - Used by multiple workflows for consistent processing patterns

5. **`/src/common/sitemap_parser.py`** (XML PARSER)
   - Contains `SitemapParser` class
   - **Function:** `parse(sitemap_content: str, sitemap_url: str)` 
   - Extracts URLs, lastmod dates, and other metadata from XML
   - Returns list of `SitemapURL` objects

### Layer 5: Configuration & Infrastructure
6. **`/src/scheduler_instance.py`**
   - Provides shared AsyncIOScheduler instance
   - Used by sitemap_import_scheduler for background processing

7. **`/src/main.py`**
   - Application startup
   - Calls `setup_sitemap_import_scheduler()` during lifespan events

8. **`/src/config/settings.py`**
   - **Settings:** `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES`
   - **Settings:** `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE`
   - **Settings:** `SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES`

### Layer 1: Data Models (WORKING)
9. **`/src/models/sitemap.py`** (DATA AUTHORITY)
   - `SitemapFile` SQLAlchemy model class
   - **Status field:** `sitemap_import_status` using `SitemapImportProcessStatusEnum`
   - **Key values:** `Queued`, `Processing`, `Complete`, `Error`
   - **URL field:** `url` - contains the sitemap XML file URL
   - **Error field:** `sitemap_import_error` - stores error messages

10. **`/src/models/page.py`** (OUTPUT DATA)
    - `Page` SQLAlchemy model class
    - **Created by:** WF6 for each URL extracted from sitemaps
    - **Key fields:** `url`, `domain_id`, `sitemap_file_id`, `last_modified`
    - **Status field:** `status` - starts as "New" for downstream processing

### Layer 2: Database Session
11. **`/src/session/async_session.py`**
    - Provides async database sessions for background processing
    - Used by scheduler and service for database operations

---

## WORKFLOW DATA FLOW (COMPLETE WORKING SEQUENCE)

### Stage 1: Scheduler Activation (WORKING)
**Location:** `/src/services/sitemap_import_scheduler.py`
1. Application startup calls `setup_sitemap_import_scheduler()`
2. Scheduler creates recurring job for `process_pending_sitemap_imports()`
3. Job runs at configured intervals (default: every few minutes)
4. Logging captures successful scheduler initialization

### Stage 2: Queue Detection (WORKING)
**Location:** `/src/common/curation_sdk/scheduler_loop.py` via scheduler
1. `run_job_loop()` queries for `SitemapFile` where `sitemap_import_status = 'Queued'`
2. Records ordered by `updated_at` (oldest first)
3. Batch limited by `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE`
4. Each record locked during processing to prevent conflicts

### Stage 3: Individual File Processing (WORKING)
**Location:** `/src/services/sitemap_import_service.py` lines 24-150+
1. **Status Update:** `sitemap_import_status` set to `Processing`
2. **HTTP Request:** Fetch sitemap XML content with 60s timeout
3. **XML Parsing:** Extract URLs using `SitemapParser`
4. **Page Creation:** Create `Page` record for each extracted URL
5. **Database Insert:** Bulk insert with fallback to individual inserts on conflicts
6. **Status Update:** Set to `Complete` or `Error` based on results

### Stage 4: Output Generation (WORKING)
**Location:** Page records created in database
1. Each extracted URL becomes a `Page` record
2. Pages linked to source `sitemap_file_id`
3. Pages start with `status = 'New'` for downstream workflows
4. Domain relationship maintained through `domain_id`

---

## PRODUCER-CONSUMER CHAIN (WORKING ECOSYSTEM)

### WF6 AS CONSUMER (What Triggers WF6)
**Consumes From:** WF5 (Sitemap Curation) - **BROKEN HANDOFF**
**Input Signal:** SitemapFile records with `sitemap_import_status = 'Queued'`
**Source Table:** `sitemap_files` table
**Trigger:** Background scheduler polling (working)

**CRITICAL NOTE:** WF5 is supposed to queue sitemaps but is broken. WF6 works perfectly but has no input source.

### WF6 AS PRODUCER (What WF6 Creates)
**Produces For:** Future page processing workflows
**Output Signal:** Page records with `status = 'New'`
**Target Table:** `pages` table
**Consumer:** Not yet implemented

### Complete Chain (PARTIALLY BROKEN)
```
WF5 → **BROKEN** (doesn't queue sitemap files) 
WF6 → **WORKS** (processes queued files perfectly)
Future WF → **NOT IMPLEMENTED** (would consume Page records)
```

---

## STATUS FIELD TRANSITIONS (WORKING STATE MACHINE)

### Import Status Flow (WORKING)
```
Queued → Processing → Complete/Error
```

### Critical State Transitions (Line References)
- **Scheduler SDK:** Updates to `Processing` during job execution
- **Service Line 87:** `sitemap_import_status = SitemapImportProcessStatusEnum.Complete`
- **Service Error Handlers:** Sets status to `Error` with appropriate error messages
- **Service Line 88:** `sitemap_import_error = None` on success

### Page Status Flow (OUTPUT)
```
Created → status = 'New' (ready for downstream processing)
```

---

## CRITICAL DEPENDENCIES (ALL WORKING)

### Database Dependencies (WORKING)
- **Primary Table:** `sitemap_files` with import status field
- **Output Table:** `pages` for extracted URLs
- **Session Management:** Async sessions for background processing
- **Transaction Boundaries:** Service manages individual file transactions

### Service Dependencies (WORKING)
- **APScheduler:** Running and configured for sitemap import
- **SitemapImportService:** Fully implemented and functional
- **HTTP Client:** `httpx` with proper timeout and redirect handling
- **XML Parser:** `SitemapParser` handles sitemap content extraction

### Configuration Dependencies (WORKING)
- **Scheduler Interval:** `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES`
- **Batch Size:** `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE`
- **HTTP Timeout:** 60 seconds for sitemap fetching
- **Database Connection:** Async sessions working correctly

---

## KNOWN ARCHITECTURAL FACTS

### The Curation SDK Pattern
**Purpose:** Standardized job processing across multiple workflows
**Implementation:** `run_job_loop()` handles common batch processing logic
**Business Value:** Consistent status management and error handling across workflows

### Background Processing Model
**Pattern:** Poll-based scheduler with standardized SDK
**Frequency:** Configurable via `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES`
**Isolation:** Each sitemap file processed in separate transaction
**Error Handling:** Comprehensive with status tracking and error messages

### HTTP Processing Model
**Client:** `httpx.AsyncClient` with redirect following
**Timeout:** 60 seconds to handle large sitemap files
**Error Handling:** Separate handling for HTTP status errors vs. network errors
**Resource Management:** Async context manager ensures proper cleanup

---

## WHERE TO GET MORE INFORMATION

### Architecture References (AUTHORITATIVE SOURCES)
1. **`/Docs/Docs_7_Workflow_Canon/Dependency_Traces/WF6-SitemapImport_dependency_trace.md`**
   - Complete file dependency map with detailed component descriptions
   - Integration points and external dependencies
   - Database tables and key fields

2. **`/Docs/Docs_7_Workflow_Canon/workflows/v_12_WF6_CANONICAL.yaml`**
   - Comprehensive workflow definition with phases and steps
   - Architectural and technical principles
   - Known issues and documentation todos

3. **`/Docs/Docs_7_Workflow_Canon/Linear-Steps/WF6-SitemapImport_linear_steps.md`**
   - 14-step detailed execution sequence
   - Integration points with other workflows
   - Observability and manual intervention points

### Code Investigation Paths
- **Scheduler Issues:** `/src/services/sitemap_import_scheduler.py`
- **Processing Issues:** `/src/services/sitemap_import_service.py`
- **Data Issues:** `/src/models/sitemap.py` and `/src/models/page.py`
- **Configuration Issues:** `/src/config/settings.py`

### Database Queries for Debugging
```sql
-- Check sitemap import queue status
SELECT sitemap_import_status, COUNT(*) 
FROM sitemap_files 
GROUP BY sitemap_import_status;

-- Find stuck or long-running imports
SELECT id, url, sitemap_import_status, updated_at 
FROM sitemap_files 
WHERE sitemap_import_status = 'Processing' 
AND updated_at < NOW() - INTERVAL '1 hour';

-- Check page creation output
SELECT COUNT(*) as pages_created, sitemap_file_id 
FROM pages 
WHERE lead_source = 'sitemap_import'
GROUP BY sitemap_file_id
ORDER BY pages_created DESC
LIMIT 10;

-- Find recent import errors
SELECT id, url, sitemap_import_error, updated_at 
FROM sitemap_files 
WHERE sitemap_import_status = 'Error' 
ORDER BY updated_at DESC 
LIMIT 10;
```

---

## WHAT CAN GO WRONG (ERROR SCENARIOS)

### HTTP-Related Failures (HANDLED)
- **Status errors (4xx, 5xx):** Sitemap marked as 'Error' with status code
- **Network timeouts:** Handled with 60s timeout and error logging
- **DNS failures:** Network error handling captures and logs
- **Redirect loops:** `httpx` handles with redirect following enabled

### XML Parsing Failures (HANDLED)
- **Invalid XML:** Parser errors caught and logged
- **Empty sitemaps:** Handled gracefully, marked as 'Complete'
- **Malformed URLs:** Skipped with logging, doesn't fail entire import
- **Missing required fields:** Individual URL failures don't stop batch

### Database Issues (HANDLED)
- **Duplicate URLs:** IntegrityError caught, falls back to individual inserts
- **Transaction failures:** Rolled back with error status set
- **Session timeouts:** Handled by async session management
- **Foreign key violations:** Logged and marked as error

### **UPSTREAM DEPENDENCY FAILURE**
- **WF5 broken:** No sitemap files get queued for processing
- **Manual intervention required:** Can queue files via database updates
- **Development endpoints:** Available for manual testing

---

## EMERGENCY PROCEDURES

### If No Sitemap Files Are Being Processed
1. **Check if scheduler is running:**
   ```bash
   docker-compose logs scrapersky | grep "sitemap_import"
   # Should show periodic job execution logs
   ```

2. **Check queue depth:**
   ```sql
   SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued';
   -- If zero, WF5 is not queuing files (known issue)
   ```

3. **Manual queue for testing:**
   ```sql
   UPDATE sitemap_files 
   SET sitemap_import_status = 'Queued' 
   WHERE id = 'some-sitemap-id';
   ```

### If Sitemap Import Is Failing
1. **Check recent errors:**
   ```sql
   SELECT sitemap_import_error FROM sitemap_files 
   WHERE sitemap_import_status = 'Error' 
   ORDER BY updated_at DESC LIMIT 5;
   ```

2. **Test individual sitemap manually:**
   ```bash
   curl -X POST "http://localhost:8000/api/v3/dev/import-sitemap/{sitemap_file_id}"
   ```

3. **Check HTTP accessibility:**
   ```bash
   curl -I "sitemap-url-here"
   # Should return 200 OK
   ```

### If Pages Are Not Being Created
1. **Check successful imports with zero pages:**
   ```sql
   SELECT sf.id, sf.url, COUNT(p.id) as page_count
   FROM sitemap_files sf
   LEFT JOIN pages p ON p.sitemap_file_id = sf.id
   WHERE sf.sitemap_import_status = 'Complete'
   GROUP BY sf.id, sf.url
   HAVING COUNT(p.id) = 0;
   ```

2. **Verify sitemap content manually:**
   ```bash
   curl "sitemap-url-here" | head -50
   # Should show XML with <url> elements
   ```

---

## FINAL WARNING

**THIS WORKFLOW IS FULLY FUNCTIONAL AND SHOULD NOT BE MODIFIED WITHOUT CAREFUL CONSIDERATION.**

**The primary issue is the UPSTREAM DEPENDENCY:** WF5 is broken and doesn't queue sitemap files for processing. WF6 works perfectly but has no input source.

**Priority Fix:** Fix WF5 (Sitemap Curation) to properly queue sitemap files, then WF6 will automatically process them.

**DO NOT** attempt to "fix" the working WF6 components. The issue is in WF5's missing scheduler logic.

**This document reflects the working state as of 2025-01-28. The implementation is solid and follows best practices for async processing, error handling, and status management.**

**The fate of WF6 operations depends on fixing the upstream WF5 dependency. WF6 itself is ready to process sitemap files as soon as they are properly queued.**