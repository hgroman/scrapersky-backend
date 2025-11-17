"""
Direct Page Submission Router (WO-009).

Implements /api/v3/pages/direct-submit endpoint to allow users to submit
individual page URLs directly, bypassing WF1-WF5 (Google Maps → Sitemap Import).

Entry Point: WF7 (Page Curation)
Bypass: WF1, WF2, WF3, WF4, WF5
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from urllib.parse import urlparse
import uuid

from src.db.session import get_db_session
from src.auth.dependencies import get_current_user
from src.models.page import Page, PageCurationStatus, PageProcessingStatus
from src.models.domain import Domain, SitemapCurationStatusEnum
from src.models.tenant import DEFAULT_TENANT_ID
from src.schemas.pages_direct_submission_schemas import (
    DirectPageSubmissionRequest,
    DirectPageSubmissionResponse,
)

router = APIRouter(prefix="/api/v3/pages", tags=["V3 - Pages Direct Submission"])


def extract_domain(url: str) -> str:
    """
    Extract domain name from URL.

    Examples:
        'https://www.example.com/page' -> 'example.com'
        'https://example.com/contact' -> 'example.com'
        'http://subdomain.example.com' -> 'subdomain.example.com'
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    # Remove 'www.' prefix if present
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


@router.post("/direct-submit", response_model=DirectPageSubmissionResponse)
async def submit_pages_directly(
    request: DirectPageSubmissionRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit page URLs directly for WF7 processing, bypassing WF1-WF5.

    **Use Case:**
    - User has specific URLs to scrape
    - Bypass Google Maps and sitemap discovery
    - Direct entry to WF7 (Page Curation)

    **Auto-Queue Behavior:**
    - `auto_queue=True`: Sets status to Selected + Queued (WF7 picks up immediately)
    - `auto_queue=False`: Sets status to New + NULL (requires manual curation)

    **Constraints:**
    - Maximum 100 URLs per request
    - Duplicate URLs are rejected with 409 Conflict
    - Requires authentication

    **Status Initialization:**
    - `page_curation_status`: "Selected" if auto_queue, else "New"
    - `page_processing_status`: "Queued" if auto_queue, else NULL
    - `domain_id`: Auto-created via get-or-create pattern (REQUIRED)
    - `sitemap_file_id`: NULL (not from sitemap workflow)

    **Domain Handling:**
    - Extracts domain from URL (e.g., 'example.com' from 'https://www.example.com/page')
    - Creates domain record if doesn't exist
    - Links page to domain (maintains referential integrity)
    """
    page_ids = []

    async with session.begin():
        for url in request.urls:
            url_str = str(url)

            # Check for duplicates
            existing_check = await session.execute(
                select(Page).where(Page.url == url_str)
            )
            existing_page = existing_check.scalar_one_or_none()

            if existing_page:
                raise HTTPException(
                    status_code=409,
                    detail=f"Page already exists: {url_str} (ID: {existing_page.id})",
                )

            # CRITICAL: Get or create domain (domain_id has nullable=False constraint)
            domain_name = extract_domain(url_str)
            domain_result = await session.execute(
                select(Domain).where(Domain.domain == domain_name)
            )
            domain = domain_result.scalar_one_or_none()

            if not domain:
                # Auto-create domain for direct submission
                domain = Domain(
                    id=uuid.uuid4(),
                    domain=domain_name,
                    tenant_id=uuid.UUID(DEFAULT_TENANT_ID),  # REQUIRED (nullable=False)
                    local_business_id=None,  # NULL OK (nullable=True per SYSTEM_MAP.md)
                    sitemap_curation_status=SitemapCurationStatusEnum.New,
                    sitemap_analysis_status=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(domain)
                await session.flush()  # Get domain.id before using it

            # Create page with proper status initialization
            page = Page(
                id=uuid.uuid4(),
                url=url_str,
                # Foreign keys
                domain_id=domain.id,  # REQUIRED (nullable=False per SYSTEM_MAP.md)
                sitemap_file_id=None,  # NULL OK (nullable=True)
                # DUAL-STATUS PATTERN (CRITICAL)
                page_curation_status=(
                    PageCurationStatus.Selected
                    if request.auto_queue
                    else PageCurationStatus.New
                ),
                page_processing_status=(
                    PageProcessingStatus.Queued if request.auto_queue else None
                ),
                # Metadata
                priority_level=request.priority_level,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                user_id=current_user.get("user_id"),
                # Honeybee fields (NULL for direct submission)
                page_category=None,
                category_confidence=None,
                depth=None,
            )

            session.add(page)
            await session.flush()  # Get page.id
            page_ids.append(page.id)

    return DirectPageSubmissionResponse(
        submitted_count=len(page_ids),
        page_ids=page_ids,
        auto_queued=request.auto_queue,
    )
