"""
HubSpot Contact Sync Scheduler (WO-016 Phase 2)

Background scheduler that automatically processes contacts queued for HubSpot sync.

Architecture: SDK-compatible scheduler using run_job_loop pattern.
Pattern Reference: src/services/WF7_V2_L4_2of2_PageCurationScheduler.py

This scheduler:
1. Runs every N minutes (configured via HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES)
2. Fetches contacts with hubspot_processing_status = 'Queued'
3. Processes each contact via HubSpotSyncService.process_single_contact()
4. Handles retries automatically based on next_retry_at timestamp
"""

import logging
from sqlalchemy import asc

from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import CRMProcessingStatus

from .hubspot_sync_service import HubSpotSyncService

logger = logging.getLogger(__name__)


async def process_hubspot_sync_queue():
    """
    Processes contacts marked as 'Queued' for HubSpot sync using the SDK job loop.

    This function:
    1. Queries contacts with hubspot_processing_status = 'Queued'
    2. Filters for contacts ready for retry (next_retry_at <= now OR next_retry_at IS NULL)
    3. Processes each contact via HubSpotSyncService.process_single_contact()
    4. Automatically handles status transitions via run_job_loop

    Called by: APScheduler at configured interval
    Frequency: HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES (default: 5 minutes)
    Batch Size: HUBSPOT_SYNC_SCHEDULER_BATCH_SIZE (default: 10)
    """
    service = HubSpotSyncService()
    logger.info("🚀 Starting HubSpot sync scheduler cycle")

    await run_job_loop(
        model=Contact,
        status_enum=CRMProcessingStatus,
        queued_status=CRMProcessingStatus.Queued,
        processing_status=CRMProcessingStatus.Processing,
        completed_status=CRMProcessingStatus.Complete,
        failed_status=CRMProcessingStatus.Error,
        processing_function=service.process_single_contact,
        batch_size=settings.HUBSPOT_SYNC_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Contact.updated_at),
        status_field_name="hubspot_processing_status",
        error_field_name="hubspot_processing_error",
    )

    logger.info("✅ Finished HubSpot sync scheduler cycle")


from src.scheduler_instance import scheduler


def setup_hubspot_sync_scheduler():
    """
    Adds the HubSpot contact sync job to the main scheduler.

    Configuration (from settings.py):
    - HUBSPOT_API_KEY: Required - scheduler will not start if missing
    - HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES: How often to run (default: 5)
    - HUBSPOT_SYNC_SCHEDULER_BATCH_SIZE: Contacts per batch (default: 10)
    - HUBSPOT_SYNC_SCHEDULER_MAX_INSTANCES: Concurrent instances (default: 1)

    Safety:
    - Scheduler disabled if HUBSPOT_API_KEY not configured
    - max_instances=1 prevents race conditions
    - misfire_grace_time=1800 (30min) handles temporary downtime
    """
    # Safety check: Don't start scheduler if API key not configured
    if not settings.HUBSPOT_API_KEY:
        logger.warning(
            "⚠️ HUBSPOT_API_KEY not configured - HubSpot sync scheduler DISABLED"
        )
        logger.warning(
            "   Set HUBSPOT_API_KEY in .env to enable automatic HubSpot sync"
        )
        return

    logger.info("📋 Configuring HubSpot sync scheduler...")
    logger.info(
        f"   Interval: {settings.HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES} minutes"
    )
    logger.info(f"   Batch size: {settings.HUBSPOT_SYNC_SCHEDULER_BATCH_SIZE} contacts")
    logger.info(f"   Max instances: {settings.HUBSPOT_SYNC_SCHEDULER_MAX_INSTANCES}")

    scheduler.add_job(
        process_hubspot_sync_queue,
        trigger="interval",
        minutes=settings.HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES,
        id="hubspot_contact_sync_processor",
        name="HubSpot Contact Sync Processor",
        replace_existing=True,
        max_instances=settings.HUBSPOT_SYNC_SCHEDULER_MAX_INSTANCES,
        misfire_grace_time=1800,  # 30 minutes grace time for temporary downtime
    )

    logger.info("✅ HubSpot sync scheduler job registered successfully")
