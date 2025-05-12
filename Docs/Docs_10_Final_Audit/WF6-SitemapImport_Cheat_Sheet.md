# ScraperSky Workflow Audit & Refactoring Cheat Sheet

**Document Version:** 1.0
**Date:** 2025-05-11
**Workflow Under Audit:** `sitemap_import` (WF6-SitemapImport)
**Lead Auditor/Implementer:** AI Assistant

## 0. Purpose & Pre-Requisites

**Purpose:** This document guides the systematic audit of the existing `sitemap_import` workflow against the ScraperSky `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`. Its goal is to identify all technical debt and deviations, prescribe refactoring actions, and track the workflow's journey to full standardization. Upon completion, this document (or a derivative) should serve as the updated, authoritative "Workflow-Specific Cheat Sheet" for the now-standardized `sitemap_import`.

**Core Guiding Principles (from AI Collaboration Constitution & Project Work Order):**

- **Zero Assumptions:** If any aspect of the current state, the target standard, or the refactoring path is unclear, HALT and seek explicit clarification.
- **Document-First Iteration:** Findings and refactoring plans for each section should be documented _before_ extensive code changes are made. This sheet is the living record of that process.
- **Blueprint as Authority:** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` are the final arbiters of the target state.

**Key Reference Documents for this Audit:**

1.  **Target Standard:** `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
2.  **Standard Clarifications:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
3.  **Source Code:** Direct review of `src/` files related to `sitemap_import`.

---

## 1. Workflow Overview & Initial Assessment

### 1.1 Workflow Name & Core Details

- **Current Workflow Name (as in code/docs):** `sitemap_import`
- **Target Standardized Workflow Name (snake_case, as per Conventions Guide):** `sitemap_import`
- **Primary Source Table(s):** `sitemap_file` (input), `page` (output)
- **Primary Purpose/Functionality:** Processing sitemap files to extract URLs and create page records
- **Key Entry Points (e.g., API routes, Scheduler job names):**
  - No direct API endpoints (background process)
  - Triggered by status field in `sitemap_file` table
  - Scheduler job for processing sitemap files

### 1.2 Overall Current State Summary & Major Known Issues

- WF6-SitemapImport follows a service-oriented background processing pattern
- Implemented as a background task in `sitemap_import_service.py` and `sitemap_import_scheduler.py`
- Triggered by the `sitemap_import_status` field in the `sitemap_file` table
- Unlike the router-centric workflows, this one has no direct API endpoints

---

## 2. Component-by-Component Audit & Refactoring Plan

**Strategic Note on Layer Prioritization:** To better inform the analysis of all architectural layers, the audit for each workflow will begin with Layer 4 (Services). The understanding gained from the service layer's logic and data handling will provide critical context for subsequently auditing other components. The methodology outlined in `Docs/Docs_10_Final_Audit/Layer-4-Service-Audit.md` should be referenced for conducting the Layer 4 audit when using this template.

For each component type below, assess the current state of the `sitemap_import` workflow, compare it to the standards, identify gaps, and plan refactoring actions.

### 2.4 Python Backend - Services (Processing Logic & Schedulers)

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** Section 4.2 and 4.3
- **Relevant `Q&A_Key_Insights.md` Section(s):** "Layer 4: Python Backend - Services", "Layer 4: Python Backend - Task Management"

| Service/Scheduler File(s) & Path(s) | Current State Assessment (Function Naming, Logic Separation, Registration) | Standard Comparison & Gap Analysis (Deviations) | Prescribed Refactoring Actions | Verification Checklist | Status |
| :---------------------------------- | :------------------------------------------------------------------------ | :---------------------------------------------- | :----------------------------- | :--------------------- | :----- |
| **Existing: `src/services/sitemap_import_service.py`** | The service implements a `SitemapImportService` class with a primary method `process_single_sitemap_file` that accepts a sitemap file ID and session parameter. The service is properly transaction-aware and designed for background processing. It handles fetching URLs from sitemap files and creating page records. Current implementation uses **Dedicated Service Layer** pattern. | **MINOR GAPS:**<br>1. The primary method is named `process_single_sitemap_file` rather than following the standard pattern `process_single_sitemap_file_for_sitemap_import` (Blueprint Section 2.2).<br>2. Potential gaps in comprehensive error handling and status update patterns.<br><br>Overall, this implementation largely conforms to the ideal Dedicated Service pattern with only minor function naming standardization issues. | 1. Rename the primary method to `process_single_sitemap_file_for_sitemap_import` for full consistency with naming standards defined in Blueprint Section 2.2.<br>2. Review and enhance error handling to ensure it's comprehensive and follows best practices.<br>3. Verify that status updates follow the dual-status pattern for proper workflow triggering.<br>4. Confirm complete removal of any tenant filtering logic. | [ ] Service properly accepts session parameters<br>[ ] Function naming standardized<br>[ ] Comprehensive error handling implemented<br>[ ] Status updates follow dual-status pattern<br>[ ] No tenant filtering logic present | `To Do` |
| **Existing: `src/services/sitemap_import_scheduler.py`** | The scheduler file likely implements background processing for sitemap import, monitoring the `sitemap_import_status` field in the `sitemap_file` table. It should handle session management through `get_background_session()` and implement a `process_sitemap_import_queue` function and a `setup_sitemap_import_scheduler` function. | **POTENTIAL GAPS:**<br>1. Unknown if properly implements `get_background_session()` for session management (Blueprint Section 2.2).<br>2. Unknown if properly manages transaction boundaries as required for scheduler components.<br>3. Unclear if correctly registered in `main.py` via standard setup function.<br>4. Unknown configuration mechanism through settings.<br><br>While the file exists and follows naming conventions, validation of these implementation details is needed to ensure full compliance. | 1. Verify that the scheduler properly uses `get_background_session()` for session management.<br>2. Confirm proper transaction boundary ownership within the scheduler functions.<br>3. Ensure the scheduler is correctly registered in `main.py` through a standard setup function.<br>4. Verify configuration is properly handled through settings for interval and batch size.<br>5. Confirm queue processing function follows standard patterns. | [ ] Uses `get_background_session()`<br>[ ] Proper transaction management<br>[ ] Has standard `process_sitemap_import_queue` function<br>[ ] Has `setup_sitemap_import_scheduler` function<br>[ ] Properly registered in `main.py`<br>[ ] Configured through settings | `To Do` |

<!-- STOP_FOR_REVIEW -->
