# ScraperAPI Documentation

## Overview & Installation

ScraperAPI is a web scraping API service that handles rotating proxies, browsers, and CAPTCHAs for you. It provides a simple REST API interface to scrape websites at scale without getting blocked.

### Key Features
- **Proxy Rotation**: Automatically rotates IP addresses and user agents
- **CAPTCHA Solving**: Handles CAPTCHAs automatically
- **JavaScript Rendering**: Full browser support with headless Chrome
- **Geotargeting**: Scrape from different countries and regions
- **High Success Rate**: 99.9% uptime with enterprise-grade infrastructure
- **Simple API**: RESTful API with straightforward parameters
- **Premium Features**: Access to residential proxies and advanced browser features

### Pricing Tiers
- **Free Plan**: 1,000 API calls/month
- **Hobby Plan**: 100K API calls/month
- **Startup Plan**: 1M API calls/month
- **Business Plan**: 3M API calls/month
- **Enterprise**: Custom pricing for high-volume usage

## Installation & Setup

### 1. Account Setup
1. Sign up at [scraperapi.com](https://scraperapi.com)
2. Get your API key from the dashboard
3. Choose your pricing plan based on usage needs

### 2. Python SDK Installation
```bash
pip install scraperapi-sdk
```

**Alternative HTTP Client Installation:**
```bash
pip install aiohttp  # For async HTTP requests
pip install requests  # For synchronous HTTP requests
```

### 3. API Key Configuration
```python
import os

# Set your API key as environment variable
os.environ['SCRAPER_API_KEY'] = 'your-api-key-here'

# Or pass directly to client
api_key = 'your-api-key-here'
```

## Core Concepts & Architecture

### REST API Structure
ScraperAPI uses a simple REST API pattern:
```
GET http://api.scraperapi.com/?api_key=YOUR_KEY&url=TARGET_URL
```

### Request Parameters
- **api_key** (required): Your ScraperAPI key
- **url** (required): Target URL to scrape
- **render** (optional): Enable JavaScript rendering (true/false)
- **country_code** (optional): Geotargeting (us, gb, de, etc.)
- **device_type** (optional): desktop, mobile, tablet
- **premium** (optional): Use premium rotating residential proxies
- **session_number** (optional): Maintain session across requests

### Response Format
- **Success**: Returns HTML content as plain text
- **Error**: Returns error message with appropriate HTTP status code

## Common Usage Patterns

### 1. Basic SDK Usage
```python
from scraperapi_sdk import ScraperAPIClient

# Initialize client
client = ScraperAPIClient('your-api-key')

# Basic scraping
response = client.get(url='https://example.com')
print(response)

# With JavaScript rendering
response = client.get(
    url='https://spa-example.com',
    render_js=True
)
```

### 2. Direct HTTP Requests
```python
import requests
from urllib.parse import urlencode

def scrape_url(url, api_key, render_js=False):
    params = {
        'api_key': api_key,
        'url': url,
        'render': 'true' if render_js else 'false'
    }
    
    api_url = f"http://api.scraperapi.com?{urlencode(params)}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"ScraperAPI error: {response.status_code} - {response.text}")

# Usage
content = scrape_url('https://example.com', 'your-api-key')
```

### 3. Async HTTP Implementation
```python
import aiohttp
import asyncio
from urllib.parse import urlencode

class AsyncScraperAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.scraperapi.com"
    
    async def fetch(self, url, render_js=False, session=None):
        params = {
            'api_key': self.api_key,
            'url': url,
            'render': 'true' if render_js else 'false',
            'country_code': 'us',
            'device_type': 'desktop'
        }
        
        api_url = f"{self.base_url}?{urlencode(params)}"
        
        if session is None:
            async with aiohttp.ClientSession() as session:
                return await self._make_request(session, api_url)
        else:
            return await self._make_request(session, api_url)
    
    async def _make_request(self, session, api_url):
        async with session.get(api_url, timeout=60) as response:
            if response.status == 200:
                return await response.text()
            else:
                error_text = await response.text()
                raise Exception(f"ScraperAPI error: {response.status} - {error_text}")

# Usage
async def main():
    scraper = AsyncScraperAPI('your-api-key')
    
    async with aiohttp.ClientSession() as session:
        content = await scraper.fetch('https://example.com', session=session)
        print(len(content))

asyncio.run(main())
```

### 4. Advanced Parameters
```python
# Geotargeting
response = client.get(
    url='https://example.com',
    country_code='gb'  # Scrape from UK
)

# Device targeting
response = client.get(
    url='https://mobile-site.com',
    device_type='mobile'
)

# Premium proxies
response = client.get(
    url='https://protected-site.com',
    premium=True
)

# Session management
response = client.get(
    url='https://site.com/login',
    session_number=123
)
```

### 5. Batch Processing
```python
import asyncio
import aiohttp

async def scrape_multiple_urls(urls, api_key):
    scraper = AsyncScraperAPI(api_key)
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            scraper.fetch(url, session=session) 
            for url in urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

# Usage
urls = ['https://site1.com', 'https://site2.com', 'https://site3.com']
results = asyncio.run(scrape_multiple_urls(urls, 'your-api-key'))
```

## Best Practices & Security

### 1. API Key Security
```python
import os
from typing import Optional

class SecureScraperAPI:
    def __init__(self, api_key: Optional[str] = None):
        # Load from environment variable
        self.api_key = api_key or os.getenv('SCRAPER_API_KEY')
        
        if not self.api_key:
            raise ValueError("SCRAPER_API_KEY environment variable is required")
    
    # Never log or expose the API key
    def __repr__(self):
        return f"ScraperAPI(key=***hidden***)"
```

### 2. Error Handling and Retries
```python
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RobustScraperAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = ScraperAPIClient(api_key)
    
    def fetch_with_retry(self, url: str, max_retries: int = 3, 
                        backoff_factor: float = 1.0) -> Optional[str]:
        """Fetch URL with exponential backoff retry logic."""
        
        for attempt in range(max_retries):
            try:
                response = self.client.get(url)
                if response:
                    return response
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed for {url}")
                    raise
                
                # Exponential backoff
                sleep_time = backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)
        
        return None
```

### 3. Rate Limiting
```python
import asyncio
from asyncio import Semaphore

class RateLimitedScraperAPI:
    def __init__(self, api_key: str, max_concurrent: int = 10):
        self.api_key = api_key
        self.semaphore = Semaphore(max_concurrent)
    
    async def fetch(self, url: str) -> str:
        async with self.semaphore:
            # Your existing fetch logic here
            await asyncio.sleep(0.1)  # Small delay between requests
            # ... ScraperAPI call ...
```

### 4. Response Validation
```python
from bs4 import BeautifulSoup
import re

def validate_response(html_content: str, expected_indicators: list) -> bool:
    """Validate that the scraped content is complete and correct."""
    
    if not html_content or len(html_content) < 100:
        return False
    
    # Check for common blocking indicators
    blocking_indicators = [
        'access denied',
        'blocked',
        'captcha',
        'robot',
        'please enable javascript'
    ]
    
    content_lower = html_content.lower()
    for indicator in blocking_indicators:
        if indicator in content_lower:
            return False
    
    # Check for expected content
    for expected in expected_indicators:
        if expected.lower() not in content_lower:
            return False
    
    return True
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import asyncio

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str
    render_js: bool = False
    country_code: str = "us"

class ScrapeResponse(BaseModel):
    url: str
    content_length: int
    success: bool
    error: str = None

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest):
    try:
        scraper = AsyncScraperAPI(os.getenv('SCRAPER_API_KEY'))
        content = await scraper.fetch(
            url=request.url,
            render_js=request.render_js
        )
        
        return ScrapeResponse(
            url=request.url,
            content_length=len(content),
            success=True
        )
        
    except Exception as e:
        return ScrapeResponse(
            url=request.url,
            content_length=0,
            success=False,
            error=str(e)
        )
```

### With Celery (Background Tasks)
```python
from celery import Celery
from scraperapi_sdk import ScraperAPIClient

app = Celery('scraper_tasks')

@app.task
def scrape_url_task(url: str, api_key: str) -> dict:
    try:
        client = ScraperAPIClient(api_key)
        content = client.get(url)
        
        return {
            'success': True,
            'url': url,
            'content_length': len(content),
            'content': content[:1000]  # First 1000 chars
        }
        
    except Exception as e:
        return {
            'success': False,
            'url': url,
            'error': str(e)
        }
```

### Data Processing Pipeline
```python
from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class ScrapedData:
    url: str
    title: Optional[str]
    content: str
    scraped_at: str
    success: bool

class ScrapingPipeline:
    def __init__(self, api_key: str):
        self.scraper = AsyncScraperAPI(api_key)
    
    async def process_urls(self, urls: List[str]) -> List[ScrapedData]:
        results = []
        
        for url in urls:
            try:
                content = await self.scraper.fetch(url)
                title = self.extract_title(content)
                
                results.append(ScrapedData(
                    url=url,
                    title=title,
                    content=content,
                    scraped_at=datetime.now().isoformat(),
                    success=True
                ))
                
            except Exception as e:
                results.append(ScrapedData(
                    url=url,
                    title=None,
                    content=str(e),
                    scraped_at=datetime.now().isoformat(),
                    success=False
                ))
        
        return results
    
    def extract_title(self, html: str) -> Optional[str]:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else None
```

## Troubleshooting & FAQs

### Common Issues

1. **API Key Errors**
   ```python
   # Check API key validity
   try:
       client = ScraperAPIClient('your-key')
       response = client.get('https://httpbin.org/ip')
       print("API key is valid")
   except Exception as e:
       print(f"API key error: {e}")
   ```

2. **Quota Exceeded**
   ```python
   # Monitor API usage
   def check_quota_status(response_headers):
       remaining = response_headers.get('X-RateLimit-Remaining')
       if remaining and int(remaining) < 100:
           print(f"Warning: Only {remaining} requests remaining")
   ```

3. **Request Timeouts**
   ```python
   # Increase timeout for slow sites
   import aiohttp
   
   timeout = aiohttp.ClientTimeout(total=120)  # 2 minutes
   async with aiohttp.ClientSession(timeout=timeout) as session:
       # Your scraping logic
   ```

4. **JavaScript Rendering Issues**
   ```python
   # Force JavaScript rendering for SPAs
   response = client.get(
       url='https://spa-site.com',
       render_js=True,
       wait=5000  # Wait 5 seconds for JS to load
   )
   ```

### Performance Optimization

1. **Connection Pooling**
   ```python
   import aiohttp
   
   # Reuse HTTP connections
   connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
   async with aiohttp.ClientSession(connector=connector) as session:
       # Multiple requests with connection reuse
   ```

2. **Concurrent Request Limiting**
   ```python
   from asyncio import Semaphore
   
   semaphore = Semaphore(10)  # Max 10 concurrent requests
   
   async def limited_fetch(url):
       async with semaphore:
           return await scraper.fetch(url)
   ```

3. **Caching Strategy**
   ```python
   import redis
   import hashlib
   import json
   
   class CachedScraperAPI:
       def __init__(self, api_key, redis_client):
           self.scraper = AsyncScraperAPI(api_key)
           self.redis = redis_client
           self.cache_ttl = 3600  # 1 hour
       
       def _cache_key(self, url):
           return f"scraper:{hashlib.md5(url.encode()).hexdigest()}"
       
       async def fetch_cached(self, url):
           cache_key = self._cache_key(url)
           
           # Try cache first
           cached = self.redis.get(cache_key)
           if cached:
               return json.loads(cached)
           
           # Fetch and cache
           content = await self.scraper.fetch(url)
           self.redis.setex(cache_key, self.cache_ttl, json.dumps(content))
           
           return content
   ```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **SDK Version**: `scraperapi-sdk==1.5.3`
- **Integration**: Custom async wrapper with fallback to SDK
- **Usage**: Web scraping for domain and sitemap analysis
- **Implementation**: `src/utils/scraper_api.py`

### ScraperSky Implementation Features
```python
# From src/utils/scraper_api.py
class ScraperAPIClient:
    """Async ScraperAPI client using aiohttp with SDK fallback."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getenv("SCRAPER_API_KEY")
        self.base_url = "http://api.scraperapi.com"
        self._session: Optional[aiohttp.ClientSession] = None
        self._sdk_client = BaseScraperAPIClient(self.api_key)
    
    async def fetch(self, url: str, render_js: bool = False, retries: int = 3) -> str:
        """Fetch with dual strategy: aiohttp primary, SDK fallback."""
        try:
            return await self._fetch_with_aiohttp(url, render_js, retries)
        except Exception:
            return await self._fetch_with_sdk(url, render_js, retries)
```

### Configuration
```python
# Environment variables required
SCRAPER_API_KEY=your-scraper-api-key

# Usage in ScraperSky services
async def scrape_domain_content(domain_url: str) -> str:
    async with ScraperAPIClient() as client:
        return await client.fetch(
            url=domain_url,
            render_js=True,  # Enable JS for modern sites
            retries=3
        )
```

### Integration with ScraperSky Workflows
1. **Domain Analysis**: Scrape domain homepages for metadata
2. **Sitemap Processing**: Fetch and analyze sitemap content
3. **Page Content Extraction**: Retrieve individual page content
4. **Business Information**: Extract structured data from business pages

This documentation provides comprehensive guidance for working with ScraperAPI in the ScraperSky project context, emphasizing async patterns and robust error handling.