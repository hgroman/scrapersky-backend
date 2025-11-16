# Service Layer - Complete Architecture Reference

**Analysis Date:** November 7, 2025
**Total Services:** 36 service files
**Architecture Pattern:** Transaction-aware, dependency injection
**Key Pattern:** Routers own transactions, services execute business logic

---

## Table of Contents

1. [Service Layer Overview](#service-layer-overview)
2. [Service Categories](#service-categories)
3. [Architectural Patterns](#architectural-patterns)
4. [External API Integrations](#external-api-integrations)
5. [Data Flow Patterns](#data-flow-patterns)

---

## Service Layer Overview

### Design Principles

**Core Principle:** Services are **transaction-aware** but do NOT manage transactions

```python
# ✅ CORRECT - Router owns transaction
@router.post("/domains")
async def create_domain(session: AsyncSession = Depends(get_session_dependency)):
    async with session.begin():  # Router creates transaction
        result = await domain_service.create(session, data)  # Service uses it
        return result

# ❌ INCORRECT - Service creating transactions
async def create(session, data):
    async with session.begin():  # DON'T do this in services
        ...
```

**Exception:** Background tasks create their own sessions via `get_background_session()`

### Service Organization

```
src/services/
├── batch/                          # Batch processing
│   ├── batch_functions.py
│   ├── batch_processor_service.py
│   └── types.py
├── places/                         # Google Maps/Places
│   ├── places_service.py
│   ├── places_search_service.py
│   ├── places_storage_service.py
│   └── places_deep_service.py
├── sitemap/                        # Sitemap processing
│   ├── sitemap_processing_service.py
│   ├── sitemap_import_service.py
│   └── sitemap_service.py
├── page_scraper/                   # Page analysis
│   ├── processing_service.py
│   └── domain_processor.py
├── core/                           # Utilities
│   ├── validation_service.py
│   └── user_context_service.py
├── domain_scheduler.py             # WF3 scheduler
├── sitemap_scheduler.py            # WF2/WF3/WF5 scheduler ⚠️
├── sitemap_import_scheduler.py     # WF6 scheduler
├── domain_sitemap_submission_scheduler.py  # WF4 scheduler
├── WF7_V2_L4_2of2_PageCurationScheduler.py # WF7 scheduler
├── job_service.py                  # Job management
├── profile_service.py              # User profiles
├── business_to_domain_service.py   # Domain extraction
├── domain_to_sitemap_adapter_service.py    # WF4 adapter
├── sitemap_files_service.py        # Sitemap CRUD
└── database_health_monitor.py      # Connection monitoring
```

---

## Service Categories

### 1. Batch Processing Services

**Location:** `src/services/batch/`

#### Purpose
Process multiple domains concurrently with progress tracking and error handling.

#### Key Services

**`batch_functions.py`** - Core batch operations
- `create_batch()` - Create batch job record
- `get_batch_status()` - Retrieve batch progress
- `process_batch_with_own_session()` - Background batch processor
  - Concurrent processing with semaphore (max 25)
  - Periodic progress updates via `session.flush()`
  - Handles partial failures gracefully

**`batch_processor_service.py`** - High-level orchestration
- `initiate_batch_processing()` - Entry point for batch jobs
- `get_batch_progress()` - Current batch status
- `cancel_batch()` - Cancel pending/processing batches

**`types.py`** - Shared type definitions
- `BatchOptions`, `BatchStatus`, `DomainResult`, `BatchResult`

#### Key Patterns
- **Concurrency Control:** `asyncio.Semaphore(25)` limits concurrent operations
- **Progress Tracking:** Periodic DB flushes during processing
- **Graceful Degradation:** Individual failures don't stop batch
- **Diagnostic Logging:** Writes markers to `/tmp/scraper_sky_task_markers/`

**See:** Comprehensive service layer documentation in conversation history above for complete details.

---

### 2. Google Maps / Places Services

**Location:** `src/services/places/`

#### Purpose
Integrate with Google Maps Platform APIs for business discovery and enrichment.

#### Key Services

**`places_search_service.py`** - Google Places Text Search API
- `search_places()` - Async HTTP calls to Google Places API
  - Rate limiting: 2-second delay between pagination tokens
  - Error handling: Sanitizes logs to prevent API key leakage
  - Returns standardized place list
- `standardize_place()` - Transform API response to database schema
- **External API:** `https://maps.googleapis.com/maps/api/place/textsearch/json`
- **Cost:** ~$7 per 1,000 requests

**`places_deep_service.py`** - Google Places Details API
- `process_single_deep_scan()` - Fetch detailed place information
  - Uses `googlemaps` Python SDK
  - Requests 15+ fields (name, address, phone, website, hours, etc.)
  - Maps response to `LocalBusiness` model
  - PostgreSQL upsert pattern (INSERT ON CONFLICT)
- **Cost:** ~$17 per 1,000 requests

**`places_storage_service.py`** - Persistence layer
- `store_places()` - Batch storage with duplicate detection
  - Pre-checks existing via `place_id IN (...)` query
  - Update-or-insert pattern
- `get_places_from_staging()` - Advanced filtering with ILIKE

**`places_service.py`** - Database operations
- `get_by_id()`, `get_places()`, `update_status()`, `create_search()`
- Uses `places_staging` and `place_searches` tables

#### Integration Details
- **API Key:** `GOOGLE_MAPS_API_KEY` environment variable
- **Rate Limiting:** Manual 2-second delays (no circuit breaker)
- **Error Handling:** Log sanitization utility prevents key leakage

**See:** `08_EXTERNAL_INTEGRATIONS.md` for complete Google Maps integration details.

---

### 3. Sitemap Services

**Location:** `src/services/sitemap/`

#### Purpose
Discover, parse, and import sitemap XML files for URL extraction.

#### Key Services

**`sitemap_processing_service.py`** - Orchestrate sitemap discovery
- `SitemapProcessingService` class wraps `SitemapAnalyzer`
- In-memory job status tracking via `_job_statuses` dict
- `initiate_domain_scan()` - Create job and trigger background processing
- `process_domain_with_own_session()` - 5-phase processing:
  1. Standardize domain (add https://, normalize)
  2. Analyze sitemaps via `SitemapAnalyzer`
  3. Create/update Domain record (upsert)
  4. Store SitemapFile records
  5. Store SitemapUrl records in batches of 100

**`sitemap_import_service.py`** - Parse sitemap XML and import URLs
- `process_single_sitemap_file()` - Download, parse, categorize, store
  - HTTP download via `httpx.AsyncClient` (60s timeout)
  - XML parsing using `SitemapParser` class
  - Detects sitemap index (recursive child sitemap fetch)
  - Page categorization via `HoneybeeCategorizer`
  - Batch insert Page records

**`sitemap_files_service.py`** - CRUD operations
- `get_by_id()`, `get_all()` with advanced filtering
- Eager loads domain relationship via `joinedload()`

#### Discovery Methods
- `ROBOTS_TXT` - Parse robots.txt for sitemap directives
- `COMMON_PATH` - Check standard paths (/sitemap.xml, etc.)
- `SITEMAP_INDEX` - Recursive child sitemap discovery
- `HTML_LINK` - Extract from HTML `<link>` tags
- `MANUAL` - User-submitted sitemaps

---

### 4. Page Scraper Services

**Location:** `src/services/page_scraper/`

#### Purpose
Extract website metadata, detect CMS, identify contact information.

#### Key Services

**`processing_service.py`** - Coordinate page scanning
- `validate_domain()` - Pure validation (no DB queries)
- `initiate_domain_scan()` - Create Domain and Job records
- `initiate_batch_scan()` - Create BatchJob record
- `get_job_status()` - Handles multiple ID types (UUID, integer)

**`domain_processor.py`** - Execute domain processing in background
- `process_domain_with_own_session()` - 3-step workflow:
  1. Get or create Domain record
  2. Update Job to 'processing' status
  3. Extract metadata via `detect_site_metadata()`
  4. Update Job with results or error
- `get_or_create_domain_orm()` - Atomic insert with `ON CONFLICT DO NOTHING`
- Uses dedicated session from `get_background_session()`

#### Metadata Extracted
- Title, description, favicon, logo
- Language detection
- WordPress detection + version
- Elementor plugin detection
- Tech stack identification
- Email addresses, phone numbers
- Social media URLs (Facebook, Twitter, LinkedIn, Instagram, YouTube)

**See:** `src/scraper/metadata_extractor.py` for scraping implementation.

---

### 5. Scheduler Services

**Location:** `src/services/*.py`

#### Purpose
Background job processing for workflow automation (7 workflows: WF1-WF7).

#### Active Schedulers

**`domain_scheduler.py`** - Domain metadata extraction (WF3)
- **3-Phase Pattern** (anti-connection-hold):
  1. Quick DB: Fetch pending domains, mark as processing
  2. Release connection: Heavy metadata extraction
  3. Quick DB: Update final results
- Processes domains with `status = pending`
- Uses `with_for_update(skip_locked=True)` for concurrency safety

**`sitemap_scheduler.py`** - Multi-workflow processor (WF2/WF3/WF5)
- ⚠️ **CRITICAL:** Single point of failure for 3 workflows
- Handles:
  - WF2: Deep scans (calls `PlacesDeepService`)
  - WF3: Domain extraction (calls `LocalBusinessToDomainService`)
  - WF5: Sitemap import (legacy, being replaced)
- **Recommendation:** Split into 3 separate schedulers

**`domain_sitemap_submission_scheduler.py`** - Submit domains to sitemap scan (WF4)
- Fetches domains with `sitemap_curation_status = Selected`
- POSTs to internal `/api/v3/sitemap/scan` endpoint
- Updates `sitemap_analysis_status` to `submitted/failed`

**`sitemap_import_scheduler.py`** - Modern sitemap import (WF6)
- Uses SDK job loop pattern (modern, reusable)
- Processes SitemapFiles with `sitemap_import_status = Queued`
- Creates Page records from sitemap URLs

**`WF7_V2_L4_2of2_PageCurationScheduler.py`** - Page processing (WF7)
- Uses SDK job loop pattern
- Processes Pages with `page_processing_status = Queued`
- Extracts contact information, categorizes pages

#### Scheduler Configuration

Each scheduler configured via environment variables:
```bash
{NAME}_SCHEDULER_INTERVAL_MINUTES=1    # Default 1 minute
{NAME}_SCHEDULER_BATCH_SIZE=50         # Items per run
{NAME}_SCHEDULER_MAX_INSTANCES=3       # Concurrent instances
```

**See:** `05_SCHEDULERS_WORKFLOWS.md` for complete scheduler documentation.

---

### 6. Utility Services

**`job_service.py`** - Job lifecycle management
- `get_by_id()` - Handles multiple ID types
- `create_for_domain()`, `update_status()`, `get_pending_jobs()`
- Uses raw SQL for Supavisor compatibility

**`validation_service.py`** - Input validation
- `validate_url()`, `validate_domain()`, `validate_email()`, `validate_uuid()`
- Uses `validators` library with regex fallbacks

**`user_context_service.py`** - User context handling
- `get_valid_user_id()` - Tries: provided ID → JWT → env vars
- `get_tenant_id()`, `get_user_name()`
- Fallback to DEV_USER_ID / SYSTEM_USER_ID

**`database_health_monitor.py`** - Connection deadlock prevention
- Queries `pg_stat_activity` for idle-in-transaction connections
- Terminates blocking connections via `pg_terminate_backend()`
- Checks for table locks on critical tables

**`business_to_domain_service.py`** - Domain extraction from LocalBusiness (WF3)
- `create_pending_domain_from_local_business()`
- Extracts domain from `website_url`
- Removes "www." prefix for consistency

**`domain_to_sitemap_adapter_service.py`** - Bridge to legacy sitemap system (WF4)
- ⚠️ **CRITICAL:** Was deleted once, breaking entire WF4 pipeline
- `submit_domain_to_legacy_sitemap()`
- POSTs to internal `/api/v3/sitemap/scan` endpoint

---

## Architectural Patterns

### 1. Transaction Boundary Pattern

**Rule:** Routers own transaction boundaries, services are transaction-aware.

```python
# Router (owns transaction)
@router.post("/resource")
async def create_resource(session: AsyncSession = Depends(get_session_dependency)):
    async with session.begin():
        result = await service.create(session, data)
        return result

# Service (transaction-aware)
async def create(session: AsyncSession, data: dict):
    # Uses session but doesn't create transactions
    stmt = insert(Model).values(**data)
    await session.execute(stmt)
    # Router commits or rolls back
```

**Exception:** Background tasks create own sessions

```python
# Background task (creates own session)
async def background_task(job_id: str):
    async with get_background_session() as session:
        async with session.begin():
            # Process independently
            pass
```

### 2. Async-First Pattern

All services use async/await:
- Database operations: `await session.execute()`
- HTTP requests: `aiohttp.ClientSession`, `httpx.AsyncClient`
- File operations: `aiofiles` (when needed)
- Background tasks: `asyncio.create_task()`, `asyncio.gather()`

### 3. Dependency Injection Pattern

Services receive dependencies as parameters:
```python
async def process(session: AsyncSession, user_id: UUID, config: Settings):
    # Session, user context, config all injected
    pass
```

### 4. Error Handling Pattern

**Graceful Degradation:**
```python
success_count = 0
failed_items = []

for item in items:
    try:
        await process_item(item)
        success_count += 1
    except Exception as e:
        logger.error(f"Failed: {item}", exc_info=True)
        failed_items.append((item, str(e)))

return (success_count, failed_items)
```

**Error Attribution:**
```python
try:
    result = await operation()
except Exception as e:
    await update_status(
        status="failed",
        last_error=str(e),
        error_details={"message": str(e), "type": type(e).__name__}
    )
```

### 5. Concurrency Control Pattern

**Semaphore for limiting concurrent operations:**
```python
semaphore = asyncio.Semaphore(25)

async def process_with_limit(item):
    async with semaphore:
        return await process_item(item)

results = await asyncio.gather(*[
    process_with_limit(item) for item in items
], return_exceptions=True)
```

### 6. Batch Processing Pattern

**Batch insert with periodic flushes:**
```python
for i, batch in enumerate(chunks(items, 100)):
    for item in batch:
        session.add(Model(**item))

    await session.flush()  # Flush every 100 items

    if i % 10 == 0:
        logger.info(f"Processed {i * 100} items")
```

### 7. Background Session Pattern

**3-Phase to prevent connection holds:**
```python
# Phase 1: Quick DB - fetch and mark
async with get_background_session() as session:
    async with session.begin():
        items = await fetch_pending(session, limit=50)
        await mark_as_processing(session, items)

# Phase 2: Heavy computation - NO DB connection
for item in items:
    result = await heavy_computation(item)  # No DB held

# Phase 3: Quick DB - update results
async with get_background_session() as session:
    async with session.begin():
        await update_results(session, items, results)
```

---

## External API Integrations

### Google Maps Platform

**Services:** `places_search_service.py`, `places_deep_service.py`

**APIs Used:**
- Text Search API: `https://maps.googleapis.com/maps/api/place/textsearch/json`
- Place Details API: Via `googlemaps` Python SDK

**Rate Limiting:** Manual 2-second delays between pagination tokens

**Error Handling:** Log sanitization to prevent API key leakage

### ScraperAPI

**Services:** Metadata extraction (via `scraper` module)

**Base URL:** `http://api.scraperapi.com`

**Cost Controls:**
- Premium: disabled by default (5x multiplier)
- JS Rendering: disabled (10x multiplier)
- Geotargeting: disabled (2x multiplier)

**Client:** Dual-method (aiohttp primary, SDK fallback)

### OpenAI

**Services:** Vector database operations

**Model:** text-embedding-ada-002

**Usage:** Semantic pattern search

**See:** `08_EXTERNAL_INTEGRATIONS.md` for complete integration details.

---

## Data Flow Patterns

### Domain Discovery → Sitemap → Pages → Contacts

```
1. Google Places Search (WF1)
   ↓ (places_search_service)
2. Deep Scan (WF2)
   ↓ (places_deep_service → local_businesses)
3. Domain Extraction (WF3)
   ↓ (business_to_domain_service → domains)
4. Domain Sitemap Submission (WF4)
   ↓ (domain_to_sitemap_adapter_service)
5. Sitemap Discovery (WF5)
   ↓ (sitemap_processing_service → sitemap_files)
6. Sitemap Import (WF6)
   ↓ (sitemap_import_service → pages)
7. Page Curation (WF7)
   ↓ (page curation scheduler → contacts)
```

### Batch Processing Flow

```
API Request
  ↓ (batch_processor_service.initiate_batch_processing)
Create BatchJob record
  ↓ (FastAPI background task)
batch_functions.process_batch_with_own_session()
  ↓ (Semaphore limit 25)
For each domain:
  ↓ (domain_processor.process_domain_with_own_session)
  Metadata extraction
  ↓
  Update Domain + Job
  ↓
Update BatchJob progress
  ↓
Final status: COMPLETED/FAILED
```

---

## Best Practices

### ✅ Well-Designed Patterns

1. **Transaction Ownership** - Clear boundaries prevent deadlocks
2. **Async-First** - Maximizes throughput for I/O-bound operations
3. **Graceful Degradation** - Partial failures don't stop entire batch
4. **Error Attribution** - Detailed errors stored for debugging
5. **Concurrency Control** - Semaphores prevent resource exhaustion
6. **3-Phase Background Pattern** - Prevents database connection holds

### ⚠️ Areas for Improvement

1. **Multi-Workflow Scheduler** - `sitemap_scheduler.py` is single point of failure
2. **No Circuit Breakers** - External API failures not handled with backoff
3. **Limited Retry Logic** - Most operations don't retry transient failures
4. **Hardcoded Values** - Some schedulers have hardcoded intervals/batch sizes
5. **Missing Observability** - Limited metrics/tracing for production monitoring

---

## Related Documentation

- **Complete Service Layer Analysis** - See exploration results in conversation history
- **Schedulers** - See `05_SCHEDULERS_WORKFLOWS.md` for background job details
- **External APIs** - See `08_EXTERNAL_INTEGRATIONS.md` for integration patterns
- **Database** - See `02_DATABASE_SCHEMA.md` for data models used by services

---

*This is a summary reference. For complete service-by-service documentation with code examples, see the service layer exploration results in the conversation history above.*
