# WORK ORDER 07-52: Single Domain Processor Background Task Supavisor Standardization

## Priority: CRITICAL

## Status: AUTHORIZED

## Estimated Time: 1 hour

## Problem Statement

The Single Domain Processor background task (`process_domain_with_own_session` in `page_scraper/processing_service.py`) creates its own database session but does not configure it with execution options required for Supavisor compatibility. This causes the service to fail when running under Supavisor with the following error:

```
ERROR: prepared statement "..." does not exist
```

When batch tasks are submitted, the fixed batch processor calls the unfixed single domain processor for each domain, causing failures in the background processing of individual domains within batches.

## Context

This is part of a pattern of needed fixes across all background tasks. The Batch Processor Service has already been fixed, but it depends on this service for individual domain processing.

Per the system architecture and documentation:

1. All background tasks must create their own database sessions
2. All database sessions must have execution options set to disable prepared statements
3. The background task in `page_scraper/processing_service.py` is responsible for processing individual domains

The issue was identified during testing of the batch domain scanner, where domain tasks were failing due to incompatibility with Supavisor connection pooling.

## Required Fix

Modify the `process_domain_with_own_session` function in `src/services/page_scraper/processing_service.py` to:

1. Set execution options on the database session immediately after creating it
2. Apply these execution options to all queries that need them
3. Ensure all transaction boundaries are properly managed

## Implementation Details

1. Locate the `process_domain_with_own_session` function in `src/services/page_scraper/processing_service.py`
2. Add execution options to the session immediately after creation:
   ```python
   # Add these options to disable prepared statements for Supavisor compatibility
   session.bind.engine.update_execution_options(
       no_parameters=True,  # Disable prepared statements
       statement_cache_size=0  # Disable statement caching
   )
   ```
3. Ensure these options are applied to any direct query execution
4. Test the function by creating a batch that processes multiple domains

## Testing Requirements

1. Restart the server after making changes
2. Submit a batch with multiple domains
3. Verify all domains are processed successfully
4. Check logs for any Supavisor-related errors

## Documentation Requirements

Update the standardization implementation template to include this fix as part of the comprehensive pattern.

## Approval

Authorized by: Modernization Team
Date: 2024-03-27
