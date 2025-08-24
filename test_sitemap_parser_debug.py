#!/usr/bin/env python3
"""
Debug script to test sitemap parsing with the actual problematic sitemap.
This helps isolate whether the bug is in sitemap_parser.py or sitemap_analyzer.py
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.common.sitemap_parser import SitemapParser
from src.scraper.sitemap_analyzer import SitemapAnalyzer
import httpx

async def test_common_sitemap_parser():
    """Test the common sitemap parser (used by WF6)"""
    print("=" * 60)
    print("TESTING: src/common/sitemap_parser.py")
    print("=" * 60)
    
    sitemap_url = "https://fingerlakeselectricbikes.com/page-sitemap1.xml"
    
    # Fetch content
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        response = await client.get(sitemap_url)
        response.raise_for_status()
        content = response.text
    
    print(f"Content length: {len(content)} chars")
    print("Content preview:")
    print(content[:500] + "..." if len(content) > 500 else content)
    print()
    
    # Parse with common parser
    parser = SitemapParser()
    urls = parser.parse(content, sitemap_url)
    
    print(f"✅ Common parser extracted {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url.loc}")
    
    return urls

async def test_scraper_sitemap_analyzer():
    """Test the scraper sitemap analyzer (used by WF5)"""
    print("\n" + "=" * 60)
    print("TESTING: src/scraper/sitemap_analyzer.py")
    print("=" * 60)
    
    sitemap_url = "https://fingerlakeselectricbikes.com/page-sitemap1.xml"
    
    analyzer = SitemapAnalyzer()
    try:
        result = await analyzer.parse_sitemap(sitemap_url, max_urls=10000)
        
        print(f"Analyzer result:")
        print(f"  - URL count: {result['url_count']}")
        print(f"  - Sitemap type: {result['sitemap_type']}")
        print(f"  - Has lastmod: {result['has_lastmod']}")
        print(f"  - Error: {result['error']}")
        print(f"  - Response time: {result['response_time_ms']}ms")
        
        if result['urls']:
            print(f"\n🔍 Analyzer extracted {len(result['urls'])} URLs:")
            for i, url_data in enumerate(result['urls'], 1):
                print(f"  {i}. {url_data.get('loc')}")
                if url_data.get('lastmod'):
                    print(f"      lastmod: {url_data.get('lastmod')}")
        else:
            print("❌ NO URLS EXTRACTED BY ANALYZER")
            
        return result
    finally:
        await analyzer.close_session()

async def test_domain_analysis():
    """Test full domain analysis (what WF5 actually does)"""
    print("\n" + "=" * 60)  
    print("TESTING: Full domain analysis (WF5 equivalent)")
    print("=" * 60)
    
    domain = "fingerlakeselectricbikes.com"
    
    analyzer = SitemapAnalyzer()
    try:
        result = await analyzer.analyze_domain_sitemaps(
            domain=domain,
            follow_robots_txt=True,
            extract_urls=True,
            max_urls_per_sitemap=10000
        )
        
        print(f"Domain analysis result for {domain}:")
        print(f"  - Total sitemaps discovered: {result['total_sitemaps']}")
        print(f"  - Total URLs extracted: {result['total_urls']}")
        print(f"  - Discovery methods: {result['discovery_methods']}")
        print(f"  - Sitemap types: {result['sitemap_types']}")
        
        if result['sitemaps']:
            print(f"\n📄 Discovered sitemaps:")
            for i, sitemap in enumerate(result['sitemaps'], 1):
                print(f"  {i}. {sitemap.get('url')}")
                print(f"      Method: {sitemap.get('discovery_method')}")
                print(f"      URL count: {sitemap.get('url_count', 0)}")
                print(f"      Type: {sitemap.get('sitemap_type')}")
                if sitemap.get('error'):
                    print(f"      ❌ Error: {sitemap.get('error')}")
        
        # Check specifically for our target sitemap
        target_sitemap = None
        for sitemap in result['sitemaps']:
            if 'page-sitemap1.xml' in sitemap.get('url', ''):
                target_sitemap = sitemap
                break
        
        if target_sitemap:
            print(f"\n🎯 Target sitemap found: {target_sitemap.get('url')}")
            print(f"   URL count: {target_sitemap.get('url_count', 0)}")
            if target_sitemap.get('urls'):
                print(f"   URLs extracted:")
                for url_data in target_sitemap.get('urls', []):
                    print(f"     - {url_data.get('loc')}")
        else:
            print(f"\n❌ Target sitemap (page-sitemap1.xml) NOT FOUND in discovery")
        
        return result
    finally:
        await analyzer.close_session()

async def main():
    """Run all tests to isolate the bug"""
    print("🔍 DEBUGGING WF5 SITEMAP PARSING BUG")
    print("Testing sitemap: https://fingerlakeselectricbikes.com/page-sitemap1.xml")
    print("Expected: 7 URLs should be extracted")
    print()
    
    # Test 1: Common sitemap parser (WF6 uses this)
    common_urls = await test_common_sitemap_parser()
    
    # Test 2: Scraper sitemap analyzer (WF5 uses this)  
    analyzer_result = await test_scraper_sitemap_analyzer()
    
    # Test 3: Full domain analysis (what WF5 scheduler actually runs)
    domain_result = await test_domain_analysis()
    
    # Summary
    print("\n" + "=" * 60)
    print("🔍 BUG ANALYSIS SUMMARY")
    print("=" * 60)
    
    common_count = len(common_urls)
    analyzer_count = analyzer_result.get('url_count', 0) if analyzer_result else 0
    domain_total = domain_result.get('total_urls', 0) if domain_result else 0
    
    print(f"Common sitemap parser:    {common_count} URLs ({'✅' if common_count == 7 else '❌'})")
    print(f"Scraper sitemap analyzer: {analyzer_count} URLs ({'✅' if analyzer_count == 7 else '❌'})")
    print(f"Domain analysis total:    {domain_total} URLs ({'✅' if domain_total >= 7 else '❌'})")
    
    if common_count == 7 and analyzer_count != 7:
        print("\n🎯 BUG LOCATED: Issue is in src/scraper/sitemap_analyzer.py")
        print("   The common parser works fine, but the scraper analyzer is broken")
    elif common_count != 7:
        print("\n🎯 BUG LOCATED: Issue is in src/common/sitemap_parser.py")
        print("   The common parser itself is broken")
    else:
        print("\n✅ Both parsers work - bug may be in WF5 scheduler integration")

if __name__ == "__main__":
    asyncio.run(main())