# Single Domain Scanner Optimization

## Overview

This document outlines the changes made to optimize the Single Domain Scanner implementation to prevent the `MissingGreenlet` error and follow the established isolated session pattern.

## Issues Identified

1. **Transaction Scope Issue**: The original implementation used a single session for multiple database operations, risking `MissingGreenlet` errors if the session became invalid.

2. **Error Handling Concerns**: Status updates after errors used the same potentially corrupted session.

3. **Missing Supavisor Compatibility**: Not all SQL operations included `execution_options(prepared=False)` as required for Supavisor compatibility.

4. **Resource Management**: External resources were not explicitly cleaned up.

5. **Domain Record Management**: No check for existing domain records before creation, potentially causing duplicates.

## Implementation Changes

### 1. Refactoring Domain Processor (`src/services/page_scraper/domain_processor.py`)

The `process_domain_with_own_session` function was completely refactored to follow the isolated session pattern:

- Replaced single-session approach with discrete, isolated sessions for each database operation
- Split functionality into individual helper functions, each with its own session context
- Implemented proper error handling with separate sessions for error status updates
- Added Supavisor compatibility with `execution_options(prepared=False)` for all SQL queries
- Added explicit NULL handling for metadata extraction results
- Improved domain record management with get-or-create pattern

### 2. Fixing Router Implementation (`src/routers/modernized_page_scraper.py`)

- Updated the import path to use the correct module for background task processing
- Ensured tenant_id is properly passed to the background task

## Pattern Implementation

Each database operation now follows this pattern:

```python
async def some_database_operation(param1, param2):
    """Perform a database operation with its own session."""
    try:
        async with get_background_session() as session:
            # Use text query with proper execution options for Supavisor compatibility
            query = text("""
                SQL QUERY HERE
            """).execution_options(prepared=False)

            result = await session.execute(query, {"param1": param1})
            # Process result as needed
    except Exception as e:
        logger.error(f"Error message: {str(e)}", exc_info=True)
        raise  # Or handle appropriately
```

## Testing Approach

The implementation should be tested with:

1. Normal case testing - valid domains
2. Error case testing - invalid domains
3. Resource leak testing - monitoring session creation/destruction
4. Concurrent request testing - multiple simultaneous domain scans

## Verification Checklist

- [x] All database operations use isolated sessions
- [x] All SQL queries include `execution_options(prepared=False)`
- [x] Error handling uses fresh sessions for status updates
- [x] Resources are properly cleaned up
- [x] No duplicate domain records are created
- [x] Tenant_id is properly propagated through the entire flow

## Implementation Details

### 1. Isolating Database Operations

Each database operation now uses its own session:

```python
async def get_or_create_domain(domain_url: str, tenant_id: Optional[str] = None) -> int:
    """Get an existing domain record or create a new one using its own session."""
    try:
        async with get_background_session() as session:
            # Use isolated session for this specific database operation
            # ...
    except Exception as e:
        # Handle error
        raise
```

### 2. Ensuring Supavisor Compatibility

All SQL queries now include proper execution options:

```python
query = text("""
    SELECT id FROM domains
    WHERE domain = :domain_url
    LIMIT 1
""").execution_options(prepared=False)  # Critical for Supavisor compatibility
```

### 3. Proper Error Handling

Error handling now uses separate sessions:

```python
try:
    # Main processing
except Exception as e:
    # Use a new session for error updates
    await update_job_with_error(job_id, str(e))
```

### 4. Implementing Tests

Comprehensive tests have been added to verify:

- Domain record management
- Job status updates
- Error handling
- Full domain processing flow

### 5. Router Updates

The router has been updated to:

- Import from the correct module
- Pass tenant_id to the background task

## Conclusion

The Single Domain Scanner implementation now follows the established isolated session pattern, eliminating the risk of `MissingGreenlet` errors. Each database operation uses its own dedicated session, proper error handling is in place, and all SQL queries include the necessary Supavisor compatibility options.

## Next Steps

After these changes are verified, the pattern should be applied to other parts of the application, such as:

1. Batch Domain Scanner
2. Sitemap Scanner
3. Other background processing functions
