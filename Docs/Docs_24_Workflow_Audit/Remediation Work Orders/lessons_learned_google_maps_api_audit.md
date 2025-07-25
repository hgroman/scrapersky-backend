# Lessons Learned: Google Maps API Workflow Audit & Test Remediation

## 1. Introduction

This document captures the critical lessons, patterns, and gotchas discovered during the intensive debugging and remediation of the Google Maps API workflow and its associated test suite. The goal is to leverage this knowledge to accelerate the upcoming audits of the other five workflows by preventing the same issues from recurring. Adhering to these principles will save significant time and effort.

---

## 2. Core Testing Principles & Environment

The test environment setup is non-negotiable and was the source of several initial, hard-to-diagnose failures.

### 2.1. The Standardized Test User is the Source of Truth

All tests requiring an authenticated user **MUST** be mocked to use the following standardized user. This user is derived from the `get_current_user` JWT dependency. Any deviation will cause authentication or data access errors.

*   **User ID:** `5905e9fe-6c61-4694-b09a-6602017b000a`
*   **Tenant ID:** `550e8400-e29b-41d4-a716-446655440000`
*   **Email:** `hankgroman@gmail.com`

**Implementation:**
Use a `pytest` fixture to override the `get_current_user` dependency for the entire test module.

```python
# in tests/routers/test_google_maps_api.py

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    mock_user = {
        "user_id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "email": "hankgroman@gmail.com",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "roles": ["admin"],
    }
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()
```

### 2.2. All Tests Run Against the Remote Database

Per project mandate, there are no in-memory or local test databases. All `pytest` runs execute against the **live remote Supabase development database**. This means test data can be persistent and may require cleanup. It also means the network connection and database state are real-world factors in test success.

### 2.3. Critical Environment Variables

Some services, particularly those interacting with external APIs, will crash at runtime if their required environment variables are not set. The test environment does not automatically inherit all variables from the runtime environment.

*   **Key Example:** The `places_search_service` crashes without `GOOGLE_MAPS_API_KEY`.
*   **Solution:** The cleanest solution, as implemented, is to patch the service method called by the background task, preventing the external API call entirely. For other tests where the call must be made, use `monkeypatch` to set the variable.

---

## 3. The Right Way to Mock FastAPI Services

This was the single biggest source of failure. Almost every `AssertionError: expected call not found` was due to incorrect mocking.

### 3.1. Problem: Keyword vs. Positional Arguments

FastAPI's dependency injection calls service methods using **keyword arguments**, not positional ones. The database `session` is passed as a keyword argument.

*   **Incorrect Mock Assertion (Positional):**
    ```python
    # This will FAIL
    mock_service.assert_called_once_with(ANY, 'some_id')
    ```
*   **Correct Mock Assertion (Keyword):**
    ```python
    # This will PASS
    from unittest.mock import ANY
    mock_service.assert_called_once_with(session=ANY, job_id='some_id')
    ```
    **Lesson:** Always inspect the service method's signature and use keyword arguments in your mock assertions. Use `unittest.mock.ANY` for injected dependencies like `session`.

### 3.2. Problem: Mismatched Parameter Names

A test was failing because it was asserting a call with `page=1, per_page=100`, but the actual service method expected `limit=100, offset=0`.

**Lesson:** The test is not the source of truth for the implementation. Always verify your mock assertion against the **actual signature of the service method** being called.

---

## 4. Testing Asynchronous Background Tasks

### 4.1. The `202 Accepted` Pattern

For an endpoint that initiates a background task and returns immediately, the correct HTTP status code is `202 Accepted`. The test suite correctly enforces this.

**Lesson:** Ensure your router decorator includes `status_code=202`.

```python
# in src/routers/google_maps_api.py
@router.post("/search/places", response_model=Dict, status_code=202)
def search_places(...):
    # ...
```

### 4.2. How to Isolate the Endpoint

The goal is to test that the endpoint *schedules* the task, not that the task *completes*.

*   **The Wrong Way:** Mocking `fastapi.BackgroundTasks` itself is complicated and was a dead end.
*   **The Right Way:** Use `unittest.mock.patch` to mock the **actual service function that the background task calls**. This prevents the real code from running, allows the endpoint to return `202` immediately, and lets you assert that the service was called once.

```python
# in tests/routers/test_google_maps_api.py
def test_search_places_success():
    with patch("src.routers.google_maps_api.places_search_service.search_and_store") as mock_search_and_store:
        # ... make the API call ...
        assert response.status_code == 202
        mock_search_and_store.assert_called_once()
```

---

## 5. Database, Schema, and Data Integrity

### 5.1. Schema Drift is Real

The initial problems were compounded by "schema drift" where the SQLAlchemy `PlaceSearch` model did not match the actual `place_searches` table in Supabase.

**Lesson:** Before debugging application logic, **always verify that the ORM model is a 1:1 match with the database table schema**. Check column names, types, nullability, and defaults.

### 5.2. ENUMs: The Silent Killers

A major issue was a mismatch in ENUM values between the Python code (`SearchStatus.COMPLETED`) and the database (which had `completed` in lowercase, and was missing other values like `RUNNING`).

**Lesson:** ENUMs must be perfectly synchronized between the application code and the database schema definition. Case sensitivity matters. When debugging status-related issues, immediately inspect the ENUM type definition in the database.

### 5.3. Direct Database Intervention (When Necessary)

While the project convention is ORM-only, the ENUM issues were so fundamental that a direct SQL script (run via the Supabase MCP tool) was the only pragmatic solution, as directed by the user.

**Lesson:** Know how to use the available tools (`supabase-mcp-server` -> `execute_sql`) to inspect or fix low-level database issues when the ORM/application layer is failing or blocked. This should be a last resort, but is a critical tool to have.

---

## 6. Useful Commands

*   **Run a specific test file with verbose output:**
    ```bash
    pytest tests/routers/test_google_maps_api.py -vv -s
    ```
    *   `-vv`: Very verbose output.
    *   `-s`: Shows print statements and logs, which is invaluable for debugging.
