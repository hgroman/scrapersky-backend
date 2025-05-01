---
title: Sitemap Services Implementation Details
date: 2025-03-26
author: System
status: Handoff Documentation
priority: High
---

# Sitemap Services Implementation Details

## 1. Overview

This document provides comprehensive implementation details for the restructured sitemap services, which have been redesigned to align with our reference architectural patterns from the Google Maps API implementation. The restructuring aims to fix database connection issues and standardize the approach to background processing tasks.

## 2. Directory Structure and Files

The sitemap-related code has been organized under `/src/services/sitemap/` with the following structure:

```
/src/
  └── services/
      └── sitemap/
          ├── analyzer_service.py      # Handles sitemap discovery and parsing
          ├── background_service.py    # Manages asynchronous processing
          └── processing_service.py    # (Existing service, to be replaced)
```

### Implemented Changes

1. **Moved the Sitemap Analyzer**:

   - Created `analyzer_service.py` based on the original `sitemap_analyzer.py`
   - Updated imports to match the new location
   - Added proper type definitions and class implementations

2. **Created Background Service**:

   - Implemented `background_service.py` following the Google Maps API pattern
   - Implemented proper session management, transaction boundaries, and error handling
   - Created separate functions for domain scanning and batch operations

3. **Identified Existing Processing Service**:
   - Discovered that `processing_service.py` already existed in the sitemap folder
   - Found non-compliant usage of sessions in the existing code

## 3. Service Components Explained

### 3.1 Analyzer Service (`analyzer_service.py`)

The analyzer service is responsible for discovering and parsing sitemaps from websites. It performs:

1. **Sitemap Discovery**: Multiple methods to find sitemaps

   - Robots.txt checking
   - Common locations checking
   - HTML page analysis

2. **Sitemap Parsing**: Extracts data from XML sitemaps

   - Handles different sitemap types (standard, index, image, news, video)
   - Supports gzipped sitemaps
   - Extracts metadata like lastmod, priority, changefreq

3. **Content Analysis**: Identifies and categorizes discovered URLs
   - Categorizes by page type (product, category, post, etc.)
   - Collects metadata and statistics

This service follows a stateless pattern, with clear method contracts and comprehensive error handling.

### 3.2 Background Service (`background_service.py`)

The background service implements proper asynchronous task processing following the Google Maps API reference patterns:

1. **Session Management**:

   - Creates a dedicated session for background tasks using `get_session()`
   - Follows the critical pattern of NOT sharing sessions between API endpoints and background tasks

2. **Transaction Management**:

   - Uses explicit transaction boundaries with `async with session.begin()`
   - Separates job status updates and domain processing into distinct transactions
   - Handles nested transactions properly

3. **Error Handling**:

   - Implements comprehensive try/except patterns at multiple levels
   - Updates job status on errors
   - Prevents application crashes while ensuring errors are logged

4. **Job Status Tracking**:
   - Updates job status throughout the process
   - Stores detailed metadata about the operation
   - Provides progress indicators

Key functions:

- `process_domain_background`: Processes a single domain's sitemaps
- `process_batch_background`: Processes multiple domains in batches
- `store_domain_data`: Helper function that encapsulates database operations

## 4. Implementation Methodology

### 4.1 Database Connection Pattern Compliance

The implementation strictly follows the database connection patterns identified in the Google Maps API reference:

1. **Separate Session for Background Tasks**:

   ```python
   async with get_session() as bg_session:
       # Background task operations
   ```

2. **Explicit Transaction Boundaries**:

   ```python
   async with bg_session.begin():
       # Transaction operations
   ```

3. **No Session Sharing Between API and Background Tasks**:

   - Router endpoints use dependency-injected sessions
   - Background tasks create their own sessions

4. **Error Handling Within Transaction Context**:
   ```python
   try:
       async with bg_session.begin():
           # Operations
   except Exception as e:
       # Error handling
   ```

### 4.2 FastAPI Integration

The implementation leverages FastAPI's error handling mechanisms:

1. **HTTP Exceptions**:

   - Uses FastAPI's `HTTPException` for client-facing errors
   - Includes appropriate status codes and detailed messages

2. **Background Tasks**:

   - Integrates with FastAPI's `BackgroundTasks` for asynchronous processing
   - Ensures proper execution of background operations

3. **Dependency Injection**:
   - Prepared for integration with FastAPI's dependency injection system
   - Designed to work with the `get_session_dependency` function

## 5. Linter Errors and Fixes Required

The current implementation has several linter errors that need to be addressed:

### 5.1 Type Checking Issues

1. **Non-Optional Parameters Handling**:

   - Parameters like `job_id` and `domain` need validation to ensure they're not `None`
   - Type annotations should be updated to be more precise

2. **Method Parameter Mismatches**:

   - `job_service.update_status()` appears to be missing `metadata` and `error_message` parameters
   - Either the method signature needs updating, or the calls need adjustment

3. **String Concatenation Type Issues**:
   - Type checking for string concatenation with potentially `None` values
   - Need proper null-checking before operations

### 5.2 Fix Approach

For each category of linter error:

1. **For None Checking**:

   ```python
   if domain is None:
       raise ValueError("Domain cannot be None")
   ```

2. **For Method Parameters**:

   - Check the actual implementation of `job_service.update_status()`
   - Use `**kwargs` if needed for flexibility:

   ```python
   await job_service.update_status(
       session=bg_session,
       job_id=job_id,
       status="failed",
       **{"error_message": str(e)}  # Use kwargs if uncertain
   )
   ```

3. **For Type Casting**:
   ```python
   domain = str(domain) if domain is not None else "default-domain.com"
   ```

## 6. Router Update Requirements

The router needs updating to use the new services. Here's what needs to be changed:

### 6.1 Import Changes

```python
# From:
from ..services.sitemap_service import SitemapService
from ..scraper.sitemap_analyzer import SitemapAnalyzer

# To:
from ..services.sitemap.sitemap_service import SitemapService
from ..services.sitemap.analyzer_service import SitemapAnalyzer
from ..services.sitemap.background_service import process_domain_background, process_batch_background
```

### 6.2 Endpoint Modifications

The `/scan` endpoint needs updating to use the background service:

```python
@router.post("/scan", response_model=Dict)
async def scan_domain(
    request: DomainScanRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    # Generate job ID
    job_id = str(uuid.uuid4())

    try:
        # Create job record with pending status
        async with session.begin():
            job = await job_service.create(
                session=session,
                job_type="sitemap_scan",
                status="pending",
                job_id=job_id,
                metadata={
                    "domain": request.domain,
                    "user_id": current_user.get("id")
                }
            )

        # Add background task with proper arguments
        background_tasks.add_task(
            process_domain_background,
            {
                "job_id": job_id,
                "domain": request.domain,
                "user_id": current_user.get("id"),
                "max_urls": request.max_pages
            }
        )

        # Return immediate response with job ID
        return {
            "job_id": job_id,
            "status": "pending",
            "status_url": f"/api/v3/sitemap/status/{job_id}"
        }
    except Exception as e:
        logger.error(f"Error initiating domain scan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initiating scan: {str(e)}")
```

## 7. Testing the Implementation

### 7.1 Test Steps

1. **Fix Linter Errors**:

   - Address all type checking issues
   - Verify method signatures match their implementations

2. **Update Router**:

   - Modify `modernized_sitemap.py` to use the new background service
   - Ensure proper dependency injection and error handling

3. **Run Debug Script**:

   - Execute `project-docs/07-database-connection-audit/scripts/debug_sitemap_flow.py`
   - Verify that it can successfully process sitemaps

4. **Test With Example Domain**:
   - Test with https://www.soulfullcup.com/
   - Verify that sitemaps are discovered and processed correctly

### 7.2 Debugging Tips

1. **Session Issues**:

   - If database errors occur, check session handling
   - Verify no sessions are shared between contexts

2. **Transaction Issues**:

   - Look for `PendingRollbackError` which indicates transaction problems
   - Ensure proper `async with session.begin()` usage

3. **Model Mismatches**:
   - Check if database schema matches model definitions
   - Pay special attention to the `url_count` column in `sitemap_files`

## 8. Conclusion and Next Steps

### 8.1 Completed Items

1. ✅ Created directory structure for standardized services
2. ✅ Moved analyzer service to proper location
3. ✅ Implemented background service following Google Maps API patterns
4. ✅ Documented implementation details and methodologies

### 8.2 Remaining Tasks

1. ⏳ Fix linter errors in background service
2. ⏳ Update router to use new background service
3. ⏳ Execute debug script to verify functionality
4. ⏳ Test with example domain (www.soulfullcup.com)
5. ⏳ Clean up old files after verification

### 8.3 Success Criteria

The implementation will be successful when:

1. The debug script `debug_sitemap_flow.py` runs without errors
2. The system can successfully scan and process sitemaps from www.soulfullcup.com
3. The database records are properly created and updated
4. All operations follow proper database connection patterns
5. No `ProgrammingError` or `PendingRollbackError` exceptions occur

By following this implementation, the sitemap functionality will align with the established architectural patterns and ensure database connection compliance according to the audit requirements.
