"""
WF2 Deep Scan Scheduler
=======================

Processes Place records queued for Google Maps deep scan analysis.
Extracts detailed business information and populates LocalBusiness records.

WORKFLOW: WF2 (Deep Scans)
MODEL: Place
STATUS FIELD: deep_scan_status
SERVICE: PlacesDeepService

This scheduler replaces the WF2 portion of the legacy sitemap_scheduler.py,
providing fault isolation and independent configuration.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.place import GcpApiDeepScanStatusEnum, Place
from src.scheduler_instance import scheduler
from src.services.places.places_deep_service import PlacesDeepService

logger = logging.getLogger(__name__)


async def process_single_deep_scan_wrapper(item_id: UUID, session: AsyncSession) -> None:
    """
    Adapter wrapper for PlacesDeepService to work with run_job_loop SDK.

    This adapter:
    1. Fetches the Place record by ID
    2. Calls the existing PlacesDeepService with place_id and tenant_id
    3. Updates the deep_scan_status based on result
    4. Manages its own transaction (required by SDK)

    Args:
        item_id: UUID of the Place record
        session: AsyncSession provided by SDK (no active transaction)

    Raises:
        ValueError: If Place record not found
        Exception: Any error during processing (caught by SDK)
    """
    # SDK passes session without active transaction
    # We must create our own transaction per SDK requirements
    async with session.begin():
        # Fetch Place record
        stmt = select(Place).where(Place.id == item_id)
        result = await session.execute(stmt)
        place = result.scalar_one_or_none()

        if not place:
            logger.error(f"Place {item_id} not found during deep scan processing")
            raise ValueError(f"Place {item_id} not found")

        logger.info(
            f"Processing deep scan for Place {place.id} "
            f"(place_id={place.place_id}, tenant_id={place.tenant_id})"
        )

        # Call existing service with its expected signature
        service = PlacesDeepService()
        result = await service.process_single_deep_scan(
            place_id=str(place.place_id),
            tenant_id=str(place.tenant_id)
        )

        # Update status based on result
        if result:
            place.deep_scan_status = GcpApiDeepScanStatusEnum.Completed
            place.deep_scan_error = None
            logger.info(f"Deep scan completed successfully for Place {place.id}")
        else:
            place.deep_scan_status = GcpApiDeepScanStatusEnum.Error
            place.deep_scan_error = "Deep scan returned None - no LocalBusiness created"
            logger.warning(f"Deep scan returned None for Place {place.id}")

        place.updated_at = datetime.utcnow()

        # Transaction auto-commits when exiting async with session.begin()


async def process_deep_scan_queue():
    """
    Process places queued for deep scan analysis using the SDK job loop.

    This function is called by the scheduler at configured intervals.
    It uses the run_job_loop SDK which handles:
    - Fetching queued items
    - Marking as Processing
    - Calling the processing function for each item
    - Error handling and Failed status management
    """
    logger.info("Starting deep scan queue processing cycle")

    await run_job_loop(
        model=Place,
        status_enum=GcpApiDeepScanStatusEnum,
        queued_status=GcpApiDeepScanStatusEnum.Queued,
        processing_status=GcpApiDeepScanStatusEnum.Processing,
        completed_status=GcpApiDeepScanStatusEnum.Completed,
        failed_status=GcpApiDeepScanStatusEnum.Error,
        processing_function=process_single_deep_scan_wrapper,
        batch_size=settings.DEEP_SCAN_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Place.updated_at),
        status_field_name="deep_scan_status",
        error_field_name="deep_scan_error",
    )

    logger.info("Finished deep scan queue processing cycle")


def setup_deep_scan_scheduler():
    """
    Add deep scan job to the main scheduler.

    Configuration is loaded from settings:
    - DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES: How often to run (default: 5)
    - DEEP_SCAN_SCHEDULER_BATCH_SIZE: Items per batch (default: 10)
    - DEEP_SCAN_SCHEDULER_MAX_INSTANCES: Max concurrent runs (default: 1)
    """
    job_id = "process_deep_scan_queue"

    logger.info(
        f"Setting up deep scan scheduler "
        f"(interval={settings.DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES}m, "
        f"batch={settings.DEEP_SCAN_SCHEDULER_BATCH_SIZE}, "
        f"max_instances={settings.DEEP_SCAN_SCHEDULER_MAX_INSTANCES})"
    )

    scheduler.add_job(
        process_deep_scan_queue,
        trigger="interval",
        minutes=settings.DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES,
        id=job_id,
        name="WF2 - Deep Scan Queue Processor",
        replace_existing=True,
        max_instances=settings.DEEP_SCAN_SCHEDULER_MAX_INSTANCES,
        coalesce=True,  # If multiple runs are queued, combine them
        misfire_grace_time=60,  # Allow 60 seconds grace for missed runs
    )

    logger.info(f"Deep scan scheduler job '{job_id}' added to shared scheduler")
