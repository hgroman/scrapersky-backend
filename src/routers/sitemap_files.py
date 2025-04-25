"""
API Router for Sitemap Files CRUD operations.
"""

import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_auth import get_current_user

# Core Dependencies
from ..db.session import get_db_session
from ..models.sitemap import (
    SitemapDeepCurationStatusEnum,
)
from ..schemas.sitemap_file import (
    PaginatedSitemapFileResponse,
    SitemapFileBatchUpdate,  # Assuming batch status update needed
    SitemapFileCreate,
    SitemapFileRead,
    SitemapFileUpdate,
)

# Service and Schemas
from ..services.sitemap_files_service import SitemapFilesService

logger = logging.getLogger(__name__)

# Define Router
router = APIRouter(
    prefix="/api/v3/sitemap-files",  # Full prefix defined here
    tags=["Sitemap Files"],
    responses={404: {"description": "Not found"}},
)

# Instantiate Service
# (Typically done at module level if stateless, or via dependency if stateful)
sitemap_files_service = SitemapFilesService()

# --- CRUD Endpoints --- #

# Order matters: Specific paths should generally come before parameterized paths


@router.get(
    "/",
    response_model=PaginatedSitemapFileResponse,
    summary="List Sitemap Files",
    description="Retrieves a paginated list of sitemap files, with optional filtering.",
)
async def list_sitemap_files(
    # Updated query parameters as per Spec 23.5 / Implementation 23.6
    domain_id: Optional[uuid.UUID] = Query(None, description="Filter by domain UUID"),
    deep_scrape_curation_status: Optional[SitemapDeepCurationStatusEnum] = Query(
        None, description="Filter by deep scrape curation status (New, Selected, etc.)"
    ),
    url_contains: Optional[str] = Query(
        None,
        description="Filter by text contained in the sitemap URL (case-insensitive)",
        alias="url_contains",  # Explicit alias
    ),
    sitemap_type: Optional[str] = Query(
        None, description="Filter by sitemap type (e.g., Standard, Index)"
    ),
    discovery_method: Optional[str] = Query(
        None, description="Filter by discovery method (e.g., robots_txt, common_path)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        15, ge=1, le=200, description="Items per page"
    ),  # Default size 15 as per spec
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Endpoint to list SitemapFile records with pagination and filtering."""
    try:
        # Call the updated service method with the correct parameters
        paginated_response = await sitemap_files_service.get_all(
            session=session,
            page=page,
            size=size,
            domain_id=domain_id,
            deep_scrape_curation_status=deep_scrape_curation_status,
            url_contains=url_contains,
            sitemap_type=sitemap_type,
            discovery_method=discovery_method,
        )
        return paginated_response
    except Exception as e:
        logger.error(f"Error listing sitemap files: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sitemap files.",
        )


@router.put(
    "/status",
    response_model=Dict[
        str, int
    ],  # Response model matches service: {"updated_count": N, "queued_count": M}
    summary="Batch Update Sitemap File Curation Status",
    description="Updates the deep_scrape_curation_status for multiple sitemap files and potentially queues them.",
)
async def update_sitemap_files_status_batch(
    update_request: SitemapFileBatchUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, int]:
    """Endpoint to batch update the curation status of SitemapFile records."""
    user_id = current_user.get("user_id")
    if not user_id:
        logger.error(
            "User ID not found in JWT token for batch update status operation."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not identify user."
        )

    logger.info(f"User {user_id} attempting batch curation status update.")

    try:
        user_uuid = uuid.UUID(user_id)  # Convert user_id to UUID
    except ValueError:
        logger.error(f"Invalid user ID format for batch update operation: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user identifier."
        )

    if not update_request.sitemap_file_ids:
        # Return early if the list is empty, consistent with service
        logger.warning(
            f"User {user_id} called batch curation update with empty ID list."
        )
        return {"updated_count": 0, "queued_count": 0}

    try:
        # Call the new service method
        result_counts = await sitemap_files_service.update_curation_status_batch(
            session=session,
            sitemap_file_ids=update_request.sitemap_file_ids,
            new_curation_status=update_request.deep_scrape_curation_status,
            updated_by=user_uuid,
        )
        logger.info(
            f"Batch curation status update by user {user_id} completed. Results: {result_counts}"
        )
        return result_counts
    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly
        raise http_exc
    except Exception as e:
        logger.error(
            f"Error during batch curation status update by user {user_id}: {e}",
            exc_info=True,
        )
        # Service layer exceptions will cause rollback via session.begin()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing batch status update.",
        )


@router.post(
    "/",
    response_model=SitemapFileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Sitemap File",
    description="Creates a new sitemap file record.",
)
async def create_sitemap_file(
    sitemap_data: SitemapFileCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Endpoint to create a new SitemapFile record."""
    user_id = current_user.get("user_id")
    if not user_id:
        # This should technically not happen if Depends(get_current_user) works,
        # but good practice to handle missing user_id.
        logger.error("User ID not found in JWT token for create operation.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not identify user."
        )

    logger.info(f"User {user_id} attempting to create sitemap file.")

    try:
        # Convert Pydantic model to dict for service layer
        sitemap_dict = sitemap_data.model_dump()

        created_sitemap_file = await sitemap_files_service.create(
            session=session,
            sitemap_data=sitemap_dict,
            created_by=uuid.UUID(user_id),  # Ensure user_id is UUID
        )
        # Service returns the ORM model instance added to the session
        # FastAPI will automatically serialize it based on the response_model
        # No need for await session.commit() here, managed by middleware/dependency
        logger.info(
            f"Sitemap file created successfully by user {user_id} (pending commit)."
        )
        return created_sitemap_file
    except ValueError as ve:
        # Handle potential UUID conversion error if user_id isn't a valid UUID string
        logger.error(
            f"Invalid user ID format for create operation: {user_id} - {ve}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user identifier."
        )
    except Exception as e:
        logger.error(
            f"Error during sitemap file creation by user {user_id}: {e}", exc_info=True
        )
        # Re-raise a generic server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating sitemap file.",
        )


@router.get(
    "/{sitemap_file_id}",
    response_model=SitemapFileRead,
    summary="Get Sitemap File by ID",
    description="Retrieves a specific sitemap file record by its UUID.",
)
async def get_sitemap_file(
    sitemap_file_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),  # Added for consistency, remove if not needed
):
    """Endpoint to get a SitemapFile record by ID."""
    # Implementation using service.get_by_id will go here
    sitemap_file = await sitemap_files_service.get_by_id(session, sitemap_file_id)
    if not sitemap_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sitemap file not found"
        )
    return sitemap_file


@router.put(
    "/{sitemap_file_id}",
    response_model=SitemapFileRead,
    summary="Update Sitemap File",
    description="Updates an existing sitemap file record by its UUID.",
)
async def update_sitemap_file(
    sitemap_file_id: uuid.UUID,
    update_data: SitemapFileUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Endpoint to update a SitemapFile record."""
    user_id = current_user.get("user_id")
    if not user_id:
        logger.error("User ID not found in JWT token for update operation.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not identify user."
        )

    logger.info(
        f"User {user_id} attempting to update sitemap file ID {sitemap_file_id}."
    )
    logger.debug(f"Entering router update_sitemap_file for ID: {sitemap_file_id}")

    try:
        # Convert Pydantic model to dict, excluding unset fields to allow partial updates
        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided.",
            )

        updated_sitemap_file = await sitemap_files_service.update(
            session=session,
            sitemap_file_id=sitemap_file_id,
            update_data=update_dict,
            updated_by=uuid.UUID(user_id),  # Ensure user_id is UUID
        )

        if updated_sitemap_file is None:
            logger.warning(
                f"Sitemap file {sitemap_file_id} not found for update by user {user_id}."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sitemap file not found"
            )

        logger.info(
            f"Sitemap file {sitemap_file_id} updated successfully by user {user_id} (pending commit)."
        )
        return updated_sitemap_file
    except ValueError as ve:
        # Handle potential UUID conversion error if user_id isn't a valid UUID string
        logger.error(
            f"Invalid user ID format for update operation: {user_id} - {ve}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user identifier."
        )
    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly (like the 400 Bad Request from empty data)
        raise http_exc
    except Exception as e:
        logger.error(
            f"Error during sitemap file update for ID {sitemap_file_id} by user {user_id}: {e}",
            exc_info=True,
        )
        # Re-raise a generic server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating sitemap file.",
        )


@router.delete(
    "/{sitemap_file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Sitemap File",
    description="Deletes a sitemap file record by its UUID.",
)
async def delete_sitemap_file(
    sitemap_file_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Endpoint to delete a SitemapFile record."""
    user_id = current_user.get("user_id")  # For logging
    # Although user_id isn't strictly needed for the delete operation itself by the service,
    # it's good practice for logging/auditing who initiated the action.
    if not user_id:
        logger.error("User ID not found in JWT token for delete operation.")
        # Potentially raise 401, but operation might proceed depending on policy
        # For now, log the attempt without user context if ID is missing.
        pass  # Allow anonymous delete attempt? Or raise HTTPException? For now, just log.

    logger.info(
        f"User {user_id or 'Unknown'} attempting to delete sitemap file ID {sitemap_file_id}."
    )

    try:
        deleted = await sitemap_files_service.delete(session, sitemap_file_id)
        if not deleted:
            logger.warning(
                f"Sitemap file {sitemap_file_id} not found for deletion by user {user_id or 'Unknown'}."
            )
            # Service returns False if rowcount is 0
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sitemap file not found"
            )

        logger.info(
            f"Sitemap file {sitemap_file_id} deleted successfully by user {user_id or 'Unknown'} (pending commit)."
        )
        # Return No Content on success (FastAPI handles this based on decorator and None return)
        return None
    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly (like the 404)
        raise http_exc
    except Exception as e:
        logger.error(
            f"Error during sitemap file deletion for ID {sitemap_file_id} by user {user_id or 'Unknown'}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting sitemap file.",
        )
