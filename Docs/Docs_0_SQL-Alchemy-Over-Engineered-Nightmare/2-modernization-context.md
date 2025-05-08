# ScraperSky Modernization Context: The Journey and Pivot to SQLAlchemy

## Original Modernization Approach

We've been working on modernizing the ScraperSky backend, which originally consisted of several loosely-coupled scraper routes with inconsistent patterns for:
- Database access
- Error handling
- Authentication
- Job tracking
- Background processing

Our initial modernization approach was to standardize around a set of core services:

### Core Services
- **auth_service**: Authentication, authorization, and tenant isolation
- **db_service**: Database access with parameterized queries
- **error_service**: Consistent error handling and HTTP responses

### Extended Services
- **validation_service**: Input data validation
- **job_manager_service**: Background job tracking and status updates
- **batch_processor_service**: Controlled concurrency for batch operations
- **user_context_service**: User context and tenant handling

This approach generated significant documentation trying to standardize patterns around raw SQL queries, with complex patterns like:

```python
# Example of the complexity we were dealing with
@router.post("/endpoint")
@error_service.async_exception_handler
async def endpoint(request: RequestModel):
    try:
        # Validate tenant ID
        tenant_id = auth_service.validate_tenant_id(request.tenant_id, current_user)
        
        # Create job
        job_id = job_service.create_job("job_type", {"status": "pending"})
        
        # Execute query
        result = await db_service.fetch_all(
            "SELECT * FROM table WHERE tenant_id = %(tenant_id)s",
            {"tenant_id": tenant_id}
        )
        
        # Update job status
        job_service.update_job_status(job_id, {"status": "complete"})
        
        return {"data": result}
    except Exception as e:
        error_service.log_exception(e, "endpoint")
        raise
```

## The Pivot to SQLAlchemy

After reviewing the complexity of our homegrown solution, we realized using SQLAlchemy would:
1. **Simplify architecture** dramatically
2. **Reduce documentation** needs
3. **Leverage established patterns** instead of inventing our own
4. **Improve maintainability** with declarative models

SQLAlchemy will replace the raw SQL approach with a model-driven architecture:

```python
# The SQLAlchemy approach is much cleaner
@router.post("/endpoint")
async def endpoint(request: RequestModel):
    # Validate tenant ID (simplified)
    tenant_id = auth_service.validate_tenant_id(request.tenant_id, current_user)
    
    # Create job using SQLAlchemy
    job = await job_service.create({
        "job_type": "job_type",
        "tenant_id": tenant_id,
        "status": "pending"
    })
    
    # Query using SQLAlchemy
    results = await domain_service.get_all(tenant_id=tenant_id)
    
    # Update job using SQLAlchemy
    await job_service.update(job.id, {"status": "complete"})
    
    return {"data": results}
```

## The Current Plan

We're now implementing SQLAlchemy across the codebase with this approach:

1. **Start with sitemap_scraper.py** as our guinea pig
2. **Update core services** to work with SQLAlchemy as we go
3. **Use the patterns** from this first route to update remaining routes
4. **Eliminate complexity** rather than document it

## What You Might Encounter

As we work on this migration, you might see:

1. **Legacy raw SQL**: Still in some routes that haven't been migrated
2. **Complex service patterns**: From our previous approach
3. **Inconsistent error handling**: That will be standardized with SQLAlchemy
4. **In-memory state management**: Being replaced with proper database persistence
5. **Overly complex documentation**: That will be simplified or removed

## The Goal

By the end of this process, we'll have:

1. **SQLAlchemy models** for all our main entities
2. **Simplified services** built around these models
3. **Consistent patterns** across all routes
4. **Reduced complexity** in both code and documentation
5. **Better maintainability** with industry-standard patterns

This context should help you understand why we're making certain changes and the overall direction we're heading.
