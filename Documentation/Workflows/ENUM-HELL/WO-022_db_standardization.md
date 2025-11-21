# WO-022: Database Standardization (Enums & Foreign Keys)

**Work Order:** WO-022
**Status:** ✅ Approved / Ready for Execution
**Target Implementation:** 2025-11-20
**Implementer:** Antigravity
**Approver:** User

---

## Executive Summary

**WO-022** addresses critical database standardization issues identified in the recent audit. It focuses on two high-priority "Fix Now" categories:
1.  **PascalCase Database Enums**: Renaming [DomainExtractionStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#192-200) and [SitemapCurationStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#152-161) to snake_case to match the project standard.
2.  **Missing Foreign Keys**: Adding missing `FOREIGN KEY` constraints to `tenant_id` columns in [local_businesses](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/local_businesses.py#47-161), [places_staging](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/places_staging.py#491-627), [sitemap_files](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/sitemap_files.py#54-105), and `sitemap_urls`.

**Critical Constraint**: This Work Order strictly adheres to the "Guardian's Paradox" principles. **NO AI will execute the database migration.** The AI will generate the migration artifact, and a human/authorized agent must execute it.

---

## Proposed Changes

### 1. Database Schema (Migration Artifact)

**File:** [supabase/migrations/20251120000000_fix_enums_and_fks.sql](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/supabase/migrations/20251120000000_fix_enums_and_fks.sql)

**Changes:**
*   **Rename Types**:
    *   [DomainExtractionStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#192-200) -> `domain_extraction_status_enum`
    *   [SitemapCurationStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#152-161) -> `sitemap_curation_status_enum`
*   **Add Constraints**:
    *   `local_businesses.tenant_id` -> FK to `tenants.id`
    *   `places_staging.tenant_id` -> FK to `tenants.id`
    *   `sitemap_files.tenant_id` -> FK to `tenants.id`
    *   `sitemap_urls.tenant_id` -> FK to `tenants.id`

### 2. Python Models

**Files:**
*   [src/models/local_business.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py)
*   [src/models/sitemap.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py)
*   [src/models/domain.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/domain.py)
*   [src/models/place.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py)

**Changes:**
*   Update `Column(Enum(..., name="..."))` to use the new snake_case names.
*   Update `Column(..., ForeignKey("tenants.id"))` to include the constraint definition.

---

## Impact Analysis (Safety Check)

### 1. Router Impact Analysis
**Finding:** SAFE.
*   **[src/routers/local_businesses.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/local_businesses.py)**: Uses [DomainExtractionStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#192-200) (Python class). Logic relies on Python Enum members (e.g., `.Queued`), not the DB type name string.
*   **[src/routers/domains.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/domains.py)**: Uses [SitemapCurationStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#152-161) (Python class). Logic maps API strings to Python Enum members. No direct dependency on DB type name.
*   **[src/routers/sitemap_files.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/sitemap_files.py)**: Uses [SitemapImportCurationStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py#54-62) (Python class). Safe.

### 2. Service Impact Analysis
**Finding:** SAFE.
*   **[src/services/domain_extraction_scheduler.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/domain_extraction_scheduler.py)**:
    *   Uses [DomainExtractionStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#192-200) (Python class) for status values.
    *   Uses `run_job_loop` SDK with `status_field_name="domain_extraction_status"`.
    *   **Safety**: The *Python Model Attribute Name* (`domain_extraction_status`) is NOT changing. Only the underlying *Database Type Name* is changing. SQLAlchemy handles this mapping transparently.

---

## Verification Plan

### 1. Automated Verification
**Script:** [tests/verification_remediation.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/tests/verification_remediation.py)
*   **Checks**:
    *   Inspects SQLAlchemy Model `__table__.columns`.
    *   Verifies [Enum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#202-224) columns have `name="snake_case_name"`.
    *   Verifies `tenant_id` columns have `ForeignKey` defined.
*   **Status**: Created and Passed locally (verifying the *code* changes).

### 2. Manual Verification (Post-Migration)
*   **Action**: User/Authorized Agent runs the SQL migration.
*   **Check**: Inspect Supabase Dashboard or run SQL `\dT+` to confirm enum names and `\d table_name` to confirm FK constraints.

---

## Rollback Plan

If the migration fails or causes issues:
1.  **Revert Code**: Revert Python model changes to point back to PascalCase names.
2.  **Revert DB**: Execute `ALTER TYPE ... RENAME TO ...` to restore PascalCase names (if migration partially succeeded).

---

## Approval Request

**Action Required**: Please review this Work Order.
*   [ ] Approve the scope and safety analysis.
*   [ ] Authorize the creation of the SQL migration artifact (to be executed by you).
