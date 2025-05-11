# In src/main.py
import asyncio
import logging # Add logger import
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Import the shared scheduler instance (ensure it's initialized before use)
from src.schedulers import scheduler # Assuming your scheduler instance is here

# Import your workflow-specific scheduler setup function
# Example: from src.services.page_curation_scheduler import setup_page_curation_scheduler
from src.services.{workflow_name}_scheduler import setup_{workflow_name}_scheduler

# ... other imports ...

logger = logging.getLogger(__name__) # Initialize logger for lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting scheduler...")
    try:
        scheduler.start()
    except Exception as e:
        logger.exception(f"Failed to start scheduler: {e}")
        # Decide if application should proceed without scheduler

    # Register workflow-specific jobs
    try:
        setup_{workflow_name}_scheduler(scheduler) # Pass the scheduler instance
        # ... register other workflow schedulers here ...
        logger.info("Scheduler jobs registered.")
    except Exception as e:
        logger.exception("Failed to register scheduler jobs.")

    yield

    # Shutdown
    logger.info("Shutting down scheduler...")
    if scheduler.running:
        try:
            # Attempt a graceful shutdown with a timeout
            scheduler.shutdown(wait=True) # Set wait=True to allow jobs to complete
            logger.info("Scheduler shut down gracefully.")
        except (asyncio.CancelledError, TimeoutError):
            logger.warning("Scheduler shutdown timed out or was cancelled. Forcing shutdown.")
            scheduler.shutdown(wait=False) # Force shutdown
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")
            scheduler.shutdown(wait=False) # Force shutdown on other errors
    else:
        logger.info("Scheduler was not running.")

# Initialize FastAPI app with lifespan manager
app = FastAPI(lifespan=lifespan)

# ... rest of your main.py (routers, etc.) ...
