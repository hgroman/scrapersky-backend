# ScraperSky Naming & Structural Conventions Guide - Layer 7: Testing

**Date:** 2025-05-11
**Version:** 1.0

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy for architectural alignment
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis.md)** - Comprehensive analysis of layer classification
- **[Q&A_Key_Insights.md](./Q&A_Key_Insights.md)** - Clarifications on implementation standards

**Objective:** This document details the naming and structural conventions for Layer 7 components (Testing) within the ScraperSky backend project. Robust testing is crucial for ensuring workflow reliability and maintainability.

---

## 8. Layer 7: Testing

Robust testing is crucial for ensuring workflow reliability and maintainability. A combination of component-focused tests and workflow integration tests should be implemented.

- **General Test Structure:**

  - Tests are primarily organized by component type within the `tests/` directory (e.g., `tests/services/`, `tests/scheduler/`, `tests/routers/`, `tests/workflows/`).
  - Test files are generally named `test_{module_or_feature_being_tested}.py`.

- **Unit/Component Test Focus & Priority:**

  - **High Priority (MUST have coverage):**
    - **Service Logic (`tests/services/test_{workflow_name}_service.py`):**
      - Primary processing function (e.g., `process_single_{source_table_name}_for_{workflow_name}`).
      - Correct status transitions (e.g., New -> Queued -> Processing -> Complete/Error).
      - Error handling paths and exception management.
    - **Scheduler Logic (`tests/scheduler/test_{workflow_name}_scheduler.py`):**
      - Correct registration with the shared APScheduler instance via its `setup_{workflow_name}_scheduler()` function.
      - Verification that the main scheduler job function (e.g., `process_{workflow_name}_queue()`) correctly calls helper functions (like `run_job_loop`) or service functions with appropriate arguments. Mocking is often used here.
      - Example: `tests/scheduler/test_process_pending_deep_scrapes.py`.
  - **Medium Priority (SHOULD have coverage):**
    - **Routers (`tests/routers/test_{workflow_name}_router.py` or `test_{entity}_routers.py`):**
      - Critical API endpoints, especially status update endpoints.
      - Basic validation of request/response schemas.
    - **Schema Validation:** For complex Pydantic schemas, dedicated tests for validation logic if not covered by router tests.
  - **Lower Priority (Covered as resources allow, or indirectly):**
    - Models (often indirectly tested via service and router tests).
    - Simpler schemas.
    - Utility functions (if not covered by tests of their primary consumers).
  - **Example of Service Test (`tests/services/test_sitemap_deep_scrape_service.py`):** Demonstrates testing individual functions within a service.

- **Workflow Integration Tests (Component Flow Tests):**

  - **Location:** Typically in a dedicated workflow test file, e.g., `tests/workflows/test_{workflow_name}_workflow.py`.
  - **Scope (Mandatory):** For a new workflow, the integration test **MUST** cover the end-to-end flow:
    1.  **Setup:** Create necessary prerequisite data (e.g., source records in the initial state) using fixtures.
    2.  **API Call:** Trigger the workflow by calling the relevant API endpoint (e.g., the Curation Status Update endpoint) using an async test client.
    3.  **Database Verification (Initial):** Assert that the `curation_status` is updated correctly in the database and `processing_status` is set to `Queued` (dual-status update).
    4.  **Scheduler/Processing Execution:**
        - **Option A (Direct Call):** Directly invoke the scheduler's main job function (e.g., `await process_{workflow_name}_queue()`). This provides more thorough testing.
        - **Option B (Mocking):** Mock the single-item processing service function (e.g., `process_single_{source_table_name}_for_{workflow_name}`) to verify it's called correctly by the scheduler. Useful for isolating scheduler logic or avoiding complex dependencies of the service.
    5.  **Database Verification (Final):** Assert that the `processing_status` transitions to `Complete` (or `Error` in failure scenario tests).
    6.  **Side-Effect Verification:** If the processing service has side-effects (e.g., creates new records in another table, calls external services that can be mocked), verify these outcomes.
  - **Example Reference:** While no single existing test may cover all points perfectly, elements of this can be seen in scheduler tests that mock service calls. New workflow integration tests should aim for this comprehensive scope.

- **Test Data Management & Fixtures (`tests/conftest.py` and local fixtures):**

  - **Shared Fixtures (`tests/conftest.py`):**
    - **Database Session:** A fixture providing a test database session with automatic transaction rollback (e.g., `db_session`).
    - **API Client:** An async HTTP client for making API calls (e.g., `async_client`).
    - **Generic Model Creation Utilities/Fixtures:** Reusable fixtures for creating common base entities (e.g., a `test_domain` fixture).
  - **Workflow-Specific Fixtures (in `tests/workflows/test_{workflow_name}_workflow.py` or `tests/services/test_{workflow_name}_service.py`):**

    - Create fixtures to set up entities in specific states required for testing that particular workflow.
    - **Example (for `page_curation`):**

      ```python
      @pytest.fixture
      async def page_for_curation(db_session, test_domain):
          # Creates a Page record in 'New' status
          # ...
          return page

      @pytest.fixture
      async def queued_page_for_processing(db_session, test_domain):
          # Creates a Page record in 'Queued' status
          # ...
          return page
      ```

  - **Guidance:** Strive for a balance: make genuinely reusable fixtures global in `conftest.py`, and keep test-specific or workflow-specific setup close to the tests that use them.

---

This guide is intended to be a living document. As new patterns emerge or existing ones are refined, this document should be updated to reflect the current best practices for the ScraperSky project.
