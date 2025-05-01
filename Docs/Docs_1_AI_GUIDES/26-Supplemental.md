# Debugging Cheat Sheet: Lessons from Sitemap Files PUT Endpoint (April 11, 2025)

## Introduction

This document summarizes the painful, multi-step debugging process required to fix the `PUT /api/v3/sitemap-files/{id}` endpoint. It serves as a "lessons learned" guide to prevent future AI assistants (or humans) from repeating these time-consuming mistakes. The core issue involved a cascade of errors stemming from incorrect API usage, schema mismatches, data integrity problems, flawed transaction handling, incorrect model definitions, and misunderstanding of authentication/test user conventions.

## Core Principles Refresher & Checklist

Before diving deep, always confirm these fundamentals:

1.  **✅ Verify API Call:**

    - **Method:** Is it correct (PUT, POST, GET, DELETE)?
    - **Path:** EXACTLY matches the router prefix + endpoint path? (e.g., `/api/v3/sitemap-files/{uuid}`). Check `src/routers/...` and `src/main.py`. Watch for trailing slashes.
    - **Query Parameters (GET):** Are the parameter names sent by the frontend (e.g., `?domain_filter=...`) EXACTLY matching the names expected by the backend router function (e.g., `domain_filter: Optional[str] = Query(...)`)? **Mismatched names are a common cause of silent filter failures.**
    - **Headers:** Correct `Content-Type`, `Authorization` (Bearer token)?
    - **Body (PUT/POST):** Valid JSON? Does it contain all required fields? Are field names correct?
    - **Test User/Token:** Using the _correct_ token (`scraper_sky_2024`) and understanding which _actual_ user UUID it maps to (`5905e9fe-...`, see #7 below & `10-TEST_USER_INFORMATION.md`)?

2.  **✅ Check Pydantic Schemas (`src/schemas/...`):**

    - **Input Schema (`Create`/`Update`):** Does it include _all_ fields being sent in the request body?
    - **Output Schema (`Read`):** Does it include _all_ fields expected in the API response? Use aliases (`alias='...'`, `populate_by_name=True`) if API names differ from model attributes. Check base schemas it inherits from.

3.  **✅ Check Logs FIRST on Errors:**

    - Don't just trust HTTP status codes (especially 404s or 500s returned from generic handlers).
    - IMMEDIATELY run `docker-compose logs --tail=100 scrapersky | cat` after a failed request.
    - Look for the _actual_ underlying error (e.g., `LookupError`, `IntegrityError`, `DatatypeMismatchError`, `ImportError`). The traceback is key.

4.  **✅ Check Database Data & Schema:**

    - Use inspection tools (`scripts/db/simple_inspect.py` is often most reliable, even without `--where`).
    - **Data Integrity:** Does data in the specific row match expected formats (esp. case-sensitivity for Enums)? Correct bad data directly via SQL Editor if needed.
    - **Schema Definition:** Verify column types (esp. Enums - `simple_inspect.py` shows `USER-DEFINED`), nullability, foreign key constraints (`FK` column in `simple_inspect.py`).

5.  **✅ Check SQLAlchemy Model Definition (`src/models/...`):**

    - Does the `Column(...)` definition match the _actual_ database schema type found in step 4?
      - Use `SQLAlchemyEnum(PythonEnum, name="db_enum_name", create_type=False)` for database Enums.
      - Ensure `nullable=True/False` matches the DB.
    - Are `ForeignKey("table.column")` definitions correct?
    - Are `relationship(..., back_populates="...")` definitions correct and symmetrical between related models?

6.  **✅ Check Transaction Handling (`src/db/session.py`):**

    - Verify `get_db_session` uses `try...except...finally`.
    - Ensure `await session.commit()` exists _after_ `yield session` in the `try` block.
    - Ensure `await session.rollback()` exists in the `except` block.
    - Ensure `await session.close()` exists in the `finally` block.

7.  **✅ Check Auth & User ID Logic (`src/auth/jwt_auth.py`):**

    - How does `get_current_user` resolve the token being used (e.g., `scraper_sky_2024`)?
    - Does it return a valid, _existing_ user UUID from `10-TEST_USER_INFORMATION.md`? (CRITICAL for `created_by`/`updated_by` FK constraints). **DO NOT** use `0000...`.
    - Confirm the returned UUID actually exists in the `users` or `profiles` table in the DB.

8.  **✅ Consult Documentation:**

    - `README.md` (esp. Quick Start, Credentials).
    - `Docs/Docs_1_AI_GUIDES/` (esp. `10-TEST_USER_INFORMATION.md`, ORM/DB guides).
    - Relevant `project-docs/`.

9.  **✅ Follow Process:**
    - Ask for permission before editing files.
    - Explain _why_ an edit is needed _before_ proposing it.
    - Add clear comments explaining non-trivial changes.

## Common Pitfalls & Solutions Encountered Here

- **Initial 404:** Incorrect `curl` path (`/v3/` missing).
- **Mismatched Query Parameters:** Frontend sending `?name_contains=...` but backend expecting `?domain_filter=...` for domain lookup. -> Ensure frontend parameter name matches backend router definition.
- **400 Bad Request:** Missing field in `SitemapFileUpdate` schema.
- **Silent 404 (Cycle 1):** Masked `LookupError` (lowercase 'completed' in DB status vs. capitalized Enum). -> Fix DB data & Model Enum type.
- **Silent 404 (Cycle 2) / Changes Not Saving:** Missing `session.commit()` in `get_db_session`. -> Fix transaction handling.
- **500 `DatatypeMismatchError`:** Incorrect `Column(String)` instead of `Column(SQLAlchemyEnum)` in Model. -> Fix model column definition.
- **500 `IntegrityError` / `ForeignKeyViolationError`:** `get_current_user` returning non-existent `0000...` UUID for `updated_by`. -> Fix `get_current_user` to return valid test UUID.
- **500 `IntegrityError` / `ForeignKeyViolationError` (Supabase User FKs):** Attempting to insert/update a record with a user foreign key (e.g., `created_by`, `user_id`) fails because the target `auth.users` table is inaccessible or the provided UUID doesn't exist in the public `profiles` table.
  - **Cause:** Direct FK references to `auth.users` are not allowed from the `public` schema. Code must reference `public.profiles.id` instead.
  - **Solution:** Ensure the foreign key column targets `profiles.id`. Verify the user UUID (obtained from JWT or elsewhere) exists in the `profiles` table before insertion/update. See `27-SUPABASE_USER_PROFILES_PATTERN.md` for the standard pattern.
- **(Other potential issues fixed along the way):** Missing FK/Relationship definition (`NoForeignKeysError`), Pydantic response schema missing fields or alias issues, circular imports.

- **Enum Value Mismatch / Type Handling in `update().values()`:** Be extremely cautious when using SQLAlchemy's `update().values({...})` with Python enums (`MyEnum.Member`) that map to database enums.

  - **Scenario 1 (Name/Value Mismatch):** SQLAlchemy might send the member _name_ (e.g., `'Queued'`) instead of its assigned _value_ (e.g., `'queued'`). If the database enum expects the specific value (often with different casing), this causes `invalid input value for enum...` errors.
  - **Scenario 2 (Fragile Handling):** Even if the member name and assigned value match the database label (e.g., `Not_a_Fit` and `'Not a Fit'`), passing the raw enum _member_ to `.values()` can sometimes lead to unexpected errors (like 500 errors) due to internal type handling.
  - **Symptom:** Database error message (`invalid input value...` showing Python enum name) or unexpected 500 errors during the update.
  - **Verification:** Check actual DB enum labels (`SELECT enum_range(NULL::your_enum_type);`) vs. Python Enum definition (names _and_ values).
  - **Solution:** **Always** explicitly use `.value` in the `update().values()` dictionary (e.g., `.values(..., status=MyEnum.Member.value)`) to pass the primitive string value. Also use `.value` in `.where()` clauses if comparing enum values (e.g., `.where(Model.status != MyEnum.OtherMember.value)`) for consistency and correct `NULL` handling.

- **Tab JavaScript Initialization Errors (`TypeError: ... addEventListener`):** Scripts specific to a tab panel (e.g., `domain-curation-tab.js`, `sitemap-curation-tab.js`) **MUST NOT** attempt to query for or attach event listeners to elements inside their corresponding panel (`#domainCurationPanel`, `#sitemapCurationPanel`, etc.) immediately upon script load (`DOMContentLoaded`).

  - **Reason:** The panel element might not be visible or even fully present in the DOM when the script first runs, especially if it's not the default active tab. Trying to access `null` elements causes `TypeError`s.
  - **Symptom:** Console errors like `TypeError: Cannot read properties of null (reading 'addEventListener')`, `TypeError: Cannot set properties of null (setting 'innerHTML')`, or event listeners simply not working on a specific tab.
  - **Interference:** **Crucially, these errors can prevent JavaScript in _other_, correctly written tab scripts from executing properly.** (e.g., errors in `domain-curation-tab.js` prevented checkbox listeners in `sitemap-curation-tab.js` from working).
  - **Solution:** Wrap all panel-specific setup (querying elements, adding listeners, fetching initial data) inside an initialization function (e.g., `initializeMyTab()`). Trigger this function _only_ when the tab becomes active. The standard pattern is to use a `MutationObserver` watching the `style` attribute of the panel `div` or, as a fallback, a click listener on the tab button itself (with a small `setTimeout`). Mark the panel as initialized (e.g., using `panel.dataset.initialized = 'true'`) to prevent re-initialization.

- **API Data Structure Mismatch (Frontend vs. Backend):** Frontend code displaying data from an API **MUST** access fields based on the _actual_ structure defined in the backend's response schema (e.g., the Pydantic `Read` schema), not based on assumptions.

  - **Reason:** Assumptions about data structure (e.g., expecting nested objects when the API returns flat fields) will lead to `undefined` values or errors.
  - **Symptom:** Data displayed as `N/A`, `undefined`, or `[object Object]` in the UI, or `TypeError`s in the console when accessing nested properties that don't exist.
  - **Example:** The Sitemap Curation tab initially failed to display domain names because the JS expected `item.domain.domain` while the `SitemapFileRead` schema provided `item.domain_name`.
  - **Verification:** Always check the relevant Pydantic `Read` schema in `src/schemas/` or inspect the actual JSON response in the browser's Network tab.
  - **Solution:** Adjust the frontend JavaScript (e.g., the `renderTable` function) to use the correct field names/paths from the API response.

- **Database Enum Definition vs. Python Enum Mismatch:** This is a critical and frustrating source of errors (`LookupError`, `InvalidTextRepresentationError`, 500 errors).

  - **Source of Truth:** The actual definition of an Enum type within the PostgreSQL database is the absolute source of truth for its allowed values and, crucially, their **exact casing**.
  - **Python Alignment:** The corresponding Python `enum.Enum` definition in `src/models/` **MUST** have values that **exactly match** the database enum's labels (including case).
  - **Inconsistency:** Be aware that the database _might_ have inconsistent definitions (e.g., `deep_scan_status_enum` used lowercase `queued`, `processing`, etc., while `SitemapCurationStatusEnum` used capitalized `New`, `Selected`, etc.). While this inconsistency should ideally be fixed in the DB schema itself (using `ALTER TYPE ... RENAME VALUE ...`), the Python code _must_ reflect the current reality of the database to function.
  - **Verification:** If _any_ Enum-related errors occur, **DO NOT GUESS**. Use the following SQL query via `docker-compose exec ... psql ... -c "..."` to get a definitive list of all enum types and their exact values from the database:
    ```sql
    SELECT
        t.typname AS enum_type,
        e.enumlabel AS enum_value
    FROM
        pg_type t
    JOIN
        pg_enum e ON t.oid = e.enumtypid
    JOIN
        pg_catalog.pg_namespace n ON n.oid = t.typnamespace
    WHERE
        n.nspname = current_schema() -- Or specify 'public' if needed
    ORDER BY
        t.typname, e.enumsortorder;
    ```
  - **Solution:** Correct the Python Enum definition in `src/models/` to exactly match the `enum_value` strings returned by this query for the relevant `enum_type`. Ensure the `SQLAlchemyEnum(..., name="db_enum_name", ...)` in the model column definition also correctly references the database `enum_type` name (`typname`).

- **Running Direct Database Modifications (Fixing Data/Schema):** When you need to run direct SQL commands (e.g., `UPDATE` to fix bad data, `ALTER TYPE` to rename enum values) and direct `psql` access via `docker-compose exec ... psql ...` fails (often because `psql` is not in the container's PATH):
  - **Effective Alternative:** Use a dedicated Python script.
  - **Method:**
    1.  Create a new script (e.g., `scripts/my_db_fix_script.py`).
    2.  Inside the script, import `os`, `asyncio`, `text` from `sqlalchemy`, and `create_async_engine` from `sqlalchemy.ext.asyncio`.
    3.  Get the database URL: `db_url = os.environ.get("DATABASE_URL")`.
    4.  Create an engine: `engine = create_async_engine(db_url)`.
    5.  Define your SQL command(s) using `stmt = text("YOUR SQL HERE")`.
    6.  Use `async with engine.connect() as connection:` and `async with connection.begin():` to execute the statement(s) (`await connection.execute(stmt)`).
    7.  Include basic error handling (`try...except...finally`) and dispose of the engine (`await engine.dispose()`).
    8.  Use `if __name__ == "__main__": asyncio.run(your_async_function())` to make the script runnable.
  - **Execution:** Run the script from your host machine terminal using:
    ```bash
    docker-compose exec -T scrapersky python scripts/my_db_fix_script.py
    ```
    _(Replace `scrapersky` if the service name differs)_.
  - **Why it Works:** This executes the script _inside_ the application container, automatically leveraging the correct `DATABASE_URL` from the environment variables, using the already installed Python and SQLAlchemy libraries, and ensuring proper network access to the database.

Adhering to the foundational principles and the revised checklist from the start would have prevented the majority of this debugging effort.
