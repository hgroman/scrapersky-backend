# Guide: Shared Scheduler Integration

**Document ID:** 24
**Date:** 2024-07-22
**Status:** Active

**CRITICAL NOTE:** For accessing application configuration (`settings`) within scheduler setup or job functions, refer to the correct import pattern documented in `28-SCHEDULER_AND_SETTINGS_PATTERNS.md`. Failure to import the `settings` instance correctly will lead to `AttributeError`.

## Purpose

This document details the integration pattern for using the **single shared `APScheduler` instance** across the ScraperSky application.

**Document ID:** 24-SHARED_SCHEDULER_INTEGRATION_GUIDE
**Created:** April 2025
**Author:** Gemini Assistant
**Related Documents:**

- `project-docs/20-BackGround-Task-Seperation-of-Concerns/20.1-Word-Order.md` (Details the shared scheduler refactoring)
- `src/scheduler_instance.py` (Defines the shared scheduler)
- `src/main.py` (Integrates and runs the scheduler)
- `src/config/settings.py` (Handles environment variable configuration)
- `README.md` (Project setup, environment variables)
- `.env` / `docker-compose.yml` (Environment variable definitions)

## 1. Overview

This application utilizes a single, shared `AsyncIOScheduler` instance (defined in `src/scheduler_instance.py`) to manage all recurring background tasks. This centralized approach simplifies management and monitoring. Adding a new background task involves creating a dedicated service module, defining the task logic, creating a setup function to register the job with the shared scheduler, and integrating this setup into the application's startup sequence in `src/main.py`.

## 2. Prerequisites

- Familiarity with Python `asyncio`.
- Understanding of APScheduler concepts (jobs, triggers).
- Access to the project codebase and understanding of its structure (`src/services`, `src/models`, `src/session`, `src/main.py`).
- Knowledge of how environment variables are managed via `.env`, `docker-compose.yml`, and accessed through `src/config/settings.py`.

## 3. Step-by-Step Guide

Follow these steps to add a new scheduled background task:

**Step 1: Create the Service Module File**

- Create a new Python file within the `src/services/` directory. Name it descriptively based on the task.
- Example: `src/services/new_report_generator_scheduler.py`

**Step 2: Define the Core Task Logic Function**

- Within your new service module, define an `async` function that contains the actual logic your background task needs to perform.
- This function should handle its own database sessions (using `get_background_session`), error handling, and logging.
- **Crucially:** Ensure this function handles exceptions gracefully. Uncaught exceptions within the task can prevent the scheduler job instance from completing, potentially blocking future runs if `max_instances=1`. Log errors clearly and consider marking relevant database records as 'failed'.

```python
# Example: src/services/new_report_generator_scheduler.py
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.session.async_session import get_background_session # Correct path needed
from src.config.settings import settings # For accessing config like batch size
from datetime import datetime # Added for batch_id example

logger = logging.getLogger(__name__)

async def generate_daily_report():
    """
    Core logic for the new background task.
    Fetches data and generates a report.
    """
    batch_id = f"report_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"--- Starting Report Generation Batch {batch_id} ---")
    processed_count = 0
    failed_count = 0

    # Use a background session for database operations
    session: AsyncSession = await anext(get_background_session()) # Ensure anext is correctly used/imported if needed
    try:
        # Ensure operations are within a transaction if needed
        async with session.begin():
            # 1. Fetch necessary data using ORM (e.g., from models)
            # stmt = select(SomeModel).where(...)
            # results = await session.execute(stmt)
            # items_to_process = results.scalars().all()
            items_to_process = [] # Placeholder

            if not items_to_process:
                logger.info("No items found to generate reports for in this batch.")
                return # Exit cleanly if nothing to do

            # 2. Process each item
            for item in items_to_process:
                try:
                    # Perform report generation logic
                    logger.debug(f"Processing item {getattr(item, 'id', 'N/A')} for report.") # Safer access to id
                    # ... report generation logic ...
                    # Mark item as processed in memory (ORM object)
                    # item.report_status = 'generated'
                    processed_count += 1
                    await asyncio.sleep(0.1) # Simulate work

                except Exception as item_error:
                    logger.error(f"Failed to generate report for item {getattr(item, 'id', 'N/A')}: {item_error}", exc_info=True)
                    # Mark item as failed in memory (ORM object)
                    # item.report_status = 'failed'
                    # item.error_message = str(item_error)
                    failed_count += 1
                    # Decide whether to continue processing other items or stop the batch
                    # continue

            # 3. ORM updates are flushed/committed automatically by session.begin()
            logger.info("Report generation batch processing complete (in-memory updates prepared).")

    except Exception as batch_error:
        logger.error(f"Critical error during report generation batch {batch_id}: {batch_error}", exc_info=True)
        # session.begin() handles rollback automatically on exception
        # Consider adding specific monitoring alerts here
    finally:
        # Session closure might be handled by get_background_session generator context
        # await session.close() # If needed
        logger.info(f"--- Finished Report Generation Batch {batch_id} --- Processed: {processed_count}, Failed: {failed_count}")

# (Setup function will be defined below)
```

**Step 3: Define the Setup Function**

- In the same service module file, define a **synchronous** function (e.g., `setup_new_report_scheduler`) responsible for adding the task logic function to the shared scheduler.
- Import the shared `scheduler` instance.
- Use environment variables (via `settings` from `src/config/settings.py`) to configure the job's trigger (interval, cron schedule), job ID, and other parameters like `max_instances`. **Strongly Recommended:** Keep `max_instances=1` unless you have implemented robust locking mechanisms within your task logic to handle concurrency.

```python
# Example: src/services/new_report_generator_scheduler.py (Continued)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger # Example if needed
from datetime import datetime, time # Example for cron

# Import the SINGLE shared scheduler instance
from src.scheduler_instance import scheduler

# Define the core task logic function (generate_daily_report) above this point

def setup_new_report_scheduler():
    """
    Adds the report generation job to the shared scheduler instance.
    Reads configuration from settings.
    """
    job_id = 'generate_daily_report_job'
    try:
        # Ensure settings are imported correctly at the module level if needed
        # from src.config.settings import settings
        interval_minutes = settings.REPORT_SCHEDULER_INTERVAL_MINUTES
        max_instances = settings.REPORT_SCHEDULER_MAX_INSTANCES
        grace_time = settings.REPORT_SCHEDULER_MISFIRE_GRACE_TIME

        logger.info(f"Setting up '{job_id}' with interval: {interval_minutes} minutes, max_instances: {max_instances}, grace: {grace_time}s")

        # Example: Run every X minutes
        trigger = IntervalTrigger(minutes=interval_minutes)

        # Example: Run daily at a specific time (e.g., 3:00 AM UTC)
        # trigger = CronTrigger(hour=3, minute=0, timezone='UTC')

        scheduler.add_job(
            generate_daily_report, # The async function containing the core logic
            trigger=trigger,
            id=job_id,
            name=f"Generate Daily Reports (interval: {interval_minutes}m)",
            replace_existing=True,
            max_instances=max_instances,
            misfire_grace_time=grace_time # Time allowed for delayed run
        )
        logger.info(f"Job '{job_id}' added to the shared scheduler.")

    except AttributeError as e:
        logger.error(f"Missing setting required for job '{job_id}'. Ensure REPORT_SCHEDULER settings are in config: {e}")
    except Exception as e:
        logger.exception(f"Failed to set up job '{job_id}': {e}")

```

**Step 4: Configure Settings**

- Add the necessary environment variable configurations to `src/config/settings.py`. Define sensible defaults.
- Ensure these variables are defined in your `.env` file and/or `docker-compose.yml` as needed.

```python
# Example: src/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional # Added for Optional

class Settings(BaseSettings):
    # ... other settings ...

    # New Report Scheduler Settings
    REPORT_SCHEDULER_INTERVAL_MINUTES: int = 60 # Default: Run every hour
    REPORT_SCHEDULER_MAX_INSTANCES: int = 1 # Default: Strongly recommend 1
    REPORT_SCHEDULER_MISFIRE_GRACE_TIME: Optional[int] = 60 # Default: Allow 60s delay (Optional type allows None)

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
```

**Step 5: Integrate into `src/main.py`**

- Open `src/main.py`.
- Import your new setup function from the service module you created.
- Within the `lifespan` async context manager function, call your setup function _before_ the `scheduler.start()` call.

```python
# Example: src/main.py (Simplified)
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Import the shared scheduler instance
from .scheduler_instance import scheduler

# Import setup functions for ALL scheduler services
from .services.domain_scheduler import setup_domain_scheduler
from .services.sitemap_scheduler import setup_sitemap_scheduler
from .services.domain_sitemap_submission_scheduler import setup_domain_sitemap_submission_scheduler
# >>> Import your new setup function <<<
# Ensure the path is correct based on your file location
from .services.new_report_generator_scheduler import setup_new_report_scheduler

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application Startup...")
    try:
        # Setup ALL scheduled jobs by calling their setup functions
        logger.info("Setting up scheduled jobs...")
        setup_domain_scheduler()
        setup_sitemap_scheduler()
        setup_domain_sitemap_submission_scheduler()
        # >>> Call your new setup function <<<
        setup_new_report_scheduler()
        logger.info("All scheduled jobs added.")

        # Start the shared scheduler
        logger.info("Starting the shared scheduler...")
        scheduler.start()
        if scheduler.running:
            logger.info("Shared scheduler started successfully.")
        else:
             logger.error("Shared scheduler failed to start!")

    except Exception as e:
        logger.exception("Error during scheduler setup or startup:")

    yield # Application runs here

    # Shutdown
    logger.info("Application Shutdown...")
    if scheduler.running:
        logger.info("Shutting down the shared scheduler...")
        scheduler.shutdown()
        logger.info("Shared scheduler shut down.")
    else:
        logger.warning("Scheduler was not running at shutdown.")

app = FastAPI(lifespan=lifespan) # Removed ellipsis for clarity
# ... rest of main.py ...

```

## 4. Configuration Best Practices

- **Use Environment Variables:** Always configure intervals, batch sizes, `max_instances`, etc., via `settings.py` backed by environment variables. Avoid hardcoding values in the service modules.
- **Sensible Defaults:** Provide reasonable default values in `settings.py` so the application can run without every single variable being explicitly set.
- **`max_instances=1`:** As emphasized, stick to `max_instances=1` unless you have a very specific reason and have implemented measures (like database row-level locking with `SKIP LOCKED`) within your task logic to handle concurrent execution safely.
- **Error Handling:** Implement robust try/except blocks within your core task logic function (`generate_daily_report` in the example) to catch errors, log them comprehensively, potentially update database status to 'failed', and ensure the function exits cleanly so the job instance completes.

## 5. Testing and Verification

1.  **Rebuild & Restart:** After adding the code, rebuild your Docker container (`docker-compose up -d --build scrapersky`).
2.  **Check Startup Logs:** Monitor the application startup logs (`docker-compose logs scrapersky`). Look for the INFO messages confirming your new setup function was called and the job was added to the scheduler. Check for any errors during setup.
3.  **Verify via Dev Tools:** Use the development endpoint `GET /api/v3/dev-tools/scheduler_status`. Check if your new job ID appears in the list with the correct trigger and next run time.
4.  **Monitor Execution Logs:** Once the scheduled time arrives, check the logs again (`docker-compose logs --tail=200 scrapersky | cat`) for the log messages from within your core task logic function (`generate_daily_report` in the example) to confirm it ran as expected. Check for any error messages.

## 6. Conclusion

By following these steps, developers can reliably add new background tasks that integrate correctly with the application's shared scheduling system, leveraging centralized management and monitoring while adhering to project standards. Remember to prioritize robust error handling within your task logic to prevent blockages.
