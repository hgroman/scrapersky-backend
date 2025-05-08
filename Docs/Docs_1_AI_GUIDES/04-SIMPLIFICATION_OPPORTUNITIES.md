# SIMPLIFICATION OPPORTUNITIES

This document outlines practical opportunities to simplify the ScraperSky codebase without major rewrites. These changes can be implemented incrementally to reduce complexity and increase consistency.

## 1. STANDARDIZED DATABASE REPOSITORIES

### Current Issue

The codebase has inconsistent patterns for database operations:
- Some modules use direct SQLAlchemy ORM
- Some use raw SQL via db_service
- Some mix approaches
- Helper methods vary across models

### Proposed Simplification

Create a standardized `Repository` pattern for each model:

```python
# Example implementation for SitemapRepository
class SitemapRepository:
    """Handles all database operations for Sitemap models."""

    @staticmethod
    async def create_sitemap(
        session: AsyncSession,
        domain_id: str,
        url: str,
        sitemap_type: str,
        tenant_id: str,
        **kwargs
    ) -> SitemapFile:
        """Create a new sitemap file record."""
        return await SitemapFile.create_new(
            session=session,
            domain_id=domain_id,
            url=url,
            sitemap_type=sitemap_type,
            tenant_id=tenant_id,
            **kwargs
        )

    @staticmethod
    async def find_by_id(
        session: AsyncSession,
        sitemap_id: str,
        tenant_id: str
    ) -> Optional[SitemapFile]:
        """Find a sitemap by ID with tenant isolation."""
        return await SitemapFile.get_by_id(
            session=session,
            sitemap_id=sitemap_id,
            tenant_id=tenant_id
        )

    @staticmethod
    async def find_by_domain(
        session: AsyncSession,
        domain_id: str,
        tenant_id: str
    ) -> List[SitemapFile]:
        """Find all sitemaps for a domain."""
        return await SitemapFile.get_by_domain_id(
            session=session,
            domain_id=domain_id,
            tenant_id=tenant_id
        )

    # Additional methods as needed...
```

### Implementation Steps

1. Create a repository for each primary model
2. Refactor services to use repositories instead of direct model calls
3. Standardize method names and parameters across repositories
4. Add transaction awareness to all repository methods

### Benefits

- Consistent database access pattern
- Easier to understand and maintain
- Centralized tenant isolation enforcement
- Cleaner service code focused on business logic
- Easier testing with potential repository mocking

## 2. STANDARDIZED API ENDPOINT STRUCTURE

### Current Issue

API endpoints have inconsistent structure:
- Transaction management varies
- Error handling approaches differ
- Background task timing varies
- Documentation is inconsistent

### Proposed Simplification

Create a standardized endpoint structure:

```python
@router.post("/resource", response_model=ResponseModel, status_code=201)
async def create_resource(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(validate_tenant)
):
    """
    Create a new resource.

    Args:
        request: The resource creation request
        background_tasks: FastAPI background tasks
        session: Database session
        current_user: Authenticated user information
        tenant_id: Validated tenant ID

    Returns:
        The created resource

    Raises:
        HTTPException: If resource creation fails
    """
    try:
        # Transaction boundary
        async with session.begin():
            # Service call
            result = await resource_service.create_resource(
                session=session,
                data=request,
                tenant_id=tenant_id,
                user_id=current_user["id"]
            )

        # Background tasks after transaction
        background_tasks.add_task(
            resource_service.process_resource_background,
            resource_id=result.id,
            tenant_id=tenant_id
        )

        # Return response
        return ResponseModel.from_orm(result)

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        # Handle permission errors
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Error creating resource: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Implementation Steps

1. Create an endpoint template in a utilities module
2. Gradually refactor existing endpoints to follow the template
3. Standardize error handling across all endpoints
4. Ensure consistent transaction management

### Benefits

- Consistent API behavior
- Predictable error handling
- Proper transaction management
- Clear separation of concerns
- Easier maintenance and understanding

## 3. SERVICE LAYER STREAMLINING

### Current Issue

Services have inconsistent patterns:
- Some have combined responsibilities
- Some create their own sessions
- Error handling varies
- Background task management differs

### Proposed Simplification

Split services into focused components:

```
QueryService: Responsible for read operations
CommandService: Responsible for write operations
BackgroundService: Responsible for background tasks
```

Example implementation:

```python
class SitemapQueryService:
    """Handles read operations for sitemap data."""

    async def get_sitemap(self, session: AsyncSession, sitemap_id: str, tenant_id: str):
        """Get a sitemap by ID."""
        return await sitemap_repository.find_by_id(session, sitemap_id, tenant_id)

    async def list_sitemaps(self, session: AsyncSession, domain_id: str, tenant_id: str):
        """List all sitemaps for a domain."""
        return await sitemap_repository.find_by_domain(session, domain_id, tenant_id)

class SitemapCommandService:
    """Handles write operations for sitemap data."""

    async def create_sitemap(self, session: AsyncSession, data: dict, tenant_id: str):
        """Create a new sitemap."""
        # Validation
        if not data.get("url"):
            raise ValueError("URL is required")

        # Domain business logic

        # Persistence
        return await sitemap_repository.create_sitemap(
            session=session,
            **data,
            tenant_id=tenant_id
        )

class SitemapBackgroundService:
    """Handles background tasks for sitemap processing."""

    async def process_domain(self, domain_id: str, tenant_id: str):
        """Process a domain in the background."""
        # Create session specifically for background task
        async with async_session_factory() as session:
            async with session.begin():
                # Implementation...
```

### Implementation Steps

1. Identify logical service boundaries
2. Split existing services into query/command/background components
3. Ensure consistent transaction handling in each component
4. Update routers to use the appropriate service components

### Benefits

- Single responsibility principle
- Clearer transaction management
- Easier testing and mocking
- More focused code
- Reduced complexity

## 4. SIMPLIFIED ERROR HANDLING

### Current Issue

Error handling is inconsistent:
- Some errors are caught and transformed
- Some are allowed to propagate
- Logging varies
- Response formats differ

### Proposed Simplification

Create a centralized error handling system:

```python
class AppError(Exception):
    """Base class for application errors."""
    status_code = 500
    error_code = "INTERNAL_ERROR"

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(AppError):
    """Validation error."""
    status_code = 400
    error_code = "VALIDATION_ERROR"

class ResourceNotFoundError(AppError):
    """Resource not found error."""
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"

class PermissionDeniedError(AppError):
    """Permission denied error."""
    status_code = 403
    error_code = "PERMISSION_DENIED"

# FastAPI exception handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Handle application errors."""
    logger.error(
        f"AppError: {exc.error_code} - {exc.message}",
        extra={"details": exc.details}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )
```

### Implementation Steps

1. Create a central exceptions module
2. Define structured exception classes
3. Add exception handlers to FastAPI app
4. Replace generic exceptions with structured ones
5. Standardize logging

### Benefits

- Consistent error handling
- Structured error responses
- Better error traceability
- Improved error logging
- Clearer client error messages

## 5. BACKGROUND TASK STANDARDIZATION

### Current Issue

Background tasks have inconsistent implementations:
- Session management varies
- Error handling differs
- State tracking is inconsistent
- Recovery mechanisms vary

### Proposed Simplification

Create a background task wrapper:

```python
async def run_background_task(
    task_func: Callable,
    task_id: str,
    *args,
    **kwargs
):
    """
    Standard wrapper for background tasks that handles session,
    transactions, error recovery, and state tracking.
    """
    # Initialize state tracking
    task_tracker.set_state(task_id, "running")

    # Create dedicated session
    session = async_session_factory()
    try:
        # Start transaction
        async with session.begin():
            # Run the actual task
            result = await task_func(session, *args, **kwargs)

            # Update success state
            task_tracker.set_state(task_id, "completed", result=result)
            return result

    except Exception as e:
        # Log error
        logger.error(f"Background task {task_id} failed: {str(e)}")

        # Update error state
        task_tracker.set_state(task_id, "failed", error=str(e))

        # Error recovery with separate session
        try:
            async with async_session_factory() as error_session:
                async with error_session.begin():
                    # Update task status in database
                    await task_repository.update_status(
                        session=error_session,
                        task_id=task_id,
                        status="failed",
                        error=str(e)
                    )
        except Exception as recovery_error:
            logger.error(f"Error recovery failed: {str(recovery_error)}")
    finally:
        # Ensure session is closed
        await session.close()
```

### Implementation Steps

1. Create the background task wrapper
2. Create a centralized task tracker
3. Refactor existing background tasks to use the wrapper
4. Standardize error recovery approaches

### Benefits

- Consistent transaction management
- Standardized error handling
- Reliable session cleanup
- Consistent state tracking
- Improved reliability and monitoring

## 6. MODULE CONSOLIDATION

### Current Issue

Related functionality is spread across multiple files:
- Similar modules with slight variations
- Duplicated code
- Inconsistent implementations
- Difficult to maintain consistency

### Proposed Simplification

Consolidate related modules:

```
Before:
- sitemap_service.py
- sitemap_analyzer.py
- sitemap_processor.py

After:
- sitemap/
  - __init__.py (exports all components)
  - query_service.py (read operations)
  - command_service.py (write operations)
  - background_service.py (background tasks)
  - analyzer.py (domain logic)
```

### Implementation Steps

1. Identify related modules
2. Create subdirectories for related functionality
3. Split by responsibility (query/command/background)
4. Update imports throughout the codebase
5. Remove duplication

### Benefits

- Better organization
- Reduced duplication
- Clearer responsibilities
- Easier to maintain consistency
- Better discoverability
