# ScraperSky Reference Implementation: Google Maps API

## CRITICAL REFERENCE FILES

**IMPORTANT: Examine these ACTUAL, WORKING implementation files directly:**

1. **Router Implementation**:
   - Actual file: [`/src/routers/google_maps_api.py`](/src/routers/google_maps_api.py)
   - Key sections:
     - Transaction boundaries: lines 301-378 (search endpoint)
     - RBAC integration: lines 323-345 (full permission checks)
     - Error handling: lines 378-446 (status endpoint)
     - Background task: lines 154-300 (process_places_search)

2. **Service Implementations**:
   - Primary service: [`/src/services/places/places_service.py`](/src/services/places/places_service.py)
   - Search service: [`/src/services/places/places_search_service.py`](/src/services/places/places_search_service.py)
   - Storage service: [`/src/services/places/places_storage_service.py`](/src/services/places/places_storage_service.py)

3. **Transaction Test Implementation**:
   - Actual file: [`/tests/transaction/test_transaction_frontendscout.py`](/tests/transaction/test_transaction_frontendscout.py)

## Architectural Diagram

```
┌───────────────────────────────────────┐
│              HTTP Request             │
└───────────────────────┬───────────────┘
                        ▼
┌───────────────────────────────────────┐
│            FastAPI Router             │
│   (/src/routers/google_maps_api.py)   │
└───────────────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌───────────────────┐         ┌───────────────────┐
│  RBAC Permission  │         │    Transaction    │
│      Checks       │         │    Boundaries     │
└───────────────────┘         └─────────┬─────────┘
                                        │
┌───────────────────────────────────────▼──────────────────────────────────────┐
│                               Service Layer                                   │
├────────────────────┬────────────────────┬─────────────────────────────────────┤
│  places_service.py │places_search_service│places_storage_service.py            │
└────────────────────┴────────────────────┴─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼──────────────────────────────────────┐
│                            SQLAlchemy ORM Layer                              │
└───────────────────────────────────────┬───────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼──────────────────────────────────────┐
│                                 Database                                     │
└────────────────────────────────────────────────────────────────────────────────┘
```

This document details the architectural patterns used in the Google Maps API component of ScraperSky, which serves as our reference implementation for all other components. Every route and service in the ScraperSky backend should follow these patterns.

## 1. Layered Architecture

The Google Maps API component follows a strict layered architecture:

```
Router → Service → Repository
```

### Router Layer (`/src/routers/google_maps_api.py`)
- Handles HTTP requests and responses
- Manages transaction boundaries
- Performs permission checks
- Dispatches to appropriate services
- Does not contain business logic

### Service Layer (`/src/services/places/places_service.py`, etc.)
- Contains business logic
- Is transaction-aware but doesn't manage transactions
- Implements domain operations
- Coordinates between multiple repositories if needed
- Is independent of HTTP/REST concepts

### Repository Layer (ORM models and query methods)
- Handles data access
- Implements database operations
- Uses SQLAlchemy ORM
- Is unaware of business rules and services

## 2. RBAC Integration Pattern

The Google Maps API component implements RBAC in a consistent manner:

### Permission Checking Pattern
```python
# 1. Check basic permission
require_permission(current_user, "places:search")

# 2. Check feature enablement
await require_feature_enabled(
    tenant_id=tenant_id,
    feature_name="google_maps_api",
    session=session,
    user_permissions=current_user.get("permissions", [])
)

# 3. Check role level
await require_role_level(
    user=current_user,
    required_role_id=ROLE_HIERARCHY["USER"],
    session=session
)

# 4. Optional: Check tab permission
await require_tab_permission(
    user=current_user,
    tab_name="review-organize",
    feature_name="google_maps_api",
    session=session
)
```

### Route-Level Permission Documentation
```python
@router.post("/search", response_model=PlacesSearchResponse)
async def search_places(
    # ... parameters
):
    """
    Search for places using Google Maps API.
    
    Permissions required:
    - places:search permission
    - google_maps_api feature enabled
    - USER role or higher
    """
```

## 3. Transaction Management Pattern

The Google Maps API follows the "Routers own transaction boundaries, services do not" pattern:

### Router Transaction Pattern
```python
@router.get("/status/{job_id}")
async def get_status(job_id, session: AsyncSession = Depends(get_session)):
    """Route handler with transaction management."""
    async with session.begin():
        result = await service.get_something(session, job_id)
    return result
```

### Service Transaction Awareness Pattern
```python
async def service_method(self, session: AsyncSession, ...):
    """Service method that is transaction-aware."""
    in_transaction = session.in_transaction()
    logger.debug(f"Session transaction state: {in_transaction}")
    
    # Implementation that doesn't create transactions
    # ...
```

### Background Task Transaction Pattern
```python
async def process_in_background(job_id: str, session: Optional[AsyncSession] = None):
    """Background task with proper transaction management."""
    # Create own session for background task
    async with async_session_factory() as task_session:
        async with task_session.begin():
            # Implementation
            pass
```

## 4. Error Handling Pattern

Consistent error handling across the component:

### Router Error Handling
```python
@router.post("/endpoint")
async def route_handler():
    try:
        # Implementation
        return result
    except ValueError as e:
        # Convert to appropriate HTTP error
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred"
        )
```

### Service Error Handling
```python
async def service_method(self, ...):
    try:
        # Implementation
        return result
    except Exception as e:
        logger.error(f"Error in service_method: {str(e)}")
        # Propagate exception with context
        raise ServiceError(f"Operation failed: {str(e)}") from e
```

## 5. Tenant Isolation Pattern

Consistent tenant isolation throughout the component:

### Tenant ID Handling
```python
# 1. Get tenant_id with proper fallbacks
tenant_id = request.tenant_id or current_user.get("tenant_id", "")
if not tenant_id:
    tenant_id = DEFAULT_TENANT_ID

# 2. Add tenant filter to database queries
query = query.where(Entity.tenant_id == tenant_id)

# 3. Pass tenant_id to services
result = await service.do_something(
    session=session,
    tenant_id=tenant_id,
    other_params=...
)
```

## 6. Dependency Injection Pattern

Clean dependency injection for easier testing and modularization:

### Router Dependencies
```python
@router.get("/endpoint")
async def route_handler(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    service: PlacesService = Depends(Depends(lambda: places_service))
):
    # Implementation using injected dependencies
```

## 7. Response Standardization Pattern

Consistent response formats:

### Response Models
```python
class PlacesResponse(BaseModel):
    success: bool
    data: Optional[List[PlaceDTO]]
    total_count: int
    message: Optional[str] = None
    
    @classmethod
    def success(cls, data, total_count):
        return cls(success=True, data=data, total_count=total_count)
    
    @classmethod
    def error(cls, message):
        return cls(success=False, data=None, total_count=0, message=message)
```

## 8. Background Processing Pattern

Consistent background task handling:

```python
@router.post("/process")
async def process_data(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    # Validate request
    # ...
    
    # Create a job record with explicit transaction
    async with session.begin():
        job = await job_service.create(
            session=session,
            job_data={...}
        )
    
    # Add background task
    background_tasks.add_task(
        process_in_background,
        job_id=job.id,
        parameters=request.parameters,
        session=None  # Pass None so background task creates its own session
    )
    
    # Return immediate response
    return {"job_id": job.id, "status": "processing"}
```

## Implementation Checklist for Components

When standardizing any ScraperSky component, use this checklist:

1. **Layered Architecture**
   - [ ] Separate router, service, and repository concerns
   - [ ] Ensure business logic is in services, not routers
   - [ ] Make services independent of HTTP concepts

2. **RBAC Integration**
   - [ ] Add all four levels of permission checks
   - [ ] Document permissions in route docstrings
   - [ ] Verify tenant isolation in database queries

3. **Transaction Management**
   - [ ] Ensure routers own transaction boundaries
   - [ ] Make services transaction-aware
   - [ ] Handle background tasks properly

4. **Error Handling**
   - [ ] Implement consistent error handling in routers
   - [ ] Add appropriate error logging
   - [ ] Convert exceptions to appropriate HTTP responses

5. **Testing**
   - [ ] Test transaction boundaries
   - [ ] Test permission checks
   - [ ] Test background task behavior
   - [ ] Test error handling

## Key Files to Reference

To understand this reference implementation, examine these files:

1. **Router Implementation**
   - `/src/routers/google_maps_api.py`

2. **Service Implementations**
   - `/src/services/places/places_service.py`
   - `/src/services/places/places_search_service.py`
   - `/src/services/places/places_storage_service.py`

3. **Transaction Tests**
   - `/tests/transaction/test_transaction_actionqueue.py`