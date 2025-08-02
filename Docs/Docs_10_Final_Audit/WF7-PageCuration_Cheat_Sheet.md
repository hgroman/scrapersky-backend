# ScraperSky Workflow Audit & Refactoring Cheat Sheet

**Document Version:** 1.0
**Date:** 2025-05-11
**Workflow Under Audit:** `page_curation` (WF7-PageCuration)
**Lead Auditor/Implementer:** AI Assistant

## 0. Purpose & Pre-Requisites

**Purpose:** This document guides the systematic audit of the existing `page_curation` workflow against the ScraperSky `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`. Its goal is to identify all technical debt and deviations, prescribe refactoring actions, and track the workflow's journey to full standardization. Upon completion, this document (or a derivative) should serve as the updated, authoritative "Workflow-Specific Cheat Sheet" for the now-standardized `page_curation`.

**Core Guiding Principles (from AI Collaboration Constitution & Project Work Order):**

- **Zero Assumptions:** If any aspect of the current state, the target standard, or the refactoring path is unclear, HALT and seek explicit clarification.
- **Document-First Iteration:** Findings and refactoring plans for each section should be documented _before_ extensive code changes are made. This sheet is the living record of that process.
- **Blueprint as Authority:** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` are the final arbiters of the target state.

**Key Reference Documents for this Audit:**

1.  **Target Standard:** `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
2.  **Standard Clarifications:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
3.  **Source Code:** Direct review of `src/` files related to `page_curation`.

---

## 1. Workflow Overview & Initial Assessment

### 1.1 Workflow Name & Core Details

- **Current Workflow Name (as in code/docs):** `page_curation`
- **Target Standardized Workflow Name (snake_case, as per Conventions Guide):** `page_curation`
- **Primary Source Table(s):** `page`
- **Primary Purpose/Functionality:** Management and curation of pages extracted from sitemaps
- **Key Entry Points (e.g., API routes, Scheduler job names):**
  - JavaScript file: `page-curation-tab.js`
  - API endpoints not yet identified (potentially in development)
  - Background processing infrastructure may be in place or planned

### 1.2 Overall Current State Summary & Major Known Issues

- WF7-PageCuration appears to be in development or not fully implemented
- According to the workflow comparison document, this workflow is marked as "(To Be Decided: Router/Service)" for its core logic location
- No router or service files could be readily identified, but the frontend JavaScript file exists

---

## 2. Component-by-Component Audit & Refactoring Plan

**Strategic Note on Layer Prioritization:** To better inform the analysis of all architectural layers, the audit for each workflow will begin with Layer 4 (Services). The understanding gained from the service layer's logic and data handling will provide critical context for subsequently auditing other components. The methodology outlined in `Docs/Docs_10_Final_Audit/Layer-4-Service-Audit.md` should be referenced for conducting the Layer 4 audit when using this template.

For each component type below, assess the current state of the `page_curation` workflow, compare it to the standards, identify gaps, and plan refactoring actions.

### 2.4 Python Backend - Services (Processing Logic & Schedulers)

- **Authoritative Blueprint:** `v_Layer-2.1-Schemas_Blueprint.md`
- **Relevant `Q&A_Key_Insights.md` Section(s):** "Layer 4: Python Backend - Services", "Layer 4: Python Backend - Task Management"

| Service/Scheduler File(s) & Path(s) | Current State Assessment (Function Naming, Logic Separation, Registration) | Standard Comparison & Gap Analysis (Deviations) | Prescribed Refactoring Actions | Verification Checklist | Status |
| :---------------------------------- | :------------------------------------------------------------------------ | :---------------------------------------------- | :----------------------------- | :--------------------- | :----- |
| **MISSING/IN DEVELOPMENT: `src/services/page_curation_service.py`** | Based on the workflow comparison document, a `page_curation_service.py` file is mentioned but could not be located. The workflow is marked as "(To Be Decided: Router/Service)" for its core logic location, suggesting implementation is pending or in progress. | **CRITICAL GAP:** Missing core service implementation file for the workflow.<br><br>This is a significant deviation from the architectural standard defined in Blueprint Section 2, which identifies the Dedicated Service pattern as the ideal implementation approach for workflow business logic.<br><br>As this workflow is still in development, it presents an opportunity to implement the proper pattern from the beginning rather than requiring refactoring later. | 1. **Critical Priority:** Create a `page_curation_service.py` file following the Dedicated Service pattern (Blueprint Section 2).<br>2. Implement methods with proper session handling (accepting session parameters rather than creating sessions).<br>3. Follow standard function naming patterns like `process_single_page_for_page_curation`.<br>4. Implement robust error handling with appropriate try-except blocks and logging.<br>5. Support the dual-status pattern with proper status field updates and transitions. | [ ] Service file created<br>[ ] Methods follow session parameter pattern<br>[ ] Function naming follows standards<br>[ ] Error handling implemented<br>[ ] Dual-status pattern supported<br>[ ] No tenant filtering included<br>[ ] ORM operations instead of raw SQL | `To Do` |
| **MISSING/IN DEVELOPMENT: `src/services/page_curation_scheduler.py`** | No scheduler file could be located for the page_curation workflow. If the workflow requires background processing (which seems likely given the `page_processing_status` field mentioned in the workflow comparison), a scheduler file would be needed. | **CRITICAL GAP:** Missing scheduler implementation for a workflow that includes a processing status field, violating the "Dedicated file per workflow" absolute rule (Blueprint Section 2.2) for workflows with background processing.<br><br>This gap prevents proper background processing of workflow items and breaks the standard architectural pattern for status-driven workflows with asynchronous processing. | 1. **Critical Priority:** Create a `page_curation_scheduler.py` file with:<br>   - A `process_page_curation_queue` function that processes records with appropriate status (e.g., "Queued")<br>   - A `setup_page_curation_scheduler` function for registration<br>   - Proper session management with `get_background_session()`<br>2. Register the scheduler in `main.py` within the application startup lifecycle.<br>3. Configure the scheduler through settings for intervals and batch sizes.<br>4. Ensure proper integration with the service layer for processing logic. | [ ] Scheduler file created<br>[ ] Uses `get_background_session()`<br>[ ] Has standard queue processing function<br>[ ] Has setup function<br>[ ] Registered in `main.py`<br>[ ] Configured through settings<br>[ ] Proper integration with service | `To Do` |

**NOTE: While this workflow appears to be in development, it presents a critical opportunity to implement the proper architectural patterns from the start. Both service and scheduler components should be created following the ideal Dedicated Service pattern outlined in Blueprint Section 2.**

<!-- STOP_FOR_REVIEW -->
