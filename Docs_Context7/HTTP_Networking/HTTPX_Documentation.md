# HTTPX Documentation

## Overview & Installation

HTTPX is a next-generation HTTP client for Python that provides both synchronous and asynchronous APIs. It's designed as a modern alternative to the popular `requests` library, offering HTTP/2 support, async capabilities, and a familiar interface.

### Key Features
- **Full HTTP/2 Support**: Native HTTP/2 implementation for improved performance
- **Async and Sync**: Both synchronous and asynchronous client APIs
- **Standard Python Types**: Built-in type annotations and IDE support
- **Requests Compatibility**: Drop-in replacement for many requests use cases
- **Streaming Support**: Efficient handling of large requests and responses
- **Connection Pooling**: Automatic connection reuse and management
- **Flexible Authentication**: Built-in and custom authentication schemes
- **Modern Architecture**: Clean, well-tested, and actively maintained

### Installation

**Standard Installation:**
```bash
pip install httpx
```

**With HTTP/2 support:**
```bash
pip install httpx[http2]
```

**Version Check:**
```python
import httpx
print(httpx.__version__)
```

## Core Concepts & Architecture

### Client Classes
HTTPX provides two main client classes:
- **`httpx.Client`**: Synchronous HTTP client
- **`httpx.AsyncClient`**: Asynchronous HTTP client

### Request/Response Model
Similar to requests, but with enhanced features:
- Type-annotated request/response objects
- Streaming capabilities built-in
- HTTP/2 multiplexing support
- Connection pooling by default

### Transport Layer
HTTPX uses a pluggable transport system:
- **HTTPTransport**: Standard HTTP/1.1 and HTTP/2
- **AsyncHTTPTransport**: Async version of HTTPTransport
- **MockTransport**: For testing
- **Custom Transports**: Extensible for special use cases

## Common Usage Patterns

### 1. Basic HTTP Operations

**Simple GET Request:**
```python
import httpx

# Using top-level function
response = httpx.get('https://httpbin.org/get')
print(response.status_code)
print(response.json())

# Using client
with httpx.Client() as client:
    response = client.get('https://httpbin.org/get')
    print(response.text)
```

**POST Request with JSON:**
```python
import httpx

data = {"key": "value", "number": 42}

# Top-level function
response = httpx.post('https://httpbin.org/post', json=data)

# With client
with httpx.Client() as client:
    response = client.post('https://httpbin.org/post', json=data)
    print(response.json())
```

**All HTTP Methods:**
```python
import httpx

with httpx.Client() as client:
    # Standard HTTP methods
    get_resp = client.get('https://httpbin.org/get')
    post_resp = client.post('https://httpbin.org/post', json={'test': True})
    put_resp = client.put('https://httpbin.org/put', json={'update': True})
    patch_resp = client.patch('https://httpbin.org/patch', json={'modify': True})
    delete_resp = client.delete('https://httpbin.org/delete')
    head_resp = client.head('https://httpbin.org/get')
    options_resp = client.options('https://httpbin.org/get')
```

### 2. Asynchronous Operations

**Basic Async Client:**
```python
import httpx
import asyncio

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://httpbin.org/get')
        return response.json()

# Run async function
result = asyncio.run(fetch_data())
print(result)
```

**Multiple Concurrent Requests:**
```python
import httpx
import asyncio

async def fetch_url(client, url):
    response = await client.get(url)
    return response.status_code, len(response.content)

async def fetch_multiple():
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2', 
        'https://httpbin.org/delay/3'
    ]
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_url(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

results = asyncio.run(fetch_multiple())
print(results)
```

**Async with Different Event Loops:**
```python
import httpx
import asyncio
import trio  # pip install trio
import anyio  # pip install anyio

# Using asyncio (default)
async def with_asyncio():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://www.example.com/')
        return response

asyncio.run(with_asyncio())

# Using trio
async def with_trio():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://www.example.com/')
        return response

trio.run(with_trio)

# Using anyio (can run on asyncio or trio)
async def with_anyio():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://www.example.com/')
        return response

anyio.run(with_anyio, backend='trio')
```

### 3. Client Configuration

**Base URL and Default Headers:**
```python
import httpx

# Configure client with base URL and default headers
headers = {
    'User-Agent': 'MyApp/1.0',
    'Authorization': 'Bearer token-here',
    'Accept': 'application/json'
}

with httpx.Client(
    base_url='https://api.example.com',
    headers=headers,
    timeout=30.0
) as client:
    # Relative URLs will be joined with base_url
    user_data = client.get('/user/profile').json()
    posts = client.get('/user/posts').json()
```

**Advanced Client Configuration:**
```python
import httpx

# Custom client with various configurations
client_config = {
    'base_url': 'https://api.example.com',
    'headers': {'User-Agent': 'MyApp/1.0'},
    'cookies': {'session': 'abc123'},
    'timeout': httpx.Timeout(
        connect=5.0,    # Connection timeout
        read=10.0,      # Read timeout
        write=10.0,     # Write timeout
        pool=5.0        # Pool acquisition timeout
    ),
    'follow_redirects': True,
    'http2': True,      # Enable HTTP/2
    'verify': True,     # SSL verification
    'trust_env': True   # Use environment proxy settings
}

with httpx.Client(**client_config) as client:
    response = client.get('/data')
```

### 4. Authentication

**Basic Authentication:**
```python
import httpx

# Using tuple (username, password)
response = httpx.get(
    'https://httpbin.org/basic-auth/user/pass',
    auth=('user', 'pass')
)

# Using BasicAuth class
auth = httpx.BasicAuth(username='user', password='pass')
with httpx.Client(auth=auth) as client:
    response = client.get('https://httpbin.org/basic-auth/user/pass')
```

**Digest Authentication:**
```python
import httpx

# Digest auth (more secure than basic)
auth = httpx.DigestAuth(username='user', password='pass')
response = httpx.get('https://httpbin.org/digest-auth/auth/user/pass', auth=auth)
print(response.history)  # Shows 401 challenge, then 200 success
```

**Custom Authentication:**
```python
import httpx

class BearerAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token
    
    def auth_flow(self, request):
        request.headers['Authorization'] = f'Bearer {self.token}'
        yield request

# Usage
auth = BearerAuth('your-jwt-token')
with httpx.Client(auth=auth) as client:
    response = client.get('https://api.example.com/protected')
```

**Token Refresh Authentication:**
```python
import httpx

class TokenRefreshAuth(httpx.Auth):
    requires_response_body = True
    
    def __init__(self, access_token, refresh_token, refresh_url):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.refresh_url = refresh_url
    
    def auth_flow(self, request):
        request.headers['Authorization'] = f'Bearer {self.access_token}'
        response = yield request
        
        if response.status_code == 401:
            # Token expired, refresh it
            refresh_response = yield self.build_refresh_request()
            self.update_tokens(refresh_response)
            
            # Retry original request with new token
            request.headers['Authorization'] = f'Bearer {self.access_token}'
            yield request
    
    def build_refresh_request(self):
        return httpx.Request(
            'POST', 
            self.refresh_url,
            json={'refresh_token': self.refresh_token}
        )
    
    def update_tokens(self, response):
        data = response.json()
        self.access_token = data['access_token']
        self.refresh_token = data.get('refresh_token', self.refresh_token)
```

### 5. Streaming

**Streaming Downloads:**
```python
import httpx

# Stream large file download
with httpx.stream('GET', 'https://httpbin.org/stream/1000') as response:
    # Stream as bytes
    for chunk in response.iter_bytes(chunk_size=8192):
        # Process chunk (e.g., write to file)
        pass
    
    # Stream as text
    for text_chunk in response.iter_text():
        print(text_chunk, end='')
    
    # Stream line by line
    for line in response.iter_lines():
        print(line)
```

**Async Streaming:**
```python
import httpx
import asyncio

async def stream_download():
    async with httpx.AsyncClient() as client:
        async with client.stream('GET', 'https://httpbin.org/stream/100') as response:
            async for chunk in response.aiter_bytes():
                # Process chunk asynchronously
                print(f"Received {len(chunk)} bytes")

asyncio.run(stream_download())
```

**Progress Monitoring:**
```python
import httpx
from tqdm import tqdm

def download_with_progress(url, filename):
    with httpx.stream('GET', url) as response:
        total = int(response.headers.get('Content-Length', 0))
        
        with open(filename, 'wb') as f, tqdm(
            total=total, unit='B', unit_scale=True, desc=filename
        ) as progress:
            for chunk in response.iter_bytes():
                f.write(chunk)
                progress.update(len(chunk))

# Download file with progress bar
download_with_progress(
    'https://httpbin.org/bytes/1048576',  # 1MB file
    'downloaded_file.bin'
)
```

## Best Practices & Security

### 1. Client Management

**Use Context Managers:**
```python
# ✅ CORRECT: Automatic cleanup
with httpx.Client() as client:
    response = client.get('https://example.com')

# ✅ CORRECT: Async version
async with httpx.AsyncClient() as client:
    response = await client.get('https://example.com')

# ❌ INCORRECT: Manual cleanup required
client = httpx.Client()
response = client.get('https://example.com')
client.close()  # Easy to forget!
```

**Reuse Clients:**
```python
import httpx
from typing import Optional

class HTTPService:
    def __init__(self):
        self._client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
    
    def get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=30.0,
                http2=True,
                follow_redirects=True
            )
        return self._client
    
    def get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=30.0,
                http2=True,
                follow_redirects=True
            )
        return self._async_client
    
    def close(self):
        if self._client:
            self._client.close()
        if self._async_client:
            # Note: This should be called from async context
            # asyncio.create_task(self._async_client.aclose())
            pass
```

### 2. Error Handling

**Comprehensive Error Handling:**
```python
import httpx
import asyncio
from typing import Optional

async def robust_request(url: str, retries: int = 3) -> Optional[httpx.Response]:
    """Make HTTP request with comprehensive error handling."""
    
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()  # Raise for 4xx/5xx status codes
                return response
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code}: {e.response.text}")
            if e.response.status_code < 500:  # Don't retry client errors
                break
                
        except httpx.ConnectError:
            print(f"Connection error on attempt {attempt + 1}")
            
        except httpx.TimeoutError:
            print(f"Request timeout on attempt {attempt + 1}")
            
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            
        if attempt < retries - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

**Status Code Handling:**
```python
import httpx

def handle_response(response: httpx.Response):
    """Handle different response status codes."""
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 204:
        return None  # No content
    elif response.status_code == 404:
        raise ValueError("Resource not found")
    elif response.status_code == 429:
        retry_after = response.headers.get('Retry-After', '60')
        raise Exception(f"Rate limited. Retry after {retry_after} seconds")
    elif 400 <= response.status_code < 500:
        raise ValueError(f"Client error: {response.status_code} - {response.text}")
    elif response.status_code >= 500:
        raise Exception(f"Server error: {response.status_code} - {response.text}")
    else:
        response.raise_for_status()  # Let httpx handle it
```

### 3. Security Configuration

**SSL/TLS Configuration:**
```python
import httpx
import ssl

# Custom SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Client with custom SSL
client = httpx.Client(verify=ssl_context)

# Certificate pinning
from httpx import Fingerprint
fingerprint = Fingerprint(b'your-cert-fingerprint')
client = httpx.Client(verify=fingerprint)

# Client certificates
ssl_context.load_cert_chain('client.pem', 'client.key')
client = httpx.Client(verify=ssl_context)
```

**Proxy Configuration:**
```python
import httpx

# Simple proxy
client = httpx.Client(proxy="http://proxy.example.com:8080")

# Proxy with authentication
client = httpx.Client(proxy="http://user:pass@proxy.example.com:8080")

# Different proxies for HTTP/HTTPS
proxies = {
    "http://": "http://proxy1.example.com:8080",
    "https://": "http://proxy2.example.com:8080"
}
client = httpx.Client(proxies=proxies)
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException
import httpx
from contextlib import asynccontextmanager

# Global HTTP client
http_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    # Startup
    http_client = httpx.AsyncClient(
        timeout=30.0,
        http2=True
    )
    yield
    # Shutdown
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/proxy/{path:path}")
async def proxy_request(path: str):
    try:
        response = await http_client.get(f"https://external-api.com/{path}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### With Pydantic
```python
import httpx
from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    name: str
    email: str

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.Client(
            base_url=base_url,
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=30.0
        )
    
    def get_user(self, user_id: int) -> Optional[User]:
        response = self.client.get(f'/users/{user_id}')
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return User(**response.json())
    
    def list_users(self) -> List[User]:
        response = self.client.get('/users')
        response.raise_for_status()
        return [User(**user_data) for user_data in response.json()]
    
    def close(self):
        self.client.close()
```

### Testing with MockTransport
```python
import httpx
import pytest

def mock_handler(request: httpx.Request) -> httpx.Response:
    """Mock handler for testing."""
    if request.url.path == "/users/1":
        return httpx.Response(200, json={"id": 1, "name": "Test User"})
    elif request.url.path == "/users/404":
        return httpx.Response(404, json={"error": "Not found"})
    else:
        return httpx.Response(200, json={"message": "Default response"})

def test_api_client():
    # Create client with mock transport
    mock_transport = httpx.MockTransport(mock_handler)
    client = httpx.Client(transport=mock_transport, base_url="https://api.example.com")
    
    # Test successful request
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
    
    # Test 404 response
    response = client.get("/users/404")
    assert response.status_code == 404
```

## Troubleshooting & FAQs

### Common Issues

1. **Import Errors**
   ```bash
   pip install httpx[http2]  # For HTTP/2 support
   pip install httpx[brotli] # For Brotli compression
   ```

2. **SSL Verification Errors**
   ```python
   # Disable SSL verification (not recommended for production)
   client = httpx.Client(verify=False)
   
   # Or use custom CA bundle
   client = httpx.Client(verify='/path/to/ca-bundle.crt')
   ```

3. **Timeout Issues**
   ```python
   # Configure comprehensive timeouts
   timeout = httpx.Timeout(
       connect=5.0,    # Connection timeout
       read=10.0,      # Read timeout  
       write=10.0,     # Write timeout
       pool=5.0        # Pool timeout
   )
   client = httpx.Client(timeout=timeout)
   ```

### Performance Tips

1. **Use HTTP/2**: Enable with `http2=True` for better multiplexing
2. **Reuse Clients**: Don't create new clients for each request
3. **Configure Timeouts**: Set appropriate timeouts for your use case
4. **Stream Large Responses**: Use streaming for large files
5. **Connection Pooling**: Clients automatically pool connections

### Migration from Requests
```python
# requests
import requests
session = requests.Session()
response = session.get('https://example.com')

# httpx equivalent
import httpx
client = httpx.Client()
response = client.get('https://example.com')

# Key differences:
# 1. httpx.Client() instead of requests.Session()
# 2. Must call client.close() or use context manager
# 3. HTTP/2 support with http2=True
# 4. Built-in async support with AsyncClient
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Version**: Available but not currently used (prefers aiohttp)
- **Potential Use Cases**: Modern HTTP client alternative to aiohttp
- **Benefits**: HTTP/2 support, better type annotations, requests compatibility

### Recommended ScraperSky Integration
```python
# Example integration for ScraperSky
import httpx
import asyncio
from typing import Optional

class HTTPXScraperClient:
    """HTTPX-based HTTP client for ScraperSky."""
    
    def __init__(self, timeout: float = 70.0):
        self._client: Optional[httpx.AsyncClient] = None
        self.timeout = timeout
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(total=self.timeout),
            http2=True,
            follow_redirects=True,
            headers={'User-Agent': 'ScraperSky/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
    
    async def fetch(self, url: str, retries: int = 3) -> str:
        """Fetch URL with retry logic."""
        for attempt in range(retries):
            try:
                response = await self._client.get(url)
                response.raise_for_status()
                return response.text
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
                
            except (httpx.ConnectError, httpx.TimeoutError):
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(1)
        
        raise Exception("Max retries exceeded")

# Usage in ScraperSky
async def scrape_with_httpx(url: str) -> str:
    async with HTTPXScraperClient() as client:
        return await client.fetch(url)
```

### Benefits for ScraperSky
1. **HTTP/2 Support**: Better performance for multiple requests
2. **Type Safety**: Better IDE support and type checking
3. **Modern API**: Clean, intuitive interface
4. **Compatibility**: Easy migration from requests-style code
5. **Testing**: Built-in mock transport for testing

This documentation provides comprehensive guidance for working with HTTPX, emphasizing both synchronous and asynchronous patterns, authentication, and integration possibilities for the ScraperSky project.