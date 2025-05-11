# TRANSACTION MANAGEMENT GUIDE

This document provides **CRITICAL** guidance on database transaction management in the ScraperSky project. The transaction management patterns described here are the result of extensive refactoring efforts throughout the codebase and must be strictly followed to avoid serious issues.

## 1. CRITICAL TRANSACTION MANAGEMENT PRINCIPLE

**ROUTERS OWN TRANSACTIONS, SERVICES DO NOT.**

This fundamental architectural principle must be followed consistently throughout the codebase. Violating this principle will lead to transaction conflicts, errors, and data inconsistency.

## 2. TRANSACTION MANAGEMENT PATTERNS

### Router Transaction Pattern (CORRECT)

```python
@router.post("/resource")
async def create_resource(
    request: RequestModel,
    session: AsyncSession = Depends(get_db_session)
):
    # CORRECT: Router establishes transaction boundaries
    async with session.begin():
        # Passing session to service, which does NOT start its own transaction
        result = await service.create_resource(session, request.data)

    # Return response after transaction is committed
    return ResponseModel(**result)
```

### Service Transaction Pattern (CORRECT)

```python
# CORRECT: Service uses provided session without transaction management
async def create_resource(
    session: AsyncSession,
    data: dict
) -> Resource:
    # Use session without transaction management
    resource = Resource(**data)
    session.add(resource)
    await session.flush()  # Flush without commit - router manages commit
    return resource
```

### Background Task Transaction Pattern (CORRECT & CRITICAL)

**IMPORTANT:** This section details the mandatory pattern for background tasks (e.g., APScheduler jobs) that interact with the database using `get_background_session` from `src.session.async_session`. Failure to adhere strictly to this pattern WILL lead to `InvalidRequestError: A transaction is already begun on this Session.` or similar hard-to-debug transaction conflicts.

**The Pattern:**

1.  Use `async with get_background_session() as session:` to manage the session lifecycle and the overall transaction boundary for the entire task execution.
2.  Perform all database operations (reads and writes) using the `session` object obtained from the context manager.
3.  **DO NOT** use nested `async with session.begin():` calls inside the main `async with get_background_session() as session:` block. The outer context manager already handles the transaction.
4.  If the background task function calls other helper functions or services that need database access, pass the _same_ `session` object to them.
5.  **CRITICAL RULE:** Helper functions or services that receive a session originating from `get_background_session()` **MUST NOT** call `await session.commit()` or `await session.rollback()` themselves. They should only perform operations using the provided session (e.g., `session.add()`, `await session.execute()`, modifying ORM object attributes). The final commit or rollback is handled _exclusively_ by the `async with get_background_session() as session:` context manager when it exits.

**Correct Example:**

```python
# File: src/services/some_scheduler.py
from src.session.async_session import get_background_session
from .some_helper_service import process_item_data
from src.models import Item
from sqlalchemy.future import select
import logging

logger = logging.getLogger(__name__)

async def scheduled_job():
    logger.info(\"Starting scheduled job...\")
    processed_count = 0
    failed_count = 0
    items_to_process = []

    # CORRECT: Use context manager for session and transaction
    try:
        async with get_background_session() as session:
            # Fetch items needing processing
            stmt = select(Item).where(Item.status == 'pending').limit(10)
            result = await session.execute(stmt)
            items_to_process = result.scalars().all()

            if not items_to_process:
                logger.info(\"No items to process.\")
                return # Context manager handles commit/close

            logger.info(f\"Processing {len(items_to_process)} items.\")
            for item in items_to_process:
                try:
                    # Update status IN MEMORY (no commit here)
                    item.status = 'processing'

                    # Call helper service, passing the session
                    # Helper service MUST NOT commit/rollback
                    success = await process_item_data(session, item)

                    if success:
                        # Helper service might update item status further in memory
                        logger.info(f\"Successfully processed item {item.id}\")
                        processed_count += 1
                    else:
                        # Helper service should have set item status to 'failed' in memory
                        logger.warning(f\"Failed to process item {item.id}\")
                        failed_count += 1

                    # WRONG: Do not add session.commit() or session.begin() here!

                except Exception as inner_exc:
                    logger.error(f\"Error processing item {item.id}: {inner_exc}\", exc_info=True)
                    failed_count += 1
                    # Mark failed IN MEMORY before re-raising
                    try:
                        item.status = 'failed'
                        item.error_message = str(inner_exc)[:500]
                    except AttributeError:
                        logger.error(\"Could not access item object after error.\")
                    # Re-raise to trigger the outer rollback for the whole batch
                    raise

            # Loop finished without error - context manager will COMMIT all changes
            logger.info(\"Batch loop finished. Context manager will commit.\")

    except Exception as outer_exc:
        # Error during session setup or outer block (e.g., DB connection, re-raised inner error)
        logger.error(f\"Error during scheduled job execution: {outer_exc}\", exc_info=True)
        # Context manager handles ROLLBACK automatically

    finally:
        logger.info(f\"Scheduled job finished. Processed: {processed_count}, Failed: {failed_count}\")

```

**Incorrect Example (Illustrating Violations):**

```python
# File: src/services/some_helper_service_WRONG.py
# ... (imports)

async def process_item_data_wrong(session: AsyncSession, item: Item):
    try:
        # ... processing logic ...
        item.status = 'completed'
        await session.commit() # WRONG: Service should not commit session passed from background task
        return True
    except Exception as e:
        logger.error(f\"Error in helper: {e}\")
        await session.rollback() # WRONG: Service should not rollback session passed from background task
        item.status = 'failed'
        # await session.commit() # WRONG: Especially don't commit after rollback!
        return False

# File: src/services/some_scheduler_WRONG.py
# ... (imports)

async def scheduled_job_wrong():
    # ... (setup)
    try:
        async with get_background_session() as session:
            # ... (fetch items)
            for item in items_to_process:
                # ...
                async with session.begin(): # WRONG: Nested transaction!
                    item.status = 'processing'
                    # ...
                # ... call helper ...
    # ... (exception handling/finally)
```

## 3. TRANSACTION ANTI-PATTERNS

### Double Transaction (WRONG)

```python
# WRONG: Nested transactions will cause errors
@router.post("/resource")
async def create_resource(request: RequestModel, session: AsyncSession):
    async with session.begin():  # Router transaction
        # Service also creates transaction - THIS WILL FAIL
        result = await service.create_with_transaction(session)
    return result

# WRONG: Service should not manage transactions
async def create_with_transaction(session: AsyncSession, data: dict):
    # NESTED TRANSACTION - THIS CAUSES ERRORS
    async with session.begin():  # ← Conflicts with router transaction!
        resource = Resource(**data)
        session.add(resource)
        return resource
```

### No Transaction Boundaries (WRONG)

```python
# WRONG: Missing transaction boundaries
@router.post("/resource")
async def create_resource(request: RequestModel, session: AsyncSession):
    # No transaction boundary! Changes might not be committed
    result = await service.create_resource(session, request.data)
    return result
```

### Incorrect Error Handling (WRONG)

```python
# WRONG: Transaction errors not properly handled
@router.post("/resource")
async def create_resource(request: RequestModel, session: AsyncSession):
    try:
        async with session.begin():
            result = await service.create_resource(session, request.data)
        return result
    except Exception:
        # WRONG: Swallowing error without rolling back transaction
        return {"error": "Something went wrong"}
```

## 4. REAL-WORLD ISSUES SOLVED

The transaction management patterns defined in this guide solved several critical issues that were found throughout the codebase:

1. **"Transaction already begun" errors**

   - Caused by: Services starting transactions when routers already had a transaction
   - Fixed by: Enforcing router-owned transactions

2. **"Current transaction is aborted" errors**

   - Caused by: Exceptions in transactions without proper rollback
   - Fixed by: Using `async with session.begin()` for automatic rollback

3. **Uncommitted changes**

   - Caused by: Missing transaction boundaries
   - Fixed by: Ensuring all router endpoints use proper transaction boundaries

4. **Connection pool exhaustion**
   - Caused by: Sessions not being properly closed in background tasks
   - Fixed by: Explicit session closure in finally blocks

## 5. VERIFICATION CHECKLIST

All code changes MUST be verified against these criteria:

1. ✅ Routers use `async with session.begin()` for transaction boundaries
2. ✅ Services never start their own transactions
3. ✅ Background tasks create their own sessions
4. ✅ All error paths properly handle transaction rollback
5. ✅ No nested transactions anywhere in the code

## 6. TRANSACTION ERROR IDENTIFICATION

When reviewing code or debugging issues, watch for these common transaction errors:

```
"A transaction is already begun on this Session"
```

- **Cause**: Nested transactions (service trying to begin a transaction when router already started one)
- **Solution**: Remove transaction handling from services

```
"Current transaction is aborted, commands ignored until end of transaction block"
```

- **Cause**: Exception occurred in transaction without proper rollback
- **Solution**: Use `async with session.begin()` for automatic rollback

```
"Can't operate on closed transaction inside context manager"
```

- **Cause**: Using a session after its transaction is closed
- **Solution**: Ensure operations happen within the transaction context manager

## 7. GOOGLE MAPS API REFERENCE IMPLEMENTATION

The Google Maps API implementation serves as the **golden standard** for proper transaction management. Refer to it when implementing transaction handling in other parts of the codebase:

- File: `src/routers/google_maps_api.py`
- Example methods: `search_places`, `get_place_details`

## 8. IMPLEMENTATION HISTORY

This transaction management pattern was established after extensive refactoring efforts throughout the codebase:

1. **Discovery Phase**: Identified inconsistent transaction management across different features
2. **Analysis Phase**: Traced "transaction already begun" errors to nested transaction starts
3. **Policy Decision**: Established router-owned transactions as architectural policy
4. **Implementation Phase**: Refactored all routers and services to follow the pattern
5. **Verification Phase**: Implemented transaction tests to verify correctness
6. **Documentation**: Created this guide as definitive reference

## 9. CONCLUSION

Transaction management is one of the most critical aspects of the ScraperSky backend. Following the patterns in this guide will ensure database operations remain consistent, predictable, and error-free.

**REMEMBER**: Routers own transactions, services do not.

## 10. SESSION HANDLING IN FASTAPI DEPENDENCIES

### Critical Issue with AsyncSession Dependencies

When using FastAPI's dependency injection system with SQLAlchemy's AsyncSession, there's a critical implementation detail that must be understood:

**IMPORTANT**: When using `get_session_dependency` to inject a session into a route handler, that session is ALREADY a context manager that manages its own lifecycle.

### Problem: Double Context Manager Anti-Pattern

This anti-pattern occurs when trying to use an injected session object with another context manager:

```python
# WRONG: Double context manager
@router.post("/endpoint")
async def endpoint(
    session: AsyncSession = Depends(get_session_dependency)
):
    # ERROR: Session already is a context manager from dependency
    async with session:  # This will cause "_AsyncGeneratorContextManager has no attribute 'add'" error
        # Perform database operations
        entity = Entity()
        session.add(entity)  # FAILS with AttributeError
```

### Solution: Direct Session Usage Pattern

The correct pattern is to use the session directly without wrapping it in another context manager:

```python
# CORRECT: Direct session usage
@router.post("/endpoint")
async def endpoint(
    session: AsyncSession = Depends(get_session_dependency)
):
    # Directly use the session without additional context manager
    entity = Entity()
    session.add(entity)  # Works correctly
```

### Real-World Example: Batch Sitemap Implementation

The sitemap batch API initially suffered from this issue. The fix involved:

1. Changing from `get_session` to `get_session_dependency` for dependency injection
2. Removing redundant `async with session:` blocks since the session is already managed by the dependency
3. Using the session directly in route handlers for database operations

#### Before:

```python
@router.post("/api/v3/sitemap/batch/create")
async def create_sitemap_batch(
    request: SitemapBatchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(user_dependency),
):
    try:
        # This caused errors
        async with session.begin():
            # Database operations...
```

#### After:

```python
@router.post("/api/v3/sitemap/batch/create")
async def create_sitemap_batch(
    request: SitemapBatchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(user_dependency),
):
    try:
        # Direct session usage without additional context manager
        # Database operations...
```

### Key Takeaways for Session Usage

1. Use `get_session_dependency` for router dependency injection (NOT `get_session`)
2. Do NOT wrap the injected session in another context manager
3. For background tasks, continue using `get_background_session` with appropriate context handling
4. Direct session usage allows the dependency injection system to manage the session lifecycle

This pattern was established after fixing the batch sitemap implementation, which encountered the "\_AsyncGeneratorContextManager object has no attribute 'add'" error due to improper session handling.
