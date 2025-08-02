import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.session import get_db_session
from src.models.page import Page
from src.models.enums import PageCurationStatus, PageProcessingStatus

router = APIRouter(prefix="/api/v2/pages", tags=["V2 - Page Curation"])

class PageBatchStatusUpdateRequest(BaseModel):
    page_ids: List[uuid.UUID]
    status: PageCurationStatus

class BatchUpdateResponse(BaseModel):
    updated_count: int
    queued_count: int

@router.put("/status", response_model=BatchUpdateResponse, status_code=status.HTTP_200_OK)
async def update_page_curation_status_batch(
    request: PageBatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Batch update the curation status of pages and queue them for processing if 'Selected'.
    """
    updated_count = 0
    queued_count = 0

    async with session.begin():
        stmt = select(Page).where(Page.id.in_(request.page_ids))
        result = await session.execute(stmt)
        pages_to_update = result.scalars().all()

        if not pages_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pages found with the provided IDs.",
            )

        for page in pages_to_update:
            page.page_curation_status = request.status
            updated_count += 1

            # Dual-Status Update Pattern
            if request.status == PageCurationStatus.Selected:
                page.page_processing_status = PageProcessingStatus.Queued
                page.page_processing_error = None  # Clear previous errors
                queued_count += 1

    return BatchUpdateResponse(updated_count=updated_count, queued_count=queued_count)
