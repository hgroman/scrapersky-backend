# DATABASE CONNECTION STANDARDS

This document outlines the **CRITICAL** database connection standards that must be followed in the ScraperSky project. These requirements are **NON-NEGOTIABLE** and **MANDATORY** for all code changes.

## 1. SUPAVISOR CONNECTION POOLING - MANDATORY REQUIREMENTS

⚠️ **CRITICAL: THIS IS NON-NEGOTIABLE AND MANDATORY FOR ALL DEPLOYMENTS** ⚠️

This system **EXCLUSIVELY** uses Supavisor for connection pooling with the following required parameters:

1. **Required Connection Parameters**:

   - `raw_sql=true` - Use raw SQL instead of ORM
   - `no_prepare=true` - Disable prepared statements
   - `statement_cache_size=0` - Control statement caching

2. **Implementation Locations**:

   - These parameters are implemented in:
     - `src/session/async_session.py`
     - `src/db/engine.py`
   - All database operations in the system respect these parameters

3. **Prohibited Alternatives**:

   - ❌ **ABSOLUTELY FORBIDDEN**: Any use of PgBouncer or references to PgBouncer
   - ❌ No alternative connection pooling methods are permitted
   - ❌ No mentions of alternative poolers should exist in code or comments
   - ❌ No attempts to modify these settings will be accepted

4. **Verification and Enforcement**:
   - Run `bin/run_supavisor_check.sh` to verify Supavisor compliance
   - Run `scripts/db/test_connection.py` to verify proper connection configuration
   - Check generated connection report for compliance
   - A pre-commit hook is installed to reject any commits containing PgBouncer references
   - All PRs will be automatically rejected if these standards are not followed

### Connection String Format

The ONLY acceptable format for database connection strings is:

```postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres

```

### Mandatory Connection Configuration

```python
from sqlalchemy.ext.asyncio import create_async_engine
from src.config.settings import settings

def get_engine():
    connection_string = settings.get_db_url()

    # Proper connection pool configuration for Supavisor
    engine = create_async_engine(
        connection_string,
        pool_pre_ping=True,  # Check connection validity before using
        pool_size=5,         # Maintain reasonable pool size
        max_overflow=10,     # Allow for spikes in connection needs
        execution_options={
            "isolation_level": "READ COMMITTED",
            "raw_sql": True,  # REQUIRED for Supavisor
            "no_prepare": True  # REQUIRED for Supavisor
        },
        connect_args={
            "statement_cache_size": 0,  # REQUIRED for Supavisor
            "raw_sql": True,
            "no_prepare": True
        },
        echo=settings.SQL_ECHO,
        future=True
    )

    return engine
```

## 2. ABSOLUTE PROHIBITION OF DIRECT CONNECTIONS

### ❌ STRICTLY FORBIDDEN

The following patterns are STRICTLY PROHIBITED and must be IMMEDIATELY removed from all code:

- Direct imports of psycopg2 or asyncpg APIs
- Manual construction of connection strings
- Custom connection handlers
- Direct connection objects
- PgBouncer-specific configurations

### ✅ MANDATORY APPROACHES

- Use ONLY `get_db_session()` or `async_session_factory()` for database sessions
- NEVER manually create engine or connection objects
- Session objects MUST be obtained ONLY via proper factory methods
- Follow proper transaction boundaries (routers own transactions, services don't)
- Ensure proper session closure in background tasks

## 3. ENDPOINT PARAMETER REQUIREMENTS

All database-intensive routes MUST support the following connection pooling parameters:

- `raw_sql=true` - Use raw SQL instead of ORM when needed
- `no_prepare=true` - Disable prepared statements for specific operations
- `statement_cache_size=0` - Control statement caching for specific operations

These parameters must be supported by ALL API endpoints that perform complex database operations.

### Implementation Details

1. **Engine Configuration**:

   ```python
   # In src/db/engine.py
   connect_args = {
       "statement_cache_size": 0,  # REQUIRED for Supavisor
       "raw_sql": True,  # REQUIRED for Supavisor
       "no_prepare": True,  # REQUIRED for Supavisor
       "server_settings": {"application_name": "scraper_sky"}
   }

   execution_options = {
       "isolation_level": "READ COMMITTED",
       "raw_sql": True,  # REQUIRED for Supavisor
       "no_prepare": True  # REQUIRED for Supavisor
   }
   ```

2. **Session Creation**:

   ```python
   # In src/session/async_session.py
   from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

   async_session_factory = async_sessionmaker(
       bind=engine,
       expire_on_commit=False,
       class_=AsyncSession
   )

   async def get_db_session() -> AsyncSession:
       session = async_session_factory()
       try:
           yield session
       finally:
           await session.close()
   ```

3. **Usage in Routers**:
   ```python
   @router.post("/endpoint")
   async def endpoint(
       request: RequestModel,
       session: AsyncSession = Depends(get_db_session)
   ):
       # Your code using session
   ```

## 4. TRANSACTION MANAGEMENT PATTERNS

### Router Responsibility

Routers OWN transaction boundaries:

```python
@router.post("/resource")
async def create_resource(
    request: RequestModel,
    session: AsyncSession = Depends(get_db_session)
):
    # Start explicit transaction
    async with session.begin():
        # Call service within transaction
        result = await service.create_resource(session, request)

    # Return response after transaction is committed
    return result
```

### Service Responsibility

Services are transaction-aware but NEVER manage transactions:

```python
async def create_resource(
    session: AsyncSession,
    data: dict
) -> Resource:
    # Use session without transaction management
    resource = Resource(**data)
    session.add(resource)
    await session.flush()  # Flush without commit
    return resource
```

### Background Task Responsibility

Background tasks create their own sessions and manage their own transactions:

```python
async def process_background_task(task_id: str):
    # Create dedicated session for background task
    session = async_session_factory()
    try:
        # Manage transaction explicitly
        async with session.begin():
            # Perform database operations
            # ...
    finally:
        # Always close the session
        await session.close()
```

### Background Session Management with asyncpg 0.30.0+ ⚠️

When using asyncpg 0.30.0 or newer with Supavisor, background tasks **MUST** use a specialized session handler to avoid prepared statement errors. Direct AsyncSession creation will cause:

```
asyncpg.exceptions.InvalidSQLStatementNameError: prepared statement "__asyncpg_XXXX__" does not exist
```

#### ✅ REQUIRED Implementation

1. **Use `get_background_session()`**: Always use the `get_background_session` context manager from `src/session/async_session.py` for background tasks.

   ```python
   from src.session.async_session import get_background_session

   async def my_background_job():
       async with get_background_session() as session:
           # ... perform database operations using session ...
           # IMPORTANT: Adhere to transaction patterns in Guide 13
           pass
   ```

2. **Adhere to Transaction Patterns**: When using `get_background_session`, you **MUST** follow the specific transaction management rules outlined in `Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md` (Section 2, Background Task Pattern). This includes letting the context manager handle the commit/rollback and ensuring any called helper functions do not commit/rollback the passed session.

3. **Engine Configuration**:

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

2. **Background Session Factory**:

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

# Create an instance of the background task session factory
background_task_session_factory = get_background_task_session_factory()
```

3. **Background Session Context Manager**:

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

4. **Usage in Background Tasks**:

```python
async def process_background_task(task_id: str):
    # ❌ NEVER do this with asyncpg 0.30.0+:
    # async with AsyncSession(engine) as session:

    # ✅ ALWAYS do this instead:
    async with get_background_session() as session:
        # Perform database operations
        # ...
```

#### Critical Notes on Parameter Placement

1. **Server Settings vs. Connect Args**:

   - `statement_cache_size` must be in `server_settings` as a string
   - Additional parameters should be at connect_args root level
   - Using both locations provides redundancy against connection errors

2. **Session Factory Constraints**:

   - NEVER pass execution_options to async_sessionmaker
   - Set execution_options ONLY at the engine level

3. **All Background Tasks Must Comply**:
   - All files with background tasks MUST be updated
   - Common locations: `batch_processor.py`, `domain_processor.py`, background workers
   - Pre-commit hooks should check for direct AsyncSession creation

## 5. VERIFICATION CHECKLIST

All code changes MUST be verified against these criteria:

1. ✅ No direct imports of psycopg2 or asyncpg
2. ✅ No manual construction of connection strings
3. ✅ Session objects obtained ONLY via proper factory methods
4. ✅ Proper transaction boundaries (routers own transactions, services don't)
5. ✅ Proper session closure in background tasks
6. ✅ Supavisor-compatible pool configuration

## 6. SQL DEBUGGING AND TRACING

For debugging database operations:

```python
# Enable SQL logging during development
settings.SQL_ECHO = True

# Debug specific database operation
async with session.begin():
    # Log the beginning of transaction
    logger.debug("Starting transaction for operation X")

    # Execute query
    result = await session.execute(select(Model).where(Model.id == model_id))

    # Log result
    logger.debug(f"Query result: {result}")
```

## 7. TRANSACTION ERROR IDENTIFICATION

Common transaction errors to watch for:

1. **"A transaction is already begun on this Session"**

   - Cause: Nested transactions
   - Solution: Ensure services don't create their own transactions

2. **"Current transaction is aborted, commands ignored until end of transaction block"**

   - Cause: Incomplete transaction management
   - Solution: Ensure proper try/except/finally with transaction cleanup

3. **"Can't operate on closed transaction inside context manager"**
   - Cause: Using a session after its transaction is closed
   - Solution: Ensure operations happen within the transaction context

## Technical Background

The Supavisor connection pooling parameters are required to prevent prepared statement cache errors. These specific settings ensure:

- No name conflicts in prepared statements
- Proper transaction isolation
- Reliable connection handling under high load

Changing these parameters will result in unpredictable application behavior, data integrity issues, and connection failures.

## PgBouncer Prohibition Rationale

PgBouncer is **strictly prohibited** in this codebase for the following reasons:

1. **Incompatible with prepared statements**: PgBouncer in transaction mode doesn't support prepared statements correctly, leading to errors like:

   ```
   (sqlalchemy.dialects.postgresql.asyncpg.Error) prepared statement "..." does not exist
   ```

2. **Transaction nesting conflicts**: PgBouncer causes conflicts between its connection pooling and SQLAlchemy's transaction management.

3. **Supavisor superiority**: Supavisor is specifically designed to work with our database architecture and handles connection pooling more reliably.

The use of PgBouncer has historically caused significant issues in this codebase, including silent failures, data inconsistency, and connection pooling conflicts.
