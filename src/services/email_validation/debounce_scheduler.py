"""
DeBounce Email Validation Scheduler (WO-017 Phase 2)

Background scheduler that automatically validates contacts queued for email validation.

Architecture: SDK-compatible scheduler using run_job_loop pattern.
Pattern Reference: src/services/crm/brevo_sync_scheduler.py

This scheduler:
1. Runs every N minutes (configured via DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES)
2. Fetches contacts with debounce_processing_status = 'Queued'
3. Processes each contact via DeBounceValidationService.process_single_contact()
4. Handles retries automatically based on next_retry_at timestamp
"""

import logging
from sqlalchemy import asc

from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import CRMProcessingStatus
from .debounce_service import DeBounceValidationService

logger = logging.getLogger(__name__)


async def process_debounce_validation_queue():
    """
    Processes contacts marked as 'Queued' for email validation using the SDK job loop.

    This function:
    1. Queries contacts with debounce_processing_status = 'Queued'
    2. Processes each contact via DeBounceValidationService.process_single_contact()
    3. Automatically handles status transitions via run_job_loop

    Note: Retry logic (next_retry_at filtering) is handled in the service layer,
    not in the scheduler, as the SDK run_job_loop() does not support additional_filters.

    Called by: APScheduler at configured interval
    Frequency: DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES (default: 5 minutes)
    Batch Size: DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE (default: 50)
    """
    service = DeBounceValidationService()
    logger.info("🚀 Starting DeBounce validation scheduler cycle")

    await run_job_loop(
        model=Contact,
        status_enum=CRMProcessingStatus,
        queued_status=CRMProcessingStatus.Queued,
        processing_status=CRMProcessingStatus.Processing,
        completed_status=CRMProcessingStatus.Complete,
        failed_status=CRMProcessingStatus.Error,
        processing_function=service.process_single_contact,
        batch_size=settings.DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Contact.updated_at),
        status_field_name="debounce_processing_status",
        error_field_name="debounce_processing_error",
    )

    logger.info("✅ Finished DeBounce validation scheduler cycle")


from src.scheduler_instance import scheduler


def setup_debounce_validation_scheduler():
    """
    Adds the DeBounce email validation job to the main scheduler.

    Configuration (from settings.py):
    - DEBOUNCE_API_KEY: Required - scheduler will not start if missing
    - DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES: How often to run (default: 5)
    - DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE: Contacts per batch (default: 50)
    - DEBOUNCE_VALIDATION_SCHEDULER_MAX_INSTANCES: Concurrent instances (default: 1)

    Safety:
    - Scheduler disabled if DEBOUNCE_API_KEY not configured
    - max_instances=1 prevents race conditions
    - misfire_grace_time=1800 (30min) handles temporary downtime
    """
    # Safety check: Don't start scheduler if API key not configured
    if not settings.DEBOUNCE_API_KEY:
        logger.warning(
            "⚠️ DEBOUNCE_API_KEY not configured - DeBounce validation scheduler DISABLED"
        )
        logger.warning(
            "   Set DEBOUNCE_API_KEY in .env to enable automatic email validation"
        )
        return

    logger.info("📋 Configuring DeBounce email validation scheduler...")
    logger.info(
        f"   Interval: {settings.DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES} minutes"
    )
    logger.info(
        f"   Batch size: {settings.DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE} emails"
    )
    logger.info(
        f"   Max instances: {settings.DEBOUNCE_VALIDATION_SCHEDULER_MAX_INSTANCES}"
    )

    scheduler.add_job(
        process_debounce_validation_queue,
        trigger="interval",
        minutes=settings.DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES,
        id="debounce_email_validation_processor",
        name="DeBounce Email Validation Processor",
        replace_existing=True,
        max_instances=settings.DEBOUNCE_VALIDATION_SCHEDULER_MAX_INSTANCES,
        misfire_grace_time=1800,  # 30 minutes grace time for temporary downtime
    )

    logger.info("✅ DeBounce validation scheduler job registered successfully")
