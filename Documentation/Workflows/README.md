# ScraperSky Workflows

**Purpose:** Document the 7 core data processing workflows that power ScraperSky's scraping and analysis capabilities.

**Background:** ScraperSky processes data through distinct workflows, each with specific inputs, outputs, and processing logic. Understanding these workflows is essential for maintaining and extending the system.

---

## Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [Workflow Descriptions](#workflow-descriptions)
3. [Data Flow](#data-flow)
4. [Schedulers and Automation](#schedulers-and-automation)
5. [Implementation Guide](#implementation-guide)

---

## Workflow Overview

| Workflow | Name | Purpose | Primary Tables | Scheduler |
|----------|------|---------|----------------|-----------|
| **WF1** | Google Places Search | Search for businesses via Google Maps API | `places`, `place_search` | None (API-triggered) |
| **WF2** | Deep Scan (Place Details) | Get detailed business info from Google Maps | `local_businesses` | None (queued by WF1) |
| **WF3** | Domain Extraction | Extract domains from business data | `domains` | Domain Scheduler |
| **WF4** | Domain Sitemap Submission | Submit domains for sitemap discovery | `domains` | Domain Sitemap Submission Scheduler |
| **WF5** | Sitemap Discovery (Legacy) | Discover sitemaps for domains | `sitemap_files` | Sitemap Scheduler |
| **WF6** | Sitemap Import (Modern) | Parse and import sitemap URLs | `sitemap_files`, `sitemap_urls` | Sitemap Import Scheduler |
| **WF7** | Page Curation | Curate and scrape pages for content | `pages`, `contacts` | Page Curation Scheduler |

---

## Workflow Descriptions

### WF1: Google Places Search

**Purpose:** Search for businesses using Google Maps Places Text Search API

**Trigger:** User initiates search via API
**Status:** User-triggered (not scheduled)

#### Process Flow

```
User Search Request
    ↓
Google Maps Places Text Search API
    ↓
Store raw place data
    ↓
Queue selected places for WF2 (Deep Scan)
```

#### Key Components

**Router:** `src/routers/google_maps_api.py`
- `POST /api/v3/google-maps-api/search/places` - Search for places
- `POST /api/v3/google-maps-api/places/{place_id}/details` - Get place details

**Service:** `src/services/places/places_search_service.py`
- `search_places()` - Execute Google Maps search
- `store_search_results()` - Save results to database

**Models:**
- `Place` - Raw place data from Google
- `PlaceSearch` - Search query metadata

#### Inputs
- Search query (text)
- Location (optional)
- Search radius (optional)

#### Outputs
- `Place` records (raw Google Maps data)
- Queued for WF2 if user selects places

---

### WF2: Deep Scan (Place Details)

**Purpose:** Retrieve detailed business information using Google Maps Place Details API

**Trigger:** User selects places from WF1 results
**Status:** Queued by user selection

#### Process Flow

```
Selected Places (from WF1)
    ↓
Google Maps Place Details API
    ↓
Extract structured business data
    ↓
Store as LocalBusiness records
    ↓
Queue for WF3 (Domain Extraction)
```

#### Key Components

**Service:** `src/services/places/places_deep_service.py`
- `process_places_batch()` - Process selected places
- `get_place_details()` - Call Google Maps Place Details API
- `extract_local_business()` - Convert to LocalBusiness model

**Models:**
- `LocalBusiness` - Structured business data
  - Business name, address, phone
  - Website (domain extracted to WF3)
  - Operating hours, ratings
  - Social media links

#### Inputs
- Place IDs from WF1
- User selection status

#### Outputs
- `LocalBusiness` records with structured data
- Domains queued for WF3

---

### WF3: Domain Extraction

**Purpose:** Extract and process domain information from business data

**Trigger:** Automated scheduler (every 1 minute)
**Status:** Active background processing

#### Process Flow

```
LocalBusiness with website
    ↓
Extract domain from URL
    ↓
Detect site metadata (title, description)
    ↓
Store as Domain record
    ↓
Queue for WF4 (Sitemap Submission)
```

#### Key Components

**Scheduler:** `src/services/domain_scheduler.py`
- Runs every 1 minute (configurable)
- Processes 50 domains per batch (configurable)
- 3-phase pattern: DB → Process → DB

**Service:** `src/services/domain_service.py`
- `process_pending_domains()` - Main processing loop
- `detect_site_metadata()` - Extract metadata from domain
- `update_from_metadata()` - Update domain record

**Models:**
- `Domain`
  - Dual-status: `curation_status` + `processing_status`
  - Metadata: title, description, technologies
  - Triggers WF4 on completion

#### 3-Phase Processing Pattern

**Phase 1: Quick DB (seconds)**
```python
async with session.begin():
    domains = select(Domain).where(status == 'pending')
    for domain in domains:
        domain.processing_status = 'processing'
# Connection released
```

**Phase 2: Slow Processing (minutes)**
```python
# NO database connection held
for domain in domains:
    metadata = await scraper_api.detect_metadata(domain.url)
    domain.metadata = metadata
```

**Phase 3: Quick DB (seconds)**
```python
async with session.begin():
    for domain in domains:
        domain.processing_status = 'complete'
        domain.sitemap_analysis_status = 'queued'  # Trigger WF4
```

**Why 3-phase:** Prevents connection timeouts during slow external API calls.

#### Configuration

```bash
DOMAIN_SCHEDULER_INTERVAL_MINUTES=1  # How often to run
DOMAIN_SCHEDULER_BATCH_SIZE=50       # Domains per batch
DOMAIN_SCHEDULER_MAX_INSTANCES=3     # Concurrent executions
```

---

### WF4: Domain Sitemap Submission

**Purpose:** Submit domains for sitemap discovery and analysis

**Trigger:** Automated scheduler (every 5 minutes)
**Status:** Active background processing

#### Process Flow

```
Domain with sitemap_analysis_status = 'queued'
    ↓
Submit domain for sitemap discovery
    ↓
Mark as submitted
    ↓
Triggers WF5/WF6 (Sitemap Discovery/Import)
```

#### Key Components

**Scheduler:** `src/services/domain_sitemap_submission_scheduler.py`
- Runs every 5 minutes (configurable)
- Processes 20 domains per batch (configurable)

**Models:**
- `Domain.sitemap_analysis_status` - Queued → Submitted

#### Configuration

```bash
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_INTERVAL_MINUTES=5
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_BATCH_SIZE=20
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_MAX_INSTANCES=2
```

---

### WF5: Sitemap Discovery (Legacy)

**Purpose:** Discover and parse sitemap files for domains

**Trigger:** Automated scheduler (every 3 minutes)
**Status:** Legacy workflow (being replaced by WF6)

#### Process Flow

```
Domain submitted for sitemap analysis
    ↓
Discover sitemap URLs (robots.txt, common paths)
    ↓
Download and parse sitemap XML
    ↓
Store sitemap file metadata
    ↓
Extract URLs for WF6
```

#### Key Components

**Scheduler:** `src/services/sitemap_scheduler.py`
- Multi-purpose scheduler (handles WF2, WF3, WF5)
- Runs every 3 minutes (configurable)

**Service:** `src/services/sitemap/sitemap_processing_service.py`
- `discover_sitemaps()` - Find sitemap URLs
- `parse_sitemap()` - Parse XML
- `extract_urls()` - Get URLs from sitemap

**Models:**
- `SitemapFile` - Sitemap metadata
  - URL, file size, last modified
  - URL count
  - Processing status

---

### WF6: Sitemap Import (Modern)

**Purpose:** Parse sitemap files and import individual URLs for processing

**Trigger:** Automated scheduler (every 2 minutes)
**Status:** Active background processing (modern replacement for WF5)

#### Process Flow

```
SitemapFile with status = 'queued'
    ↓
Download and parse sitemap XML
    ↓
Extract individual URLs
    ↓
Store as SitemapUrl records
    ↓
Queue URLs for WF7 (Page Curation)
```

#### Key Components

**Scheduler:** `src/services/sitemap_import_scheduler.py`
- Runs every 2 minutes (configurable)
- Processes 10 sitemaps per batch (configurable)

**Service:** `src/services/sitemap/sitemap_import_service.py`
- `process_sitemap_imports()` - Main import loop
- `parse_sitemap_file()` - Parse XML
- `import_urls()` - Store URLs

**Models:**
- `SitemapFile` - Source sitemap
  - Dual-status: `curation_status` + `processing_status`
- `SitemapUrl` - Individual URLs from sitemap
  - URL, priority, change frequency
  - Queued for WF7

#### Configuration

```bash
SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES=2
SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE=10
SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES=2
```

---

### WF7: Page Curation

**Purpose:** Curate and scrape individual pages for content and contacts

**Trigger:** Automated scheduler (every 5 minutes)
**Status:** Active background processing

#### Process Flow

```
SitemapUrl or Page with curation_status = 'selected'
    ↓
Scrape page content (ScraperAPI)
    ↓
Extract structured data
    ↓
Extract contact information (emails, phones, social)
    ↓
Store as Page + Contact records
```

#### Key Components

**Scheduler:** `src/services/page_curation_scheduler.py`
- Runs every 5 minutes (configurable)
- Processes 20 pages per batch (configurable)

**Service:** `src/services/page_scraper/processing_service.py`
- `process_pages_batch()` - Main curation loop
- `scrape_page()` - Fetch page content
- `extract_contacts()` - Find contact info

**Models:**
- `Page` - Page metadata and content
  - Dual-status: `curation_status` + `processing_status`
  - Content, metadata, extract
- `Contact` - Extracted contact information
  - Emails, phones, social media links
  - Associated with page

#### Configuration

```bash
PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES=5
PAGE_CURATION_SCHEDULER_BATCH_SIZE=20
PAGE_CURATION_SCHEDULER_MAX_INSTANCES=3
```

---

## Data Flow

### Complete Pipeline

```
WF1: Google Places Search
  ↓
WF2: Place Details (Deep Scan)
  ↓
WF3: Domain Extraction
  ↓
WF4: Domain Sitemap Submission
  ↓
WF5: Sitemap Discovery (Legacy)
  ↓
WF6: Sitemap Import (Modern)
  ↓
WF7: Page Curation
```

### Handoffs Between Workflows

**WF1 → WF2:**
- User selects places from search results
- Selected places queued for deep scan
- Trigger: `Place.curation_status = 'selected'`

**WF2 → WF3:**
- LocalBusiness created with website URL
- Domain extracted from website
- Trigger: `LocalBusiness.website` populated

**WF3 → WF4:**
- Domain metadata extraction complete
- Domain queued for sitemap analysis
- Trigger: `Domain.sitemap_analysis_status = 'queued'`

**WF4 → WF5/WF6:**
- Domain submitted for sitemap discovery
- Sitemaps queued for parsing
- Trigger: `Domain.sitemap_analysis_status = 'submitted'`

**WF5/WF6 → WF7:**
- Sitemap URLs extracted
- Pages queued for curation
- Trigger: `SitemapUrl.curation_status = 'selected'` or `Page.curation_status = 'selected'`

---

## Schedulers and Automation

### Active Schedulers

**5 Active Background Schedulers:**

1. **Domain Scheduler** (WF3)
   - Interval: 1 minute
   - Batch: 50 domains
   - Max instances: 3

2. **Sitemap Scheduler** (WF2/WF3/WF5 - Multi-purpose)
   - Interval: 3 minutes
   - Batch: Varies
   - Max instances: 2

3. **Domain Sitemap Submission Scheduler** (WF4)
   - Interval: 5 minutes
   - Batch: 20 domains
   - Max instances: 2

4. **Sitemap Import Scheduler** (WF6)
   - Interval: 2 minutes
   - Batch: 10 sitemaps
   - Max instances: 2

5. **Page Curation Scheduler** (WF7)
   - Interval: 5 minutes
   - Batch: 20 pages
   - Max instances: 3

### Scheduler Lifecycle

**Startup (in main.py):**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start shared scheduler
    start_scheduler()

    # Register all jobs
    setup_domain_scheduler()
    setup_sitemap_scheduler()
    setup_domain_sitemap_submission_scheduler()
    setup_sitemap_import_scheduler()
    setup_page_curation_scheduler()

    yield  # App runs

    # Shutdown
    shutdown_scheduler()
```

**Shared Scheduler Instance:**
- Single APScheduler instance (`src/scheduler_instance.py`)
- All workflows share this scheduler
- Nuclear shared service (deletion breaks all workflows)

---

## Implementation Guide

### Adding Features to Existing Workflows

**Pattern: Follow existing workflow structure**

**Example: Extend WF3 (Domain Extraction)**

1. **Find existing code:**
   ```bash
   cat src/services/domain_scheduler.py
   ```

2. **Copy structure:**
   ```python
   # Your enhancement
   async def process_pending_domains_with_new_feature(limit: int = 50):
       # Phase 1: Quick DB
       async with get_session() as session:
           async with session.begin():
               domains = await fetch_pending(session, limit)
               for domain in domains:
                   domain.processing_status = 'processing'

       # Phase 2: Process (no connection held)
       for domain in domains:
           # Your new feature here
           new_data = await your_new_extraction(domain.url)
           domain.new_field = new_data

       # Phase 3: Quick DB
       async with get_session() as session:
           async with session.begin():
               for domain in domains:
                   domain.processing_status = 'complete'
   ```

3. **Test with small batch:**
   ```bash
   # Test with 5 domains first
   DOMAIN_SCHEDULER_BATCH_SIZE=5 python -c "..."
   ```

### Creating New Workflows

**If you need a new workflow (WF8+):**

1. **Define Purpose:** What does this workflow do?
2. **Identify Inputs:** What triggers it? What data does it need?
3. **Define Outputs:** What records does it create? What workflow does it trigger next?
4. **Choose Pattern:**
   - User-triggered (like WF1, WF2)
   - Scheduled background (like WF3-WF7)
   - Event-driven (status changes)

5. **Follow Existing Structure:**
   - Copy from similar workflow
   - Use dual-status if processable entity
   - Use 3-phase pattern for slow operations
   - Follow transaction boundaries (router owns transaction)

6. **Register Scheduler (if background):**
   ```python
   # src/services/your_new_scheduler.py
   def setup_your_scheduler():
       from src.scheduler_instance import scheduler

       scheduler.add_job(
           process_your_workflow,
           trigger=IntervalTrigger(minutes=5),
           id="process_your_workflow",
           name="Your Workflow Name",
           max_instances=2
       )

   # src/main.py (in lifespan)
   setup_your_scheduler()
   ```

---

## Related Documentation

- **Schedulers Implementation:** `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/05_SCHEDULERS_WORKFLOWS.md`
- **ADR-003:** Dual-Status Workflow Pattern
- **ADR-004:** Transaction Boundaries
- **CONTRIBUTING.md:** Code standards and patterns

---

## Summary: Workflow Quick Reference

**User-Triggered:**
- WF1: Google Places Search
- WF2: Place Details (Deep Scan)

**Automated Background Processing:**
- WF3: Domain Extraction (every 1 min)
- WF4: Domain Sitemap Submission (every 5 min)
- WF5: Sitemap Discovery - Legacy (every 3 min)
- WF6: Sitemap Import - Modern (every 2 min)
- WF7: Page Curation (every 5 min)

**Key Patterns:**
- Dual-status for processable entities (curation + processing)
- 3-phase pattern for long operations (DB → Process → DB)
- Transaction boundaries owned by routers/schedulers

**Handoff Mechanism:** Status field changes trigger next workflow (queued → processing → complete)
