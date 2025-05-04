# Database Transaction Patterns Reference

**Date:** 2025-03-25
**Author:** Cascade AI
**Status:** Active
**Related Document:** [Database Connection Audit Plan](./07-03-database-connection-audit-plan.md)

## Purpose

This document serves as a comprehensive reference for transaction management patterns in the ScraperSky backend. It details the responsibilities of different components in the system regarding transaction handling and provides examples of correct implementation patterns.

## Transaction Management Responsibilities

The architecture defines a clear separation of responsibilities for transaction management:

### 1. Router Responsibility (Transaction Owners)

Routers **own transaction boundaries** and are responsible for:
- Creating explicit transaction boundaries with `async with session.begin()`
- Obtaining sessions via dependency injection
- Calling services within transaction boundaries
- Adding background tasks AFTER transaction completion

**Correct Pattern:**
```python
@router.post("/resource")
async def create_resource(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)
):
    # Start explicit transaction
    async with session.begin():
        # Call service within transaction
        result = await service.create_resource(session, request, current_user)

    # Add background tasks AFTER transaction is committed
    background_tasks.add_task(service.background_operation, result.id)

    # Return response after transaction is committed
    return ResponseModel(**result.dict())
```

### 2. Service Responsibility (Transaction Aware)

Services are **transaction-aware but NEVER manage transactions** and are responsible for:
- Using the provided session without creating transactions
- Performing database operations within the transaction context provided by the router
- Being "transaction-aware" but not "transaction-managing"

**Correct Pattern:**
```python
async def create_resource(
    session: AsyncSession,
    data: dict,
    user_id: str
) -> Resource:
    # Use session without transaction management
    resource = Resource(**data, created_by=user_id)
    session.add(resource)
    await session.flush()  # Flush without commit
    return resource
```

### 3. Background Task Responsibility (Self-Contained)

Background tasks **create their own sessions and manage their own transactions** and are responsible for:
- Creating dedicated sessions using the proper session factory
- Managing their own transaction boundaries
- Ensuring proper session closure, even in error cases
- Handling errors appropriately

**Correct Pattern:**
```python
async def process_background_task(task_id: str):
    # Import the proper session factory
    from src.session.async_session import get_session

    logger.info(f"Starting background task: {task_id}")

    try:
        # Create dedicated session for background task
        async with get_session() as session:
            # Manage transaction explicitly
            async with session.begin():
                # Perform database operations
                result = await session.execute(
                    select(Task).where(Task.id == task_id)
                )
                task = result.scalar_one_or_none()

                if not task:
                    logger.error(f"Task not found: {task_id}")
                    return

                # Update task status
                task.status = "processing"
                task.started_at = datetime.utcnow()

                # Process task
                # ...

                # Update task status
                task.status = "completed"
                task.completed_at = datetime.utcnow()

        logger.info(f"Background task completed: {task_id}")
    except Exception as e:
        logger.error(f"Error in background task {task_id}: {str(e)}", exc_info=True)

        # Create a new session for error handling
        try:
            async with get_session() as error_session:
                async with error_session.begin():
                    # Update task status to error
                    result = await error_session.execute(
                        select(Task).where(Task.id == task_id)
                    )
                    task = result.scalar_one_or_none()

                    if task:
                        task.status = "error"
                        task.error = str(e)
                        task.completed_at = datetime.utcnow()
        except Exception as inner_e:
            logger.error(f"Error handling failure for task {task_id}: {str(inner_e)}")
```

## Common Transaction Errors and Solutions

### 1. "A transaction is already begun on this Session"

**Cause:** Nested transactions or services attempting to create their own transactions.

**Solution:**
- Ensure services don't create their own transactions
- Check for nested `session.begin()` calls
- Verify that routers are the only components starting transactions

### 2. "Current transaction is aborted, commands ignored until end of transaction block"

**Cause:** Incomplete transaction management after an error occurs.

**Solution:**
- Ensure proper try/except/finally blocks with transaction cleanup
- Let exceptions propagate for proper transaction rollback
- Don't catch exceptions that should trigger rollback

### 3. "Can't operate on closed transaction inside context manager"

**Cause:** Using a session after its transaction is closed.

**Solution:**
- Ensure operations happen within the transaction context
- Don't store session objects for later use outside the transaction
- Verify transaction boundaries are properly defined

## File-by-File Transaction Pattern Analysis

### Router Files

| File | Transaction Pattern | Status | Issues |
|------|---------------------|--------|--------|
| `/src/routers/google_maps_api.py` | Mixed | Non-Compliant | Uses async_session_factory directly in background task |
| `/src/routers/batch_page_scraper.py` | Mixed | Non-Compliant | Uses db_params pattern for background tasks |
| `/src/routers/domain_router.py` | Transaction Owner | Compliant | Uses proper transaction boundaries |
| `/src/routers/sitemap_router.py` | Transaction Owner | Compliant | Uses proper transaction boundaries |
| `/src/routers/health_router.py` | Transaction Owner | Compliant | Uses proper transaction boundaries |
| `/src/routers/admin_router.py` | Transaction Owner | Compliant | Uses proper transaction boundaries |
| `/src/routers/user_router.py` | Transaction Owner | Compliant | Uses proper transaction boundaries |

### Service Files

| File | Transaction Pattern | Status | Issues |
|------|---------------------|--------|--------|
| `/src/services/sitemap/processing_service.py` | Mixed | Non-Compliant | Creates own sessions in background tasks |
| `/src/services/domain_service.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/page_scraper/processing_service.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/db_inspector.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/places/places_service.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/places/places_search_service.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/places/places_storage_service.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/job_service.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/batch/batch_processor_service.py` | Mixed | Non-Compliant | Creates own sessions in background tasks |
| `/src/services/core/user_context_service.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/core/db_service.py` | Transaction Aware | Compliant | Uses provided session |
| `/src/services/core/validation_service.py` | Transaction Aware | Compliant | Uses provided session |

### Background Task Implementations

| File | Transaction Pattern | Status | Issues |
|------|---------------------|--------|--------|
| `/src/services/sitemap/processing_service.py:process_domain_with_own_session` | Self-Contained | Partially Compliant | Creates own session but uses non-standard pattern |
| `/src/routers/google_maps_api.py:process_places_search_background` | Self-Contained | Non-Compliant | Uses async_session_factory directly |
| `/src/routers/batch_page_scraper.py:background tasks` | Self-Contained | Non-Compliant | Uses db_params pattern |
| `/src/services/batch/batch_processor_service.py:process_batch_background` | Self-Contained | Partially Compliant | Creates own session but may not handle errors properly |

## Remediation Recommendations

### High Priority

1. **Fix `/src/services/sitemap/processing_service.py`**
   - Replace `process_domain_with_own_session` with a version that uses `get_session()`
   - Ensure proper error handling with separate error sessions
   - Follow the self-contained background task pattern

2. **Fix `/src/routers/google_maps_api.py`**
   - Replace direct `async_session_factory()` calls with `get_session()`
   - Update background task to follow the self-contained pattern
   - Ensure proper session closure

### Medium Priority

1. **Fix `/src/routers/batch_page_scraper.py`**
   - Replace db_params pattern with proper session creation
   - Update background tasks to use `get_session()`
   - Ensure proper error handling

2. **Fix `/src/services/batch/batch_processor_service.py`**
   - Update background tasks to use `get_session()`
   - Ensure proper error handling with separate error sessions
   - Follow the self-contained background task pattern

## Verification Checklist

For each file, verify:

1. **Router Files**
   - [ ] Uses dependency injection for session
   - [ ] Creates explicit transaction boundaries
   - [ ] Calls services within transaction
   - [ ] Adds background tasks after transaction completion

2. **Service Files**
   - [ ] Accepts session parameter
   - [ ] Does not create transactions
   - [ ] Uses session for database operations
   - [ ] Properly handles errors

3. **Background Tasks**
   - [ ] Creates own session using `get_session()`
   - [ ] Manages own transaction boundaries
   - [ ] Ensures proper session closure
   - [ ] Handles errors with separate error sessions
