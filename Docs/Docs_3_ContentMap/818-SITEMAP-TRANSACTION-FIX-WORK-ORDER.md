# ContentMap Service Transaction Management Fix: Work Order

## 1. Issue Summary

We have identified critical transaction management issues in the ContentMap service, specifically in the sitemap processing functionality. The primary symptom is the error:

> "Can't operate on closed transaction inside context manager. Please complete the context manager before emitting further commands."

This occurs when the service attempts to persist sitemap data to the database. The issue stems from improper transaction boundary management, violating our core principle that "Routers own transaction boundaries, services are transaction-aware but do not create transactions."

## 2. Required Changes

### 2.1 Fix Session/Transaction Management in Background Processing

The primary issue is in the `processing_service.py` file, where database operations in the background processing task are not properly isolated with correct transaction boundaries. Following our established transaction management pattern (as documented in `16-TRANSACTION-MANAGEMENT-COMPREHENSIVE-GUIDE.md`), we need to implement the following changes:

1. **In `processing_service.py`**:
   - Modify the background task database persistence code to follow proper transaction isolation
   - Ensure that when errors occur in one sitemap, they don't affect the entire transaction
   - Add proper session handling with dedicated error recovery session

### 2.2 Fix Background Database Operations

The background sitemap processing operations need to:

- Create a new dedicated session for background operations
- Use proper transaction boundaries with `async with session.begin()`
- Implement proper error handling with transaction awareness
- Avoid nested transactions

### 2.3 Add Transaction State Logging

Add transaction state debugging to help diagnose issues:

- Log transaction state at key points using `session.in_transaction()`
- Add detailed error logging to trace transaction failures
- Include transaction operation context in log messages

## 3. Implementation Steps

1. **Update Background Task Database Operations**:

   ```python
   # Create a standalone background processor function
   async def process_domain_with_own_session(job_id: str, domain: str, tenant_id: str, max_urls: int = 100):
       """Process domain with its own dedicated session for background task reliability"""
       from src.db.session import get_session

       logger.info(f"Starting dedicated background processing for domain: {domain}, job_id: {job_id}")

       # Create new dedicated session for background task
       async with get_session() as background_session:
           try:
               # Start explicit transaction
               async with background_session.begin():
                   logger.debug(f"Started transaction for job {job_id}")

                   # Process sitemaps and persist data
                   await _process_domain(
                       session=background_session,
                       domain=domain,
                       tenant_id=tenant_id,
                       job_id=job_id,
                       max_urls=max_urls
                   )

                   logger.info(f"Successfully completed transaction for job {job_id}")

           except Exception as e:
               logger.error(f"Error in background processing for domain {domain}: {str(e)}")

               # Error recovery with separate session
               try:
                   async with get_session() as error_session:
                       async with error_session.begin():
                           # Update job status to failed
                           await _update_job_failure(
                               session=error_session,
                               job_id=job_id,
                               error_message=f"Error discovering sitemaps for {domain}: {str(e)}"
                           )
               except Exception as inner_e:
                   logger.error(f"Failed to update job status: {str(inner_e)}")
   ```

2. **Update Domain Processing Method**:

   ```python
   async def _process_domain(session: AsyncSession, domain: str, tenant_id: str, job_id: str, max_urls: int = 100):
       """Process domain and store sitemaps in database. This method is transaction-aware."""
       # Log transaction state
       in_transaction = session.in_transaction()
       logger.debug(f"Transaction state in _process_domain: {in_transaction}")

       try:
           # Domain processing logic here
           # ...

           # Store discovered sitemaps using SQLAlchemy ORM
           # ...

       except Exception as e:
           logger.error(f"Error processing domain {domain}: {str(e)}")
           # Propagate exception for proper transaction handling
           raise
   ```

3. **Update Router Method**:

   ```python
   @router.post("/scan", response_model=SitemapScrapingResponse)
   async def scan_domain(
       background_tasks: BackgroundTasks,
       request: SitemapScanRequest = Body(...),
       session: AsyncSession = Depends(get_db_session),
       # Other dependencies...
   ):
       # Create job record within transaction
       async with session.begin():
           # Create job record using job_service
           job_id = f"sitemap_{uuid.uuid4().hex[:32]}"

           # Create job via service
           job = await job_service.create_job(
               session=session,
               job_type="sitemap_scan",
               status="pending",
               job_id=job_id,
               tenant_id=request.tenant_id
           )

       # Add background task AFTER transaction is committed
       background_tasks.add_task(
           process_domain_with_own_session,
           job_id=job_id,
           domain=request.base_url,
           tenant_id=request.tenant_id,
           max_urls=request.max_pages
       )

       # Return response immediately
       return SitemapScrapingResponse(
           job_id=job_id,
           status_url=f"/api/v3/sitemap/status/{job_id}"
       )
   ```

## 4. Testing Strategy

1. **API Testing**:

   - Test `/api/v3/sitemap/scan` endpoint with a domain having sitemaps
   - Test `/api/v3/sitemap/status/{job_id}` to verify job completion
   - Verify error handling with invalid domains

2. **Database Verification**:

   - Check `sitemap_files` table for new records
   - Verify `job` table records show proper status
   - Check domain updates in `domains` table

3. **Error Recovery Testing**:
   - Test with domains that will cause processing errors
   - Verify job status is updated correctly on failure
   - Check error messages are properly recorded

## 5. Acceptance Criteria

1. No "Can't operate on closed transaction inside context manager" errors
2. Successful persistence of sitemap data to database
3. Proper job status updates in both success and failure cases
4. Transaction boundaries follow the standard pattern
5. No nested transactions
6. Background tasks use dedicated sessions
7. Detailed logging of transaction states and errors

## 6. Implementation Timeline

1. Transaction management fix implementation: 2 hours
2. Testing and verification: 1 hour
3. Documentation of changes: 30 minutes

**Total Estimated Time**: 3.5 hours
