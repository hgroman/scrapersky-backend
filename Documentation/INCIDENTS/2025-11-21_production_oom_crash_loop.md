# Production Incident Report: OOM Crash Loop

**Incident ID:** 2025-11-21-OOM-CRASH-LOOP  
**Date:** November 21, 2025  
**Severity:** Critical (P0)  
**Status:** Resolved  
**Duration:** ~6 hours (03:18 AM - 09:54 AM PST)

---

## Executive Summary

Production experienced a critical crash loop with instances failing every 2-5 minutes due to Out of Memory (OOM) errors (exit code 137). The root cause was O(n²) regex operations in the sitemap parser that caused memory exhaustion when processing large sitemaps. A hotfix was deployed removing the expensive operations, resolving the crash loop.

---

## Timeline (PST)

| Time | Event |
|------|-------|
| 03:12 AM | Deploy `b393249` (import path fixes) went live |
| 03:18 AM | First crash detected - health check timeout |
| 03:18-09:45 AM | Continuous crash loop - instances failing every 2-5 minutes |
| 09:13 AM | Deploy `a707b83` (Phase 4 - WF3 naming) went live |
| 09:15-09:45 AM | Crash loop continued with same pattern |
| 09:30 AM | Applied enrichment columns migration via MCP (unrelated fix) |
| 09:44 AM | Root cause identified: sitemap_analyzer.py O(n²) regex |
| 09:52 AM | Hotfix `41087ae` pushed to production |
| 09:54 AM | Incident resolved - crash loop stopped |

---

## Root Cause Analysis

### Primary Cause
**File:** `src/scraper/sitemap_analyzer.py`  
**Lines:** 684-714  
**Issue:** O(n²) regex operations causing memory exhaustion

### Technical Details

The `parse_sitemap()` function contained expensive per-URL metadata extraction:

```python
# BEFORE (causing OOM)
for url_value in urls:  # Could be 10,000 URLs
    url_data = {"loc": url_value}
    
    # For EACH URL, search the ENTIRE sitemap content (947KB)
    lastmod_pattern = f"<loc>\\s*{re.escape(url_value)}\\s*</loc>.*?<lastmod>\\s*(.*?)\\s*</lastmod>"
    lastmod_match = re.search(lastmod_pattern, content, re.DOTALL | re.IGNORECASE)
    # ... similar for priority and changefreq
```

**Complexity:** O(n²) where n = number of URLs  
**Memory Impact:** For a 947KB sitemap with 10,000 URLs, this created massive memory pressure

### Trigger Event
Processing `webcyclery.com/sitemap.xml`:
- Size: 947,383 bytes
- Estimated URLs: ~10,000
- Memory consumption: Exceeded container limits → exit 137 (OOM kill)

---

## Impact Assessment

### Availability
- **Downtime:** ~6 hours of degraded service
- **Pattern:** Crash every 2-5 minutes, brief recovery, then crash again
- **Health Checks:** Timing out after 5 seconds
- **User Impact:** Intermittent 503 errors, API unavailable during crashes

### Data Integrity
- **Database:** No data loss
- **Transactions:** Some in-flight transactions killed mid-execution
- **Evidence:** PostgreSQL logs showed "unexpected EOF on client connection with an open transaction"

---

## Resolution

### Hotfix Applied
**Commit:** `41087ae`  
**File:** `src/scraper/sitemap_analyzer.py`  
**Changes:**
- Removed expensive per-URL regex operations (lines 684-714)
- Simplified to extract URLs only, skip metadata
- Reduced complexity from O(n²) to O(n)

```python
# AFTER (fixed)
for url_value in urls:
    url_data = {"loc": url_value}
    result["urls"].append(url_data)
    if len(result["urls"]) >= max_urls:
        break

# Check metadata presence at sitemap level (not per-URL)
result["has_lastmod"] = "<lastmod>" in content
result["has_priority"] = "<priority>" in content
result["has_changefreq"] = "<changefreq>" in content
```

### Verification
- Commit pushed at 09:52 AM
- Render auto-deployed within 2-3 minutes
- Crash loop stopped
- Health checks passing consistently

---

## Secondary Issue (Resolved During Incident)

### Missing Database Columns
**Issue:** `UndefinedColumnError: column contacts.enrichment_status does not exist`  
**Cause:** Enrichment fields existed in `wf7_contact.py` model but no migration was ever created  
**Resolution:** Applied migration via MCP tool (`mcp1_apply_migration`) adding 15 enrichment columns  
**Status:** Resolved (columns now exist in production database)

---

## Lessons Learned

### What Went Wrong
1. **No performance testing** on large sitemaps before deploying sitemap analyzer
2. **Regex complexity** not identified during code review
3. **Memory limits** not monitored - no alerts for high memory usage
4. **Missing migration** for enrichment columns went undetected

### What Went Right
1. **Health checks** detected failures immediately
2. **Render auto-recovery** prevented total outage
3. **Database logs** helped identify connection issues
4. **MCP tools** enabled direct database fixes without deployment

---

## Action Items

### Immediate (Completed)
- [x] Deploy hotfix for sitemap parser OOM
- [x] Apply enrichment columns migration
- [x] Verify production stability

### Short-term (Next 7 days)
- [ ] Add memory usage monitoring and alerts
- [ ] Review all regex operations for performance issues
- [ ] Add sitemap size limits (reject >1MB sitemaps)
- [ ] Create migration for enrichment columns in repo (currently only applied via MCP)
- [ ] Add integration tests for large sitemap processing

### Long-term (Next 30 days)
- [ ] Implement streaming XML parser for sitemaps
- [ ] Add memory profiling to CI/CD pipeline
- [ ] Document migration creation process
- [ ] Create runbook for OOM incidents
- [ ] Review all O(n²) operations in codebase

---

## Related Commits

- `b393249` - Import path fixes (deployed before incident)
- `a707b83` - Phase 4 WF3 naming standardization (deployed during incident)
- `41087ae` - **HOTFIX:** Remove O(n²) regex causing OOM (resolved incident)

---

## Related Files

- `src/scraper/sitemap_analyzer.py` - Primary file with bug
- `src/models/wf7_contact.py` - Model with missing migration
- `supabase/migrations/20251121000000_add_enrichment_columns.sql` - Migration created (not yet committed)

---

## Incident Commander

**Agent:** Antigravity  
**User:** Henry Groman  
**Communication:** Real-time debugging session

---

## Post-Incident Review Date

**Scheduled:** TBD  
**Attendees:** TBD
