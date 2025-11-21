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

from ...config.settings import settings
from ...models.wf4_domain import (
    Domain,
    SitemapAnalysisStatusEnum,
)  # Import the Domain model and SitemapAnalysisStatusEnum
from ...models.enums import DomainStatusEnum  # Import the new Enum

# Import the shared scheduler instance
from src.scheduler_instance import scheduler
from src.scraper.domain_utils import get_domain_url, standardize_domain
from src.scraper.metadata_extractor import detect_site_metadata
from src.session.async_session import get_background_session

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
    CRITICAL: DO NOT HOLD DATABASE CONNECTIONS DURING SCRAPER API CALLS
    See: AP-20250730-002 - Database Connection Long Hold Anti-Pattern
    Pattern: Quick DB → Release → Slow Operations → Quick DB
    Violation will cause: asyncpg.exceptions.ConnectionDoesNotExistError

    Process pending domains using 3-phase approach to prevent connection timeouts:
    Phase 1: Quick DB transaction to fetch and mark domains as 'processing'
    Phase 2: Release connection, perform metadata extraction without DB connections
    Phase 3: Quick DB transaction to update final results

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

    # Phase 1: Quick DB transaction to fetch and mark domains as 'processing'
    domains_to_process = []
    try:
        async with get_background_session() as session:
            async with session.begin():
                logger.debug(f"Phase 1: Acquiring domains for processing")

                # Fetch pending domains using ORM
                stmt = (
                    select(Domain)
                    .where(Domain.status == DomainStatusEnum.pending.value)
                    .order_by(Domain.updated_at.asc())
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
                result = await session.execute(stmt)
                domains_from_db = list(result.scalars().all())
                domains_found = len(domains_from_db)
                logger.info(f"Found {domains_found} pending domain(s).")

                if not domains_from_db:
                    logger.info("No domains to process in this batch.")
                    return

                # Mark all domains as processing and collect their info for processing
                for domain in domains_from_db:
                    domain.status = DomainStatusEnum.processing
                    domain.last_error = None
                    domain.updated_at = datetime.utcnow()

                    # Store domain info for processing (detached from session)
                    domains_to_process.append(
                        {
                            "id": domain.id,
                            "domain": getattr(domain, "domain", None),
                            "url": getattr(domain, "domain", None),
                        }
                    )
                    logger.debug(f"Domain {domain.id} marked as processing")

                logger.info(
                    f"Phase 1 complete: {len(domains_to_process)} domains marked as processing"
                )
        # End of Phase 1 - Connection released

        # Phase 2: Metadata extraction WITHOUT database connections (slow operations)
        logger.debug(
            f"Phase 2: Extracting metadata for {len(domains_to_process)} domains"
        )
        domain_results = []

        for domain_info in domains_to_process:
            domain_id = domain_info["id"]
            url = domain_info["url"]
            domains_processed += 1
            logger.debug(f"Processing domain {domain_id} ({url})")

            try:
                if not url:
                    raise ValueError(
                        f"Domain record {domain_id} has no domain/url value."
                    )

                std_domain = standardize_domain(url)
                if not std_domain:
                    raise ValueError(f"Invalid domain format: {url}")

                domain_url = get_domain_url(std_domain)
                logger.debug(f"Extracting metadata for: {domain_url}")

                # CRITICAL: This slow operation now happens WITHOUT holding DB connection
                metadata = await detect_site_metadata(domain_url, max_retries=3)
                logger.debug(f"Metadata extraction complete for {std_domain}")

                if metadata is None:
                    raise ValueError(f"Failed to extract metadata from {std_domain}")

                # Store successful result
                domain_results.append(
                    {
                        "id": domain_id,
                        "status": "completed",
                        "metadata": metadata,
                        "error": None,
                    }
                )
                domains_successful += 1
                logger.info(f"Successfully extracted metadata for domain {domain_id}")

            except Exception as processing_error:
                error_message = str(processing_error)
                logger.error(
                    f"Error processing domain {domain_id}: {error_message}",
                    exc_info=True,
                )

                # Store failed result
                domain_results.append(
                    {
                        "id": domain_id,
                        "status": "error",
                        "metadata": None,
                        "error": error_message[:1024],
                    }
                )
                domains_failed += 1

        logger.info(
            f"Phase 2 complete: {domains_successful} successful, {domains_failed} failed"
        )

        # Phase 3: Quick DB transaction to update final results
        async with get_background_session() as session:
            async with session.begin():
                logger.debug(f"Phase 3: Updating {len(domain_results)} domain results")

                for result in domain_results:
                    domain_id = result["id"]

                    # Fetch the domain again (it's been detached from the previous session)
                    domain = await session.get(Domain, domain_id)
                    if not domain:
                        logger.error(
                            f"Domain {domain_id} not found during result update"
                        )
                        continue

                    try:
                        if result["status"] == "completed":
                            # Update domain with metadata
                            await Domain.update_from_metadata(
                                session, domain, result["metadata"]
                            )
                            domain.status = DomainStatusEnum.completed
                            domain.updated_at = datetime.utcnow()

                            # CRITICAL WF4→WF5 CONNECTION: Queue domain for sitemap analysis
                            setattr(
                                domain,
                                "sitemap_analysis_status",
                                SitemapAnalysisStatusEnum.queued,
                            )
                            logger.info(
                                f"Domain {domain_id} queued for sitemap analysis (WF4→WF5 trigger)"
                            )

                        else:  # error status
                            domain.status = DomainStatusEnum.error
                            domain.last_error = result["error"]
                            domain.updated_at = datetime.utcnow()
                            logger.warning(
                                f"Marked domain {domain_id} as error: {result['error']}"
                            )

                    except Exception as update_error:
                        logger.error(
                            f"Error updating domain {domain_id}: {update_error}",
                            exc_info=True,
                        )
                        domain.status = DomainStatusEnum.error
                        domain.last_error = f"Update failed: {str(update_error)[:1024]}"
                        domain.updated_at = datetime.utcnow()

                logger.info(f"Phase 3 complete: All domain results updated")
        # End of Phase 3 - Final results committed

    except Exception as outer_error:
        logger.error(
            f"Outer error during domain processing job {job_id}: {outer_error}",
            exc_info=True,
        )
        # Session context managers ensure rollback occurred for any failed transactions

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
