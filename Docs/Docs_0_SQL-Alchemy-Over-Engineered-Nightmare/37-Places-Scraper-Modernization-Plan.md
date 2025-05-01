# Places Scraper Modernization Plan

## 1. Current State Assessment

The `places_scraper.py` router provides functionality for searching Google Places API and managing results in a staging table. Key characteristics of the current implementation:

- Mixed service usage (both modernized and legacy)
- Direct SQL queries for database operations
- Large functions with complex logic
- Background task processing for search operations
- Some modernized patterns already in use (job_service with SQLAlchemy)

## 2. Modernization Goals

1. **Replace Direct SQL**: Convert all raw SQL to SQLAlchemy ORM operations
2. **Service Reorganization**: Move database operations into appropriate service layers
3. **Standardize Error Handling**: Implement consistent error_service usage
4. **Improve Transaction Management**: Use proper session.begin() patterns
5. **Refactor Large Functions**: Break down complex functions
6. **Follow Service Organization**: Implement domain-specific service structure

## 3. Lessons Learned from Previous Modernization Efforts

This plan builds directly on lessons documented throughout the ScraperSky modernization project:

1. **From Doc 35 (ScraperSky Modernization Milestone Updated Plan)**:

   - Applied the successful step-by-step approach used for sitemap_scraper.py
   - Adopted the proven service organization structure
   - Focused on clear separation between database operations and API logic

2. **From Doc 33 (Service Interface Standardization)**:

   - Implemented consistent service method signatures
   - Added proper error handling with clear messages
   - Standardized validation patterns across services

3. **From Doc 28 (BatchProcessor Modernization Summary)**:

   - Incorporated transaction management best practices
   - Applied proper session handling patterns
   - Utilized the async/await patterns consistently throughout services

4. **From Doc 21 (Sitemap Scraper Refactoring Plan)**:

   - Followed the successful pattern of breaking down large functions
   - Applied the proven approaches for replacing raw SQL with SQLAlchemy
   - Used the tested error handling strategies

5. **Key Implementation Patterns Reused**:
   - Consistent use of `async with session.begin()` for transaction management
   - Service methods with clear single responsibilities
   - Schema validation before database operations
   - Standardized tenant isolation in queries
   - Background task processing with status updates

## 4. Required SQLAlchemy Models

### Place Model

```python
# src/models/place.py
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .base import Base

class Place(Base):
    __tablename__ = "places_staging"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(String, nullable=False, unique=True, index=True)
    name = Column(String)
    formatted_address = Column(String)
    business_type = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    vicinity = Column(String)
    rating = Column(Float)
    user_ratings_total = Column(Integer)
    price_level = Column(Integer)
    status = Column(String, default="new")
    tenant_id = Column(UUID(as_uuid=True), index=True)
    created_by = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    search_job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    search_query = Column(String)
    search_location = Column(String)
    raw_data = Column(Text)
    search_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### PlaceSearch Model

```python
# src/models/place_search.py
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .base import Base

class PlaceSearch(Base):
    __tablename__ = "place_searches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(UUID(as_uuid=True))
    location = Column(String)
    business_type = Column(String)
    params = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 5. Service Creation and Organization

### 5.1 Service Directory Structure

```
src/
  services/
    places/
      __init__.py
      places_service.py       # Primary service for database operations
      places_search_service.py # Service for Google Places API operations
      places_storage_service.py # Service for storage operations
```

### 5.2 Places Service Implementation

Key service methods to create:

1. **Create Search Record**
2. **Store Places Data**
3. **Update Place Status**
4. **Retrieve Places with Filtering**
5. **Batch Place Operations**

## 6. Implementation Steps

### Step 1: Create SQLAlchemy Models

- Create Place and PlaceSearch models in the models directory
- Add proper relationships and indexes
- Ensure UUID handling is consistent

### Step 2: Implement Places Service

- Create places_service.py with core CRUD operations
- Implement transaction management with session.begin()
- Add error handling and logging

Example method:

```python
@staticmethod
async def get_places(
    session: AsyncSession,
    tenant_id: str,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Tuple[List[Place], int]:
    """
    Get places with filtering options

    Returns tuple of (places, total_count)
    """
    query = select(Place).where(Place.tenant_id == tenant_id)

    if status:
        query = query.where(Place.status == status)

    # Get total count for pagination
    count_query = select(func.count()).select_from(
        query.order_by(None).subquery()
    )
    total_count = await session.scalar(count_query)

    # Apply pagination
    query = (
        query.order_by(Place.search_time.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await session.execute(query)
    places = result.scalars().all()

    return places, total_count
```

### Step 3: Implement Places Search Service

- Create places_search_service.py for Google Places API operations
- Extract Google Places search functionality from router
- Add error handling and retry logic

### Step 4: Refactor Endpoints

- Update `/places/search` endpoint to use new services
- Use SQLAlchemy session management with `session.begin()`
- Apply error_service consistently

Example endpoint refactoring:

```python
@router.post("/places/search", response_model=PlacesSearchResponse)
async def search_places(
    request: PlacesSearchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(auth_service.get_current_user)
):
    """Search Places API and store results"""
    try:
        # Validate tenant ID
        tenant_id = auth_service.validate_tenant_id(
            request.tenant_id, current_user
        )

        # Create job
        async with session.begin():
            job = await job_service.create(
                session,
                {
                    "job_type": "places",
                    "tenant_id": tenant_id,
                    "status": "pending",
                    "created_by": current_user.get("user_id"),
                    "job_metadata": {
                        "search_query": request.business_type,
                        "search_location": request.location,
                        "user_id": current_user.get("user_id"),
                        "user_name": current_user.get("name", "Unknown User")
                    }
                }
            )

        # Launch background task
        background_tasks.add_task(
            process_places_search,
            str(job.id),
            request,
            current_user
        )

        return PlacesSearchResponse(
            job_id=str(job.id),
            status="started",
            status_url=f"/api/v1/places/status/{job.id}"
        )

    except ValidationError as e:
        return error_service.validation_error(str(e))
    except Exception as e:
        return error_service.internal_error(
            f"Error creating job: {str(e)}"
        )
```

### Step 5: Refactor Background Task

- Break down large process_places_search function
- Use service methods for data processing and storage
- Implement proper transaction management

## 7. Testing Strategy

1. **Unit Tests**: Create tests for each service method
2. **Integration Tests**: Test the integration between services
3. **API Tests**: Test the endpoints with various inputs

Example test case:

```python
async def test_places_search():
    """Test places search functionality"""
    # Test setup and data

    # Test the search function
    response = await client.post(
        "/api/v1/places/search",
        json={
            "location": "New York",
            "business_type": "restaurant",
            "radius_km": 10
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assertions
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert "status_url" in response.json()
```

## 8. Implementation Timeline

### Week 1: Setup and Models

- Day 1-2: Create SQLAlchemy models
- Day 3-4: Set up service directory structure
- Day 5: Basic service implementation

### Week 2: Core Service Implementation

- Day 1-2: Implement places_service.py
- Day 3-4: Implement places_search_service.py
- Day 5: Integration testing

### Week 3: Endpoint Refactoring

- Day 1-2: Refactor search endpoint
- Day 3-4: Refactor status and update endpoints
- Day 5: Final testing and documentation
