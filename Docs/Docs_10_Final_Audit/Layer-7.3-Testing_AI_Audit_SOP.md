# AI Standard Operating Procedure: Layer 7 (Testing) Audit

**Document Version:** 1.0
**Date:** 2025-05-14
**Purpose:** This Standard Operating Procedure (SOP) guides an AI assistant in performing a comprehensive audit of Layer 7 (Testing) components and practices within the ScraperSky backend. The goal is to identify deviations from established architectural standards (as defined in the `Layer-7-Testing_Blueprint.md`) and recommend improvements to ensure robust quality assurance.

---

## Introduction: Context from Architectural Truth

This SOP is designed to be used in conjunction with the `Layer-7-Testing_Blueprint.md` (Version 1.0 or later). Both documents are informed by `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`, which notes that Layer 7 documentation may be outdated and need refreshing. This audit process is key to identifying specific areas for such updates and ensuring alignment with modern testing best practices using Pytest.

---

## 1. Prerequisites & Inputs

Before starting the audit of Layer 7 components, ensure you have access to and have reviewed:

1.  **The Layer 7 Blueprint (Version 1.0 or later):**
    - `Docs/Docs_10_Final_Audit/Layer-7-Testing_Blueprint.md` (Primary standard).
2.  **Core Architectural & Convention Guides:**
    - `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`.
    - `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md` (for any existing test naming or structure conventions).
3.  **Target for Audit Output:**
    - The specific audit checklist, report document, or section where Layer 7 findings will be recorded.
4.  **Relevant Source Code Files & Artifacts:**
    - Test directories (e.g., `src/tests/` or `tests/`, including subdirectories like `tests/models/`, `tests/services/`).
    - `conftest.py` files at various levels.
    - CI configuration files (e.g., `.github/workflows/ci.yml`).
    - (If available) Test coverage reports.

---

## 2. Audit Procedure

Audit Layer 7 by examining test code structure, individual tests, fixtures, and CI integration:

### Step 2.1: Audit Test Framework & Organization (Overall Structure)

1.  **Identify:** Examine the main test directory (`tests/` or `src/tests/`) and its subdirectories. Check `pyproject.toml` for test dependencies.
2.  **Analyze Against Blueprint (Section 2.1):**
    - Verify Pytest is the primary framework and `httpx` (or similar `AsyncClient` provider) is used for API tests.
    - Check if test file naming conventions (`test_*.py`, `*_test.py`) are followed.
    - Assess if the test directory structure mirrors the `src/` application structure.
3.  **Document Gaps:** Note use of other frameworks without justification, incorrect file naming, or disorganized test directory structure.

### Step 2.2: Audit Individual Test Files & Functions

For each test file (e.g., `tests/services/test_user_service.py`):

1.  **Identify:** Examine test functions (`def test_...():`).
2.  **Analyze Against Blueprint (Sections 2.1, 2.2):**
    - Verify test function naming (`test_...`).
    - Assess if assertions are clear and specific.
    - **Determine Test Type:** Is it a unit or integration test? Is this appropriate for the component under test?
    - **Unit Test Isolation:** If a unit test, are external dependencies (DB, other services, network) properly mocked?
    - **Integration Test Scope:** If an integration test, does it realistically test component interactions (e.g., service with DB)?
    - **Layer-Specific Focus:** Does the test primarily verify the responsibilities of the layer its component belongs to?
3.  **Document Gaps:** Note unclear assertions, inappropriate test types, lack of isolation in unit tests, or tests not focusing on the layer's responsibilities.

### Step 2.3: Audit Fixtures (`conftest.py` and local fixtures)

1.  **Identify:** Examine fixtures defined in `conftest.py` files and locally within test modules.
2.  **Analyze Against Blueprint (Section 2.3):**
    - Is fixture usage promoting DRY principles (avoiding repetitive setup)?
    - Are fixture scopes (`function`, `module`, `session`) used appropriately?
    - Are shared fixtures correctly placed in `conftest.py`?
    - Are fixture names clear and descriptive?
3.  **Document Gaps:** Note lack of fixture usage leading to repetition, incorrect scoping, or poorly named/organized fixtures.

### Step 2.4: Audit Mocking & Patching Practices

Within unit tests primarily:

1.  **Identify:** Locate uses of `mocker` (from `pytest-mock`) or `unittest.mock.patch`.
2.  **Analyze Against Blueprint (Section 2.4):**
    - Is mocking targeted correctly (dependencies of the SUT, not its internals)?
    - Is `patch` used effectively (e.g., as a context manager)?
    - Is it clear what is being mocked and how?
    - Is there evidence of over-mocking, especially in tests that should be integration tests?
3.  **Document Gaps:** Note overly broad mocking, unclear mock setup, or mocking in integration tests where real components should be used.

### Step 2.5: Audit Test Data Management

1.  **Identify:** How is test data created and managed? (e.g., via fixtures, factories, hardcoded in tests).
2.  **Analyze Against Blueprint (Section 2.5):**
    - **Isolation:** Is test data isolated between tests? Is a test database used and correctly managed (e.g., reset/rolled back)?
    - Is test data setup readable and relevant to the test scenario?
3.  **Document Gaps:** Note shared test data state that could lead to flaky tests, use of production DB for tests, or overly complex/irrelevant test data.

### Step 2.6: Audit CI Testing Integration

1.  **Identify:** Examine CI configuration files (e.g., GitHub Actions workflows).
2.  **Analyze Against Blueprint (Section 2.6):**
    - Is there a CI pipeline that automatically runs the test suite?
    - Does it run on relevant triggers (e.g., push, PR)?
    - Does the CI report successes/failures clearly?
    - (If discernible) Are there signs of flaky tests impacting CI reliability?
3.  **Document Gaps:** Note missing CI integration, unreliable CI test runs, or poor reporting of test results.

### Step 2.7: Populate Audit Report / Cheat Sheet (Layer 7 Section)

For each identified gap across all audited aspects:

1.  **Area / Component:** Specify the relevant area (e.g., `Test Organization`, `File: tests/services/test_user_service.py::test_create_user`, `Fixture: user_fixture`, `CI Config`).
2.  **Gap Analysis (Technical Debt Identification):**
    - Follow the logic outlined in **Section 4, Step 3 ("Document Technical Debt")** of the `Layer-7-Testing_Blueprint.md`.
    - Clearly list each deviation identified.
    - **Prioritize issues like low test coverage (if inferable), lack of test isolation, flaky tests, and missing CI integration.**
    - Reference the specific Blueprint section/criterion (e.g., "Blueprint 2.2.2: Unit test for `UserService.create` makes a real database call.", "Blueprint 2.3.1: Repetitive setup code in `test_pages_router.py`; should use fixtures.", "Blueprint 2.6.1: No CI pipeline found to automate test execution.", "Blueprint 2.1.2: Test file `users_tests.py` does not follow `test_*.py` convention.").
    - Use `<!-- NEED_CLARITY: [Your question here] -->` if compliance is ambiguous.
3.  **Prescribed Refactoring Actions:**
    - Suggest concrete actions aligned with **Section 4, Step 4 ("Prescribe Refactoring Actions")** of the `Layer-7-Testing_Blueprint.md`.
    - Examples:
      - "Add unit tests for `AuthService` methods, mocking external calls."
      - "Refactor `test_process_data` in `test_utils.py` to use `mocker` for `requests.post`."
      - "Create a shared `db_session` fixture in `conftest.py` for integration tests."
      - "Implement a GitHub Actions workflow to run `pytest` on all pull requests."
      - "Investigate and stabilize flaky tests in `test_integration_workflow.py`."

### Step 2.8: Review and Finalize

1.  Ensure all key aspects of Layer 7 (organization, test types, fixtures, mocking, data management, CI) have been assessed.
2.  Verify that the audit report entries are clear, concise, and reference the Layer 7 Blueprint.
3.  Mark any sections with `<!-- STOP_FOR_REVIEW -->` for complex issues or areas requiring significant strategic decisions (e.g., adopting a new testing tool or strategy).

### Step 2.9: Conclude Audit for this Layer

1.  **Audit Focus:** Reiterate that the actions performed under this SOP (Steps 2.1-2.8) are strictly for auditing and documenting findings. The primary output is the comprehensive Layer 7 assessment.
2.  **No Refactoring:** Confirm that no code refactoring is performed during this audit phase. All identified technical debt and refactoring actions are documented for future work by the appropriate persona.
3.  **Output Destination:** Ensure all findings from Step 2.7 (Populate Audit Report / Cheat Sheet) are consolidated into the designated Layer 7 audit report document, typically located in `Docs/Docs_10_Final_Audit/Audit Reports Layer 7/Layer7_Testing_Audit_Report.md` (or a similarly named file specific to this layer).
4.  **Next Steps:** Once all Layer 7 aspects as outlined in this SOP have been audited and documented, notify the USER that the Layer 7 Testing audit is complete. Await further instructions.

---

## 3. Output

- A comprehensive Layer 7 audit report document (e.g., `Layer7_Testing_Audit_Report.md`) detailing assessments for all relevant testing aspects, including identified gaps, technical debt, and prescribed refactoring actions (for future implementation).

---

This SOP is a living document and may be updated as the Blueprint evolves, testing tools change, or new insights are gained.
