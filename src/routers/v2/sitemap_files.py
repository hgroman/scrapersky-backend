import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.session import get_db_session
from src.models.sitemap import SitemapFile
from src.models.sitemap import (
    SitemapImportCurationStatusEnum,
    SitemapImportProcessStatusEnum,
)

router = APIRouter(prefix="/api/v2/sitemap-files", tags=["V2 - Sitemap Curation"])

class SitemapFileBatchStatusUpdateRequest(BaseModel):
    sitemap_file_ids: List[uuid.UUID]
    status: SitemapImportCurationStatusEnum

class BatchUpdateResponse(BaseModel):
    updated_count: int
    queued_count: int

@router.put("/status", response_model=BatchUpdateResponse, status_code=status.HTTP_200_OK)
async def update_sitemap_curation_status_batch(
    request: SitemapFileBatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Batch update the curation status of sitemap files and queue them for import if 'Selected'.
    """
    updated_count = 0
    queued_count = 0

    async with session.begin():
        stmt = select(SitemapFile).where(SitemapFile.id.in_(request.sitemap_file_ids))
        result = await session.execute(stmt)
        files_to_update = result.scalars().all()

        if not files_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sitemap files found with the provided IDs.",
            )

        for sitemap_file in files_to_update:
            # Update the curation status field (actual column name: deep_scrape_curation_status)
            sitemap_file.deep_scrape_curation_status = request.status
            updated_count += 1

            # Dual-Status Update Pattern
            if request.status == SitemapImportCurationStatusEnum.Selected:
                sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Queued
                sitemap_file.sitemap_import_error = None  # Clear previous errors
                queued_count += 1

    return BatchUpdateResponse(updated_count=updated_count, queued_count=queued_count)
