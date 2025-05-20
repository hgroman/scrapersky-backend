# Layer 4 Audit Report: WF1-SingleSearch

**Document Version:** 1.0
**Date of Audit:** 2025-05-20
**Auditor:** Cascade (AI Agent)

---

## 1. Workflow Audited

- **Workflow Name:** `WF1-SingleSearch`

## 2. Files Audited

This audit covers the Layer 4 (Services & Schedulers) and relevant Layer 3 components (Routers with Layer 4 responsibilities) associated with the `WF1-SingleSearch` workflow.

- `src/services/places/places_search_service.py`
- `src/services/places/places_service.py`
- `src/services/places/places_storage_service.py`
- `src/routers/places_staging.py`

## 3. Consolidated Summary of Findings

The Layer 4 components and associated router logic for `WF1-SingleSearch` exhibit significant technical debt and deviations from the established `Layer-4.1-Services_Blueprint.md` and project-wide architectural mandates. Key issues include:

1.  **Tenant ID Isolation Violations (CRITICAL):** All three service files and the `places_staging.py` router (specifically `list_all_staged_places()`) show violations. This includes accepting `tenant_id` as parameters, implementing tenant-specific filtering, and using **hardcoded default `tenant_id` UUIDs**. This directly contradicts the project's tenant isolation removal strategy (ref: `09-TENANT_ISOLATION_REMOVED.md`).
2.  **ORM Usage & Raw SQL:**
    *   **Raw SQL Violations:** `places_service.py` (`get_by_id`) and `places_staging.py` (`list_all_staged_places`) use raw SQL, which is a major blueprint violation.
    *   **SQLAlchemy Core `update()` Concerns:** `places_search_service.py` (`search_and_store`), `places_service.py` (`update_status`, `batch_update_status`), and `places_staging.py` (`queue_places_for_deep_scan` - though conditionally compliant for batch) use `session.execute(update_stmt)` instead of preferred ORM object manipulation for updates.
3.  **Hardcoding:** Hardcoded default `user_uuid` and `tenant_uuid` were found in `places_storage_service.py` and `places_staging.py`, reducing flexibility.
4.  **Naming Conventions (Service Files):** `places_search_service.py` does not strictly follow the `{workflow_name}_service.py` pattern. While other service names are acceptable as generic helpers, the primary service for WF1 should ideally align.
5.  **Transaction Management (Router):** `places_staging.py` (`queue_places_for_deep_scan`) uses explicit `session.commit()` and `session.rollback()` instead of the preferred `async with session.begin():` pattern.

Addressing these issues, particularly tenant ID removal and raw SQL elimination, is crucial for aligning the workflow with architectural standards.

## 4. Detailed Findings per File

(Extracted from `WF1-SingleSearch_Cheat_Sheet.md` - Layer 4 Sections)

### 4.1 `src/services/places/places_search_service.py`

-   **Naming**: File/class name `PlacesSearchService` doesn't align with `{workflow_name}_service.py` (i.e., `single_search_service.py`). Its role seems specific to Google API & `PlaceSearch` table for WF1.
    -   *Blueprint Criterion*: General Naming Conventions, Service Naming.
-   **ORM**: `search_and_store()` uses `session.execute(update())` for `PlaceSearch` status update - should ideally use ORM object manipulation for updates.
    -   *Blueprint Criterion*: Section 2.2.3 (Database Operations - ORM Usage).
-   **Session Handling**: Generally correct (accepts session or manages for background tasks).
-   **Tenant ID**: `get_search_by_id` and other methods accepting `tenant_id` need this removed.
    -   *Blueprint Criterion*: Section 2.2.1 (Tenant ID Isolation).

### 4.2 `src/services/places/places_service.py`

-   **Naming**: `PlacesService` is generic. Acceptable as a helper if its generic nature is intended.
-   **ORM**: `get_by_id()` uses `text()` (raw SQL) - **Major Violation**. `update_status` and `batch_update_status` use `session.execute(update())` - ORM concern.
    -   *Blueprint Criterion*: Section 2.2.3 (Database Operations - ORM Usage, No Raw SQL).
-   **Tenant ID**: Active `tenant_id` usage in multiple methods (`get_by_id`, `create_search`, etc.) is a **Major Violation** of tenant isolation removal.
    -   *Blueprint Criterion*: Section 2.2.1 (Tenant ID Isolation).
-   **Error Handling**: Minimal; relies on caller. Should be reviewed for standard error propagation if needed.
    -   *Blueprint Criterion*: Section 2.2.6 (Error Handling).

### 4.3 `src/services/places/places_storage_service.py`

-   **Naming**: `PlacesStorageService` is generic. Acceptable as a helper.
-   **ORM**: `store_places()` uses `session.execute(text(...))` for fetching existing `gcp_place_id` - **Raw SQL Violation**. `update_existing_place()` uses `session.execute(update())` - ORM concern.
    -   *Blueprint Criterion*: Section 2.2.3 (Database Operations - ORM Usage, No Raw SQL).
-   **Tenant ID**: Accepts `tenant_id` in `store_places()` and `update_existing_place()`. Contains **hardcoded default `tenant_uuid` and `user_uuid`** - **Major Violations**.
    -   *Blueprint Criterion*: Section 2.2.1 (Tenant ID Isolation), Section 2.2.7 (No Hardcoding).
-   **Transaction Management**: Correctly passes session and relies on external transaction management.

### 4.4 `src/routers/places_staging.py` (Layer 4 Responsibilities)

-   **Pattern**: Router-Handled CRUD & Dual-Status Updates (Pattern B).
-   **Naming**: File name `places_staging.py` is descriptive and acceptable.
-   **ORM/Raw SQL**: `list_all_staged_places()` uses **Raw SQL** - **Major Violation**.
    -   *Blueprint Criterion*: Section 3.2.2 (Database Operations - ORM Usage, No Raw SQL).
-   **Tenant ID Isolation**: `list_all_staged_places()` re-introduces `tenant_id` logic (retrieval from token, filtering) and uses a **hardcoded default `tenant_id`** - **Major Violations**.
    -   *Blueprint Criterion*: Section 3.2.1 (Tenant ID Isolation).
-   **Transaction Management**: `queue_places_for_deep_scan()` uses explicit `session.commit()` / `session.rollback()` - **Minor Deviation** (should use `async with session.begin():`).
    -   *Blueprint Criterion*: Section 3.2.3 (Transaction Management).
-   **Hardcoding**: Default `tenant_id` in `list_all_staged_places()` - **Major Violation**.
    -   *Blueprint Criterion*: Section 3.2.6 (No Hardcoding).
-   **Scope of Logic**: The logic within `places_staging.py` generally seems within the bounded scope for Pattern B routers handling CRUD and status updates for a primary entity (`Place`). No significant overreach into complex orchestration was noted that would mandate an immediate move to Pattern A, provided the above violations are fixed.

## 5. Key Areas Requiring Attention (for Remediation Persona)

Based on this audit, the following are the most critical areas for the remediation team to address for `WF1-SingleSearch` Layer 4 components:

1.  **Tenant ID Isolation (Highest Priority):**
    *   Remove ALL `tenant_id` parameters, filtering logic, and hardcoded `tenant_id`/`user_id` values from all identified service methods and router endpoints.
2.  **Eliminate Raw SQL:**
    *   Refactor all instances of raw SQL (`text()`, direct SQL strings) to use SQLAlchemy ORM or Core Expression Language for database queries.
3.  **Standardize ORM Update Operations:**
    *   Where `session.execute(update_stmt)` is used for single-entity or simple batch updates, refactor to use ORM object manipulation (fetch, modify, flush/commit) for better maintainability and to leverage ORM features fully.
4.  **Remove Hardcoding:**
    *   Eliminate all other hardcoded values beyond tenant IDs (e.g., default user IDs if not contextually appropriate).
5.  **Transaction Management Consistency:**
    *   Ensure all router endpoints performing database writes use the `async with session.begin():` pattern for transaction management.
6.  **Service Naming Review:**
    *   Clarify the role of `places_search_service.py` and decide if it should be renamed to `single_search_service.py` to reflect it as the primary service for WF1, or if its helper status is appropriate (update documentation accordingly).

---

**End of Report**
`<!-- STOP_FOR_REVIEW -->`
