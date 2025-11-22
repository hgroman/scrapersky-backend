# Critical Patterns (Must Follow)

**Document:** 07_CRITICAL_PATTERNS.md  
**Type:** Reference  
**Importance:** CRITICAL - Do not violate these patterns

---

## Overview

These patterns are NON-NEGOTIABLE. They are based on hard-learned lessons from ScraperSky production deployment.

---

## 1. Supavisor Connection Parameters

### The Pattern (MANDATORY)

```python
# In connect_args
connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
}

# In execution_options
execution_options = {
    "isolation_level": "READ COMMITTED",
    "no_prepare": True,
    "raw_sql": True,
}
```

### Why This Matters

Supabase uses Supavisor for connection pooling. These parameters are REQUIRED for compatibility. Without them, you'll get:
- `prepared statement does not exist` errors
- Connection pool exhaustion
- Random disconnects

### Reference

See `src/db/engine.py` lines 140-192 in ScraperSky

---

## 2. Transaction Boundaries

### The Pattern (MANDATORY)

**Routers own transactions:**
```python
@router.post("/items")
async def create_item(
    data: ItemCreate,
    session: AsyncSession = Depends(get_session_dependency)
):
    # Service creates item
    item = await ItemService.create_item(session, data)
    
    # Router commits transaction
    await session.commit()
    await session.refresh(item)
    
    return item
```

**Services execute within transactions:**
```python
class ItemService:
    @staticmethod
    async def create_item(session: AsyncSession, data: ItemCreate):
        item = Item(**data.dict())
        session.add(item)
        await session.flush()  # NOT commit!
        return item
```

### Why This Matters

- Clear responsibility
- Prevents deadlocks
- Enables proper error handling
- Services remain testable

### What NOT To Do

❌ **Never do this in services:**
```python
async def create_item(data):
    async with get_session() as session:  # DON'T CREATE TRANSACTIONS
        item = Item(**data.dict())
        session.add(item)
        await session.commit()  # DON'T COMMIT IN SERVICES
```

---

## 3. Dual-Status Workflow Pattern

### The Pattern (MANDATORY for processable entities)

```python
class ProcessableEntity(Base):
    # User-facing status (user decisions)
    curation_status: Mapped[str] = mapped_column(String(50))
    
    # System-facing status (scheduler tracking)
    processing_status: Mapped[str] = mapped_column(String(50))
```

**Adapter converts between statuses:**
```python
if entity.curation_status == "Selected":
    entity.processing_status = "Queued"
```

**Scheduler queries processing_status:**
```python
entities = await session.execute(
    select(Entity).where(Entity.processing_status == "Queued")
)
```

### Why This Matters

- Separates user intent from system state
- Enables reliable background processing
- Prevents race conditions
- Clear audit trail

### When To Use

Use dual-status when:
- Users select items for processing
- Background schedulers process items
- Processing can fail and retry
- You need to track both "what user wants" and "what system is doing"

---

## 4. 3-Phase Long Operations

### The Pattern (MANDATORY for operations >1 second)

```python
# Phase 1: Write to database (fast)
async def queue_processing(session: AsyncSession, item_id: str):
    item = await get_item(session, item_id)
    item.processing_status = "Queued"
    await session.commit()
    # Release database connection here

# Phase 2: Perform computation (no DB connection)
async def process_item_background(item_id: str):
    # Long-running operation
    result = await expensive_api_call(item_id)
    return result

# Phase 3: Write results back (fast)
async def save_results(session: AsyncSession, item_id: str, result):
    item = await get_item(session, item_id)
    item.result = result
    item.processing_status = "Complete"
    await session.commit()
```

### Why This Matters

- Prevents connection pool exhaustion
- Enables horizontal scaling
- Improves reliability
- Reduces database load

### What NOT To Do

❌ **Never hold connections during long operations:**
```python
async def process_item(session: AsyncSession, item_id: str):
    item = await get_item(session, item_id)
    
    # DON'T DO THIS - holds connection for minutes
    result = await expensive_api_call()  # Takes 30 seconds
    
    item.result = result
    await session.commit()
```

---

## 5. Centralized Enums

### The Pattern (MANDATORY)

**All enums in one file:**
```python
# src/models/enums.py

from enum import Enum

class ItemStatus(str, Enum):
    Pending = "Pending"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"

class UserRole(str, Enum):
    Admin = "Admin"
    User = "User"
```

### Why This Matters

- Single source of truth
- Prevents duplication
- Easy to maintain
- Prevents enum drift

### What NOT To Do

❌ **Never define enums in multiple files:**
```python
# models/item.py
class ItemStatus(Enum):  # DON'T
    Pending = "Pending"

# services/item_service.py  
class ItemStatus(Enum):  # DON'T DUPLICATE
    Pending = "Pending"
```

---

## 6. Async Session Management

### The Pattern (MANDATORY)

**Use dependency injection:**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.session.async_session import get_session_dependency

@router.get("/items")
async def list_items(
    session: AsyncSession = Depends(get_session_dependency)
):
    # Session automatically managed
    items = await ItemService.list_items(session)
    return items
```

### Why This Matters

- Automatic session cleanup
- Proper error handling
- Connection pooling
- Testability

---

## 7. Retry Logic with Exponential Backoff

### The Pattern (RECOMMENDED for external APIs)

```python
async def call_external_api_with_retry(item_id: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            result = await external_api_call(item_id)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff: 5min, 10min, 20min
            delay_minutes = 5 * (2 ** attempt)
            await asyncio.sleep(delay_minutes * 60)
```

### Why This Matters

- Handles temporary failures
- Doesn't hammer failing services
- Gives time for service recovery
- Reduces wasted API calls

---

## Pattern Violations = Technical Debt

These patterns exist because:
1. They solve real production problems
2. Alternatives were tried and failed
3. Recovery from violations is expensive

**When in doubt, follow the pattern.**

---

## Reference

For complete implementations, see:
- **Supavisor:** `src/db/engine.py`
- **Transactions:** `src/routers/wf7_page_modernized_scraper_router.py`
- **Dual-Status:** `src/services/wf7_page_curation_service.py`
- **3-Phase:** `src/services/background/wf5_sitemap_import_scheduler.py`
- **Enums:** `src/models/enums.py`

---

**Status:** ✅ Critical patterns documented
