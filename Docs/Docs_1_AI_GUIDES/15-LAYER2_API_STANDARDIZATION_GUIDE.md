# API STANDARDIZATION GUIDE

This document outlines the standardized API structure implemented across the ScraperSky project. All APIs have been standardized to version 3 (v3) with a consistent URL structure and response format.

## 1. API VERSION STANDARDIZATION

### Current API Structure

All ScraperSky APIs use the `/api/v3/` prefix with standardized naming conventions:

```
/api/v3/{resource}/{action}
```

Examples:

- `/api/v3/sitemap/scan`
- `/api/v3/google-maps-api/search/places`
- `/api/v3/batch-page-scraper/scan`

### Previous API Versions (REMOVED)

All previous API versions (v1, v2) have been completely removed from the codebase. There is **NO backward compatibility** with previous endpoints.

### Pattern Compliance

When implementing new endpoints or modifying existing ones:

```python
# CORRECT API Router Definition
router = APIRouter(
    prefix="/api/v3/resource-name",  # Hyphenated resource name
    tags=["Resource Name"],          # Pascal case tag name
    responses={404: {"description": "Not found"}},
)

# CORRECT Endpoint Definition
@router.post("/action", response_model=ResponseModel)
async def perform_action(
    request: RequestModel,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    # Implementation
    pass
```

**Note on Schema Definitions:** Pydantic models used for request validation (`RequestModel`) and response serialization (`response_model`) are typically defined within the `src/models/api_models.py` file.

## 2. RESPONSE STRUCTURE STANDARDIZATION

### Synchronous Operations

For immediately completed operations:

```json
{
  "status": "success",
  "data": {
    // Operation-specific response data
  }
}
```

### Asynchronous Operations

For long-running operations that use the job system:

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000", // Standard UUID format
  "status": "pending",
  "status_url": "/api/v3/resource/status/123e4567-e89b-12d3-a456-426614174000"
}
```

### Error Responses

All error responses follow standard HTTP status codes with a consistent format:

```json
{
  "status": "error",
  "detail": "Descriptive error message",
  "type": "ErrorType" // Optional error classification
}
```

## 3. STANDARDIZED STATUS ENDPOINTS

For all asynchronous operations, implement a status endpoint:

```python
@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(
    job_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    # Validate job_id as UUID
    try:
        # Convert string to UUID for validation
        uuid_obj = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    # Retrieve job status
    async with session.begin():
        job = await job_service.get_by_id(session, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

    # Return standardized response
    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "progress": job.progress or 0,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "error": job.error_message,
        # Include job-specific metadata
        **job.metadata
    }
```

## 4. URL PATH PARAMETERS

### UUID Path Parameters

When using UUIDs in paths, ensure proper validation:

```python
@router.get("/resource/{resource_id}")
async def get_resource(
    resource_id: UUID,  # FastAPI will validate and convert to UUID object
    session: AsyncSession = Depends(get_db_session)
):
    # Implementation
    pass
```

### Query Parameters

For filtering, pagination, and sorting:

```python
@router.get("/resources")
async def list_resources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    session: AsyncSession = Depends(get_db_session)
):
    # Implementation with pagination
    pass
```

## 5. ERROR HANDLING

FastAPI's built-in error handling is used throughout the application:

```python
# CORRECT Error Handling
@router.post("/resource")
async def create_resource(
    request: ResourceRequest,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        # Validate request
        if not request.name:
            raise HTTPException(status_code=400, detail="Name is required")

        # Database operation
        async with session.begin():
            # Implementation

        return {"status": "success", "data": result}
    except ValueError as e:
        # Client error
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Server error with logging
        logger.error(f"Error creating resource: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 6. STANDARDIZED FRONTEND API CALLS

Front-end code should use the standardized endpoints:

```javascript
// CORRECT API Call
async function fetchResource(resourceId) {
  const response = await fetch(`/api/v3/resources/${resourceId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch resource");
  }

  return await response.json();
}
```

## 7. CONCLUSION

This API standardization creates a consistent, maintainable API structure and removes potential confusion from having multiple API versions. All new endpoints should follow these standardized patterns to ensure a clean, consistent API surface.

**IMPORTANT**: When adding new endpoints, ALWAYS follow this standardized structure.
