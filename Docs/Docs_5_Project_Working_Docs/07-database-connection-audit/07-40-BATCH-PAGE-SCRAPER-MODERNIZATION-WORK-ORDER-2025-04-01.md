# Batch Page Scraper Modernization Work Order - 2025-04-01

## 1. Overview

This work order outlines the necessary changes to modernize the Batch Page Scraper endpoint according to our established architectural principles and standardization framework. Based on the analysis of the existing implementation in `src/routers/batch_page_scraper.py` and its associated frontend in `static/batch-domain-scanner.html`, this document identifies critical issues that need to be addressed and provides a detailed implementation plan.

## 2. Current Issues Identified

After a thorough review of the batch_page_scraper implementation, the following issues have been identified:

### 2.1 Linter Errors

The following linter errors are present in the current implementation:

```
Line 112: Argument of type "Unknown | None" cannot be assigned to parameter "user_id" of type "str" in function "initiate_domain_scan"
Line 117: Argument missing for parameter "session"
Line 195: No parameter named "session"
Line 205: Argument missing for parameter "session"
Line 243: Argument expression after ** must be a mapping with a "str" key type
Line 243: Arguments missing for parameters "batch_id", "status", "total_domains", ... (and more)
```

These errors indicate parameter mismatches, missing parameters, and incorrect assumptions about the structure of returned data.

### 2.2 Transaction Management Issues

1. **Background Task Transaction Violations**: The implementation adds background tasks that call service methods directly without proper session management. This violates our architectural principle that "background tasks must manage their own sessions."

2. **Inconsistent Session Usage**: The `/batch/{batch_id}/status` endpoint doesn't use a session parameter for the `batch_processor_service.get_batch_status` call, but the service likely requires one.

### 2.3 UUID Handling Issues

1. **Non-Standard UUID Generation**: The batch*id is created with a custom format (`batch*{uuid.uuid4().hex[:12]}`) instead of using the standard UUID format as required by our UUID Standardization Guide.

2. **Inconsistent ID Type Handling**: The endpoints don't implement proper UUID validation or flexible handling for different ID formats.

### 2.4 Model Inconsistencies

1. **Custom Model Definitions**: The router defines its own BatchRequest and BatchResponse models instead of using shared models from the imports, creating potential inconsistencies.

2. **Response Model Mismatch**: The BatchStatusResponse doesn't match the expected format from the service, causing the linter to flag missing parameters.

### 2.5 Frontend/Backend Synchronization Issues

1. **Endpoint URL Discrepancies**: The frontend appears to be designed for a specific API structure that doesn't fully align with the current implementation.

2. **Error Handling Discrepancies**: The frontend has sophisticated error handling that expects certain error formats which may not match the actual backend responses.

## 3. Required Changes

### 3.1 Update Model Definitions

1. Standardize model imports:

   - Use the shared model definitions from `..models` instead of defining custom models in the router
   - Update the models to ensure they have all required fields, including `tenant_id`

2. Fix the BatchStatusResponse usage:
   - Ensure the service returns data in the format expected by the model
   - Add proper data validation and transformation before returning the response

### 3.2 Fix Transaction Management

1. Ensure router endpoints properly establish transaction boundaries:

   ```python
   async with session.begin():
       result = await service.method(session=session, ...)
   ```

2. Fix background task implementation:

   ```python
   # Import session factory
   from ..session.async_session import AsyncSessionLocal

   async def background_task_processor(batch_id: str, tenant_id: str, ...):
       # Create own session
       async with AsyncSessionLocal() as session:
           async with session.begin():
               # Do work with proper session management
               await service.process_batch(session=session, ...)
   ```

### 3.3 Implement Proper UUID Handling

1. Use standard UUID format for batch_id:

   ```python
   # Correct UUID generation
   batch_id = str(uuid.uuid4())
   ```

2. Add proper UUID validation for input parameters:
   ```python
   def validate_uuid(id_value: str) -> uuid.UUID:
       try:
           return uuid.uuid4(id_value)
       except ValueError:
           # Handle non-UUID format gracefully
           logger.warning(f"Non-standard UUID format: {id_value}")
           return id_value
   ```

### 3.4 Improve Error Handling

1. Add comprehensive try/except blocks with specific error handling:

   ```python
   try:
       # Operation that might fail
       ...
   except UniqueViolationError as e:
       # Handle specific error
       logger.warning(f"Domain already exists: {str(e)}")
       # Provide user-friendly error response
       raise HTTPException(status_code=409, detail={"message": "Domain already exists", "error": str(e)})
   except ValueError as e:
       logger.error(f"Invalid input: {str(e)}")
       raise HTTPException(status_code=400, detail={"message": "Invalid input", "error": str(e)})
   except Exception as e:
       # Handle unexpected errors
       logger.error(f"Unexpected error: {str(e)}", exc_info=True)
       raise HTTPException(status_code=500, detail={"message": "An unexpected error occurred", "error": str(e)})
   ```

2. Use defensive programming for attribute access:
   ```python
   # Safe attribute access
   result = {
       "batch_id": batch.id,
       "status": batch.status,
       "total_domains": getattr(batch, "total_domains", 0),
       "completed_domains": getattr(batch, "completed_domains", 0),
       # More attributes with safe access
   }
   ```

### 3.5 Update Frontend Integration

1. Update the frontend JS to match the actual API endpoints and response formats
2. Ensure error handling in the frontend matches the backend error response format
3. Add proper tenant_id handling from the frontend to the backend

## 4. Implementation Steps

### 4.1 Fix Pydantic Models

1. Update model imports to use consistent model definitions:

   ```python
   from ..models import (
       SitemapScrapingRequest,
       SitemapScrapingResponse,
       BatchRequest,  # Use shared model instead of custom definition
       BatchResponse,  # Use shared model instead of custom definition
       JobStatusResponse,
       BatchStatusResponse
   )
   ```

2. If necessary, update the shared model definitions to include all required fields:

   ```python
   # In models/__init__.py or appropriate model file
   class BatchRequest(BaseModel):
       domains: List[str] = Field(..., description="List of domains to scan")
       max_pages: int = Field(1000, description="Maximum number of pages to scan per domain")
       max_concurrent_jobs: int = Field(5, description="Maximum number of concurrent jobs")
       tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant isolation")
   ```

### 4.2 Fix Transaction Management

1. Update the `/scan` endpoint to properly handle transactions:

   ```python
   @router.post("/scan", response_model=SitemapScrapingResponse)
   async def scan_domain(
       background_tasks: BackgroundTasks,
       request: Dict[str, Any] = Body(...),
       session: AsyncSession = Depends(get_session_dependency),
       current_user: Dict = Depends(user_dependency),
       db_params: Dict[str, Any] = Depends(get_db_params)
   ) -> SitemapScrapingResponse:
       """Scan a domain to extract metadata from its pages."""
       try:
           # Get required parameters
           base_url = request.get("base_url")
           max_pages = request.get("max_pages", 100)

           if not base_url:
               raise HTTPException(status_code=400, detail="base_url is required")

           logger.info(f"Starting domain scan for {base_url}")

           # Router owns transaction boundary
           async with session.begin():
               # Initiate domain scan within transaction
               result = await page_processing_service.initiate_domain_scan(
                   session=session,
                   base_url=base_url,
                   tenant_id=DEFAULT_TENANT_ID,
                   user_id=str(current_user.get("id", "")),  # Ensure string type
                   max_pages=max_pages
               )

           # Add background task for processing AFTER transaction commits
           # Import the background processing function
           from ..services.page_scraper.processing_service import process_domain_with_own_session

           # Add background task with proper task function that creates its own session
           background_tasks.add_task(
               process_domain_with_own_session,
               job_id=result["job_id"],
               domain=base_url,
               tenant_id=DEFAULT_TENANT_ID,
               user_id=str(current_user.get("id", "")),
               max_pages=max_pages
           )

           # Return job details with status URL
           return SitemapScrapingResponse(
               job_id=result["job_id"],
               status_url=result["status_url"]
           )
       except HTTPException:
           raise
       except Exception as e:
           logger.error(f"Error scanning domain: {str(e)}", exc_info=True)
           raise HTTPException(
               status_code=500,
               detail=f"An error occurred while scanning domain: {str(e)}"
           )
   ```

2. Update the `/batch` endpoint with proper transaction boundaries and background task handling:

   ```python
   @router.post("/batch", response_model=BatchResponse)
   async def create_batch(
       background_tasks: BackgroundTasks,
       request: BatchRequest,
       session: AsyncSession = Depends(get_session_dependency),
       current_user: Dict = Depends(user_dependency),
       db_params: Dict[str, Any] = Depends(get_db_params)
   ) -> BatchResponse:
       """Create a batch of domain scanning jobs."""
       try:
           # Use proper UUID format
           batch_id = str(uuid.uuid4())

           # Router owns transaction boundary
           async with session.begin():
               # Create batch in database with proper session parameter
               batch = await batch_processor_service.create_batch(
                   session=session,
                   batch_id=batch_id,
                   domains=request.domains,
                   tenant_id=DEFAULT_TENANT_ID,
                   user_id=str(current_user.get("id", "")),
                   options={"max_concurrent": request.max_concurrent_jobs}
               )

           # Import the background processor function that creates its own session
           from ..services.batch.batch_processor_service import process_batch_with_own_session

           # Add background task with proper function
           background_tasks.add_task(
               process_batch_with_own_session,
               batch_id=batch_id,
               domains=request.domains,
               tenant_id=DEFAULT_TENANT_ID,
               user_id=str(current_user.get("id", "")),
               max_pages=request.max_pages
           )

           # Return batch details
           return BatchResponse(
               batch_id=batch_id,
               status_url=f"/api/v3/batch_page_scraper/batch/{batch_id}/status",
               job_count=len(request.domains),
               created_at=datetime.utcnow().isoformat()
           )
       except Exception as e:
           logger.error(f"Error creating batch: {str(e)}", exc_info=True)
           raise HTTPException(
               status_code=500,
               detail=f"An error occurred while creating batch: {str(e)}"
           )
   ```

3. Fix the batch status endpoint to use proper session management:

   ```python
   @router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse)
   async def get_batch_status(
       batch_id: str,
       session: AsyncSession = Depends(get_session_dependency),  # Add session parameter
       current_user: Dict = Depends(user_dependency)
   ) -> BatchStatusResponse:
       """Get the status of a batch operation."""
       try:
           # Router owns transaction boundary
           async with session.begin():
               # Get batch status with session parameter
               batch_status = await batch_processor_service.get_batch_status(
                   session=session,  # Pass session to service
                   batch_id=batch_id,
                   tenant_id=current_user.get("tenant_id", DEFAULT_TENANT_ID)
               )

               # Ensure we have all required fields for BatchStatusResponse
               # Use safe attribute access with defaults
               status_data = {
                   "batch_id": batch_id,
                   "status": batch_status.get("status", "unknown"),
                   "total_domains": batch_status.get("total_domains", 0),
                   "completed_domains": batch_status.get("completed_domains", 0),
                   "failed_domains": batch_status.get("failed_domains", 0),
                   "progress": batch_status.get("progress", 0),
                   "created_at": batch_status.get("created_at", datetime.utcnow().isoformat()),
                   "updated_at": batch_status.get("updated_at", datetime.utcnow().isoformat()),
                   "start_time": batch_status.get("start_time"),
                   "end_time": batch_status.get("end_time"),
                   "processing_time": batch_status.get("processing_time", 0),
                   "domain_statuses": batch_status.get("domain_statuses", {}),
                   "error": batch_status.get("error"),
                   "metadata": batch_status.get("metadata", {})
               }

           return BatchStatusResponse(**status_data)
       except Exception as e:
           logger.error(f"Error retrieving batch status: {str(e)}", exc_info=True)
           raise HTTPException(
               status_code=500,
               detail=f"An error occurred while retrieving batch status: {str(e)}"
           )
   ```

### 4.3 Implement Proper UUID Handling

1. Add a UUID validation helper function:

   ```python
   def validate_uuid(id_value: str) -> Any:
       """Handle different ID formats gracefully."""
       if not id_value:
           return None

       if isinstance(id_value, str):
           # If it's already a UUID string, try to convert it
           try:
               return uuid.UUID(id_value)
           except ValueError:
               # Log warning for non-standard format but continue
               logger.warning(f"Non-standard UUID format: {id_value}")
               return id_value

       # If it's already a UUID object or something else, return as is
       return id_value
   ```

2. Use standard UUID format in batch_id generation:

   ```python
   # Generate standard UUID
   batch_id = str(uuid.uuid4())
   ```

3. Apply UUID validation to path parameters:

   ```python
   @router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse)
   async def get_batch_status(
       batch_id: str,
       session: AsyncSession = Depends(get_session_dependency),
       current_user: Dict = Depends(user_dependency)
   ) -> BatchStatusResponse:
       # Validate UUID format
       validated_id = validate_uuid(batch_id)

       # Rest of the function...
   ```

### 4.4 Implement Comprehensive Error Handling

1. Add specific error handling for different scenarios:

   ```python
   try:
       # Operation that might fail
       ...
   except UniqueViolationError as e:
       # Log with appropriate level
       logger.warning(f"Domain already exists: {str(e)}")

       # Return structured error response
       raise HTTPException(
           status_code=409,
           detail={
               "message": "Domain already exists in the database",
               "error": str(e),
               "domain": base_url
           }
       )
   except ValueError as e:
       logger.error(f"Invalid input parameter: {str(e)}")
       raise HTTPException(
           status_code=400,
           detail={
               "message": "Invalid input parameter",
               "error": str(e)
           }
       )
   except Exception as e:
       # Log unexpected errors with full traceback
       logger.error(f"Unexpected error processing request: {str(e)}", exc_info=True)
       raise HTTPException(
           status_code=500,
           detail={
               "message": "An unexpected error occurred processing your request",
               "error": str(e)
           }
       )
   ```

2. Use safe attribute access for all database objects:

   ```python
   # Convert database object to response safely
   response_data = {
       "job_id": getattr(job, "id", None),
       "status": getattr(job, "status", "unknown"),
       "created_at": getattr(job, "created_at", datetime.utcnow().isoformat()),
       # More attributes with safe access
   }
   ```

### 4.5 Create Integration Test Script

1. Create a comprehensive test script at `scripts/testing/test_batch_page_scraper.py`:

   ```python
   """
   Test script for the batch page scraper functionality.

   This script tests:
   1. Single domain scanning
   2. Batch domain scanning
   3. Status checking
   4. Error handling
   """
   import asyncio
   import logging
   import sys
   from typing import List, Dict

   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
       stream=sys.stdout
   )

   logger = logging.getLogger("test_batch_page_scraper")

   # Set up test constants
   TEST_DOMAINS = [
       "example.com",
       "example.org",
       "example.net"
   ]
   TEST_AUTH_TOKEN = "scraper_sky_2024"
   TEST_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"
   BASE_URL = "http://localhost:8000"

   async def test_single_domain_scan():
       """Test scanning a single domain."""
       # Test implementation...

   async def test_batch_domain_scan():
       """Test scanning multiple domains in a batch."""
       # Test implementation...

   async def test_status_checking():
       """Test checking the status of jobs and batches."""
       # Test implementation...

   async def test_error_handling():
       """Test handling of various error conditions."""
       # Test implementation...

   async def main():
       """Run all tests in sequence."""
       logger.info("Starting batch page scraper tests")

       try:
           await test_single_domain_scan()
           await test_batch_domain_scan()
           await test_status_checking()
           await test_error_handling()
           logger.info("All tests completed successfully!")
       except Exception as e:
           logger.error(f"Test failed: {str(e)}", exc_info=True)
           sys.exit(1)

   if __name__ == "__main__":
       asyncio.run(main())
   ```

## 5. Frontend Updates

The frontend (`static/batch-domain-scanner.html`) has several sophisticated features, but needs to be updated to match the backend implementation:

1. Update the API endpoints in the frontend JS:

   - Ensure all endpoints match the actual backend URLs
   - Make sure parameter names match expected backend parameters

2. Fix error handling to match backend error format:

   - Update error extraction logic to match the structured error responses
   - Handle different error types appropriately

3. Add proper tenant_id handling:
   - Ensure tenant_id is included in all requests
   - Validate tenant_id before submission

## 6. Verification Steps

After implementing these changes, verify the correct functionality by:

1. **Linter Verification**: Run the linter to confirm no more errors related to the batch page scraper.

2. **API Testing**: Use curl to test the APIs:

   ```bash
   # Test single domain scan
   curl -v http://localhost:8000/api/v3/batch_page_scraper/scan -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer scraper_sky_2024" \
     -d '{"base_url": "https://www.example.com", "max_pages": 10}'

   # Test batch scan
   curl -v http://localhost:8000/api/v3/batch_page_scraper/batch -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer scraper_sky_2024" \
     -d '{"domains": ["https://www.example.com", "https://www.example.org"], "max_pages": 10, "max_concurrent_jobs": 2}'
   ```

3. **Test Script**: Run the test script to verify full functionality:

   ```bash
   python scripts/testing/test_batch_page_scraper.py
   ```

4. **Frontend Verification**: Test the frontend by:
   - Adding domains in the textarea
   - Uploading CSV files with domains
   - Checking status updates work correctly
   - Verifying error handling displays properly

## 7. Implementation Timeline

1. **Model Updates**: 2 hours
2. **Transaction Management Fixes**: 4 hours
3. **UUID Handling Improvements**: 2 hours
4. **Error Handling Enhancements**: 3 hours
5. **Frontend Updates**: 3 hours
6. **Test Script Creation**: 4 hours
7. **Testing and Verification**: 4 hours

Total: 22 hours (approximately 3 days of work)

## 8. Reference Materials

- [07-39-Endpoint Modernization Work Order - 2025-03-27.md](/project-docs/07-database-connection-audit/07-39-Endpoint%20Modernization%20Work%20Order%20-%202025-03-27.md) - Framework for endpoint modernization
- [07-37-MODERNIZED-PAGE-SCRAPER-FIX-IMPLEMENTATION-2025-03-27.md](/project-docs/07-database-connection-audit/07-37-MODERNIZED-PAGE-SCRAPER-FIX-IMPLEMENTATION-2025-03-27.md) - Reference implementation
- [07-38-Modernized Page Scraper Fix Implementation Addendum](/project-docs/07-database-connection-audit/07-38-Modernized%20Page%20Scraper%20Fix%20Implementation%20Addendum%20-%202025-03-27.md) - Critical lessons
- [13-TRANSACTION_MANAGEMENT_GUIDE.md](/AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md) - Transaction management principles
- [16-UUID_STANDARDIZATION_GUIDE.md](/AI_GUIDES/16-UUID_STANDARDIZATION_GUIDE.md) - UUID handling guidelines
