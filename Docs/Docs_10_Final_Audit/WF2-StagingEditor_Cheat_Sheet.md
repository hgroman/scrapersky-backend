# ScraperSky Workflow Audit & Refactoring Cheat Sheet

**Document Version:** 1.0
**Date:** 2025-05-11
**Workflow Under Audit:** `staging_editor` (WF2-StagingEditor)
**Lead Auditor/Implementer:** AI Assistant

## 0. Purpose & Pre-Requisites

**Purpose:** This document guides the systematic audit of the existing `staging_editor` workflow against the ScraperSky `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`. Its goal is to identify all technical debt and deviations, prescribe refactoring actions, and track the workflow's journey to full standardization. Upon completion, this document (or a derivative) should serve as the updated, authoritative "Workflow-Specific Cheat Sheet" for the now-standardized `staging_editor`.

**Core Guiding Principles (from AI Collaboration Constitution & Project Work Order):**

- **Zero Assumptions:** If any aspect of the current state, the target standard, or the refactoring path is unclear, HALT and seek explicit clarification.
- **Document-First Iteration:** Findings and refactoring plans for each section should be documented _before_ extensive code changes are made. This sheet is the living record of that process.
- **Blueprint as Authority:** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` are the final arbiters of the target state.

**Key Reference Documents for this Audit:**

1.  **Target Standard:** `Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md`
2.  **Standard Clarifications:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
3.  **Source Code:** Direct review of `src/` files related to `staging_editor`.

---

## 1. Workflow Overview & Initial Assessment

### 1.1 Workflow Name & Core Details

- **Current Workflow Name (as in code/docs):** `staging_editor`
- **Target Standardized Workflow Name (snake_case, as per Conventions Guide):** `staging_editor`
- **Primary Source Table(s):** `place`
- **Primary Purpose/Functionality:** Management and curation of Places data, including viewing, filtering, and status updates
- **Key Entry Points (e.g., API routes, Scheduler job names):**
  - `/api/v3/places/staging` - List all staged places
  - `/api/v3/places/status` - Update place status batch endpoint

### 1.2 Overall Current State Summary & Major Known Issues

- WF2-StagingEditor is primarily implemented directly in the router file without dedicated service or scheduler files
- The router uses direct SQLAlchemy operations with raw SQL in places, rather than delegating to a service layer
- The workflow manages `place` statuses, but does not follow the standard dual-status pattern for workflow triggering

---

## 2. Component-by-Component Audit & Refactoring Plan

**Strategic Note on Layer Prioritization:** To better inform the analysis of all architectural layers, the audit for each workflow will begin with Layer 4 (Services). The understanding gained from the service layer's logic and data handling will provide critical context for subsequently auditing other components. The methodology outlined in `Docs/Docs_10_Final_Audit/Layer-4-Service-Audit.md` should be referenced for conducting the Layer 4 audit when using this template.

For each component type below, assess the current state of the `staging_editor` workflow, compare it to the standards, identify gaps, and plan refactoring actions.

### 2.4 Python Backend - Services (Processing Logic & Schedulers)

- **Authoritative Blueprint:** `v_Layer-2.1-Schemas_Blueprint.md`
- **Relevant `Q&A_Key_Insights.md` Section(s):** "Layer 4: Python Backend - Services", "Layer 4: Python Backend - Task Management"

| Service/Scheduler File(s) & Path(s) | Current State Assessment (Function Naming, Logic Separation, Registration) | Standard Comparison & Gap Analysis (Deviations) | Prescribed Refactoring Actions | Verification Checklist | Status |
| :---------------------------------- | :------------------------------------------------------------------------ | :---------------------------------------------- | :----------------------------- | :--------------------- | :----- |
| **MISSING: `src/services/staging_editor_service.py`** | No dedicated service file exists for the staging_editor workflow. Instead, business logic is handled directly in the router (`src/routers/places_staging.py`). The router contains both API endpoint definitions and direct database operations with raw SQL in some cases. Current implementation uses **Router-Handled CRUD & Dual-Status Updates** pattern. | **PRIMARY GAP:** Use of Router-Handled pattern is a deviation from the ideal Dedicated Service pattern, which recommends business logic encapsulation in dedicated service files.<br><br>**ADDITIONAL GAPS:**<br>1. Router logic **exceeds the bounded scope** defined in Blueprint Section 3.2 by containing raw SQL and complex data manipulations beyond basic CRUD and dual-status updates.<br>2. Raw SQL usage violates the ORM-Only rule (Blueprint Section 3.2).<br>3. Implementation deviates from the architectural principle that service layers, not routers, should handle business logic. | 1. **Critical Priority:** Create a new `src/services/staging_editor_service.py` file to extract complex business logic and raw SQL operations from the router.<br>2. Implement methods for listing and updating place statuses that accept session parameters rather than creating sessions directly.<br>3. Replace all raw SQL operations with proper ORM usage.<br>4. Maintain only simple CRUD and status update operations in the router, with transaction boundary management. | [ ] New `staging_editor_service.py` file created<br>[ ] Complex business logic extracted from router<br>[ ] Raw SQL replaced with ORM<br>[ ] Methods accept session parameters<br>[ ] Proper error handling implemented<br>[ ] Router contains only appropriate operations within scope | `To Do` |
| **Existing: `src/services/places/places_service.py`** | This file provides generic place-related operations but is not specific to the staging_editor workflow. It handles operations like getting places by ID, listing, and updating statuses. The service correctly accepts session parameters and doesn't manage transactions itself. However, it retains tenant filtering logic, despite comments indicating it should be removed per architectural mandate. | **GAPS:**<br>1. Not workflow-specific, lacks standard workflow function naming per Blueprint Section 2.2.<br>2. Still contains tenant filtering code despite architectural mandate for tenant isolation removal (Blueprint Section 2.2).<br>3. No standard orchestration methods for processing following the `process_single_{source_table_name}_for_{workflow_name}` pattern. | 1. Keep as a generic entity service but ensure it's properly utilized by the newly created `staging_editor_service.py`.<br>2. Complete the removal of tenant filtering code to comply with architectural mandate.<br>3. Ensure methods follow the session parameter pattern with proper type hints.<br>4. Consider adding standard orchestration methods if this service will be directly involved in workflow processing. | [ ] Tenant filtering code completely removed<br>[ ] Methods follow session parameter pattern<br>[ ] Proper type hints for all functions<br>[ ] Used by the new workflow-specific service | `To Do` |
| **Existing: `src/services/places/places_deep_service.py`** | Extends `PlacesService` and adds functionality for deep scanning places. It creates its own session directly with `get_session()` instead of accepting a session parameter in at least one method (`process_single_deep_scan`). Still contains tenant ID handling despite architectural mandate to remove it. | **CRITICAL GAPS:**<br>1. Creates its own sessions instead of accepting them as parameters, violating key service compliance criteria (Blueprint Section 2.2).<br>2. Still contains tenant handling logic, violating architectural mandate.<br>3. Function naming doesn't follow the standard `process_single_{source_table_name}_for_{workflow_name}` pattern.<br>4. No clear reference to a dedicated scheduler for handling background processing. | 1. **Critical Priority:** Refactor to accept session parameters instead of creating sessions, to properly follow transaction-aware pattern.<br>2. Remove all tenant handling logic to comply with architectural mandate.<br>3. Rename methods to follow standard pattern, e.g., `process_single_place_for_staging_editor`.<br>4. Ensure proper integration with a dedicated scheduler component. | [ ] Methods accept session parameters<br>[ ] No direct session creation<br>[ ] Tenant handling removed<br>[ ] Standard function naming pattern<br>[ ] Integration with scheduler | `To Do` |
| **MISSING: `src/services/staging_editor_scheduler.py`** | No dedicated scheduler file exists for the staging_editor workflow. The workflow does support a deep scan operation that should be handled by a background task, but there's no standard scheduler implementation for it. Instead, the router's `queue_places_for_deep_scan` endpoint directly updates a status field that presumably triggers a process elsewhere (possibly in `places_deep_service.py`). | **CRITICAL GAP:** Missing a dedicated scheduler file, violating the "Dedicated file per workflow" absolute rule (Blueprint Section 2.2).<br><br>**ADDITIONAL GAPS:**<br>1. Lack of standard polling pattern implementation with `run_job_loop`.<br>2. No clear scheduler registration in `main.py`.<br>3. No consistent handling for the `deep_scan_status` field that should trigger background processing. | 1. **Critical Priority:** Create a new `src/services/staging_editor_scheduler.py` file implementing:<br>   - A `process_staging_editor_queue` function to process places with `deep_scan_status == 'Queued'`<br>   - A `setup_staging_editor_scheduler` function for registration<br>   - Proper session management with `get_background_session()`<br>2. Integrate with refactored `places_deep_service.py`.<br>3. Add registration in `main.py`.<br>4. Configure through settings for interval and batch size. | [ ] `staging_editor_scheduler.py` file created<br>[ ] `process_staging_editor_queue` implemented<br>[ ] `setup_staging_editor_scheduler` implemented<br>[ ] Scheduler registered in `main.py`<br>[ ] Proper session handling using `get_background_session()`<br>[ ] Configured through settings | `To Do` |

**NOTE: While "Code is King" acknowledges the current implementation, the technical debt analysis identified above must be addressed to align with architectural standards. The router-centric implementation exceeds the bounded scope defined for this pattern and requires refactoring toward the ideal Dedicated Service pattern.**

<!-- STOP_FOR_REVIEW -->
