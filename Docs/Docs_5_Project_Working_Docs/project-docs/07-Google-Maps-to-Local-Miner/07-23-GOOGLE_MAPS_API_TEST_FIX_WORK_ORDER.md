# Google Maps API Test Script Fix Work Order

## Overview

Fix the Google Maps API test script to align with our architectural principles and ensure proper functionality for searching coffee shops near Ithaca, NY.

## Current Issues

1. Session Management

   - Using direct session creation instead of standardized pattern
   - Mixing connection patterns (direct DB access and session creation)

2. Method Compatibility

   - Incorrect method names in service calls
   - Missing proper transaction boundaries

3. Database Access
   - Direct database access using db.get_cursor()
   - Not following SQLAlchemy patterns

## Required Changes

### 1. Session Management Fix

```python
# Remove:
from src.session.async_session import get_session, create_async_session

# Add:
from src.session.async_session import get_session
from sqlalchemy import select
from src.models.profile import Profile
from src.models.place import Place
```

### 2. Service Method Alignment

```python
# Update method calls:
search_results = await places_search_service.search_places(
    business_type=business_type,
    location=location,
    radius_km=10,
    api_key=api_key
)

await places_storage_service.save_place(
    session=session,
    place_data=place,
    job_id=job_id,
    user_id=TEST_USER_ID,
    business_type=business_type
)

result = await places_service.get_place_details(
    place_id=place_id,
    api_key=api_key
)
```

### 3. Database Access Standardization

```python
# Replace direct DB access with SQLAlchemy:
async with get_session() as session:
    async with session.begin():
        result = await session.execute(
            select(Profile).where(Profile.id == TEST_USER_ID)
        )
        user = result.scalar_one_or_none()
```

## Implementation Steps

1. Update imports and remove direct session creation
2. Fix service method calls to match implementations
3. Replace direct database access with SQLAlchemy
4. Update database verification logic
5. Test with coffee shops in Ithaca, NY

## Success Criteria

1. No linter errors
2. Successful connection to Google Maps API
3. Proper transaction management
4. Correct database operations
5. Successful search for coffee shops in Ithaca, NY

## Test Parameters

- Business Type: "coffee shop"
- Location: "Ithaca, NY"
- Radius: 10km
- Test User: 5905e9fe-6c61-4694-b09a-6602017b000a

## Execution Plan

1. Create backup of current test script
2. Implement changes in order
3. Run tests and verify results
4. Document any issues or adjustments needed
