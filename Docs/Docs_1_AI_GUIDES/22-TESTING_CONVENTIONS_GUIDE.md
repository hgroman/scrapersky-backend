# 22-TESTING_CONVENTIONS_GUIDE.md

**Document ID:** 22-TESTING_CONVENTIONS_GUIDE
**Date:** 2023-04-03
**Status:** Active

## Objective

Provide a concise guide to the standard conventions and environment setup expected for writing automated tests (Unit, Integration, E2E) within this project. This aims to save developers time by clarifying established patterns.

## Key Conventions

1.  **Test Runner:**

    - Use `pytest` for executing the automated test suite.

2.  **Database Sessions in Tests:**

    - **DO NOT** rely on specialized database fixtures (like a hypothetical `test_db_session`).
    - **DO** acquire database sessions directly within test functions using the standard application utility `src.session.async_session.get_session`:

      ```python
      from src.session.async_session import get_session

      async with get_session() as session:
          # Perform DB setup or verification
          await session.execute(...)
      ```

    - This pattern ensures tests use the same session handling as the application code.
    - Refer to `scripts/testing/test_batch_e2e.py` or `scripts/testing/test_page_scraper.py` for examples.

3.  **Test Data Isolation & Management:**

    - Use transactions (e.g., `async with session.begin():`) within tests where appropriate to manage state changes.
    - Create helper functions within test files to seed necessary prerequisite data and clean it up afterwards (e.g., `seed_...`, `cleanup_...`).
    - Aim for tests to run against an isolated test database if possible, or ensure cleanup logic prevents interference with development data.

4.  **Authentication & Context:**

    - **API Tests:** Use the development token (`DEV_TOKEN` from `.env`) via the `Authorization: Bearer <token>` header when using `httpx.AsyncClient` for E2E tests.
    - **User/Tenant:** Utilize standard development IDs (e.g., `DEV_USER_ID`, `DEFAULT_TENANT_ID` from `.env`) when tests require user or tenant context. See `Docs/Docs_1_AI_GUIDES/10-TEST_USER_INFORMATION.md` for more context.

5.  **Mocking External Services:**

    - **Mandatory:** All external network calls (e.g., Google Maps API, external scrapers) **MUST** be mocked using `unittest.mock.patch` in Integration and E2E tests.
    - This ensures test reliability, speed, and avoids unintended external interactions or costs.
    - Patch the specific client method making the external call (e.g., `patch('googlemaps.Client.place', ...)`).

6.  **Scope of Automated Tests vs. Scripts:**
    - The `tests/` directory contains the automated test suite (unit, integration, e2e) run by `pytest`.
    - Utility scripts in `scripts/db`, `scripts/testing`, etc., are intended for **manual** inspection, setup, debugging, or specific testing scenarios outside the main `pytest` execution flow.

Adhering to these conventions ensures consistency and maintainability across the project's test suite.

---

## Test Environment Setup & Execution

This section covers how to set up your local environment to run the automated test suite located in the `tests/` directory.

1.  **Editable Installation (Crucial):**

    - The project uses `pytest` which needs to import the application code (`src/`).
    - To make the `src` directory importable as the `scrapersky` package from the `tests/` directory (and elsewhere), you **MUST** install the project in editable mode within your active virtual environment.
    - Run this command from the project root directory:
      ```bash
      pip install -e .
      ```
    - This uses the `setup.py` file to link the installed package to your source code.

2.  **Pytest Configuration (`pytest.ini`):**

    - This file configures the `pytest` runner.
    - Key settings include:
      - `testpaths = tests`: Tells pytest to look for tests in the `tests/` directory and its subdirectories.
      - `asyncio_mode = auto`: Configures `pytest-asyncio` to automatically discover and run `async def` test functions.
      - `markers`: Defines custom markers (like `e2e`, `integration`) to categorize tests and prevent warnings.

3.  **Test Fixtures (`tests/conftest.py`):**

    - This file is automatically discovered by `pytest`.
    - It's used to define **fixtures**: functions decorated with `@pytest.fixture` that provide data or setup/teardown logic needed by tests.
    - For example, it currently provides default values for `business_type`, `job_id`, `batch_id`, and `domain` used by some tests.
    - Test functions request fixtures by including their names as arguments.

4.  **Running Tests:**

    - Ensure your virtual environment is active and you have run `pip install -e .`.
    - Navigate to the project root directory in your terminal.
    - Run the test suite using the command:
      ```bash
      pytest
      ```
    - Add `-k <keyword>` to run specific tests matching a keyword.
    - Add `-m <marker>` to run only tests with a specific marker (e.g., `pytest -m integration`).

5.  **Current Status (as of 2025-05-01):**
    - The core test suite (10 tests located directly under `tests/`) currently passes.
    - There are numerous warnings (~48) related to dependency deprecations (Pydantic V1, SQLAlchemy, `datetime.utcnow()`) that should be addressed eventually.
    - More specific integration/E2E tests (previously located in `tests-wrong/`) failed when last attempted and have been archived by the user. These would require updates to run correctly.
