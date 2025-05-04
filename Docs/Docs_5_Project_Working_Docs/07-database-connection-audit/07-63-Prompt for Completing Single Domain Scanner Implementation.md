# Prompt for Completing Single Domain Scanner Implementation

## Project Context

You're working on the ScraperSky backend – a FastAPI application using SQLAlchemy for database interactions with PostgreSQL via Supavisor. Following our success in fixing the `MissingGreenlet` error in the batch processing service, we now need to ensure the Single Domain Scanner route is fully optimized using the same pattern.

## Previous Accomplishments

We've:

1. Fixed the `MissingGreenlet` error in batch processing by implementing isolated session management
2. Established a pattern for background tasks that properly maintains SQLAlchemy async context
3. Created documentation in `07-59-BACKGROUND-TASK-STANDARDIZATION-WORK-ORDER.md`
4. Successfully implemented the pattern in `src/services/batch/batch_functions.py`

## Your Mission: Complete Single Domain Scanner Route Implementation

Your task is to ensure the Single Domain Scanner route is completely implemented, tested, and documented following our established pattern. Take a holistic approach to understand all aspects of the route before making any adjustments.

## Single Domain Scanner Dependency Tree

```
┌─────────────────────────────────────┐
│ Router Layer                        │
│ src/routers/modernized_page_scraper.py │
└───────────────────┬─────────────────┘
                    ▼
┌─────────────────────────────────────┐
│ Service Layer                       │
│ src/services/page_scraper/          │
│  └── processing_service.py          │
│      ├── initiate_domain_scan()     │
│      ├── process_domain_with_own_session() │
│      └── get_job_status()           │
└───────────────────┬─────────────────┘
                    ▼
┌─────────────────────────────────────┐
│ Scraper Layer                       │
│ src/scraper/                        │
│  ├── metadata_extractor.py          │
│  │   └── Extract metadata from pages │
│  └── domain_utils.py                │
│      └── URL normalization & parsing │
└───────────────────┬─────────────────┘
                    ▼
┌─────────────────────────────────────┐
│ Data Access Layer                   │
│ src/models/                         │
│  ├── Job                            │
│  └── Domain                         │
└─────────────────────────────────────┘
```

## Implementation Tasks

1. **Verify Router Implementation** (`src/routers/modernized_page_scraper.py`):

   - Ensure proper transaction boundaries
   - Confirm BackgroundTasks are properly used
   - Verify error handling is comprehensive
   - Check that all endpoints follow the same pattern

2. **Review Service Layer** (`src/services/page_scraper/processing_service.py`):

   - Verify transaction-aware approach (not creating its own transactions)
   - Ensure proper background task implementation
   - Check for any lingering direct session creation
   - Verify that any SQL text queries include proper execution options for Supavisor compatibility (`execution_options(prepared=False)`)
   - Ensure status updates use new, dedicated sessions, especially after error handling
   - Confirm that transaction boundaries do not span across multiple domain operations

3. **Confirm Domain Processing** (`src/services/page_scraper/domain_processor.py`):

   - Ensure it uses `get_background_session()` properly
   - Verify error handling and recovery
   - Check for any complex nested async operations

4. **Verify Scraper Layer** (`src/scraper/metadata_extractor.py` and `src/scraper/domain_utils.py`):

   - Ensure proper separation of concerns
   - Confirm no direct database access
   - Check that all errors are properly propagated

5. **Test All Single Domain Operations End-to-End**:
   - Create domain scan
   - Process domain
   - Handle errors gracefully
   - Verify status updates
   - Confirm final results

## Technical Requirements

1. **Session Management**:

   - `src/session/async_session.py` is already properly implemented - DO NOT modify this file
   - All background tasks must use `get_background_session()`
   - Each discrete database operation should use its own session
   - Session lifecycle (commit/rollback) should be handled by context managers
   - When using raw SQL queries via SQLAlchemy text() objects, always apply `execution_options(prepared=False)` to prevent prepared statement issues with Supavisor
   - Ensure that transaction scope is kept as narrow as possible - begin transactions immediately before needed and commit promptly after operations complete

2. **Async Flow in Background Tasks**:

   - Maintain linear, sequential processing
   - Avoid nested async operations that share database connections
   - Use proper async context management

3. **Error Handling**:
   - Catch all exceptions at appropriate levels
   - Use new sessions for status updates after errors
   - Ensure domain processing continues despite individual failures

## Verification Steps

1. **API Contract Verification**:

   - `/api/v3/modernized_page_scraper/scan` POST endpoint creates scan and starts processing
   - `/api/v3/modernized_page_scraper/status/{job_id}` GET endpoint returns accurate status

2. **Background Processing Verification**:

   - Job status updates correctly during processing
   - Metadata extraction succeeds for valid domains
   - Error handling works properly for invalid domains
   - Verify that database connections are properly released after each operation
   - Confirm that the connection pool usage remains stable during extended processing

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

- Focus ONLY on the Single Domain Scanner route
- Take a holistic approach to understand how all components work together
- Apply the same successful pattern we implemented for batch processing
- The `src/session/async_session.py` file is already optimized - do not modify it
- Pay special attention to the `process_domain_with_own_session()` function, which is potentially at risk for the same `MissingGreenlet` error

After this route is fully completed and verified, we'll move to the next route (Sitemap Scanner) following the same methodical approach.

**Note:** Additional standardization requirements are documented in `07-64-Single-Domain-Scanner-Standardization-Requirements.md` and should be applied after the core implementation is verified to be working correctly.
