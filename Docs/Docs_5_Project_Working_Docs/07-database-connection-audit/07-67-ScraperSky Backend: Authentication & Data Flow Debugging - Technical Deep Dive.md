# ScraperSky Backend System Investigation & Debugging

## Problem Statement

The ScraperSky metadata extraction system was failing to extract and display website metadata when triggered through the web interface, but it worked correctly when triggered via direct API calls with cURL. This inconsistency pointed to issues in the data flow or authentication pathways.

## System Architecture Overview

### Core Components

```
+------------------------+     +------------------------+     +-----------------------+
|      Web Interface     |     |   API Endpoints/Routes |     |   Database (PostgreSQL)|
| (single-domain-scanner)|---->| (/api/v3/*)           |---->| - jobs                |
+------------------------+     +------------------------+     | - domains             |
                                         |                    +-----------------------+
                                         v                               ^
                                +------------------------+               |
                                | Background Processing  |               |
                                | - domain_processor     |---------------+
                                | - metadata_extractor   |
                                +------------------------+
                                         |
                                         v
                                +------------------------+
                                | External Service       |
                                | - ScraperAPI           |
                                +------------------------+
```

### Key API Routes

1. **Scan Initiation**: `POST /api/v3/modernized_page_scraper/scan`

   - Creates a job and initiates background processing
   - Returns a job ID and status URL

2. **Status Checking**: `GET /api/v3/batch_page_scraper/status/{job_id}`
   - Returns job status, progress, and results

### Data Flow

```
1. Client Request
   |
2. API Endpoint (Router)
   |
3. Create Job Record → DATABASE
   |
4. Spawn Background Task
   |
5. Fetch Website via ScraperAPI
   |
6. Process Website Content (extract metadata)
   |
7. Update Job with Results → DATABASE
   |
8. Client Polls Status Endpoint
   |
9. Status Endpoint Returns Results From DATABASE
```

## Root Causes Identified

1. **Inconsistent Development Mode Detection**

   - The authentication bypass logic was not properly checking environment settings
   - Web interface and cURL requests were being treated differently based on auth state

2. **Import Paths Issues**

   - Incorrect import paths for `settings` module in multiple files
   - Consistency issues between development and production code

3. **ScraperAPI Integration Limitations**
   - Some domains required premium or ultra_premium parameters
   - Rate limits and protection measures affected scraping success

## Fixes Implemented

1. **Authentication Consistency Fix**

Before:

```python
def is_development_mode() -> bool:
    dev_mode = os.getenv("SCRAPER_SKY_DEV_MODE", "").lower() == "true"
    if dev_mode:
        logger.warning("⚠️ Running in DEVELOPMENT mode - ALL AUTH CHECKS BYPASSED ⚠️")
    return dev_mode
```

After:

```python
def is_development_mode() -> bool:
    dev_mode = os.getenv("SCRAPER_SKY_DEV_MODE", "").lower() == "true"
    if dev_mode:
        logger.warning("⚠️ Running in DEVELOPMENT mode - ALL AUTH CHECKS BYPASSED ⚠️")
    return dev_mode or settings.environment.lower() in ["development", "dev"]
```

2. **Import Path Fix**

Before:

```python
from ..config import settings
```

After:

```python
from ..config.settings import settings
```

3. **ScraperAPI Integration** (identified issues, didn't change to avoid additional costs):
   - Premium and ultra_premium parameters would have improved success rates
   - Protected domains require additional configuration

## Key System Components in Detail

### 1. Metadata Extraction Process

The heart of the system is the metadata extraction workflow:

```
detect_site_metadata() → site_metadata
       ↓
[result_metadata creation with site_metadata]
       ↓
update_job_with_results(job_id, "completed", result_metadata)
       ↓
SQL: UPDATE jobs
     SET status = :status,
         result = :result_json,
         result_data = :result_json,
         completed_at = NOW()
     WHERE job_id = :job_id
```

Located in:

- `src/scraper/metadata_extractor.py`: Extracts website metadata
- `src/services/page_scraper/domain_processor.py`: Processes domain and updates job status

### 2. Background Processing System

The system uses FastAPI background tasks for asynchronous processing:

```python
# In router
background_tasks.add_task(
    process_domain_with_own_session,
    job_id=result["job_id"],
    domain=base_url,
    user_id=user_id,
    max_pages=max_pages
)
```

This ensures the API can respond quickly while processing continues in the background.

### 3. Authentication System

A key insight was that the development mode bypass was critical for testing but needed to consistently check both:

- Environment variable `SCRAPER_SKY_DEV_MODE`
- Application settings `settings.environment`

### 4. Database Interaction

The system uses raw SQL with transaction handling for maximum compatibility with Supavisor connection pooling:

```python
update_query = text("""
    UPDATE jobs
    SET status = :status,
        result = :result_json,
        result_data = :result_json,
        completed_at = NOW()
    WHERE job_id = :job_id
""").execution_options(prepared=False)
```

## Operational Notes

1. **Environment Configuration**

   - Development mode: Set `SCRAPER_SKY_DEV_MODE=true` or ensure `settings.environment` is "development"
   - API key: Set `SCRAPER_API_KEY` to valid ScraperAPI key

2. **Protected Domains**

   - Some domains require premium or ultra_premium ScraperAPI parameters
   - Error message: "Protected domains may require adding premium=true OR ultra_premium=true parameter"

3. **Response Times**
   - Scraping can take from seconds to minutes depending on website complexity
   - Polling for status should implement exponential backoff

## Testing Strategy

When testing changes:

1. Test with cURL for direct API access:

   ```
   curl -X POST http://localhost:8000/api/v3/modernized_page_scraper/scan -H "Content-Type: application/json" -H "Authorization: Bearer scraper_sky_2024" -d '{"base_url":"example.org", "max_pages": 1}'
   ```

2. Test with web interface to verify full flow
3. Check logs with:
   ```
   docker-compose logs --tail=100 scrapersky
   ```

## Troubleshooting Guide

### If Scraping Fails

1. **Check Authentication**

   - Verify development mode is properly detected
   - Check if Authorization header is present

2. **Check ScraperAPI Integration**

   - Verify API key is valid with direct test:
     ```
     curl "http://api.scraperapi.com?api_key=YOUR_KEY&url=http://example.org"
     ```
   - Check if domain requires premium/ultra_premium parameters

3. **Database Issues**

   - Verify job records are being created
   - Check if results are being properly stored

4. **Environment Variables**
   - Ensure `SCRAPER_API_KEY` is set
   - Check `SCRAPER_SKY_DEV_MODE` and `environment` settings

## Conclusion

The debugging process revealed that the system's authentication mechanism and import paths were inconsistent between different entry points. By standardizing these elements and understanding the full data flow, we ensured that both web interface and direct API calls follow the same path through the system, resulting in consistent behavior.

The experience also highlighted the importance of proper settings management and how seemingly small differences in authentication logic can lead to significant divergences in behavior.
