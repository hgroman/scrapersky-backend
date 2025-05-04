# Background Tasks with SQLAlchemy in FastAPI

## Technical Reference

This document provides a detailed technical reference for implementing background tasks that use SQLAlchemy in FastAPI applications. It addresses the common `MissingGreenlet` error and provides a proven pattern for reliable background processing.

## The Problem: MissingGreenlet Error

SQLAlchemy's async mode uses greenlets to manage async context, which can cause problems in FastAPI background tasks. The error typically looks like this:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
```

This error occurs because:

1. FastAPI's background tasks run in a different context than the request handling code
2. SQLAlchemy requires proper greenlet context for async operations
3. Background tasks attempt to use SQLAlchemy's async methods outside their proper context

## The Solution: Isolated Session Management Pattern

Our solution involves a specific pattern that addresses these issues:

1. Using isolated, short-lived sessions for each database operation
2. Maintaining a simple, linear control flow
3. Implementing thorough error handling for each operation

### Principles of the Pattern

1. **One Operation, One Session**

   - Create a new session for each discrete database operation
   - Keep session lifecycles short and focused
   - Always use `get_background_session()` designed for background tasks

2. **Linear Control Flow**

   - Process items sequentially rather than with nested async operations
   - Avoid complex async structures that share database connections
   - Maintain clear, predictable execution paths

3. **Comprehensive Error Handling**
   - Catch exceptions for each operation individually
   - Use new sessions for error recovery and status updates
   - Log detailed error information

## Implementation Guide

### Core Pattern

```python
async def background_task_function(task_id: str, items: List[str], user_id: str):
    """Background task with proper SQLAlchemy async context management."""
    logger.info(f"Starting task processing for {len(items)} items")

    # Step 1: Update status to processing with dedicated session
    try:
        async with get_background_session() as session:
            task = await Task.get_by_id(session, task_id)
            if task:
                task.status = "processing"
                task.start_time = datetime.now()
                await session.flush()
                logger.info(f"Updated task {task_id} status to processing")
    except Exception as e:
        logger.error(f"Error updating task status: {str(e)}", exc_info=True)
        # Continue processing even if update fails

    # Step 2: Process items with isolated sessions for each
    completed = 0
    failed = 0

    for item in items:
        try:
            # Process item with its own dedicated session
            await process_item_with_own_session(item, user_id)

            # Update progress with a new dedicated session
            completed += 1
            try:
                async with get_background_session() as session:
                    task = await Task.get_by_id(session, task_id)
                    if task:
                        task.completed_count = completed
                        await session.flush()
            except Exception as update_error:
                logger.error(f"Error updating progress: {str(update_error)}")

        except Exception as e:
            # Handle item processing failure
            failed += 1
            logger.error(f"Error processing item {item}: {str(e)}", exc_info=True)

            # Update error status with a new dedicated session
            try:
                async with get_background_session() as session:
                    task = await Task.get_by_id(session, task_id)
                    if task:
                        task.failed_count = failed
                        task.last_error = f"Error processing item {item}: {str(e)}"
                        await session.flush()
            except Exception as update_error:
                logger.error(f"Error updating error status: {str(update_error)}")

    # Step 3: Update final status with dedicated session
    try:
        async with get_background_session() as session:
            task = await Task.get_by_id(session, task_id)
            if task:
                # Determine final status
                if failed == 0:
                    task.status = "completed"
                elif completed == 0:
                    task.status = "failed"
                else:
                    task.status = "partial"

                task.end_time = datetime.now()
                await session.flush()
                logger.info(f"Updated task {task_id} status to {task.status}")
    except Exception as e:
        logger.error(f"Error updating final status: {str(e)}", exc_info=True)

    logger.info(f"Task processing completed: {completed} succeeded, {failed} failed")
```

### Process Item Function

The `process_item_with_own_session` function follows the same pattern:

```python
async def process_item_with_own_session(item: str, user_id: str):
    """Process a single item with its own session."""
    try:
        async with get_background_session() as session:
            # Perform database operations
            item_record = await Item.get_by_name(session, item)
            if not item_record:
                item_record = Item(name=item, created_by=user_id)
                session.add(item_record)

            # Process the item
            item_record.status = "processing"
            await session.flush()

            # Perform actual processing
            result = await some_external_api_call(item)

            # Update with results
            item_record.status = "completed"
            item_record.result = result
            await session.flush()

        return True
    except Exception as e:
        logger.error(f"Error processing item {item}: {str(e)}", exc_info=True)
        raise  # Re-raise to allow the parent function to handle it
```

## How to Use in FastAPI

In your FastAPI application, use the background task as follows:

```python
@app.post("/process")
async def process_batch(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_dependency)
):
    # Create task record in application context
    task_id = str(uuid.uuid4())

    # Create task in the database within a transaction
    async with session.begin():
        task = Task(
            id=task_id,
            status="pending",
            item_count=len(request.items)
        )
        session.add(task)

    # Add the background task - this is the key part
    background_tasks.add_task(
        background_task_function,
        task_id=task_id,
        items=request.items,
        user_id=request.user_id
    )

    # Return immediate response
    return {"task_id": task_id, "status": "pending"}
```

## Key Requirements

1. **Session Factory**

   You need a specialized session factory for background tasks:

   ```python
   @asynccontextmanager
   async def get_background_session() -> AsyncSession:
       """Get a session specifically configured for background tasks."""
       session = background_session_factory()
       try:
           yield session
           await session.commit()
       except Exception:
           await session.rollback()
           raise
       finally:
           await session.close()
   ```

2. **Connection Parameters**

   The database connection parameters must be set correctly:

   ```python
   connect_args = {
       "statement_cache_size": 0,
       "prepared_statement_cache_size": 0,
       "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
       "server_settings": {
           "statement_cache_size": "0"  # As string in server_settings!
       }
   }
   ```

3. **Error Handling**

   Always implement proper error handling:

   - Catch all exceptions in each discrete operation
   - Log detailed error information
   - Use new sessions for status updates after errors
   - Ensure errors in one item don't prevent processing of others

## Common Pitfalls

1. **Reusing Sessions**

   - **Incorrect**: Reusing the same session for multiple operations
   - **Correct**: Create a new session for each discrete operation

2. **Complex Async Flow**

   - **Incorrect**: Nesting async operations that share database connections
   - **Correct**: Process items sequentially with clean, linear control flow

3. **Inadequate Error Handling**

   - **Incorrect**: Allowing errors in one item to prevent processing of others
   - **Correct**: Catch exceptions for each item and continue processing

4. **Lack of Status Updates**
   - **Incorrect**: Only updating status at the beginning and end
   - **Correct**: Update status after each operation with a new session

## Testing Background Tasks

1. **Normal Flow Test**

   ```python
   @pytest.mark.asyncio
   async def test_background_task_normal_flow():
       # Arrange
       task_id = str(uuid.uuid4())
       await create_test_task(task_id)
       items = ["item1", "item2"]

       # Act
       await background_task_function(task_id, items, "test_user")

       # Assert
       task = await get_task(task_id)
       assert task.status == "completed"
       assert task.completed_count == 2
       assert task.failed_count == 0
   ```

2. **Error Handling Test**

   ```python
   @pytest.mark.asyncio
   async def test_background_task_error_handling():
       # Arrange
       task_id = str(uuid.uuid4())
       await create_test_task(task_id)
       items = ["good_item", "bad_item"]  # bad_item will cause an error

       # Mock the process_item function to fail for bad_item
       with patch("your_module.process_item_with_own_session") as mock_process:
           async def mock_implementation(item, user_id):
               if item == "bad_item":
                   raise ValueError("Test error")
               return True

           mock_process.side_effect = mock_implementation

           # Act
           await background_task_function(task_id, items, "test_user")

       # Assert
       task = await get_task(task_id)
       assert task.status == "partial"
       assert task.completed_count == 1
       assert task.failed_count == 1
       assert "bad_item" in task.last_error
   ```

## Further Reading

1. [SQLAlchemy AsyncIO Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
2. [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
3. [MissingGreenlet Error Explanation](https://sqlalche.me/e/20/xd2s)
4. [Internal Work Order 07-58: Direct Session Background Compatibility](./07-58-DIRECT-SESSION-BACKGROUND-COMPATIBILITY-WORK-ORDER.md)
5. [Internal Work Order 07-59: Background Task Standardization](./07-59-BACKGROUND-TASK-STANDARDIZATION-WORK-ORDER.md)
