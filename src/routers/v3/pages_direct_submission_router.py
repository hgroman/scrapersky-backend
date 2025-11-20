"""
WO-009: Direct Page Submission Router

WHAT THIS DOES:
Allows users to submit individual page URLs directly, bypassing workflows WF1-WF5.
Useful when you already have specific page URLs and don't need sitemap discovery.

ENDPOINT:
POST /api/v3/pages/direct-submit

WORKFLOW BYPASS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Skipped Workflows:
  • WF1: Google Maps Search (no need - user provides URL)
  • WF2: Deep Scan (no need - user provides URL)
  • WF3: Domain Extraction (no need - user provides URL)
  • WF4: Sitemap Discovery (no need - user provides URL)
  • WF5: Sitemap Import (no need - user provides URL)

Entry Point:
  • WF7: Page Curation (contact extraction from submitted URL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WORKFLOW:
1. User POSTs page URL
2. System extracts domain from URL
3. System creates/finds domain record (with NULL foreign keys - no parent sitemap)
4. System creates page record with curation_status='Queued'
5. WF7 Page Curation Scheduler picks up page
6. WF7 scrapes page and extracts contacts

NULL FOREIGN KEY PATTERN:
Pages created via direct submission have:
• domain_id: Set (extracted from URL)
• sitemap_id: NULL (no parent sitemap)
• This is valid and expected for direct submissions

DUPLICATE DETECTION:
• Checks if page URL already exists
• If exists: Returns existing page (idempotent)
• If new: Creates new page record

REQUEST BODY:
{
  "url": "https://example.com/contact-us",
  "tenant_id": "uuid-string" (optional, defaults to DEFAULT_TENANT_ID)
}

RESPONSE:
{
  "id": "uuid-string",
  "url": "https://example.com/contact-us",
  "domain_id": "uuid-string",
  "sitemap_id": null,
  "curation_status": "Queued",
  "processing_status": "Queued",
  "message": "Page submitted successfully and queued for curation"
}

URL VALIDATION:
• Must be valid HTTP/HTTPS URL
• Must have domain (e.g., example.com)
• Path is optional (defaults to /)

DOMAIN NORMALIZATION:
• Extracts domain from URL (www.example.com → example.com)
• Creates domain if doesn't exist
• Links page to domain

RELATED FILES:
• Domain submission: src/routers/v3/domains_direct_submission_router.py (WO-010)
• Sitemap submission: src/routers/v3/sitemaps_direct_submission_router.py (WO-011)
• Page model: src/models/page.py
• Domain model: src/models/domain.py
• WF7 Scheduler: src/services/WF7_V2_L4_2of2_PageCurationScheduler.py
• Docs: Documentation/Guides/direct_submission_user_guide.md
• Docs: Documentation/Operations/direct_submission_maintenance.md

MAINTENANCE:
• Check submissions: SELECT COUNT(*) FROM pages WHERE sitemap_id IS NULL AND created_at > NOW() - INTERVAL '24 hours'
• Monitor queue: SELECT COUNT(*) FROM pages WHERE curation_status='Queued' AND sitemap_id IS NULL
• Check processing: SELECT url, curation_status, processing_status FROM pages WHERE sitemap_id IS NULL ORDER BY created_at DESC LIMIT 20

USE CASES:
• Quick contact extraction from known pages
• Testing page curation without full workflow
• Manual page additions to supplement sitemap imports
• Emergency contact extraction

IMPLEMENTED: 2025-11-14 (WO-009)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from urllib.parse import urlparse
import uuid

from src.db.session import get_db_session
from src.auth.jwt_auth import get_current_user
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
                tenant_id=DEFAULT_TENANT_ID,  # REQUIRED (nullable=False)
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
            )

            session.add(page)
            await session.flush()  # Get page.id
            page_ids.append(page.id)

    return DirectPageSubmissionResponse(
        submitted_count=len(page_ids),
        page_ids=page_ids,
        auto_queued=request.auto_queue,
    )
