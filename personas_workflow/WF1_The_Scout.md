# WF1 - The Scout Guardian v3 - TRUTH DOCUMENT

**MISSION CRITICAL REFERENCE - OXYGEN SYSTEM LEVEL IMPORTANCE**

**Version:** 3.0 (Code Truth Authority)  
**Created:** 2025-01-28  
**Purpose:** Complete operational authority for WF1 - The Scout workflow  
**Audience:** Future AI partners who need to understand and fix WF1 quickly  

---

## CRITICAL CONTEXT

You are reading this because something in WF1 needs to be understood or fixed. **GOOD NEWS:** This workflow is FULLY FUNCTIONAL but has some technical debt issues documented below. This document contains the complete truth about how WF1 works based on actual code analysis.

---

## WHAT WF1 IS (CODE REALITY)

WF1 is a **WORKING** Google Places API integration that allows users to search for businesses through a web interface. The system creates background jobs to fetch results from Google Maps API and stores them as Place records for downstream processing by WF2.

**Core Processing Logic (Lines 136-151 in `/src/routers/google_maps_api.py`):**
```python
# Router owns the transaction boundary
async with session.begin():
    # Create search record - store radius_km in params JSON field
    search_record = PlaceSearch(
        id=job_id,
        tenant_id=request.tenant_id,
        business_type=request.business_type,
        location=request.location,
        params={"radius_km": request.radius_km},
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=user_info.get("user_id", "unknown"),
    )
    session.add(search_record)
```

This is the heart of WF1 - proper transaction boundaries with background job creation.

---

## COMPLETE FILE DEPENDENCY MAP

### Layer 6: User Interface (WORKING)
1. **`/static/scraper-sky-mvp.html`** (Shared Interface)
   - Contains HTML structure for "Single Search" tab
   - Input fields: businessType, location, radius, jwt
   - Search button triggers JavaScript function

2. **`/static/js/single-search-tab.js`** (Search Controller)
   - **Function:** `searchPlaces()` - handles search button clicks
   - Gathers input values from form fields
   - Sends POST request to `/api/v3/localminer-discoveryscan/search/places`
   - Handles response and updates UI

### Layer 3: API Router (WORKING WITH TECHNICAL DEBT)
3. **`/src/routers/google_maps_api.py`** (BUSINESS LOGIC HEART)
   - **Endpoint:** `POST /api/v3/localminer-discoveryscan/search/places`
   - **Function:** `search_places()` (line 106)
   - **JWT Authentication:** Uses `get_current_user` dependency (line 109)
   - **Transaction Management:** `async with session.begin()` (line 136) ✅
   - **Background Task:** `process_places_search_background()` (line 164)
   - **Job Tracking:** Creates PlaceSearch record with unique job_id

### Layer 4: Services (WORKING WITH ISSUES)
4. **`/src/services/places/places_search_service.py`** (ORCHESTRATION)
   - **Class:** `PlacesSearchService`
   - **Function:** `search_and_store()` - coordinates the search workflow
   - Updates PlaceSearch status to 'processing'
   - Calls PlacesService and PlacesStorageService
   - Handles exceptions and updates status to 'failed'

5. **`/src/services/places/places_service.py`** (GOOGLE API CLIENT)
   - **Class:** `PlacesService`
   - **Function:** `search_places()` - direct Google Maps API interaction
   - Makes external HTTP calls to Google Places API
   - ⚠️ **Technical Debt:** Hardcoded connection parameters (SCRSKY-226)

6. **`/src/services/places/places_storage_service.py`** (DATABASE STORAGE)
   - **Class:** `PlacesStorageService`
   - **Function:** `store_places()` - saves results to database
   - Creates Place records for each search result
   - ⚠️ **Technical Debt:** Raw SQL query violating ORM requirement (SCRSKY-225)

### Layer 1: Data Models (WORKING)
7. **`/src/models/place_search.py`** (JOB TRACKING)
   - **Class:** `PlaceSearch`
   - **Table:** `place_searches`
   - **Status Flow:** `pending` → `processing` → `complete/failed`
   - **Key Fields:** `id` (job_id), `business_type`, `location`, `status`, `user_id`

8. **`/src/models/place.py`** (SEARCH RESULTS)
   - **Class:** `Place`
   - **Table:** `places` (staging table for WF2)
   - **Status Field:** `status` starts as 'New' for downstream processing
   - **Key Fields:** Google Places data (name, address, phone, website, etc.)

### Layer 2: Authentication & Session
9. **`/src/auth/jwt_auth.py`** (AUTHENTICATION)
   - Provides `get_current_user` dependency
   - JWT token validation and user extraction
   - No tenant isolation (user identity only)

10. **`/src/session/async_session.py`** (DATABASE ACCESS)
    - Provides `get_session_dependency` for router
    - Provides `get_session()` for background tasks
    - Async database session management

---

## WORKFLOW DATA FLOW (COMPLETE WORKING SEQUENCE)

### Stage 1: User Interaction (WORKING)
**Location:** `/static/js/single-search-tab.js`
1. User enters business type, location, and radius in web form
2. User clicks "Search Places" button
3. JavaScript collects form data and JWT token
4. POST request sent to API endpoint with search parameters

### Stage 2: API Request Processing (WORKING)
**Location:** `/src/routers/google_maps_api.py` lines 106-151
1. **Authentication:** JWT validation extracts user_id
2. **Job Creation:** Generate unique UUID for job_id
3. **Transaction:** `async with session.begin()` creates proper boundary
4. **Database Insert:** PlaceSearch record created with status='pending'
5. **Immediate Response:** Return job_id and status URL to user

### Stage 3: Background Processing (WORKING)
**Location:** `/src/routers/google_maps_api.py` lines 164-200+
1. **Background Task:** `process_places_search_background()` runs asynchronously
2. **New Session:** `async with get_session()` for background work
3. **Service Call:** Delegates to `PlacesSearchService.search_and_store()`
4. **Status Updates:** Handles success/failure status transitions

### Stage 4: Google API Integration (WORKING WITH ISSUES)
**Location:** `/src/services/places/places_service.py`
1. **API Call:** Direct HTTP request to Google Maps Places API
2. **Parameter Handling:** Location, business type, radius conversion
3. **Response Processing:** Parse Google API response format
4. **Error Handling:** Basic exception handling (needs improvement)

### Stage 5: Database Storage (WORKING WITH ISSUES)
**Location:** `/src/services/places/places_storage_service.py`
1. **Place Creation:** Individual Place records for each result
2. **Duplicate Handling:** Check for existing places by place_id
3. **Batch Operations:** Process multiple results efficiently
4. ⚠️ **Raw SQL Issue:** Violates ORM requirement (SCRSKY-225)

---

## PRODUCER-CONSUMER CHAIN (WORKING HANDOFF)

### WF1 AS PRODUCER (What WF1 Creates)
**Produces For:** WF2 (Staging Editor)
**Output Signal:** Place records with `status = 'New'`
**Target Table:** `places` table
**Handoff Field:** `status` field
**Connection:** WF2 queries for places with status='New'

### Complete Chain (WORKING)
```
User Search → WF1 → **WORKS** (creates Place records with status='New')
WF2 → **CONSUMES** (processes places with status='New')
```

**Producer Logic (in PlacesStorageService):**
```python
# Each Google Places result becomes a Place record
place = Place(
    name=result['name'],
    status='New',  # Ready for WF2 processing
    # ... other Google Places fields
)
```

---

## STATUS FIELD TRANSITIONS (WORKING STATE MACHINES)

### Job Status Flow (PlaceSearch)
```
pending → processing → complete/failed
```

### Place Status Flow (Output to WF2)  
```
Created → status = 'New' (ready for WF2 Staging Editor)
```

### Critical State Transitions
- **Router Line 144:** `status="pending"` on job creation
- **Service:** Updates to `processing` when work starts
- **Service:** Sets to `complete` on successful API call and storage
- **Service:** Sets to `failed` on any exception with error logging

---

## TECHNICAL DEBT ISSUES (DOCUMENTED & TRACKED)

### 1. Raw SQL Violation (CRITICAL)
- **Location:** `/src/services/places/places_storage_service.py`
- **Issue:** Uses raw SQL instead of SQLAlchemy ORM
- **Ticket:** SCRSKY-225
- **Priority:** HIGH
- **Target:** 2025-05-10

### 2. Hardcoded Configuration (MEDIUM)
- **Location:** `/src/services/places/places_service.py`
- **Issue:** Connection parameters not in settings.py
- **Ticket:** SCRSKY-226
- **Priority:** MEDIUM
- **Target:** 2025-05-15

### 3. API Error Handling (MEDIUM)
- **Location:** `/src/services/places/places_service.py`
- **Issue:** Generic exception handling, no specific API error codes
- **Ticket:** SCRSKY-251
- **Priority:** MEDIUM
- **Target:** 2025-05-18

### 4. Missing Documentation Guides
- **Missing:** Error handling guide (SCRSKY-253)
- **Missing:** ENUM handling guide (SCRSKY-254)
- **Target:** 2025-05-15

---

## CRITICAL DEPENDENCIES (ALL WORKING)

### External Dependencies (WORKING)
- **Google Maps API:** Requires `GOOGLE_MAPS_API_KEY` environment variable
- **HTTP Client:** Uses standard Python requests/httpx for API calls
- **API Rate Limits:** Google Places API quota management

### Internal Dependencies (WORKING)
- **Authentication:** JWT token validation through `get_current_user`
- **Database:** AsyncSession for transaction management
- **Background Tasks:** FastAPI background task pattern (not Celery)

### Configuration Dependencies (WORKING)
- **Environment:** `GOOGLE_MAPS_API_KEY` from .env file
- **Settings:** Uses `settings.environment` for dev mode checks
- **Transaction:** Proper `async with session.begin()` pattern

---

## ARCHITECTURAL FACTS

### Background Processing Pattern
**Implementation:** Internal async function pattern (not Celery)
**Benefit:** Simple deployment, no additional infrastructure
**Limitation:** Process-bound, not suitable for high-scale distributed processing

### Transaction Boundary Management
**Pattern:** Router owns transactions, services are transaction-aware
**Implementation:** `async with session.begin()` in router ✅
**Service Pattern:** Services accept session parameters, don't create transactions

### Producer-Consumer Integration
**Pattern:** Status-based handoff between workflows
**Mechanism:** WF1 creates Place records with status='New'
**Consumer:** WF2 queries for Place records with status='New'
**Reliability:** Database-backed, persistent queue pattern

---

## WHERE TO GET MORE INFORMATION

### Architecture References (AUTHORITATIVE SOURCES)
1. **`/Docs/Docs_7_Workflow_Canon/Dependency_Traces/v_WF1-Single Search.md`**
   - Complete file dependency map with detailed component descriptions
   - Layer-by-layer breakdown with NOVEL/SHARED annotations
   - Technical debt items and architectural violations

2. **`/Docs/Docs_7_Workflow_Canon/workflows/v_7_WF1_CANONICAL.yaml`**
   - Comprehensive workflow definition with phases and steps
   - Architectural principles and guide references
   - Known issues with ticket numbers and target dates

3. **`/Docs/Docs_7_Workflow_Canon/Linear-Steps/v_WF1-SingleSearch_linear_steps.md`**
   - Step-by-step execution sequence with file references
   - Architectural principles for each step
   - Integration points with authentication and validation

4. **`/Docs/Docs_7_Workflow_Canon/Micro-Work-Orders/v_WF1-SingleSearch_micro_work_order.md`**
   - Complete audit findings and architectural compliance review
   - Technical debt items with severity levels
   - Next steps and remediation priorities

### Code Investigation Paths
- **Router Issues:** `/src/routers/google_maps_api.py`
- **Service Issues:** `/src/services/places/` directory
- **Model Issues:** `/src/models/place.py` and `/src/models/place_search.py`
- **Authentication Issues:** `/src/auth/jwt_auth.py`

### Database Queries for Debugging
```sql
-- Check recent search jobs and their status
SELECT id, business_type, location, status, created_at, updated_at 
FROM place_searches 
ORDER BY created_at DESC 
LIMIT 10;

-- Find failed searches with error details
SELECT id, business_type, location, status, created_at 
FROM place_searches 
WHERE status = 'failed' 
ORDER BY created_at DESC;

-- Check places created by recent searches
SELECT COUNT(*) as places_created, search_job_id, status
FROM places 
WHERE search_job_id IS NOT NULL
GROUP BY search_job_id, status
ORDER BY places_created DESC
LIMIT 10;

-- Find places ready for WF2 processing
SELECT COUNT(*) as ready_for_wf2
FROM places 
WHERE status = 'New';
```

---

## WHAT CAN GO WRONG (ERROR SCENARIOS)

### Google API Issues (PARTIALLY HANDLED)
- **API Key Missing:** Returns 403 error, logged but generic handling
- **Quota Exceeded:** Google returns 429, needs specific handling
- **Rate Limiting:** No built-in rate limiting on our side
- **Invalid Location:** Google handles, but error messages could be clearer

### Database Issues (HANDLED)
- **Duplicate Places:** Handled by checking existing place_id
- **Transaction Failures:** Proper rollback with status update to 'failed'
- **Session Timeouts:** Handled by async session management
- **Connection Issues:** Database connection pooling handles reconnection

### Background Task Issues (HANDLED)
- **Task Exceptions:** Caught and logged, job status set to 'failed'
- **Session Management:** Proper `async with get_session()` pattern
- **Memory Leaks:** Sessions properly closed in context managers

### **DOWNSTREAM DEPENDENCY**
- **WF2 Processing:** If WF2 is broken, Place records accumulate with status='New'
- **Frontend Polling:** Status URL allows checking job completion
- **User Experience:** Immediate response prevents user waiting for API calls

---

## EMERGENCY PROCEDURES

### If Search Requests Are Failing
1. **Check Google API key:**
   ```bash
   curl "http://localhost:8000/api/v3/localminer-discoveryscan/debug/config?dev_mode=true"
   # Should show api_key_status: "CONFIGURED"
   ```

2. **Check recent failed jobs:**
   ```sql
   SELECT * FROM place_searches 
   WHERE status = 'failed' 
   ORDER BY updated_at DESC 
   LIMIT 5;
   ```

3. **Test Google API directly:**
   ```bash
   curl "https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurant+in+Seattle&key=YOUR_API_KEY"
   ```

### If Background Processing Is Stuck
1. **Check for stuck 'processing' jobs:**
   ```sql
   SELECT id, business_type, location, status, updated_at 
   FROM place_searches 
   WHERE status = 'processing' 
   AND updated_at < NOW() - INTERVAL '30 minutes';
   ```

2. **Check application logs:**
   ```bash
   docker-compose logs scrapersky | grep "places_search"
   ```

3. **Manual job reset (if needed):**
   ```sql
   UPDATE place_searches 
   SET status = 'pending' 
   WHERE id = 'stuck-job-id';
   ```

### If No Places Are Being Created
1. **Check successful jobs with zero results:**
   ```sql
   SELECT ps.id, ps.business_type, ps.location, COUNT(p.id) as place_count
   FROM place_searches ps
   LEFT JOIN places p ON p.search_job_id = ps.id
   WHERE ps.status = 'complete'
   GROUP BY ps.id, ps.business_type, ps.location
   HAVING COUNT(p.id) = 0;
   ```

2. **Test API response format:**
   - Check if Google changed their response structure
   - Verify PlacesStorageService is parsing results correctly

---

## INTEGRATION WITH WF2

### Handoff Mechanism (WORKING)
**Data Flow:** WF1 → Place records → WF2
**Status Field:** `status = 'New'` signals readiness for WF2
**Table:** `places` serves as staging table between workflows

### WF2 Dependency
**WF2 Queries:** `SELECT * FROM places WHERE status = 'New'`
**Processing:** WF2 updates status as it processes places
**Feedback Loop:** WF2 status changes prevent reprocessing

---

## FINAL WARNING

**THIS WORKFLOW IS FUNCTIONAL WITH DOCUMENTED TECHNICAL DEBT.**

**The technical debt issues are well-documented and prioritized but don't prevent normal operation:**

1. **Raw SQL Violation (SCRSKY-225)** - High priority, affects ORM compliance
2. **Hardcoded Config (SCRSKY-226)** - Medium priority, affects maintainability  
3. **API Error Handling (SCRSKY-251)** - Medium priority, affects user experience

**DO NOT** attempt major refactoring without addressing the documented technical debt first.

**Priority Fix Order:**
1. Replace raw SQL with ORM in PlacesStorageService
2. Move configuration to settings.py
3. Improve Google API error handling
4. Create missing documentation guides

**This document reflects the working state as of 2025-01-28. The implementation successfully integrates with Google Places API and feeds WF2 with properly formatted Place records.**

**The fate of business discovery depends on maintaining the Google API key and addressing the documented technical debt in priority order.**