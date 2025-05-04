# Core Architectural Principles

This document outlines the core architectural principles that should guide all development in the ScraperSky Backend. These principles have been extracted from our recent work and successes, particularly with the sitemap scanner and database connection optimizations.

## 1. Connection Management

- **ALWAYS use Supavisor connection pooling** - Never use direct connections
- **Connection pooler parameters are required** for all database-intensive endpoints
- **Disable prepared statements** with `raw_sql=true`, `no_prepare=true`, and `statement_cache_size=0` when needed
- **Sessions should not be shared** across asynchronous contexts

## 2. Responsibility Boundaries

- **Routers OWN transactions** - They begin, commit, and rollback transactions
- **Services are transaction-AWARE** - They work within existing transactions but don't manage them
- **Background jobs manage their OWN sessions/transactions** - They create sessions for their complete lifecycle

## 3. UUID Standardization

- **All UUIDs must be proper UUIDs** - No prefixes or custom formats
- **Use PostgreSQL UUID type** in database schema
- **Handle type conversion gracefully** - Convert strings to UUIDs as needed
- **Use PGUUID SQLAlchemy type** for UUID columns

## 4. Authentication & Authorization Boundaries ⚠️ CRITICAL

- **⚠️ JWT authentication happens ONLY at API gateway/router level** - This is a STRICT boundary
- **Database operations must NEVER handle JWT authentication or verification**
- **Services must be authentication-agnostic** - They should receive user IDs, not tokens
- **Authorization checks belong in routers** - Not in services or models
- **Always have test user information available** - See [10-TEST_USER_INFORMATION.md](/AI_GUIDES/10-TEST_USER_INFORMATION.md)

## 5. Error Handling

- **Provide detailed error messages** - Include error type and description
- **Log errors with context** - Include job IDs, domain information, etc.
- **Handle database errors gracefully** - Use try/except blocks around database operations
- **Validate inputs before processing** - Check for required fields, valid formats, etc.

## 6. Testing Approach

- **Always test with real user credentials** - Use the documented test users
- **Test boundary conditions** - Empty results, large results, etc.
- **Test error conditions** - Invalid inputs, database errors, etc.
- **Use integration tests** to verify complete flows

## 7. Code Quality

- **Fix linter errors immediately** - Don't let them accumulate
- **Use consistent naming conventions** - snake_case for Python, camelCase for JavaScript
- **Document public interfaces** - Provide docstrings for all public functions
- **Follow type safety practices** - Use type hints and handle type conversions properly

## 8. Project Organization

- **Services should have a single responsibility**
- **Routers should be thin** - Business logic belongs in services
- **Models should match database schema** - Use alembic for migrations
- **Documentation should be current** - Update docs when code changes

## 9. Deployment Pipeline

- **Always test locally before deploying**
- **Use staging environments** for final verification
- **Monitor deployments** for unexpected errors
- **Roll back quickly** if issues are detected

## 10. Development Workflow

- **Work from a clear specification**
- **Document changes** in project-docs
- **Update AI_GUIDES** when architectural decisions are made
- **Test thoroughly** before considering work complete

---

By following these principles, we ensure that the codebase remains maintainable, scalable, and reliable as we continue to develop new features and fix issues.
