# AIOHTTP Documentation

## Overview & Installation

AIOHTTP is an asynchronous HTTP client/server framework for asyncio and Python. It provides both HTTP client and server functionality built on top of Python's asyncio library, making it ideal for building high-performance web applications and HTTP clients.

### Key Features
- **High Performance**: Asynchronous I/O with asyncio for concurrent requests
- **Client and Server**: Complete HTTP client and server implementations
- **WebSocket Support**: Full WebSocket client and server support
- **Connection Pooling**: Automatic connection reuse and pooling
- **Middleware Support**: Extensible middleware system for servers
- **SSL/TLS Support**: Comprehensive SSL/TLS configuration options
- **Streaming**: Support for streaming uploads and downloads
- **Modern Python**: Built for Python 3.7+ with async/await syntax

### Installation

**Standard Installation:**
```bash
pip install aiohttp
```

**With optional dependencies:**
```bash
pip install aiohttp[speedups]  # For performance improvements
```

**Version Check:**
```python
import aiohttp
print(aiohttp.__version__)
```

## Core Concepts & Architecture

### ClientSession - The Heart of HTTP Client
The `ClientSession` is the main interface for making HTTP requests. It manages connection pooling, cookies, headers, and other session-level configurations.

```python
import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://python.org') as response:
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])
            html = await response.text()
            print("Body:", html[:15], "...")

asyncio.run(main())
```

### Connection Management
AIOHTTP uses connection pooling automatically:
- **TCP Connector**: Manages TCP connections with pooling
- **Connection Limits**: Control total and per-host connections
- **Keep-Alive**: Automatic connection reuse
- **Timeouts**: Configurable timeouts for different phases

### Request/Response Lifecycle
1. **Session Creation**: Initialize ClientSession with configuration
2. **Connection Acquisition**: Get connection from pool or create new
3. **Request Sending**: Send HTTP request through connection
4. **Response Processing**: Receive and process response
5. **Connection Return**: Return connection to pool for reuse

## Common Usage Patterns

### 1. Basic HTTP Client Operations

**Simple GET Request:**
```python
import aiohttp
import asyncio

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise Exception(f"HTTP {response.status}: {await response.text()}")

# Usage
asyncio.run(fetch_url('http://httpbin.org/get'))
```

**POST Request with JSON:**
```python
async def post_json_data(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

# Usage
data = {'key': 'value', 'test': True}
result = await post_json_data('http://httpbin.org/post', data)
```

**Multiple HTTP Methods:**
```python
async def http_methods_example():
    async with aiohttp.ClientSession() as session:
        # GET
        async with session.get('http://httpbin.org/get') as resp:
            get_data = await resp.json()
        
        # POST
        async with session.post('http://httpbin.org/post', json={'data': 'test'}) as resp:
            post_data = await resp.json()
        
        # PUT
        async with session.put('http://httpbin.org/put', json={'update': True}) as resp:
            put_data = await resp.json()
        
        # DELETE
        async with session.delete('http://httpbin.org/delete') as resp:
            delete_data = await resp.json()
        
        return get_data, post_data, put_data, delete_data
```

### 2. Session Configuration

**Custom Headers and Authentication:**
```python
async def configured_session_example():
    headers = {
        "Authorization": "Bearer your-token-here",
        "User-Agent": "MyApp/1.0",
        "Accept": "application/json"
    }
    
    timeout = aiohttp.ClientTimeout(total=60, connect=10)
    
    async with aiohttp.ClientSession(
        headers=headers,
        timeout=timeout
    ) as session:
        async with session.get('http://api.example.com/data') as response:
            return await response.json()
```

**Base URL Configuration:**
```python
async def base_url_example():
    base_url = 'https://api.github.com'
    
    async with aiohttp.ClientSession(base_url=base_url) as session:
        # Relative URLs will be joined with base_url
        async with session.get('/user') as resp:
            user_data = await resp.json()
        
        async with session.get('/user/repos') as resp:
            repos_data = await resp.json()
        
        return user_data, repos_data
```

### 3. Connection Pooling and Limits

**Custom Connection Limits:**
```python
import aiohttp

async def connection_pooling_example():
    # Custom connector with connection limits
    connector = aiohttp.TCPConnector(
        limit=100,           # Total connection pool size
        limit_per_host=30,   # Max connections per host
        keepalive_timeout=60,  # Keep connections alive for 60 seconds
        enable_cleanup_closed=True
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # All requests through this session will use the custom connector
        tasks = []
        for i in range(50):
            task = session.get(f'http://httpbin.org/delay/{i%3}')
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [resp.status for resp in responses]
```

**Disable Connection Limits:**
```python
# For high-throughput applications
connector = aiohttp.TCPConnector(limit=0)  # No limit
async with aiohttp.ClientSession(connector=connector) as session:
    # Handle thousands of concurrent connections
    pass
```

### 4. Timeout Configuration

**Comprehensive Timeout Settings:**
```python
async def timeout_configuration():
    # Define different timeout phases
    timeout = aiohttp.ClientTimeout(
        total=120,        # Total time for entire request
        connect=10,       # Time to establish connection
        sock_connect=5,   # Socket connection time
        sock_read=30      # Time to read data from socket
    )
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get('http://slow-server.com') as response:
                return await response.text()
        except asyncio.TimeoutError:
            print("Request timed out")
            return None
        except aiohttp.ClientTimeout:
            print("Client timeout occurred")
            return None
```

**Per-Request Timeout Override:**
```python
async def per_request_timeout():
    async with aiohttp.ClientSession() as session:
        # Override session timeout for specific request
        custom_timeout = aiohttp.ClientTimeout(total=5)
        
        async with session.get(
            'http://example.com',
            timeout=custom_timeout
        ) as response:
            return await response.text()
```

### 5. Error Handling and Retries

**Comprehensive Error Handling:**
```python
import aiohttp
import asyncio
from typing import Optional

async def robust_fetch(url: str, retries: int = 3) -> Optional[str]:
    """Fetch URL with retries and comprehensive error handling."""
    
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    # Raise exception for bad status codes
                    response.raise_for_status()
                    return await response.text()
                    
        except aiohttp.ClientError as e:
            print(f"Client error on attempt {attempt + 1}: {e}")
        except aiohttp.ServerTimeoutError:
            print(f"Server timeout on attempt {attempt + 1}")
        except aiohttp.ClientResponseError as e:
            print(f"Response error {e.status}: {e.message}")
            if e.status < 500:  # Don't retry client errors
                break
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
        
        if attempt < retries - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

**Custom Retry Logic:**
```python
class RetryableHTTPClient:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def fetch_with_retry(self, session: aiohttp.ClientSession, 
                              url: str, **kwargs) -> aiohttp.ClientResponse:
        """Fetch with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = await session.get(url, **kwargs)
                if response.status < 500:  # Don't retry client errors
                    return response
                
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
            
            if attempt < self.max_retries - 1:
                wait_time = self.backoff_factor * (2 ** attempt)
                await asyncio.sleep(wait_time)
        
        raise last_exception or Exception("Max retries exceeded")
```

## Best Practices & Security

### 1. Session Management

**Always Use Context Managers:**
```python
# ✅ CORRECT: Automatic cleanup
async def correct_session_usage():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://example.com') as response:
            return await response.text()

# ❌ INCORRECT: Manual cleanup required
async def incorrect_session_usage():
    session = aiohttp.ClientSession()
    response = await session.get('http://example.com')
    text = await response.text()
    await session.close()  # Easy to forget!
    return text
```

**Reuse Sessions:**
```python
class HTTPService:
    def __init__(self):
        self._session = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
                connector=aiohttp.TCPConnector(limit=100)
            )
        return self._session
    
    async def fetch(self, url: str) -> str:
        session = await self.get_session()
        async with session.get(url) as response:
            return await response.text()
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
```

### 2. Security Best Practices

**SSL/TLS Configuration:**
```python
import ssl
import aiohttp

async def secure_client_example():
    # Create custom SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # All requests will use the custom SSL context
        async with session.get('https://secure-api.com') as response:
            return await response.json()

# Certificate pinning
async def certificate_pinning():
    # Pin specific certificate fingerprint
    fingerprint = aiohttp.Fingerprint(b'your-cert-fingerprint-here')
    connector = aiohttp.TCPConnector(ssl=fingerprint)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get('https://pinned-site.com') as response:
            return await response.text()
```

**Authentication Handling:**
```python
async def authentication_examples():
    # Basic Authentication
    auth = aiohttp.BasicAuth('username', 'password')
    
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get('http://protected-api.com') as response:
            return await response.json()

# Bearer Token
async def bearer_token_auth():
    headers = {'Authorization': 'Bearer your-jwt-token-here'}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get('http://api.example.com') as response:
            return await response.json()
```

### 3. Performance Optimization

**Connection Pooling Optimization:**
```python
async def optimized_connection_pool():
    connector = aiohttp.TCPConnector(
        limit=200,                    # Total connections
        limit_per_host=50,            # Per-host limit
        keepalive_timeout=60,         # Keep connections alive
        force_close=False,            # Reuse connections
        enable_cleanup_closed=True    # Clean up closed connections
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Batch requests efficiently
        urls = [f'http://api.example.com/item/{i}' for i in range(100)]
        
        async def fetch_one(url):
            async with session.get(url) as response:
                return await response.json()
        
        # Process all requests concurrently
        results = await asyncio.gather(*[fetch_one(url) for url in urls])
        return results
```

**Streaming for Large Responses:**
```python
async def stream_large_response(url: str, chunk_size: int = 8192):
    """Stream large response instead of loading into memory."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            
            content = []
            async for chunk in response.content.iter_chunked(chunk_size):
                # Process chunk by chunk
                content.append(chunk)
                
                # You could also write directly to file:
                # await file.write(chunk)
            
            return b''.join(content)
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException
import aiohttp
from contextlib import asynccontextmanager

# Global session management
http_session = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_session
    # Startup
    http_session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=60),
        connector=aiohttp.TCPConnector(limit=100)
    )
    yield
    # Shutdown
    await http_session.close()

app = FastAPI(lifespan=lifespan)

@app.get("/proxy/{path:path}")
async def proxy_request(path: str):
    try:
        async with http_session.get(f"http://external-api.com/{path}") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise HTTPException(status_code=response.status, 
                                  detail=await response.text())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Async Context Manager Pattern
```python
class HTTPClientManager:
    def __init__(self, base_url: str = None, **session_kwargs):
        self.base_url = base_url
        self.session_kwargs = session_kwargs
        self._session = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            base_url=self.base_url,
            **self.session_kwargs
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def get(self, url: str, **kwargs):
        async with self._session.get(url, **kwargs) as response:
            return await response.json()
    
    async def post(self, url: str, **kwargs):
        async with self._session.post(url, **kwargs) as response:
            return await response.json()

# Usage
async def example_usage():
    async with HTTPClientManager(base_url="https://api.example.com") as client:
        user_data = await client.get("/user/123")
        update_result = await client.post("/user/123", json={"status": "active"})
        return user_data, update_result
```

### Concurrent Request Processing
```python
import asyncio
from typing import List, Dict, Any

class ConcurrentHTTPProcessor:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_with_semaphore(self, session: aiohttp.ClientSession, 
                                 url: str) -> Dict[str, Any]:
        async with self.semaphore:
            try:
                async with session.get(url) as response:
                    return {
                        'url': url,
                        'status': response.status,
                        'data': await response.json() if response.status == 200 else None,
                        'error': None
                    }
            except Exception as e:
                return {
                    'url': url,
                    'status': None,
                    'data': None,
                    'error': str(e)
                }
    
    async def process_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_with_semaphore(session, url) 
                for url in urls
            ]
            return await asyncio.gather(*tasks)

# Usage
processor = ConcurrentHTTPProcessor(max_concurrent=20)
urls = [f"https://api.example.com/item/{i}" for i in range(100)]
results = await processor.process_urls(urls)
```

## Troubleshooting & FAQs

### Common Issues

1. **Resource Warnings (Unclosed Connections)**
   ```python
   # ❌ PROBLEM: Not using context managers
   session = aiohttp.ClientSession()
   response = await session.get('http://example.com')
   # Forgot to close session!
   
   # ✅ SOLUTION: Always use context managers
   async with aiohttp.ClientSession() as session:
       async with session.get('http://example.com') as response:
           content = await response.text()
   
   # For non-SSL connections, add a small delay
   await asyncio.sleep(0)
   
   # For SSL connections, add a longer delay
   await asyncio.sleep(0.250)
   ```

2. **Connection Pool Exhaustion**
   ```python
   # ❌ PROBLEM: Too many concurrent connections
   # ✅ SOLUTION: Use semaphore to limit concurrency
   semaphore = asyncio.Semaphore(20)  # Max 20 concurrent requests
   
   async def limited_fetch(session, url):
       async with semaphore:
           async with session.get(url) as response:
               return await response.text()
   ```

3. **Timeout Errors**
   ```python
   # Handle different timeout types
   try:
       async with session.get(url) as response:
           return await response.text()
   except aiohttp.ServerTimeoutError:
       print("Server took too long to respond")
   except aiohttp.ClientTimeout:
       print("Client timeout occurred")
   except asyncio.TimeoutError:
       print("General timeout error")
   ```

### Performance Tips

1. **Reuse Sessions**: Create one session per application, not per request
2. **Configure Connection Limits**: Set appropriate limits based on target servers
3. **Use Streaming**: For large responses, use streaming to avoid memory issues
4. **Implement Retries**: Add retry logic for transient failures
5. **Monitor Connections**: Use connection pool metrics to optimize settings

### Memory Management
```python
# Monitor connection pool usage
async def monitor_connections():
    connector = aiohttp.TCPConnector(limit=100)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Make requests...
        
        # Check connection stats
        print(f"Total connections: {len(connector._conns)}")
        print(f"Available connections: {connector._limit}")
        print(f"Acquired connections: {len(connector._acquired)}")
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Primary Use**: HTTP client for external API calls and web scraping
- **Integration**: Used in ScraperAPI client wrapper (`src/utils/scraper_api.py`)
- **Connection Management**: Custom async client with connection pooling
- **Error Handling**: Comprehensive retry logic with exponential backoff

### ScraperSky Implementation Example
```python
# From src/utils/scraper_api.py
class ScraperAPIClient:
    """Async ScraperAPI client using aiohttp with SDK fallback."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getenv("SCRAPER_API_KEY")
        self.base_url = "http://api.scraperapi.com"
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=70)  # ScraperAPI timeout
            )
    
    async def _fetch_with_aiohttp(self, url: str, render_js: bool = False, 
                                retries: int = 3) -> str:
        """Fetch using aiohttp with retry logic."""
        params = {
            "api_key": self.api_key,
            "url": url,
            "render": "true" if render_js else "false",
            "country_code": "us",
            "device_type": "desktop",
            "premium": "true",
        }
        
        api_url = f"{self.base_url}?{urlencode(params)}"
        
        await self._ensure_session()
        
        for attempt in range(retries):
            try:
                async with self._session.get(api_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        if content:
                            return content
                    elif response.status == 429:  # Rate limit
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue
                    else:
                        error_text = await response.text()
                        raise ValueError(f"HTTP {response.status}: {error_text}")
                        
            except Exception as e:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(1)
```

### Best Practices for ScraperSky
1. **Session Reuse**: Single session instance for ScraperAPI calls
2. **Timeout Configuration**: 70-second timeout for ScraperAPI compatibility
3. **Error Handling**: Specific handling for 429 (rate limit) responses  
4. **Retry Logic**: Exponential backoff for failed requests
5. **Resource Cleanup**: Proper session cleanup with context managers

This documentation provides comprehensive guidance for working with AIOHTTP in the ScraperSky project context, emphasizing async patterns, performance optimization, and robust error handling.