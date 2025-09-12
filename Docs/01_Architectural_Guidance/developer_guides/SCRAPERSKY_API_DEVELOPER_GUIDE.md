# SCRAPERSKY API DEVELOPER GUIDE
*Mandatory Patterns, Conventions & Best Practices*

## 1. OVERVIEW
This guide documents the established, mandatory patterns for all API endpoint development in the ScraperSky backend. It consolidates several core architectural guides into a single source of truth. Adherence to these patterns is required to ensure consistency, maintainability, and stability.

---

## 2. ROUTER & ENDPOINT DEFINITION

### 2.1. API Versioning & Prefix Convention

**The Rule:** The main `FastAPI` app instance in `src/main.py` is responsible for applying the `/api/v3` prefix. Routers defined in `src/routers/` should **only** define the resource-specific part of their prefix.

*   **Source Guide:** `23-LAYER3_FASTAPI_ROUTER_PREFIX_CONVENTION.md`

**CORRECT ROUTER DEFINITION (`src/routers/my_router.py`):**
```python
# Note: No /api/v3 prefix here.
router = APIRouter(prefix="/my-resource", tags=["My Resource"])
```

**CORRECT INCLUSION (`src/main.py`):**
```python
# The /api/v3 prefix is added here.
app.include_router(my_router, prefix="/api/v3")
```

**ANTI-PATTERN:** Defining the full `/api/v3/my-resource` prefix in the router itself will cause FastAPI to create a duplicate path (`/api/v3/api/v3/...`), leading to 404 errors.

---

## 3. DEPENDENCY INJECTION

### 3.1. Database Session

**The Rule:** To get a database session inside an endpoint, you **MUST** use the `get_session_dependency` function.

*   **Source Guide:** `30-LAYER3_STANDARD_DEPENDENCY_INJECTION_PATTERNS.md`

**CORRECT IMPLEMENTATION:**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.session.async_session import get_session_dependency

@router.get("/items")
async def get_items(session: AsyncSession = Depends(get_session_dependency)):
    # Use the session object directly.
    # The dependency handles session lifecycle (creation, commit, rollback, close).
```

**ANTI-PATTERN:** Do not use `get_session` or `get_background_session` as FastAPI dependencies. Do not wrap the injected session in an `async with session.begin()` block at the router level, as the dependency already manages this.

### 3.2. Authentication

*   The pattern for authentication is to add `current_user: dict = Depends(get_current_user)` to the endpoint signature. This is documented in our other guides and should be followed.

---

## 4. TRANSACTION MANAGEMENT

**The Rule:** Routers own transactions; services do not.

*   **Source Guide:** `13-LAYER5_TRANSACTION_MANAGEMENT_GUIDE.md`

**CORRECT PATTERN:** The `get_session_dependency` from the previous step provides a session where the transaction is already managed. For more complex operations requiring an explicit transaction block within the endpoint, use `async with session.begin():`.

```python
@router.post("/items")
async def create_item(
    request: ItemCreateRequest,
    session: AsyncSession = Depends(get_session_dependency)
):
    # The dependency provides the session.
    # For explicit transaction control within the endpoint:
    async with session.begin():
        # This block is now an atomic transaction.
        result = await item_service.create(session=session, item_data=request.dict())
    return result
```

**ANTI-PATTERN:** Services or helper functions should NEVER call `session.commit()` or `session.rollback()` on a session that is passed into them. They operate within the transaction created by the router.

---

## 5. API SCHEMAS & RESPONSES

**The Rule:** All API responses must follow a standardized structure.

*   **Source Guide:** `15-LAYER2_API_STANDARDIZATION_GUIDE.md`

**SUCCESS RESPONSE:**
```json
{
  "status": "success",
  "data": { /* Operation-specific response data */ }
}
```

**ASYNC JOB RESPONSE:**
```json
{
  "job_id": "a-valid-uuid",
  "status": "pending",
  "status_url": "/api/v3/resource/status/a-valid-uuid"
}
```

**ERROR RESPONSE:**
*   Use `fastapi.HTTPException` to produce standard error responses.
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found.",
)
```
