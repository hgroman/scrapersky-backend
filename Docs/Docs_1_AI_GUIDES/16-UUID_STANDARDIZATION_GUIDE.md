# UUID STANDARDIZATION GUIDE

This document provides critical guidance on the standardized approach to UUIDs throughout the ScraperSky project. Following these standards is essential for database compatibility and consistent API behavior.

## 1. CRITICAL UUID REQUIREMENTS

### Standard UUID Format

All UUIDs in the ScraperSky project MUST:

- Use the **standard UUID format** without prefixes or custom formatting
- Be stored in the database as **PostgreSQL UUID type**
- Be properly converted between string and UUID types when needed

### INCORRECT (Legacy) Approaches

The following patterns are **NO LONGER USED** and should be corrected if encountered:

```python
# ❌ INCORRECT: Prefixed UUID (LEGACY PATTERN)
job_id = f"sitemap_{uuid.uuid4().hex[:32]}"
job_id = f"places_{uuid.uuid4().hex}"
batch_id = f"batch_{uuid.uuid4().hex}"

# ❌ INCORRECT: Custom UUID formatting
job_id = uuid.uuid4().hex  # Missing hyphens
job_id = uuid.uuid4().hex[:32]  # Truncated
```

### CORRECT Approach

```python
# ✅ CORRECT: Standard UUID generation
job_id = uuid.uuid4()  # UUID object for database ORM
job_id_str = str(uuid.uuid4())  # String format for API responses
```

## 2. DATABASE SCHEMA STANDARDS

### SQLAlchemy Model Definition

```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid

class Job(Base):
    __tablename__ = "jobs"

    # ✅ CORRECT: UUID column definition
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ✅ CORRECT: UUID foreign key definition
    user_id = Column(PGUUID(as_uuid=True), nullable=True)
```

### Alembic Migration Definition

When creating migrations for UUID columns:

```python
# In an alembic migration
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    op.add_column('table_name', sa.Column('job_id', UUID(as_uuid=True), nullable=True))

    # For converting existing string columns to UUID
    op.execute("ALTER TABLE table_name ALTER COLUMN job_id TYPE uuid USING job_id::uuid")
```

## 3. UUID HANDLING IN ROUTERS

### Path Parameter Validation

```python
from uuid import UUID

@router.get("/status/{job_id}")
async def get_job_status(
    job_id: UUID,  # FastAPI will validate and convert to UUID
    session: AsyncSession = Depends(get_db_session)
):
    # job_id is already a UUID object
    async with session.begin():
        job = await job_service.get_by_id(session, job_id)

    return {"status": job.status}
```

### Response Formatting

```python
@router.post("/scan")
async def scan_resource(
    request: ScanRequest,
    session: AsyncSession = Depends(get_db_session)
):
    # Generate proper UUID
    job_id = uuid.uuid4()

    async with session.begin():
        # Create job with UUID
        job = await job_service.create(
            session=session,
            job_id=job_id,  # Pass UUID object to service
            status="pending"
        )

    # Return string representation in response
    return {
        "job_id": str(job_id),  # Convert to string for JSON response
        "status": "pending",
        "status_url": f"/api/v3/resource/status/{job_id}"
    }
```

## 4. UUID HANDLING IN SERVICES

### Service Method Definition

```python
async def create_job(
    session: AsyncSession,
    job_id: UUID,  # Accept UUID type
    status: str,
    **kwargs
) -> Job:
    """Create a new job with proper UUID handling."""
    job = Job(
        id=job_id,  # UUID object for ORM model
        status=status,
        **kwargs
    )
    session.add(job)
    await session.flush()
    return job
```

### UUID Validation Helper

```python
def validate_uuid(uuid_str: Optional[str]) -> UUID:
    """Convert string UUID to UUID object with validation."""
    if not uuid_str:
        raise ValueError("UUID string is required")

    try:
        return uuid.UUID(uuid_str)
    except ValueError:
        raise ValueError(f"Invalid UUID format: {uuid_str}")
```

## 5. UUID HANDLING IN PYDANTIC MODELS

### Request Model Definition

```python
from pydantic import BaseModel, UUID4

class JobCreateRequest(BaseModel):
    # Pydantic will validate UUID format
    parent_job_id: Optional[UUID4] = None
    name: str
    priority: int = 0
```

### Response Model Definition

```python
from pydantic import BaseModel, UUID4, Field
from datetime import datetime

class JobResponse(BaseModel):
    # UUID fields in responses
    job_id: UUID4
    parent_job_id: Optional[UUID4] = None
    created_at: datetime
    status: str

    # Model configuration
    class Config:
        # Allow UUID objects in ORM mode
        orm_mode = True
```

## 6. UUID CONVERSION FOR LEGACY DATA

If you encounter legacy data with prefixed UUIDs, use this conversion approach:

```python
def convert_legacy_job_id(legacy_job_id: str) -> UUID:
    """Convert legacy prefixed job_id to standard UUID."""
    if not legacy_job_id:
        raise ValueError("Job ID is required")

    # Check if it's already a standard UUID
    try:
        return uuid.UUID(legacy_job_id)
    except ValueError:
        pass

    # Handle prefixed format (e.g., "sitemap_123e4567...")
    try:
        # Extract UUID part after prefix
        if "_" in legacy_job_id:
            prefix, uuid_part = legacy_job_id.split("_", 1)
            return uuid.UUID(uuid_part)

        # If no underscore but it's a hex string, try to convert directly
        return uuid.UUID(legacy_job_id)
    except Exception:
        raise ValueError(f"Cannot convert legacy job ID: {legacy_job_id}")
```

## 7. COMMON ISSUES AND SOLUTIONS

### Type Mismatch Errors

**Problem**: `sqlalchemy.exc.DataError: (psycopg2.errors.InvalidTextRepresentation) invalid input syntax for type uuid`

**Solution**: Ensure you're passing a UUID object, not a string:

```python
# ❌ INCORRECT
job = await job_service.get_by_id(session, job_id_string)

# ✅ CORRECT
job = await job_service.get_by_id(session, uuid.UUID(job_id_string))
```

### UUID Validation Errors

**Problem**: `ValueError: badly formed hexadecimal UUID string`

**Solution**: Implement proper validation and error handling:

```python
try:
    job_id = uuid.UUID(job_id_string)
except ValueError:
    raise HTTPException(status_code=400, detail="Invalid job ID format")
```

## 8. TESTING CONSIDERATIONS

When writing tests that involve UUIDs:

1. **Generate consistent UUIDs** for reproducible tests:

   ```python
   TEST_UUID = uuid.UUID('123e4567-e89b-12d3-a456-426614174000')
   ```

2. **Validate UUID responses**:

   ```python
   response = client.post("/api/v3/resource/scan")
   data = response.json()

   # Validate UUID format
   assert uuid.UUID(data["job_id"])
   ```

## 9. CONCLUSION

Following these UUID standardization guidelines ensures consistency across the ScraperSky codebase and database. All UUID handling should follow the standard patterns outlined in this document to prevent type mismatch errors and ensure proper database operation.
