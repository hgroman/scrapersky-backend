# WORK ORDER: 07-51-BATCH-PROCESSOR-SESSION-STANDARDIZATION

## Overview

This work order addresses critical database session handling issues in the batch processor service that are causing compatibility problems with Supavisor and pgbouncer. The batch processing pipeline shows inconsistent behavior, with background tasks failing silently due to improper session management.

## Objective

Systematically identify and replace all instances of non-standard database session handling in the batch processor service with the proper pattern that ensures Supavisor compatibility.

## Issues

1. Direct session creation instead of using `get_session()`
2. Manual engine imports and construction
3. Improper execution_options configuration
4. Sessions without proper context managers
5. Missing transaction boundaries
6. Incompatible prepared statement handling

## Search Methodology

Perform the following systematic searches on `src/services/batch/batch_processor_service.py`:

| Pattern to Search                 | What It Finds                     | Replacement Pattern                 |
| --------------------------------- | --------------------------------- | ----------------------------------- |
| `Session(`                        | Direct session creation           | Use `get_session()` context manager |
| `create_async_engine`             | Manual engine imports             | Remove, use session factory         |
| `execution_options`               | Manual execution options          | Remove, let session handle it       |
| `session.execute` without context | Raw execution without transaction | Use `async with session.begin()`    |
| `psycopg2`                        | Direct database connections       | Remove, use SQLAlchemy              |
| `.begin()`                        | Old transaction style             | Use `async with session.begin()`    |
| `AsyncSession`                    | Session imports                   | Use only get_session import         |

## Required Changes

1. **Import Structure Changes:**

   - Remove direct imports of AsyncSession, engine, etc.
   - Add proper import: `from ...session.async_session import get_session`

2. **Replace Direct Session Creation:**

   - Find any instances where sessions are created directly
   - Replace with context-manager pattern: `async with get_session() as session:`

3. **Transaction Boundary Standardization:**

   - Ensure all database operations occur within transaction boundaries
   - Pattern: `async with session.begin(): # operations here`

4. **Error Handling:**

   - Add proper try/except blocks that respect transaction boundaries
   - Roll back transactions on errors

5. **Task Execution:**
   - Ensure background tasks create their own sessions and manage transactions

## Estimated Impact

Based on initial analysis, there could be between 3-7 instances of non-standard session handling in the batch processor service. Each instance poses a potential risk for silent failures during batch processing.

## Testing Plan

1. Run all search patterns to identify instances
2. Create fixes for each identified pattern
3. Test batch creation
4. Verify background task execution
5. Check batch status endpoint
6. Validate completed batches in database

## Deliverables

1. Updated batch_processor_service.py with standardized session handling
2. Documentation of found and fixed issues
3. Test results showing successful batch processing

## Priority

**HIGH** - This is blocking production batch processing functionality.

## Timeline

- Search and identification: 2 hours
- Implementation of fixes: 4 hours
- Testing: 2 hours
- Documentation: 1 hour

## Assignee

TBD

## Related Documentation

- [07-50-BACKGROUND-TASK-SUPAVISOR-STANDARDIZATION-IMPLEMENTATION.md](./07-50-BACKGROUND-TASK-SUPAVISOR-STANDARDIZATION-IMPLEMENTATION.md)
- [07-48-BATCH-PROCESSING-CODE-FIXES-SUMMARY.md](./07-48-BATCH-PROCESSING-CODE-FIXES-SUMMARY.md)
