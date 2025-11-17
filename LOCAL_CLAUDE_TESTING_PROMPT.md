# Instructions for Local Claude: Testing WO-009, WO-010, WO-011

**Your Mission:** Perform comprehensive testing of three new direct submission endpoints that were just implemented.

---

## Background

The online AI has completed implementation of three work orders:
- **WO-010:** Direct Domain Submission (`/api/v3/domains/direct-submit`)
- **WO-009:** Direct Page Submission (`/api/v3/pages/direct-submit`)
- **WO-011:** Direct Sitemap Submission (`/api/v3/sitemaps/direct-submit`)

These endpoints allow users to bypass early workflow stages and submit data directly into the system.

**Your Branch:** `claude/read-context-docs-01E8GWdNj2rJUHkN231xBFus`

**Implementation Commits:**
- 1ad0a1d: WO-010 implementation
- 4819c66: WO-009 implementation
- 45fe838: WO-011 implementation

---

## Your Task

Follow the comprehensive testing guide located at:
**`Documentation/Work_Orders/TESTING_INSTRUCTIONS_WO-009-010-011.md`**

This document contains:
- **8 Testing Phases** with step-by-step instructions
- **50+ Test Cases** covering success, error, and edge cases
- **SQL Verification Queries** to check database state
- **Docker Build Instructions** to set up local environment
- **Troubleshooting Guide** for common issues
- **Success Criteria Checklist**

---

## Step-by-Step Process

### Step 1: Read the Testing Guide
```bash
# Open and read the complete testing instructions
cat Documentation/Work_Orders/TESTING_INSTRUCTIONS_WO-009-010-011.md
```

### Step 2: Build and Start Docker Environment
```bash
# Follow Phase 0 in the testing guide
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Step 3: Execute All Test Phases

Work through each phase systematically:
- **Phase 0:** Environment Setup
- **Phase 1:** Authentication Setup
- **Phase 2:** Test WO-010 (Direct Domain Submission)
- **Phase 3:** Test WO-009 (Direct Page Submission)
- **Phase 4:** Test WO-011 (Direct Sitemap Submission)
- **Phase 5:** Integration Tests
- **Phase 6:** Error Handling Tests
- **Phase 7:** Database Integrity Checks
- **Phase 8:** Cleanup

### Step 4: Document Results

As you run tests, track:
- ✅ Tests that pass
- ❌ Tests that fail (with error details)
- ⚠️ Unexpected behavior
- 📝 Observations

### Step 5: Create Test Report

After completing all tests, create a summary document:
```
Documentation/Work_Orders/TEST_RESULTS_WO-009-010-011.md
```

Include:
1. **Executive Summary**
   - Overall pass/fail status
   - Critical issues found (if any)
   - Recommendation (approve/fix bugs/revert)

2. **Test Results by Phase**
   - Phase 0-8 results
   - Specific test case outcomes
   - SQL verification results

3. **Issues Found**
   - Bug descriptions
   - Severity ratings
   - Steps to reproduce
   - Suggested fixes

4. **Database State Verification**
   - Constraint violations (should be 0)
   - Foreign key integrity (should be 100%)
   - ENUM value correctness
   - Sample data inspection

5. **Performance Observations**
   - Response times
   - Database query efficiency
   - Any bottlenecks noticed

6. **Recommendations**
   - Approve for merge to main?
   - Bugs that need fixing?
   - Improvements to consider?

---

## Critical Verification Points

**These MUST all be TRUE for tests to pass:**

1. ✅ All endpoints are accessible and respond correctly
2. ✅ Authentication works (401 without token, success with token)
3. ✅ Duplicate detection works (409 Conflict for existing records)
4. ✅ Domain auto-creation works (new domains created when needed)
5. ✅ Tenant ID is ALWAYS set to DEFAULT_TENANT_ID for auto-created domains
6. ✅ domain_id is NEVER NULL in pages table
7. ✅ domain_id is NEVER NULL in sitemap_files table
8. ✅ sitemap_type is NEVER NULL in sitemap_files table
9. ✅ Dual-status pattern works (curation + processing status)
10. ✅ Auto-queue/auto-import flags work correctly
11. ✅ No errors in application logs
12. ✅ All ENUM values are valid
13. ✅ Foreign key relationships are correct
14. ✅ Validation errors return 422 with helpful messages

---

## Key Files to Review

Before testing, familiarize yourself with:

1. **Implementation Files:**
   - `src/routers/v3/domains_direct_submission_router.py`
   - `src/routers/v3/pages_direct_submission_router.py`
   - `src/routers/v3/sitemaps_direct_submission_router.py`
   - `src/schemas/domains_direct_submission_schemas.py`
   - `src/schemas/pages_direct_submission_schemas.py`
   - `src/schemas/sitemaps_direct_submission_schemas.py`

2. **Work Order Documentation:**
   - `Documentation/Work_Orders/WO-009_DIRECT_PAGE_SUBMISSION.md`
   - `Documentation/Work_Orders/WO-010_DIRECT_DOMAIN_SUBMISSION.md`
   - `Documentation/Work_Orders/WO-011_DIRECT_SITEMAP_SUBMISSION.md`

3. **Model Files (for constraint verification):**
   - `src/models/domain.py`
   - `src/models/page.py`
   - `src/models/sitemap.py`
   - `src/models/tenant.py` (for DEFAULT_TENANT_ID)

---

## Expected Outcomes

### If All Tests Pass:
✅ Create positive test report
✅ Recommend approval for merge to main
✅ Note any minor improvements for future work

### If Critical Issues Found:
❌ Document the issues clearly
❌ Recommend fixes before merge
❌ Categorize severity (Critical/High/Medium/Low)
❌ Suggest whether to fix or revert

### If Minor Issues Found:
⚠️ Document the issues
⚠️ Recommend fixing if easy, or defer to future work
⚠️ Assess if they block merge to main

---

## Common Issues & Solutions

### Issue: Can't obtain JWT token
**Solution:** Check if app is in debug mode (may bypass auth) or create a test user account

### Issue: Endpoints return 404
**Solution:** Verify routers are registered in `src/main.py` and check application logs

### Issue: Database constraints violated
**Solution:** This is a CRITICAL bug - document in detail and recommend fix before merge

### Issue: Docker build fails
**Solution:** Check for Python syntax errors, missing dependencies, or Docker cache issues

### Issue: Tests create orphaned records
**Solution:** Follow Phase 8 cleanup procedures to remove test data

---

## Communication Protocol

After completing testing, report back with:

1. **Quick Status:** "✅ All tests passed" or "❌ Critical issues found" or "⚠️ Minor issues found"

2. **Summary Stats:**
   - X tests run
   - X passed
   - X failed
   - X warnings

3. **Critical Findings:** (if any)
   - List of bugs/issues
   - Severity ratings
   - Recommended actions

4. **Test Report Location:**
   - Path to your detailed test report document

---

## Time Estimate

- **Environment setup:** 15-20 minutes
- **Test execution:** 60-90 minutes
- **Documentation:** 30-45 minutes
- **Total:** 2-3 hours

---

## Questions to Answer

By the end of testing, you should be able to answer:

1. Do all three endpoints work as specified in the work orders?
2. Are all nullable=False constraints properly handled?
3. Is the domain get-or-create pattern working correctly?
4. Is tenant_id always set to DEFAULT_TENANT_ID for auto-created domains?
5. Does the dual-status pattern work correctly for all endpoints?
6. Are duplicate submissions properly rejected with 409 Conflict?
7. Do auto-queue and auto-import flags work correctly?
8. Are all validation errors returning 422 with helpful messages?
9. Is the database integrity maintained (no orphaned records)?
10. Are there any performance concerns or optimization opportunities?

---

## Ready to Begin?

1. Pull the latest code from branch `claude/read-context-docs-01E8GWdNj2rJUHkN231xBFus`
2. Open `Documentation/Work_Orders/TESTING_INSTRUCTIONS_WO-009-010-011.md`
3. Follow the guide step-by-step
4. Document your findings
5. Report back with results

Good luck! 🚀

---

**Remember:** Your testing is critical. These endpoints will be used in production, so thoroughness is more important than speed. If you find issues, that's a SUCCESS - it means we caught them before production deployment.
