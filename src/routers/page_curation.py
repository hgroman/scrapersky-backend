import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.page import Page, PageCurationStatus, PageProcessingStatus
from src.schemas.page_curation import (
    PageCurationUpdateRequest,
    PageCurationUpdateResponse,
)
from src.session.async_session import get_session_dependency

from src.auth.jwt_auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/pages/curation-status", response_model=PageCurationUpdateResponse)
async def update_page_curation_status_batch(
    request: PageCurationUpdateRequest,
    session: AsyncSession = Depends(get_session_dependency),  # noqa: B008
    current_user: Dict[str, Any] = Depends(get_current_user),  # Example
):
    """
    Updates the page_curation_status for a batch of pages.
    If the target curation status is 'Queued', this endpoint will also set the
    page_processing_status to 'Queued' and clear any previous processing errors.
    """
    target_curation_status = request.curation_status
    logger.info(
        "Updating %d pages to status: %s",
        len(request.page_ids),
        target_curation_status.value,
    )

    should_queue_for_processing = target_curation_status == PageCurationStatus.Queued

    update_values: Dict[Any, Any] = {Page.page_curation_status: target_curation_status}

    if should_queue_for_processing:
        logger.debug("Queueing pages %s for processing.", request.page_ids)
        update_values[Page.page_processing_status] = PageProcessingStatus.Queued
        update_values[Page.page_processing_error] = None

    async with session.begin():
        stmt = (
            update(Page)
            .where(Page.id.in_(request.page_ids))
            .values(update_values)
            .returning(Page.id)
        )
        result = await session.execute(stmt)
        updated_ids = result.scalars().all()
        count = len(updated_ids)
        logger.info("Database update successful for %d page IDs.", count)

    if count != len(request.page_ids):
        logger.warning(
            "Req %d updates, but only %d found/updated.",
            len(request.page_ids),
            count,
        )

    response_message = (
        f"Updated {count} page(s) to status '{target_curation_status.value}'."
    )
    if should_queue_for_processing and count > 0:
        response_message += f" {count} page(s) also queued for processing."

    return PageCurationUpdateResponse(message=response_message, updated_count=count)
