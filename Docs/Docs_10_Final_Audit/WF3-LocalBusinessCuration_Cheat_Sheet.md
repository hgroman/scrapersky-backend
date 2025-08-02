# ScraperSky Workflow Audit & Refactoring Cheat Sheet

**Document Version:** 1.0
**Date:** 2025-05-11
**Workflow Under Audit:** `local_business_curation` (WF3-LocalBusinessCuration)
**Lead Auditor/Implementer:** AI Assistant

## 0. Purpose & Pre-Requisites

**Purpose:** This document guides the systematic audit of the existing `local_business_curation` workflow against the ScraperSky `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`. Its goal is to identify all technical debt and deviations, prescribe refactoring actions, and track the workflow's journey to full standardization. Upon completion, this document (or a derivative) should serve as the updated, authoritative "Workflow-Specific Cheat Sheet" for the now-standardized `local_business_curation`.

**Core Guiding Principles (from AI Collaboration Constitution & Project Work Order):**

- **Zero Assumptions:** If any aspect of the current state, the target standard, or the refactoring path is unclear, HALT and seek explicit clarification.
- **Document-First Iteration:** Findings and refactoring plans for each section should be documented _before_ extensive code changes are made. This sheet is the living record of that process.
- **Blueprint as Authority:** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` are the final arbiters of the target state.

**Key Reference Documents for this Audit:**

1.  **Target Standard:** `Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md`
2.  **Standard Clarifications:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
3.  **Source Code:** Direct review of `src/` files related to `local_business_curation`.

---

## 1. Workflow Overview & Initial Assessment

### 1.1 Workflow Name & Core Details

- **Current Workflow Name (as in code/docs):** `local_business_curation`
- **Target Standardized Workflow Name (snake_case, as per Conventions Guide):** `local_business_curation`
- **Primary Source Table(s):** `local_business`
- **Primary Purpose/Functionality:** Management and curation of local business data extracted from places, including viewing, filtering, and status updates
- **Key Entry Points (e.g., API routes, Scheduler job names):**
  - `/api/v3/local-businesses` - List businesses with filtering and pagination
  - Status update endpoint for batch status changes

### 1.2 Overall Current State Summary & Major Known Issues

- WF3-LocalBusinessCuration follows a router-centric pattern where business logic is implemented directly in the router (`src/routers/local_businesses.py`)
- The workflow follows the dual-status pattern with a main status field (`status`) and a queue status field (`domain_extraction_status`)
- There is no dedicated service file specifically for this workflow

---

## 2. Component-by-Component Audit & Refactoring Plan

**Strategic Note on Layer Prioritization:** To better inform the analysis of all architectural layers, the audit for each workflow will begin with Layer 4 (Services). The understanding gained from the service layer's logic and data handling will provide critical context for subsequently auditing other components. The methodology outlined in `Docs/Docs_10_Final_Audit/Layer-4-Service-Audit.md` should be referenced for conducting the Layer 4 audit when using this template.

For each component type below, assess the current state of the `local_business_curation` workflow, compare it to the standards, identify gaps, and plan refactoring actions.

### 2.4 Python Backend - Services (Processing Logic & Schedulers)

- **Authoritative Blueprint:** `v_Layer-2.1-Schemas_Blueprint.md`
- **Relevant `Q&A_Key_Insights.md` Section(s):** "Layer 4: Python Backend - Services", "Layer 4: Python Backend - Task Management"

| Service/Scheduler File(s) & Path(s) | Current State Assessment (Function Naming, Logic Separation, Registration) | Standard Comparison & Gap Analysis (Deviations) | Prescribed Refactoring Actions | Verification Checklist | Status |
| :---------------------------------- | :------------------------------------------------------------------------ | :---------------------------------------------- | :----------------------------- | :--------------------- | :----- |
| **MISSING: `src/services/local_business_curation_service.py`** | No dedicated service file exists for the local_business_curation workflow. Instead, business logic is handled directly in the router (`src/routers/local_businesses.py`). The router uses SQLAlchemy ORM (good) but implements notable query logic. Current implementation uses **Router-Handled CRUD & Dual-Status Updates** pattern. | **PRIMARY GAP:** Use of Router-Handled pattern, especially for the listing logic, is a deviation from the ideal Dedicated Service pattern (Pattern A), which recommends business logic encapsulation in dedicated service files (Blueprint Section 2.1.A).<br><br>**SCOPE ASSESSMENT of `src/routers/local_businesses.py`:**<br>- The `update_local_businesses_status_batch` method's dual-status logic aligns with Pattern B (Blueprint Section 3.2.A).
- However, the `list_local_businesses` endpoint, with its dynamic sorting and multiple filter conditions (e.g., `ilike` for name), presents query construction logic that **likely exceeds the 'simple CRUD' scope** intended for Pattern B routers (Blueprint Section 3.2.A). <br>- Uses a hardcoded default tenant ID (Blueprint Section 2.2.B.1 violation if not approved system default).
- Adheres to ORM-only and session dependency (Blueprint Section 3.2.C compliant). | 1. **Recommended:** Create `src/services/local_business_curation_service.py`. Extract the query and update logic from `src/routers/local_businesses.py`, especially the complex listing logic, into this new service.<br>2. Ensure service methods accept `AsyncSession` and manage transactions appropriately.<br>3. Simplify `src/routers/local_businesses.py` to delegate to the new service, retaining Pydantic models and request/response handling. Address hardcoded default tenant ID.<br>4. The dual-status update logic can remain in the router if Pattern B is partially retained, or move to the service for full Pattern A alignment. | [x] Code review of router completed<br>[ ] Decision documented on service extraction (Recommended: Extract)<br>[ ] Service file created<br>[ ] Business logic (esp. complex list query) extracted<br>[ ] Methods follow session parameter pattern<br>[ ] Router simplified, hardcoded tenant ID addressed | `To Do` |
| **MISSING: `src/services/local_business_curation_scheduler.py`** | No dedicated scheduler file exists for the local_business_curation workflow. The workflow uses a dual-status pattern where `domain_extraction_status` is presumably monitored by a background process, but there's no standard scheduler implementation for it. | **CRITICAL GAP:** Missing a dedicated scheduler file, violating the "Dedicated file per workflow" absolute rule (Blueprint Section 2.2) for workflows with background processing.<br><br>**ADDITIONAL GAPS:**<br>1. No clear ownership of background processing for `domain_extraction_status`.<br>2. Lack of standard scheduler pattern implementation with proper registration.<br>3. No clear documentation of how the background processing is currently being handled. | 1. **Critical Priority:** Determine the exact background processing needs for this workflow.<br>2. If domain extraction is handled as part of this workflow (rather than by a different workflow), create a dedicated `local_business_curation_scheduler.py` file with:<br>   - Proper session management with `get_background_session()`<br>   - A standard queue processing function<br>   - Registration in `main.py`<br>3. If confirmed that background processing is handled by another workflow, document this cross-workflow dependency clearly. | [ ] Background processing ownership clarified<br>[ ] Scheduler file created if needed<br>[ ] Proper session handling implemented<br>[ ] Queue processing function implemented<br>[ ] Registered in `main.py`<br>[ ] Cross-workflow dependencies documented | `To Do` |

**NOTE: While "Code is King" acknowledges the current implementation, the technical debt analysis above identifies deviations from ideal architectural patterns. Further code review is needed to determine if the router logic exceeds the bounded scope defined for the Router-Handled pattern.**

<!-- STOP_FOR_REVIEW -->
