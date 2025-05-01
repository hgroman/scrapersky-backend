# Transaction Management Guide: ScraperSky Backend

## Critical Issue Identified

We have identified a **systemic architectural inconsistency** across the ScraperSky backend regarding database transaction management. This inconsistency is causing numerous failures including:

- Transaction conflicts ("transaction already begun" errors)
- Session handling errors
- Race conditions in database operations
- Unpredictable API behavior

The root problem is **inconsistent transaction boundary ownership** between routers and services.

## Core Architectural Policy

To ensure system stability and consistent behavior, we hereby establish this architectural policy:

### 1. Transaction Boundary Ownership

**ROUTERS OWN TRANSACTION BOUNDARIES, SERVICES DO NOT.**

- Routers are responsible for starting, committing, and rolling back transactions
- Services must never start their own transactions independently
- Services should operate on the session passed from routers

### 2. Implementation Pattern

```python
# CORRECT PATTERN

# In Router (transaction owner):
@router.get("/endpoint")
async def endpoint(db: AsyncSession = Depends(get_db)):
    async with db.begin():  # Transaction starts and commits here
        # Pass the session to service
        result = await some_service.do_something(db)
        return result

# In Service (session user):
async def do_something(session: AsyncSession):
    # Just use the session, don't start transactions
    result = await session.execute(select(Entity))
    return result.scalars().all()
```

### 3. Anti-Patterns to Avoid

```python
# INCORRECT PATTERN - DOUBLE TRANSACTION

# In Router:
@router.get("/endpoint")
async def endpoint(db: AsyncSession = Depends(get_db)):
    async with db.begin():  # Transaction starts here
        # DON'T call a service that also starts a transaction
        result = await some_service.do_something(db)  # CONFLICT!
        return result

# In Service:
async def do_something(session: AsyncSession):
    async with session.begin():  # CONFLICT! Transaction already started in router
        result = await session.execute(select(Entity))
        return result.scalars().all()
```

## Action Items

1. **Audit All Routers and Services** - Review for transaction management issues
2. **Standardize Implementation** - Apply consistent pattern throughout
3. **Add Documentation** - Update service and router docstrings
4. **Code Review** - Add transaction boundary review to PR checklist

## Why This Matters

Inconsistent transaction management affects:

- **Reliability**: Failures when transactions conflict
- **Scalability**: Poor connection pool utilization
- **Performance**: Unnecessary transaction overhead
- **Debuggability**: Hard-to-trace errors

By following this architectural policy, we ensure database interactions remain consistent, predictable, and maintainable across the entire application.
