# Tenant Isolation Removal Work Order

## Overview

**Document ID**: 07-65-TENANT-ISOLATION-REMOVAL-WORK-ORDER
**Date**: 2025-03-29
**Author**: Claude
**Status**: Completed

## Objective

This work order details the plan to completely remove tenant isolation from the Single Domain Scanner route and its dependency tree. According to our architectural documents, tenant isolation has been simplified system-wide, but vestigial tenant_id references still exist in our codebase, causing inconsistencies and bugs. Our goal is to systematically remove these references while maintaining database integrity.

## Success Criteria

1. All tenant_id parameter passing and extraction is removed from the Single Domain Scanner route
2. API continues to function with no regressions
3. Background processing continues to work correctly
4. Database integrity is maintained through default values

## Current State Analysis

1. **Router** (`src/routers/modernized_page_scraper.py`):

   - Extracts tenant_id from request but no longer passes it to processing_service methods
   - Still passes tenant_id to background tasks

2. **Domain Processor** (`src/services/page_scraper/domain_processor.py`):

   - Accepts tenant_id parameter but only uses it for domain creation/lookup

3. **Pydantic Models**:

   - `SitemapScrapingRequest` and `BatchRequest` have optional tenant_id fields

4. **Database Models**:
   - Domain, Job, and BatchJob have non-nullable tenant_id fields with DEFAULT_TENANT_ID defaults

## Implementation Plan

### Stage 1: Modify Domain Processor

1. Update `process_domain_with_own_session` to remove tenant_id parameter
2. Update `get_or_create_domain` to use DEFAULT_TENANT_ID instead of a parameter

### Stage 2: Update Router

1. Remove all tenant_id extraction from request/user context
2. Remove tenant_id parameter from background task calls
3. Keep DEFAULT_TENANT_ID import for dev user

### Stage 3: Test Incremental Changes

1. Test domain scanning with tenant_id parameter removed
2. Verify all API endpoints work correctly
3. Check database records to ensure tenant_id is still populated with default value

### Stage 4: Documentation

1. Update inline code documentation to remove tenant_id mentions
2. Create implementation report

## Detailed Implementation

### Stage 1: Modify Domain Processor

```python
# BEFORE
async def process_domain_with_own_session(
    job_id: str,
    domain: str,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    max_pages: int = 10
) -> None:
    # ...
```

```python
# AFTER
async def process_domain_with_own_session(
    job_id: str,
    domain: str,
    user_id: Optional[str] = None,
    max_pages: int = 10
) -> None:
    # ...
```

Update domain creation to use DEFAULT_TENANT_ID instead of parameter.

### Stage 2: Update Router

Remove tenant_id extraction and usage:

```python
# BEFORE
tenant_id = request.tenant_id or current_user.get("tenant_id", DEFAULT_TENANT_ID)

# Add background task
background_tasks.add_task(
    process_domain_with_own_session,
    job_id=result["job_id"],
    domain=request.base_url,
    tenant_id=tenant_id,
    user_id=user_id,
    max_pages=request.max_pages or 1000
)
```

```python
# AFTER
# Add background task
background_tasks.add_task(
    process_domain_with_own_session,
    job_id=result["job_id"],
    domain=request.base_url,
    user_id=user_id,
    max_pages=request.max_pages or 1000
)
```

## Testing Strategy

### Unit Testing

1. Update existing unit tests to remove tenant_id parameters
2. Create new unit tests for domain processor functions without tenant_id
3. Verify database records contain correct DEFAULT_TENANT_ID

### Integration Testing

1. Test domain scanning API endpoint
2. Verify background processing completes successfully
3. Check job status endpoints
4. Verify errors are handled properly

### Manual Testing

1. Test the API with Swagger UI
2. Monitor logs during processing
3. Verify database records have correct tenant_id values

## Rollback Plan

If issues are detected:

1. Revert code changes
2. Restore previous parameter passing behavior
3. Keep tenant_id parameters optional with default values

## Verification Steps

For each stage:

1. Run the application locally
2. Execute the API endpoints
3. Check database records
4. Verify logs for errors
5. Run unit and integration tests

## Schedule

1. Stage 1: Modify Domain Processor - 1 hour
2. Stage 2: Update Router - 1 hour
3. Stage 3: Test Incremental Changes - 2 hours
4. Stage 4: Documentation - 1 hour

Total estimated time: 5 hours

## Risk Assessment

| Risk                               | Impact | Likelihood | Mitigation                            |
| ---------------------------------- | ------ | ---------- | ------------------------------------- |
| API breaks                         | High   | Low        | Thorough testing after each stage     |
| Database records missing tenant_id | Medium | Low        | Verify ORM default values are applied |
| Background processing fails        | High   | Medium     | Test with various domain types        |
| Performance issues                 | Low    | Low        | Monitor processing times before/after |

## Approvals Required

- Lead Developer
- System Architect

## Follow-up Activities

1. Apply similar tenant isolation removal to other routes
2. Create a standardized pattern document for tenant-free implementations
3. Consider database migration to make tenant_id nullable in the future
