"""
Brevo Contact Sync Scheduler (WO-015 Phase 2 Step 2)

Background scheduler that automatically processes contacts queued for Brevo sync.

Architecture: SDK-compatible scheduler using run_job_loop pattern.
Pattern Reference: src/services/WF7_V2_L4_2of2_PageCurationScheduler.py

This scheduler:
1. Runs every N minutes (configured via BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES)
2. Fetches contacts with brevo_processing_status = 'Queued'
3. Processes each contact via BrevoSyncService.process_single_contact()
4. Handles retries automatically based on next_retry_at timestamp
"""

import logging
from sqlalchemy import asc, or_
from datetime import datetime

from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import CRMProcessingStatus
from .brevo_sync_service import BrevoSyncService

logger = logging.getLogger(__name__)


async def process_brevo_sync_queue():
    """
    Processes contacts marked as 'Queued' for Brevo sync using the SDK job loop.

    This function:
    1. Queries contacts with brevo_processing_status = 'Queued'
    2. Filters for contacts ready for retry (next_retry_at <= now OR next_retry_at IS NULL)
    3. Processes each contact via BrevoSyncService.process_single_contact()
    4. Automatically handles status transitions via run_job_loop

    Called by: APScheduler at configured interval
    Frequency: BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES (default: 5 minutes)
    Batch Size: BREVO_SYNC_SCHEDULER_BATCH_SIZE (default: 10)
    """
    service = BrevoSyncService()
    logger.info("🚀 Starting Brevo sync scheduler cycle")

    await run_job_loop(
        model=Contact,
        status_enum=CRMProcessingStatus,
        queued_status=CRMProcessingStatus.Queued,
        processing_status=CRMProcessingStatus.Processing,
        completed_status=CRMProcessingStatus.Complete,
        failed_status=CRMProcessingStatus.Error,
        processing_function=service.process_single_contact,
        batch_size=settings.BREVO_SYNC_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Contact.updated_at),
        status_field_name="brevo_processing_status",
        error_field_name="brevo_processing_error",
        # Additional filter: Only process contacts ready for retry
        additional_filters=[
            or_(
                Contact.next_retry_at.is_(None),
                Contact.next_retry_at <= datetime.utcnow(),
            )
        ],
    )

    logger.info("✅ Finished Brevo sync scheduler cycle")


from src.scheduler_instance import scheduler


def setup_brevo_sync_scheduler():
    """
    Adds the Brevo contact sync job to the main scheduler.

    Configuration (from settings.py):
    - BREVO_API_KEY: Required - scheduler will not start if missing
    - BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES: How often to run (default: 5)
    - BREVO_SYNC_SCHEDULER_BATCH_SIZE: Contacts per batch (default: 10)
    - BREVO_SYNC_SCHEDULER_MAX_INSTANCES: Concurrent instances (default: 1)

    Safety:
    - Scheduler disabled if BREVO_API_KEY not configured
    - max_instances=1 prevents race conditions
    - misfire_grace_time=1800 (30min) handles temporary downtime
    """
    # Safety check: Don't start scheduler if API key not configured
    if not settings.BREVO_API_KEY:
        logger.warning("⚠️ BREVO_API_KEY not configured - Brevo sync scheduler DISABLED")
        logger.warning("   Set BREVO_API_KEY in .env to enable automatic Brevo sync")
        return

    logger.info("📋 Configuring Brevo sync scheduler...")
    logger.info(
        f"   Interval: {settings.BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES} minutes"
    )
    logger.info(f"   Batch size: {settings.BREVO_SYNC_SCHEDULER_BATCH_SIZE} contacts")
    logger.info(f"   Max instances: {settings.BREVO_SYNC_SCHEDULER_MAX_INSTANCES}")

    scheduler.add_job(
        process_brevo_sync_queue,
        trigger="interval",
        minutes=settings.BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES,
        id="brevo_contact_sync_processor",
        name="Brevo Contact Sync Processor",
        replace_existing=True,
        max_instances=settings.BREVO_SYNC_SCHEDULER_MAX_INSTANCES,
        misfire_grace_time=1800,  # 30 minutes grace time for temporary downtime
    )

    logger.info("✅ Brevo sync scheduler job registered successfully")
