# External Integrations Quick Reference

## Environment Variables Checklist

### Database (Supabase)
```
SUPABASE_URL                          # Supabase project URL
SUPABASE_ANON_KEY                     # Public anonymous key
SUPABASE_SERVICE_ROLE_KEY             # Private service role key
SUPABASE_DB_PASSWORD                  # Database password
SUPABASE_JWT_SECRET                   # JWT signing secret

# Pooler (production)
SUPABASE_POOLER_HOST                  # e.g., aws-0-us-west-1.pooler.supabase.com
SUPABASE_POOLER_PORT                  # e.g., 6543
SUPABASE_POOLER_USER                  # e.g., postgres.project_ref
SUPABASE_POOLER_PASSWORD              # Same as DB password

# Direct (fallback/migrations)
SUPABASE_DB_HOST                      # e.g., db.project_ref.supabase.co
SUPABASE_DB_PORT                      # e.g., 5432
SUPABASE_DB_USER                      # postgres or postgres.project_ref
DATABASE_URL                          # Full connection string (optional override)
```

### API Keys - External Services
```
GOOGLE_MAPS_API_KEY                   # Google Maps API key
SCRAPER_API_KEY                       # ScraperAPI key
OPENAI_API_KEY                        # OpenAI embeddings API key
```

### Cost Control - ScraperAPI
```
SCRAPER_API_COST_CONTROL_MODE=true    # Enable cost monitoring
SCRAPER_API_ENABLE_PREMIUM=false      # Disable 5x premium multiplier
SCRAPER_API_ENABLE_JS_RENDERING=false # Disable 10x JS rendering
SCRAPER_API_ENABLE_GEOTARGETING=false # Disable 2x geotargeting
SCRAPER_API_MAX_RETRIES=1             # Minimize costs (default 3)
```

### Optional Services
```
MAUTIC_BASE_URL                       # Mautic CRM instance
MAUTIC_CLIENT_ID                      # OAuth client ID
MAUTIC_CLIENT_SECRET                  # OAuth client secret

GCP_PROJECT_ID                        # Google Cloud project
GCP_SERVICE_ACCOUNT_EMAIL             # Service account
GCP_SERVICE_ACCOUNT_PRIVATE_KEY       # Private key (escaped newlines)
GCP_SERVICE_ACCOUNT_TOKEN_URI         # OAuth token endpoint
```

## Connection Strings

### Supavisor (Production)
```
postgresql+asyncpg://postgres.{project_ref}:{password}@{pooler_host}:6543/postgres?statement_cache_size=0
```

### Direct PostgreSQL
```
postgresql+asyncpg://postgres.{project_ref}:{password}@db.{project_ref}.supabase.co:5432/postgres?statement_cache_size=0
```

## Code Integration Points

### 1. Database in Routes
```python
from fastapi import Depends
from src.db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

@app.post("/endpoint")
async def my_endpoint(session: AsyncSession = Depends(get_db_session)):
    # Session auto-commits on success
    # Auto-rollbacks on error
    pass
```

### 2. Database in Background Tasks
```python
from src.db.session import get_session

async def background_task():
    async with get_session() as session:
        # Perform database operations
        pass
```

### 3. Google Maps Search
```python
from src.services.places.places_search_service import PlacesSearchService

places = await PlacesSearchService.search_places(
    location="New York, NY",
    business_type="dentist",
    radius_km=10,
    max_results=20
)
```

### 4. Google Maps Deep Scan
```python
from src.services.places.places_deep_service import PlacesDeepService

service = PlacesDeepService()
business = await service.process_single_deep_scan(place_id, tenant_id)
```

### 5. ScraperAPI
```python
from src.utils.scraper_api import ScraperAPIClient

async with ScraperAPIClient() as client:
    # Basic fetch
    content = await client.fetch(url)
    
    # With JavaScript rendering
    content = await client.fetch_with_js(url)
```

### 6. Vector Search
```python
from src.routers.vector_db_ui import router

# POST /api/v3/vector-db/search
# Body: {"query": "search text", "limit": 5}
```

## Critical Configurations

### Connection Pooling (Mandatory for Supavisor)
```python
# MUST include in all connections:
raw_sql=true
no_prepare=true
statement_cache_size=0

# Timeouts
pool_pre_ping=True          # Validate before use
pool_timeout=30             # Connection acquisition timeout
command_timeout=30          # Query execution timeout
```

### HTTP Clients

**aiohttp (Google Maps, Scraper):**
- Limit: 50 total connections
- Per-host limit: 20
- Keepalive: 60 seconds
- Timeout: 30 seconds (scrapers), 70 seconds (ScraperAPI)

**SSL Configuration:**
```python
# Production: Enable verification
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Development: Disable for self-signed
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.check_hostname = False
```

## File Locations Reference

| Component | File(s) |
|-----------|---------|
| Database Config | `src/db/engine.py`, `src/db/session.py` |
| Settings | `src/config/settings.py` |
| Google Maps | `src/services/places/*` |
| ScraperAPI | `src/utils/scraper_api.py` |
| Simple Scraper | `src/utils/simple_scraper.py` |
| Metadata Extractor | `src/scraper/metadata_extractor.py` |
| Sitemap Analyzer | `src/scraper/sitemap_analyzer.py` |
| Vector DB | `src/routers/vector_db_ui.py` |
| Email Scraper | `src/tasks/email_scraper.py` |

## Cost Monitoring

### ScraperAPI Credit Calculation
```
Base: 1 credit
Premium: ×5 (if enabled)
JS Rendering: ×10 (if enabled)
Geotargeting: ×2 (if enabled)

Example costs:
- Basic request: 1 credit
- Premium + JS: 50 credits
- All options: 100 credits

Alerts:
- Per-request: Log warning if >= 10 credits
- Cumulative: Log error if >= 1000 credits
```

### Google Maps
- Text Search: ~$7 per 1000 requests
- Place Details: ~$17 per 1000 requests
- Monitor via Google Cloud Console

### OpenAI
- Embeddings (text-embedding-ada-002): ~$0.02 per 1M tokens
- Query costs vary by model version

## Testing Integration Points

### 1. Database Connection
```bash
# Check database health
curl http://localhost:8000/health/database
```

### 2. Google Maps
```python
# In code
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
assert api_key, "Google Maps API key not configured"
```

### 3. ScraperAPI
```python
from src.utils.scraper_api import ScraperAPIClient

# Test client
success = await ScraperAPIClient.test_client("https://example.com")
```

## Troubleshooting

### Connection Pooler Issues
```
Error: "too many connections"
Solution:
1. Check pool_size configuration
2. Verify Supavisor is active
3. Ensure statement_cache_size=0
4. Check pool_recycle settings
```

### API Key Missing
```
Error: "GOOGLE_MAPS_API_KEY environment variable not set"
Solution:
1. Verify .env file
2. Check settings.py loads from environment
3. Fallback to settings.google_maps_api_key
```

### ScraperAPI Cost Overrun
```
High credit usage detected
Solution:
1. Check SCRAPER_API_COST_CONTROL_MODE
2. Disable premium/JS rendering
3. Review request patterns
4. Check credit_monitor logs
```

### Supavisor Compatibility
```
Error: "prepared statement name conflicts"
Solution:
1. Ensure raw_sql=true
2. Ensure no_prepare=true
3. Ensure statement_cache_size=0
4. Use statement name function with UUIDs
```

## API Endpoints Summary

### Google Maps Search
```
POST /api/v3/localminer-discoveryscan/search/places
Body: {
  "business_type": "dentist",
  "location": "New York, NY",
  "radius_km": 10,
  "tenant_id": "uuid"
}
Response: {"job_id": "uuid", "status_url": "..."}
```

### Vector Database Search
```
POST /api/v3/vector-db/search
Body: {"query": "search term", "limit": 5}
Response: [{"id": "...", "title": "...", "similarity": 0.95, ...}]
```

### Database Health Check
```
GET /health/database
Response: {"status": "ok", "connection": "healthy"}
```

## Key Dependencies

```
# Database
SQLAlchemy==2.0.38
asyncpg==0.30.0
psycopg[binary]==3.2.5

# HTTP Clients
aiohttp>=3.9.3
httpx
requests==2.32.3

# External APIs
googlemaps==4.10.0
scraperapi-sdk==1.5.3
openai

# Parsing
beautifulsoup4==4.13.3
lxml>=5.2.2

# Other
pydantic==2.10.6
pydantic-settings==2.7.1
```
