# WF4→WF5→WF7 Service Layer Architecture
**Part of:** Complete Pipeline Documentation  
**Last Updated:** November 17, 2025

---

## Service Overview

| Service | File | Purpose | Workflow |
|---------|------|---------|----------|
| DomainToSitemapAdapterService | `domain_to_sitemap_adapter_service.py` | Bridge domain curation to sitemap jobs | WF4 |
| SitemapProcessingService | `sitemap/processing_service.py` | Discover sitemap URLs | WF4→WF5 |
| SitemapImportService | `sitemap_import_service.py` | Extract URLs from sitemaps | WF5 |
| PageCurationService | `WF7_V2_L4_1of2_PageCurationService.py` | Scrape pages, extract contacts | WF7 |
| JobService | `job_service.py` | Manage job records | All |

---

## WF4 Services

### DomainToSitemapAdapterService

**File:** `src/services/domain_to_sitemap_adapter_service.py`

**Purpose:** Adapter between Domain Curation workflow and Sitemap Job system

#### Key Method: `submit_domain_to_legacy_sitemap()`

```python
async def submit_domain_to_legacy_sitemap(
    self,
    domain_id: UUID,
    session: AsyncSession
) -> bool
```

**Parameters:**
- `domain_id`: UUID of domain record to process
- `session`: Database session (transaction managed by caller)

**Returns:**
- `True` if job created successfully
- `False` if domain not found or job creation failed

**Process Flow:**
1. Fetch Domain record by ID
2. Validate domain has a domain name
3. Generate new job_id (UUID)
4. Create job_data dictionary
5. Call `job_service.create()` to persist job
6. Initialize job in `_job_statuses` (in-memory state)
7. Trigger `asyncio.create_task(process_domain_with_own_session())`
8. Update Domain.sitemap_analysis_status to 'submitted'
9. Return success/failure

**Critical Fix (Commit 9f091f6 - Nov 17, 2025):**

**BEFORE (Broken):**
```python
# Only created job record, didn't trigger processing
job = await job_service.create(session, job_data)
domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.submitted
return True
```

**AFTER (Fixed):**
```python
# Create job record
job = await job_service.create(session, job_data)

# Initialize in-memory state (required for status tracking)
from src.services.sitemap.processing_service import _job_statuses
_job_statuses[job_id] = {
    "status": "pending",
    "created_at": datetime.utcnow().isoformat(),
    "domain": domain.domain,
    "progress": 0.0,
    "metadata": {"sitemaps": []},
}

# Trigger background processing (THIS WAS MISSING)
import asyncio
from src.services.sitemap.processing_service import process_domain_with_own_session

asyncio.create_task(
    process_domain_with_own_session(
        job_id=job_id,
        domain=domain.domain,
        user_id=None,  # System-initiated
        max_urls=1000,
    )
)

domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.submitted
return True
```

**Why This Matters:**
- HTTP endpoint uses `BackgroundTasks.add_task()` to trigger processing
- Direct service call must use `asyncio.create_task()` to achieve same effect
- Without this, jobs sit in "pending" state forever (silent failure)

**Dependencies:**
- `job_service.create()` - Creates job record in database
- `process_domain_with_own_session()` - Performs actual sitemap discovery
- `_job_statuses` - In-memory dict tracking job state

**Error Handling:**
- Domain not found → Returns False, no job created
- Job creation fails → Returns False, domain status set to 'failed'
- Exception during processing → Caught, logged, domain status set to 'failed'

---

### SitemapProcessingService

**File:** `src/services/sitemap/processing_service.py`

**Purpose:** Discover sitemap URLs from domains and create SitemapFile records

#### Key Method: `process_domain_with_own_session()`

```python
async def process_domain_with_own_session(
    job_id: str,
    domain: str,
    user_id: Optional[str],
    max_urls: int
) -> None
```

**Parameters:**
- `job_id`: UUID string of job record
- `domain`: Domain name to scan (e.g., "example.com")
- `user_id`: User ID or None for system jobs
- `max_urls`: Maximum URLs to process (typically 1000)

**Returns:** None (updates job status and creates records)

**Process Flow:**
1. Create own database session (transaction isolation)
2. Update job status to 'running' in memory
3. Try common sitemap paths:
   - `https://{domain}/sitemap.xml`
   - `https://www.{domain}/sitemap.xml`
   - `https://{domain}/sitemap_index.xml`
   - `https://{domain}/wp-sitemap.xml`
   - etc.
4. For each found sitemap:
   - Parse XML
   - If sitemap index, recursively fetch child sitemaps
   - Create SitemapFile record
5. Update job status to 'complete'
6. Commit transaction

**Sitemap Discovery Logic:**
```python
SITEMAP_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/wp-sitemap.xml",
    "/sitemap-index.xml",
    "/post-sitemap.xml",
    "/page-sitemap.xml",
    "/category-sitemap.xml",
    "/product-sitemap.xml",
]

for path in SITEMAP_PATHS:
    for protocol in ["https", "http"]:
        for prefix in ["", "www."]:
            url = f"{protocol}://{prefix}{domain}{path}"
            # Try to fetch...
```

**XML Parsing:**
- Handles both regular sitemaps and sitemap indexes
- Extracts `<loc>` tags for URLs
- Follows `<sitemap>` tags in indexes

**Error Handling:**
- HTTP errors → Logged, continue to next path
- XML parse errors → Logged, skip that sitemap
- Database errors → Job marked as 'failed'
- Timeout → Job marked as 'failed' after threshold

**Dependencies:**
- `httpx.AsyncClient` - HTTP requests
- `xml.etree.ElementTree` - XML parsing
- Database session for creating SitemapFile records

---

## WF5 Services

### SitemapImportService

**File:** `src/services/sitemap_import_service.py`

**Purpose:** Extract individual page URLs from sitemap files and create Page records

#### Key Method: `process_single_sitemap_file()`

```python
async def process_single_sitemap_file(
    self,
    sitemap_file: SitemapFile,
    session: AsyncSession
) -> None
```

**Parameters:**
- `sitemap_file`: SitemapFile ORM object to process
- `session`: Database session (transaction managed by SDK)

**Returns:** None (updates sitemap_file status and creates Page records)

**Process Flow:**
1. Update sitemap_file.sitemap_import_status to 'Processing'
2. Fetch sitemap XML from URL
3. Parse XML, extract all `<url><loc>` entries
4. For each URL:
   - Run Honeybee categorization
   - Determine page_type, confidence, depth
   - Apply auto-selection rules
   - Build page_data dict
5. Bulk create Page records (batch insert)
6. Update sitemap_file.sitemap_import_status to 'Complete'
7. Commit transaction (handled by SDK)

**Honeybee Integration:**
```python
from honeybee import categorize_url

for url in extracted_urls:
    hb = categorize_url(url)
    
    page_data = {
        "url": url,
        "sitemap_file_id": sitemap_file.id,
        "page_type": hb["category"],
        "priority_level": 3,  # default low
        "page_curation_status": PageCurationStatus.New,
        "page_processing_status": None,
    }
    
    # Auto-selection rules
    if (
        hb["category"] in {PageTypeEnum.CONTACT_ROOT, PageTypeEnum.CAREER_CONTACT, PageTypeEnum.LEGAL_ROOT}
        and hb["confidence"] >= 0.6
        and hb["depth"] <= 2
    ):
        page_data["page_curation_status"] = PageCurationStatus.Selected
        page_data["page_processing_status"] = PageProcessingStatus.Queued
        page_data["priority_level"] = 1
    
    pages_to_create.append(page_data)
```

**Auto-Selection Criteria:**
- **Category:** CONTACT_ROOT, CAREER_CONTACT, or LEGAL_ROOT
- **Confidence:** >= 0.6 (60% confidence threshold)
- **Depth:** <= 2 (shallow pages more likely to have contacts)

**When auto-selected:**
- `page_curation_status = 'Selected'`
- `page_processing_status = 'Queued'` (triggers WF7 scheduler)
- `priority_level = 1` (high priority)

**Error Handling:**
- HTTP errors → sitemap_import_status = 'Error', error message stored
- XML parse errors → sitemap_import_status = 'Error'
- Database errors → Rolled back by SDK, status remains 'Queued'

**Dependencies:**
- Honeybee categorization system
- `httpx.AsyncClient` - Fetch sitemap XML
- `xml.etree.ElementTree` - Parse XML
- Database session for bulk insert

---

## WF7 Services

### PageCurationService

**File:** `src/services/WF7_V2_L4_1of2_PageCurationService.py`

**Purpose:** Scrape pages via ScraperAPI and extract contact information

#### Key Method: `process_single_page_for_curation()`

```python
async def process_single_page_for_curation(
    self,
    page: Page,
    session: AsyncSession
) -> None
```

**Parameters:**
- `page`: Page ORM object to process
- `session`: Database session (transaction managed by SDK)

**Returns:** None (updates page status and scraped_content)

**Process Flow:**
1. Update page.page_processing_status to 'Processing'
2. Build ScraperAPI request URL
3. Fetch page HTML via ScraperAPI
4. Extract emails using regex
5. Extract phone numbers using regex
6. Extract addresses (if implemented)
7. Build scraped_content dict
8. Store in page.scraped_content (JSONB)
9. Update page.page_processing_status to 'Complete'
10. Commit transaction (handled by SDK)

**ScraperAPI Integration:**
```python
SCRAPER_API_KEY = settings.scraper_api_key
SCRAPER_API_URL = "http://api.scraperapi.com"

params = {
    "api_key": SCRAPER_API_KEY,
    "url": page.url,
    "render": "false",  # Don't render JavaScript (faster, cheaper)
}

async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.get(SCRAPER_API_URL, params=params)
    html = response.text
```

**Email Extraction:**
```python
import re

EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
emails = re.findall(EMAIL_PATTERN, html)
emails = list(set(emails))  # Deduplicate
```

**Phone Extraction:**
```python
PHONE_PATTERN = r'(\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4})'
phones = re.findall(PHONE_PATTERN, html)
phones = list(set(phones))
```

**Scraped Content Structure:**
```json
{
  "emails": ["contact@example.com"],
  "phones": ["+1-555-0100"],
  "addresses": [],
  "extraction_timestamp": "2025-11-17T09:52:00Z",
  "scraper_metadata": {
    "status_code": 200,
    "credits_used": 1
  }
}
```

**Outcomes:**
- **Contacts found:** page_processing_status = 'Complete', scraped_content populated
- **No contacts:** page_processing_status = 'Complete', scraped_content = {"emails": [], "phones": []}
- **Error:** page_processing_status = 'Error', page_processing_error set

**Error Handling:**
- HTTP errors → Status 'Error', error message stored
- Timeout → Status 'Error', "Timeout" message
- ScraperAPI errors → Status 'Error', API error message
- Extraction errors → Logged, partial data stored

**Dependencies:**
- ScraperAPI (external service, costs credits)
- `httpx.AsyncClient` - HTTP requests
- Regex patterns for extraction
- Database session for updates

---

## Supporting Services

### JobService

**File:** `src/services/job_service.py`

**Purpose:** CRUD operations for Job records

#### Key Methods

**create()**
```python
async def create(
    session: AsyncSession,
    job_data: Dict
) -> Optional[Job]
```
- Creates new Job record
- Returns Job object or None on failure

**get_pending_jobs()**
```python
async def get_pending_jobs(
    session: AsyncSession,
    job_type: Optional[str] = None,
    limit: int = 10
) -> List[Job]
```
- Fetches jobs with status='pending'
- Optionally filters by job_type
- Returns list of Job objects

**update_status()**
```python
async def update_status(
    session: AsyncSession,
    job_id: str,
    status: str,
    error: Optional[str] = None
) -> bool
```
- Updates job status and optional error message
- Returns True on success

**Note:** This service is used but the old sitemap job processor (lines 137-179 of sitemap_scheduler.py) is DISABLED as of Sept 9, 2025. Jobs are now processed immediately via asyncio.create_task() instead of being queued and picked up by a scheduler.

---

## Service Communication Patterns

### ✅ CORRECT Pattern: Direct Service Calls

```python
# Service A calls Service B directly
service_b = ServiceB()
result = await service_b.process(item_id, session)
```

**Examples:**
- DomainToSitemapAdapterService → job_service.create()
- Schedulers → Service.process_single_item()

**Benefits:**
- No network overhead
- No authentication needed
- Single transaction context
- Simpler error handling

### ❌ WRONG Pattern: HTTP Calls Between Services

```python
# Service A makes HTTP call to Service B's endpoint
async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8000/api/...", ...)
```

**Problems:**
- Network overhead
- Authentication complexity
- Multiple failure points
- Can't share transaction context
- **Doesn't trigger background tasks** (critical issue)

**Historical Note:** DomainToSitemapAdapterService used this pattern until Nov 17, 2025 (Commit 1ffa371, then 9f091f6).

---

## Service Dependencies Graph

```
DomainToSitemapAdapterService
    ├─ job_service.create()
    ├─ _job_statuses (in-memory)
    └─ asyncio.create_task(process_domain_with_own_session)
            ↓
        SitemapProcessingService
            ├─ httpx.AsyncClient
            ├─ xml.etree.ElementTree
            └─ Creates SitemapFile records
                    ↓
                (Scheduler picks up)
                    ↓
            SitemapImportService
                ├─ httpx.AsyncClient
                ├─ Honeybee categorization
                └─ Creates Page records
                        ↓
                    (Scheduler picks up)
                        ↓
                PageCurationService
                    ├─ ScraperAPI
                    ├─ Regex extraction
                    └─ Updates Page.scraped_content
```

---

## Service Configuration

### Environment Variables

```bash
# ScraperAPI
SCRAPER_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://...

# Scheduler Intervals (minutes)
PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES=5
SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES=5
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_INTERVAL_MINUTES=1

# Batch Sizes
PAGE_CURATION_SCHEDULER_BATCH_SIZE=10
SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE=10
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_BATCH_SIZE=10

# Max Instances (prevent overlapping runs)
PAGE_CURATION_SCHEDULER_MAX_INSTANCES=1
SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES=1
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_MAX_INSTANCES=1
```

### Settings Access

```python
from src.config.settings import settings

api_key = settings.scraper_api_key
batch_size = settings.PAGE_CURATION_SCHEDULER_BATCH_SIZE
```

---

## Service Testing Recommendations

### Unit Tests Needed

1. **DomainToSitemapAdapterService**
   - Test job creation
   - Test background task trigger
   - Test error handling

2. **SitemapProcessingService**
   - Test sitemap discovery
   - Test XML parsing
   - Test sitemap index handling

3. **SitemapImportService**
   - Test URL extraction
   - Test Honeybee integration
   - Test auto-selection logic

4. **PageCurationService**
   - Test ScraperAPI integration
   - Test email/phone extraction
   - Test error handling

### Integration Tests Needed

1. **End-to-end WF4→WF5→WF7**
   - Create domain → verify sitemaps → verify pages → verify contacts

2. **Scheduler Integration**
   - Verify schedulers pick up queued items
   - Verify status transitions
   - Verify error handling

3. **Database Transactions**
   - Verify rollback on errors
   - Verify cascade deletes
   - Verify concurrent access
