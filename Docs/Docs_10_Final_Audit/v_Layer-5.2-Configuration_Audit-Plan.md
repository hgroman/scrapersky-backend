# Layer 5 (Configuration, Standards & Cross-Cutting Concerns) - Actionable Audit Plan

**Date:** 2025-05-21
**Version:** 1.1
**Author:** Cascade (as Audit Plan Architect)
**Derived From:** `Layer-5.1-Configuration_Blueprint.md`, `Layer-5.3-Configuration_AI_Audit_SOP.md`

## 1. Purpose

This document provides a practical, actionable audit plan for Layer 5 (Configuration, Standards & Cross-Cutting Concerns) of the ScraperSky backend. It is designed to guide the audit process, ensuring systematic identification of deviations from the `Layer-5.1-Configuration_Blueprint.md` and adherence to the `Layer-5.3-Configuration_AI_Audit_SOP.md`. The audit will cover settings management, dependency injection, FastAPI application setup, core utilities, and project dependency management.

## 2. Layer 5 Audit Principles (from Blueprint)

These principles, derived from the Layer 5 Blueprint, form the core of this audit plan:

1.  **Centralization:** Provide a single, well-defined location for application-wide settings, configurations, and core utilities.
2.  **Consistency:** Ensure consistent application of cross-cutting concerns like dependency injection, middleware, and foundational application setup.
3.  **Explicitness:** Make configuration sources (e.g., environment variables, `.env` files) and their validation explicit, typically using Pydantic settings management.
4.  **Maintainability:** Structure configuration and core utilities in a way that is easy to understand, modify, and test.
5.  **Security of Sensitive Data (Implicit):** Sensitive information (API keys, secrets, passwords) MUST NOT be hardcoded and must be managed securely (Blueprint 2.1.4).
6.  **Correct Resource Management (Implicit):** Dependencies yielding resources must correctly handle setup and teardown (Blueprint 2.2.2).
7.  **Dependency Pinning (Implicit):** Project dependencies should be pinned to ensure reproducible builds (Blueprint 2.5.1).

## 3. Audit Process Overview (from SOP)

The audit will follow the procedures outlined in `Layer-5.3-Configuration_AI_Audit_SOP.md`, focusing on:

1.  **Settings Management Audit (SOP Step 2.1):** Reviewing `src/core/config.py` (or similar) against Blueprint Section 2.1.
2.  **Dependency Injection Audit (SOP Step 2.2):** Reviewing `src/dependencies.py` (or similar) against Blueprint Section 2.2.
3.  **FastAPI App Setup Audit (SOP Step 2.3):** Reviewing `src/main.py` against Blueprint Section 2.3.
4.  **Core Utilities Audit (SOP Step 2.4):** Reviewing `src/core/`, `src/utils/` against Blueprint Section 2.4.
5.  **Dependency Management Audit (SOP Step 2.5):** Reviewing `pyproject.toml` / `requirements.txt` against Blueprint Section 2.5.
6.  **Documentation:** Findings, gaps, and prescribed refactoring actions will be documented as per SOP Step 2.6, referencing the Blueprint.

### Handling Files with AI (as per SOP & general best practice)

-   **`.env` files:** Actual `.env` files (with secrets) should NOT be directly viewed or exposed. Audit `.env.example` and `docker-compose.yml` or Python settings files for variable *names* and *usage patterns*.
-   **Large Files (`docker-compose.yml`, `main.py` if complex):** Use `view_file` in chunks if necessary, or `codebase_search` / `view_code_item` for specific sections/definitions.
-   **Python Modules (`config.py`, `dependencies.py`):** Use `view_file` for overall structure and `view_code_item` for specific classes/functions.

## 4. Technical Debt Prioritization (from Blueprint Section 4)

1.  **High Priority:**
    *   Hardcoded secrets or configurations (Blueprint 2.1.4).
    *   Improper resource management in dependencies (e.g., leaking DB sessions) (Blueprint 2.2.2).
    *   Unpinned or outdated critical dependencies (Blueprint 2.5.1).
    *   Missing critical configuration leading to runtime failures.
2.  **Medium Priority:**
    *   Missing type hints in settings or dependencies (Blueprint 2.1.2, 2.2.3).
    *   Inconsistent application setup or incorrect middleware order (Blueprint 2.3).
    *   Non-standard patterns without clear justification.
    *   Redundant configurations.
3.  **Low Priority:**
    *   Minor naming inconsistencies if functionality is clear.
    *   Missing non-critical default values.
    *   Layer-specific logic misplaced in `src/core/` if minor and not causing issues (Blueprint 2.4.1) – though still to be noted.
    *   Documentation gaps in `.env.example` or code comments.

## 5. Audit Checklist by Component Type & Workflow Context

This checklist integrates the Blueprint's compliance criteria and the SOP's audit steps. Workflow-specific configuration items (like scheduler variables from `.env`) will be assessed under 'Settings Management'.

### 5.1 Settings Management (e.g., `src/core/config.py`, `.env.example`, `docker-compose.yml`)

**Relevant Blueprint Section: 2.1**
**Relevant SOP Step: 2.1**

- [ ] **Base Class:** Inherits from `pydantic_settings.BaseSettings`.
- [ ] **Type Hinting:** All settings have explicit type hints.
- [ ] **.env Usage:** Prioritizes environment variables, supports `.env` loading. `.env` is in `.gitignore`.
- [ ] **Secret Management:** NO hardcoded secrets (e.g., `GOOGLE_MAPS_API_KEY`). Loaded from env.
- [ ] **Instantiation:** Single, cached instance of settings is available (e.g., via `@lru_cache`).
- [ ] **Workflow Variables (from `0-ScraperSky-Comprehensive-Files-By-Layer-And-Workflow.md`):**
    - [ ] **WF1 (`GOOGLE_MAPS_API_KEY`):** Securely loaded, correctly named.
    - [ ] **WF2 (`SITEMAP_SCHEDULER_*`):** Correctly named, types, defaults, documented in `.env.example`.
    - [ ] **WF3 (Reuses WF2 Config ⚠️):** Document if this sharing is appropriate or if dedicated `LOCAL_BUSINESS_SCHEDULER_*` vars are needed. Assess clarity and potential for conflict.
    - [ ] **WF4 (`DOMAIN_SITEMAP_SCHEDULER_*` ✓):** Verify naming, types, defaults, documentation. Confirm compliance.
    - [ ] **WF5 (Reuses WF2 Config ⚠️):** Document if sharing is appropriate or if dedicated `SITEMAP_CURATION_SCHEDULER_*` vars are needed.
    - [ ] **WF6 (`SITEMAP_IMPORT_SCHEDULER_*` ✓):** Verify naming, types, defaults, documentation. Confirm compliance.
    - [ ] **WF7 (`PAGE_CURATION_SCHEDULER_*` ✓):** Verify naming, types, defaults, documentation. Confirm compliance. Note if `_MAX_INSTANCES` is intentionally missing.
- [ ] **General `.env.example`:** Exists, is up-to-date, includes comments for all variables.
- [ ] **`docker-compose.yml`:** Defines environment variables from `.env` file, provides sensible defaults where appropriate, does not contain secrets.

### 5.2 Dependency Injection Setup (e.g., `src/dependencies.py`)

**Relevant Blueprint Section: 2.2**
**Relevant SOP Step: 2.2**

- [ ] **Standard Functions:** Uses standard names (e.g., `get_db`, `get_current_active_user`).
- [ ] **Resource Management:** Correct setup/teardown for resources (e.g., `get_db` uses `try...finally` or context manager for session).
- [ ] **Type Hinting:** Clear return type hints for dependency functions.
- [ ] **Reusability:** Dependencies are defined once and reused.

### 5.3 FastAPI Application Setup & Middleware (e.g., `src/main.py`)

**Relevant Blueprint Section: 2.3**
**Relevant SOP Step: 2.3**

- [ ] **Clear Initialization:** FastAPI app creation and router inclusion is clear.
- [ ] **Middleware Order:** Logical middleware order (e.g., CORS early).
- [ ] **Standard Middleware:** Uses well-known middleware (e.g., `CORSMiddleware`) correctly.
- [ ] **Router Inclusion:** All active Layer 3 routers are included.
- [ ] **Lifespan Events:** Startup/shutdown events are correctly defined if used.

### 5.4 Core Utilities & Base Classes (e.g., `src/core/`, `src/utils/`)

**Relevant Blueprint Section: 2.4**
**Relevant SOP Step: 2.4**

- [ ] **Cross-Cutting:** Utilities/bases are genuinely cross-cutting, not layer-specific.
- [ ] **Cohesion:** Related utilities are logically grouped.
- [ ] **Minimal Dependencies:** Core utilities have minimal dependencies on higher application layers.
- [ ] **Custom Exceptions:** If defined, are they appropriate and well-placed?

### 5.5 Dependency Management (`pyproject.toml` or `requirements.txt`)

**Relevant Blueprint Section: 2.5**
**Relevant SOP Step: 2.5**

- [ ] **Pinning:** Dependencies are pinned to specific, compatible versions.
- [ ] **Consistency:** Lock file (`poetry.lock`, `pdm.lock`, or `requirements.txt` from a higher-level spec) is in sync and committed.
- [ ] **Unused Dependencies:** (High-level scan) Any obviously unused dependencies?
- [ ] **Prod vs. Dev:** If using `pyproject.toml`, clear separation of production and development dependencies.

## 6. References

- `Docs/Docs_10_Final_Audit/Layer-5.1-Configuration_Blueprint.md`
- `Docs/Docs_10_Final_Audit/Layer-5.3-Configuration_AI_Audit_SOP.md`
- `Docs/Docs_10_Final_Audit/0-ScraperSky-Comprehensive-Files-By-Layer-And-Workflow.md`
- `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`
- `../Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`

## 7. Output

The findings from this audit plan will be used to populate `Docs/Docs_10_Final_Audit/Audit Reports Layer 5/Layer5_Configuration_Audit_Report.md` (or a similarly named file), as per the SOP.
