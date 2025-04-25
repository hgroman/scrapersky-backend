"""
Profile Router

This module provides API endpoints for managing user profiles.
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt_auth import get_current_user
from ..core.response import standard_response
from ..models.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from ..models.tenant import DEFAULT_TENANT_ID
from ..services.profile_service import ProfileService
from ..session.async_session import get_session_dependency
from ..utils.db_helpers import get_db_params

# Configure logging
logger = logging.getLogger(__name__)

# Initialize services
profile_service = ProfileService()

# Create router
router = APIRouter(
    prefix="/api/v3/profiles",
    tags=["profiles"]
)

@router.get("", response_model=dict)
async def get_profiles(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user),
    db_params: Dict[str, Any] = Depends(get_db_params),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get a list of profiles.

    Args:
        session: Database session
        current_user: The authenticated user
        db_params: Standardized database parameters (raw_sql, no_prepare, statement_cache_size)
        limit: Maximum number of profiles to return
        offset: Number of profiles to skip

    Returns:
        List of profiles
    """
    try:
        # Always use default tenant ID
        logger.info("Using default tenant ID for get_profiles endpoint")

        # Get profiles with proper transaction context
        async with session.begin():
            profiles = await profile_service.get_profiles(
                session=session,
                tenant_id=DEFAULT_TENANT_ID,
                limit=limit,
                offset=offset
            )

        return standard_response(profiles)
    except Exception as e:
        logger.error(f"Error getting profiles: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error getting profiles: {str(e)}"
        )

@router.get("/{profile_id}", response_model=dict)
async def get_profile(
    profile_id: UUID,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a single profile by ID.

    Args:
        profile_id: Profile UUID
        session: Database session
        current_user: The authenticated user

    Returns:
        Profile details
    """
    try:
        # Always use default tenant ID
        logger.info("Using default tenant ID for get_profile endpoint")

        # Get profile with proper transaction context
        async with session.begin():
            profile = await profile_service.get_profile(
                session=session,
                profile_id=profile_id,
                tenant_id=DEFAULT_TENANT_ID
            )

        return standard_response(profile)
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error getting profile: {str(e)}"
        )

@router.post("", response_model=dict)
async def create_profile(
    profile: ProfileCreate,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new profile.

    Args:
        profile: Profile data to create
        session: Database session
        current_user: The authenticated user

    Returns:
        Created profile details
    """
    try:
        # Always use default tenant ID
        logger.info("Using default tenant ID for create_profile endpoint")

        # Create profile with proper transaction context
        async with session.begin():
            new_profile = await profile_service.create_profile(
                session=session,
                tenant_id=DEFAULT_TENANT_ID,
                profile=profile,
                created_by=current_user.get("user_id", "unknown")
            )

        return standard_response(new_profile)
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error creating profile: {str(e)}"
        )

@router.put("/{profile_id}", response_model=dict)
async def update_profile(
    profile_id: UUID,
    profile: ProfileUpdate,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing profile.

    Args:
        profile_id: Profile UUID
        profile: Updated profile data
        session: Database session
        current_user: The authenticated user

    Returns:
        Updated profile
    """
    try:
        # Always use default tenant ID
        logger.info("Using default tenant ID for update_profile endpoint")

        # Update profile with proper transaction context
        async with session.begin():
            updated_profile = await profile_service.update_profile(
                session=session,
                profile_id=profile_id,
                tenant_id=DEFAULT_TENANT_ID,
                profile=profile
            )

        return standard_response(updated_profile)
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error updating profile: {str(e)}"
        )

@router.delete("/{profile_id}", response_model=dict)
async def delete_profile(
    profile_id: UUID,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a profile.

    Args:
        profile_id: Profile UUID to delete
        session: Database session
        current_user: The authenticated user

    Returns:
        Deletion status
    """
    try:
        # Always use default tenant ID
        logger.info("Using default tenant ID for delete_profile endpoint")

        # Delete profile with proper transaction context
        async with session.begin():
            result = await profile_service.delete_profile(
                session=session,
                profile_id=profile_id,
                tenant_id=DEFAULT_TENANT_ID
            )

        return standard_response({"deleted": result})
    except Exception as e:
        logger.error(f"Error deleting profile: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting profile: {str(e)}"
        )
