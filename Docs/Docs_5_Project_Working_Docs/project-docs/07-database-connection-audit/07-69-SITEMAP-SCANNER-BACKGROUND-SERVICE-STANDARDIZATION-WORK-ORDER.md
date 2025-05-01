# SITEMAP SCANNER BACKGROUND SERVICE STANDARDIZATION WORK ORDER

**Document ID:** 07-69-SITEMAP-SCANNER-BACKGROUND-SERVICE-STANDARDIZATION-WORK-ORDER
**Date:** 2025-03-29
**Status:** Open
**Priority:** High
**Related Documents:** 07-50-BACKGROUND-TASK-SUPAVISOR-STANDARDIZATION-IMPLEMENTATION, 07-61-BACKGROUND-TASK-SQLALCHEMY-PATTERN, 20-DATABASE_CONNECTION_ASYNCPG_COMPATIBILITY

## 1. Executive Summary

This work order addresses critical issues with the sitemap scanner background service implementation. Based on error logs and architectural audit, the sitemap scanner's `process_domain_with_own_session()` background service is not properly implementing the required database connection standards for Supavisor compatibility. We need to apply the same successful patterns used in the batch processor to ensure proper session management, transaction boundaries, and error handling.

## 2. Current Issues

1. **Session Management**:

   - Error logs show `cannot access local variable 'update' where it is not associated with a value` in the sitemap processing service
   - Likely using direct session creation instead of `get_background_session()`
   - Potential scope issues with variables across async operations

2. **Transaction Boundaries**:

   - Improper transaction boundary management
   - Missing or inconsistent use of `async with session.begin()` blocks
   - Possible nested transactions causing issues

3. **Error Handling**:

   - Insufficient error handling around database operations
   - Missing finally blocks to ensure session closure
   - Errors not properly propagated to status updates

4. **Supavisor Compatibility**:
   - Not using required execution options for asyncpg 0.30.0+ compatibility
   - Possibly using prepared statements which fail with connection pooling

## 3. Required Changes

### 3.1 Update Background Process Implementation

1. **File**: `src/services/sitemap/processing_service.py`
2. **Function**: `process_domain_with_own_session()`
3. **Changes Required**:

   - Replace direct session creation with `get_background_session()`
   - Implement proper transaction boundaries with discrete operations
   - Add comprehensive error handling with try/except/finally blocks
   - Ensure session closure in all code paths
   - Implement separate sessions for status updates after errors
   - Remove any nested async database operations
   - Add proper logging for diagnostics

### 3.2 Standardize Session Parameters

1. Ensure all database operations use the correct execution options:
   - `no_prepare=True`
   - `statement_cache_size=0`
   - Proper execution options for Supavisor compatibility

### 3.3 Linearize Processing Flow

1. Review the processing flow to ensure sequential, linear execution
2. Remove any parallel processing that shares database connections
3. Refactor to ensure independent operations with clear boundaries

## 4. Implementation Pattern

Follow this pattern for the implementation:

```python
async def process_domain_with_own_session(job_id, domain, user_id, options=None):
    """Process a domain's sitemap with an isolated session."""
    # Tracking variables
    job_completed = False
    error_message = None

    # Step 1: Update status to processing using dedicated session
    try:
        async with get_background_session() as session:
            async with session.begin():
                # Update job status to processing
                # Get job by ID
                # Update status
                pass
    except Exception as e:
        logger.error(f"Error updating job status: {str(e)}")
        return

    # Step 2: Process sitemap with dedicated session
    try:
        async with get_background_session() as session:
            async with session.begin():
                # Main processing logic
                # Extract sitemap URLs
                # Process data
                pass

            # Mark as completed
            job_completed = True
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing sitemap: {error_message}")
    finally:
        # Step 3: Update final status with dedicated session
        try:
            async with get_background_session() as session:
                async with session.begin():
                    # Get job again
                    # Update final status based on job_completed and error_message
                    pass
        except Exception as final_e:
            logger.error(f"Error updating final status: {str(final_e)}")
```

## 5. Testing Requirements

### 5.1 Unit Tests

- Test session creation
- Test error handling
- Test transaction boundaries

### 5.2 Integration Tests

- Test sitemap processing with valid sitemap
- Test handling of invalid sitemap
- Test recovery from errors

### 5.3 End-to-End Tests

- Test complete workflow from API to background processing
- Verify all status updates are correctly reflected
- Ensure proper error reporting

## 6. Verification Criteria

A successful implementation must satisfy these requirements:

1. **No Database Errors**:

   - No `MissingGreenlet` errors
   - No "prepared statement does not exist" errors
   - No session-related exceptions

2. **Proper Status Updates**:

   - Jobs transition through expected states (pending → processing → completed/failed)
   - Error messages are properly recorded

3. **Resource Management**:

   - No connection leaks
   - Sessions properly closed in all cases
   - No excessive connection usage

4. **Logging and Diagnostics**:
   - Clear log messages for all key operations
   - Proper error information for debugging

## 7. Implementation Checklist

- [ ] Review current sitemap scanner implementation
- [ ] Update background service to use `get_background_session()`
- [ ] Refactor transaction boundaries
- [ ] Implement proper error handling
- [ ] Add logging for key operations
- [ ] Test with valid sitemaps
- [ ] Test with invalid sitemaps
- [ ] Test error recovery
- [ ] Verify status updates
- [ ] Document changes

## 8. Resources

1. **Reference Implementations**:

   - `src/services/batch/batch_functions.py`
   - `src/services/batch/batch_processor_service.py`

2. **Standards Documentation**:
   - 20-DATABASE_CONNECTION_ASYNCPG_COMPATIBILITY.md
   - 07-61-BACKGROUND-TASK-SQLALCHEMY-PATTERN.md

## 9. Timeline

1. Implementation: 1 day
2. Testing: 1 day
3. Documentation: 0.5 day
4. Total: 2.5 days

## 10. Reporting Requirements

Upon completion, create a detailed implementation report following the template in previous completion reports, documenting:

1. Changes made
2. Testing methodology
3. Test results
4. Any remaining issues
5. Lessons learned

This report should be saved as `07-69-SITEMAP-SCANNER-BACKGROUND-SERVICE-STANDARDIZATION-COMPLETION.md`
