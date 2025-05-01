# ScraperSky sitemap_scraper.py Refactoring Plan

This document outlines a detailed plan for refactoring the sitemap_scraper.py file to align with the ScraperSky modernization project goals, focusing on SQLAlchemy migration and service standardization.

## Current Issues

Based on the analysis in [Document 20](./20-Sitemap-Scraper-Service-Usage-Analysis.md), the sitemap_scraper.py file has several issues:

1. **Direct Database Operations**: Multiple instances of direct session operations that bypass service layers
2. **Raw SQL Queries**: Usage of raw SQL through db_service
3. **Inconsistent Service Usage**: Mix of modern SQLAlchemy services and legacy services
4. **Legacy In-Memory Job Tracking**: Some code still uses in-memory job tracking
5. **Large, Complex Functions**: Several functions exceed recommended length
6. **Inconsistent Error Handling**: Different patterns for error handling throughout the file

## Refactoring Goals

1. Eliminate all direct database operations by encapsulating them in service methods
2. Replace all raw SQL queries with SQLAlchemy ORM operations
3. Standardize service usage patterns
4. Remove legacy in-memory job tracking
5. Break down large functions into smaller, more focused functions
6. Standardize error handling using error_service

## Phase 1: Remove Direct Database Operations

### Task 1.1: Refactor Direct Session Operations

Current pattern:

```python
result = await session.execute(query)
job = result.scalar_one_or_none()
```

Target pattern:

```python
job = await job_service.get_by_id(session, job_id, tenant_id)
```

Specific changes required:

1. Identify all direct session operations in the file:

   - Line 184: `await session.commit()`
   - Line 311: `result = await session.execute(`
   - Line 465: `result = await session.execute(query)`
   - Line 481: `result = await session.execute(query)`
   - Line 607: `batch_job_result = await session.execute(batch_job_query)`
   - Line 687: `jobs_result = await session.execute(jobs_query)`
   - Line 1321: `domain_session.add(domain_job)`
   - Line 1349: `domain_session.add(domain_job)`
   - Line 1403: `domain_session.add(domain_job)`

2. For each operation, determine the appropriate service method to use:

   - `session.execute(query)` with Job model → job_service.get_by_id() or job_service.get_all()
   - `session.execute(batch_job_query)` → batch_processor_service.get_batch()
   - `domain_session.add(domain_job)` → domain_service.create() or domain_service.update()

3. If no appropriate service method exists, extend the relevant service class

### Task 1.2: Extend Service Methods as Needed

1. **job_service.py** - Add the following methods if not present:

   ```python
   async def get_with_domain(self, session, job_id, tenant_id=None):
       """Get a job with its related domain loaded"""
       query = select(Job).options(selectinload(Job.domain)).where(Job.id == job_id)
       if tenant_id:
           query = query.where(Job.tenant_id == tenant_id)
       result = await session.execute(query)
       return result.scalar_one_or_none()
   ```

2. **domain_service.py** - Add the following methods if not present:

   ```python
   async def add_job(self, session, domain_id, job_data):
       """Add a job to a domain"""
       domain = await self.get_by_id(session, domain_id)
       job = Job(**job_data)
       domain.jobs.append(job)
       return job
   ```

3. **batch_processor_service.py** - Add the following methods if not present:
   ```python
   async def get_batch_with_jobs(self, session, batch_id, tenant_id=None):
       """Get a batch with all its jobs loaded"""
       query = select(BatchJob).options(selectinload(BatchJob.jobs)).where(BatchJob.batch_id == batch_id)
       if tenant_id:
           query = query.where(BatchJob.tenant_id == tenant_id)
       result = await session.execute(query)
       return result.scalar_one_or_none()
   ```

## Phase 2: Replace Raw SQL with SQLAlchemy

### Task 2.1: Identify Raw SQL Queries

Current pattern:

```python
domains_query = """
    SELECT id, domain, tenant_id, status, last_scan
    FROM domains
    WHERE tenant_id = %(tenant_id)s
"""
select_result = await db_service.fetch_all(domains_query, {"tenant_id": tenant_id})
```

Target pattern:

```python
domains = await domain_service.get_all(session, tenant_id=tenant_id)
```

Specific changes required:

1. Identify all raw SQL queries in the file
2. For each query, determine the equivalent SQLAlchemy ORM operation
3. Implement the operation in the appropriate service if not already available

### Task 2.2: Extend Domain Service

Add the following methods to domain_service.py if not present:

```python
async def get_all(self, session, tenant_id=None, status=None):
    """Get all domains with optional filtering"""
    query = select(Domain)
    if tenant_id:
        query = query.where(Domain.tenant_id == tenant_id)
    if status:
        query = query.where(Domain.status == status)
    result = await session.execute(query)
    return result.scalars().all()

async def get_with_status_counts(self, session, tenant_id):
    """Get status counts for domains"""
    query = select(Domain.status, func.count(Domain.id)).where(Domain.tenant_id == tenant_id).group_by(Domain.status)
    result = await session.execute(query)
    return {status: count for status, count in result.all()}
```

## Phase 3: Standardize Service Usage

### Task 3.1: Ensure Consistent Service Import Patterns

Current pattern:

```python
from ..services.core.auth_service import auth_service
from ..services.error.error_service import error_service
from ..services.db_service import db_service
from ..services.domain_service import domain_service
```

Target pattern:

```python
# Core services
from ..services.core.auth_service import auth_service
from ..services.core.user_context_service import user_context_service

# Error and validation
from ..services.error.error_service import error_service
from ..services.validation.validation_service import validation_service

# Domain services
from ..services.domain.domain_service import domain_service
from ..services.job.job_service import job_service

# Process services
from ..services.batch.batch_processor_service import batch_processor_service
```

Specific changes:

1. Group service imports by category
2. Standardize import paths
3. Remove unused imports

### Task 3.2: Remove Legacy Job Tracking

Current pattern:

```python
job_id = job_service.create_job("batch_scan", {"status": "pending"})
job_service.update_job_status(job_id, {"status": "running"})
```

Target pattern:

```python
job = await job_service.create(session, {
    "job_type": "batch_scan",
    "tenant_id": tenant_id,
    "status": "pending"
})
await job_service.update_status(session, job.id, "running")
```

Specific changes:

1. Identify all instances of legacy job tracking
2. Replace with SQLAlchemy-based job_service methods
3. Ensure proper session management

## Phase 4: Refactor Large Functions

### Task 4.1: Break Down process_domain_scan

This function should be split into smaller, focused functions:

1. **validate_domain** - Validate domain format and existence
2. **extract_metadata** - Extract metadata from the domain
3. **store_results** - Store the results in the database
4. **handle_errors** - Handle any errors that occur during processing

### Task 4.2: Break Down process_batch_scan_sqlalchemy

This function should be split into smaller, focused functions:

1. **validate_batch** - Validate batch parameters
2. **process_domains** - Process each domain in the batch
3. **track_progress** - Track and update batch progress
4. **handle_errors** - Handle any errors that occur during processing

## Phase 5: Standardize Error Handling

### Task 5.1: Implement Consistent Error Handling

Current pattern (mixed):

```python
# Pattern 1: Manual try/except
try:
    # Code
except Exception as e:
    logger.error(f"Error: {str(e)}")
    return {"error": str(e)}

# Pattern 2: Incomplete error service usage
try:
    # Code
except Exception as e:
    error_service.log_error("domain_scan_error", str(e))
    return {"error": "An error occurred"}
```

Target pattern:

```python
try:
    # Code
except Exception as e:
    error_details = error_service.handle_exception(
        e,
        "domain_scan_error",
        context={"domain": domain, "user_id": user_id},
        log_error=True
    )
    return error_service.format_error_response(error_details)
```

Specific changes:

1. Standardize all error handling to use error_service
2. Ensure consistent error context is provided
3. Use standardized error responses

## Implementation Order

For this refactoring plan, we recommend the following implementation order:

1. **Extend Services**: First, extend the service methods to support all operations needed
2. **Replace Direct Operations**: Replace direct database operations with service calls
3. **Replace Raw SQL**: Convert raw SQL to SQLAlchemy ORM operations
4. **Refactor Large Functions**: Break down large functions into smaller ones
5. **Standardize Error Handling**: Implement consistent error handling
6. **Remove Legacy Job Tracking**: Finally, remove any legacy job tracking code

## Testing Approach

For each change:

1. **Write Unit Tests**: Create unit tests for new service methods
2. **Create Integration Tests**: Test the refactored router functions
3. **Validate Results**: Ensure results match the original implementation
4. **Performance Testing**: Validate that performance is maintained or improved

## Rollout Strategy

1. **Development Environment**: Implement changes on development first
2. **Staged Deployment**: Deploy in stages, starting with non-critical functions
3. **Feature Flags**: Use feature flags to enable/disable new implementations
4. **Monitoring**: Add detailed monitoring for performance and errors

## Success Criteria

The refactoring will be considered successful when:

1. All direct database operations have been moved to services
2. All raw SQL has been replaced with SQLAlchemy ORM
3. Code passes all linters with no SQLAlchemy-related warnings
4. Functions follow the single responsibility principle
5. Error handling is consistent throughout the file
6. All tests pass with the same or better performance

## Conclusion

This refactoring plan provides a structured approach to modernizing the sitemap_scraper.py file to align with the ScraperSky modernization project goals. By following this plan, the file will become more maintainable, testable, and consistent with the rest of the codebase.
