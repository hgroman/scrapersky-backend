"""
🚨 NUCLEAR SHARED SERVICE - Multi-Workflow Background Processor
==============================================================
⚠️  SERVES: WF2 (Deep Scans), WF3 (Domain Extraction), WF5 (Sitemap Import)
⚠️  DELETION BREAKS: 3 workflows simultaneously
⚠️  GUARDIAN DOC: WF0_Critical_File_Index.md (SHARED.2)
⚠️  MODIFICATION REQUIRES: Architecture team review

🔒 DISASTER VULNERABILITY: High - Serves multiple critical workflows
🔒 PROTECTION LEVEL: NUCLEAR - Changes affect 3 workflow pipelines
🔒 SPLIT NEEDED: Should be separated into workflow-specific processors

URGENT: This shared processor is a single point of failure for multiple
workflows. Needs architectural refactoring to reduce risk.

Sitemap Scheduler Service

This module provides a scheduling service that periodically processes sitemaps
with 'pending' status in the database.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone

from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import func, select, update

from ..config.settings import settings

# SitemapCurationStatusEnum removed (commented out) - Not used in this scheduler service.
# Was likely added erroneously during previous model refactoring and caused ImportError.
# from ..models.sitemap import SitemapFile, SitemapUrl, SitemapFileStatusEnum, SitemapCurationStatusEnum
from ..models.job import Job
from ..models.local_business import DomainExtractionStatusEnum, LocalBusiness

# Import the NEW Enum for deep scan status
from ..models.place import GcpApiDeepScanStatusEnum, Place

# Import the shared scheduler instance
from ..scheduler_instance import scheduler
from ..services.business_to_domain_service import LocalBusinessToDomainService
from ..services.job_service import job_service
from ..services.places.places_deep_service import PlacesDeepService
from ..services.sitemap.processing_service import process_domain_with_own_session
from ..session.async_session import get_background_session

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create diagnostic directory from settings
DIAGNOSTIC_DIR = settings.DIAGNOSTIC_DIR
os.makedirs(DIAGNOSTIC_DIR, exist_ok=True)

# Define a timeout for individual sitemap processing jobs (slightly less than interval)
# TODO: Make this configurable?
SITEMAP_JOB_TIMEOUT_SECONDS = 55


def log_diagnostic_info(message):
    """Log diagnostic information to file and logger."""
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(f"{timestamp} - {message}")

    try:
        filename = f"{DIAGNOSTIC_DIR}/sitemap_scheduler_{datetime.now(timezone.utc).strftime('%Y%m%d')}.log"
        with open(filename, "a") as f:
            f.write(f"{timestamp} - {message}\n")
    except Exception as e:
        logger.error(f"Error writing diagnostic log: {str(e)}")


async def handle_job_error(job_id: int, error_message: str):
    """Handle job errors by updating job status and logging."""
    try:
        async with get_background_session() as session:
            # Update job status to failed and store error message
            stmt = (
                update(Job)
                .where(Job.id == job_id)
                .values(
                    status="failed",
                    error=error_message[:1024],  # Truncate error if too long
                    updated_at=func.now(),
                )
            )
            await session.execute(stmt)
            # FIXED: Removed manual commit - get_background_session() handles this automatically
            logger.info(f"Marked Job {job_id} as failed: {error_message}")
    except Exception as db_error:
        logger.error(
            f"Database error while marking job {job_id} as failed: {db_error}",
            exc_info=True,
        )


async def process_pending_jobs(limit: int = 10):
    """
    Processes pending jobs fetched from the database, including sitemaps and deep scans.

    This function now handles both legacy sitemap job processing and the new
    Curation-Driven deep scan workflow by querying the places_staging table directly
    using the `deep_scan_status` field.

    Args:
        limit: Maximum number of jobs/places of *each type* to process in one batch
    """
    batch_id = f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    logger.debug("--------------------------------------------------")
    logger.debug(
        f"STARTING BACKGROUND PROCESSING BATCH {batch_id} ({limit} items max per type)"
    )
    logger.debug("--------------------------------------------------")

    sitemaps_processed = 0
    sitemaps_successful = 0
    deep_scans_processed = 0
    deep_scans_successful = 0
    domain_extractions_processed = 0
    domain_extractions_successful = 0

    # --- Process Pending Sitemap Jobs (Legacy Method) ---
    # DISABLED as per new PRD v1.2 and holistic analysis.
    # This entire workflow is being replaced by the modern, SDK-based sitemap_import_scheduler.
    # pending_sitemap_jobs = []
    # try:
    #     # Fetch jobs within its own session scope
    #     async with get_background_session() as fetch_session:
    #         pending_sitemap_jobs = await job_service.get_pending_jobs(
    #             fetch_session, job_type="sitemap", limit=limit
    #         )
    #         logger.info(
    #             f"Found {len(pending_sitemap_jobs)} pending sitemap jobs to process."
    #         )
    #
    # except Exception as e:
    #     logger.error(f"Error fetching pending sitemap jobs: {str(e)}", exc_info=True)
    #     # If fetching fails, we can still proceed to other job types
    #
    # # Process fetched jobs individually with error handling and timeout
    # for job in pending_sitemap_jobs:
    #     sitemaps_processed += 1
    #     # Use getattr to get the actual ID value
    #     job_id_val = getattr(job, "job_id", None)
    #     domain = None  # Initialize domain variable
    #     try:
    #         # Check if job_id_val is valid before proceeding
    #         if job_id_val is None:
    #             logger.error(
    #                 f"Job object {job} appears to have no 'id' attribute. Skipping."
    #             )
    #             continue
    #
    #         result_data = {} if job.result_data is None else job.result_data
    #         domain = result_data.get("domain")  # Extract domain for logging
    #
    #         if not domain:
    #             error_msg = f"Sitemap Job {job_id_val} has no domain specified. Marking as error."
    #             logger.error(error_msg)
    #             await handle_job_error(
    #                 int(job_id_val), error_msg
    #             )  # job_id_val is now int or None
    #             continue  # Move to the next job
    #
    #         logger.info(
    #             f"Processing sitemap for domain {domain} (job_id: {job_id_val}) with timeout {SITEMAP_JOB_TIMEOUT_SECONDS}s"
    #         )
    #
    #         # Run the processing with a timeout
    #         await asyncio.wait_for(
    #             process_domain_with_own_session(
    #                 job_id=str(job_id_val),  # Pass as string
    #                 domain=domain,
    #                 user_id="5905e9fe-6c61-4694-b09a-6602017b000a",  # System/Scheduler User
    #                 max_urls=1000,  # Consider making this configurable
    #             ),
    #             timeout=SITEMAP_JOB_TIMEOUT_SECONDS,
    #         )
    #
    #         sitemaps_successful += 1
    #         logger.info(
    #             f"Successfully processed sitemap for {domain} (job_id: {job_id_val})"
    #         )
    #
    #     except asyncio.TimeoutError:
    #         if job_id_val is not None:
    #             error_msg = f"Timeout processing sitemap job {job_id_val} for domain {domain} after {SITEMAP_JOB_TIMEOUT_SECONDS} seconds."
    #             logger.error(error_msg)
    #             await handle_job_error(int(job_id_val), error_msg)
    #         else:
    #             logger.error(
    #                 f"Timeout occurred but job_id was None for job object {job}"
    #             )
    #         continue  # Move to the next job
    #
    #     except Exception as e:
    #         if job_id_val is not None:
    #             error_msg = f"Error processing sitemap job {job_id_val} for domain {domain}: {str(e)}"
    #             logger.error(error_msg, exc_info=True)
    #             await handle_job_error(int(job_id_val), error_msg)
    #         else:
    #             logger.error(
    #                 f"Error occurred but job_id was None for job object {job}: {str(e)}",
    #                 exc_info=True,
    #             )
    #         continue  # Move to the next job

    logger.info(
        f"Finished processing legacy sitemap jobs. Processed: {sitemaps_processed}, Successful: {sitemaps_successful}"
    )

    # --- Process Pending Deep Scans (Curation-Driven Method - Minimal Fix) ---
    try:
        async with (
            get_background_session() as session
        ):  # Session for the deep scan batch
            stmt_select = (
                select(Place)
                # Query using the dedicated deep_scan_status field and the NEW enum
                .where(Place.deep_scan_status == GcpApiDeepScanStatusEnum.Queued)
                .order_by(Place.updated_at.asc())  # Process oldest first
                .limit(limit)
                # --- Reinstated after debugging --- #
                .with_for_update(
                    skip_locked=True
                )  # Avoid race conditions if multiple schedulers run
            )
            result = await session.execute(stmt_select)
            places_to_scan = result.scalars().all()
            logger.info(f"Found {len(places_to_scan)} places queued for deep scan.")

            if not places_to_scan:
                logger.debug("No places found in 'queued' deep scan state.")
            else:
                deep_service = PlacesDeepService()
                for place in places_to_scan:
                    deep_scans_processed += 1
                    place_id_str = str(place.place_id)
                    tenant_id_str = str(place.tenant_id)
                    logger.info(
                        f"Processing deep scan for place_id: {place_id_str} (tenant: {tenant_id_str})"
                    )

                    try:
                        # Mark as Processing immediately using the NEW enum
                        place.deep_scan_status = GcpApiDeepScanStatusEnum.Processing  # type: ignore
                        place.updated_at = datetime.utcnow()  # type: ignore
                        await (
                            session.flush()
                        )  # Flush to update status before potentially long task

                        logger.info(
                            f"Deep Scan: Triggering deep scan for Place ID: {place.place_id}"
                        )

                        # Call the actual deep scan service method
                        result = await deep_service.process_single_deep_scan(
                            place_id=place_id_str, tenant_id=tenant_id_str
                        )

                        if result.get("success"):
                            logger.info(
                                f"Deep Scan: Success for Place ID: {place.place_id}"
                            )
                            # Update status to Completed using the NEW enum
                            place.deep_scan_status = GcpApiDeepScanStatusEnum.Completed  # type: ignore
                            place.deep_scan_error = None  # type: ignore
                            place.updated_at = datetime.utcnow()  # type: ignore
                            deep_scans_successful += 1
                        else:
                            error_msg = result.get("error", "Unknown deep scan error")
                            logger.error(
                                f"Deep Scan: Failed for Place ID: {place.place_id} - Error: {error_msg}"
                            )
                            # Update status to Error using the NEW enum
                            place.deep_scan_status = GcpApiDeepScanStatusEnum.Error  # type: ignore
                            place.deep_scan_error = error_msg[:1024]  # type: ignore # Truncate
                            place.updated_at = datetime.utcnow()  # type: ignore

                    except Exception as deep_scan_e:
                        logger.error(
                            f"Deep Scan: Exception during processing Place ID: {place.place_id} - {deep_scan_e}",
                            exc_info=True,
                        )
                        try:
                            # Attempt to mark as Error using the NEW enum on exception
                            place.deep_scan_status = GcpApiDeepScanStatusEnum.Error  # type: ignore
                            place.deep_scan_error = str(deep_scan_e)[:1024]  # type: ignore
                            place.updated_at = datetime.utcnow()  # type: ignore
                        except Exception as inner_e:
                            logger.error(
                                f"Error marking place {place.place_id} as error: {inner_e}",
                                exc_info=True,
                            )
                        finally:
                            # If loop completes, context manager commits changes for this deep scan batch
                            logger.info(
                                "Deep scan batch loop finished. Session context manager will commit/rollback."
                            )

    except Exception as e:
        logger.error(
            f"Error fetching or processing pending deep scans: {str(e)}", exc_info=True
        )

    # --- Process Pending Domain Extractions (Minimal Fix) ---
    try:
        async with (
            get_background_session() as session
        ):  # Session for the domain extraction batch
            stmt_select_lb = (
                select(LocalBusiness)
                .where(
                    LocalBusiness.domain_extraction_status
                    == DomainExtractionStatusEnum.Queued
                )
                .order_by(LocalBusiness.updated_at.asc())  # Process oldest first
                .limit(limit)
                .with_for_update(skip_locked=True)  # Avoid race conditions
            )
            result_lb = await session.execute(stmt_select_lb)
            businesses_to_process = result_lb.scalars().all()
            logger.info(
                f"Found {len(businesses_to_process)} local businesses queued for domain extraction."
            )

            if not businesses_to_process:
                logger.debug(
                    "No local businesses found in 'queued' domain extraction state."
                )
            else:
                domain_extraction_service = LocalBusinessToDomainService()
                for business in businesses_to_process:
                    domain_extractions_processed += 1
                    # Use getattr for business ID
                    business_id_val = getattr(business, "id", None)
                    business_id_str = (
                        str(business_id_val) if business_id_val else "UnknownID"
                    )
                    logger.info(
                        f"Processing domain extraction for local_business_id: {business_id_str}"
                    )

                    try:
                        if business_id_val is None:
                            raise ValueError(f"Business object {business} has no ID.")

                        # Update status to Processing IN MEMORY using setattr
                        business.domain_extraction_status = (
                            DomainExtractionStatusEnum.Processing
                        )  # type: ignore
                        business.domain_extraction_error = None  # type: ignore
                        await session.flush()  # Flush if needed before service call
                        logger.debug(
                            f"Updated business {business_id_str} domain_extraction_status to processing (in memory)"
                        )

                        # Perform the domain extraction and queuing
                        # Pass the existing session - ensure service does NOT commit
                        success = await domain_extraction_service.create_pending_domain_from_local_business(
                            local_business_id=business_id_val,  # Pass the UUID value
                            session=session,
                        )

                        # Update status based on success IN MEMORY using setattr
                        # Assumes service raises error on failure or returns False and sets error on business object
                        if success:
                            # Assume service set status to completed or queued_for_analysis if appropriate
                            business.domain_extraction_status = (
                                DomainExtractionStatusEnum.Completed
                            )  # type: ignore
                            business.domain_extraction_error = None  # type: ignore
                            logger.info(
                                f"Successfully processed domain extraction for business {business_id_str}. Status updated (in memory)."
                            )
                            domain_extractions_successful += 1
                        else:
                            # Assume service set status to failed and set error message
                            business.domain_extraction_status = (
                                DomainExtractionStatusEnum.Error
                            )  # type: ignore
                            business.domain_extraction_error = error_message[:1024]  # type: ignore
                            logger.warning(
                                f"Domain extraction failed for business {business_id_str}. Status updated to failed (in memory). Error: {getattr(business, 'domain_extraction_error', 'N/A')}"
                            )  # Use getattr to read

                    except Exception as extraction_error:
                        error_message = str(extraction_error)
                        logger.error(
                            f"Error during domain extraction for business {business_id_str}: {error_message}",
                            exc_info=True,
                        )
                        # Update status to Failed IN MEMORY using the *existing* session with setattr
                        try:
                            business.domain_extraction_status = (
                                DomainExtractionStatusEnum.Error
                            )  # type: ignore
                            business.domain_extraction_error = error_message[:1024]  # type: ignore
                            logger.warning(
                                f"Updated business {business_id_str} domain_extraction_status to failed (in memory)."
                            )
                        except AttributeError:
                            logger.error(
                                f"Could not access business object for {business_id_str} after error to mark as failed."
                            )
                        # Do not create a new session here.

            # If loop completes, context manager commits changes for this domain extraction batch
            logger.info(
                "Domain extraction batch loop finished. Session context manager will commit/rollback."
            )

    except Exception as e:
        logger.error(
            f"Error fetching or processing pending domain extractions: {str(e)}",
            exc_info=True,
        )

    finally:
        # Log completion statistics
        logger.debug("--------------------------------------------------")
        logger.debug(f"BACKGROUND BATCH {batch_id} COMPLETE")
        logger.debug(
            f"Sitemaps: Processed={sitemaps_processed}, Successful={sitemaps_successful}"
        )
        logger.debug(
            f"Deep Scans: Processed={deep_scans_processed}, Successful={deep_scans_successful}"
        )
        logger.debug(
            f"Domain Extractions: Processed={domain_extractions_processed}, Successful={domain_extractions_successful}"
        )
        logger.debug("--------------------------------------------------")


def setup_sitemap_scheduler():
    """Sets up the sitemap processing scheduler job using the shared scheduler."""
    try:
        # Use SITEMAP specific interval/batch settings if defined, else maybe fallback or default?
        # Assuming settings.SITEMAP_SCHEDULER_INTERVAL_MINUTES exists
        interval_minutes = settings.SITEMAP_SCHEDULER_INTERVAL_MINUTES
        batch_size = settings.SITEMAP_SCHEDULER_BATCH_SIZE
        # Assuming settings.SITEMAP_SCHEDULER_MAX_INSTANCES exists
        max_instances = settings.SITEMAP_SCHEDULER_MAX_INSTANCES

        job_id = "process_pending_jobs"  # This job covers sitemaps, deep scans, domain extraction

        logger.info(
            f"Setting up Sitemap/DeepScan/DomainExtraction job on shared scheduler (ID: {job_id}, Interval: {interval_minutes}m, Batch: {batch_size}, Max Instances: {max_instances})"
        )

        # Remove existing job from the shared scheduler if it exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Removed existing job '{job_id}' from shared scheduler.")

        # Add job to the shared scheduler instance
        scheduler.add_job(
            process_pending_jobs,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            name="Process Sitemaps, DeepScans, DomainExtractions",  # More descriptive name
            replace_existing=True,
            max_instances=max_instances,
            coalesce=True,
            misfire_grace_time=60,
            kwargs={"limit": batch_size},
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
            f"Error setting up sitemap processing scheduler job: {e}", exc_info=True
        )
        # No need to manage scheduler start/stop here
        # return None
