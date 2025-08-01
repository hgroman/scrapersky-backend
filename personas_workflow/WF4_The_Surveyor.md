# WF4 - The Surveyor Guardian v3 - TRUTH DOCUMENT

**MISSION CRITICAL REFERENCE - OXYGEN SYSTEM LEVEL IMPORTANCE**

**Version:** 3.0 (Code Truth Authority)  
**Created:** 2025-01-27  
**Purpose:** Complete operational authority for WF4 - The Surveyor workflow  
**Audience:** Future AI partners who need to understand and fix WF4 quickly  

---

## CRITICAL CONTEXT

You are reading this because something in WF4 needs to be fixed. This document contains the complete truth about how WF4 works based on actual code analysis. Every statement is traceable to specific code lines. No embellishments. No assumptions. Only facts.

---

## WHAT WF4 IS (CODE REALITY)

WF4 is a dual-status automation system that transforms user domain selections into queued sitemap analysis jobs. When users mark domains as "Selected", the system automatically queues them for background sitemap processing.

**Core Business Logic (Lines 229-236 in `/src/routers/domains.py`):**
```python
# Conditional logic: If status is 'Selected', queue for analysis
if db_curation_status == SitemapCurationStatusEnum.Selected:
    domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.queued
    domain.sitemap_analysis_error = None
    queued_count += 1
```

This is the heart of WF4. Everything else is infrastructure to support this transformation.

---

## COMPLETE FILE DEPENDENCY MAP

### Layer 6: User Interface
1. **`/static/scraper-sky-mvp.html`** (Lines 808-895)
   - Domain Curation panel with checkboxes and status dropdown
   - Batch update controls for selecting multiple domains
   - Status options: New, Selected, Maybe, Not a Fit, Archived

2. **`/static/js/domain-curation-tab.js`** (Lines 393-413)
   - Sends PUT requests to `/api/v3/domains/sitemap-curation/status`
   - Manages checkbox selection state
   - Updates button text with selected count

### Layer 3: API Router
3. **`/src/routers/domains.py`** (PRIMARY BUSINESS LOGIC)
   - **Line 161:** `@router.put("/sitemap-curation/status")`
   - **Line 162:** `async def update_domain_sitemap_curation_status_batch()`
   - **Lines 229-236:** Dual-status update logic (THE CRITICAL CODE)
   - **Line 240:** `await session.commit()`

### Layer 4: Background Services
4. **`/src/services/domain_sitemap_submission_scheduler.py`** (PROCESSING ENGINE)
   - **Line 27:** `from src.scraper.sitemap_analyzer import SitemapAnalyzer`
   - **Lines 60-67:** Query for domains with `sitemap_analysis_status == "queued"`
   - **Line 117:** `sitemap_results = await sitemap_analyzer.analyze_domain_sitemaps(str(domain_url))`
   - **Line 162:** Runs every 1 minute

5. **`/src/scraper/sitemap_analyzer.py`** (ACTUAL WORK ENGINE)
   - Contains `SitemapAnalyzer` class
   - Function: `analyze_domain_sitemaps(domain_url: str)`
   - Performs actual sitemap discovery and analysis

### Layer 5: Configuration & Infrastructure
6. **`/src/scheduler_instance.py`**
   - Provides shared AsyncIOScheduler instance
   - Used by domain_sitemap_submission_scheduler

7. **`/src/main.py`**
   - Application startup
   - Initializes domain sitemap scheduler

### Layer 1: Data Models
8. **`/src/models/domain.py`** (DATA AUTHORITY)
   - **Lines 36-46:** `SitemapCurationStatusEnum` values
   - **Lines 52-61:** `SitemapAnalysisStatusEnum` values
   - **Line 116:** `domain = Column(String, nullable=False)`
   - **Lines 177-186:** `sitemap_analysis_status` field
   - **Lines 190-199:** `sitemap_curation_status` field

9. **`/src/models/api_models.py`**
   - Contains `DomainBatchCurationStatusUpdateRequest`
   - Defines API request/response schemas

### Layer 2: Database Session
10. **`/src/db/session.py`**
    - Provides `get_db_session()` for API routes
    - Provides `get_background_session()` for scheduler

---

## WORKFLOW DATA FLOW (EXACT EXECUTION SEQUENCE)

### Stage 1: User Trigger
**Location:** Browser → `/static/scraper-sky-mvp.html`
1. User selects domain checkboxes
2. User sets dropdown to "Selected"
3. User clicks "Update X Selected" button
4. JavaScript sends PUT request to `/api/v3/domains/sitemap-curation/status`

### Stage 2: API Processing
**Location:** `/src/routers/domains.py` lines 162-253
1. Router receives `DomainBatchCurationStatusUpdateRequest`
2. Maps API enum to DB enum (lines 184-196)
3. Fetches Domain objects by ID (lines 201-204)
4. **CRITICAL:** Executes dual-status update (lines 220-236)
5. Commits transaction (line 240)
6. Returns `{"updated_count": int, "queued_count": int}`

### Stage 3: Background Processing
**Location:** `/src/services/domain_sitemap_submission_scheduler.py`
1. **Every 1 minute:** Scheduler polls for queued domains (line 162)
2. **Query:** Selects domains where `sitemap_analysis_status = "queued"` (lines 60-67)
3. **Batch size:** Processes up to 10 domains per cycle (line 64)
4. **Processing:** Calls `SitemapAnalyzer.analyze_domain_sitemaps()` (line 117)
5. **Status update:** Updates `sitemap_analysis_status` based on results

### Stage 4: Actual Work
**Location:** `/src/scraper/sitemap_analyzer.py`
1. `analyze_domain_sitemaps(domain_url)` executes
2. Discovers and analyzes sitemaps for the domain
3. Returns analysis results to scheduler

---

## PRODUCER-CONSUMER CHAIN (ECOSYSTEM POSITION)

### WF4 AS CONSUMER (What Triggers WF4)
**Consumes From:** WF3 (Local Business Curation)
**Input Signal:** Domains with `sitemap_curation_status = 'New'`
**Source Table:** `domains` table
**Trigger:** User action in Domain Curation UI

### WF4 AS PRODUCER (What WF4 Creates)
**Produces For:** WF5 (Sitemap Curation)  
**Output Signal:** Domains with `sitemap_analysis_status = 'queued'`
**Target Table:** `domains` table
**Consumer:** WF5 background services

### Complete Chain
```
WF3 → domains.sitemap_curation_status = 'New'
WF4 → User selection → sitemap_analysis_status = 'queued'  
WF5 → Consumes queued analysis jobs
```

---

## STATUS FIELD TRANSITIONS (DATA STATE MACHINE)

### Curation Status Flow
```
'New' → User selects → 'Selected' → (triggers analysis queueing)
```

### Analysis Status Flow  
```
null → 'queued' → 'processing' → 'completed'/'failed'
```

### Critical State Transitions (Line References)
- **Router Line 222:** `domain.sitemap_curation_status = db_curation_status`
- **Router Line 231:** `domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.queued`
- **Scheduler Line 109:** `domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.processing`
- **Scheduler Line 127:** `domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.completed`

---

## CRITICAL DEPENDENCIES (FAILURE POINTS)

### Database Dependencies
- **Primary Table:** `domains` with dual status fields
- **Session Management:** Both sync (API) and async (background) sessions
- **Transaction Boundaries:** Router owns API transactions, scheduler manages background transactions

### Service Dependencies  
- **APScheduler:** Must be running for background processing
- **SitemapAnalyzer:** Must be available for actual sitemap work
- **HTTP Frontend:** Must send correct API payloads

### Configuration Dependencies
- **Scheduler Interval:** 1 minute polling (line 162 in scheduler)
- **Batch Size:** 10 domains per cycle (line 64 in scheduler)
- **Database Connection:** Both API and background sessions must work

---

## KNOWN ARCHITECTURAL FACTS

### The Dual-Status Pattern
**Purpose:** User curation decisions automatically trigger background processing
**Implementation:** Single API call updates two different status fields
**Business Value:** Manual domain selection becomes automated analysis pipeline

### Background Processing Model
**Pattern:** Poll-based scheduler with direct service calls
**Frequency:** Every 1 minute
**Isolation:** Each domain processed in separate transaction
**Error Handling:** Per-domain error tracking with status updates

### Layer Separation
**UI Layer:** Manages user interaction and API calls
**API Layer:** Owns business logic and transaction boundaries  
**Service Layer:** Handles background processing and actual work
**Data Layer:** Enforces status constraints and relationships

---

## WHERE TO GET MORE INFORMATION

### Architecture References (AUTHORITATIVE SOURCES)
1. **`/Docs/Docs_7_Workflow_Canon/Dependency_Traces/v_WF4-Domain Curation.md`**
   - Complete 18-file dependency map
   - Producer-consumer relationships
   - Layer-by-layer breakdown

2. **`/Docs/Docs_7_Workflow_Canon/workflows/v_10_WF4_CANONICAL.yaml`** ⚡ VECTORIZED
   - Business workflow definition
   - Compliance verification
   - Cross-workflow connections

3. **`/Docs/Docs_7_Workflow_Canon/Linear-Steps/v_WF4-DomainCuration_linear_steps.md`**
   - 8-step atomic workflow execution
   - File annotations (NOVEL/SHARED)
   - Architectural principles

### Code Investigation Paths
- **API Issues:** Start with `/src/routers/domains.py` lines 162-253
- **Background Issues:** Check `/src/services/domain_sitemap_submission_scheduler.py`
- **Data Issues:** Examine `/src/models/domain.py` enum definitions
- **UI Issues:** Debug `/static/js/domain-curation-tab.js` API calls

### Database Queries for Debugging
```sql
-- Check domain status distribution
SELECT sitemap_curation_status, sitemap_analysis_status, COUNT(*) 
FROM domains 
GROUP BY sitemap_curation_status, sitemap_analysis_status;

-- Find stuck domains
SELECT id, domain, sitemap_analysis_status, updated_at 
FROM domains 
WHERE sitemap_analysis_status = 'processing' 
AND updated_at < NOW() - INTERVAL '10 minutes';

-- Check queue depth
SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued';
```

---

## WHAT CAN GO WRONG (ERROR SCENARIOS)

### Dual-Status Update Failures
- **Router transaction rollback:** Both status fields revert
- **Enum validation errors:** Invalid status values rejected
- **Concurrent updates:** Multiple users updating same domains

### Background Processing Failures  
- **Scheduler not running:** Domains stuck in 'queued' status
- **SitemapAnalyzer errors:** Domains marked as 'failed'
- **Database connection issues:** Processing halts entirely

### UI/API Disconnect
- **Frontend sends wrong payload:** API returns 400 errors
- **Authentication failures:** 401/403 responses
- **Network timeouts:** User sees failed updates

---

## EMERGENCY PROCEDURES

### If Domains Are Stuck in 'Queued' Status
1. Check if scheduler is running: `docker-compose logs scrapersky | grep sitemap_submission`
2. Verify SitemapAnalyzer is working: Test direct function call
3. Check database connections: Verify background session works

### If Dual-Status Update Fails
1. Check router logs for transaction errors
2. Verify enum values match between API and database
3. Test API endpoint directly with curl

### If UI Shows Wrong Status
1. Check browser network tab for API call results
2. Verify JavaScript is sending correct payloads
3. Test API endpoint returns expected data

---

## FINAL WARNING

**This document reflects the actual running code as of 2025-01-27. If you change the implementation, UPDATE THIS DOCUMENT. Future AI partners depend on this truth to fix critical issues quickly.**

**The orphaned `domain_to_sitemap_adapter_service.py` has been removed. The scheduler now calls `SitemapAnalyzer` directly. Do not attempt to restore the adapter service - it will break the working implementation.**

**VECTORIZATION NOTICE:** This workflow analysis framework is available as `v_WORKFLOW_TRUTH_DOCUMENTATION_PROTOCOL.md` ⚡ in the vector database for semantic search.

**The fate of WF4 operations depends on the accuracy of this documentation. Keep it truthful.**