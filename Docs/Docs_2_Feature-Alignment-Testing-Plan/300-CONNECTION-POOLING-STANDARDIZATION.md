# ScraperSky Connection Pooling Standardization Plan

## 1. Overview

This document outlines the plan to address the second high-leverage issue identified in our system assessment: inconsistent application of connection pooling parameters across database endpoints. Standardizing these parameters will significantly improve database reliability and performance, particularly in production environments.

## 2. Current Status

Our health assessment (document 90.1) identified that while some endpoints correctly include the required connection pooling parameters, others don't, leading to inconsistent behavior.

### 2.1 Required Connection Parameters

The following parameters are mandatory for reliable database access with Supavisor connection pooling:

- `raw_sql=true` - Use raw SQL instead of ORM for complex operations
- `no_prepare=true` - Disable prepared statements which can conflict with pooling
- `statement_cache_size=0` - Control statement caching to avoid conflicts

### 2.2 Current Implementation

- **Inconsistent Implementation**: Some endpoints include these parameters, others don't
- **Manual Parameter Addition**: Each endpoint needs to manually add these parameters
- **No Centralized Enforcement**: No mechanism ensures these parameters are used consistently

## 3. Implementation Plan

This plan aims to address the inconsistencies by creating a central mechanism to automatically apply these parameters.

### 3.1 High-Level Approach

Create a middleware or utility function that automatically applies connection pooling parameters to all database operations. This should be a minimal change with maximum impact across all endpoints.

### 3.2 Specific Implementation Tasks

1. **Create Database URL Modifier Utility**:
   - Create a utility function that modifies database URLs to include the required parameters
   - Apply this to all database connection creation points

2. **Implement Query Parameter Standardization**:
   - Create a mechanism to add required parameters to endpoints automatically
   - Ensure parameters are properly passed to database operations

3. **Update Documentation**:
   - Document the connection pooling requirements
   - Explain the automatic parameter handling system

### 3.3 Detailed Implementation Steps

#### 3.3.1 Create Database URL Modifier in `src/db/engine.py`

```python
def get_supavisor_ready_url(db_url: str) -> str:
    """
    Enhance database URL with required Supavisor connection pooling parameters.

    Args:
        db_url: Original database URL

    Returns:
        Enhanced URL with connection pooling parameters
    """
    # Already has query parameters
    if "?" in db_url:
        return f"{db_url}&raw_sql=true&no_prepare=true&statement_cache_size=0"
    # No existing query parameters
    else:
        return f"{db_url}?raw_sql=true&no_prepare=true&statement_cache_size=0"
```

#### 3.3.2 Modify Database Engine Creation in `src/db/engine.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

def create_db_engine() -> AsyncEngine:
    """
    Create SQLAlchemy async engine with proper Supavisor parameters.

    Returns:
        Configured AsyncEngine instance
    """
    database_url = settings.get_database_url()

    # Apply connection pooling parameters
    enhanced_url = get_supavisor_ready_url(database_url)

    # Create engine with enhanced URL
    engine = create_async_engine(
        enhanced_url,
        echo=settings.sqlalchemy_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_recycle=settings.db_pool_recycle,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True  # Verify connections before use
    )

    return engine
```

#### 3.3.3 Create Endpoint Parameter Helper in `src/utils/db_helpers.py`

```python
from typing import Dict, Any, Optional
from fastapi import Query

def get_db_params(
    raw_sql: bool = Query(True, description="Use raw SQL for complex operations"),
    no_prepare: bool = Query(True, description="Disable prepared statements"),
    statement_cache_size: int = Query(0, description="Set statement cache size")
) -> Dict[str, Any]:
    """
    Get standardized database parameters for endpoints.

    This function can be used as a dependency in FastAPI endpoints
    to ensure consistent parameters for database operations.

    Returns:
        Dictionary of standardized database parameters
    """
    return {
        "raw_sql": raw_sql,
        "no_prepare": no_prepare,
        "statement_cache_size": statement_cache_size
    }
```

#### 3.3.4 Update Example Endpoint in `src/routers/profile.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_db_session
from ..utils.db_helpers import get_db_params

router = APIRouter()

@router.get("/profiles")
async def get_profiles(
    session: AsyncSession = Depends(get_db_session),
    db_params: Dict[str, Any] = Depends(get_db_params)
):
    """
    Get profiles with standardized database parameters.

    The db_params dependency automatically includes
    the required connection pooling parameters.
    """
    # Parameters are now available through db_params
    raw_sql = db_params["raw_sql"]
    no_prepare = db_params["no_prepare"]
    statement_cache_size = db_params["statement_cache_size"]

    # Use parameters as needed...
    # ...
    return {"profiles": results}
```

## 4. Testing Plan

### 4.1 Test Cases

1. **Database URL Transformation**:
   - Test with URLs with and without existing query parameters
   - Verify that parameters are correctly added

2. **Engine Creation**:
   - Verify that the engine is created with correct parameters
   - Test connection successes with the enhanced engine

3. **API Endpoint Parameters**:
   - Test that endpoints correctly receive the parameters
   - Verify parameters are passed to database operations

### 4.2 Test Endpoints

1. **Profiles Endpoint** - `/api/v3/profiles`
2. **RBAC Roles Endpoint** - `/api/v3/rbac/roles`
3. **Features Endpoint** - `/api/v3/features/`

## 5. Success Criteria

The connection pooling standardization will be considered successful when:

1. All database connections automatically include the required parameters
2. No manual parameter addition is needed for new endpoints
3. Existing endpoints work correctly with the standardized approach
4. No connection errors appear in the logs related to pooling
5. Documentation clearly explains the automatic parameter handling

## 6. Implementation Timeline

| Task | Estimated Effort | Priority |
|------|------------------|----------|
| Create URL Modifier | 1 hour | High |
| Update Engine Creation | 2 hours | High |
| Create Parameter Helper | 1 hour | High |
| Update Documentation | 1 hour | Medium |
| Testing | 3 hours | High |

Total estimated effort: 8 hours

## 7. Risk Assessment

### 7.1 Potential Risks

1. **Parameter Conflicts**: Existing endpoints might explicitly override these parameters
2. **Connection Failures**: Changes to connection handling might temporarily impact stability
3. **ORM Compatibility**: Some SQLAlchemy ORM operations might behave differently with raw_sql=true

### 7.2 Mitigation Strategies

1. **Phased Rollout**: Implement changes on a single endpoint first
2. **Extensive Testing**: Test thoroughly before deploying to production
3. **Rollback Plan**: Maintain ability to quickly revert changes if issues arise
4. **Monitoring**: Implement special logging during the transition period

## 8. Next Steps

1. Begin implementation of the URL modifier utility
2. Update engine creation function
3. Implement the parameter helper
4. Test with priority endpoints
5. Document the new approach
