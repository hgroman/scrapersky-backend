# ScraperSky Scheduler Architecture - Complete Documentation

**Generated:** 2025-11-07  
**Analysis Depth:** Very Thorough (All Scheduler Files Reviewed)  
**Focus:** APScheduler Infrastructure, Scheduler Services, Configuration, and Workflow Orchestration

---

## Table of Contents

1. [Scheduler Infrastructure Setup](#scheduler-infrastructure-setup)
2. [Individual Scheduler Documentation](#individual-scheduler-documentation)
3. [Configuration and Tuning](#configuration-and-tuning)
4. [Workflow Orchestration](#workflow-orchestration)
5. [Critical Issues and Anti-Patterns](#critical-issues-and-anti-patterns)
6. [Recommendations](#recommendations)

---

## Scheduler Infrastructure Setup

### APScheduler Core Engine

**File:** `/home/user/scrapersky-backend/src/scheduler_instance.py`

#### Initialization & Architecture

- **Type:** AsyncIOScheduler (APScheduler)
- **Timezone:** UTC
- **Singleton Pattern:** Single shared instance used across entire application
- **Guardian Classification:** NUCLEAR SHARED SERVICE
  - Serves ALL Workflows (WF1-WF7)
  - Deletion breaks entire ScraperSky automation pipeline
  - Protection Level: NUCLEAR

#### Core Components

```python
scheduler = AsyncIOScheduler(timezone="UTC")
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
```

**Event Listener:** `job_listener()` function
- Logs successful job executions at INFO level
- Logs job exceptions at ERROR level with full traceback
- Provides basic observability for background jobs

#### Lifecycle Management

**Start Function:** `start_scheduler()`
```
Behavior:
- Checks if scheduler.running == False before starting
- Logs "Shared APScheduler started" on successful start
- Logs warning if already running
- Attempts graceful shutdown if start fails partially
```

**Shutdown Function:** `shutdown_scheduler()`
```
Behavior:
- Checks if scheduler.running == True before shutdown
- Uses wait=False to allow shutdown during lifespan context exit
- Prevents blocking the FastAPI shutdown sequence
- Logs all state transitions
```

#### Lifespan Integration

**File:** `/home/user/scrapersky-backend/src/main.py`

**Integration Pattern:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the ScraperSky API - Lifespan Start")
    start_scheduler()
    
    # Add jobs from each module
    setup_domain_scheduler()
    setup_sitemap_scheduler()
    setup_domain_sitemap_submission_scheduler()
    setup_sitemap_import_scheduler()
    setup_page_curation_scheduler()
    
    yield  # Application runs here
    
    logger.info("Shutting down the ScraperSky API - Lifespan End")
    shutdown_scheduler()
```

**Key Properties:**
- Scheduler starts BEFORE any jobs are registered
- All job registration happens in lifespan before yield
- Scheduler shuts down AFTER all other cleanup
- Job registration failures are caught and logged individually (don't crash app)

---

## Individual Scheduler Documentation

### WF3/WF2/WF5 - Domain Scheduler

**File:** `/home/user/scrapersky-backend/src/services/domain_scheduler.py`

**Purpose:** Processes domains with 'pending' status for metadata extraction

#### Processing Workflow

**3-Phase Approach (Critical Pattern):**

**Phase 1: Quick DB Transaction (Fetch & Mark)**
- Fetches domains where `status == DomainStatusEnum.pending`
- Locks rows with `with_for_update(skip_locked=True)`
- Marks all as `processing` immediately
- Clears previous errors
- **Duration:** Seconds
- **Connection:** HELD briefly

**Phase 2: Metadata Extraction (Slow Operations)**
- Database connection is RELEASED
- Calls `detect_site_metadata(domain_url, max_retries=3)` for each domain
- External HTTP requests to extract metadata
- NO database operations during this phase
- **Duration:** Minutes (slow)
- **Connection:** RELEASED

**Phase 3: Quick DB Transaction (Update Results)**
- Re-acquires database connection
- Updates domains with extracted metadata
- Uses `Domain.update_from_metadata()` method
- Sets status to `completed` or `error`
- **CRITICAL:** Sets `sitemap_analysis_status = SitemapAnalysisStatusEnum.queued` (WF4→WF5 trigger)
- **Duration:** Seconds
- **Connection:** HELD briefly

#### Selection Criteria

| Field | Value | Notes |
|-------|-------|-------|
| status | `DomainStatusEnum.pending` | Only pending domains |
| limit | Configurable (default: 50) | Batch size control |
| order_by | `updated_at ASC` | Process oldest first |
| locking | `skip_locked=True` | Avoid race conditions |

#### Status Transitions

```
pending → processing → completed (success)
                    ↘ error (failure)
```

#### Error Handling

- Wraps each domain in try-except
- Captures error message (truncated to 1024 chars)
- Sets domain status to `error` with error message
- Logs full traceback at ERROR level
- Session transactions ensure atomicity

#### Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| `DOMAIN_SCHEDULER_INTERVAL_MINUTES` | 1 | Job frequency |
| `DOMAIN_SCHEDULER_BATCH_SIZE` | 50 | Domains per batch |
| `DOMAIN_SCHEDULER_MAX_INSTANCES` | 3 | Concurrent executions |

#### APScheduler Registration

```python
scheduler.add_job(
    process_pending_domains,
    trigger=IntervalTrigger(minutes=interval_minutes),
    id="process_pending_domains",
    name="Process Pending Domains",
    replace_existing=True,
    max_instances=max_instances,
    coalesce=True,
    misfire_grace_time=60,
    kwargs={"limit": batch_size}
)
```

**Key Parameters:**
- `coalesce=True` - Skip missed runs if scheduler paused
- `misfire_grace_time=60` - 1-minute grace period for delayed execution
- `max_instances=3` - Allow up to 3 concurrent domain processing jobs

#### Workflow Triggers

**Output:** WF4 Trigger
- Sets `Domain.sitemap_analysis_status = queued` for downstream sitemap analysis
- Enables pipeline continuation: WF3 → WF4 → WF5

---

### WF2/WF3/WF5 - Sitemap Scheduler (Multi-Purpose)

**File:** `/home/user/scrapersky-backend/src/services/sitemap_scheduler.py`

**CRITICAL WARNING:** Nuclear Shared Service
- Serves 3 workflows simultaneously (WF2, WF3, WF5)
- Single point of failure for multiple pipelines
- Needs architectural refactoring to reduce risk

**Purpose:** Processes sitemaps, deep scans, and domain extractions in one unified batch

#### Processing Workflow

**Three Sub-Workflows in One Batch:**

**Sub-Workflow 1: Legacy Sitemap Jobs (DISABLED)**
- Status: Commented out as per PRD v1.2
- Reason: Replaced by modern SDK-based `sitemap_import_scheduler`
- Code: Lines 130-214 (commented)

**Sub-Workflow 2: Deep Scans (Curation-Driven)**

Selection:
- Model: `Place`
- Status: `deep_scan_status == GcpApiDeepScanStatusEnum.Queued`
- Limit: Configurable batch size
- Locking: `with_for_update(skip_locked=True)`

Processing:
1. Marks Place as `Processing`
2. Calls `PlacesDeepService.process_single_deep_scan(place_id, tenant_id)`
3. Updates status to `Completed` or `Error`
4. Stores error message if failed

Status Updates:
```
Queued → Processing → Completed (success)
                   ↘ Error (failure)
```

**Sub-Workflow 3: Domain Extractions**

Selection:
- Model: `LocalBusiness`
- Status: `domain_extraction_status == DomainExtractionStatusEnum.Queued`
- Limit: Configurable batch size
- Locking: `with_for_update(skip_locked=True)`

Processing:
1. Marks LocalBusiness as `Processing`
2. Calls `LocalBusinessToDomainService.create_pending_domain_from_local_business()`
3. Updates status to `Completed` or `Error`

Status Updates:
```
Queued → Processing → Completed (success)
                   ↘ Error (failure)
```

#### Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| `SITEMAP_SCHEDULER_INTERVAL_MINUTES` | 1 | Job frequency |
| `SITEMAP_SCHEDULER_BATCH_SIZE` | 25 | Items per type per batch |
| `SITEMAP_SCHEDULER_MAX_INSTANCES` | 3 | Concurrent executions |

#### APScheduler Registration

```python
scheduler.add_job(
    process_pending_jobs,  # Handles ALL 3 sub-workflows
    trigger=IntervalTrigger(minutes=interval_minutes),
    id="process_pending_jobs",
    name="Process Sitemaps, DeepScans, DomainExtractions",
    replace_existing=True,
    max_instances=max_instances,
    coalesce=True,
    misfire_grace_time=60,
    kwargs={"limit": batch_size}
)
```

#### Session Management

- Uses `get_background_session()` context manager
- Each sub-workflow runs within its own session
- Context manager auto-commits on success, auto-rollbacks on exception
- Proper transaction boundaries

#### Error Handling

- Individual try-except blocks per item
- Failed items marked as `Error` with message
- Outer try-except handles batch-level failures
- Full statistics logged at completion

#### Statistics Logged

```
Sitemaps: Processed=X, Successful=Y
Deep Scans: Processed=X, Successful=Y
Domain Extractions: Processed=X, Successful=Y
```

---

### WF4 - Domain Sitemap Submission Scheduler

**File:** `/home/user/scrapersky-backend/src/services/domain_sitemap_submission_scheduler.py`

**CRITICAL COMPONENT:** WF4 Domain Curation
- Processes domains queued for sitemap analysis
- Fixed to use proper adapter service (not email scraping)
- Guardian: WF4_Domain_Curation_Guardian_v3.md

#### Processing Workflow

**Two-Phase Approach:**

**Phase 1: Fetch Domains (Quick)**
- Selects domains where `sitemap_analysis_status == SitemapAnalysisStatusEnum.queued`
- Fetches only IDs (minimal data)
- Reads 10 domains max per batch
- No locks held during selection

**Phase 2: Process Each Domain**

For each domain:
1. Lock domain with `with_for_update(skip_locked=True)`
2. Update status to `processing`
3. Call `DomainToSitemapAdapterService.submit_domain_to_legacy_sitemap()`
4. Check adapter result
5. Update status based on adapter result:
   - `submitted` - Adapter successfully queued domain
   - `failed` - Adapter encountered error

#### Selection Criteria

| Field | Value | Notes |
|-------|-------|-------|
| sitemap_analysis_status | `SitemapAnalysisStatusEnum.queued` | WF4→WF5 handoff |
| limit | 10 | Fixed batch size |
| order_by | `updated_at ASC` | Oldest first |
| locking | `with_for_update(skip_locked=True)` | Row-level locking |

#### Status Transitions

```
queued → processing → submitted (success)
                   ↘ failed (error)
```

#### Session Management

- Each domain gets its own session
- Session begin/end per domain
- Explicit error tracking
- Full context manager usage

#### Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| Interval | 1 minute | Fixed (hardcoded) |
| Max Instances | 1 | Single concurrent execution |
| Coalesce | True | Skip missed runs |

#### APScheduler Registration

```python
scheduler.add_job(
    process_pending_domain_sitemap_submissions,
    trigger=IntervalTrigger(minutes=1),
    id="process_pending_domain_sitemap_submissions",
    name="Domain Sitemap Submission Scheduler",
    replace_existing=True,
    max_instances=1,
    coalesce=True,
    misfire_grace_time=60
)
```

#### Critical Bugfix History

**June 28, 2025 Crisis:** Domain scheduler was calling email scraping instead of sitemap analysis
- **Symptom:** WF4 domains never reached WF5
- **Root Cause:** Broken adapter substitution
- **Fix:** Restored `DomainToSitemapAdapterService.submit_domain_to_legacy_sitemap()`
- **Validation:** WF4→WF5 pipeline now functional

#### Adapter Service Integration

Uses `DomainToSitemapAdapterService`:
- Responsible for submitting domains to sitemap analysis
- Updates domain status via setattr
- Returns success/failure flag
- Error handling with logging

---

### WF6 - Sitemap Import Scheduler (Modern SDK)

**File:** `/home/user/scrapersky-backend/src/services/sitemap_import_scheduler.py`

**Purpose:** Modern SDK-based sitemap URL extraction and import

**Key Characteristic:** Uses reusable `run_job_loop` SDK pattern

#### Processing Workflow

Uses generic `run_job_loop()` function from curation SDK:

**Phase 1: Batch Fetch & Mark (Atomic)**
- Selects `SitemapFile` where `sitemap_import_status == SitemapImportProcessStatusEnum.Queued`
- Marks all as `Processing` in single transaction
- Collects IDs for phase 2

**Phase 2: Individual Processing**
- Calls `SitemapImportService.process_single_sitemap_file(sitemap_file_id, session)`
- Service handles its own transaction
- On error, service status is marked as `Error` with message
- On success, service marks status as `Complete`

#### Selection Criteria

| Field | Value | Notes |
|-------|-------|-------|
| sitemap_import_status | `SitemapImportProcessStatusEnum.Queued` | Ready for processing |
| limit | Configurable | Default: 20 |
| order_by | `updated_at ASC` | Oldest first |

#### Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES` | 1 | Job frequency |
| `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE` | 20 | Items per batch |
| `SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES` | 1 | Single concurrent |

#### APScheduler Registration

```python
scheduler.add_job(
    process_pending_sitemap_imports,
    trigger="interval",
    minutes=settings.SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES,
    id="process_sitemap_imports",
    name="Process Pending Sitemap Imports",
    replace_existing=True,
    max_instances=settings.SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES,
    misfire_grace_time=1800  # 30 minutes
)
```

#### Session Management Pattern

- Handled entirely by `run_job_loop()` SDK
- Provides sessions to both:
  - Fetch phase (reads)
  - Process phase (individual processing)
- Automatic error handling sessions

#### Service Contract

`SitemapImportService.process_single_sitemap_file(sitemap_file_id, session)`:
- Accepts UUID ID and AsyncSession
- Handles own transaction
- Updates status field directly
- Updates error field on failure
- Expected to commit/rollback within function

#### Statistics Logged

```
Success: X, Failed: Y, Total: Z
```

---

### WF7 - Page Curation Scheduler

**File:** `/home/user/scrapersky-backend/src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`

**Purpose:** Process pages queued for curation (WF7)

**Key Characteristic:** Uses SDK `run_job_loop` pattern (modern)

#### Processing Workflow

Uses `run_job_loop()` with these parameters:

**Phase 1: Batch Fetch & Mark**
- Selects `Page` where `page_processing_status == PageProcessingStatus.Queued`
- Marks all as `Processing`
- Collects batch of IDs

**Phase 2: Individual Processing**
- Calls `PageCurationService.process_single_page_for_curation(page_id, session)`
- Service handles curation processing
- Status updated based on result

#### Selection Criteria

| Field | Value | Notes |
|-------|-------|-------|
| page_processing_status | `PageProcessingStatus.Queued` | Ready for curation |
| limit | Configurable | Default: 10 |
| order_by | `updated_at ASC` | Oldest first |
| status_field_name | "page_processing_status" | Flexible enum field |
| error_field_name | "page_processing_error" | Flexible error field |

#### Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| `PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES` | 1 | Job frequency |
| `PAGE_CURATION_SCHEDULER_BATCH_SIZE` | 10 | Pages per batch |
| `PAGE_CURATION_SCHEDULER_MAX_INSTANCES` | 1 | Single concurrent |

#### APScheduler Registration

```python
scheduler.add_job(
    process_page_curation_queue,
    "interval",
    minutes=settings.PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES,
    id="v2_page_curation_processor",
    replace_existing=True,
    max_instances=settings.PAGE_CURATION_SCHEDULER_MAX_INSTANCES
)
```

#### Status Transitions

```
Queued → Processing → Complete (success)
                   ↘ Error (failure)
```

#### Service Contract

`PageCurationService.process_single_page_for_curation(page_id, session)`:
- Processes single page for curation
- Updates `page_processing_status`
- Expected to be SDK-compatible (accepts ID, session)

---

### Infrastructure - Curation SDK Job Loop

**File:** `/home/user/scrapersky-backend/src/common/curation_sdk/scheduler_loop.py`

**Purpose:** Reusable generic job processing loop for modern schedulers

**Usage Pattern:**
- Used by: `sitemap_import_scheduler` and `page_curation_scheduler`
- Type-safe generic implementation with TypeVar bounds
- Handles batch fetch → individual processing → error handling

#### Generic Function Signature

```python
async def run_job_loop(
    model: Type[T],                           # SQLAlchemy model (e.g., SitemapFile)
    status_enum: Type[Enum],                  # Enum class (e.g., SitemapImportProcessStatusEnum)
    queued_status: Enum,                      # Status value for "ready" (e.g., .Queued)
    processing_status: Enum,                  # Status value for "in progress"
    completed_status: Enum,                   # Status value for "done"
    failed_status: Enum,                      # Status value for "failed"
    processing_function: Callable[            # Function to process one item
        [UUID, AsyncSession], Coroutine[Any, Any, None]
    ],
    batch_size: int,                          # How many to fetch per batch
    order_by_column: Optional[ColumnElement], # Sort order
    status_field_name: str,                   # Column name for status
    error_field_name: str                     # Column name for error message
) -> None:
```

#### Execution Flow

**Phase 1: Fetch & Mark (Single Transaction)**
```
1. Get session
2. Start transaction
3. Fetch records where status == queued_status, limit batch_size
4. For each record ID: UPDATE status = processing_status
5. Commit transaction
6. Close session
```

**Phase 2: Process Each Item (Separate Transactions)**
```
For each item ID:
  1. Get new session
  2. Call processing_function(item_id, session)
  3. Function is responsible for its own transaction
  4. On success: count as successful
  5. On error:
     a. Attempt to get error session
     b. UPDATE status = failed_status, error = error_message
     c. Close error session
  6. Close main session
```

#### Error Handling Strategy

- **Item-level errors:** Caught in try-except, marked as failed, continue to next
- **Error session failures:** Logged as CRITICAL, item left in Processing state
- **Fetch phase failures:** Return early, no processing happens
- **Graceful degradation:** Process what can be processed

#### Key Safety Features

- `skip_locked=True` prevents race conditions
- Separate sessions per item prevent timeout
- Explicit transaction boundaries
- Error recovery sessions
- Full logging at each phase

---

## Configuration and Tuning

### Environment Variables (from settings.py)

**Domain Scheduler:**
```python
DOMAIN_SCHEDULER_INTERVAL_MINUTES: int = 1
DOMAIN_SCHEDULER_BATCH_SIZE: int = 50
DOMAIN_SCHEDULER_MAX_INSTANCES: int = 3
```

**Sitemap Scheduler (Multi-Purpose):**
```python
SITEMAP_SCHEDULER_INTERVAL_MINUTES: int = (
    # Value from config - not visible in grep
)
SITEMAP_SCHEDULER_BATCH_SIZE: int = 25
SITEMAP_SCHEDULER_MAX_INSTANCES: int = 3
```

**Domain Sitemap Submission Scheduler:**
```python
DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES: int = (
    # Value from config
)
DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE: int = 10
# Max instances: hardcoded to 1 in setup function
```

**Sitemap Import Scheduler:**
```python
SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES: int = 1
SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE: int = 20
SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES: int = 1
```

**Page Curation Scheduler:**
```python
PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES: int = 1
PAGE_CURATION_SCHEDULER_BATCH_SIZE: int = 10
PAGE_CURATION_SCHEDULER_MAX_INSTANCES: int = 1
```

### Default Tuning Values

| Scheduler | Interval | Batch Size | Max Instances | Notes |
|-----------|----------|-----------|---------------|-------|
| Domain | 1 min | 50 | 3 | Highest throughput |
| Sitemap | 1 min | 25 | 3 | Multi-purpose |
| Domain Sitemap | 1 min | 10 | 1 (fixed) | Sequential |
| Sitemap Import | 1 min | 20 | 1 | SDK-based |
| Page Curation | 1 min | 10 | 1 | SDK-based |

### Overlap Protection

**APScheduler Parameters Used:**

| Parameter | Value | Behavior |
|-----------|-------|----------|
| `coalesce` | `True` | Skip missed executions if backlog exists |
| `misfire_grace_time` | 60 seconds | Grace period for delayed execution |
| `max_instances` | 1-3 | Prevent concurrent runs (when set to 1) |

**Race Condition Prevention:**

```python
# In database queries
.with_for_update(skip_locked=True)  # Row-level locking
```

Behavior:
- Locks rows being processed
- Skips rows already locked by other instances
- Prevents duplicate processing

---

## Workflow Orchestration

### Workflow Dependency Graph

```
WF1: Single Search (Place Search)
     ↓
WF3: Place Staging (Domain Discovery) [Uses sitemap_scheduler]
     ↓
WF4: Domain Curation (Sitemap Analysis) [Uses domain_sitemap_submission_scheduler]
     ↓
WF5: Sitemap Curation (URL Extraction) [Uses sitemap_import_scheduler]
     ↓
WF6: Sitemap Import (Deep Scraping) [Uses sitemap_import_scheduler output]
     ↓
WF7: Page Curation (Contact Extraction) [Uses page_curation_scheduler]
     ↓
WF8: Contact CRUD (Storage)

Parallel: Deep Scans (WF2?) [Uses sitemap_scheduler]
```

### Scheduler Execution Sequence

**Every 1 Minute (Default Interval):**

```
Time T+0min:
  └─ domain_scheduler runs
     └─ Marks domains as processing
     └─ Extracts metadata (slow, async)
     └─ Marks completed domains
     └─ QUEUES for WF4: sitemap_analysis_status = queued
  
  └─ sitemap_scheduler runs (3 sub-workflows)
     ├─ deep_scan workflow
     │  └─ Processes Place.deep_scan_status = Queued
     │  └─ Calls PlacesDeepService
     │  └─ Updates Place status
     │
     ├─ domain_extraction workflow
     │  └─ Processes LocalBusiness.domain_extraction_status = Queued
     │  └─ Creates pending Domain records
     │
     └─ legacy_sitemap workflow (DISABLED)
  
  └─ domain_sitemap_submission_scheduler runs
     └─ Processes Domain.sitemap_analysis_status = queued
     └─ Calls DomainToSitemapAdapterService
     └─ Updates Domain.sitemap_analysis_status → submitted/failed
  
  └─ sitemap_import_scheduler runs
     └─ Processes SitemapFile.sitemap_import_status = Queued
     └─ Calls SitemapImportService per file
     └─ Extracts URLs, creates Page records
     └─ Updates SitemapFile status
  
  └─ page_curation_scheduler runs
     └─ Processes Page.page_processing_status = Queued
     └─ Calls PageCurationService
     └─ Performs curation
     └─ Updates Page status

Time T+1min: Repeat all above
```

### Data Flow Between Schedulers

**WF3 → WF4 Handoff:**
```
Domain Scheduler Output:
  Domain.status = completed
  Domain.sitemap_analysis_status = queued ← TRIGGER FOR WF4

Domain Sitemap Submission Scheduler Input:
  Domain.sitemap_analysis_status = queued
```

**WF4 → WF5 Handoff:**
```
Domain Sitemap Submission Scheduler Output:
  Domain.sitemap_analysis_status = submitted/failed

Sitemap Import Scheduler Input:
  SitemapFile.sitemap_import_status = queued
  (Created by external process, not domain_scheduler)
```

**WF5 → WF7 Handoff:**
```
Sitemap Import Scheduler Output:
  Page records created from sitemap URLs
  Page.page_processing_status = Queued (initial)

Page Curation Scheduler Input:
  Page.page_processing_status = Queued
```

### Status Enum Mapping

**Standard Curation Status Values:**
```
New → Queued → Processing → Complete/Error
```

**Processing Status Values:**
```
Queued → Processing → Complete/Error
```

**Custom Status Values by Workflow:**

| Workflow | Status Field | Values |
|----------|--------------|--------|
| WF1 | N/A | N/A |
| WF2 | deep_scan_status | Queued, Processing, Completed, Error |
| WF3 | N/A | N/A |
| WF4 | sitemap_analysis_status | pending, queued, processing, submitted, failed |
| WF5 | sitemap_import_status | Queued, Processing, Complete, Error |
| WF6 | sitemap_import_status | (same as WF5) |
| WF7 | page_processing_status | Queued, Processing, Complete, Error, Filtered |
| WF8 | N/A | N/A |

---

## Critical Issues and Anti-Patterns

### CRITICAL ISSUE #1: Multi-Workflow Single Scheduler (Nuclear Risk)

**File:** `/home/user/scrapersky-backend/src/services/sitemap_scheduler.py`

**Problem:**
- Single scheduler processes 3 different workflows (WF2, WF3, WF5)
- Failure in one sub-workflow doesn't affect others (good error handling)
- BUT: Complex interdependencies increase maintenance risk
- Single point of failure for multiple pipelines

**Risk Assessment:** HIGH
- Affects: WF2 (Deep Scans), WF3 (Domain Extraction), WF5 (Sitemap Processing)
- Impact: Any production issue requires understanding all 3 workflows
- Recovery: Single fix must address cross-workflow concerns

**Recommendation:** Refactor into 3 separate schedulers:
1. `deep_scan_scheduler.py`
2. `domain_extraction_scheduler.py`
3. `legacy_sitemap_scheduler.py` (if re-enabled)

---

### CRITICAL ISSUE #2: Database Connection Hold Anti-Pattern (Partially Resolved)

**File:** `/home/user/scrapersky-backend/src/services/domain_scheduler.py`

**Previous Issue (AP-20250730-002):**
- Holding database connections during slow external API calls
- Caused: `asyncpg.exceptions.ConnectionDoesNotExistError`
- Symptom: Timeout failures in domain metadata extraction

**Current State (RESOLVED):**
- Domain scheduler now uses 3-phase approach
- Phase 1 & 3: Quick DB operations (seconds)
- Phase 2: No DB connections held during `detect_site_metadata()` call
- Pattern implemented correctly: ✓

**Remaining Risk:**
- Other schedulers may have similar issues
- `PlacesDeepService` holds connection during processing
- Need audit of other services

---

### CRITICAL ISSUE #3: Hardcoded Tenant ID in Service Calls

**Files Affected:**
- `/home/user/scrapersky-backend/src/services/sitemap_scheduler.py` (line 182)
- `/home/user/scrapersky-backend/src/services/places_search_service.py`
- `/home/user/scrapersky-backend/src/services/places_storage_service.py`

**Problem:**
```python
# In sitemap_scheduler.py line 182
user_id="5905e9fe-6c61-4694-b09a-6602017b000a"  # Hardcoded System/Scheduler User
```

**Issues:**
- System user UUID hardcoded
- Not configurable
- Makes audit trail opaque
- No way to distinguish scheduler-created records from user-created

**Risk Assessment:** MEDIUM
- Security: Non-critical (system user is expected)
- Maintainability: Poor (hardcoded values)
- Auditability: Reduced (can't configure audit user)

**Recommendation:**
1. Move to `settings.SCHEDULER_SYSTEM_USER_ID`
2. Make configurable via environment variable
3. Add validation that user exists

---

### CRITICAL ISSUE #4: Duplicate Domain Sitemap Submission Schedulers

**Files:**
- `/home/user/scrapersky-backend/src/services/domain_sitemap_submission_scheduler.py`
- `/home/user/scrapersky-backend/src/services/domain_sitemap_submission_scheduler_fixed.py`

**Problem:**
- Two versions of same scheduler exist
- Only `domain_sitemap_submission_scheduler.py` is registered in `main.py`
- `_fixed.py` version uses different session management (fixed session mode)
- Unclear which one should be used

**Status:**
- Current (registered): Uses `get_background_session()` with nested transactions
- Fixed version: Uses `get_fixed_scheduler_session()` with session mode

**Risk Assessment:** HIGH
- Code duplication leads to maintenance burden
- Unclear which approach is correct
- Potential to use wrong version during refactoring

**Recommendation:**
1. Determine correct session management approach
2. Delete old version
3. Update documentation with chosen pattern
4. Consider Docker vs. production session mode requirements

---

### CRITICAL ISSUE #5: Missing Configuration for Some Schedulers

**Problem:**
```python
# domain_sitemap_submission_scheduler.py has HARDCODED values:
interval_minutes = 1  # Not from settings
batch_size = 10      # Uses settings (good)
max_instances = 1    # Hardcoded (should be configurable)
```

**Current State:**
- Domain scheduler: ✓ All configurable
- Sitemap scheduler: ✓ All configurable
- Domain Sitemap Submission: ✗ Partially hardcoded
- Sitemap Import: ✓ All configurable
- Page Curation: ✓ All configurable

**Risk Assessment:** LOW
- Interval being hardcoded to 1 minute is reasonable
- But inconsistent with other schedulers

**Recommendation:**
- Add to settings:
  ```python
  DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES: int = 1
  DOMAIN_SITEMAP_SCHEDULER_MAX_INSTANCES: int = 1
  ```
- Update scheduler to use settings values

---

### CRITICAL ISSUE #6: Error Recovery in SDK Job Loop

**File:** `/home/user/scrapersky-backend/src/common/curation_sdk/scheduler_loop.py`

**Problem (Lines 157-189):**
```python
# If processing fails, attempts to get error session
error_session = await get_session()
if error_session is None:
    logger.error("Failed to get error session for item")
    continue  # Item left in Processing state ← ZOMBIE
```

**Issue:**
- If error session can't be obtained, item stays in `Processing` status
- Creates "zombie" records stuck in intermediate state
- Won't be retried (Processing != Queued)
- Manual intervention required

**Risk Assessment:** MEDIUM
- Occurs when database is already under stress
- Probability: Low (but increases with scale)
- Impact: Stuck records require manual cleanup

**Recommendation:**
1. Add monitoring for stuck Processing items
2. Implement cleanup job to reset old Processing items to Queued
3. Add dead-letter queue for permanently failed items
4. Log zombie items to dedicated error table

---

### CRITICAL ISSUE #7: Missing Scheduler for Domain Sitemap Submission (WF4 Specific)

**Based on WF4 Cheat Sheet:**

**Current Gap:**
- `domain_scheduler.py` processes Domain.status (general)
- `domain_sitemap_submission_scheduler_fixed.py` handles WF4-specific logic
- **Missing:** Dedicated `domain_curation_scheduler.py` as per architectural standard

**Impact:**
- WF4 workflow deviates from standard pattern
- No dedicated service for domain curation logic
- Business logic mixed between router and scheduler

**Current Workaround:**
- Using adapter service pattern
- Works but not ideal architecture

---

### ANTI-PATTERN #1: Async Task Timeout Without Mechanism

**File:** `/home/user/scrapersky-backend/src/services/sitemap_scheduler.py` (Line 65)

```python
SITEMAP_JOB_TIMEOUT_SECONDS = 55
# Defined but never used
```

**Problem:**
- Timeout value defined but commented-out code doesn't use it
- No actual timeout mechanism for sitemap processing
- Could hang indefinitely

**Current Implementation:**
- Uses context manager auto-commit/rollback
- No explicit timeout protection
- Service-level timeout would help prevent hangs

---

### ANTI-PATTERN #2: Transaction Nesting in Some Flows

**File:** `/home/user/scrapersky-backend/src/services/domain_sitemap_submission_scheduler.py`

```python
async with get_background_session() as session_fetch:
    # Read-only query
    stmt_fetch = ...
    result = await session_fetch.execute(stmt_fetch)
    # No explicit transaction here - relies on context manager
```

vs.

```python
async with get_background_session() as session_inner:
    async with session_inner.begin():  # NESTED TRANSACTION
        # Read + Write
```

**Issue:**
- Inconsistent transaction management patterns
- Some use context manager auto-begin/end
- Some nest explicit `begin()` blocks
- Confusing for maintenance

**Recommendation:**
- Standardize on one pattern:
  - Option A: Context manager only (current `run_job_loop` pattern)
  - Option B: Explicit begin() for clarity

---

## Recommendations

### Priority 1: Immediate Actions

1. **Remove Duplicate Scheduler File**
   - Delete `domain_sitemap_submission_scheduler_fixed.py`
   - Clarify correct session management approach
   - Document decision in code comments

2. **Add Monitoring/Alerting for Stuck Jobs**
   - Monitor for items stuck in Processing > N minutes
   - Alert on scheduler job failures
   - Track job duration statistics

3. **Configure System User ID**
   - Move hardcoded UUID to settings
   - Make schedulable user configurable
   - Add validation

4. **Add Missing Configuration**
   - `DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES`
   - `DOMAIN_SITEMAP_SCHEDULER_MAX_INSTANCES`
   - Update scheduler to use settings

### Priority 2: Medium-term Refactoring

1. **Separate Multi-Purpose Scheduler**
   - Split `sitemap_scheduler.py` into:
     - `deep_scan_scheduler.py` (WF2)
     - `domain_extraction_scheduler.py` (WF3/WF5)
     - `legacy_sitemap_scheduler.py` (if re-enabling)
   - Reduce complexity and risk

2. **Create Dedicated Domain Curation Service**
   - Create `domain_curation_service.py`
   - Extract logic from router
   - Follow standard service pattern
   - Aligns with architectural standards

3. **Standardize Session Management**
   - Document chosen pattern (context manager vs explicit begin())
   - Apply consistently across all schedulers
   - Update `run_job_loop` pattern documentation

4. **Implement Zombie Record Cleanup**
   - Add periodic job to reset stuck Processing records
   - Monitor for permanently failed items
   - Create dead-letter queue for investigation

### Priority 3: Long-term Improvements

1. **Add Scheduler Observability**
   - Track job duration metrics
   - Monitor queue sizes (Queued items count)
   - Alert on metric anomalies
   - Dashboard for scheduler health

2. **Implement Scheduler Backpressure**
   - Monitor queue buildup
   - Adjust batch sizes dynamically
   - Prevent cascading failures

3. **Add Dead-Letter Queue Pattern**
   - Items that fail N times go to DLQ
   - Separate investigation workflow
   - Prevents infinite retry loops

4. **Document Workflow Dependencies**
   - Create formal workflow dependency graph
   - Document status field mappings
   - Create workflow troubleshooting guide
   - Add architecture decision records (ADRs)

---

## Summary Table: Scheduler Overview

| Scheduler | Workflow | Trigger | Model | Status Field | Batch | Interval | Max Inst |
|-----------|----------|---------|-------|--------------|-------|----------|----------|
| domain | WF3 | DB Status | Domain | status | 50 | 1m | 3 |
| sitemap | WF2/WF3/WF5 | DB Status | Multi | multi | 25 | 1m | 3 |
| domain_sitemap_submission | WF4 | DB Status | Domain | sitemap_analysis_status | 10 | 1m | 1 |
| sitemap_import | WF6 | DB Status | SitemapFile | sitemap_import_status | 20 | 1m | 1 |
| page_curation | WF7 | DB Status | Page | page_processing_status | 10 | 1m | 1 |

---

## Conclusion

The ScraperSky scheduler architecture is **functional but has significant technical debt**:

**Strengths:**
- Centralized APScheduler instance prevents conflicts
- Proper async pattern with AsyncIOScheduler
- Good error handling in most scheduler jobs
- SDK job loop pattern is modern and reusable
- 3-phase domain scheduler solves connection hold issue
- Row-level locking prevents race conditions

**Weaknesses:**
- Multi-workflow single scheduler increases risk
- Configuration inconsistencies between schedulers
- Code duplication (two domain_sitemap_submission versions)
- Duplicate status field definitions in models
- Missing zombie record cleanup mechanism
- Hardcoded system user IDs
- Inconsistent transaction management patterns

**Next Steps:**
1. Implement Priority 1 recommendations immediately
2. Plan Priority 2 refactoring for next sprint
3. Create monitoring/alerting for production visibility
4. Document workflow dependencies and troubleshooting

---

**End of Analysis**
