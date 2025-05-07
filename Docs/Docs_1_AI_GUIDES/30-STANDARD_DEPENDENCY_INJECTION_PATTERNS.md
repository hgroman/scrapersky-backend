# Standard Dependency Injection Patterns for ScraperSky

**Version:** 1.0
**Date:** [Current Date]
**Purpose:** This document serves as the authoritative guide for common and mandatory dependency injection patterns within the ScraperSky backend. Adherence to these patterns is crucial for consistency, maintainability, and ensuring that AI assistants can reliably locate and utilize core project components.

---

## 1. FastAPI Asynchronous Database Session Dependency

**Objective:** To provide a standardized, project-wide method for injecting an SQLAlchemy `AsyncSession` into FastAPI router endpoints.

**Mandatory Import and Usage:**

When an asynchronous database session is required within a FastAPI endpoint, the **ONLY** approved method for dependency injection is as follows:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# CORRECT AND MANDATORY IMPORT:
from src.session.async_session import get_session_dependency

# ... other necessary imports ...

router = APIRouter()

@router.get("/example-items")
async def get_example_items(
    session: AsyncSession = Depends(get_session_dependency) # Standard usage
):
    # Use the session object directly for database operations
    # Example:
    # result = await session.execute(select(Item).where(Item.is_active == True))
    # items = result.scalars().all()
    # return items
    pass # Replace with actual endpoint logic
```

**Key Details:**

- **File Location of `get_session_dependency`:** The `get_session_dependency` function is definitively located in the file `src/session/async_session.py`.
- **Function Purpose:** This function is specifically designed as a FastAPI dependency that provides a managed `AsyncSession`. It handles session creation, commit/rollback, and closing.
- **No Redundant Context Managers:** The session yielded by `get_session_dependency` is already managed. Do **NOT** wrap it in an additional `async with session:` or `async with session.begin():` block directly within the endpoint signature's scope if you are just using it for ORM operations that the dependency manager handles. For explicit transaction control _within_ the endpoint, use `async with session.begin():` as per standard SQLAlchemy practice with an already-provided session.

**Rationale & Supporting Documentation:**

The standardization of this import and usage pattern is based on analysis of the existing codebase and project documentation. Multiple sources confirm the location and intended use of `get_session_dependency` in `src/session/async_session.py`. These include, but are not limited to:

- **`Docs/Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md`**: Discusses session dependency and correct usage patterns, referencing `get_session_dependency`.
- **`Docs/Docs_4_ProjectDocs/905-PROJECT-UNDERSTANDING.md`**: Contains examples showing `get_session_dependency` from `src/session/async_session.py`.
- **`Docs/Docs_5_Project_Working_Docs/07-database-connection-audit/07-70-Dependency-Map-ALL-Routes`**: Illustrates `get_session_dependency` as a core part of the data access layer originating from `src/session/async_session.py`.
- **`Docs/Docs_0_SQL-Alchemy-Over-Engineered-Nightmare/65-Synthesized Documentation Suite for ScraperSky RBAC Implementation.md`**: Shows `get_session_dependency` in context.
- **`Docs/Docs_5_Project_Working_Docs/41-Code-Audit-And-Archive/41.22-DTree-Batch-Domain-Scanner.md`**: Lists `src.session.async_session: get_session_dependency` as a direct dependency for routers.
- **`Docs/Docs_4_ProjectDocs/920-DB-CONSOLIDATION_SUMMARY-2025-03-24.md`**: Provides examples of router patterns using this dependency.

**Common Pitfalls to Avoid:**

- **Incorrect Import Paths:** Using older or incorrect paths such as `src.db.session` or `src.db.dependencies` will result in import errors.
- **Using `get_session` or `get_background_session` as direct FastAPI dependencies:** These functions from `src/session/async_session.py` have different purposes (typically for direct invocation or background tasks) and are not intended for FastAPI dependency injection in route handlers. `get_session_dependency` is specifically tailored for this.

---

## 2. Other Standard Dependencies (To Be Expanded)

This section will be expanded to include other standardized dependency injection patterns as they are identified and mandated (e.g., for configuration, logging, authentication/user context).

---

This guide should be considered the primary reference for these dependency patterns. Workflow-specific cheat sheets and other documentation should refer back to this guide for these core concerns.
