"""
Scheduler Service for Domain Sitemap Submission

Periodically checks for domains marked with sitemap_analysis_status = 'queued'
and triggers the DomainToSitemapAdapterService to submit them to the legacy
sitemap scanning system.
"""

import logging
import traceback
import uuid
from datetime import datetime, timedelta, timezone
from typing import List

# from apscheduler.schedulers.asyncio import AsyncIOScheduler # Remove local scheduler import
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from src.config.settings import settings
from src.models.domain import Domain, SitemapAnalysisStatusEnum
import asyncio
from src.services.website_scan_service import WebsiteScanService
from src.tasks.email_scraper import scan_website_for_emails
from src.session.async_session import get_background_session

# Import the shared scheduler instance
from ..scheduler_instance import scheduler

logger = logging.getLogger(__name__)

# Initialize scheduler instance specific to this task # <-- REMOVE THIS LINE
# scheduler = AsyncIOScheduler()


async def process_pending_domain_sitemap_submissions():
    """
    Fetches domains queued for sitemap submission (handling stale entries),
    processes them using the adapter service, handling each domain in its own transaction.
    Uses explicit SQL casting for enum comparison due to raw_sql=True engine config.
    """
    batch_id = f"domain_sitemap_submission_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"--- Starting Domain Sitemap Submission Batch {batch_id} ---")

    batch_size = settings.DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE
    domains_found = 0
    domains_processed = 0
    domains_submitted_successfully = 0
    domains_failed = 0  # Unified failure counter
    stale_threshold_minutes = 15  # Threshold for considering a domain stuck in 'queued'

    website_scan_service = WebsiteScanService()
    domain_ids_to_process: List[uuid.UUID] = []

    # --- Step 1: Fetch IDs of domains to process (outside main transaction loop) ---
    try:
        # Use a temporary session just for fetching IDs
        async with get_background_session() as session_outer:
            # Use naive UTC datetime to match potential naive DB column type
            stale_timestamp = datetime.utcnow() - timedelta(
                minutes=stale_threshold_minutes
            )

            # Use text() for explicit enum casting due to raw_sql=True engine config
            # Also add check for potentially stale entries
            stmt_select_ids = (
                select(Domain.id)  # Select only IDs initially
                .where(
                    # Standard ORM Enum comparison
                    Domain.sitemap_analysis_status == SitemapAnalysisStatusEnum.Queued,
                )
                .order_by(Domain.updated_at.asc())
                .limit(batch_size)
                # No lock needed here, lock will happen per-domain
            )
            result_ids = await session_outer.execute(stmt_select_ids)
            domain_ids_to_process = list(result_ids.scalars().all())  # Explicitly list
            domains_found = len(domain_ids_to_process)
            logger.info(
                f"Found {domains_found} domain IDs potentially queued (or stale) for sitemap submission."
            )

            if not domain_ids_to_process:
                logger.info("No domain IDs found to process in this batch.")
                # Log final counts before returning
                logger.info(
                    f"--- Finished Domain Sitemap Submission Batch {batch_id} --- Found: {domains_found}, Processed: {domains_processed}, Submitted OK: {domains_submitted_successfully}, Failed: {domains_failed}"
                )
                return

    except SQLAlchemyError as e_fetch_sql:
        logger.error(
            f"SQLAlchemy error fetching domain IDs for batch {batch_id}: {e_fetch_sql}",
            exc_info=True,
        )
        traceback.print_exc()
        logger.info(
            f"--- Finished Domain Sitemap Submission Batch {batch_id} --- Found: {domains_found} (SQL FETCH ERROR), Processed: {domains_processed}, Submitted OK: {domains_submitted_successfully}, Failed: {domains_failed}"
        )
        return
    except Exception as e_fetch:
        logger.error(
            f"Error fetching domain IDs for batch {batch_id}: {e_fetch}", exc_info=True
        )
        traceback.print_exc()
        logger.info(
            f"--- Finished Domain Sitemap Submission Batch {batch_id} --- Found: {domains_found} (FETCH ERROR), Processed: {domains_processed}, Submitted OK: {domains_submitted_successfully}, Failed: {domains_failed}"
        )
        return

    # --- Step 2: Process each domain ID in its own transaction ---
    for domain_id in domain_ids_to_process:
        logger.debug(f"Attempting to process domain ID {domain_id}")
        # Start a new transaction for *this domain only*
        async with get_background_session() as session_inner:
            try:
                # Fetch the specific domain *within this transaction* and lock it
                locked_domain = await session_inner.get(
                    Domain, domain_id, with_for_update=True
                )

                if not locked_domain:
                    logger.warning(
                        f"Domain ID {domain_id} not found or locked by another process during fetch. Skipping."
                    )
                    domains_failed += 1  # Count as failed if cannot be fetched/locked
                    continue  # Move to the next domain ID

                logger.info(
                    f"Processing domain {domain_id} ({locked_domain.domain}) - Current status: {locked_domain.sitemap_analysis_status}"
                )

                # 1. Mark as 'processing' (direct assignment)
                locked_domain.sitemap_analysis_status = (
                    SitemapAnalysisStatusEnum.Processing
                )
                locked_domain.sitemap_analysis_error = None
                await session_inner.flush()  # Flush 'processing' state
                logger.debug(
                    f"Domain {domain_id} status set to 'processing' and flushed."
                )

                # 2. Initiate the scan directly using the service
                domains_processed += 1
                system_user_id = uuid.UUID(settings.SYSTEM_USER_ID)
                job = await website_scan_service.initiate_scan(
                    domain_id=locked_domain.id,
                    user_id=system_user_id,
                    session=session_inner,
                )

                # 3. Queue the background task
                if job.status == TaskStatus.PENDING:
                    asyncio.create_task(scan_website_for_emails(job.id))
                    logger.info(f"Queued background task for job {job.id} for domain {domain_id}.")
                    # Mark domain as completed since the job is now queued
                    locked_domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.Completed
                    await session_inner.flush()
                    domains_submitted_successfully += 1
                elif job.status == TaskStatus.RUNNING:
                    logger.info(f"Job {job.id} for domain {domain_id} is already running. No new task queued.")
                    # Mark domain as completed as a job is already active
                    locked_domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.Completed
                    await session_inner.flush()
                    domains_submitted_successfully += 1
                else:
                    logger.error(f"Failed to initiate scan for domain {domain_id}. Job status: {job.status}")
                    locked_domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.Error
                    locked_domain.sitemap_analysis_error = "Failed to create or find active job for scan."
                    await session_inner.flush()
                    domains_failed += 1

                # 4. Commit this domain's transaction
                await session_inner.commit()
                logger.debug(f"Committed transaction for domain {domain_id}.")

            except SQLAlchemyError as e_inner_sql:
                # Error during DB operations for this domain
                logger.error(
                    f"SQLAlchemy error processing domain {domain_id}: {e_inner_sql}",
                    exc_info=True,
                )
                traceback.print_exc()
                await session_inner.rollback()
                logger.warning(
                    f"Rolled back transaction for domain {domain_id} due to SQLAlchemy error."
                )
                domains_failed += 1  # Count as failed if transaction fails
            except Exception as e_inner:
                # Catch-all for other unexpected errors during this domain's processing
                logger.error(
                    f"Unexpected error processing domain {domain_id}: {e_inner}",
                    exc_info=True,
                )
                traceback.print_exc()
                await session_inner.rollback()
                logger.warning(
                    f"Rolled back transaction for domain {domain_id} due to unexpected error."
                )
                domains_failed += 1  # Count as failed

    # --- Step 3: Log final counts after processing all IDs ---
    logger.info(
        f"--- Finished Domain Sitemap Submission Batch {batch_id} --- Found: {domains_found}, Processed: {domains_processed}, Submitted OK: {domains_submitted_successfully}, Failed: {domains_failed}"
    )


# --- Setup and Shutdown Functions ---


def setup_domain_sitemap_submission_scheduler():
    """Sets up the domain sitemap submission scheduler job using the shared scheduler."""
    try:
        interval_minutes = settings.DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES
        batch_size = settings.DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE
        # Use max_instances = 1 as per previous default
        max_instances = 1

        job_id = "process_pending_domain_sitemap_submissions"

        logger.info(
            f"Setting up Domain Sitemap Submission job on shared scheduler (ID: {job_id}, Interval: {interval_minutes}m, Batch: {batch_size}, Max Instances: {max_instances})"
        )

        # Remove existing job from the shared scheduler if it exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Removed existing job '{job_id}' from shared scheduler.")

        # Add job to the shared scheduler instance
        scheduler.add_job(
            process_pending_domain_sitemap_submissions,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            name="Process Pending Domain Sitemap Submissions",
            replace_existing=True,
            max_instances=max_instances,
            coalesce=True,
            misfire_grace_time=60,
            # kwargs? This job doesn't seem to take limit/batch_size in its signature
        )

        logger.info(f"Added/Updated job '{job_id}' on shared scheduler.")
        current_job = scheduler.get_job(job_id)
        if current_job:
            logger.info(f"Job '{job_id}' next run time: {current_job.next_run_time}")
        else:
            logger.error(
                f"Failed to verify job '{job_id}' after adding to shared scheduler."
            )

        # No need to return scheduler
        # return scheduler

    except Exception as e:
        logger.error(
            f"Error setting up domain sitemap submission scheduler job: {e}",
            exc_info=True,
        )
        # No need to manage scheduler start/stop here
        # return None


# Remove local shutdown function
# def shutdown_domain_sitemap_submission_scheduler():
#     """Shuts down the domain sitemap submission scheduler."""
#     logger.info("Attempting to shut down Domain Sitemap Submission scheduler...")
#     try:
#         if scheduler.running:
#             scheduler.shutdown()
#             logger.info("Domain Sitemap Submission scheduler shut down successfully.")
#         else:
#             logger.info("Domain Sitemap Submission scheduler was not running.")
#     except Exception as e:
#         logger.error(f"Error shutting down domain sitemap submission scheduler: {e}", exc_info=True)
