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

### 2.1 Python Backend - Models & Enums

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** Sections 3, 4
- **Current Progress:** [0/2] components standardized.

#### Component Inventory & Gap Analysis

| Component File & Path                                | Current State Assessment                                                                                                                                                                                                                                                                                                | Standard Comparison & Gap Analysis                                                                                                                                                                                                                                                                                                                                                              | Prescribed Refactoring Actions                                                                                                                                                                                                                                                                                                                                                                                                    | Verification Checklist                                                                                                                                                                                                                                                                                                             | Status  |
| :--------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------ |
| **`src/models/place_search.py` (Primary)**          | The `PlaceSearch` model uses a simple string status column named `status` with default value "pending". No enums are defined for status values. Status options are not formalized in any way. No dedicated status columns for workflow processing or curation. Status is stored as `String(50)` with default="pending". | Deviations: <br>1. Missing `SingleSearchCurationStatus` enum class<br>2. Missing `SingleSearchProcessingStatus` enum class<br>3. Status column is named `status` instead of `single_search_curation_status`<br>4. No processing status column<br>5. No database enum types created<br>6. Status is stored as simple string, not enum<br>7. Status values don't match standard patterns (e.g., "pending" vs. "New") | 1. Create `SingleSearchCurationStatus` enum in `place_search.py` with standard values: "New", "Queued", "Processing", "Complete", "Error", "Skipped"<br>2. Create `SingleSearchProcessingStatus` enum with standard values: "Queued", "Processing", "Complete", "Error"<br>3. Create PostgreSQL enum types via SQL: `singlesearchcurationstatus` and `singlesearchprocessingstatus`<br>4. Rename `status` column to `single_search_curation_status`<br>5. Add `single_search_processing_status` column<br>6. Add `single_search_processing_error` column (TEXT) | [ ] Python ENUM classes match standard values & naming (`SingleSearchCurationStatus`, etc.)<br>[ ] DB ENUM types match standard naming (`singlesearchcurationstatus`, etc.)<br>[ ] ENUMs defined in model file.<br>[ ] `create_type=False` used.<br>[ ] Status columns correctly named & typed.<br>[ ] Error message column added. | `To Do` |
| **`src/models/place.py` (Related)**                  | Contains two enum classes: `PlaceStatusEnum` with non-standard values ("New", "Selected", "Maybe", "Not a Fit", "Archived") and `GcpApiDeepScanStatusEnum` with standard values ("Queued", "Processing", "Completed", "Error"). The status field uses `PlaceStatusEnum` with DB enum type `place_status_enum`. A `deep_scan_status` field uses `GcpApiDeepScanStatusEnum` with DB enum type `gcp_api_deep_scan_status_enum`. Both use `create_type=False`. | Deviations: <br>1. `PlaceStatusEnum` uses non-standard values, particularly "Selected" instead of "Queued" and "Completed" instead of "Complete"<br>2. `GcpApiDeepScanStatusEnum` uses "Completed" instead of standard "Complete"<br>3. Enum names don't follow `{WorkflowName}CurationStatus` and `{WorkflowName}ProcessingStatus` patterns<br>4. DB enum type names don't follow `{workflow_name}curationstatus` pattern | 1. For `place.py`, consider whether to standardize the existing enums (if part of the `single_search` workflow) or leave them as is (if part of a different workflow)<br>2. If these enums are part of the `single_search` workflow, rename and standardize them; otherwise, note them as belonging to a separate workflow<!-- NEED_CLARITY -->: Is `place.py` considered part of the `single_search` workflow, or is it associated with a different workflow (e.g., "deep_scan")? | [ ] Determine if `place.py` enums need standardization for this workflow<br>[ ] If applicable, standardize enums to match naming conventions<br>[ ] Ensure proper DB enum type naming                                                                                                          | `To Do` |

<!-- STOP_FOR_REVIEW -->
