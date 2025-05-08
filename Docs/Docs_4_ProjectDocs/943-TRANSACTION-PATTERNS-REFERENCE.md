# Database Transaction Patterns Reference

**Date:** 2025-03-25
**Author:** Cascade AI
**Status:** Active
**Related Document:** [Database Connection Audit Plan](./942-DATABASE-CONNECTION-AUDIT-PLAN.md)

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
    current_user: User = Depends(get_current_user)
):
    try:
        # Router explicitly creates transaction boundary
        async with session.begin():
            # Services are called within the transaction
            result = await resource_service.create_resource(
                session=session,
                data=request.data,
                user_id=current_user.id  # Pass only the user ID, not the token
            )

        # Background tasks added AFTER transaction completes
        # This prevents issues where background job runs before transaction commits
        background_tasks.add_task(
            notification_service.send_notification,
            resource_id=result.id
        )

        return result

    except Exception as e:
        # Error handling with proper logging
        logger.error(f"Error creating resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Service Responsibility (Transaction Aware)

Services are **transaction aware** but:
- Do NOT create their own transactions
- Do NOT commit or rollback transactions
- Accept session objects passed from routers
- May call other services, passing the same session

**Correct Pattern:**
```python
class ResourceService:
    async def create_resource(self, session: AsyncSession, data: dict, user_id: str):
        # Service USES the transaction but doesn't manage it
        new_resource = Resource(
            name=data["name"],
            description=data["description"],
            user_id=user_id
        )

        session.add(new_resource)

        # May call other services, passing the SAME session
        await self.tag_service.add_tags(
            session=session,
            resource=new_resource,
            tags=data.get("tags", [])
        )

        # NO commit or rollback here!
        # The router owns the transaction

        return new_resource
```

### 3. Background Task Responsibility (Own Transaction)

Background tasks are **transaction owners** for their scope:
- Create their own sessions
- Manage their own transactions
- Close their sessions when done
- Handle their own errors

**Correct Pattern:**
```python
async def process_background_job(job_id: str):
    # Create a new session for the background job
    async with AsyncSessionLocal() as session:
        try:
            # Create a transaction for the background job
            async with session.begin():
                job = await session.get(Job, job_id)
                if not job:
                    logger.error(f"Job not found: {job_id}")
                    return

                # Process the job
                job.status = "processing"
                # ... processing logic ...
                job.status = "completed"

            # Transaction is committed when exiting the context
            logger.info(f"Background job completed: {job_id}")

        except Exception as e:
            # Handle errors - transaction is automatically rolled back
            logger.error(f"Error in background job {job_id}: {str(e)}")
            # Optionally update job status outside the failed transaction
            async with session.begin():
                job = await session.get(Job, job_id)
                if job:
                    job.status = "failed"
                    job.error = str(e)
```

## Common Anti-patterns to Avoid

### 1. Service Committing Transactions

**Bad Example:**
```python
# DON'T DO THIS
class BadService:
    async def create_resource(self, session, data):
        new_resource = Resource(**data)
        session.add(new_resource)
        await session.commit()  # WRONG: Services should not commit!
        return new_resource
```

### 2. Nested Transactions

**Bad Example:**
```python
# DON'T DO THIS
@router.post("/resource")
async def create_resource(session: AsyncSession = Depends(get_session)):
    async with session.begin():  # Outer transaction
        # ... some logic ...

        # WRONG: Nested transaction
        result = await service.create_with_transaction(session, data)

        # ... more logic ...

# Service incorrectly creates nested transaction
async def create_with_transaction(session, data):
    async with session.begin():  # WRONG: Nested transaction!
        # ... implementation ...
```

### 3. Session Sharing Across Async Boundaries

**Bad Example:**
```python
# DON'T DO THIS
@router.post("/resource")
async def create_resource(session: AsyncSession = Depends(get_session)):
    async with session.begin():
        resource = await service.create_resource(session, data)

    # WRONG: Passing session to background task
    background_tasks.add_task(process_in_background, session, resource.id)
```

## Test Patterns for Transaction Management

When testing transaction management, verify:

1. **Rollback on Error**: Data changes are rolled back if an exception occurs
2. **Proper Commit**: Changes are persisted after successful completion
3. **Background Task Timing**: Background tasks don't run until after transaction commits
4. **Isolation**: Transactions are properly isolated from each other
5. **Error Handling**: Errors in services are properly propagated to routers

## References

- [SQLAlchemy Transaction Documentation](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Database Connection Audit Plan](./942-DATABASE-CONNECTION-AUDIT-PLAN.md)
