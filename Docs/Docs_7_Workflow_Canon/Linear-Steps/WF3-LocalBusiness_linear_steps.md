# WF3-LocalBusiness Linear Steps

**Workflow:** Local Business Curation to Domain Extraction
**Version:** 1.0
**Date:** 2025-05-04

---

## Step-by-Step Workflow Breakdown

### 1. UI Interaction
- **Files:**
  - `static/scraper-sky-mvp.html` [NOVEL]
  - `static/js/local-business-curation-tab.js` [NOVEL]
- **Action:**
  - User selects local businesses in the UI, sets status to "Selected", clicks "Update X Selected".
  - JavaScript gathers selected IDs and new status, triggers API call.
- **Principles:**
  - Clear UI feedback
  - Accurate mapping of user intent to API call
  - API endpoint consistency
- **Notes:**
  - Ensure JS correctly collects IDs and status, and provides user feedback on success/failure.

### 2. API Routing
- **File:** `src/routers/local_businesses.py`
- **Action:**
  - PUT `/api/v3/local-businesses/status` receives IDs and status, validates input, maps status to enum.
- **Principles:**
  - API standardization
  - Input validation
  - Enum handling
  - Transaction boundary
- **Notes:**
  - Ensure request model matches expected schema. Log and handle invalid input.

### 3. Domain Extraction Trigger
- **File:** `src/routers/local_businesses.py`
- **Action:**
  - If status is "Selected", set `domain_extraction_status = Queued`, clear errors, update timestamps.
- **Principles:**
  - Business logic encapsulation
  - Atomic update
  - Correct enum usage
- **Notes:**
  - Confirm logic for eligibility (currently, all selected are queued).

### 4. Commit Transaction
- **File:** `src/routers/local_businesses.py`
- **Action:**
  - Commit all changes in a transaction context.
- **Principles:**
  - Transaction boundary
  - Error handling
- **Notes:**
  - Ensure rollback on failure and correct use of `session.begin()`.

### 5. Background Processing
- **File:** `src/services/sitemap_scheduler.py` [SHARED]
- **Action:**
  - Scheduler polls for `domain_extraction_status = Queued`, triggers extraction process.
- **Principles:**
  - Background job compliance
  - Idempotency
  - Retry logic
- **Notes:**
  - Confirm scheduler picks up all eligible items and logs failures/retries.

### 6. Testing & Verification
- **File:** `tests/services/test_sitemap_scheduler.py` [NOVEL]
- **Action:**
  - Tests ensure queued items are picked up and processed.
- **Principles:**
  - Test coverage
  - Reproducibility
- **Notes:**
  - Ensure tests cover edge cases and error conditions.

---

## Audit/Compliance Checklist
- [ ] All steps above are implemented and referenced in canonical YAML
- [ ] All files are annotated in python_file_status_map.md
- [ ] All exceptions and issues are logged in the micro work order and master log
- [ ] Artifacts are synchronized and up to date
- [ ] All architectural principles are followed

---

**Logged by Cascade AI | 2025-05-04**
