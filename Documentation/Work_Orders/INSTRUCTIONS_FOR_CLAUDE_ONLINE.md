# Instructions for Claude Online: WO-009-011 Corrections

## Quick Start (2 Commands)

```bash
# 1. Pull your branch to see corrected work orders
git pull origin claude/read-context-docs-01E8GWdNj2rJUHkN231xBFus

# 2. Switch to main to see new documentation sections
git checkout main
```

---

## What Changed

### Your Branch (Corrected Work Orders)
**Files to review:**
1. `Documentation/Work_Orders/WO-009_DIRECT_PAGE_SUBMISSION.md`
   - **Critical fix:** `domain_id` cannot be NULL (nullable=False)
   - **Added:** Get-or-create domain logic (lines 361-383)
   - **Time:** +1.5 hours

2. `Documentation/Work_Orders/WO-011_DIRECT_SITEMAP_SUBMISSION.md`
   - **Critical fix:** `domain_id` cannot be NULL (nullable=False)
   - **Resolved:** Phase 0 verification complete (model structure documented)
   - **Time:** +1 hour

### Main Branch (New Documentation)
**File to review:**
- `Documentation/Context_Reconstruction/SYSTEM_MAP.md` (v2.0)
  - **New section:** Core Model File Map (line 89)
  - **New section:** Critical Model Constraints (line 105)
  - **New section:** Core ENUM Registry (line 162)

---

## Critical Finding

**Your assumption:** `domain_id` can be NULL for direct submissions  
**Ground truth:** `domain_id` has `nullable=False` constraint  
**Impact:** Would cause 100% failure (database constraint violation)  
**Solution:** Get-or-create Domain pattern (see corrected work orders)

---

## Verification Report

Read the full analysis:
```bash
git checkout main
cat Documentation/Work_Orders/WO-009-011_CRITICAL_VERIFICATION_REPORT.md
```

---

## Next Steps

1. ✅ Review corrected WO-009 and WO-011 on your branch
2. ✅ Review new SYSTEM_MAP.md sections on main
3. ✅ Confirm you understand the get-or-create domain pattern
4. ✅ Proceed with implementation using corrected logic

**WO-010 is unchanged and can proceed as-is.**

---

## Questions to Answer

Before implementing, confirm:
- [ ] Do you see the get-or-create domain logic in WO-009 (lines 361-383)?
- [ ] Do you understand why `domain_id=None` would fail?
- [ ] Have you reviewed the new ENUM Registry in SYSTEM_MAP.md?
- [ ] Are you ready to implement with the corrected patterns?
