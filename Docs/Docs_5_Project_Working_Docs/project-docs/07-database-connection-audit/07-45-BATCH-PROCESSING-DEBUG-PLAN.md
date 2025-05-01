# BATCH PROCESSING DEBUG PLAN

**Document ID:** 07-51-BATCH-PROCESSING-DEBUG-PLAN
**Date:** 2025-03-28
**Status:** Active
**Priority:** Critical
**Related Document:** 07-44-BATCH-PROCESSING-DEBUG-WORK-ORDER

## 1. Issue Summary

The batch processing API allows creation of batch jobs but background tasks are not executing properly. Batches are created with "pending" status but never transition to "running" or "completed" status. Evidence suggests the `process_batch_with_own_session` background task is not executing or fails silently before logging.

## 2. Diagnostic Approach

Our investigation will follow a systematic approach with increasing levels of instrumentation:

1. **Minimal Verification** - Simple logging to confirm task execution
2. **Progressive Instrumentation** - Step-by-step logging to identify failure points
3. **Architectural Compliance** - Verification against standard patterns
4. **Alternative Implementation** - Fallback approach if needed

## 3. Step-by-Step Debugging Plan

### Phase 1: Basic Execution Verification

1. **Task Registration Validation**

   - Add instrumentation to confirm background task is added to queue
   - Implement request ID tracing through logging to track specific requests
   - Add counters for background task registration

2. **Initial Execution Verification**
   - Add simple synchronous database update immediately before background task to verify write capability
   - Insert ultra-minimal logging as first statement in background task function
   - Create marker file on disk as fallback trace mechanism

### Phase 2: Dependency Execution Tracing

3. **Import Path Verification**

   - Create simplified test module without business logic to test execution
   - Refactor imports to eliminate potential circular dependencies
   - Implement staged imports with detailed logging

4. **Session Creation Verification**
   - Extract session creation logic outside the try/except block
   - Add detailed connection pool monitoring instrumentation
   - Verify database credentials and connection string

### Phase 3: Architectural Pattern Verification

5. **Transaction Boundary Verification**

   - Verify router owns transactions per standard pattern
   - Confirm background task manages its own transaction properly
   - Test transaction isolation level impact

6. **Background Task Implementation Comparison**
   - Compare implementation against Google Maps API exemplar
   - Verify compliance with core architectural principles
   - Test with verified working background task pattern

### Phase 4: Alternative Implementation Strategy

7. **Simple Polling Mechanism**

   - Implement simple API polling for pending batches
   - Create minimal standalone task processor outside FastAPI
   - Verify functionality with simplified implementation

8. **Task Queue Integration**
   - Prepare Redis or Celery implementation if needed
   - Design proper task queue pattern following architectural standards
   - Create migration plan to dedicated task processing

## 4. Implementation Checklist

### Immediate Diagnostics

- [x] Add DEBUG-level logging to FastAPI app startup
- [x] Add synchronous database update before background task registration
- [x] Create ultra-minimal background task test function
- [x] Implement batch status transition logging

### Code Verification

- [ ] Review imports for circular dependencies
- [ ] Verify session creation follows standards
- [ ] Compare background task pattern to Google Maps API exemplar
- [ ] Ensure transaction boundaries follow guidance

### Environment Verification

- [ ] Confirm database connection parameters
- [ ] Verify FastAPI background task configuration
- [ ] Check for resource limitations
- [ ] Test batch processing in clean environment

### Alternate Implementation

- [ ] Prepare simplified polling mechanism
- [ ] Design alternative task queue integration
- [ ] Test direct execution path

## 5. Verification Criteria

The solution will be considered successful when:

1. Batch jobs transition through all states: pending → running → completed
2. Status updates appear in logs showing progress
3. Background task execution is confirmed
4. Completion rates match expected values

## 6. Implementation Sequence

1. **Day 1 (2025-03-28):**

   - Implement immediate diagnostics
   - Review code against architectural standards
   - Create minimal test verification

2. **Day 2 (2025-03-29):**

   - Analyze diagnostic results
   - Implement identified fixes
   - Test with sample batch jobs

3. **Day 3 (2025-03-30):**
   - If not resolved, implement alternative strategy
   - Test end-to-end workflow
   - Document findings and solution

## 7. Fallback Strategy

If background tasks continue to fail after thorough debugging:

1. **Option 1: Direct Processing**

   - Implement direct synchronous processing for small batches
   - Add periodic polling for pending batches via scheduled task

2. **Option 2: External Task Queue**
   - Implement Redis or Celery queue integration
   - Update batch creation endpoint to use external queue
   - Modernize background processing architecture

## 8. Reporting

For each implementation phase, document:

1. Diagnostics collected
2. Code changes applied
3. Verification results
4. Next steps

## 9. Resources

1. Source code: `/src/services/batch/batch_processor_service.py`
2. Router: `/src/routers/batch_page_scraper.py`
3. HTML interface: `/static/batch-domain-scanner.html`
4. Architectural pattern: `/Docs/Docs_1_AI_GUIDES/14-GOOGLE_MAPS_API_EXEMPLAR.md`
5. Transaction guide: `/Docs/Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md`

## 10. Implementation Details

### 10.1 Task Execution Verification

We have created a robust task execution verification mechanism with multiple layers:

1. **Diagnostic Marker System**

   - Created `/src/services/batch/task_debugger.py` - a lightweight utility to create and manage task marker files
   - Implemented file-based verification with timestamp tracking
   - Added detailed logging with emojis for visual distinction in logs

2. **Batch Processor Instrumentation**

   - Modified `process_batch_with_own_session` to create marker files at the earliest point of execution
   - Added standalone file creation before any imports or try blocks
   - Implemented fallback verification if task_debugger import fails

3. **Router Diagnostic Updates**

   - Added synchronous database update in `create_batch_endpoint` to verify database writes before background task
   - Added diagnostic markers in batch metadata
   - Added detailed logging before and after background task registration

4. **Simple Task Test Module**

   - Created `/src/services/batch/simple_task_test.py` with minimal dependencies
   - Implemented standalone background task function for isolated testing
   - Added verification utility to check for task execution

5. **Test Endpoint**

   - Added `/api/v3/batch_page_scraper/test_background_task` endpoint
   - Created isolated test path with no database dependencies
   - Provided test ID for checking execution results

6. **Verification Script**
   - Created `scripts/batch/verify_background_tasks.py` for end-to-end testing
   - Implemented API request, marker file checking, and status monitoring
   - Added timing and execution verification

### 10.2 Next Steps

After implementing these diagnostic tools, the next steps are:

1. Run the verification script with the server running:

   ```
   PYTHONPATH=$PYTHONPATH:. python scripts/batch/verify_background_tasks.py
   ```

2. Test the simple background task endpoint:

   ```
   curl http://localhost:8000/api/v3/batch_page_scraper/test_background_task
   ```

3. Check for marker files:

   ```
   ls -la /tmp/scraper_sky_task_markers/
   ```

4. Analyze results to determine:

   - If background tasks are being registered properly
   - If they start execution at all
   - Which part of the execution is failing (import, session creation, etc.)

5. Based on findings, proceed to one of these actions:
   - Fix identified issues in background task implementation
   - Address circular dependency problems
   - Implement alternative task processing strategy
