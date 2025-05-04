# BACKGROUND TASK SUPAVISOR STANDARDIZATION WORK ORDER

**Document ID:** 07-49-BACKGROUND-TASK-SUPAVISOR-STANDARDIZATION-WORK-ORDER
**Date:** 2025-04-02
**Status:** Draft
**Priority:** High

## 1. Executive Summary

This work order addresses a critical architectural standardization needed across all background tasks in the ScraperSky backend. Despite architectural standardization in many service areas, there are inconsistencies in how background task sessions are created and managed. Specifically, the `batch_processor_service.py` creates raw database sessions that are incompatible with Supavisor connection pooling requirements, causing silently failing background tasks.

The issue represents a pattern that must be fixed system-wide to ensure reliability with the Supabase Supavisor architecture. This work order provides both immediate fixes for the `batch_processor_service.py` and a template for standardizing all background tasks system-wide.

## 2. Problem Statement

### 2.1 Critical Issues

1. **Inconsistent Session Creation**: Background tasks in different services use different approaches to create database sessions:

   - `page_scraper/processing_service.py` - Uses the proper `get_session()` context manager
   - `sitemap/background_service.py` - Uses the proper `get_session()` context manager
   - `batch/batch_processor_service.py` - Uses direct `async_session_factory()` without Supavisor configuration

2. **Silent Failures**: Background tasks with incompatible session creation silently fail without reaching their first log statement, leaving batch operations in a "pending" state indefinitely.

3. **Architectural Inconsistency**: The current implementation violates the architectural principle that "all database connections must use Supavisor compatible session creation" outlined in the database connection architecture document.

### 2.2 Root Cause Analysis

The root cause is the direct session creation in `process_batch_with_own_session()` that imports and uses `async_session_factory()` directly instead of using the `get_session()` context manager. This approach:

1. Bypasses Supavisor connection parameters and execution options
2. Creates sessions without proper error handling
3. Does not apply the required execution options for Supavisor compatibility

## 3. Required Changes

### 3.1 Immediate Fix for batch_processor_service.py

1. **Replace Direct Session Creation**: Replace direct use of `async_session_factory()` with the standard `get_session()` context manager.

2. **Simplify Import Structure**: Reorganize imports to avoid runtime imports that cause fragility.

3. **Ensure Proper Transaction Management**: Maintain the existing transaction boundaries while ensuring Supavisor compatibility.

4. **Enhance Error Handling**: Improve error handling to provide clearer diagnostics when sessions fail.

### 3.2 System-Wide Standardization Template

Implement the following standard pattern in **all** background task functions:

```python
async def process_x_with_own_session(job_id: str, ...):
    """
    Process X with its own dedicated session for background task reliability.

    This function follows the proper transaction management pattern for background tasks:
    1. Creates its own dedicated session using get_session()
    2. Manages its own transaction boundaries
    3. Handles errors with proper transaction awareness
    4. Updates job status appropriately
    """
    # Import here to avoid circular imports
    from ...session.async_session import get_session
    # Other imports as needed

    logger.info(f"Starting dedicated background processing for job_id: {job_id}")

    try:
        # Create a new session specifically for this background task using the context manager
        async with get_session() as session:
            try:
                # Update job status to processing
                async with session.begin():
                    # Initial status update

                # Process the core task
                async with session.begin():
                    # Main processing logic

                # Update job status to completed
                async with session.begin():
                    # Final status update

            except Exception as e:
                logger.error(f"Error in background processing: {str(e)}")
                # Update job status to failed
                try:
                    async with session.begin():
                        # Error status update
                except Exception as update_error:
                    logger.error(f"Failed to update status: {str(update_error)}")

    except Exception as outer_error:
        logger.error(f"Critical error in background processing: {str(outer_error)}")
```

## 4. Implementation Plan

### 4.1 Phase 1: Immediate Fix for batch_processor_service.py

1. **Code Changes**:

   - Update imports in `process_batch_with_own_session` to import `get_session`
   - Replace direct session creation with the context manager
   - Maintain existing transaction boundaries
   - Improve error handling
   - Add clear diagnostic logging

2. **Testing**:
   - Create test batches with multiple domains
   - Verify background task execution through logs
   - Confirm status transitions from "pending" to "running" to "completed"
   - Test error handling by introducing controlled failures

### 4.2 Phase 2: System-Wide Audit and Standardization

1. **Audit**:

   - Identify all background task functions across the codebase
   - Classify each by session creation pattern
   - Prioritize based on critical path and usage

2. **Standardization**:

   - Apply the standard pattern to each background task function
   - Update task function signatures to maintain compatibility
   - Add improved error handling and diagnostics
   - Ensure transaction boundary consistency

3. **Validation**:
   - Create automated test cases for each background task
   - Verify successful task execution
   - Test error handling
   - Confirm proper status updates

## 5. Technical Implementation Details

### 5.1 Required Changes to batch_processor_service.py

The current problematic code:

```python
# Create our own session
print(f"DEBUGGING: Attempting to create session")
session = async_session_factory()
try:
    print(f"DEBUGGING: Created session successfully")
    # Fix indentation and try/except structure
    # ... rest of the function using this session ...
```

Should be changed to:

```python
# Create a new session specifically for this background task
print(f"DEBUGGING: Creating session using get_session()")
async with get_session() as session:
    try:
        print(f"DEBUGGING: Created session successfully")
        # ... rest of the function using this session ...
```

### 5.2 Key Implementation Considerations

1. **Transaction Boundaries**: Each logical operation should have its own transaction with `async with session.begin()`.

2. **Error Handling**: Every operation should have proper error handling with specific error messages.

3. **Resource Cleanup**: The `get_session()` context manager ensures proper session cleanup.

4. **Import Strategy**: Imports should be at the function level to avoid circular dependencies.

## 6. Benefits and Expected Outcomes

1. **Reliability**: Background tasks will consistently execute with proper database connectivity.

2. **Maintainability**: Standard pattern makes code more maintainable and easier to debug.

3. **Performance**: Proper connection pooling improves database connection efficiency.

4. **Architectural Consistency**: Ensures all database connections follow the same pattern.

## 7. Verification and Testing

The implementation will be verified by:

1. Successful execution of batch processing tasks
2. Proper status updates in the database
3. Clear logs showing session creation and transaction boundaries
4. Reliable error handling when errors occur

## 8. Conclusion

This standardization represents a critical architectural improvement that will:

1. Resolve silently failing background tasks
2. Ensure consistent implementation across services
3. Improve system reliability and maintainability
4. Set the foundation for future background processing enhancements

This template will serve as the standard for all background task implementations going forward.
