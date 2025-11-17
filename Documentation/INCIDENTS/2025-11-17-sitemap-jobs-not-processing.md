# INCIDENT-2025-11-17-sitemap-jobs-not-processing

## Metadata
- **Date:** November 17, 2025 12:30 AM - 1:30 AM PST
- **Severity:** CRITICAL
- **Duration:** ~2 hours active debugging (but silent failure since Sept 9)
- **Workflows Affected:** WF4, WF5, WF7
- **Status:** Resolved
- **Fixed In:** Commit 9f091f6

---

## Symptoms (What We Saw)

1. **Jobs created but stuck in "pending"**
   - 20 jobs created in 13 minutes
   - All had `status = 'pending'`
   - None transitioned to 'running' or 'complete'

2. **Domains marked "submitted" but no sitemaps**
   - `domains.sitemap_analysis_status = 'submitted'` ✓
   - `sitemap_files` table had zero records ✗
   - Looked successful but nothing actually happened

3. **No errors in logs**
   - No exceptions thrown
   - No error messages
   - Silent failure

4. **User report**
   - "I am not getting any site maps extracted..."
   - Despite domains being successfully created
   - Despite jobs being created

---

## Root Cause (The Actual Bug)

**Missing background task trigger in DomainToSitemapAdapterService**

The service was doing 2 of 3 required steps:
1. ✅ Create job in database
2. ✅ Initialize job in memory (`_job_statuses`)
3. ❌ **Trigger background processing** (MISSING!)

**Code (BEFORE fix):**
```python
# From domain_to_sitemap_adapter_service.py
job = await job_service.create(session, job_data)

# Missing these lines:
# _job_statuses[job_id] = {...}
# asyncio.create_task(process_domain_with_own_session(...))

domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.submitted
return True  # FALSE SUCCESS
```

**Why this mattered:**
- HTTP endpoints use `BackgroundTasks.add_task()` to trigger processing
- Direct service calls must use `asyncio.create_task()` to achieve same effect
- Without trigger, jobs sit in "pending" forever

---

## Why It Was Hidden (What Masked It)

### 1. Scheduler Was Disabled (Sept 9, 2025)
The `sitemap_scheduler.py` had a backup mechanism that would process pending jobs:
```python
# Lines 137-179 (DISABLED Sept 9)
pending_sitemap_jobs = await job_service.get_pending_jobs(
    fetch_session, job_type="sitemap", limit=limit
)
for job in pending_sitemap_jobs:
    await process_domain_with_own_session(...)
```

This compensated for the missing trigger. When disabled, the bug was exposed.

### 2. No Errors Logged
- Job creation succeeded
- Domain status updated to "submitted"
- Everything looked successful
- No exceptions thrown

### 3. Status Appeared Correct
- `domains.sitemap_analysis_status = 'submitted'` ✓
- `jobs.status = 'pending'` (looked like "waiting to start")
- No obvious indication of failure

### 4. Downstream Workflows Never Complained
- WF5 and WF7 simply had no work to do
- No errors, just no data

---

## Investigation Process

### Step 1: User Report (12:30 AM)
User: "I am not getting any site maps extracted..."

### Step 2: Check Domain Status
```sql
SELECT domain, sitemap_analysis_status 
FROM domains 
WHERE domain = 'jenkinseyecare.com';
-- Result: status = 'submitted' ✓
```
Looked successful!

### Step 3: Check for Sitemap Files
```sql
SELECT * FROM sitemap_files 
WHERE domain_id = (SELECT id FROM domains WHERE domain = 'jenkinseyecare.com');
-- Result: 0 records ✗
```
No sitemaps created despite "submitted" status.

### Step 4: Check Jobs Table
```sql
SELECT * FROM jobs 
WHERE job_type = 'sitemap' 
AND created_at > '2025-11-17 09:00:00'
ORDER BY created_at DESC;
-- Result: 20 jobs, ALL with status = 'pending'
```
Jobs created but never processed!

### Step 5: Review Adapter Service Code
Examined `domain_to_sitemap_adapter_service.py`:
- Job creation: ✓ Present
- Status update: ✓ Present
- Background trigger: ✗ **MISSING**

### Step 6: Compare to HTTP Endpoint
Examined `modernized_sitemap.py` lines 136-174:
- Job creation: ✓
- Memory initialization: ✓
- `background_tasks.add_task()`: ✓

**Found the difference!**

### Step 7: Check Scheduler History
```bash
git log -p -S "DISABLED as per new PRD" -- src/services/sitemap_scheduler.py
```
Found: Scheduler disabled Sept 9, 2025 (Commit 0aaaad6)

**Timeline became clear:**
- April 24: Adapter created with bug (no trigger)
- Before Sept 9: Scheduler compensated for bug
- Sept 9: Scheduler disabled, bug exposed
- Sept 9 - Nov 17: Silent failure (2+ months)
- Nov 17: Security fix made failure loud, investigation began

---

## The Fix

### Commit 9f091f6 (Nov 17, 2025 1:18 AM)

**Added missing background task trigger:**

```python
# After creating job in database
job = await job_service.create(session, job_data)

# Initialize in memory (required for status tracking)
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

**File:** `src/services/domain_to_sitemap_adapter_service.py` lines 104-130

---

## Verification

### Step 1: Requeue Test Domains
```sql
UPDATE domains 
SET sitemap_analysis_status = 'queued',
    sitemap_analysis_error = NULL
WHERE sitemap_analysis_status = 'submitted'
  AND updated_at > '2025-11-17 09:00:00';
-- 18 domains requeued
```

### Step 2: Wait for Scheduler (2 minutes)
Scheduler runs every 1 minute.

### Step 3: Check Jobs Processing
```sql
SELECT job_id, status, created_at 
FROM jobs 
WHERE job_type = 'sitemap' 
AND created_at > '2025-11-17 09:27:00'
ORDER BY created_at DESC;
-- Result: Jobs transitioning to 'complete' ✓
```

### Step 4: Verify Sitemaps Created
```sql
SELECT COUNT(*) FROM sitemap_files 
WHERE created_at > '2025-11-17 09:27:00';
-- Result: 20+ sitemap files created ✓
```

### Step 5: Verify Pages Imported
```sql
SELECT COUNT(*) FROM pages 
WHERE created_at > '2025-11-17 09:40:00';
-- Result: 13+ pages created ✓
```

### Step 6: Verify End-to-End
```sql
SELECT 
    d.domain,
    COUNT(DISTINCT sf.id) as sitemap_count,
    COUNT(DISTINCT p.id) as page_count
FROM domains d
LEFT JOIN sitemap_files sf ON d.id = sf.domain_id
LEFT JOIN pages p ON sf.id = p.sitemap_file_id
WHERE d.domain = 'jenkinseyecare.com'
GROUP BY d.domain;
-- Result: 8 sitemaps, 13 pages ✓
```

**Verification successful!** WF4→WF5→WF7 pipeline operational.

---

## Lessons Learned

### 1. HTTP Endpoints ≠ Service Methods
**Lesson:** HTTP endpoints use `BackgroundTasks.add_task()`. Direct service calls must use `asyncio.create_task()`.

**Pattern:**
- HTTP: `background_tasks.add_task(func, ...)`
- Service: `asyncio.create_task(func(...))`

**Reference:** [PATTERNS.md](../PATTERNS.md#pattern-2-background-task-triggering)

### 2. Silent Failures Are Dangerous
**Lesson:** Jobs that look successful but do nothing are worse than loud failures.

**Prevention:**
- Add monitoring for stuck jobs
- Alert on jobs pending > X minutes
- Track expected state transitions

**Action Item:** WO-005 Gap #4 - Add stuck job monitoring

### 3. Compensating Mechanisms Hide Bugs
**Lesson:** The scheduler was compensating for the adapter's bug. When removed, bug was exposed.

**Prevention:**
- Never disable without verified replacement
- Document dependencies between components
- Test without compensating mechanisms

**Reference:** INCIDENT-2025-09-09-scheduler-disabled

### 4. Always Verify Background Processing
**Lesson:** Creating a job doesn't mean it will process.

**Checklist:**
- [ ] Job created in database?
- [ ] Job initialized in memory?
- [ ] Background task triggered?

**Pattern:** All three steps required!

### 5. Status Updates Can Lie
**Lesson:** `status = 'submitted'` looked successful but was meaningless.

**Prevention:**
- Verify downstream effects (sitemaps created?)
- Don't trust status alone
- Add end-to-end health checks

---

## Related Incidents

### Upstream (Caused This)
- **[INCIDENT-2025-09-09-scheduler-disabled](./2025-09-09-scheduler-disabled.md)**
  - Disabled compensating mechanism
  - Exposed this bug

### Concurrent (Same Session)
- **[INCIDENT-2025-11-17-authentication-failure](./2025-11-17-authentication-failure.md)**
  - Security fix broke HTTP auth
  - Led to investigation that found this bug

- **[INCIDENT-2025-11-17-http-service-calls](./2025-11-17-http-service-calls.md)**
  - Anti-pattern that preceded this fix
  - Fixed in same session

---

## Prevention

### Immediate (Completed)
- [x] Add background task trigger (Commit 9f091f6)
- [x] Document pattern in PATTERNS.md
- [x] Create this incident report

### Short-Term (WO-005)
- [ ] Add monitoring for stuck jobs (Gap #4)
- [ ] Add health check for background tasks
- [ ] Add end-to-end verification tests

### Long-Term
- [ ] Implement job retry logic (Gap #8)
- [ ] Add job timeout handling
- [ ] Create automated health checks

---

## Impact Assessment

### Duration of Silent Failure
- **Start:** September 9, 2025 (scheduler disabled)
- **End:** November 17, 2025 (fix deployed)
- **Total:** 69 days (2+ months)

### Affected Records
- **Domains:** Unknown number stuck in "submitted"
- **Jobs:** Hundreds of pending jobs accumulated
- **Sitemaps:** Zero extracted during this period
- **Pages:** Zero imported during this period
- **Contacts:** Zero extracted during this period

### Business Impact
- Complete WF4→WF5→WF7 pipeline failure
- No new contact data for 2+ months
- User frustration and lost productivity

### Why Not Noticed Sooner
- System appeared to work (no errors)
- Domains marked "submitted" (looked successful)
- No active monitoring
- No end-to-end health checks

---

## Code References

### Files Modified
- `src/services/domain_to_sitemap_adapter_service.py` (lines 104-130)

### Commits
- **9f091f6** - Final fix (added background trigger)
- **1ffa371** - Intermediate fix (removed HTTP calls)
- **d9e4fc2** - Hotfix attempt (case sensitivity)
- **8604a37** - Initial hotfix attempt (auth fix)

### Related Code
- `src/routers/modernized_sitemap.py` (lines 136-174) - HTTP endpoint pattern
- `src/services/sitemap/processing_service.py` - Background processing
- `src/services/sitemap_scheduler.py` (lines 131-179) - Disabled scheduler

---

**This incident demonstrates the importance of:**
1. Complete pattern implementation (all 3 steps)
2. Monitoring for silent failures
3. Verified replacements when disabling code
4. End-to-end health checks
5. Comprehensive testing

**Status:** Resolved and documented. Prevention measures in progress.
