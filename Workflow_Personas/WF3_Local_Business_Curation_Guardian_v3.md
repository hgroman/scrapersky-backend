# WF3 Local Business Curation Guardian v3 - TRUTH DOCUMENT

**MISSION CRITICAL REFERENCE - OXYGEN SYSTEM LEVEL IMPORTANCE**

**Version:** 3.0 (Code Truth Authority)  
**Created:** 2025-01-28  
**Purpose:** Complete operational authority for WF3 Local Business Curation workflow  
**Audience:** Future AI partners who need to understand and fix WF3 quickly  

---

## CRITICAL CONTEXT

You are reading this because something in WF3 needs to be fixed. This document contains the complete truth about how WF3 works based on actual code analysis. Every statement is traceable to specific code lines. No embellishments. No assumptions. Only facts.

---

## WHAT WF3 IS (CODE REALITY)

WF3 is a dual-status automation system that transforms user local business selections into queued domain extraction jobs. When users mark local businesses as "Selected", the system automatically queues them for domain extraction processing.

**Core Business Logic (Lines 273-282 in `/src/routers/local_businesses.py`):**
```python
# Conditional logic for domain extraction queueing
if trigger_domain_extraction:
    # Check eligibility (only queue if not already completed/processing etc.)
    current_extraction_status = business.domain_extraction_status
    # REMOVED eligibility check: current_extraction_status in eligible_queueing_statuses:
    # if current_extraction_status in eligible_queueing_statuses:
    business.domain_extraction_status = (
        DomainExtractionStatusEnum.Queued
    )  # type: ignore # Changed from 'queued' to 'Queued' to match new enum
    business.domain_extraction_error = None  # type: ignore # Clear any previous error
    actually_queued_count += 1
```

This is the heart of WF3. Everything else is infrastructure to support this transformation.

---

## COMPLETE FILE DEPENDENCY MAP

### Layer 6: User Interface
1. **`/static/scraper-sky-mvp.html`** (Local Business Curation tab)
   - Contains HTML structure for Local Business Curation tab
   - Table with checkboxes and status dropdown (`localBusinessBatchStatusUpdate`)
   - Update button (`applyLocalBusinessBatchUpdate`)

2. **`/static/js/local-business-curation-tab.js`** 
   - Handles user interactions within the Local Business Curation tab
   - Function: `applyLocalBusinessBatchUpdate()` 
   - Sends PUT requests to `/api/v3/local-businesses/status`
   - Collects selected IDs and target status from UI

### Layer 3: API Router
3. **`/src/routers/local_businesses.py`** (PRIMARY BUSINESS LOGIC)
   - **Line 181:** `@router.put("/status", status_code=status.HTTP_200_OK)`
   - **Line 182:** `async def update_local_businesses_status_batch()`
   - **Line 227:** `trigger_domain_extraction = target_db_status_member == PlaceStatusEnum.Selected`
   - **Lines 273-282:** Dual-status update logic (THE CRITICAL CODE)
   - **Line 289:** Transaction commit within `session.begin()` context

### Layer 4: Background Services
4. **`/src/services/sitemap_scheduler.py`** (PROCESSING ENGINE)
   - Contains scheduled job `process_pending_jobs()`
   - **Query logic:** Selects LocalBusiness records where `domain_extraction_status == DomainExtractionStatusEnum.Queued`
   - **Processing:** Calls `LocalBusinessToDomainService.create_pending_domain_from_local_business()`
   - **Polling:** Runs periodically based on `SITEMAP_SCHEDULER_INTERVAL_MINUTES`

5. **`/src/services/business_to_domain_service.py`** (ACTUAL WORK ENGINE)
   - Contains `LocalBusinessToDomainService` class
   - Function: `create_pending_domain_from_local_business(local_business_id: UUID, session: AsyncSession)` (line 27)
   - Extracts/validates website URL from LocalBusiness (lines 58-96)
   - Creates Domain records with `status="pending"` (line 114)
   - Links domain to local_business_id (line 115)

### Layer 5: Configuration & Infrastructure
6. **`/src/scheduler_instance.py`**
   - Provides shared AsyncIOScheduler instance
   - Used by sitemap_scheduler for background processing

7. **`/src/main.py`**
   - Application startup
   - Calls `setup_sitemap_scheduler()` on startup

### Layer 1: Data Models
8. **`/src/models/local_business.py`** (DATA AUTHORITY)
   - `LocalBusiness` SQLAlchemy model class
   - **Status field:** Uses `PlaceStatusEnum` from `src/models/place.py`
   - **Domain extraction field:** `domain_extraction_status` using `DomainExtractionStatusEnum`
   - **Key values:** `Queued`, `Processing`, `Completed`, `Error`

9. **`/src/models/domain.py`**
   - Contains `Domain` model
   - Fields created/updated by business_to_domain_service
   - Receives `sitemap_curation_status` for WF4 handoff

### Layer 2: Database Session
10. **`/src/db/session.py`**
    - Provides `get_db_session()` for API routes
    - Provides `get_background_session()` for scheduler

---

## WORKFLOW DATA FLOW (EXACT EXECUTION SEQUENCE)

### Stage 1: User Trigger
**Location:** Browser → `/static/scraper-sky-mvp.html`
1. User selects local business checkboxes in curation tab
2. User sets dropdown to "Selected"
3. User clicks "Update X Selected" button
4. JavaScript (`local-business-curation-tab.js`) sends PUT request to `/api/v3/local-businesses/status`

### Stage 2: API Processing
**Location:** `/src/routers/local_businesses.py` lines 182-299
1. Router receives `LocalBusinessBatchStatusUpdateRequest`
2. Maps API enum to DB enum `PlaceStatusEnum` (lines 210-213)
3. Sets trigger flag: `trigger_domain_extraction = target_db_status_member == PlaceStatusEnum.Selected` (line 227)
4. Fetches LocalBusiness objects by ID (lines 247-251)
5. **CRITICAL:** Executes dual-status update (lines 267-282)
6. Commits transaction (line 289)
7. Returns `{"updated_count": int, "queued_count": int}`

### Stage 3: Background Processing
**Location:** `/src/services/sitemap_scheduler.py`
1. **Periodic polling:** Scheduler runs based on `SITEMAP_SCHEDULER_INTERVAL_MINUTES`
2. **Query:** Selects LocalBusiness where `domain_extraction_status = "Queued"`
3. **Batch processing:** Processes up to `limit` businesses per cycle
4. **Service call:** Instantiates `LocalBusinessToDomainService` and calls `create_pending_domain_from_local_business()`
5. **Status updates:** Updates `domain_extraction_status` based on results

### Stage 4: Actual Work
**Location:** `/src/services/business_to_domain_service.py`
1. `create_pending_domain_from_local_business(local_business_id, session)` executes (line 27)
2. Fetches LocalBusiness record and extracts website URL (lines 48-65)
3. Validates and standardizes URL to domain format (lines 67-96)
4. Creates Domain record with `status="pending"` (line 114)
5. Links domain to local_business_id (line 115)
6. Returns boolean success/failure status

---

## PRODUCER-CONSUMER CHAIN (ECOSYSTEM POSITION)

### WF3 AS CONSUMER (What Triggers WF3)
**Consumes From:** WF2 (Staging Editor)
**Input Signal:** LocalBusiness records with various statuses
**Source Table:** `local_businesses` table
**Trigger:** User action in Local Business Curation UI

### WF3 AS PRODUCER (What WF3 Creates)
**Produces For:** WF4 (Domain Curation)  
**Output Signal:** Domain records with `status = 'pending'`
**Target Table:** `domains` table
**Consumer:** WF4 Domain Curation workflow

### Complete Chain
```
WF2 → local_businesses.status = various values
WF3 → User selection → domain_extraction_status = 'Queued' → Domain creation
WF4 → Consumes domains with status = 'pending'
```

---

## STATUS FIELD TRANSITIONS (DATA STATE MACHINE)

### Business Curation Status Flow
```
Any Status → User selects → 'Selected' → (triggers domain extraction queueing)
```

### Domain Extraction Status Flow  
```
null → 'Queued' → 'Processing' → 'Completed'/'Error'
```

### Critical State Transitions (Line References)
- **Router Line 268:** `business.status = target_db_status_member`
- **Router Line 278:** `business.domain_extraction_status = DomainExtractionStatusEnum.Queued`
- **Router Line 281:** `business.domain_extraction_error = None`
- **Scheduler:** Updates status to `Processing` during execution
- **Service:** Updates status to `Completed` or `Error` based on outcome

---

## CRITICAL DEPENDENCIES (FAILURE POINTS)

### Database Dependencies
- **Primary Table:** `local_businesses` with dual status fields
- **Target Table:** `domains` for created records
- **Session Management:** Both sync (API) and async (background) sessions
- **Transaction Boundaries:** Router owns API transactions, scheduler manages background transactions

### Service Dependencies  
- **APScheduler:** Must be running for background processing
- **LocalBusinessToDomainService:** Must be available for actual domain extraction
- **HTTP Frontend:** Must send correct API payloads

### Configuration Dependencies
- **Scheduler Interval:** Polling frequency via `SITEMAP_SCHEDULER_INTERVAL_MINUTES`
- **Batch Size:** Processing limit via `SITEMAP_SCHEDULER_BATCH_SIZE`
- **Database Connection:** Both API and background sessions must work

---

## KNOWN ARCHITECTURAL FACTS

### The Dual-Status Pattern
**Purpose:** User curation decisions automatically trigger background processing
**Implementation:** Single API call updates two different status fields
**Business Value:** Manual business selection becomes automated domain extraction pipeline

### Background Processing Model
**Pattern:** Poll-based scheduler with direct service calls
**Frequency:** Configurable via environment variables
**Isolation:** Each business processed in separate transaction
**Error Handling:** Per-business error tracking with status updates

### Eligibility Check Removal
**Current State:** Lines 276-277 show commented out eligibility check
**Implication:** ALL selections trigger domain extraction, regardless of previous status
**Risk:** May override previous extraction states without validation

---

## WHERE TO GET MORE INFORMATION

### Architecture References (AUTHORITATIVE SOURCES)
1. **`/Docs/Docs_7_Workflow_Canon/Dependency_Traces/WF3-Local Business Curation.md`**
   - Complete file dependency map with layer organization
   - Producer-consumer relationships
   - NOVEL vs SHARED file annotations

2. **`/Docs/Docs_7_Workflow_Canon/workflows/v_9_WF3_CANONICAL.yaml`**
   - Business workflow definition
   - Compliance verification requirements
   - Cross-workflow connections

3. **`/Docs/Docs_7_Workflow_Canon/Linear-Steps/WF3-LocalBusiness_linear_steps.md`**
   - 6-step atomic workflow execution
   - File annotations and principles
   - Audit/compliance checklist

### Code Investigation Paths
- **API Issues:** Start with `/src/routers/local_businesses.py` lines 182-299
- **Background Issues:** Check `/src/services/sitemap_scheduler.py` processing logic
- **Data Issues:** Examine `/src/models/local_business.py` enum definitions
- **UI Issues:** Debug `/static/js/local-business-curation-tab.js` API calls

### Database Queries for Debugging
```sql
-- Check local business status distribution
SELECT status, domain_extraction_status, COUNT(*) 
FROM local_businesses 
GROUP BY status, domain_extraction_status;

-- Find stuck businesses
SELECT id, website_url, domain_extraction_status, updated_at 
FROM local_businesses 
WHERE domain_extraction_status = 'Processing' 
AND updated_at < NOW() - INTERVAL '10 minutes';

-- Check queue depth
SELECT COUNT(*) FROM local_businesses WHERE domain_extraction_status = 'Queued';
```

---

## WHAT CAN GO WRONG (ERROR SCENARIOS)

### Dual-Status Update Failures
- **Router transaction rollback:** Both status fields revert
- **Enum validation errors:** Invalid status values rejected
- **Concurrent updates:** Multiple users updating same businesses

### Background Processing Failures  
- **Scheduler not running:** Businesses stuck in 'Queued' status
- **LocalBusinessToDomainService errors:** Businesses marked as 'Error'
- **Database connection issues:** Processing halts entirely

### Domain Extraction Service Failures
- **Invalid website URLs:** Service cannot extract valid domains
- **Domain creation conflicts:** Duplicate domain handling
- **External service timeouts:** Processing failures

### UI/API Disconnect
- **Frontend sends wrong payload:** API returns 400 errors
- **Authentication failures:** 401/403 responses
- **Network timeouts:** User sees failed updates

---

## EMERGENCY PROCEDURES

### If Businesses Are Stuck in 'Queued' Status
1. Check if scheduler is running: `docker-compose logs scrapersky | grep sitemap_scheduler`
2. Verify LocalBusinessToDomainService is working: Test direct function call
3. Check database connections: Verify background session works
4. Review recent error logs for processing failures

### If Dual-Status Update Fails
1. Check router logs for transaction errors
2. Verify enum values match between API and database
3. Test API endpoint directly with curl
4. Validate LocalBusinessBatchStatusUpdateRequest schema

### If Domain Creation Fails
1. Check business_to_domain_service logs for URL validation errors
2. Verify Domain model constraints and indexes
3. Test domain extraction logic with sample data
4. Check for database constraint violations

### If UI Shows Wrong Status
1. Check browser network tab for API call results
2. Verify JavaScript is sending correct payloads
3. Test API endpoint returns expected data
4. Validate enum mappings between API and UI

---

## FINAL WARNING

**This document reflects the actual running code as of 2025-01-28. If you change the implementation, UPDATE THIS DOCUMENT. Future AI partners depend on this truth to fix critical issues quickly.**

**The commented eligibility check (lines 276-277) means ALL selections trigger domain extraction. This may be intentional but should be verified against business requirements.**

**CRITICAL NOTE:** The sitemap_scheduler.py handles multiple workflow types. Changes to scheduler configuration affect both WF3 and WF4 processing.

**The fate of WF3 operations depends on the accuracy of this documentation. Keep it truthful.**