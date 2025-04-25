"""
Service layer for handling Google Maps Place Details (Deep Scan) operations.

Inherits from PlacesService and adds functionality to retrieve and store
detailed place information.
"""
import logging
import os
from typing import Any, Dict, Optional

# Import insert for PostgreSQL upsert
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session  # Use absolute path

# Import only Job model, JobStatus is a string literal
from src.models.job import Job
from src.models.local_business import LocalBusiness  # Use absolute path
from src.models.place import Place

# Import base service, session factory, and models
from .places_service import PlacesService

# Define logger early
logger = logging.getLogger(__name__)

# Import JobService (assuming it exists and provides necessary methods)
# If JobService doesn't exist or lacks methods, we might need direct DB access or create/update it.
try:
    from src.services.job_service import JobService  # Use absolute path
except ImportError:
    logger.warning("JobService not found at 'src.services.job_service'. Job status updates will be skipped.")
    JobService = None # Define as None if import fails

# Import the googlemaps library
# Import UUID for type hinting
from uuid import UUID

import googlemaps

# Import select for querying
from sqlalchemy import (  # Import update for direct status changes if needed
    select,
    update,
)

# Get API key (consider moving to a central config or dependency injection)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
# --- Add default tenant ID if needed for standalone testing, but should come from context normally ---
# Import UUID type
from uuid import UUID

# You might want a specific test tenant ID or fetch one
# For now, using a placeholder or requiring it via param
# TEST_TENANT_ID = UUID('...')
# --- End temp addition ---

class PlacesDeepService(PlacesService):
    """Service for retrieving and storing detailed place information."""

    def __init__(self):
        # Initialize base service if necessary (check PlacesService.__init__)
        super().__init__()
        logger.info("PlacesDeepService initialized.")
        if not GOOGLE_MAPS_API_KEY:
            logger.warning("GOOGLE_MAPS_API_KEY environment variable not set! Place Details API calls will fail.")
        # Initialize the googlemaps client
        # Consider making this a dependency or shared instance
        try:
            self.gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        except ValueError as e:
            logger.error(f"Failed to initialize googlemaps client: {e}. API Key might be invalid.")
            self.gmaps = None # Ensure self.gmaps exists but is None if init fails

        # Initialize JobService instance if available
        # TODO: Uncomment and ensure JobService has required methods when available/verified.
        # self.job_service = JobService() if JobService else None
        self.job_service = None # Temporarily disable JobService usage
        if not self.job_service:
             logger.warning("JobService is not initialized. Job status/progress updates will be skipped.")

    # --- Orchestration Method ---
    # OBSOLETE METHOD - REMOVED
    # async def process_places_deep_scan_job(self, job_id: UUID, tenant_id: UUID):
    # ... (entire method body removed) ...

    # --- Single Place Processing Method (from previous steps) ---
    async def process_single_deep_scan(self, place_id: str, tenant_id: str) -> Optional[LocalBusiness]:
        """Retrieves details for a single place_id and upserts into local_businesses."""
        logger.info(f"Processing single deep scan for place_id: {place_id}, tenant_id: {tenant_id}")
        # Basic input validation
        if not place_id or not tenant_id:
            logger.error("Missing place_id or tenant_id for deep scan.")
            return None

        # Validate tenant_id format
        try:
            tenant_uuid = UUID(tenant_id)
        except ValueError:
            logger.error(f"Invalid UUID format for tenant_id: {tenant_id}")
            return None

        if not self.gmaps:
             logger.error("Cannot perform deep scan: Google Maps client failed to initialize (check API key).")
             return None

        try:
            # Placeholder for API call
            # logger.debug(f"Calling Google Place Details API for {place_id}...")
            # --- Example API Call Structure (Check library docs for exact parameters/fields) ---
            # Define the fields required to populate LocalBusiness model
            # Refer to Google Places API documentation for available fields: https://developers.google.com/maps/documentation/places/web-service/details
            required_fields = [
                'place_id', 'name', 'formatted_address', 'international_phone_number',
                'website', 'rating', 'user_ratings_total', 'price_level', 'opening_hours',
                'address_component', 'business_status', 'type', 'geometry/location',
                'photo', 'review', # Requesting reviews and photos might increase cost/complexity
                'utc_offset', 'vicinity' # Corrected from 'utc_offset_minutes'
                # Add any other specific fields corresponding to LocalBusiness ARRAY/Boolean fields
                # e.g., 'serves_beer', 'wheelchair_accessible_entrance', etc.
                # Note: Some fields might require separate API calls or specific licensing.
            ]
            logger.debug(f"Requesting fields: {required_fields} for place_id: {place_id}")
            details_result = self.gmaps.place(place_id=place_id, fields=required_fields) # type: ignore
            # -------------------------------------------------------------------------------
            # api_response = {} # Remove this placeholder
            # logger.warning(f"Google API call for {place_id} not yet implemented.") # Placeholder

            # --- Handle API Response ---
            if not details_result or details_result.get('status') != 'OK':
                logger.warning(f"Received non-OK status from Google API for {place_id}: {details_result.get('status', 'N/A')}")
                # Handle specific statuses like ZERO_RESULTS if needed
                return None

            api_response = details_result.get('result')
            if not api_response:
                logger.warning(f"No 'result' key found in OK API response for {place_id}")
                return None
            logger.debug(f"Successfully received API details for {place_id}")
            # -------------------------

            # Map data
            mapped_data = self._map_details_to_model(api_response)
            if not mapped_data:
                logger.error(f"Failed to map API response for place_id: {place_id}")
                return None
            mapped_data['place_id'] = place_id # Ensure place_id is included for upsert
            mapped_data['tenant_id'] = tenant_id # <<< ADD TENANT ID TO DATA >>>
            # logger.warning(f"Mapping for {place_id} not yet implemented.") # Placeholder # Remove placeholder comment
            # mapped_data = {'place_id': place_id} # Remove this placeholder

            # Save to DB
            session = await get_session()
            if not session:
                logger.error("Failed to acquire database session.")
                return None

            try:
                async with session.begin(): # Start transaction
                    # Example using PG Upsert (more explicit)
                    # Pass the full dictionary including tenant_id
                    stmt = insert(LocalBusiness).values(**mapped_data)
                    # Define columns to update on conflict
                    # Exclude primary key ('id') and potentially 'created_at' if you don't want it updated
                    # Also exclude 'place_id' itself as it's the conflict target
                    # Ensure tenant_id is updated if needed, though usually it wouldn't change on conflict
                    update_dict = {
                        col.name: getattr(stmt.excluded, col.name)
                        for col in LocalBusiness.__table__.columns
                        if col.name not in ['id', 'place_id', 'created_at', 'tenant_id'] # Exclude tenant_id from update?
                    }
                    on_conflict_stmt = stmt.on_conflict_do_update(
                        index_elements=['place_id'], # Assumes unique constraint on place_id
                        set_=update_dict
                    ).returning(LocalBusiness)
                    result = await session.execute(on_conflict_stmt)
                    merged_business = result.scalar_one_or_none()

                # Transaction automatically committed/rolled back by session.begin()

                if merged_business:
                    logger.info(f"Successfully saved/updated deep scan details for place_id: {place_id} (ID: {merged_business.id})")
                    return merged_business
                else:
                    # This case might indicate an issue with the RETURNING clause or the upsert logic itself
                    # if no error was raised but no row was returned.
                    logger.error(f"DB operation completed but failed to return the saved/updated object for {place_id}.")
                    return None
            except Exception as db_error:
                logger.error(f"Database error during upsert for place_id {place_id} under tenant {tenant_id}: {db_error}", exc_info=True)
                # The session.begin() context manager handles rollback on exception
                return None
            finally:
                 # Ensure session is closed if get_session doesn't use a context manager internally
                 # This depends on get_session implementation; if it yields, closing might be automatic.
                 # Assuming get_session provides a session that needs closing:
                 await session.close()
            # logger.warning(f"DB save for {place_id} not yet implemented.") # Placeholder - REMOVED
            # return None # Placeholder return - REMOVED

        except googlemaps.exceptions.ApiError as api_error:
            logger.error(f"Google Maps API error for place_id {place_id}: {api_error}")
            # Consider specific handling for different statuses like ZERO_RESULTS, INVALID_REQUEST
            if api_error.status == 'NOT_FOUND':
                logger.warning(f"Place ID {place_id} not found on Google Maps.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during deep scan for place_id {place_id}: {e}", exc_info=True)
            return None

    def _map_details_to_model(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper function to map Google Place Details API response to LocalBusiness model fields.
        Handles basic mapping and type conversions. More complex fields like opening_hours,
        photos, reviews, and address_components might need further processing.
        """
        mapped_data = {}

        # --- Basic Information ---
        mapped_data['business_name'] = details.get('name')
        mapped_data['full_address'] = details.get('formatted_address')
        mapped_data['phone'] = details.get('international_phone_number') # Use 'phone' model key
        mapped_data['website_url'] = details.get('website') # Use 'website_url' model key
        mapped_data['rating'] = details.get('rating')
        mapped_data['reviews_count'] = details.get('user_ratings_total') # Use 'reviews_count' model key

        # Map price_level (int) to price_text (str) - Basic Example
        price_level = details.get('price_level')
        if price_level is not None:
            mapped_data['price_text'] = "$" * price_level if price_level > 0 else "Free/Unspecified"
        else:
            mapped_data['price_text'] = None # Or keep as None if preferred

        # Map types (list) to main_category and extra_categories
        google_types = details.get('types', [])
        if google_types:
            mapped_data['main_category'] = google_types[0] # Use first type as main
            mapped_data['extra_categories'] = google_types[1:] # Use rest as extra
        else:
            mapped_data['main_category'] = None
            mapped_data['extra_categories'] = []

        # --- Location ---
        geometry = details.get('geometry', {})
        location = geometry.get('location', {})
        mapped_data['latitude'] = location.get('lat')
        mapped_data['longitude'] = location.get('lng')

        # --- Timezone/Offset ---
        # Map utc_offset (minutes, int) to timezone (str) - Placeholder, might need tz library for real mapping
        utc_offset = details.get('utc_offset')
        if utc_offset is not None:
             # This is a simplification. Real mapping needs timezone database (e.g., using pytz based on lat/lng)
             mapped_data['timezone'] = f"UTC{utc_offset:+g}" # Simple offset string
        else:
             mapped_data['timezone'] = None

        # --- Fields not directly mapped (Store in additional_json or ignore) ---
        unmapped_data = {}
        if 'business_status' in details:
            unmapped_data['business_status'] = details['business_status']
        if 'vicinity' in details:
            unmapped_data['vicinity'] = details['vicinity']
        # Add other complex fields like opening_hours, photos, reviews, address_components here if needed
        if 'opening_hours' in details:
            unmapped_data['opening_hours'] = details['opening_hours'] # Store raw complex object
        # Add other desired fields from API response that don't have direct columns

        if unmapped_data:
            mapped_data['additional_json'] = unmapped_data

        # Ensure place_id is included (it's handled separately in process_single_deep_scan for upsert)
        # mapped_data['place_id'] = details.get('place_id') # No need to map it here

        # Filter out None values *after* all mapping to avoid removing intentionally set Nones if needed by model
        # Reconsider if filtering None is always desired.
        # For now, let SQLAlchemy handle None values based on column nullability.
        # mapped_data = {k: v for k, v in mapped_data.items() if v is not None}

        logger.debug(f"Mapped data for place_id {details.get('place_id')}: {mapped_data}")
        return mapped_data
