# WF8 – The Connector
# Purpose: Contact validation, enrichment, and delivery to external systems
# NEVER put page-scraping logic here – that belongs in WF7

"""
n8n Webhook Sync Scheduler (WO-020)

Background scheduler that automatically processes contacts queued for n8n enrichment.

Architecture: SDK-compatible scheduler using run_job_loop pattern.
Pattern Reference: src/services/crm/brevo_sync_scheduler.py

This scheduler:
1. Runs every N minutes (configured via N8N_SYNC_SCHEDULER_INTERVAL_MINUTES)
2. Fetches contacts with n8n_processing_status = 'Queued'
3. Processes each contact via N8nSyncService.process_single_contact()
4. Handles retries automatically based on next_retry_at timestamp
"""

import logging
from sqlalchemy import asc

from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.wf8_contact import Contact
from src.models.enums import CRMProcessingStatus
from ..crm.wf8_n8n_sync_service import N8nSyncService

logger = logging.getLogger(__name__)


async def process_n8n_sync_queue():
    """
    Processes contacts marked as 'Queued' for n8n webhook sync using the SDK job loop.

    This function:
    1. Queries contacts with n8n_processing_status = 'Queued'
    2. Processes each contact via N8nSyncService.process_single_contact()
    3. Automatically handles status transitions via run_job_loop

    Note: Retry logic (next_retry_at filtering) is handled in the service layer,
    not in the scheduler, as the SDK run_job_loop() does not support additional_filters.

    Called by: APScheduler at configured interval
    Frequency: N8N_SYNC_SCHEDULER_INTERVAL_MINUTES (default: 5 minutes)
    Batch Size: N8N_SYNC_SCHEDULER_BATCH_SIZE (default: 10)
    """
    service = N8nSyncService()
    logger.info("🚀 Starting n8n webhook sync scheduler cycle")

    await run_job_loop(
        model=Contact,
        status_enum=CRMProcessingStatus,
        queued_status=CRMProcessingStatus.Queued,
        processing_status=CRMProcessingStatus.Processing,
        completed_status=CRMProcessingStatus.Complete,
        failed_status=CRMProcessingStatus.Error,
        processing_function=service.process_single_contact,
        batch_size=settings.N8N_SYNC_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Contact.updated_at),
        status_field_name="n8n_processing_status",
        error_field_name="n8n_processing_error",
    )

    logger.info("✅ Finished n8n webhook sync scheduler cycle")


from src.scheduler_instance import scheduler


def setup_n8n_sync_scheduler():
    """
    Adds the n8n webhook sync job to the main scheduler.

    Configuration (from settings.py):
    - N8N_WEBHOOK_URL: Required - scheduler will not start if missing
    - N8N_SYNC_SCHEDULER_INTERVAL_MINUTES: How often to run (default: 5)
    - N8N_SYNC_SCHEDULER_BATCH_SIZE: Contacts per batch (default: 10)
    - N8N_SYNC_SCHEDULER_MAX_INSTANCES: Concurrent instances (default: 1)

    Safety:
    - Scheduler disabled if N8N_WEBHOOK_URL not configured
    - max_instances=1 prevents race conditions
    - misfire_grace_time=1800 (30min) handles temporary downtime
    """
    # Safety check: Don't start scheduler if webhook URL not configured
    if not settings.N8N_WEBHOOK_URL:
        logger.warning("⚠️ N8N_WEBHOOK_URL not configured - n8n sync scheduler DISABLED")
        logger.warning("   Set N8N_WEBHOOK_URL in .env to enable automatic n8n webhook sync")
        return

    logger.info("📋 Configuring n8n webhook sync scheduler...")
    logger.info(
        f"   Interval: {settings.N8N_SYNC_SCHEDULER_INTERVAL_MINUTES} minutes"
    )
    logger.info(f"   Batch size: {settings.N8N_SYNC_SCHEDULER_BATCH_SIZE} contacts")
    logger.info(f"   Max instances: {settings.N8N_SYNC_SCHEDULER_MAX_INSTANCES}")
    logger.info(f"   Webhook URL: {settings.N8N_WEBHOOK_URL}")

    scheduler.add_job(
        process_n8n_sync_queue,
        trigger="interval",
        minutes=settings.N8N_SYNC_SCHEDULER_INTERVAL_MINUTES,
        id="n8n_webhook_sync_processor",
        name="n8n Webhook Sync Processor",
        replace_existing=True,
        max_instances=settings.N8N_SYNC_SCHEDULER_MAX_INSTANCES,
        misfire_grace_time=1800,  # 30 minutes grace time for temporary downtime
    )

    logger.info("✅ n8n webhook sync scheduler job registered successfully")
