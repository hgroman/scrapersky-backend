# ScraperSky Workflow Audit & Refactoring Cheat Sheet

**Document Version:** 1.0
**Date:** 2025-05-11
**Workflow Under Audit:** `sitemap_curation` (WF5-SitemapCuration)
**Lead Auditor/Implementer:** AI Assistant

## 0. Purpose & Pre-Requisites

**Purpose:** This document guides the systematic audit of the existing `sitemap_curation` workflow against the ScraperSky `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`. Its goal is to identify all technical debt and deviations, prescribe refactoring actions, and track the workflow's journey to full standardization. Upon completion, this document (or a derivative) should serve as the updated, authoritative "Workflow-Specific Cheat Sheet" for the now-standardized `sitemap_curation`.

**Core Guiding Principles (from AI Collaboration Constitution & Project Work Order):**

- **Zero Assumptions:** If any aspect of the current state, the target standard, or the refactoring path is unclear, HALT and seek explicit clarification.
- **Document-First Iteration:** Findings and refactoring plans for each section should be documented _before_ extensive code changes are made. This sheet is the living record of that process.
- **Blueprint as Authority:** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` are the final arbiters of the target state.

**Key Reference Documents for this Audit:**

1.  **Target Standard:** `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
2.  **Standard Clarifications:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
3.  **Source Code:** Direct review of `src/` files related to `sitemap_curation`.

---

## 1. Workflow Overview & Initial Assessment

### 1.1 Workflow Name & Core Details

- **Current Workflow Name (as in code/docs):** `sitemap_curation`
- **Target Standardized Workflow Name (snake_case, as per Conventions Guide):** `sitemap_curation`
- **Primary Source Table(s):** `sitemap_file`
- **Primary Purpose/Functionality:** Management and curation of sitemap files, including selection for deep scraping
- **Key Entry Points (e.g., API routes, Scheduler job names):**
  - `/api/v3/sitemap-files` - List sitemap files with filtering and pagination
  - Sitemap batch status update endpoint
  - CRUD operations for sitemap files

### 1.2 Overall Current State Summary & Major Known Issues

- WF5-SitemapCuration follows a service-oriented architecture pattern with business logic delegated to a dedicated service (`src/services/sitemap_files_service.py`)
- The router (`src/routers/sitemap_files.py`) manages transaction boundaries and forwards requests to the service
- The service is properly transaction-aware, accepting session parameters rather than creating its own

---

## 2. Component-by-Component Audit & Refactoring Plan

**Strategic Note on Layer Prioritization:** To better inform the analysis of all architectural layers, the audit for each workflow will begin with Layer 4 (Services). The understanding gained from the service layer's logic and data handling will provide critical context for subsequently auditing other components. The methodology outlined in `Docs/Docs_10_Final_Audit/Layer-4-Service-Audit.md` should be referenced for conducting the Layer 4 audit when using this template.

For each component type below, assess the current state of the `sitemap_curation` workflow, compare it to the standards, identify gaps, and plan refactoring actions.

### 2.4 Python Backend - Services (Processing Logic & Schedulers)

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** Section 4.2 and 4.3
- **Relevant `Q&A_Key_Insights.md` Section(s):** "Layer 4: Python Backend - Services", "Layer 4: Python Backend - Task Management"

| Service/Scheduler File(s) & Path(s) | Current State Assessment (Function Naming, Logic Separation, Registration) | Standard Comparison & Gap Analysis (Deviations) | Prescribed Refactoring Actions | Verification Checklist | Status |
| :---------------------------------- | :------------------------------------------------------------------------ | :---------------------------------------------- | :----------------------------- | :--------------------- | :----- |
| **Existing: `src/services/sitemap_files_service.py`** | This file provides a comprehensive service implementation for sitemap file operations. The service is transaction-aware, accepting session parameters rather than creating sessions. The service implements methods for CRUD operations, batch status updates, and pagination. Methods are well-documented with docstrings, and the service follows the proper pattern of being transaction-aware without owning transaction boundaries. Current implementation uses **Dedicated Service Layer** pattern. | **MINOR GAPS:**<br>1. Naming deviation from standard pattern - uses `sitemap_files_service.py` instead of `sitemap_curation_service.py` (Blueprint Section 2.1)<br>2. Function naming may not fully follow the standard `process_single_{source_table_name}_for_{workflow_name}` pattern for processing functions (Blueprint Section 2.2)<br>3. Unclear handling of dual-status pattern for triggering background processing<br><br>Overall, this implementation largely complies with the ideal Dedicated Service pattern, with minor standardization issues. | 1. Consider renaming to `sitemap_curation_service.py` for full consistency with the workflow name.<br>2. Review and standardize function names to follow the `process_single_{source_table_name}_for_{workflow_name}` pattern where applicable.<br>3. Ensure proper implementation of the dual-status pattern for triggering background processes.<br>4. Verify complete removal of any tenant filtering code. | [ ] Service properly accepts session parameters<br>[ ] No direct session creation<br>[ ] All transaction handling delegated to router<br>[ ] Function naming standardized<br>[ ] File name standardized<br>[ ] Dual-status pattern properly implemented<br>[ ] No tenant filtering | `To Do` |
| **Existing/MISSING: `src/services/sitemap_scheduler.py`** | Based on the workflow comparison document, this workflow uses a `deep_scrape_process_status` field for triggering background processing. A scheduler file likely exists to monitor this status field, but it may be named `sitemap_scheduler.py` instead of following the standard `sitemap_curation_scheduler.py` pattern. | **GAPS:**<br>1. If the scheduler exists, non-standard naming convention - should be `sitemap_curation_scheduler.py` for full compliance with Blueprint Section 2.1.<br>2. If non-existent, critical violation of the "Dedicated file per workflow" absolute rule (Blueprint Section 2.2).<br>3. Unknown if properly implements `get_background_session()` for session management.<br>4. Unclear standard queue processing function implementation.<br><br>These deviations (especially if the scheduler is missing) create technical debt against the architectural standard. | 1. **Critical Priority:** Verify if `sitemap_scheduler.py` exists and handles the workflow's background processing.<br>2. If it exists:<br>   - Ensure it properly uses `get_background_session()` for session management<br>   - Verify it has appropriate queue processing and setup functions<br>   - Consider renaming to `sitemap_curation_scheduler.py` for consistency<br>3. If it doesn't exist:<br>   - Create a dedicated `sitemap_curation_scheduler.py` file with all required components<br>   - Register the scheduler in `main.py`<br>   - Configure through settings | [ ] Scheduler existence verified<br>[ ] Uses `get_background_session()`<br>[ ] Has standard queue processing function<br>[ ] Has setup function registered in `main.py`<br>[ ] Processes records with correct status<br>[ ] Consider renaming for consistency<br>[ ] Configured through settings | `To Do` |

<!-- STOP_FOR_REVIEW -->
