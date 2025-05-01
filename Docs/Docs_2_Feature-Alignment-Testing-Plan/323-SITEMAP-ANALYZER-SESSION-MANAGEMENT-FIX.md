# ScraperSky Sitemap Analyzer Session Management Fix

## Overview

We've implemented proper database transaction management for the Sitemap Analyzer components to address session handling issues similar to those found in the Google Maps API endpoints. This document explains the changes made and best practices for session management.

## Problem Identified

The Sitemap Analyzer components were not consistently using proper transaction contexts around database operations, which could lead to:

1. Unpredictable transaction state
2. `_AsyncGeneratorContextManager` errors when session objects were misused
3. Lack of proper error handling and rollback mechanisms
4. Potential for orphaned database connections

## Changes Made

### 1. Router Changes (`src/routers/modernized_sitemap.py`)

We added explicit transaction contexts around service method calls:

```python
# Before
status = await sitemap_processing_service.get_job_status(
    session=session,
    job_id=job_id,
    tenant_id=DEFAULT_TENANT_ID
)

# After
async with session.begin():
    status = await sitemap_processing_service.get_job_status(
        session=session,
        job_id=job_id,
        tenant_id=DEFAULT_TENANT_ID
    )
```

This ensures that:

- Each database operation has a clear transaction boundary
- Automatic rollback occurs on exceptions
- Connections are properly managed and released

### 2. Service Changes (`src/services/sitemap/processing_service.py`)

We improved background task handling to ensure all database operations within the service are wrapped in proper transaction contexts:

```python
async def _process_domain(self, ...):
    try:
        # Ensure database operations are wrapped in a transaction
        async with session.begin():
            # Domain processing logic
            pass
    except Exception as e:
        # Error handling with proper transaction for status updates
        try:
            async with session.begin():
                # Update job status
                pass
        except Exception as update_err:
            logger.error(f"Failed to update job status: {update_err}")
```

### 3. Documentation Changes (`src/services/sitemap/sitemap_service.py`)

We added clear documentation to emphasize that transaction contexts should be managed by the router:

```python
async def analyze_domain(self, session: AsyncSession, ...):
    """
    Analyze a domain for sitemaps.

    Note: Transaction context should be managed by the router.
    This method assumes it's being called within an active transaction.

    ...
    """
```

## Best Practices for Session Management

1. **Router-Level Transaction Management**

   - All database operations in endpoint handlers should be wrapped in `async with session.begin():`
   - This provides clear transaction boundaries and automatic rollback on errors

2. **Service Method Design**

   - Service methods should accept an active session and perform operations
   - They should NOT manage transactions unless explicitly designed to do so
   - Documentation should clarify transaction expectations

3. **Background Task Handling**

   - Background tasks should manage their own transaction contexts
   - Each logical unit of work should have its own transaction
   - Error handling should include transaction contexts for status updates

4. **Error Handling**
   - Let transaction contexts handle rollbacks automatically
   - Log errors at the appropriate level
   - Consider nested transactions for recovery operations

## Example of Correct Pattern

```python
# In router
@router.post("/analyze")
async def analyze_domain(
    request: AnalyzeRequest,
    session: AsyncSession = Depends(get_session)
):
    # Wrap service call in transaction
    async with session.begin():
        result = await sitemap_service.analyze_domain(
            session=session,
            domain=request.domain,
            tenant_id=request.tenant_id
        )

    return result

# In service
async def analyze_domain(self, session: AsyncSession, domain: str, ...):
    """
    Note: Transaction context should be managed by the router.
    """
    # Use session for operations, don't manage transaction
    domain_record = await self._get_or_create_domain(session, domain)
    job = await self._create_job(session, domain_record.id)

    return {"job_id": str(job.id), "status": "created"}
```

## Affected Files

1. `src/routers/modernized_sitemap.py`

   - Added transaction contexts around all database operations

2. `src/services/sitemap/processing_service.py`

   - Improved background task transaction handling
   - Added proper error handling with transaction contexts

3. `src/services/sitemap/sitemap_service.py`
   - Added documentation clarifying transaction management expectations

## Testing Recommendations

1. Test all sitemap endpoints to ensure they handle errors correctly
2. Verify that background tasks complete successfully
3. Monitor logs for any session-related errors
4. Check connection pool metrics to ensure connections are properly released

## What's Next

Similar session management improvements should be extended to:

1. Domain manager endpoints
2. Any remaining legacy sitemap endpoints
3. Other services that interface with the database
