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
| **Existing: `src/services/sitemap_files_service.py`** | Transaction-aware (accepts session; router uses `get_db_session`). No tenant filtering. Handles dual-status: `update_curation_status_batch` sets `sitemap_import_status` to `QUEUED` when `deep_scrape_curation_status` is `SELECTED`. Implements CRUD & batch updates. This service's role is to manage `SitemapFile` entities and prepare them for processing by queuing them. | **Minor Gaps:**<br>1. File Naming: `sitemap_files_service.py` vs. standard `sitemap_curation_service.py`. (Blueprint Section 2.1)<br>2. Function Naming: CRUD methods are standard. `update_curation_status_batch` is specific and suitable. No `process_single_...` as actual import is handled by `SitemapImportService`.<br><br>Largely compliant for its role in the workflow. | 1. **Recommended:** Rename to `sitemap_curation_service.py` for consistency. | [x] Service properly accepts session parameters<br>[x] No direct session creation<br>[x] All transaction handling delegated to router<br>[x] Function naming standardized (for its role)<br>[ ] File name standardized (currently `sitemap_files_service.py`)<br>[x] Dual-status pattern properly implemented<br>[x] No tenant filtering | `Mostly Compliant` |
| **Existing: `src/services/sitemap_import_scheduler.py`** | Monitors `SitemapFile.sitemap_import_status == SitemapImportProcessStatusEnum.Queued`. Uses `run_job_loop` (SDK component, expected to use `get_background_session()`). Calls `SitemapImportService.process_single_sitemap_file` for actual sitemap processing. `setup_sitemap_import_scheduler()` is registered in `main.py`. | **Compliant:**<br>1. File Naming: `sitemap_import_scheduler.py` is descriptive and acceptable (alternative: `sitemap_curation_scheduler.py`).<br>2. Session Management: Compliant via `run_job_loop` SDK.<br>3. Queue Processing & Registration: Compliant. | 1. Consider renaming to `sitemap_curation_scheduler.py` for absolute naming consistency if desired (current name is acceptable). | [x] Scheduler existence verified<br>[x] Uses `get_background_session()` (via SDK)<br>[x] Has standard queue processing function (via SDK)<br>[x] Has setup function registered in `main.py`<br>[x] Processes records with correct status (`sitemap_import_status == QUEUED`)<br>[ ] Consider renaming for consistency (currently `sitemap_import_scheduler.py`)<br>[x] Configured through settings | `Compliant` |
| **Existing: `src/services/sitemap_import_service.py`** | Called by `sitemap_import_scheduler.py`. Transaction-aware (accepts session from `run_job_loop`); handles its own commit/rollback for processing a single sitemap. Fetches sitemap content, parses URLs, creates `Page` records. Updates `SitemapFile.sitemap_import_status` to `Completed` or `Error`. | **CRITICAL VIOLATION:**<br>1. **Tenant ID Usage:** Uses `tenant_id` from `SitemapFile` when creating `Page` records. This VIOLATES the `09-TENANT_ISOLATION_REMOVED.md` architectural standard.<br><br>**Compliant Aspects:**<br>1. Function Naming: `process_single_sitemap_file` is appropriate.<br>2. Session Management: Compliant for its role in processing a single item from a scheduled job. | 1. **CRITICAL:** Remove all usage of `tenant_id` from `SitemapFile` when creating/updating `Page` records. Ensure `Page` model and DB schema no longer expect/require `tenant_id`. | [x] Service properly accepts session parameters<br>[x] No direct session creation (session from `run_job_loop`)<br>[x] Transaction handling appropriate for scheduler-called service<br>[x] Function naming standardized (`process_single_sitemap_file`)<br>[x] File name standardized (`sitemap_import_service.py`)<br>[x] Correctly updates `SitemapFile` status post-processing<br>[ ] **CRITICAL: No tenant filtering/usage (Currently VIOLATED)** | `Partially Compliant (Critical Violation)` |

<!-- STOP_FOR_REVIEW -->
