# WO-017 Phase 2: DeBounce Scheduler - Test Plan for Local Claude

**Date:** 2025-11-19
**Test Environment:** Windsurf IDE with MCP Supabase Access + Local Docker
**Tester:** Local Claude (Windsurf)
**Implementation:** Online Claude
**Status:** ⏳ **READY FOR TESTING**

---

## What Was Just Implemented

**WO-017 Phase 2: Automated Background Scheduler**

Online Claude just implemented the automated background scheduler for email validation. This means contacts queued for validation will now be processed automatically every 5 minutes without manual intervention.

### Key Components Added

1. **SDK-Compatible Wrapper** (`debounce_service.py`)
   - Added `process_single_contact()` method for SDK compatibility
   - Delegates to existing `process_batch_validation()` with single contact

2. **Background Scheduler** (`debounce_scheduler.py`) - NEW FILE
   - `process_debounce_validation_queue()` - Main scheduler function
   - `setup_debounce_validation_scheduler()` - APScheduler registration
   - Runs every 5 minutes (configurable)
   - Processes 50 contacts per cycle (configurable)

3. **Main App Integration** (`main.py`)
   - Scheduler registered in app lifespan
   - Runs after HubSpot scheduler
   - Wrapped in try/except for error handling

### How It Works

```
Every 5 minutes (automatic):
  ↓
1. Query contacts with debounce_processing_status = 'Queued'
  ↓
2. Mark as 'Processing'
  ↓
3. Validate email via DeBounce API
  ↓
4. Update database with results
  ↓
5. Mark as 'Complete' or 'Error'
  ↓
6. Auto-queue valid emails for CRM sync
  ↓
7. Skip invalid/disposable emails
```

---

## Test Objectives

✅ Verify scheduler starts successfully on Docker startup
✅ Verify scheduler processes queued contacts automatically
✅ Verify email validation works correctly
✅ Verify auto-CRM queueing for valid emails
✅ Verify invalid/disposable emails are skipped
✅ Verify retry logic works for failed validations
✅ Verify scheduler runs every 5 minutes

---

## Prerequisites

### Environment Setup
- ✅ Windsurf IDE running
- ✅ MCP Supabase server connected
- ✅ Docker Desktop running
- ✅ `.env` file configured with DeBounce API key

### Required .env Variables
```bash
# DeBounce API Configuration
DEBOUNCE_API_KEY=691d38cd78602  # ✅ Already configured (from Phase 1)
DEBOUNCE_API_BASE_URL=https://api.debounce.io/v1

# Scheduler Settings
DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES=5
DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE=50
DEBOUNCE_VALIDATION_SCHEDULER_MAX_INSTANCES=1

# Auto-CRM Queue
DEBOUNCE_AUTO_QUEUE_VALID_EMAILS=true
DEBOUNCE_AUTO_QUEUE_DEFAULT_CRM=brevo
DEBOUNCE_SKIP_DISPOSABLE=true
DEBOUNCE_SKIP_INVALID=true
DEBOUNCE_QUEUE_CATCH_ALL=false
```

---

## Test Procedure

### Phase 1: Pre-Test Setup (Supabase MCP)

#### Step 1.1: Verify Test Contacts Exist

**Action:** Query existing test contacts from Phase 1
```sql
SELECT
    id,
    email,
    debounce_validation_status,
    debounce_processing_status,
    debounce_result,
    debounce_score,
    brevo_sync_status
FROM contacts
WHERE id IN (
    '8ef2449f-d3eb-4831-b85e-a385332b6475',  -- test.valid.email@gmail.com
    'f1bae019-a2a4-4caf-aeb6-43c1d8464fd6',  -- test@mailinator.com
    'bc5de95f-de77-4993-94a5-a2230349809b'   -- test@invaliddomain12345.com
);
```

**Expected Result:** 3 contacts with Phase 1 validation results

#### Step 1.2: Create Fresh Test Contacts

**Action:** Create 3 new test contacts for scheduler testing
```sql
-- Create test contact 1: Valid email
INSERT INTO contacts (
    id,
    email,
    first_name,
    last_name,
    debounce_validation_status,
    debounce_processing_status,
    brevo_sync_status,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'scheduler.test.valid@gmail.com',
    'Scheduler',
    'Test Valid',
    'Queued',
    'Queued',
    'New',
    NOW(),
    NOW()
) RETURNING id, email;

-- Create test contact 2: Invalid email
INSERT INTO contacts (
    id,
    email,
    first_name,
    last_name,
    debounce_validation_status,
    debounce_processing_status,
    brevo_sync_status,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'scheduler.test@invalidtestdomain99999.com',
    'Scheduler',
    'Test Invalid',
    'Queued',
    'Queued',
    'New',
    NOW(),
    NOW()
) RETURNING id, email;

-- Create test contact 3: Disposable email
INSERT INTO contacts (
    id,
    email,
    first_name,
    last_name,
    debounce_validation_status,
    debounce_processing_status,
    brevo_sync_status,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'scheduler.test@guerrillamail.com',
    'Scheduler',
    'Test Disposable',
    'Queued',
    'Queued',
    'New',
    NOW(),
    NOW()
) RETURNING id, email;
```

**Expected Result:** 3 new UUIDs and emails returned
**Save these UUIDs** for later verification!

#### Step 1.3: Verify Contacts Are Queued

**Action:** Confirm contacts are ready for scheduler
```sql
SELECT
    id,
    email,
    debounce_validation_status,
    debounce_processing_status,
    created_at
FROM contacts
WHERE debounce_processing_status = 'Queued'
ORDER BY created_at DESC
LIMIT 10;
```

**Expected Result:** At least 3 contacts with status 'Queued'

---

### Phase 2: Docker Startup & Scheduler Verification

#### Step 2.1: Build and Start Docker Container

**Action:** Start the application
```bash
# Terminal command
docker compose up --build
```

**What to Watch For:**
```
✅ Building app image
✅ Container starts successfully
✅ Database connection established
✅ Schedulers start registering
```

#### Step 2.2: Verify Scheduler Registration

**Action:** Look for these log messages during startup

**Expected Logs:**
```
📋 Configuring DeBounce email validation scheduler...
   Interval: 5 minutes
   Batch size: 50 emails
   Max instances: 1
✅ DeBounce validation scheduler job registered successfully
```

**If You See This Instead:**
```
⚠️ DEBOUNCE_API_KEY not configured - DeBounce validation scheduler DISABLED
```
**Problem:** API key missing - check `.env` file

#### Step 2.3: Verify Scheduler is Active

**Action:** Wait for first scheduler cycle (up to 5 minutes)

**Expected Logs:**
```
🚀 Starting DeBounce validation scheduler cycle
🚀 Starting DeBounce validation for contact <UUID>
📧 Validating 3 emails via DeBounce API
HTTP Request: GET https://api.debounce.io/v1/?api=***&email=scheduler.test.valid@gmail.com "HTTP/1.1 200 OK"
✅ Validated scheduler.test.valid@gmail.com: valid
✅ Validated scheduler.test.valid@gmail.com: valid (score: 100)
📤 Auto-queueing scheduler.test.valid@gmail.com for brevo sync
✅ Validated scheduler.test@invalidtestdomain99999.com: invalid (score: 0)
⏭️ Skipping invalid email: scheduler.test@invalidtestdomain99999.com
✅ Validated scheduler.test@guerrillamail.com: disposable (score: 10)
⏭️ Skipping invalid email: scheduler.test@guerrillamail.com
✅ Batch validation complete: 3 emails processed
✅ Finished DeBounce validation scheduler cycle
```

**Timing Notes:**
- First cycle may take up to 5 minutes to start
- Each validation takes ~500ms per email
- Full batch of 3 emails: ~3-5 seconds total

---

### Phase 3: Database Verification (Supabase MCP)

#### Step 3.1: Verify Validation Results

**Action:** Check that all 3 test contacts were validated
```sql
SELECT
    email,
    debounce_validation_status,
    debounce_processing_status,
    debounce_result,
    debounce_score,
    debounce_reason,
    debounce_validated_at,
    brevo_sync_status,
    created_at
FROM contacts
WHERE email LIKE 'scheduler.test%'
ORDER BY email;
```

**Expected Results:**

| Email | Validation Status | Processing Status | Result | Score | Brevo Status |
|-------|------------------|-------------------|--------|-------|--------------|
| scheduler.test.valid@gmail.com | Complete | Complete | valid | 100 | Queued ✅ |
| scheduler.test@invalidtestdomain99999.com | Complete | Complete | invalid | 0 | New |
| scheduler.test@guerrillamail.com | Complete | Complete | invalid/disposable | 10-50 | New |

**Key Checks:**
- ✅ `debounce_processing_status` = 'Complete'
- ✅ `debounce_validated_at` is NOT NULL
- ✅ `debounce_score` is populated
- ✅ Valid email has `brevo_sync_status` = 'Queued' (auto-queued!)
- ✅ Invalid emails have `brevo_sync_status` = 'New' (not queued)

#### Step 3.2: Verify No Processing Errors

**Action:** Check for failed validations
```sql
SELECT
    email,
    debounce_processing_status,
    debounce_processing_error,
    retry_count,
    next_retry_at
FROM contacts
WHERE debounce_processing_status = 'Error'
AND email LIKE 'scheduler.test%';
```

**Expected Result:** 0 rows (no errors)

**If Errors Found:**
- Check `debounce_processing_error` field for error message
- Verify API key is correct
- Check DeBounce credits remaining
- Review retry_count (should be ≤ 3)

#### Step 3.3: Verify Auto-CRM Queue

**Action:** Confirm valid email was auto-queued for Brevo
```sql
SELECT
    email,
    debounce_result,
    debounce_score,
    brevo_sync_status,
    brevo_processing_status,
    hubspot_sync_status
FROM contacts
WHERE email = 'scheduler.test.valid@gmail.com';
```

**Expected Result:**
- `debounce_result` = 'valid'
- `debounce_score` = 90-100
- `brevo_sync_status` = 'Queued' ✅ (auto-queued!)
- `brevo_processing_status` = 'Queued'
- `hubspot_sync_status` = 'New' (only Brevo queued)

---

### Phase 4: Retry Logic Testing

#### Step 4.1: Create Contact That Will Fail

**Action:** Create contact with invalid API scenario
```sql
-- Note: This will test retry logic in a future scenario
-- For now, verify retry fields are properly managed

SELECT
    email,
    retry_count,
    last_retry_at,
    next_retry_at,
    debounce_processing_error
FROM contacts
WHERE email LIKE 'scheduler.test%'
AND retry_count > 0;
```

**Expected Result:** 0 rows (successful validations have retry_count = 0)

#### Step 4.2: Verify Retry Reset on Success

**Action:** Check that successful contacts have clean retry state
```sql
SELECT
    email,
    debounce_processing_status,
    retry_count,
    next_retry_at,
    last_retry_at
FROM contacts
WHERE email LIKE 'scheduler.test%'
AND debounce_processing_status = 'Complete';
```

**Expected Results:**
- `retry_count` = 0 for all successful validations
- `next_retry_at` = NULL for all successful validations
- `last_retry_at` may be NULL or have timestamp (depending on history)

---

### Phase 5: Continuous Operation Testing

#### Step 5.1: Queue Additional Contacts

**Action:** Add more contacts to test continuous processing
```sql
-- Reset Phase 1 test contacts to Queued
UPDATE contacts
SET
    debounce_validation_status = 'Queued',
    debounce_processing_status = 'Queued',
    debounce_validated_at = NULL,
    brevo_sync_status = 'New'
WHERE id IN (
    '8ef2449f-d3eb-4831-b85e-a385332b6475',  -- test.valid.email@gmail.com
    'f1bae019-a2a4-4caf-aeb6-43c1d8464fd6',  -- test@mailinator.com
    'bc5de95f-de77-4993-94a5-a2230349809b'   -- test@invaliddomain12345.com
)
RETURNING id, email, debounce_processing_status;
```

**Expected Result:** 3 contacts reset to 'Queued'

#### Step 5.2: Monitor Next Scheduler Cycle

**Action:** Wait for next 5-minute cycle

**Expected Behavior:**
1. Scheduler runs again after 5 minutes
2. Picks up the 3 re-queued contacts
3. Validates them successfully
4. Updates database with results

**Look for in Logs:**
```
🚀 Starting DeBounce validation scheduler cycle
📧 Validating 3 emails via DeBounce API
✅ Batch validation complete: 3 emails processed
✅ Finished DeBounce validation scheduler cycle
```

#### Step 5.3: Verify Scheduler Runs Continuously

**Action:** Monitor logs for 15 minutes

**Expected Pattern:**
```
T+0:00  - 🚀 Starting DeBounce validation scheduler cycle (initial)
T+5:00  - 🚀 Starting DeBounce validation scheduler cycle (cycle 2)
T+10:00 - 🚀 Starting DeBounce validation scheduler cycle (cycle 3)
T+15:00 - 🚀 Starting DeBounce validation scheduler cycle (cycle 4)
```

**Key Checks:**
- ✅ Scheduler runs every ~5 minutes
- ✅ No crashes or errors
- ✅ Graceful handling of empty queue (when no contacts queued)

---

## Performance Benchmarks

### Expected Metrics

**Startup Time:**
- Container build: 30-60 seconds
- Scheduler registration: < 1 second
- First cycle start: 0-5 minutes (interval-based)

**Processing Time:**
- Per-email validation: ~500ms (DeBounce API call)
- Database update: ~50ms per contact
- Total per contact: ~550ms
- Batch of 50: ~27 seconds

**Throughput:**
- Cycle interval: 5 minutes
- Batch size: 50 contacts
- Throughput: 600 contacts/hour

**DeBounce Credits:**
- Test cost: 6 credits (3 Phase 1 + 3 Phase 2)
- Remaining balance: Should be > 1,725,929

---

## Success Criteria

### ✅ Phase 2 Complete When:

**Scheduler Operation:**
- ✅ Scheduler starts successfully on Docker startup
- ✅ Scheduler registration logged without errors
- ✅ Scheduler runs every 5 minutes automatically
- ✅ No crashes or error loops

**Email Validation:**
- ✅ Valid emails detected correctly (score 90-100)
- ✅ Invalid emails detected correctly (score 0-10)
- ✅ Disposable emails detected correctly
- ✅ All 3 test scenarios pass

**Auto-CRM Queue:**
- ✅ Valid emails auto-queued for Brevo
- ✅ Invalid emails NOT queued
- ✅ Disposable emails NOT queued
- ✅ brevo_sync_status = 'Queued' for valid emails

**Database Updates:**
- ✅ All contacts marked as 'Complete'
- ✅ debounce_validated_at populated
- ✅ debounce_result populated correctly
- ✅ debounce_score populated correctly
- ✅ No processing errors

**Retry Logic:**
- ✅ Successful validations have retry_count = 0
- ✅ Successful validations have next_retry_at = NULL
- ✅ No infinite retry loops

---

## Troubleshooting Guide

### Problem: Scheduler Not Starting

**Symptoms:**
```
⚠️ DEBOUNCE_API_KEY not configured - DeBounce validation scheduler DISABLED
```

**Solution:**
1. Check `.env` file has `DEBOUNCE_API_KEY=691d38cd78602`
2. Rebuild Docker: `docker compose down && docker compose up --build`
3. Verify environment variable loaded: Check startup logs

### Problem: No Contacts Being Processed

**Symptoms:**
- Scheduler logs show "Starting cycle" but no validations
- No emails validated after 5+ minutes

**Diagnosis:**
```sql
-- Check if contacts are actually queued
SELECT COUNT(*)
FROM contacts
WHERE debounce_processing_status = 'Queued';
```

**Solution:**
1. If count = 0: Queue test contacts (Step 1.2)
2. If count > 0: Check scheduler is picking them up
3. Review logs for error messages

### Problem: Validation Failing

**Symptoms:**
```
❌ DeBounce API failed for email (HTTP 401/402/429)
```

**Solutions:**

**HTTP 401 - Invalid API Key:**
```
❌ Invalid DeBounce API key
```
- Verify API key: `DEBOUNCE_API_KEY=691d38cd78602`
- Check DeBounce dashboard for key status

**HTTP 402 - Credits Exhausted:**
```
❌ DeBounce credits exhausted
```
- Check DeBounce account balance
- Purchase more credits or upgrade plan

**HTTP 429 - Rate Limit:**
```
⚠️ DeBounce rate limit exceeded - will retry
```
- Reduce batch size: `DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE=10`
- Increase interval: `DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES=10`

### Problem: Contacts Stuck in 'Processing'

**Symptoms:**
- Contacts remain in 'Processing' status forever
- No completion or error status

**Diagnosis:**
```sql
SELECT
    email,
    debounce_processing_status,
    updated_at,
    NOW() - updated_at AS stuck_duration
FROM contacts
WHERE debounce_processing_status = 'Processing'
AND updated_at < NOW() - INTERVAL '10 minutes';
```

**Solution:**
1. Check logs for crash during processing
2. Reset stuck contacts:
```sql
UPDATE contacts
SET
    debounce_processing_status = 'Queued',
    retry_count = retry_count + 1
WHERE debounce_processing_status = 'Processing'
AND updated_at < NOW() - INTERVAL '10 minutes';
```
3. Restart Docker container

### Problem: Auto-Queue Not Working

**Symptoms:**
- Valid emails validated successfully
- But brevo_sync_status remains 'New'

**Diagnosis:**
```sql
SELECT
    email,
    debounce_result,
    debounce_score,
    brevo_sync_status,
    debounce_validated_at
FROM contacts
WHERE debounce_result = 'valid'
AND brevo_sync_status = 'New'
LIMIT 5;
```

**Solution:**
1. Check configuration:
```bash
DEBOUNCE_AUTO_QUEUE_VALID_EMAILS=true  # Must be true
DEBOUNCE_AUTO_QUEUE_DEFAULT_CRM=brevo  # Must be brevo/hubspot/etc
```
2. Review logs for auto-queue messages:
```
📤 Auto-queueing email@example.com for brevo sync
```
3. If missing, check service code or restart Docker

---

## Test Report Template

After completing all tests, create a test report:

```markdown
# WO-017 Phase 2 Test Report

**Date:** [Date]
**Tester:** Local Claude (Windsurf)
**Environment:** Docker + Supabase MCP
**Duration:** [X] minutes

## Test Results Summary

- ✅/❌ Scheduler started successfully
- ✅/❌ 3 test contacts validated
- ✅/❌ Auto-CRM queue working
- ✅/❌ Retry logic verified
- ✅/❌ Continuous operation confirmed

## Detailed Results

### Valid Email Test
- Email: scheduler.test.valid@gmail.com
- Result: [valid/invalid]
- Score: [0-100]
- Brevo Status: [Queued/New]
- ✅/❌ PASS

### Invalid Email Test
- Email: scheduler.test@invalidtestdomain99999.com
- Result: [valid/invalid]
- Score: [0-100]
- Brevo Status: [Queued/New]
- ✅/❌ PASS

### Disposable Email Test
- Email: scheduler.test@guerrillamail.com
- Result: [valid/invalid/disposable]
- Score: [0-100]
- Brevo Status: [Queued/New]
- ✅/❌ PASS

## Issues Found

[List any issues, or "None"]

## Recommendations

[Any suggestions for improvement]

## Next Steps

- [ ] Proceed to Phase 3 (API Endpoints)
- [ ] Report test results to Online Claude
- [ ] Deploy to production
```

---

## Quick Reference

### Essential Supabase Queries

**Check Queued Contacts:**
```sql
SELECT COUNT(*), debounce_processing_status
FROM contacts
GROUP BY debounce_processing_status;
```

**Check Validation Results:**
```sql
SELECT debounce_result, COUNT(*)
FROM contacts
WHERE debounce_result IS NOT NULL
GROUP BY debounce_result;
```

**Check Auto-Queue Success:**
```sql
SELECT COUNT(*)
FROM contacts
WHERE debounce_result = 'valid'
AND brevo_sync_status = 'Queued';
```

### Essential Docker Commands

**View Logs:**
```bash
docker compose logs -f app
```

**Restart:**
```bash
docker compose restart app
```

**Rebuild:**
```bash
docker compose down && docker compose up --build
```

**Stop:**
```bash
docker compose down
```

---

## Contact for Issues

If you encounter problems during testing:

1. **Check Logs First:** Most issues show clear error messages
2. **Review Troubleshooting Guide:** Common issues documented above
3. **Report to Online Claude:** Share logs and database state
4. **Document in Test Report:** Help improve the system

---

**Status:** ⏳ **READY FOR TESTING**
**Priority:** 🟢 **HIGH** - Phase 2 completion blocker
**Estimated Time:** 30-45 minutes
**Next:** Phase 3 (API Endpoints) after successful Phase 2 test
