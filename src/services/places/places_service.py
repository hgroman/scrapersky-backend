"""
Places Service

This module provides database operations for places data.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.place import Place
from ...models.place_search import PlaceSearch

logger = logging.getLogger(__name__)


class PlacesService:
    """
    Service for handling Place database operations.

    This service provides methods for interacting with the places_staging
    and place_searches tables using SQLAlchemy ORM.
    """

    @staticmethod
    async def get_by_id(
        session: AsyncSession, place_id: str
    ) -> Optional[Place]:
        """
        Get a place by its place_id.

        Args:
            session: SQLAlchemy session
            place_id: The Google Place ID

        Returns:
            Place object or None if not found
        """
        query = select(Place).where(Place.place_id == place_id)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_places(
        session: AsyncSession,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Place], int]:
        """
        Get places with filtering options.

        Args:
            session: SQLAlchemy session
            status: Optional status filter
            limit: Maximum number of records
            offset: Offset for pagination

        Returns:
            Tuple of (places, total_count)
        """
        # REMOVED tenant filtering as per architectural mandate
        # JWT authentication happens ONLY at API gateway endpoints
        # Database operations should NEVER handle JWT or tenant authentication

        query = select(Place)

        if status:
            query = query.where(Place.status == status)

        # Get total count for pagination
        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        count_result = await session.scalar(count_query)
        total_count = 0 if count_result is None else count_result

        # Apply pagination
        query = query.order_by(Place.search_time.desc()).offset(offset).limit(limit)

        result = await session.execute(query)
        places = result.scalars().all()

        return list(places), total_count

    @staticmethod
    async def update_status(
        session: AsyncSession,
        place_id: str,
        status: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Update the status of a place.

        Args:
            session: SQLAlchemy session
            place_id: The Google Place ID
            status: New status to set
            user_id: Optional user ID for attribution

        Returns:
            True if update was successful
        """
        stmt = (
            update(Place)
            .where(Place.place_id == place_id)
            .values(status=status, updated_at=datetime.utcnow())
        )

        if user_id:
            user_uuid = (
                user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(user_id)
            )
            stmt = stmt.values(user_id=user_uuid)

        result = await session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    async def create_search(
        session: AsyncSession,
        user_id: str,
        location: str,
        business_type: str,
        params: Dict[str, Any],
    ) -> PlaceSearch:
        """
        Create a place search record.

        Args:
            session: SQLAlchemy session
            user_id: User ID
            location: Search location
            business_type: Business type
            params: Additional search parameters

        Returns:
            Created PlaceSearch object
        """
        # Convert user_id to UUID if it's a string
        user_uuid = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(user_id)

        search = PlaceSearch(
            user_id=user_uuid,
            location=location,
            business_type=business_type,
            params=params,
        )

        session.add(search)
        await session.flush()

        return search

    @staticmethod
    async def batch_update_status(
        session: AsyncSession, place_ids: List[str], status: str
    ) -> int:
        """
        Update the status of multiple places in batch.

        Args:
            session: SQLAlchemy session
            place_ids: List of Google Place IDs
            status: New status to set

        Returns:
            Number of records updated
        """
        # REMOVED tenant filtering as per architectural mandate
        # JWT authentication happens ONLY at API gateway endpoints
        # Database operations should NEVER handle JWT or tenant authentication

        stmt = (
            update(Place)
            .where(Place.place_id.in_(place_ids))
            .values(status=status, updated_at=datetime.utcnow())
        )

        result = await session.execute(stmt)
        return result.rowcount
