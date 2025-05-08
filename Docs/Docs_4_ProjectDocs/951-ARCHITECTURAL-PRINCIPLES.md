# ScraperSky Architectural Principles

This document outlines the core architectural principles that guide the ScraperSky Backend development. These principles should be considered inviolable and followed in all development work.

## 1. Transaction Management

### Core Principle
**Routers own transactions, services are transaction-aware**

### Guidelines
- Transactions MUST be started and committed/rolled back at the router level
- Services should accept session objects but NEVER commit or rollback
- Always use context managers for transaction blocks
- Ensure proper error handling to guarantee transaction rollback on errors
- Never leave transactions open across asynchronous boundaries

### Example Pattern
```python
@router.post("/resource", response_model=ResourceResponse)
async def create_resource(resource_data: ResourceCreate, db: Session = Depends(get_db)):
    try:
        # Transaction starts here
        db.begin()

        # Services use the session but don't commit/rollback
        result = resource_service.create_resource(db, resource_data)

        # Router commits the transaction
        db.commit()
        return result

    except Exception as e:
        # Router handles rollback
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

## 2. Session Management

### Core Principle
**Use dependency injection for sessions with proper lifecycle management**

### Guidelines
- Always obtain database sessions through FastAPI dependency injection
- Never create database connections directly in service code
- Close sessions at the end of request lifecycle
- Use connection pooling for efficient resource utilization
- Maintain clear separation between session creation and session usage

### Example Pattern
```python
# In dependencies.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In router.py
@router.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    return item_service.get_item(db, item_id)
```

## 3. Authentication Boundary

### Core Principle
**JWT authentication ONLY at API router level, never in services**

### Guidelines
- Authentication MUST occur at the router/controller level only
- Services should NEVER check authentication or access tokens
- Pass authorized user context to services as needed
- Keep authentication logic isolated from business logic
- Use dependency injection for authentication checks

### Example Pattern
```python
# In auth.py
def get_current_user(token: str = Depends(oauth2_scheme)):
    # JWT validation logic here
    return validated_user

# In router.py
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    # User is already authenticated here
    return user_service.get_user_data(current_user.id)
```

## 4. UUID Standardization

### Core Principle
**All UUIDs must be proper PostgreSQL UUIDs, no custom formats**

### Guidelines
- Use UUID v4 for all identifiers requiring high uniqueness
- Store UUIDs as UUID type in the database, not as strings
- Generate UUIDs using standard libraries, not custom implementations
- Ensure consistent UUID handling across application and database
- Validate UUID format when receiving as input

### Example Pattern
```python
import uuid
from sqlalchemy import Column, UUID

class MyModel(Base):
    __tablename__ = "my_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

def create_resource(db: Session, data: Dict):
    new_resource = MyModel(
        id=uuid.uuid4(),  # Use standard uuid library
        # other fields
    )
    db.add(new_resource)
    return new_resource
```

## 5. Connection Pooling

### Core Principle
**All database connections must use connection pooling**

### Guidelines
- Never create direct database connections outside the connection pool
- Configure appropriate pool size based on workload
- Monitor pool usage to identify connection leaks
- Implement retry logic for temporary connection failures
- Use SQLAlchemy for all database interactions

### Example Pattern
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## 6. Error Handling

### Core Principle
**Consistent error handling with proper HTTP status codes**

### Guidelines
- Map application exceptions to appropriate HTTP status codes
- Provide meaningful error messages to clients
- Log detailed error information for debugging
- Handle expected exceptions gracefully
- Always roll back transactions on errors

### Example Pattern
```python
@router.get("/resource/{resource_id}")
def get_resource(resource_id: str, db: Session = Depends(get_db)):
    try:
        resource = resource_service.get_resource(db, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        return resource
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving resource {resource_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 7. API Standardization

### Core Principle
**Consistent API patterns with standardized responses**

### Guidelines
- Use standard HTTP methods appropriately (GET, POST, PUT, DELETE)
- Return consistent response structures
- Use meaningful API paths following REST principles
- Include version in API paths
- Implement pagination for list endpoints

### Example Pattern
```python
@router.get("/v3/resources", response_model=PaginatedResponse[ResourceResponse])
def list_resources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    resources = resource_service.list_resources(db, skip=skip, limit=limit)
    total = resource_service.count_resources(db)

    return {
        "items": resources,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": total > skip + limit
    }
```

## Compliance

All new code must comply with these architectural principles. Existing code should be refactored to comply as part of ongoing maintenance.

Team leads and code reviewers are responsible for ensuring compliance with these principles during code reviews.

## Exceptions

Any exceptions to these principles must be:
1. Documented with a clear rationale
2. Approved by the architecture team
3. Limited in scope
4. Scheduled for remediation

## References

- [Transaction Management Guide](./943-TRANSACTION-PATTERNS-REFERENCE.md)
- [Session Management Guide](./942-DATABASE-CONNECTION-AUDIT-PLAN.md)
- [Authentication Boundary Documentation](./924-AUTHENTICATION-STANDARDIZATION.md)
- [UUID Standardization Guide](./953-JOB-ID-STANDARDIZATION-2025-03-25.md)
- [Connection Pooling Guide](./944-DATABASE-CONNECTION-ENFORCEMENT-RECOMMENDATIONS.md)
