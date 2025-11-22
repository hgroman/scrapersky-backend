"""
WF3 Domain Extraction Scheduler
================================

Processes LocalBusiness records queued for domain extraction.
Creates Domain records from business website information for sitemap analysis.

WORKFLOW: WF3 (Domain Extraction)
MODEL: LocalBusiness
STATUS FIELD: domain_extraction_status
SERVICE: LocalBusinessToDomainService

This scheduler replaces the WF3 portion of the legacy sitemap_scheduler.py,
providing fault isolation and independent configuration.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.wf3_local_business import DomainExtractionStatusEnum, LocalBusiness
from src.scheduler_instance import scheduler
from src.services.wf3_business_to_domain_service import LocalBusinessToDomainService

logger = logging.getLogger(__name__)


async def process_domain_extraction_wrapper(item_id: UUID, session: AsyncSession) -> None:
    """
    Adapter wrapper for LocalBusinessToDomainService to work with run_job_loop SDK.

    This adapter:
    1. Fetches the LocalBusiness record by ID
    2. Calls the existing LocalBusinessToDomainService
    3. Updates the domain_extraction_status based on result
    4. Manages its own transaction (required by SDK)

    Args:
        item_id: UUID of the LocalBusiness record
        session: AsyncSession provided by SDK (no active transaction)

    Raises:
        ValueError: If LocalBusiness record not found
        Exception: Any error during processing (caught by SDK)
    """
    # SDK passes session without active transaction
    # We must create our own transaction per SDK requirements
    async with session.begin():
        # Fetch LocalBusiness record
        stmt = select(LocalBusiness).where(LocalBusiness.id == item_id)
        result = await session.execute(stmt)
        business = result.scalar_one_or_none()

        if not business:
            logger.error(f"LocalBusiness {item_id} not found during domain extraction")
            raise ValueError(f"LocalBusiness {item_id} not found")

        logger.info(
            f"Processing domain extraction for LocalBusiness {business.id} "
            f"(website={business.website_url})"
        )

        # Call existing service (already accepts UUID and session)
        service = LocalBusinessToDomainService()
        success = await service.create_pending_domain_from_local_business(
            local_business_id=item_id,
            session=session
        )

        # Update status based on result
        if success:
            business.domain_extraction_status = DomainExtractionStatusEnum.Completed
            business.domain_extraction_error = None
            logger.info(f"Domain extraction completed successfully for LocalBusiness {business.id}")
        else:
            business.domain_extraction_status = DomainExtractionStatusEnum.Error
            business.domain_extraction_error = "Failed to create Domain record from website"
            logger.warning(f"Domain extraction failed for LocalBusiness {business.id}")

        business.updated_at = datetime.utcnow()

        # Transaction auto-commits when exiting async with session.begin()


async def process_domain_extraction_queue():
    """
    Process local businesses queued for domain extraction using the SDK job loop.

    This function is called by the scheduler at configured intervals.
    It uses the run_job_loop SDK which handles:
    - Fetching queued items
    - Marking as Processing
    - Calling the processing function for each item
    - Error handling and Failed status management
    """
    logger.info("Starting domain extraction queue processing cycle")

    await run_job_loop(
        model=LocalBusiness,
        status_enum=DomainExtractionStatusEnum,
        queued_status=DomainExtractionStatusEnum.Queued,
        processing_status=DomainExtractionStatusEnum.Processing,
        completed_status=DomainExtractionStatusEnum.Completed,
        failed_status=DomainExtractionStatusEnum.Error,
        processing_function=process_domain_extraction_wrapper,
        batch_size=settings.DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(LocalBusiness.updated_at),
        status_field_name="domain_extraction_status",
        error_field_name="domain_extraction_error",
    )

    logger.info("Finished domain extraction queue processing cycle")


def setup_domain_extraction_scheduler():
    """
    Add domain extraction job to the main scheduler.

    Configuration is loaded from settings:
    - DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES: How often to run (default: 2)
    - DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE: Items per batch (default: 20)
    - DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES: Max concurrent runs (default: 1)
    """
    job_id = "process_domain_extraction_queue"

    logger.info(
        f"Setting up domain extraction scheduler "
        f"(interval={settings.DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES}m, "
        f"batch={settings.DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE}, "
        f"max_instances={settings.DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES})"
    )

    scheduler.add_job(
        process_domain_extraction_queue,
        trigger="interval",
        minutes=settings.DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES,
        id=job_id,
        name="WF3 - Domain Extraction Queue Processor",
        replace_existing=True,
        max_instances=settings.DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES,
        coalesce=True,  # If multiple runs are queued, combine them
        misfire_grace_time=60,  # Allow 60 seconds grace for missed runs
    )

    logger.info(f"Domain extraction scheduler job '{job_id}' added to shared scheduler")
