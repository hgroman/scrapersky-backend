# CORE ARCHITECTURAL PRINCIPLES

This document outlines the core architectural principles that should guide all development in the ScraperSky Backend. These principles have been extracted from our recent consolidation and standardization efforts across the entire codebase.

## 1. API STANDARDIZATION

- **All APIs use /api/v3/ prefix** - No legacy endpoints are supported
- **Consistent resource naming** - Hyphenated resource names in URLs
- **Standardized response formats** - Consistent structure for success/error responses
- **Proper status endpoints** - All asynchronous operations have status endpoints
- **Standardized error handling** - Use FastAPI's built-in error handling

## 2. CONNECTION MANAGEMENT

- **ALWAYS use Supavisor connection pooling** - Never use direct connections
- **STRICTLY PROHIBITED: Any use of PgBouncer** - PgBouncer is incompatible with our architecture
- **Connection pooler parameters are MANDATORY** - `raw_sql=true`, `no_prepare=true`, and `statement_cache_size=0`
- **Run compliance scripts regularly** - Use `bin/run_supavisor_check.sh` to verify compliance
- **Sessions should not be shared** across asynchronous contexts
- **Connection strings must follow Supavisor format** - See 07-DATABASE_CONNECTION_STANDARDS.md

## 3. TRANSACTION BOUNDARIES

- **Routers OWN transactions** - They begin, commit, and rollback transactions
- **Services are transaction-AWARE** - They work within existing transactions but don't manage them
- **Background jobs manage their OWN sessions/transactions** - They create sessions for their complete lifecycle
- **Never nest transactions** - This causes "transaction already begun" errors

## 4. UUID STANDARDIZATION

- **All IDs must be proper UUIDs** - No prefixes or custom formats
- **Use PostgreSQL UUID type** in database schema
- **Handle type conversion gracefully** - Convert strings to UUIDs as needed
- **Use PGUUID SQLAlchemy type** for UUID columns

## 5. AUTHENTICATION BOUNDARY

- **JWT authentication happens ONLY at API gateway/router level** - This is a STRICT boundary
- **Database operations must NEVER handle JWT authentication or verification**
- **Services must be authentication-agnostic** - They should receive user IDs, not tokens
- **Use only JWT for authentication** - RBAC and tenant isolation have been removed

## 6. ERROR HANDLING

- **Use FastAPI's built-in error handling** - No custom error service
- **Provide detailed error messages** - Include error type and description
- **Log errors with context** - Include job IDs, domain information, etc.
- **Handle database errors gracefully** - Use try/except blocks around database operations
- **Validate inputs before processing** - Check for required fields, valid formats, etc.

## 7. BACKGROUND TASK PATTERN

- **Create dedicated sessions** for background tasks
- **Handle errors properly** with separate error sessions
- **Always ensure session closure** in finally blocks
- **Use the job tracking pattern** for long-running operations
- **Add background tasks AFTER transaction commits**

## 8. CODE ORGANIZATION

- **Services should have a single responsibility**
- **Routers should be thin** - Business logic belongs in services
- **Models should match database schema** - Use alembic for migrations
- **Documentation should be current** - Update docs when code changes

## 9. EXEMPLAR IMPLEMENTATIONS

When implementing new features, refer to these exemplar implementations:

- **Google Maps API** - The gold standard for proper implementation
- **Modernized Sitemap** - Follows best practices for background processing
- **Batch Page Scraper** - Shows proper job tracking implementation

## 10. DEVELOPMENT WORKFLOW

- **Work from a clear specification**
- **Document changes** in project-docs
- **Update AI_GUIDES** when architectural decisions are made
- **Test thoroughly** before considering work complete

## IMPLEMENTATION GUIDANCE

### API Implementation Pattern

```python
# Router definition
router = APIRouter(
    prefix="/api/v3/resource-name",
    tags=["Resource Name"],
)

# Endpoint definition
@router.post("/action", response_model=ResponseModel)
async def action(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)  # JWT auth only
):
    # Validate request
    if not request.field:
        raise HTTPException(status_code=400, detail="Field is required")

    # Transaction boundary - router owns transactions
    async with session.begin():
        # Call service
        result = await service.perform_action(
            session=session,
            data=request.dict(),
            user_id=current_user["id"]  # Pass user ID, not token
        )

    # Add background tasks AFTER transaction commits
    background_tasks.add_task(
        service.background_process,
        job_id=str(result.id)
    )

    # Return standard response
    return {
        "job_id": str(result.id),
        "status": "pending",
        "status_url": f"/api/v3/resource-name/status/{result.id}"
    }
```

### Service Implementation Pattern

```python
# Service implementation - transaction aware, not managing
async def perform_action(
    session: AsyncSession,
    data: dict,
    user_id: str
) -> Entity:
    # Create entity
    entity = Entity(
        id=uuid.uuid4(),  # Standard UUID
        name=data["name"],
        created_by=user_id
    )

    # Use session but don't manage transactions
    session.add(entity)
    await session.flush()  # Flush without commit

    return entity
```

### Background Task Implementation Pattern

```python
# Background task - creates and manages own session
async def background_process(job_id: str):
    # Create dedicated session
    session = async_session_factory()
    try:
        # Manage own transaction
        async with session.begin():
            # Get job
            job = await get_job_by_id(session, uuid.UUID(job_id))
            # Update status
            job.status = "processing"

        # Process in separate transaction
        try:
            async with session.begin():
                # Processing logic
                # ...

            # Update status on success
            async with session.begin():
                job = await get_job_by_id(session, uuid.UUID(job_id))
                job.status = "completed"

        except Exception as processing_error:
            logger.error(f"Processing error: {str(processing_error)}")
            # Update status on error - separate transaction
            async with session.begin():
                job = await get_job_by_id(session, uuid.UUID(job_id))
                job.status = "failed"
                job.error = str(processing_error)

    finally:
        # Always close session
        await session.close()
```

---

By following these principles, we ensure that the codebase remains maintainable, scalable, and reliable as we continue to develop new features and fix issues.
