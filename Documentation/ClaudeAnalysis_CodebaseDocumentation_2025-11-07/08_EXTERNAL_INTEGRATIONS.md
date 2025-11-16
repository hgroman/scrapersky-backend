# ScraperSky Backend - External Service Integrations

**Last Updated:** 2025-11-07  
**Scope:** Complete inventory of external APIs, services, and libraries  
**Thoroughness Level:** Medium - All major integrations documented

---

## Table of Contents

1. [Database Integration (Supabase)](#database-integration-supabase)
2. [Google Maps/Places API](#google-mapsplaces-api)
3. [ScraperAPI Integration](#scraperapi-integration)
4. [Additional External Services](#additional-external-services)
5. [HTTP Client Libraries & Patterns](#http-client-libraries--patterns)
6. [Web Scraping Tools](#web-scraping-tools)
7. [Vector Database Integration](#vector-database-integration)
8. [Integration Best Practices & Concerns](#integration-best-practices--concerns)

---

## Database Integration (Supabase)

### Connection Architecture

**Primary System:** Supabase PostgreSQL via Supavisor connection pooling (port 6543)

**Critical Configuration Requirements:**
```
Database Driver: asyncpg (async) + psycopg[binary] (sync)
Connection Pooling: Supavisor ONLY - non-negotiable per architecture mandate
Required URL Parameters:
  - raw_sql=true              (Use raw SQL instead of ORM)
  - no_prepare=true           (Disable prepared statements)
  - statement_cache_size=0    (Disable statement caching)
```

**File References:**
- `/src/db/engine.py` - Main database engine configuration
- `/src/db/session.py` - Async session factory and context managers
- `/src/config/settings.py` - Environment variable configuration

### Connection Variants

#### 1. Pooler Connection (IPv4 Compatible)
```
URL Format: postgresql+asyncpg://postgres.{project_ref}:{password}@{pooler_host}:6543/postgres
Configuration:
  - SUPABASE_POOLER_HOST
  - SUPABASE_POOLER_PORT (typically 6543)
  - SUPABASE_POOLER_USER (e.g., postgres.ddfldwzhdhhzhxywqnyz)
  - SUPABASE_POOLER_PASSWORD
```

**Used in:** Production deployments, optimized for IPv4 networks

#### 2. Direct Connection
```
URL Format: postgresql+asyncpg://postgres.{project_ref}:{password}@db.{project_ref}.supabase.co:5432/postgres
Configuration:
  - SUPABASE_DB_HOST
  - SUPABASE_DB_PORT (typically 5432)
  - SUPABASE_DB_USER
  - SUPABASE_DB_PASSWORD
```

**Used in:** Fallback when pooler unavailable, migrations, direct operations

### Pool Configuration

```python
Pool Settings (from src/db/session.py):
  - pool_size: 10 (production) / 5 (development)
  - max_overflow: 15 (production) / 10 (development)
  - pool_recycle: 1800 seconds (30 min production) / 3600 (60 min dev)
  - pool_timeout: 30 seconds
  - pool_pre_ping: True (validate connections before use)
```

### Session Management

**Dependency-Based Pattern:**
```python
# In routers (FastAPI endpoints)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Used with Depends(get_db_session) in route handlers"""
    
# Background Tasks
async with get_session() as session:
    """Used in schedulers and background processes"""
```

### SQL RPC Functions

**Vector Operations:** PostgreSQL RPC functions via dedicated module
- Located: `Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py`
- **Critical:** Never pass raw vector embeddings as SQL strings
- Use dedicated PostgreSQL RPC functions for vector operations

**Vector Tables:**
- `fix_patterns` - Storage for pattern data with embeddings

### Supabase-Specific Features

1. **JWT Authentication** (at API gateway only)
   - Not enforced at database layer
   - Tenant isolation explicitly removed per architecture mandate

2. **SSL Configuration**
   - SSL Context created with disabled hostname verification
   - Certificate verification disabled for Supabase self-signed certs

3. **Async Implementation**
   - All database operations use `async/await`
   - No synchronous blocking calls in async context
   - Fallback sync engine for migrations

---

## Google Maps/Places API

### Services Integrated

#### 1. Text Search API
**File:** `/src/services/places/places_search_service.py`

**HTTP Method:** `aiohttp` async client
```python
Endpoint: https://maps.googleapis.com/maps/api/place/textsearch/json
Parameters:
  - query: "{business_type} in {location}"
  - radius: search_radius_in_meters
  - key: GOOGLE_MAPS_API_KEY
```

**Features:**
- Paginated results with `next_page_token` support
- 2-second delay between pagination requests (Google requirement)
- Automatic limit to max_results (default 20)
- Response status validation

**Error Handling:**
- HTTP status validation (200 required)
- API status check (`data.get('status') != 'OK'`)
- Error message extraction from response
- Graceful pagination failure handling

#### 2. Place Details API (Deep Scan)
**File:** `/src/services/places/places_deep_service.py`

**Library:** `googlemaps` SDK
```python
Client Initialization:
  gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
  
API Call:
  details_result = gmaps.place(place_id=place_id, fields=required_fields)
```

**Requested Fields:**
```
place_id, name, formatted_address, international_phone_number,
website, rating, user_ratings_total, price_level, opening_hours,
address_component, business_status, type, geometry/location,
photo, review, utc_offset, vicinity
```

**Data Mapping:**
- `business_name` ← name
- `full_address` ← formatted_address
- `phone` ← international_phone_number
- `website_url` ← website
- `rating`, `reviews_count`, `main_category`, `extra_categories`
- `latitude`, `longitude` ← geometry.location
- `price_text` ← mapped from price_level ($ notation)
- Additional fields stored in `additional_json`

**Database Storage:**
- Uses PostgreSQL upsert (INSERT ... ON CONFLICT DO UPDATE)
- Upsert key: `place_id`
- Storage table: `local_businesses`

### Authentication & API Keys

**Configuration:**
```
Environment Variable: GOOGLE_MAPS_API_KEY
Location in Code:
  - Loaded in settings.py: settings.google_maps_api_key
  - Fallback: os.getenv("GOOGLE_MAPS_API_KEY")
  - Validation in places_search_service.py with fallback to settings
```

**Security:** API key is sanitized in error logs using `log_sanitizer`

### Rate Limiting & Quota Management

**Text Search API:**
- Pagination delay: 2 seconds between requests (prevents rate limit 429)
- Exponential backoff: `2^attempt` for retries
- Max results capped to prevent quota waste

**Place Details API:**
- No explicit rate limiting in code
- Google's quota applies per request
- Cost considerations: Reviews and photos may require additional API pricing

**Cost Implications:**
- Text Search: Standard pricing per request
- Place Details: Basic request includes core fields
- Premium fields (photos, reviews): May increase cost
- Geolocation targeting: Additional cost multiplier

### Error Handling

```python
Try/except with specific exception types:
  - googlemaps.exceptions.ApiError (for details API)
  - HTTP status codes (for text search)
  - "NOT_FOUND" status handling for missing places
  - Graceful fallback when API key missing
```

### Job Status Tracking

- Search record created with status "pending"
- Updated to "processing" during API call
- Final status: "complete" or "failed"
- Progress tracking: 0 → 0.1 → 0.8 → 1.0

---

## ScraperAPI Integration

### Architecture

**File:** `/src/utils/scraper_api.py`

**Primary Purpose:** Browser automation and JavaScript rendering for web scraping

### Client Implementation

#### ScraperAPIClient Class

**Dual-Method Approach:**
```
Method 1: aiohttp (Async HTTP)
  - Direct API calls to api.scraperapi.com
  - Connection pooling with configurable limits
  - Preferred for async context
  
Method 2: SDK Fallback (Sync)
  - scraperapi_sdk.ScraperAPIClient
  - Runs in executor for async compatibility
  - Automatic fallback if aiohttp fails
```

### Request Configuration

**Base URL:** `http://api.scraperapi.com`

**Default Parameters:**
```python
params = {
    "api_key": SCRAPER_API_KEY,
    "url": target_url,
    "render": "false" (or "true" if JS enabled),
    "premium": "false" (disabled by default for cost control),
    "country_code": "us" (optional, only if geotargeting enabled),
    "device_type": "desktop" (optional)
}
```

**Optional Features (Cost-Controlled):**
| Feature | Cost Multiplier | Default | Enable Via |
|---------|-----------------|---------|-----------|
| JavaScript Rendering | 10x | Disabled | `SCRAPER_API_ENABLE_JS_RENDERING=true` |
| Premium Mode | 5x | Disabled | `SCRAPER_API_ENABLE_PREMIUM=true` |
| Geotargeting | 2x | Disabled | `SCRAPER_API_ENABLE_GEOTARGETING=true` |

### Credit Usage Monitoring

**CreditUsageMonitor Class:**
```python
Features:
  - Per-request cost calculation
  - Cumulative tracking
  - Cost alerts at 10+ credits per request
  - Alert at 1000+ cumulative credits
  - Logging: {URL, Factors, EstimatedCost, TotalRequests, TotalCredits}
  
Enable/Disable: SCRAPER_API_COST_CONTROL_MODE=true/false
```

**Cost Calculation:**
```
Base: 1 credit
Multipliers (cumulative):
  - Premium: ×5
  - JS Rendering: ×10
  - Geotargeting: ×2
  
Example: Premium + JS Rendering = 1 × 5 × 10 = 50 credits
```

### HTTP Client Configuration

**Connection Pooling:**
```python
TCPConnector(
    limit: 50 (total connections)
    limit_per_host: 20 (per host)
    keepalive_timeout: 60 seconds
    enable_cleanup_closed: True
)

Timeout: 70 seconds total (configurable via HTTP_CONNECTION_TIMEOUT)
```

### Retry Logic

```python
Default Retries: 1 (overridable)
Between Retries: 1 second pause
Rate Limit Handling: Exponential backoff 2^attempt on 429 status
```

### Error Handling

```python
Specific Errors:
  - 200: Success
  - 429: Rate limit (exponential backoff)
  - 4xx/5xx: Error with message extraction
  
Empty Response Validation: Raises if content length = 0
SDK Fallback: Automatic on aiohttp failure
```

### Async/Sync Context Management

```python
# Async context manager
async with ScraperAPIClient() as client:
    content = await client.fetch(url, render_js=True)

# Session management
- Auto-creates session on first use
- Reuses session across requests
- Proper cleanup on __aexit__
```

### Security & Cost Management

**Critical Settings:**
```
SCRAPER_API_KEY: From environment, required
SCRAPER_API_MAX_RETRIES: Default 1 (reduce from 3)
SCRAPER_API_COST_CONTROL_MODE: Default true
WF7_ENABLE_JS_RENDERING: Default false (for workflow 7)
```

**Cost Prevention Strategies:**
1. Premium features disabled by default
2. JS rendering opt-in only
3. Per-request and cumulative credit alerts
4. Configurable retry limits
5. No automatic geotargeting

---

## Additional External Services

### Mautic CRM Integration

**Status:** Configured but not actively integrated

**Configuration:**
```
MAUTIC_BASE_URL: Base URL of Mautic instance
MAUTIC_CLIENT_ID: OAuth client ID
MAUTIC_CLIENT_SECRET: OAuth client secret
```

**Location:** `src/config/settings.py` lines 92-94

**Use Case:** CRM integration for contact management (not currently implemented)

### GCP (Google Cloud Platform)

**Status:** Configured but not actively integrated in code

**Configuration:**
```
GCP_PROJECT_ID: Project identifier
GCP_SERVICE_ACCOUNT_EMAIL: Service account email
GCP_SERVICE_ACCOUNT_PRIVATE_KEY: Private key (escaped newlines)
GCP_SERVICE_ACCOUNT_TOKEN_URI: OAuth token endpoint
```

**Potential Uses:**
- Cloud Storage (GCS) for file uploads
- BigQuery for analytics
- Cloud Tasks for distributed processing

**Note:** Code references enum `gcp_api_deep_scan_status` in models/place.py but no active integration

### OpenAI / Vector Embeddings

**Library:** `openai`

**Usage Location:** `/src/routers/vector_db_ui.py`

**API:** Text embedding generation for pattern similarity search
```python
Endpoint: OpenAI Embeddings API
Model: text-embedding-ada-002
Purpose: Generate vector embeddings for fix_patterns table
```

**Configuration:**
```
OPENAI_API_KEY: Required for embeddings
Authentication: Bearer token in Authorization header
```

**Implementation:**
- Vector similarity search via httpx
- Pattern matching for fix_patterns table
- Semantic query support

---

## HTTP Client Libraries & Patterns

### aiohttp (Async HTTP)

**Primary Use Cases:**
1. Google Maps Text Search API calls
2. ScraperAPI requests
3. Web scraping (metadata extraction, sitemap analysis)
4. Metadata detection from websites

**Typical Configuration:**
```python
# Session creation
timeout = aiohttp.ClientTimeout(total=30)
session = aiohttp.ClientSession(timeout=timeout, headers=headers)

# Connection pooling
connector = aiohttp.TCPConnector(
    limit=50,           # Total connections
    limit_per_host=20,  # Per-host limit
    keepalive_timeout=60
)

# Standard User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
}
```

**Files Using aiohttp:**
- `/src/services/places/places_search_service.py`
- `/src/utils/scraper_api.py`
- `/src/scraper/metadata_extractor.py`
- `/src/scraper/sitemap_analyzer.py`
- `/src/utils/simple_scraper.py`

### requests (Synchronous HTTP)

**Use Cases:**
- Email scraper (legacy, blocking)
- Simple page content fetching

**Location:** `/src/tasks/email_scraper.py`

**Pattern:**
```python
response = requests.get(url, headers=HEADERS)
response.raise_for_status()
html = response.text
```

### httpx (Async HTTP)

**Use Cases:**
- Vector database pattern search
- Alternative to aiohttp in specific contexts

**Location:** `/src/routers/vector_db_ui.py`

**Pattern:**
```python
async with httpx.AsyncClient() as client:
    response = await client.post(url, headers=headers, json=json_body)
```

### Connection Pooling Best Practices

**Implemented Across All Clients:**
- Session reuse across multiple requests
- Connection limit management
- Keepalive timeout configuration
- Proper cleanup on shutdown
- Timeout per request/connection

**Session Manager Pattern:**
```python
class SessionManager:
    """Manages aiohttp session lifecycle"""
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(...)
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
```

---

## Web Scraping Tools

### BeautifulSoup4

**Primary Purpose:** HTML parsing and element extraction

**Files Using:**
- `/src/tasks/email_scraper.py` - Email extraction from HTML
- `/src/scraper/metadata_extractor.py` - Site metadata detection
- `/src/scraper/sitemap_analyzer.py` - XML sitemap parsing

**Common Patterns:**
```python
soup = BeautifulSoup(html_content, 'html.parser')
soup.title.string          # Get page title
soup.find_all('a')         # Find all links
soup.get_text()            # Extract all text
```

### lxml

**Primary Purpose:** Efficient XML parsing

**Use Case:** XML Sitemap parsing with namespace support

**File:** `/src/scraper/sitemap_analyzer.py`

**XML Namespaces Handled:**
```python
NAMESPACES = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
    "video": "http://www.google.com/schemas/sitemap-video/1.1",
    "xhtml": "http://www.w3.org/1999/xhtml",
}
```

### Custom Scrapers

#### 1. Simple Async Scraper
**File:** `/src/utils/simple_scraper.py`

**Purpose:** Basic page content fetching with browser-like headers

**Features:**
- Async/await with aiohttp
- SSL verification disabled (for dev)
- Standard browser User-Agent
- HTTP/HTTPS redirect handling
- Error handling with empty string fallback

#### 2. Metadata Extractor
**File:** `/src/scraper/metadata_extractor.py`

**Purpose:** Comprehensive site metadata detection

**Detects:**
```
- Page title, description, language
- WordPress detection (version, theme, plugins)
- CMS identification (Elementor, Divi, WooCommerce)
- Favicon and logo URLs
- Contact information (email, phone)
- Social media links
```

**Processing:**
- ScraperAPI integration (commented out, temporarily bypassed)
- HTML parsing via BeautifulSoup
- RegEx pattern matching for metadata
- Session management for HTTP requests

#### 3. Sitemap Analyzer
**File:** `/src/scraper/sitemap_analyzer.py`

**Purpose:** Discover and parse sitemap files

**Discovery Methods:**
```
1. Common paths (robots.txt directive)
2. Fixed locations (/sitemap.xml, /wp-sitemap.xml, etc.)
3. robots.txt parsing
4. Breadth-first search of sitemap indexes
```

**Parsing:**
- XML parsing with namespace support
- Support for:
  - Standard sitemaps
  - Sitemap indexes
  - Image sitemaps
  - News sitemaps
  - Video sitemaps
- Gzip compression support
- URL validation and formatting

---

## Vector Database Integration

### Architecture

**Storage:** PostgreSQL with pgvector extension (via Supabase)

**Table:** `fix_patterns`

**Fields:**
```
- id: Unique pattern identifier
- title: Pattern name
- problem_type: Category of problem
- code_type: Type of code (Python, JS, etc.)
- severity: Issue severity level
- problem_description: Detailed description
- solution_steps: Steps to resolve
- embedding: Vector representation (pgvector)
```

### Implementation

**File:** `/src/routers/vector_db_ui.py`

**Endpoints:**
```
GET /api/v3/vector-db/patterns
  - Retrieve all patterns

POST /api/v3/vector-db/search
  - Semantic similarity search
  - Uses OpenAI text-embedding-ada-002
  - Returns patterns ranked by similarity
```

**Search Process:**
1. Receive query text
2. Call OpenAI Embeddings API
3. Execute PostgreSQL vector similarity query
4. Return ranked results

### Critical Notes

- Vector embeddings NOT created inline in SQL
- Always use dedicated RPC functions
- Never serialize vectors as strings
- Use PostgreSQL native vector operations

---

## Integration Best Practices & Concerns

### 1. Connection Management

**Best Practice:**
```python
# Use async context managers
async with aiohttp.ClientSession() as session:
    # Use session for requests
    
# Use database session dependency
async def endpoint(session: AsyncSession = Depends(get_db_session)):
    # Session auto-commits on success, rollbacks on error
```

**Concern:** Long-held database connections
- Risk: Connection pool exhaustion
- Mitigation: Keep sessions short, use background tasks for long operations

### 2. API Key Security

**Current Implementation:**
- Environment variables (good)
- Log sanitization for sensitive keys
- No hardcoded keys (verified)

**Concern:** Key exposure in error messages
- Mitigation: Log sanitizer in places_search_service.py sanitizes exceptions

### 3. Rate Limiting & Quota

**Google Maps:**
- No built-in rate limiting in code
- Reliant on Google's quota system
- Risk: Quota exhaustion on heavy usage
- Mitigation: Monitoring and cost alerts recommended

**ScraperAPI:**
- Credit monitoring implemented
- Exponential backoff for 429 errors
- Cost control flags default to disabled

### 4. Async/Sync Mismatch

**Concern:** Blocking operations in async code

**Current Issues:**
- ScraperAPI SDK runs sync code in executor (workaround)
- Email scraper uses requests (synchronous)

**Mitigation:** Async wrappers and executor pools prevent blocking

### 5. Error Recovery

**Pattern:** Try/except with fallbacks
```python
# ScraperAPI: Falls back from aiohttp to SDK
# Sitemap parser: Continues on individual URL failures
# Places search: Returns partial results on pagination error
```

**Concern:** Silent failures in batch operations
- Risk: Incomplete data without explicit error reporting
- Mitigation: Status fields track completion in database

### 6. Transaction Boundaries

**Best Practice:**
- Routers own transaction boundaries
- Services operate within existing transactions
- No auto-commits in services

**Implementation:**
```python
# Router manages transaction
async with session.begin():
    # Service operates within transaction
    result = await service.process(session)
    # Router commits on success, rolls back on error
```

### 7. Supavisor Compatibility

**Critical Requirements:**
- `raw_sql=true`
- `no_prepare=true`
- `statement_cache_size=0`

**Concern:** ORM operations may fail with Supavisor
- Some prepared statement features disabled
- Parameter binding limited
- Mitigation: Use SQLAlchemy text() for complex queries

### 8. Cost Control

**ScraperAPI Cost Issues (Documented):**
- Premium: 5x multiplier (default disabled ✓)
- JS Rendering: 10x multiplier (default disabled ✓)
- Geotargeting: 2x multiplier (default disabled ✓)

**Monitoring:**
- Per-request cost tracking
- Cumulative alert at 1000+ credits
- Environment variables for feature toggling

### 9. SSL/TLS Handling

**Current Implementation:**
- SSL verification disabled in development
- Custom SSL context for Supabase self-signed certs
- Production should enable proper certificate validation

**Concern:** Man-in-the-middle attacks in development
- Risk: Low in dev environment
- Mitigation: Enable in production

### 10. Database Connection Pooling

**Supavisor-Specific:**
- Connection pooling enforced at gateway level
- No additional ORM pooling needed
- Reduced connection overhead

**Configuration:**
```
pool_size: 5-10 connections
max_overflow: 10-15 additional
recycle: 1800-3600 seconds
```

---

## Summary Table

| Service | Library/SDK | Type | Status | Cost | Risk Level |
|---------|------------|------|--------|------|------------|
| Supabase PostgreSQL | asyncpg, psycopg | Database | Active | ~$25/mo | Low |
| Google Maps Text Search | aiohttp | External API | Active | Per API call | Medium |
| Google Maps Place Details | googlemaps | External API | Active | Per API call | Medium |
| ScraperAPI | aiohttp + SDK | External API | Active | Credits (variable) | High |
| Mautic CRM | — | External Service | Configured | — | Low |
| GCP | — | Cloud Platform | Configured | — | Low |
| OpenAI Embeddings | openai, httpx | External API | Active | Per 1K tokens | Medium |
| BeautifulSoup4 | Local Library | HTML Parsing | Active | — | Low |
| lxml | Local Library | XML Parsing | Active | — | Low |

---

## Recommendations

1. **Implement rate limiting** for Google Maps API calls
2. **Add circuit breakers** for external API failures
3. **Monitor Supabase connection pool** metrics
4. **Enable SSL verification** in production
5. **Add comprehensive logging** for external API calls
6. **Document API quota limits** and alert thresholds
7. **Test ScraperAPI cost control** monthly
8. **Implement caching** for expensive API calls (Google Maps, OpenAI)
