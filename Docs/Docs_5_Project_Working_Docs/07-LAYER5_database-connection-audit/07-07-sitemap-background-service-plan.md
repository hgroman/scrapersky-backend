---
title: Sitemap Background Service Implementation Plan
date: 2025-03-26
author: System
status: Proposed
priority: High
---

# Sitemap Background Service Implementation Plan

## 1. Overview

This document outlines the plan to implement a dedicated background service for sitemap processing that follows the architectural patterns demonstrated in the Google Maps API reference implementation. The goal is to resolve current issues with sitemap functionality while ensuring compliance with database connection standards.

## 2. Current Issues

From debugging the sitemap flow, we've identified these issues:

1. Database schema mismatch error: Column `url_count` does not exist in the `sitemap_files` table
2. Improper session management in background tasks
3. Transaction management issues leading to `PendingRollbackError`
4. Lack of proper error handling for background tasks

## 3. Reference Implementation Analysis

The Google Maps API implementation (`/src/routers/google_maps_api.py`) demonstrates these key patterns:

1. **Background Task Pattern**:

   - Dedicated background function (`process_places_search_background`)
   - Creates a NEW session using `get_session()`
   - Proper transaction boundaries with `async with bg_session.begin()`
   - Comprehensive error handling and status tracking

2. **Database Connection Management**:
   - Dependency injection in endpoints
   - Explicit transaction boundaries
   - No session sharing between API endpoints and background tasks

## 4. Implementation Plan

### 4.1 Service Location

We will enhance the existing sitemap services by placing the new background service implementation in:

```
/src/services/sitemap/background_service.py
```

This follows the logical structure already established in the project, while maintaining separation of concerns.

### 4.2 Database Schema Fix

1. Verify and update the sitemap_files table schema to include the missing `url_count` column:

   ```sql
   ALTER TABLE sitemap_files ADD COLUMN url_count INTEGER DEFAULT 0;
   ```

2. Update any related database models to reflect this change.

### 4.3 Background Service Implementation

1. Create `background_service.py` with these core functions:

   ```python
   """
   Sitemap Background Service

   Handles asynchronous processing of sitemap scanning operations following
   the architectural patterns from the Google Maps API reference implementation.
   """
   import logging
   import uuid
   from datetime import datetime
   from typing import Dict, Any

   from sqlalchemy.ext.asyncio import AsyncSession

   from ...session.async_session import get_session
   from ...scraper.sitemap_analyzer import SitemapAnalyzer
   from ..job_service import job_service

   logger = logging.getLogger(__name__)

   async def process_domain_background(args: Dict[str, Any]):
       """
       Background task to process domain sitemap scanning.
       Following the Google Maps API pattern for proper session handling.
       """
       job_id = args.get("job_id")
       domain = args.get("domain")
       user_id = args.get("user_id", "system")

       try:
           # Create a new session specifically for this background task
           async with get_session() as bg_session:
               try:
                   # Update job status to processing
                   async with bg_session.begin():
                       await job_service.update_status(
                           session=bg_session,
                           job_id=job_id,
                           status="processing",
                           progress=0.1
                       )

                   # Initialize analyzer with current session
                   analyzer = SitemapAnalyzer()

                   # Process the domain in a transaction
                   async with bg_session.begin():
                       result = await analyzer.scan_domain(
                           session=bg_session,
                           domain=domain,
                           job_id=job_id,
                           user_id=user_id
                       )

                       # Update job with successful completion
                       await job_service.update_status(
                           session=bg_session,
                           job_id=job_id,
                           status="completed",
                           progress=1.0,
                           metadata={
                               "sitemap_count": result.get("sitemap_count", 0),
                               "url_count": result.get("url_count", 0)
                           }
                       )

                       logger.info(f"Completed sitemap scan for {domain}, job_id: {job_id}")
                       return result

               except Exception as e:
                   logger.error(f"Error processing domain {domain} (job_id: {job_id}): {str(e)}")

                   # Update job status to failed in a new transaction
                   try:
                       async with bg_session.begin():
                           await job_service.update_status(
                               session=bg_session,
                               job_id=job_id,
                               status="failed",
                               progress=0.5,  # Indicate partial progress
                               error_message=str(e)
                           )
                   except Exception as update_error:
                       logger.critical(f"Failed to update job status after error: {str(update_error)}")

                   # Re-raise for caller to handle
                   raise
       except Exception as e:
           logger.error(f"Critical error in background process: {str(e)}")
           # Ensure error is logged but doesn't crash the application


   async def process_batch_background(args: Dict[str, Any]):
       """
       Background task to process batch sitemap scanning operations.
       Following the Google Maps API pattern for proper session handling.
       """
       job_id = args.get("job_id")
       domains = args.get("domains", [])
       user_id = args.get("user_id", "system")

       try:
           # Create a new session specifically for this background task
           async with get_session() as bg_session:
               try:
                   # Update job status to processing
                   async with bg_session.begin():
                       await job_service.update_status(
                           session=bg_session,
                           job_id=job_id,
                           status="processing",
                           progress=0.1
                       )

                   # Process domains in batches
                   total_domains = len(domains)
                   processed = 0
                   results = []

                   for domain in domains:
                       try:
                           # Process each domain in its own transaction
                           async with bg_session.begin():
                               analyzer = SitemapAnalyzer()
                               result = await analyzer.scan_domain(
                                   session=bg_session,
                                   domain=domain,
                                   job_id=job_id,
                                   user_id=user_id
                               )
                               results.append(result)

                           # Update progress after each domain
                           processed += 1
                           progress = processed / total_domains
                           async with bg_session.begin():
                               await job_service.update_status(
                                   session=bg_session,
                                   job_id=job_id,
                                   status="processing",
                                   progress=progress
                               )

                       except Exception as domain_error:
                           logger.error(f"Error processing domain {domain}: {str(domain_error)}")
                           # Continue with next domain instead of failing entire batch

                   # Update job with completion status
                   async with bg_session.begin():
                       await job_service.update_status(
                           session=bg_session,
                           job_id=job_id,
                           status="completed",
                           progress=1.0,
                           metadata={
                               "total_domains": total_domains,
                               "successful_domains": len(results),
                               "failed_domains": total_domains - len(results)
                           }
                       )

                   logger.info(f"Completed batch processing, job_id: {job_id}")
                   return results

               except Exception as e:
                   logger.error(f"Error in batch processing (job_id: {job_id}): {str(e)}")

                   # Update job status to failed
                   try:
                       async with bg_session.begin():
                           await job_service.update_status(
                               session=bg_session,
                               job_id=job_id,
                               status="failed",
                               progress=processed / total_domains if total_domains > 0 else 0,
                               error_message=str(e)
                           )
                   except Exception as update_error:
                       logger.critical(f"Failed to update job status after error: {str(update_error)}")

                   # Re-raise for caller to handle
                   raise
       except Exception as e:
           logger.error(f"Critical error in background batch process: {str(e)}")
           # Ensure error is logged but doesn't crash the application
   ```

### 4.4 Router Updates

Modify the router endpoints to use the new background service:

1. Update `/src/routers/modernized_sitemap.py` to use the new background service:

   ```python
   from ..services.sitemap.background_service import process_domain_background, process_batch_background

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

           # Start background task with proper arguments
           # DO NOT pass the session to the background task
           background_tasks.add_task(
               process_domain_background,
               {
                   "job_id": job_id,
                   "domain": request.domain,
                   "user_id": current_user.get("id")
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

### 4.5 Analyzer Update

Update the SitemapAnalyzer to handle the proper database operations:

1. Modify `/src/scraper/sitemap_analyzer.py` to ensure it works with the provided session and handles transactions properly:

   ```python
   # Update scan_domain method to use the provided session
   async def scan_domain(self, session: AsyncSession, domain: str, job_id: str, user_id: str):
       # Process domain using the provided session
       # Don't create new transactions here - the background service manages transactions
       # ...
   ```

## 5. Testing Plan

1. **Unit Tests**:

   - Test background service functions with mocked session and dependencies
   - Verify transaction boundaries and error handling

2. **Integration Tests**:

   - Test end-to-end flow of sitemap scanning
   - Verify job status updates correctly
   - Test error conditions and recovery

3. **Manual Testing**:
   - Run the `debug_sitemap_flow.py` script to verify fixes
   - Test with multiple simultaneous scans to ensure concurrency handling

## 6. Rollout Plan

1. Implement database schema changes
2. Implement background service according to this plan
3. Update affected router endpoints
4. Run comprehensive tests
5. Deploy changes to staging
6. Verify functionality with debug scripts
7. Update documentation to reflect the new implementation
8. Deploy to production

## 7. Success Criteria

1. No `ProgrammingError` or `PendingRollbackError` when running sitemap operations
2. Successful job status tracking throughout the process
3. Clear error handling that allows diagnostics without breaking the application
4. Compliance with database connection standards as defined in the audit
