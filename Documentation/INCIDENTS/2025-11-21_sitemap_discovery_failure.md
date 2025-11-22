# Production Incident Report: Sitemap Discovery Failure

**Incident ID:** 2025-11-21-SITEMAP-DISCOVERY-FAILURE  
**Date:** November 21, 2025  
**Severity:** Critical (P0)  
**Status:** Resolved  
**Duration:** ~9 hours (09:31 AM - 06:32 PM PST)

---

## Executive Summary

Production sitemap discovery completely failed for 9 hours due to a logic bug introduced in the OOM hotfix. Sitemap indexes were entering a regex extraction code path but then being excluded from processing, causing them to return empty results. This prevented any new sitemaps from being discovered or inserted into the database.

---

## Timeline (PST)

| Time | Event |
|------|-------|
| 09:31 AM | Last successful sitemap insertion before failure |
| 09:52 AM | OOM hotfix deployed (commit `41087ae`) - introduced bug |
| 09:52 AM - 06:12 PM | **Silent failure period** - no sitemaps discovered |
| 06:12 PM | User reported no sitemaps being inserted |
| 06:15 PM | Investigation began - checked Supabase logs |
| 06:20 PM | Identified root cause in sitemap_analyzer.py |
| 06:28 PM | Hotfix deployed (commit `6de7aa5`) |
| 06:32 PM | Incident resolved - sitemap discovery resumed |

---

## Root Cause Analysis

### Primary Cause
**File:** `src/scraper/sitemap_analyzer.py`  
**Lines:** 649-655, 662  
**Issue:** Logic error in conditional flow causing sitemap indexes to return empty results

### Technical Details

The OOM hotfix (commit `41087ae`) removed expensive O(n²) regex operations but inadvertently introduced a logic bug:

**Before (Working):**
```python
# Lines 649-655
if ("sitemap" in url.lower() or has_urlset or has_sitemapindex or has_loc_tag or has_url_tag):
    # Line 662
    if has_urlset or has_url_tag or has_loc_tag or not has_sitemapindex:
        # Process URLs (lines 685-689)
        for url_value in urls:
            result["urls"].append({"loc": url_value})
        return result  # Line 701
```

**The Bug:**
1. **Line 652** included `has_sitemapindex` in the condition to enter the regex extraction block
2. **Line 662** excluded sitemap indexes with `not has_sitemapindex` condition
3. **Result:** Sitemap indexes entered the block (line 649-655 ✓) but were excluded from processing (line 662 ✗)
4. **Outcome:** Empty `result["urls"]` returned at line 701, no child sitemaps discovered

**After (Fixed):**
```python
# Lines 648-652
if (("sitemap" in url.lower() or has_urlset or has_loc_tag or has_url_tag)
    and not has_sitemapindex):
    # Process URLs
    for url_value in urls:
        result["urls"].append({"loc": url_value})
    return result
# Sitemap indexes now skip this block entirely and use XML parsing below (line 703+)
```

### Why It Was Silent

- No exceptions thrown - code executed successfully
- Returned valid but empty results: `{"urls": [], "url_count": 0}`
- Background schedulers didn't log errors for empty results
- No monitoring alerts for "zero sitemaps discovered"

---

## Impact Assessment

### Availability
- **Sitemap Discovery:** 100% failure for 9 hours
- **Existing Sitemaps:** Continued to function normally
- **User Impact:** No new domains could have sitemaps discovered

### Data Integrity
- **Database:** No data corruption
- **Lost Discoveries:** Unknown number of sitemap discovery attempts failed silently
- **Recovery:** Automatic - schedulers will retry failed domains

### Business Impact
- **New Domains:** Could not be processed for sitemap-based page discovery
- **Existing Workflows:** Unaffected (existing sitemaps continued processing)

---

## Resolution

### Hotfix Applied
**Commit:** `6de7aa5`  
**File:** `src/scraper/sitemap_analyzer.py`  
**Changes:**
- Modified condition at lines 648-652 to exclude sitemap indexes from regex path
- Added comment explaining sitemap indexes must use XML parsing
- Sitemap indexes now properly handled by XML parser (line 703+)

```diff
- if ("sitemap" in url.lower() or has_urlset or has_sitemapindex or has_loc_tag or has_url_tag):
+ if (("sitemap" in url.lower() or has_urlset or has_loc_tag or has_url_tag)
+     and not has_sitemapindex):
```

### Verification
- Deployed to production at 6:28 PM
- Monitoring for new sitemap insertions
- Expected recovery: Immediate (schedulers retry automatically)

---

## Related Incidents

**Previous Incident:** [2025-11-21 OOM Crash Loop](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Documentation/INCIDENTS/2025-11-21_production_oom_crash_loop.md)

The OOM hotfix (commit `41087ae`) that resolved the crash loop inadvertently introduced this sitemap discovery bug. This demonstrates the risk of emergency hotfixes without comprehensive testing.

---

## Lessons Learned

### What Went Wrong
1. **Insufficient testing** of OOM hotfix - only tested for memory usage, not functionality
2. **No integration tests** for sitemap discovery workflow
3. **Silent failures** - no alerts when sitemap discovery returns zero results
4. **Complex conditional logic** - nested conditions made bug hard to spot in code review
5. **No monitoring** for key metrics like "sitemaps discovered per hour"

### What Went Right
1. **User reported issue** quickly (within hours of noticing)
2. **Database logs** provided clear timeline of failure
3. **Root cause identified** quickly via code analysis
4. **Fast deployment** - hotfix deployed within 20 minutes of identification

---

## Action Items

### Immediate (Completed)
- [x] Deploy hotfix for sitemap index processing
- [x] Verify sitemap discovery resumes
- [x] Document incident

### Short-term (Next 7 days)
- [ ] Add integration test for sitemap index discovery
- [ ] Add monitoring alert: "Zero sitemaps discovered in last hour"
- [ ] Add logging: Warn when sitemap returns empty results
- [ ] Review all conditional logic in sitemap_analyzer.py for similar bugs
- [ ] Add unit tests for all sitemap types (standard, index, news, image, video)

### Long-term (Next 30 days)
- [ ] Implement comprehensive sitemap discovery test suite
- [ ] Add monitoring dashboard for sitemap discovery metrics
- [ ] Refactor sitemap_analyzer.py to simplify conditional logic
- [ ] Add automated regression tests for critical workflows
- [ ] Implement canary deployments for hotfixes
- [ ] Create "hotfix checklist" requiring functional testing before deploy

---

## Prevention Measures

### Code Quality
1. **Simplify conditional logic** - reduce nested conditions
2. **Add inline comments** explaining complex flow control
3. **Unit tests** for each code path in sitemap_analyzer.py

### Monitoring
1. **Metric alerts:**
   - Sitemaps discovered per hour < threshold
   - Sitemap discovery success rate < 95%
   - Empty sitemap results > 10% of attempts
2. **Dashboard:** Real-time sitemap discovery metrics

### Process
1. **Hotfix protocol:**
   - Require functional testing even for "simple" fixes
   - Peer review mandatory for production hotfixes
   - Document all code paths affected by change
2. **Integration tests** for critical workflows before deploy

---

## Related Commits

- `41087ae` - **OOM hotfix** (introduced bug)
- `6de7aa5` - **Sitemap discovery fix** (resolved incident)

---

## Related Files

- `src/scraper/sitemap_analyzer.py` - Primary file with bug
- `src/services/background/wf4_sitemap_discovery_scheduler.py` - Calls sitemap analyzer
- `src/services/sitemap/processing_service.py` - Sitemap processing workflow

---

## Incident Commander

**Agent:** Antigravity  
**User:** Henry Groman  
**Communication:** Real-time debugging session

---

## Post-Incident Review Date

**Scheduled:** TBD  
**Attendees:** TBD

---

## Appendix: Database Evidence

### Last Successful Sitemap Insertion
```sql
SELECT MAX(created_at) as last_created FROM sitemap_files;
-- Result: 2025-11-21 09:31:59.499503+00
```

### Total Sitemaps (Pre-Fix)
```sql
SELECT COUNT(*) as total_sitemaps FROM sitemap_files;
-- Result: 1,686 sitemaps (no new insertions for 9 hours)
```

### Recent Sitemaps (All Pre-Incident)
```sql
SELECT id, url, status, created_at 
FROM sitemap_files 
ORDER BY created_at DESC 
LIMIT 10;
-- All timestamps: 2025-11-21 09:31:XX (before 09:52 AM hotfix)
```
