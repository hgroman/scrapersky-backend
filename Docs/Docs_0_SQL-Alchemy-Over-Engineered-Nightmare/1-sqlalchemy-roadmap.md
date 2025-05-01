# ScraperSky Modernization Roadmap: SQLAlchemy First (8-Hour Implementation)

This document provides a rapid approach to implementing SQLAlchemy in ScraperSky, replacing the home-grown SQL architecture with a standardized ORM in a single 8-hour shift.

## Core Philosophy

Rather than refactoring the existing architecture while preserving its raw SQL foundation, we're pivoting to:

1. **Implement SQLAlchemy fast** as the foundation
2. **Convert all scrapers in one go**
3. **Simplify and standardize** rather than document complexity

## Hour 1: SQLAlchemy Setup (60 min)

### Setup and Configuration (30 min)

- Install required packages: `pip install sqlalchemy alembic asyncpg`
- Create database connection in `src/db/engine.py`:
  ```python
  from sqlalchemy.ext.asyncio import create_async_engine
  
  DATABASE_URL = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
  engine = create_async_engine(DATABASE_URL, echo=False)
  ```
- Create session manager in `src/db/session.py`:
  ```python
  from sqlalchemy.ext.asyncio import AsyncSession
  from sqlalchemy.orm import sessionmaker
  
  async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  
  async def get_session():
      async with async_session() as session:
          yield session
  ```

### Core Model Definition (30 min)

Create base models in `src/models/`:
```python
# src/models/base.py
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# src/models/domain.py
from sqlalchemy import Column, String, UUID
from sqlalchemy.sql import func
from .base import Base
import uuid

class Domain(Base):
    __tablename__ = "domains"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    domain = Column(String, nullable=False)
    tenant_id = Column(UUID, nullable=False, index=True)
    # Add other fields...
```

## Hour 2: Core Service Layer (60 min)

### Generic SQLAlchemy Service (45 min)

Create a single generic service in `src/services/sqlalchemy_service.py`:
```python
class SQLAlchemyService:
    def __init__(self, model):
        self.model = model
        
    async def get_by_id(self, id, tenant_id=None):
        async with async_session() as session:
            query = select(self.model).where(self.model.id == id)
            if tenant_id:
                query = query.where(self.model.tenant_id == tenant_id)
            result = await session.execute(query)
            return result.scalars().first()
            
    async def get_all(self, tenant_id=None, **filters):
        async with async_session() as session:
            query = select(self.model)
            if tenant_id:
                query = query.where(self.model.tenant_id == tenant_id)
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
            result = await session.execute(query)
            return result.scalars().all()
            
    async def create(self, data):
        async with async_session() as session:
            async with session.begin():
                obj = self.model(**data)
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
                return obj
                
    # Add update and delete methods
```

### Model Service Instances (15 min)

Create instances for each model:
```python
# src/services/domain_service.py
from .sqlalchemy_service import SQLAlchemyService
from ..models.domain import Domain

domain_service = SQLAlchemyService(Domain)

# Repeat for other models (Place, Job, etc.)
```

## Hour 3-4: Convert First Scraper (120 min)

### Sitemap Analyzer Conversion (90 min)

Update the sitemap_scraper.py file:
```python
from ..services.domain_service import domain_service
from ..services.job_service import job_service
from ..models.domain import Domain
from ..models.job import Job

@router.post("/scrapersky")
async def analyze_domain(
    request: DomainScanRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(auth_service.get_current_user)
):
    # Validate tenant_id 
    tenant_id = auth_service.validate_tenant_id(request.tenant_id, current_user)
    
    # Create domain using SQLAlchemy service
    domain = await domain_service.create({
        "domain": request.base_url,
        "tenant_id": tenant_id,
        "created_by": current_user.get("id"),
        "status": "pending"
    })
    
    # Create job using SQLAlchemy service
    job = await job_service.create({
        "job_type": "domain_scan",
        "domain_id": domain.id,
        "tenant_id": tenant_id,
        "status": "pending"
    })
    
    # Start background task
    background_tasks.add_task(
        process_domain_scan,
        str(job.id),
        str(domain.id),
        tenant_id
    )
    
    return {
        "job_id": str(job.id),
        "domain_id": str(domain.id),
        "status": "pending"
    }
```

### Update Process Function (30 min)

Convert the background processing function:
```python
async def process_domain_scan(job_id, domain_id, tenant_id):
    try:
        # Update job status using SQLAlchemy
        await job_service.update(job_id, {"status": "running"})
        
        # Get domain using SQLAlchemy
        domain = await domain_service.get_by_id(domain_id, tenant_id)
        
        # Scraping logic remains the same
        results = await scrape_domain(domain.domain)
        
        # Store results using SQLAlchemy
        await domain_service.update(domain_id, {
            "status": "complete",
            "metadata": results
        })
        
        # Update job status using SQLAlchemy
        await job_service.update(job_id, {
            "status": "complete",
            "result_data": {"urls_found": len(results.get("urls", []))}
        })
    except Exception as e:
        await job_service.update(job_id, {
            "status": "failed",
            "error": str(e)
        })
        raise
```

## Hour 5-6: Convert Core Services (120 min)

### Error Service Update (30 min)

Modify error_service.py to handle SQLAlchemy exceptions:
```python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

class ErrorService:
    def handle_exception(self, exception):
        if isinstance(exception, IntegrityError):
            return HTTPException(status_code=400, detail="Database constraint violation")
        if isinstance(exception, NoResultFound):
            return HTTPException(status_code=404, detail="Resource not found")
        if isinstance(exception, SQLAlchemyError):
            return HTTPException(status_code=500, detail="Database error")
        # Other error handling
```

### Auth Service Update (30 min)

Simplify auth_service.py:
```python
class AuthService:
    async def get_current_user(self, token):
        # Implementation stays mostly the same
        
    def validate_tenant_id(self, tenant_id, current_user):
        # Convert to UUID if needed
        try:
            tenant_id = str(UUID(tenant_id))
            return tenant_id
        except (ValueError, TypeError):
            return current_user.get("tenant_id", DEFAULT_TENANT_ID)
```

### Job Manager Service Update (60 min)

Rewrite job_manager_service.py using SQLAlchemy:
```python
class JobManagerService:
    async def create_job(self, job_type, tenant_id, user_id, metadata=None):
        return await job_service.create({
            "job_type": job_type,
            "tenant_id": tenant_id,
            "created_by": user_id,
            "status": "pending",
            "metadata": metadata or {}
        })
    
    async def update_job_status(self, job_id, status, progress=None, error=None):
        updates = {"status": status}
        if progress is not None:
            updates["progress"] = progress
        if error is not None:
            updates["error"] = error
        return await job_service.update(job_id, updates)
```

## Hour 7: Convert Remaining Scrapers (60 min)

### Convert Places Scraper (30 min)

Apply the same pattern to places_scraper.py:
```python
@router.post("/places/search")
async def search_places(
    request: PlacesSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(auth_service.get_current_user)
):
    # Validate and create job using SQLAlchemy services
    # Start background task
```

### Convert Other Scrapers (30 min)

Apply the pattern to any remaining scrapers:
- Email scraper
- Contact scraper
- Other endpoints

## Hour 8: Testing and Cleanup (60 min)

### Manual Testing (30 min)

Test all converted endpoints:
- Test sitemap analyzer endpoint
- Test places scraper endpoint
- Verify job tracking works
- Check error handling

### Deployment Prep (30 min)

Prepare for deployment:
- Check for any missed imports
- Verify configuration works in Docker environment
- Create a brief document on the new architecture
- Clean up any unused code

## Success Criteria

1. All database operations use SQLAlchemy
2. All four scrapers work as expected
3. Core services (auth, error, job) operate with SQLAlchemy
4. Performance is comparable to previous implementation

## Benefits Achieved

1. **Standardized Database Access**: Using industry-standard ORM
2. **Tenant Isolation**: Built into model queries
3. **Error Handling**: More consistent with SQLAlchemy exceptions
4. **Code Reduction**: Elimination of raw SQL strings
5. **Maintainability**: Clearer model relationships

## Breaking Changes and Mitigation

1. **Response Format Changes**
   - IDs will be UUIDs instead of strings in some cases
   - Timestamps may be formatted differently

2. **Request Validation**
   - More strict validation on UUID fields
   - Better error messages

3. **API Behavior**
   - More consistent error handling
   - Better transaction integrity

## Key Architecture Principles to Preserve

1. **Separation of concerns**
   - Models for data structures
   - Services for business logic
   - Routes for API endpoints

2. **Tenant isolation**
   - Built into SQLAlchemy models
   - Enforced at the service layer

3. **Standardized error handling**
   - Consistent HTTP responses
   - Proper error logging

4. **Background processing**
   - Job tracking and status updates
   - Progress reporting

## Simplified Approach to Common Problems

### Tenant Isolation

```python
# Before: Complex SQL where clauses
query = "SELECT * FROM table WHERE tenant_id = %(tenant_id)s"

# After: Built into the service
records = await domain_service.get_all(tenant_id=tenant_id)
```

### Complex Queries

```python
# Before: Raw SQL with multiple conditions
query = """
    SELECT * FROM places_staging 
    WHERE tenant_id = %(tenant_id)s 
    AND status = %(status)s 
    AND business_type = %(business_type)s
"""

# After: Simple filter parameters
places = await place_service.get_all(
    tenant_id=tenant_id,
    status=status,
    business_type=business_type
)
```

### Transaction Management

```python
# Before: Manual transaction handling
await db_service.execute_transaction([
    ("INSERT INTO table1 ...", params1),
    ("UPDATE table2 ...", params2)
])

# After: SQLAlchemy session
async with async_session() as session:
    async with session.begin():
        session.add(Domain(**domain_data))
        session.add(Place(**place_data))
```

### Job Status Tracking

```python
# Before: Manual status updates to in-memory dict
_job_statuses[job_id]["status"] = "running"

# After: Database record updates
await job_service.update(job_id, {"status": "running", "progress": 0.5})
```

## Success Criteria

1. All database operations use SQLAlchemy
2. Documentation is reduced by at least 60%
3. Code is more maintainable with fewer lines
4. Performance is equal or better than before
5. API behavior remains consistent where possible

## Conclusion

This approach prioritizes building on a solid foundation (SQLAlchemy) rather than continuing to document and refine a more complex architecture. By establishing a clean base, future development will be simpler, better documented by default, and more maintainable.
