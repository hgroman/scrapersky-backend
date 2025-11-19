# Work Order 003: Zombie Record Cleanup and Prevention

**ID:** WO-003
**Created:** 2025-11-16
**Priority:** 🟠 HIGH
**Status:** OPEN
**Estimated Time:** 2 hours
**Assignee:** TBD

---

## Issue Summary

**HIGH PRIORITY RELIABILITY ISSUE:** The SDK job loop in `src/common/curation_sdk/scheduler_loop.py` can leave records permanently stuck in `Processing` state if the error-handling database session cannot be obtained, creating "zombie records" that require manual intervention.

---

## Severity Classification

**Level:** 🟠 HIGH

**Impact:**
- Records stuck in `Processing` state are invisible to schedulers
- Background processing queues gradually fill with zombie records
- Manual database intervention required to reset stuck records
- Affects ALL workflows using the SDK loop (WF6, WF7, potentially others)
- Data processing stalls without visible errors

**Affected Workflows:**
- **WF6:** Sitemap Import (`SitemapFile` records)
- **WF7:** Page Curation (`Page` records)
- **Future workflows:** Any workflow using the SDK scheduler loop

---

## Root Cause Analysis

### Vulnerable Code

**File:** `src/common/curation_sdk/scheduler_loop.py`
**Lines:** 136-142

```python
# Phase 2: Process Each Item Individually (Separate Transactions)
for item_id in items_to_process_ids:
    item_session: Optional[AsyncSession] = None
    try:
        item_session = await get_session()
        if item_session is None:
            logger.error(
                f"SCHEDULER_LOOP: Failed to get session for processing item "
                f"{item_id}. Skipping."
            )
            items_failed += 1
            continue  # ⚠️ PROBLEM: Item stays in "Processing" forever

        logger.info(f"SCHEDULER_LOOP: Processing {model.__name__} ID: {item_id}")
        await processing_function(item_id, item_session)
        items_processed_successfully += 1

    except Exception as process_err:
        items_failed += 1
        logger.exception(...)
        # Error handling session attempts to mark as Failed (lines 158-192)
        # BUT: What if THIS session also fails to be obtained?
```

### The Problem Flow

1. **Phase 1 (Lines 68-114):** Batch of items marked as `Processing` ✅
2. **Phase 2 (Lines 132-196):** Process each item individually
   - **Line 135:** Try to get session for item
   - **Line 136:** If `get_session()` returns `None`:
     - Item is skipped (line 142: `continue`)
     - ❌ Item remains in `Processing` state
     - ❌ Not marked as `Failed`
     - ❌ Never requeued
3. **Result:** Zombie record stuck in `Processing` forever

### Why Error Handling Session Can Fail

Even the error handling (lines 158-192) has the same vulnerability:

```python
except Exception as process_err:
    # Attempt to mark as Failed
    error_session: Optional[AsyncSession] = None
    try:
        error_session = await get_session()
        if error_session is None:  # ⚠️ Can also fail here
            logger.error(
                f"SCHEDULER_LOOP: Failed to get error session for item "
                f"{item_id}. Cannot mark as Failed."
            )
            continue  # ⚠️ Item stays in "Processing"
```

**Database session failures can occur due to:**
- Connection pool exhaustion
- Database maintenance windows
- Network issues
- Configuration errors
- Resource limits

---

## Current Workaround (Manual Recovery)

### Operational Runbook: Manual Zombie Record Reset

**When to use:** When records are stuck in `Processing` state for > 1 hour

#### Step 1: Identify Zombie Records

For **WF6 (Sitemap Import):**
```sql
SELECT id, domain, updated_at, sitemap_import_status, sitemap_import_error
FROM sitemap_files
WHERE sitemap_import_status = 'Processing'
  AND updated_at < NOW() - INTERVAL '1 hour'
ORDER BY updated_at ASC
LIMIT 100;
```

For **WF7 (Page Curation):**
```sql
SELECT id, url, updated_at, page_processing_status, page_processing_error
FROM pages
WHERE page_processing_status = 'Processing'
  AND updated_at < NOW() - INTERVAL '1 hour'
ORDER BY updated_at ASC
LIMIT 100;
```

#### Step 2: Verify Records Are Actually Stuck

Check scheduler logs for the record IDs to confirm they were skipped:
```bash
grep "Failed to get session for processing item" /var/log/scheduler.log | grep <RECORD_ID>
```

#### Step 3: Reset to Queued State

For **WF6:**
```sql
UPDATE sitemap_files
SET sitemap_import_status = 'Queued',
    sitemap_import_error = 'Auto-reset from stuck Processing state',
    updated_at = NOW()
WHERE sitemap_import_status = 'Processing'
  AND updated_at < NOW() - INTERVAL '1 hour';
```

For **WF7:**
```sql
UPDATE pages
SET page_processing_status = 'Queued',
    page_processing_error = 'Auto-reset from stuck Processing state',
    updated_at = NOW()
WHERE page_processing_status = 'Processing'
  AND updated_at < NOW() - INTERVAL '1 hour';
```

#### Step 4: Monitor Re-Processing

Watch scheduler logs to verify records are picked up and processed:
```bash
tail -f /var/log/scheduler.log | grep "Processing.*ID:"
```

---

## Proposed Solutions

### Solution 1: Automated Cleanup Job (Recommended)

**Create a periodic cleanup scheduler that resets stuck records.**

#### Implementation

**File:** `src/services/zombie_record_cleanup_scheduler.py`

```python
"""
Zombie Record Cleanup Scheduler

Automatically resets records stuck in 'Processing' state for longer
than the configured threshold back to 'Queued' state.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import update
from src.models.sitemap import SitemapFile, SitemapImportProcessStatusEnum
from src.models.page import Page
from src.models.enums import PageProcessingStatus
from src.session.async_session import get_background_session
from src.scheduler_instance import scheduler
from src.config.settings import settings

logger = logging.getLogger(__name__)

# Configuration
STUCK_THRESHOLD_MINUTES = 60  # Records stuck > 1 hour
CLEANUP_INTERVAL_MINUTES = 15  # Run every 15 minutes

async def cleanup_zombie_records():
    """Reset records stuck in Processing state back to Queued."""
    stuck_threshold = datetime.utcnow() - timedelta(minutes=STUCK_THRESHOLD_MINUTES)

    total_reset = 0

    try:
        async with get_background_session() as session:
            async with session.begin():
                # Cleanup WF6: Sitemap Files
                stmt_sitemap = (
                    update(SitemapFile)
                    .where(
                        SitemapFile.sitemap_import_status == SitemapImportProcessStatusEnum.Processing,
                        SitemapFile.updated_at < stuck_threshold
                    )
                    .values(
                        sitemap_import_status=SitemapImportProcessStatusEnum.Queued,
                        sitemap_import_error="Auto-reset from stuck Processing state",
                        updated_at=datetime.utcnow()
                    )
                )
                result_sitemap = await session.execute(stmt_sitemap)
                sitemap_reset_count = result_sitemap.rowcount

                # Cleanup WF7: Pages
                stmt_pages = (
                    update(Page)
                    .where(
                        Page.page_processing_status == PageProcessingStatus.Processing,
                        Page.updated_at < stuck_threshold
                    )
                    .values(
                        page_processing_status=PageProcessingStatus.Queued,
                        page_processing_error="Auto-reset from stuck Processing state",
                        updated_at=datetime.utcnow()
                    )
                )
                result_pages = await session.execute(stmt_pages)
                pages_reset_count = result_pages.rowcount

                total_reset = sitemap_reset_count + pages_reset_count

                if total_reset > 0:
                    logger.warning(
                        f"Zombie Record Cleanup: Reset {total_reset} stuck records "
                        f"(Sitemaps: {sitemap_reset_count}, Pages: {pages_reset_count})"
                    )
                else:
                    logger.debug("Zombie Record Cleanup: No stuck records found")

    except Exception as e:
        logger.error(f"Zombie Record Cleanup: Error during cleanup: {e}", exc_info=True)

    return total_reset

def setup_zombie_cleanup_scheduler():
    """Add zombie record cleanup job to the scheduler."""
    job_id = "cleanup_zombie_records"

    logger.info(f"Setting up zombie record cleanup job (every {CLEANUP_INTERVAL_MINUTES} min)")

    scheduler.add_job(
        cleanup_zombie_records,
        trigger="interval",
        minutes=CLEANUP_INTERVAL_MINUTES,
        id=job_id,
        name="Zombie Record Cleanup",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    logger.info(f"Added job '{job_id}' to shared scheduler")
```

#### Integration

**File:** `src/main.py`

```python
from src.services.zombie_record_cleanup_scheduler import setup_zombie_cleanup_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the ScraperSky API - Lifespan Start")
    start_scheduler()

    # Existing schedulers
    setup_domain_scheduler()
    setup_sitemap_scheduler()
    setup_domain_sitemap_submission_scheduler()
    setup_sitemap_import_scheduler()
    setup_page_curation_scheduler()

    # ADD THIS
    setup_zombie_cleanup_scheduler()

    yield
```

---

### Solution 2: Improve SDK Loop Error Handling

**Enhance the SDK loop to handle session failures more robustly.**

#### Implementation

**File:** `src/common/curation_sdk/scheduler_loop.py`
**Lines:** 136-142

**BEFORE:**
```python
item_session = await get_session()
if item_session is None:
    logger.error(f"Failed to get session for processing item {item_id}. Skipping.")
    items_failed += 1
    continue  # ⚠️ Item stays in "Processing"
```

**AFTER:**
```python
item_session = await get_session()
if item_session is None:
    logger.error(f"Failed to get session for processing item {item_id}.")
    items_failed += 1

    # Attempt multiple retries to get error-handling session
    error_session = None
    for retry in range(3):
        try:
            error_session = await get_session()
            if error_session:
                break
            await asyncio.sleep(1)  # Wait 1 second between retries
        except Exception as retry_err:
            logger.warning(f"Retry {retry+1}/3 to get error session failed: {retry_err}")

    if error_session:
        # Successfully got error session - mark item as Failed
        async with error_session.begin():
            update_stmt = (
                update(model)
                .where(model.id == item_id)
                .values(
                    **{
                        status_field_name: failed_status,
                        error_field_name: "Failed to obtain processing session",
                    }
                )
            )
            await error_session.execute(update_stmt)
        await error_session.close()
        logger.warning(f"Marked {model.__name__} ID {item_id} as Failed")
    else:
        # Even error session failed - log critical error
        # Item will be picked up by zombie cleanup job
        logger.critical(
            f"ZOMBIE RECORD ALERT: {model.__name__} ID {item_id} "
            f"stuck in Processing - could not obtain error session"
        )

    continue
```

---

## Implementation Checklist

### Phase 1: Operational Runbook (Immediate)
- [ ] Document manual zombie record identification queries
- [ ] Document manual reset SQL commands
- [ ] Create monitoring dashboard for stuck records
- [ ] Add alerting for records stuck > 1 hour

### Phase 2: Automated Cleanup Job (Week 1)
- [ ] Create `zombie_record_cleanup_scheduler.py`
- [ ] Implement cleanup logic for WF6 (SitemapFile)
- [ ] Implement cleanup logic for WF7 (Page)
- [ ] Add configuration for stuck threshold (default: 60 minutes)
- [ ] Add configuration for cleanup interval (default: 15 minutes)
- [ ] Integrate into `main.py` lifespan
- [ ] Add metrics/logging for cleanup operations
- [ ] Deploy to staging and monitor

### Phase 3: SDK Loop Improvement (Week 2)
- [ ] Add retry logic for error-handling session
- [ ] Add critical logging for zombie record creation
- [ ] Test with simulated session failures
- [ ] Deploy to staging and monitor

### Phase 4: Monitoring & Alerting (Week 3)
- [ ] Create Grafana dashboard for stuck records
- [ ] Add PagerDuty alert for zombie record spike
- [ ] Add weekly report of cleanup operations
- [ ] Document troubleshooting procedures

---

## Testing Strategy

### Unit Tests

**File:** `tests/services/test_zombie_cleanup.py`

```python
from datetime import datetime, timedelta
from src.services.zombie_record_cleanup_scheduler import cleanup_zombie_records
from src.models.page import Page
from src.models.enums import PageProcessingStatus

async def test_cleanup_resets_stuck_records(db_session):
    """Verify cleanup resets records stuck > threshold"""

    # Create stuck record (updated 2 hours ago)
    stuck_page = Page(
        url="https://example.com",
        page_processing_status=PageProcessingStatus.Processing,
        updated_at=datetime.utcnow() - timedelta(hours=2)
    )
    db_session.add(stuck_page)
    await db_session.commit()

    # Run cleanup
    reset_count = await cleanup_zombie_records()

    # Verify record was reset
    assert reset_count == 1
    await db_session.refresh(stuck_page)
    assert stuck_page.page_processing_status == PageProcessingStatus.Queued
    assert "Auto-reset" in stuck_page.page_processing_error

async def test_cleanup_ignores_recent_processing_records(db_session):
    """Verify cleanup does NOT reset recently updated records"""

    # Create recent processing record (updated 5 minutes ago)
    recent_page = Page(
        url="https://example.com",
        page_processing_status=PageProcessingStatus.Processing,
        updated_at=datetime.utcnow() - timedelta(minutes=5)
    )
    db_session.add(recent_page)
    await db_session.commit()

    # Run cleanup
    reset_count = await cleanup_zombie_records()

    # Verify record was NOT touched
    assert reset_count == 0
    await db_session.refresh(recent_page)
    assert recent_page.page_processing_status == PageProcessingStatus.Processing
```

### Integration Tests

```python
async def test_sdk_loop_with_session_failure():
    """Simulate session failure and verify zombie handling"""

    # Mock get_session to fail
    with patch('src.db.session.get_session', return_value=None):
        # Run SDK loop
        await run_job_loop(...)

        # Verify critical log was generated
        assert "ZOMBIE RECORD ALERT" in caplog.text
```

---

## Monitoring & Alerting

### Metrics to Track

1. **Zombie Record Count** (by workflow)
   ```sql
   SELECT COUNT(*) as zombie_count
   FROM pages
   WHERE page_processing_status = 'Processing'
     AND updated_at < NOW() - INTERVAL '1 hour';
   ```

2. **Cleanup Operations** (daily/weekly)
   - Records reset per cleanup run
   - Total cleanup operations per day
   - Trends over time

3. **Session Failure Rate**
   - Track `get_session()` failures in logs
   - Alert if failure rate > 1% of attempts

### Alerting Thresholds

- **Warning:** > 10 zombie records detected
- **Critical:** > 50 zombie records detected
- **PagerDuty:** Zombie count doubles in 1 hour

---

## Configuration

### Environment Variables

Add to `.env` and `settings.py`:

```python
# Zombie Record Cleanup Configuration
ZOMBIE_CLEANUP_ENABLED: bool = True
ZOMBIE_STUCK_THRESHOLD_MINUTES: int = 60
ZOMBIE_CLEANUP_INTERVAL_MINUTES: int = 15
```

---

## Success Criteria

- ✅ Manual recovery runbook documented and tested
- ✅ Automated cleanup job running every 15 minutes
- ✅ Stuck records (> 1 hour) automatically reset to Queued
- ✅ SDK loop attempts retry for error-handling session
- ✅ Critical logging for true zombie records (all session attempts fail)
- ✅ Monitoring dashboard shows zombie record trends
- ✅ Alerting triggers when zombie count exceeds threshold
- ✅ Zero manual interventions required over 1 week period

---

## Future Enhancements

1. **Database-Level Constraint**
   - Add trigger to auto-reset records stuck > threshold
   - Reduces dependency on scheduler

2. **Graceful Degradation**
   - If session pool is exhausted, queue records in Redis
   - Process from Redis queue when sessions available

3. **Circuit Breaker Pattern**
   - Detect repeated session failures
   - Temporarily pause scheduler to allow recovery
   - Resume when session pool is healthy

---

## Related Documents

- **STATE_OF_THE_NATION_2025-11-16.md** - Issue identification
- **src/common/curation_sdk/scheduler_loop.py** - SDK loop implementation
- **Documentation/Operations/Runbooks/** - Operational procedures

---

## Notes

- This issue affects ALL workflows using the SDK scheduler loop
- The zombie cleanup job is a safety net, not a fix for the root cause
- Improving SDK loop error handling is the proper long-term solution
- Consider this pattern when designing new schedulers
- Session pool sizing may need adjustment if failures are frequent

---

**Created by:** Claude (AI Assistant)
**Validation Date:** 2025-11-16
**Related Issue:** HIGH priority reliability issue - Zombie records in SDK loop
