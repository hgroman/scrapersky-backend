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

## Pattern 2: Service Method (Transaction-Aware)

```python
class SomeService:
    @staticmethod
    async def operation(
        session: AsyncSession,
        data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        # Service uses session but doesn't start transaction
        # It can use ORM models
        some_model = SomeModel(
            field1=data["field1"],
            field2=data["field2"],
            user_id=user_id
        )
        session.add(some_model)
        await session.flush()  # Flush but don't commit

        # Or it can use the db_service for raw SQL operations
        # which is also transaction-aware
        await db_service.execute(
            query="INSERT INTO table (col1, col2) VALUES (:val1, :val2)",
            params={"val1": data["val1"], "val2": data["val2"]}
        )

        # Return result without committing transaction
        return {"id": str(some_model.id), "status": "created"}
```

## Pattern 3: Background Task with Session Management

```python
async def process_background_task(job_id: str, data: Dict[str, Any]):
    """Background task that needs database access."""
    try:
        # Create a new session for background task
        async with async_session_factory() as bg_session:
            # Start a transaction
            async with bg_session.begin():
                # Perform database operations in transaction
                model = await some_service.operation(
                    session=bg_session,
                    data=data,
                    job_id=job_id
                )

                # The transaction will be committed automatically
                # when the context manager exits
    except Exception as e:
        logger.error(f"Error in background task: {str(e)}")
        # Handle error appropriately
```

## Pattern 4: Read-Only Endpoint (No Transaction)

```python
@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    # For read-only operations, no need to start a transaction
    item = await item_service.get_item_by_id(
        session=session,
        item_id=item_id,
        tenant_id=current_user.get("tenant_id", DEFAULT_TENANT_ID)
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item
```

## Batch Operations Example

```python
@router.post("/batch-create", response_model=BatchResponse)
async def batch_create(
    request: BatchRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    # Single transaction for all operations in the batch
    async with session.begin():
        results = []
        for item_data in request.items:
            result = await item_service.create_item(
                session=session,
                data=item_data,
                user_id=current_user.get("id")
            )
            results.append(result)

    # Return after all items are processed and transaction is committed
    return {"success": True, "items": results}
```

## Transaction Context Utility

We also provide a `transaction_context` utility in `db/session.py` that can be used when more explicit transaction control is needed:

```python
@asynccontextmanager
async def transaction_context(session: AsyncSession):
    """
    Context manager for handling transactions.

    Example:
        ```python
        async with transaction_context(session):
            # Execute database operations
            result = await session.execute(query)
        ```
    """
    try:
        async with session.begin():
            logger.debug("Transaction started")
            yield
            logger.debug("Transaction committed")
    except Exception as e:
        logger.error(f"Transaction error: {e}")
        raise
```

## Reference Implementation

For a complete implementation example, refer to the Google Maps API router:
- Router: `src/routers/google_maps_api.py`
- Services: `src/services/places/places_storage_service.py`

This implementation demonstrates:
1. Router-owned transactions
2. Transaction-aware services
3. Background task session management
4. Proper error handling

## Common Mistakes to Avoid

1. ❌ **Creating transactions in services**:
   ```python
   # WRONG!
   async def service_operation(data):
       async with session_factory() as session:
           async with session.begin():
               # Create a transaction in a service
   ```

2. ❌ **Committing inside services**:
   ```python
   # WRONG!
   async def service_operation(session, data):
       # Do something
       await session.commit()  # Services should never commit
   ```

3. ❌ **Reusing session after commit**:
   ```python
   # WRONG!
   async with session.begin():
       # First operation

   # Session already committed, can't use again
   await session.execute(query)  # This will fail
   ```

4. ❌ **Creating nested transactions**:
   ```python
   # WRONG!
   async with session.begin():
       # Parent transaction
       async with session.begin():
           # Nested transaction, this is a problem
   ```

## Transaction Testing

When writing tests for database operations, follow this pattern:

```python
@pytest.mark.asyncio
async def test_database_operation():
    async with TestingSessionLocal() as session:
        async with session.begin():
            # Set up test data

        # Start a new transaction for the actual test
        async with session.begin():
            # Perform the operation being tested
            result = await some_service.operation(session, test_data)

            # Assert without committing (transaction will be rolled back)
            assert result is not None

        # Test transaction is rolled back automatically
```
