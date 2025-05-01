# Scheduled Tasks with APScheduler in FastAPI

## Quick Reference

This guide provides the essential patterns for implementing scheduled recurring tasks in FastAPI using APScheduler.

## Core Implementation Pattern

### 1. Install APScheduler

```bash
pip install apscheduler
```

### 2. Create Scheduler Module

```python
# src/services/scheduler.py

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text

from src.session.async_session import get_background_session

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def process_data(limit: int = 10):
    """Process pending data with isolated sessions."""
    # Step 1: Query data with dedicated session
    try:
        async with get_background_session() as session:
            query = text("SELECT id FROM items WHERE status = 'pending' LIMIT :limit")
            query = query.execution_options(prepared=False)  # Critical for Supavisor
            result = await session.execute(query, {"limit": limit})
            items = result.fetchall()
    except Exception as e:
        logger.error(f"Error fetching data: {e}", exc_info=True)
        return

    # Step 2: Process each item with isolated sessions
    for item in items:
        item_id = item.id

        # Update status to processing
        try:
            async with get_background_session() as session:
                update = text("UPDATE items SET status = 'processing' WHERE id = :id")
                update = update.execution_options(prepared=False)
                await session.execute(update, {"id": item_id})
        except Exception as e:
            logger.error(f"Error updating item {item_id}: {e}", exc_info=True)
            continue

        # Process and update with results
        try:
            # Your processing logic here
            result = {"status": "success"}

            # Update with success status
            async with get_background_session() as session:
                update = text("UPDATE items SET status = 'completed', data = :data WHERE id = :id")
                update = update.execution_options(prepared=False)
                await session.execute(update, {"id": item_id, "data": result})

        except Exception as e:
            # Update with error status
            try:
                async with get_background_session() as session:
                    update = text("UPDATE items SET status = 'error', last_error = :error WHERE id = :id")
                    update = update.execution_options(prepared=False)
                    await session.execute(update, {"id": item_id, "error": str(e)})
            except Exception as update_error:
                logger.error(f"Error updating error status: {update_error}", exc_info=True)

def setup_scheduler():
    """Configure and return the scheduler."""
    # Schedule jobs
    scheduler.add_job(
        process_data,
        'interval',
        minutes=5,
        id='process_pending_data',
        kwargs={'limit': 10},
        replace_existing=True
    )

    logger.info("Scheduler configured")
    return scheduler

def shutdown_scheduler():
    """Shut down the scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler shut down")
```

### 3. Integrate with FastAPI (Modern Lifespan Pattern)

```python
# src/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.services.scheduler import setup_scheduler, shutdown_scheduler

# Lifespan pattern (recommended for FastAPI 0.95.0+)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Define startup and shutdown events using the modern lifespan pattern."""
    # Startup: initialize and start scheduler
    scheduler = setup_scheduler()
    scheduler.start()
    app.logger.info("Scheduler started")

    yield  # Application is running

    # Shutdown: stop the scheduler
    shutdown_scheduler()
    app.logger.info("Scheduler shut down")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)
```

### 4. Add Diagnostic Endpoint

```python
# src/routers/dev.py

from fastapi import APIRouter
from src.services.scheduler import process_data

router = APIRouter(prefix="/api/v3/dev", tags=["dev-tools"])

@router.get("/process-data")
async def trigger_processing(limit: int = 5):
    """Manually trigger data processing."""
    await process_data(limit=limit)
    return {"message": "Processing triggered"}
```

## Critical Database Patterns

1. **Isolated Sessions**: Use a new session for each database operation

   ```python
   async with get_background_session() as session:
       # Only ONE database operation per session context
   ```

2. **Execution Options**: Always set for raw SQL with Supavisor

   ```python
   query = text("SELECT ...").execution_options(prepared=False)
   ```

3. **Error Handling**: Isolate and handle errors at each step
   ```python
   try:
       async with get_background_session() as session:
           # Database operation
   except Exception as e:
       logger.error(f"Operation failed: {e}", exc_info=True)
       # Error recovery logic
   ```

## Common Job Types

```python
# Interval job (every 5 minutes)
scheduler.add_job(process_data, 'interval', minutes=5)

# Cron job (midnight every day)
scheduler.add_job(daily_job, 'cron', hour=0, minute=0)

# One-time job (1 hour from now)
from datetime import datetime, timedelta
run_time = datetime.now() + timedelta(hours=1)
scheduler.add_job(future_job, 'date', run_date=run_time)
```

## Best Practices

1. **Critical Transaction Handling:** Database operations within scheduled jobs **MUST** use `get_background_session` and strictly adhere to the transaction patterns detailed in `Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md`. Specifically, use the `async with get_background_session() as session:` context manager to control the transaction, and **never** commit or rollback the session within helper functions/services called by the job. The context manager handles the final commit/rollback.
2. **Avoid Session Sharing**: _While the primary transaction should span the logical unit of work for the batch_, avoid passing the same session between completely independent steps _if_ a failure in one shouldn't roll back the others. For simple loops processing items where batch atomicity is desired (all succeed or all fail), using the single session from the main context manager is correct (as per Guide 13).
3. **Keep Transactions Short**: If processing individual items completely independently (failure of one doesn't affect others), consider fetching IDs first, then processing each item with its _own_ separate `async with get_background_session()` block. (This contradicts the batch atomicity pattern in Guide 13, use the pattern appropriate for the task's requirements).
4. **Implement Robust Error Handling**: Catch exceptions at every level.
5. **Use Linear Control Flow**: Process items sequentially unless parallel processing is explicitly designed and managed.
6. **Always Use ORM (Primary)** or Raw SQL Execution Options: Prefer the SQLAlchemy ORM (`select`, `update`). If raw SQL is absolutely necessary (rare), set execution options: `text(...).execution_options(prepared=False)`.
7. **Set Job ID**: Makes it easier to reference and replace jobs.
8. **Close Resources**: Ensure any opened non-session resources are properly closed.
9. **Logging**: Add comprehensive logging for operations.
10. **Implement Diagnostic Endpoints**: For manual triggering and testing.
11. **Use Modern Lifespan Pattern**: Avoid deprecated on_event handlers.

## Troubleshooting

If you encounter the `MissingGreenlet` error, check:

1. Are you using a new session for each operation?
2. Is the session properly managed with context managers?
3. Have you added execution options for raw SQL?
4. Are you maintaining linear control flow?

### Common Database Errors

1. **Column not found errors**:

   ```
   sqlalchemy.exc.ProgrammingError: column "error_message" of relation "domains" does not exist
   ```

   Always verify column names match your actual database schema. Common fixes:

   - Use `last_error` instead of `error_message` for storing error information
   - Check the database schema with inspection tools before implementing
   - Always test error handling paths, not just the happy path

## Legacy Integration Pattern (Deprecated)

> **⚠️ DEPRECATED:** The following pattern uses deprecated `on_event` handlers. Use the lifespan pattern above instead.

```python
# DEPRECATED: Old-style integration
@app.on_event("startup")
async def startup_event():
    """Start scheduler with application."""
    global scheduler
    scheduler = setup_scheduler()
    scheduler.start()
    app.logger.info("Scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Shut down scheduler with application."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        app.logger.info("Scheduler shut down")
```

## Related Documents

- [Background Task SQLAlchemy Pattern](./21-BACKGROUND-TASK-SQLALCHEMY-PATTERN.md)
- [Database Connection Standards](./07-DATABASE_CONNECTION_STANDARDS.md)
- [Full Pattern Documentation](../project-docs/10-architectural-patterns/01-SCHEDULED-TASKS-APSCHEDULER-PATTERN.md)
