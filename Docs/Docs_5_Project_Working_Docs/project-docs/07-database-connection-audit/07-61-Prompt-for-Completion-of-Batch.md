# Prompt for Completing Batch Scraper Implementation

## Project Context

You're working on the ScraperSky backend – a FastAPI application using SQLAlchemy for database interactions with PostgreSQL via Supavisor. We've made significant progress in fixing a critical issue with background tasks in the batch processing service, where SQLAlchemy async operations were failing with `MissingGreenlet` errors.

## What Was Accomplished So Far

We've:

1. Fixed the primary `MissingGreenlet` error in batch processing by implementing isolated session management
2. Updated `src/services/batch/batch_functions.py` with proper error handling and session lifecycle
3. Created documentation in `07-59-BACKGROUND-TASK-STANDARDIZATION-WORK-ORDER.md`

## Your Mission: Complete Batch Scraper Route Implementation

Your task is to ensure the batch scraper route is completely implemented, tested, and documented. Follow a holistic approach to understand all aspects of the route before making any final adjustments.

## Batch Scraper Dependency Tree

```
┌─────────────────────────────────────┐
│ Router Layer                        │
│ src/routers/batch_page_scraper.py   │
└───────────────────┬─────────────────┘
                    ▼
┌─────────────────────────────────────┐
│ Service Layer                       │
│ src/services/batch/                 │
│  ├── types.py                       │
│  ├── batch_functions.py             │
│  └── batch_processor_service.py     │
└───────────────────┬─────────────────┘
                    ▼
┌─────────────────────────────────────┐
│ Domain Processing                   │
│ src/services/page_scraper/          │
│  └── domain_processor.py            │
└───────────────────┬─────────────────┘
                    ▼
┌─────────────────────────────────────┐
│ Data Access Layer                   │
│ src/models/batch_job.py             │
└─────────────────────────────────────┘
```

## Implementation Tasks

1. **Verify Router Implementation** (`src/routers/batch_page_scraper.py`):

   - Ensure proper transaction boundaries
   - Confirm BackgroundTasks are properly used
   - Verify error handling is comprehensive
   - Check that all endpoints follow the same pattern

2. **Review Service Layer** (`src/services/batch/batch_processor_service.py`):

   - Verify service is transaction-aware (not creating its own transactions)
   - Ensure proper coordination with batch_functions.py
   - Check for any lingering direct session creation

3. **Confirm Domain Processing** (`src/services/page_scraper/domain_processor.py`):

   - Ensure it uses `get_background_session()` properly
   - Verify error handling and recovery
   - Check for any complex nested async operations

4. **Test All Batch Operations End-to-End**:
   - Create batch
   - Process domains
   - Handle errors gracefully
   - Verify status updates
   - Confirm final results

## Technical Requirements

1. **Session Management**:

   - `src/session/async_session.py` is already properly implemented - DO NOT modify this file
   - All background tasks must use `get_background_session()`
   - Each discrete database operation should use its own session
   - Session lifecycle (commit/rollback) should be handled by context managers

2. **Async Flow in Background Tasks**:

   - Maintain linear, sequential processing
   - Avoid nested async operations that share database connections
   - Use proper async context management

3. **Error Handling**:
   - Catch all exceptions at appropriate levels
   - Use new sessions for status updates after errors
   - Ensure batch processing continues despite individual domain failures

## Verification Steps

1. **API Contract Verification**:

   - `/api/v3/batch_page_scraper/batch` POST endpoint creates batch and starts processing
   - `/api/v3/batch_page_scraper/batch/{batch_id}/status` GET endpoint returns accurate status

2. **Background Processing Verification**:

   - Batch status updates correctly during processing
   - Both successful and failed domains are properly tracked
   - Final status reflects overall success/failure

3. **Error Scenario Testing**:

   - Test with invalid domains
   - Test with network failures
   - Test with database errors
   - Verify proper recovery in all cases

4. **Performance Checks**:
   - Verify reasonable resource usage
   - Check for any potential memory leaks
   - Ensure connection pool is properly utilized

## Deliverables

1. A summary of your verification findings
2. Any remaining fixes implemented
3. Documentation of the complete implementation
4. Recommendations for any further improvements

## Important Notes

- Focus ONLY on batch scraper route completion
- Take a holistic approach to understand how all components work together
- Ensure all edge cases are handled
- The `src/session/async_session.py` file is already optimized - do not modify it

After this route is fully completed and verified, we'll move to the next route following the same methodical approach.
