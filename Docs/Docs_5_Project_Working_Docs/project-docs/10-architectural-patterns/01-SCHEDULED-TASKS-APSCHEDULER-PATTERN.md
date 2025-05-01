# Scheduled Tasks with APScheduler in FastAPI

## Technical Reference

This document provides a detailed technical reference for implementing scheduled recurring tasks using APScheduler within FastAPI applications. It follows the same database session management principles as the background tasks pattern to avoid the `MissingGreenlet` error and ensure reliable scheduled processing.

## Introduction to Scheduled Tasks

Unlike one-off background tasks that are triggered by specific API requests, scheduled tasks need to run periodically based on a defined schedule, regardless of API activity. Common use cases include:

1. Processing queued items at regular intervals
2. Performing periodic maintenance operations
3. Syncing data with external systems
4. Cleaning up stale records

## APScheduler Overview

APScheduler (Advanced Python Scheduler) is a Python library that lets you schedule jobs to run at specific times or intervals. It's well-suited for FastAPI applications because:

1. It can run in-process alongside your API server
2. It supports various scheduling patterns (interval, cron, one-time)
3. It works well with asyncio for non-blocking operations
4. It's lightweight and easy to integrate

## Implementation Pattern

### Core Components

1. **Scheduler Configuration**: Set up APScheduler with the appropriate job store and executor
2. **FastAPI Integration**: Hook into FastAPI's lifecycle events to start and stop the scheduler
3. **Task Functions**: Implement processing functions following the isolated session pattern
4. **Diagnostic Endpoints**: Add endpoints to manually trigger or check scheduled tasks

### Example Implementation

#### 1. Create the Scheduler Module

Create a module for your scheduled tasks (e.g., `src/services/domain_scheduler.py`):

```python
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.session.async_session import get_background_session
from src.scraper.metadata_extractor import MetadataExtractor

# Configure logger
logger = logging.getLogger(__name__)

# Create a scheduler instance
scheduler = AsyncIOScheduler()

async def process_pending_domains(limit: int = 10) -> Dict[str, Any]:
    """
    Process domains with 'pending' status.

    This function follows the isolated session pattern to avoid MissingGreenlet errors.
    Each database operation uses its own dedicated session.

    **Note:** While this function handles the scheduling logic (querying for pending
    items, updating status), the actual core task (metadata extraction in this example)
    is delegated to a dedicated service class, `MetadataExtractor`, imported from
    `src.scraper.metadata_extractor.py`. This separation of concerns (scheduler
    orchestrates, service executes core logic) is a recommended practice within
    scheduled job functions.

    Args:
        limit: Maximum number of domains to process

    Returns:
        Dict with results summary
    """
    results = {
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "domains": []
    }

    # Step 1: Get pending domains using a dedicated session
    pending_domains = []
    try:
        async with get_background_session() as session:
            # Use raw SQL with proper execution options for Supavisor compatibility
            query = text("""
                SELECT id, domain, tenant_id
                FROM domains
                WHERE status = 'pending'
                LIMIT :limit
            """).execution_options(prepared=False)

            result = await session.execute(query, {"limit": limit})
            pending_domains = result.fetchall()
            logger.info(f"Found {len(pending_domains)} pending domains to process")
    except Exception as e:
        logger.error(f"Error fetching pending domains: {e}", exc_info=True)
        return results

    # Initialize metadata extractor
    metadata_extractor = MetadataExtractor()

    # Step 2: Process each domain with isolated sessions
    for domain_row in pending_domains:
        domain_id = domain_row.id
        domain_name = domain_row.domain
        tenant_id = domain_row.tenant_id

        results["domains"].append({"domain_id": domain_id, "domain": domain_name})

        # Update domain status to processing with a dedicated session
        try:
            async with get_background_session() as session:
                update_query = text("""
                    UPDATE domains
                    SET status = 'processing', processing_started_at = NOW()
                    WHERE id = :domain_id
                """).execution_options(prepared=False)

                await session.execute(update_query, {"domain_id": domain_id})
                logger.info(f"Updated domain {domain_name} to processing status")
        except Exception as e:
            logger.error(f"Error updating domain {domain_name} status to processing: {e}", exc_info=True)
            continue

        # Process the domain and update with results using dedicated sessions
        try:
            # Extract domain metadata
            metadata = await metadata_extractor.extract_metadata(domain_name)

            # Update domain with a dedicated session
            async with get_background_session() as session:
                update_query = text("""
                    UPDATE domains
                    SET
                        status = 'completed',
                        processing_completed_at = NOW(),
                        metadata = :metadata,
                        last_processed = NOW()
                    WHERE id = :domain_id
                """).execution_options(prepared=False)

                await session.execute(
                    update_query,
                    {
                        "domain_id": domain_id,
                        "metadata": metadata
                    }
                )

            results["processed"] += 1
            results["successful"] += 1
            logger.info(f"Successfully processed domain {domain_name}")

        except Exception as e:
            # Update domain with error status using a dedicated session
            try:
                async with get_background_session() as session:
                    error_update = text("""
                        UPDATE domains
                        SET
                            status = 'error',
                            processing_completed_at = NOW(),
                            error_message = :error_message
                        WHERE id = :domain_id
                    """).execution_options(prepared=False)

                    await session.execute(
                        error_update,
                        {
                            "domain_id": domain_id,
                            "error_message": str(e)
                        }
                    )

                results["processed"] += 1
                results["failed"] += 1
                logger.error(f"Error processing domain {domain_name}: {e}", exc_info=True)

            except Exception as update_error:
                logger.error(f"Error updating domain {domain_name} with error status: {update_error}", exc_info=True)

    # Close metadata extractor session
    await metadata_extractor.close()

    # Log summary
    logger.info(f"Domain processing completed: {results['successful']} successful, {results['failed']} failed")
    return results

def setup_scheduler():
    """Set up the scheduler with jobs and return the scheduler instance."""
    # Add jobs to the scheduler
    scheduler.add_job(
        process_pending_domains,
        'interval',
        minutes=5,
        id='process_pending_domains',
        kwargs={'limit': 10},
        replace_existing=True
    )

    logger.info("Scheduler configured with domain processing job")
    return scheduler
```

#### 2. Integrate with FastAPI Lifecycle

Update your FastAPI application (`main.py`) to start and stop the scheduler:

```python
from fastapi import FastAPI
from src.services.domain_scheduler import setup_scheduler

app = FastAPI()

# Store scheduler reference
scheduler = None

@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the application starts."""
    global scheduler
    scheduler = setup_scheduler()
    scheduler.start()
    app.logger.info("Domain processing scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Shut down the scheduler when the application stops."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        app.logger.info("Domain processing scheduler shut down")
```

#### 3. Add Diagnostic Endpoints

Add endpoints to manually trigger scheduled tasks for testing:

```python
from fastapi import APIRouter, Depends
from src.services.domain_scheduler import process_pending_domains

router = APIRouter(prefix="/api/v3/dev", tags=["dev-tools"])

@router.get("/process-pending-domains")
async def trigger_domain_processing(limit: int = 5):
    """
    Manually trigger processing of pending domains.
    This is useful for testing and debugging.
    """
    results = await process_pending_domains(limit=limit)
    return {
        "message": f"Processed {results['processed']} domains: {results['successful']} successful, {results['failed']} failed",
        "results": results
    }
```

## Session Management

The same principles apply for scheduled tasks as for background tasks:

1. **Isolated Sessions**: Each database operation should use its own session
2. **Context Management**: Always use proper async context managers for sessions
3. **Error Handling**: Implement thorough error handling for each operation
4. **Supavisor Compatibility**: Use execution options for raw SQL queries

Follow these principles to avoid the `MissingGreenlet` error:

```python
async def safe_database_operation():
    try:
        async with get_background_session() as session:
            # Your database operations here
            query = text("SELECT * FROM table WHERE condition = :value")
            query = query.execution_options(prepared=False)  # Important for Supavisor
            result = await session.execute(query, {"value": some_value})
            # Process result
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
```

## Scheduler Configuration Options

APScheduler offers flexible configuration options:

```python
scheduler = AsyncIOScheduler(
    job_defaults={
        'coalesce': False,            # Run all missed executions
        'max_instances': 1,           # Don't allow parallel instances of the same job
        'misfire_grace_time': 60      # Time window for misfires (in seconds)
    },
    timezone="UTC"                   # Use UTC for consistent scheduling
)
```

## Common Job Types

1. **Interval Jobs** - Run at fixed intervals:

```python
scheduler.add_job(
    process_function,
    'interval',
    minutes=5,                      # Run every 5 minutes
    id='process_interval_job'
)
```

2. **Cron Jobs** - Run at specific times:

```python
scheduler.add_job(
    daily_report_function,
    'cron',
    hour=0,                        # Run at midnight
    minute=0,
    id='daily_report_job'
)
```

3. **One-time Jobs** - Run once at a specific time:

```python
from datetime import datetime, timedelta

run_time = datetime.now() + timedelta(hours=1)
scheduler.add_job(
    future_function,
    'date',
    run_date=run_time,
    id='one_time_job'
)
```

## Testing Scheduled Tasks

### Manual Testing

1. Use the diagnostic endpoint to trigger the task
2. Observe logs and database updates
3. Verify expected outcomes

### Automated Testing

Test the processing function independently:

```python
@pytest.mark.asyncio
async def test_process_pending_domains():
    # Arrange: Create test domains with pending status
    await create_test_domains(status="pending", count=3)

    # Act: Run the processing function
    results = await process_pending_domains(limit=10)

    # Assert: Verify results
    assert results["processed"] == 3
    assert results["successful"] >= 0

    # Verify database state
    async with get_test_session() as session:
        query = text("SELECT status FROM domains WHERE status = 'pending'")
        result = await session.execute(query)
        remaining_pending = result.fetchall()
        assert len(remaining_pending) == 0
```

## Monitoring and Maintenance

1. **Logging**: Implement comprehensive logging for scheduled tasks
2. **Error Alerts**: Set up notifications for repeated task failures
3. **Performance Tracking**: Monitor execution time and resource usage
4. **Job Status**: Add endpoints to check scheduler status and job history

## Common Pitfalls

1. **Resource Leaks**:

   - Always close connections and sessions
   - Use context managers consistently

2. **Error Propagation**:

   - Handle errors at each step
   - Avoid letting one error break the entire schedule

3. **Long-Running Jobs**:

   - Be aware of job duration vs. schedule interval
   - Use `max_instances=1` to prevent overlapping runs

4. **Server Deployment**:

   - Multiple server instances might run the same scheduled tasks
   - Consider using a distributed scheduler for production scale

5. **Database Connection Limits**:
   - Monitor connection pool usage
   - Ensure connections are properly released

## Production Considerations

For production environments:

1. **Consider Celery**: For high-volume or demanding workloads, consider migrating to Celery
2. **Job Persistence**: Use a persistent job store (like SQLAlchemy) to survive restarts
3. **Distributed Locking**: Implement locks for tasks that shouldn't run concurrently
4. **Health Checks**: Add endpoints to verify scheduler health

## Conclusion

The APScheduler pattern provides a simple yet effective way to implement recurring tasks in your FastAPI application. By following proper session management practices, you can avoid the common `MissingGreenlet` error while maintaining a clean, maintainable codebase.

## Further Reading

1. [APScheduler Documentation](https://apscheduler.readthedocs.io/en/stable/)
2. [FastAPI Events](https://fastapi.tiangolo.com/advanced/events/)
3. [SQLAlchemy AsyncIO Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
4. [Background Task SQLAlchemy Pattern](./21-BACKGROUND-TASK-SQLALCHEMY-PATTERN.md)
5. [Internal Document: Domain Scheduler Implementation](../project-docs/07-database-connection-audit/07-62-DOMAIN-SCHEDULER-IMPLEMENTATION-COMPLETION-REPORT.md)
