# INCIDENT-2025-09-09-scheduler-disabled

## Metadata
- **Date:** September 9, 2025
- **Severity:** CRITICAL
- **Duration:** 69 days (until Nov 17 fix)
- **Workflows Affected:** WF4, WF5, WF7
- **Status:** Resolved (indirectly via Commit 9f091f6)

---

## Symptoms

- Sitemap job processor code commented out
- Comment: "DISABLED as per new PRD v1.2 and holistic analysis"
- Comment: "This entire workflow is being replaced by the modern, SDK-based sitemap_import_scheduler"
- No replacement actually implemented

---

## Root Cause

**Incomplete refactoring** - Disabled old system without implementing replacement

**Code (sitemap_scheduler.py lines 131-179):**
```python
# DISABLED as per new PRD v1.2 and holistic analysis.
# This entire workflow is being replaced by the modern, SDK-based sitemap_import_scheduler.
# pending_sitemap_jobs = []
# try:
#     pending_sitemap_jobs = await job_service.get_pending_jobs(
#         fetch_session, job_type="sitemap", limit=limit
#     )
#     ...all processing code commented out...
```

**What was disabled:**
- Job queue processor that picked up pending sitemap jobs
- Backup mechanism for jobs that weren't immediately processed

**What was supposed to replace it:**
- `sitemap_import_scheduler` - but this processes **SitemapFile** records, not **Job** records
- Mismatch: Different data models, different workflows

---

## Why It Was Hidden

1. **No immediate errors** - Code simply stopped running
2. **Assumed replacement existed** - Comment said it was "being replaced"
3. **No verification** - Didn't test that replacement actually worked
4. **Adapter bug compensated** - DomainToSitemapAdapterService was supposed to trigger jobs directly (but didn't)

---

## Investigation

Discovered during Nov 17, 2025 debugging session:

```bash
git log -p -S "DISABLED as per new PRD" -- src/services/sitemap_scheduler.py
# Found: Commit 0aaaad6, Sept 9, 2025
```

**Commit message:** "fix: Commit status updates and improve transaction handling in schedulers"

**Actual change:** Disabled 88 lines of job processing code

---

## The "Fix"

No direct fix. Instead, fixed the root cause:
- **Commit 9f091f6** - Made DomainToSitemapAdapterService trigger jobs immediately
- This eliminated need for job queue processor
- Jobs now process immediately when created, not queued for scheduler

---

## Lessons Learned

### 1. Never Disable Without Verified Replacement
**Lesson:** "Being replaced" ≠ "Has been replaced"

**Checklist before disabling code:**
- [ ] Replacement implemented?
- [ ] Replacement tested?
- [ ] Replacement handles all cases?
- [ ] No gaps in functionality?

### 2. Document Dependencies
**Lesson:** The adapter depended on this scheduler as backup

**Prevention:**
- Document what depends on what
- Test without compensating mechanisms
- Verify end-to-end after changes

### 3. Verify Replacement Compatibility
**Lesson:** `sitemap_import_scheduler` processes different data model

**Prevention:**
- Ensure replacement handles same inputs/outputs
- Don't assume similar names mean same functionality
- Test data flow end-to-end

---

## Related Incidents

### Downstream (Caused By This)
- **[INCIDENT-2025-11-17-sitemap-jobs-not-processing](./2025-11-17-sitemap-jobs-not-processing.md)**
  - This disabled the compensating mechanism
  - Exposed the adapter's missing trigger

---

## Prevention

- [x] Document this incident
- [x] Add to DECISIONS/ log
- [ ] Create "Disabling Code" checklist
- [ ] Add dependency mapping
- [ ] Require end-to-end tests before disabling

---

## Impact

- **Duration:** 69 days of silent failure
- **Records Affected:** All domains processed during this period
- **Business Impact:** Complete WF4→WF5→WF7 pipeline failure

---

**Status:** Resolved via different approach (immediate job triggering). Original scheduler remains disabled but is no longer needed.
