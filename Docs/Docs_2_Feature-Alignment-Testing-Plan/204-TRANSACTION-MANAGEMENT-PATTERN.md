# Transaction Management Pattern Guide

## Overview

This document provides standardized patterns for transaction management across ScraperSky, addressing the architectural issues identified during the audit.

## Core Pattern: Router-Owned Transactions

The most important rule: **Routers own transaction boundaries, services use the provided session.**

### Key Principles

1. **Router Responsibility**: Routers create and manage transaction boundaries using explicit `async with session.begin()` blocks
2. **Service Simplicity**: Services receive session objects and use them directly without managing transactions
3. **Background Tasks**: Background tasks create their own sessions; never reuse sessions from requests
4. **Session Flow**: Session objects flow from routers → services → repositories
5. **Standardized Decorators**: Use the `@managed_transaction` decorator for service methods

## Background Task Session Management

Background tasks are a special exception to the "services don't manage transactions" rule because:

1. They run after HTTP response has been sent
2. They cannot reuse the request's session
3. They need session/transaction management for reliability

### Background Task Implementation Pattern

```python
async def background_task_method(param1, param2, session: Optional[AsyncSession] = None):
    """
    Background task implementation with proper session management.

    IMPORTANT: This method creates its own session when session=None and manages
    transaction boundaries as an exception to the general pattern.

    Session Handling:
    - If session=None (default for background tasks): creates and manages own session
    - If session is provided: respects existing transaction state
    - Error recovery uses separate session management
    """
    # Import session factory
    from ...db.session import async_session

    # Create new session if none provided
    own_session = session is None
    if own_session:
        session_ctx = async_session()
    else:
        session_ctx = session

    try:
        # Use session appropriately based on ownership
        if own_session:
            async with session_ctx as session_obj:
                async with session_obj.begin():
                    # Do work within transaction...
        else:
            # Use provided session with transaction awareness
            in_transaction = session_ctx.in_transaction()
            if not in_transaction:
                async with session_ctx.begin():
                    # Create transaction if needed...
            else:
                # Use existing transaction...

    except Exception as e:
        # Error handling with proper session management
        try:
            if own_session:
                # Create new session for error recovery
                async with async_session() as error_session:
                    async with error_session.begin():
                        # Update job status, log error, etc.
            else:
                # Use existing session with new transaction
                async with session_ctx.begin():
                    # Update job status, log error, etc.
        except Exception as inner_e:
            # Log inner exception
            pass
```

### Key Rules for Background Tasks

1. **Default to None**: Background task methods should default `session=None`
2. **Session Creation**: Create a new session when `session is None`
3. **Transaction Awareness**: Always check transaction state with `session.in_transaction()`
4. **Error Handling**: Use separate sessions/transactions for error recovery
5. **Documentation**: Clearly document the exception pattern in method docstrings
6. **Testing**: Create specific tests for background task session handling

This exception pattern ensures background tasks can operate reliably while maintaining architectural consistency with the rest of the application.

## Implementation Patterns

### Pattern 1: Router with Transaction Boundary

```python
@router.post("/endpoint")
async def create_entity(
    request: EntityCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    # Create transaction boundary
    async with session.begin():
        # Call service, passing the session
        entity = await entity_service.create_entity(session, request.data)

    # Return response outside transaction
    return EntityResponse.from_entity(entity)
```

### Pattern 2: Service with Managed Transaction

```python
class EntityService:
    @managed_transaction
    async def create_entity(self, session: AsyncSession, data: dict) -> Entity:
        # Use session directly, don't manage transactions
        entity = Entity(**data)
        session.add(entity)
        await session.flush()
        return entity
```

### Pattern 3: Background Task with Own Session

```python
async def process_background_task(task_id: str, data: dict):
    # Always create a new session for background tasks
    async with async_session_factory() as task_session:
        # Use explicit transaction blocks
        async with task_session.begin():
            # Call service with task_session
            result = await service.process(task_session, data)
```

## Common Anti-Patterns to Avoid

### Anti-Pattern 1: Nested Transactions

```python
# BAD EXAMPLE - DON'T DO THIS
@router.post("/endpoint")
async def create_entity(session: AsyncSession = Depends(get_session)):
    async with session.begin():  # Router starts transaction
        await service.create(session)  # Service starts another transaction
```

### Anti-Pattern 2: Using Session Context Manager as Session

```python
# BAD EXAMPLE - DON'T DO THIS
session = get_session()  # This returns a context manager, not a session!
await session.execute(query)  # Will fail with AttributeError
```

### Anti-Pattern 3: Reusing Request Sessions in Background Tasks

```python
# BAD EXAMPLE - DON'T DO THIS
@router.post("/endpoint")
async def create_entity(session: AsyncSession = Depends(get_session)):
    # This session might be closed when the background task runs
    background_tasks.add_task(process_task, session=session)
```

## Job Service Specific Patterns

The job service requires special attention for correct handling of job IDs:

1. **Job Creation**: Always explicitly set the `job_id` field when creating jobs
2. **Job Retrieval**: Query using the `job_id` field, not the numeric `id` field
3. **Background Tasks**: Create dedicated sessions for background processing

```python
# CORRECT EXAMPLE
async def create_job(job_id: str, data: dict):
    job_data = {
        "job_id": uuid.UUID(job_id),  # Explicitly set job_id
        "job_type": "task_type",
        "status": "pending",
        "tenant_id": data.get("tenant_id")
    }

    async with task_session.begin():
        job = await job_service.create(task_session, job_data)
```

## Implementation Status

This pattern has been successfully applied to:

1. Google Maps API router and job service
2. Job Service core methods
3. Background task processing

## Upcoming Work

The remaining routers that need this pattern applied are listed in `1.4-TRANSACTION_FIX_ROUTES.md`.
