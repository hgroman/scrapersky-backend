# Database Service Consolidation Plan

**Date:** 2025-03-23 (UPDATED)

This document outlines the detailed plan for standardizing on `services/core/db_service.py` across the ScraperSky codebase. This is the third phase of our service consolidation effort, following the successful completion of auth service and error service consolidation.

## ⚠️ MANDATORY DIRECTIVES ⚠️

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

## Goals

1. **Standardize on `services/core/db_service.py`**
   - All database access should go through this service
   - Remove direct SQL execution where possible

2. **Enforce consistent transaction patterns**
   - Routers own transaction boundaries
   - Services are transaction-aware but don't create transactions
   - Background tasks manage their own sessions but follow same pattern

3. **Simplify the codebase**
   - Remove redundant database access code
   - Consolidate similar functionality
   - Make database operations more consistent and maintainable

4. **⚠️ CRITICAL: Ensure Supavisor connection pooling**
   - ONLY use Supavisor connection strings with proper format:
     `postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
   - NEVER use direct database connections or PgBouncer configurations
   - ALWAYS configure proper pool parameters:
     ```python
     pool_pre_ping=True
     pool_size=5 (minimum)
     max_overflow=10 (recommended)
     ```
   - ALL database-intensive endpoints MUST support connection pooling parameters:
     `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`

## Current Database Access Patterns

After analyzing the codebase, we found these distinct patterns:

1. **Direct SQLAlchemy ORM** (preferred for model operations)
   ```python
   session.add(model)
   await session.flush()
   ```

2. **Raw SQL through SQLAlchemy** (useful for complex queries)
   ```python
   result = await session.execute(text("SELECT * FROM table"))
   ```

3. **db_service methods** (our target standard)
   ```python
   await db_service.fetch_all(query, params)
   ```

4. **Handler classes** (domain_handler.py, sitemap_handler.py)
   - These wrap database operations in domain-specific methods
   - They should be updated to use db_service internally

## Files Needing Updates

### HIGH PRIORITY
1. **src/db/sitemap_handler.py**
   - Current: Uses direct SQL execution with session
   - Target: Update to use db_service methods

2. **src/db/domain_handler.py**
   - Current: Mix of raw SQL and ORM
   - Target: Use db_service or direct ORM consistently

3. **src/services/db_inspector.py**
   - Current: Direct session usage
   - Target: Use db_service methods

### MEDIUM PRIORITY
These routers use mixed database access patterns:

1. **src/routers/db_portal.py**
2. **src/routers/sitemap_analyzer.py**
3. **src/routers/modernized_page_scraper.py**
4. **src/routers/modernized_sitemap.py**

### LOW PRIORITY
Background services that need database access:

1. **src/services/places/places_service.py**
2. **src/services/places/places_search_service.py**
3. **src/services/places/places_storage_service.py**

## Implementation Approach

### Phase 1: Standardize Handler Classes
1. Start with `src/db/sitemap_handler.py`
   - Create a modernized version that uses `db_service` consistently
   - Verify it works with existing code
   - Test thoroughly before replacing the original

2. Update `src/db/domain_handler.py`
   - Follow the same pattern established with sitemap_handler.py
   - Ensure transaction patterns are correct

### Phase 2: Standardize Router Database Access
For each router:
1. Identify all database operations
2. Ensure router owns transaction boundaries
3. Update service calls to be transaction-aware
4. Test functionality to verify changes

### Phase 3: Review Services
For each service:
1. Verify it doesn't create transactions
2. Update to use db_service where appropriate
3. Maintain ORM usage for model operations
4. Test thoroughly

## Conversion Examples

### Example 1: Direct SQL to db_service
```python
# Before
query = "SELECT * FROM table WHERE id = :id"
result = await session.execute(text(query), {"id": record_id})
return result.fetchone()

# After
result = await db_service.fetch_one(
    "SELECT * FROM table WHERE id = :id",
    {"id": record_id}
)
return result
```

### Example 2: Transaction Handling
```python
# Before (service creating transaction)
async def update_record(record_id, data):
    async with session_factory() as session:
        async with session.begin():
            record = await session.get(Model, record_id)
            record.field = data["field"]
            return record

# After (transaction-aware service)
async def update_record(session, record_id, data):
    record = await session.get(Model, record_id)
    record.field = data["field"]
    return record

# And in router
@router.put("/record/{record_id}")
async def update_record(
    record_id: str,
    data: Dict,
    session: AsyncSession = Depends(get_db_session)
):
    async with session.begin():
        result = await record_service.update_record(session, record_id, data)
    return result
```

## Testing Strategy

1. **Unit Tests:**
   - For each updated file, run associated unit tests
   - Create new tests for missing coverage

2. **Transaction Tests:**
   - Use tests in tests-for-transactions/ directory
   - Focus on proper transaction boundary handling

3. **Integration Testing:**
   - Test each API endpoint after changes
   - Verify database operations work as expected

## Progress Tracking

We'll create a detailed tracking document (DATABASE_CONSOLIDATION_PROGRESS.md) to:
- Mark files as they're updated
- Note any issues encountered
- Track testing results

## Reference Implementation

Use `src/routers/google_maps_api.py` as a reference for proper transaction handling.
This file demonstrates:
1. Router-owned transactions
2. Transaction-aware services
3. Proper background task session management

## Timeline

1. **Week 1:** Update handler classes (sitemap_handler.py, domain_handler.py)
2. **Week 2:** Update high-priority routers (db_portal.py, sitemap_analyzer.py)
3. **Week 3:** Update remaining routers and finalize testing

## Success Criteria

1. All database operations consistently use db_service or ORM
2. All transaction boundaries are properly owned by routers
3. No services create or commit transactions
4. All tests pass
5. Application functions correctly in development environment
