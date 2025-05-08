# Transaction Pattern Reference Guide

This document provides concrete examples of the standardized transaction handling patterns in ScraperSky. Use these patterns consistently across the codebase.

## Core Principles

1. **Routers own transactions** - Only router endpoints should begin/commit transactions
2. **Services are transaction-aware** - Services work with sessions but never start transactions
3. **Background tasks manage sessions** - Background tasks create sessions but follow same pattern

## Pattern 1: Router Endpoint with Transaction

```python
@router.post("/endpoint", response_model=ResponseModel)
async def endpoint(
    request: RequestModel,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    # Router owns the transaction boundary
    async with session.begin():
        # Call service passing the session
        result = await some_service.operation(
            session=session,
            data=request.data,
            user_id=current_user.get("id")
        )

    # Return after transaction is committed
    return result
```

## Pattern 2: Router with Background Task

```python
@router.post("/async-endpoint", response_model=AsyncResponseModel)
async def async_endpoint(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    # Create job record in a transaction
    async with session.begin():
        job = await job_service.create_job(
            session=session,
            user_id=current_user.get("id"),
            job_type="operation",
            status="pending"
        )

    # Add background task AFTER transaction commits
    # Don't pass the session to background task
    background_tasks.add_task(
        process_background_job,
        job_id=str(job.id),
        data=request.dict()
    )

    return {"job_id": str(job.id), "status": "processing"}

# Background task function - creates its own session
async def process_background_job(job_id: str, data: dict):
    # Create a new session for background task
    async with AsyncSessionLocal() as bg_session:
        try:
            # Background task manages its own transaction
            async with bg_session.begin():
                # Update job status
                job = await job_service.get_job_by_id(bg_session, job_id)
                if not job:
                    logger.error(f"Job not found: {job_id}")
                    return

                job.status = "processing"

                # Process data
                result = await some_service.process_data(
                    session=bg_session,
                    data=data
                )

                # Update job with result
                job.status = "completed"
                job.result = result

            # Transaction committed when exiting context
            logger.info(f"Background job completed: {job_id}")

        except Exception as e:
            # Handle errors - transaction is rolled back
            logger.error(f"Error in background job {job_id}: {str(e)}")
            try:
                # Create a new transaction to update job status
                async with bg_session.begin():
                    job = await job_service.get_job_by_id(bg_session, job_id)
                    if job:
                        job.status = "failed"
                        job.error = str(e)
            except Exception as update_error:
                # Log if we couldn't update the job status
                logger.error(f"Failed to update job status: {str(update_error)}")
```

## Pattern 3: Transaction-Aware Service

```python
# Service is transaction-aware but doesn't create transactions
class SomeService:
    async def operation(self, session: AsyncSession, data: dict, user_id: str):
        # Use session but don't begin/commit transactions
        # No async with session.begin():

        # Perform operations using session
        new_record = SomeModel(
            name=data.get("name"),
            description=data.get("description"),
            user_id=user_id
        )
        session.add(new_record)

        # No session.commit() - router handles that

        # May call other services, passing the same session
        related_data = await other_service.create_related(
            session=session,
            parent_id=new_record.id,
            data=data.get("related_items", [])
        )

        return {
            "id": new_record.id,
            "name": new_record.name,
            "related_items": related_data
        }
```

## Pattern 4: Error Handling with Transactions

```python
@router.post("/endpoint-with-errors", response_model=ResponseModel)
async def endpoint_with_errors(
    request: RequestModel,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    try:
        # Transaction boundary with error handling
        async with session.begin():
            # Business logic validation
            if not request.data:
                raise ValueError("Data is required")

            # Call service
            result = await some_service.operation(
                session=session,
                data=request.data,
                user_id=current_user.get("id")
            )

        # Return after successful transaction
        return result

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))

    except SQLAlchemyError as e:
        # Handle database errors
        # Transaction is automatically rolled back
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
```

## Pattern 5: Testing with Transactions

```python
# Test function with transaction handling
async def test_some_operation():
    # Create test session
    async with AsyncSessionLocal() as test_session:
        try:
            # Test within transaction that will be rolled back
            async with test_session.begin():
                # Create test data
                test_user_id = "test-user-id"
                test_data = {
                    "name": "Test Record",
                    "description": "Test Description"
                }

                # Call service directly
                result = await some_service.operation(
                    session=test_session,
                    data=test_data,
                    user_id=test_user_id
                )

                # Assert results
                assert result.get("name") == "Test Record"

                # Retrieve record to verify
                record = await test_session.get(SomeModel, result.get("id"))
                assert record is not None
                assert record.name == "Test Record"

                # Intentionally roll back by raising exception
                raise TestRollbackException("Rolling back test transaction")

        except TestRollbackException:
            # Expected exception for rollback
            pass

        # Verify transaction was rolled back
        # Create a new transaction
        async with test_session.begin():
            # Record should not exist
            record_count = await test_session.execute(
                select(func.count()).select_from(SomeModel)
                .where(SomeModel.name == "Test Record")
            )
            count = record_count.scalar_one()
            assert count == 0, "Transaction was not rolled back"
```

## Common Anti-patterns to Avoid

1. ❌ **Services creating transactions**:
   ```python
   # WRONG - Service shouldn't own transactions
   async def bad_service_method(self, data):
       async with session_factory() as session:
           async with session.begin():
               # Implementation
               await session.commit()
   ```

2. ❌ **Nested transactions**:
   ```python
   # WRONG - Creates nested transactions
   async with session.begin():
       # Some logic
       async with session.begin():  # Nested transaction!
           # More logic
   ```

3. ❌ **Committing in services**:
   ```python
   # WRONG - Services shouldn't commit
   async def bad_service_method(self, session, data):
       # Implementation
       await session.commit()  # Wrong!
   ```

4. ❌ **Passing request session to background tasks**:
   ```python
   # WRONG - Don't pass request session to background tasks
   background_tasks.add_task(process_job, session, job_id)
   ```

## References

- [Database Service Consolidation Plan](../02-database-consolidation/02-03-database-service-consolidation-plan-2025-03-23.md)
- [Implementation Guide](../02-database-consolidation/02-02-implementation-guide-2025-03-24.md)
- [Google Maps API Implementation](../../src/routers/google_maps_api.py) (reference implementation)
