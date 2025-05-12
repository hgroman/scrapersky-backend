# 07-58 Direct Session and Background Compatibility Work Order

## Executive Summary

This work order addresses remaining database connection issues in background tasks, focusing specifically on `src/db/direct_session.py` and other modules that create database sessions for background operations. It follows the implementations established in work order 07-57 (Background Session Handler Implementation).

**Root Problem**: Several modules still create direct database connections without the proper asyncpg 0.30.0 compatibility settings required for Supavisor. These connections are causing "prepared statement does not exist" errors in background operations.

**Secondary Problem**: Background tasks were experiencing `MissingGreenlet` errors due to improper async context management when running SQLAlchemy operations in FastAPI background tasks.

**Solutions**:

1. Update all remaining background task session creation code to use the newly implemented `get_background_session()` function
2. Update the background task handling to ensure proper SQLAlchemy async context
3. Restructure the batch processing to simplify async flow and improve error handling

**Priority**: CRITICAL - Affects core background processing functionality
**Timeline**: Immediate implementation
**Status**: COMPLETED

## Affected Files

1. `src/db/direct_session.py` - Direct connection handler updated with server_settings
2. `src/services/sitemap/background_service.py` - Updated to use get_background_session()
3. `src/tasks/email_scraper.py` - Updated to use get_background_session()
4. `src/services/batch/batch_processor_service.py` - Simplified to remove task creation
5. `src/routers/batch_page_scraper.py` - Updated to handle background tasks correctly
6. `src/services/batch/batch_functions.py` - Restructured for proper SQLAlchemy async context

## Detailed Problem Statement

### Issue #1: Direct Session Creation in Background Tasks

When background tasks create database connections, they need specific configuration to work properly with asyncpg 0.30.0 and Supavisor:

```python
# WRONG - Using standard session creator in background tasks
async with get_session() as session:
    # Operations that will eventually fail with:
    # "asyncpg.exceptions.InvalidSQLStatementNameError: prepared statement does not exist"
```

### Issue #2: Incorrect Configuration in direct_session.py

The direct session module has almost all required settings, but is missing the critical server_settings parameter format:

```python
# CURRENT - Almost correct but missing server_settings format
connect_args = {
    "statement_cache_size": 0,  # This is at root level
    # ... other settings ...
    "server_settings": {
        "search_path": "public",
        "application_name": "scrapersky_backend"
        # Missing "statement_cache_size": "0" as a string in server_settings
    }
}
```

### Issue #3: Inconsistent Connection Parameters

Different background task modules use different session creation methods, leading to inconsistent connection parameters:

1. Some use `get_session()` from async_session.py
2. Some use `get_direct_session()` from direct_session.py
3. Some may create AsyncSession instances directly

### Issue #4: Improper Background Task Creation

The way background tasks were being created did not properly set up SQLAlchemy's async context:

```python
# WRONG - Using direct asyncio.create_task without proper context setup
asyncio.create_task(
    process_batch_with_own_session(
        batch_id=batch_id,
        domains=domains,
        user_id=user_id,
    )
)
```

This resulted in a MissingGreenlet error:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here
```

The solution required:

1. Proper router-level handling of background tasks using FastAPI's `BackgroundTasks`
2. Ensuring background tasks with database operations use `get_background_session()`
3. Implementing proper error handling and status updates

## Implementation Solutions

### 1. Database Connection Parameters

The database connection parameters must be set correctly in `connect_args` for Supavisor:

```python
connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    "server_settings": {
        "statement_cache_size": "0"  # As string in server_settings!
    }
}
```

### 2. Background Session Context Manager

All background tasks must use the specialized `get_background_session()` context manager:

```python
async with get_background_session() as session:
    # Database operations
    await session.execute(...)
```

### 3. Correct Background Task Creation

FastAPI's `BackgroundTasks` must be used correctly for database operations:

```python
# Router-level:
@router.post("/batch")
async def create_batch(
    background_tasks: BackgroundTasks,  # Injected by FastAPI
    # ... other parameters
):
    # Create batch record in transaction
    async with session.begin():
        batch_result = await service.create_batch(...)

    # Add background task directly
    background_tasks.add_task(
        process_batch_with_own_session,
        batch_id=batch_result["batch_id"],
        domains=domains
    )
```

### 4. Proper Async Error Handling

Background tasks must have proper error handling for async operations:

```python
try:
    async with get_background_session() as session:
        # Database operations
except Exception as e:
    logger.error(f"Error: {str(e)}")
    # Error recovery with a new session
    async with get_background_session() as recovery_session:
        # Update status to failed
```

## Implementation Tracking

- [x] Update src/db/direct_session.py

  - Added `"statement_cache_size": "0"` to server_settings as a string
  - Kept existing integer parameter at root level for maximum compatibility

- [x] Update src/services/sitemap/background_service.py

  - Changed import from `get_session` to `get_background_session`
  - Updated both `process_domain_background` and `process_batch_background` functions
  - Added comments explaining the reasons for using the specialized background session

- [x] Identify and update any other background task modules

  - Updated `src/tasks/email_scraper.py` to use `get_background_session()`
  - Identified some linter errors in the email_scraper.py file, but these are unrelated to the database connection issues

- [x] Fix background task handling

  - Updated router to use FastAPI's BackgroundTasks correctly
  - Removed complex task creation from service layer
  - Simplified the service layer to focus on database operations
  - Created a direct call to the background task function

- [x] Restructure batch processing for proper SQLAlchemy async context

  - Streamlined the process_batch_with_own_session function
  - Improved error handling with nested try/except blocks
  - Added detailed logging for troubleshooting
  - Fixed the MissingGreenlet error by ensuring proper session creation

- [x] Test each modification

  - Verified that the batch endpoint works correctly with new modifications
  - Confirmed that the MissingGreenlet error is resolved
  - Ensured proper error handling for background tasks

- [x] Document confirmed fixes
  - Updated 07-DATABASE_CONNECTION_STANDARDS.md
  - Created 20-DATABASE_CONNECTION_ASYNCPG_COMPATIBILITY.md with visual documentation
  - Completed this work order with implementation details

## Conclusion

All identified background task modules have been updated to use the proper database connection patterns for asyncpg 0.30.0 and Supavisor compatibility. Additionally, we've resolved the MissingGreenlet errors by implementing proper async context management for background tasks.

The key lessons learned:

1. Database connection parameters must be correctly configured for Supavisor:

   - `statement_cache_size` must be set both as an integer at connect_args root level AND as a string in server_settings
   - These parameters must be applied consistently across all connection points

2. Background tasks with SQLAlchemy async operations require special handling:

   - Always use `get_background_session()` for background tasks
   - Use FastAPI's `BackgroundTasks` at the router level
   - Implement proper error handling with multiple levels of try/except
   - Create direct task calls rather than complex nested functions

3. Always structure background tasks with clean, simple async flows:
   - Keep the async context clear and understandable
   - Avoid nested async functions when possible
   - Use session for as short a duration as possible

These changes ensure consistent database connectivity for background tasks and prevent both the "prepared statement does not exist" errors and MissingGreenlet errors.
