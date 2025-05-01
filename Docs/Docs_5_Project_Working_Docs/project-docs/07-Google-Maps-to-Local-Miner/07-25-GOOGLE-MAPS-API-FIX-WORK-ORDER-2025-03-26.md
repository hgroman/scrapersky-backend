# Google Maps API Fix Work Order - 2025-03-26

## URGENT: Critical Implementation Issues Requiring Immediate Attention

This document serves as a formal work order for fixing critical issues with the Google Maps API implementation. The previous implementation (documented in `07-24-GOOGLE-MAPS-API-IMPLEMENTATION-2025-03-26.md`) contains **SERIOUS FLAWS** that must be addressed immediately before this code can be considered production-ready.

## Executive Summary

During implementation of the Google Maps API functionality, the following issues were addressed:

1. ✅ Created the missing `place_searches` table
2. ✅ Fixed UUID standardization in JWT authentication
3. ✅ Restored missing `search_and_store` method in `PlacesSearchService` class

However, a **CRITICAL ISSUE** was introduced:

4. ❌ **URGENT FIX NEEDED**: Instead of properly updating the database schema to include required status tracking fields, an **UNACCEPTABLE in-memory workaround** was implemented that will fail in production environments.

## Detailed Issue Description

### Critical Issue: Improper Status Tracking Implementation

**Problem**: The Google Maps API router code expects the `place_searches` table to have `status` and `updated_at` columns, but these columns were not added to the database schema. Instead of properly altering the database table, an in-memory workaround was implemented that temporarily appears to work but will cause serious failures in production.

**Specific Implementation Flaws**:

1. Status information is stored only in memory (in the `_job_statuses` dictionary in `google_maps_api.py`)
2. All status data is lost on server restart
3. Solution completely fails in multi-server environments
4. No database persistence for critical tracking information
5. Violates architectural principles and creates technical debt

**Current Implementation**:

```python
# In google_maps_api.py
_job_statuses = {}  # In-memory dictionary for status tracking

# Status updates happen here, but only in memory
_job_statuses[job_id] = {
    "job_id": job_id,
    "status": "complete" if result["success"] else "failed",
    "progress": 1.0,
    "created_at": _job_statuses[job_id]["created_at"],
    "updated_at": datetime.now().isoformat(),
    "places_count": result.get("places_count", 0),
    "error": result.get("error")
}
```

## Required Fixes

### 1. Database Schema Update

Execute the following SQL to add the missing columns to the `place_searches` table:

```sql
ALTER TABLE place_searches
ADD COLUMN status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW();
```

### 2. Update SQLAlchemy Model

Modify the `PlaceSearch` model in `src/models/place_search.py` to include the new columns:

```python
# Add these fields to the PlaceSearch class
status = Column(String(50), default="pending")
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3. Update Service Implementation

Modify the `search_and_store` method in `PlacesSearchService` to use database status tracking instead of the in-memory workaround:

```python
@staticmethod
async def search_and_store(
    session: Any,
    job_id: str,
    business_type: str,
    location: str,
    radius_km: int = 10,
    api_key: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for places and store them in the database.
    """
    from ...models.place_search import PlaceSearch
    from sqlalchemy import update
    from .places_storage_service import PlacesStorageService

    try:
        # Update the search record to mark it as processing
        stmt = update(PlaceSearch).where(
            PlaceSearch.id == job_id
        ).values(
            status="processing",
            updated_at=datetime.utcnow()
        )
        await session.execute(stmt)
        await session.commit()

        # Perform the search
        places = await PlacesSearchService.search_places(
            location=location,
            business_type=business_type,
            radius_km=radius_km,
            max_results=20
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
            user_id=user_id or "00000000-0000-0000-0000-000000000000"
        )

        # Update the status in the database
        stmt = update(PlaceSearch).where(
            PlaceSearch.id == job_id
        ).values(
            status="complete",
            updated_at=datetime.utcnow()
        )
        await session.execute(stmt)
        await session.commit()

        return {
            "success": True,
            "places_count": success_count,
            "job_id": job_id
        }

    except Exception as e:
        logger.error(f"Error in search and store: {str(e)}")

        # Update the status to failed in the database
        try:
            stmt = update(PlaceSearch).where(
                PlaceSearch.id == job_id
            ).values(
                status="failed",
                updated_at=datetime.utcnow()
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as update_err:
            logger.error(f"Error updating search status: {str(update_err)}")

        return {
            "success": False,
            "error": str(e),
            "job_id": job_id
        }
```

### 4. Update Status Endpoint

Modify the `get_search_status` endpoint in `google_maps_api.py` to primarily use the database for status information:

```python
@router.get("/search/status/{job_id}", response_model=PlacesStatusResponse)
async def get_search_status(
    job_id: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user)
) -> PlacesStatusResponse:
    """
    Get the status of a places search job.
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
                session=session,
                job_id=job_id,
                tenant_id=tenant_id
            )

            if not search_record:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

            # Use database status information
            return PlacesStatusResponse(
                job_id=job_id,
                status=search_record.status or "unknown",
                progress=1.0 if search_record.status == "complete" else 0.0,
                created_at=search_record.created_at,
                updated_at=search_record.updated_at
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving search status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")
```

## Additional Issues to Address

1. Tenant ID handling in `search_and_store` is using a hardcoded value rather than properly passing the tenant from the request
2. Error handling in `get_search_by_id` could be improved for robustness
3. The `search_and_store` method should be refactored to better adhere to transaction management principles

## Verification Steps

After implementing these fixes, verify the correct functionality by:

1. **Schema Verification**: Use psql to verify the new columns exist in the `place_searches` table:

   ```bash
   \d place_searches
   ```

2. **API Testing**: Use curl to test the full workflow:

   ```bash
   # 1. Make search request
   curl -v http://localhost:8000/api/v3/google-maps-api/search/places -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer scraper_sky_2024" \
     -d '{"business_type": "coffee", "location": "Ithaca, NY", "radius_km": 10, "tenant_id": "550e8400-e29b-41d4-a716-446655440000"}'

   # 2. Check status (use job_id from previous response)
   curl -v "http://localhost:8000/api/v3/google-maps-api/search/status/{job_id}" \
     -H "Authorization: Bearer scraper_sky_2024"

   # 3. Verify database directly
   SELECT id, status, created_at, updated_at FROM place_searches WHERE id = '{job_id}';
   ```

3. **Restart Testing**: Restart the server and verify status information persists:
   ```bash
   # After server restart, check status again
   curl -v "http://localhost:8000/api/v3/google-maps-api/search/status/{job_id}" \
     -H "Authorization: Bearer scraper_sky_2024"
   ```

## Future Considerations

1. Consider implementing database migrations properly using Alembic
2. Add unit and integration tests specifically for this functionality
3. Review the error handling strategy for all Google Maps API related components

## Related Documentation

- [07-24-GOOGLE-MAPS-API-IMPLEMENTATION-2025-03-26.md](/project-docs/07-database-connection-audit/07-24-GOOGLE-MAPS-API-IMPLEMENTATION-2025-03-26.md) - Original implementation document (contains flaws)
- [07-23-GOOGLE_MAPS_API_TEST_FIX_WORK_ORDER.md](/project-docs/07-database-connection-audit/07-23-GOOGLE_MAPS_API_TEST_FIX_WORK_ORDER.md) - Initial work order
- [07-17-ARCHITECTURAL_PRINCIPLES.md](/project-docs/07-database-connection-audit/07-17-ARCHITECTURAL_PRINCIPLES.md) - Architectural guidelines
