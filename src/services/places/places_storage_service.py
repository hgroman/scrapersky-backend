"""
Places Storage Service

This module provides storage operations for Place entities.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.place import Place, PlaceStatusEnum
from .places_service import PlacesService

logger = logging.getLogger(__name__)


class PlacesStorageService:
    """
    Service for storing and retrieving Place entities.

    This service handles the storage operations for places data,
    including batch operations and error handling.
    """

    @staticmethod
    async def store_places(
        session: AsyncSession,
        places: List[Dict[str, Any]],
        search_id: str,
        tenant_id: str,
        user_id: str,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Store places from Google Maps API.

        Args:
            session: SQLAlchemy session
            places: List of places to store
            search_id: Search job ID
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution

        Returns:
            Tuple of (success_count, failed_places)
        """
        if not places:
            logger.info("No places to store")
            return 0, []

        # Convert string UUIDs to UUID objects with better error handling
        tenant_uuid = None
        user_uuid = None
        search_uuid = None
        user_name = "Unknown User"

        try:
            # Try to convert tenant_id to UUID
            if tenant_id and tenant_id != "default":
                try:
                    tenant_uuid = (
                        uuid.UUID(tenant_id)
                        if isinstance(tenant_id, str)
                        else tenant_id
                    )
                except ValueError:
                    logger.warning(
                        f"Invalid UUID format for tenant_id: {tenant_id}, using default UUID"
                    )
                    tenant_uuid = uuid.UUID(
                        "550e8400-e29b-41d4-a716-446655440000"
                    )  # Default UUID
            else:
                # Use default tenant ID if not provided or is "default"
                tenant_uuid = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
                logger.info("Using default tenant UUID")

            # Try to convert user_id to UUID
            if user_id:
                try:
                    user_uuid = (
                        uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                    )
                except ValueError:
                    logger.warning(
                        f"Invalid UUID format for user_id: {user_id}, using default UUID"
                    )
                    user_uuid = uuid.UUID(
                        "00000000-0000-0000-0000-000000000000"
                    )  # Default UUID
            else:
                user_uuid = uuid.UUID(
                    "00000000-0000-0000-0000-000000000000"
                )  # Default UUID
                logger.info("Using default user UUID")

            # Try to convert search_id to UUID
            if search_id:
                try:
                    search_uuid = (
                        uuid.UUID(search_id)
                        if isinstance(search_id, str)
                        else search_id
                    )
                except ValueError:
                    logger.warning(
                        f"Invalid UUID format for search_id: {search_id}, generating new UUID"
                    )
                    search_uuid = uuid.uuid4()  # Generate a new UUID as fallback
            else:
                search_uuid = (
                    uuid.uuid4()
                )  # Generate a new UUID if search_id is not provided
                logger.info(f"Generated new search_uuid: {search_uuid}")

            # Log the UUID conversions for debugging
            logger.info(
                f"Using tenant_uuid: {tenant_uuid}, user_uuid: {user_uuid}, search_uuid: {search_uuid}"
            )

        except Exception as e:
            logger.error(f"Error processing UUID conversions: {e}")
            return 0, places

        success_count = 0
        failed_places = []

        # First, get all existing place IDs to avoid duplicates
        try:
            place_ids = [
                place.get("place_id") for place in places if place.get("place_id")
            ]
            query = select(Place.place_id).where(Place.place_id.in_(place_ids))
            result = await session.execute(query)
            existing_place_ids = {row[0] for row in result.fetchall()}
            logger.info(
                f"Found {len(existing_place_ids)} existing places that will be updated"
            )
        except Exception as e:
            logger.error(f"Error checking existing places: {e}")
            existing_place_ids = set()

        for place_data in places:
            try:
                place_id = place_data.get("place_id")
                if not place_id:
                    logger.warning(f"Skipping place without place_id: {place_data}")
                    failed_places.append(place_data)
                    continue

                # Check if place already exists
                if place_id in existing_place_ids:
                    # Get existing place
                    existing_place = await PlacesService.get_by_id(
                        session, place_id
                    )

                    if existing_place:
                        # Update existing place
                        existing_place.name = place_data.get(
                            "name", existing_place.name
                        )
                        existing_place.formatted_address = place_data.get(
                            "formatted_address", existing_place.formatted_address
                        )
                        existing_place.business_type = place_data.get(
                            "business_type", existing_place.business_type
                        )
                        existing_place.latitude = place_data.get(
                            "latitude", existing_place.latitude
                        )
                        existing_place.longitude = place_data.get(
                            "longitude", existing_place.longitude
                        )
                        existing_place.vicinity = place_data.get(
                            "vicinity", existing_place.vicinity
                        )
                        existing_place.rating = place_data.get(
                            "rating", existing_place.rating
                        )
                        existing_place.user_ratings_total = place_data.get(
                            "user_ratings_total", existing_place.user_ratings_total
                        )
                        existing_place.price_level = place_data.get(
                            "price_level", existing_place.price_level
                        )
                        # For SQLAlchemy columns, we need to use setattr for Column values
                        existing_place.search_job_id = search_uuid
                        existing_place.search_query = place_data.get(
                            "search_query", existing_place.search_query
                        )
                        existing_place.search_location = place_data.get(
                            "search_location", existing_place.search_location
                        )
                        # For datetime fields, set with setattr for SQLAlchemy Columns
                        existing_place.search_time = datetime.utcnow()
                        existing_place.raw_data = place_data.get(
                            "raw_data", existing_place.raw_data
                        )
                        existing_place.updated_at = datetime.utcnow()

                        # No need to add to session since it's already tracked
                        success_count += 1
                    else:
                        logger.warning(
                            f"Place ID {place_id} was found in database but get_by_id failed"
                        )
                        failed_places.append(place_data)
                else:
                    # Create new place
                    try:
                        # Prepare fields with safe UUID conversion
                        new_place_data = {
                            "place_id": place_id,
                            "name": place_data.get("name", ""),
                            "formatted_address": place_data.get("formatted_address"),
                            "business_type": place_data.get("business_type"),
                            "latitude": place_data.get("latitude"),
                            "longitude": place_data.get("longitude"),
                            "vicinity": place_data.get("vicinity"),
                            "rating": place_data.get("rating"),
                            "user_ratings_total": place_data.get("user_ratings_total"),
                            "price_level": place_data.get("price_level"),
                            "status": PlaceStatusEnum.New,
                            "search_query": place_data.get("search_query"),
                            "search_location": place_data.get("search_location"),
                            "raw_data": place_data.get("raw_data"),
                        }

                        # Convert raw_data from string to dict for JSONB column
                        raw_data = new_place_data.get("raw_data")
                        if isinstance(raw_data, str):
                            try:
                                import json

                                new_place_data["raw_data"] = json.loads(raw_data)
                            except json.JSONDecodeError:
                                logger.warning(
                                    f"Could not parse raw_data as JSON for place {place_id}"
                                )

                        # Ensure tenant_id is a valid UUID
                        new_place_data["tenant_id"] = tenant_uuid

                        # IMPORTANT: Always provide default UUIDs for created_by and user_id
                        # The database has a NOT NULL constraint on these columns
                        new_place_data["created_by"] = user_uuid
                        new_place_data["user_id"] = user_uuid

                        # Set search_job_id if valid
                        new_place_data["search_job_id"] = search_uuid

                        # Add user's name if available
                        if "user_name" in place_data:
                            new_place_data["user_name"] = place_data.get("user_name")
                        else:
                            new_place_data["user_name"] = "Unknown User"

                        # Now create the place with valid data
                        new_place = Place(**new_place_data)
                        session.add(new_place)

                        # Increment success counter
                        success_count += 1

                    except Exception as e:
                        logger.error(f"Error creating new place {place_id}: {e}")
                        failed_places.append(place_data)
                        continue

            except Exception as e:
                logger.error(f"Error storing place {place_data.get('place_id')}: {e}")
                failed_places.append(place_data)

        # Flush session to ensure all places are stored
        try:
            await session.flush()
        except Exception as e:
            logger.error(f"Error flushing session: {e}")
            # Don't rethrow the exception - we want to return what we have

        logger.info(
            f"Successfully stored {success_count} places, {len(failed_places)} failed"
        )
        return success_count, failed_places

    @staticmethod
    async def get_places_for_job(
        session: AsyncSession,
        job_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Place], int]:
        """
        Get places associated with a specific job.

        Args:
            session: SQLAlchemy session
            job_id: Job ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of records
            offset: Offset for pagination

        Returns:
            Tuple of (places, total_count)
        """
        try:
            job_uuid = uuid.UUID(job_id) if isinstance(job_id, str) else job_id
            tenant_uuid = (
                uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
            )
        except ValueError as e:
            logger.error(f"Invalid UUID format: {e}")
            return [], 0

        # Build query
        query = (
            select(Place)
            .where(
                and_(Place.search_job_id == job_uuid, Place.tenant_id == tenant_uuid)
            )
            .limit(limit)
            .offset(offset)
        )

        # Get total count
        count_query = select(func.count()).select_from(
            select(Place)
            .where(
                and_(Place.search_job_id == job_uuid, Place.tenant_id == tenant_uuid)
            )
            .subquery()
        )
        count_result = await session.scalar(count_query)
        total_count = 0 if count_result is None else count_result

        result = await session.execute(query)
        places = result.scalars().all()

        return list(places), total_count

    @staticmethod
    async def get_places_from_staging(
        session: AsyncSession,
        tenant_id: str,
        job_id: Optional[str] = None,
        status: Optional[str] = None,
        business_type: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Place], int]:
        """
        Get places from the staging table with filtering capabilities.

        Args:
            session: SQLAlchemy session
            tenant_id: Tenant ID for isolation
            job_id: Optional job ID to filter by
            status: Optional status to filter by (New, Selected, Maybe, Not a Fit, Archived)
            business_type: Optional business type to filter by
            location: Optional location to filter by
            limit: Maximum number of records to return
            offset: Offset for pagination

        Returns:
            Tuple of (places, total_count)
        """
        try:
            # Convert tenant_id to UUID
            tenant_uuid = (
                uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
            )

            # Build base query for places
            query = select(Place).where(Place.tenant_id == tenant_uuid)

            # Apply optional filters
            if job_id:
                try:
                    job_uuid = uuid.UUID(job_id) if isinstance(job_id, str) else job_id
                    query = query.where(Place.search_job_id == job_uuid)
                except ValueError:
                    logger.warning(f"Invalid UUID format for job_id: {job_id}")

            if status:
                # Filter by status - using the enum type from database
                query = query.where(Place.status == status)

            if business_type:
                # Add ILIKE for case-insensitive partial matching
                query = query.where(Place.business_type.ilike(f"%{business_type}%"))

            if location:
                # Search in both search_location and formatted_address fields
                location_filter = or_(
                    Place.search_location.ilike(f"%{location}%"),
                    Place.formatted_address.ilike(f"%{location}%"),
                )
                query = query.where(location_filter)

            # Add order by most recent search_time
            query = query.order_by(Place.search_time.desc())

            # Get total count for pagination
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await session.scalar(count_query)
            total_count = 0 if count_result is None else count_result

            # Apply pagination
            paginated_query = query.limit(limit).offset(offset)

            # Execute query
            result = await session.execute(paginated_query)
            places = result.scalars().all()

            return list(places), total_count

        except Exception as e:
            logger.error(f"Error retrieving places from staging: {str(e)}")
            # Return empty list on error
            return [], 0

    @staticmethod
    async def update_places_status(
        session: AsyncSession,
        place_id: str,
        status: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Update the status of a place in the staging table.

        Args:
            session: SQLAlchemy session
            place_id: Google Place ID
            status: New status (New, Selected, Maybe, Not a Fit, Archived)
            tenant_id: Optional tenant ID for isolation
            user_id: Optional user ID for attribution

        Returns:
            Boolean indicating success
        """
        try:
            # Validate status value
            valid_statuses = ["New", "Selected", "Maybe", "Not a Fit", "Archived"]
            if status not in valid_statuses:
                logger.warning(
                    f"Invalid status value: {status}. Must be one of {valid_statuses}"
                )
                return False

            # First check if the place exists
            query = select(Place).where(Place.place_id == place_id)

            # Add tenant filter if provided
            if tenant_id:
                try:
                    tenant_uuid = (
                        uuid.UUID(tenant_id)
                        if isinstance(tenant_id, str)
                        else tenant_id
                    )
                    query = query.where(Place.tenant_id == tenant_uuid)
                except ValueError:
                    logger.warning(f"Invalid UUID format for tenant_id: {tenant_id}")

            result = await session.execute(query)
            place = result.scalar_one_or_none()

            if not place:
                logger.warning(f"Place with place_id {place_id} not found")
                return False

            # Update the place directly - Use capitalized enum member NAME
            # Handle potential spaces in incoming status string for 'Not a Fit'
            status_name = status.replace(" ", "_")
            place.status = PlaceStatusEnum[status_name]
            place.updated_at = datetime.utcnow()

            # Add user_id for attribution if provided
            if user_id:
                try:
                    user_uuid = (
                        uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                    )
                    place.user_id = user_uuid
                    place.updated_by = str(user_uuid)
                except ValueError:
                    logger.warning(f"Invalid UUID format for user_id: {user_id}")

            # The session will automatically track these changes
            await session.flush()

            return True

        except Exception as e:
            logger.error(f"Error updating place status: {str(e)}")
            return False

    @staticmethod
    async def batch_update_places(
        session: AsyncSession,
        place_ids: List[str],
        status: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> int:
        """
        Update the status of multiple places in batch.

        Args:
            session: SQLAlchemy session
            place_ids: List of Google Place IDs
            status: New status (New, Selected, Maybe, Not a Fit, Archived)
            tenant_id: Optional tenant ID for isolation
            user_id: Optional user ID for attribution

        Returns:
            Number of records updated
        """
        try:
            # Validate input
            if not place_ids:
                logger.warning("No place_ids provided for batch update")
                return 0

            # Validate status value
            valid_statuses = ["New", "Selected", "Maybe", "Not a Fit", "Archived"]
            if status not in valid_statuses:
                logger.warning(
                    f"Invalid status value: {status}. Must be one of {valid_statuses}"
                )
                return 0

            # For batch updates, we'll query for all matching places and update them individually
            # This ensures proper enum handling
            query = select(Place).where(Place.place_id.in_(place_ids))

            # Add tenant filter if provided
            if tenant_id:
                try:
                    tenant_uuid = (
                        uuid.UUID(tenant_id)
                        if isinstance(tenant_id, str)
                        else tenant_id
                    )
                    query = query.where(Place.tenant_id == tenant_uuid)
                except ValueError:
                    logger.warning(f"Invalid UUID format for tenant_id: {tenant_id}")

            result = await session.execute(query)
            places = result.scalars().all()

            # Convert status string to enum member - Use capitalized enum member NAME
            # Handle potential spaces in incoming status string for 'Not a Fit'
            status_name = status.replace(" ", "_")
            status_enum_member = PlaceStatusEnum[status_name]

            # Process user ID if provided
            user_uuid = None
            user_id_str = None
            if user_id:
                try:
                    user_uuid = (
                        uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                    )
                    user_id_str = str(user_uuid)
                except ValueError:
                    logger.warning(f"Invalid UUID format for user_id: {user_id}")

            # Update each place
            count = 0
            for place in places:
                place.status = status_enum_member
                place.updated_at = datetime.utcnow()
                if user_uuid:
                    place.user_id = user_uuid
                    place.updated_by = user_id_str
                count += 1

            # Flush changes
            await session.flush()

            return count

        except Exception as e:
            logger.error(f"Error in batch update places: {str(e)}")
            return 0
