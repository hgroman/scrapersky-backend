# ScraperSky Glossary
**Purpose:** Define all terminology with code examples  
**Last Updated:** November 17, 2025

---

## Architecture Terms

### Dual-Status Pattern
**Definition:** Tables have two status fields - one for user curation decisions, one for system processing state.

**Fields:**
- **Curation Status:** User's decision (New, Selected, Rejected)
- **Processing Status:** System's state (Queued, Processing, Complete, Error)

**Rule:** When curation status → "Selected", processing status → "Queued"

**Examples:**
- `domains`: `sitemap_curation_status` + `sitemap_analysis_status`
- `pages`: `page_curation_status` + `page_processing_status`
- `sitemap_files`: ⚠️ Missing curation status (known gap)

**Code Example:**
```python
# From WF7_V3_L3_1of1_PagesRouter.py lines 145-148
if request.status == PageCurationStatus.Selected:
    page.page_processing_status = PageProcessingStatus.Queued
    page.page_processing_error = None
    queued_count += 1
```

**Why:** Separates user decisions from system state, allowing independent tracking

**Reference:** [WF4_WF5_WF7_DATABASE_SCHEMA.md](../Architecture/WF4_WF5_WF7_DATABASE_SCHEMA.md)

---

### Adapter Service
**Definition:** Service that bridges two workflows by translating data and status between them.

**Purpose:** Connect workflows that use different data models or status systems

**Example:** DomainToSitemapAdapterService
- **Input:** Domain record with `sitemap_analysis_status = 'queued'`
- **Output:** Job record + background task trigger
- **Bridges:** WF4 (Domain Curation) → WF5 (Sitemap Discovery)

**Code Location:** `src/services/domain_to_sitemap_adapter_service.py`

**Key Method:**
```python
async def submit_domain_to_legacy_sitemap(
    self,
    domain_id: UUID,
    session: AsyncSession
) -> bool
```

**Why:** Allows workflows to evolve independently while maintaining integration

**Critical Fix (Commit 9f091f6):** Added missing background task trigger

---

### Honeybee
**Definition:** URL categorization system that classifies pages by type and purpose.

**Purpose:** Automatically identify high-value pages (contact, careers, legal)

**Categories:**
- `CONTACT_ROOT` - Main contact page
- `CAREER_CONTACT` - Jobs/careers page
- `LEGAL_ROOT` - Legal/privacy pages
- `unknown` - Not categorized or low confidence
- [Many others]

**Output:**
- `category` - Page type
- `confidence` - 0.0 to 1.0
- `depth` - URL depth from root

**Used By:** SitemapImportService (WF5)

**Code Example:**
```python
# From sitemap_import_service.py
from honeybee import categorize_url

hb = categorize_url(url)
page_data["page_type"] = hb["category"]
page_data["priority_level"] = 3  # default low

# Auto-selection logic
if (
    hb["category"] in {PageTypeEnum.CONTACT_ROOT, PageTypeEnum.CAREER_CONTACT, PageTypeEnum.LEGAL_ROOT}
    and hb["confidence"] >= 0.6
    and hb["depth"] <= 2
):
    page_data["page_curation_status"] = PageCurationStatus.Selected
    page_data["page_processing_status"] = PageProcessingStatus.Queued
    page_data["priority_level"] = 1
```

**Why:** Automatically prioritizes pages likely to contain contact information

---

### Job vs Task vs Workflow
**Job:**
- Database record in `jobs` table
- Tracks background processing
- Has status: pending, running, complete, failed
- Example: Sitemap discovery job

**Task:**
- Async operation (Python asyncio)
- May or may not have database record
- Example: `asyncio.create_task(process_domain())`

**Workflow:**
- Complete business process (WF1-WF7)
- Spans multiple tables and services
- Example: WF4 (Domain Curation)

**Why Distinction Matters:**
- Jobs are persistent (database)
- Tasks are ephemeral (memory)
- Workflows are conceptual (business logic)

---

## Status Values

### Queued
**Meaning:** Item is ready for processing and waiting for scheduler to pick it up

**Used In:**
- `domains.sitemap_analysis_status = 'queued'`
- `sitemap_files.sitemap_import_status = 'Queued'` (note capitalization)
- `pages.page_processing_status = 'Queued'`

**Transition:**
- **From:** NULL or 'New' (when user selects)
- **To:** 'Processing' (when scheduler picks up)

**How Set:** Automatically when curation status → "Selected"

---

### Submitted
**Meaning:** Job has been created and submitted for processing

**Used In:**
- `domains.sitemap_analysis_status = 'submitted'`

**Transition:**
- **From:** 'queued' (when adapter service processes)
- **To:** (stays submitted - no further updates)

**Note:** This is a terminal state for domains. The job continues processing, but domain status doesn't update further.

---

### Processing
**Meaning:** Item is currently being processed by a service

**Used In:**
- `sitemap_files.sitemap_import_status = 'Processing'`
- `pages.page_processing_status = 'Processing'`

**Transition:**
- **From:** 'Queued' (when scheduler starts processing)
- **To:** 'Complete' or 'Error' (when processing finishes)

**Duration:** Varies by workflow (seconds to minutes)

---

### Complete
**Meaning:** Processing finished successfully (may or may not have found data)

**Used In:**
- `sitemap_files.sitemap_import_status = 'Complete'`
- `pages.page_processing_status = 'Complete'`

**Important:** "Complete" doesn't mean "found contacts" - it means "finished processing"

**Example:** Page with no contacts still gets status "Complete"

---

### Error / Failed
**Meaning:** Processing failed due to an error

**Used In:**
- `domains.sitemap_analysis_status = 'failed'`
- `sitemap_files.sitemap_import_status = 'Error'`
- `pages.page_processing_status = 'Error'`

**Accompanied By:** Error message in corresponding `*_error` field

**Requires:** Manual intervention or retry logic to reprocess

---

## Service Communication Patterns

### Direct Service Call (Correct)
**Definition:** Service A calls Service B's method directly

**Pattern:**
```python
service = SomeService()
result = await service.process(item_id, session)
```

**Benefits:**
- No network overhead
- No authentication needed
- Shares transaction context
- Can trigger background tasks

**Examples:**
- `deep_scan_scheduler.py` → `PlacesDeepService`
- `domain_sitemap_submission_scheduler.py` → `DomainToSitemapAdapterService`

**Reference:** [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md#service-communication-patterns)

---

### HTTP Call (Anti-Pattern)
**Definition:** Service A makes HTTP request to Service B's API endpoint

**Anti-Pattern:**
```python
# DON'T DO THIS
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v3/sitemap/scan",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
```

**Problems:**
- Network overhead
- Authentication complexity
- Can't share transaction
- **Doesn't trigger background tasks** (critical!)
- Multiple failure points

**Real Incident:** INCIDENT-2025-11-17-sitemap-jobs-not-processing  
**Fixed In:** Commit 1ffa371, then 9f091f6

**Why This Existed:** Legacy pattern before service layer was mature

---

### Background Task Trigger
**Definition:** Starting async processing without blocking the caller

**HTTP Endpoint Pattern:**
```python
# In FastAPI route
background_tasks.add_task(
    process_domain_with_own_session,
    job_id=job_id,
    domain=domain,
    user_id=user_id,
    max_urls=1000
)
```

**Direct Service Pattern:**
```python
# In service method
import asyncio
asyncio.create_task(
    process_domain_with_own_session(
        job_id=job_id,
        domain=domain,
        user_id=None,
        max_urls=1000
    )
)
```

**Critical:** If you create a job, you MUST trigger its processing

**Reference:** Commit 9f091f6 - Added missing trigger

---

## Database Terms

### Curation Status
**Definition:** User's decision about whether to process an item

**Values:** New, Selected, Rejected

**Fields:**
- `domains.sitemap_curation_status`
- `pages.page_curation_status`
- `sitemap_files.sitemap_curation_status` (⚠️ missing)

**Set By:** User via GUI or API

**Effect:** When set to "Selected", triggers processing status → "Queued"

---

### Processing Status
**Definition:** System's current state for processing an item

**Values:** NULL, Queued, Processing, Complete, Error/Failed

**Fields:**
- `domains.sitemap_analysis_status`
- `sitemap_files.sitemap_import_status`
- `pages.page_processing_status`

**Set By:** System (schedulers and services)

**Tracked:** Throughout processing lifecycle

---

### Auto-Selection Rules
**Definition:** Logic that automatically sets items to "Selected" based on criteria

**Used In:** SitemapImportService (WF5) when creating Page records

**Criteria:**
```python
if (
    page_type in {CONTACT_ROOT, CAREER_CONTACT, LEGAL_ROOT}
    and confidence >= 0.6
    and depth <= 2
):
    # Auto-select
    page_curation_status = Selected
    page_processing_status = Queued
    priority_level = 1
```

**Why:** Automatically prioritize high-value pages for contact extraction

**Code:** `src/services/sitemap_import_service.py` lines 223-229

---

## Scheduler Terms

### Scheduler
**Definition:** Background job that runs on an interval to process queued items

**Examples:**
- Domain Sitemap Submission Scheduler (1 minute)
- Sitemap Import Scheduler (configurable)
- Page Curation Scheduler (configurable)

**Pattern:** Uses SDK's `run_job_loop()` function

**Configuration:**
- Interval (minutes)
- Batch size
- Max instances

---

### SDK Job Loop
**Definition:** Standardized function for processing queued items

**Function:** `run_job_loop()` from `src.common.curation_sdk.scheduler_loop`

**Parameters:**
- `model` - Database model class
- `status_enum` - Status enumeration
- `queued_status` - Status value for queued items
- `processing_status` - Status value while processing
- `completed_status` - Status value when done
- `failed_status` - Status value on error
- `processing_function` - Service method to call
- `batch_size` - How many to process per run
- `order_by_column` - Sort order
- `status_field_name` - Name of status field
- `error_field_name` - Name of error field

**Why:** Ensures consistent error handling and status management

---

## Authentication Terms

### Service Role Key
**Definition:** Supabase admin key for internal service-to-service communication

**Variable:** `settings.supabase_service_role_key`

**Use Case:** Direct database access from services

**Security:** Never expose to frontend, only use server-side

**Note:** Case-sensitive! (lowercase, not uppercase)

---

### Dev Bypass Token
**Definition:** Development-only authentication token

**Variable:** `settings.DEV_TOKEN` (value: "scraper_sky_2024")

**Restriction:** Only works in development environment (WO-001/WO-002)

**Historical Issue:** Was used in production, caused authentication failures

**Fixed In:** Commits 8604a37, d9e4fc2, 1ffa371

---

### JWT Token
**Definition:** JSON Web Token for user authentication

**Use Case:** Frontend → Backend API calls

**Required By:** All `/api/v3/*` endpoints

**Not Used For:** Internal service-to-service calls

---

## External Service Terms

### ScraperAPI
**Definition:** External service for fetching web page HTML

**Used By:** PageCurationService (WF7)

**Cost:** 1 credit per page request

**Configuration:** `settings.scraper_api_key`

**Failure Mode:** Page marked as Error, no retry

**Reference:** [DEPENDENCY_MAP.md](./DEPENDENCY_MAP.md)

---

### Supabase
**Definition:** PostgreSQL database hosting and management

**Access Method:** MCP (Model Context Protocol) tools

**Tables:** All application tables

**Connection:** Via connection string in environment

---

### Render.com
**Definition:** Deployment platform for Docker containers

**Environment:** Production

**Access:** Web dashboard for logs and management

**Deployment:** Automatic on git push to main

---

## Workflow Terms

### WF1 through WF7
**Definition:** The 7 main business workflows

**WF1:** Single Search (Google Maps)
**WF2:** Deep Scan (enrichment)
**WF3:** Domain Extraction
**WF4:** Sitemap Discovery
**WF5:** Sitemap Import
**WF7:** Page Curation / Contact Extraction

**Note:** There is no WF6. The numbering skips from WF5 to WF7.

**Reference:** [QUICK_START.md](./QUICK_START.md)

---

## Common Abbreviations

- **MCP:** Model Context Protocol
- **SDK:** Software Development Kit (curation_sdk)
- **JSONB:** JSON Binary (PostgreSQL data type)
- **FK:** Foreign Key
- **PK:** Primary Key
- **UUID:** Universally Unique Identifier
- **API:** Application Programming Interface
- **HTTP:** Hypertext Transfer Protocol
- **SQL:** Structured Query Language
- **GUI:** Graphical User Interface

---

## Terminology Notes

### Case Sensitivity
Status values have inconsistent capitalization:
- `sitemap_import_status = 'Queued'` (capital Q)
- `sitemap_analysis_status = 'queued'` (lowercase q)

**Why:** Historical inconsistency, not yet standardized

**Impact:** Must use exact case in queries

---

### NULL vs "New"
Some status fields use NULL for initial state, others use "New":
- `sitemap_analysis_status = NULL` initially
- `page_curation_status = 'New'` initially

**Why:** Different workflows evolved separately

**Impact:** Check for both NULL and "New" in queries

---

**For more terminology, see specific documentation:**
- Database terms: [WF4_WF5_WF7_DATABASE_SCHEMA.md](../Architecture/WF4_WF5_WF7_DATABASE_SCHEMA.md)
- Service terms: [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md)
- Pattern terms: [PATTERNS.md](./PATTERNS.md)
