# Requests Documentation

## Overview & Installation

Requests is an elegant and simple HTTP library for Python, built for human beings. It's one of the most popular Python packages and is widely considered the de facto standard for making HTTP requests in Python.

### Key Features
- **Simple API**: Clean, intuitive interface for HTTP operations
- **Built-in JSON Support**: Automatic JSON encoding/decoding
- **Session Management**: Persistent connections and cookie handling
- **Authentication**: Built-in support for various auth methods
- **SSL/TLS Verification**: Automatic certificate verification
- **Connection Pooling**: Efficient connection reuse via urllib3
- **Wide Compatibility**: Works with Python 2.7 and 3.x
- **Extensive Documentation**: Well-documented with excellent examples

### Installation

**Standard Installation:**
```bash
pip install requests
```

**With security extras:**
```bash
pip install requests[security]
```

**Version Check:**
```python
import requests
print(requests.__version__)
```

## Core Concepts & Architecture

### Request/Response Model
Requests follows a simple request-response pattern:
- Make a request using HTTP verbs (GET, POST, etc.)
- Receive a Response object with status, headers, and content
- Parse response data as text, JSON, or binary

### Session Objects
Sessions provide:
- Connection pooling and reuse
- Persistent cookies across requests
- Default headers and authentication
- Request configuration persistence

### Built on urllib3
Requests is built on top of urllib3, providing:
- Thread-safe connection pooling
- Automatic retries and redirects
- Comprehensive SSL/TLS support
- HTTP/1.1 persistent connections

## Common Usage Patterns

### 1. Basic HTTP Operations

**Simple GET Request:**
```python
import requests

# Basic GET request
response = requests.get('https://httpbin.org/get')
print(response.status_code)  # 200
print(response.text)         # Response body as text
print(response.json())       # Parse JSON response
```

**Query Parameters:**
```python
# Using params argument
payload = {'key1': 'value1', 'key2': 'value2'}
response = requests.get('https://httpbin.org/get', params=payload)
print(response.url)  # https://httpbin.org/get?key1=value1&key2=value2

# Multiple values for same key
payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
response = requests.get('https://httpbin.org/get', params=payload)
print(response.url)  # https://httpbin.org/get?key1=value1&key2=value2&key2=value3
```

**All HTTP Methods:**
```python
import requests

# All common HTTP methods
r = requests.get('https://httpbin.org/get')
r = requests.post('https://httpbin.org/post', data={'key': 'value'})
r = requests.put('https://httpbin.org/put', data={'key': 'value'})
r = requests.delete('https://httpbin.org/delete')
r = requests.head('https://httpbin.org/get')
r = requests.options('https://httpbin.org/get')

# Custom HTTP methods
r = requests.request('MKCOL', 'https://httpbin.org/anything', data={'key': 'value'})
```

### 2. Sending Data

**Form Data (POST):**
```python
# Send form-encoded data
payload = {'key1': 'value1', 'key2': 'value2'}
response = requests.post('https://httpbin.org/post', data=payload)

# The data is automatically form-encoded
print(response.json()['form'])  # {'key1': 'value1', 'key2': 'value2'}
```

**JSON Data:**
```python
import json

# Method 1: Using json parameter (recommended)
data = {'key': 'value', 'number': 42}
response = requests.post('https://httpbin.org/post', json=data)

# Method 2: Manual JSON encoding
data = {'key': 'value', 'number': 42}
response = requests.post(
    'https://httpbin.org/post',
    data=json.dumps(data),
    headers={'Content-Type': 'application/json'}
)
```

**File Uploads:**
```python
# Upload a file
with open('file.txt', 'rb') as f:
    files = {'file': f}
    response = requests.post('https://httpbin.org/post', files=files)

# Upload with custom filename
files = {'file': ('custom_name.txt', open('file.txt', 'rb'), 'text/plain')}
response = requests.post('https://httpbin.org/post', files=files)

# Multipart data with text fields
files = {'file': ('data.txt', 'some,data,to,send\nanother,row,to,send\n')}
data = {'field1': 'value1', 'field2': 'value2'}
response = requests.post('https://httpbin.org/post', files=files, data=data)
```

### 3. Headers and Authentication

**Custom Headers:**
```python
# Add custom headers
headers = {
    'User-Agent': 'MyApp/1.0',
    'Accept': 'application/json',
    'Authorization': 'Bearer token-here'
}

response = requests.get('https://httpbin.org/headers', headers=headers)
```

**Basic Authentication:**
```python
from requests.auth import HTTPBasicAuth

# Method 1: Using tuple
response = requests.get('https://httpbin.org/basic-auth/user/pass', 
                       auth=('user', 'pass'))

# Method 2: Using HTTPBasicAuth class
auth = HTTPBasicAuth('user', 'pass')
response = requests.get('https://httpbin.org/basic-auth/user/pass', auth=auth)
```

**Digest Authentication:**
```python
from requests.auth import HTTPDigestAuth

auth = HTTPDigestAuth('user', 'pass')
response = requests.get('https://httpbin.org/digest-auth/auth/user/pass', auth=auth)
print(response.history)  # Shows 401 challenge, then 200 success
```

**Custom Authentication:**
```python
from requests.auth import AuthBase

class TokenAuth(AuthBase):
    """Custom token authentication"""
    def __init__(self, token):
        self.token = token
    
    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r

# Usage
auth = TokenAuth('your-token-here')
response = requests.get('https://api.example.com/protected', auth=auth)
```

### 4. Session Usage

**Basic Session:**
```python
import requests

# Create session for connection reuse
with requests.Session() as session:
    # Set default headers
    session.headers.update({'User-Agent': 'MyApp/1.0'})
    
    # Set default authentication
    session.auth = ('user', 'pass')
    
    # All requests through this session will use the defaults
    response1 = session.get('https://httpbin.org/get')
    response2 = session.get('https://httpbin.org/user-agent')
```

**Persistent Cookies:**
```python
# Sessions automatically handle cookies
with requests.Session() as session:
    # Set a cookie
    session.get('https://httpbin.org/cookies/set/session_cookie/123456789')
    
    # Cookie is automatically sent in subsequent requests
    response = session.get('https://httpbin.org/cookies')
    print(response.json())  # {'cookies': {'session_cookie': '123456789'}}
```

**Session Configuration:**
```python
import requests

session = requests.Session()

# Configure various session defaults
session.headers.update({'Accept': 'application/json'})
session.auth = HTTPBasicAuth('user', 'pass')
session.proxies = {'http': 'http://proxy.example.com:8080'}
session.verify = '/path/to/ca-bundle.crt'
session.cert = '/path/to/client.cert'

# Use configured session
response = session.get('https://api.example.com/data')
```

### 5. Response Handling

**Status Codes and Headers:**
```python
response = requests.get('https://httpbin.org/get')

# Status code
print(response.status_code)  # 200
print(response.status_code == requests.codes.ok)  # True

# Headers (case-insensitive access)
print(response.headers['Content-Type'])
print(response.headers.get('content-type'))

# Request headers
print(response.request.headers)
```

**Response Content:**
```python
response = requests.get('https://httpbin.org/get')

# Text content (automatically decoded)
print(response.text)

# Binary content
print(response.content)

# JSON parsing
data = response.json()

# Encoding
print(response.encoding)  # 'utf-8'
response.encoding = 'ISO-8859-1'  # Change encoding if needed
```

**Error Handling:**
```python
import requests
from requests.exceptions import RequestException, HTTPError, Timeout

try:
    response = requests.get('https://httpbin.org/status/404', timeout=5)
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx status codes
    
except HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Status Code: {e.response.status_code}")
    
except Timeout:
    print("Request timed out")
    
except RequestException as e:
    print(f"Request failed: {e}")
```

## Best Practices & Security

### 1. Session Management

**Always Use Sessions for Multiple Requests:**
```python
# ✅ GOOD: Reuse connections
with requests.Session() as session:
    for url in urls:
        response = session.get(url)
        process(response)

# ❌ BAD: Creates new connection each time
for url in urls:
    response = requests.get(url)  # New TCP connection each time
    process(response)
```

**Configure Session Defaults:**
```python
class APIClient:
    def __init__(self, base_url, api_key):
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'MyApp/1.0',
            'Accept': 'application/json'
        })
        self.base_url = base_url
    
    def get(self, endpoint):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return self.session.get(url)
    
    def post(self, endpoint, data=None, json=None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return self.session.post(url, data=data, json=json)
    
    def close(self):
        self.session.close()
```

### 2. Error Handling

**Comprehensive Error Handling:**
```python
import requests
from requests.exceptions import (
    RequestException, ConnectionError, HTTPError, 
    Timeout, TooManyRedirects
)

def safe_request(url, max_retries=3, timeout=10):
    """Make HTTP request with comprehensive error handling."""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
            
        except ConnectionError:
            print(f"Connection failed on attempt {attempt + 1}")
            
        except HTTPError as e:
            print(f"HTTP {e.response.status_code}: {e.response.reason}")
            if e.response.status_code < 500:  # Don't retry client errors
                break
                
        except Timeout:
            print(f"Request timed out on attempt {attempt + 1}")
            
        except TooManyRedirects:
            print("Too many redirects")
            break
            
        except RequestException as e:
            print(f"Request failed: {e}")
            
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

### 3. Security Best Practices

**SSL/TLS Configuration:**
```python
import requests
import ssl

# Default: SSL verification enabled
response = requests.get('https://secure-site.com')

# Custom CA bundle
response = requests.get('https://site.com', verify='/path/to/ca-bundle.crt')

# Disable SSL verification (NOT recommended for production)
response = requests.get('https://site.com', verify=False)

# Client certificates
response = requests.get(
    'https://site.com',
    cert=('/path/to/client.cert', '/path/to/client.key')
)
```

**Secure Authentication:**
```python
import os
from requests.auth import HTTPBasicAuth

# Load credentials from environment
username = os.environ.get('API_USERNAME')
password = os.environ.get('API_PASSWORD')

if not username or not password:
    raise ValueError("Authentication credentials not found")

auth = HTTPBasicAuth(username, password)

# Or use OAuth/JWT tokens
token = os.environ.get('API_TOKEN')
headers = {'Authorization': f'Bearer {token}'}
```

**Proxy Configuration:**
```python
# HTTP proxies
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080'
}

response = requests.get('http://example.com', proxies=proxies)

# Proxy with authentication
proxies = {
    'http': 'http://user:pass@proxy.example.com:8080',
    'https': 'http://user:pass@proxy.example.com:8080'
}

# Session-level proxies
session = requests.Session()
session.proxies.update(proxies)
```

### 4. Performance Optimization

**Connection Pooling and Retries:**
```python
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

# Configure retries with backoff
retry_strategy = Retry(
    total=3,                    # Total number of retries
    backoff_factor=0.1,         # Backoff factor
    status_forcelist=[429, 500, 502, 503, 504],  # HTTP statuses to retry
    allowed_methods=frozenset(['GET', 'POST']),   # Methods to retry
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)

# Use session with retry logic
response = session.get('https://unreliable-api.com/data')
```

**Streaming Large Responses:**
```python
# Stream large downloads
def download_file(url, filename):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

# Stream JSON responses
def stream_json_lines(url):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield json.loads(line)
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException
import requests
from contextlib import asynccontextmanager

# Global session
http_session = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_session
    # Startup
    http_session = requests.Session()
    http_session.headers.update({'User-Agent': 'FastAPI-Proxy/1.0'})
    yield
    # Shutdown
    http_session.close()

app = FastAPI(lifespan=lifespan)

@app.get("/proxy/{path:path}")
def proxy_request(path: str):
    try:
        response = http_session.get(f"https://external-api.com/{path}")
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, 
                          detail=e.response.text)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### API Client Class
```python
import requests
from typing import Optional, Dict, Any
import logging

class APIClient:
    """Generic API client using requests."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Configure session
        self.session.headers.update({
            'User-Agent': 'APIClient/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
        
        # Configure retries
        retry_adapter = HTTPAdapter(max_retries=Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504]
        ))
        self.session.mount('http://', retry_adapter)
        self.session.mount('https://', retry_adapter)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"API request failed: {method} {url} - {e}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        response = self._make_request('GET', endpoint, params=params)
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        response = self._make_request('POST', endpoint, json=data)
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        response = self._make_request('PUT', endpoint, json=data)
        return response.json()
    
    def delete(self, endpoint: str) -> bool:
        response = self._make_request('DELETE', endpoint)
        return response.status_code == 204
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage
with APIClient('https://api.example.com', api_key='your-key') as client:
    users = client.get('users')
    new_user = client.post('users', {'name': 'John', 'email': 'john@example.com'})
```

### Event Hooks
```python
import requests
import time

def log_request(response, *args, **kwargs):
    """Log request details."""
    print(f"Request: {response.request.method} {response.request.url}")
    print(f"Status: {response.status_code}")
    print(f"Response time: {response.elapsed.total_seconds():.2f}s")

def rate_limit_handler(response, *args, **kwargs):
    """Handle rate limiting."""
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limited. Waiting {retry_after} seconds...")
        time.sleep(retry_after)

# Add hooks to individual requests
hooks = {'response': [log_request, rate_limit_handler]}
response = requests.get('https://api.github.com/user', hooks=hooks)

# Add hooks to session
session = requests.Session()
session.hooks['response'].append(log_request)
response = session.get('https://api.github.com/user')
```

## Troubleshooting & FAQs

### Common Issues

1. **SSL Certificate Verification Errors**
   ```python
   # Check certificate validity
   try:
       response = requests.get('https://expired.badssl.com/')
   except requests.exceptions.SSLError as e:
       print(f"SSL Error: {e}")
   
   # For development only - disable verification
   response = requests.get('https://site.com', verify=False)
   ```

2. **Connection Timeouts**
   ```python
   # Set appropriate timeouts
   try:
       response = requests.get('https://slow-site.com', timeout=(5, 30))
       # timeout=(connect_timeout, read_timeout)
   except requests.exceptions.Timeout:
       print("Request timed out")
   ```

3. **Encoding Issues**
   ```python
   response = requests.get('https://site.com')
   
   # Check detected encoding
   print(f"Detected encoding: {response.encoding}")
   
   # Force specific encoding if needed
   response.encoding = 'utf-8'
   print(response.text)
   ```

### Performance Tips

1. **Use Sessions**: Always use Session objects for multiple requests
2. **Connection Pooling**: Let requests handle connection reuse automatically
3. **Set Timeouts**: Always set appropriate timeouts to avoid hanging
4. **Stream Large Files**: Use `stream=True` for large downloads
5. **Implement Retries**: Use urllib3 Retry for transient failures

### Migration from urllib2
```python
# Old urllib2 way
import urllib2
response = urllib2.urlopen('http://example.com')
content = response.read()

# New requests way
import requests
response = requests.get('http://example.com')
content = response.content  # or response.text for unicode
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Available but not extensively used (prefers aiohttp for async)
- **Use Cases**: Synchronous HTTP requests, legacy compatibility
- **Benefits**: Simple API, extensive documentation, wide compatibility

### Recommended ScraperSky Integration
```python
# Example synchronous HTTP client for ScraperSky
import requests
from typing import Optional
import os

class SyncHTTPClient:
    """Synchronous HTTP client for ScraperSky legacy support."""
    
    def __init__(self, timeout: float = 30.0):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ScraperSky/1.0'
        })
        self.session.timeout = timeout
        
        # Configure retries
        retry_adapter = HTTPAdapter(max_retries=Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504]
        ))
        self.session.mount('http://', retry_adapter)
        self.session.mount('https://', retry_adapter)
    
    def fetch(self, url: str) -> str:
        """Fetch URL content with error handling."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
            
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage in ScraperSky
def scrape_with_requests(url: str) -> str:
    with SyncHTTPClient() as client:
        return client.fetch(url)
```

### When to Use Requests vs AIOHTTP in ScraperSky
- **Use Requests for**:
  - Simple synchronous operations
  - Legacy code compatibility
  - Quick prototyping
  - External tool integration

- **Use AIOHTTP for**:
  - High-performance async operations
  - Concurrent request processing
  - Production scraping workflows
  - Integration with async frameworks

This documentation provides comprehensive guidance for working with Requests, emphasizing synchronous HTTP operations, session management, and integration possibilities for the ScraperSky project.