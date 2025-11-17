# External Dependency Map
**Purpose:** Document all external service dependencies  
**Last Updated:** November 17, 2025

---

## ScraperAPI

### Overview
- **Type:** Web scraping service
- **Purpose:** Fetch page HTML for contact extraction
- **Used By:** PageCurationService (WF7)
- **URL:** http://api.scraperapi.com

### Configuration
```python
# From settings
SCRAPER_API_KEY = settings.scraper_api_key

# Usage
params = {
    "api_key": SCRAPER_API_KEY,
    "url": page_url,
    "render": "false"  # Don't render JavaScript
}
response = await client.get("http://api.scraperapi.com", params=params)
```

### Cost
- **Pricing:** 1 credit per page request
- **Current Usage:** Unknown (needs monitoring)
- **Budget:** Unknown (needs definition)

### Rate Limits
- **Unknown** - Needs verification with ScraperAPI
- **Recommendation:** Add rate limit monitoring

### Failure Modes
- **HTTP errors:** Page marked as Error
- **Timeout:** Page marked as Error
- **No retry:** Manual requeue required

### Mitigation
- [ ] Add retry logic (WO-005 Gap #8)
- [ ] Add credit monitoring
- [ ] Add rate limit handling
- [ ] Cache responses where possible

### Impact if Down
- **Severity:** HIGH
- **Impact:** WF7 stops, no contact extraction
- **Workaround:** None (required for scraping)
- **Recovery:** Wait for service restoration, requeue failed pages

---

## Supabase

### Overview
- **Type:** PostgreSQL database hosting
- **Purpose:** Primary database for all application data
- **Access Method:** MCP (Model Context Protocol) tools
- **Environment:** Production

### Configuration
```python
# Connection via environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Service role key for admin operations
SUPABASE_SERVICE_ROLE_KEY = settings.supabase_service_role_key
```

### Tables
- places
- local_business
- domains
- sitemap_files
- pages
- jobs

### Access Patterns
- **Read:** Via MCP tools or direct SQL
- **Write:** Via SQLAlchemy ORM
- **Admin:** Via service role key

### Backup Strategy
- **Frequency:** [Needs documentation]
- **Retention:** [Needs documentation]
- **Recovery:** [Needs documentation]

### Failure Modes
- **Connection loss:** All operations fail
- **Query timeout:** Individual operations fail
- **Storage full:** Writes fail

### Mitigation
- Connection pooling (configured)
- Query timeout handling (needs improvement)
- Storage monitoring (needs implementation)

### Impact if Down
- **Severity:** CRITICAL
- **Impact:** Complete system failure
- **Workaround:** None
- **Recovery:** Wait for Supabase restoration

---

## Render.com

### Overview
- **Type:** Deployment platform
- **Purpose:** Host Docker containers in production
- **Environment:** Production
- **Access:** Web dashboard

### Configuration
- **Auto-deploy:** On git push to main branch
- **Container:** Docker-based
- **Environment Variables:** Set in Render dashboard

### Logs
- **Access:** Render.com web dashboard
- **Retention:** [Needs documentation]
- **Search:** Via dashboard UI

### Deployment Process
1. Push to main branch
2. Render detects push
3. Builds Docker image
4. Deploys new container
5. Health check
6. Routes traffic

### Failure Modes
- **Build failure:** Deployment stops, old version continues
- **Health check failure:** Deployment rolls back
- **Container crash:** Auto-restart

### Mitigation
- Pre-deployment testing
- Health check endpoint (needs implementation)
- Monitoring and alerts

### Impact if Down
- **Severity:** CRITICAL
- **Impact:** Production unavailable
- **Workaround:** None
- **Recovery:** Wait for Render restoration or migrate to backup

---

## Honeybee

### Overview
- **Type:** URL categorization system
- **Purpose:** Classify pages by type and purpose
- **Used By:** SitemapImportService (WF5)
- **Integration:** Python library

### Configuration
```python
from honeybee import categorize_url

result = categorize_url(url)
# Returns: {category, confidence, depth}
```

### Categories
- CONTACT_ROOT - Main contact page
- CAREER_CONTACT - Jobs/careers page
- LEGAL_ROOT - Legal/privacy pages
- unknown - Not categorized or low confidence
- [Many others]

### Auto-Selection Rules
```python
if (
    category in {CONTACT_ROOT, CAREER_CONTACT, LEGAL_ROOT}
    and confidence >= 0.6
    and depth <= 2
):
    # Auto-select for processing
```

### Failure Modes
- **Import error:** WF5 fails to start
- **Categorization error:** Pages marked as 'unknown'
- **Performance issue:** Slow URL import

### Mitigation
- Error handling around categorization calls
- Fallback to 'unknown' category
- Performance monitoring

### Impact if Down
- **Severity:** MEDIUM
- **Impact:** No auto-selection, all pages manual
- **Workaround:** Manual page selection
- **Recovery:** Fix Honeybee integration

---

## Google Maps API

### Overview
- **Type:** External API (Google Cloud Platform)
- **Purpose:** Business search and place details (WF1 Single Search)
- **Used By:** WF1 services (`src/services/places/`) and router (`src/routers/google_maps_api.py`)
- **API Documentation:** `Docs_Context7/External_APIs/Google_Maps_API_Documentation.md`

### Configuration
```python
# From .env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Used in WF1 services
from src.config.settings import settings
api_key = settings.google_maps_api_key
```

### APIs Used
- **Places API:** Text search for businesses (`places()` method)
- **Geocoding API:** Address-to-coordinate conversion
- **Place Details API:** Additional place information

### Rate Limits
- **Quota Type:** Per project (Google Cloud)
- **Limit:** Varies by API and billing plan
- **Monitoring:** Google Cloud Console
- **Best Practice:** Implement caching to reduce API calls

### Cost Structure
- **Pricing Model:** Pay-per-request
- **Place Search:** $32 per 1,000 requests (Text Search)
- **Place Details:** $17 per 1,000 requests (Basic Data)
- **Optimization:** Cache results, batch requests where possible
- **Free Tier:** $200/month credit (Google Cloud)

### Failure Modes
- **Invalid API Key:** HTTP 403 errors
- **Quota Exceeded:** HTTP 429 errors
- **Network Timeout:** Connection failures
- **Invalid Query:** HTTP 400 errors
- **Rate Limiting:** Temporary throttling

### Mitigation
- [x] API key in environment variables (security)
- [ ] Implement request caching (cost reduction)
- [ ] Add retry logic with exponential backoff
- [ ] Monitor quota usage in Google Cloud Console
- [ ] Alert on quota thresholds (80%, 90%)

### Impact if Down
- **Severity:** HIGH
- **Impact:** WF1 stops, no new business discovery
- **Workaround:** None (required for business search)
- **Recovery:** Wait for Google service restoration
- **Mitigation:** Cache previous results for common queries

---

## Dependency Summary

| Service | Used By | Severity | Cost | Monitoring |
|---------|---------|----------|------|------------|
| ScraperAPI | WF7 | HIGH | 1 credit/page | ❌ Needed |
| Supabase | All | CRITICAL | Monthly | ✅ Basic |
| Render.com | All | CRITICAL | Monthly | ✅ Basic |
| Honeybee | WF5 | MEDIUM | None | ❌ Needed |
| Google Maps | WF1 | HIGH | Per request | ❌ Needed |

---

## Monitoring Recommendations

### Immediate (P0)
- [ ] ScraperAPI credit monitoring
- [ ] ScraperAPI rate limit tracking
- [ ] Database storage monitoring

### Short-Term (P1)
- [ ] Google Maps API usage tracking
- [ ] Honeybee performance monitoring
- [ ] Render.com deployment alerts

### Long-Term (P2)
- [ ] Cost optimization analysis
- [ ] Dependency health dashboard
- [ ] Automated failover strategies

---

## Cost Optimization

### ScraperAPI
- **Current:** No caching, every page fetched
- **Opportunity:** Cache responses for duplicate URLs
- **Savings:** Potentially 20-30% reduction

### Database
- **Current:** Unknown storage usage
- **Opportunity:** Archive old records, optimize indexes
- **Savings:** Reduce storage costs

### Render.com
- **Current:** Always-on containers
- **Opportunity:** Scale down during low usage
- **Savings:** Potentially 10-20% reduction

---

**For more information:**
- [SYSTEM_MAP.md](./SYSTEM_MAP.md) - How dependencies fit into architecture
- [HEALTH_CHECKS.md](./HEALTH_CHECKS.md) - How to verify dependencies
- [WF4_WF5_WF7_GAPS_IMPROVEMENTS.md](../Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md) - Improvement opportunities
