"""
API Router for Local Business related operations.
"""

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.auth.jwt_auth import (
    get_current_user,  # Corrected import based on places_staging.py
)

# Assuming DB Session, Auth dependencies are similar to other routers
from src.db.session import get_db_session  # Adjust path if necessary
from src.models.api_models import (
    LocalBusinessBatchStatusUpdateRequest,
    LocalBusinessFilteredUpdateRequest,
    LocalBusinessBatchUpdateResponse,
)
from src.schemas.wf3_local_business_schemas import (
    LocalBusinessRecord,
    PaginatedLocalBusinessResponse,
)
from src.models.wf3_local_business import DomainExtractionStatusEnum, LocalBusiness
from src.models.wf1_place_staging import PlaceStatusEnum  # For DB mapping

logger = logging.getLogger(__name__)


# --- API Models --- #
# Models have been moved to src/schemas/local_business_schemas.py


# --- Router Definition --- #
router = APIRouter(prefix="/api/v3/local-businesses", tags=["Local Businesses"])


# --- GET Endpoint Implementation --- #
@router.get(
    "",
    response_model=PaginatedLocalBusinessResponse,
    summary="List Local Businesses (Paginated)",
    description="Retrieves a paginated list of local businesses, allowing filtering and sorting.",
)
async def list_local_businesses(
    status_filter: Optional[PlaceStatusEnum] = Query(
        None,
        alias="status",
        description="Filter by main business status (e.g., New, Selected, Maybe)",
    ),
    business_name: Optional[str] = Query(
        None, description="Filter by business name (case-insensitive partial match)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=200, description="Page size"),
    sort_by: Optional[str] = Query(
        "updated_at",
        description="Field to sort by (e.g., business_name, status, updated_at)",
    ),
    sort_dir: Optional[str] = Query(
        "desc", description="Sort direction: 'asc' or 'desc'"
    ),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Lists local businesses with pagination, filtering, and sorting."""
    tenant_id_str = current_user.get(
        "tenant_id", "550e8400-e29b-41d4-a716-446655440000"
    )  # Use default tenant
    try:
        tenant_uuid = UUID(tenant_id_str)
    except ValueError:
        logger.error(f"Invalid tenant ID format in token: {tenant_id_str}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant ID format"
        )

    logger.info(
        f"Listing local businesses for tenant {tenant_uuid}, filter_status='{status_filter}', filter_name='{business_name}', page={page}, size={size}, sort_by='{sort_by}', sort_dir='{sort_dir}'"
    )

    try:
        # --- Build Base Query --- #
        select_stmt = select(LocalBusiness).where(
            LocalBusiness.tenant_id == tenant_uuid
        )
        count_stmt = (
            select(func.count())
            .select_from(LocalBusiness)
            .where(LocalBusiness.tenant_id == tenant_uuid)
        )

        # --- Apply Filters --- #
        if status_filter:
            # Ensure filtering uses the exact enum member
            select_stmt = select_stmt.where(LocalBusiness.status == status_filter)
            count_stmt = count_stmt.where(LocalBusiness.status == status_filter)

        if business_name:
            select_stmt = select_stmt.where(
                LocalBusiness.business_name.ilike(f"%{business_name}%")
            )  # Case-insensitive search
            count_stmt = count_stmt.where(
                LocalBusiness.business_name.ilike(f"%{business_name}%")
            )

        # --- Calculate Total Count --- #
        total_result = await session.execute(count_stmt)
        total = total_result.scalar_one_or_none() or 0
        total_pages = math.ceil(total / size) if size > 0 else 0

        # --- Apply Sorting --- #
        sort_field = sort_by if sort_by else "updated_at"  # Ensure sort_field is str
        sort_column = getattr(LocalBusiness, sort_field, LocalBusiness.updated_at)

        if sort_dir and sort_dir.lower() == "asc":
            select_stmt = select_stmt.order_by(sort_column.asc())
        else:
            select_stmt = select_stmt.order_by(sort_column.desc())  # Default desc

        # --- Apply Pagination --- #
        offset = (page - 1) * size
        select_stmt = select_stmt.offset(offset).limit(size)

        # --- Execute Query --- #
        logger.debug(f"Executing LocalBusiness query: {select_stmt}")
        result = await session.execute(select_stmt)
        db_items = result.scalars().all()

        # --- Prepare Response --- #
        # Pydantic models with from_attributes=True handle the conversion
        response_items = [LocalBusinessRecord.from_orm(item) for item in db_items]

        return PaginatedLocalBusinessResponse(
            items=response_items, total=total, page=page, size=size, pages=total_pages
        )

    except AttributeError:
        # Use the confirmed sort_field in the error message
        logger.warning(
            f"Invalid sort_by field requested: '{sort_field}'. Check available fields on LocalBusiness model."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field: {sort_field}",
        )
    except Exception as e:
        logger.error(f"Error listing local businesses: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list local businesses",
        )


@router.put("/status", status_code=status.HTTP_200_OK)
async def update_local_businesses_status_batch(
    update_request: LocalBusinessBatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Update the main status for one or more local businesses identified by their UUIDs.

    If the target status is 'Selected', this will also queue the business
    for domain extraction.
    """
    local_business_ids_to_update: List[UUID] = update_request.local_business_ids
    new_api_status = update_request.status  # This is LocalBusinessApiStatusEnum
    user_id = current_user.get("user_id", "unknown")  # Or however user ID is stored

    logger.info(
        f"Received request to update status to '{new_api_status.value}' for {len(local_business_ids_to_update)} local businesses by user '{user_id}'."
    )

    if not local_business_ids_to_update:
        return {
            "message": "No local business IDs provided.",
            "updated_count": 0,
            "queued_count": 0,
        }

    # Map the incoming API status enum member to the DB enum member (PlaceStatusEnum)
    # Compare by NAME for robustness against potential value differences/casing
    target_db_status_member = next(
        (member for member in PlaceStatusEnum if member.name == new_api_status.name),
        None,
    )

    if target_db_status_member is None:
        # This case handles potential mismatches, e.g., if API enum has 'Not_a_Fit' and DB has 'Not a Fit'
        # A more robust mapping might be needed if values differ significantly besides underscores.
        logger.error(
            f"API status '{new_api_status.name}' ({new_api_status.value}) has no matching member name in DB PlaceStatusEnum."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status mapping for '{new_api_status.value}'",
        )

    # Determine if domain extraction should be triggered based on the target DB status
    trigger_domain_extraction = target_db_status_member == PlaceStatusEnum.Selected
    if trigger_domain_extraction:
        logger.info(
            f"Target DB status '{target_db_status_member.name}' will trigger domain extraction queueing."
        )

    # Define which existing domain extraction statuses allow re-queueing (e.g., only if failed or not yet processed)
    eligible_queueing_statuses = [
        None,  # Not yet processed
        DomainExtractionStatusEnum.Error,  # Changed from 'failed' to 'Error' to match new enum
        # Add other statuses if needed (e.g., completed if re-running is desired)
    ]

    updated_count = 0
    actually_queued_count = 0
    now = datetime.utcnow()

    try:
        async with session.begin():  # Start transaction
            # Fetch the relevant LocalBusiness objects
            stmt_select = select(LocalBusiness).where(
                LocalBusiness.id.in_(local_business_ids_to_update)
            )
            result = await session.execute(stmt_select)
            businesses_to_process = result.scalars().all()

            if not businesses_to_process:
                logger.warning(
                    f"No local businesses found for the provided UUIDs: {local_business_ids_to_update}"
                )
                # Return success but indicate nothing was updated/queued
                return {
                    "message": "No matching local businesses found for the provided IDs.",
                    "updated_count": 0,
                    "queued_count": 0,
                }

            updated_count = len(businesses_to_process)

            # Loop and update attributes in Python before the commit
            for business in businesses_to_process:
                business.status = target_db_status_member  # type: ignore # Assign the DB enum member
                business.updated_at = now  # type: ignore
                # TODO: Potentially add updated_by field if tracking user modifications

                # Conditional logic for domain extraction queueing
                if trigger_domain_extraction:
                    # Check eligibility (only queue if not already completed/processing etc.)
                    current_extraction_status = business.domain_extraction_status
                    # REMOVED eligibility check: current_extraction_status in eligible_queueing_statuses:
                    # if current_extraction_status in eligible_queueing_statuses:
                    business.domain_extraction_status = (
                        DomainExtractionStatusEnum.Queued
                    )  # type: ignore # Changed from 'queued' to 'Queued' to match new enum
                    business.domain_extraction_error = None  # type: ignore # Clear any previous error
                    actually_queued_count += 1
                    logger.debug(
                        f"Queuing business {business.id} for domain extraction."
                    )
                    # else:
                    #     logger.debug(f"Business {business.id} not queued. Current domain_extraction_status (\'{current_extraction_status}\') not eligible.")

            # session.begin() handles commit/rollback
            logger.info(f"ORM updates prepared for {updated_count} local businesses.")
            if trigger_domain_extraction:
                logger.info(
                    f"Attempted to queue {actually_queued_count} businesses for domain extraction."
                )

        # After successful commit
        return {
            "message": f"Successfully updated status for {updated_count} local businesses.",
            "updated_count": updated_count,
            "queued_count": actually_queued_count,
        }

    except Exception as e:
        logger.error(f"Error updating local business statuses: {e}", exc_info=True)
        # Let the exception propagate if not handled by session.begin rollback, FastAPI will catch it
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while updating statuses.",
        )


@router.put("/status/filtered", response_model=LocalBusinessBatchUpdateResponse, status_code=status.HTTP_200_OK)
async def update_local_businesses_status_filtered(
    request: LocalBusinessFilteredUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update ALL local businesses matching filter criteria with new status.
    
    Enables 'Select All' functionality by applying updates to filtered results
    rather than requiring explicit local business ID lists.
    
    Implements same dual-status pattern:
    - Updates status to requested value  
    - If status is 'Selected', triggers domain extraction by setting domain_extraction_status to 'Queued'
    
    Args:
        request: Filtered update request with criteria and target status
        session: Database session (injected)
        current_user: Authenticated user context (injected)
    
    Returns:
        LocalBusinessBatchUpdateResponse with update and queue counts
    
    Raises:
        HTTPException: If no local businesses found matching the provided filter criteria
    """
    # Get tenant ID from user context
    tenant_id_str = current_user.get(
        "tenant_id", "550e8400-e29b-41d4-a716-446655440000"
    )
    try:
        tenant_uuid = UUID(tenant_id_str)
    except ValueError:
        logger.error(f"Invalid tenant ID format in token: {tenant_id_str}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant ID format"
        )
    
    # Build filter conditions (same logic as GET endpoint)
    filters = [LocalBusiness.tenant_id == tenant_uuid]  # Always include tenant filter
    
    if request.status_filter is not None:
        # Map API enum to DB enum (same logic as batch endpoint)
        target_filter_db_status = next(
            (member for member in PlaceStatusEnum if member.name == request.status_filter.name),
            None,
        )
        if target_filter_db_status is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter mapping for '{request.status_filter.value}'"
            )
        filters.append(LocalBusiness.status == target_filter_db_status)
    
    if request.business_name:
        filters.append(LocalBusiness.business_name.ilike(f"%{request.business_name}%"))
    
    # Map target status from API enum to DB enum (same logic as batch endpoint)
    target_db_status_member = next(
        (member for member in PlaceStatusEnum if member.name == request.status.name),
        None,
    )
    if target_db_status_member is None:
        logger.error(
            f"API status '{request.status.name}' ({request.status.value}) has no matching member name in DB PlaceStatusEnum."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status mapping for '{request.status.value}'",
        )
    
    # Determine if domain extraction should be triggered
    trigger_domain_extraction = target_db_status_member == PlaceStatusEnum.Selected
    
    updated_count = 0
    queued_count = 0
    now = datetime.utcnow()
    
    try:
        async with session.begin():
            # Get all local businesses matching filter criteria
            stmt = select(LocalBusiness)
            if filters:
                stmt = stmt.where(*filters)
            
            result = await session.execute(stmt)
            businesses_to_update = result.scalars().all()
            
            if not businesses_to_update:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No local businesses found matching the provided filter criteria"
                )
            
            # Apply updates to all matching businesses
            for business in businesses_to_update:
                business.status = target_db_status_member  # type: ignore
                business.updated_at = now  # type: ignore
                updated_count += 1
                
                # Dual-Status Update Pattern - trigger domain extraction when Selected
                if trigger_domain_extraction:
                    business.domain_extraction_status = DomainExtractionStatusEnum.Queued  # type: ignore
                    business.domain_extraction_error = None  # type: ignore
                    queued_count += 1
            
            logger.info(f"Filtered update completed: {updated_count} businesses updated, {queued_count} queued for domain extraction")
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error in filtered local business update: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while updating local businesses"
        )
    
    return LocalBusinessBatchUpdateResponse(
        updated_count=updated_count,
        queued_count=queued_count
    )


# The GET endpoint implementation is above, so this TODO is no longer needed.
# # TODO: Implement GET / endpoint for frontend data grid
# # @router.get("", ...)
# # async def list_local_businesses(...):
# #    ... (Add pagination, filtering, sorting)
