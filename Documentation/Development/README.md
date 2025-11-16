# Development Documentation

**Purpose:** How to write code that follows ScraperSky patterns.

**Philosophy:** Show AI the code to copy. Don't rely on docs to guide it.

---

## What's Inside

### CONTRIBUTING.md - The Essential Guide

**Purpose:** Everything you need to add features and write code

**Contents:**
1. **Quick Start** - Run tests, lint, docker
2. **Code Standards** - Async-first architecture
3. **Adding New Features** - Copy existing code patterns
4. **Critical Patterns (DO NOT VIOLATE)** - 5 mandatory patterns
5. **Anti-Patterns (Lessons Learned)** - Production incidents
6. **Testing** - How to run tests
7. **Code Review Checklist** - What to check before committing

**When to read:** Before writing any code

---

## Quick Reference

### The Golden Rules

1. **Show AI the Code to Copy**
   - Find existing similar code
   - Paste it in your prompt
   - Ask AI to follow that exact pattern

2. **Trust the Code**
   - The code is good
   - The architecture is solid
   - Don't "improve" patterns without understanding why they exist

3. **Don't Reinvent the Wheel**
   - Copy existing structures
   - Follow the same patterns
   - Test thoroughly

4. **Coordinate Cross-Layer Changes**
   - Read ADR-005 (ENUM Catastrophe) first
   - Plan backwards-compatible transitions
   - Change one layer at a time

5. **Follow Critical Patterns**
   - Supavisor parameters: DO NOT MODIFY
   - Routers own transactions
   - 3-phase for long operations
   - Dual-status for processable entities
   - Always add authentication

---

## Critical Patterns (DO NOT VIOLATE)

### 1. Supavisor Connection Parameters

**Reference:** `../Architecture/ADR-001-Supavisor-Requirements.md`

```python
# DO NOT MODIFY
connection_string = "...?raw_sql=true&no_prepare=true&statement_cache_size=0"
```

---

### 2. Transaction Boundary Ownership

**Reference:** `../Architecture/ADR-004-Transaction-Boundaries.md`

✅ **CORRECT:**
```python
# Router owns transaction
@router.post("/domains")
async def create_domain(session: AsyncSession = Depends(get_session_dependency)):
    async with session.begin():
        domain = await service.create_domain(session, data)
```

❌ **WRONG:**
```python
# Service creates transaction (NEVER DO THIS)
async def create_domain(session: AsyncSession, data):
    async with session.begin():  # ← BAD
        domain = Domain(**data)
```

---

### 3. Database Connection Management (Long Operations)

**Reference:** `../Architecture/ADR-004-Transaction-Boundaries.md`

✅ **CORRECT - 3-Phase Pattern:**
```python
# Phase 1: Quick DB
async with session.begin():
    domain = await session.get(Domain, id)
    domain.processing_status = "Processing"

# Phase 2: Slow operation (NO connection held)
metadata = await external_api.call(domain.url)

# Phase 3: Quick DB
async with session.begin():
    domain.metadata = metadata
    domain.processing_status = "Complete"
```

❌ **WRONG:**
```python
async with session.begin():
    domain = await session.get(Domain, id)
    metadata = await external_api.call(domain.url)  # ← CONNECTION TIMES OUT
    domain.metadata = metadata
```

---

### 4. Dual-Status for Processable Entities

**Reference:** `../Architecture/ADR-003-Dual-Status-Workflow.md`

```python
class Widget(BaseModel):
    curation_status: str  # New | Selected | Maybe | Discarded
    processing_status: str  # Queued | Processing | Complete | Failed
```

---

### 5. Always Add Authentication

```python
# Router-level (preferred)
router = APIRouter(..., dependencies=[Depends(get_current_user)])

# Endpoint-level
@router.get("/")
async def endpoint(current_user: dict = Depends(get_current_user)):
    pass
```

---

## Common Tasks

### Add a New API Endpoint

1. **Find pattern:** `src/routers/domains.py`
2. **Copy structure:**
   ```python
   @router.post("/widgets")
   async def create_widget(
       request: WidgetCreate,
       session: AsyncSession = Depends(get_session_dependency),
       current_user: dict = Depends(get_current_user)  # ← Auth
   ):
       async with session.begin():  # ← Router owns transaction
           widget = await widget_service.create(session, request)
           return widget
   ```
3. **Register:** Add to `src/main.py`
4. **Test:** Verify auth, transactions, error handling

---

### Add a New Background Job

1. **Find pattern:** `src/services/domain_scheduler.py`
2. **Copy 3-phase structure:**
   - Phase 1: Quick DB (fetch and mark)
   - Phase 2: Slow processing (no connection)
   - Phase 3: Quick DB (update results)
3. **Register:** Add to lifespan in `main.py`
4. **Test:** Run with small batch first

---

### Modify Database Schema

1. **✋ STOP** - Read `../Architecture/ADR-005-ENUM-Catastrophe.md`
2. **Impact analysis:** What layers are affected?
3. **Plan transition:** Backwards-compatible steps
4. **Execute layer-by-layer:**
   - Layer 1: Database (add new, keep old)
   - Layer 2: Services (support both)
   - Layer 3: Routers (prefer new, accept old)
   - Data migration
   - Remove old
5. **Test between each layer**

---

## Anti-Patterns (Don't Do This)

### Database Connection Long Hold

**What happened:** WF4 broken - `ConnectionDoesNotExistError`
**Why:** Held connection during 2-3 second API call
**Fix:** 3-phase pattern

### Double Transaction Management

**What happened:** Nested transaction deadlocks
**Why:** Both router and service creating transactions
**Fix:** Router owns transaction

### Invalid ENUM Reference

**What happened:** Status updates failing silently
**Why:** Using wrong ENUM values
**Fix:** Use actual database ENUM values

**Reference:** `CONTRIBUTING.md` → "Anti-Patterns" section

---

## Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_domains.py

# Fast tests only
pytest -q

# With coverage
pytest --cov=src --cov-report=html
```

---

## Code Review Checklist

### For All Changes
- [ ] Authentication added to all endpoints
- [ ] Routers own transactions, services don't create them
- [ ] All I/O uses async/await
- [ ] Proper error handling with HTTP exceptions
- [ ] Type hints on all functions

### For Database Changes
- [ ] No connections held during external API calls
- [ ] 3-phase pattern for long operations
- [ ] No modifications to Supavisor parameters

### For Schema Changes
- [ ] Impact analysis completed (all layers identified)
- [ ] Backwards-compatible transition planned
- [ ] ADR-005 reviewed (ENUM Catastrophe lessons)

### For New Endpoints
- [ ] Copied pattern from existing router
- [ ] Authentication added
- [ ] Transaction handling correct
- [ ] Router registered in main.py

---

## Getting Help

**I need to understand patterns:**
→ Read `CONTRIBUTING.md`

**I need to add a feature:**
→ Find similar code, copy its pattern

**I need to understand architecture:**
→ Read `../Architecture/` (ADRs)

**I need to understand workflows:**
→ Read `../Workflows/README.md`

**I'm stuck:**
→ Find existing code that does something similar, paste it in your prompt

---

## Summary

**One Essential Document:**
→ `CONTRIBUTING.md` - Read this before writing code

**5 Critical Patterns:**
1. Supavisor parameters: DO NOT MODIFY
2. Routers own transactions
3. 3-phase for long operations
4. Dual-status for processable entities
5. Always add authentication

**The Approach:**
1. Find existing similar code
2. Copy its structure exactly
3. Follow the same patterns
4. Test thoroughly
5. Commit and deploy

**Remember:** Show AI the code to copy. Don't rely on docs to guide it.
