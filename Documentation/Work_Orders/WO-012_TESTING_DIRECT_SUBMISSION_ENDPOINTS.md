# WO-012: Testing Direct Submission Endpoints (WO-009, WO-010, WO-011)

**Created:** November 17, 2025  
**Priority:** CRITICAL  
**Estimated Effort:** 2-3 hours  
**Status:** 🔴 READY TO START  
**Branch:** `claude/read-context-docs-01E8GWdNj2rJUHkN231xBFus`  
**Assigned To:** Fresh AI Instance (Testing Specialist)

---

## Mission Brief

You are a **Testing Specialist AI** starting with a clean slate. Your mission is to comprehensively test three newly implemented direct submission endpoints that allow users to bypass early workflow stages.

**Implementation Commits (Already Complete):**
- `1ad0a1d`: WO-010 (Direct Domain Submission)
- `4819c66`: WO-009 (Direct Page Submission)
- `45fe838`: WO-011 (Direct Sitemap Submission)

**Your Job:** Verify these implementations work correctly, satisfy all database constraints, and are ready for production.

---

## Phase 0: Context Establishment (15-20 minutes)

### Critical: Read These Documents First

You MUST establish firm context before testing. Read these in order:

#### 1. The Lesson (WHY our docs exist)
**File:** `Documentation/Analysis/POSTMORTEM_WO-009_DOC_FAILURE.md`

**Why Read This:**
- Explains the painful 3-hour process that created these work orders
- Shows why SYSTEM_MAP.md exists and why it's critical
- Defines the "New Standard" for documentation

**Key Takeaway:** Documentation now includes **Data Model Contracts** (nullable=False constraints, ENUMs, file locations). This is your ground truth.

#### 2. The Ground Truth (WHAT the constraints are)
**File:** `Documentation/Context_Reconstruction/SYSTEM_MAP.md`

**Why Read This:**
- Contains ALL database constraints (nullable=False, unique, ForeignKey)
- Documents all ENUMs with exact casing
- Provides model file locations

**Critical Sections to Read:**
- **Core Model File Map** (lines 85-110)
- **Critical Model Constraints** (lines 112-190)
- **Core ENUM Registry** (lines 192-280)

**Key Constraints You'll Verify:**
```python
# From SYSTEM_MAP.md
Domain.tenant_id: nullable=False (must use DEFAULT_TENANT_ID)
Page.domain_id: nullable=False (must use get-or-create pattern)
SitemapFile.domain_id: nullable=False (must use get-or-create pattern)
SitemapFile.sitemap_type: nullable=False (must be "STANDARD")
```

#### 3. The Approval (WHAT was approved)
**File:** `Documentation/Work_Orders/FINAL_APPROVAL_LOCAL_AI.md`

**Why Read This:**
- Shows what was reviewed and approved
- Lists architecture compliance checklist
- Documents expected behavior

**Key Sections:**
- Verification Summary (lines 10-30)
- Code Quality Review (lines 32-60)
- Architecture Compliance (lines 62-75)

#### 4. The Specifications (HOW they should work)
**Files:**
- `Documentation/Work_Orders/WO-010_DIRECT_DOMAIN_SUBMISSION.md`
- `Documentation/Work_Orders/WO-009_DIRECT_PAGE_SUBMISSION.md`
- `Documentation/Work_Orders/WO-011_DIRECT_SITEMAP_SUBMISSION.md`

**Why Read These:**
- Define expected behavior for each endpoint
- Include testing plans (SQL queries, curl commands)
- Document success criteria

**Focus On:**
- "Testing & Verification" sections
- "Expected Results" sections
- "Database Verification" SQL queries

#### 5. The Testing Guide (HOW to test)
**File:** `Documentation/Work_Orders/TESTING_INSTRUCTIONS_WO-009-010-011.md`

**Why Read This:**
- 1,117 lines of comprehensive testing instructions
- 8 testing phases with step-by-step commands
- 50+ specific test cases
- SQL verification queries
- Troubleshooting guide

**This is your execution playbook.**

---

## Phase 1: Environment Setup (15-20 minutes)

### Step 1: Verify Branch and Code

```bash
# Confirm you're on the correct branch
git branch --show-current
# Expected: claude/read-context-docs-01E8GWdNj2rJUHkN231xBFus

# Verify implementation commits exist
git log --oneline -10 | grep -E "(1ad0a1d|4819c66|45fe838)"

# List new files
ls -la src/routers/v3/domains_direct_submission_router.py
ls -la src/routers/v3/pages_direct_submission_router.py
ls -la src/routers/v3/sitemaps_direct_submission_router.py
ls -la src/schemas/domains_direct_submission_schemas.py
ls -la src/schemas/pages_direct_submission_schemas.py
ls -la src/schemas/sitemaps_direct_submission_schemas.py
```

### Step 2: Build Docker Environment

```bash
# Stop existing containers
docker compose down

# Build fresh containers with new code
docker compose build --no-cache

# Start services
docker compose up -d

# Wait for initialization
sleep 10

# Verify services are running
docker compose ps
# Expected: All services "Up"

# Check app logs for errors
docker compose logs app | tail -50
# Expected: "Uvicorn running on http://0.0.0.0:8000"
# Expected: No ERROR messages
```

### Step 3: Verify Router Registration

```bash
# Check that routers were loaded
docker compose logs app | grep -i "router"

# Verify endpoints in OpenAPI schema
curl -s http://localhost:8000/api/schema.json | python -m json.tool > /tmp/openapi_schema.json

# Check for new endpoints
grep "/api/v3/domains/direct-submit" /tmp/openapi_schema.json
grep "/api/v3/pages/direct-submit" /tmp/openapi_schema.json
grep "/api/v3/sitemaps/direct-submit" /tmp/openapi_schema.json
```

**Expected:** All three endpoints present in schema.

---

## Phase 2: Execute Testing Plan (90-120 minutes)

### Follow the Comprehensive Testing Guide

**File:** `Documentation/Work_Orders/TESTING_INSTRUCTIONS_WO-009-010-011.md`

Execute all 8 phases systematically:

1. **Phase 0:** Environment Setup (DONE above)
2. **Phase 1:** Authentication Setup (obtain JWT token)
3. **Phase 2:** Test WO-010 (Direct Domain Submission)
   - 15 test cases
   - Verify tenant_id constraint
   - Test duplicate detection
   - Test auto_queue flag
4. **Phase 3:** Test WO-009 (Direct Page Submission)
   - 20 test cases
   - Verify domain_id constraint (get-or-create)
   - Verify tenant_id in auto-created domains
   - Test dual-status pattern
   - Test auto_queue flag
5. **Phase 4:** Test WO-011 (Direct Sitemap Submission)
   - 15 test cases
   - Verify domain_id constraint (get-or-create)
   - Verify sitemap_type constraint
   - Test dual-status pattern
   - Test auto_import flag
6. **Phase 5:** Integration Tests
   - End-to-end workflows
   - Cross-endpoint interactions
7. **Phase 6:** Error Handling Tests
   - Invalid inputs (422 validation errors)
   - Duplicates (409 conflicts)
   - Authentication failures (401)
8. **Phase 7:** Database Integrity Checks
   - **CRITICAL:** Verify all nullable=False constraints satisfied
   - Check for orphaned records
   - Verify foreign key relationships
   - Validate ENUM values
9. **Phase 8:** Cleanup
   - Remove test data from database

---

## Critical Verification Points

As you test, you MUST verify these constraints are satisfied:

### ✅ Constraint 1: Domain.tenant_id (nullable=False)

**SQL Verification:**
```sql
-- All domains should have tenant_id
SELECT id, domain, tenant_id, local_business_id 
FROM domains 
WHERE tenant_id IS NULL;
-- Expected: 0 rows

-- Auto-created domains should use DEFAULT_TENANT_ID
SELECT id, domain, tenant_id 
FROM domains 
WHERE local_business_id IS NULL;
-- Expected: tenant_id = '550e8400-e29b-41d4-a716-446655440000'
```

### ✅ Constraint 2: Page.domain_id (nullable=False)

**SQL Verification:**
```sql
-- All pages should have domain_id
SELECT id, url, domain_id 
FROM pages 
WHERE domain_id IS NULL;
-- Expected: 0 rows

-- Pages should link to valid domains
SELECT p.id, p.url, p.domain_id, d.domain 
FROM pages p
LEFT JOIN domains d ON p.domain_id = d.id
WHERE d.id IS NULL;
-- Expected: 0 rows (no orphaned pages)
```

### ✅ Constraint 3: SitemapFile.domain_id (nullable=False)

**SQL Verification:**
```sql
-- All sitemaps should have domain_id
SELECT id, url, domain_id 
FROM sitemap_files 
WHERE domain_id IS NULL;
-- Expected: 0 rows

-- Sitemaps should link to valid domains
SELECT sf.id, sf.url, sf.domain_id, d.domain 
FROM sitemap_files sf
LEFT JOIN domains d ON sf.domain_id = d.id
WHERE d.id IS NULL;
-- Expected: 0 rows (no orphaned sitemaps)
```

### ✅ Constraint 4: SitemapFile.sitemap_type (nullable=False)

**SQL Verification:**
```sql
-- All sitemaps should have sitemap_type
SELECT id, url, sitemap_type 
FROM sitemap_files 
WHERE sitemap_type IS NULL;
-- Expected: 0 rows

-- Direct submissions should use "STANDARD"
SELECT id, url, sitemap_type 
FROM sitemap_files 
WHERE discovery_method IS NULL;
-- Expected: sitemap_type = 'STANDARD'
```

### ✅ Constraint 5: Dual-Status Pattern

**SQL Verification (Pages):**
```sql
-- Pages with auto_queue=false
SELECT url, page_curation_status, page_processing_status 
FROM pages 
WHERE page_processing_status IS NULL;
-- Expected: page_curation_status = 'New'

-- Pages with auto_queue=true
SELECT url, page_curation_status, page_processing_status 
FROM pages 
WHERE page_processing_status IS NOT NULL;
-- Expected: page_curation_status = 'Selected'
-- Expected: page_processing_status = 'Queued'
```

**SQL Verification (Sitemaps):**
```sql
-- Sitemaps with auto_import=false
SELECT url, deep_scrape_curation_status, sitemap_import_status 
FROM sitemap_files 
WHERE sitemap_import_status IS NULL;
-- Expected: deep_scrape_curation_status = 'New'

-- Sitemaps with auto_import=true
SELECT url, deep_scrape_curation_status, sitemap_import_status 
FROM sitemap_files 
WHERE sitemap_import_status IS NOT NULL;
-- Expected: deep_scrape_curation_status = 'Selected'
-- Expected: sitemap_import_status = 'Queued'
```

---

## Deliverable: Test Results Report

### Create This File:
`Documentation/Work_Orders/TEST_RESULTS_WO-009-010-011.md`

### Required Sections:

#### 1. Executive Summary
```markdown
**Overall Status:** ✅ PASS / ⚠️ PASS WITH ISSUES / ❌ FAIL

**Critical Issues:** [Count]
**Major Issues:** [Count]
**Minor Issues:** [Count]

**Recommendation:** APPROVE / FIX BUGS / REVERT

**Summary:** [2-3 sentence overview]
```

#### 2. Environment Setup Results
- Docker build status
- Service startup status
- Router registration verification
- OpenAPI schema verification

#### 3. Test Results by Phase
For each phase (1-8), document:
- Test cases executed
- Pass/fail status
- SQL verification results
- Unexpected behavior
- Performance observations

#### 4. Critical Constraint Verification
**MUST INCLUDE:**
- ✅/❌ Domain.tenant_id constraint satisfied
- ✅/❌ Page.domain_id constraint satisfied
- ✅/❌ SitemapFile.domain_id constraint satisfied
- ✅/❌ SitemapFile.sitemap_type constraint satisfied
- ✅/❌ Dual-status pattern implemented correctly
- ✅/❌ No orphaned records
- ✅/❌ All ENUM values valid

#### 5. Issues Found
For each issue:
```markdown
### Issue #N: [Title]
**Severity:** CRITICAL / MAJOR / MINOR
**Component:** WO-009 / WO-010 / WO-011
**Description:** [What's wrong]
**Steps to Reproduce:** [How to trigger]
**Expected:** [What should happen]
**Actual:** [What actually happens]
**SQL Evidence:** [Query results showing the issue]
**Suggested Fix:** [How to fix it]
```

#### 6. Database State Summary
- Total domains created
- Total pages created
- Total sitemaps created
- Foreign key integrity status
- Constraint satisfaction status

#### 7. Performance Observations
- Response times
- Database query performance
- Any bottlenecks noticed

#### 8. Final Recommendation
```markdown
**Decision:** APPROVE / FIX BUGS / REVERT

**Justification:** [Why]

**Next Steps:** [What should happen next]
```

---

## Success Criteria

### ✅ All Tests Must Pass:
- [ ] All 50+ test cases execute successfully
- [ ] All SQL verification queries return expected results
- [ ] No database constraint violations
- [ ] No orphaned records
- [ ] All ENUM values valid
- [ ] Duplicate detection works (409 responses)
- [ ] Validation errors work (422 responses)
- [ ] Authentication works (401 for missing token)

### ✅ All Critical Constraints Satisfied:
- [ ] Domain.tenant_id: No NULL values
- [ ] Page.domain_id: No NULL values
- [ ] SitemapFile.domain_id: No NULL values
- [ ] SitemapFile.sitemap_type: No NULL values
- [ ] All auto-created domains use DEFAULT_TENANT_ID
- [ ] Dual-status pattern works correctly

### ✅ Architecture Compliance:
- [ ] ADR-004: Transaction boundaries correct
- [ ] ADR-005: ENUM safety maintained
- [ ] Dual-status pattern implemented
- [ ] Get-or-create pattern works
- [ ] No code smells or anti-patterns

---

## Communication Protocol

### During Testing:
- Report progress after each phase
- Flag critical issues immediately
- Document unexpected behavior
- Ask questions if something is unclear

### After Testing:
- Create comprehensive test results report
- Commit report to branch
- Provide clear recommendation (APPROVE/FIX/REVERT)
- List any blockers or concerns

---

## Troubleshooting Guide

### Issue: Docker containers won't start
**Solution:** Check `docker compose logs app` for errors. Verify Python syntax in new files.

### Issue: Endpoints not in OpenAPI schema
**Solution:** Check `src/main.py` - routers must be included. Verify import statements.

### Issue: Authentication fails
**Solution:** Follow Phase 1 in testing guide to obtain valid JWT token.

### Issue: Database constraint violations
**Solution:** This is a CRITICAL bug. Document with SQL evidence and recommend FIX.

### Issue: Can't connect to database
**Solution:** Verify `docker compose ps` shows db service running. Check connection string.

---

## References

**Implementation Commits:**
- 1ad0a1d: WO-010 implementation
- 4819c66: WO-009 implementation  
- 45fe838: WO-011 implementation

**Documentation Commits:**
- 72e83a4: Post-mortem and documentation updates (main branch)
- e5ee31a: SYSTEM_MAP.md v2.1 with constraints (main branch)
- 451d97b: Final approval document (feature branch)

**Key Documents:**
- `Documentation/Analysis/POSTMORTEM_WO-009_DOC_FAILURE.md`
- `Documentation/Context_Reconstruction/SYSTEM_MAP.md`
- `Documentation/Work_Orders/FINAL_APPROVAL_LOCAL_AI.md`
- `Documentation/Work_Orders/TESTING_INSTRUCTIONS_WO-009-010-011.md`
- `LOCAL_CLAUDE_TESTING_PROMPT.md`

---

## Time Estimates

- **Phase 0 (Context):** 15-20 minutes
- **Phase 1 (Environment):** 15-20 minutes
- **Phase 2 (Testing):** 90-120 minutes
- **Phase 3 (Report):** 20-30 minutes

**Total:** 2.5-3 hours

---

## Final Notes

**You are starting fresh.** You have no prior context from the documentation creation or implementation process. This is intentional - you're testing as an independent verifier.

**Your job is to verify, not assume.** Even though these endpoints were approved, you must verify they work correctly in practice.

**Focus on database constraints.** The entire painful process that created these work orders was about missing nullable=False constraints. Your primary job is to verify these are satisfied.

**Document everything.** Your test results report will be used to decide whether to merge this code to production.

**Good luck!** 🚀

---

**Status:** Ready to start  
**Next Action:** Read Phase 0 documents, then begin testing
