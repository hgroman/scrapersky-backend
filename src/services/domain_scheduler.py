"""
Domain Scheduler Service

This module provides a scheduling service that periodically processes domains
with 'pending' status in the database.
"""

import logging
import os
import sys
from datetime import datetime, timezone

# from apscheduler.schedulers.asyncio import AsyncIOScheduler # Remove local scheduler import
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.future import select

from ..config.settings import settings
from ..models.domain import Domain  # Import the Domain model
from ..models.enums import DomainStatusEnum  # Import the new Enum

# Import the shared scheduler instance
from ..scheduler_instance import scheduler
from ..scraper.domain_utils import get_domain_url, standardize_domain
from ..scraper.metadata_extractor import detect_site_metadata
from ..session.async_session import get_background_session

# Load settings
if not os.environ.get("PYTHONPATH"):
    os.environ["PYTHONPATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
    sys.path.insert(0, os.environ["PYTHONPATH"])

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create settings instance
# settings = Settings()

# Create diagnostic directory from settings
DIAGNOSTIC_DIR = settings.DIAGNOSTIC_DIR
os.makedirs(DIAGNOSTIC_DIR, exist_ok=True)


def log_diagnostic_info(message):
    """Log diagnostic information to file and logger."""
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"{timestamp} - {message}")

    try:
        filename = f"{DIAGNOSTIC_DIR}/domain_scheduler_{datetime.utcnow().strftime('%Y%m%d')}.log"
        with open(filename, "a") as f:
            f.write(f"{timestamp} - {message}\n")
    except Exception as e:
        logger.error(f"Error writing diagnostic log: {str(e)}")


async def process_pending_domains(limit: int = 10):
    """
    Process pending domains using a single transaction for the batch.
    Fetches domains, updates status to processing, extracts metadata,
    and updates final status (completed/error) in memory.
    The entire batch is committed or rolled back atomically.

    Args:
        limit: Maximum number of domains to process in one batch
    """
    job_id = f"domain_batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    logger.debug("--------------------------------------------------")
    logger.debug(f"STARTING DOMAIN PROCESSING JOB {job_id} ({limit} domains max)")
    logger.debug("--------------------------------------------------")

    domains_found = 0
    domains_processed = 0
    domains_successful = 0
    domains_failed = 0

    try:
        # CORRECT: Use a single session and transaction for the entire batch
        async with get_background_session() as session:
            async with session.begin():  # FIX: Add transaction boundary to commit changes
                logger.debug(f"Acquired session for batch: {session}")

                # Step 1: Fetch pending domains using ORM
                stmt = (
                    select(Domain)
                    .where(Domain.status == DomainStatusEnum.pending)  # Use Enum member
                    .order_by(Domain.updated_at.asc())
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                    # .options(selectinload(Domain.some_relationship)) # Optional: Eager load relationships if needed
                )
                result = await session.execute(stmt)
                # --- DEBUG LOGGING ---
                raw_peek_results = []
                try:
                    # Peek at first few rows without consuming the whole result yet
                    # Need to handle the raw Row objects returned
                    peek_limit = 5  # Increase peek limit slightly
                    # Use result.partitions() which returns an iterable without consuming
                    # or simply re-execute and fetchmany
                    temp_result = await session.execute(stmt)  # Re-execute for peeking
                    raw_rows = temp_result.fetchmany(peek_limit)
                    if raw_rows:
                        logger.debug(
                            f"Peeked {len(raw_rows)} raw rows before scalars().all()"
                        )
                        for row_num, row in enumerate(raw_rows):
                            # Log basic info about the row object
                            logger.debug(
                                f"  Raw Row {row_num}: Type={type(row)}, Content={str(row)[:200]}..."
                            )
                            try:
                                # Try accessing common attributes if it's an ORM object
                                logger.debug(
                                    f"    -> ID: {getattr(row, 'id', 'N/A')}, Domain: {getattr(row, 'domain', 'N/A')}, Status: {getattr(row, 'status', 'N/A')}"
                                )
                            except Exception:
                                pass  # Ignore errors if it's not an ORM object
                    else:
                        logger.debug("Peeking with fetchmany() returned no rows.")
                    # No need to re-execute again, result is still valid for scalars()
                except Exception as dbg_err:
                    logger.error(f"Debug logging error: {dbg_err}", exc_info=True)
                # --- END DEBUG LOGGING ---
                # Explicitly convert Sequence to List and handle potential None from getattr
                domains_to_process = list(result.scalars().all())
                domains_found = len(domains_to_process)
                logger.info(f"Found {domains_found} pending domain(s).")

                if not domains_to_process:
                    logger.info("No domains to process in this batch.")
                    return  # Context manager handles commit/close

                # Step 2: Process each domain
                for domain in domains_to_process:
                    domain_id = domain.id
                    # Use getattr to ensure we get the string value, not the Column object
                    url = getattr(domain, "domain", None)
                    domains_processed += 1
                    logger.debug(f"Processing domain {domain_id} ({url})")

                    try:
                        # Step 2.1: Update status to 'processing' IN MEMORY using setattr
                        domain.status = DomainStatusEnum.processing  # Use Enum member
                        domain.last_error = None  # Clear previous error
                        domain.updated_at = datetime.utcnow()  # Keep updated_at fresh
                        logger.debug(
                            f"Domain {domain_id} status set to '{DomainStatusEnum.processing.value}' in memory."
                        )
                        # NO COMMIT here

                        # Step 2.2: Extract metadata
                        if not url:
                            raise ValueError(
                                f"Domain record {domain_id} has no domain/url value."
                            )

                        std_domain = standardize_domain(
                            url
                        )  # url is now guaranteed to be str or None (handled above)
                        if not std_domain:
                            raise ValueError(f"Invalid domain format: {url}")

                        domain_url = get_domain_url(std_domain)
                        logger.debug(f"Extracting metadata for: {domain_url}")
                        metadata = await detect_site_metadata(domain_url, max_retries=3)
                        logger.debug(f"Metadata extraction complete for {std_domain}")

                        if metadata is None:
                            raise ValueError(
                                f"Failed to extract metadata from {std_domain}"
                            )

                        # Step 2.3: Update domain with results IN MEMORY using ORM method
                        # Assuming Domain model has an update_from_metadata method
                        # that takes metadata dict and updates relevant fields IN MEMORY
                        await Domain.update_from_metadata(session, domain, metadata)
                        domain.status = DomainStatusEnum.completed  # Use Enum member
                        domain.updated_at = datetime.utcnow()

                        domains_successful += 1
                        logger.info(
                            f"Successfully processed and marked domain {domain_id} as '{DomainStatusEnum.completed.value}' in memory."
                        )

                    except Exception as processing_error:
                        error_message = str(processing_error)
                        logger.error(
                            f"Error processing domain {domain_id}: {error_message}",
                            exc_info=True,
                        )
                        domains_failed += 1
                        # Update status to 'error' IN MEMORY using setattr
                        try:
                            domain.status = DomainStatusEnum.error  # Use Enum member
                            domain.last_error = error_message[
                                :1024
                            ]  # Truncate if necessary
                            domain.updated_at = datetime.utcnow()
                            logger.warning(
                                f"Marked domain {domain_id} as '{DomainStatusEnum.error.value}' in memory."
                            )
                        except AttributeError:
                            logger.error(
                                f"Could not access domain object for {domain_id} after error to mark as failed."
                            )
                        # Do NOT re-raise here if we want the batch to continue and commit successes/failures
                        # If batch atomicity is strict (all fail if one fails), uncomment the next line:
                        # raise

                # Step 3: Commit (or rollback if error occurred and wasn't caught/handled above)
                # The context manager handles this automatically based on whether an exception exited the block.
                logger.info(
                    "Batch loop finished. Session context manager will now commit/rollback."
                )

        # End of async with session block

    except Exception as outer_error:
        logger.error(
            f"Outer error during domain processing job {job_id}: {outer_error}",
            exc_info=True,
        )
        # Session context manager ensures rollback occurred

    finally:
        # Log completion statistics
        logger.debug("--------------------------------------------------")
        logger.debug(f"DOMAIN PROCESSING JOB {job_id} COMPLETE")
        logger.debug(
            f"Found: {domains_found}, Processed: {domains_processed}, Successful: {domains_successful}, Failed: {domains_failed}"
        )
        logger.debug("--------------------------------------------------")


def setup_domain_scheduler():
    """Sets up the domain processing scheduler job using the shared scheduler."""
    try:
        interval_minutes = settings.DOMAIN_SCHEDULER_INTERVAL_MINUTES
        batch_size = settings.DOMAIN_SCHEDULER_BATCH_SIZE
        max_instances = settings.DOMAIN_SCHEDULER_MAX_INSTANCES

        job_id = "process_pending_domains"

        logger.info(
            f"Setting up Domain scheduler job on shared scheduler (Interval: {interval_minutes}m, Batch: {batch_size}, Max Instances: {max_instances})"
        )

        # Remove existing job from the shared scheduler if it exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Removed existing job '{job_id}' from shared scheduler.")

        # Add job to the shared scheduler instance
        scheduler.add_job(
            process_pending_domains,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            name="Process Pending Domains",
            replace_existing=True,
            max_instances=max_instances,
            coalesce=True,
            misfire_grace_time=60,
            kwargs={"limit": batch_size},  # Pass batch_size as limit
        )

        logger.info(f"Added/Updated job '{job_id}' on shared scheduler.")
        current_job = scheduler.get_job(job_id)
        if current_job:
            logger.info(f"Job '{job_id}' next run time: {current_job.next_run_time}")
        else:
            logger.error(
                f"Failed to verify job '{job_id}' after adding to shared scheduler."
            )

        # No need to return the scheduler instance anymore
        # return scheduler

    except Exception as e:
        logger.error(f"Error setting up domain scheduler job: {e}", exc_info=True)
        # No need to manage scheduler start/stop here; main.py handles it.
        # if scheduler.running:
        #     scheduler.shutdown()
        # return None
