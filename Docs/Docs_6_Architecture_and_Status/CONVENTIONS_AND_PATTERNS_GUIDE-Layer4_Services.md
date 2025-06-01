# ScraperSky Naming & Structural Conventions Guide - Layer 4: Services

**Date:** 2025-05-11
**Version:** 1.0

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy for architectural alignment
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis.md)** - Comprehensive analysis of layer classification
- **[Q&A_Key_Insights.md](./Q&A_Key_Insights.md)** - Clarifications on implementation standards

**Objective:** This document details the naming and structural conventions for Layer 4 components (Services and Schedulers) within the ScraperSky backend project. Adherence to these conventions is crucial for maintaining consistency, readability, and maintainability across the codebase, especially concerning transaction management and session handling.

---

## 5. Layer 4: Services

Services encapsulate the business logic for workflows, including schedulers for background tasks and the core processing logic.

- **Scheduler File Names & Structure:**

  - **Strict Convention (Absolute Rule):** For _any_ new workflow that includes a background processing component initiated by a scheduler (e.g., polling for a `_processing_status` of `Queued`), a new, dedicated scheduler file **MUST** be created in `src/services/` and named `{workflow_name}_scheduler.py`.
    - **Rationale:** This ensures clear separation of concerns, allows for independent deployment/scaling of workflows, provides centralized error handling per workflow, and simplifies maintenance. Sharing scheduler files is strongly discouraged and would create technical debt.
    - **Examples:** `src/services/sitemap_import_scheduler.py`, `src/services/domain_scheduler.py`.
    - **Deviation Protocol:** Exceptions are extremely discouraged. Any consideration requires written justification, technical lead approval, explicit code comments, and documentation in canonical YAMLs and the technical debt register.
  - **Standard Helper:** Schedulers typically utilize the `run_job_loop` helper function (from `src/common/curation_sdk/scheduler_loop.py`) for the standard polling pattern.

- **Processing Service File Names:**

  - **Strict Convention:** Core processing logic for a workflow **MUST** reside in a dedicated service file named `src/services/{workflow_name}_service.py`.
  - **Derivation:** From `workflow_name`.
  - **Example (`workflow_name = page_curation`):** `src/services/page_curation_service.py`.

- **Scheduler Job Function Names (main polling function within `{workflow_name}_scheduler.py`):**

  - **Strong Guideline (Default):** `async def process_{workflow_name}_queue():`
  - **Alternative (Less Preferred for New Work):** An existing pattern is `async def process_pending_{entity_plural}():` (e.g., `process_pending_sitemap_imports()`).
  - **Rules for Deviation:** If deviating from the default for significant clarity:
    1.  MUST start with `process_`.
    2.  MUST include the entity being processed.
    3.  MUST clearly describe the action.
    4.  SHOULD end with a collective noun or plural form.
    5.  MUST have a docstring explaining its purpose and any deviation from the standard name.
  - **Example (`workflow_name = page_curation`):** Default is `async def process_page_curation_queue():`.

- **Processing Service Function Names (within `{workflow_name}_service.py` for processing a single item):**

  - **Strict Convention (Mandatory):** `async def process_single_{source_table_name}_for_{workflow_name}(session: AsyncSession, record_id: UUID) -> None:`
  - **Rationale:** Provides maximum clarity on the action (processing a single item), the entity involved (`source_table_name`), and the specific workflow context (`for_{workflow_name}`).
  - **Example (`workflow_name = page_curation`, `source_table_name = page`):** `async def process_single_page_for_page_curation(...)`.
  - **Technical Debt:** Existing deviations are considered technical debt:
    - E.g., `process_single_sitemap_file` in `sitemap_import_service.py` (missing `_for_sitemap_import`).
    - Workflows handling batch processing directly in the scheduler instead of delegating single item processing to a service function with this naming convention.
    - Workflows lacking a dedicated processing service file and function.

- **Scheduler Registration & Settings Pattern (Mandatory for New Workflows):**
  - **Setup Function:** Each `src/services/{workflow_name}_scheduler.py` file **MUST** implement a setup function: `def setup_{workflow_name}_scheduler() -> None:`. This function is responsible for adding the workflow's job(s) to the shared APScheduler instance.
    - **Example (`workflow_name = page_curation`):** `def setup_page_curation_scheduler() -> None:`
  - **Registration in `main.py`:** The `setup_{workflow_name}_scheduler()` function **MUST** be imported into `src/main.py` and called within the `lifespan` context manager to register the job(s) upon application startup.
  - **Settings Import:** Configuration values within service/scheduler files **MUST** be accessed by importing the `settings` instance: `from ..config.settings import settings` (then `settings.YOUR_SETTING`).
  - **Job Configuration Settings Variables:** Parameters for scheduler jobs (e.g., interval, batch size) **MUST** be defined in `src/config/settings.py` and `.env.example` using the convention: `{WORKFLOW_NAME_UPPERCASE}_SCHEDULER_{PARAMETER_NAME}`.
    - **Examples:** `PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES`, `PAGE_CURATION_SCHEDULER_BATCH_SIZE`.

---

## Session Management & Transaction Handling (CRITICAL FOR COMPLIANCE)

This section addresses the most critical technical debt in Layer 4: services incorrectly managing database sessions and transactions.

- **STRICT RULE:** Services **MUST NEVER** create their own sessions or transactions. They receive the `AsyncSession` object as a parameter from the calling layer (typically a router).
- **COMPLIANT Service Pattern Example:**
  ```python
  async def process_single_page_for_page_curation(
      session: AsyncSession, 
      record_id: UUID
  ) -> None:
      # Service logic here - session provided by caller
      # NO transaction creation (e.g., async with session.begin()) in service
      pass
  ```
- **NON-COMPLIANT Anti-Pattern (Technical Debt):**
  ```python
  async def bad_service_function(record_id: UUID):
      async with get_session() as session:  # ❌ WRONG - Service creating session
          # logic here
  ```
- **Current Compliance Crisis:** Only **11%** of Layer 4 services currently follow the compliant pattern. This is the primary reason for the low compliance rate in this layer.
- **Root Cause:** Services are creating their own sessions instead of receiving them as parameters via dependency injection.
- **Technical Debt Identification:** Any service function that directly calls `get_session()` or `get_async_session()` (or similar session-creation utilities) is considered non-compliant technical debt and is a primary target for refactoring.
