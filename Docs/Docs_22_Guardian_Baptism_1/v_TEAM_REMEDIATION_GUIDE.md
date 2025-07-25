# Team Remediation Guide: Aligning Tests, Services & Routers

## 1. Overview and Purpose

This document provides the official marching orders for the development team to align the application's test suite, services, and routers with the foundational Layer 1 refactoring. The core code has been brought into compliance with our architectural blueprint; this guide details the necessary follow-up actions to ensure the entire application is stable and functional.

This work should be performed in parallel with the instructions in `DATABASE_MIGRATION_GUIDE.md`.

## 2. Part 1: Test Suite Remediation (High Priority Action)

**The test suite is currently broken.** It reflects the old architecture and will fail until it is updated. This is the highest priority task for the development team.

### Step 1: Identify Failing Tests

Run the test suite using your standard command (e.g., `pytest`). Expect a large number of failures due to `ImportError`, `AttributeError`, and `ValueError`. This is expected.

### Step 2: Fix Imports

The primary cause of failures is that tests are importing schemas and ENUMs from old, now-deleted locations.

**Action:** Update all import statements in the test files (`/tests/`) to point to the new, centralized locations.

**Example: Schema Imports**
-   **OLD (Incorrect):** `from src.models.api_models import DomainRecord`
-   **NEW (Correct):** `from src.schemas.domain import DomainRecord`

**Example: ENUM Imports**
-   **OLD (Incorrect):** `from src.models.domain import SitemapCurationStatusEnum`
-   **NEW (Correct):** `from src.models.enums import SitemapCurationStatus`

### Step 3: Update ENUM Member References

The naming convention for ENUM members has been standardized to `UPPERCASE`.

**Action:** Find all references to old `PascalCase` ENUM members and update them.

-   **OLD (Incorrect):** `SitemapCurationStatus.Selected`
-   **NEW (Correct):** `SitemapCurationStatus.SELECTED`

### Step 4: Update Mocks and Fixtures

Any test fixtures or `unittest.mock` patches that target the old file paths or object structures must be updated.

**Action:** Search for any mocks targeting `src.models.api_models` or local ENUMs within model files and retarget them to the new locations in `src/schemas` and `src/models/enums.py`.

## 3. Part 2: Service & Router Layer (Verification)

**I have already refactored the code in the Service and Router layers.** No further coding changes should be required from the team in these areas. However, it is crucial that the team **reviews and understands** these changes to be able to work with the new patterns effectively.

### Step 1: Review Affected Service Files

**Action:** The team responsible for services should review the following files to see how the ENUM imports were corrected. This demonstrates the new pattern of depending only on `src/models/enums.py`.

-   `src/services/sitemap_import_scheduler.py`
-   `src/services/domain_scheduler.py`
-   `src/services/sitemap_scheduler.py`

### Step 2: Review Affected Router & Schema Files

**Action:** The team responsible for the API layer should review the following files. This demonstrates the full architectural pattern: routers use schemas from `src/schemas`, and schemas use ENUMs from `src/models/enums`.

-   **Routers Changed:**
    -   `src/routers/sitemap_files.py`
    -   `src/routers/batch_sitemap.py`
    -   `src/routers/domains.py`
    -   `src/routers/local_businesses.py`

-   **New Schemas to Review:**
    -   `src/schemas/sitemap_file.py`
    -   `src/schemas/domain.py`
    -   `src/schemas/local_business.py`

## 4. Conclusion

Completing the test suite remediation (Part 1) and the database migration are the two critical paths to getting the application running again. The verification steps (Part 2) are essential for team knowledge transfer and ensuring adherence to the new architecture going forward. My role is to support you in this process. Please let me know of any issues you encounter.
