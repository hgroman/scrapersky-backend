# ContentMap (Sitemap Analyzer) Database Persistence Implementation

## Overview

This work order outlines the process for implementing database persistence for the ContentMap (Sitemap Analyzer) feature in the ScraperSky backend. We've successfully modernized the API structure and integrated the business logic, but the final step of saving sitemap data to the database is incomplete.

## Current State Analysis

1. **Architecture Progress**:

   - ✅ Modernized router structure in `modernized_sitemap.py`
   - ✅ Proper transaction handling at router level
   - ✅ Integration with original `SitemapAnalyzer` for business logic
   - ✅ In-memory job status tracking for API responses
   - ❌ Missing database persistence for discovered sitemaps and URLs

2. **Architectural Pattern**:

   - The codebase follows a service-oriented architecture
   - Routers own transaction boundaries
   - Services use the database session provided by the router
   - The db_service is used for database operations with proper transaction handling

3. **Existing Database Schema**:
   - `sitemap_files`: Stores information about discovered sitemap files
   - `sitemap_urls`: Stores URLs extracted from the sitemap files

## Implementation Plan

### 1. Database Persistence with db_service

We need to implement the database persistence logic in the `_process_domain` method of the `SitemapProcessingService` class, using the provided db_service pattern. The method already has proper session handling for background tasks.

### 2. Database Schema Overview

**sitemap_files Table**:

- Primary Fields: id, domain_id, url, sitemap_type, discovery_method
- Metadata: size_bytes, has_lastmod, has_priority, has_changefreq, url_count
- Security: tenant_id, created_by
- Processing: job_id, status

**sitemap_urls Table**:

- Primary Fields: id, sitemap_id, url
- Metadata: lastmod, changefreq, priority
- Security: tenant_id, created_by

### 3. Transaction Handling Requirements

- Follow the established transaction pattern in the project
- Background tasks create their own sessions when session=None
- Ensure proper error handling with session management
- Maintain tenant isolation by including tenant_id in all database operations

## Implementation Tasks

### 1. Update Processing Service for Database Persistence

**File**: `src/services/sitemap/processing_service.py`

**Changes Needed**:

1. Update the `_process_domain` method to persist discovered sitemaps and URLs using db_service
2. Implement proper error handling with transaction management
3. Add database query for the `get_job_status` method to retrieve historic jobs

### 2. Implementation Details

#### A. Storing Sitemap Files

For each discovered sitemap, we need to insert a record in the sitemap_files table:

```python
# Example using db_service for sitemap file insertion
sitemap_id = await db_service.execute_returning(
    """
    INSERT INTO sitemap_files (
        id, domain_id, url, sitemap_type, discovery_method,
        tenant_id, created_by, job_id, status, url_count
    ) VALUES (
        gen_random_uuid(), :domain_id, :url, :sitemap_type, :discovery_method,
        :tenant_id, :created_by, :job_id, :status, :url_count
    ) RETURNING id
    """,
    {
        "domain_id": domain_id,
        "url": sitemap_url,
        "sitemap_type": sitemap_type,
        "discovery_method": discovery_method,
        "tenant_id": tenant_id,
        "created_by": user_id,
        "job_id": job_id,
        "status": "complete",
        "url_count": len(urls)
    }
)
```

#### B. Storing Sitemap URLs

For each URL in a sitemap, we need to insert a record in the sitemap_urls table:

```python
# Example using db_service for batch URL insertion
# Note: URLs should be inserted in batches for better performance
url_values = []
url_params = {}

for idx, url_data in enumerate(batch_urls):
    prefix = f"url_{idx}"
    url_values.append(f"(gen_random_uuid(), :sitemap_id, :{prefix}_url, :{prefix}_lastmod, :{prefix}_changefreq, :{prefix}_priority, :tenant_id, :created_by)")
    url_params[f"{prefix}_url"] = url_data.get("loc")
    url_params[f"{prefix}_lastmod"] = url_data.get("lastmod")
    url_params[f"{prefix}_changefreq"] = url_data.get("changefreq")
    url_params[f"{prefix}_priority"] = url_data.get("priority")

url_params["sitemap_id"] = sitemap_id
url_params["tenant_id"] = tenant_id
url_params["created_by"] = user_id

values_clause = ", ".join(url_values)
insert_query = f"""
    INSERT INTO sitemap_urls (
        id, sitemap_id, url, lastmod, changefreq,
        priority, tenant_id, created_by
    ) VALUES {values_clause}
"""

await db_service.execute(insert_query, url_params)
```

#### C. Retrieving Job Status from Database

When a job is not found in memory (e.g., server restart), we should query the database:

```python
# Example using db_service to retrieve job status from database
if job_id not in _job_statuses:
    # Try to fetch from database
    sitemap_files = await db_service.fetch_all(
        """
        SELECT * FROM sitemap_files
        WHERE job_id = :job_id AND tenant_id = :tenant_id
        ORDER BY created_at DESC
        """,
        {"job_id": job_id, "tenant_id": tenant_id}
    )

    if sitemap_files:
        # Build status from database records
        # ...
```

### 3. Transaction Management

**Key Transaction Rules**:

1. In background tasks, create a new session when session=None
2. Use proper transaction boundaries with async with session.begin()
3. Handle errors with try/except and ensure proper session cleanup
4. Batch inserts for better performance

### 4. Testing

After implementation, test with:

1. **Scan a domain**:

   ```bash
   curl -H "Authorization: Bearer scraper_sky_2024" -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" -H "Content-Type: application/json" -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 10000}' http://localhost:8000/api/v3/sitemap/scan
   ```

2. **Check job status**:

   ```bash
   curl -H "Authorization: Bearer scraper_sky_2024" -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" http://localhost:8000/api/v3/sitemap/status/{job_id}
   ```

3. **Verify database records**:
   ```sql
   SELECT * FROM sitemap_files WHERE job_id = '{job_id}';
   SELECT COUNT(*) FROM sitemap_urls WHERE sitemap_id IN (SELECT id FROM sitemap_files WHERE job_id = '{job_id}');
   ```

## Deliverables

1. Updated `_process_domain` method in `SitemapProcessingService` with database persistence
2. Updated `get_job_status` method to retrieve job status from database when not in memory
3. Proper error handling and transaction management
4. Verified test results with data persisted in the database

## Success Criteria

1. Sitemap scan jobs complete successfully
2. Discovered sitemaps are stored in the sitemap_files table
3. Extracted URLs are stored in the sitemap_urls table
4. Job status can be retrieved even after server restart
5. All operations maintain proper transaction boundaries and tenant isolation

## Additional Resources

1. **Transaction Management Pattern**: Found in `204-TRANSACTION-MANAGEMENT-PATTERN.md`
2. **Sitemap Transaction Fix**: Found in `323-MODERNIZED-SITEMAP-TRANSACTION-FIX-SUMMARY.md`
3. **ContentMap Feature Fix**: Found in `601-SITEMAP-ANALYZER-FEATURE-FIX-SUMMARY.md`
4. **Database Models**: Found in `src/models/sitemap.py`
5. **DB Service**: Found in `src/services/db_service.py`
6. **Sitemap DB Handler**: Found in `src/db/sitemap_handler.py`
