# Document 36: Domain Manager Implementation Plan

## Executive Summary

This document outlines the implementation plan for creating a modernized `domain_manager.py` router, which is identified as the next high-priority component in the ScraperSky modernization project following the successful modernization of `sitemap_scraper.py`. The domain manager will provide comprehensive CRUD operations for domain entities, supporting the core functionality of the ScraperSky platform.

## 1. Current State Assessment

According to the Route-Service Usage Matrix (Document 23), `domain_manager.py` currently:

1. Is identified as a router that handles `/api/v1/domains` path pattern for Domain CRUD operations
2. Uses a mix of modern and legacy service patterns
3. Contains medium-level direct database operations (5-10 instances)
4. Uses SQL queries and SQLAlchemy directly
5. Has dependencies on several services:
   - Core services: auth_service, user_context_service, db_service, error_service, validation_service (all legacy)
   - Domain services: domain_service (modern), job_service (mixed)
   - Process services: batch_processor_service (mixed)
   - API services: api_service, webhook_service, notification_service (all legacy)

However, the current file appears to be missing from the codebase, representing an opportunity to implement it from scratch using modern patterns rather than refactoring an existing implementation.

## 2. Implementation Goals

The modernized `domain_manager.py` will:

1. **Provide Full Domain CRUD Operations**: Create, read, update, and delete operations for domain entities
2. **Use Pure SQLAlchemy ORM**: No direct SQL operations, using SQLAlchemy models and queries
3. **Implement Modern Service Patterns**: Consistent with patterns established in `sitemap_scraper.py`
4. **Support API Versioning**: Structure to accommodate future v2 API integration
5. **Standardize Error Handling**: Use consistent error_service patterns
6. **Include Comprehensive Validation**: Leverage the modernized validation_service
7. **Implement Modern Authentication**: Use updated auth_service patterns

## 3. Domain Manager Router Endpoints

The following endpoints will be implemented:

| Method | Endpoint                             | Description                      | Request Body             | Response Model            |
| ------ | ------------------------------------ | -------------------------------- | ------------------------ | ------------------------- |
| GET    | `/api/v1/domains`                    | List all domains with pagination | Query parameters         | DomainListResponse        |
| GET    | `/api/v1/domains/{id}`               | Get a specific domain by ID      | Path parameter           | DomainDetailResponse      |
| POST   | `/api/v1/domains`                    | Create a new domain              | DomainCreateRequest      | DomainCreateResponse      |
| PUT    | `/api/v1/domains/{id}`               | Update an existing domain        | DomainUpdateRequest      | DomainUpdateResponse      |
| DELETE | `/api/v1/domains/{id}`               | Delete a domain                  | Path parameter           | DomainDeleteResponse      |
| GET    | `/api/v1/domains/search`             | Search domains by criteria       | Query parameters         | DomainListResponse        |
| POST   | `/api/v1/domains/validate`           | Validate a domain                | DomainValidateRequest    | DomainValidateResponse    |
| POST   | `/api/v1/domains/batch`              | Create multiple domains          | DomainBatchCreateRequest | DomainBatchCreateResponse |
| GET    | `/api/v1/domains/tenant/{tenant_id}` | Get domains by tenant            | Path parameter           | DomainListResponse        |

## 4. Required Models and Schemas

### 4.1 SQLAlchemy Models

Ensure that a `Domain` model exists with the following attributes:

```python
# Existing or to be created in src/models/domain.py
class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    normalized_name = Column(String(255), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="domains")
    jobs = relationship("Job", back_populates="domain")
    scans = relationship("Scan", back_populates="domain")
```

### 4.2 Pydantic Schemas

Define the following Pydantic schemas for request/response models:

```python
# To be created in src/schemas/domain.py
class DomainBase(BaseModel):
    name: str
    tenant_id: UUID

class DomainCreate(DomainBase):
    status: str = "active"
    metadata: Optional[Dict[str, Any]] = None

class DomainUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DomainInDB(DomainBase):
    id: int
    normalized_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class DomainListResponse(BaseModel):
    domains: List[DomainInDB]
    total: int
    page: int
    page_size: int

class DomainDetailResponse(BaseModel):
    domain: DomainInDB

class DomainCreateResponse(BaseModel):
    domain: DomainInDB
    message: str = "Domain created successfully"

class DomainUpdateResponse(BaseModel):
    domain: DomainInDB
    message: str = "Domain updated successfully"

class DomainDeleteResponse(BaseModel):
    id: int
    message: str = "Domain deleted successfully"

class DomainValidateRequest(BaseModel):
    name: str

class DomainValidateResponse(BaseModel):
    is_valid: bool
    message: str
    normalized_name: Optional[str] = None

class DomainBatchCreateRequest(BaseModel):
    domains: List[DomainCreate]

class DomainBatchCreateResponse(BaseModel):
    successful: List[DomainInDB]
    failed: List[Dict[str, Any]]
    message: str
```

## 5. Implementation Structure

The implementation will follow this structure:

### 5.1 Router Factory Implementation

```python
# In src/routers/domain_manager.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
# Import schemas and models
# Import services

# Create router using factory pattern or directly
router = APIRouter(
    prefix="/api/v1/domains",
    tags=["domains"],
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)

# Register in __init__.py
# from .domain_manager import router as domain_manager_router
# Add to routers list: domain_manager_router
```

### 5.2 Endpoint Implementations

Each endpoint will follow the pattern established in `sitemap_scraper.py`:

```python
@router.get("", response_model=DomainListResponse)
async def list_domains(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """List domains with pagination and optional filtering."""
    try:
        # Authorization check
        if not auth_service.can_access_resource(current_user, "domains", "read"):
            raise HTTPException(status_code=403, detail="Not authorized to access domains")

        # Get domains using domain_service
        domains, total = await domain_service.get_domains(
            session,
            page=page,
            page_size=page_size,
            status=status
        )

        return DomainListResponse(
            domains=domains,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error listing domains: {str(e)}")
        error_details = error_service.handle_exception(e, "list_domains_error")
        raise HTTPException(status_code=500, detail=error_details)
```

Similar patterns will be followed for all endpoints.

### 5.3 Domain Service Implementation

If not already existing, a domain service will be implemented:

```python
# In src/services/domain/domain_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Tuple, List, Optional, Dict, Any
from ...models.domain import Domain

class DomainService:
    async def get_domains(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        status: Optional[str] = None
    ) -> Tuple[List[Domain], int]:
        """Get domains with pagination and optional filtering."""
        query = select(Domain)

        # Apply filters
        if status:
            query = query.where(Domain.status == status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query)

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await session.execute(query)
        domains = result.scalars().all()

        return domains, total

    # Additional methods for CRUD operations
```

## 6. Integration With Services

### 6.1 Service Dependencies

The following service dependencies will be managed:

1. **domain_service**: For domain operations (create, read, update, delete)
2. **validation_service**: For domain validation and normalization
3. **auth_service**: For authentication and authorization
4. **error_service**: For standardized error handling
5. **job_service**: For job creation and management (if needed)
6. **batch_processor_service**: For batch operations (if needed)

### 6.2 Background Tasks

For long-running operations, background tasks will be used:

```python
@router.post("/batch", response_model=DomainBatchCreateResponse)
async def create_domains_batch(
    request: DomainBatchCreateRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create multiple domains in a batch operation."""
    try:
        # Validation and processing logic

        # Add background task for processing
        background_tasks.add_task(
            batch_processor_service.process_domain_batch,
            domains=request.domains,
            user_id=current_user.id
        )

        return DomainBatchCreateResponse(
            successful=[],  # Initial response
            failed=[],
            message="Batch domain creation started"
        )
    except Exception as e:
        # Error handling
```

## 7. Error Handling and Validation

### 7.1 Error Handling Pattern

All endpoints will follow the standardized error handling pattern:

```python
try:
    # Operation logic
except ValueError as ve:
    logger.error(f"Validation error: {str(ve)}")
    error_details = error_service.handle_exception(
        ve,
        "domain_validation_error"
    )
    raise HTTPException(status_code=400, detail=error_details)
except Exception as e:
    logger.error(f"Error: {str(e)}")
    logger.error(traceback.format_exc())
    error_details = error_service.handle_exception(
        e,
        "domain_processing_error"
    )
    raise HTTPException(status_code=500, detail=error_details)
```

### 7.2 Validation Pattern

Domain validation will use the modernized validation_service:

```python
@router.post("/validate", response_model=DomainValidateResponse)
async def validate_domain(
    request: DomainValidateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Validate a domain name."""
    try:
        # Use validation_service with triple return pattern
        is_valid, message, normalized_domain = validation_service.validate_domain(request.name)

        return DomainValidateResponse(
            is_valid=is_valid,
            message=message,
            normalized_name=normalized_domain
        )
    except Exception as e:
        # Error handling
```

## 8. Testing Strategy

A comprehensive testing strategy will be implemented:

### 8.1 Unit Tests

Create unit tests for:

- Domain service methods
- Validation logic
- Error handling

### 8.2 Integration Tests

Create integration tests for:

- API endpoints
- Service interactions
- Database operations

### 8.3 End-to-End Tests

Create a `test_domain_endpoints.py` script similar to the `test_endpoints.py` created for sitemap_scraper.py:

```python
#!/usr/bin/env python3
import argparse
import requests
import json
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_DOMAIN = "example.com"
TEST_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

def test_create_domain():
    """Test domain creation endpoint."""
    url = f"{BASE_URL}/domains"
    payload = {
        "name": TEST_DOMAIN,
        "tenant_id": TEST_TENANT_ID,
        "status": "active",
        "metadata": {"source": "test_script"}
    }

    logger.info(f"Testing domain creation with {TEST_DOMAIN}")
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        logger.info(f"Domain created successfully: {response.json()}")
        return response.json()["domain"]["id"]
    else:
        logger.error(f"Failed to create domain: {response.status_code} - {response.text}")
        return None

# Additional test functions for other endpoints
```

## 9. Implementation Timeline

The implementation will follow a 2-week timeline as outlined in Document 35:

### Week 1: Analysis and Service Updates

- Day 1: Setup project structure, define schemas and models
- Day 2-3: Implement domain_service if not already existing
- Day 4-5: Implement core endpoint functionality

### Week 2: SQL to ORM Migration and Testing

- Day 1-2: Implement remaining endpoints and background tasks
- Day 3-4: Create comprehensive tests
- Day 5: Documentation and final review

## 10. Implementation Approach

The implementation will follow these steps:

1. **Initial Setup**:

   - Create necessary directory structure
   - Define Pydantic schemas
   - Ensure SQLAlchemy models are in place

2. **Core Implementation**:

   - Implement the domain_service (if not existing)
   - Create the main router with factory pattern
   - Implement core CRUD endpoints

3. **Advanced Features**:

   - Add search functionality
   - Implement batch operations
   - Add validation endpoints

4. **Testing and Documentation**:

   - Create unit and integration tests
   - Create end-to-end test script
   - Document endpoints and usage

5. **Integration**:
   - Register the router in the application
   - Verify all dependencies are correctly handled
   - Test in the full application context

## 11. Appendix A: Sample API Requests

### Create Domain

```bash
curl -X POST "http://localhost:8000/api/v1/domains" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {token}" \
     -d '{
       "name": "example.com",
       "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
       "status": "active",
       "metadata": {"source": "api"}
     }'
```

### Get Domain

```bash
curl -X GET "http://localhost:8000/api/v1/domains/1" \
     -H "Authorization: Bearer {token}"
```

### List Domains

```bash
curl -X GET "http://localhost:8000/api/v1/domains?page=1&page_size=50" \
     -H "Authorization: Bearer {token}"
```

### Update Domain

```bash
curl -X PUT "http://localhost:8000/api/v1/domains/1" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {token}" \
     -d '{
       "status": "inactive",
       "metadata": {"reason": "testing"}
     }'
```

### Delete Domain

```bash
curl -X DELETE "http://localhost:8000/api/v1/domains/1" \
     -H "Authorization: Bearer {token}"
```

### Validate Domain

```bash
curl -X POST "http://localhost:8000/api/v1/domains/validate" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {token}" \
     -d '{
       "name": "example.com"
     }'
```
