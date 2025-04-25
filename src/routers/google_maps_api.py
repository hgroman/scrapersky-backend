"""
Google Maps API Router

This module provides API endpoints for interacting with Google Maps API.
It uses standard FastAPI routing with explicit permission checks.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt_auth import DEFAULT_TENANT_ID, get_current_user

# RBAC imports removed
# from ..utils.permissions import (
#     require_permission,
#     require_feature_enabled,
#     require_role_level
# )
from ..config.settings import settings
from ..models import PlaceSearch
from ..services.places.places_search_service import PlacesSearchService
from ..services.places.places_service import PlacesService
from ..services.places.places_storage_service import PlacesStorageService
from ..session.async_session import get_session, get_session_dependency

# from ..constants.rbac import ROLE_HIERARCHY

# Configure logger
logger = logging.getLogger(__name__)


# Create API models
class PlacesSearchRequest(BaseModel):
    business_type: str
    location: str
    radius_km: int = 10
    tenant_id: Optional[str] = None


class PlacesStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Create router
router = APIRouter(prefix="/api/v3/localminer-discoveryscan", tags=["google-maps-api"])

# Initialize services
places_service = PlacesService()
places_storage_service = PlacesStorageService()
places_search_service = PlacesSearchService()

# Development mode detection
dev_mode = os.getenv("SCRAPER_SKY_DEV_MODE", "").lower() == "true"

# Get API key from environment
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")


@router.get("/debug/info")
async def get_debug_info(current_user: Dict = Depends(get_current_user)):
    """
    Get debug information about the Google Maps API configuration.
    """
    # This endpoint is for debugging only
    if not dev_mode and settings.environment != "development":
        raise HTTPException(
            status_code=403,
            detail="Debug endpoints are only available in development mode",
        )

    # Check if API key is configured properly
    api_key_status = "CONFIGURED" if GOOGLE_MAPS_API_KEY else "MISSING"

    # In production, don't expose actual configuration values
    return {
        "status": "ok",
        "api_key_status": api_key_status,
        "development_mode": dev_mode,
        "environment": settings.environment,
        "default_values": {
            "tenant_id": DEFAULT_TENANT_ID,
            "user_id": "dev-admin-id" if dev_mode else None,
            "max_results": 100,
        },
    }


@router.post("/search/places", response_model=Dict)
async def search_places(
    request: PlacesSearchRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Search for places using Google Maps API.

    Uses the Google Places API to search for business locations based on type and location.
    Results are stored in the database for later retrieval.

    Args:
        request: Search parameters
        session: Database session
        current_user: Authenticated user information

    Returns:
        Dictionary with job ID and status URL
    """
    # Extract user information
    user_info = current_user
    logger.info(
        f"🔍 User details: user_id={user_info.get('user_id')}, tenant_id={request.tenant_id}"
    )

    # Generate job ID
    job_id = str(uuid.uuid4())

    try:
        # Router owns the transaction boundary
        async with session.begin():
            # Create search record - store radius_km in params JSON field
            search_record = PlaceSearch(
                id=job_id,
                tenant_id=request.tenant_id,
                business_type=request.business_type,
                location=request.location,
                params={"radius_km": request.radius_km},
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                user_id=user_info.get("user_id", "unknown"),
            )

            # Store search record
            session.add(search_record)

            # Set up background task arguments
            task_args = {
                "job_id": job_id,
                "business_type": request.business_type,
                "location": request.location,
                "radius_km": request.radius_km,
                "user_info": user_info,
                "tenant_id": request.tenant_id,
            }

        # Start background processing task outside transaction
        async def process_places_search_background(args: Dict[str, Any]):
            """Background task to process places search."""
            try:
                # Create a new session for background task using the ONE AND ONLY ONE acceptable method
                async with get_session() as bg_session:
                    # Extract task arguments
                    job_id = args["job_id"]
                    business_type = args["business_type"]
                    location = args["location"]
                    radius_km = args["radius_km"]
                    user_info = args["user_info"]

                    # As per architectural mandate: JWT authentication happens ONLY at API gateway endpoints,
                    # while database operations NEVER handle JWT or tenant authentication
                    # We'll still log the tenant_id for tracking purposes
                    logger.info(f"🔍 Processing job {job_id} from API gateway")

                    # Log user info for audit purposes only
                    user_id = user_info.get("user_id", "dev-admin-id")
                    logger.info(f"🔍 Request initiated by user_id {user_id}")

                    # Perform search via the search service inside a transaction
                    async with bg_session.begin():
                        # As per architectural mandate: database operations NEVER handle JWT or tenant authentication
                        result = await places_search_service.search_and_store(
                            session=bg_session,
                            job_id=job_id,
                            business_type=business_type,
                            location=location,
                            radius_km=radius_km,
                            api_key=GOOGLE_MAPS_API_KEY or None,
                            user_id=user_id,
                        )

                        logger.info(
                            f"🔍 Completed places search job {job_id}: {result}"
                        )
            except Exception as e:
                logger.error(f"Error in background places search task: {str(e)}")
                # Create a new session for error handling
                try:
                    async with get_session() as error_session:
                        async with error_session.begin():
                            # Update status to failed in database
                            from sqlalchemy import update

                            from ..models.place_search import PlaceSearch

                            stmt = (
                                update(PlaceSearch)
                                .where(PlaceSearch.id == uuid.UUID(job_id))
                                .values(status="failed", updated_at=datetime.utcnow())
                            )
                            await error_session.execute(stmt)
                except Exception as db_error:
                    logger.error(
                        f"Failed to update error status in database: {str(db_error)}"
                    )

        # Run background task concurrently
        await process_places_search_background(task_args)

        # Return job ID and status URL
        return {
            "job_id": job_id,
            "status_url": f"/api/v3/localminer-discoveryscan/search/status/{job_id}",
            "status": "processing",
        }
    except Exception as e:
        logger.error(f"Error initiating places search: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error initiating search: {str(e)}"
        )


@router.get("/search/status/{job_id}", response_model=PlacesStatusResponse)
async def get_search_status(
    job_id: str,
    request: Request,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
) -> PlacesStatusResponse:
    """
    Get the status of a places search job.

    Args:
        job_id: Job ID to check
        request: FastAPI request object
        session: Database session
        current_user: Authenticated user information

    Returns:
        Job status response
    """
    # Validate input
    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID is required")

    # Get tenant ID with proper fallbacks
    tenant_id = current_user.get("tenant_id", "")
    if not tenant_id:
        tenant_id = DEFAULT_TENANT_ID  # Ensure tenant_id is never None

    logger.info(f"Using JWT validation only (RBAC removed) for tenant: {tenant_id}")

    try:
        # Check database for status (primary source of truth)
        async with session.begin():
            search_record = await places_search_service.get_search_by_id(
                session=session, job_id=job_id, tenant_id=tenant_id
            )

            if not search_record:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

            # Calculate progress based on status
            progress = 0.0
            if search_record.status == "processing":
                progress = 0.5
            elif search_record.status == "complete":
                progress = 1.0

            # Use database status information
            return PlacesStatusResponse(
                job_id=job_id,
                status=search_record.status or "unknown",
                progress=progress,
                created_at=search_record.created_at,
                updated_at=search_record.updated_at,
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving search status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving status: {str(e)}"
        )


@router.get("/places/staging", response_model=List[Dict])
async def get_staging_places(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
    job_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[Dict]:
    """
    Get places from the staging area.

    Args:
        session: Database session
        current_user: Authenticated user information
        job_id: Optional job ID filter
        tenant_id: Optional tenant ID filter
        limit: Maximum number of places to return
        offset: Number of places to skip

    Returns:
        List of place records
    """
    # RBAC permission check removed
    # require_permission(current_user, "places:view")

    # Validate tenant ID
    tenant_id = tenant_id or current_user.get("tenant_id", "")

    # Ensure tenant_id is never None
    if not tenant_id:
        logger.warning("No tenant ID found in request or user token, using default")
        tenant_id = DEFAULT_TENANT_ID

    # RBAC feature checks removed
    # await require_feature_enabled(
    #     tenant_id=tenant_id,
    #     feature_name="google_maps_api",
    #     session=session,
    #     user_permissions=current_user.get("permissions", [])
    # )

    logger.info(
        f"Using JWT validation only (RBAC removed) for staging places, tenant: {tenant_id}"
    )

    try:
        # Get places from staging
        async with session.begin():
            places, total_count = await places_storage_service.get_places_for_job(
                session=session,
                tenant_id=tenant_id or DEFAULT_TENANT_ID,
                job_id=job_id or "",  # Ensure job_id is never None
                limit=limit,
                offset=offset,
            )

            # Convert to serializable dictionaries
            result = []
            for place in places:
                place_dict = {
                    "id": str(place.id) if place.id is not None else None,
                    "name": place.name,
                    "address": place.address,
                    "website": place.website,
                    "phone": place.phone,
                    "latitude": place.latitude,
                    "longitude": place.longitude,
                    "place_id": place.place_id,
                    "tenant_id": str(place.tenant_id)
                    if place.tenant_id is not None
                    else None,
                    "business_type": place.business_type,
                    "source": place.source,
                    "created_at": place.created_at.isoformat()
                    if place.created_at is not None
                    else None,
                    "updated_at": place.updated_at.isoformat()
                    if place.updated_at is not None
                    else None,
                    "job_id": place.job_id,
                }
                result.append(place_dict)

            return result
    except Exception as e:
        logger.error(f"Error retrieving staging places: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving places: {str(e)}"
        )


@router.post("/places/staging/status", response_model=Dict)
async def update_place_status(
    place_ids: List[str],
    status: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
    tenant_id: Optional[str] = None,
) -> Dict:
    """
    Update the status of places in the staging area.

    Args:
        place_ids: List of place IDs to update
        status: New status value
        session: Database session
        current_user: Authenticated user information
        tenant_id: Optional tenant ID

    Returns:
        Result with count of updated places
    """
    # Validate input
    if not place_ids:
        raise HTTPException(status_code=400, detail="Place IDs are required")

    if status not in ["approved", "rejected", "pending"]:
        raise HTTPException(
            status_code=400, detail="Status must be one of: approved, rejected, pending"
        )

    # Validate tenant ID
    tenant_id = tenant_id or current_user.get("tenant_id", "")

    # Ensure tenant_id is never None
    if not tenant_id:
        logger.warning("No tenant ID found in request or user token, using default")
        tenant_id = DEFAULT_TENANT_ID

    # RBAC feature checks removed
    # await require_feature_enabled(
    #     tenant_id=tenant_id,
    #     feature_name="google_maps_api",
    #     session=session,
    #     user_permissions=current_user.get("permissions", [])
    # )

    logger.info(
        f"Using JWT validation only (RBAC removed) for update status, tenant: {tenant_id}"
    )

    try:
        # Update place status
        async with session.begin():
            # Use PlacesService for status updates instead of missing PlacesStorageService method
            count = 0
            for place_id in place_ids:
                success = await PlacesService.update_status(
                    session=session,
                    place_id=place_id,
                    status=status,
                    tenant_id=tenant_id,
                    user_id=current_user.get("user_id", "system"),
                )
                if success:
                    count += 1

            return {"success": True, "updated_count": count, "status": status}
    except Exception as e:
        logger.error(f"Error updating place status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")


@router.post("/places/staging/batch", response_model=Dict)
async def batch_update_places(
    places: List[Dict],
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
    tenant_id: Optional[str] = None,
) -> Dict:
    """
    Batch update places in the staging area.

    Args:
        places: List of place records to update
        session: Database session
        current_user: Authenticated user information
        tenant_id: Optional tenant ID

    Returns:
        Result with count of updated places
    """
    # Validate input
    if not places:
        raise HTTPException(status_code=400, detail="Places are required")

    # Validate tenant ID
    tenant_id = tenant_id or current_user.get("tenant_id", "")

    # Ensure tenant_id is never None
    if not tenant_id:
        logger.warning("No tenant ID found in request or user token, using default")
        tenant_id = DEFAULT_TENANT_ID

    # RBAC feature checks removed
    # await require_feature_enabled(
    #     tenant_id=tenant_id,
    #     feature_name="google_maps_api",
    #     session=session,
    #     user_permissions=current_user.get("permissions", [])
    # )

    logger.info(
        f"Using JWT validation only (RBAC removed) for batch update, tenant: {tenant_id}"
    )

    try:
        # Convert dict records to Place model instances
        place_ids = []
        for place_dict in places:
            # We need to ensure each place has an ID
            if not place_dict.get("id"):
                raise HTTPException(
                    status_code=400, detail="Each place must have an ID"
                )

            # Collect place IDs for batch update
            place_ids.append(place_dict.get("id"))

        # Update the places using PlacesService
        async with session.begin():
            # Use batch_update_status
            updated_count = await PlacesService.batch_update_status(
                session=session,
                place_ids=place_ids,
                status="updated",  # Default status
                tenant_id=tenant_id,
            )

            return {"success": True, "updated_count": updated_count}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch update places: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating places: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the Google Maps API service."""
    config_status = {
        "api_key_configured": bool(GOOGLE_MAPS_API_KEY),
        "environment": settings.environment,
        "default_values": {"tenant_id": DEFAULT_TENANT_ID, "search_radius_km": 10},
    }

    return {"status": "healthy", "config": config_status}


@router.get("/results/{job_id}", response_model=Dict)
async def get_job_results(
    job_id: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> Dict:
    """
    Get places discovered for a specific job ID.

    This endpoint retrieves all places found during a discovery scan for a given job.

    Args:
        job_id: The ID of the search job
        session: Database session
        current_user: Authenticated user information
        limit: Maximum number of results to return
        offset: Pagination offset

    Returns:
        Dictionary with places data, total count, and job information
    """
    # Validate tenant ID with proper fallbacks
    tenant_id = current_user.get("tenant_id", "")
    if not tenant_id:
        tenant_id = DEFAULT_TENANT_ID  # Ensure tenant_id is never None

    logger.info(f"Retrieving job results for job_id={job_id}, tenant_id={tenant_id}")

    try:
        # Get search job details first to include in response
        from sqlalchemy import select

        from ..models.place_search import PlaceSearch

        # Get job details
        stmt = select(PlaceSearch).where(PlaceSearch.id == uuid.UUID(job_id))
        result = await session.execute(stmt)
        job = result.scalars().first()

        if not job:
            logger.warning(f"Job {job_id} not found")
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        # Use the get_places_for_job method from the storage service
        places_list, total_count = await places_storage_service.get_places_for_job(
            session=session,
            job_id=job_id,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
        )

        # Convert to serializable dictionaries
        places = []
        for place in places_list:
            # Create base dictionary with required fields
            place_dict = {
                "id": str(place.id) if place.id is not None else None,
                "name": place.name,
                "place_id": place.place_id,
                "business_type": place.business_type,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "status": getattr(place, "status", "new"),
            }

            # Add optional fields if they exist
            if (
                hasattr(place, "formatted_address")
                and place.formatted_address is not None
            ):
                place_dict["formatted_address"] = place.formatted_address

            if hasattr(place, "vicinity") and place.vicinity is not None:
                place_dict["vicinity"] = place.vicinity

            if hasattr(place, "rating") and place.rating is not None:
                place_dict["rating"] = place.rating

            if (
                hasattr(place, "user_ratings_total")
                and place.user_ratings_total is not None
            ):
                place_dict["user_ratings_total"] = place.user_ratings_total

            # Add timestamps
            if hasattr(place, "search_time") and place.search_time is not None:
                place_dict["search_time"] = place.search_time.isoformat()

            # Add reference to job
            if place.search_job_id is not None:
                place_dict["search_job_id"] = str(place.search_job_id)

            places.append(place_dict)

        # Return formatted response
        return {
            "places": places,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "job_info": {
                "job_id": str(job.id),
                "business_type": job.business_type,
                "location": job.location,
                "status": job.status,
                "created_at": job.created_at.isoformat()
                if job.created_at is not None
                else None,
                "completed_at": job.updated_at.isoformat()
                if job.updated_at is not None
                else None,
            },
            "filters": {},
        }
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid job ID format: {e}")
    except Exception as e:
        logger.error(f"Error retrieving job results: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving results: {str(e)}"
        )


@router.get("/search/history", response_model=List[Dict])
async def get_search_history(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> List[Dict]:
    """
    Get search history for the tenant.

    This endpoint retrieves the history of search jobs for a tenant,
    which can be used to avoid duplicate searches and view past results.

    Args:
        session: Database session
        current_user: Authenticated user information
        limit: Maximum number of records to return
        offset: Pagination offset
        status: Optional filter by status
        tenant_id: Optional tenant ID override

    Returns:
        List of search job records
    """
    # Validate tenant ID with proper fallbacks
    tenant_id = tenant_id or current_user.get("tenant_id", "")
    if not tenant_id:
        tenant_id = DEFAULT_TENANT_ID  # Ensure tenant_id is never None

    logger.info(f"Retrieving search history for tenant_id={tenant_id}")

    try:
        from sqlalchemy import desc, select

        from ..models.place_search import PlaceSearch

        # Build base query
        query = (
            select(PlaceSearch)
            .where(PlaceSearch.tenant_id == uuid.UUID(tenant_id))
            .order_by(desc(PlaceSearch.created_at))
        )

        # Add status filter if provided
        if status:
            query = query.where(PlaceSearch.status == status)

        # Add pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        result = await session.execute(query)
        searches = result.scalars().all()

        # Convert to serializable dictionaries
        search_history = []
        for search in searches:
            # Create search dictionary with essential fields
            search_dict = {
                "id": str(search.id),
                "business_type": search.business_type,
                "location": search.location,
                "status": search.status,
                "created_at": search.created_at.isoformat()
                if search.created_at is not None
                else None,
                "updated_at": search.updated_at.isoformat()
                if search.updated_at is not None
                else None,
            }

            # Add user ID if available
            if search.user_id is not None:
                search_dict["user_id"] = search.user_id

            # Add parameters if available
            if search.params is not None:
                search_dict["params"] = search.params

            search_history.append(search_dict)

        return search_history
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid tenant ID format: {e}")
    except Exception as e:
        logger.error(f"Error retrieving search history: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving search history: {str(e)}"
        )
