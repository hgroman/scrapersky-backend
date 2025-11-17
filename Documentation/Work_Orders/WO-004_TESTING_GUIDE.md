# WO-004 Testing Guide
# Multi-Scheduler Split - Testing Strategy & Implementation

**Document Version:** 1.0
**Created:** 2025-11-17
**Status:** READY FOR EXECUTION
**Related Work Order:** WO-004_Multi_Scheduler_Split.md

---

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [End-to-End Tests](#end-to-end-tests)
5. [Performance Tests](#performance-tests)
6. [Manual Testing Checklist](#manual-testing-checklist)
7. [Test Execution Plan](#test-execution-plan)

---

## Testing Overview

### Testing Pyramid

```
                    ┌────────────┐
                    │    E2E     │  ← Few (smoke tests)
                    │   Tests    │
                    └────────────┘
                 ┌──────────────────┐
                 │   Integration    │  ← Some (scheduler registration)
                 │      Tests       │
                 └──────────────────┘
            ┌────────────────────────────┐
            │      Unit Tests            │  ← Many (each scheduler)
            │  (Adapter + Processing)    │
            └────────────────────────────┘
```

### Test Coverage Goals

- **Unit Tests:** 90%+ coverage of scheduler files
- **Integration Tests:** All scheduler registration paths
- **E2E Tests:** At least 1 full workflow per scheduler
- **Performance Tests:** Throughput baseline validation

### Testing Phases

1. **Phase 1:** Unit tests during development
2. **Phase 2:** Integration tests before deployment
3. **Phase 3:** E2E tests in staging
4. **Phase 4:** Performance tests in staging
5. **Phase 5:** Manual validation in production

---

## Unit Tests

### Test File Structure

```
tests/
└── services/
    ├── test_deep_scan_scheduler.py
    ├── test_domain_extraction_scheduler.py
    └── fixtures/
        └── scheduler_fixtures.py
```

### Test Categories

#### 1. Adapter Function Tests

Test the wrapper functions that adapt existing services to SDK signature.

**Deep Scan Adapter Tests:**
- ✅ Successfully processes valid Place record
- ✅ Updates status to Completed on success
- ✅ Updates status to Error on failure
- ✅ Raises ValueError when Place not found
- ✅ Manages transaction correctly
- ✅ Updates updated_at timestamp

**Domain Extraction Adapter Tests:**
- ✅ Successfully processes valid LocalBusiness record
- ✅ Updates status to Completed on success
- ✅ Updates status to Error on failure
- ✅ Raises ValueError when LocalBusiness not found
- ✅ Manages transaction correctly
- ✅ Updates updated_at timestamp

#### 2. Queue Processing Tests

Test the main scheduler loop functions.

**Deep Scan Queue Tests:**
- ✅ Processes queued places
- ✅ Skips non-queued places
- ✅ Respects batch size limit
- ✅ Handles empty queue gracefully
- ✅ Orders by updated_at ascending

**Domain Extraction Queue Tests:**
- ✅ Processes queued businesses
- ✅ Skips non-queued businesses
- ✅ Respects batch size limit
- ✅ Handles empty queue gracefully
- ✅ Orders by updated_at ascending

#### 3. Setup Function Tests

Test scheduler registration.

**Setup Tests:**
- ✅ Registers job with correct ID
- ✅ Uses correct interval from settings
- ✅ Uses correct batch size from settings
- ✅ Uses correct max instances from settings
- ✅ Job is callable

#### 4. Edge Case Tests

**Edge Cases:**
- ✅ Record deleted between fetch and process
- ✅ Record updated by another process
- ✅ Service raises exception
- ✅ Database connection fails
- ✅ Invalid status enum value
- ✅ Null/empty fields

---

## Integration Tests

### Test File Structure

```
tests/
└── integration/
    ├── test_scheduler_registration.py
    ├── test_scheduler_execution.py
    └── test_workflow_isolation.py
```

### Test Categories

#### 1. Scheduler Registration Tests

**Test: All Schedulers Register Successfully**
```python
async def test_all_schedulers_registered():
    """Verify all workflow schedulers are registered correctly."""

    # Start application
    app = create_app()

    # Check scheduler has all expected jobs
    jobs = scheduler.get_jobs()
    job_ids = {job.id for job in jobs}

    # New schedulers present
    assert "process_deep_scan_queue" in job_ids
    assert "process_domain_extraction_queue" in job_ids

    # Old scheduler removed
    assert "process_pending_jobs" not in job_ids

    # Other schedulers still present
    assert "process_domain_queue" in job_ids
    assert "process_sitemap_import_queue" in job_ids
```

**Test: Scheduler Configuration Correct**
```python
async def test_scheduler_configuration():
    """Verify schedulers use correct configuration."""

    jobs = scheduler.get_jobs()

    # Find deep scan job
    deep_scan_job = next(j for j in jobs if j.id == "process_deep_scan_queue")
    assert deep_scan_job.trigger.interval.total_seconds() == 5 * 60  # 5 minutes

    # Find domain extraction job
    domain_job = next(j for j in jobs if j.id == "process_domain_extraction_queue")
    assert domain_job.trigger.interval.total_seconds() == 2 * 60  # 2 minutes
```

#### 2. Scheduler Execution Tests

**Test: Schedulers Execute Without Errors**
```python
async def test_schedulers_execute_successfully():
    """Verify schedulers can execute at least once without errors."""

    # Execute deep scan scheduler
    await process_deep_scan_queue()
    # Should complete without exceptions (even if queue is empty)

    # Execute domain extraction scheduler
    await process_domain_extraction_queue()
    # Should complete without exceptions (even if queue is empty)
```

#### 3. Workflow Isolation Tests

**Test: WF2 Failure Doesn't Affect WF3**
```python
async def test_wf2_failure_isolates_from_wf3(db_session, monkeypatch):
    """Verify WF2 failure doesn't affect WF3 processing."""

    # Create queued items for both workflows
    place = create_test_place(status=GcpApiDeepScanStatusEnum.Queued)
    business = create_test_business(status=DomainExtractionStatusEnum.Queued)

    # Make WF2 service fail
    def mock_deep_scan_fail(*args, **kwargs):
        raise Exception("WF2 Service Error")

    monkeypatch.setattr(
        "src.services.places.places_deep_service.PlacesDeepService.process_single_deep_scan",
        mock_deep_scan_fail
    )

    # Run both schedulers
    await process_deep_scan_queue()  # Should fail gracefully
    await process_domain_extraction_queue()  # Should succeed

    # Verify WF2 failed
    await db_session.refresh(place)
    assert place.deep_scan_status == GcpApiDeepScanStatusEnum.Error

    # Verify WF3 succeeded
    await db_session.refresh(business)
    assert business.domain_extraction_status == DomainExtractionStatusEnum.Completed
```

---

## End-to-End Tests

### Test File Structure

```
tests/
└── e2e/
    ├── test_wf2_deep_scan_e2e.py
    └── test_wf3_domain_extraction_e2e.py
```

### WF2 Deep Scan E2E Test

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_wf2_deep_scan_full_workflow(db_session):
    """
    End-to-end test of WF2 Deep Scan workflow.

    Flow:
    1. Create Place with Queued status
    2. Run deep scan scheduler
    3. Verify LocalBusiness created
    4. Verify Place status updated to Completed
    """

    # Setup: Create test place
    tenant = create_test_tenant()
    place = Place(
        id=uuid4(),
        tenant_id=tenant.id,
        place_id="test_place_123",
        name="Test Business",
        deep_scan_status=GcpApiDeepScanStatusEnum.Queued,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(place)
    await db_session.commit()

    # Execute: Run scheduler
    await process_deep_scan_queue()

    # Verify: Place status updated
    await db_session.refresh(place)
    assert place.deep_scan_status == GcpApiDeepScanStatusEnum.Completed
    assert place.deep_scan_error is None

    # Verify: LocalBusiness created
    stmt = select(LocalBusiness).where(LocalBusiness.place_id == place.id)
    result = await db_session.execute(stmt)
    local_business = result.scalar_one_or_none()

    assert local_business is not None
    assert local_business.name == "Test Business"
```

### WF3 Domain Extraction E2E Test

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_wf3_domain_extraction_full_workflow(db_session):
    """
    End-to-end test of WF3 Domain Extraction workflow.

    Flow:
    1. Create LocalBusiness with Queued status
    2. Run domain extraction scheduler
    3. Verify Domain created
    4. Verify LocalBusiness status updated to Completed
    """

    # Setup: Create test local business
    tenant = create_test_tenant()
    business = LocalBusiness(
        id=uuid4(),
        tenant_id=tenant.id,
        name="Test Business",
        website="https://example.com",
        domain_extraction_status=DomainExtractionStatusEnum.Queued,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(business)
    await db_session.commit()

    # Execute: Run scheduler
    await process_domain_extraction_queue()

    # Verify: LocalBusiness status updated
    await db_session.refresh(business)
    assert business.domain_extraction_status == DomainExtractionStatusEnum.Completed
    assert business.domain_extraction_error is None

    # Verify: Domain created
    stmt = select(Domain).where(Domain.url == "example.com")
    result = await db_session.execute(stmt)
    domain = result.scalar_one_or_none()

    assert domain is not None
    assert domain.tenant_id == tenant.id
```

---

## Performance Tests

### Throughput Baseline Test

```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_scheduler_split_maintains_throughput(db_session):
    """
    Verify split schedulers process same volume as original combined scheduler.

    Baseline: Original scheduler processed ~30 items/minute total
    Target: Split schedulers process >= 30 items/minute combined
    """

    # Setup: Create 100 items for each workflow
    for _ in range(100):
        place = create_test_place(status=GcpApiDeepScanStatusEnum.Queued)
        business = create_test_business(status=DomainExtractionStatusEnum.Queued)
        db_session.add(place)
        db_session.add(business)
    await db_session.commit()

    # Execute: Run for 5 minutes
    start_time = datetime.utcnow()

    while (datetime.utcnow() - start_time).total_seconds() < 300:
        await process_deep_scan_queue()
        await process_domain_extraction_queue()
        await asyncio.sleep(10)  # Wait between runs

    end_time = datetime.utcnow()

    # Measure: Count processed items
    deep_scans_completed = await count_completed_deep_scans(start_time, end_time)
    extractions_completed = await count_completed_extractions(start_time, end_time)

    total_processed = deep_scans_completed + extractions_completed
    items_per_minute = total_processed / 5

    # Assert: Maintain baseline throughput
    assert items_per_minute >= 30, f"Only processed {items_per_minute} items/min (target: 30)"
```

### Resource Utilization Test

```python
@pytest.mark.performance
async def test_concurrent_scheduler_execution(db_session):
    """Verify schedulers can run concurrently without deadlocks."""

    # Create test data
    for _ in range(50):
        place = create_test_place(status=GcpApiDeepScanStatusEnum.Queued)
        business = create_test_business(status=DomainExtractionStatusEnum.Queued)
        db_session.add(place)
        db_session.add(business)
    await db_session.commit()

    # Run schedulers concurrently
    results = await asyncio.gather(
        process_deep_scan_queue(),
        process_domain_extraction_queue(),
        process_deep_scan_queue(),  # Second instance
        process_domain_extraction_queue(),  # Second instance
        return_exceptions=True
    )

    # Verify no deadlocks or exceptions
    for result in results:
        assert not isinstance(result, Exception), f"Scheduler failed: {result}"
```

---

## Manual Testing Checklist

### Pre-Deployment Validation

- [ ] **Code Review**
  - [ ] All new files reviewed
  - [ ] No hardcoded values
  - [ ] Proper error handling
  - [ ] Logging statements added

- [ ] **Configuration Validation**
  - [ ] Settings.py updated correctly
  - [ ] .env.example updated
  - [ ] No conflicting settings
  - [ ] Default values reasonable

- [ ] **Import Validation**
  - [ ] All imports resolve
  - [ ] No circular dependencies
  - [ ] main.py imports correct

### Staging Environment Tests

- [ ] **Scheduler Registration**
  - [ ] Application starts without errors
  - [ ] Both new schedulers registered
  - [ ] Old scheduler not registered
  - [ ] Check logs for registration messages

- [ ] **WF2 Deep Scan**
  - [ ] Create test Place with Queued status
  - [ ] Wait for scheduler to run
  - [ ] Verify status changes to Processing
  - [ ] Verify status changes to Completed
  - [ ] Verify LocalBusiness created
  - [ ] Check logs for processing messages

- [ ] **WF3 Domain Extraction**
  - [ ] Create test LocalBusiness with Queued status
  - [ ] Wait for scheduler to run
  - [ ] Verify status changes to Processing
  - [ ] Verify status changes to Completed
  - [ ] Verify Domain created
  - [ ] Check logs for processing messages

- [ ] **Error Handling**
  - [ ] Create Place with invalid data
  - [ ] Verify status changes to Error
  - [ ] Verify error message populated
  - [ ] Check logs for error details

- [ ] **Fault Isolation**
  - [ ] Break WF2 service (e.g., invalid API key)
  - [ ] Verify WF2 fails gracefully
  - [ ] Verify WF3 continues processing
  - [ ] Verify other schedulers unaffected

### Production Monitoring (First 48 Hours)

- [ ] **Application Health**
  - [ ] Application started successfully
  - [ ] No startup errors in logs
  - [ ] All schedulers registered

- [ ] **WF2 Processing**
  - [ ] Places being processed
  - [ ] Completion rate normal
  - [ ] Error rate acceptable
  - [ ] API quota not exceeded

- [ ] **WF3 Processing**
  - [ ] LocalBusinesses being processed
  - [ ] Completion rate normal
  - [ ] Error rate acceptable
  - [ ] Domains being created

- [ ] **System Metrics**
  - [ ] CPU usage normal
  - [ ] Memory usage normal
  - [ ] Database connections healthy
  - [ ] No connection pool exhaustion

- [ ] **Queue Depths**
  - [ ] WF2 queue not growing
  - [ ] WF3 queue not growing
  - [ ] Throughput meets expectations

---

## Test Execution Plan

### Development Phase

```bash
# 1. Run unit tests
pytest tests/services/test_deep_scan_scheduler.py -v
pytest tests/services/test_domain_extraction_scheduler.py -v

# 2. Run integration tests
pytest tests/integration/test_scheduler_registration.py -v

# 3. Check coverage
pytest --cov=src/services/deep_scan_scheduler tests/
pytest --cov=src/services/domain_extraction_scheduler tests/
```

### Staging Phase

```bash
# 1. Deploy to staging
docker-compose -f docker-compose.staging.yml up --build

# 2. Run E2E tests
pytest tests/e2e/ -v --e2e

# 3. Run performance tests
pytest tests/performance/ -v --performance

# 4. Monitor for 24 hours
# Check logs, metrics, queue depths
```

### Production Phase

```bash
# 1. Deploy with feature flag
# Set USE_SPLIT_SCHEDULERS=true

# 2. Monitor for 48 hours
# Watch logs, alerts, metrics

# 3. Validate throughput
# Compare to baseline metrics

# 4. If successful, proceed to cleanup
# Remove old scheduler file
# Remove deprecated settings
```

---

## Success Criteria

### Unit Tests
- ✅ All unit tests passing
- ✅ 90%+ code coverage
- ✅ No flaky tests

### Integration Tests
- ✅ All schedulers register correctly
- ✅ No conflicts with existing schedulers
- ✅ Fault isolation verified

### E2E Tests
- ✅ WF2 processes end-to-end successfully
- ✅ WF3 processes end-to-end successfully
- ✅ Error handling works correctly

### Performance Tests
- ✅ Throughput >= baseline (30 items/min)
- ✅ No deadlocks under concurrent load
- ✅ Resource usage within acceptable limits

### Production Validation
- ✅ No increase in error rates
- ✅ Queue depths stable or decreasing
- ✅ No customer impact
- ✅ Successful for 1 week

---

## Troubleshooting Guide

### Issue: Scheduler Not Registered

**Symptoms:**
- Logs show "Failed to setup Deep Scan scheduler"
- Job not in scheduler.get_jobs()

**Debug:**
```python
# Check imports
from src.services.deep_scan_scheduler import setup_deep_scan_scheduler

# Try manual registration
setup_deep_scan_scheduler()

# Check scheduler instance
from src.scheduler_instance import scheduler
print(scheduler.get_jobs())
```

**Common Causes:**
- Import error (missing dependency)
- Settings validation error
- Scheduler instance not started

### Issue: Items Not Processing

**Symptoms:**
- Queue depth growing
- Status stays "Queued"

**Debug:**
```sql
-- Check queued items
SELECT COUNT(*) FROM place WHERE deep_scan_status = 'Queued';

-- Check processing items (stuck?)
SELECT COUNT(*) FROM place WHERE deep_scan_status = 'Processing';

-- Check recent updates
SELECT * FROM place
WHERE deep_scan_status IN ('Processing', 'Completed', 'Error')
ORDER BY updated_at DESC
LIMIT 10;
```

**Common Causes:**
- Scheduler not running
- Batch size too small
- Service throwing exceptions
- Database connection issues

### Issue: High Error Rate

**Symptoms:**
- Many items with Error status
- Error messages in logs

**Debug:**
```sql
-- Check error distribution
SELECT deep_scan_error, COUNT(*)
FROM place
WHERE deep_scan_status = 'Error'
GROUP BY deep_scan_error;

-- Check recent errors
SELECT * FROM place
WHERE deep_scan_status = 'Error'
ORDER BY updated_at DESC
LIMIT 10;
```

**Common Causes:**
- External API issues
- Invalid data
- Service bugs
- Configuration errors

---

## Related Documentation

- **Work Order:** `WO-004_Multi_Scheduler_Split.md`
- **Architecture:** `WO-004_ARCHITECTURE_UPDATE.md`
- **Readiness Report:** `WO-004_IMPLEMENTATION_READINESS_REPORT.md`
- **Test Files:** `tests/services/test_*_scheduler.py`

---

**Document Status:** COMPLETE
**Created:** 2025-11-17
**Next Update:** After first test execution
