"""
Centralized APScheduler Instance

This module initializes and provides a single, shared instance of
AsyncIOScheduler for use across the application to manage background tasks.
"""

import logging

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

# --- Event Listener Functions ---

def job_listener(event):
    """Listens for job execution events and logs them."""
    if event.exception:
        logger.error(f"Scheduler job '{event.job_id}' crashed: {event.exception}", exc_info=event.exception)
    else:
        logger.info(f"Scheduler job '{event.job_id}' executed successfully.")

# --- Scheduler Initialization ---

# Create the single scheduler instance
# Configure with appropriate timezone, jobstores, executors if needed
# For now, using defaults which typically suffice
scheduler = AsyncIOScheduler(timezone="UTC")

# Add event listeners for better observability
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

logger.info("Centralized APScheduler instance created.")

# --- Functions to manage the scheduler lifecycle (called from main.py lifespan) ---

def start_scheduler():
    """Starts the shared scheduler if it's not already running."""
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info("Shared APScheduler started.")
        else:
            logger.info("Shared APScheduler is already running.")
    except Exception as e:
        logger.error(f"Failed to start shared APScheduler: {e}", exc_info=True)
        # Attempt shutdown if start failed partially
        if scheduler.running:
             try:
                 scheduler.shutdown()
             except Exception as shutdown_e:
                 logger.error(f"Error shutting down scheduler after failed start: {shutdown_e}", exc_info=True)

def shutdown_scheduler():
    """Shuts down the shared scheduler."""
    try:
        if scheduler.running:
            # wait=False allows shutdown during lifespan context exit
            scheduler.shutdown(wait=False)
            logger.info("Shared APScheduler shut down.")
        else:
            logger.info("Shared APScheduler was not running.")
    except Exception as e:
        logger.error(f"Failed to shut down shared APScheduler: {e}", exc_info=True)
