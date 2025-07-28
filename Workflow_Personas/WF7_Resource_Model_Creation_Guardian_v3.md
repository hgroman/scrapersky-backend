# WF7 Resource Model Creation Guardian v3 - TRUTH DOCUMENT

**MISSION CRITICAL REFERENCE - UNIMPLEMENTED STATE AUTHORITY**

**Version:** 3.0 (Code Truth Authority)  
**Created:** 2025-01-28  
**Purpose:** Complete operational authority for WF7 Resource Model Creation workflow  
**Audience:** Future AI partners who need to understand WF7's unimplemented state  

---

## ⚠️ CRITICAL CONTEXT

You are reading this because someone asked about WF7. **HARD TRUTH:** This workflow is **COMPLETELY UNIMPLEMENTED**. This document serves as the definitive record of what WF7 was intended to do and what would need to be built to make it functional.

---

## WHAT WF7 IS (CURRENT REALITY)

WF7 is an **UNIMPLEMENTED** workflow concept that was intended to process Page records and extract resource information (contacts, business data, etc.) from webpage content. The workflow exists only as:

1. **Database Model:** Complete Page model with status fields ✅
2. **Documentation Fragments:** Partial audit documents ⚠️
3. **Implementation:** **NONE** ❌

**Key Missing Components:**
- `/src/services/page_curation_service.py` - **DOES NOT EXIST**
- `/src/services/page_curation_scheduler.py` - **DOES NOT EXIST**
- Router endpoints - **NOT IMPLEMENTED**
- Business logic - **NOT IMPLEMENTED**

---

## WHAT WF7 WAS INTENDED TO DO (BASED ON AVAILABLE EVIDENCE)

### Intended Data Model (EXISTS)
**Location:** `/src/models/page.py` lines 103-116

```python
# --- Page Curation Workflow Columns ---
page_curation_status: Column[PageCurationStatus] = Column(
    PgEnum(PageCurationStatus, name="page_curation_status", create_type=False),
    nullable=False,
    default=PageCurationStatus.New,
    index=True,
)
page_processing_status: Column[Optional[PageProcessingStatus]] = Column(
    PgEnum(PageProcessingStatus, name="page_processing_status", create_type=False),
    nullable=True,
    index=True,
)
page_processing_error: Column[Optional[str]] = Column(Text, nullable=True)
```

### Intended Workflow Pattern (INFERRED)
Based on ScraperSky architectural patterns, WF7 would have followed this structure:

1. **Input:** Page records with `page_curation_status = 'New'` (from WF6)
2. **Processing:** Extract business information from webpage content
3. **Output:** Create Contact records and update page status
4. **Background:** Scheduled processing similar to other workflows

---

## INTENDED ARCHITECTURE (BASED ON SCRAPERSKY PATTERNS)

### Missing Layer 3: Router (UNIMPLEMENTED)
**Would be:** `/src/routers/pages.py` or similar
**Purpose:** Manual curation endpoints for page selection
**Pattern:** Dual-status update (select pages → queue for processing)

### Missing Layer 4: Service (UNIMPLEMENTED)
**Would be:** `/src/services/page_curation_service.py`
**Purpose:** Extract contacts and business data from webpage content
**Functions:** 
- `process_single_page_for_page_curation(page_id, session)`
- HTTP fetching of page content
- HTML parsing and data extraction
- Contact record creation

### Missing Layer 4: Scheduler (UNIMPLEMENTED)
**Would be:** `/src/services/page_curation_scheduler.py`
**Purpose:** Background processing of queued pages
**Pattern:** Use `run_job_loop()` from curation SDK
**Query:** `page_processing_status = 'Queued'`

---

## EXISTING FOUNDATION (WHAT'S ALREADY BUILT)

### Layer 1: Data Models (COMPLETE)
1. **`/src/models/page.py`** - Page model with workflow fields ✅
   - Complete page data structure
   - Status fields for workflow management
   - Relationships to Domain and Contact models

2. **`/src/models/contact.py`** - Contact model (assumed to exist)
   - Would store extracted business contact information
   - Linked to pages via relationships

### Layer 1: Status Enums (COMPLETE)
**Location:** `/src/models/enums.py` (assumed)
- `PageCurationStatus` - workflow selection states
- `PageProcessingStatus` - background processing states

### Layer 6: UI Components (PARTIAL)
**Location:** `/static/js/page-curation-tab.js` (referenced in audit docs)
- Frontend interface for manual page curation
- Would connect to unimplemented router endpoints

---

## PRODUCER-CONSUMER CHAIN (BROKEN LINK)

### WF7 AS CONSUMER (What Should Trigger WF7)
**Should Consume From:** WF6 (Sitemap Import) ✅ WORKING
**Input Signal:** Page records with `page_curation_status = 'New'`
**Source Table:** `pages` table
**Current Status:** WF6 creates pages but nothing processes them

### WF7 AS PRODUCER (What WF7 Should Create)
**Should Produce For:** Contact management systems
**Output Signal:** Contact records with extracted business data
**Target Table:** `contacts` table
**Current Status:** No contacts being extracted from pages

### Complete Chain (COMPLETELY BROKEN)
```
WF6 → **WORKS** (creates Page records)
WF7 → **MISSING** (should extract contacts from pages)
Contact System → **STARVED** (no contact data being generated)
```

---

## IMPLEMENTATION REQUIREMENTS (WHAT NEEDS TO BE BUILT)

### Phase 1: Core Service Implementation
1. **Create `/src/services/page_curation_service.py`**
   - `process_single_page_for_page_curation()` function
   - HTTP client for fetching page content
   - HTML parsing logic (BeautifulSoup or similar)
   - Contact extraction algorithms
   - Database transaction management

2. **Create `/src/services/page_curation_scheduler.py`**
   - Use standardized `run_job_loop()` pattern
   - Query for `page_processing_status = 'Queued'`
   - Proper session management with `get_background_session()`
   - Error handling and status updates

### Phase 2: Router Implementation
3. **Create `/src/routers/pages.py`**
   - Page listing endpoints with filtering
   - Manual page selection endpoints
   - Dual-status update pattern implementation
   - Integration with frontend JavaScript

### Phase 3: System Integration
4. **Update `/src/main.py`**
   - Register page curation scheduler
   - Add to application startup lifecycle

5. **Update `/src/config/settings.py`**
   - Add scheduler configuration settings
   - HTTP timeout and retry settings
   - Batch size configuration

---

## ARCHITECTURAL PATTERNS TO FOLLOW

### Dual-Status Pattern (REQUIRED)
Following WF4 model from `domains.py:229-236`:
```python
if page_curation_status == PageCurationStatusEnum.Selected:
    page.page_processing_status = PageProcessingStatusEnum.Queued
    page.page_processing_error = None
    queued_count += 1
```

### Background Processing Pattern (REQUIRED)
Following WF6 model from `sitemap_import_scheduler.py:29-44`:
```python
await run_job_loop(
    model=Page,
    status_enum=PageProcessingStatusEnum,
    queued_status=PageProcessingStatusEnum.Queued,
    processing_status=PageProcessingStatusEnum.Processing,
    completed_status=PageProcessingStatusEnum.Complete,
    failed_status=PageProcessingStatusEnum.Error,
    processing_function=service.process_single_page_for_page_curation,
    batch_size=settings.PAGE_CURATION_SCHEDULER_BATCH_SIZE,
    order_by_column=asc(Page.updated_at),
    status_field_name="page_processing_status",
    error_field_name="page_processing_error",
)
```

---

## DATABASE IMPACT ANALYSIS

### Current State
```sql
-- Pages created by WF6 but never processed
SELECT COUNT(*) FROM pages WHERE page_curation_status = 'New';

-- Should show many unprocessed pages
```

### Expected State After Implementation
```sql
-- Pages in various processing states
SELECT page_curation_status, COUNT(*) 
FROM pages 
GROUP BY page_curation_status;

-- Contacts extracted from processed pages
SELECT COUNT(*) FROM contacts WHERE page_id IS NOT NULL;
```

---

## RISK ASSESSMENT

### Business Impact
- **Critical Gap:** No contact extraction happening from discovered pages
- **Data Waste:** Page URLs discovered but business value not extracted
- **Pipeline Break:** Workflow chain stops at WF6, never reaching final value

### Technical Debt
- **Architecture Violation:** Missing Layer 4 components
- **Pattern Inconsistency:** Only workflow without service/scheduler pair
- **Integration Gaps:** Frontend components reference non-existent backend

### Operational Risk
- **No Monitoring:** Cannot monitor progress of non-existent workflow
- **No Error Handling:** No status tracking for processing failures
- **No Recovery:** No way to retry failed contact extractions

---

## IMPLEMENTATION PRIORITY

### Phase 1 (Critical - Foundation)
1. Create basic service with HTML fetching
2. Create scheduler with standard polling pattern
3. Implement dual-status update in router
4. Basic contact extraction (name, email, phone)

### Phase 2 (Enhancement)
1. Advanced contact extraction algorithms
2. Business information extraction
3. Data quality validation
4. Performance optimization

### Phase 3 (Integration)
1. Contact deduplication logic
2. CRM system integration
3. Advanced filtering and curation
4. Analytics and reporting

---

## COMPARISON WITH OTHER WORKFLOWS

### WF4 (Domain Curation) - WORKING ✅
- Complete router with dual-status pattern
- Background scheduler processing
- Clear producer-consumer chain
- **LESSON:** Use as implementation template

### WF5 (Sitemap Curation) - BROKEN ❌
- Missing scheduler query logic
- Service exists but never called
- **LESSON:** Avoid broken scheduler patterns

### WF6 (Sitemap Import) - WORKING ✅
- Perfect implementation of background processing
- Uses curation SDK correctly
- Comprehensive error handling
- **LESSON:** Follow this exact pattern

---

## IMPLEMENTATION SPECIFICATION

When implementing WF7, follow these exact patterns:

### Service Function Signature
```python
async def process_single_page_for_page_curation(
    page_id: uuid.UUID, 
    session: AsyncSession
) -> bool:
    """
    Process a single page for contact extraction.
    Returns True on success, False on failure.
    """
```

### Scheduler Registration
```python
def setup_page_curation_scheduler():
    """Set up the page curation background scheduler."""
    scheduler.add_job(
        process_page_curation_queue,
        "interval",
        minutes=settings.PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES,
        id="page_curation_processor",
        max_instances=settings.PAGE_CURATION_SCHEDULER_MAX_INSTANCES,
    )
```

### Router Status Update
```python
@router.put("/pages/{page_id}/curate")
async def curate_page(
    page_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Select page for contact extraction processing."""
    page = await session.get(Page, page_id)
    if page.page_curation_status == PageCurationStatusEnum.Selected:
        page.page_processing_status = PageProcessingStatusEnum.Queued
        page.page_processing_error = None
    await session.commit()
```

---

## WHERE TO GET MORE INFORMATION

### Architecture References (FOR IMPLEMENTATION)
1. **WF4 Implementation:** `/src/routers/domains.py` and `/src/services/domain_curation_service.py`
   - Perfect example of dual-status pattern
   - Router transaction management
   - Service architecture

2. **WF6 Implementation:** `/src/services/sitemap_import_scheduler.py` and service
   - Perfect background processing pattern
   - Curation SDK usage
   - Error handling and status management

3. **Page Model:** `/src/models/page.py`
   - Complete data structure available
   - Status fields properly defined
   - Relationships ready for contact extraction

### Documentation Gaps (MISSING)
- **Dependency Trace:** Only empty file exists
- **Linear Steps:** Not created
- **Canonical YAML:** Not created
- **Micro Work Order:** Not created

**ALL DOCUMENTATION WOULD NEED TO BE CREATED AFTER IMPLEMENTATION**

---

## EMERGENCY PROCEDURES

### If Someone Asks "Why Isn't WF7 Working?"
**Answer:** "WF7 doesn't exist. It was never implemented. Only the database model exists."

### If Someone Wants to Implement WF7
1. **Reference this document** for complete requirements
2. **Follow WF6 patterns** for background processing
3. **Follow WF4 patterns** for router implementation
4. **Create canonical documentation** after implementation
5. **Test with WF6 output** (Page records exist and ready)

### If Someone Sees WF7 in Documentation
**Explanation:** Documentation references are either:
- Planning documents for future implementation
- Architectural audit documents describing missing components
- Template documents showing what should exist

**Reality:** The implementation files do not exist in the codebase.

---

## FINAL VERDICT

**WF7 "Resource Model Creation" is a completely unimplemented workflow concept.**

**Database Foundation:** Ready ✅  
**Service Layer:** Missing ❌  
**Scheduler:** Missing ❌  
**Router:** Missing ❌  
**Documentation:** Incomplete ❌  

**IMPLEMENTATION STATUS:** 0% complete

**BUSINESS IMPACT:** High - No contact extraction from discovered pages

**RECOMMENDED ACTION:** Either implement following this specification or formally declare WF7 out of scope for current system.

**This document serves as the complete specification for implementing WF7 if the business decides to proceed with contact extraction functionality.**

**Until implementation occurs, WF7 remains a gap in the ScraperSky workflow pipeline, preventing the extraction of business value from discovered page content.**