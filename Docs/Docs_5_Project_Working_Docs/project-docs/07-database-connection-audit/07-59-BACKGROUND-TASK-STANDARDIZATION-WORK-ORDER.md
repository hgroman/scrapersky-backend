# 07-59 Background Task Standardization Work Order

## Executive Summary

This work order addresses SQLAlchemy async context management issues in FastAPI background tasks. Following our resolution of `MissingGreenlet` errors in the batch processing service, we need to systematically review and standardize all background services in the project.

**Root Problem**: FastAPI background tasks require special handling when using SQLAlchemy async operations. Without proper async context management, tasks encounter `MissingGreenlet` errors that silently fail, resulting in unprocessed data.

**Solution Pattern**: We successfully implemented a clean approach in batch processing that involves:

1. Using isolated session management for each database operation
2. Avoiding nested async contexts
3. Implementing comprehensive error handling and recovery

**Scope**: This work order will identify, evaluate, and update all background task implementations across the project to follow this standardized pattern.

**Priority**: HIGH - Background tasks are critical for asynchronous processing
**Timeline**: 5 days
**Status**: DRAFT

## Problem Analysis and Solution Pattern

### The MissingGreenlet Error

The `MissingGreenlet` error occurs when SQLAlchemy's async operations are executed outside the expected async context:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
```

This happens because FastAPI's background tasks run in a different context than the request handling code, and SQLAlchemy requires careful management of its async context.

### Successful Pattern Implementation

Our solution to this problem implemented in batch processing follows these principles:

1. **Isolated Session Management**

   - Create a new session for each discrete database operation
   - Keep session lifecycles short and focused
   - Use the specialized `get_background_session()` context manager

2. **Clean Async Flow**

   - Avoid nesting async operations that share database connections
   - Process items sequentially rather than with complex nested async structures
   - Maintain clear, linear control flow

3. **Robust Error Handling**
   - Implement error recovery for each operation
   - Use clean new sessions for status updates after errors
   - Document error paths clearly

### Example Solution Pattern

```python
async def process_batch_with_own_session(batch_id: str, items: List[str], user_id: str):
    """Process a batch of items with proper SQLAlchemy async context management."""
    logger.info(f"Starting batch processing for {len(items)} items")

    # First, update status to processing
    try:
        async with get_background_session() as session:
            batch = await BatchJob.get_by_id(session, batch_id)
            if batch:
                batch.status = "processing"
                batch.start_time = datetime.now()
                await session.flush()
    except Exception as e:
        logger.error(f"Error updating batch status: {str(e)}", exc_info=True)
        # Continue processing even if update fails

    # Track processing results
    completed_count = 0
    failed_count = 0
    item_results = {}

    # Process each item with isolated sessions
    for item in items:
        try:
            # Process item with its own session
            await process_item_with_own_session(item, user_id)

            # Item processed successfully
            completed_count += 1
            item_results[item] = "completed"

            # Update batch progress with a new session
            try:
                async with get_background_session() as session:
                    batch = await BatchJob.get_by_id(session, batch_id)
                    if batch:
                        batch.completed_count = completed_count
                        await session.flush()
            except Exception as update_error:
                logger.error(f"Error updating progress: {str(update_error)}")

        except Exception as e:
            # Item processing failed
            failed_count += 1
            item_results[item] = f"failed: {str(e)}"
            logger.error(f"Error processing item {item}: {str(e)}", exc_info=True)

            # Update batch progress with a new session
            try:
                async with get_background_session() as session:
                    batch = await BatchJob.get_by_id(session, batch_id)
                    if batch:
                        batch.failed_count = failed_count
                        batch.error = f"Error processing item {item}: {str(e)}"
                        await session.flush()
            except Exception as update_error:
                logger.error(f"Error updating progress: {str(update_error)}")

    # Update final batch status with a new session
    try:
        async with get_background_session() as session:
            batch = await BatchJob.get_by_id(session, batch_id)
            if batch:
                # Determine final status
                final_status = "completed" if failed_count == 0 else "partial"
                batch.status = final_status
                batch.end_time = datetime.now()

                # Store results in metadata
                metadata = batch.metadata or {}
                metadata["item_results"] = item_results
                batch.metadata = metadata

                await session.flush()
    except Exception as e:
        logger.error(f"Error updating final status: {str(e)}", exc_info=True)

    logger.info(f"Batch processing completed: {completed_count} succeeded, {failed_count} failed")
```

## Affected Services

Based on initial analysis, the following services contain background task implementations that need evaluation:

1. **Batch Processing** ✅ (Already fixed)

   - `src/services/batch/batch_functions.py`
   - `process_batch_with_own_session()`

2. **Sitemap Processing**

   - `src/services/sitemap/background_service.py`
   - `process_domain_background()`
   - `process_batch_background()`

3. **Places Search**

   - `src/services/places/places_search_service.py`
   - `process_places_search_background()`

4. **Email Scraper**

   - `src/tasks/email_scraper.py`
   - (Needs detailed inspection)

5. **Potentially others to be identified in code review**

## Implementation Plan

### Phase 1: Discovery (1 day)

1. **Comprehensive Code Scan**

   - Identify all background task implementations
   - Document current patterns and approaches
   - Prioritize based on usage and risk level

2. **Test Case Development**
   - Create tests to validate background task handling
   - Establish baseline for existing functionality
   - Define success criteria for fixes

### Phase 2: Implementation (3 days)

1. **Update Each Background Service**

   - Apply the standardized pattern to each service
   - Implement robust error handling
   - Add comprehensive logging
   - Update each service in isolation to allow for proper testing

2. **Common Utilities**
   - Create shared background task utilities if needed
   - Consolidate repeated patterns into helper functions
   - Ensure consistent behavior across all implementations

### Phase 3: Validation and Documentation (1 day)

1. **Testing**

   - Validate each implementation
   - Ensure no regressions in functionality
   - Test error handling and recovery

2. **Documentation**
   - Update development guidelines with background task patterns
   - Create examples for future reference
   - Document common pitfalls and solutions

## Technical Requirements

### 1. Session Management Requirements

- **MUST** use `get_background_session()` for all database operations
- **MUST** create a new session for each discrete database operation when updating status
- **MUST NOT** reuse sessions across different operations
- **MUST** implement proper error handling and recovery mechanisms

### 2. Async Pattern Requirements

- **MUST** avoid nesting async operations that share database connections
- **SHOULD** process items sequentially in most cases
- **MUST** maintain clear, linear control flow
- **MUST NOT** create complex nested async structures

### 3. Error Handling Requirements

- **MUST** catch and log all exceptions
- **MUST** attempt to update status even when errors occur
- **MUST** use clean new sessions for status updates after errors
- **SHOULD** include detailed error information in logs and status updates

## Testing & Validation

### Test Objectives

1. **Normal Operation**

   - Verify successful processing of all items
   - Validate proper status updates
   - Confirm final status reflects success

2. **Error Handling**

   - Test with failing items
   - Verify error status updates
   - Confirm processing continues after errors
   - Validate final status reflects failures

3. **Performance**
   - Measure processing time
   - Identify potential bottlenecks
   - Ensure reasonable resource usage

## Success Criteria

Each background task implementation will be considered successfully updated when:

1. It properly uses `get_background_session()` for all database operations
2. It implements isolated session management for each operation
3. It includes comprehensive error handling and recovery
4. It avoids nested async operations that share database connections
5. It passes all tests for normal operation and error handling

## References

### Key Technical References

1. **SQLAlchemy Documentation**

   - [SQLAlchemy 2.0 AsyncIO Integration](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
   - [MissingGreenlet Error](https://sqlalche.me/e/20/xd2s)

2. **FastAPI Documentation**

   - [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

3. **Internal References**
   - [07-58-DIRECT-SESSION-BACKGROUND-COMPATIBILITY-WORK-ORDER.md](./07-58-DIRECT-SESSION-BACKGROUND-COMPATIBILITY-WORK-ORDER.md)
   - [07-57-BACKGROUND-SESSION-HANDLER-IMPLEMENTATION-WORK-ORDER.md](./07-57-BACKGROUND-SESSION-HANDLER-IMPLEMENTATION-WORK-ORDER.md)

## Conclusion and Next Steps

This work order outlines a systematic approach to standardizing background task implementations across the project. The solution pattern developed for batch processing has proven effective in resolving the `MissingGreenlet` error and will be applied to all other background services.

By standardizing these implementations, we will ensure:

1. Reliable background processing without silent failures
2. Consistent error handling and recovery
3. Clear, maintainable code patterns
4. Proper SQLAlchemy async context management

### Next Actions

1. Begin Phase 1 discovery process
2. Review findings with the team
3. Develop test cases
4. Implement the standardized pattern in each affected service
5. Update documentation and guidelines

**Expected completion**: 5 working days from start
