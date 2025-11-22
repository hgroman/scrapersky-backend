# INCIDENT: SitemapFile NOT NULL Constraint Violation (sitemap_type)
**Date:** 2025-11-22  
**Severity:** HIGH  
**Status:** RESOLVED  
**Fix Commit:** 445206f

---

## Summary

WordPress split sitemaps (e.g., `post-sitemap.xml`, `product-sitemap.xml`) were failing to insert into the `sitemap_files` table with the error:
```
null value in column "sitemap_type" of relation "sitemap_files" violates not-null constraint
```

**Root Cause:** The sitemap analyzer (`sitemap_analyzer.py`) returns `SitemapType` enum objects (e.g., `SitemapType.INDEX`, `SitemapType.STANDARD`), but the database expects lowercase string values (`"index"`, `"standard"`). The enum-to-string conversion was missing in the sitemap creation code.

---

## Timeline

**2025-11-22 02:19 PST** - Bug reported by external AI pairing partner  
**2025-11-22 02:20 PST** - Investigation started  
**2025-11-22 02:25 PST** - Root cause identified in `wf5_processing_service.py`  
**2025-11-22 02:27 PST** - Fix applied and pushed (commit 445206f)

---

## Technical Details

### The Bug

In `src/services/sitemap/wf5_processing_service.py` line 582:
```python
sitemap_type = sitemap.get("sitemap_type", "standard")
```

When the scraper returns `{"sitemap_type": SitemapType.INDEX}`, the variable `sitemap_type` becomes the enum object, not the string `"index"`. 

When passed to `SitemapFile()` constructor (line 622), SQLAlchemy couldn't properly convert the enum object to the expected string value, resulting in NULL being inserted.

### Why It Manifested Now

WordPress sites use split sitemaps with specific patterns:
- `https://example.com/post-sitemap.xml`
- `https://example.com/product-sitemap.xml`
- `https://example.com/page-sitemap.xml`
- `https://example.com/category-sitemap.xml`

These are correctly detected by the scraper as `SitemapType.INDEX` or `SitemapType.STANDARD`, but the enum wasn't being converted to a string.

### The Fix

Added defensive enum-to-string conversion in `wf5_processing_service.py` lines 583-587:

```python
sitemap_type = sitemap.get("sitemap_type", "standard")
# CRITICAL: Convert enum to string if needed (handles SitemapType.INDEX -> "index")
if hasattr(sitemap_type, 'value'):
    sitemap_type = sitemap_type.value
elif sitemap_type is None:
    sitemap_type = "standard"
```

This handles:
1. Enum objects with `.value` attribute → extract string value
2. None values → fallback to `"standard"`
3. Already-string values → pass through unchanged

---

## Impact

**Before Fix:**
- All WordPress split sitemaps failed to insert
- Domains with split sitemaps couldn't progress through WF4→WF5 pipeline
- Manual intervention required to process these domains

**After Fix:**
- Split sitemaps insert successfully
- Full WF4→WF5→WF7 pipeline operational
- No data loss (failed inserts were rolled back)

---

## Related Code

**Files Modified:**
- `src/services/sitemap/wf5_processing_service.py` (lines 583-587)

**Related Models:**
- `src/models/api_models.py` - `SitemapType` enum definition (line 106)
- `src/models/__init__.py` - `SitemapType` enum definition (line 48)
- `src/models/wf5_sitemap_file.py` - `SitemapFile.sitemap_type` column (line 99, NOT NULL)

**Scraper Code:**
- `src/scraper/sitemap_analyzer.py` - Returns `SitemapType` enum objects (lines 460, 464, 497, 506, etc.)

---

## Lessons Learned

### What Went Right
1. **External validation caught the bug** - AI pairing partner identified the symptom
2. **Defensive coding worked** - The `.get()` with default prevented crashes, just NULL inserts
3. **Fast turnaround** - 8 minutes from report to fix deployed

### What Went Wrong
1. **Type mismatch not caught** - Enum vs string type wasn't validated at creation time
2. **Missing type hints** - Could have caught this with stricter typing
3. **No integration test** - Split sitemap scenario wasn't covered in tests

### Preventive Measures
1. **Add type validation** - Consider adding explicit type checks or Pydantic models for sitemap data
2. **Integration test** - Add test case for WordPress split sitemaps
3. **Enum handling pattern** - Document standard pattern for enum-to-string conversion across codebase

---

## Related Incidents

- [2025-11-17-sitemap-jobs-not-processing.md](./2025-11-17-sitemap-jobs-not-processing.md) - Similar WF4/WF5 pipeline issue
- [2025-11-21_sitemap_discovery_failure.md](./2025-11-21_sitemap_discovery_failure.md) - Related sitemap processing failure

---

## Verification

**Test Command:**
```bash
# Check for NULL sitemap_type values
SELECT COUNT(*) FROM sitemap_files WHERE sitemap_type IS NULL;

# Should return 0 after fix
```

**Docker Test:**
```bash
docker compose -f docker-compose.dev.yml restart
docker compose -f docker-compose.dev.yml logs --tail=30 scrapersky | grep -E "ERROR|sitemap"
# Should show no sitemap_type errors
```

---

**Status:** ✅ RESOLVED  
**Fix Deployed:** 2025-11-22 02:27 PST  
**Monitoring:** Active - watching for any remaining enum conversion issues
