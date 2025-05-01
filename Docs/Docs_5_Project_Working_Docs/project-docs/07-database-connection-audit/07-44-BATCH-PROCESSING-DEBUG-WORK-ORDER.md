# BATCH PROCESSING DEBUG WORK ORDER

**Document ID:** 07-44-BATCH-PROCESSING-DEBUG-WORK-ORDER
**Date:** 2025-03-27
**Status:** Handover
**Priority:** Critical

## 1. Issue Summary

The batch-domain-scanner.html interface has been updated to use the batch processing API endpoints, but the background task processing is not functioning correctly. Batches are created in the database with "pending" status but never transition to "running" or "completed" status, suggesting the background task execution is failing silently.

## 2. Current Implementation Status

### 2.1 Completed Changes

1. Modified `batch-domain-scanner.html` to:

   - Use `/api/v3/batch_page_scraper/batch` endpoint for batch creation
   - Poll `/api/v3/batch_page_scraper/batch/{batch_id}/status` for status updates
   - Add detailed results viewing interface similar to single-domain-scanner

2. Added extensive debugging to `process_batch_with_own_session` function in `batch_processor_service.py`:

   - Print statements at critical points (session creation, imports, etc.)
   - Exception handling with detailed output
   - Alternate import paths for potential circular dependency issues

3. Added debug prints in `batch_page_scraper.py` router to track background task registration

### 2.2 Identified Issues

1. **Background Task Execution**: The background task `process_batch_with_own_session` is added to FastAPI's background tasks but shows no evidence of executing. No debug logs appear, suggesting the task is never run or fails silently before first log statement.

2. **Database State**: Batches are created with "pending" status but never progress, confirming background tasks aren't running successfully.

3. **Import Errors**: Linter errors indicate potential circular dependency issues with imports in batch_processor_service.py, which could prevent background tasks from running correctly.

4. **Missing End-to-End Testing**: No comprehensive end-to-end test script was created to validate all steps of the batch processing workflow.

## 3. Attempted Solutions

1. Added debug print statements in router's batch creation endpoint to verify background task is being added
2. Added extensive debug logging in `process_batch_with_own_session` function
3. Modified import statements in background task to handle potential circular dependencies
4. Tried to execute background tasks with various batch configurations (different domain counts, etc.)
5. Checked for error logs in docker container output

## 4. Technical Investigation

### 4.1 Background Task Registration

The FastAPI endpoint in `batch_page_scraper.py` adds a background task:

```python
background_tasks.add_task(
    process_batch_with_own_session,
    batch_id=batch_id,
    domains=request.domains,
    tenant_id=tenant_id,
    user_id=user_id,
    max_pages=request.max_pages
)
```

Debug prints confirm this code executes, but no evidence the task ever runs.

### 4.2 Background Task Internal Execution

The `process_batch_with_own_session` function has circular dependency handling:

```python
# We delay imports until runtime to avoid circular imports and linter errors
try:
    # At runtime, import the session factory
    import importlib
    async_session_module = importlib.import_module("...session.async_session", package=__package__)
    AsyncSessionLocal = getattr(async_session_module, "AsyncSessionLocal")
    # ...
```

But since debug logs don't appear, execution likely fails before this point or the task is never scheduled.

### 4.3 Database Structure

BatchJob model requires the following fields:

- batch_id (UUID)
- tenant_id (UUID)
- created_by (UUID)
- processor_type (str)
- status (str)
- total_domains (int)
- etc.

Create_batch function ensures proper creation, but batch status never updates beyond "pending".

## 5. Next Steps Recommendation

1. **Fix Background Task Execution**:

   - Investigate FastAPI background task execution mechanism
   - Confirm if tasks are being lost/dropped during server restarts
   - Consider implementing a dedicated task queue (Celery, Redis, etc.)

2. **Database Session Management**:

   - Verify session factory is correctly imported in background tasks
   - Check if database connection pool is properly configured for async tasks
   - Ensure transaction isolation level is appropriate

3. **End-to-End Testing**:

   - Create a standalone script that tests the entire workflow
   - Track database state changes during execution
   - Add detailed logging at each step

4. **User Interface Improvement**:

   - Add better error reporting in batch-domain-scanner.html
   - Show detailed diagnostic information on failure

5. **Alternative Approach**:
   - If background tasks continue to fail, consider direct synchronous processing for small batches
   - Implement a polling mechanism to check for pending batches and process them

## 6. Debug Data

### Current Output from Batch Creation:

```json
{
  "batch_id": "282348a7-ac5b-41c2-a279-9eea14a17bcc",
  "status_url": "/api/v3/batch_page_scraper/batch/282348a7-ac5b-41c2-a279-9eea14a17bcc/status",
  "job_count": 1,
  "created_at": "2025-03-27T18:23:11.397631"
}
```

### Current Output from Batch Status:

```json
{
  "batch_id": "282348a7-ac5b-41c2-a279-9eea14a17bcc",
  "status": "pending",
  "total_domains": 1,
  "completed_domains": 0,
  "failed_domains": 0,
  "progress": 0.0,
  "created_at": "2025-03-27T18:23:11.250585",
  "updated_at": "2025-03-27T18:23:11.250585",
  "start_time": null,
  "end_time": null,
  "processing_time": null,
  "domain_statuses": {},
  "error": null,
  "metadata": {
    "domain_count": 1
  }
}
```

## 7. Resources

1. Source code: `/src/services/batch/batch_processor_service.py`
2. Router: `/src/routers/batch_page_scraper.py`
3. HTML interface: `/static/batch-domain-scanner.html`
4. Previous work order: `07-43-BATCH-DOMAIN-SCANNER-HTML-INTEGRATION-WORK-ORDER.md`

## 8. Final Notes

The HTML interface changes are functional in terms of submitting batch requests and displaying results, but the underlying background task processing is broken. The most critical issue is determining why FastAPI background tasks are not executing as expected. This may require deeper investigation into FastAPI's background task implementation or consideration of alternative task processing approaches.
