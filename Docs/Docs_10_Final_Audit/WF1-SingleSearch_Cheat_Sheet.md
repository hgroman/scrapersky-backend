# ScraperSky Workflow Audit & Refactoring Cheat Sheet: Single Search

**Document Version:** 1.0
**Date:** 2025-05-10
**Workflow Under Audit:** `single_search`
**Lead Auditor/Implementer:** Henry Groman & Windsurf AI

## 0. Purpose & Pre-Requisites

**Purpose:** This document guides the systematic audit of the existing `single_search` workflow against the ScraperSky `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`. Its goal is to identify all technical debt and deviations, prescribe refactoring actions, and track the workflow's journey to full standardization. Upon completion, this document (or a derivative) should serve as the updated, authoritative "Workflow-Specific Cheat Sheet" for the now-standardized `single_search`.

**Core Guiding Principles (from AI Collaboration Constitution & Project Work Order):**

- **Zero Assumptions:** If any aspect of the current state, the target standard, or the refactoring path is unclear, HALT and seek explicit clarification.
- **Document-First Iteration:** Findings and refactoring plans for each section should be documented _before_ extensive code changes are made. This sheet is the living record of that process.
- **Blueprint as Authority:** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` are the final arbiters of the target state.

**Key Reference Documents for this Audit:**

1.  **Target Standard:** `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
2.  **Standard Clarifications:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
3.  **Existing Workflow Analysis (if available, e.g., from `Docs/Docs_5_Project_Working_Docs/52-Gold-Standard-Blue-Print/`):**
    - `52.B-Analysis-Layer_Main_App_Integration.md` (for `single_search` if covered)
    - `52.C-Analysis-Layer_API_Routers.md` (for `single_search` if covered)
    - `52.D-Analysis-Layer_Services.md` (for `single_search` if covered)
    - `52.E-Analysis-Layer_Data_Models.md` (for `single_search` if covered)
4.  **Source Code:** Direct review of `src/` files related to `single_search`.
5.  **Audit Log (if pre-existing issues noted):** `Docs/Docs_7_Workflow_Canon/Audit/WORKFLOW_AUDIT_JOURNAL.md`

---

## 1. Workflow Overview & Initial Assessment

### 1.1 Workflow Name & Core Details

- **Current Workflow Name (as in code/docs):** `single_search`
- **Target Standardized Workflow Name (snake_case, as per Conventions Guide):** `single_search`
  - _Note: This name will drive all other naming conventions._
- **Primary Source Table(s):** `place_search`
- **Primary Purpose/Functionality:** To perform location-based searches using the Google Places API and store the results for review and further processing.
- **Key Entry Points (e.g., API routes, Scheduler job names):** To be determined during router analysis

### 1.2 Overall Current State Summary & Major Known Issues

- Initial review of the models indicates non-standard status columns and lack of workflow-specific enums for the curation and processing statuses.
- Status tracking is currently implemented as a simple string column rather than using the standard enum pattern.
- The `place_search` model lacks workflow-specific curation and processing status columns.

---

## 2. Component-by-Component Audit & Refactoring Plan

### 2.1 Layer 1: Models & ENUMs

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** Sections 3, 4
- **Current Progress:** [0/2] components standardized.

#### Component Inventory & Gap Analysis

| Component File & Path                      | Current State Assessment                                                                                                                                                                                                                                                                                                                                                                                                                                   | Standard Comparison & Gap Analysis                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Prescribed Refactoring Actions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Verification Checklist                                                                                                                                                                                                                                                                                                             | Status  |
| :----------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------ |
| **`src/models/place_search.py` (Primary)** | The `PlaceSearch` model uses a simple string status column named `status` with default value "pending". No enums are defined for status values. Status options are not formalized in any way. No dedicated status columns for workflow processing or curation. Status is stored as `String(50)` with default="pending".                                                                                                                                    | Deviations: <br>1. Missing `SingleSearchCurationStatus` enum class<br>2. Missing `SingleSearchProcessingStatus` enum class<br>3. Status column is named `status` instead of `single_search_curation_status`<br>4. No processing status column<br>5. No database enum types created<br>6. Status is stored as simple string, not enum<br>7. Status values don't match standard patterns (e.g., "pending" vs. "New")                                                                            | 1. Create `SingleSearchCurationStatus` enum in `place_search.py` with standard values: "New", "Queued", "Processing", "Complete", "Error", "Skipped"<br>2. Create `SingleSearchProcessingStatus` enum with standard values: "Queued", "Processing", "Complete", "Error"<br>3. Create PostgreSQL enum types via SQL: `singlesearchcurationstatus` and `singlesearchprocessingstatus`<br>4. Rename `status` column to `single_search_curation_status`<br>5. Add `single_search_processing_status` column<br>6. Add `single_search_processing_error` column (TEXT)                                                                                                                                                                                                                                                                                                                                | [ ] Python ENUM classes match standard values & naming (`SingleSearchCurationStatus`, etc.)<br>[ ] DB ENUM types match standard naming (`singlesearchcurationstatus`, etc.)<br>[ ] ENUMs defined in model file.<br>[ ] `create_type=False` used.<br>[ ] Status columns correctly named & typed.<br>[ ] Error message column added. | `To Do` |
| **`src/models/place.py` (Related)**        | Contains two enum classes: `PlaceStatusEnum` with non-standard values ("New", "Selected", "Maybe", "Not a Fit", "Archived") and `GcpApiDeepScanStatusEnum` with standard values ("Queued", "Processing", "Completed", "Error"). The status field uses `PlaceStatusEnum` with DB enum type `place_status_enum`. A `deep_scan_status` field uses `GcpApiDeepScanStatusEnum` with DB enum type `gcp_api_deep_scan_status_enum`. Both use `create_type=False`. | Deviations: <br>1. `PlaceStatusEnum` uses non-standard values, particularly "Selected" instead of "Queued" and "Completed" instead of "Complete"<br>2. `GcpApiDeepScanStatusEnum` uses "Completed" instead of standard "Complete"<br>3. Enum names don't follow `{WorkflowName}CurationStatus` and `{WorkflowName}ProcessingStatus` patterns (should be `SingleSearchCurationStatus` or similar if tied to WF1)<br>4. DB enum type names don't follow `{workflow_name}curationstatus` pattern | 1. **Clarification:** Based on service analysis, `src/models/place.py` IS part of WF1 (`single_search`) as it stores the search results. <br>2. Rename `PlaceStatusEnum` to `SingleSearchPlaceStatus` (or a more fitting WF1-specific name if "curation" or "processing" is not the right fit for its role in WF1, though `PlaceStatusEnum.New` is used by `PlacesStorageService`). Standardize its values (e.g., `New`, `Queued`, `Processing`, `Complete`, `Error`, `Skipped` if it serves as a primary curation status for these `Place` records _within the context of WF1_). <br>3. If `GcpApiDeepScanStatusEnum` is _also_ used by WF1, it should be `SingleSearchDeepScanStatus` and its values standardized. If it serves a _different_ workflow (e.g., a deep scan workflow like WF7), it should be standardized under that workflow. <br>4. Update corresponding DB ENUM type names. | [ ] `place.py` enums standardized for WF1 (`single_search`) context.<br>[ ] Enum names follow `SingleSearch...Status` pattern.<br>[ ] Enum values are standard.<br>[ ] DB enum type names standardized.                                                                                                                            | `To Do` |

<!-- STOP_FOR_REVIEW -->

### 2.2 Layer 3: API Routers (Pattern B - Router-Handled CRUD & Dual-Status Updates)

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** Section 3.2 (Routers - Pattern B: {workflow}_CRUD.py)
- **Relevant `Q&A_Key_Insights.md` Section(s):** "Python Backend - API Routers"
- **Current Progress:** [0/1] components standardized.

#### Component Inventory & Gap Analysis

| Router File & Path                          | Current State Assessment (Endpoints, Logic, DB Interaction, Tenant Handling, Transactions, JIRA Tickets) | Standard Comparison & Gap Analysis (Deviations from Blueprint Section 3.2) | Prescribed Refactoring Actions | Verification Checklist (from Blueprint 3.2 & Conventions) | Status |
| :------------------------------------------ | :------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------- | :----------------------------- | :------------------------------------------------------------------ | :----- |
| **`src/routers/places_staging.py`**         | - Handles `Place` entity staging, relevant to `single_search`.<br>- `list_all_staged_places()`: Uses **Raw SQL**. Re-introduces `tenant_id` from token with **hardcoded default**.<br>- `update_places_status_batch()`: Good ORM object manipulation. Uses `session.begin()`. No tenant issues.<br>- `queue_places_for_deep_scan()`: Uses `session.execute(update())`. Explicit commit/rollback. No tenant issues.<br>- `list_staged_places()`: Good ORM `select()`. No tenant issues. | - **Naming**: File name `places_staging.py` is descriptive. Acceptable for its role.<br>- **ORM/Raw SQL**: `list_all_staged_places` uses Raw SQL (**Major Violation**). Other update methods are compliant/conditionally compliant.<br>- **Tenant ID Isolation**: `list_all_staged_places` re-introduces `tenant_id` logic and hardcoded default (**Major Violation**). Other endpoints are compliant.<br>- **Transaction Mgmt**: `queue_places_for_deep_scan` uses explicit commit/rollback (**Minor Deviation**). `update_places_status_batch` is compliant.<br>- **Hardcoding**: Default `tenant_id` in `list_all_staged_places` (**Major Violation**). | - **`list_all_staged_places`**: <br>  1. Replace Raw SQL with SQLAlchemy ORM/Core `select()`.<br>  2. Remove all `tenant_id` retrieval (from token) and filtering logic.<br>  3. Remove hardcoded default `tenant_id`.<br>- **`queue_places_for_deep_scan`**: <br>  1. Refactor explicit `session.commit()` / `session.rollback()` to use `async with session.begin():`. | `[ ] No raw SQL in list_all_staged_places`<br>`[ ] No tenant_id filtering or hardcoded tenant_id in list_all_staged_places`<br>`[ ] queue_places_for_deep_scan uses async with session.begin()`<br>`[ ] Session mgmt, ORM usage in updates, error handling correct.` | `To Do` |

<!-- STOP_FOR_REVIEW -->

### 2.4 Python Backend - Services (Processing Logic & Schedulers)

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** Section 5 (Services), Section 9 (Schedulers & Background Tasks) in older guide version, now primarily Section 5 in unified guide.
- **Relevant `Q&A_Key_Insights.md` Section(s):** "Python Backend - Services", "Python Backend - Task Management"
- **Current Progress:** [0/3] components standardized.

#### Component Inventory & Gap Analysis

| Service/Scheduler File(s) & Path(s)                | Current State Assessment (Function Naming, Logic Separation, Session Handling, Transactions, Raw SQL, Error Handling, JIRA Tickets) | Standard Comparison & Gap Analysis (Deviations from Blueprint & Layer-4-Service-Audit.md) | Prescribed Refactoring Actions | Verification Checklist (from Layer-4-Service-Audit.md & Conventions) | Status |
| :------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------- | :----------------------------- | :------------------------------------------------------------------- | :----- |
| **`src/services/places/places_search_service.py`** | - Class `PlacesSearchService`. Interacts with Google Places API and updates `PlaceSearch` records.                                  |

- `search_places()`: External API calls, no DB session. Good API key/error handling (SCRSKY-251 potentially addressed for external calls).
- `search_and_store()`: Accepts session. Uses `session.execute(update_stmt)` for `PlaceSearch` status (ORM concern). Calls `PlacesStorageService` (passes session).
- `get_search_by_id()`: Accepts session. (Full ORM usage to be verified).
- `process_places_search_background()`: Standalone function. Correctly uses `get_background_session()` and manages its own transaction for background task entry. | - **Naming**: File/class name `PlacesSearchService` doesn't align with `{workflow_name}_service.py` (i.e., `single_search_service.py`). Role seems specific to Google API & `PlaceSearch` table for WF1.
- **ORM**: `search_and_store()` uses `session.execute(update())` for `PlaceSearch` status update - should ideally use ORM object manipulation for updates.
- **Session**: `search_places()` doesn't need a DB session (correct). Others accept session or manage it correctly for background tasks.
- **Transactions**: Aware of external transaction ownership (`search_and_store`); background task manages its own (correct). | - **Naming**: Consider if this service should be renamed/refactored to `single_search_service.py` if it's the primary service for WF1, or if its role is a distinct helper. If helper, current name might be acceptable if clearly documented.
- **ORM**: Refactor `search_and_store()` to update `PlaceSearch` status via ORM object modification (fetch, set, flush) instead of `session.execute(update_stmt)`.
- **Tenant ID**: Ensure `get_search_by_id` has `tenant_id` references removed. | `[ ] Accepts session as argument (for DB methods)<br>[ ] Does NOT create/manage transactions (except background entry points)<br>[ ] No raw SQL (`session.execute()`for DML is a concern)<br>[ ] Adheres to naming conventions (file/class name needs review for WF1 context)<br>[ ] Standard error handling implemented (SCRSKY-251 for external calls looks okay)<br>[ ]`get_background_session` used appropriately.` | `To Do` |
  | **`src/services/places/places_service.py`** | - Class `PlacesService`. Generic helper for `Place` and `PlaceSearch` DB ops.
- All methods accept `AsyncSession`.
- No methods create own sessions/transactions.
- `get_by_id()`: Uses `text()` for tenant_id filtering (Raw SQL Violation).
- `update_status()`, `batch_update_status()`: Use `session.execute(update_stmt)` (ORM concern).
- `create_search()`: Good ORM usage for insert.
- **Tenant ID**: `get_by_id`, `create_search` (and likely others not fully shown) still use `tenant_id`. Contradicts removal mandate. | - **Naming**: `PlacesService` is generic. Its role for WF1 is as a helper. Current name acceptable if its generic nature is intended and documented.
- **ORM**: `get_by_id()` uses `text()` (raw SQL) - clear violation. `update_status` and `batch_update_status` use `session.execute(update())` - ORM concern (SCRSKY-225 if widespread).
- **Tenant ID**: Active `tenant_id` usage in multiple methods is a major violation of tenant isolation removal.
- **Error Handling**: Minimal; relies on caller. | - **ORM**: Refactor `get_by_id` to remove `text()` and use ORM for all query parts. Refactor `update_status`, `batch_update_status` to use ORM object manipulation.
- **Tenant ID**: Remove ALL `tenant_id` parameters and logic from all methods.
- **Error Handling**: Consider adding more specific error logging/handling within service methods. | `[ ] Accepts session as argument<br>[ ] Does NOT create/manage transactions<br>[ ] No raw SQL (`text()`is a violation,`session.execute()` for DML is a concern)<br>[ ] Adheres to naming conventions (seems okay for a generic helper)<br>[ ] Standard error handling (minimal currently)` | `To Do` |
  | **`src/services/places/places_storage_service.py`** | - Class `PlacesStorageService`. Stores/updates `Place` entities, used by `places_search_service`.
- All methods accept `AsyncSession`.
- No methods create own sessions/transactions.
- `store_places()`: Uses good ORM for new inserts (`session.add()`) and updates (attribute modification on fetched objects). Calls `PlacesService.get_by_id()` (inherits its issues).
- **Tenant ID**: `store_places()` and other methods (from outline) accept and use `tenant_id`. Uses hardcoded default tenant UUIDs (SCRSKY-226).
- **Hardcoding**: Uses hardcoded default UUIDs for tenant and user (SCRSKY-226).
- **Error Handling**: `store_places()` has fairly robust local error handling. | - **Naming**: `PlacesStorageService` is descriptive. Role for WF1 is a helper. Acceptable.
- **ORM**: Generally good in `store_places`, but other outlined update methods need checking for `session.execute(update())` usage (SCRSKY-225).
- **Tenant ID**: Active `tenant_id` usage and hardcoded default UUIDs are major violations of tenant isolation and config standards (SCRSKY-226).
- **Error Handling**: `store_places` is good. Propagation strategy should be consistent. | - **Tenant ID**: Remove ALL `tenant_id` parameters and logic. Remove hardcoded default UUIDs; rely on proper user/context propagation if needed, or make them configurable if truly system-level defaults are required (unlikely for tenant_id).
- **Hardcoding**: Address SCRSKY-226 by removing hardcoded default UUIDs.
- **ORM**: Verify other update methods; refactor if they use `session.execute(update_stmt)`. | `[ ] Accepts session as argument<br>[ ] Does NOT create/manage transactions<br>[ ] No raw SQL (`session.execute()`for DML in other methods is a concern)<br>[ ] Adheres to naming conventions (seems okay for a helper)<br>[ ] Standard error handling (good in`store_places`)<br>[ ] No hardcoded connection/tenant parameters (SCRSKY-226 violated)` | `To Do` |

<!-- STOP_FOR_REVIEW -->
