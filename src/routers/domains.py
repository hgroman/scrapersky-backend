"""
API Router for Domain Curation and Management.

Provides endpoints for listing domains with filtering/pagination and
batch updating sitemap curation status.
"""

import logging
import math
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func  # Import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# from src.services.security import get_current_user # Assuming security setup exists
# from src.auth.security import get_current_user # Trying common auth location
from src.auth.jwt_auth import get_current_user  # Corrected based on other routers

# Project specifics
from src.db.session import (
    get_db_session,  # Import the correct session dependency
)
from src.models.api_models import (
    DomainBatchCurationStatusUpdateRequest,
    DomainFilteredUpdateRequest,
    DomainBatchUpdateResponse,
    DomainRecord,
    PaginatedDomainResponse,
)
from src.models.domain import (
    Domain,
    SitemapAnalysisStatusEnum,
    SitemapCurationStatusEnum,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v3/domains",
    tags=["Domains"],
    # dependencies=[Depends(get_current_user)], # Apply auth to all routes if needed
)

# Allowed sort fields mapping (DB Column Name -> Model Attribute)
# Prevents arbitrary column sorting
ALLOWED_SORT_FIELDS = {
    "domain": Domain.domain,
    "created_at": Domain.created_at,
    "updated_at": Domain.updated_at,
    "sitemap_curation_status": Domain.sitemap_curation_status,
    "sitemap_analysis_status": Domain.sitemap_analysis_status,
    "status": Domain.status,  # Original domain status
}


@router.get("", response_model=PaginatedDomainResponse)
async def list_domains(
    session: AsyncSession = Depends(get_db_session),  # Correct dependency for routers
    current_user: Dict[str, Any] = Depends(get_current_user),  # More specific type hint
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    sort_by: Optional[str] = Query(
        "updated_at",
        description=(
            f"Field to sort by. Allowed fields: {', '.join(ALLOWED_SORT_FIELDS.keys())}"
        ),
    ),
    sort_desc: bool = Query(True, description="Sort in descending order"),
    sitemap_curation_status: Optional[SitemapCurationStatusEnum] = Query(
        None, description="Filter by sitemap curation status"
    ),
    domain_filter: Optional[str] = Query(
        None, description="Filter by domain name (case-insensitive, partial match)"
    ),
):
    """
    List domains with pagination, filtering, and sorting.

    Supports filtering by sitemap_curation_status and domain name.
    Supports sorting by various domain fields.
    """
    user_sub = current_user.get("sub", "unknown_user")  # Provide default
    logger.info(
        f"User {user_sub} listing domains: page={page}, size={size}, "
        f"sort_by={sort_by}, sort_desc={sort_desc}, "
        f"curation_status={sitemap_curation_status}, "
        f"domain_filter={domain_filter}"
    )

    # Validate sort_by field
    if sort_by and sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid sort field '{sort_by}'. Allowed fields: "
                f"{', '.join(ALLOWED_SORT_FIELDS.keys())}"
            ),
        )

    # Determine the sort column, using the default if sort_by is None or invalid (though invalid checked above)
    sort_column_key = sort_by if sort_by else "updated_at"  # Use default if None
    sort_column = ALLOWED_SORT_FIELDS.get(
        sort_column_key, Domain.updated_at
    )  # Use default sort
    sort_direction = desc if sort_desc else asc

    # --- Build Base Query ---
    base_query = select(Domain)

    # --- Apply Filters ---
    filters = []
    if sitemap_curation_status:
        filters.append(Domain.sitemap_curation_status == sitemap_curation_status)
        logger.debug(
            f"Applying filter: sitemap_curation_status == {sitemap_curation_status}"
        )
    if domain_filter:
        filters.append(Domain.domain.ilike(f"%{domain_filter}%"))
        logger.debug(f"Applying filter: domain ilike %{domain_filter}%")

    # Apply filters to the main query
    if filters:
        base_query = base_query.where(*filters)

    # --- Get Total Count (with filters) ---
    # Correctly build the count query by applying filters individually
    count_query = select(func.count(Domain.id)).select_from(Domain)
    if filters:
        count_query = count_query.where(*filters)  # Apply filters correctly here too

    count_result = await session.execute(count_query)
    total = count_result.scalar_one()
    logger.debug(f"Total domains matching filters: {total}")

    # --- Apply Sorting and Pagination ---
    query = (
        base_query.order_by(sort_direction(sort_column))
        .offset((page - 1) * size)
        .limit(size)
    )

    # --- Execute Query ---
    results = await session.execute(query)
    items: List[Domain] = cast(List[Domain], results.scalars().all())  # Cast to List
    logger.debug(f"Fetched {len(items)} domain records for page {page}")

    # --- Prepare Response ---
    pages = math.ceil(total / size) if total > 0 else 0

    return PaginatedDomainResponse(
        items=[
            DomainRecord.model_validate(item) for item in items
        ],  # Use model_validate for Pydantic v2
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.put("/sitemap-curation/status", response_model=Dict[str, int])
async def update_domain_sitemap_curation_status_batch(
    session: AsyncSession = Depends(get_db_session),  # Correct dependency for routers
    request_body: DomainBatchCurationStatusUpdateRequest = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Batch update the sitemap_curation_status for multiple domains.

    If the status is set to 'Selected', it also queues the domain for
    sitemap analysis by setting sitemap_analysis_status to 'queued'.
    """
    user_sub = current_user.get("sub", "unknown_user")
    logger.info(
        f"User {user_sub} requesting batch sitemap curation update for "
        f"{len(request_body.domain_ids)} domains to status "
        f"'{request_body.sitemap_curation_status.value}'"
    )

    domain_ids = request_body.domain_ids
    api_status = request_body.sitemap_curation_status

    # Map API Enum to DB Enum (should match directly based on definition)
    try:
        db_curation_status = SitemapCurationStatusEnum[
            api_status.name
        ]  # Use .name for reliable mapping
    except KeyError as e:
        # Log the error including the invalid value received
        logger.error(
            f"Invalid API status value received: {api_status.value}", exc_info=True
        )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sitemap curation status value: {api_status.value}",
        ) from e

    updated_count = 0
    queued_count = 0

    # Fetch domains within a single query
    stmt = select(Domain).where(Domain.id.in_(domain_ids))
    result = await session.execute(stmt)
    domains_to_update = result.scalars().all()

    if len(domains_to_update) != len(domain_ids):
        found_ids = {str(d.id) for d in domains_to_update}
        missing_ids = [str(uid) for uid in domain_ids if str(uid) not in found_ids]
        logger.warning(
            f"Could not find all requested domains. Missing IDs: {missing_ids}"
        )
        # Proceed with updating the ones found, but log the warning.
        # Depending on requirements, could raise an error here.

    if not domains_to_update:
        logger.warning("No valid domains found to update.")
        return {"updated_count": 0, "queued_count": 0}

    try:
        for domain in domains_to_update:
            # Update the curation status
            domain.sitemap_curation_status = db_curation_status  # type: ignore
            updated_count += 1
            logger.debug(
                f"Updating domain {domain.id} sitemap_curation_status to "
                f"{db_curation_status.value}"
            )

            # Conditional logic: If status is 'Selected', queue for analysis
            if db_curation_status == SitemapCurationStatusEnum.Selected:
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.queued  # type: ignore
                domain.sitemap_analysis_error = None  # type: ignore # Clear previous errors
                queued_count += 1
                logger.debug(
                    f"Setting domain {domain.id} sitemap_analysis_status to queued"
                )
            # Add domain to session implicitly via modification

        # Rely on session context / middleware for commit/rollback
        await session.commit()  # Explicitly commit changes
    except Exception as e:
        logger.error(f"Error during domain status update: {e}", exc_info=True)
        await session.rollback()  # Rollback on error
        raise HTTPException(
            status_code=500, detail="Internal server error during database update."
        ) from e

    logger.info(
        f"Batch sitemap curation update completed by {user_sub}. "
        f"Updated: {updated_count}, Queued for analysis: {queued_count}"
    )

    return {"updated_count": updated_count, "queued_count": queued_count}


@router.put("/sitemap-curation/status/filtered", response_model=DomainBatchUpdateResponse)
async def update_domain_sitemap_curation_status_filtered(
    request: DomainFilteredUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update ALL domains matching filter criteria with new sitemap curation status.
    
    Enables 'Select All' functionality by applying updates to filtered results
    rather than requiring explicit domain ID lists.
    
    Implements same dual-status pattern:
    - Updates sitemap_curation_status to requested value
    - If status is 'Selected', triggers sitemap analysis by setting sitemap_analysis_status to 'queued'
    
    Args:
        request: Filtered update request with criteria and target status
        session: Database session (injected)
        current_user: Authenticated user context (injected)
    
    Returns:
        DomainBatchUpdateResponse with update and queue counts
    
    Raises:
        HTTPException: If no domains found matching the provided filter criteria
    """
    user_sub = current_user.get("sub", "unknown_user")
    logger.info(
        f"User {user_sub} requesting filtered domain curation update to status "
        f"'{request.sitemap_curation_status.value}' with filters: "
        f"status_filter={request.sitemap_curation_status_filter}, domain_filter='{request.domain_filter}'"
    )
    
    # Build filter conditions (same logic as GET endpoint)
    # NOTE: Domain router does not use tenant filtering (per existing pattern)
    filters = []
    
    if request.sitemap_curation_status_filter is not None:
        # Map API enum to DB enum (same logic as existing batch endpoint)
        db_filter_status = next(
            (member for member in SitemapCurationStatusEnum if member.name == request.sitemap_curation_status_filter.name),
            None,
        )
        if db_filter_status is None:
            logger.error(
                f"API filter status '{request.sitemap_curation_status_filter.name}' has no matching member in DB SitemapCurationStatusEnum"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sitemap curation status filter: {request.sitemap_curation_status_filter.value}",
            )
        filters.append(Domain.sitemap_curation_status == db_filter_status)
    
    if request.domain_filter:
        filters.append(Domain.domain.ilike(f"%{request.domain_filter}%"))
    
    # Map target status from API enum to DB enum (same logic as existing batch endpoint)
    db_curation_status = next(
        (member for member in SitemapCurationStatusEnum if member.name == request.sitemap_curation_status.name),
        None,
    )
    if db_curation_status is None:
        logger.error(
            f"API status '{request.sitemap_curation_status.name}' has no matching member in DB SitemapCurationStatusEnum"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sitemap curation status: {request.sitemap_curation_status.value}",
        )
    
    # Determine if sitemap analysis should be triggered
    trigger_sitemap_analysis = db_curation_status == SitemapCurationStatusEnum.Selected
    
    updated_count = 0
    queued_count = 0
    
    try:
        async with session.begin():
            # Get all domains matching filter criteria
            stmt = select(Domain)
            if filters:
                stmt = stmt.where(*filters)
            
            result = await session.execute(stmt)
            domains_to_update = result.scalars().all()
            
            if not domains_to_update:
                logger.warning("No domains found matching the provided filter criteria")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No domains found matching the provided filter criteria"
                )
            
            # Apply updates to all matching domains
            for domain in domains_to_update:
                # Update the curation status
                domain.sitemap_curation_status = db_curation_status  # type: ignore
                updated_count += 1
                logger.debug(
                    f"Updating domain {domain.id} sitemap_curation_status to "
                    f"{db_curation_status.value}"
                )
                
                # Dual-Status Update Pattern - trigger sitemap analysis when Selected
                if trigger_sitemap_analysis:
                    domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.queued  # type: ignore
                    domain.sitemap_analysis_error = None  # type: ignore
                    queued_count += 1
                    logger.debug(f"Queuing domain {domain.id} for sitemap analysis")
            
            logger.info(f"Filtered domain update completed: {updated_count} domains updated, {queued_count} queued for analysis")
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error in filtered domain update: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during filtered domain update"
        ) from e
    
    logger.info(
        f"Batch sitemap curation filtered update completed by {user_sub}. "
        f"Updated: {updated_count}, Queued for analysis: {queued_count}"
    )
    
    return DomainBatchUpdateResponse(
        updated_count=updated_count,
        queued_count=queued_count
    )
