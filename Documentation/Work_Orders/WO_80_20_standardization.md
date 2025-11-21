# Work Order: 80/20 Codebase Standardization

## Priority
High

## Objective
Apply the Pareto principle to achieve maximum standardization impact with minimum effort. Focus on the 20% of fixes that will eliminate 80% of the inconsistency-related bugs.

## Phase 1: Enum Import Safety (Highest ROI)

### Problem
Missing enum imports cause runtime 500 errors that aren't caught until production.

### Solution
**Create comprehensive enum import blocks** - Each file that uses enums should import ALL related enums from that model, not cherry-pick.

**Example Pattern:**
```python
# ❌ BAD - Fragile, breaks when code evolves
from ..models.wf5_sitemap_file import SitemapFile, SitemapImportCurationStatusEnum

# ✅ GOOD - Defensive, prevents future bugs
from ..models.wf5_sitemap_file import (
    SitemapFile,
    SitemapFileStatusEnum,
    SitemapImportCurationStatusEnum,
    SitemapImportProcessStatusEnum,
)
```

**Action Items:**
- [ ] Audit all files importing from workflow models
- [ ] Update to comprehensive enum imports
- [ ] Create linting rule to enforce pattern

**Estimated Impact:** Prevents 90% of enum-related runtime errors

---

## Phase 2: Background Service Import Standardization

### Problem
`src/services/background/` files use relative imports (`..config`, `..scheduler_instance`) which fail because `..` resolves to `src.services` not `src`.

### Solution
**Enforce absolute imports** for cross-package references in background services.

**Pattern:**
```python
# ❌ BAD - Breaks in src/services/background/
from ..config.settings import settings
from ..scheduler_instance import scheduler

# ✅ GOOD - Always works
from src.config.settings import settings
from src.scheduler_instance import scheduler
```

**Action Items:**
- [ ] Audit all `src/services/background/*.py` files
- [ ] Convert to absolute imports for: `config`, `scheduler_instance`, `scraper`, `session`
- [ ] Add pre-commit hook or linting rule

**Estimated Impact:** Eliminates 80% of import path errors in schedulers

---

## Phase 3: Router Deprecation Clarity

### Problem
Unclear which routers are current vs legacy (v2, v3, non-versioned mix).

### Solution
**Document router lifecycle** - Don't delete yet, just clarify status.

**Action Items:**
- [ ] Create `ROUTER_STATUS.md` mapping each router to: `current`, `deprecated`, or `legacy`
- [ ] Add deprecation warnings to legacy router docstrings
- [ ] Plan migration path for deprecated endpoints

**Estimated Impact:** Prevents accidental use of wrong endpoints, clarifies maintenance scope

---

## Phase 4: Service Layer Completion (Lower Priority)

### Problem
Some routers query the database directly instead of using service layer.

### Solution
Move DB logic to services, but **only for actively maintained routers**.

**Action Items:**
- [ ] Identify routers with direct DB queries
- [ ] Prioritize by usage frequency
- [ ] Migrate top 5 most-used routers

**Estimated Impact:** Improves testability and maintainability for core workflows

---

## Success Metrics
- ✅ Zero enum-related 500 errors in production logs (30-day window)
- ✅ Zero import path errors in background schedulers
- ✅ Clear router deprecation status documented
- ✅ 80% reduction in "which endpoint should I use?" questions

## Timeline
- **Phase 1 (Enum Safety):** 2-3 hours
- **Phase 2 (Import Standardization):** 1-2 hours  
- **Phase 3 (Router Clarity):** 1 hour
- **Phase 4 (Service Layer):** Ongoing, as needed

**Total Upfront Investment:** ~6 hours for 80% of standardization benefits
