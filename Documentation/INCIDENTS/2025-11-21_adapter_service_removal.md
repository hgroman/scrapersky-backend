# Production Incident Report: Adapter Service Removal

**Incident ID:** 2025-11-21-ADAPTER-SERVICE-REMOVAL  
**Date:** November 21, 2025  
**Severity:** Critical (P0)  
**Status:** Resolved  
**Duration:** ~19 hours (00:53 AM - 07:33 PM PST)

---

## Executive Summary

Sitemap discovery completely failed for 19 hours due to accidental promotion of broken code during a file rename refactor. The working scheduler was replaced with a "fixed" version that removed the critical adapter service call, preventing any sitemaps from being inserted into the database despite successful discovery.

---

## Timeline (PST)

| Time | Event |
|------|-------|
| 00:53 AM | Rename refactor (commit `9080221`) promoted broken scheduler |
| 00:53 AM - 07:33 PM | **Complete sitemap insertion failure** - 0 new sitemaps created |
| 06:12 PM | User reported no sitemaps being inserted (related to earlier OOM incident) |
| 07:00 PM | Investigation revealed scheduler was running but not inserting sitemaps |
| 07:18 PM | Root cause identified - adapter service call was removed |
| 07:28 PM | Fix deployed (commit `d5e98fd`) - restored adapter service call |
| 07:33 PM | Verified working - new sitemaps being inserted |

---

## Root Cause Analysis

### Primary Cause
**File:** `src/services/background/wf4_sitemap_discovery_scheduler.py`  
**Issue:** Accidental promotion of broken "_fixed" version during rename refactor

### The Fatal Mistake

**Two versions existed:**
1. `domain_sitemap_submission_scheduler.py` (WORKING) - Called adapter service
2. `domain_sitemap_submission_scheduler_fixed.py` (BROKEN) - Removed adapter service

**What happened:**
- AI performing rename refactor saw two similar files
- Assumed "_fixed" suffix meant "better version"
- Renamed the BROKEN version to `wf4_sitemap_discovery_scheduler.py`
- Deleted both old versions
- **Never asked which version was correct**

### The Missing Code

**What was removed:**
```python
adapter_service = DomainToSitemapAdapterService()
await adapter_service.submit_domain_to_legacy_sitemap(
    domain_id=domain.id,
    session=session,
)
```

**What replaced it:**
```python
sitemap_results = await sitemap_analyzer.analyze_domain_sitemaps(str(domain_url))
# Analyzer returned results but NEVER inserted into database
```

### Why It Failed Silently

1. **Scheduler ran successfully** - no errors thrown
2. **Analyzer discovered sitemaps** - returned valid results
3. **Domains marked as "submitted"** - status updated correctly
4. **BUT: No database insertion** - adapter service was never called
5. **No monitoring alerts** - system appeared healthy

---

## Impact Assessment

### Availability
- **Sitemap Discovery:** 100% insertion failure for 19 hours
- **Sitemap Analysis:** Continued to work (discovery happened, just not insertion)
- **User Impact:** No new domains could have sitemaps saved to database

### Data Integrity
- **Database:** No data corruption
- **Lost Sitemaps:** All domains processed during outage need reprocessing
- **Recovery:** Automatic - scheduler will retry domains with NULL status

### Business Impact
- **New Domains:** Could not be processed for sitemap-based page discovery
- **Existing Workflows:** Unaffected (existing sitemaps continued processing)

---

## Resolution

### Fix Applied
**Commit:** `d5e98fd`  
**Changes:**
1. Added import: `from src.services.domain_to_sitemap_adapter_service import DomainToSitemapAdapterService`
2. Replaced direct analyzer call with adapter service call
3. Adapter service creates sitemap job via `job_service`
4. Job triggers `process_domain_with_own_session()` in background
5. Sitemaps are discovered AND inserted into database

### Verification
- Deployed to production at 7:28 PM
- Tested with `wordpress.org` domain
- Confirmed sitemaps being inserted within 2 minutes
- System fully operational

---

## Related Incidents

1. **[2025-11-21 OOM Crash Loop](./2025-11-21_production_oom_crash_loop.md)** - Sitemap analyzer OOM issues
2. **[2025-11-21 Sitemap Discovery Failure](./2025-11-21_sitemap_discovery_failure.md)** - Sitemap index processing bug

All three incidents occurred on the same day, creating a cascade of sitemap-related failures.

---

## Lessons Learned

### What Went Wrong

1. **AI made critical assumption** - assumed "_fixed" = "better" without verification
2. **No verification of active version** - didn't check which file was imported in `main.py`
3. **No comparison of versions** - didn't diff the two files to see differences
4. **No end-to-end testing** - rename was assumed safe without functional testing
5. **No explicit approval** - AI should have stopped and asked which version to use

### What Went Right

1. **User caught it quickly** - reported issue same day
2. **Git history preserved both versions** - could recover working code
3. **Fast diagnosis** - root cause identified within 1 hour of investigation
4. **Clean fix** - single commit restored functionality

---

## Action Items

### Immediate (Completed)
- [x] Restore adapter service call
- [x] Deploy fix to production
- [x] Verify sitemaps being inserted
- [x] Document incident

### Short-term (Next 7 days)
- [ ] Add integration test: "Scheduler creates sitemap_files records"
- [ ] Add monitoring alert: "Zero new sitemaps in last hour"
- [ ] Review all "_fixed" files in codebase - verify which are actually being used
- [ ] Create git pre-commit hook: Flag file deletions during renames
- [ ] Add code review checklist: "Verify renamed file is the active version"

### Long-term (Next 30 days)
- [ ] **Establish AI pairing protocol:** AI MUST stop and ask when encountering:
  - Multiple similar files during rename/cleanup
  - Files with "_fixed", "_new", "_old" suffixes
  - Any file deletion during refactor
  - Any code removal that looks like business logic
- [ ] Add automated test: "All schedulers create expected database records"
- [ ] Implement canary deployments for scheduler changes
- [ ] Create "critical files" list that requires extra review

---

## Prevention Measures

### Code Quality
1. **No "_fixed" suffixes** - use git branches for fixes, not parallel files
2. **Delete unused code immediately** - don't leave "backup" versions in codebase
3. **Explicit imports** - verify which version is imported before renaming

### AI Pairing Protocol
1. **STOP and ASK when:**
   - Multiple similar files exist
   - File has "_fixed", "_new", "_backup" suffix
   - Deleting files during refactor
   - Removing code that looks like business logic
2. **NEVER assume:**
   - Newer = better
   - "_fixed" = correct
   - Unused = safe to delete
3. **ALWAYS verify:**
   - Which version is imported/used
   - Diff between similar files
   - End-to-end functionality after rename

### Process
1. **Rename checklist:**
   - [ ] Verify file is imported in `main.py` or other entry points
   - [ ] Check for similar files - ask which is correct
   - [ ] Diff similar files to understand differences
   - [ ] Test end-to-end after rename
   - [ ] Get explicit approval for any file deletions

---

## Related Commits

- `9080221` - **Rename refactor** (introduced bug)
- `d5e98fd` - **Adapter service restoration** (resolved incident)

---

## Related Files

- `src/services/background/wf4_sitemap_discovery_scheduler.py` - Scheduler that was broken
- `src/services/domain_to_sitemap_adapter_service.py` - Critical service that was removed
- `src/services/sitemap/processing_service.py` - Handles actual sitemap insertion

---

## Incident Commander

**Agent:** Antigravity  
**User:** Henry Groman  
**Communication:** Real-time debugging session

---

## Post-Incident Review

**Key Takeaway:** AI assistants must NEVER make judgment calls about which code version is "correct" during refactors. When in doubt, STOP and ASK.

This incident demonstrates the critical importance of explicit human approval for any code removal or version selection, especially during "safe" operations like file renames.
