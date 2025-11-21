"""
FastAPI router for direct domain submission (WO-010).

Implements /api/v3/domains/direct-submit endpoint for bypassing WF1-WF2.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from src.db.session import get_db_session
from src.auth.jwt_auth import get_current_user
from src.models.wf4_domain import (
    Domain,
    SitemapCurationStatusEnum,
    SitemapAnalysisStatusEnum,
)
from src.models.tenant import DEFAULT_TENANT_ID
from src.schemas.domains_direct_submission_schemas import (
    DirectDomainSubmissionRequest,
    DirectDomainSubmissionResponse,
)

router = APIRouter(prefix="/api/v3/domains", tags=["V3 - Domains Direct Submission"])


@router.post("/direct-submit", response_model=DirectDomainSubmissionResponse)
async def submit_domains_directly(
    request: DirectDomainSubmissionRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit domain names directly for sitemap discovery, bypassing WF1-WF2.

    **Use Case:**
    - User has list of domains to analyze
    - Bypass Google Maps search and place details
    - Direct entry to WF4 (Sitemap Discovery)

    **Auto-Queue Behavior:**
    - `auto_queue=True`: Sets status to Selected + queued (WF4 picks up immediately)
    - `auto_queue=False`: Sets status to New + NULL (requires manual curation)

    **Domain Format:**
    Accepts any of these formats (all normalized to "example.com"):
    - "example.com"
    - "www.example.com"
    - "https://example.com"
    - "https://www.example.com/path"

    **Constraints:**
    - Maximum 100 domains per request
    - Duplicate domains are rejected with 409 Conflict
    - Requires authentication

    **Status Initialization:**
    - `sitemap_curation_status`: "Selected" if auto_queue, else "New"
    - `sitemap_analysis_status`: "queued" if auto_queue, else NULL
    - `local_business_id`: NULL (not from Google Maps workflow)
    - `tenant_id`: DEFAULT_TENANT_ID (required field)
    """
    domain_ids = []
    normalized_domains = []

    # Domains are already validated and normalized by pydantic
    normalized_domains = request.domains

    # Deduplicate in case multiple input variations normalize to same domain
    # e.g., ["www.example.com", "https://example.com"] both become "example.com"
    normalized_domains = list(dict.fromkeys(normalized_domains))

    async with session.begin():
        for domain_str in normalized_domains:

            # Check for duplicates
            existing_check = await session.execute(
                select(Domain).where(Domain.domain == domain_str)
            )
            existing_domain = existing_check.scalar_one_or_none()

            if existing_domain:
                raise HTTPException(
                    status_code=409,
                    detail=f"Domain already exists: {domain_str} (ID: {existing_domain.id})",
                )

            # Create domain with proper status initialization
            domain = Domain(
                id=uuid.uuid4(),
                domain=domain_str,
                # Required fields
                tenant_id=uuid.UUID(DEFAULT_TENANT_ID),  # REQUIRED (nullable=False)
                # NULL foreign key (not from WF2 flow)
                local_business_id=None,
                # DUAL-STATUS PATTERN (CRITICAL)
                # Note: ENUM values have inconsistent casing (this is existing code behavior)
                sitemap_curation_status=(
                    SitemapCurationStatusEnum.Selected
                    if request.auto_queue
                    else SitemapCurationStatusEnum.New
                ),
                sitemap_analysis_status=(
                    SitemapAnalysisStatusEnum.queued if request.auto_queue else None
                ),
                # Metadata (NULL for direct submission)
                # Timestamps
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(domain)
            domain_ids.append(domain.id)

    return DirectDomainSubmissionResponse(
        submitted_count=len(domain_ids),
        domain_ids=domain_ids,
        auto_queued=request.auto_queue,
        normalized_domains=normalized_domains,
    )
