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
| **Existing: `src/services/sitemap_import_service.py`** | Called by `sitemap_import_scheduler.py`. Transaction-aware (accepts session from `run_job_loop`); handles its own commit/rollback for processing a single sitemap. Fetches sitemap content, parses URLs, creates `Page` records. Updates `SitemapFile.sitemap_import_status` to `Completed` or `Error`. Error handling and status updates are compliant. | **CRITICAL VIOLATION:**<br>1. **Tenant ID Usage:** Uses `tenant_id` from `SitemapFile` when creating `Page` records. This VIOLATES the `09-TENANT_ISOLATION_REMOVED.md` architectural standard.<br><br>**Compliant Aspects:**<br>1. Function Naming: `process_single_sitemap_file` is appropriate for its role and clear.<br>2. Session Management: Compliant for its role in processing a single item from a scheduled job.<br>3. File Naming: `sitemap_import_service.py` is descriptive and standard. | 1. **CRITICAL:** Remove all usage of `tenant_id` from `SitemapFile` when creating/updating `Page` records. Ensure `Page` model and DB schema no longer expect/require `tenant_id`. | [x] Service properly accepts session parameters<br>[x] No direct session creation (session from `run_job_loop`)<br>[x] Transaction handling appropriate for scheduler-called service<br>[x] Function naming standardized (`process_single_sitemap_file`)<br>[x] File name standardized (`sitemap_import_service.py`)<br>[x] Correctly updates `SitemapFile` status post-processing<br>[x] Comprehensive error handling implemented<br>[ ] **CRITICAL: No tenant filtering/usage (Currently VIOLATED)** | `Partially Compliant (Critical Violation)` |
| **Existing: `src/services/sitemap_import_scheduler.py`** | Monitors `SitemapFile.sitemap_import_status == SitemapImportProcessStatusEnum.Queued`. Uses `run_job_loop` (SDK component, uses `get_background_session()`). Calls `SitemapImportService.process_single_sitemap_file` for actual sitemap processing. `setup_sitemap_import_scheduler()` is registered in `main.py`. Configured via settings. | **Compliant:**<br>1. File Naming: `sitemap_import_scheduler.py` is descriptive and acceptable.<br>2. Session Management: Compliant via `run_job_loop` SDK.<br>3. Queue Processing & Registration: Compliant. | 1. None required; consider renaming to `sitemap_curation_scheduler.py` only if absolute naming consistency with a conceptual parent workflow (`sitemap_curation`) is desired (current name is acceptable and functional). | [x] Uses `get_background_session()` (via SDK)<br>[x] Proper transaction management (via SDK)<br>[x] Has standard queue processing function (via SDK)<br>[x] Has `setup_sitemap_import_scheduler` function<br>[x] Properly registered in `main.py`<br>[x] Configured through settings<br>[x] Processes records with correct status (`sitemap_import_status == QUEUED`) | `Compliant` |

<!-- STOP_FOR_REVIEW -->
