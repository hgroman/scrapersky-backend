# Transaction Management Fix Plan

## 1. Overview

This document outlines the plan to implement transaction management fixes for several components in the ScraperSky backend that were not included in our initial fix implementation. These fixes will ensure all components follow our established architectural pattern: **"Routers own transaction boundaries, services do not."**

## 2. Components Requiring Fixes

The following components require transaction management fixes:

### 2.1. FrontendScout Components
- `src/services/page_scraper/processing_service.py`
- `src/routers/modernized_page_scraper.py`

### 2.2. EmailHunter Components
- `src/services/domain_service.py`

### 2.3. ActionQueue Components
- `src/services/job_service.py`

### 2.4. SocialRadar Components
- `src/services/batch/batch_processor_service.py`

### 2.5. ContentMap Components
- `src/routers/sitemap.py`
- `src/services/sitemap_service.py`
- `src/services/sitemap/sitemap_service.py`

## 3. Transaction Management Patterns

For all fixes, we'll apply the following patterns:

### 3.1. Router Pattern
1. Routers should NOT start transactions that wrap service calls
2. Any `async with session.begin():` blocks that wrap service calls should be removed
3. Session objects should be passed as-is to service methods
4. Error handling should include appropriate status codes and messages

### 3.2. Service Pattern
1. Services should be transaction-aware but not transaction-controlling
2. Services should check if they're already in a transaction using `session.in_transaction()`
3. Transaction management should be done by callers (routers), not by services
4. Background tasks should create their own sessions and manage their own transactions

## 4. Implementation Approach

For each component, we'll:

1. **Identify Issues**: Identify all instances where transaction management doesn't follow our pattern
2. **Fix Code**: Implement the necessary changes following our architectural pattern
3. **Add Documentation**: Add clear comments explaining the transaction management approach
4. **Create Tests**: Develop tests to verify the transaction fixes work as expected

## 5. Code Change Examples

### 5.1. Router Fix Example

**Before:**
```python
@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(verify_page_scraper_access)
) -> JobStatusResponse:
    # Get tenant ID if user is authenticated
    tenant_id = current_user.get("tenant_id") if current_user else None

    # Get job status with proper transaction context - problematic transaction wrapping
    async with session.begin():
        status = await page_processing_service.get_job_status(
            session=session,
            job_id=job_id,
            tenant_id=tenant_id
        )

    # Return the response
    return JobStatusResponse(**status)
```

**After:**
```python
@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(verify_page_scraper_access)
) -> JobStatusResponse:
    # Get tenant ID if user is authenticated
    tenant_id = current_user.get("tenant_id") if current_user else None

    # IMPORTANT: Do not wrap service calls in session.begin() blocks.
    # Services should handle their own transaction management internally.
    # This ensures consistent transaction boundary ownership.

    # Get job status without transaction context
    status = await page_processing_service.get_job_status(
        session=session,
        job_id=job_id,
        tenant_id=tenant_id
    )

    # Return the response
    return JobStatusResponse(**status)
```

### 5.2. Service Fix Example

**Before:**
```python
async def create_for_domain(
    self,
    session: AsyncSession,
    job_type: str,
    tenant_id: str,
    domain_id: Optional[str] = None,
    created_by: Optional[str] = None
) -> Optional[Job]:
    # Start a new transaction
    async with session.begin():
        # Create job data dictionary
        job_data = {
            "job_type": job_type,
            "tenant_id": tenant_id,
            "status": self.STATUS_PENDING,
            "domain_id": domain_id,
            "created_by": created_by,
            "progress": 0.0
        }

        # Create job
        job = await self.create(session, job_data)
        return job
```

**After:**
```python
async def create_for_domain(
    self,
    session: AsyncSession,
    job_type: str,
    tenant_id: str,
    domain_id: Optional[str] = None,
    created_by: Optional[str] = None
) -> Optional[Job]:
    try:
        # Check if the session is already in a transaction
        in_transaction = session.in_transaction()
        logger.debug(f"Session transaction state in create_for_domain: {in_transaction}")

        # Create job data dictionary
        job_data = {
            "job_type": job_type,
            "tenant_id": tenant_id,
            "status": self.STATUS_PENDING,
            "domain_id": domain_id,
            "created_by": created_by,
            "progress": 0.0
        }

        # Create job - let caller handle transaction
        job = await self.create(session, job_data)
        return job
    except Exception as e:
        logger.error(f"Error creating job for domain: {str(e)}")
        # Propagate exception to caller for proper transaction handling
        raise
```

## 6. Testing Strategy

For each component, we'll create tests to verify:

1. **Transaction Boundaries**: Ensure routers manage transaction boundaries correctly
2. **Error Handling**: Check that exceptions are properly propagated and handled
3. **Concurrency**: Test behavior with concurrent operations
4. **Integration**: Verify that components work together as expected

## 7. Implementation Timeline

1. **Phase 1 (High Priority)**: Fix FrontendScout and EmailHunter components
2. **Phase 2 (Medium Priority)**: Fix ActionQueue and SocialRadar components
3. **Phase 3 (Lower Priority)**: Fix ContentMap components

## 8. Documentation Requirements

For each fixed component, we'll add:

1. **Code Comments**: Clear comments in the code explaining the transaction management approach
2. **Test Documentation**: Documentation of test cases and expected behavior
3. **Implementation Summary**: Summary of changes made for future reference

## 9. Conclusion

By implementing these transaction management fixes, we'll ensure consistent transaction handling across all components, reduce errors, and improve the overall reliability of the system. This will help prevent transaction-related issues like deadlocks, reduce database connection usage, and make the system more robust.
