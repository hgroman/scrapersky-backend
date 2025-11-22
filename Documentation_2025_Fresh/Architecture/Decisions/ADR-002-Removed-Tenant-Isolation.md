# ADR-002: Removed Tenant Isolation

**Status:** Active
**Date:** 2025-11-16
**Decision Makers:** System Architecture
**Supersedes:** Prior multi-tenant architecture
**Related Files:** `src/models/base_model.py`, `src/config/settings.py`

---

## Context

ScraperSky's database schema includes `tenant_id` columns across all major tables (inherited from `BaseModel`). This suggests a multi-tenant architecture with tenant isolation.

**Historical State:** The system previously implemented (or planned to implement):
- Row-Level Security (RLS) via Supabase
- JWT-based tenant context
- Per-tenant data isolation
- Role-Based Access Control (RBAC)

**Current Reality:** None of this is enforced. The system is **single-tenant by design.**

---

## Decision

**All tenant isolation, RBAC, and multi-tenant features have been explicitly removed.**

**Current Implementation:**
- All operations use `DEFAULT_TENANT_ID` from configuration
- No Row-Level Security (RLS) enforcement
- No tenant-based data filtering in application layer
- No RBAC middleware
- System operates as single-tenant

**The `tenant_id` column remains in the schema but is NOT enforced.**

---

## Rationale

### Why Remove Multi-Tenancy?

**Complexity vs Need:**
- Multi-tenant architecture adds significant complexity
- RLS policies require careful design and testing
- RBAC adds authorization overhead to every request
- Current use case is single-tenant (one customer, one dataset)

**Operational Simplicity:**
- Removing tenant isolation simplifies queries
- No need to validate tenant context on every operation
- Easier debugging (no "why can't I see this data?" mysteries)
- Faster development (no tenant-aware testing required)

**Future Flexibility:**
- `tenant_id` column preserved in schema
- Can re-add isolation if multi-tenancy becomes required
- Clean migration path if needed

---

## Current State

### What Was Removed

❌ **Supabase Row-Level Security (RLS)**
- No RLS policies enforced
- Database does NOT filter by tenant_id automatically

❌ **Application-Layer Tenant Filtering**
- Services do NOT filter queries by tenant_id
- No `WHERE tenant_id = ?` clauses in service methods

❌ **RBAC Middleware**
- No role-based authorization checks
- Authentication exists (JWT), but authorization is minimal

❌ **Tenant Context from JWT**
- JWT contains `tenant_id` claim
- But it's NOT used for data isolation
- Always uses `DEFAULT_TENANT_ID` instead

### What Remains

✅ **`tenant_id` Column in Schema**
```python
# src/models/base_model.py
class BaseModel:
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )
```

✅ **`DEFAULT_TENANT_ID` Configuration**
```python
# src/config/settings.py
DEFAULT_TENANT_ID: str = "default-tenant-id"
```

✅ **Tenant Reference in Records**
- All records created with `tenant_id = DEFAULT_TENANT_ID`
- Consistent across all tables
- But NOT enforced or filtered

---

## Consequences

### Positive

✅ **Simplified Development**
- No tenant context to manage
- No RLS policy debugging
- Faster feature development

✅ **Simplified Operations**
- No tenant-based access issues
- Easier database queries
- Simpler debugging

✅ **Performance**
- No RLS overhead
- No tenant filtering on every query
- Simpler query plans

### Negative

⚠️ **Single-Tenant Only**
- Cannot serve multiple customers
- Cannot isolate data per customer
- No multi-tenant SaaS capability

⚠️ **Schema Confusion**
- `tenant_id` exists but isn't used for isolation
- May confuse developers expecting multi-tenancy
- Outdated documentation references tenant isolation

⚠️ **Future Re-Implementation Cost**
- If multi-tenancy needed later, requires:
  - RLS policy implementation
  - Application-layer tenant filtering
  - RBAC re-implementation
  - Extensive testing

---

## Implementation

### How It Works Now

**Creating Records:**
```python
# Services receive tenant_id from JWT (or use default)
tenant_id = current_user.get("tenant_id", settings.default_tenant_id)

# Records created with this tenant_id
domain = Domain(
    tenant_id=tenant_id,
    domain_name="example.com",
    # ...
)
```

**Reading Records:**
```python
# NO tenant filtering
stmt = select(Domain).where(Domain.id == domain_id)
# Does NOT filter by tenant_id
```

**Why `tenant_id` is Still Passed:**
- BaseModel requires it
- Records need valid foreign key to tenants table
- Maintains schema integrity
- Allows future multi-tenancy if needed

---

## Enforcement

**This decision is enforced through:**

1. **No RLS Policies** - Database does not filter by tenant
2. **No Service-Layer Filtering** - Services do not filter by tenant_id
3. **Configuration** - All operations use `DEFAULT_TENANT_ID`
4. **This ADR** - Documents that single-tenant is intentional

**If you see `tenant_id` and think "I should add tenant filtering":**
- **STOP**
- Read this ADR
- Understand single-tenant is intentional
- Do not add tenant isolation without architectural review

---

## Migration Notes

### Outdated Documentation

**⚠️ WARNING:** Some legacy documentation describes multi-tenant architecture:

**Outdated:** `Docs/Docs_21_SeptaGram_Personas/tenant_id_handling_strategy.md`
- Claims: "RLS enforces tenant isolation"
- Claims: "Application layer doesn't filter by tenant_id (RLS does it)"
- **Reality:** This is NOT how the system works anymore

**Correct:** This ADR and current codebase analysis

### If Multi-Tenancy Needed in Future

**Requirements for re-implementation:**

1. **Database Layer:**
   - Implement Supabase RLS policies for all tables
   - Test RLS with multiple tenant contexts
   - Ensure RLS performs well (indexed properly)

2. **Application Layer:**
   - Add tenant validation middleware
   - Filter all queries by tenant_id from JWT
   - Implement tenant-aware service methods

3. **Authorization:**
   - Re-implement RBAC
   - Define roles and permissions per tenant
   - Add authorization checks to all endpoints

4. **Testing:**
   - Multi-tenant test scenarios
   - Cross-tenant access prevention tests
   - Performance testing with RLS

**Estimated Effort:** 2-3 weeks for full multi-tenant implementation

---

## Related Decisions

- **ADR-004:** Transaction Boundaries (doesn't involve tenant filtering)
- **Authentication:** JWT contains tenant_id claim but isn't used for isolation

---

## References

- **Analysis:** `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/STATE_OF_THE_NATION_2025-11-16.md`
- **Outdated Doc:** `Docs/Docs_21_SeptaGram_Personas/tenant_id_handling_strategy.md` (DO NOT FOLLOW)
- **Current Schema:** `src/models/base_model.py`

---

## Revision History

- **2025-11-16:** Initial ADR created documenting current single-tenant architecture
- **Supersedes:** Any prior multi-tenant design documentation
