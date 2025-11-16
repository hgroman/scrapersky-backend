# Architecture Decision Records (ADRs)

**Purpose:** Document critical architectural decisions that must NOT be violated.

**Why ADRs:** Prevent future developers (human or AI) from undoing hard-learned lessons.

---

## What is an ADR?

An **Architecture Decision Record** documents a significant architectural decision, including:
- **What** the decision is
- **Why** it was made
- **What** the consequences are
- **How** to enforce it

**ADRs are NOT:**
- Code documentation (that's in code comments)
- Implementation guides (that's in CONTRIBUTING.md)
- Historical learning journeys (that's archived)

**ADRs ARE:**
- Critical decisions that must be preserved
- Lessons learned the hard way (often through production incidents)
- Constraints that future code must respect

---

## The 5 Critical ADRs

### ADR-001: Supavisor Requirements

**TL;DR:** Database connection parameters are mandatory and immutable.

**The Rule:**
```python
# DO NOT MODIFY THESE PARAMETERS
connection_string = "...?raw_sql=true&no_prepare=true&statement_cache_size=0"
```

**Why:** Supavisor (Supabase connection pooler) requires these exact parameters. Changing them causes connection failures.

**When to read:** Before modifying `src/session/async_session.py`

---

### ADR-002: Removed Tenant Isolation

**TL;DR:** System is single-tenant by design. DO NOT add tenant filtering.

**The Rule:**
- No RLS (Row-Level Security)
- No application-layer tenant filtering
- All operations use `DEFAULT_TENANT_ID`

**Why:** Multi-tenancy complexity removed for operational simplicity.

**When to read:** Before adding tenant-related features

---

### ADR-003: Dual-Status Workflow

**TL;DR:** Processable entities have two statuses: `curation_status` + `processing_status`

**The Pattern:**
```python
class Domain(BaseModel):
    curation_status: str  # User decision: New, Selected, Maybe, Discarded
    processing_status: str  # System state: Queued, Processing, Complete, Failed
```

**Why:** Separates user intent from system state. Users can curate while system processes.

**When to read:** Before adding new processable entities

---

### ADR-004: Transaction Boundaries

**TL;DR:** Routers own transactions. Services execute within them.

**The Rule:**
```python
# Router (CORRECT)
@router.post("/domains")
async def create_domain(session: AsyncSession = Depends(get_session_dependency)):
    async with session.begin():  # ← Router owns transaction
        domain = await service.create_domain(session, data)

# Service (CORRECT)
async def create_domain(session: AsyncSession, data):
    # NO transaction creation here
    domain = Domain(**data)
    session.add(domain)
    await session.flush()  # Flush OK, commit NOT OK
    return domain
```

**Why:** Prevents deadlocks, clear responsibility.

**When to read:** Before writing new services or routers

---

### ADR-005: ENUM Catastrophe

**TL;DR:** Cross-layer changes require coordination. NEVER refactor across layers autonomously.

**The Incident:**
- Autonomous ENUM refactor broke entire system
- One week recovery time
- All workflows halted

**The Lesson:**
1. Identify ALL layers affected
2. Plan backwards-compatible transition
3. Change one layer at a time
4. Test between each layer

**When to read:** Before changing ENUMs, status fields, or database schema

---

## When to Create a New ADR

**Create an ADR when:**
- ✅ You make a decision that future developers MUST respect
- ✅ You learn a lesson the hard way (production incident)
- ✅ You establish a pattern that code MUST follow
- ✅ You remove a feature that should NOT be re-added

**Don't create an ADR for:**
- ❌ Every code change
- ❌ Implementation details
- ❌ Temporary experiments
- ❌ Personal preferences

---

## ADR Template

```markdown
# ADR-XXX: Title

**Status:** Active | Superseded | Deprecated
**Date:** YYYY-MM-DD
**Decision Makers:** Who decided
**Related Files:** src/path/to/affected/code.py

---

## Context

What problem are we solving? What's the background?

---

## Decision

What did we decide to do?

---

## Rationale

WHY did we make this decision?

---

## Consequences

### Positive
✅ Benefits of this decision

### Negative
⚠️ Trade-offs and downsides

---

## Implementation

Where is this enforced? How do we follow it?

---

## References

- Related docs
- Related code
- Related ADRs
```

---

## Reading Order for New Developers

**First Time:**
1. Read ADR-004 (Transaction Boundaries) - Most commonly violated
2. Read ADR-003 (Dual-Status Workflow) - Most commonly needed
3. Read ADR-001 (Supavisor Requirements) - Most critical to not break
4. Read ADR-005 (ENUM Catastrophe) - Historical warning
5. Read ADR-002 (Removed Tenant Isolation) - Context about what NOT to add

**Before Making Changes:**
1. Check if your change affects database connections → Read ADR-001
2. Check if your change adds transactions → Read ADR-004
3. Check if your change adds processable entities → Read ADR-003
4. Check if your change modifies ENUMs or schema → Read ADR-005
5. Check if your change adds tenant features → Read ADR-002

---

## Enforcing ADRs

**How ADRs are enforced:**
1. **Code comments** - Critical code marked with "DO NOT MODIFY" and ADR reference
2. **This documentation** - ADRs explain why patterns exist
3. **Code reviews** - Check for ADR violations
4. **CONTRIBUTING.md** - References ADRs in critical patterns section

**If you see code that violates an ADR:**
1. ✋ STOP
2. Read the ADR to understand why the rule exists
3. If the rule no longer applies, update the ADR (don't just violate it)
4. If the rule still applies, follow it

---

## Summary

**5 Critical Decisions:**
1. **Supavisor parameters** - DO NOT MODIFY
2. **No tenant isolation** - DO NOT add tenant filtering
3. **Dual-status pattern** - Use for processable entities
4. **Routers own transactions** - Services don't create transactions
5. **Coordinate cross-layer changes** - Don't refactor autonomously

**Remember:** These are lessons learned the hard way. Trust them.
