"""
Places Search Service

This module provides services for interacting with the Google Places API.
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

# Removed custom error service import in favor of FastAPI's built-in error handling

logger = logging.getLogger(__name__)


class PlacesSearchService:
    """
    Service for searching Google Places API.

    This service provides methods for searching the Google Places API
    and handling the results.
    """

    @staticmethod
    async def search_places(
        location: str, business_type: str, radius_km: int = 10, max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search Google Places API for businesses.

        Args:
            location: Location to search (e.g., "New York, NY")
            business_type: Type of business to search (e.g., "dentist")
            radius_km: Search radius in kilometers
            max_results: Maximum number of results to return

        Returns:
            List of place results from Google Places API

        Raises:
            ValueError: If API key is not set or API request fails
        """
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            # Log more detailed diagnostic information
            env_keys = [k for k in os.environ.keys()]
            google_related_keys = [k for k in env_keys if "GOOGLE" in k.upper()]

            logger.error(
                "❌ [API KEY] GOOGLE_MAPS_API_KEY environment variable not set"
            )
            logger.error(
                f"❌ [API KEY] Google-related environment variables: {google_related_keys}"
            )
            logger.error(f"❌ [API KEY] Total environment variables: {len(env_keys)}")

            # Check if API key might be in settings
            from ...config.settings import settings

            if (
                hasattr(settings, "google_maps_api_key")
                and settings.google_maps_api_key
            ):
                logger.info(
                    "✅ [API KEY] Found API key in settings, using that instead"
                )
                api_key = settings.google_maps_api_key
            else:
                logger.error("❌ [API KEY] No API key found in settings either")
                raise ValueError(
                    "GOOGLE_MAPS_API_KEY environment variable not set - Google Places API search will fail"
                )

        # Convert km to meters for the API
        radius_meters = radius_km * 1000

        # Format the query for Google Places API Text Search
        query = f"{business_type} in {location}"

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {"query": query, "radius": radius_meters, "key": api_key}

        all_results = []

        try:
            async with aiohttp.ClientSession() as session:
                # First page
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_msg = f"Google Places API request failed with status {response.status}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)

                    data = await response.json()
                    if data.get("status") != "OK":
                        error_message = data.get("error_message", "Unknown error")
                        logger.error(f"Google Places API error: {error_message}")
                        raise ValueError(f"Google Places API error: {error_message}")

                    all_results.extend(data.get("results", []))

                    # Handle pagination with next_page_token if it exists
                    next_page_token = data.get("next_page_token")

                    # Google requires a delay before using next_page_token
                    while next_page_token and len(all_results) < max_results:
                        await asyncio.sleep(2)  # Wait for token to be valid

                        next_params = {"pagetoken": next_page_token, "key": api_key}

                        async with session.get(
                            url, params=next_params
                        ) as next_response:
                            if next_response.status != 200:
                                logger.warning(
                                    f"Failed to fetch next page with status {next_response.status}"
                                )
                                break

                            next_data = await next_response.json()
                            if next_data.get("status") != "OK":
                                logger.warning(
                                    f"Failed to fetch next page with error: {next_data.get('error_message', 'Unknown error')}"
                                )
                                break

                            all_results.extend(next_data.get("results", []))
                            next_page_token = next_data.get("next_page_token")

                            # Stop if we've reached the maximum results
                            if len(all_results) >= max_results:
                                break

                            # If we have next_page_token, wait again before using it
                            if next_page_token:
                                await asyncio.sleep(2)

            # Limit results if needed
            if len(all_results) > max_results:
                all_results = all_results[:max_results]

            # Standardize result format
            standardized_results = []
            for place in all_results:
                standardized_results.append(
                    PlacesSearchService.standardize_place(
                        place, location, business_type
                    )
                )

            logger.info(
                f"Found {len(standardized_results)} places matching '{business_type}' in '{location}'"
            )
            return standardized_results

        except Exception as e:
            # SECURITY: Sanitize exception to prevent API key leakage in logs
            from ...utils.log_sanitizer import sanitize_exception_message, get_safe_exception_info
            
            sanitized_error = sanitize_exception_message(e)
            exception_info = get_safe_exception_info(e)
            
            logger.error(f"Error searching Google Places: {sanitized_error}")
            logger.error(f"Exception details: {exception_info}")
            
            raise ValueError(f"Error searching Google Places: {sanitized_error}")

    @staticmethod
    def standardize_place(
        place: Dict[str, Any], search_location: str, search_query: str
    ) -> Dict[str, Any]:
        """
        Standardize a Google Places API result.

        Args:
            place: Place result from Google Places API
            search_location: Original search location
            search_query: Original search query (business type)

        Returns:
            Standardized place dictionary
        """
        # Extract location data
        geometry = place.get("geometry", {})
        location = geometry.get("location", {})

        # Build standardized record
        return {
            "place_id": place.get("place_id", ""),
            "name": place.get("name", ""),
            "formatted_address": place.get("formatted_address", ""),
            "business_type": search_query,
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
            "vicinity": place.get("vicinity", ""),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "price_level": place.get("price_level"),
            "search_location": search_location,
            "search_query": search_query,
            "raw_data": json.dumps(place),
        }

    @staticmethod
    async def search_and_store(
        session: Any,
        job_id: str,
        business_type: str,
        location: str,
        radius_km: int = 10,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for places and store them in the database.

        Args:
            session: Database session
            job_id: Unique job identifier
            business_type: Type of business to search
            location: Location to search
            radius_km: Search radius in kilometers
            api_key: Google Maps API key (optional)
            user_id: User ID for attribution

        Returns:
            Dictionary with search results and status
        """
        from sqlalchemy import update

        from ...models.wf1_place_search import PlaceSearch
        from .places_storage_service import PlacesStorageService

        try:
            # Update the search record to mark it as processing
            stmt = (
                update(PlaceSearch)
                .where(PlaceSearch.id == uuid.UUID(job_id))
                .values(status="processing", updated_at=datetime.utcnow())
            )
            await session.execute(stmt)
            # Note: We don't commit here as the router owns the transaction

            # Perform the search
            places = await PlacesSearchService.search_places(
                location=location,
                business_type=business_type,
                radius_km=radius_km,
                max_results=20,
            )

            # Get storage service to store places
            storage_service = PlacesStorageService()

            # Store the places in the database
            tenant_id = "550e8400-e29b-41d4-a716-446655440000"  # Default tenant ID
            success_count, failed_places = await storage_service.store_places(
                session=session,
                places=places,
                search_id=job_id,
                tenant_id=tenant_id,
                user_id=user_id or "00000000-0000-0000-0000-000000000000",
            )

            # Update the status in the database
            stmt = (
                update(PlaceSearch)
                .where(PlaceSearch.id == uuid.UUID(job_id))
                .values(status="complete", updated_at=datetime.utcnow())
            )
            await session.execute(stmt)
            # Note: We don't commit here as the router owns the transaction

            return {"success": True, "places_count": success_count, "job_id": job_id}

        except Exception as e:
            logger.error(f"Error in search and store: {str(e)}")

            # Update the status to failed in the database
            try:
                stmt = (
                    update(PlaceSearch)
                    .where(PlaceSearch.id == uuid.UUID(job_id))
                    .values(status="failed", updated_at=datetime.utcnow())
                )
                await session.execute(stmt)
                # Note: We don't commit here as the router owns the transaction
            except Exception as update_err:
                logger.error(f"Error updating search status: {str(update_err)}")

            return {"success": False, "error": str(e), "job_id": job_id}

    @staticmethod
    async def get_search_by_id(
        session: Any, job_id: str, tenant_id: str
    ) -> Optional[Any]:
        """
        Get a place search record by its ID.
        """
        from sqlalchemy import select

        from ...models.wf1_place_search import PlaceSearch

        try:
            stmt = select(PlaceSearch).where(PlaceSearch.id == job_id)
            result = await session.execute(stmt)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error getting search by ID: {str(e)}")
            return None


async def process_places_search_background(
    session: AsyncSession,
    job_id: str,
    business_type: str,
    location: str,
    radius_km: int = 10,
    api_key: Optional[str] = None,
    user_id: Optional[str] = None,
):
    """
    Process a places search in the background.

    Args:
        job_id (str): The ID of the job.
        business_type (str): The type of business to search for.
        location (str): The location to search in.
        radius_km (int, optional): The radius in kilometers to search. Defaults to 10.
        api_key (Optional[str], optional): The Google Maps API key. Defaults to None.
        user_id (Optional[str], optional): The ID of the user performing the search. Defaults to None.
    """
    print(f"DEBUGGING: Starting background task for job_id {job_id}")

    import uuid

    from sqlalchemy import select

    from ...models.wf1_place_staging import Place
    from ...models.job import Job as SearchJob
    from ...services.job_service import job_service

    # Create job_uuid from job_id
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        print(f"DEBUGGING ERROR: Invalid job_id format: {job_id}")
        return

    # Create a dedicated session for background task
    async with get_session() as session:
        # Add these options to disable prepared statements for Supavisor compatibility
        session.bind.engine.update_execution_options(
            no_parameters=True,  # Disable prepared statements
            statement_cache_size=0,  # Disable statement caching
        )
        print("DEBUGGING: Created session with Supavisor compatibility options")

        try:
            # Update job status to processing
            async with session.begin():
                await job_service.update_status(
                    session=session, job_id=job_uuid, status="processing", progress=0.1
                )

            # Perform the search
            print(
                f"DEBUGGING: Performing search for {business_type} in {location} with radius {radius_km}km"
            )

            search_results = []
            try:
                # Execute Google Maps API search
                places_service = PlacesSearchService()
                search_results = await places_service.search_places(
                    location=location,
                    business_type=business_type,
                    radius_km=radius_km,
                    max_results=50,  # Reasonable limit for testing
                )

                print(f"DEBUGGING: Found {len(search_results)} places")

                # Store results
                async with session.begin():
                    # Find job by id to get tenant_id
                    job_query = select(SearchJob).where(SearchJob.job_id == job_uuid)
                    job_result = await session.execute(
                        job_query,
                        execution_options={
                            "no_parameters": True,
                            "statement_cache_size": 0,
                        },
                    )
                    job = job_result.scalars().first()

                    if not job:
                        raise ValueError(f"Job {job_id} not found")

                    # Get tenant_id from job
                    tenant_id = job.tenant_id

                    # Store each place
                    for place in search_results:
                        # Check if place already exists
                        place_id = place.get("place_id")
                        if not place_id:
                            continue

                        existing_query = select(Place).where(
                            Place.place_id == place_id, Place.tenant_id == tenant_id
                        )
                        existing_result = await session.execute(
                            existing_query,
                            execution_options={
                                "no_parameters": True,
                                "statement_cache_size": 0,
                            },
                        )
                        existing_place = existing_result.scalars().first()

                        if existing_place:
                            # Update existing place
                            for key, value in place.items():
                                if hasattr(existing_place, key) and key != "id":
                                    setattr(existing_place, key, value)
                            session.add(existing_place)
                        else:
                            # Create new place
                            new_place = Place(
                                id=uuid.uuid4(),
                                tenant_id=tenant_id,
                                job_id=job_uuid,
                                place_id=place_id,
                                name=place.get("name", ""),
                                address=place.get("address", ""),
                                phone=place.get("phone", ""),
                                website=place.get("website", ""),
                                location_lat=place.get("location_lat"),
                                location_lng=place.get("location_lng"),
                                rating=place.get("rating"),
                                place_types=place.get("place_types", []),
                                business_status=place.get("business_status", ""),
                                raw_data=place,
                            )
                            session.add(new_place)

                    await session.flush()

                # Update job status to complete
                async with session.begin():
                    await job_service.update_status(
                        session=session,
                        job_id=job_uuid,
                        status="completed",
                        progress=1.0,
                        result_data={
                            "places_found": len(search_results),
                            "location": location,
                            "business_type": business_type,
                            "radius_km": radius_km,
                        },
                    )

                print(f"DEBUGGING: Successfully completed search job {job_id}")

            except Exception as search_error:
                print(f"DEBUGGING ERROR in search: {str(search_error)}")
                # Update job status to failed
                async with session.begin():
                    await job_service.update_status(
                        session=session,
                        job_id=job_uuid,
                        status="failed",
                        error=str(search_error),
                        progress=0,
                    )

        except Exception as e:
            print(f"DEBUGGING CRITICAL ERROR: {str(e)}")
            # Try to update status one last time
            try:
                async with session.begin():
                    await job_service.update_status(
                        session=session,
                        job_id=job_uuid,
                        status="failed",
                        error=f"Critical error: {str(e)}",
                        progress=0,
                    )
            except Exception as final_error:
                print(f"DEBUGGING: Failed to update job status: {str(final_error)}")
