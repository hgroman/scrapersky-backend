# DATABASE CONSOLIDATION IMPLEMENTATION GUIDE

**Date:** 2025-03-24
**Status:** Active
**Version:** 1.0

This document provides a step-by-step guide for implementing the database service consolidation effort, ensuring consistent standardization across all files.

## 1. STANDARDIZATION PROCESS OVERVIEW

For each file requiring standardization, follow these general steps:

1. **Analysis**: Review the current implementation and identify patterns
2. **Planning**: Document the specific changes needed
3. **Implementation**: Make the necessary changes
4. **Testing**: Verify the changes work correctly
5. **Documentation**: Update the progress tracker

## 2. ROUTER STANDARDIZATION GUIDE

### Step 1: Ensure Session Dependency Injection

```python
# BEFORE:
# Various non-standard approaches to getting a session

# AFTER:
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db_session
from fastapi import Depends

@router.post("/endpoint")
async def endpoint(
    request: SomeRequest,
    session: AsyncSession = Depends(get_db_session)
):
    # Router implementation
```

### Step 2: Add Router-Owned Transaction Boundaries

```python
# BEFORE:
# No explicit transaction boundaries or service-owned transactions

# AFTER:
@router.post("/endpoint")
async def endpoint(
    request: SomeRequest,
    session: AsyncSession = Depends(get_db_session)
):
    # Router explicitly owns transaction boundary
    async with session.begin():
        # Call service passing the session
        result = await some_service.operation(
            session=session,
            data=request.dict()
        )
    
    # Return after transaction is committed
    return result
```

### Step 3: Update Service Calls to Pass Session

```python
# BEFORE:
result = await some_service.operation(data=request.dict())

# AFTER:
result = await some_service.operation(
    session=session,
    data=request.dict()
)
```

### Step 4: Ensure Proper Background Task Handling

```python
# BEFORE:
# Various approaches to background tasks, sometimes using request session

# AFTER:
@router.post("/endpoint-with-bg-task")
async def endpoint(
    request: SomeRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session)
):
    # Transaction for initial processing
    async with session.begin():
        job = await job_service.create_job(
            session=session,
            data=request.dict()
        )
    
    # Add background task AFTER transaction is committed
    # Don't pass the session to background task
    background_tasks.add_task(
        process_background_job,
        job_id=job.id,
        data=request.dict()
    )
    
    return {"job_id": job.id, "status": "processing"}

# Background task creates its own session
async def process_background_job(job_id: str, data: dict):
    from src.db.session import async_session_factory
    
    # Create a new session for background task
    async with async_session_factory() as bg_session:
        try:
            # Explicitly manage transaction
            async with bg_session.begin():
                # Process data within transaction
                await service.process_data(
                    session=bg_session,
                    job_id=job_id,
                    data=data
                )
        except Exception as e:
            # Log errors but don't propagate since this is a background task
            logger.error(f"Error in background task {job_id}: {str(e)}")
```

## 3. SERVICE STANDARDIZATION GUIDE

### Step 1: Update Service Methods to Accept Session

```python
# BEFORE:
async def service_operation(data: dict):
    # Creating its own session
    async with session_factory() as session:
        # Doing work
        return result

# AFTER:
async def service_operation(session: AsyncSession, data: dict):
    # Using provided session, no transaction management
    # Service operations
    return result
```

### Step 2: Replace Direct SQL with db_service

```python
# BEFORE:
query = text("SELECT * FROM table WHERE id = :id")
result = await session.execute(query, {"id": record_id})
return result.fetchone()

# AFTER:
from src.services.core.db_service import db_service

result = await db_service.fetch_one(
    session=session,
    query="SELECT * FROM table WHERE id = :id", 
    params={"id": record_id}
)
return result
```

### Step 3: Replace String Concatenation with Parameterized Queries

```python
# BEFORE - SECURITY RISK:
query = f"SELECT * FROM table WHERE name = '{name}'"
result = await session.execute(text(query))

# AFTER - SAFE:
result = await db_service.fetch_all(
    session=session,
    query="SELECT * FROM table WHERE name = :name",
    params={"name": name}
)
```

### Step 4: Make Services Transaction-Aware

```python
# BEFORE:
async def service_operation(session, data):
    async with session.begin():  # Creating a transaction - WRONG
        # Do work
        return result

# AFTER:
async def service_operation(session, data):
    # No transaction management, just use the session
    # Optional transaction state logging for debugging
    in_transaction = session.in_transaction()
    logger.debug(f"Transaction state in operation: {in_transaction}")
    
    # Do work
    return result
```

## 4. ERROR HANDLING STANDARDIZATION

```python
# Standard pattern for router error handling:
@router.post("/endpoint")
async def endpoint(request: SomeRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        async with session.begin():
            result = await some_service.operation(session=session, data=request.dict())
        return result
    except ValueError as e:
        # Handle expected errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 5. REFERENCE IMPLEMENTATION

The file `src/routers/google_maps_api.py` provides the reference implementation for all these patterns. When in doubt, refer to this file for examples of proper:

- Transaction boundary management
- Session dependency injection
- Background task session management
- Error handling
- Service method calls

## 6. VERIFICATION CHECKLIST

After updating each file, verify:

1. [ ] Router uses session dependency injection
2. [ ] Router owns transaction boundaries with `async with session.begin()`
3. [ ] Services accept session parameter and never manage transactions
4. [ ] Background tasks create their own sessions and manage their own transactions
5. [ ] All direct SQL is replaced with db_service methods
6. [ ] No string concatenation in SQL queries (use parameterized queries)
7. [ ] Proper error handling for transaction rollback

## 7. COMMON ISSUES & SOLUTIONS

| Issue | Solution |
|-------|----------|
| Service creating its own transactions | Update to accept session and remove transaction boundaries |
| Raw SQL with string concatenation | Replace with db_service parameterized queries |
| Session creation in router | Use dependency injection |
| Background task using request session | Create new session in background task |
| Nested transactions | Ensure only router creates transactions |
| Missing error handling | Add try/except blocks with proper transaction rollback |

## 8. TESTING INSTRUCTIONS

For each updated file:

1. Test normal operation flow
2. Test error conditions to ensure proper rollback
3. Test concurrent operations if applicable
4. Verify database operations complete as expected
5. Check logs for any transaction errors

Update the progress tracker after completion to maintain accurate status information.