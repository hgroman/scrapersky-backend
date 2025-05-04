# 07-57 Background Session Handler Implementation Work Order

## Executive Summary

This work order addresses critical issues with database connections in background tasks. The current implementation creates direct `AsyncSession` instances, bypassing the necessary Supavisor compatibility settings, which leads to prepared statement errors.

**Root Problem**: Background tasks directly instantiate `AsyncSession` objects instead of using properly configured session factories with Supavisor settings.

**Solution**: Implement a centralized background session handler in `async_session.py` and update all background task code to use this handler exclusively.

**Status**: ✅ COMPLETED
**Priority**: CRITICAL - Affects core batch processing functionality

## Affected Files

1. `src/session/async_session.py` - Added background session factory and context manager
2. `src/services/batch/batch_functions.py` - Updated direct session creation
3. `src/services/page_scraper/domain_processor.py` - Updated direct session creation

## Issue Details

### Current Implementation Problems

1. **Direct Session Creation**: Background tasks directly create `AsyncSession` instances:

   ```python
   async with AsyncSession(engine) as session:
       # Operations
   ```

2. **Missing Supavisor Settings**: These direct sessions lack critical Supavisor compatibility parameters:

   - `statement_cache_size=0` in `server_settings`
   - Other parameters needed for asyncpg 0.30.0

3. **Error Manifestation**: Results in `asyncpg.exceptions.InvalidSQLStatementNameError` errors:

   ```
   prepared statement "__asyncpg_XXXX__" does not exist
   ```

4. **Transaction Management**: Inconsistent handling of commits and rollbacks

## Implementation Details

### 1. Engine Configuration

The _correct_ approach requires setting parameters in `connect_args` rather than `execution_options`:

```python
# Create connect_args with appropriate settings for Supavisor
connect_args = {
    "ssl": ssl_context,
    "timeout": settings.db_connection_timeout,
    # Generate unique prepared statement names for Supavisor compatibility
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    # Required Supavisor connection parameters - MUST be in server_settings
    "server_settings": {
        "statement_cache_size": "0"
    },
    # Explicitly disable prepared statements for asyncpg 0.30.0
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0
}

# Create async engine with environment-specific settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_size=10,
    max_overflow=20,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,
    # Only place isolation_level in execution_options
    execution_options={
        "isolation_level": "READ COMMITTED"
    }
)
```

### 2. Session Factory Implementation

The background task session factory must NOT include execution_options:

```python
def get_background_task_session_factory():
    """
    Returns a session factory specifically configured for background tasks
    with all necessary asyncpg 0.30.0 compatibility settings applied.
    """
    # Simply use the existing engine - all settings are already applied at engine level
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )
```

### 3. Background Session Context Manager

```python
@asynccontextmanager
async def get_background_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for background task database sessions.

    This should be used for ALL background tasks to ensure proper
    connection parameter handling with asyncpg 0.30.0.

    Example:
        async with get_background_session() as session:
            # Background task database operations
    """
    session = background_task_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Background task session error: {str(e)}")
        raise
    finally:
        await session.close()
```

### 4. Usage in Background Tasks

Update all direct session creation:

```python
# Replace this:
async with AsyncSession(engine) as session:
    # Operations

# With this:
async with get_background_session() as session:
    # Operations
```

## Implementation Notes and Lessons Learned

1. **Parameter Placement is Critical**:

   - `statement_cache_size` must be in `server_settings` as a string within connect_args
   - Additional parameters like `prepared_statement_cache_size` should be at the connect_args root level

2. **Don't Pass Execution Options to Session Factory**:

   - Setting `execution_options` on the sessionmaker will cause errors
   - Only isolation_level should be in execution_options at the engine level

3. **Using Multiple Parameter Points**:

   - We found redundant parameter setting in multiple places provides more resilience
   - Both `server_settings` and direct parameters are needed for complete coverage

4. **Background Task Sessions vs Regular Sessions**:

   - Regular sessions (used in API endpoints) work with the standard configuration
   - Background tasks need their dedicated session factory and context manager

5. **Domain-Specific Errors vs Connection Errors**:
   - After fixing the connection issues, domain validation errors may appear
   - This is normal and unrelated to the database connection fixes

## Verification

The implementation was verified by:

1. Creating batch jobs via the API
2. Confirming no prepared statement errors in background tasks
3. Observing domain processing (some domain validation errors occurred, but these are unrelated)
4. Checking logs for connection errors

## Reference

These changes align with the architectural principles outlined in:

- [07-DATABASE_CONNECTION_STANDARDS.md](../Docs/Docs_1_AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md)
- [07-49-BACKGROUND-TASK-SUPAVISOR-STANDARDIZATION-WORK-ORDER.md](./07-49-BACKGROUND-TASK-SUPAVISOR-STANDARDIZATION-WORK-ORDER.md)

## Sign-off

This work order acknowledges that direct session creation in background tasks must be eliminated to ensure compatibility with Supavisor. All background tasks must use the `get_background_session()` function exclusively.
