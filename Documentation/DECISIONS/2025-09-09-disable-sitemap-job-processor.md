# DECISION-2025-09-09-disable-sitemap-job-processor

## Metadata
- **Date:** September 9, 2025
- **Decider:** Team
- **Status:** FAILED
- **Impact:** HIGH (broke pipeline for 2 months)

---

## Context

Sitemap job processor in `sitemap_scheduler.py` was processing pending jobs from the `jobs` table. Code was seen as legacy and needed refactoring.

---

## Decision

Disable the sitemap job processor (lines 131-179 of sitemap_scheduler.py).

**Rationale stated in code:**
> "DISABLED as per new PRD v1.2 and holistic analysis. This entire workflow is being replaced by the modern, SDK-based sitemap_import_scheduler."

---

## Alternatives Considered

1. **Keep both systems** - Run old and new in parallel
2. **Gradual migration** - Migrate one workflow at a time
3. **Immediate disable** - Disable old, assume new works (CHOSEN)

---

## Outcome

❌ **FAILED**

- `sitemap_import_scheduler` processes **SitemapFile** records, not **Job** records
- No actual replacement implemented
- 2+ months of silent failures

**Reference:** [INCIDENT-2025-09-09-scheduler-disabled](../INCIDENTS/2025-09-09-scheduler-disabled.md)

---

## Lessons Learned

1. **"Being replaced" ≠ "Has been replaced"** - Verify before disabling
2. **Similar names ≠ same functionality** - Test data flow
3. **Document dependencies** - Map what depends on what

---

**Status:** Superseded by Commit 9f091f6 (immediate job triggering)
