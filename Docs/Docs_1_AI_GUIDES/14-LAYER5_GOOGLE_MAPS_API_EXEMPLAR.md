# GOOGLE MAPS API EXEMPLAR IMPLEMENTATION

This document highlights the Google Maps API implementation as the **golden exemplar** of best practices for the ScraperSky project. This implementation embodies all the architectural patterns and practices that should be followed throughout the codebase.

## 1. WHY GOOGLE MAPS API IS THE EXEMPLAR

The Google Maps API implementation:

1. **Follows all architectural principles correctly**
2. **Demonstrates proper transaction handling**
3. **Shows correct background task management**
4. **Properly handles errors and edge cases**
5. **Uses the job service pattern for asynchronous operations**
6. **Implements correct service dependencies**

When implementing or modifying any feature in ScraperSky, you should refer to this implementation as the standard to follow.

## 2. KEY ARCHITECTURAL PATTERNS DEMONSTRATED

### Transaction Management

```python
@router.post("/search")
async def search_places(
    request: PlacesSearchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    # EXEMPLARY: Router establishes transaction boundaries
    async with session.begin():
        # Generate job ID
        job_id = uuid.uuid4()

        # Create job record with pending status
        job = await job_service.create(
            session=session,
            job_type="places_search",
            status="pending",
            job_id=job_id,
            metadata={
                "user_id": current_user["id"],
                "query": request.query
            }
        )

    # Add background task AFTER transaction is committed
    background_tasks.add_task(
        places_service.process_search,
        job_id=str(job_id),
        query=request.query
    )

    # Return immediate response with job ID
    return PlacesSearchResponse(
        job_id=str(job_id),
        status="pending",
        status_url=f"/api/places/status/{job_id}"
    )
```

### Background Task Management

```python
# EXEMPLARY: Background task with proper session management
async def process_search(job_id: str, query: str):
    # Create dedicated session for background task
    session = async_session_factory()
    try:
        # Update job status to processing
        async with session.begin():
            await job_service.update_status(
                session=session,
                job_id=job_id,
                status="processing",
                progress=0.1
            )

        try:
            # Perform search in separate transaction
            async with session.begin():
                # API call logic here
                results = await places_api.search(query)

                # Store results
                for place in results:
                    place_entity = Place(
                        id=place.id,
                        name=place.name,
                        # other fields...
                    )
                    session.add(place_entity)

            # Update job to completed in final transaction
            async with session.begin():
                await job_service.update_status(
                    session=session,
                    job_id=job_id,
                    status="completed",
                    progress=1.0,
                    metadata={"result_count": len(results)}
                )

        except Exception as e:
            # Handle errors with proper logging
            logger.error(f"Error processing search job {job_id}: {str(e)}")

            # Update job to failed with error details
            async with session.begin():
                await job_service.update_status(
                    session=session,
                    job_id=job_id,
                    status="failed",
                    error_message=str(e)
                )
    finally:
        # EXEMPLARY: Always close session in finally block
        await session.close()
```

### Service Responsibility Separation

```python
# EXEMPLARY: Clear separation of responsibilities
class PlacesService:
    def __init__(self):
        self.places_api = PlacesApi()
        self.storage_service = PlacesStorageService()

    # Domain logic only, no transaction management
    async def search_places(self, session: AsyncSession, query: str):
        # Call API
        results = await self.places_api.search(query)

        # Store results using storage service
        stored_places = await self.storage_service.store_places(
            session=session,
            places=results
        )

        return stored_places
```

### Storage Service Pattern

```python
# EXEMPLARY: Dedicated storage service for database operations
class PlacesStorageService:
    async def store_places(self, session: AsyncSession, places: List[Dict]):
        # Check for existing places to avoid duplicates
        place_ids = [place["id"] for place in places if "id" in place]
        query = select(Place.id).where(Place.id.in_(place_ids))
        result = await session.execute(query)
        existing_ids = {row[0] for row in result.fetchall()}

        # Process each place
        stored_places = []
        for place_data in places:
            place_id = place_data.get("id")
            if not place_id:
                continue

            if place_id in existing_ids:
                # Update existing place
                query = select(Place).where(Place.id == place_id)
                result = await session.execute(query)
                existing_place = result.scalar_one_or_none()

                if existing_place:
                    # Update fields
                    for key, value in place_data.items():
                        if hasattr(existing_place, key):
                            setattr(existing_place, key, value)

                    stored_places.append(existing_place)
            else:
                # Create new place
                new_place = Place(**place_data)
                session.add(new_place)
                stored_places.append(new_place)

        # Return all stored places
        return stored_places
```

### Error Handling Pattern

```python
# EXEMPLARY: Comprehensive error handling
@router.get("/places/{place_id}")
async def get_place(place_id: str, session: AsyncSession = Depends(get_db_session)):
    try:
        async with session.begin():
            # Parameter validation with clear error messages
            if not place_id:
                raise ValueError("Place ID is required")

            # Service call
            place = await places_service.get_place_by_id(session, place_id)

            # Not found handling
            if not place:
                raise HTTPException(
                    status_code=404,
                    detail=f"Place with ID {place_id} not found"
                )

            return place
    except ValueError as e:
        # Client error with 400 response
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected error with logging
        logger.error(f"Error retrieving place {place_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 3. JOB SERVICE PATTERN

The Job Service pattern is a key part of the Google Maps API exemplar and should be used for all asynchronous operations:

```python
# EXEMPLARY: Job creation and tracking
@router.post("/batch-operation")
async def start_batch_operation(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session)
):
    # Create job with consistent pattern
    async with session.begin():
        job = await job_service.create(
            session=session,
            job_type="batch_operation",
            status="pending",
            metadata=request.dict()
        )

    # Add background task after transaction commits
    background_tasks.add_task(
        process_batch_operation,
        job_id=str(job.id),
        items=request.items
    )

    # Consistent response format
    return {
        "job_id": str(job.id),
        "status": "pending",
        "status_url": f"/api/batch/status/{job.id}"
    }
```

## 4. PATTERNS TO EMULATE

When working on any part of the codebase, emulate these patterns from the Google Maps API implementation:

### 1. Transaction Ownership

- **Routers** own transaction boundaries with `async with session.begin()`
- **Services** are transaction-aware but never start their own transactions
- **Background tasks** create their own sessions and manage their own transactions

### 2. Job Tracking for Async Operations

- Generate job ID at the router level
- Store job with pending status before starting background task
- Update job status throughout processing
- Include useful metadata with jobs
- Provide status endpoints to check job progress

### 3. Error Handling

- Validate inputs with clear error messages
- Use appropriate HTTP status codes
- Log errors with context
- Update job status on failures
- Don't expose internal errors to clients

### 4. Duplicate Entity Handling

- Check for existing entities before insertion
- Update existing entities when appropriate
- Handle constraint violations gracefully

### 5. Clean Service Dependencies

- Use dependency injection
- Separate domain logic from storage logic
- Follow consistent naming patterns
- Don't mix responsibilities

## 5. WHERE TO FIND THE EXEMPLAR CODE

The exemplar Google Maps API implementation can be found in:

- **Router**: `src/routers/google_maps_api.py`
- **Services**:
  - `src/services/places/places_service.py`
  - `src/services/places/places_storage_service.py`
- **Models**: `src/models/place.py`

## 6. APPLYING THESE PATTERNS TO YOUR WORK

When implementing new features or fixing existing ones:

1. **Start with the Google Maps API pattern**
2. **Copy its transaction management approach**
3. **Follow its service organization**
4. **Reuse patterns like the Job Service for async operations**
5. **Maintain consistent error handling**

If you're uncertain about how to implement a specific aspect, refer to the Google Maps API code first before seeking other examples.

## 7. CONCLUSION

The Google Maps API implementation is considered the **gold standard** for how features should be implemented in ScraperSky. By following its patterns consistently, we ensure that the entire codebase maintains high quality, reliability, and maintainability.

Remember: When in doubt, refer to the Google Maps API implementation as your guide.

## Current Work Orders and Documentation

The following work orders document the implementation of the Google Maps API features:

1. **Database Schema Updates**:

   - `project-docs/07-database-connection-audit/07-26-DATABASE-SCHEMA-CHANGE-GUIDE.md`

2. **Results Implementation**:

   - `project-docs/07-database-connection-audit/07-27-LOCALMINER-DISCOVERYSCAN-RESULTS-IMPLEMENTATION.md`

3. **Search History UI**:
   - `project-docs/07-database-connection-audit/07-28-SEARCH-HISTORY-UI-IMPLEMENTATION.md`
