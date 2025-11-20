# ScraperSky Backend Architecture Constitution

> [!IMPORTANT]
> **The Guardian's Paradox**: We do exactly what is asked, nothing more. Database modifications are forbidden. Initiative beyond scope is catastrophe.

This document formalizes the core architectural principles of the ScraperSky backend. It serves as the source of truth for all development, ensuring consistency, stability, and adherence to the "Guardian" philosophy.

## 1. Core Principles

### 1.1. Truth in Code
The code itself must clearly convey design principles. If a pattern is "standard," it must be reflected in the codebase, not just in external documentation.
- **Action**: Use explicit naming, clear directory structures, and consistent patterns.

### 1.2. The "No Initiative" Rule
AI agents and developers must execute specific tasks without "improving" unrelated areas.
- **Constraint**: Do not refactor code outside the immediate scope of the ticket.
- **Constraint**: Never modify database schemas (ENUMs, tables) unless explicitly tasked.

## 2. Database Interaction

### 2.1. ORM Only
We exclusively use SQLAlchemy ORM for database interactions.
- **Rule**: No raw SQL `update()` or `insert()` statements in application code (except for specific, approved bulk operations or migrations).
- **Pattern**: Fetch object -> Modify attributes -> Commit.
- **Why**: Ensures lifecycle hooks run, history is tracked, and logic is centralized in the model.

### 2.2. Router-Owned Sessions
API Routers are the "Traffic Controllers" and own the transaction boundary.
- **Pattern**:
  ```python
  @router.post("/items")
  async def create_item(session: AsyncSession = Depends(get_db_session)):
      async with session.begin():
          # ... service calls ...
  ```
- **Constraint**: Services generally accept an active `session` as an argument. They do not create their own sessions unless they are background tasks.

### 2.3. Supavisor Compatibility
The system is designed to run on Supabase with Supavisor connection pooling.
- **Mandatory Settings**:
  - `raw_sql=True`
  - `no_prepare=True`
  - `statement_cache_size=0`
- **Constraint**: Never remove these settings from `src/config/settings.py` or `src/db/engine.py`.

## 3. Code Organization

### 3.1. Schema Extraction
Pydantic models (Schemas) must be defined in `src/schemas/`, not inline within routers.
- **Rule**: Routers should only contain route definitions and logic flow.
- **Benefit**: Reusability and cleaner router files.

### 3.2. Service Layer
Services contain business logic.
- **Signature**: Service methods should accept `session: AsyncSession` as the first argument (where applicable).
- **Background Tasks**: Services running in the background (e.g., schedulers) must manage their own sessions using `get_background_session()`.

## 4. Infrastructure

### 4.1. Deployment
- **Platform**: Render.com
- **Containerization**: Docker (Production & Dev)

### 4.2. Authentication
- **Mechanism**: Dependency Injection (`get_current_user`).
- **Constraint**: No global middleware for Auth/RBAC.

---
*Verified and Ratified: 2025-11-19*
