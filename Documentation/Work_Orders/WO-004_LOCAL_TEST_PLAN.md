# WO-004 Local Testing Plan
# Multi-Scheduler Split - Pre-Deployment Validation

**Test Date:** 2025-11-16  
**Branch:** `claude/review-scheduler-split-docs-01DJ5yjSxDxwmmuDdWoTV5zF`  
**Latest Commit:** `52fd793` (race condition fix)  
**Tester:** Manual + Automated

---

## Critical Fix Applied

**Race Condition Protection Added** ✅

**File:** `src/common/curation_sdk/scheduler_loop.py`  
**Line:** 72  
**Change:** Added `.with_for_update(skip_locked=True)`

This prevents multiple scheduler instances from processing the same records simultaneously.

---

## Pre-Test Checklist

### 1. Environment Setup

```bash
# Ensure you're on the correct branch
git checkout claude/review-scheduler-split-docs-01DJ5yjSxDxwmmuDdWoTV5zF
git pull origin claude/review-scheduler-split-docs-01DJ5yjSxDxwmmuDdWoTV5zF

# Verify latest commit includes race condition fix
git log --oneline -3
# Should show:
# 52fd793 fix: add row-level locking to SDK scheduler_loop
# e5279f7 test: add database fixtures and execute WO-004 scheduler tests
# 60b1ef8 feat: implement WO-004 multi-scheduler split
```

### 2. Environment Variables

Ensure your `.env` file has:

```bash
# WF2 Deep Scan Scheduler
DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES=5
DEEP_SCAN_SCHEDULER_BATCH_SIZE=10
DEEP_SCAN_SCHEDULER_MAX_INSTANCES=1

# WF3 Domain Extraction Scheduler
DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES=2
DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE=20
DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES=1

# Environment
ENVIRONMENT=development
ENV=development
```

### 3. Database Access

Verify you have:
- ✅ Supabase connection configured
- ✅ Database credentials in `.env`
- ✅ Network access to database

---

## Test Suite

### Test 1: Application Startup ✅

**Objective:** Verify app starts and schedulers register

```bash
# Build and start
docker-compose -f docker-compose.dev.yml up --build

# Expected logs (watch for these):
# ✅ "Setting up deep scan scheduler (interval=5m, batch=10, max_instances=1)"
# ✅ "Deep scan scheduler job 'process_deep_scan_queue' added to shared scheduler"
# ✅ "Setting up domain extraction scheduler (interval=2m, batch=20, max_instances=1)"
# ✅ "Domain extraction scheduler job 'process_domain_extraction_queue' added to shared scheduler"
```

**Pass Criteria:**
- [ ] Application starts without errors
- [ ] Both new schedulers register successfully
- [ ] No import errors
- [ ] No configuration errors

---

### Test 2: Scheduler Registration ✅

**Objective:** Verify schedulers are active in APScheduler

```bash
# Check running container
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs app | grep -i "scheduler"
```

**Expected Output:**
```
Setting up deep scan scheduler
Deep scan scheduler job 'process_deep_scan_queue' added
Setting up domain extraction scheduler  
Domain extraction scheduler job 'process_domain_extraction_queue' added
```

**Pass Criteria:**
- [ ] WF2 scheduler registered
- [ ] WF3 scheduler registered
- [ ] Old sitemap_scheduler NOT running (commented out)
- [ ] No duplicate job IDs

---

### Test 3: WF2 Deep Scan Processing ✅

**Objective:** Verify WF2 processes Place records correctly

#### 3.1 Setup Test Data

```sql
-- Connect to your Supabase database
-- Create a test Place record with Queued status

INSERT INTO place (
    id,
    place_id,
    tenant_id,
    deep_scan_status,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'ChIJN1t_tDeuEmsRUsoyG83frY4',  -- Example Google Place ID
    '550e8400-e29b-41d4-a716-446655440000',  -- Default tenant
    'Queued',
    NOW(),
    NOW()
);
```

#### 3.2 Monitor Processing

```bash
# Watch logs for WF2 activity
docker-compose -f docker-compose.dev.yml logs -f app | grep -i "deep scan"
```

**Expected Logs:**
```
Starting deep scan queue processing cycle
SCHEDULER_LOOP: Found X Place items with status Queued
Processing deep scan for Place <uuid> (place_id=..., tenant_id=...)
Deep scan completed successfully for Place <uuid>
Finished deep scan queue processing cycle
```

#### 3.3 Verify Database Updates

```sql
-- Check Place record was processed
SELECT 
    id,
    place_id,
    deep_scan_status,
    deep_scan_error,
    updated_at
FROM place
WHERE deep_scan_status IN ('Processing', 'Completed', 'Error')
ORDER BY updated_at DESC
LIMIT 10;
```

**Pass Criteria:**
- [ ] Place status changes from Queued → Processing → Completed
- [ ] LocalBusiness record created (if successful)
- [ ] Error status set if processing fails
- [ ] Timestamp updated
- [ ] No duplicate processing

---

### Test 4: WF3 Domain Extraction Processing ✅

**Objective:** Verify WF3 processes LocalBusiness records correctly

#### 4.1 Setup Test Data

```sql
-- Create a test LocalBusiness record with Queued status

INSERT INTO local_business (
    id,
    name,
    website,
    tenant_id,
    domain_extraction_status,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'Test Business',
    'https://example.com',
    '550e8400-e29b-41d4-a716-446655440000',
    'Queued',
    NOW(),
    NOW()
);
```

#### 4.2 Monitor Processing

```bash
# Watch logs for WF3 activity
docker-compose -f docker-compose.dev.yml logs -f app | grep -i "domain extraction"
```

**Expected Logs:**
```
Starting domain extraction queue processing cycle
SCHEDULER_LOOP: Found X LocalBusiness items with status Queued
Processing domain extraction for LocalBusiness <uuid>
Domain extraction completed successfully for LocalBusiness <uuid>
Finished domain extraction queue processing cycle
```

#### 4.3 Verify Database Updates

```sql
-- Check LocalBusiness record was processed
SELECT 
    id,
    name,
    website,
    domain_extraction_status,
    domain_extraction_error,
    updated_at
FROM local_business
WHERE domain_extraction_status IN ('Processing', 'Completed', 'Error')
ORDER BY updated_at DESC
LIMIT 10;

-- Check if Domain record was created
SELECT 
    id,
    domain,
    created_at
FROM domain
ORDER BY created_at DESC
LIMIT 10;
```

**Pass Criteria:**
- [ ] LocalBusiness status changes from Queued → Processing → Completed
- [ ] Domain record created (if successful)
- [ ] Error status set if processing fails
- [ ] Timestamp updated
- [ ] No duplicate processing

---

### Test 5: Race Condition Protection ✅

**Objective:** Verify `.with_for_update(skip_locked=True)` prevents duplicate processing

#### 5.1 Setup Multiple Test Records

```sql
-- Create 5 test Place records
INSERT INTO place (id, place_id, tenant_id, deep_scan_status, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'ChIJN1t_tDeuEmsRUsoyG83frY4_' || generate_series,
    '550e8400-e29b-41d4-a716-446655440000',
    'Queued',
    NOW(),
    NOW()
FROM generate_series(1, 5);
```

#### 5.2 Trigger Manual Processing

```bash
# In one terminal, watch logs
docker-compose -f docker-compose.dev.yml logs -f app | grep "SCHEDULER_LOOP"

# The scheduler will automatically process these records
# Watch for the SELECT ... FOR UPDATE SKIP LOCKED behavior
```

#### 5.3 Verify No Duplicates

```sql
-- Check that each record was processed exactly once
SELECT 
    place_id,
    deep_scan_status,
    COUNT(*) as process_count
FROM place
WHERE place_id LIKE 'ChIJN1t_tDeuEmsRUsoyG83frY4_%'
GROUP BY place_id, deep_scan_status
HAVING COUNT(*) > 1;

-- Should return 0 rows (no duplicates)
```

**Pass Criteria:**
- [ ] Each record processed exactly once
- [ ] No duplicate LocalBusiness records created
- [ ] Logs show proper locking behavior
- [ ] No race condition errors

---

### Test 6: Error Handling ✅

**Objective:** Verify schedulers handle errors gracefully

#### 6.1 Create Invalid Test Data

```sql
-- Create Place with null place_id (should fail)
INSERT INTO place (
    id,
    place_id,
    tenant_id,
    deep_scan_status,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    NULL,  -- Invalid: null place_id
    '550e8400-e29b-41d4-a716-446655440000',
    'Queued',
    NOW(),
    NOW()
);
```

#### 6.2 Monitor Error Handling

```bash
# Watch for error logs
docker-compose -f docker-compose.dev.yml logs -f app | grep -i "error"
```

**Expected Behavior:**
```
Processing deep scan for Place <uuid> (place_id=None, tenant_id=...)
Error processing Place ID <uuid>: ...
Marked Place ID <uuid> as Failed due to error
```

#### 6.3 Verify Error Status

```sql
-- Check error was recorded
SELECT 
    id,
    place_id,
    deep_scan_status,
    deep_scan_error
FROM place
WHERE deep_scan_status = 'Error'
ORDER BY updated_at DESC
LIMIT 5;
```

**Pass Criteria:**
- [ ] Error logged clearly
- [ ] Status set to Error/Failed
- [ ] Error message stored in error field
- [ ] Other records continue processing
- [ ] No scheduler crash

---

### Test 7: Configuration Validation ✅

**Objective:** Verify scheduler configuration is applied correctly

```bash
# Check settings are loaded
docker-compose -f docker-compose.dev.yml exec app python -c "
from src.config.settings import settings
print(f'WF2 Interval: {settings.DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES}m')
print(f'WF2 Batch: {settings.DEEP_SCAN_SCHEDULER_BATCH_SIZE}')
print(f'WF2 Max Instances: {settings.DEEP_SCAN_SCHEDULER_MAX_INSTANCES}')
print(f'WF3 Interval: {settings.DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES}m')
print(f'WF3 Batch: {settings.DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE}')
print(f'WF3 Max Instances: {settings.DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES}')
"
```

**Expected Output:**
```
WF2 Interval: 5m
WF2 Batch: 10
WF2 Max Instances: 1
WF3 Interval: 2m
WF3 Batch: 20
WF3 Max Instances: 1
```

**Pass Criteria:**
- [ ] All settings load correctly
- [ ] Values match .env configuration
- [ ] No default fallbacks used (unless intended)

---

### Test 8: Performance Baseline ✅

**Objective:** Establish performance baseline for comparison

#### 8.1 Create Test Dataset

```sql
-- Create 50 test Place records
INSERT INTO place (id, place_id, tenant_id, deep_scan_status, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'ChIJTest_' || LPAD(generate_series::text, 5, '0'),
    '550e8400-e29b-41d4-a716-446655440000',
    'Queued',
    NOW(),
    NOW()
FROM generate_series(1, 50);
```

#### 8.2 Measure Processing Time

```bash
# Record start time
START_TIME=$(date +%s)

# Watch processing
docker-compose -f docker-compose.dev.yml logs -f app | grep "Finished deep scan"

# Record end time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "Processing time: ${DURATION} seconds"
```

#### 8.3 Calculate Throughput

```sql
-- Check processing results
SELECT 
    deep_scan_status,
    COUNT(*) as count
FROM place
WHERE place_id LIKE 'ChIJTest_%'
GROUP BY deep_scan_status;
```

**Metrics to Record:**
- [ ] Total processing time
- [ ] Items per minute
- [ ] Success rate
- [ ] Error rate
- [ ] Average time per item

---

## Post-Test Validation

### Checklist

- [ ] All 8 tests passed
- [ ] No errors in logs
- [ ] Database records updated correctly
- [ ] No race conditions observed
- [ ] Performance acceptable
- [ ] Error handling works
- [ ] Configuration applied correctly

### Cleanup

```bash
# Stop containers
docker-compose -f docker-compose.dev.yml down

# Clean up test data (optional)
# DELETE FROM place WHERE place_id LIKE 'ChIJTest_%';
# DELETE FROM place WHERE place_id LIKE 'ChIJN1t_tDeuEmsRUsoyG83frY4_%';
```

---

## Decision Matrix

### If All Tests Pass ✅

**PROCEED TO STAGING DEPLOYMENT**

1. Push changes to GitHub
2. Deploy to staging environment
3. Monitor for 24 hours
4. Deploy to production

### If Any Test Fails ❌

**DO NOT DEPLOY**

1. Document the failure
2. Fix the issue
3. Re-run tests
4. Only deploy after all tests pass

---

## Test Results Log

**Date:** _____________  
**Tester:** _____________  
**Duration:** _____________

| Test | Status | Notes |
|------|--------|-------|
| 1. Application Startup | ⬜ Pass ⬜ Fail | |
| 2. Scheduler Registration | ⬜ Pass ⬜ Fail | |
| 3. WF2 Deep Scan | ⬜ Pass ⬜ Fail | |
| 4. WF3 Domain Extraction | ⬜ Pass ⬜ Fail | |
| 5. Race Condition Protection | ⬜ Pass ⬜ Fail | |
| 6. Error Handling | ⬜ Pass ⬜ Fail | |
| 7. Configuration | ⬜ Pass ⬜ Fail | |
| 8. Performance | ⬜ Pass ⬜ Fail | |

**Overall Result:** ⬜ PASS - Deploy to Staging ⬜ FAIL - Fix and Retest

---

**Related Documents:**
- `WO-004_IMPLEMENTATION_SUMMARY.md` - Deployment guide
- `WO-004_TESTING_GUIDE.md` - Comprehensive testing strategy
- `WO-004_TEST_RESULTS.md` - Unit test results

**END OF LOCAL TEST PLAN**
