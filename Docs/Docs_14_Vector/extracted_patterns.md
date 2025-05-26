# Extracted Patterns for Vector DB Knowledge System

**Date:** 2025-05-23
**Author:** Cascade AI

## Pattern 1: Missing Service Creation

### Metadata
- **Title:** Missing Service Creation Pattern
- **Description:** Pattern for extracting business logic from routers into dedicated service files, following the architectural principle of separation of concerns.
- **File Types:** ["py"]
- **Code Type:** "service"
- **Severity:** "CRITICAL-ARCHITECTURE"
- **Confidence Score:** 0.95
- **Applied Count:** 1
- **Source Task ID:** 3p49o6N28enG
- **Source Document ID:** ROg40BvEt0vR

### Problem Pattern
```python
# Router file containing business logic
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.db.session import get_session_dependency
from src.models.place import Place, PlaceStatusEnum

router = APIRouter(prefix="/api/v3/places-staging", tags=["places-staging"])

@router.get("/queue")
async def get_staging_queue(
    session: AsyncSession = Depends(get_session_dependency)
):
    # Business logic directly in router
    query = select(Place).where(Place.status == PlaceStatusEnum.Selected)
    result = await session.execute(query)
    places = result.scalars().all()
    return {"places": places}

@router.post("/update-status/{place_id}")
async def update_place_status(
    place_id: str,
    status: str,
    session: AsyncSession = Depends(get_session_dependency)
):
    # Business logic directly in router
    query = update(Place).where(Place.place_id == place_id).values(status=status)
    await session.execute(query)
    await session.commit()
    return {"status": "updated"}
```

### Solution Pattern
```python
# Step 1: Create new service file
# src/services/staging_editor_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.models.place import Place, PlaceStatusEnum

class StagingEditorService:
    @staticmethod
    async def get_staged_places(session: AsyncSession, filters=None):
        """Get places from the staging queue with optional filters"""
        query = select(Place).where(Place.status == PlaceStatusEnum.Selected)
        # Apply additional filters if provided
        if filters:
            # Add filter logic here
            pass
        
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_place_status(session: AsyncSession, place_id: str, status: str):
        """Update the status of a place in the staging queue"""
        query = update(Place).where(Place.place_id == place_id).values(status=status)
        await session.execute(query)
        # Note: We don't commit here as transaction management is router's responsibility
        return {"status": "updated"}
    
    @staticmethod
    async def process_staging_editor_queue(session: AsyncSession):
        """Process the staging editor queue"""
        # Implementation of queue processing logic
        pass

# Step 2: Update router to use the service
# src/routers/places_staging.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_session_dependency
from src.services.staging_editor_service import StagingEditorService

router = APIRouter(prefix="/api/v3/places-staging", tags=["places-staging"])

@router.get("/queue")
async def get_staging_queue(
    session: AsyncSession = Depends(get_session_dependency)
):
    # Router delegates to service
    places = await StagingEditorService.get_staged_places(session)
    return {"places": places}

@router.post("/update-status/{place_id}")
async def update_place_status(
    place_id: str,
    status: str,
    session: AsyncSession = Depends(get_session_dependency)
):
    # Router handles transaction and delegates business logic to service
    async with session.begin():
        result = await StagingEditorService.update_place_status(session, place_id, status)
    return result
```

### Verification Steps
1. Service accepts AsyncSession parameters (no self-created sessions)
2. Router delegates to service (no business logic in router)
3. All ORM operations use session parameter
4. No tenant_id filtering in service methods
5. Router handles transaction boundaries

### Key Learnings
1. Architectural Adherence: Keep business logic within the service layer and routers focused on request handling and dependency injection.
2. Code Organization: Creating dedicated service files improves code organization, maintainability, and testability.
3. Session Handling: Services should accept database sessions as parameters rather than creating their own.
4. Transaction Management: Routers should own transaction boundaries, not services.

## Pattern 2: Authentication and Attribute Access Correction

### Metadata
- **Title:** Authentication and Attribute Access Correction Pattern
- **Description:** Pattern for fixing authentication issues and attribute access errors in API routers, particularly when accessing user data from JWT tokens.
- **File Types:** ["py"]
- **Code Type:** "router"
- **Severity:** "CRITICAL-SECURITY"
- **Confidence Score:** 0.9
- **Applied Count:** 1
- **Source Task ID:** ildO8Gz1EtoV
- **Source Document ID:** eYzJsz2tQlQ7

### Problem Pattern
```python
# Router file with authentication and attribute access issues
from fastapi import APIRouter, Depends, HTTPException
from src.auth.jwt_auth import get_current_active_user, UserInToken  # Import error - UserInToken doesn't exist

router = APIRouter(prefix="/api/v3/scan", tags=["email-scanner"])

# Missing authentication dependency
@router.post("/website")
async def scan_website(domain_id: str):
    # No authentication check
    return {"job_id": "123", "status": "queued"}

# Incorrect type hint and attribute access
@router.get("/status/{job_id}")
async def get_scan_status(
    job_id: str,
    current_user: UserInToken = Depends(get_current_active_user)  # Incorrect type hint
):
    # Incorrect attribute access (dot notation instead of dictionary access)
    user_id = current_user.id  # Error: current_user is a dictionary, not an object
    return {"job_id": job_id, "user_id": user_id, "status": "processing"}
```

### Solution Pattern
```python
# Fixed router file
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from src.auth.jwt_auth import get_current_active_user  # Removed non-existent import

router = APIRouter(prefix="/api/v3/scan", tags=["email-scanner"])

# Added authentication dependency
@router.post("/website")
async def scan_website(
    domain_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)  # Added authentication
):
    return {"job_id": "123", "status": "queued"}

# Corrected type hint and attribute access
@router.get("/status/{job_id}")
async def get_scan_status(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)  # Corrected type hint
):
    # Corrected attribute access (dictionary access)
    user_id = current_user['id']  # Fixed: using dictionary key access
    return {"job_id": job_id, "user_id": user_id, "status": "processing"}
```

### Verification Steps
1. Server restarts successfully without import errors
2. All endpoints have authentication dependencies
3. User ID is correctly accessed using dictionary notation
4. Endpoints can be accessed with valid JWT token
5. Endpoints reject requests without authentication

### Key Learnings
1. Import Verification: Always verify that imported names are actually defined and exported by the source module.
2. Attribute Access Consistency: Use appropriate access patterns based on object type (dot notation for objects, key access for dictionaries).
3. Authentication Requirements: All API endpoints must include authentication dependencies.
4. Type Hints: Ensure type hints accurately reflect the actual types returned by dependencies.
5. Testing Strategy: Directly test endpoints using tools like curl or Swagger UI to verify functionality.

## SQL for Inserting Patterns into Vector DB

To insert these patterns into the vector database, the following SQL can be used after generating the appropriate embeddings:

```sql
-- Insert Pattern 1: Missing Service Creation
INSERT INTO fix_patterns (
    title,
    description,
    code_before,
    code_after,
    pattern_vector,
    file_types,
    code_type,
    severity,
    confidence_score,
    applied_count
) VALUES (
    'Missing Service Creation Pattern',
    'Pattern for extracting business logic from routers into dedicated service files, following the architectural principle of separation of concerns.',
    '# Router file containing business logic...',  -- Insert full code_before here
    '# Step 1: Create new service file...',  -- Insert full code_after here
    [EMBEDDING_VECTOR],  -- This will be generated programmatically
    ARRAY['py'],
    'service',
    'CRITICAL-ARCHITECTURE',
    0.95,
    1
);

-- Insert Pattern 2: Authentication and Attribute Access Correction
INSERT INTO fix_patterns (
    title,
    description,
    code_before,
    code_after,
    pattern_vector,
    file_types,
    code_type,
    severity,
    confidence_score,
    applied_count
) VALUES (
    'Authentication and Attribute Access Correction Pattern',
    'Pattern for fixing authentication issues and attribute access errors in API routers, particularly when accessing user data from JWT tokens.',
    '# Router file with authentication and attribute access issues...',  -- Insert full code_before here
    '# Fixed router file...',  -- Insert full code_after here
    [EMBEDDING_VECTOR],  -- This will be generated programmatically
    ARRAY['py'],
    'router',
    'CRITICAL-SECURITY',
    0.9,
    1
);
```

## Next Steps

1. Generate embeddings for these patterns using OpenAI's text-embedding-ada-002 model
2. Insert the patterns with their embeddings into the fix_patterns table
3. Update the Vector DB Implementation Plan document to reflect progress
4. Test the vector search functionality with these patterns
5. Identify candidate files for pattern application
