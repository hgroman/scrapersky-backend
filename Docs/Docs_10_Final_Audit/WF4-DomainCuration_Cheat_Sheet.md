# ScraperSky Workflow Audit & Refactoring Cheat Sheet

**Document Version:** 1.0
**Date:** 2025-05-11
**Workflow Under Audit:** `domain_curation` (WF4-DomainCuration)
**Lead Auditor/Implementer:** AI Assistant

## 0. Purpose & Pre-Requisites

**Purpose:** This document guides the systematic audit of the existing `domain_curation` workflow against the ScraperSky `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`. Its goal is to identify all technical debt and deviations, prescribe refactoring actions, and track the workflow's journey to full standardization. Upon completion, this document (or a derivative) should serve as the updated, authoritative "Workflow-Specific Cheat Sheet" for the now-standardized `domain_curation`.

**Core Guiding Principles (from AI Collaboration Constitution & Project Work Order):**

- **Zero Assumptions:** If any aspect of the current state, the target standard, or the refactoring path is unclear, HALT and seek explicit clarification.
- **Document-First Iteration:** Findings and refactoring plans for each section should be documented _before_ extensive code changes are made. This sheet is the living record of that process.
- **Blueprint as Authority:** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` are the final arbiters of the target state.

**Key Reference Documents for this Audit:**

1.  **Target Standard:** `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
2.  **Standard Clarifications:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
3.  **Source Code:** Direct review of `src/` files related to `domain_curation`.

---

## 1. Workflow Overview & Initial Assessment

### 1.1 Workflow Name & Core Details

- **Current Workflow Name (as in code/docs):** `domain_curation`
- **Target Standardized Workflow Name (snake_case, as per Conventions Guide):** `domain_curation`
- **Primary Source Table(s):** `domain`
- **Primary Purpose/Functionality:** Management and curation of domain records, with workflow for sitemap analysis
- **Key Entry Points (e.g., API routes, Scheduler job names):**
  - `/api/v3/domains` - List domains with filtering and pagination
  - Domain sitemap curation status update endpoint
  - Domain sitemap extraction functionality

### 1.2 Overall Current State Summary & Major Known Issues

- WF4-DomainCuration follows a router-centric pattern where business logic is implemented directly in the router (`src/routers/domains.py`)
- The workflow follows the dual-status pattern with a primary curation status field (`sitemap_curation_status`) and a queue status field (`sitemap_analysis_status`)
- There is no dedicated service file specifically for this workflow, but there is a `domain_scheduler.py` for background processing

---

## 2. Component-by-Component Audit & Refactoring Plan

**Strategic Note on Layer Prioritization:** To better inform the analysis of all architectural layers, the audit for each workflow will begin with Layer 4 (Services). The understanding gained from the service layer's logic and data handling will provide critical context for subsequently auditing other components. The methodology outlined in `Docs/Docs_10_Final_Audit/Layer-4-Service-Audit.md` should be referenced for conducting the Layer 4 audit when using this template.

For each component type below, assess the current state of the `domain_curation` workflow, compare it to the standards, identify gaps, and plan refactoring actions.

### 2.4 Python Backend - Services (Processing Logic & Schedulers)

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** Section 4.2 and 4.3
- **Relevant `Q&A_Key_Insights.md` Section(s):** "Layer 4: Python Backend - Services", "Layer 4: Python Backend - Task Management"

| Service/Scheduler File(s) & Path(s) | Current State Assessment (Function Naming, Logic Separation, Registration) | Standard Comparison & Gap Analysis (Deviations) | Prescribed Refactoring Actions | Verification Checklist | Status |
| :---------------------------------- | :------------------------------------------------------------------------ | :---------------------------------------------- | :----------------------------- | :--------------------- | :----- |
| **MISSING: `src/services/domain_curation_service.py`** | No dedicated service file exists for the domain_curation workflow. Instead, business logic is handled directly in the router (`src/routers/domains.py`). The router contains both API endpoint definitions and database operations using SQLAlchemy ORM. Current implementation uses **Router-Handled CRUD & Dual-Status Updates** pattern. | **PRIMARY GAP:** Use of Router-Handled pattern is a deviation from the ideal Dedicated Service pattern, which recommends business logic encapsulation in dedicated service files.<br><br>**SCOPE ASSESSMENT:** Analysis of `domains.py` indicates it likely **exceeds the bounded scope** defined in Blueprint Section 3.2. The router appears to implement complex logic beyond simple CRUD and dual-status updates, including pagination, filtering, and potentially complex data manipulations.<br><br>This implementation pattern creates technical debt against the architectural standard that recommends service-layer business logic. | 1. **Critical Priority:** Create a new `src/services/domain_curation_service.py` file to extract business logic from the router.<br>2. Implement service methods that accept session parameters for transaction awareness.<br>3. Extract complex logic from router to service, particularly pagination, filtering, and any external API interactions.<br>4. Keep only simple CRUD operations and transaction boundaries in the router.<br>5. Ensure proper integration between router, service, and existing scheduler. | [ ] New `domain_curation_service.py` file created<br>[ ] Business logic extracted from router<br>[ ] Service methods accept session parameters<br>[ ] Router simplified to appropriate scope<br>[ ] Integration with scheduler maintained<br>[ ] Proper error handling implemented | `To Do` |
| **Existing: `src/services/domain_scheduler.py`** | There appears to be a scheduler file for domain operations, which likely handles the processing of domains with `sitemap_analysis_status` set to 'Queued'. This aligns with the standard pattern for background processing. | **GAPS:**<br>1. Non-standard naming convention - should be `domain_curation_scheduler.py` for full compliance with Blueprint Section 2.2.<br>2. Unknown if properly implements `get_background_session()` for session management.<br>3. Unknown if properly follows standard queue processing function patterns.<br>4. Unclear registration mechanism in `main.py`.<br><br>While the scheduler exists, these potential deviations create technical debt against the architectural standard. | 1. Review the scheduler file to ensure it properly:<br>   - Uses `get_background_session()` for session management<br>   - Has a proper queue processing function following naming conventions<br>   - Has a setup function registered in `main.py`<br>2. Consider renaming to `domain_curation_scheduler.py` for consistency with the workflow name.<br>3. Ensure configuration through settings for interval and batch size. | [ ] Scheduler uses `get_background_session()`<br>[ ] Has standard queue processing function<br>[ ] Has setup function registered in `main.py`<br>[ ] Consider renaming for consistency<br>[ ] Configured through settings | `To Do` |

**NOTE: While "Code is King" acknowledges the current implementation, the technical debt analysis above identifies significant deviations from ideal architectural patterns. The router-centric implementation likely exceeds the bounded scope defined for this pattern and requires refactoring toward the Dedicated Service pattern.**

<!-- STOP_FOR_REVIEW -->
