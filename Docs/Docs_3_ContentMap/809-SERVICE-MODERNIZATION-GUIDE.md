# ScraperSky Service Architecture Modernization Guide

## Overview

This guide outlines the process of modernizing ScraperSky backend components by separating concerns and leveraging a service-oriented architecture. The key principles of this architecture are:

- **Separation of concerns**: Each service has a focused responsibility
- **Standardized interfaces**: Consistent APIs across all services
- **Error handling**: Centralized, consistent error management
- **Resource management**: Better memory and connection handling
- **Testability**: Easier unit testing with clear dependencies
- **Reusability**: Common functionality extracted into shared services

## Core Architecture

The service architecture separates database operations from router logic. Instead of embedding database queries directly in route handlers, we use dedicated services:

```
┌───────────────────────────────────────────────────────────────────────┐
│                          API Layer (FastAPI)                           │
└───────────────────┬───────────────────┬───────────────────────────────┘
                    │                   │
┌───────────────────▼───┐   ┌───────────▼───────────┐   ┌───────────────┐
│    Core Services      │   │  Business Services    │   │Infrastructure  │
│                       │   │                       │   │   Services     │
│ ┌─────────┐ ┌────────┐│   │ ┌──────────┐ ┌──────┐ │   │ ┌─────────────┐│
│ │Auth     │ │DB      ││   │ │Scraping  │ │RBAC  │ │   │ │Logging      ││
│ │Service  │ │Service ││   │ │Service   │ │Service│ │   │ │Service      ││
│ └─────────┘ └────────┘│   │ └──────────┘ └──────┘ │   │ └─────────────┘│
└───────────────────────┘   └───────────────────────┘   └───────────────┘
```

## Core Services

### 1. Database Service (`db_service`)

The Database Service provides standardized database access patterns:

```python
from ..services.db_service import db_service

# Fetch a single record
record = await db_service.fetch_one(
    "SELECT * FROM table WHERE id = %(id)s AND tenant_id = %(tenant_id)s",
    {"id": record_id, "tenant_id": tenant_id}
)

# Fetch multiple records
records = await db_service.fetch_all(
    "SELECT * FROM table WHERE tenant_id = %(tenant_id)s",
    {"tenant_id": tenant_id}
)

# Execute a query (INSERT, UPDATE, DELETE)
await db_service.execute(
    "UPDATE table SET status = %(status)s WHERE id = %(id)s AND tenant_id = %(tenant_id)s",
    {"status": "complete", "id": record_id, "tenant_id": tenant_id}
)
```

### 2. Authentication Service (`auth_service`)

Handles authentication, authorization, and tenant isolation:

```python
from ..services.auth_service import auth_service

# Get current authenticated user
@router.get("/endpoint")
async def endpoint(current_user: dict = Depends(auth_service.get_current_user)):
    # Route implementation

# Validate tenant ID
tenant_id = auth_service.validate_tenant_id(request.tenant_id, current_user)
```

### 3. Error Service (`error_service`)

Provides consistent error handling:

```python
from ..services.error_service import error_service

# Apply to router
router = APIRouter()
router = error_service.route_error_handler(router)

# OR apply to specific function (not both!)
@error_service.async_exception_handler
async def function_name():
    # Implementation
```

### 4. Job Service (`job_service`)

Manages background job tracking and status updates:

```python
from ..services.job_service import job_service

# Create a new job
job_id = job_service.create_job("resource_prefix", initial_status)

# Update job status
job_service.update_job_status(job_id, {"progress": 0.5})

# Save to database
await job_service.save_job_to_database(job_id, tenant_id)
```

## Modernization Process

### 1. Assessment Phase

Analyze existing code to identify:
- Functional areas and responsibilities
- Repeated patterns and code duplication
- Error handling approaches
- Resource management patterns
- Service opportunities

### 2. Service Mapping Phase

Map functionality to available services:

| Functionality           | Service to Use        | Benefits                                      |
| ----------------------- | --------------------- | --------------------------------------------- |
| Input validation        | `validation_service`  | Standardized validation, consistent errors    |
| Database operations     | `db_service`          | Connection pooling, query standardization     |
| Job tracking            | `job_manager_service` | Reliable status tracking, persistence         |
| Error handling          | `error_service`       | Consistent error responses, centralized logs  |

### 3. Implementation Phase

1. **Import services**: Start by importing all required services
2. **Apply router-level error handling**: For consistent error responses
3. **Modernize validation**: Replace ad-hoc validation with validation_service
4. **Upgrade database operations**: Use db_service for all database operations
5. **Enhance job tracking**: Implement job_manager_service for background tasks
6. **Clean up**: Remove unused imports, variables, and functions

## Standard Implementation Pattern

```python
"""
Module docstring explaining purpose and functionality.
"""
# Imports - group by functionality
from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional

# Import models
from ..models import RequestModel, ResponseModel

# Import services
from ..services import (
    # Core services
    auth_service, db_service,
    # Enhanced services
    error_service, validation_service, job_manager_service
)

# Initialize router with error handling
router = APIRouter(prefix="/api/path", tags=["tag"])
router = error_service.route_error_handler(router)

# Endpoints
@router.post("/endpoint", response_model=ResponseModel)
async def endpoint(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """Docstring explaining endpoint purpose."""
    # Validate input using validation_service
    is_valid, message = validation_service.validate_string_length(
        request.field, min_length=2, max_length=100
    )
    if not is_valid:
        raise ValueError(message)  # Automatically converted to HTTP 400

    # Validate tenant ID
    tenant_id = auth_service.validate_tenant_id(request.tenant_id, current_user)

    # Create job using job_manager_service
    job_id = await job_manager_service.create_job(
        "job_type", tenant_id, current_user.get("user_id"),
        {"initial": "data"}
    )

    # Start background task
    background_tasks.add_task(
        process_task, job_id, request, tenant_id, current_user
    )

    # Return response
    return ResponseModel(
        job_id=job_id,
        status="started",
        status_url=f"/api/path/status/{job_id}"
    )

# Background processing function
@error_service.async_exception_handler
async def process_task(job_id, request, tenant_id, current_user):
    try:
        # Update job status
        await job_manager_service.update_job_status(
            job_id, status="running", message="Starting task"
        )

        # Database operation using db_service
        results = await db_service.fetch_all(
            "SELECT * FROM table WHERE tenant_id = %(tenant_id)s",
            {"tenant_id": tenant_id}
        )

        # Process results
        processed_data = [process_item(item) for item in results]

        # Store results using db_service
        for item in processed_data:
            await db_service.execute(
                """
                INSERT INTO results_table (id, data, tenant_id, created_by)
                VALUES (%(id)s, %(data)s, %(tenant_id)s, %(user_id)s)
                """,
                {
                    "id": str(uuid.uuid4()),
                    "data": item,
                    "tenant_id": tenant_id,
                    "user_id": current_user.get("user_id")
                }
            )

        # Complete job
        await job_manager_service.update_job_status(
            job_id, status="complete", progress=1.0,
            result_data={"count": len(processed_data)},
            message="Task completed"
        )

        # Save job to database
        await job_manager_service.save_job_to_database(job_id, tenant_id)

    except Exception as e:
        # Log error
        error_service.log_exception(
            e, "process_task",
            context={"job_id": job_id, "tenant_id": tenant_id}
        )

        # Update job status
        await job_manager_service.update_job_status(
            job_id, status="failed", error=str(e),
            message="Task failed"
        )

        # Save failed job to database
        await job_manager_service.save_job_to_database(job_id, tenant_id)

        # Re-raise for error handling
        raise
```

## Key Benefits

Before modernization:
```python
@router.post("/endpoint")
async def endpoint(request: RequestModel):
    try:
        # Manual validation
        if not request.field or len(request.field) < 2:
            raise HTTPException(status_code=400, detail="Invalid field")

        # Direct database connection
        conn = await get_db_connection()

        # Generate job ID
        job_id = f"prefix_{uuid.uuid4().hex}"
        _job_statuses[job_id] = {"status": "pending"}

        # Start background task
        background_tasks.add_task(process_task, job_id)

        return {"job_id": job_id}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error")
```

After modernization:
```python
@router.post("/endpoint")
async def endpoint(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(auth_service.get_current_user)
):
    # Validate input
    is_valid, message = validation_service.validate_string_length(request.field)
    if not is_valid:
        raise ValueError(message)

    # Create job
    job_id = await job_manager_service.create_job("job_type", tenant_id, user_id)

    # Start background task
    background_tasks.add_task(process_task, job_id, request)

    return {"job_id": job_id, "status": "started"}
```

## Evolution to SQLAlchemy (Future Direction)

The service architecture is evolving from raw SQL queries to SQLAlchemy ORM:

```python
# Import SQLAlchemy services
from ..services.domain_service import domain_service
from ..services.job_service import job_service

@router.post("/endpoint")
async def endpoint(request: RequestModel):
    # Create domain using SQLAlchemy service
    domain = await domain_service.create({
        "domain": request.domain,
        "tenant_id": tenant_id,
        "created_by": user_id
    })

    # Create job using SQLAlchemy service
    job = await job_service.create({
        "job_type": "domain_scan",
        "domain_id": domain.id,
        "tenant_id": tenant_id,
        "status": "pending"
    })

    # Start background task
    background_tasks.add_task(process_task, str(job.id), str(domain.id))

    return {
        "job_id": str(job.id),
        "domain_id": str(domain.id),
        "status": "pending"
    }
```

## Best Practices

1. **Service Injection**: Import services at the module level for clean function signatures
2. **Decorators First**: Apply error handling decorators before other functionality
3. **Parameter Validation**: Validate all inputs before processing begins
4. **Error Bubbling**: Let errors propagate for automatic handling when appropriate
5. **Context Logging**: Include relevant context when logging errors
6. **Tenant Isolation**: Always validate tenant ID before database operations
7. **Progress Updates**: Update job status at meaningful progress points

## Common Pitfalls to Avoid

1. **Don't use double error handling**: Choose either router-level OR endpoint-level error handling, not both
2. **Don't embed raw SQL**: Use the db_service for all database operations
3. **Don't use in-memory job status**: Use job_manager_service for persistence
4. **Don't skip tenant isolation**: Always include tenant_id in database operations
5. **Don't ignore validations**: Validate all inputs before processing
