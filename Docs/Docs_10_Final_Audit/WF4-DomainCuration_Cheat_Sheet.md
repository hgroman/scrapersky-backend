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
| **MISSING: `src/services/domain_curation_service.py`** | No dedicated service file exists for the domain_curation workflow. Business logic (complex listing, dual-status updates) is handled directly in `src/routers/domains.py` using SQLAlchemy ORM. | **PRIMARY GAP (Service):** Deviation from Pattern A (Dedicated Service - Blueprint Sec 2.1.A). `src/routers/domains.py` listing logic (dynamic sort, multi-filter) exceeds Pattern B scope (Blueprint Sec 3.2.A). Router uses no explicit tenant_id filtering (aligns with tenant isolation removal for some entities - Memory `50f678e2-3197-40c2-8bd7-45f7b4d08098`). | 1. **Create `src/services/domain_curation_service.py`**. Extract complex query/update logic from `src/routers/domains.py` into this service. Ensure methods accept `AsyncSession`.<br>2. Simplify `src/routers/domains.py` to delegate to the new service. | [x] Router code (`domains.py`) reviewed<br>[ ] Service file created<br>[ ] Business logic (esp. complex list query) extracted<br>[ ] Methods use session parameter<br>[ ] Router simplified | `To Do` |
| **Existing (`src/services/domain_scheduler.py`) but NOT for WF4** <br><br> **MISSING: `src/services/domain_curation_scheduler.py` (for WF4 `sitemap_analysis_status`)** | `src/services/domain_scheduler.py` exists and processes domains based on `Domain.status` and `DomainStatusEnum`. It uses `get_background_session()` and standard registration. <br><br>**However, it does NOT process `Domain.sitemap_analysis_status` (used by WF4-DomainCuration).** Thus, WF4 effectively has NO dedicated scheduler for its specific background task. | **PRIMARY GAP (Scheduler):** `WF4-DomainCuration` lacks a scheduler to process its `sitemap_analysis_status` queue. This is a critical gap for its dual-status pattern (Blueprint Sec 2.2.D.1).
<br>**Regarding `src/services/domain_scheduler.py` (general scheduler):**
- Naming (`domain_scheduler.py`) is generic, not workflow-specific (acceptable if it's a general utility).
- It correctly uses `get_background_session()` and standard registration via `scheduler_instance`. | 1. **Create `src/services/domain_curation_scheduler.py`** specifically for `WF4-DomainCuration`.
2. Implement logic to query domains where `sitemap_analysis_status == SitemapAnalysisStatusEnum.QUEUED`.
3. Implement processing logic (e.g., sitemap extraction/analysis) and update `sitemap_analysis_status` to `PROCESSING`, then `COMPLETED` or `ERROR`.
4. Use `get_background_session()` and register with the shared `scheduler_instance` in `main.py`.
5. Rename `domain_scheduler.py` to `generic_domain_scheduler.py` if it's confirmed to be a general utility, to avoid confusion (optional, but good practice). | [x] `domain_scheduler.py` code reviewed
[ ] **New `domain_curation_scheduler.py` created for WF4**
[ ] New scheduler processes `sitemap_analysis_status`
[ ] New scheduler uses `get_background_session()`
[ ] New scheduler registered in `main.py` | `To Do` |

**NOTE: While "Code is King" acknowledges the current implementation, the technical debt analysis above identifies significant deviations from ideal architectural patterns. The router-centric implementation likely exceeds the bounded scope defined for this pattern and requires refactoring toward the Dedicated Service pattern.**

<!-- STOP_FOR_REVIEW -->
