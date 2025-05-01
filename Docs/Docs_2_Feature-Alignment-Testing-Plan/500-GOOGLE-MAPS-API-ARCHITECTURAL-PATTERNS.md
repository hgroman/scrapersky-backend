# Google Maps API Architectural Patterns

This document outlines key architectural patterns identified during the implementation and debugging of the Google Maps API integration. These patterns are likely applicable to other routes and services in the ScraperSky backend.

## 1. Job Service Pattern

The Job Service pattern handles asynchronous processing with status tracking. It's critical for long-running operations like API searches, batch scraping, and data processing.

### Core Implementation

```python
# 1. Job Creation (Router)
@router.post("/search")
async def search_endpoint(request: Request, background_tasks: BackgroundTasks, session: AsyncSession):
    # Generate a unique job ID
    job_id = uuid.uuid4()

    # Create job record with pending status
    async with session.begin():
        job = await job_service.create(
            session=session,
            job_type="feature_operation",
            tenant_id=tenant_id,
            status="pending",
            job_id=job_id,  # Explicitly pass the job_id
            metadata={
                "user_id": current_user["id"],
                "query_params": request.query_params
            }
        )

    # Add background task (ALWAYS create a new session in the background task)
    background_tasks.add_task(
        process_task,
        job_id=str(job.job_id),
        tenant_id=tenant_id
    )

    # Return immediate response with job ID and status URL
    return {
        "job_id": str(job.job_id),
        "status": "pending",
        "status_url": f"/api/v3/feature/status/{job.job_id}"
    }
```

### Job Status Retrieval

```python
@router.get("/status/{job_id}")
async def get_status(job_id: str, session: AsyncSession):
    # Retrieve job status
    async with session.begin():
        job = await job_service.get_by_id(session, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

    # Return job status with metadata
    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "progress": job.progress or 0,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "error": job.error_message,
        # Include job-specific metadata from the job_metadata field
        **job.metadata
    }
```

### Background Task Processing

```python
async def process_task(job_id: str, tenant_id: str):
    # ALWAYS create a new session for background tasks
    async with get_session() as session:
        try:
            # Update job status to processing
            async with session.begin():
                job = await job_service.get_by_id(session, job_id)
                if not job:
                    logger.error(f"Job {job_id} not found")
                    return

                await job_service.update_status(
                    session=session,
                    job_id=job_id,
                    status="processing",
                    progress=0.1
                )

            # Perform actual task in a separate transaction
            async with session.begin():
                # Your task implementation here
                result = await feature_service.perform_operation(session, job.metadata)

                # Update job status based on result
                await job_service.update_status(
                    session=session,
                    job_id=job_id,
                    status="completed",
                    progress=1.0,
                    metadata={"result_count": len(result)}
                )

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            # Update job status to failed with error message
            async with session.begin():
                await job_service.update_status(
                    session=session,
                    job_id=job_id,
                    status="failed",
                    progress=0.5,  # Indicate partial progress
                    error_message=str(e)
                )
```

### Key Considerations

1. **Job ID Management**:

   - ALWAYS explicitly pass the job_id when creating a job
   - Use UUID type consistently (convert string UUIDs when needed)
   - Return job_id as a string in API responses

2. **Status Flow**:

   - Standard statuses: "pending" → "processing" → "completed"/"failed"
   - Include progress indicator (0.0 - 1.0) for long-running tasks
   - Store detailed error messages when failures occur

3. **Metadata**:
   - Store query parameters in job_metadata for reproducibility
   - Include user context (user_id, tenant_id)
   - Add operation-specific details as needed

## 2. Transaction Management Pattern

Proper transaction management is critical for maintaining data consistency, especially with background tasks.

### Router Transaction Pattern

```python
# CORRECT: Router establishes transaction boundaries, service uses provided session
@router.post("/endpoint")
async def endpoint_handler(session: AsyncSession):
    async with session.begin():
        # Service methods receive session but don't start transactions
        result = await service.perform_operation(session, params)
    return result
```

### Service Transaction Pattern

```python
# CORRECT: Service uses provided session without transaction handling
class FeatureService:
    @staticmethod
    async def perform_operation(session: AsyncSession, params: dict):
        # Use session directly without begin()
        query = select(Model).where(Model.field == params["value"])
        result = await session.execute(query)
        return result.scalars().all()
```

### Managed Transaction Decorator

For services that should manage their own transactions, use a standard decorator:

```python
def managed_transaction(func):
    """
    Decorator for managing transactions in service methods.
    Ensures consistent transaction handling and error propagation.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Find session parameter
        session = None
        for arg in args:
            if isinstance(arg, AsyncSession):
                session = arg
                break

        if session is None:
            for key, value in kwargs.items():
                if isinstance(value, AsyncSession):
                    session = value
                    break

        if session is None:
            raise ValueError("No AsyncSession parameter found")

        # Execute function in transaction if not already in one
        if session.in_transaction():
            return await func(*args, **kwargs)
        else:
            async with session.begin():
                return await func(*args, **kwargs)

    return wrapper
```

### Background Task Transaction Pattern

```python
async def background_task():
    # CORRECT: Create a new session for background tasks
    async with get_session() as session:
        async with session.begin():
            # Perform operations
            pass
```

### Anti-Patterns to Avoid

```python
# WRONG: Service creating transaction when router already has one
@router.post("/endpoint")
async def endpoint_handler(session: AsyncSession):
    async with session.begin():  # Router transaction
        # Service also creates transaction - THIS WILL FAIL
        result = await service.operation_with_transaction(session)
    return result

# Service with its own transaction
async def operation_with_transaction(session: AsyncSession):
    # NESTED TRANSACTION - THIS CAUSES ERRORS
    async with session.begin():  # ← This conflicts with router transaction
        query = select(Model)
        result = await session.execute(query)
        return result.scalars().all()
```

## 3. Entity Storage Patterns

These patterns ensure robust entity storage, especially for batch operations and handling duplicate entities.

### Duplicate Entity Handling

```python
async def store_entities(session: AsyncSession, entities: List[Dict]):
    # 1. First check for existing entities to avoid constraint violations
    entity_ids = [entity["id"] for entity in entities if "id" in entity]
    query = select(Entity.id).where(Entity.id.in_(entity_ids))
    result = await session.execute(query)
    existing_ids = {row[0] for row in result.fetchall()}

    # 2. Process each entity individually
    for entity_data in entities:
        entity_id = entity_data.get("id")
        if not entity_id:
            logger.warning(f"Skipping entity without ID")
            continue

        try:
            if entity_id in existing_ids:
                # Update existing entity
                query = select(Entity).where(Entity.id == entity_id)
                result = await session.execute(query)
                existing_entity = result.scalar_one_or_none()

                if existing_entity:
                    # Update fields
                    for key, value in entity_data.items():
                        if hasattr(existing_entity, key):
                            setattr(existing_entity, key, value)
            else:
                # Create new entity
                new_entity = Entity(**entity_data)
                session.add(new_entity)

        except Exception as e:
            logger.error(f"Error processing entity {entity_id}: {str(e)}")
            # Continue with other entities rather than failing entirely
            continue
```

### UUID Validation and Defaults

```python
def validate_uuid(uuid_str: Optional[str], default_uuid: Optional[UUID] = None) -> UUID:
    """Convert string UUID to UUID object with validation and default handling."""
    if not uuid_str:
        if default_uuid:
            return default_uuid
        return uuid.uuid4()  # Generate new UUID

    try:
        return uuid.UUID(uuid_str)
    except ValueError:
        logger.warning(f"Invalid UUID format: {uuid_str}, using default")
        if default_uuid:
            return default_uuid
        return uuid.uuid4()
```

### Batch Operation Error Handling

```python
async def batch_operation(session: AsyncSession, items: List[Dict]) -> Tuple[int, List[Dict]]:
    """Process batch of items with proper error handling."""
    success_count = 0
    failed_items = []

    for item in items:
        try:
            # Process item
            await process_item(session, item)
            success_count += 1
        except Exception as e:
            logger.error(f"Error processing item {item.get('id')}: {str(e)}")
            # Add to failed items with error information
            failed_items.append({
                "item": item,
                "error": str(e)
            })

    return success_count, failed_items
```

## 4. Service Dependencies

Understanding service dependencies is critical for maintaining a clean architecture.

### Common Dependency Graph

```
Router
  ↓
FeatureService (domain logic)
  ↓
StorageService (database operations)
  ↓
AsyncSession (database access)
```

### Implementation Example

```python
class GoogleMapsApiRouter:
    def __init__(self):
        self.places_service = PlacesService()  # Domain logic
        self.job_service = JobService()        # Job tracking

    @router.post("/search")
    async def search_places(self, session: AsyncSession):
        # Use both services with the same session
        job = await self.job_service.create(session, ...)
        await self.places_service.start_search(session, job.id, ...)
```

### Service Reuse Guidelines

1. **Identify Common Operations**:

   - JobService can be reused for any asynchronous operation
   - StorageServices can be shared between related features

2. **Maintain Separation of Concerns**:

   - RouterA → ServiceA → CommonStorageService
   - RouterB → ServiceB → CommonStorageService

3. **Consistent Session Handling**:
   - Always pass session from outer service to inner service
   - Don't create new sessions inside services (except for background tasks)

## 5. Error Propagation

Proper error handling ensures that failures are properly captured and reported.

### Service-Level Error Handling

```python
class FeatureService:
    @staticmethod
    async def perform_operation(session: AsyncSession, params: dict):
        try:
            # Operation code
            result = await process_data(session, params)
            return result
        except ValueError as e:
            # Client error - rethrow with clear message
            logger.warning(f"Validation error: {str(e)}")
            raise ValueError(f"Invalid parameters: {str(e)}")
        except Exception as e:
            # Unexpected error - log details but return generic message
            logger.error(f"Operation error: {str(e)}", exc_info=True)
            raise RuntimeError(f"Error performing operation: {str(e)}")
```

### Router-Level Error Handling

```python
@router.post("/endpoint")
async def endpoint_handler(request: Request, session: AsyncSession):
    try:
        # Normal processing
        async with session.begin():
            result = await service.perform_operation(session, request.params)
        return result
    except ValueError as e:
        # Client validation error
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Server processing error
        raise HTTPException(status_code=500, detail=str(e))
```

### Background Task Error Handling

```python
async def background_task(job_id: str):
    async with get_session() as session:
        try:
            # Task processing
            result = await perform_complex_operation(session)

            # Update job on success
            async with session.begin():
                await job_service.update_status(
                    session, job_id,
                    status="completed",
                    result=result
                )

        except Exception as e:
            logger.error(f"Background task error: {str(e)}", exc_info=True)

            # Ensure job status is updated even on error
            try:
                async with session.begin():
                    await job_service.update_status(
                        session, job_id,
                        status="failed",
                        error_message=str(e)
                    )
            except Exception as update_error:
                # Log but don't rethrow - we're already in an error state
                logger.critical(
                    f"Failed to update job status after error: {str(update_error)}"
                )
```

## Implementation Status and Roadmap

The patterns documented here have been implemented for the Google Maps API routes with improvements to:

1. **Transaction Management**:

   - Fixed router-level transaction handling
   - Ensured background tasks use their own sessions
   - Applied managed_transaction decorator to services

2. **Job Service**:

   - Standardized job ID handling
   - Implemented consistent status updates
   - Added proper error propagation

3. **Entity Storage**:
   - Added checks for existing entities before insertion
   - Implemented UUID validation with defaults
   - Improved error handling during batch operations

### Next Steps

1. Apply these patterns to other routers:

   - Batch scraper endpoints
   - Data processing endpoints
   - Any endpoint with background processing

2. Create standardized base classes:

   - BaseStorageService with duplicate entity handling
   - BaseBackgroundTask with session and error handling

3. Add targeted tests:
   - Test transaction boundary handling
   - Test job status flow
   - Test duplicate entity handling

## Conclusion

These architectural patterns provide a foundation for consistent implementation across the ScraperSky backend. By following these patterns, we can ensure that all routes handle transactions, jobs, and errors in a standardized way, improving maintainability and reducing bugs.
