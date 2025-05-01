# WORK ORDER 07-53: Comprehensive Background Services Supavisor Standardization

## Priority: CRITICAL

## Status: AUTHORIZED

## Estimated Time: 4 hours

## Problem Statement

All four background service files contain multiple database operations that are not configured with proper execution options for Supavisor compatibility. While we previously fixed some individual functions, we have not systematically addressed ALL database operations in these files, causing continued failures with pgbouncer errors:

```
prepared statement "..." does not exist
HINT: pgbouncer with pool_mode set to "transaction" or "statement" does not support prepared statements properly
```

The most critical issue is in `batch_processor_service.py`, where the `get_batch_status` method is failing, preventing batch processing results from displaying correctly in the UI.

## Background Services Requiring Complete Fixes

1. ✅ **batch_processor_service.py** (HIGHEST PRIORITY)

   - Currently preventing batch results from displaying
   - We've fixed `process_batch_with_own_session` but missed `get_batch_status` and other methods

2. ✅ **page_scraper/processing_service.py**

   - We've fixed the main process function but need to verify all database operations

3. ✅ **sitemap/processing_service.py**

   - Completely unfixed, contains multiple database operations

4. ✅ **places_search_service.py**

   - Completely unfixed, contains multiple database operations

5. ✅ **job_service.py** (CRITICAL CORE SERVICE)
   - Central service used by ALL background tasks
   - Contains numerous database operations for job status updates
   - Status updates were failing with pgbouncer errors

## Required Approach

For EACH file:

1. Identify ALL methods that interact with the database by:

   - Looking for methods that accept a `session` parameter
   - Searching for direct database operations like:
     - `session.execute`
     - `select()` statements
     - `update()` statements
     - `delete()` statements
     - `session.add()`
     - ORM query operations

2. Apply Supavisor compatibility options to EVERY database operation:

   - For background service functions that create their own sessions, add:
     ```python
     session.bind.engine.update_execution_options(
         no_parameters=True,
         statement_cache_size=0
     )
     ```
   - For individual query operations, add execution options:
     ```python
     result = await session.execute(
         query,
         execution_options={
             "no_parameters": True,
             "statement_cache_size": 0
         }
     )
     ```

3. Thoroughly test each fix before moving to the next file

## Implementation Priority

1. ✅ First fix: `batch_processor_service.py` - `get_batch_status` method to immediately resolve the UI display issue
2. ✅ Then systematically fix all remaining methods in `batch_processor_service.py`
3. ✅ Then fix the remaining three background service files in order:
   - ✅ `page_scraper/processing_service.py`
   - ✅ `sitemap/processing_service.py`
   - ✅ `places_search_service.py`

## Completed Fixes

### 1. batch_processor_service.py

- ✅ `get_batch_status` - Added execution options to select query
- ✅ `process_batch_with_own_session` - Added:
  - Global execution options to session after creation
  - Execution options to all update statements (6 instances)
  - Execution options to select query for start_time

### 2. page_scraper/processing_service.py

- ✅ `process_domain_with_own_session` - Added global execution options to session after creation
- ✅ Fixed all other database operations:
  - Added execution options to all session.execute calls in the file
  - Fixed domain query in `initiate_domain_scan`

### 3. sitemap/processing_service.py

- ✅ Added global execution options to session after creation
- ✅ Fixed all database operations:
  - Added execution options to all query execution calls (7 instances)
  - Added execution options to all update statements
  - Applied execution options to all text SQL queries

### 4. places_search_service.py

- ✅ Completely implemented `process_places_search_background` with:
  - Global execution options on the session
  - Execution options for all query executions
  - Proper transaction handling

### 5. job_service.py

- ✅ Added execution options to ALL database operations:
  - Fixed job retrieval queries
  - Fixed job update statements
  - Fixed batch job status updates
  - Fixed all select operations

## Final Status

All five service files have been fixed to properly handle database connections with Supavisor compatibility options. The server has been restarted and is showing healthy status.

The batch processing system should now work correctly with no pgbouncer errors in the UI.

## Testing Requirements

For each file:

1. Restart the server after making changes
2. Test the associated functionality:
   - For batch processor: Submit a batch and verify results display properly
   - For page scraper: Submit a single domain scan and verify results
   - For sitemap scanner: Submit a sitemap scan and verify results
   - For places search: Submit a places search and verify results

## Documentation

Document each fix with detailed comments explaining:

1. What was modified
2. Why the execution options were added
3. What SQL operations were affected

## Authorization

Authorized by: Modernization Team
Date: 2024-03-28
