# ADR-005: The ENUM Catastrophe - Coordinating Cross-Layer Changes

**Status:** Active
**Date:** 2025-11-16
**Decision Makers:** Learned from Production Incident
**Incident Date:** ~July-August 2025
**Related Files:** All models, services, routers (affected entire codebase)

---

## Context

ScraperSky has a layered architecture:
- **Layer 1:** Database Schema (Models)
- **Layer 2:** Service Logic
- **Layer 3:** API Routers
- **Additional Layers:** Schedulers, External Integrations, etc.

Changes often span multiple layers. For example, changing a database ENUM affects:
- Database schema (migrations)
- SQLAlchemy models (Layer 1)
- Service validation logic (Layer 2)
- API request/response models (Layer 3)
- Frontend expectations (external)

**The Incident:** An autonomous refactor of all database ENUMs broke the entire system and required one week to recover.

---

## What Happened (The ENUM Catastrophe)

### The Trigger

A well-intentioned change attempted to refactor all ENUM definitions across the codebase:
- Standardize ENUM naming conventions
- Update database schema
- Update model definitions
- Update validation logic

**The approach:** Autonomous refactor executed without full impact analysis.

### What Broke

**Layer 1 (Database):**
- Database migrations changed ENUM values
- Existing data no longer matched new ENUMs
- Constraints violated

**Layer 2 (Services):**
- Service logic still used old ENUM values
- Validation checks failed
- Business logic broken

**Layer 3 (Routers):**
- API contracts changed
- Request validation rejected valid requests
- Response serialization failed

**Workflows:**
- Schedulers stopped working (ENUM mismatches)
- Background jobs failed
- Processing pipelines halted

### Impact

- **Duration:** One week to identify all breakages and fix
- **Scope:** Entire system affected
- **Data:** Some records left in inconsistent state
- **Operations:** All workflows halted during recovery

---

## Decision

**NEVER perform autonomous cross-layer refactors. ALWAYS coordinate changes that span architectural layers.**

### Mandatory Process for Cross-Layer Changes

**1. Impact Analysis (REQUIRED)**
- Identify ALL layers affected by the change
- Search codebase for ALL references (not just obvious ones)
- Check for dependent systems (frontend, schedulers, external APIs)
- Document expected impact

**2. Layer-by-Layer Planning**
- Plan changes for each layer separately
- Identify dependencies between layers
- Determine safe order of changes
- Plan rollback strategy per layer

**3. Testing Strategy**
- Unit tests per layer
- Integration tests across layers
- End-to-end tests for workflows
- Test rollback procedures

**4. Incremental Deployment**
- Change one layer at a time
- Verify each layer before proceeding
- Allow rollback at each step
- Monitor for unexpected breakage

---

## Rationale

### Why This Rule Exists

**1. Hidden Dependencies**
- ENUM values used in:
  - Database constraints
  - Service validation
  - API contracts
  - Frontend dropdowns
  - Background job logic
  - Integration tests
  - Documentation

**2. Data Migration Complexity**
- Changing ENUMs requires migrating existing data
- Can't just update the definition
- Need to handle records with old values

**3. Rollback Difficulty**
- Once data migrated, hard to rollback
- Multiple layers must rollback together
- Inconsistent state if partial rollback

**4. Testing Incompleteness**
- Unit tests pass but integration fails
- Each layer works independently
- But layers don't work together

---

## Lessons Learned

### What We Should Have Done

**Correct Approach for ENUM Refactor:**

```
1. Analysis Phase (1 day)
   - Search for ALL ENUM references: grep -r "old_enum_value"
   - Document every file that needs changing
   - Identify data migration needs

2. Planning Phase (1 day)
   - Write migration script for database data
   - Plan changes per layer:
     * Layer 1: Add new ENUM values (don't remove old yet)
     * Layer 2: Support both old and new values
     * Layer 3: API accepts both, returns new
   - Plan backwards-compatible transition

3. Implementation Phase (2-3 days)
   - Step 1: Add new ENUM values (backwards compatible)
   - Step 2: Migrate data to new values
   - Step 3: Update services to use new values
   - Step 4: Update routers to prefer new values
   - Step 5: Remove old ENUM values (only after all data migrated)

4. Testing Phase (1 day)
   - Test each layer independently
   - Test integration between layers
   - Test with existing data
   - Test rollback procedure

5. Deployment
   - Deploy incrementally
   - Monitor each step
   - Rollback plan ready
```

**Total time:** 5-6 days planned vs 1 week crisis recovery.

**The difference:** Planned migration vs emergency fixes.

---

## Anti-Patterns (What NOT To Do)

### ❌ Anti-Pattern 1: Autonomous Cross-Layer Refactor

```python
# WRONG - Changing ENUM everywhere at once
# database/migration.py
ALTER TYPE status_enum RENAME VALUE 'old_value' TO 'new_value';

# models/domain.py
status: Mapped[str] = mapped_column(Enum('new_value'))  # Changed

# services/domain_service.py
if domain.status == 'new_value':  # Changed

# routers/domains.py
class DomainStatus(str, Enum):
    VALUE = 'new_value'  # Changed
```

**Problem:** All layers changed simultaneously. If one breaks, all break.

### ❌ Anti-Pattern 2: Database-First Migration

```python
# WRONG - Changing database before application code
# migration.sql
ALTER TYPE status_enum DROP VALUE 'old_value';
ALTER TYPE status_enum ADD VALUE 'new_value';
```

**Problem:** Application still uses 'old_value', now database rejects it.

### ❌ Anti-Pattern 3: No Data Migration

```python
# WRONG - Changing definition without migrating data
# Old enum: ['pending', 'complete']
# New enum: ['queued', 'done']

# Just update the definition
class Status(str, Enum):
    QUEUED = 'queued'  # Was 'pending'
    DONE = 'done'       # Was 'complete'
```

**Problem:** Existing data has 'pending' and 'complete', no longer valid.

---

## Correct Patterns

### ✅ Pattern 1: Backwards-Compatible Transition

```python
# Step 1: Add new values alongside old (database migration)
ALTER TYPE status_enum ADD VALUE 'queued';
ALTER TYPE status_enum ADD VALUE 'done';
# Don't remove 'pending' and 'complete' yet

# Step 2: Update model to support both
class Status(str, Enum):
    PENDING = 'pending'  # Old (deprecated)
    COMPLETE = 'complete'  # Old (deprecated)
    QUEUED = 'queued'    # New (preferred)
    DONE = 'done'        # New (preferred)

# Step 3: Migrate data
UPDATE domains SET status = 'queued' WHERE status = 'pending';
UPDATE domains SET status = 'done' WHERE status = 'complete';

# Step 4: Update application to use new values
# Services, routers, etc. use 'queued' and 'done'

# Step 5: Remove old values (after verification)
ALTER TYPE status_enum DROP VALUE 'pending';
ALTER TYPE status_enum DROP VALUE 'complete';
```

### ✅ Pattern 2: Layer-by-Layer Coordination

```python
# Layer 1: Database (first)
# Add new ENUM values (backwards compatible)

# Layer 2: Services (second)
# Accept both old and new, use new internally

# Layer 3: Routers (third)
# Accept both in requests, return new in responses

# Data Migration (fourth)
# Migrate all existing records

# Cleanup (fifth)
# Remove old ENUM values from all layers
```

---

## Consequences

### Positive

✅ **No More Catastrophic Refactors** - Incremental changes only
✅ **Coordinated Changes** - Layers changed in safe order
✅ **Rollback Possible** - Can revert at each step
✅ **Data Integrity** - Migration planned before schema change

### Negative

⚠️ **Slower Refactors** - Multi-step process takes longer
⚠️ **Temporary Duplication** - Support both old and new during transition
⚠️ **More Planning Required** - Must think through impact

### Trade-offs

**Sacrificed:** Speed of autonomous refactors
**Gained:** System stability and data integrity

---

## Enforcement

**This decision is enforced through:**

1. **Code Reviews** - Check for cross-layer changes, require coordination plan
2. **This ADR** - Documents the lesson and correct approach
3. **Team Knowledge** - War story shared to prevent recurrence
4. **CI/CD Gates** - Migration review required for schema changes

**Before making cross-layer changes:**
1. Read this ADR
2. Complete impact analysis
3. Write coordination plan
4. Get review approval
5. Execute incrementally

---

## Related Decisions

- **ADR-003:** Dual-Status Workflow (ENUM-heavy design, must coordinate changes)
- **Architecture:** Layered design requires coordinated cross-layer changes

---

## References

- **Incident Documentation:** `Docs/Docs_21_SeptaGram_Personas/Guardian_Operational_Manual.md` (references the catastrophe)
- **Persona Audit:** `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/PERSONA_AUDIT_2025-11-16.md`
- **Lesson:** Real production incident, one week recovery time

---

## Key Takeaway

**"Don't optimize autonomously across layers. Coordinate deliberately across layers."**

The ENUM catastrophe taught us that moving fast and breaking things works in some contexts, but NOT when changing foundational data structures across a layered architecture.

**When in doubt:**
- Slower and coordinated > Faster and broken
- Backwards-compatible transition > Big-bang migration
- Plan the rollback > Hope it works

---

## Revision History

- **2025-11-16:** Initial ADR documenting ENUM catastrophe lesson learned
