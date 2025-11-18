# WO-009-011: Direct Submission Endpoints - Summary
**Created:** November 17, 2025
**Work Orders:** WO-009, WO-010, WO-011
**Total Estimated Effort:** 7.5-10 hours
**Overall Risk:** MEDIUM

---

## Overview

This document summarizes three related work orders for implementing direct submission endpoints, allowing users to bypass early workflow stages (WF1-WF5) and enter the pipeline at specific points.

---

## Work Order Breakdown

### WO-009: Direct Page Submission ✅ READY
**Endpoint:** `POST /api/v3/pages/direct-submit`
**Entry Point:** WF7 (Page Curation)
**Bypass:** WF1→WF5 (Google Maps → Sitemap Import)
**Effort:** 3-4 hours
**Risk:** MEDIUM
**Status:** READY FOR IMPLEMENTATION

**Key Features:**
- Submit page URLs directly for scraping
- Auto-queue for WF7 processing
- Duplicate detection
- Priority level control

**Critical Dependencies:**
- Page model: Verified dual-status pattern
- ENUMs: PageCurationStatus, PageProcessingStatus
- NULL domain_id: Confirmed supported

---

### WO-010: Direct Domain Submission ✅ READY
**Endpoint:** `POST /api/v3/domains/direct-submit`
**Entry Point:** WF4 (Sitemap Discovery)
**Bypass:** WF1→WF2 (Google Maps → Deep Scan)
**Effort:** 2-3 hours
**Risk:** LOW
**Status:** READY FOR IMPLEMENTATION

**Key Features:**
- Submit domain names directly
- Domain normalization (removes www, protocol, paths)
- Auto-queue for sitemap discovery
- Flexible input formats

**Critical Dependencies:**
- Domain model: Verified dual-status pattern
- ENUMs: SitemapCurationStatusEnum, SitemapAnalysisStatusEnum (inconsistent casing)
- NULL local_business_id: Confirmed supported

---

### WO-011: Direct Sitemap Submission ⚠️ REQUIRES VERIFICATION
**Endpoint:** `POST /api/v3/sitemaps/direct-submit`
**Entry Point:** WF5 (Sitemap Import)
**Bypass:** WF1→WF4 (Google Maps → Sitemap Discovery)
**Effort:** 2.5-3 hours
**Risk:** MEDIUM
**Status:** REQUIRES PHASE 0 VERIFICATION

**Key Features:**
- Submit sitemap XML URLs directly
- Auto-import to create Page records
- Optional domain association
- Sitemap URL validation

**Critical Dependencies:**
- **⚠️ MUST VERIFY:** Actual SitemapFile model structure
- **⚠️ MUST VERIFY:** Exact ENUM definitions
- **⚠️ MUST VERIFY:** NULL domain_id support
- **⚠️ MUST VERIFY:** WF5 scheduler compatibility

**Blockers:**
- Phase 0 verification must complete before implementation

---

## Implementation Strategy

### Recommended Order

**Option A: Sequential (Safest)**
1. WO-010 (Domain) - Lowest risk, good warm-up
2. WO-009 (Page) - Medium risk, most valuable
3. WO-011 (Sitemap) - After verification complete

**Option B: Parallel (Faster)**
1. WO-010 (Domain) - Developer 1
2. WO-009 (Page) - Developer 2
3. WO-011 Phase 0 - Developer 3 (verification only)

**Option C: Value-First (User Impact)**
1. WO-009 (Page) - Immediate user value
2. WO-010 (Domain) - Follow-up
3. WO-011 (Sitemap) - After verification

**RECOMMENDED: Option A (Sequential)** - Minimizes risk, allows learning between implementations

---

## Shared Patterns

All three work orders follow the same architectural patterns:

### 1. Dual-Status Pattern (ADR-003)
```python
# Curation status: User decision
entity_curation_status = "Selected" if auto_queue else "New"

# Processing status: System state
entity_processing_status = "Queued" if auto_queue else None
```

### 2. Transaction Boundaries (ADR-004)
```python
# Router owns transaction
async with session.begin():
    # All database operations here
    session.add(entity)
# Transaction commits automatically
```

### 3. Duplicate Detection
```python
# Check before creating
existing = await session.execute(
    select(Entity).where(Entity.url == url)
)
if existing.scalar_one_or_none():
    raise HTTPException(409, "Entity already exists")
```

### 4. Status Initialization
```python
# NULL foreign keys (not from previous workflows)
entity = Entity(
    id=uuid.uuid4(),
    url=url,
    parent_id=None,  # NULL when directly submitted
    curation_status=...,
    processing_status=...,
    created_at=datetime.utcnow(),
    user_id=current_user.get("user_id")
)
```

---

## ENUM Management (CRITICAL - ADR-005)

### Identified ENUMs

**WO-009 (Pages):**
- `PageCurationStatus`: New, Selected, Rejected
- `PageProcessingStatus`: Queued, Processing, Complete, Error

**WO-010 (Domains):**
- `SitemapCurationStatusEnum`: New, Selected, Rejected
- `SitemapAnalysisStatusEnum`: queued, submitted, failed
- ⚠️ **Inconsistent casing** (PascalCase vs lowercase)

**WO-011 (Sitemaps):**
- ⚠️ **VERIFY BEFORE USE**
- Expected: SitemapCurationStatus, SitemapImportStatus
- Actual: TBD (Phase 0 verification)

### ENUM Safety Checklist

For each work order:
- [ ] Document exact ENUM definitions from Layer 1 (models)
- [ ] Verify Layer 2 (schemas) imports from Layer 1
- [ ] DO NOT create new ENUM values
- [ ] DO NOT change existing ENUM values
- [ ] DO NOT rename ENUM classes
- [ ] Use `.value` when querying (SQLAlchemy ENUM bug)

---

## Risk Matrix

| Work Order | Risk Level | Risk Factors | Mitigation |
|------------|------------|--------------|------------|
| WO-009 | MEDIUM | WF7 is production-critical | Thorough testing, rollback plan |
| WO-010 | LOW | Early in pipeline, isolated | Pre-verify domain normalization |
| WO-011 | MEDIUM | Model structure unknown | Phase 0 verification required |

### Overall Risk Assessment

**Combined Risk:** MEDIUM

**Key Risk Factors:**
1. **ENUM Catastrophe (ADR-005):** Cross-layer ENUM changes could break system
2. **Workflow Interference:** Direct submissions could conflict with existing workflows
3. **NULL Foreign Keys:** Queries assuming non-NULL FKs might break

**Risk Mitigation:**
1. **No ENUM Changes:** Use existing ENUMs only
2. **Duplicate Detection:** Prevent conflicts before creation
3. **Query Audit:** Verify LEFT JOIN usage, not INNER JOIN
4. **Comprehensive Testing:** Test with and without auto-queue
5. **Rollback Plans:** Can undo in < 5 minutes

---

## Testing Strategy

### Unit Tests (Per Work Order)
```bash
# Test schema validation
pytest tests/schemas/test_direct_submission_schemas.py

# Test router logic
pytest tests/routers/v3/test_direct_submission_routers.py
```

### Integration Tests (Per Work Order)
```bash
# Basic submission (auto_queue=False)
# Auto-queue submission (auto_queue=True)
# Duplicate detection (409 Conflict)
# Invalid input (422 Validation Error)
# Batch submission
```

### End-to-End Tests (Cross-Workflow)
```bash
# Test 1: Direct page submission + WF7 processing
# Test 2: Direct domain submission + WF4 discovery + WF5 import
# Test 3: Direct sitemap submission + WF5 import + WF7 processing
```

### Regression Tests (Critical)
```bash
# Verify existing workflows still work
# Test: WF1 → WF2 → WF3 → WF4 → WF5 → WF7 (full pipeline)
# Test: Manual curation interfaces still work
# Test: Scheduler pickup logic unchanged
```

---

## Success Criteria (All Work Orders)

- ✅ All endpoints return 200 with valid input
- ✅ Auto-queue flag triggers scheduler pickup
- ✅ Manual submission requires curation
- ✅ Duplicate detection works (409 responses)
- ✅ Invalid input rejected (422 responses)
- ✅ Existing workflows unaffected
- ✅ No database constraint violations
- ✅ No application errors in logs
- ✅ All regression tests pass

---

## Documentation Updates (After Implementation)

### Files to Update

1. **EXTENSIBILITY_PATTERNS.md**
   - Mark implemented patterns with ✅
   - Add actual endpoint URLs
   - Add production examples

2. **Workflows/README.md**
   - Add "Direct Submission" section
   - Link to API documentation

3. **API Documentation (Swagger)**
   - Auto-generated from FastAPI decorators
   - Verify examples are clear

4. **QUICK_START.md**
   - Add direct submission commands
   - Add to "Common Development Tasks"

---

## Rollback Procedures

### If Any Implementation Fails

**Step 1: Disable Endpoint**
```python
# In main.py, comment out:
# app.include_router(problematic_router)
```

**Step 2: Delete Test Data**
```sql
-- Pages (WO-009)
DELETE FROM pages WHERE domain_id IS NULL AND created_at > 'YYYY-MM-DD';

-- Domains (WO-010)
DELETE FROM domains WHERE local_business_id IS NULL AND created_at > 'YYYY-MM-DD';

-- Sitemaps (WO-011)
DELETE FROM sitemap_files WHERE [condition] AND created_at > 'YYYY-MM-DD';
```

**Step 3: Remove Code**
```bash
rm src/routers/v3/*_direct_submission_router.py
rm src/schemas/*_direct_submission_schemas.py
```

**Step 4: Restart**
```bash
docker compose restart app
```

**Total Rollback Time:** < 10 minutes per work order

---

## Timeline Estimate

### Sequential Implementation (Option A)

**Week 1:**
- Day 1: WO-010 (Domain) - Implementation + Testing
- Day 2: WO-010 (Domain) - Code review + Deploy
- Day 3: WO-009 (Page) - Implementation + Testing
- Day 4: WO-009 (Page) - Code review + Deploy
- Day 5: WO-011 Phase 0 - Verification complete

**Week 2:**
- Day 1-2: WO-011 (Sitemap) - Implementation + Testing
- Day 3: WO-011 (Sitemap) - Code review + Deploy
- Day 4: Integration testing all three endpoints
- Day 5: Documentation updates + retrospective

**Total Time:** 10 days (2 weeks)

### Parallel Implementation (Option B)

**Week 1:**
- All three work orders in parallel
- Daily sync meetings

**Week 2:**
- Integration testing
- Bug fixes
- Documentation

**Total Time:** 7-10 days (1.5-2 weeks)

---

## Dependencies

### External
- ✅ Database schema (no changes needed)
- ✅ Authentication system (existing JWT)
- ✅ WF4, WF5, WF7 schedulers (must remain compatible)

### Internal
- ✅ Pydantic validators (for URL/domain validation)
- ✅ SQLAlchemy models (use existing, no changes)
- ✅ FastAPI framework (for routing)

### Blocking
- ⚠️ **WO-011:** Blocked by Phase 0 verification

---

## Review Checklist

Before starting implementation, verify:

- [ ] All work orders reviewed and approved
- [ ] ENUM definitions documented
- [ ] Risk assessment accepted
- [ ] Testing strategy agreed upon
- [ ] Rollback procedures understood
- [ ] Timeline approved
- [ ] WO-011 Phase 0 verification scheduled

---

## Related Work

- **EXTENSIBILITY_PATTERNS.md** - Original design spec
- **ADR-003** - Dual-Status Workflow Pattern
- **ADR-004** - Transaction Boundaries
- **ADR-005** - ENUM Catastrophe (critical reading!)
- **WO-006, WO-007** - Documentation work (context for these WOs)
- **WO-008** - Verification work (quality standards)

---

**Status:** ALL WORK ORDERS READY FOR REVIEW
**Next Step:** Review and approve before implementation begins
**Review By:** Technical Lead / Product Owner
