# Contributing to ScraperSky

**Welcome!** This guide helps you make changes to the ScraperSky codebase while following established patterns and avoiding common pitfalls.

**Philosophy:** Show AI the code to copy, don't rely on docs to guide it.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Code Standards](#code-standards)
3. [Adding New Features](#adding-new-features)
4. [Critical Patterns (Do NOT Violate)](#critical-patterns-do-not-violate)
5. [Anti-Patterns (Lessons Learned)](#anti-patterns-lessons-learned)
6. [Testing](#testing)
7. [Code Review Checklist](#code-review-checklist)

---

## Quick Start

### Development Environment

```bash
# Run tests
pytest -q

# Lint and format
ruff check .
ruff format .

# Run all pre-commit checks
pre-commit run --all-files

# Start development stack
docker compose up --build

# View logs
docker compose logs -f app
```

### File Discovery Audit

```bash
# Check for orphaned/phantom files
python tools/file_discovery.py
```

---

## Code Standards

### Async-First Architecture

✅ **ALWAYS use async/await:**
```python
# Services
async def create_domain(session: AsyncSession, domain_name: str) -> Domain:
    domain = Domain(domain_name=domain_name)
    session.add(domain)
    await session.flush()
    return domain

# Routers
@router.post("/domains")
async def create_domain_endpoint(
    request: DomainCreate,
    session: AsyncSession = Depends(get_session_dependency)
):
    async with session.begin():
        domain = await domain_service.create_domain(session, request.domain_name)
        return domain
```

❌ **NEVER use synchronous operations for I/O:**
```python
# WRONG
def create_domain(session, domain_name):  # Missing async
    result = session.execute(stmt)  # Missing await
```

---

## Adding New Features

### Pattern: Follow Existing Code

**Best Practice:** Find similar existing code and copy its structure exactly.

#### Example: Adding a New API Endpoint

**Step 1: Find the pattern**
```bash
# Find existing router with similar functionality
cat src/routers/domains.py
```

**Step 2: Copy the structure**
```python
# Your new router: src/routers/widgets.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.jwt_auth import get_current_user
from src.session.async_session import get_session_dependency
from src.services import widget_service

router = APIRouter(
    prefix="/api/v3/widgets",
    tags=["widgets"]
)

@router.post("/")
async def create_widget(
    request: WidgetCreate,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)  # ← Don't forget auth!
):
    """Create a new widget following domain.py pattern."""
    async with session.begin():  # ← Router owns transaction
        widget = await widget_service.create_widget(
            session,
            name=request.name,
            user_id=current_user["id"]
        )
        return widget
```

**Step 3: Register in main.py**
```python
# src/main.py
from src.routers import widgets

app.include_router(widgets.router)  # No prefix needed, router has full path
```

---

### Pattern: Dual-Status for Processable Entities

If your entity needs user curation AND background processing, use dual-status pattern.

**Reference:** `Documentation/Architecture/ADR-003-Dual-Status-Workflow.md`

**Example: Widget Model**
```python
# src/models/widget.py
from src.models.base_model import BaseModel

class Widget(BaseModel):
    __tablename__ = "widgets"

    name: Mapped[str] = mapped_column(String, nullable=False)

    # Dual-Status Pattern
    curation_status: Mapped[str] = mapped_column(
        String,
        default="New",
        index=True
    )
    # Values: New | Selected | Maybe | Discarded

    processing_status: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        index=True
    )
    # Values: Queued | Processing | Complete | Failed
```

**When user selects widget, auto-queue for processing:**
```python
@router.patch("/widgets/{widget_id}")
async def update_widget_curation(widget_id: UUID, request: WidgetUpdate):
    async with session.begin():
        widget = await session.get(Widget, widget_id)
        widget.curation_status = request.curation_status

        # Auto-queue if Selected
        if request.curation_status == "Selected":
            widget.processing_status = "Queued"

        return widget
```

---

## Critical Patterns (Do NOT Violate)

### 1. Supavisor Connection Parameters

**Reference:** `Documentation/Architecture/ADR-001-Supavisor-Requirements.md`

**CRITICAL:** These parameters are MANDATORY and IMMUTABLE:

```python
# src/session/async_session.py
connection_string = (
    f"postgresql+asyncpg://{user}:{password}@{host}:6543/{database}"
    f"?raw_sql=true&no_prepare=true&statement_cache_size=0"
)

# DO NOT MODIFY THESE PARAMETERS
# They are required for Supavisor compatibility
```

**Why:** Supavisor (Supabase connection pooler) requires these exact parameters. Changing them causes connection failures.

---

### 2. Transaction Boundary Ownership

**Reference:** `Documentation/Architecture/ADR-004-Transaction-Boundaries.md`

**Rule:** Routers own transactions. Services do NOT create transactions.

✅ **CORRECT - Router owns transaction:**
```python
# Router
@router.post("/domains")
async def create_domain(session: AsyncSession = Depends(get_session_dependency)):
    async with session.begin():  # ← Router creates transaction
        domain = await domain_service.create_domain(session, "example.com")
        await sitemap_service.queue_sitemap(session, domain.id)
        # Multiple services in ONE transaction
        return domain
```

```python
# Service
async def create_domain(session: AsyncSession, domain_name: str) -> Domain:
    # NO transaction creation here
    domain = Domain(domain_name=domain_name)
    session.add(domain)
    await session.flush()  # Flush OK, commit NOT OK
    return domain
```

❌ **WRONG - Service creates transaction:**
```python
# Service
async def create_domain(session: AsyncSession, domain_name: str):
    async with session.begin():  # ← BAD: Nested transaction
        domain = Domain(domain_name=domain_name)
        session.add(domain)
        await session.commit()  # ← BAD: Service commits
```

---

### 3. Database Connection Management (Long-Running Operations)

**Reference:** `Docs/Docs_27_Anti-Patterns/v_20250730_Database_Connection_Long_Hold_CRITICAL.md`

**Rule:** NEVER hold database connections during external API calls or slow operations.

✅ **CORRECT - 3-Phase Pattern:**
```python
async def process_domain(domain_id: UUID):
    # Phase 1: Quick DB - fetch and mark
    async with get_session() as session:
        async with session.begin():
            domain = await session.get(Domain, domain_id)
            domain.processing_status = "Processing"
    # Transaction ends, connection released

    # Phase 2: Slow operation WITHOUT database connection
    metadata = await scraper_api.extract_metadata(domain.url)  # 2-3 seconds

    # Phase 3: Quick DB - update results
    async with get_session() as session:
        async with session.begin():
            domain.processing_status = "Complete"
            domain.metadata = metadata
```

❌ **WRONG - Hold connection during API call:**
```python
async def process_domain(domain_id: UUID):
    async with get_session() as session:
        async with session.begin():
            domain = await session.get(Domain, domain_id)
            domain.processing_status = "Processing"

            # BAD: Connection held during slow external API call
            metadata = await scraper_api.extract_metadata(domain.url)  # ← CONNECTION TIMES OUT

            domain.metadata = metadata  # ← FAILS: Connection gone
```

**Why:** Supavisor connection timeouts. External API calls (ScraperAPI, Google Maps) take 2-3 seconds. Database connections timeout if held that long.

---

### 4. Tenant Isolation (Don't Add It)

**Reference:** `Documentation/Architecture/ADR-002-Removed-Tenant-Isolation.md`

**Rule:** System is single-tenant by design. Do NOT add tenant filtering.

✅ **CORRECT - No tenant filtering:**
```python
async def get_domains(session: AsyncSession) -> List[Domain]:
    stmt = select(Domain)
    # No tenant_id filtering
    result = await session.execute(stmt)
    return result.scalars().all()
```

❌ **WRONG - Adding tenant filtering:**
```python
async def get_domains(session: AsyncSession, tenant_id: UUID) -> List[Domain]:
    stmt = select(Domain).where(Domain.tenant_id == tenant_id)  # ← Don't add this
```

**Why:** Multi-tenant features were explicitly removed. `tenant_id` exists in schema for future use but is NOT enforced.

---

### 5. Cross-Layer Changes Require Coordination

**Reference:** `Documentation/Architecture/ADR-005-ENUM-Catastrophe.md`

**Rule:** NEVER refactor across layers autonomously. Coordinate layer-by-layer.

**Layers:**
- Layer 1: Database Schema (Models)
- Layer 2: Service Logic
- Layer 3: API Routers
- Plus: Schedulers, Integrations

**If changing ENUMs, status fields, or database schema:**

1. ✋ **STOP**
2. Read ADR-005
3. Perform impact analysis
4. Plan backwards-compatible transition
5. Change one layer at a time
6. Test between each layer

**Why:** The "ENUM Catastrophe" - autonomous refactor of all ENUMs broke entire system, took one week to recover.

---

## Anti-Patterns (Lessons Learned)

### Database Connection Long Hold

**Incident:** WF4 completely broken - `ConnectionDoesNotExistError`
**Root Cause:** Held database connection during 2-3 second ScraperAPI calls
**Fix:** 3-phase pattern (DB → API → DB)
**Reference:** `Docs/Docs_27_Anti-Patterns/v_20250730_Database_Connection_Long_Hold_CRITICAL.md`

### Double Transaction Management

**Incident:** Nested transaction deadlocks
**Root Cause:** Both router and service creating transactions
**Fix:** Router owns transaction, service executes within it
**Reference:** `Docs/Docs_27_Anti-Patterns/v_20250731_WF4_Double_Transaction_Management_CRITICAL.md`

### Invalid ENUM Reference

**Incident:** Status updates failing silently
**Root Cause:** Using wrong ENUM values (not matching database)
**Fix:** Always reference actual database ENUM values
**Reference:** `Docs/Docs_27_Anti-Patterns/20250731_WF4_Invalid_Enum_Reference_CRITICAL.md`

---

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_domains.py

# With coverage
pytest --cov=src --cov-report=html

# Fast (no slow tests)
pytest -q
```

### Test Patterns

**Async Test Pattern:**
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_domain(async_session: AsyncSession):
    """Test domain creation following existing patterns."""
    async with async_session.begin():
        domain = await domain_service.create_domain(
            async_session,
            domain_name="example.com"
        )

        assert domain.id is not None
        assert domain.domain_name == "example.com"
        assert domain.curation_status == "New"
```

---

## Code Review Checklist

### For All Changes

- [ ] **Authentication:** All endpoints have `Depends(get_current_user)` (unless explicitly public)
- [ ] **Transactions:** Routers own transactions, services do NOT create them
- [ ] **Async/Await:** All I/O operations use `async`/`await`
- [ ] **Error Handling:** Proper try/except with appropriate HTTP exceptions
- [ ] **Type Hints:** All function parameters and returns typed

### For Database Changes

- [ ] **Connection Management:** No connections held during external API calls
- [ ] **3-Phase Pattern:** Long operations use: DB → Compute → DB
- [ ] **Transaction Scope:** Single transaction per API request (router-owned)
- [ ] **Supavisor Parameters:** NO changes to connection string parameters

### For Schema Changes

- [ ] **Impact Analysis:** All affected layers identified
- [ ] **Migration Script:** Database migration created (if schema change)
- [ ] **Backwards Compatible:** Old data still works during transition
- [ ] **Cross-Layer Plan:** Layer-by-layer change plan documented
- [ ] **ADR-005 Review:** ENUM Catastrophe lessons applied

### For New Endpoints

- [ ] **Copied Pattern:** Followed existing router structure (e.g., `domains.py`)
- [ ] **Authentication:** `Depends(get_current_user)` added
- [ ] **Transaction:** `async with session.begin()` in router
- [ ] **Registered:** Router included in `main.py`
- [ ] **Dual-Status:** If processable entity, used curation_status + processing_status

---

## Common Pitfalls

### 1. Forgetting Authentication

```python
# WRONG - No auth
@router.get("/domains")
async def get_domains():
    pass

# CORRECT - Auth added
@router.get("/domains")
async def get_domains(current_user: dict = Depends(get_current_user)):
    pass
```

### 2. Service Creating Transaction

```python
# WRONG - Service owns transaction
async def create_domain(session: AsyncSession):
    async with session.begin():  # ← BAD
        pass

# CORRECT - Router owns transaction
@router.post("/domains")
async def create_domain(session: AsyncSession = Depends(get_session_dependency)):
    async with session.begin():  # ← GOOD (router)
        await domain_service.create_domain(session, "example.com")
```

### 3. Holding Connection During API Call

```python
# WRONG
async with session.begin():
    domain = await session.get(Domain, id)
    metadata = await external_api.call()  # ← Connection times out
    domain.metadata = metadata  # ← Fails

# CORRECT
async with session.begin():
    domain = await session.get(Domain, id)

metadata = await external_api.call()  # Connection released

async with session.begin():
    domain.metadata = metadata
```

### 4. Modifying Supavisor Parameters

```python
# WRONG - Changing parameters
connection_string = f"...?prepared_statements=true"  # ← BREAKS

# CORRECT - Use exact parameters
connection_string = f"...?raw_sql=true&no_prepare=true&statement_cache_size=0"
```

---

## Getting Help

### Architecture Decision Records (ADRs)

**Before making changes, read relevant ADRs:**
- `Documentation/Architecture/ADR-001-Supavisor-Requirements.md`
- `Documentation/Architecture/ADR-002-Removed-Tenant-Isolation.md`
- `Documentation/Architecture/ADR-003-Dual-Status-Workflow.md`
- `Documentation/Architecture/ADR-004-Transaction-Boundaries.md`
- `Documentation/Architecture/ADR-005-ENUM-Catastrophe.md`

### Code Analysis

**Comprehensive codebase documentation:**
- `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/00_START_HERE.md`

### Anti-Patterns Registry

**Learn from past mistakes:**
- `Docs/Docs_27_Anti-Patterns/v_README_Anti-Patterns_Registry.md`

---

## Summary: The Golden Rules

1. **Show AI the code to copy** - Don't rely on docs, paste existing code
2. **Routers own transactions** - Services execute within router transactions
3. **3-Phase for long operations** - DB → Compute → DB (never hold connections)
4. **Supavisor parameters are immutable** - DO NOT MODIFY connection string
5. **Coordinate cross-layer changes** - Never autonomous refactors across layers
6. **Dual-status for processable entities** - curation_status + processing_status
7. **Always add authentication** - `Depends(get_current_user)` unless explicitly public
8. **Async-first** - All I/O operations use async/await

---

**Remember:** The code works. Trust the patterns. Don't reinvent the wheel.

When adding features:
1. Find existing similar code
2. Copy its structure exactly
3. Follow the same patterns
4. Test thoroughly
5. Commit and deploy

**Keep it simple. Keep it working.**
