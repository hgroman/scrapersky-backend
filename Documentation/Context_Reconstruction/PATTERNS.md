# ScraperSky Code Patterns
**Purpose:** Correct vs incorrect patterns with real examples  
**Last Updated:** November 17, 2025

---

## Pattern 1: Service Communication

### ✅ CORRECT: Direct Service Call

**When to use:** Internal service-to-service communication

**Pattern:**
```python
# In scheduler or another service
service = SomeService()
result = await service.process(item_id, session)
```

**Benefits:**
- No network overhead
- No authentication needed
- Shares transaction context
- Can trigger background tasks
- Single point of failure

**Real Examples in Codebase:**
```python
# From deep_scan_scheduler.py
service = PlacesDeepService()
result = await service.process_single_deep_scan(
    place_id=str(place.place_id),
    tenant_id=str(place.tenant_id)
)

# From domain_sitemap_submission_scheduler.py (after fix)
adapter = DomainToSitemapAdapterService()
success = await adapter.submit_domain_to_legacy_sitemap(
    domain_id=domain.id,
    session=session
)
```

**File Locations:**
- `src/services/deep_scan_scheduler.py` lines 60-89
- `src/services/domain_sitemap_submission_scheduler.py`

---

### ❌ WRONG: HTTP Call Between Services

**Anti-Pattern:**
```python
# DON'T DO THIS
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v3/sitemap/scan",
        json={"base_url": domain},
        headers={"Authorization": f"Bearer {api_key}"}
    )
```

**Why This Fails:**
1. **Network overhead** - Unnecessary HTTP round-trip
2. **Authentication complexity** - Need to manage tokens
3. **Can't share transaction** - Separate database connections
4. **Doesn't trigger background tasks** - Critical issue!
5. **Multiple failure points** - Network, auth, endpoint availability

**Real Incident:**
- **Incident:** INCIDENT-2025-11-17-sitemap-jobs-not-processing
- **Duration:** 2+ months of silent failures (Sept 9 - Nov 17)
- **Symptom:** Jobs created but never processed
- **Root Cause:** HTTP call didn't trigger background processing
- **Fixed In:** Commit 1ffa371 (removed HTTP), then 9f091f6 (added trigger)

**Historical Code (BEFORE fix):**
```python
# From domain_to_sitemap_adapter_service.py (OLD VERSION)
api_key = settings.DEV_TOKEN
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
scan_endpoint = f"{INTERNAL_API_BASE_URL}/api/v3/sitemap/scan"

async with httpx.AsyncClient() as client:
    response = await client.post(
        scan_endpoint, 
        json=scan_payload, 
        headers=headers, 
        timeout=30.0
    )
```

**Why It Existed:** Legacy pattern before service layer matured

---

## Pattern 2: Background Task Triggering

### ✅ CORRECT: Trigger After Job Creation

**When to use:** After creating a job that needs immediate processing

**HTTP Endpoint Pattern:**
```python
# In FastAPI route (src/routers/modernized_sitemap.py)
from fastapi import BackgroundTasks

@router.post("/scan")
async def scan_sitemap(
    request: SitemapScrapingRequest,
    background_tasks: BackgroundTasks,
    ...
):
    # 1. Create job in database
    job_data = {...}
    await job_service.create(session, job_data)
    
    # 2. Initialize in memory
    _job_statuses[job_id] = {
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        ...
    }
    
    # 3. Trigger background processing
    background_tasks.add_task(
        process_domain_with_own_session,
        job_id=job_id,
        domain=request.base_url,
        user_id=current_user.get("id"),
        max_urls=request.max_pages
    )
```

**Direct Service Pattern:**
```python
# In service method (src/services/domain_to_sitemap_adapter_service.py)
import asyncio
from src.services.sitemap.processing_service import process_domain_with_own_session

# 1. Create job in database
job = await job_service.create(session, job_data)

# 2. Initialize in memory
from src.services.sitemap.processing_service import _job_statuses
_job_statuses[job_id] = {
    "status": "pending",
    "created_at": datetime.utcnow().isoformat(),
    ...
}

# 3. Trigger background processing
asyncio.create_task(
    process_domain_with_own_session(
        job_id=job_id,
        domain=domain.domain,
        user_id=None,  # System-initiated
        max_urls=1000
    )
)
```

**Critical:** All three steps are required!

**File Locations:**
- HTTP pattern: `src/routers/modernized_sitemap.py` lines 136-174
- Service pattern: `src/services/domain_to_sitemap_adapter_service.py` lines 104-130

---

### ❌ WRONG: Create Job Without Triggering

**Anti-Pattern:**
```python
# DON'T DO THIS
job_data = {
    "job_id": job_id,
    "job_type": "sitemap",
    "status": "pending",
    ...
}
job = await job_service.create(session, job_data)
# Missing: Background task trigger!
return True  # Looks successful but nothing will happen
```

**Why This Fails:**
- Job sits in "pending" state forever
- No errors logged (silent failure)
- Looks successful (job created, status updated)
- Downstream workflows never execute

**Real Incident:**
- **Incident:** INCIDENT-2025-11-17-sitemap-jobs-not-processing
- **Symptom:** 20 jobs stuck in "pending" for 13+ minutes
- **Root Cause:** Missing `asyncio.create_task()` call
- **Fixed In:** Commit 9f091f6
- **Impact:** 2+ months of no sitemap processing

**Historical Code (BEFORE fix):**
```python
# From domain_to_sitemap_adapter_service.py (BROKEN VERSION)
job = await job_service.create(session, job_data)

# Missing these lines:
# _job_statuses[job_id] = {...}
# asyncio.create_task(process_domain_with_own_session(...))

domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.submitted
return True  # FALSE SUCCESS
```

---

## Pattern 3: Dual-Status Updates

### ✅ CORRECT: Update Both Statuses

**When to use:** User selects an item for processing

**Pattern:**
```python
# From WF7_V3_L3_1of1_PagesRouter.py
for page in pages_to_update:
    # Update curation status (user decision)
    page.page_curation_status = request.status
    updated_count += 1
    
    # Dual-Status Update Pattern - trigger when Selected
    if request.status == PageCurationStatus.Selected:
        # Update processing status (system state)
        page.page_processing_status = PageProcessingStatus.Queued
        page.page_processing_error = None
        queued_count += 1
```

**Why:** Separates user decisions from system state

**File Locations:**
- Pages: `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py` lines 140-148
- Domains: `src/routers/v3/WF4_V3_L3_1of1_DomainsRouter.py` (similar pattern)

---

### ❌ WRONG: Update Only One Status

**Anti-Pattern:**
```python
# DON'T DO THIS
page.page_curation_status = PageCurationStatus.Selected
# Missing: page.page_processing_status = PageProcessingStatus.Queued
```

**Why This Fails:**
- Item marked "Selected" but never queued for processing
- Scheduler won't pick it up
- User expects processing but nothing happens

**Impact:** User confusion, manual intervention required

---

## Pattern 4: Error Handling in Schedulers

### ✅ CORRECT: Comprehensive Error Handling

**Pattern:**
```python
async def process_queue():
    """Standard scheduler pattern with error handling"""
    logger.info("Starting scheduler cycle")
    
    try:
        await run_job_loop(
            model=Model,
            status_enum=StatusEnum,
            queued_status=StatusEnum.Queued,
            processing_status=StatusEnum.Processing,
            completed_status=StatusEnum.Complete,
            failed_status=StatusEnum.Error,
            processing_function=service.process_single_item,
            batch_size=settings.BATCH_SIZE,
            order_by_column=asc(Model.updated_at),
            status_field_name="status_field",
            error_field_name="error_field",
        )
    except Exception as e:
        logger.exception(f"Critical error in scheduler: {e}")
        # Don't re-raise - let scheduler continue on next interval
    
    logger.info("Finished scheduler cycle")
```

**Why:** Prevents one error from stopping all future scheduler runs

**File Locations:**
- `src/services/sitemap_import_scheduler.py` lines 28-46
- `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`

---

### ❌ WRONG: No Error Handling

**Anti-Pattern:**
```python
# DON'T DO THIS
async def process_queue():
    # No try/except - exception will crash scheduler
    await run_job_loop(...)
```

**Why This Fails:**
- Single error stops all future processing
- Scheduler stops running silently
- No alerts or logging

---

## Pattern 5: Database Transaction Management

### ✅ CORRECT: Let SDK Manage Transactions

**Pattern:**
```python
# In service method called by SDK
async def process_single_item(
    self,
    item: Model,
    session: AsyncSession
) -> None:
    # Session provided by SDK - already in transaction
    # Make changes to item
    item.status = "Complete"
    item.result = "Success"
    
    # Create related records
    related = RelatedModel(...)
    session.add(related)
    
    # DON'T commit - SDK handles it
    # await session.commit()  # WRONG!
```

**Why:** SDK commits on success, rolls back on error automatically

**File Locations:**
- `src/services/sitemap_import_service.py`
- `src/services/WF7_V2_L4_1of2_PageCurationService.py`

---

### ❌ WRONG: Manual Transaction Management

**Anti-Pattern:**
```python
# DON'T DO THIS in SDK-called methods
async def process_single_item(self, item, session):
    item.status = "Complete"
    await session.commit()  # WRONG - SDK will commit again
```

**Why This Fails:**
- Double commits
- Can't roll back on error
- Breaks SDK's transaction management

---

## Pattern 6: Scheduler Configuration

### ✅ CORRECT: Use Settings and Shared Scheduler

**Pattern:**
```python
from src.scheduler_instance import scheduler
from src.config.settings import settings

def setup_scheduler():
    job_id = "process_items"
    
    scheduler.add_job(
        process_queue,
        trigger="interval",
        minutes=settings.SCHEDULER_INTERVAL_MINUTES,
        id=job_id,
        name="Process Items",
        replace_existing=True,
        max_instances=settings.SCHEDULER_MAX_INSTANCES,
        misfire_grace_time=1800,  # 30 minutes
    )
    
    logger.info(f"Added job '{job_id}' to shared scheduler")
```

**Why:**
- Centralized configuration
- Prevents overlapping runs (max_instances)
- Handles missed runs (misfire_grace_time)
- Uses shared scheduler instance

**File Locations:**
- `src/services/sitemap_import_scheduler.py` lines 53-85
- `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`

---

### ❌ WRONG: Hardcoded Values or Separate Scheduler

**Anti-Pattern:**
```python
# DON'T DO THIS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()  # Separate scheduler!

scheduler.add_job(
    process_queue,
    trigger="interval",
    minutes=5,  # Hardcoded!
    # Missing: max_instances, misfire_grace_time
)
```

**Why This Fails:**
- Can't change interval without code changes
- Multiple scheduler instances (resource waste)
- No protection against overlapping runs
- No handling of missed runs

---

## Pattern 7: Job Creation with Full Context

### ✅ CORRECT: Three-Step Job Creation

**Pattern:**
```python
# Step 1: Create in database
job_id = str(uuid.uuid4())
job_data = {
    "job_id": job_id,
    "job_type": "sitemap",
    "status": "pending",
    "created_by": user_id,  # or None for system
    "result_data": {
        "domain": domain,
        "max_pages": 1000,
    },
}
job = await job_service.create(session, job_data)

# Step 2: Initialize in memory
from src.services.sitemap.processing_service import _job_statuses
_job_statuses[job_id] = {
    "status": "pending",
    "created_at": datetime.utcnow().isoformat(),
    "domain": domain,
    "progress": 0.0,
    "metadata": {"sitemaps": []},
}

# Step 3: Trigger processing
import asyncio
asyncio.create_task(
    process_domain_with_own_session(
        job_id=job_id,
        domain=domain,
        user_id=user_id,
        max_urls=1000
    )
)
```

**Why All Three Steps:**
1. **Database:** Persistent record for audit trail
2. **Memory:** Fast status lookups without DB queries
3. **Trigger:** Actually starts the processing

**File Location:** `src/services/domain_to_sitemap_adapter_service.py` lines 86-130

---

### ❌ WRONG: Incomplete Job Creation

**Anti-Pattern:**
```python
# DON'T DO THIS - Missing steps 2 and 3
job = await job_service.create(session, job_data)
return True  # Job will never process!
```

**Real Incident:** INCIDENT-2025-11-17-sitemap-jobs-not-processing

---

## Pattern 8: Auto-Selection Logic

### ✅ CORRECT: Criteria-Based Auto-Selection

**Pattern:**
```python
# From sitemap_import_service.py
for url in extracted_urls:
    hb = categorize_url(url)  # Honeybee categorization
    
    page_data = {
        "url": url,
        "page_type": hb["category"],
        "priority_level": 3,  # default low
        "page_curation_status": PageCurationStatus.New,
        "page_processing_status": None,
    }
    
    # Auto-selection rules
    if (
        hb["category"] in {
            PageTypeEnum.CONTACT_ROOT,
            PageTypeEnum.CAREER_CONTACT,
            PageTypeEnum.LEGAL_ROOT
        }
        and hb["confidence"] >= 0.6
        and hb["depth"] <= 2
    ):
        # High-value page - auto-select
        page_data["page_curation_status"] = PageCurationStatus.Selected
        page_data["page_processing_status"] = PageProcessingStatus.Queued
        page_data["priority_level"] = 1
    
    pages_to_create.append(page_data)
```

**Why:**
- Automatically prioritizes high-value pages
- Reduces manual curation work
- Consistent criteria across system

**File Location:** `src/services/sitemap_import_service.py` lines 223-229

---

### ❌ WRONG: No Auto-Selection or Arbitrary Rules

**Anti-Pattern:**
```python
# DON'T DO THIS - No auto-selection
page_data = {
    "page_curation_status": PageCurationStatus.New,
    "page_processing_status": None,
}
# All pages require manual selection

# OR THIS - Arbitrary rules
if "contact" in url.lower():  # Too simplistic!
    page_data["page_curation_status"] = PageCurationStatus.Selected
```

**Why This Fails:**
- First approach: Too much manual work
- Second approach: Misses variations, false positives

---

## Pattern Summary

| Pattern | Correct | Wrong | Incident Reference |
|---------|---------|-------|-------------------|
| Service Communication | Direct call | HTTP call | INCIDENT-2025-11-17-http-service-calls |
| Background Tasks | asyncio.create_task() | Nothing | INCIDENT-2025-11-17-sitemap-jobs-not-processing |
| Dual-Status | Update both | Update one | N/A (design pattern) |
| Error Handling | Try/except in scheduler | No handling | N/A (best practice) |
| Transactions | Let SDK manage | Manual commits | N/A (best practice) |
| Scheduler Config | Use settings | Hardcode values | N/A (best practice) |
| Job Creation | Three steps | One or two steps | INCIDENT-2025-11-17-sitemap-jobs-not-processing |
| Auto-Selection | Criteria-based | None or arbitrary | N/A (feature) |

---

## How to Apply These Patterns

**When writing new code:**
1. Check this file for relevant patterns
2. Copy the ✅ CORRECT example
3. Adapt to your specific use case
4. Avoid the ❌ WRONG patterns

**When reviewing code:**
1. Check for anti-patterns
2. Reference incidents caused by anti-patterns
3. Suggest correct pattern with example

**When debugging:**
1. Check if code follows correct patterns
2. Look for anti-patterns that might cause issue
3. Reference related incidents

---

**For more patterns and anti-patterns, see:**
- [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md#service-communication-patterns)
- [INCIDENTS/](../INCIDENTS/) for real-world failures
- [DECISIONS/](../DECISIONS/) for architectural choices
