"""
Direct Sitemap Submission Router (WO-011).

Implements /api/v3/sitemaps/direct-submit endpoint to allow users to submit
sitemap URLs directly, bypassing WF1-WF4 (Google Maps → Sitemap Discovery).

Entry Point: WF5 (Sitemap Import)
Bypass: WF1, WF2, WF3, WF4
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from urllib.parse import urlparse
import uuid

from src.db.session import get_db_session
from src.auth.dependencies import get_current_user
from src.models.sitemap import (
    SitemapFile,
    SitemapImportCurationStatusEnum,
    SitemapImportProcessStatusEnum,
)
from src.models.domain import Domain, SitemapCurationStatusEnum
from src.models.tenant import DEFAULT_TENANT_ID
from src.schemas.sitemaps_direct_submission_schemas import (
    DirectSitemapSubmissionRequest,
    DirectSitemapSubmissionResponse,
)

router = APIRouter(
    prefix="/api/v3/sitemaps", tags=["V3 - Sitemaps Direct Submission"]
)


def extract_domain_from_sitemap_url(url: str) -> str:
    """
    Extract domain name from sitemap URL.

    Examples:
        'https://www.example.com/sitemap.xml' -> 'example.com'
        'https://example.com/sitemaps/index.xml' -> 'example.com'
        'http://subdomain.site.org/sitemap.xml' -> 'subdomain.site.org'
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    # Remove 'www.' prefix if present
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


@router.post("/direct-submit", response_model=DirectSitemapSubmissionResponse)
async def submit_sitemaps_directly(
    request: DirectSitemapSubmissionRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit sitemap URLs directly for WF5 import, bypassing WF1-WF4.

    **Use Case:**
    - User knows specific sitemap URLs to import
    - Bypass Google Maps, domain extraction, and sitemap discovery
    - Direct entry to WF5 (Sitemap Import)

    **Auto-Import Behavior:**
    - `auto_import=True`: Sets status to Selected + Queued (WF5 picks up immediately)
    - `auto_import=False`: Sets status to New + NULL (requires manual curation)

    **Domain Handling:**
    - Extracts domain from sitemap URL (e.g., 'example.com' from 'https://example.com/sitemap.xml')
    - Creates domain record if doesn't exist
    - Links sitemap to domain (maintains referential integrity)

    **Constraints:**
    - Maximum 50 sitemap URLs per request
    - URLs must end with .xml or contain 'sitemap'
    - Duplicate URLs are rejected with 409 Conflict
    - Requires authentication

    **Status Initialization:**
    - `deep_scrape_curation_status`: "Selected" if auto_import, else "New"
    - `sitemap_import_status`: "Queued" if auto_import, else NULL
    - `domain_id`: Auto-created via get-or-create pattern (REQUIRED)
    """
    sitemap_ids = []

    async with session.begin():
        for sitemap_url in request.sitemap_urls:
            url_str = str(sitemap_url)

            # Check for duplicates
            existing_check = await session.execute(
                select(SitemapFile).where(SitemapFile.url == url_str)
            )
            existing_sitemap = existing_check.scalar_one_or_none()

            if existing_sitemap:
                raise HTTPException(
                    status_code=409,
                    detail=f"Sitemap already exists: {url_str} (ID: {existing_sitemap.id})",
                )

            # CRITICAL: Get or create domain (domain_id has nullable=False constraint)
            domain_name = extract_domain_from_sitemap_url(url_str)
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

            # Create sitemap file with proper status initialization
            sitemap_file = SitemapFile(
                id=uuid.uuid4(),
                url=url_str,
                # Foreign key
                domain_id=domain.id,  # REQUIRED (nullable=False per SYSTEM_MAP.md)
                # DUAL-STATUS PATTERN (CRITICAL)
                deep_scrape_curation_status=(
                    SitemapImportCurationStatusEnum.Selected
                    if request.auto_import
                    else SitemapImportCurationStatusEnum.New
                ),
                sitemap_import_status=(
                    SitemapImportProcessStatusEnum.Queued
                    if request.auto_import
                    else None
                ),
                # Required fields
                sitemap_type="STANDARD",  # REQUIRED (nullable=False) - default for direct submissions
                # Metadata (NULL initially, populated after import)
                url_count=None,
                last_modified=None,
                file_size=None,
                # Timestamps
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                user_id=current_user.get("user_id"),
            )

            session.add(sitemap_file)
            await session.flush()  # Get sitemap_file.id
            sitemap_ids.append(sitemap_file.id)

    return DirectSitemapSubmissionResponse(
        submitted_count=len(sitemap_ids),
        sitemap_ids=sitemap_ids,
        auto_queued=request.auto_import,
    )
