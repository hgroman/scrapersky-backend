# WORK ORDER: WF7 Simple Scraper Laser Strike

**Date**: 2025-09-20  
**Author**: Claude AI  
**Status**: PENDING PEER REVIEW  
**Priority**: CRITICAL  

## OBJECTIVE

Replace WF7's broken aiohttp/ScraperAPI scraping with proven working simple scraper using `requests` library.

## EVIDENCE OF NEED

**Current State**: WF7 scraping fails with `ClientResponseError` on direct HTTP and ScraperAPI is exhausted (403 errors).

**Proof of Solution**: `test_simple_scraper.py` successfully extracts target contact:
- ✅ Email: `svale@acuitylaservision.com`  
- ✅ Phone: `1661396306`
- ✅ Content: 149,088 characters

## SURGICAL STRIKE PLAN

### Target File: `src/services/WF7_V2_L4_1of2_PageCurationService.py`

### Phase 1: Comment Out Broken Code

**Lines 52-120**: Comment out entire broken scraping section
```python
# COMMENTED OUT - BROKEN AIOHTTP/SCRAPERAPI SCRAPING
# try:
#     max_retries = 3
#     base_delay = 1  # seconds
#     
#     headers = {
#         'User-Agent': 'Mozilla/5.0...',
#         # ... all existing headers
#     }
#     
#     for attempt in range(max_retries):
#         # ... entire aiohttp direct fetch loop (lines 65-95)
#     
#     # ScraperAPI fallback section (lines 96-120)
#     # ... entire ScraperAPI fallback code
```

### Phase 2: Import Simple Scraper

**Line 15** (after existing imports): Add import
```python
from ..utils.simple_scraper import scrape_page_simple
```

### Phase 3: Replace with Working Scraper

**Lines 52-120**: Replace with simple call
```python
# NEW: Use proven working simple scraper
scrape_result = scrape_page_simple(page_url)

if scrape_result['success'] and scrape_result['emails']:
    html_content = f"SCRAPED_CONTENT_WITH_CONTACTS: {scrape_result['emails']} | {scrape_result['phones']}"
    logging.info(f"Simple scraper successful for {page_url}: {len(scrape_result['emails'])} emails, {len(scrape_result['phones'])} phones")
else:
    html_content = ""
    logging.error(f"Simple scraper failed for {page_url}: {scrape_result.get('error', 'No contacts found')}")
```

### Phase 4: Create Utils Module

**New File**: `src/utils/simple_scraper.py`
- Copy exact working code from `test_simple_scraper.py`
- Remove main() function, keep only `scrape_page_simple()`

## EXACT LINE NUMBERS

### `src/services/WF7_V2_L4_1of2_PageCurationService.py`

**Line 15**: Add import
```python
from ..utils.simple_scraper import scrape_page_simple
```

**Lines 52-120**: Replace entire try/except block with:
```python
# Use proven working simple scraper
scrape_result = scrape_page_simple(page_url)

if scrape_result['success'] and scrape_result['emails']:
    html_content = f"SCRAPED_CONTENT_WITH_CONTACTS: {scrape_result['emails']} | {scrape_result['phones']}"
    logging.info(f"Simple scraper successful for {page_url}: {len(scrape_result['emails'])} emails, {len(scrape_result['phones'])} phones")
else:
    html_content = ""
    logging.error(f"Simple scraper failed for {page_url}: {scrape_result.get('error', 'No contacts found')}")
```

## RISK ASSESSMENT

**Risk Level**: LOW
- Commenting out broken code cannot make things worse
- Simple scraper is proven to work
- Easy to revert if needed

**Fallback Plan**: Uncomment original code if issues arise

## SUCCESS CRITERIA

1. ✅ WF7 processes page without `ClientResponseError`
2. ✅ Contact `svale@acuitylaservision.com` extracted successfully  
3. ✅ Contact created in database with BaseModel fix
4. ✅ Page marked as `Complete` with `ContactFound`

## FILES TO MODIFY

1. **`src/services/WF7_V2_L4_1of2_PageCurationService.py`** - Replace scraping logic
2. **`src/utils/simple_scraper.py`** - Create new utility module

## DEPENDENCIES

- `requests` library (already in requirements)
- `beautifulsoup4` library (already in requirements)  
- `urllib3` library (already available)

---

**PEER REVIEW REQUIRED**: This work order requires approval before execution.

**Estimated Time**: 15 minutes  
**Rollback Time**: 5 minutes  
**Testing Time**: 10 minutes
