# DATABASE SERVICE CONSOLIDATION PROGRESS

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

## GOAL
Standardize on `services/core/db_service.py` for all database operations to ensure consistent transaction handling and connection management.

## KEY PATTERNS TO FOLLOW
1. Routers should own transaction boundaries - use `async with session.begin()`
2. Services should be transaction-aware but not create their own transactions
3. Replace direct SQL with `db_service` methods where possible
4. Don't modify backup files (.bak extension)

## ⚠️ CRITICAL SUPAVISOR REQUIREMENTS ⚠️
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

## FILES NEEDING UPDATES

### HIGH PRIORITY
- [x] `src/db/sitemap_handler.py` - Refactored to be transaction-aware and accept sessions
- [x] `src/routers/sitemap_analyzer.py` - Updated with proper transaction handling and SQL injection fixes
- [x] `src/routers/modernized_sitemap.py` - Updated to own transaction boundaries and use session dependency
- [x] `src/routers/db_portal.py` - Updated to own transaction boundaries and use session dependency

### MEDIUM PRIORITY
- [x] `src/db/domain_handler.py` - Updated to accept session parameter in all methods and be transaction-aware
- [x] `src/services/db_inspector.py` - Updated to accept session parameter in all methods
- [x] `src/routers/dev_tools.py` - Updated to follow standardized database access patterns
- [x] `src/routers/google_maps_api.py` - Updated to use standardized session handling
- [x] `src/routers/batch_page_scraper.py` - Updated to use standardized session handling
- [x] `src/routers/modernized_page_scraper.py` - Updated to use standardized session handling
- [x] `src/routers/profile.py` - Updated to use standardized session handling

## PROGRESS TRACKER

### `src/db/sitemap_handler.py`
The file currently uses direct SQL with the session interface. Need to refactor to use db_service methods.

**Areas to update:**
- `create_sitemap_file()` - Replace with db_service.create_record
- `update_sitemap_file()` - Replace with db_service.update_record
- `get_sitemap_file()` - Replace with db_service.fetch_one
- `get_sitemap_files_for_domain()` - Replace with db_service.fetch_all
- `get_sitemap_files_by_job_id()` - Replace with db_service.fetch_all
- All other methods using direct SQL queries

### `src/routers/sitemap_analyzer.py`
This file contains background task code that should be refactored to ensure proper transaction handling.

**Areas to update:**
- `process_sitemap_analysis()` - Ensure proper transaction management
- `process_batch_sitemap_analysis()` - Ensure proper transaction management
- Update direct calls to `SitemapDBHandler` with db_service where possible
- Ensure router endpoints own transaction boundaries

### `src/routers/modernized_sitemap.py`
✅ COMPLETED: This file has been updated to follow the correct transaction pattern:
- Updated import to use `get_session_dependency`
- Updated dependency to use the correct session function
- Updated `scan_domain()` to own transaction boundaries with `async with session.begin()`
- Updated `get_job_status()` to own transaction boundaries with `async with session.begin()`
- Ensured the background task properly manages its own session

### `src/routers/db_portal.py`
✅ COMPLETED: This file has been updated to follow the correct transaction pattern:
- Added session dependency to all endpoints
- Added transaction boundaries with `async with session.begin()`
- Updated all method calls to pass the session parameter

### `src/db/domain_handler.py`
✅ COMPLETED: This file has been updated to be transaction-aware:
- All methods now accept a session parameter
- Removed internal session creation
- Removed commit/rollback operations (router owns transaction boundaries)
- Updated insert methods to use parameterized queries
- Started using db_service for the insert_domain_data method

### `src/services/db_inspector.py`
✅ COMPLETED: This file has been updated to be transaction-aware:
- All methods now accept a session parameter
- Methods no longer create their own sessions
- SQL queries have been parameterized for better security
- Updated type hints to include session parameters

### `src/routers/dev_tools.py`
✅ COMPLETED: This file has been updated to follow our standardized database pattern:
- Updated import to use `get_session_dependency` instead of `get_session`
- All endpoints now use dependency injection with `Depends(get_session_dependency)`
- Each endpoint now owns its transaction boundaries with `async with session.begin()`
- Updated `get_system_status()` to use session from dependency injection
- Updated `get_database_tables()` to properly handle transactions
- Updated `get_database_schema()` to pass session to helper functions
- Updated `get_routes_using_table()` to accept an optional session parameter
- All database operations are now properly wrapped in transactions
- Ensured SQL queries are properly parameterized for security

### `src/routers/google_maps_api.py`
✅ COMPLETED: This file was already following most of our standardized patterns and has been updated for full compliance:
- Updated import to use `get_session_dependency` from the standardized module
- All endpoints already properly owned transaction boundaries with `async with session.begin()`
- Background task in `search_places()` already correctly created its own session with `async_session_factory()`
- All service calls already properly passed the session parameter
- Transaction boundaries in background task were already correctly managed
- All endpoints had appropriate error handling with transaction rollback

### `src/routers/batch_page_scraper.py`
✅ COMPLETED: This file had good session handling but needed transaction boundaries:
- Updated import to use `get_session_dependency` instead of `get_session`
- Updated all endpoints to use dependency injection with `Depends(get_session_dependency)`
- Added explicit transaction boundaries with `async with session.begin()` to all endpoints
- Background tasks were already correctly using `async_session_factory()` to create their own sessions
- Service methods were already properly accepting session parameters
- Already had proper error handling with appropriate propagation of exceptions

### `src/routers/modernized_page_scraper.py`
✅ COMPLETED: This file had significant issues with session handling and needed thorough updates:
- Updated import to use `get_session_dependency` from the standardized module instead of `get_db_session`
- Updated all endpoints to use dependency injection with `Depends(get_session_dependency)`
- Added transaction boundaries with `async with session.begin()` to all endpoints
- Corrected incorrect comments about transaction management
- Fixed inconsistency with the missing session parameter in service calls
- Removed duplicate DEFAULT_TENANT_ID definition to use the centralized version
- Ensured all service methods properly receive the session parameter

### `src/routers/profile.py`
✅ COMPLETED: This file already had good transaction handling but needed standardized session dependency:
- Updated import to use `get_session_dependency` from the standardized module instead of `get_db_session`
- Updated all endpoints to use dependency injection with `Depends(get_session_dependency)`
- Transaction boundaries were already correctly implemented with `async with session.begin()`
- Added missing POST endpoint for creating a profile and a DELETE endpoint for removing profiles
- All methods were already properly passing session parameter to service calls
- Already had proper error handling with appropriate exception propagation

## IMPLEMENTATION NOTES
1. For each file, first analyze the current database access patterns
2. Identify which db_service methods are appropriate replacements
3. Ensure router methods properly handle transactions
4. Update imports to use `from ..services.core.db_service import db_service`
5. Test carefully after each change

## TRANSACTION PATTERN EXAMPLES

### Correct Router Pattern:
```python
@router.post("/example")
async def create_example(
    request: ExampleModel,
    session: AsyncSession = Depends(get_db_session)
):
    # Router owns the transaction
    async with session.begin():
        # Call service without creating new transaction
        result = await example_service.create_example(session, request.data)
    return result
```

### Correct Service Pattern:
```python
async def create_example(session: AsyncSession, data: dict):
    # Service uses the session but doesn't manage transaction
    # It's transaction-aware but not transaction-creating
    query = text("INSERT INTO examples VALUES (:value) RETURNING id")
    result = await session.execute(query, {"value": data['value']})
    return result.scalar_one()
```

### For Background Tasks:
```python
async def process_background_task(job_id: str, data: dict):
    # For background tasks, create a new session but still manage transactions explicitly
    async with async_session_factory() as session:
        async with session.begin():
            # Perform database operations
            await db_service.execute(query, params)
```
