# ScraperSky Database Session Factory Enhancement

## 1. Overview

Based on the findings in document 90.9, it's clear that our connection pooling standardization would be most effectively implemented through a central enhancement to the database session factory. This approach would eliminate the need for complex parameter passing through multiple layers and ensure consistent application of Supavisor parameters across all database operations.

## 2. Current Status

The connection pooling standardization has made good progress:

- URL modifier implemented in `src/db/engine.py`
- Engine creation updated to use Supavisor parameters
- Parameter helpers created in `src/utils/db_helpers.py`
- Profile service updated to support raw SQL operations

However, key challenges remain:

- Parameter passing between layers is complex and error-prone
- Not all services use the raw SQL pattern consistently
- Session factory does not automatically apply Supavisor parameters

## 3. Proposed Solution

Enhance the database session factory in `src/db/session.py` to automatically apply Supavisor compatibility parameters to all sessions, eliminating the need for explicit parameter passing.

### 3.1 Core Implementation

```python
# In src/db/session.py

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from ..config.settings import settings
from .engine import get_engine

# Get the engine with Supavisor parameters already applied
engine = get_engine()

# Create async session factory with Supavisor parameters automatically applied
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # Apply Supavisor compatibility options by default
    execution_options={
        "postgresql_expert_mode": True  # Equivalent to no_prepare=True
    }
)

async def get_db_session() -> AsyncSession:
    """
    Get a database session with Supavisor compatibility parameters pre-applied.
    
    This dependency automatically includes proper connection pooling settings,
    making individual endpoints simpler and more consistent.
    
    Returns:
        AsyncSession: Session with Supavisor compatibility
    """
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()
```

### 3.2 Raw SQL Helper in `src/utils/db_utils.py`

```python
# In src/utils/db_utils.py

from sqlalchemy import text
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

async def execute_raw_sql(
    session: AsyncSession,
    sql: str,
    params: Dict[str, Any] = None,
    fetch_all: bool = True
) -> Optional[List[Dict[str, Any]]]:
    """
    Execute raw SQL with Supavisor compatibility.
    
    This helper ensures consistent SQL execution patterns across all services.
    
    Args:
        session: SQLAlchemy async session
        sql: Raw SQL query
        params: Query parameters
        fetch_all: Whether to fetch all results (True) or just one (False)
        
    Returns:
        Results as dict list if fetch_all=True, or single dict if fetch_all=False
    """
    try:
        # Create text SQL with Supavisor compatibility options
        query = text(sql).execution_options(postgresql_expert_mode=True)
        
        # Execute with params dictionary
        result = await session.execute(query, params or {})
        
        # Return results based on fetch mode
        if fetch_all:
            rows = result.fetchall()
            # Convert to list of dicts with column names as keys
            if rows:
                column_names = result.keys()
                return [dict(zip(column_names, row)) for row in rows]
            return []
        else:
            row = result.fetchone()
            if row:
                column_names = result.keys()
                return dict(zip(column_names, row))
            return None
    except Exception as e:
        logger.error(f"Error executing raw SQL: {str(e)}")
        logger.error(f"SQL: {sql}")
        logger.error(f"Params: {params}")
        raise
```

### 3.3 Service Pattern Example

```python
# Example service implementation using the enhanced session factory and SQL helper

from ..utils.db_utils import execute_raw_sql

class ProfileService:
    async def get_profiles(
        self,
        session: AsyncSession,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        # SQL for profile retrieval
        sql = """
            SELECT id, name, email, role, bio, tenant_id, active, created_at, updated_at
            FROM profile
            WHERE tenant_id = :tenant_id
            LIMIT :limit OFFSET :offset
        """
        
        # Parameters for query
        params = {
            "tenant_id": tenant_id,
            "limit": limit,
            "offset": offset
        }
        
        # Execute using helper - Supavisor parameters applied automatically
        return await execute_raw_sql(session, sql, params)
```

## 4. Implementation Plan

### 4.1 Specific Tasks

1. **Enhance Session Factory in `src/db/session.py`**
   - Update factory to include Supavisor parameters
   - Document automatic parameter application

2. **Create SQL Utility Helpers**
   - Implement `execute_raw_sql` function
   - Implement `execute_raw_sql_one` for single result queries

3. **Update Key Services**
   - Update `profile_service.py` to use the new pattern
   - Update `job_service.py` with raw SQL patterns
   - Update `batch_processor_service.py` with raw SQL patterns

4. **Remove Parameter Passing**
   - Remove explicit parameter passing from endpoints
   - Update endpoint documentation to reflect automatic parameter application

5. **Testing and Verification**
   - Test all endpoints with complex database operations
   - Verify consistent behavior across environments

### 4.2 Implementation Timeline

| Task | Estimated Effort | Priority |
|------|------------------|----------|
| Enhance Session Factory | 2 hours | High |
| Create SQL Utilities | 2 hours | High |
| Update Key Services | 4 hours | High |
| Remove Parameter Passing | 2 hours | Medium |
| Testing | 3 hours | High |

Total estimated effort: 13 hours

## 5. Success Criteria

The session factory enhancement will be considered successful when:

1. All database connections automatically include the required Supavisor parameters
2. Services use a consistent pattern for raw SQL operations
3. No explicit parameter passing is needed in endpoints
4. All database operations work reliably in all environments
5. Code is cleaner and easier to maintain without parameter complexity

## 6. Testing Plan

### 6.1 Core Tests

1. **Session Parameter Verification**
   - Verify that all sessions created through the factory have the correct parameters
   - Test with and without explicit options

2. **Service SQL Execution**
   - Test the `execute_raw_sql` helper with various types of queries
   - Verify correct results with different parameter types

3. **End-to-End Tests**
   - Test endpoints that use database operations
   - Verify they work without explicit parameter passing

### 6.2 Test Endpoints

1. **Profiles Endpoint** - `/api/v3/profiles`
2. **Jobs Endpoint** - `/api/v3/jobs`
3. **Batch Processing Endpoint** - `/api/v3/batch_page_scraper/batch`

## 7. Risk Assessment

### 7.1 Potential Risks

1. **ORM Compatibility**: Some SQLAlchemy ORM operations might behave differently with postgresql_expert_mode
2. **Session Behavior Changes**: Changing session default behavior might affect existing code
3. **Performance Impact**: Raw SQL operations might have different performance characteristics

### 7.2 Mitigation Strategies

1. **Thorough Testing**: Test each service with the enhanced session factory
2. **Staged Rollout**: Apply to non-critical services first
3. **Monitoring**: Implement detailed logging during transition
4. **Documentation**: Update documentation to explain the new patterns

## 8. Recommended Next Steps

1. Begin implementation of the enhanced session factory
2. Create the SQL utility helpers
3. Update a single service (profile_service.py) as proof of concept
4. Test thoroughly before expanding to other services