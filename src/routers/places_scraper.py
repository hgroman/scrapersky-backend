"""Google Places search and staging functionality."""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import logging
import asyncio
import uuid
import json
import aiohttp
import jwt
from datetime import datetime
import os

from ..models import PlacesSearchRequest, PlacesSearchResponse, PlacesStatusResponse
from ..db.sb_connection import db

# Security setup for JWT authentication
security = HTTPBearer()

# Status tracking (in-memory for simplicity, replace with Redis in production)
_job_statuses: Dict[str, PlacesStatusResponse] = {}

router = APIRouter(prefix="/api/v1", tags=["places-search"])

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user info."""
    try:
        # Get JWT secret from environment
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not jwt_secret:
            raise ValueError("SUPABASE_JWT_SECRET not configured")

        # Decode the JWT token
        payload = jwt.decode(credentials.credentials, jwt_secret, algorithms=["HS256"])
        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("User ID not found in token")

        # Get user profile from Supabase
        with db.get_cursor() as cur:
            cur.execute("SELECT * FROM profiles WHERE id = %s", (user_id,))
            user_profile_tuple = cur.fetchone()

            # Get column names from cursor description
            columns = [desc[0] for desc in cur.description] if cur.description else []

        if not user_profile_tuple:
            # If no profile exists, use default tenant
            return {
                "user_id": user_id,
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Unknown User"
            }

        # Convert tuple to dictionary
        user_profile = dict(zip(columns, user_profile_tuple)) if columns else {}

        # Return user information
        return {
            "user_id": user_id,
            "tenant_id": user_profile.get("tenant_id", "550e8400-e29b-41d4-a716-446655440000"),
            "name": user_profile.get("name", "Unknown User"),
            "email": user_profile.get("email")
        }
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        )

async def search_google_places(location: str, business_type: str, radius_km: int = 10) -> List[Dict]:
    """Search Google Places API for businesses."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable not set")

    # Convert km to meters for the API
    radius_meters = radius_km * 1000

    # Format the query for Google Places API Text Search
    query = f"{business_type} in {location}"

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "radius": radius_meters,
        "key": api_key
    }

    all_results = []

    try:
        async with aiohttp.ClientSession() as session:
            # First page
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Google Places API request failed")

                data = await response.json()
                if data.get("status") != "OK":
                    error_message = data.get("error_message", "Unknown error")
                    raise HTTPException(status_code=400, detail=f"Google Places API error: {error_message}")

                all_results.extend(data.get("results", []))

                # Handle pagination with next_page_token if it exists
                next_page_token = data.get("next_page_token")

                # Google requires a delay before using next_page_token
                while next_page_token:
                    await asyncio.sleep(2)  # Wait for token to be valid

                    next_params = {
                        "pagetoken": next_page_token,
                        "key": api_key
                    }

                    async with session.get(url, params=next_params) as next_response:
                        if next_response.status != 200:
                            break

                        next_data = await next_response.json()
                        if next_data.get("status") != "OK":
                            break

                        all_results.extend(next_data.get("results", []))
                        next_page_token = next_data.get("next_page_token")

                        # If we have next_page_token, wait again before using it
                        if next_page_token:
                            await asyncio.sleep(2)

        return all_results

    except Exception as e:
        logging.error(f"Error searching Google Places: {str(e)}")
        raise

async def process_places_search(job_id: str, request: PlacesSearchRequest, user_info: dict):
    """Process the places search in the background."""
    status = _job_statuses[job_id]
    status.status = "running"

    try:
        # Search Google Places API
        places = await search_google_places(
            location=request.location,
            business_type=request.business_type,
            radius_km=request.radius_km
        )

        status.total_places = len(places)

        # Insert results into staging table
        for place in places:
            try:
                # Extract relevant data
                place_data = {
                    "place_id": place.get("place_id"),
                    "name": place.get("name"),
                    "formatted_address": place.get("formatted_address", ""),
                    "business_type": request.business_type,
                    "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                    "longitude": place.get("geometry", {}).get("location", {}).get("lng"),
                    "vicinity": place.get("vicinity", ""),
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("user_ratings_total"),
                    "price_level": place.get("price_level"),
                    "tenant_id": user_info.get("tenant_id", request.tenant_id),
                    "created_by": user_info.get("user_id", "system"),
                    "user_id": user_info.get("user_id"),
                    "user_name": user_info.get("name", "Unknown"),
                    "search_job_id": job_id,
                    "search_query": request.business_type,
                    "search_location": request.location,
                    "raw_data": json.dumps(place)  # Store the raw JSON for future reference
                }

                # Use an "upsert" operation to avoid duplicates
                query = """
                    INSERT INTO places_staging (
                        place_id, name, formatted_address, business_type,
                        latitude, longitude, vicinity, rating,
                        user_ratings_total, price_level, tenant_id,
                        created_by, user_id, user_name, search_job_id,
                        search_query, search_location, raw_data
                    ) VALUES (
                        %(place_id)s, %(name)s, %(formatted_address)s, %(business_type)s,
                        %(latitude)s, %(longitude)s, %(vicinity)s, %(rating)s,
                        %(user_ratings_total)s, %(price_level)s, %(tenant_id)s,
                        %(created_by)s, %(user_id)s, %(user_name)s, %(search_job_id)s,
                        %(search_query)s, %(search_location)s, %(raw_data)s
                    )
                    ON CONFLICT (place_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        formatted_address = EXCLUDED.formatted_address,
                        business_type = EXCLUDED.business_type,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        vicinity = EXCLUDED.vicinity,
                        rating = EXCLUDED.rating,
                        user_ratings_total = EXCLUDED.user_ratings_total,
                        price_level = EXCLUDED.price_level,
                        search_job_id = EXCLUDED.search_job_id,
                        search_query = EXCLUDED.search_query,
                        search_location = EXCLUDED.search_location,
                        search_time = NOW(),
                        user_id = EXCLUDED.user_id,
                        user_name = EXCLUDED.user_name,
                        raw_data = EXCLUDED.raw_data;
                """

                with db.get_cursor() as cur:
                    cur.execute(query, place_data)

                status.stored_places += 1

            except Exception as e:
                logging.error(f"Error storing place {place.get('name', 'unknown')}: {str(e)}")
                # Continue with next place

        # Mark job as completed
        status.status = "completed"

    except Exception as e:
        # Mark job as failed
        status.status = "failed"
        status.error = str(e)
        logging.error(f"Places search job failed: {str(e)}")

@router.post("/places/search", response_model=PlacesSearchResponse)
async def search_places(
    request: PlacesSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Search for places using Google Places API and store in staging table.
    """
    # Generate a unique job ID
    job_id = str(uuid.uuid4())

    # Use tenant ID from authenticated user if available
    if current_user and "tenant_id" in current_user:
        request.tenant_id = current_user["tenant_id"]

    # Initialize job status
    _job_statuses[job_id] = PlacesStatusResponse(
        job_id=job_id,
        status="pending",
        search_query=request.business_type,
        search_location=request.location,
        user_id=current_user.get("user_id", "anonymous"),
        user_name=current_user.get("name", "Unknown User")
    )

    # Launch search in background
    background_tasks.add_task(process_places_search, job_id, request, current_user)

    # Return response with job ID
    return PlacesSearchResponse(
        job_id=job_id,
        status="started",
        status_url=f"/api/v1/places/status/{job_id}"
    )

@router.get("/places/status/{job_id}", response_model=PlacesStatusResponse)
async def get_search_status(job_id: str):
    """
    Get the status of a places search job.
    """
    if job_id not in _job_statuses:
        raise HTTPException(status_code=404, detail="Job not found")

    return _job_statuses[job_id]

@router.get("/places/staging")
async def get_staging_places(
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Get places from the staging table with optional filtering.
    """
    # Use authenticated user's tenant_id if none provided
    if not tenant_id:
        tenant_id = current_user.get("tenant_id", "550e8400-e29b-41d4-a716-446655440000")

    query = "SELECT * FROM places_staging WHERE tenant_id = %(tenant_id)s"
    params = {"tenant_id": tenant_id, "limit": limit, "offset": offset}

    if status:
        query += " AND status = %(status)s"
        params["status"] = status

    query += " ORDER BY search_time DESC LIMIT %(limit)s OFFSET %(offset)s"

    with db.get_cursor() as cur:
        try:
            cur.execute(query, params)
            places = cur.fetchall()

            # Get total count for pagination
            count_query = "SELECT COUNT(*) FROM places_staging WHERE tenant_id = %(tenant_id)s"
            count_params = {"tenant_id": tenant_id}

            if status:
                count_query += " AND status = %(status)s"
                count_params["status"] = status

            cur.execute(count_query, count_params)
            count_result = cur.fetchone()
            total_count = count_result[0] if count_result else 0

            return {
                "places": places,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logging.error(f"Error getting staging places: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/places/update-status")
async def update_place_status(
    place_id: str,
    status: str,
    tenant_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Update the status of a place in the staging table.
    """
    # Use authenticated user's tenant_id if none provided
    if not tenant_id:
        tenant_id = current_user.get("tenant_id", "550e8400-e29b-41d4-a716-446655440000")

    valid_statuses = ["new", "selected", "maybe", "not_a_fit", "archived"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    query = """
        UPDATE places_staging
        SET
            status = %(status)s,
            updated_by = %(user_id)s,
            updated_at = NOW()
        WHERE place_id = %(place_id)s AND tenant_id = %(tenant_id)s
        RETURNING id;
    """

    with db.get_cursor() as cur:
        try:
            cur.execute(query, {
                "status": status,
                "place_id": place_id,
                "tenant_id": tenant_id,
                "user_id": current_user.get("user_id", "anonymous")
            })
            result = cur.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Place not found")

            return {"message": "Status updated successfully"}

        except Exception as e:
            logging.error(f"Error updating place status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/places/update-notes")
async def update_place_notes(
    place_id: str,
    notes: str,
    tenant_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Update the notes for a place in the staging table.
    """
    # Use authenticated user's tenant_id if none provided
    if not tenant_id:
        tenant_id = current_user.get("tenant_id", "550e8400-e29b-41d4-a716-446655440000")

    query = """
        UPDATE places_staging
        SET
            notes = %(notes)s,
            updated_by = %(user_id)s,
            updated_at = NOW()
        WHERE place_id = %(place_id)s AND tenant_id = %(tenant_id)s
        RETURNING id;
    """

    with db.get_cursor() as cur:
        try:
            cur.execute(query, {
                "notes": notes,
                "place_id": place_id,
                "tenant_id": tenant_id,
                "user_id": current_user.get("user_id", "anonymous")
            })
            result = cur.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Place not found")

            return {"message": "Notes updated successfully"}

        except Exception as e:
            logging.error(f"Error updating place notes: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
