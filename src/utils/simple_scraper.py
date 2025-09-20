"""
Simple, effective, non-blocking async scraper.
Logic is translated from the working test_simple_scraper.py.
"""

import aiohttp
import asyncio
import logging

def scrape_page_simple_async(url: str) -> str:
    """Scrape a page using aiohttp with settings from the test script."""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # The connector is used to disable SSL verification, mimicking `verify=False`
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=20)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
                html_content = await response.text()
                logging.info(f"Simple async scraper successful for {url}. Content length: {len(html_content)}")
                return html_content
                
    except Exception as e:
        logging.error(f"Simple async scraper failed for {url}: {e}")
        return "" # Return empty string on failure
