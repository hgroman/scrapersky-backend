"""
API Router for interacting with Places Staging data.

Provides endpoints for listing staged places based on discovery jobs
and updating their status for selection (e.g., for deep scanning).
"""

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

# from ..services.place_staging_service import PlaceStagingService # Ideal, but might not exist yet
# --- Add Auth dependency if needed ---
# from ..auth.dependencies import get_current_active_user
from ..auth.jwt_auth import get_current_user  # Corrected import for auth dependency
from ..db.session import get_db_session  # Assuming this provides the session

# Import models and services
from ..models.api_models import (
    PlaceStagingListResponse,
    PlaceStagingRecord,
    PlaceStagingStatusEnum,
)

# We need a service or direct model access to interact with Place model
from ..models.place import (  # Import the Place model AND the new DeepScanStatusEnum
    GcpApiDeepScanStatusEnum,
    Place,
    PlaceStatusEnum,
)

# from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Places Staging"],
    # dependencies=[Depends(get_current_active_user)], # Uncomment if auth is needed
    responses={404: {"description": "Not found"}},
)

# Placeholder for a potential service layer
# place_staging_service = PlaceStagingService()

# --- API Models defined within this router file --- #


# Add a new response model for paginated results
class PaginatedPlaceStagingResponse(BaseModel):
    items: List[PlaceStagingRecord]
    total: int
    page: int
    size: int
    pages: int


# Model for the direct queueing endpoint
class QueueDeepScanRequest(BaseModel):
    # Prioritize place_ids as the primary input
    place_ids: List[str] = Field(
        ..., description="List of Google Place IDs to queue for deep scan."
    )
    # Keep staging_ids as optional secondary identifier if needed, or remove if place_ids are sufficient
    # staging_ids: List[int] = Field(default_factory=list, description="List of internal integer IDs from places_staging to queue.")


# Model for the unified batch/single status update endpoint
class PlaceBatchStatusUpdateRequest(BaseModel):
    place_ids: List[str] = Field(
        ..., min_length=1, description="List of one or more Google Place IDs to update."
    )
    status: PlaceStagingStatusEnum = Field(
        ..., description="The new main status to set."
    )
    error_message: Optional[str] = Field(
        None, description="Optional error message to set when status is Error."
    )


# --- API Endpoints --- #


# NEW Endpoint: General listing for the data grid
@router.get(
    "/places/staging",
    response_model=PaginatedPlaceStagingResponse,
    summary="List All Staged Places (Paginated)",
    description="Retrieves a paginated list of all places currently in the staging area, optionally filtered by status.",
)
async def list_all_staged_places(
    status_filter: Optional[PlaceStagingStatusEnum] = Query(
        None, alias="status", description="Filter places by their main status"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=200, description="Page size"),
    session: AsyncSession = Depends(get_db_session),
    # Add current_user dependency if tenant filtering or auth is needed later
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PaginatedPlaceStagingResponse:
    """List all places in the staging table (Place model) with pagination and optional status filtering."""
    # Get Tenant ID (Use default if not provided in token)
    tenant_id_str = current_user.get(
        "tenant_id", "550e8400-e29b-41d4-a716-446655440000"
    )  # Use default directly
    try:
        tenant_uuid = UUID(tenant_id_str)
    except ValueError:
        logger.error(
            f"Invalid tenant ID format in token or default: {tenant_id_str}. Using default UUID."
        )
        tenant_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")

    logger.info(
        f"Listing all staged places for tenant {tenant_uuid} using RAW SQL, status: {status_filter}, page: {page}, size: {size}"
    )
    offset = (page - 1) * size

    try:
        # --- Use Raw SQL for Data Fetching --- #

        # Still need count query (using ORM is fine for count)
        count_query = (
            select(func.count())
            .select_from(Place)
            .where(Place.tenant_id == tenant_uuid)
        )
        # Apply status filter to count if provided
        if status_filter:
            try:
                db_status_filter_member = next(
                    member
                    for member in PlaceStatusEnum
                    if member.value == status_filter.value
                )
                count_query = count_query.where(Place.status == db_status_filter_member)
            except StopIteration:
                logger.warning(
                    f"[Count Query] Could not map status filter '{status_filter.value}'. Ignoring."
                )

        total_result = await session.execute(count_query)
        total = total_result.scalar_one_or_none() or 0
        total_pages = math.ceil(total / size) if size > 0 else 0

        # Construct Raw SQL Query
        params = {"tenant_id": tenant_uuid, "limit": size, "offset": offset}
        raw_sql = """
            SELECT
                place_id, name, formatted_address, business_type,
                search_location, latitude, longitude, rating,
                user_ratings_total, price_level, status,
                updated_at, processed_time, search_job_id, tenant_id
            FROM places_staging
            WHERE tenant_id = :tenant_id
        """
        # Add status filter to raw SQL if applicable
        if status_filter and db_status_filter_member:
            raw_sql += " AND status = :status"
            params["status"] = (
                db_status_filter_member.value
            )  # Use the actual DB value for the parameter

        # Add Limit and Offset
        raw_sql += " ORDER BY updated_at DESC LIMIT :limit OFFSET :offset"  # Keep ordering here for consistency if possible

        # Execute Raw SQL
        logger.debug(f"Executing Raw SQL: {raw_sql} with params: {params}")
        result = await session.execute(text(raw_sql), params)
        # Fetch rows as mappings (dict-like objects)
        db_rows = result.mappings().all()
        logger.debug(f"Raw SQL fetched {len(db_rows)} rows.")

        # --- Convert Raw SQL Rows to Pydantic Models --- #
        response_items = []
        for row in db_rows:
            # Check for missing critical required fields from raw SQL result
            place_id = row.get("place_id")
            tenant_id = row.get("tenant_id")
            updated_at = row.get("updated_at")  # Should always exist based on schema
            search_job_id = row.get(
                "search_job_id"
            )  # Should always exist based on schema

            if not place_id or not tenant_id or not updated_at or not search_job_id:
                logger.error(
                    f"Skipping row due to missing critical data: place_id={place_id}, tenant_id={tenant_id}, updated_at={updated_at}, search_job_id={search_job_id}"
                )
                continue

            item_dict = {
                "place_id": place_id,
                "business_name": row.get("name"),
                "address": row.get("formatted_address"),
                "category": row.get("business_type"),
                "search_location": row.get("search_location"),
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "rating": row.get("rating"),
                "reviews_count": row.get("user_ratings_total"),
                "price_level": row.get("price_level"),
                "status": row.get("status"),  # Raw value from DB
                "updated_at": updated_at,
                "last_deep_scanned_at": row.get("processed_time"),
                "search_job_id": search_job_id,
                "tenant_id": tenant_id,
            }
            try:
                # Validate dict against Pydantic model (should work now if fields match)
                validated_item = PlaceStagingRecord(**item_dict)
                response_items.append(validated_item)
            except Exception as validation_error:
                logger.error(
                    f"Pydantic validation failed for raw SQL row {place_id}: {validation_error}",
                    exc_info=True,
                )
                continue  # Skip invalid rows

        return PaginatedPlaceStagingResponse(
            items=response_items, total=total, page=page, size=size, pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error listing all staged places (Raw SQL): {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list staged places",
        )


# Add the new unified batch/single status update endpoint (Placed BEFORE parameterized route)
@router.put("/places/staging/status", status_code=status.HTTP_200_OK)
async def update_places_status_batch(
    request_body: PlaceBatchStatusUpdateRequest = Body(...),
    trigger_deep_scan: bool = Query(
        False,
        description="If true, also queue places for deep scan when updating to a non-error status.",
    ),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update the status of one or more places by place_id list."""
    place_ids_to_update = request_body.place_ids
    new_main_status = request_body.status
    error_message = request_body.error_message
    user_id = current_user.get("user_id")

    logger.info(
        f"User {user_id} initiating batch status update (ORM fetch-update) for {len(place_ids_to_update)} place_ids to status: {new_main_status}"
    )

    updated_count = 0
    actually_queued_count = 0

    try:
        # Map the incoming API status enum member to the DB enum member
        # Compare by NAME, not VALUE, as value casing might differ (API='Selected', DB='selected')
        logger.debug(
            f"Attempting to map API status: Name={new_main_status.name}, Value={new_main_status.value}"
        )
        logger.debug(f"Database enum members: {[m.name for m in PlaceStatusEnum]}")
        target_db_status_member = next(
            (
                member
                for member in PlaceStatusEnum
                if member.name.lower() == new_main_status.name.lower()
            ),
            None,
        )
        logger.debug(
            f"Mapped DB status member: {target_db_status_member.name if target_db_status_member else 'None'}"
        )

        if target_db_status_member is None:
            logger.error(
                f"API status '{new_main_status.name}' ({new_main_status.value}) has no matching member name in DB PlaceStatusEnum."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status mapping for '{new_main_status.value}'",
            )

        # Determine if deep scan should be triggered based on the *target database status*
        trigger_deep_scan = target_db_status_member == PlaceStatusEnum.Selected
        logger.debug(
            f"Proceeding with DB status: {target_db_status_member.name}, Trigger deep scan? {trigger_deep_scan}"
        )
        if trigger_deep_scan:
            logger.info(
                f"API status '{new_main_status.name}' (mapping to DB '{target_db_status_member.name}') will trigger deep scan queueing."
            )

        eligible_deep_scan_statuses = [None, GcpApiDeepScanStatusEnum.Error]

        # Execute within a transaction
        logger.debug(
            f"About to fetch places with IDs: {place_ids_to_update} and apply status {target_db_status_member.name}"
        )
        logger.info("Attempting to begin database transaction for batch status update.")
        async with session.begin():
            # 1. Fetch the relevant Place objects
            stmt_select = select(Place).where(Place.place_id.in_(place_ids_to_update))
            result = await session.execute(stmt_select)
            places_to_process = result.scalars().all()

            if not places_to_process:
                logger.warning(
                    f"No places found for the provided place_ids: {place_ids_to_update}"
                )
                return {
                    "message": "No matching places found for the provided IDs.",
                    "updated_count": 0,
                    "queued_count": 0,  # Ensure queued_count is returned even if no places found
                }

            updated_count = 0
            now = datetime.utcnow()

            # 2. Loop and update attributes in Python
            for place in places_to_process:
                # Avoid unnecessary updates if status is already the target
                if place.status == target_db_status_member:  # type: ignore
                    continue

                # Update status and timestamp
                place.status = target_db_status_member  # type: ignore
                place.updated_at = now  # type: ignore
                updated_count += 1

                # Handle deep scan queueing if requested
                if (
                    trigger_deep_scan
                    and place.deep_scan_status in eligible_deep_scan_statuses
                ):  # type: ignore
                    place.deep_scan_status = GcpApiDeepScanStatusEnum.Queued  # type: ignore
                    place.deep_scan_error = None  # type: ignore
                    place.updated_at = now  # type: ignore
                    actually_queued_count += 1

            # 3. Commit the transaction
            logger.info(f"ORM updates prepared for {updated_count} places.")
            if trigger_deep_scan:
                logger.info(
                    f"Attempted to queue {actually_queued_count} places for deep scan."
                )
        logger.info(
            f"Database transaction for batch status update committed successfully. Updated: {updated_count}, Queued: {actually_queued_count}"
        )

    except Exception as e:
        # Rollback happens automatically with session.begin() context manager
        logger.error(
            f"Database error during batch status update (ORM fetch-update): {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during batch status update.",
        )

    return {
        "message": f"Status update request processed. Matched and updated: {updated_count} places. Queued for deep scan: {actually_queued_count}.",
        "updated_count": updated_count,
        "queued_count": actually_queued_count,
    }


# Keep the secondary direct queueing endpoint (Placed BEFORE parameterized route)
@router.put("/places/staging/queue-deep-scan", status_code=status.HTTP_202_ACCEPTED)
async def queue_places_for_deep_scan(
    request_body: QueueDeepScanRequest = Body(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """(Secondary Endpoint) Queue selected places (identified by Google Place IDs) for deep scanning.

    Updates ONLY the 'deep_scan_status' to 'queued' and clears 'deep_scan_error'.
    Does NOT modify the main 'status' field. Requires authentication.
    Used for programmatic/admin queueing.
    """
    user_id = current_user.get("user_id")
    logger.info(
        f"User {user_id} requested to DIRECTLY queue places for deep scan via place_ids."
    )
    place_ids_to_queue = request_body.place_ids
    if not place_ids_to_queue:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request must contain a non-empty list of 'place_ids'.",
        )
    updated_count = 0
    try:
        # Ensure we only queue places whose current deep_scan_status indicates they haven't run successfully
        eligible_statuses = [None, GcpApiDeepScanStatusEnum.Error]  # Changed from Error
        stmt_update = (
            update(Place)
            .where(
                Place.place_id.in_(place_ids_to_queue),
                Place.deep_scan_status.in_(
                    eligible_statuses
                ),  # Check current status before queuing
            )
            .values(
                deep_scan_status=GcpApiDeepScanStatusEnum.Queued,  # Ensuring uppercase Queued is used
                deep_scan_error=None,  # Clear any previous error when queuing
                updated_at=datetime.utcnow(),
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(stmt_update)
        await session.commit()
        updated_count = result.rowcount
        logger.info(
            f"DIRECTLY Queued {updated_count} places for deep scan (Target place_ids: {place_ids_to_queue})."
        )
        if updated_count < len(place_ids_to_queue):
            logger.warning(
                f"Could not DIRECTLY queue all requested places. Requested: {len(place_ids_to_queue)}, Queued: {updated_count}."
            )
    except Exception as e:
        logger.error(
            f"Database error while DIRECTLY queueing places: {e}", exc_info=True
        )
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during direct queueing.",
        )
    return {
        "message": f"Request accepted. {updated_count} places directly queued for deep scan.",
        "updated_count": updated_count,
    }


# Original endpoint that expects a discovery_job_id (Placed LAST)
@router.get(
    "/places/staging/{discovery_job_id}",
    response_model=PlaceStagingListResponse,
    summary="List Staged Places for a Discovery Job",
    description="Retrieves a list of places found by a specific discovery scan job, allowing filtering by status and pagination.",
)
async def list_staged_places(
    discovery_job_id: UUID,
    status_filter: Optional[PlaceStagingStatusEnum] = Query(
        None,
        alias="status",
        description="Filter places by their current staging status",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    # current_user: User = Depends(get_current_active_user), # Uncomment if auth/tenant check needed
    session: AsyncSession = Depends(get_db_session),
) -> PlaceStagingListResponse:
    """List places in the staging table for a given discovery job ID with pagination."""
    logger.info(
        f"Listing staged places for discovery job: {discovery_job_id}, status: {status_filter}, page: {page}, size: {size}"
    )
    offset = (page - 1) * size

    try:
        # Base query
        query = select(Place).where(Place.search_job_id == discovery_job_id)
        count_query = (
            select(func.count())
            .select_from(Place)
            .where(Place.search_job_id == discovery_job_id)
        )

        # Apply status filter if provided
        if status_filter:
            query = query.where(Place.status == status_filter.value)
            count_query = count_query.where(Place.status == status_filter.value)

        # Get total count
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()

        # Apply ordering and pagination
        query = query.order_by(Place.created_at.asc()).offset(offset).limit(size)

        # Execute query
        result = await session.execute(query)
        db_items = result.scalars().all()

        # Convert db models to Pydantic models
        response_items = [PlaceStagingRecord.from_orm(item) for item in db_items]

        return PlaceStagingListResponse(items=response_items, total=total)

    except Exception as e:
        logger.error(
            f"Error listing staged places for job {discovery_job_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list staged places",
        )


# --- Debug Endpoint Removed --- #
# The temporary debug endpoint previously located here has been removed.
