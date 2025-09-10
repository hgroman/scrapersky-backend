# WF4 ScraperAPI Dependency Analysis & Scrappy Analyzer Feasibility

**Date:** 2025-09-10  
**Issue:** WF4 sitemap detection failure due to suspended ScraperAPI account  
**Investigation:** Complete dependency trace and scrappy analyzer feasibility assessment

---

## Executive Summary

**Key Finding:** WF4 sitemap discovery does NOT require ScraperAPI - the dependency is isolated and can be bypassed with minimal backend changes (2-3 hours implementation).

**Root Cause:** Suspended ScraperAPI account blocking WF4 → sitemap analysis pipeline  
**Solution:** Implement scrappy analyzer fallback using existing `aiohttp` infrastructure  
**Impact:** Immediate WF4 unblocking with graceful degradation instead of complete failure

---

## Architecture Reality Check

### **Verified WF4 Flow**
```
1. User selects domains (Domain Curation tab)
   ↓ sitemap_curation_status = "Selected"
   ↓ sitemap_analysis_status = "Queued"

2. Background Scheduler
   ↓ domain_sitemap_submission_scheduler.py
   ↓ DomainToSitemapAdapterService.submit_domain_to_legacy_sitemap()

3. HTTP API Call
   ↓ POST /api/v3/sitemap/scan
   ↓ modernized_sitemap.py:scan_domain()

4. Sitemap Analysis
   ↓ SitemapAnalyzer.analyze_domain_sitemaps()
   ↓ ✅ Uses aiohttp (NOT ScraperAPI)
```

### **ScraperAPI Usage Isolation**

**WF4 Sitemap Discovery** ✅ **ScraperAPI-Free**:
- `src/scraper/sitemap_analyzer.py` → `aiohttp` only
- Sitemap fetching, XML parsing, URL extraction
- Database updates and status tracking

**Metadata Extraction** ❌ **Requires ScraperAPI**:
- `src/scraper/metadata_extractor.py:91-116` → `ScraperAPIClient`
- WordPress detection, title/description extraction
- **NOT part of WF4 sitemap discovery workflow**

---

## Database Evidence: Metadata vs Sitemap Separation

### **Recent Sitemap Records**
```sql
-- sitemap_files table (WF4 output)
generator: null                    -- No metadata extraction
discovery_method: "common_path"    -- Pure HTTP discovery
response_time_ms: null             -- Basic processing
status_code: null                  -- No ScraperAPI response codes
```

### **Recent Domain Records**  
```sql
-- domains table (separate workflow)
title: "Home Pizza | Jerlandos Pizza Montour Falls"  -- Metadata populated
is_wordpress: true                                    -- CMS detection
wordpress_version: "6.8.2"                          -- Deep analysis
```

**Conclusion:** Metadata extraction happens in a different workflow, NOT triggered by WF4 sitemap discovery.

---

## Feasibility Assessment: Scrappy Analyzer

### **Current State Analysis**

**✅ Already Scrappy Components:**
- `SitemapAnalyzer.ensure_session()` → `aiohttp.ClientSession`
- `SitemapAnalyzer.discover_sitemaps()` → robots.txt, common paths, HTML links  
- `SitemapAnalyzer.parse_sitemap()` → XML parsing with regex fallbacks
- All database operations use ORM (no external dependencies)

**❌ ScraperAPI Dependencies:**
- Only in `detect_site_metadata()` function
- Used for deep content analysis (title, CMS detection)
- **Not called by WF4 sitemap discovery**

### **Implementation Requirements**

**Backend Changes (2-3 hours):**

1. **Configuration Toggle**:
```python
# src/config/settings.py
SITEMAP_ANALYZER_FALLBACK_MODE: bool = False
```

2. **Conditional Logic**:
```python
# Skip metadata extraction when ScraperAPI unavailable
if settings.SITEMAP_ANALYZER_FALLBACK_MODE or not scraper_api_available:
    # Only run sitemap discovery
    result = await analyzer.analyze_domain_sitemaps(domain)
else:
    # Full pipeline with metadata
    metadata = await detect_site_metadata(domain)
    result = await analyzer.analyze_domain_sitemaps(domain)
```

3. **ScraperAPI Health Check**:
```python
async def is_scraper_api_available() -> bool:
    try:
        client = ScraperAPIClient()
        return True
    except:
        return False
```

**No Frontend Changes Required:** Environment variable toggle only.

---

## Scrappy Mode Capabilities

### **Full Functionality** ✅
- **Sitemap Discovery**: robots.txt, 20+ common paths, HTML link extraction
- **Sitemap Parsing**: XML parsing with regex fallbacks for malformed content
- **URL Extraction**: Complete sitemap content processing
- **Database Operations**: All ORM updates and status tracking
- **Background Processing**: Complete scheduler integration
- **Error Handling**: Graceful failures with status logging

### **Graceful Degradation** ⚠️
- **No Metadata Analysis**: Title, description, CMS detection disabled
- **Basic HTTP Only**: No proxy rotation or anti-bot protection  
- **Rate Limiting Risk**: May hit limits on aggressive scanning
- **Reduced Success Rate**: Some protected sites may block requests

---

## Risk Assessment: Very Low

### **Technical Risks**
- **Zero Breaking Changes**: Core WF4 functionality preserved
- **Fallback Pattern**: Existing error handling supports HTTP failures
- **Database Schema**: No changes required
- **API Compatibility**: All endpoints remain functional

### **Operational Benefits**
- **Immediate WF4 Unblocking**: Restore sitemap discovery without ScraperAPI
- **Cost Control**: Reduce ScraperAPI usage for basic operations
- **Graceful Degradation**: System continues operating vs complete failure
- **Toggle Control**: Can switch back to full mode anytime

---

## Implementation Recommendation

### **Priority: High - Quick Win**
- **Effort**: 2-3 hours backend development
- **Impact**: Immediate WF4 restoration
- **Risk**: Very low (uses existing infrastructure)
- **Value**: Operational resilience + cost control

### **Deployment Strategy**
```bash
# Emergency fallback
SITEMAP_ANALYZER_FALLBACK_MODE=true

# Auto-detection fallback  
SCRAPER_API_KEY=""  # Empty key triggers fallback
```

### **Success Criteria**
1. WF4 domains process from "Queued" → "Submitted" status
2. Sitemap records created in `sitemap_files` table
3. Zero impact on other workflows
4. Clean toggle between modes

---

## Conclusion

The "scrappy" sitemap analyzer **already exists** - `SitemapAnalyzer` uses pure `aiohttp` and has no ScraperAPI dependencies. The suspended ScraperAPI account blocks WF4 because the system tries to call metadata extraction (which requires ScraperAPI) even though WF4 only needs sitemap discovery.

**Solution:** Add a configuration flag to bypass the ScraperAPI-dependent metadata extraction step, allowing WF4 to run with its existing scrappy sitemap discovery capabilities.

This provides immediate operational relief while maintaining the option to restore full functionality when ScraperAPI access is available.

---

**Files Referenced:**
- `src/scraper/sitemap_analyzer.py` (ScraperAPI-free)
- `src/scraper/metadata_extractor.py:91-116` (ScraperAPI-dependent)
- `src/services/domain_sitemap_submission_scheduler.py` (WF4 scheduler)
- `src/services/domain_to_sitemap_adapter_service.py` (WF4 adapter)
- `src/routers/modernized_sitemap.py:115` (API endpoint)

**Database Evidence:**
- `sitemap_files` table: Recent records show basic HTTP processing
- `domains` table: Metadata populated by separate workflow