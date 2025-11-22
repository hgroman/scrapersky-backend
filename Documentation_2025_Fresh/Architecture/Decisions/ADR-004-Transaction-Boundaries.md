# ADR-004: Transaction Boundary Ownership

**Status:** Active
**Date:** 2025-11-16
**Decision Makers:** System Architecture
**Related Files:** `src/routers/*.py`, `src/services/*.py`

---

## Context

In async database applications, transactions define the scope of atomic operations. A transaction groups multiple database operations together - they all succeed or all fail.

**The Problem:** WHO is responsible for creating and managing transactions?

**Anti-Pattern Options:**
1. **Services create transactions** → Nested transaction deadlocks when routers also try
2. **Both create transactions** → Deadlocks and unpredictable behavior
3. **Neither creates transactions** → No atomicity guarantees

**The Challenge:** We need ONE clear owner of transaction boundaries.

---

## Decision

**Routers own transaction boundaries. Services are transaction-aware but do NOT create transactions.**

### Router Responsibility
✅ **Routers:**
- Create transactions using `async with session.begin()`
- Define the atomic boundary of an API request
- Handle transaction commit/rollback
- Catch exceptions and rollback

### Service Responsibility
✅ **Services:**
- Receive `session` as parameter
- Execute operations within the transaction
- Do NOT create new transactions
- Trust that router has transaction active

---

## Rationale

### Why Routers Own Transactions?

**1. Clear Scope**
- One API request = One transaction
- Easy to reason about: "This endpoint is atomic"
- Transaction scope matches user action

**2. Prevents Deadlocks**
- Only one level of transaction
- No nested transaction confusion
- No competing transaction managers

**3. Composable Services**
- Services can be called from multiple routers
- Each router defines its own transaction boundary
- Services don't assume transaction context

**4. Easier Testing**
- Mock session in service tests
- Test with or without transactions
- Router integration tests verify atomicity

---

## Implementation

### Router Pattern (CORRECT)

```python
# src/routers/domains.py
@router.post("/domains")
async def create_domain(
    request: DomainCreate,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)
):
    """Router owns the transaction boundary."""

    async with session.begin():  # ← Router creates transaction
        # All operations within this block are atomic
        domain = await domain_service.create_domain(
            session,
            domain_name=request.domain_name,
            user_id=current_user["id"]
        )

        # Can call multiple services in same transaction
        await sitemap_service.queue_sitemap_discovery(session, domain.id)

        # Transaction commits automatically at end of block
        return domain

    # If exception raised, transaction auto-rolls back
```

### Service Pattern (CORRECT)

```python
# src/services/domain_service.py
async def create_domain(
    session: AsyncSession,  # ← Receives session from router
    domain_name: str,
    user_id: UUID
) -> Domain:
    """Service is transaction-aware but does NOT create transaction."""

    # Executes within router's transaction
    domain = Domain(
        domain_name=domain_name,
        created_by=user_id,
        curation_status="New"
    )

    session.add(domain)
    await session.flush()  # ← Flush, not commit (router commits)

    return domain
```

### Scheduler Pattern (CORRECT)

Schedulers are like routers - they own their transaction boundaries:

```python
# src/services/domain_scheduler.py
async def process_domains_batch():
    """Scheduler creates its own transaction per batch."""

    async with get_session_context() as session:
        async with session.begin():  # ← Scheduler owns transaction
            domains = await domain_service.get_queued_domains(
                session,
                limit=batch_size
            )

            for domain in domains:
                await domain_service.process_domain(session, domain)

            # All domains in batch committed together
```

---

## Anti-Patterns (INCORRECT)

### ❌ Anti-Pattern 1: Service Creates Transaction

```python
# WRONG - Service creating transaction
async def create_domain(session: AsyncSession, domain_name: str):
    async with session.begin():  # ← BAD: Service owns transaction
        domain = Domain(domain_name=domain_name)
        session.add(domain)
        await session.commit()
        return domain
```

**Problem:**
- If router also has transaction, this creates nested transaction
- Deadlock risk
- Unclear who's responsible for rollback

### ❌ Anti-Pattern 2: Service Commits

```python
# WRONG - Service commits
async def create_domain(session: AsyncSession, domain_name: str):
    domain = Domain(domain_name=domain_name)
    session.add(domain)
    await session.commit()  # ← BAD: Service commits
    return domain
```

**Problem:**
- Commits before router is done
- Can't combine multiple service calls in one transaction
- Router loses control of atomicity

### ❌ Anti-Pattern 3: Router Passes Transaction Responsibility

```python
# WRONG - Router doesn't create transaction
@router.post("/domains")
async def create_domain(session: AsyncSession = Depends(get_session_dependency)):
    # No transaction created
    domain = await domain_service.create_domain(session, "example.com")
    # Service must create transaction - unclear ownership
    return domain
```

**Problem:**
- Unclear who owns transaction
- Service may or may not be atomic
- No guarantee of atomicity

---

## Consequences

### Positive

✅ **Clear Responsibility** - Routers always own transactions
✅ **No Deadlocks** - Only one transaction level
✅ **Composable Services** - Can combine multiple services atomically
✅ **Easier Testing** - Services don't require transaction context
✅ **Predictable Behavior** - One request = one transaction

### Negative

⚠️ **Router Complexity** - Routers must manage transactions
⚠️ **Discipline Required** - Services must NOT create transactions
⚠️ **Exception Handling** - Routers must handle rollback

### Trade-offs

**Sacrificed:** Service autonomy (services can't independently commit)
**Gained:** Clear ownership and predictable transaction behavior

---

## Transaction Lifecycle

### Typical Flow

```
1. Request arrives at router
   ↓
2. Router creates transaction: async with session.begin()
   ↓
3. Router calls service(s) passing session
   ↓
4. Service executes operations using session
   ↓
5. Service flushes (optional, for getting IDs)
   ↓
6. Service returns result
   ↓
7. Router commits transaction (end of `async with` block)
   ↓
8. Response returned to client
```

### Error Handling

```python
@router.post("/domains")
async def create_domain(session: AsyncSession = Depends(get_session_dependency)):
    try:
        async with session.begin():
            domain = await domain_service.create_domain(session, "example.com")
            return domain

    except ValueError as e:
        # Transaction auto-rolled back
        raise HTTPException(400, str(e))

    except Exception as e:
        # Transaction auto-rolled back
        logger.error(f"Failed to create domain: {e}")
        raise HTTPException(500, "Internal server error")
```

**Key Point:** Transaction auto-rolls back on exception. Router just needs to catch and respond.

---

## When to Commit/Flush

### Flush vs Commit

**`session.flush()`**
- Sends SQL to database but doesn't commit
- Useful for getting auto-generated IDs
- Stays within transaction
- Services can flush

**`session.commit()`**
- Commits the transaction permanently
- Can't rollback after this
- Only routers should commit
- Happens automatically at end of `async with session.begin()`

### Service Usage

```python
async def create_domain(session: AsyncSession, domain_name: str):
    domain = Domain(domain_name=domain_name)
    session.add(domain)

    # Flush to get auto-generated ID
    await session.flush()

    # Now domain.id is available
    logger.info(f"Created domain with ID: {domain.id}")

    return domain
    # Router commits later
```

---

## Enforcement

**This pattern is enforced through:**

1. **Code Reviews** - Check that services don't create transactions
2. **Linting** - Flag `session.commit()` in service files
3. **This ADR** - Documents the pattern
4. **Examples** - All existing routers follow this pattern

**When writing new code:**
- ✅ Routers: Create `async with session.begin()`
- ✅ Services: Accept `session` parameter, use but don't commit
- ✅ Schedulers: Create their own transactions (they're like routers)

---

## Special Cases

### Background Jobs (Schedulers)

**Schedulers are transaction owners** (like routers):

```python
async def process_batch():
    async with get_session_context() as session:
        async with session.begin():  # ← Scheduler owns transaction
            # Process batch atomically
            items = await service.get_items(session)
            for item in items:
                await service.process_item(session, item)
```

### Long-Running Operations

**Pattern: Quick DB → Release → Heavy Compute → Quick DB**

```python
async def process_domain():
    # Phase 1: Quick DB - fetch and mark
    async with session.begin():
        domain = await service.get_queued_domain(session)
        domain.processing_status = "Processing"
    # Transaction commits here

    # Phase 2: Release connection, do heavy work
    result = await heavy_computation(domain)

    # Phase 3: Quick DB - update results
    async with session.begin():
        domain.processing_status = "Complete"
        domain.result = result
    # Transaction commits here
```

**Rationale:** Prevents holding database connections during long operations.

---

## Related Decisions

- **ADR-001:** Supavisor Requirements (these connections are used in transactions)
- **ADR-003:** Dual-Status Workflow (status updates happen in transactions)

---

## References

- **Router Examples:** `src/routers/domains.py`, `src/routers/modernized_page_scraper.py`
- **Service Examples:** `src/services/domain_service.py`, `src/services/places/places_service.py`
- **Scheduler Examples:** `src/services/domain_scheduler.py`, `src/services/sitemap_scheduler.py`
- **Analysis:** `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/01_ARCHITECTURE.md` (Transaction Pattern section)

---

## Revision History

- **2025-11-16:** Initial ADR documenting transaction boundary ownership pattern
