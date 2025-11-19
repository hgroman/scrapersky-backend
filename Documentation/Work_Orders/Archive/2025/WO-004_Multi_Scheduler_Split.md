# Work Order 004: Multi-Scheduler Split - Eliminate Single Point of Failure

**ID:** WO-004
**Created:** 2025-11-16
**Priority:** 🟠 HIGH
**Status:** OPEN
**Estimated Time:** 4 hours
**Assignee:** TBD

---

## Issue Summary

**HIGH RISK TECHNICAL DEBT:** The `sitemap_scheduler.py` scheduler handles THREE distinct workflows (WF2, WF3, WF5) in a single `process_pending_jobs()` function, creating a single point of failure that can break multiple critical pipelines simultaneously.

---

## Severity Classification

**Level:** 🟠 HIGH

**Risk:**
- If `sitemap_scheduler.py` crashes, 3 workflows stop simultaneously
- Debugging is complex due to multi-workflow logic in single function
- Resource contention between workflows (shared batch limits, timing)
- Cannot tune individual workflow performance independently
- Maintenance changes risk breaking multiple workflows

**Current Architecture Warning:**
```python
# File header comment (lines 2-14) explicitly warns:
"""
🚨 NUCLEAR SHARED SERVICE - Multi-Workflow Background Processor
==============================================================
⚠️  SERVES: WF2 (Deep Scans), WF3 (Domain Extraction), WF5 (Sitemap Import)
⚠️  DELETION BREAKS: 3 workflows simultaneously
⚠️  GUARDIAN DOC: WF0_Critical_File_Index.md (SHARED.2)
⚠️  MODIFICATION REQUIRES: Architecture team review

🔒 DISASTER VULNERABILITY: High - Serves multiple critical workflows
🔒 PROTECTION LEVEL: NUCLEAR - Changes affect 3 workflow pipelines
🔒 SPLIT NEEDED: Should be separated into workflow-specific processors
"""
```

---

## Current State Analysis

### File Structure

**File:** `src/services/sitemap_scheduler.py`
**Function:** `process_pending_jobs(limit: int = 10)`
**Lines:** 105-442

### Workflow Breakdown

The single function handles three distinct workflows:

#### WF2: Deep Scans (Lines 220-309)
- **Model:** `Place`
- **Status Field:** `deep_scan_status`
- **Processing:** Places with `deep_scan_status == GcpApiDeepScanStatusEnum.Queued`
- **Service:** `PlacesDeepService.process_single_deep_scan()`
- **Output:** Updates `LocalBusiness` with deep scan data

#### WF3: Domain Extraction (Lines 315-420)
- **Model:** `LocalBusiness`
- **Status Field:** `domain_extraction_status`
- **Processing:** Businesses with `domain_extraction_status == DomainExtractionStatusEnum.Queued`
- **Service:** `LocalBusinessToDomainService.create_pending_domain_from_local_business()`
- **Output:** Creates `Domain` records for sitemap analysis

#### WF5: Sitemap Import (DISABLED - Lines 130-214)
- **Model:** `Job` (legacy)
- **Status:** Commented out as "DISABLED per PRD v1.2"
- **Note:** Being replaced by modern `sitemap_import_scheduler.py`
- **Action:** Can be removed entirely during split

### Configuration

**Scheduler Setup:** Lines 444-496
```python
def setup_sitemap_scheduler():
    interval_minutes = settings.SITEMAP_SCHEDULER_INTERVAL_MINUTES
    batch_size = settings.SITEMAP_SCHEDULER_BATCH_SIZE
    max_instances = settings.SITEMAP_SCHEDULER_MAX_INSTANCES

    scheduler.add_job(
        process_pending_jobs,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="process_pending_jobs",  # Handles all 3 workflows
        name="Process Sitemaps, DeepScans, DomainExtractions",
        max_instances=max_instances,
        kwargs={"limit": batch_size},
    )
```

**Issue:** Single configuration applies to all workflows equally, preventing individual tuning.

---

## Proposed Solution: Split into Three Schedulers

### New Architecture

Create three independent scheduler files:

1. **`deep_scan_scheduler.py`** - WF2 (Deep Scans)
2. **`domain_extraction_scheduler.py`** - WF3 (Domain Extraction)
3. ~~**`sitemap_import_scheduler.py`**~~ - Already exists for WF6

### Benefits

- ✅ **Fault Isolation:** One workflow failure doesn't affect others
- ✅ **Independent Tuning:** Each workflow can have custom intervals, batch sizes
- ✅ **Clearer Responsibility:** Single-purpose schedulers are easier to maintain
- ✅ **Better Monitoring:** Per-workflow metrics and alerts
- ✅ **Reduced Complexity:** Easier debugging and testing
- ✅ **Follows WF7 Pattern:** Modern SDK-based implementation

---

## Implementation Plan

### Phase 1: Create Deep Scan Scheduler (WF2)

**File:** `src/services/deep_scan_scheduler.py`

```python
"""
WF2 Deep Scan Scheduler

Processes Place records queued for Google Maps deep scan analysis.
Extracts detailed business information and populates LocalBusiness records.
"""

import logging
from sqlalchemy import asc
from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.place import Place, GcpApiDeepScanStatusEnum
from src.services.places.places_deep_service import PlacesDeepService
from src.scheduler_instance import scheduler

logger = logging.getLogger(__name__)

async def process_deep_scan_queue():
    """Process places queued for deep scan analysis."""
    logger.info("Starting deep scan queue processing cycle")

    service = PlacesDeepService()

    await run_job_loop(
        model=Place,
        status_enum=GcpApiDeepScanStatusEnum,
        queued_status=GcpApiDeepScanStatusEnum.Queued,
        processing_status=GcpApiDeepScanStatusEnum.Processing,
        completed_status=GcpApiDeepScanStatusEnum.Completed,
        failed_status=GcpApiDeepScanStatusEnum.Error,
        processing_function=service.process_single_deep_scan,
        batch_size=settings.DEEP_SCAN_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Place.updated_at),
        status_field_name="deep_scan_status",
        error_field_name="deep_scan_error",
    )

    logger.info("Finished deep scan queue processing cycle")

def setup_deep_scan_scheduler():
    """Add deep scan job to the main scheduler."""
    job_id = "process_deep_scan_queue"

    logger.info(f"Setting up deep scan scheduler (every {settings.DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES} min)")

    scheduler.add_job(
        process_deep_scan_queue,
        trigger="interval",
        minutes=settings.DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES,
        id=job_id,
        name="WF2 - Deep Scan Queue Processor",
        replace_existing=True,
        max_instances=settings.DEEP_SCAN_SCHEDULER_MAX_INSTANCES,
        coalesce=True,
        misfire_grace_time=60,
    )

    logger.info(f"Added job '{job_id}' to shared scheduler")
```

**New Settings (add to `src/config/settings.py`):**
```python
# WF2 Deep Scan Scheduler Configuration
DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES: int = 5
DEEP_SCAN_SCHEDULER_BATCH_SIZE: int = 10
DEEP_SCAN_SCHEDULER_MAX_INSTANCES: int = 1
```

---

### Phase 2: Create Domain Extraction Scheduler (WF3)

**File:** `src/services/domain_extraction_scheduler.py`

```python
"""
WF3 Domain Extraction Scheduler

Processes LocalBusiness records queued for domain extraction.
Creates Domain records from business website information.
"""

import logging
from sqlalchemy import asc
from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.local_business import LocalBusiness, DomainExtractionStatusEnum
from src.services.business_to_domain_service import LocalBusinessToDomainService
from src.scheduler_instance import scheduler

logger = logging.getLogger(__name__)

async def process_domain_extraction_queue():
    """Process local businesses queued for domain extraction."""
    logger.info("Starting domain extraction queue processing cycle")

    service = LocalBusinessToDomainService()

    await run_job_loop(
        model=LocalBusiness,
        status_enum=DomainExtractionStatusEnum,
        queued_status=DomainExtractionStatusEnum.Queued,
        processing_status=DomainExtractionStatusEnum.Processing,
        completed_status=DomainExtractionStatusEnum.Completed,
        failed_status=DomainExtractionStatusEnum.Error,
        processing_function=service.create_pending_domain_from_local_business,
        batch_size=settings.DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(LocalBusiness.updated_at),
        status_field_name="domain_extraction_status",
        error_field_name="domain_extraction_error",
    )

    logger.info("Finished domain extraction queue processing cycle")

def setup_domain_extraction_scheduler():
    """Add domain extraction job to the main scheduler."""
    job_id = "process_domain_extraction_queue"

    logger.info(f"Setting up domain extraction scheduler (every {settings.DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES} min)")

    scheduler.add_job(
        process_domain_extraction_queue,
        trigger="interval",
        minutes=settings.DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES,
        id=job_id,
        name="WF3 - Domain Extraction Queue Processor",
        replace_existing=True,
        max_instances=settings.DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES,
        coalesce=True,
        misfire_grace_time=60,
    )

    logger.info(f"Added job '{job_id}' to shared scheduler")
```

**New Settings:**
```python
# WF3 Domain Extraction Scheduler Configuration
DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES: int = 2
DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE: int = 20
DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES: int = 1
```

---

### Phase 3: Update Main Application

**File:** `src/main.py`

**BEFORE:**
```python
from src.services.sitemap_scheduler import setup_sitemap_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    setup_domain_scheduler()
    setup_sitemap_scheduler()  # ⚠️ Handles WF2, WF3, WF5
    setup_domain_sitemap_submission_scheduler()
    setup_sitemap_import_scheduler()
    setup_page_curation_scheduler()
    yield
```

**AFTER:**
```python
from src.services.deep_scan_scheduler import setup_deep_scan_scheduler
from src.services.domain_extraction_scheduler import setup_domain_extraction_scheduler
# Remove: from src.services.sitemap_scheduler import setup_sitemap_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    setup_domain_scheduler()

    # Split schedulers (formerly in sitemap_scheduler)
    setup_deep_scan_scheduler()           # WF2
    setup_domain_extraction_scheduler()   # WF3

    setup_domain_sitemap_submission_scheduler()
    setup_sitemap_import_scheduler()      # WF6
    setup_page_curation_scheduler()       # WF7
    yield
```

---

### Phase 4: Service Adaptation

**Update Services to Match SDK Pattern**

Both services need minor updates to work with the SDK loop:

#### PlacesDeepService

**Current signature:**
```python
async def process_single_deep_scan(
    self, place_id: str, tenant_id: str
) -> Optional[LocalBusiness]:
```

**Required signature for SDK loop:**
```python
async def process_single_deep_scan(
    self, item_id: UUID, session: AsyncSession
) -> None:
```

**Adapter Pattern:**
Create wrapper in `deep_scan_scheduler.py`:
```python
async def process_single_deep_scan_wrapper(item_id: UUID, session: AsyncSession):
    """Wrapper to adapt PlacesDeepService to SDK loop signature."""
    async with session.begin():
        place = await session.get(Place, item_id)
        if not place:
            raise ValueError(f"Place {item_id} not found")

        service = PlacesDeepService()
        result = await service.process_single_deep_scan(
            place_id=str(place.place_id),
            tenant_id=str(place.tenant_id)
        )

        if result:
            place.deep_scan_status = GcpApiDeepScanStatusEnum.Completed
            place.deep_scan_error = None
        else:
            place.deep_scan_status = GcpApiDeepScanStatusEnum.Error
            place.deep_scan_error = "Deep scan returned None"

        place.updated_at = datetime.utcnow()
```

#### LocalBusinessToDomainService

**Current signature:**
```python
async def create_pending_domain_from_local_business(
    self, local_business_id: UUID, session: AsyncSession
) -> bool:
```

**Already compatible!** This service already accepts `(UUID, AsyncSession)`.

Just needs status management wrapper:
```python
async def process_domain_extraction_wrapper(item_id: UUID, session: AsyncSession):
    """Wrapper to manage status for domain extraction."""
    async with session.begin():
        business = await session.get(LocalBusiness, item_id)
        if not business:
            raise ValueError(f"LocalBusiness {item_id} not found")

        service = LocalBusinessToDomainService()
        success = await service.create_pending_domain_from_local_business(
            local_business_id=item_id,
            session=session
        )

        if success:
            business.domain_extraction_status = DomainExtractionStatusEnum.Completed
            business.domain_extraction_error = None
        else:
            business.domain_extraction_status = DomainExtractionStatusEnum.Error
            business.domain_extraction_error = "Domain extraction failed"

        business.updated_at = datetime.utcnow()
```

---

### Phase 5: Remove Old Scheduler

- [ ] Delete `src/services/sitemap_scheduler.py` entirely
- [ ] Remove old settings:
  - `SITEMAP_SCHEDULER_INTERVAL_MINUTES`
  - `SITEMAP_SCHEDULER_BATCH_SIZE`
  - `SITEMAP_SCHEDULER_MAX_INSTANCES`
- [ ] Update any documentation referencing `sitemap_scheduler.py`

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review current `sitemap_scheduler.py` for any missed dependencies
- [ ] Confirm `PlacesDeepService` and `LocalBusinessToDomainService` are ready
- [ ] Document current scheduler performance metrics for comparison

### Phase 1: Deep Scan Scheduler
- [ ] Create `src/services/deep_scan_scheduler.py`
- [ ] Add settings to `src/config/settings.py`
- [ ] Add to `.env.example`
- [ ] Create adapter wrapper for `PlacesDeepService`
- [ ] Write unit tests

### Phase 2: Domain Extraction Scheduler
- [ ] Create `src/services/domain_extraction_scheduler.py`
- [ ] Add settings to `src/config/settings.py`
- [ ] Add to `.env.example`
- [ ] Create status management wrapper
- [ ] Write unit tests

### Phase 3: Integration
- [ ] Update `src/main.py` lifespan
- [ ] Remove `sitemap_scheduler` import
- [ ] Add new scheduler imports
- [ ] Test all schedulers start correctly

### Phase 4: Testing
- [ ] Unit tests for each scheduler
- [ ] Integration tests for scheduler registration
- [ ] End-to-end tests for each workflow
- [ ] Performance testing (compare to baseline)

### Phase 5: Deployment
- [ ] Deploy to staging
- [ ] Monitor for 24 hours
- [ ] Verify all workflows process correctly
- [ ] Check for resource contention issues
- [ ] Deploy to production
- [ ] Monitor for 1 week

### Phase 6: Cleanup
- [ ] Delete `sitemap_scheduler.py`
- [ ] Remove old settings
- [ ] Update documentation
- [ ] Archive old scheduler code for reference

---

## Testing Strategy

### Unit Tests

**File:** `tests/services/test_deep_scan_scheduler.py`

```python
from src.services.deep_scan_scheduler import process_deep_scan_queue
from src.models.place import Place, GcpApiDeepScanStatusEnum

async def test_deep_scan_processes_queued_places(db_session):
    """Verify deep scan scheduler processes queued places"""

    # Create queued place
    place = Place(
        place_id="test_place_123",
        tenant_id="test_tenant",
        deep_scan_status=GcpApiDeepScanStatusEnum.Queued
    )
    db_session.add(place)
    await db_session.commit()

    # Run scheduler
    await process_deep_scan_queue()

    # Verify processing occurred
    await db_session.refresh(place)
    assert place.deep_scan_status in [
        GcpApiDeepScanStatusEnum.Completed,
        GcpApiDeepScanStatusEnum.Error
    ]
```

### Integration Tests

```python
async def test_all_schedulers_registered():
    """Verify all workflow schedulers are registered"""

    # Check scheduler has all expected jobs
    jobs = scheduler.get_jobs()
    job_ids = [job.id for job in jobs]

    assert "process_deep_scan_queue" in job_ids
    assert "process_domain_extraction_queue" in job_ids
    assert "process_pending_jobs" not in job_ids  # Old scheduler removed
```

### Performance Tests

```python
async def test_scheduler_split_maintains_throughput():
    """Verify split schedulers process same volume as original"""

    # Baseline: Original scheduler processed 30 items/minute total
    # Target: Split schedulers process >= 30 items/minute combined

    start_time = datetime.utcnow()

    # Run for 5 minutes
    await asyncio.sleep(300)

    end_time = datetime.utcnow()

    # Count processed items
    deep_scans = await count_completed_deep_scans(start_time, end_time)
    extractions = await count_completed_extractions(start_time, end_time)

    total_processed = deep_scans + extractions
    items_per_minute = total_processed / 5

    assert items_per_minute >= 30  # Maintain baseline throughput
```

---

## Configuration Tuning Recommendations

### Suggested Initial Settings

**WF2 (Deep Scans):**
- Interval: 5 minutes (slower, external API calls)
- Batch size: 10 (external API rate limits)
- Max instances: 1 (prevent API throttling)

**WF3 (Domain Extraction):**
- Interval: 2 minutes (faster, internal processing)
- Batch size: 20 (no external dependencies)
- Max instances: 1 (database write constraints)

### Monitoring Points

- Deep scan API quota usage
- Domain extraction throughput
- Database connection pool utilization
- Scheduler execution time per batch

---

## Risk Assessment

### Risks

1. **Service Adapter Bugs**
   - Risk: Wrapper functions may not handle errors correctly
   - Mitigation: Comprehensive unit tests, staging deployment

2. **Performance Regression**
   - Risk: Split schedulers may have overhead
   - Mitigation: Performance testing, baseline comparison

3. **Missing Dependencies**
   - Risk: Services may have undocumented dependencies
   - Mitigation: Thorough code review, staged rollout

### Rollback Plan

1. **Keep old scheduler file** (don't delete immediately)
2. **Deploy with feature flag:**
   ```python
   USE_SPLIT_SCHEDULERS = os.getenv("USE_SPLIT_SCHEDULERS", "false") == "true"

   if USE_SPLIT_SCHEDULERS:
       setup_deep_scan_scheduler()
       setup_domain_extraction_scheduler()
   else:
       setup_sitemap_scheduler()  # Old multi-workflow scheduler
   ```
3. **Monitor for 1 week** before deleting old code
4. **Rollback:** Set `USE_SPLIT_SCHEDULERS=false` and restart

---

## Success Criteria

- ✅ Three independent scheduler files created and operational
- ✅ Each workflow processes items correctly
- ✅ No decrease in throughput (>= baseline performance)
- ✅ Independent configuration working (different intervals/batch sizes)
- ✅ Fault isolation verified (one scheduler failure doesn't affect others)
- ✅ Old `sitemap_scheduler.py` removed
- ✅ All tests passing
- ✅ Production running successfully for 1 week

---

## Future Enhancements

1. **Dynamic Configuration**
   - Adjust intervals based on queue depth
   - Auto-scale batch sizes based on processing time

2. **Circuit Breaker**
   - Pause scheduler if error rate exceeds threshold
   - Auto-resume when system is healthy

3. **Queue Prioritization**
   - Process urgent items first
   - Age-based priority boosting

---

## Related Documents

- **STATE_OF_THE_NATION_2025-11-16.md** - Issue identification
- **src/services/sitemap_scheduler.py** - Current multi-workflow scheduler
- **src/services/WF7_V2_L4_2of2_PageCurationScheduler.py** - Modern SDK pattern example
- **src/common/curation_sdk/scheduler_loop.py** - SDK loop implementation
- **ADR-004-Transaction-Boundaries.md** - Transaction ownership patterns

---

## Notes

- This follows the WF7 pattern (modern SDK-based scheduler)
- Each scheduler is ~50 lines of code (vs 400+ lines in sitemap_scheduler)
- Enables independent monitoring and alerting per workflow
- Reduces cognitive load for future maintenance
- Aligns with single-responsibility principle

---

**Created by:** Claude (AI Assistant)
**Validation Date:** 2025-11-16
**Related Issue:** HIGH RISK technical debt - Multi-workflow single point of failure
