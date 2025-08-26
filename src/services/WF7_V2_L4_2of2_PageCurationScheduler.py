import logging
from sqlalchemy import asc
from src.common.curation_sdk.scheduler_loop import run_job_loop
from ..config.settings import settings
from ..models.page import Page
from ..models.enums import PageProcessingStatus, PageCurationStatus
from .WF7_V2_L4_1of2_PageCurationService import PageCurationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_page_curation_queue():
    """
    Processes pages marked as 'Queued' for curation using the SDK job loop.
    """
    # settings already imported at module level
    service = PageCurationService()
    logger.info("Starting page curation queue processing cycle.")

    await run_job_loop(
        model=Page,
        status_enum=PageCurationStatus,
        queued_status=PageCurationStatus.Selected,
        processing_status=PageCurationStatus.Processing,
        completed_status=PageCurationStatus.Complete,
        failed_status=PageCurationStatus.Error,
        processing_function=service.process_single_page_for_curation,
        batch_size=settings.PAGE_CURATION_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Page.updated_at),
        status_field_name="page_curation_status",
        error_field_name="page_processing_error",
    )
    logger.info("Finished page curation queue processing cycle.")

from src.scheduler_instance import scheduler

def setup_page_curation_scheduler():
    """Adds the page curation job to the main scheduler."""
    scheduler.add_job(
        process_page_curation_queue,
        "interval",
        minutes=settings.PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES,
        id="v2_page_curation_processor",
        replace_existing=True,
        max_instances=settings.PAGE_CURATION_SCHEDULER_MAX_INSTANCES,
    )
    logger.info("Page curation scheduler job added.")