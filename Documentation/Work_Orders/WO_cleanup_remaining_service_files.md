# Work Order: Cleanup Remaining Service Files & Misplaced Schemas

**Status:** Pending Research
**Priority:** Medium
**Created:** 2025-11-21
**Updated:** 2025-11-21 (Added Router Cleanup)

## Context
The "WF1-WF7 Naming Standardization" project (Nov 2025) successfully renamed core models, schedulers, and routers. However, during verification, we discovered several files that were not included in the original plan but should be standardized to match the new convention.

## Objectives
1.  **Audit Service Logic Files:** Identify all service logic files (not schedulers) that belong to specific workflows but lack the `wfX_` prefix.
2.  **Audit Misplaced Schemas:** Identify Pydantic schema files incorrectly located in `src/models/` instead of `src/schemas/`.
3.  **Plan Renaming/Moving:** Create a plan to rename these files and move schemas to the correct directory.

## Identified Candidates (Preliminary List)

### 1. Service Logic Files (Missing `wfX_` prefix)
These files contain the core business logic for workflows but weren't renamed.

*   **WF1 (Places):**
    *   `src/services/places/*` (Entire directory content)
*   **WF2 (Deep Scan):**
    *   `src/services/website_scan_service.py` (Likely WF2 or WF4)
*   **WF3 (Local Business):**
    *   `src/services/business_to_domain_service.py`
*   **WF4 (Domains):**
    *   `src/services/domain_to_sitemap_adapter_service.py`
*   **WF5 (Sitemaps):**
    *   `src/services/sitemap_files_service.py`
    *   `src/services/sitemap_import_service.py`
    *   `src/services/sitemap/*` (Entire directory content)
*   **WF7 (Pages/Contacts):**
    *   `src/services/WF7_V2_L4_1of2_PageCurationService.py` (Needs rename to `wf7_page_curation_service.py`)
    *   `src/services/page_scraper/*`
    *   `src/services/crm/*`
    *   `src/services/email_validation/*`

### 2. Misplaced Schemas (In `src/models/`)
These files appear to be Pydantic schemas but are located in the SQLAlchemy models directory.

*   `src/models/sitemap_file.py` (Confirmed Pydantic schema, imports from `wf5_sitemap_file.py`)
*   *Check for others...*

### 3. Legacy Routers (In `src/routers/v2` and `src/routers/v3`)
These routers are active but should be moved to `src/routers/` with `wfX_` prefix.

*   **WF4 (Domains):**
    *   `src/routers/v3/domains_direct_submission_router.py` -> `src/routers/wf4_domain_direct_submission_router.py`
    *   `src/routers/v3/domains_csv_import_router.py` -> `src/routers/wf4_domain_csv_import_router.py`
*   **WF7 (Pages/Contacts):**
    *   `src/routers/v2/WF7_V2_L3_1of1_PagesRouter.py` -> `src/routers/wf7_page_v2_router.py`
    *   `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py` -> `src/routers/wf7_page_v3_router.py`
    *   `src/routers/v3/contacts_router.py` -> `src/routers/wf7_contact_router.py`
    *   `src/routers/v3/contacts_validation_router.py` -> `src/routers/wf7_contact_validation_router.py`
    *   `src/routers/v3/n8n_webhook_router.py` -> `src/routers/wf7_n8n_webhook_router.py`

### 4. Ghost Files (To Delete)
Files that were supposed to be removed/renamed but still exist.

*   `src/services/domain_sitemap_submission_scheduler.py` (Old version, replaced by `wf4_sitemap_discovery_scheduler.py`)
*   `src/routers/v2/sitemap_files.py` (Appears unused, check imports)

## Action Plan for Researcher
1.  **Verify Usage:** Check where each candidate file is imported.
2.  **Confirm Workflow:** definitively assign each file to a WF (1-7).
3.  **Propose New Names:** e.g., `sitemap_files_service.py` -> `wf5_sitemap_files_service.py`.
4.  **Propose Moves:** e.g., `src/models/sitemap_file.py` -> `src/schemas/wf5_sitemap_file_schemas.py`.
5.  **Draft Execution Script:** Create a script similar to `wf_rename_atomic.py` for this batch.

## Constraints
*   **DO NOT** rename shared services (`job_service.py`, `profile_service.py`, `tenant.py`).
*   **DO NOT** break imports - use `check_imports.py` to verify.
