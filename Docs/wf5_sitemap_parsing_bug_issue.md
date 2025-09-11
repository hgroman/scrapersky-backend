# WF5 Sitemap Parsing Bug - Only Extracting 1 URL Instead of All URLs

## Issue Description

**Bug Summary**: WF5 (sitemap analysis workflow) is only extracting 1 URL from sitemaps that contain multiple URLs, causing downstream failures in the WF1-WF7 sequential pipeline.

**Impact**: Critical - breaks the entire sequential data pipeline for sitemap import and page curation workflows.

## Evidence

### Expected vs Actual Behavior

**Expected**: 
- Sitemap: `https://fingerlakeselectricbikes.com/page-sitemap1.xml` contains 7 URLs
- WF5 should extract all 7 URLs and store them in `sitemap_urls` table
- `sitemap_files` table should show `url_count = 7`

**Actual**:
- WF5 only extracted 1 URL (homepage only)
- `sitemap_files` table shows `url_count = 1` 
- Only 2 `sitemap_urls` records exist for the domain (both homepage)
- WF6 sitemap import only created 1 page instead of 7

### Database Evidence

```sql
-- sitemap_files record shows incorrect count
SELECT id, url, url_count, sitemap_type, discovery_method 
FROM sitemap_files 
WHERE domain_id = '45e9b4aa-abc1-4c7e-bba4-1eb70f4b8c35';
-- Result: url_count = 1 (should be 7)

-- Only 2 sitemap_urls exist for domain (both homepage)
SELECT COUNT(*) FROM sitemap_urls 
WHERE domain_id = '45e9b4aa-abc1-4c7e-bba4-1eb70f4b8c35';
-- Result: 2 (should be 7+)

-- Only 1 page created by WF6
SELECT COUNT(*) FROM pages 
WHERE domain_id = '45e9b4aa-abc1-4c7e-bba4-1eb70f4b8c35';
-- Result: 1 (should be 7)
```

### Sitemap Content Verification

The actual sitemap contains 7 valid URLs:

```bash
curl -s "https://fingerlakeselectricbikes.com/page-sitemap1.xml" | grep -c "<url>"
# Output: 7

curl -s "https://fingerlakeselectricbikes.com/page-sitemap1.xml" | grep "<loc>"
```

URLs in sitemap:
1. `https://fingerlakeselectricbikes.com/11-year-anniversary-promo/`
2. `https://fingerlakeselectricbikes.com/contact/`
3. `https://fingerlakeselectricbikes.com/cart/`
4. `https://fingerlakeselectricbikes.com/checkout/`
5. `https://fingerlakeselectricbikes.com/my-account/`
6. `https://fingerlakeselectricbikes.com/`
7. `https://fingerlakeselectricbikes.com/bikes/`

## Root Cause Analysis

### Files Involved

1. **Sitemap Parser**: `src/common/sitemap_parser.py`
   - Appears to be working correctly - can parse all 7 URLs from XML

2. **Sitemap Analyzer**: `src/scraper/sitemap_analyzer.py` 
   - Contains complex fallback logic for URL extraction
   - Multiple extraction methods (XML parsing, regex patterns)
   - **SUSPECTED BUG LOCATION**

3. **WF5 Scheduler**: Background job that calls sitemap analyzer
   - Uses `scheduler_loop.py` for batch processing
   - Calls sitemap analyzer to process discovered sitemaps

### Bug Hypothesis

The issue is likely in `src/scraper/sitemap_analyzer.py` in the `parse_sitemap()` method (lines 552-987). The method has multiple extraction paths:

1. **Regex-based extraction** (lines 645-720) - Primary method
2. **XML ElementTree parsing** (lines 722-979) - Fallback method

**Theory**: The regex extraction is failing to find all URLs, and the XML fallback is not being triggered properly.

### Key Code Sections to Investigate

**Regex Pattern (Line 661)**:
```python
loc_pattern = r"<loc>\s*(.*?)\s*</loc>"
urls = re.findall(loc_pattern, content, re.IGNORECASE)
```

**Alternative Pattern (Line 672)**:
```python
alt_pattern = r'https?://[^\s<>"\']+\.[^\s<>"\']+(/[^\s<>"\']*)?'
urls = re.findall(alt_pattern, content)
```

## Test Case for Reproduction

### Manual Test

```python
import asyncio
from src.scraper.sitemap_analyzer import SitemapAnalyzer

async def test_sitemap_parsing():
    analyzer = SitemapAnalyzer()
    result = await analyzer.parse_sitemap(
        "https://fingerlakeselectricbikes.com/page-sitemap1.xml", 
        max_urls=10000
    )
    print(f"URL count: {result['url_count']}")
    print(f"URLs found: {len(result['urls'])}")
    for url in result['urls']:
        print(f"  - {url.get('loc')}")
    await analyzer.close_session()

# Should return 7 URLs, currently returns 1
```

### Expected Fix Areas

1. **Regex Pattern Issues**: The regex patterns may not be capturing all `<loc>` tags properly
2. **Content Processing**: The XML content may not be preprocessed correctly before regex extraction
3. **Fallback Logic**: The XML ElementTree fallback may not be triggered when regex fails
4. **Loop Termination**: Early exit conditions may be stopping URL extraction prematurely

## Pipeline Impact

This bug breaks the entire WF1-WF7 sequential pipeline:

- **WF1** ✅ Domain discovery (works)
- **WF2** ✅ Domain staging (works) 
- **WF3** ✅ Local business data (works)
- **WF4** ✅ Domain curation (works)
- **WF5** ❌ **BROKEN** - Sitemap analysis (only extracts 1 URL instead of all)
- **WF6** ❌ **CASCADING FAILURE** - Sitemap import (only 1 page created instead of 7)
- **WF7** ❌ **CASCADING FAILURE** - Page curation (insufficient data)

## Priority: CRITICAL

This is a **production-critical bug** that:
- Breaks the core data extraction pipeline
- Causes massive data loss (86% of URLs not extracted: 1/7 = 14% success rate)
- Affects all sitemap-based domains in the system
- Prevents successful completion of end-to-end workflow testing

## Test Context

This bug was discovered during comprehensive WF1-WF7 sequential pipeline testing for ebike businesses in Ithaca, NY. The pipeline execution plan required all workflows to use actual results from previous steps, revealing this critical parsing failure.