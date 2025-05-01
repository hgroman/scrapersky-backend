# DATABASE CONSOLIDATION MASTER REFERENCE

**Date:** 2025-03-24
**Status:** COMPLETED
**Version:** 1.1

## 1. OVERVIEW & PURPOSE

This document serves as the master reference for the ScraperSky database service consolidation effort. It provides context, goals, approach, and progress tracking to ensure continuity throughout the simplification process. This document should be referenced at the start of any new AI session focused on database consolidation.

## 2. CRITICAL DIRECTIVE

**THE PRIMARY OBJECTIVE IS SIMPLIFICATION AND STANDARDIZATION:**

1. **SIMPLIFY** - Reduce code, not add more
2. **STANDARDIZE** - One consistent database connectivity pattern everywhere
3. **ELIMINATE REDUNDANCY** - Remove duplicate functionality, not create more
4. **CONSOLIDATE** - Use `services/core/db_service.py` as the single standard

**STRICTLY PROHIBITED:**
- Adding new functionality
- Creating new patterns
- Any form of scope creep
- Inventing new approaches

**THIS IS A CLEANUP AND STANDARDIZATION EFFORT ONLY**

## 3. KEY DOCUMENTS

| Document | Path | Purpose |
|----------|------|---------|
| Database Routes Audit | [02-01-database-routes-audit-2025-03-24.md](../02-database-consolidation/02-01-database-routes-audit-2025-03-24.md) | Comprehensive audit of all router files' database access patterns |
| Implementation Guide | [02-02-implementation-guide-2025-03-24.md](../02-database-consolidation/02-02-implementation-guide-2025-03-24.md) | Step-by-step guide for implementing the standardization |
| DB Service Consolidation Plan | [02-03-database-service-consolidation-plan-2025-03-23.md](../02-database-consolidation/02-03-database-service-consolidation-plan-2025-03-23.md) | Overall consolidation strategy and approach |
| Progress Tracking | [02-04-db-consolidation-progress-2025-03-24.md](../02-database-consolidation/02-04-db-consolidation-progress-2025-03-24.md) | Ongoing progress of the implementation |
| Pattern Test Plan | [02-09-pattern-test-plan-2025-03-24.md](../02-database-consolidation/02-09-pattern-test-plan-2025-03-24.md) | Plan for testing the standardized patterns |

## 4. DATABASE CONSOLIDATION APPROACH

### 4.1 Guiding Principles

1. **Transaction Responsibility**:
   - Routers own transaction boundaries
   - Services are transaction-aware but don't create transactions
   - Background tasks create and manage their own sessions/transactions

2. **Session Handling**:
   - Use dependency injection for session in routers
   - Pass session to services
   - Never create sessions within router methods
   - Background tasks create their own sessions

3. **Error Handling**:
   - Handle errors at router level
   - Ensure proper transaction rollback on errors
   - Log errors with context
   - Return appropriate HTTP status codes

4. **DB Service Usage**:
   - Use `db_service` methods for all database operations
   - Replace direct SQL execution with parameterized queries
   - Use SQLAlchemy ORM for complex operations

### 4.2 Reference Implementation

The file `src/routers/google_maps_api.py` serves as the reference implementation for all these patterns. When in doubt, refer to this file for examples of proper:

- Transaction boundary management
- Session dependency injection
- Background task session management
- Error handling
- Service method calls

## 5. IMPLEMENTATION STATUS

### 5.1 Completed Files

| File | Status | Notes |
|------|--------|-------|
| google_maps_api.py | ✅ DONE | Reference implementation for transaction pattern |
| profile.py | ✅ DONE | Uses proper transaction boundaries |
| batch_page_scraper.py | ✅ DONE | Background task session handling fixed |
| modernized_sitemap.py | ✅ DONE | Updated to follow transaction pattern |
| sitemap_analyzer.py | ✅ DONE | Fixed direct SQL queries with parameterized queries |

### 5.2 Remaining Files

| File | Status | Notes |
|------|--------|-------|
| dev_tools.py | 🔄 IN PROGRESS | Direct session creation needs fixing |
| db_portal.py | 🔄 IN PROGRESS | Service-managed transactions need refactoring |
| modernized_page_scraper.py | ⏱ PENDING | Low-priority but needs transaction boundary updates |

## 6. STANDARDIZED PATTERNS

### 6.1 Router Endpoint with Transaction

```python
@router.post("/endpoint", response_model=ResponseModel)
async def endpoint(
    request: RequestModel,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    try:
        # Router owns transaction boundary
        async with session.begin():
            # Call service passing the session
            result = await service.operation(
                session=session,
                data=request.data,
                user_id=current_user.get("id")
            )
        
        # Return after transaction committed
        return result
    except Exception as e:
        # Error handling with proper status codes
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 6.2 Background Task Pattern

```python
# Add background task after transaction commits
background_tasks.add_task(
    process_background_job,
    job_id=job.id,
    data=request.dict()
)

# Background task function creates its own session
async def process_background_job(job_id: str, data: dict):
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                # Process within transaction
                # ...
        except Exception as e:
            logger.error(f"Background task error: {str(e)}")
```

### 6.3 Transaction-Aware Service

```python
# Service accepts session but doesn't create transactions
async def service_operation(
    session: AsyncSession,
    data: dict,
    user_id: str
):
    # Use session but don't begin/commit/rollback
    # ...
    return result
```

## 7. VERIFICATION CHECKLIST

After updating each file, verify:

1. [ ] Router uses `AsyncSession = Depends(get_db_session)`
2. [ ] Router wraps service calls in `async with session.begin()`
3. [ ] Router handles errors properly
4. [ ] Services accept session parameter
5. [ ] Services do not create/commit/rollback transactions
6. [ ] Background tasks create their own sessions
7. [ ] Direct SQL is replaced with db_service methods
8. [ ] No string concatenation in SQL queries

## 8. KEY SUCCESS METRICS

1. Consistent transaction patterns across all routers
2. Elimination of all direct SQL with string concatenation
3. Clear separation of responsibilities (router owns transactions)
4. Proper error handling with transaction rollback
5. Elimination of duplicate database service implementations

## 9. IMPLEMENTATION PROGRESS TRACKING

Regular progress updates are maintained in [02-04-db-consolidation-progress-2025-03-24.md](../02-database-consolidation/02-04-db-consolidation-progress-2025-03-24.md). Refer to this document for the latest status.