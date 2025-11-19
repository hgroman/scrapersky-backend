# WO-004 Deployment Hotfix Post-Mortem
**Date:** November 17, 2025  
**Duration:** ~2 hours (12:30 AM - 1:30 AM)  
**Severity:** CRITICAL - Complete WF4→WF5 pipeline failure  
**Status:** RESOLVED

---

## Executive Summary

WO-004 deployment succeeded, but exposed a **critical, pre-existing bug** in the domain-to-sitemap workflow that had been **silently failing since September 9, 2025**. The bug was masked by a disabled scheduler and only became visible when the WO-001/WO-002 security fixes broke the authentication workaround.

**Impact:**
- All domain sitemap submissions failing
- Zero sitemap extraction happening in production
- WF4→WF5 pipeline completely broken

**Root Cause:**
- September 9th: Sitemap job processor was disabled without replacement
- Domain adapter service was creating jobs but not triggering processing
- Jobs accumulated in "pending" state forever

---

## Timeline of Events

### Pre-History (Before Tonight)

**April 24, 2025**
- `domain_to_sitemap_adapter_service.py` created
- Used HTTP calls with `settings.DEV_TOKEN`
- **Never triggered background processing** (original bug)

**June 28, 2025**
- File deleted as part of refactoring

**July 28, 2025**
- File restored after 4+ hour emergency debugging session
- Restored with same HTTP-only approach (bug persisted)

**September 9, 2025** ⚠️ **CRITICAL CHANGE**
- Sitemap job processor in `sitemap_scheduler.py` was **DISABLED**
- Comment: "This entire workflow is being replaced by the modern, SDK-based sitemap_import_scheduler"
- **NO REPLACEMENT WAS IMPLEMENTED**
- From this point forward, sitemap jobs were created but never processed

**September (Before 9th)**
- User's end-to-end tests passed (job processor was still active)

**September 9th - November 17th**
- Silent failure: Jobs created, marked "submitted", but never processed
- No errors logged because technically "everything worked"
- Jobs accumulated in database with status "pending"

### Tonight's Events

**12:30 AM - Initial Deployment**
- WO-004 multi-scheduler split deployed successfully
- User reports "invalid authentication submitted" error

**12:32 AM - WO-001/WO-002 Security Fix Deployed**
- Dev bypass token `"scraper_sky_2024"` restricted to development-only
- Broke domain adapter's HTTP authentication

**12:35 AM - First Hotfix Attempt (Commit 8604a37)**
- Changed to use `settings.SUPABASE_SERVICE_ROLE_KEY`
- **FAILED:** Wrong case (uppercase vs lowercase)

**12:43 AM - Second Hotfix Attempt (Commit d9e4fc2)**
- Fixed case: `settings.supabase_service_role_key`
- **FAILED:** Service role key not valid for JWT authentication

**12:55 AM - Third Hotfix Attempt (Commit 1ffa371)**
- Removed HTTP calls entirely
- Called `job_service.create()` directly
- **FAILED:** Jobs created but not processed (original bug exposed)

**1:18 AM - Final Fix (Commit 9f091f6)**
- Added background task trigger: `asyncio.create_task()`
- Initialized job in `_job_statuses` memory
- **SUCCESS:** Sitemap extraction working

**1:30 AM - Verification**
- 20+ sitemap_files records created
- Multiple domains successfully processed
- WF4→WF5 pipeline operational

---

## Root Cause Analysis

### The Original Bug (April 2025)

The `domain_to_sitemap_adapter_service.py` was **fundamentally broken from day one**:

```python
# What it did:
1. Create job in database
2. Make HTTP call to /api/v3/sitemap/scan
3. Return success

# What it SHOULD have done:
1. Create job in database
2. Initialize job in _job_statuses (memory)
3. Trigger background processing via asyncio.create_task()
4. Return success
```

The HTTP endpoint does all three steps. The adapter only did step 1.

### Why It "Worked" (Until September 9th)

The `sitemap_scheduler.py` had a **separate job processor** that would:
- Query for jobs with status "pending"
- Process them in a loop
- This compensated for the adapter's missing step 3

**Code (sitemap_scheduler.py lines 137-179):**
```python
pending_sitemap_jobs = await job_service.get_pending_jobs(
    fetch_session, job_type="sitemap", limit=limit
)
for job in pending_sitemap_jobs:
    await process_domain_with_own_session(...)
```

### Why It Stopped Working (September 9th)

That entire code block was **commented out**:

```python
# DISABLED as per new PRD v1.2 and holistic analysis.
# This entire workflow is being replaced by the modern, SDK-based sitemap_import_scheduler.
# pending_sitemap_jobs = []
# try:
#     ...all the processing code...
```

**The replacement never happened.** The `sitemap_import_scheduler` processes **SitemapFile** records, not **Job** records.

### Why Tonight's Security Fix Exposed It

The security fix changed the failure mode:
- **Before:** Jobs created, marked "submitted", sat pending forever (silent failure)
- **After:** HTTP authentication failed, jobs not created, error visible (loud failure)

The loud failure forced us to investigate, which exposed the underlying bug.

---

## The Fix (Commit 9f091f6)

### What We Changed

```python
# BEFORE (Broken):
job = await job_service.create(session, job_data)
domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.submitted
return True

# AFTER (Fixed):
job = await job_service.create(session, job_data)

# Initialize job in memory (required for background processing)
from src.services.sitemap.processing_service import _job_statuses
_job_statuses[job_id] = {
    "status": "pending",
    "created_at": datetime.utcnow().isoformat(),
    "domain": domain.domain,
    "progress": 0.0,
    "metadata": {"sitemaps": []},
}

# Trigger background processing
import asyncio
from src.services.sitemap.processing_service import process_domain_with_own_session

asyncio.create_task(
    process_domain_with_own_session(
        job_id=job_id,
        domain=domain.domain,
        user_id=None,
        max_urls=1000,
    )
)

domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.submitted
return True
```

### Why This Is The Right Fix

This matches **exactly** what the HTTP endpoint does (modernized_sitemap.py lines 152-174):
1. Creates job in database
2. Initializes in-memory state
3. Triggers background processing
4. Returns immediately

No scheduler needed. Jobs process immediately when created.

---

## Architecture Diagrams

### BEFORE (Broken Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│ WF3: Domain Extraction                                      │
│ (LocalBusiness → Domain)                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Domain Sitemap Submission Scheduler                         │
│ - Runs every 1 minute                                       │
│ - Fetches domains with status "queued"                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ DomainToSitemapAdapterService                               │
│ ❌ Makes HTTP call to /api/v3/sitemap/scan                  │
│ ❌ Creates Job in database                                  │
│ ❌ Does NOT trigger processing                              │
│ ❌ Returns "success"                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Job Table                                                   │
│ - job_id: "abc-123"                                         │
│ - status: "pending" ← STUCK HERE FOREVER                    │
│ - job_type: "sitemap"                                       │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
                  ❌ DEAD END
     (Sitemap Scheduler Disabled Sept 9th)
```

### AFTER (Fixed Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│ WF3: Domain Extraction                                      │
│ (LocalBusiness → Domain)                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Domain Sitemap Submission Scheduler                         │
│ - Runs every 1 minute                                       │
│ - Fetches domains with status "queued"                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ DomainToSitemapAdapterService                               │
│ ✅ Calls job_service.create() directly (no HTTP)            │
│ ✅ Initializes job in _job_statuses (memory)                │
│ ✅ Triggers asyncio.create_task()                           │
│ ✅ Returns "success"                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─────────────────┬──────────────────────┐
                     ▼                 ▼                      ▼
              ┌──────────┐      ┌──────────┐         ┌──────────┐
              │ Job DB   │      │ Memory   │         │ Async    │
              │ Record   │      │ State    │         │ Task     │
              └──────────┘      └──────────┘         └────┬─────┘
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────┐
│ process_domain_with_own_session()                           │
│ - Fetches sitemap URLs                                      │
│ - Creates SitemapFile records                               │
│ - Updates job status to "complete"                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ WF5: Sitemap Import Scheduler                               │
│ - Processes SitemapFile records                             │
│ - Extracts URLs → Page records                              │
└─────────────────────────────────────────────────────────────┘
```

### Service Communication Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ WRONG PATTERN (What We Had)                                 │
│                                                             │
│  Service A ──HTTP──> API Endpoint ──> Service B            │
│                      (Auth Required)                        │
│                                                             │
│  Problems:                                                  │
│  - Network overhead                                         │
│  - Authentication complexity                                │
│  - Failure points                                           │
│  - Doesn't trigger background tasks                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ RIGHT PATTERN (What We Fixed)                               │
│                                                             │
│  Service A ──Direct Call──> Service B                       │
│                                                             │
│  Benefits:                                                  │
│  - No network overhead                                      │
│  - No authentication needed                                 │
│  - Single point of failure                                  │
│  - Can trigger background tasks                             │
│  - Same pattern as ALL other working schedulers             │
└─────────────────────────────────────────────────────────────┘
```

---

## Why This Was So Painful

### 1. **Multiple Compounding Issues**

Each fix exposed a new layer:
1. Authentication broken (security fix side effect)
2. Wrong attribute name (case sensitivity)
3. Wrong authentication method (JWT vs API key)
4. Missing background task trigger (original bug)

### 2. **No Logging for Silent Failures**

Jobs were created successfully, so no errors were logged. The system appeared to work but was actually broken.

### 3. **Misleading Success Indicators**

- Domain status: "submitted" ✅
- Job created in DB ✅
- No errors ❌
- **But nothing actually happened** ❌

### 4. **Historical Context Lost**

The September 9th change that disabled the job processor had no migration plan or documentation about what would replace it.

### 5. **Pattern Inconsistency**

- Deep scan scheduler: Direct service calls ✅
- Domain extraction scheduler: Direct service calls ✅
- Sitemap adapter: HTTP calls ❌ (wrong pattern)

---

## Lessons Learned

### 1. **Service-to-Service Communication**

**RULE:** Internal services MUST call each other directly, never via HTTP.

**Pattern:**
```python
# ✅ CORRECT
service = SomeService()
result = await service.process(item_id, session)

# ❌ WRONG
async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8000/api/...")
```

### 2. **Background Task Triggers**

**RULE:** If an HTTP endpoint uses `BackgroundTasks.add_task()`, any service that replicates that endpoint MUST use `asyncio.create_task()`.

**Pattern:**
```python
# When creating a job that needs processing:
1. Create job in database
2. Initialize in-memory state (_job_statuses)
3. Trigger background processing (asyncio.create_task)
```

### 3. **Scheduler Deprecation**

**RULE:** When disabling a scheduler, document:
- What it was doing
- What will replace it
- Migration plan
- Verification that replacement works

### 4. **Silent Failure Detection**

**RULE:** Add monitoring for:
- Jobs stuck in "pending" state > X minutes
- Expected downstream records not appearing
- Status transitions that should happen but don't

### 5. **End-to-End Testing**

**RULE:** After any scheduler changes, run full WF1→WF7 test to verify nothing broke.

---

## Verification Checklist

### ✅ Immediate Verification (Completed)

- [x] Domain records created with status "queued"
- [x] Jobs created in database
- [x] Jobs processed (status changed to "complete")
- [x] SitemapFile records created
- [x] Multiple domains tested successfully

### 🔄 24-Hour Monitoring

- [ ] No jobs stuck in "pending" > 5 minutes
- [ ] All domains with status "submitted" have corresponding sitemap_files
- [ ] No authentication errors in logs
- [ ] Scheduler running without errors

### 📊 Metrics to Track

```sql
-- Jobs stuck in pending
SELECT COUNT(*) FROM jobs 
WHERE job_type = 'sitemap' 
  AND status = 'pending' 
  AND created_at < NOW() - INTERVAL '5 minutes';

-- Domains submitted but no sitemaps
SELECT COUNT(*) FROM domains d
LEFT JOIN sitemap_files sf ON d.id = sf.domain_id
WHERE d.sitemap_analysis_status = 'submitted'
  AND sf.id IS NULL
  AND d.updated_at < NOW() - INTERVAL '5 minutes';
```

---

## Action Items

### Immediate (This Week)

1. **Add monitoring alerts** for jobs stuck in pending
2. **Document service communication pattern** in architecture docs
3. **Review all schedulers** for similar HTTP-based anti-patterns
4. **Add end-to-end test** for WF4→WF5 pipeline

### Short-Term (Next Sprint)

1. **Audit all disabled schedulers** - verify replacements exist
2. **Add health check endpoint** that verifies job processing
3. **Create runbook** for scheduler debugging
4. **Add metrics dashboard** for job processing

### Long-Term (Next Quarter)

1. **Implement job monitoring service** (detect stuck jobs automatically)
2. **Create scheduler framework** (standardize patterns)
3. **Add integration tests** for all workflow transitions
4. **Document all workflow dependencies** in architecture diagrams

---

## Related Commits

- `9f091f6` - Final fix: trigger background processing
- `1ffa371` - Remove HTTP calls, use direct service calls
- `d9e4fc2` - Fix case sensitivity in settings
- `8604a37` - Initial authentication fix attempt
- `0aaaad6` - Sept 9th: Disabled sitemap job processor (root cause)

---

## Related Documents

- `WO-004_Multi_Scheduler_Split.md` - Original work order
- `WO-004_DEPLOYMENT_MONITORING.md` - Deployment guide
- `WO-001` & `WO-002` - Security fixes that exposed the bug
- `05_SCHEDULERS_WORKFLOWS.md` - Scheduler architecture

---

## Conclusion

This incident revealed a **7-month-old silent failure** that was masked by a compensating mechanism (the sitemap job processor). When that mechanism was removed in September without a replacement, the system appeared to work but was actually broken.

The security fixes deployed tonight changed the failure mode from silent to loud, forcing us to investigate and ultimately fix the root cause.

**The system is now more robust than before:**
- No HTTP overhead for internal calls
- No authentication complexity
- Immediate job processing (no scheduler dependency)
- Consistent pattern with other working schedulers

**Total Time:** 2 hours of intense debugging  
**Root Cause Age:** 7 months (since April 2025)  
**Silent Failure Period:** 2+ months (since September 9th)  
**Impact:** CRITICAL - Complete WF4→WF5 pipeline failure  
**Resolution:** COMPLETE - Pipeline operational and more robust

---

**Prepared by:** Cascade AI  
**Reviewed by:** [Pending]  
**Date:** November 17, 2025 1:33 AM
