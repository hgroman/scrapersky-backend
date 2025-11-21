# src/services/sitemap_import_scheduler.py

import logging

from sqlalchemy import asc

# SDK and Config Imports
from src.common.curation_sdk.scheduler_loop import run_job_loop

# Model and Enum Imports
from src.models.wf5_sitemap_file import SitemapFile, SitemapImportProcessStatusEnum
from src.scheduler_instance import scheduler  # Import shared scheduler instance

# Service to be called
from src.services.sitemap_import_service import SitemapImportService

logger = logging.getLogger(__name__)


async def process_pending_sitemap_imports() -> None:
    """Job function to process sitemap files queued for URL extraction/import."""
    logger.info("Running scheduled job: process_pending_sitemap_imports")

    # Import the INSTANCE 'settings' from the module 'src.config.settings'
    from src.config.settings import settings

    service = SitemapImportService()  # Use renamed service
    try:
        await run_job_loop(
            model=SitemapFile,
            status_enum=SitemapImportProcessStatusEnum,
            queued_status=SitemapImportProcessStatusEnum.Queued,
            processing_status=SitemapImportProcessStatusEnum.Processing,
            completed_status=SitemapImportProcessStatusEnum.Complete,
            failed_status=SitemapImportProcessStatusEnum.Error,
            # Pass the service method as the processing function
            processing_function=service.process_single_sitemap_file,
            # Use RENAMED setting
            batch_size=settings.SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE,
            order_by_column=asc(SitemapFile.updated_at),
            # Updated to new DB column names
            status_field_name="sitemap_import_status",
            error_field_name="sitemap_import_error",
        )
    except Exception as e:
        logger.exception(f"Error in process_pending_sitemap_imports job: {e}")

    logger.info(
        "Finished scheduled job: process_pending_sitemap_imports"
    )  # Updated log


def setup_sitemap_import_scheduler() -> None:
    """Adds the sitemap import processing job to the shared scheduler."""
    # Import the INSTANCE 'settings' from the module 'src.config.settings'
    from src.config.settings import settings

    job_id = "process_sitemap_imports"  # Renamed job_id
    logger.info(f"Setting up scheduler job: {job_id}")
    # Use the imported shared scheduler instance
    try:
        # --- TEMPORARY DEBUGGING REMOVED --- #

        scheduler.add_job(
            process_pending_sitemap_imports,  # Use renamed job function
            trigger="interval",
            # Use RENAMED setting
            minutes=settings.SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES,
            id=job_id,
            name="Process Pending Sitemap Imports",  # Updated job name
            replace_existing=True,
            # Use RENAMED setting
            max_instances=settings.SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES,
            misfire_grace_time=1800,  # 30 minutes
        )
        logger.info(f"Added/Updated job '{job_id}' on shared scheduler.")
        # Check if job exists before logging next run time
        job = scheduler.get_job(job_id)
        if job and job.next_run_time:
            logger.info(f"Job '{job_id}' next run time: {job.next_run_time}")
        else:
            logger.warning(f"Could not determine next run time for job '{job_id}'.")
    except Exception as e:
        logger.exception(f"Failed to add job {job_id}: {e}")
