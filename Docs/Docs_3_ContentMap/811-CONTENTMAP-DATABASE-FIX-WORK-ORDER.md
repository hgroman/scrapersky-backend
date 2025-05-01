# ContentMap Database Persistence Fix Work Order

## Overview

This work order outlines the process for fixing database persistence issues in the ContentMap (Sitemap Analyzer) feature. Our current implementation successfully processes sitemaps and URLs but fails to properly store data in the database. This document provides comprehensive instructions to resolve these issues and ensure proper database integration.

## Current State Analysis

1. **Implementation Status**:

   - ✅ API endpoints function correctly
   - ✅ Sitemap discovery and processing logic works
   - ✅ In-memory job status tracking operates as expected
   - ❌ Database persistence is failing - no records are being stored

2. **Database Schema**:

   - **sitemap_files**: Contains metadata about discovered sitemap files
   - **sitemap_urls**: Stores individual URLs extracted from sitemaps

3. **Identified Issues**:
   - No records with our job ID format (`job_*`) appear in the database
   - The existing records in `sitemap_files` use a different job ID format (`sitemap_*`)
   - Field mismatches between implementation and database schema
   - Potential transaction rollbacks or silent failures

## Implementation Requirements

### 1. Code Modifications

#### A. Update Job ID Format

First, modify the job ID generation in `src/services/sitemap/processing_service.py`:

```python
# Current implementation
job_id = f"job_{str(uuid.uuid4())[:8]}"

# Modify to match existing format
job_id = f"sitemap_{uuid.uuid4().hex[:32]}"
```

#### B. Align Field Names with Database Schema

Fix field name mismatches in the database insertion code:

```python
# For sitemap_urls table
# Current implementation uses "priority" directly
# Should use "priority_value" for this field

# For example, modify:
url_params[f"{prefix}_priority"] = priority

# To:
url_params[f"{prefix}_priority_value"] = priority
```

#### C. Fix Database Insertion Logic

Update the database insertion code in `_process_domain` to properly handle fields:

```python
# For sitemap_files table
sitemap_id = await db_service.execute_returning(
    """
    INSERT INTO sitemap_files (
        id, tenant_id, domain_id, url, sitemap_type, discovery_method,
        size_bytes, has_lastmod, has_priority, has_changefreq,
        status, job_id
    ) VALUES (
        gen_random_uuid(), :tenant_id, :domain_id, :url, :sitemap_type, :discovery_method,
        :size_bytes, :has_lastmod, :has_priority, :has_changefreq,
        'completed', :job_id
    ) RETURNING id
    """,
    {
        "tenant_id": tenant_id,
        "domain_id": clean_domain,  # Use domain as domain_id
        "url": sitemap_url,
        "sitemap_type": sitemap_type,
        "discovery_method": discovery_method,
        "size_bytes": sitemap.get('size_bytes', 0),
        "has_lastmod": has_lastmod,
        "has_priority": has_priority,
        "has_changefreq": has_changefreq,
        "job_id": job_id
    }
)
```

#### D. Fix URL Insertion

Ensure the URL insertion SQL matches the exact database schema:

```python
# For sitemap_urls table
values_clause = ", ".join(url_values)
insert_query = f"""
    INSERT INTO sitemap_urls (
        id, tenant_id, domain_id, sitemap_id, url,
        lastmod, changefreq, priority_value, status,
        created_at, created_by
    ) VALUES {values_clause}
"""
```

#### E. Add Explicit Transaction Handling

Ensure proper transaction handling with explicit error logging:

```python
try:
    # Database operations here
    logger.info(f"Successfully stored {len(sitemap_ids)} sitemaps and {total_urls} URLs")
except Exception as e:
    logger.error(f"Database error in _process_domain: {str(e)}", exc_info=True)
    # Re-raise to ensure the transaction is rolled back
    raise
```

### 2. Debugging Enhancements

#### A. Add Detailed Logging

Add detailed logging throughout the database operations:

```python
# Before database operations
logger.info(f"Starting database persistence for job {job_id}, domain {clean_domain}")

# Before each sitemap insertion
logger.debug(f"Inserting sitemap: {sitemap_url}, type: {sitemap_type}, discovery: {discovery_method}")

# After successful sitemap insertion
logger.debug(f"Inserted sitemap with ID {sitemap_id}")

# Before URL batch insertion
logger.debug(f"Inserting batch of {len(batch_urls)} URLs for sitemap {sitemap_id}")

# After successful URL batch insertion
logger.debug(f"Successfully inserted URL batch for sitemap {sitemap_id}")
```

#### B. Add SQL Query Logging

Enable SQL query logging for development:

```python
# At the top of the file
import logging
logger = logging.getLogger(__name__)
```

#### C. Add Parameter Validation

Add explicit parameter validation:

```python
# Validate domain_id
if not clean_domain:
    logger.error("domain_id cannot be empty")
    raise ValueError("domain_id cannot be empty")

# Validate tenant_id
if not tenant_id:
    logger.error("tenant_id cannot be empty")
    raise ValueError("tenant_id cannot be empty")
```

## Database Requirements

### 1. Foreign Key Constraints

Ensure that foreign keys are properly handled:

1. `tenant_id` must exist in the `tenants` table
2. `domain_id` must exist in the `domains` table
3. `sitemap_id` in `sitemap_urls` must reference a valid ID in `sitemap_files`

If domain doesn't exist, create it first:

```python
# Check if domain exists
domain_result = await db_service.fetch_one(
    """
    SELECT id FROM domains
    WHERE domain = :domain AND tenant_id = :tenant_id
    """,
    {"domain": clean_domain, "tenant_id": tenant_id}
)

domain_id = None
if domain_result:
    domain_id = domain_result.get('id')
else:
    # Create domain
    domain_result = await db_service.execute_returning(
        """
        INSERT INTO domains (id, domain, tenant_id, created_by)
        VALUES (gen_random_uuid(), :domain, :tenant_id, :created_by)
        RETURNING id
        """,
        {
            "domain": clean_domain,
            "tenant_id": tenant_id,
            "created_by": user_id
        }
    )
    domain_id = domain_result.get('id')

# Then use domain_id in all subsequent queries
```

### 2. Required Fields

For `sitemap_files` table, ensure these fields are never null:

- `tenant_id`
- `domain_id`
- `url`
- `sitemap_type`
- `status`

For `sitemap_urls` table, ensure these fields are never null:

- `tenant_id`
- `domain_id`
- `sitemap_id`
- `url`
- `status`

## Testing and Verification Plan

### 1. Test Script

Create a test script at `scripts/test_contentmap_db.py`:

```python
#!/usr/bin/env python
"""
ContentMap Database Persistence Test

This script tests the database persistence of the ContentMap feature
by making API calls and verifying database records.
"""
import sys
import os
import requests
import time
import json
from typing import Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import db_service for verification
from src.services.core.db_service import db_service

async def test_contentmap_persistence():
    """Test ContentMap feature database persistence."""
    # API endpoint and headers
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": "Bearer scraper_sky_2024",
        "X-Tenant-ID": "550e8400-e29b-41d4-a716-446655440000",
        "Content-Type": "application/json"
    }

    # Step 1: Initiate a scan
    scan_url = f"{base_url}/api/v3/sitemap/scan"
    payload = {
        "base_url": "example.com",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "max_pages": 100
    }

    response = requests.post(scan_url, headers=headers, json=payload)
    print(f"Scan Response: {response.status_code}")

    if response.status_code != 202:
        print(f"Error initiating scan: {response.text}")
        return

    data = response.json()
    job_id = data.get("job_id")

    print(f"Job created with ID: {job_id}")

    # Step 2: Wait for job to complete
    status_url = f"{base_url}/api/v3/sitemap/status/{job_id}"
    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        time.sleep(2)  # Wait 2 seconds between checks
        status_response = requests.get(status_url, headers=headers)

        if status_response.status_code != 200:
            print(f"Error checking status: {status_response.text}")
            break

        status_data = status_response.json()
        status = status_data.get("status")

        print(f"Job status: {status}")

        if status in ["complete", "failed"]:
            break

        attempts += 1

    # Step 3: Check database records
    sitemap_files = await db_service.fetch_all(
        "SELECT * FROM sitemap_files WHERE job_id = :job_id",
        {"job_id": job_id}
    )

    print(f"Found {len(sitemap_files)} sitemap records in database")

    if sitemap_files:
        sitemap_id = sitemap_files[0].get("id")
        sitemap_urls = await db_service.fetch_all(
            "SELECT COUNT(*) FROM sitemap_urls WHERE sitemap_id = :sitemap_id",
            {"sitemap_id": sitemap_id}
        )

        url_count = sitemap_urls[0].get("count") if sitemap_urls else 0
        print(f"Found {url_count} URL records for the first sitemap")

    # Return success/failure
    return len(sitemap_files) > 0

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_contentmap_persistence())
    print(f"Test result: {'Success' if success else 'Failure'}")
    sys.exit(0 if success else 1)
```

### 2. Manual Verification SQL Queries

After running the test script, execute these SQL queries to verify records:

```sql
-- Check for sitemap files
SELECT COUNT(*) FROM sitemap_files WHERE job_id LIKE 'sitemap_%';

-- Get details of the latest job
SELECT job_id, tenant_id, domain_id, url, sitemap_type, discovery_method,
       created_at, updated_at
FROM sitemap_files
ORDER BY created_at DESC
LIMIT 5;

-- Check for URLs
SELECT COUNT(*) FROM sitemap_urls;

-- Check URL details for a specific sitemap
SELECT sitemap_id, url, lastmod, changefreq, priority_value
FROM sitemap_urls
WHERE sitemap_id = '<sitemap_id>'
LIMIT 10;
```

### 3. Verification Procedure

Follow these steps to verify the fix:

1. Implement all the code modifications described above
2. Restart the service (docker-compose restart)
3. Run the test script: `python scripts/test_contentmap_db.py`
4. Check the logs for any errors
5. Manually inspect the database records using the verification SQL queries
6. Verify that domain, sitemap, and URL records are being properly created
7. Confirm that job status is correctly tracked after server restart

## Success Criteria

The implementation is considered successful when:

1. The test script passes with a success result
2. Database inspection confirms records are being created with correct:
   - Job ID format (using 'sitemap\_' prefix)
   - Foreign key relationships (tenant_id, domain_id, sitemap_id)
   - Field values (sitemap_type, discovery_method, etc.)
3. URL records are being correctly associated with their parent sitemaps
4. No errors or warnings appear in the logs related to database operations
5. Job status retrieval works even after server restart (database fallback)

## Additional Resources

1. **Database Schema**:

   - `sitemap_files` table schema (see 'inspect_table.py sitemap_files' output)
   - `sitemap_urls` table schema (see 'inspect_table.py sitemap_urls' output)

2. **Existing Code**:

   - `src/services/sitemap/processing_service.py`: Contains current implementation
   - `src/scraper/sitemap_analyzer.py`: Original business logic

3. **Database Utilities**:
   - `scripts/db/inspect_table.py`: For examining table structure and data

## Reference Implementation

Here's a reference implementation of the `_process_domain` method with proper database persistence:

```python
async def _process_domain(
    self,
    domain: str,
    job_id: str,
    tenant_id: str,
    max_pages: int,
    user_id: Optional[str] = None,
    session: Optional[AsyncSession] = None
) -> None:
    """
    Process a domain in the background using SitemapAnalyzer.

    This method discovers sitemaps, extracts URLs, and persists data to the database.

    Args:
        domain: Domain to process
        job_id: Unique job identifier
        tenant_id: Tenant ID for isolation
        max_pages: Maximum number of pages to process
        user_id: User ID who initiated the request
        session: Database session (typically None for background tasks)
    """
    logger.info(f"Starting background processing for domain: {domain}, job_id: {job_id}")

    # Update job status to running
    if job_id in _job_statuses:
        _job_statuses[job_id]['status'] = 'running'
        _job_statuses[job_id]['started_at'] = datetime.utcnow().isoformat()
        _job_statuses[job_id]['progress'] = 0.1

    # Create a new session if one wasn't provided
    from ...db.session import get_session, async_session

    own_session = session is None
    if own_session:
        logger.debug(f"Creating new session for background task: {job_id}")
        session_ctx = async_session()
    else:
        logger.debug(f"Using provided session for background task: {job_id}")
        session_ctx = session

    try:
        # Standardize domain
        try:
            clean_domain = standardize_domain(domain)
            logger.info(f"Standardized domain: {clean_domain}")

            # Update status with standardized domain
            if job_id in _job_statuses:
                _job_statuses[job_id]['domain'] = clean_domain
        except ValueError as e:
            logger.error(f"Invalid domain: {domain}, error: {str(e)}")
            if job_id in _job_statuses:
                _job_statuses[job_id]['status'] = 'failed'
                _job_statuses[job_id]['error'] = f"Invalid domain: {str(e)}"
                _job_statuses[job_id]['completed_at'] = datetime.utcnow().isoformat()
            return

        # Update progress
        if job_id in _job_statuses:
            _job_statuses[job_id]['progress'] = 0.2

        # Use SitemapAnalyzer to discover sitemaps
        logger.info(f"Discovering sitemaps for domain: {clean_domain}")

        # Now leverage the actual SitemapAnalyzer instance
        result = await self.analyzer.analyze_domain_sitemaps(
            domain=clean_domain,
            follow_robots_txt=True,
            extract_urls=True,
            max_urls_per_sitemap=max_pages
        )

        # Process the results
        logger.info(f"Sitemap analysis complete for {clean_domain}")

        # Extract data from the result
        sitemaps = result.get('sitemaps', [])
        total_sitemaps = len(sitemaps)
        total_urls = sum(sitemap.get('url_count', 0) for sitemap in sitemaps)

        # Count discovery methods
        discovery_methods = {}
        for sitemap in sitemaps:
            method = sitemap.get('discovery_method', 'unknown')
            if method in discovery_methods:
                discovery_methods[method] += 1
            else:
                discovery_methods[method] = 1

        # Count sitemap types
        sitemap_types = {}
        for sitemap in sitemaps:
            sitemap_type = sitemap.get('sitemap_type', 'unknown')
            if sitemap_type in sitemap_types:
                sitemap_types[sitemap_type] += 1
            else:
                sitemap_types[sitemap_type] = 1

        # Store data in database if we have a session
        if own_session:
            async with session_ctx as session_obj:
                # Ensure database operations are wrapped in a transaction
                async with session_obj.begin():
                    logger.info(f"Starting database persistence for job {job_id}, domain {clean_domain}")

                    # Check if domain exists in domains table
                    domain_result = await db_service.fetch_one(
                        """
                        SELECT id FROM domains
                        WHERE domain = :domain AND tenant_id = :tenant_id
                        """,
                        {"domain": clean_domain, "tenant_id": tenant_id}
                    )

                    domain_id = None
                    if domain_result:
                        domain_id = domain_result.get('id')
                        logger.debug(f"Found existing domain record with ID: {domain_id}")
                    else:
                        # Create domain
                        logger.debug(f"Creating new domain record for: {clean_domain}")
                        domain_result = await db_service.execute_returning(
                            """
                            INSERT INTO domains (id, domain, tenant_id, created_by)
                            VALUES (gen_random_uuid(), :domain, :tenant_id, :created_by)
                            RETURNING id
                            """,
                            {
                                "domain": clean_domain,
                                "tenant_id": tenant_id,
                                "created_by": user_id
                            }
                        )
                        domain_id = domain_result.get('id')
                        logger.debug(f"Created domain record with ID: {domain_id}")

                    # Store discovered sitemaps in the database
                    sitemap_ids = []
                    for sitemap in sitemaps:
                        sitemap_url = sitemap.get('url', '')
                        sitemap_type = sitemap.get('sitemap_type', 'standard')
                        discovery_method = sitemap.get('discovery_method', 'unknown')
                        url_count = sitemap.get('url_count', 0)
                        sitemap_size = sitemap.get('size_bytes', 0)
                        sitemap_urls = sitemap.get('urls', [])

                        # Check for metadata flags
                        has_lastmod = any(url.get('lastmod') for url in sitemap_urls if url)
                        has_priority = any(url.get('priority') for url in sitemap_urls if url)
                        has_changefreq = any(url.get('changefreq') for url in sitemap_urls if url)

                        # Insert sitemap record
                        try:
                            logger.debug(f"Inserting sitemap: {sitemap_url}, type: {sitemap_type}, discovery: {discovery_method}")
                            result = await db_service.execute_returning(
                                """
                                INSERT INTO sitemap_files (
                                    id, tenant_id, domain_id, url, sitemap_type, discovery_method,
                                    size_bytes, has_lastmod, has_priority, has_changefreq,
                                    status, job_id
                                ) VALUES (
                                    gen_random_uuid(), :tenant_id, :domain_id, :url, :sitemap_type, :discovery_method,
                                    :size_bytes, :has_lastmod, :has_priority, :has_changefreq,
                                    'completed', :job_id
                                ) RETURNING id
                                """,
                                {
                                    "tenant_id": tenant_id,
                                    "domain_id": domain_id,
                                    "url": sitemap_url,
                                    "sitemap_type": sitemap_type,
                                    "discovery_method": discovery_method,
                                    "size_bytes": sitemap_size,
                                    "has_lastmod": has_lastmod,
                                    "has_priority": has_priority,
                                    "has_changefreq": has_changefreq,
                                    "job_id": job_id
                                }
                            )

                            sitemap_id = result.get('id')
                            if sitemap_id:
                                sitemap_ids.append(sitemap_id)
                                logger.debug(f"Inserted sitemap with ID {sitemap_id}")

                                # Insert URLs in batches for better performance
                                if sitemap_urls:
                                    # Process URLs in batches of 100
                                    batch_size = 100
                                    for i in range(0, len(sitemap_urls), batch_size):
                                        batch_urls = sitemap_urls[i:i+batch_size]
                                        url_values = []
                                        url_params = {}

                                        for idx, url_data in enumerate(batch_urls):
                                            if not url_data or not url_data.get('loc'):
                                                continue

                                            prefix = f"url_{idx}"
                                            url_values.append(f"(gen_random_uuid(), :tenant_id, :domain_id, :sitemap_id, :{prefix}_url, :{prefix}_lastmod, :{prefix}_changefreq, :{prefix}_priority_value, 'completed', CURRENT_TIMESTAMP, :created_by)")
                                            url_params[f"{prefix}_url"] = url_data.get('loc')

                                            # Handle datetime conversion for lastmod
                                            lastmod = url_data.get('lastmod')
                                            if lastmod and isinstance(lastmod, str):
                                                try:
                                                    # Attempt to parse the datetime string
                                                    lastmod = datetime.fromisoformat(lastmod.replace('Z', '+00:00'))
                                                except (ValueError, TypeError):
                                                    lastmod = None

                                            url_params[f"{prefix}_lastmod"] = lastmod
                                            url_params[f"{prefix}_changefreq"] = url_data.get('changefreq')

                                            # Convert priority to float
                                            priority = url_data.get('priority')
                                            if priority and isinstance(priority, str):
                                                try:
                                                    priority = float(priority)
                                                except (ValueError, TypeError):
                                                    priority = None

                                            url_params[f"{prefix}_priority_value"] = priority

                                        if url_values:
                                            url_params["tenant_id"] = tenant_id
                                            url_params["domain_id"] = domain_id
                                            url_params["sitemap_id"] = sitemap_id
                                            url_params["created_by"] = user_id

                                            values_clause = ", ".join(url_values)
                                            insert_query = f"""
                                                INSERT INTO sitemap_urls (
                                                    id, tenant_id, domain_id, sitemap_id, url,
                                                    lastmod, changefreq, priority_value, status,
                                                    created_at, created_by
                                                ) VALUES {values_clause}
                                            """

                                            logger.debug(f"Inserting batch of {len(url_values)} URLs for sitemap {sitemap_id}")
                                            await db_service.execute(insert_query, url_params)
                                            logger.debug(f"Successfully inserted URL batch for sitemap {sitemap_id}")

                        except Exception as e:
                            logger.error(f"Error storing sitemap {sitemap_url}: {str(e)}", exc_info=True)
                            # Continue with the next sitemap even if this one fails

                    logger.info(f"Stored {len(sitemap_ids)} sitemaps for domain {clean_domain}")

        # Update job status to complete
        if job_id in _job_statuses:
            _job_statuses[job_id]['status'] = 'complete'
            _job_statuses[job_id]['progress'] = 1.0
            _job_statuses[job_id]['completed_at'] = datetime.utcnow().isoformat()
            _job_statuses[job_id]['total_sitemaps'] = total_sitemaps
            _job_statuses[job_id]['total_urls'] = total_urls
            _job_statuses[job_id]['discovery_methods'] = discovery_methods
            _job_statuses[job_id]['sitemap_types'] = sitemap_types
            _job_statuses[job_id]['sitemaps'] = sitemaps[:10]  # Store just the first 10 for status response

        logger.info(f"Completed background processing for domain: {clean_domain}, job_id: {job_id}")

    except Exception as e:
        logger.error(f"Error processing domain {domain}: {str(e)}", exc_info=True)
        # Update job status to failed
        if job_id in _job_statuses:
            _job_statuses[job_id]['status'] = 'failed'
            _job_statuses[job_id]['error'] = str(e)
            _job_statuses[job_id]['completed_at'] = datetime.utcnow().isoformat()
            _job_statuses[job_id]['progress'] = 0.0

    finally:
        # Close the analyzer session
        await self.analyzer.close_session()

        # If we created our own session, make sure to close it
        if own_session and session_ctx is not None:
            try:
                await session_ctx.close()
            except Exception as e:
                logger.error(f"Error closing session: {str(e)}")
```

## Conclusion

The ContentMap database persistence fix should ensure that sitemap data is properly stored in the database. By following this work order, you will modify the existing implementation to align with the database schema, fix the job ID format, ensure proper foreign key relationships, and add comprehensive logging for diagnostics. The success of the implementation can be verified by running the test script and checking database records.
