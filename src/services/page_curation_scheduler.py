import logging
from sqlalchemy import asc
from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import get_settings
from src.models.page import Page
from src.models.enums import PageProcessingStatus
from src.services.page_curation_service import PageCurationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_page_curation_queue():
    """
    Processes pages marked as 'Queued' for curation using the SDK job loop.
    """
    settings = get_settings()
    service = PageCurationService()
    logger.info("Starting page curation queue processing cycle.")

    await run_job_loop(
        model=Page,
        status_enum=PageProcessingStatus,
        queued_status=PageProcessingStatus.Queued,
        processing_status=PageProcessingStatus.Processing,
        completed_status=PageProcessingStatus.Complete,
        failed_status=PageProcessingStatus.Error,
        processing_function=service.process_single_page_for_curation,
        batch_size=settings.PAGE_CURATION_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Page.updated_at),
        status_field_name="page_processing_status",
        error_field_name="page_processing_error",
    )
    logger.info("Finished page curation queue processing cycle.")

from src.scheduler_instance import scheduler

def setup_page_curation_scheduler():
    """Adds the page curation job to the main scheduler."""
    scheduler.add_job(
        process_page_curation_queue,
        "interval",
        minutes=get_settings().PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES,
        id="v2_page_curation_processor",
        replace_existing=True,
        max_instances=get_settings().PAGE_CURATION_SCHEDULER_MAX_INSTANCES,
    )
    logger.info("Page curation scheduler job added.")