# SCRAPERSKY ARCHITECTURE QUICK REFERENCE

This document provides a concise overview of the ScraperSky architecture, patterns, and conventions. Use it as a quick reference when working with any part of the system.

## DATABASE ACCESS PATTERNS

### Critical Connection Requirements

- **MANDATORY**: Use Supavisor connection string format:

  ```
  postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres
  ```

- **REQUIRED Parameters**:

  - `raw_sql=true`
  - `no_prepare=true`
  - `statement_cache_size=0`

- **Configuration Requirements**:

  - `pool_pre_ping=True`
  - `pool_size=5` (minimum)
  - `max_overflow=10` (recommended)

- **STRICTLY PROHIBITED** ⚠️:
  - Any use of PgBouncer or references to it
  - Direct psycopg2/asyncpg usage
  - Manual connection string construction

### Enforcement and Verification

- Run `bin/run_supavisor_check.sh` to verify Supavisor compliance
- Run `scripts/db/test_connection.py` to test connections
- Pre-commit hooks will block any PgBouncer references
- All PRs containing PgBouncer references will be rejected

| Component           | Responsibility                                                                    |
| ------------------- | --------------------------------------------------------------------------------- |
| **ROUTER**          | Creates session, manages transaction boundaries with `async with session.begin()` |
| **SERVICE**         | Uses provided session, doesn't create transactions, is "transaction-aware"        |
| **BACKGROUND TASK** | Creates own session, manages own transactions                                     |
| **MODELS**          | Provide helper methods like `create_new()` for database operations                |

### Key Rules

1. **Session Creation**

   - Routers get sessions via `get_db_session` dependency
   - Background tasks create sessions via `async_session_factory()`
   - Services NEVER create sessions (except in background tasks)

2. **Transaction Boundaries**

   - Routers define transaction boundaries with `async with session.begin()`
   - Services work within existing transactions
   - Background tasks manage their own transactions

3. **Error Handling**

   - Errors must be propagated for proper transaction rollback
   - Background tasks must use separate error sessions for recovery

4. **Connection Pooling Parameters**
   - All database-intensive endpoints must support:
     - `raw_sql=true` - Use raw SQL instead of ORM when needed
     - `no_prepare=true` - Disable prepared statements
     - `statement_cache_size=0` - Control statement caching

## AUTHENTICATION

### Key Components

| Component            | Responsibility                       |
| -------------------- | ------------------------------------ |
| **jwt_auth.py**      | Core JWT verification and generation |
| **auth_service.py**  | Authentication business logic        |
| **get_current_user** | FastAPI dependency for auth          |

### Auth Flow

1. JWT Token in Authorization header
2. `get_current_user` dependency validates token
3. User identity passed to services (user_id only)
4. No RBAC or tenant isolation checks

### ⚠️ AUTHENTICATION CHANGES ⚠️

**ALL RBAC AND TENANT ISOLATION HAS BEEN REMOVED**

- ❌ **REMOVED ENTIRELY**:
  - RBAC system (roles, permissions, features)
  - Tenant isolation (tenant_id filtering)
  - Permission checking functions
  - Feature flag checks
  - Role level checks

## MODULE DEPENDENCIES

```
routers → services → models
   ↓          ↓
dependencies  utils
```

### Key Rules

1. **Dependency Direction**

   - Import from deeper levels only (services can import models)
   - Never import across (routers never import other routers)
   - No circular dependencies allowed

2. **Service Organization**
   - Core services provide shared functionality
   - Feature-specific services implement business logic
   - Utility services provide helper functions

## ERROR HANDLING

1. **Pattern**

   - Routers catch and transform exceptions to HTTP responses
   - Services propagate domain-specific exceptions
   - Database errors are caught and logged with appropriate context

2. **Key Error Types**
   - `HTTPException` for HTTP-specific errors
   - Domain-specific exceptions in `exceptions.py`
   - Database errors are logged with context and transformed to HTTP errors

## CODE ORGANIZATION

### Directory Structure

```
/src
  /auth         # Authentication components
  /config       # Configuration and settings
  /constants    # Constants and enums
  /core         # Core utilities and exceptions
  /db           # Database connection and session management
  /models       # SQLAlchemy models
  /routers      # API endpoints
  /schemas      # Pydantic models for API
  /services     # Business logic
  /utils        # Utilities and helpers
```

### Naming Conventions

- **Files**: snake_case
- **Classes**: PascalCase
- **Functions/Methods**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Variables**: snake_case

## API STRUCTURE

### Endpoint Pattern

```python
@router.post("/path")
async def handler(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)  # JWT validation only
):
    # JWT authentication only, no RBAC or tenant checks
    user_id = current_user.get("id")

    # Set up transaction
    async with session.begin():
        # Call service - no tenant_id, no permissions
        result = await service.do_operation(
            session=session,
            request=request,
            user_id=user_id
        )

    # Add background tasks AFTER transaction is committed
    background_tasks.add_task(service.background_operation, result.id)

    # Format and return response
    return ResponseModel(**result.dict())
```

## WHAT TO DO IF YOU ENCOUNTER REMOVED FEATURES

If you encounter any of the following in the codebase:

- Permission checks (`require_permission`, `has_permission`)
- Feature flag checks (`require_feature_enabled`)
- Role level checks (`require_role_level`)
- Tenant isolation code (tenant_id filtering, etc.)
- The constants file `src.constants.rbac`
- The utils file `src.utils.permissions`

**STOP IMMEDIATELY** and:

1. Note the location of the code
2. Report it to the project maintainer
3. Do not modify the code until receiving guidance

## TESTING APPROACH

- Unit tests for services and utilities
- Integration tests for API endpoints
- Transaction tests to verify proper transaction management
- Authentication tests to verify security

## DEPLOYMENT CONFIGURATION

- Docker containerization
- Environment variables for configuration
- Supabase for authentication and database
- Connection pooling with Supavisor
