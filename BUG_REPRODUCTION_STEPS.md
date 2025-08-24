# WF5 Sitemap Bug - Reproduction Steps

## Root Cause Identified

**The bug is NOT in the sitemap parsing logic**. Both parsers work correctly:
- `src/common/sitemap_parser.py` extracts 7 URLs ✅
- `src/scraper/sitemap_analyzer.py` extracts 7 URLs ✅

**The actual bug is in sitemap discovery**: WF5 is discovering and processing the wrong sitemap file.

## Evidence

### Sitemap Structure

The domain has a sitemap index at `/sitemaps.xml`:
```xml
<sitemapindex>
  <sitemap>
    <loc>https://fingerlakeselectricbikes.com/post-sitemap1.xml</loc>
  </sitemap>
  <sitemap>  
    <loc>https://fingerlakeselectricbikes.com/page-sitemap1.xml</loc>
    <lastmod>2024-04-22T12:29:45-04:00</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://fingerlakeselectricbikes.com/category-sitemap1.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://fingerlakeselectricbikes.com/post_tag-sitemap1.xml</loc>
  </sitemap>
</sitemapindex>
```

### Discovery Issue

WF5 is discovering `/page-sitemap.xml` (7 URLs) but NOT `/page-sitemap1.xml` (also 7 URLs).

**What's happening**:
1. WF5 checks common paths including `/page-sitemap.xml` 
2. This returns the correct 7 URLs when tested directly
3. But WF5 is NOT following the sitemap index to discover `/page-sitemap1.xml`
4. The sitemap index processing is working, but not linking child sitemaps to the right URLs

### Debug Output Analysis

From debug script:
```
Target sitemap found: https://fingerlakeselectricbikes.com/page-sitemap.xml
URL count: 7
```

But the issue is that `/page-sitemap.xml` and `/page-sitemap1.xml` are DIFFERENT files:
- `/page-sitemap.xml` (discovered by common path) - 7 URLs
- `/page-sitemap1.xml` (from sitemap index) - 7 URLs

The WF5 scheduler is processing one sitemap file but the database shows it only extracted 1 URL, which means there's a mismatch between:
1. Which sitemap WF5 discovers/processes 
2. Which sitemap gets stored in the database with `url_count = 1`

## Database Evidence

Current database state shows:
```sql
-- The sitemap file stored has url_count = 1
SELECT url, url_count FROM sitemap_files 
WHERE domain_id = '45e9b4aa-abc1-4c7e-bba4-1eb70f4b8c35';
-- Shows: url_count = 1
```

This suggests WF5 processed a DIFFERENT sitemap than the one with 7 URLs.

## Hypothesis: Discovery vs Storage Mismatch

**Theory**: WF5 is discovering multiple sitemaps but only storing/processing one of them incorrectly:

1. Discovery finds multiple sitemaps (robots.txt + common paths)
2. One of those sitemaps has only 1 URL (likely `/post-sitemap1.xml` which is empty)
3. That sitemap gets stored in database instead of the page sitemap with 7 URLs
4. The issue is in how WF5 selects which discovered sitemap to process and store

## Reproduction Steps

1. Run WF5 domain analysis on `fingerlakeselectricbikes.com`
2. Check which sitemap gets stored in `sitemap_files` table  
3. Verify if it's the right sitemap URL with 7 pages
4. The bug is likely in the sitemap selection/storage logic, not parsing

## Files to Investigate

1. **WF5 Scheduler Logic** - How discovered sitemaps get selected and stored
2. **Domain Sitemap Analysis** - Which sitemap gets priority for storage
3. **Database Storage** - Mismatch between discovery and storage

## Next Steps

1. Fix WF5 to ensure the correct sitemap with 7 URLs gets stored
2. Re-run WF6 with the corrected sitemap
3. Continue with WF7 testing