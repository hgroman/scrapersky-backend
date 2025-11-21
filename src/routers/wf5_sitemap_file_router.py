"""
API Router for Sitemap Files CRUD operations.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.auth.jwt_auth import get_current_user

# Core Dependencies
from ..db.session import get_db_session
from ..models.wf5_sitemap_file import (
    SitemapFile,
    SitemapFileStatusEnum,
    SitemapImportCurationStatusEnum,
    SitemapImportProcessStatusEnum,
)
from ..schemas.sitemap_file import (
    PaginatedSitemapFileResponse,
    SitemapFileBatchUpdate,  # Assuming batch status update needed
    SitemapFileBatchUpdateResponse,
    SitemapFileCreate,
    SitemapFileFilteredUpdateRequest,
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
    deep_scrape_curation_status: Optional[SitemapImportCurationStatusEnum] = Query(
        None,
        description="Filter by sitemap import curation status (New, Selected, etc.)",
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
    "/sitemap_import_curation/status",
    response_model=Dict[str, int],
    summary="Batch Update Sitemap Import Curation Status",
    description="Updates the `sitemap_import_curation_status` for multiple sitemap files and potentially queues them for processing. Compliant with Layer-3 conventions.",
)
async def update_sitemap_import_curation_status_batch(
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


@router.put(
    "/sitemap_import_curation/status/filtered",
    response_model=SitemapFileBatchUpdateResponse,
    summary="Filtered Update Sitemap Import Curation Status",
    description="Updates the `deep_scrape_curation_status` for ALL sitemap files matching filter criteria and potentially queues them for processing. Enables 'Select All' functionality.",
)
async def update_sitemap_import_curation_status_filtered(
    request: SitemapFileFilteredUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SitemapFileBatchUpdateResponse:
    """
    Update ALL sitemap files matching filter criteria with new curation status.
    
    Enables 'Select All' functionality by applying updates to filtered results
    rather than requiring explicit sitemap file ID lists.
    
    Implements same dual-status pattern:
    - Updates deep_scrape_curation_status to requested value
    - If status is 'Selected', triggers sitemap import by setting sitemap_import_status to 'Queued'
    
    Args:
        request: Filtered update request with criteria and target status
        session: Database session (injected)
        current_user: Authenticated user context (injected)
    
    Returns:
        SitemapFileBatchUpdateResponse with update and queue counts
    
    Raises:
        HTTPException: If no sitemap files found matching the provided filter criteria
    """
    user_id = current_user.get("user_id", "unknown_user")
    logger.info(
        f"User {user_id} requesting filtered sitemap curation update to status "
        f"'{request.deep_scrape_curation_status.value}' with filters: "
        f"status_filter={request.deep_scrape_curation_status_filter}, domain_id={request.domain_id}, url_contains='{request.url_contains}'"
    )
    
    # Build filter conditions (same logic as GET endpoint)
    filters = []
    
    if request.deep_scrape_curation_status_filter is not None:
        # Direct enum comparison - SQLAlchemy handles the type matching
        filters.append(SitemapFile.deep_scrape_curation_status == request.deep_scrape_curation_status_filter)
    
    if request.domain_id is not None:
        filters.append(SitemapFile.domain_id == request.domain_id)
    
    if request.url_contains:
        filters.append(SitemapFile.url.ilike(f"%{request.url_contains}%"))
    
    # Determine if sitemap import should be triggered
    trigger_sitemap_import = request.deep_scrape_curation_status == SitemapImportCurationStatusEnum.Selected
    
    updated_count = 0
    queued_count = 0
    now = datetime.utcnow()
    
    try:
        async with session.begin():
            # Get all sitemap files matching filter criteria
            stmt = select(SitemapFile)
            if filters:
                stmt = stmt.where(*filters)
            
            result = await session.execute(stmt)
            sitemap_files_to_update = result.scalars().all()
            
            if not sitemap_files_to_update:
                logger.warning("No sitemap files found matching the provided filter criteria")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No sitemap files found matching the provided filter criteria"
                )
            
            # Apply updates to all matching sitemap files
            for sitemap_file in sitemap_files_to_update:
                # Update the curation status
                sitemap_file.deep_scrape_curation_status = request.deep_scrape_curation_status  # type: ignore
                sitemap_file.updated_at = now  # type: ignore
                updated_count += 1
                logger.debug(
                    f"Updating sitemap file {sitemap_file.id} deep_scrape_curation_status to "
                    f"{request.deep_scrape_curation_status.value}"
                )
                
                # Dual-Status Update Pattern - trigger sitemap import when Selected
                if trigger_sitemap_import:
                    sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Queued  # type: ignore
                    sitemap_file.sitemap_import_error = None  # type: ignore
                    queued_count += 1
                    logger.debug(f"Queuing sitemap file {sitemap_file.id} for import processing")
            
            logger.info(f"Filtered sitemap update completed: {updated_count} files updated, {queued_count} queued for import processing")
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error in filtered sitemap file update: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during filtered sitemap file update"
        ) from e
    
    logger.info(
        f"Batch sitemap curation filtered update completed by {user_id}. "
        f"Updated: {updated_count}, Queued for import processing: {queued_count}"
    )
    
    return SitemapFileBatchUpdateResponse(
        updated_count=updated_count,
        queued_count=queued_count
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
