"""
Profile Service

This module provides services for managing user profiles.
"""

import logging
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import NotFoundError
from ..models.profile import Profile, ProfileUpdate

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for managing user profiles."""

    async def get_profiles(
        self,
        session: AsyncSession,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        raw_sql: bool = True,
        no_prepare: bool = True,
        statement_cache_size: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get a list of profiles.

        Args:
            session: Database session
            tenant_id: Tenant ID to filter by
            limit: Maximum number of profiles to return
            offset: Number of profiles to skip
            raw_sql: Use raw SQL instead of ORM
            no_prepare: Disable prepared statements
            statement_cache_size: Set statement cache size

        Returns:
            List of profile dictionaries
        """
        try:
            if raw_sql:
                # Use raw SQL for better compatibility with connection pooler
                query = text("""
                    SELECT id, name, email, role, bio, tenant_id, active, created_at, updated_at
                    FROM profile
                    WHERE tenant_id = :tenant_id
                    LIMIT :limit OFFSET :offset
                """)

                # For Supavisor compatibility, modify query execution
                if no_prepare:
                    # Apply PostgreSQL specific options to the statement
                    query = query.execution_options(postgresql_expert_mode=True)

                result = await session.execute(
                    query, {"tenant_id": tenant_id, "limit": limit, "offset": offset}
                )
                profiles = result.fetchall()
                return [
                    dict(
                        id=row.id,
                        name=row.name,
                        email=row.email,
                        role=row.role,
                        bio=row.bio,
                        tenant_id=row.tenant_id,
                        active=row.active,
                        created_at=row.created_at,
                        updated_at=row.updated_at,
                    )
                    for row in profiles
                ]
            else:
                # Use ORM if explicitly requested
                # REMOVED tenant filtering as per architectural mandate
                # JWT authentication happens ONLY at API gateway endpoints
                # Database operations should NEVER handle JWT or tenant authentication
                stmt = select(Profile).limit(limit).offset(offset)
                result = await session.execute(stmt)
                profiles = result.scalars().all()
                return [
                    dict(
                        id=profile.id,
                        name=profile.name,
                        email=profile.email,
                        role=profile.role,
                        bio=profile.bio,
                        tenant_id=profile.tenant_id,
                        active=profile.active,
                        created_at=profile.created_at,
                        updated_at=profile.updated_at,
                    )
                    for profile in profiles
                ]
        except Exception as e:
            logger.error(f"Error fetching profiles: {str(e)}")
            raise

    async def get_profile(
        self, session: AsyncSession, profile_id: UUID, tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get a single profile by ID.

        Args:
            session: Database session
            profile_id: Profile UUID
            tenant_id: Tenant ID for validation

        Returns:
            Profile dictionary

        Raises:
            NotFoundError: If profile not found
        """
        # REMOVED tenant filtering as per architectural mandate
        # JWT authentication happens ONLY at API gateway endpoints
        # Database operations should NEVER handle JWT or tenant authentication
        stmt = select(Profile).where(Profile.id == profile_id)
        result = await session.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            raise NotFoundError(f"Profile {profile_id} not found")

        return dict(
            id=profile.id,
            name=profile.name,
            email=profile.email,
            role=profile.role,
            bio=profile.bio,
            tenant_id=profile.tenant_id,
            active=profile.active,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def update_profile(
        self,
        session: AsyncSession,
        profile_id: UUID,
        tenant_id: str,
        profile: ProfileUpdate,
    ) -> Dict[str, Any]:
        """
        Update an existing profile.

        Args:
            session: Database session
            profile_id: Profile UUID
            tenant_id: Tenant ID for validation
            profile: Updated profile data

        Returns:
            Updated profile dictionary

        Raises:
            NotFoundError: If profile not found
        """
        # REMOVED tenant filtering as per architectural mandate
        # JWT authentication happens ONLY at API gateway endpoints
        # Database operations should NEVER handle JWT or tenant authentication
        stmt = select(Profile).where(Profile.id == profile_id)
        result = await session.execute(stmt)
        db_profile = result.scalar_one_or_none()

        if not db_profile:
            raise NotFoundError(f"Profile {profile_id} not found")

        update_data = profile.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_profile, key, value)

        await session.commit()

        return dict(
            id=db_profile.id,
            name=db_profile.name,
            email=db_profile.email,
            role=db_profile.role,
            bio=db_profile.bio,
            tenant_id=db_profile.tenant_id,
            active=db_profile.active,
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at,
        )
