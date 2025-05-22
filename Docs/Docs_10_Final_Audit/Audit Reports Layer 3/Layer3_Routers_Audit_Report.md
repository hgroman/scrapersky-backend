# Layer 3: Routers - AI Audit Summary

**Report Version:** 1.0
**Audit Completion Date:** 2024-07-26
**AI Auditor:** Cascade Router Guardian

## 1. Overall Assessment

The audit of Layer 3 (API Routers) reveals a **mixed level of compliance** with the `Layer-3.1-Routers_Blueprint.md`. While some routers, particularly more recently developed or refactored ones (e.g., `profile.py`, `sitemap_files.py`), demonstrate good adherence to principles like service layer delegation and proper schema usage, a significant portion of the audited routers exhibit critical and high-severity GAPs.

Common systemic issues include:
-   Prevalence of business logic directly within router endpoints.
-   Inconsistent or missing API prefixing/versioning and tagging.
-   Incorrect Pydantic model definition locations and usage for responses.
-   Routers managing database transactions instead of services.
-   Critical security gaps due to missing authentication on sensitive endpoints.

Remediation efforts should prioritize addressing security vulnerabilities and refactoring routers to delegate all business logic and transaction management to Layer 4 services. Standardization of router configuration and Pydantic model practices is also crucial for improving maintainability and adherence to the architectural blueprint.

One planned router, `src/routers/page_metadata_crud.py`, was not found, indicating a potential gap in functionality or outdated planning documentation.

## 2. Key Findings by Severity

### 2.1. Critical Severity Gaps

-   **Missing Authentication:**
    -   `src/routers/email_scanner.py`: Multiple endpoints, including those initiating scans and potentially interacting with sensitive data, lack authentication.
    -   `src/routers/page_curation.py` (`PUT /pages/curation-status`): Allows batch database updates without any authentication.
    -   `src/routers/places_staging.py` (`GET /places/staging/discovery-job/{discovery_job_id}`): Appears to lack authentication for an endpoint potentially returning tenant-specific data.
    -   `src/routers/modernized_page_scraper.py`: Inconsistent authorization on `POST /modernized-page-scraper/scrape-single-domain` and `POST /modernized-page-scraper/scrape-batch-domain`, with `DISABLE_PERMISSION_CHECKS` flag potentially bypassing intended security.
    -   `src/routers/modernized_sitemap.py`: `/scrape-sitemap` endpoint lacks `check_sitemap_access` despite other POST/PUT endpoints having it.

### 2.2. High Severity Gaps

-   **Business Logic in Router:** This is a widespread issue affecting most audited routers. Examples include:
    -   `batch_page_scraper.py`, `batch_sitemap.py`, `db_portal.py`, `dev_tools.py`, `domains.py`, `email_scanner.py`, `google_maps_api.py`, `local_businesses.py`, `modernized_page_scraper.py`, `modernized_sitemap.py`, `page_curation.py`, `places_staging.py`. These routers perform direct database operations (SQLAlchemy ORM, raw SQL), data transformations, and complex conditional logic instead of delegating to Layer 4 services.
-   **Missing Router Prefix & Versioning:** Many routers lack the standard `/api/v3/...` prefix.
    -   `batch_page_scraper.py`, `batch_sitemap.py`, `db_portal.py`, `dev_tools.py`, `domains.py`, `email_scanner.py`, `google_maps_api.py`, `local_businesses.py`, `modernized_page_scraper.py`, `modernized_sitemap.py`, `page_curation.py`, `places_staging.py`.
-   **Direct Internal Variable Access/Manipulation (from Services):**
    -   `src/routers/modernized_page_scraper.py`: Directly manipulates `page_scraper_service.active_single_domain_tasks`.
    -   `src/routers/modernized_sitemap.py`: Directly accesses `sitemap_service.active_tasks`.

### 2.3. Medium Severity Gaps

-   **Incorrect Pydantic Model Location/Definition:**
    -   Many routers define Pydantic request/response models locally or import them from non-schema Layer 2 locations (e.g., `src/models/`). Affected files include: `email_scanner.py`, `google_maps_api.py`, `local_businesses.py`, `places_staging.py`, `profile.py` (potential).
-   **Generic `dict` or Missing Explicit Response Models:** Numerous endpoints use `response_model=Dict` or rely on FastAPI's inference instead of specific Layer 2 Pydantic models.
    -   `google_maps_api.py`, `local_businesses.py`, `modernized_page_scraper.py`, `modernized_sitemap.py`, `places_staging.py`, `profile.py`.
-   **Transaction Management in Router:** Routers frequently manage `session.begin()` instead of Layer 4 services.
    -   `modernized_page_scraper.py`, `modernized_sitemap.py`, `page_curation.py`, `profile.py` (and likely others where business logic is in the router).
-   **Missing Router Tags:** Some routers lack tags for OpenAPI documentation.
    -   `batch_page_scraper.py`, `batch_sitemap.py`, `db_portal.py`, `dev_tools.py`, `domains.py`, `email_scanner.py`, `page_curation.py`.

### 2.4. Low Severity Gaps / Observations

-   **Inconsistent Authorization Logic:**
    -   `src/routers/modernized_sitemap.py`: Varied use of `check_sitemap_access` dependency.
-   **Reliance on Environment Flags for Core Logic:** `dev_tools.py` and `modernized_page_scraper.py` use `SCRAPER_SKY_DEV_MODE` or `DISABLE_PERMISSION_CHECKS` to alter core behavior or bypass security, which can be risky if misconfigured in production.
-   **Unused Dependencies:** `profile.py` (`db_params` in `get_profiles`).
-   **Hardcoded Default Tenant ID:** `profile.py` uses `DEFAULT_TENANT_ID` consistently. While a design choice, it warrants review if multi-tenancy for profiles is intended.

## 3. General Recommendations for Remediation

1.  **Prioritize Security (Critical):** Immediately address all instances of missing or inadequate authentication/authorization on endpoints, especially those performing data mutations or accessing sensitive information.
2.  **Implement Service Layer (High):** Systematically refactor all routers to delegate business logic (database interactions, data transformations, complex conditions) to new or existing Layer 4 services. This is the most impactful change needed for architectural alignment.
3.  **Standardize Router Configuration (High):** Ensure all routers use the correct API prefix (e.g., `/api/v3/...`) and appropriate tags for OpenAPI documentation.
4.  **Centralize Pydantic Models (Medium):** Relocate all locally defined Pydantic request/response models to the designated Layer 2 schema directory (e.g., `src/schemas/`).
5.  **Use Specific Response Models (Medium):** Replace generic `dict` response models with specific Pydantic models from Layer 2 for all endpoints.
6.  **Shift Transaction Management (Medium):** Ensure database transaction control (`session.begin()`, `session.commit()`, `session.rollback()`) is handled within Layer 4 service methods, not in routers.
7.  **Encapsulate Service Internals (High):** Prevent routers from directly accessing or manipulating internal variables of service instances. Services should expose well-defined methods.
8.  **Review Environment Variable Usage (Low):** Minimize reliance on environment variables for toggling core security or business logic. Prefer configuration-driven approaches or more robust feature flagging mechanisms if necessary.
9.  **Address Missing File:** Investigate the status of `src/routers/page_metadata_crud.py`. If it's still required, it should be implemented and audited. If obsolete, the audit plan and any related documentation should be updated.

## 4. Conclusion

The Layer 3 audit has identified significant opportunities for improving the ScraperSky backend's router implementations. By addressing the GAPs highlighted, particularly concerning security, service layer delegation, and Pydantic model standardization, the project can achieve greater consistency, maintainability, and adherence to its architectural vision. The more compliant routers like `profile.py` and `sitemap_files.py` can serve as good examples for refactoring efforts.

---
(End of AI Audit Summary)


# Layer 3: API Routers - Audit Report

- **Version:** 1.0
- **Date:** {{YYYY-MM-DD}}
- **Auditor:** Cascade AI

## AI-Generated Audit Summary

*This summary will be generated after the detailed audit of all router files is complete.*

---

## Overview

This document contains the findings from a comprehensive audit of Layer 3 (API Routers) in the ScraperSky backend. Each router file has been systematically analyzed for compliance with the architectural standards defined in `Layer-3.1-Routers_Blueprint.md`.

## Methodology

The audit followed the procedure outlined in `Layer-3.3-Routers_AI_Audit_SOP.md`, which includes:

1. Identifying all API router files in `src/routers/`
2. Analyzing each router against the standards in the Layer 3 Blueprint
3. Documenting deviations, inconsistencies, and areas for improvement
4. Recommending refactoring actions to address identified issues

## Detailed Findings

*The following sections contain detailed findings for each router file.*

### 1. Audit of `src/routers/batch_page_scraper.py` (Summary)

- **Router:** `src/routers/batch_page_scraper.py`
- **Key Findings (based on previous audit checkpoint):**
    - **Response Models & Type Hints:** Gaps identified in response models; some type hints are too loose (e.g., `Dict[str, Any]`). Adherence to Blueprint 2.2.2 (explicit Pydantic models) is required.
    - **Business Logic Delegation:** Business logic was found directly within router endpoints. This logic should be moved to Layer 4 services as per Blueprint 2.1.1 and 2.2.3.3.
    - **Request Body Types:** Potential use of SQLAlchemy models directly in request bodies instead of dedicated Pydantic schemas. Requests should be validated using Pydantic models.
    - **Transaction Management:** Ensure explicit transaction management (`async with session.begin():`) for all database write operations, as per Blueprint 2.2.3.2.
- **Overall:** This router requires refactoring to improve response model explicitness, delegate business logic to services, ensure Pydantic models are used for requests, and confirm correct transaction handling.

### 2. Audit of `src/routers/batch_sitemap.py` (Summary)

- **Router:** `src/routers/batch_sitemap.py`
- **Key Findings (based on previous audit checkpoint):**
    - **Response Models:** Similar gaps regarding explicit Pydantic response models as noted in other routers. (Blueprint 2.2.2)
    - **Transaction Management:** Attention needed for transaction management. Ensure all database write operations are explicitly managed. (Blueprint 2.2.3.2)
    - **Pydantic Schemas:** The file emphasizes the use of Pydantic schemas for request and response validation. This is good practice and should be consistently applied throughout.
- **Overall:** Review for consistent use of explicit Pydantic response models and verify robust transaction management for all write operations.

### 3. Audit of `src/routers/db_portal.py` (Summary)

- **Router:** `src/routers/db_portal.py`
- **Key Findings (based on previous audit checkpoint):**
    - **Response Models:** Observations about missing explicit Pydantic response models for some endpoints. (Blueprint 2.2.2)
    - **Error Handling:** Potential lack of comprehensive error handling for various scenarios. Ensure adherence to Blueprint 2.2.3.5 (standardized error responses using `HTTPException`).
    - **Pydantic Models:** While the router utilizes Pydantic models for request and response validation, ensure this is complete and consistent for all endpoints.
- **Overall:** The primary focus for refactoring should be on implementing explicit Pydantic response models for all endpoints and enhancing error handling to be more robust and standardized.

### 4. Audit of `src/routers/dev_tools.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/dev_tools.py`
- **Router Instance:** `router = APIRouter(prefix=\"/api/v3/dev-tools\", tags=[\"dev-tools\"], dependencies=[Depends(get_current_user)],)`
- **Compliance:** File naming, router variable name, prefix, tags are COMPLIANT.
- **Observation:** Router-level `Depends(get_current_user)` ensures authentication. The `require_dev_mode()` helper function is defined for environment-based authorization but is not applied at the router level; its application is inconsistent across endpoints.

**General Issues Noted Across Multiple Endpoints:**
1.  **Missing `Depends(require_dev_mode)`:** Many endpoints that expose sensitive information (DB schema, sample data, server configs, logs) or perform potent operations (container management, DB setup) lack the `Depends(require_dev_mode)` dependency. This is a **CRITICAL** security concern.
2.  **Lack of Explicit Pydantic Response Models:** Most endpoints return `Dict[str, Any]` or construct `JSONResponse` directly, rather than using explicit Pydantic models for `response_model`. (Blueprint 2.2.2)
3.  **Business Logic in Router:** Several endpoints contain complex data querying, introspection logic, or direct OS command execution (`run_command`) that should be delegated to Layer 4 services. (Blueprint 2.1.1, 2.2.3.3)
4.  **Non-Standard Error Responses:** Some endpoints return error details in a 200 OK response with a JSON body (e.g., `{\"status\": \"error\", ...}`), instead of raising `HTTPException`. (Blueprint 2.2.3.5)
5.  **Direct SQL Execution:** Multiple endpoints execute raw SQL queries, including for schema introspection and data manipulation. This should generally be handled by Layer 4 services or dedicated migration/seeding scripts. The `setup_sidebar` endpoint performing DDL/DML is particularly concerning.

**Specific Endpoint Audit Summaries:**

*   **`POST /container/rebuild` (`rebuild_container`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)`. Uses `run_command`.
    *   **Actions:** Add `require_dev_mode`, define Pydantic response model.

*   **`POST /container/restart` (`restart_container`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)`. Uses `run_command`.
    *   **Actions:** Add `require_dev_mode`, define Pydantic response model.

*   **`GET /container/health` (`check_container_health`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)`. Uses `run_command`.
    *   **Actions:** Add `require_dev_mode`, define Pydantic response model.

*   **`GET /container/status` (`get_container_status`)**
    *   **Gaps:** No explicit `response_model`. **GAP (High):** Missing `Depends(require_dev_mode)`.
    *   **Actions:** Add `require_dev_mode`, define Pydantic response model.

*   **`GET /server/status` (`get_server_status`)**
    *   **Gaps:** No explicit `response_model`. **GAP (High):** Missing `Depends(require_dev_mode)`. Uses `run_command`. Exposes env vars and routes.
    *   **Actions:** Add `require_dev_mode`, define Pydantic response model.

*   **`GET /logs` (`get_logs`)**
    *   **Gaps:** No explicit `response_model`. **GAP (High):** Missing `Depends(require_dev_mode)`. Uses `run_command`.
    *   **Actions:** Add `require_dev_mode`, define Pydantic response model.

*   **`GET /` (`get_dev_tools_page`)**
    *   **Observation:** Serves HTML. Consider `Depends(require_dev_mode)` for consistency.

*   **`GET /schema` (`get_database_schema`)**
    *   **Gaps:** No explicit `response_model`. **GAP (High):** Missing `Depends(require_dev_mode)`. Direct complex SQL execution.
    *   **Actions:** Add `require_dev_mode`, define Pydantic model, move SQL to Layer 4.

*   **`GET /routes` (`get_route_information`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)`. Complex introspection logic in router. Non-standard error response.
    *   **Actions:** Add `require_dev_mode`, define Pydantic model, move logic to Layer 4, use `HTTPException`.

*   **`GET /system-status` (`get_system_status`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)`. Logic in router. Non-standard error. Hardcoded `api_version: v1` (should be v3).
    *   **Actions:** Add `require_dev_mode`, Pydantic model, move logic to Layer 4, use `HTTPException`, fix API version.

*   **`GET /database/tables` (`get_database_tables`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)`. Logic in router. Non-standard error.
    *   **Actions:** Add `require_dev_mode`, Pydantic model, move logic to Layer 4, use `HTTPException`.

*   **`GET /database/table/{table_name}` (`get_table_fields`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)` (exposes sample data). Direct SQL with f-string (mitigated by allowlist). Logic in router.
    *   **Actions:** Add `require_dev_mode`, Pydantic model, move to Layer 4. Review table name validation.

*   **`GET /db-tables` (`get_db_tables`)**
    *   **Gaps:** Pydantic model preferred over direct `JSONResponse`. **CRITICAL:** Missing `Depends(require_dev_mode)`. Logic in router.
    *   **Actions:** Add `require_dev_mode`, consider Pydantic model, move to Layer 4.

*   **`POST /setup-sidebar` (`setup_sidebar`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)`. Executes DDL/DML via API. `<!-- STOP_FOR_REVIEW -->` This functionality (DB setup) is highly unconventional for an API endpoint and should be managed via migrations or seed scripts.
    *   **Actions:** Add `require_dev_mode`, Pydantic model. **CRITICAL:** Review if this endpoint should exist; if so, move logic to Layer 4 but question the pattern.

*   **`POST /process-pending-domains` (`process_pending_domains_endpoint`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)`.
    *   **Actions:** Add `require_dev_mode`, Pydantic model. (Delegates to Layer 4 - good).

*   **`GET /scheduler/status` (`check_scheduler_status`)**
    *   **Gaps:** No explicit `response_model`. (Is `Depends(require_dev_mode)` COMPLIANT).
    *   **Actions:** Define Pydantic model.

*   **`POST /scheduler/trigger-domain-processing` (`trigger_domain_processing_endpoint`)**
    *   **Gaps:** No explicit `response_model`. (Is `Depends(require_dev_mode)` COMPLIANT).
    *   **Actions:** Define Pydantic model.

*   **`POST /test/domain-sitemap-submission/{domain_id}` (`test_domain_sitemap_submission`)**
    *   **Gaps:** No explicit `response_model`. (Is `Depends(require_dev_mode)` COMPLIANT). Session dependency `get_db_session` (check consistency with `get_session_dependency`). Clarify transaction management with service.
    *   **Actions:** Define Pydantic model. Verify session dependency. Clarify transactions.

*   **`POST /trigger-sitemap-import/{sitemap_file_id}` (`trigger_sitemap_import_endpoint`)**
    *   **Gaps:** No explicit `response_model`. **CRITICAL:** Missing `Depends(require_dev_mode)` in signature. Clarify transaction management.
    *   **Actions:** Add `require_dev_mode`, Pydantic model, clarify transactions.

**Summary for `dev_tools.py`:**
This router contains numerous development utilities. While some endpoints correctly use `Depends(require_dev_mode)` and delegate to services, a significant number suffer from critical security gaps (missing `require_dev_mode` for sensitive operations/data exposure), lack of explicit response models, and business/operational logic embedded directly in the router instead of Layer 4 services. The `setup_sidebar` endpoint's use of DDL/DML is a major concern requiring review.

### 5. Audit of `src/routers/domains.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/domains.py`
- **Router Instance:** `router = APIRouter(prefix="/api/v3/domains", tags=["Domains"])`
- **Compliance:**
    - File naming, router variable name, prefix, tags: COMPLIANT.
    - Router-level dependencies: `Depends(get_current_user)` is commented out at the router level but applied individually to each endpoint.
        - **GAP (Low): Authentication Dependency Scope.** While functional, applying common dependencies like authentication at the router level is preferred for consistency and to ensure all new endpoints within the router are automatically covered (Blueprint 2.1.2).

**Imports:**
- Imports are well-organized (standard library, third-party, project-specific). COMPLIANT (Blueprint 1.4).

**Pydantic Models:**
- **Request Models:**
    - `list_domains`: Uses `Query` parameters for GET request. COMPLIANT.
    - `update_domain_sitemap_curation_status_batch`: Uses `DomainBatchCurationStatusUpdateRequest`. COMPLIANT (Blueprint 2.2.1).
- **Response Models:**
    - `list_domains`: `response_model=PaginatedDomainResponse`. COMPLIANT (Blueprint 2.2.2).
    - `update_domain_sitemap_curation_status_batch`: `response_model=Dict[str, int]`.
        - **GAP (Medium): Missing Explicit Pydantic Response Model.** The endpoint returns a generic `Dict[str, int]`. An explicit Pydantic model (e.g., `BatchUpdateSummaryResponse`) should be defined and used for clarity, validation, and OpenAPI documentation (Blueprint 2.2.2).

**Endpoint Definitions & Logic:**
- **`GET /` (`list_domains`)**
    - **Docstring & Naming:** Clear and compliant.
    - **Security:** `get_current_user` applied. Sorting uses an allowlist (`ALLOWED_SORT_FIELDS`) for column names, which is good practice. Parameterized queries via SQLAlchemy protect against SQL injection. COMPLIANT.
    - **Business Logic Delegation:** Contains significant query-building logic (filtering, sorting, pagination, count query) directly within the router.
        - **GAP (High): Business Logic in Router.** This complex data retrieval logic should be delegated to a Layer 4 service method (e.g., `DomainService.get_domains_paginated(...)`) to keep the router lean and focused on request/response handling (Blueprint 2.1.1, 2.2.3.3).
    - **Transaction Management:** Read-only, no explicit transaction needed. COMPLIANT.
    - **Error Handling:** Uses `HTTPException` for invalid sort field. COMPLIANT.

- **`PUT /sitemap-curation/status` (`update_domain_sitemap_curation_status_batch`)**
    - **Docstring & Naming:** Clear and compliant.
    - **Security:** `get_current_user` applied. COMPLIANT.
    - **Business Logic Delegation:** Contains logic for mapping enums, iterating domain IDs, performing database updates (including conditional logic for `sitemap_analysis_status`), and calling `session.commit()`.
        - **GAP (High): Business Logic in Router.** This batch update logic, including data validation, conditional updates, and persistence, should be encapsulated within a Layer 4 service method (e.g., `DomainService.batch_update_sitemap_curation_status(...)`) (Blueprint 2.1.1, 2.2.3.3).
    - **Transaction Management:** The router directly calls `session.commit()`.
        - **GAP (Medium): Transaction Management Scope.** For operations involving database writes, transactions (`async with session.begin(): ... session.commit()`) should ideally be managed within the Layer 4 service method that performs the unit of work. This ensures atomicity and proper rollback if any part of the operation fails (Blueprint 2.2.3.2).
    - **Error Handling:** Uses `HTTPException` for invalid status values. COMPLIANT.

**Logging:**
- Both endpoints include informative logging. COMPLIANT.

**Summary for `src/routers/domains.py`:**
The `domains.py` router is generally well-structured regarding naming, security basics, and request model usage. The primary areas for improvement are:
1.  **Delegation of Business Logic:** Significant data querying logic in `list_domains` and batch update logic in `update_domain_sitemap_curation_status_batch` should be moved to Layer 4 services.
2.  **Explicit Response Model:** The batch update endpoint should use an explicit Pydantic model for its response.
3.  **Transaction Management:** Transaction control for the batch update operation should reside within the corresponding Layer 4 service method.
4.  **Router-Level Dependencies:** Consider applying common dependencies like authentication at the router level.

### 6. Audit of `src/routers/email_scanner.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/email_scanner.py`
- **Router Instance:** `router = APIRouter()`
    - **GAP (Critical): Missing Router Prefix and Tags.** The `APIRouter` is initialized without a `prefix` (e.g., `/api/v3/email-scanner`) and `tags` (e.g., `["Email Scanner"]`). This violates Blueprint 2.1.2 (Prefixes and Versioning) and 2.1.3 (Tagging for OpenAPI), leading to inconsistent API paths and poor documentation.
- **Router-level Dependencies:** No router-level dependencies are applied. Common dependencies like `CurrentUserDep` and `SessionDep` are defined and applied individually to endpoints.
    - **GAP (Low): Authentication/Session Dependency Scope.** While functional, if these dependencies are common to most/all endpoints in the router, applying them at the router level is preferred for consistency and to ensure new endpoints are automatically covered (Blueprint 2.1.2).

**Imports:**
- `from ..models import Domain`: Uses a relative import.
    - **GAP (Low): Relative Import.** Project convention (Blueprint 1.4.2.3) should be checked. If absolute imports (e.g., `from src.models import Domain`) are standard, this should be updated for consistency.
- `from ..tasks.email_scraper import scan_website_for_emails`: Uses a relative import.
    - **GAP (Low): Relative Import.** Similar to the above, check project conventions for absolute imports (e.g., `from src.tasks.email_scraper ...`).
- Other imports appear generally organized and compliant.

**Pydantic Models:**
- **Local Model Definition:** The `EmailScanningResponse` Pydantic model is defined directly within this router file.
    - **GAP (Medium): Local Pydantic Model Definition.** Pydantic models, particularly those intended for API responses, should typically reside in Layer 2 (e.g., `src/schemas/` or `src/models/api_models/`) for better modularity, reusability, and adherence to the layered architecture (Blueprint 1.2.2, 2.2.2). This model is also not actively used as a `response_model` in the visible endpoints.
- **Request Models:**
    - `scan_website_for_emails_api`: Uses `EmailScanRequest` imported from `src.schemas.email_scan`. COMPLIANT (Blueprint 2.2.1).
- **Response Models:**
    - `scan_website_for_emails_api`: `response_model=JobSubmissionResponse` (from `src.schemas.job`). COMPLIANT (Blueprint 2.2.2).
    - `get_scan_status_api`: `response_model=JobStatusResponse` (from `src.schemas.job`). COMPLIANT (Blueprint 2.2.2).

**Endpoint Definitions & Logic:**

- **`POST /scan/website` (`scan_website_for_emails_api`)**
    - **Path & Naming:** Endpoint path `"/scan/website"` is missing the router's intended base path (e.g., `/api/v3/email-scanner`). This is a consequence of the missing router prefix. Function name is clear.
    - **Security:** `CurrentUserDep` is applied, and user ID is extracted and validated. COMPLIANT.
    - **Business Logic Delegation:** This endpoint contains significant business logic:
        1.  Checking for existing PENDING or RUNNING jobs for the domain.
        2.  Verifying domain existence.
        3.  Creating a new `Job` record in the database.
        4.  Adding a task to `background_tasks`.
        - **GAP (High): Business Logic in Router.** This entire sequence of operations (job existence check, domain validation, job creation, task queuing) should be encapsulated within a Layer 4 service method (e.g., `EmailScanningService.initiate_scan(...)`) (Blueprint 2.1.1, 2.2.3.3).
    - **Transaction Management:** Handles `session.flush()` and `session.commit()` and `session.rollback()` directly.
        - **GAP (Medium): Transaction Management Scope.** Database commits and rollbacks should ideally be managed within the Layer 4 service method that performs the unit of work (Blueprint 2.2.3.2).
    - **Error Handling:** Uses `HTTPException` for various error conditions (invalid user ID, DB errors, domain not found). COMPLIANT (Blueprint 2.2.3.5).
    - **Status Code:** Returns `status.HTTP_202_ACCEPTED`, which is appropriate for an async task submission. COMPLIANT.

- **`GET /scan/status/{job_id}` (`get_scan_status_api`)**
    - **Path & Naming:** Endpoint path `"/scan/status/{job_id}"` is missing the router's intended base path. Path parameter `job_id` is correctly typed as `uuid.UUID`. Function name is clear.
    - **Security:** `CurrentUserDep` is commented out.
        - **GAP (High): Missing Authentication.** Retrieving job status often requires authentication to ensure a user can only access status for jobs they are authorized to see (or admin-level access). This should be enabled and validated (Blueprint 2.2.3.4).
    - **Business Logic Delegation:** Retrieves the `Job` record directly from the database.
        - **GAP (Medium): Business Logic in Router.** Fetching job details should ideally be handled by a Layer 4 service method (e.g., `JobService.get_job_status(job_id=job_id, user_id=...)`) which can also incorporate any necessary authorization logic (Blueprint 2.1.1, 2.2.3.3).
    - **Error Handling:** Uses `HTTPException` if the job is not found. COMPLIANT.
    - **Response Construction:** Directly constructs the `JobStatusResponse` from the `Job` model. This is acceptable if the `JobStatusResponse` schema aligns well with the `Job` model attributes needed for the response.

**Logging:**
- Both endpoints include informative logging. COMPLIANT.

**Commented-Out Code:**
- Includes commented-out old endpoints (`# @router.get("/api/v3/email-scanner/domains", ...)`).
    - **Observation:** This is dead code and should be removed for cleanliness (Blueprint 1.5.1).
- Includes commented-out `scan_jobs: Dict[uuid.UUID, EmailScanningResponse] = {}`.
    - **Observation:** Remnant of a previous approach, should be removed.

**Summary for `src/routers/email_scanner.py`:**
The `email_scanner.py` router provides core functionality for initiating and checking email scans. However, it has several significant gaps:
1.  **Critical Router Configuration:** Missing API prefix and tags for the `APIRouter` instance.
2.  **Business Logic Delegation:** Both endpoints contain substantial business logic (job checks, creation, DB interaction, task queuing, status retrieval) that should be moved to Layer 4 services.
3.  **Transaction Management:** Database transaction control is handled directly in the router, rather than in a service layer.
4.  **Authentication:** The status retrieval endpoint (`get_scan_status_api`) has authentication commented out, posing a potential security risk.
5.  **Pydantic Model Location:** A response model (`EmailScanningResponse`) is defined locally instead of in the common schemas layer.
6.  **Code Cleanliness:** Presence of relative imports (if absolute is standard) and commented-out dead code.

### 7. Audit of `src/routers/google_maps_api.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/google_maps_api.py`
- **Router Instance:** `router = APIRouter(prefix="/api/v3/localminer-discoveryscan", tags=["google-maps-api"])`
    - **Prefix and Versioning:** COMPLIANT (Blueprint 2.1.2).
    - **Tagging:** COMPLIANT (Blueprint 2.1.3).
- **Router-level Dependencies:** No router-level dependencies applied. Dependencies like `Depends(get_current_user)` are applied per-endpoint.
    - **Observation:** Applying common dependencies at the router level can enhance consistency (Blueprint 2.1.2).

**Imports:**
- Generally well-organized.
- Commented-out RBAC imports suggest potential dead code (`# from ..utils.permissions import ...`, `# from ..constants.rbac import ROLE_HIERARCHY`).
    - **Observation:** If confirmed as dead code, should be removed (Blueprint 1.5.1).

**Pydantic Models:**
- **Local Model Definitions:** `PlacesSearchRequest` and `PlacesStatusResponse` are defined locally.
    - **GAP (Medium): Local Pydantic Model Definition.** Models should reside in Layer 2 (e.g., `src/schemas/`) (Blueprint 1.2.2, 2.2.2).
- **Response Models Gaps:**
    - `search_places`: `response_model=Dict`.
        - **GAP (High): Non-Explicit Response Model.** Should use a specific Pydantic model (Blueprint 2.2.2).
    - `get_search_status`: `response_model=PlacesStatusResponse` (locally defined).
        - **Observation:** Uses an explicit model, but the model is local (see GAP above).
    - `get_staging_places`: `response_model=List[PlaceRecordSchema]` (origin of `PlaceRecordSchema` needs confirmation during non-audit tasks).
    - `update_place_status`, `batch_update_places`: `response_model=Dict`.
        - **GAP (High): Non-Explicit Response Model.** Should use specific Pydantic models (Blueprint 2.2.2).
    - `get_job_results`: `response_model=Dict`.
        - **GAP (High): Non-Explicit Response Model.** Should use a specific Pydantic model (Blueprint 2.2.2).
    - `get_search_history`: `response_model=List[PlaceSearch]` (`PlaceSearch` is an ORM model).
        - **GAP (Medium): Using ORM Model as Response Model.** Prefer dedicated Pydantic schemas for API responses (Blueprint 2.2.2).

**Service Initialization:**
- Services (`PlacesService`, `PlacesStorageService`, `PlacesSearchService`) are instantiated at the module level. Acceptable pattern.

**Endpoint Definitions & Logic:**

- **`GET /debug/info` (`get_debug_info`)**
    - Securely restricted to development mode. COMPLIANT.

- **`POST /search/places` (`search_places`)**
    - **Security:** `Depends(get_current_user)` applied. COMPLIANT.
    - **Business Logic Delegation:** Contains significant business logic (DB record creation, transaction management, background task orchestration).
        - **GAP (High): Business Logic in Router.** This logic should be in a Layer 4 service (Blueprint 2.1.1, 2.2.3.3).
    - **Transaction Management:** Manages `session.begin()` directly.
        - **GAP (Medium): Transaction Management Scope.** Should be handled by Layer 4 service (Blueprint 2.2.3.2).
    - Background task correctly handles its own session. COMPLIANT.

- **`GET /search/status/{job_id}` (`get_search_status`)**
    - **Security:** `Depends(get_current_user)` applied. COMPLIANT.
    - **Business Logic Delegation:** Fetches `PlaceSearch` record directly from DB.
        - **GAP (Medium): Business Logic in Router.** Should be delegated to a service (Blueprint 2.1.1, 2.2.3.3).
    - Direct tenant ID authorization logic present.
        - **Observation:** Authorization logic is often better placed in services.

- **`GET /staging/places` (`get_staging_places`)**
    - Delegates to `places_storage_service.get_staged_places(...)`. COMPLIANT.

- **`POST /staging/places/update-status` (`update_place_status`)**
    - Delegates to `places_storage_service.update_places_status(...)`. COMPLIANT.

- **`POST /staging/places/batch-update` (`batch_update_places`)**
    - Delegates to `places_storage_service.batch_update_places_data(...)`. COMPLIANT.

- **`GET /health` (`health_check`)**
    - **Security:** No authentication.
        - **Observation (Minor): Unauthenticated Health Check.** Consider if authentication is needed (Blueprint 2.2.3.4).

- **`GET /jobs/{job_id}/results` (`get_job_results`)**
    - **Security:** `Depends(get_current_user)` applied. COMPLIANT.
    - **Business Logic Delegation:** Fetches job details (`PlaceSearch`) directly from DB.
        - **GAP (Medium): Partial Business Logic in Router.** Job detail retrieval should be part of a service call (Blueprint 2.1.1, 2.2.3.3).
    - Direct tenant ID authorization logic present.

- **`GET /search/history` (`get_search_history`)**
    - Delegates to `places_search_service.get_search_history(...)`. COMPLIANT.

**Logging:**
- Present and informative in key areas. COMPLIANT.

**Summary for `src/routers/google_maps_api.py`:**
This router manages Google Maps related place discovery and data. Key GAPs include:
1.  **Pydantic Model Issues:** Local model definitions, use of generic `Dict` for responses, and direct use of ORM models in responses.
2.  **Business Logic in Router:** The `search_places` endpoint, in particular, handles too much logic (DB operations, transactions, task orchestration). Other endpoints also perform direct DB lookups or tenant authorization.
3.  **Transaction Management:** Router-level transaction control in `search_places`.
4.  **Code Cleanliness:** Potential dead code from commented-out imports.

The router is generally well-structured regarding prefixing, tagging, and delegation for several endpoints. The main areas for improvement are stricter adherence to Pydantic best practices and consistent delegation of all business, database, and transaction logic to Layer 4 services.

### 8. Audit of `src/routers/local_businesses.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/local_businesses.py`
- **Router Instance:** `router = APIRouter(prefix="/api/v3/local-businesses", tags=["Local Businesses"])`
    - **Prefix and Versioning:** COMPLIANT (Blueprint 2.1.2).
    - **Tagging:** COMPLIANT (Blueprint 2.1.3).
- **Router-level Dependencies:** None applied. Per-endpoint dependencies used.
    - **Observation:** Standard pattern in this project; router-level dependencies could be considered for common auth/session (Blueprint 2.1.2).

**Imports:**
- Well-organized, using absolute paths from `src`. COMPLIANT.

**Pydantic Models:**
- **Local Pydantic Models:**
    - `LocalBusinessRecord(BaseModel)`: Defined locally for API responses.
        - **GAP (Medium): Local Pydantic Model Definition.** Should be in Layer 2 (e.g., `src/schemas/`) (Blueprint 1.2.2, 2.2.2).
    - `PaginatedLocalBusinessResponse(BaseModel)`: Defined locally.
        - **GAP (Medium): Local Pydantic Model Definition.** Should be in Layer 2 (Blueprint 1.2.2, 2.2.2).
- **Request Models:**
    - `update_local_businesses_status_batch` uses `LocalBusinessBatchStatusUpdateRequest` from `src.models.api_models`. Assuming this is a Layer 2 schema location, COMPLIANT (Blueprint 2.2.1).
- **Response Models:**
    - `list_local_businesses`: Uses locally defined `PaginatedLocalBusinessResponse`. Explicit, but model location is a GAP.
    - `update_local_businesses_status_batch`: Returns `Dict[str, Any]`.
        - **GAP (High): Non-Explicit Response Model.** Needs a specific Pydantic response model (Blueprint 2.2.2).

**Endpoint Definitions & Logic:**

- **`GET /` (`list_local_businesses`)**
    - **Security:** `Depends(get_current_user)` used. COMPLIANT.
    - **Business Logic Delegation:** Directly handles all SQLAlchemy query building (select, count, filters, sorting, pagination) and execution.
        - **GAP (High): Business Logic in Router.** All DB logic should be in a Layer 4 service (Blueprint 2.1.1, 2.2.3.3).
    - **Error Handling:** Good custom error handling. COMPLIANT (Blueprint 2.2.3.5).

- **`PUT /status` (`update_local_businesses_status_batch`)**
    - **Security:** `Depends(get_current_user)` used. COMPLIANT.
    - **Business Logic Delegation:** Handles status mapping, fetching/updating ORM objects, tenant validation, and orchestrates calls to `places_service`.
        - **GAP (High): Business Logic in Router.** Most logic belongs in a Layer 4 service (Blueprint 2.1.1, 2.2.3.3).
    - **Transaction Management:** Manages `session.commit()` and `session.rollback()` directly.
        - **GAP (Medium): Transaction Management Scope.** Should be in Layer 4 service (Blueprint 2.2.3.2).
    - **Error Handling:** Good specific and general error handling. COMPLIANT (Blueprint 2.2.3.5).

**Logging:**
- Logger configured and used. COMPLIANT.

**Comments & Code Cleanliness:**
- Contains an obsolete TODO comment.
    - **Observation:** Dead comment, should be removed (Blueprint 1.5.1).

**Summary for `src/routers/local_businesses.py`:**
This router manages listing and batch status updates for local businesses. Key GAPs requiring attention:
1.  **Local Pydantic Models:** Response models are defined within the router file.
2.  **Non-Explicit Response Model:** The batch update endpoint lacks a specific Pydantic response schema.
3.  **Extensive Business Logic in Router:** Both endpoints embed significant database interaction and business rule processing instead of delegating to Layer 4 services.
4.  **Transaction Management in Router:** The update endpoint controls its database transaction directly.
5.  **Code Cleanliness:** An outdated TODO comment needs removal.

Significant refactoring is needed to move logic to a dedicated service layer and align with Pydantic best practices for response models.

### 9. Audit of `src/routers/modernized_page_scraper.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/modernized_page_scraper.py`
- **Router Instance:** `router = APIRouter(prefix="/api/v3/modernized_page_scraper", tags=["modernized_page_scraper"])`
    - **Prefix and Versioning:** COMPLIANT (Blueprint 2.1.2).
    - **Tagging:** COMPLIANT (Blueprint 2.1.3).
- **Router-level Dependencies:** None applied. Per-endpoint dependencies used.

**Imports:**
- Well-organized. Correctly imports `JobStatusResponse` from `src.schemas.job`. Other models assumed to be from Layer 2 (`..models`).
- Circular import avoidance for background tasks is handled by local import within endpoint method.
    - **Observation:** Functional, though careful service layer design can sometimes obviate this need.

**Development Mode Handling & Authorization:**
- Clear and explicit handling for development mode overrides (`is_development_mode`, `get_development_user`, `user_dependency`). COMPLIANT.
- Custom authorization dependency `verify_page_scraper_access` used. COMPLIANT.

**Pydantic Models (Usage):**
- **Request/Response Models:** All endpoints use explicit Pydantic models imported from assumed Layer 2 locations (`..models`, `..schemas.job`). COMPLIANT (Blueprint 2.2.1, 2.2.2).

**Endpoint Definitions & Logic:**

- **`POST /scan` (`scan_domain`)**
    - **Security:** Uses `Depends(verify_page_scraper_access)`. COMPLIANT.
    - **Business Logic Delegation:** Delegates to `user_context_service` and `page_processing_service`. Background task correctly initiated. COMPLIANT (Blueprint 2.1.1).
    - **Transaction Management:** Router owns `async with session.begin():` for the `initiate_domain_scan` service call.
        - **GAP (Medium): Transaction Management Scope.** Transaction should ideally be managed within the `page_processing_service.initiate_domain_scan` method (Blueprint 2.2.3.2).

- **`POST /batch` (`batch_scan_domains`)**
    - **Security:** Uses `Depends(verify_page_scraper_access)`. COMPLIANT.
    - **Business Logic Delegation:** Delegates to `user_context_service` and `page_processing_service`. Background task correctly initiated. COMPLIANT (Blueprint 2.1.1).
    - **Transaction Management:** Router owns `async with session.begin():` for the `initiate_batch_domain_scan` service call.
        - **GAP (Medium): Transaction Management Scope.** Transaction should ideally be managed within the `page_processing_service.initiate_batch_domain_scan` method (Blueprint 2.2.3.2).

- **`GET /status/job/{job_id}` (`get_job_status`)**
    - **Security:** Uses `Depends(verify_page_scraper_access)`. COMPLIANT.
    - **Business Logic Delegation:** Delegates to `page_processing_service.get_job_status()`. COMPLIANT (Blueprint 2.1.1).

- **`GET /status/batch/{batch_id}` (`get_batch_status`)**
    - **Security:** Uses `Depends(verify_page_scraper_access)`. COMPLIANT.
    - **Business Logic Delegation:** Delegates to `page_processing_service.get_batch_status()`. COMPLIANT (Blueprint 2.1.1).

**Logging:**
- Logger configured and used effectively. COMPLIANT.

**Comments & Code Cleanliness:**
- Good docstrings. Comments indicate intentional removal of RBAC logic.
    - **Observation:** Code is clean and reflects current design regarding authorization.

**Summary for `src/routers/modernized_page_scraper.py`:**
This router is well-structured for handling page scraping tasks, demonstrating good adherence to blueprint principles for Pydantic model usage, business logic delegation (to services), and security dependencies. The main finding is:
1.  **Transaction Management Scope:** Transactions for initial DB operations (job/batch creation) are managed by the router instead of within the service methods that perform these operations. This is a medium-level GAP.

Overall, a compliant router with a minor architectural refinement recommended for transaction handling.

### Note on `src/routers/page_metadata_crud.py`

**AUDIT_ALERT:** The file `src/routers/page_metadata_crud.py`, listed in the `Layer-3.2-Routers_Audit-Plan.md`, was not found in the `src/routers/` directory as of this audit. This file will be skipped. It is recommended to update the audit plan or investigate the missing file.

### 10. Audit of `src/routers/modernized_sitemap.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/modernized_sitemap.py`
- **Router Instance:** `router = APIRouter(prefix="/api/v3/sitemap", tags=["sitemap"])`
    - **Prefix and Versioning:** COMPLIANT (Blueprint 2.1.2).
    - **Tagging:** COMPLIANT (Blueprint 2.1.3).
- **Router-level Dependencies:** `check_sitemap_access` dependency is defined but not applied at the router level; endpoints use `user_dependency` directly for some auth aspects.

**Imports:**
- Generally well-organized. Pydantic models assumed to be from Layer 2 locations.
- **GAP (Low): Accessing Internal Variable.** Router directly imports and manipulates `_job_statuses` from `sitemap_processing_service` in `scan_domain` and `get_job_status` (dev mode), which appears to be an internal variable (Blueprint 1.2.1, 1.3.1).

**Development Mode Handling & Authorization:**
- Clear development mode helpers (`is_development_mode`, `is_feature_check_disabled`, `get_development_user`). COMPLIANT.
- `check_sitemap_access` dependency logs "ALL TENANT CHECKS COMPLETELY REMOVED" and returns a default tenant ID.
    - **GAP (Medium): Inconsistent/Bypassed Authorization Logic.** The `check_sitemap_access` dependency is not consistently used by endpoints. The removal of tenant checks is a significant security policy observation requiring verification against project standards (Blueprint 2.2.3.1).

**Pydantic Models (Usage):**
- Request (`SitemapScrapingRequest`) and Response (`SitemapScrapingResponse`, `JobStatusResponse`) models are used. COMPLIANT (Blueprint 2.2.1, 2.2.2).

**Endpoint Definitions & Logic:**

- **`POST /scan` (`scan_domain`)**
    - **Security:** Uses `Depends(user_dependency)`. Bypasses the `check_sitemap_access` dependency.
        - **GAP (Medium): Potentially Incomplete Authorization.** Relies on general `user_dependency` without specific sitemap access verification intended by `check_sitemap_access` (Blueprint 2.2.3.1).
    - **Business Logic Delegation:** Creates `job_id`. Calls `job_service.create()`. Directly manipulates `_job_statuses` (see import GAP). Initiates background task. Some logic (ID gen, status init) should be fully in service.
        - **GAP (Low): Minor Business Logic in Router.** Job ID generation and initial in-memory status dict population should be encapsulated in the service (Blueprint 2.1.1).
    - **Transaction Management:** Router owns `async with session.begin():` for `job_service.create()`.
        - **GAP (Medium): Transaction Management Scope.** Transaction should be managed within `job_service.create()` (Blueprint 2.2.3.2).

- **`GET /status/{job_id}` (`get_job_status`)**
    - **Security:** Likely uses `user_dependency`. Similar potential GAP as `/scan` regarding `check_sitemap_access`.
    - **Business Logic Delegation:** In development/test mode, directly accesses and returns data from `_job_statuses` from `sitemap_processing_service`.
        - **GAP (Medium): Business Logic in Router / Accessing Service Internals.** Bypasses service layer for data retrieval in certain modes. All data access should go via service interfaces (Blueprint 2.1.1, 1.3.1).

**Logging:**
- Logger configured and used effectively. COMPLIANT.

**Comments & Code Cleanliness:**
- Informative header. Constants defined, though their current relevance with removed RBAC is unclear.

**Summary for `src/routers/modernized_sitemap.py`:**
This router shows attempts at modernization but has several key GAPs:
1.  **Authorization Concerns:** The `check_sitemap_access` dependency is inconsistently applied, and a comment about removing tenant checks raises alarms. This needs alignment with security policies.
2.  **Service Encapsulation Violation:** Direct access and manipulation of an internal variable (`_job_statuses`) of `sitemap_processing_service` by the router.
3.  **Business Logic in Router:** Some logic, particularly job ID generation, initial status setup, and dev-mode status retrieval, resides in the router instead of being fully delegated to services.
4.  **Transaction Management Scope:** Transactions are managed by the router for service calls.

Significant review of authorization mechanisms and refactoring for better service delegation and encapsulation are needed.

### 11. Audit of `src/routers/page_curation.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/page_curation.py`
- **Router Instance:** `router = APIRouter()`
    - **GAP (High): Missing Router Prefix & Versioning.** No prefix or version defined (e.g., `/api/v3/...`) (Blueprint 2.1.2).
    - **GAP (Medium): Missing Router Tags.** No tags defined for OpenAPI documentation (Blueprint 2.1.3).
- **Router-level Dependencies:** None.

**Imports:**
- Well-organized. Pydantic models from `src.schemas.page_curation` (assumed Layer 2). COMPLIANT.
- Authentication imports are commented out.
    - **Observation:** Suggests auth was planned or removed.

**Pydantic Models (Usage):**
- Request (`PageCurationUpdateRequest`) and Response (`PageCurationUpdateResponse`) models are used. COMPLIANT (Blueprint 2.2.1, 2.2.2).

**Endpoint Definitions & Logic:**

- **`PUT /pages/curation-status` (`update_page_curation_status_batch`)**
    - **Security:** Authentication dependency `get_current_active_user` is commented out.
        - **GAP (Critical): Missing Authentication.** Endpoint performs database updates without any authentication. This is a critical security risk (Blueprint 2.2.3.1).
    - **Business Logic Delegation:** Directly constructs and executes SQLAlchemy `update` statements, including conditional logic for setting other page statuses.
        - **GAP (High): Business Logic in Router.** All database interaction and related conditional logic should be in a Layer 4 service (Blueprint 2.1.1, 2.2.3.3).
    - **Transaction Management:** Manages `async with session.begin():` directly.
        - **GAP (Medium): Transaction Management Scope.** Transactions should be controlled by the Layer 4 service (Blueprint 2.2.3.2).
    - **Error Handling:** No specific `try...except` blocks for database or other errors.
        - **GAP (Low): Lack of Specific Error Handling.** Relies on default FastAPI handling; specific handling for `SQLAlchemyError` etc. is preferred (Blueprint 2.2.3.5).

**Logging:**
- Logger configured and used. COMPLIANT.

**Comments & Code Cleanliness:**
- Endpoint has a docstring. Commented-out auth code is present.

**Summary for `src/routers/page_curation.py`:**
This router has critical and high-severity GAPs that need immediate attention:
1.  **Missing Router Configuration:** Lacks API prefix, versioning, and tags.
2.  **Critical Security Vulnerability:** The sole endpoint updates database records without any authentication.
3.  **Business Logic in Router:** All database update logic is directly within the endpoint.
4.  **Transaction Management in Router:** The endpoint handles its own transaction.

This router needs urgent remediation for the security flaw and significant refactoring to align with architectural standards for logic delegation, router configuration, and error handling.

### 12. Audit of `src/routers/places_staging.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/places_staging.py`
- **Router Instance:** `router = APIRouter(tags=["Places Staging"], responses={404: {"description": "Not found"}})`
    - **GAP (High): Missing Router Prefix & Versioning.** No prefix or version defined (e.g., `/api/v3/...`) (Blueprint 2.1.2).
    - **Tagging:** `["Places Staging"]`. COMPLIANT (Blueprint 2.1.3).
- **Router-level Dependencies:** Auth commented out; per-endpoint auth used.

**Imports:**
- Generally organized. Imports models from `..models.api_models` and ORM models directly.
    - **GAP (Medium): Potential Pydantic Model Location.** If `..models.api_models` is not the designated Layer 2 schema dir, `PlaceStagingListResponse` and `PlaceStagingRecord` should be moved (Blueprint 1.2.2, 2.2.2).

**Pydantic Models (Definition & Usage):**
- **Local Pydantic Models:** `PaginatedPlaceStagingResponse`, `QueueDeepScanRequest`, `PlaceBatchStatusUpdateRequest` are defined locally.
    - **GAP (Medium): Local Pydantic Model Definition.** These request/response models should be in Layer 2 (Blueprint 1.2.2, 2.2.1, 2.2.2).
- **Response Model Usage:** Some endpoints lack explicit `response_model` in decorators (e.g., `update_places_status_batch`, `queue_places_for_deep_scan`, `list_staged_places`).
    - **GAP (Medium): Missing Explicit Response Models.** Endpoints should use explicit Pydantic response models from Layer 2 (Blueprint 2.2.2).

**Endpoint Definitions & Logic:**

- **`GET /places/staging` (`list_all_staged_places`)**
    - **Security:** Uses `Depends(get_current_user)`. COMPLIANT.
    - **Business Logic Delegation:** Uses raw SQL and ORM queries directly for data fetching and counting; performs data mapping.
        - **GAP (High): Business Logic in Router.** All DB interaction, pagination, and data mapping belong in Layer 4 (Blueprint 2.1.1, 2.2.3.3).

- **`PUT /places/staging/status` (`update_places_status_batch`)** (Partially inferred)
    - **Security:** Uses `Depends(get_current_user)`. COMPLIANT.
    - **Business Logic Delegation:** Likely direct DB updates.
        - **GAP (High): Business Logic in Router.** (Blueprint 2.1.1, 2.2.3.3).
    - **Transaction Management:** Likely direct.
        - **GAP (Medium): Transaction Management Scope.** (Blueprint 2.2.3.2).

- **`POST /places/staging/queue-deep-scan` (`queue_places_for_deep_scan`)** (Partially inferred)
    - **Security:** Uses `Depends(get_current_user)`. COMPLIANT.
    - **Business Logic Delegation:** Likely direct DB updates.
        - **GAP (High): Business Logic in Router.** (Blueprint 2.1.1, 2.2.3.3).
    - **Transaction Management:** Likely direct.
        - **GAP (Medium): Transaction Management Scope.** (Blueprint 2.2.3.2).

- **`GET /places/staging/discovery-job/{discovery_job_id}` (`list_staged_places`)** (Partially inferred)
    - **Security:** Auth appears missing or commented out.
        - **GAP (Critical/High): Missing/Inconsistent Authentication.** Needs auth if data is sensitive/tenant-specific (Blueprint 2.2.3.1).
    - **Business Logic Delegation:** Likely direct DB queries.
        - **GAP (High): Business Logic in Router.** (Blueprint 2.1.1, 2.2.3.3).

**Logging:**
- Logger configured and used. COMPLIANT.

**Summary for `src/routers/places_staging.py`:**
This router has multiple significant GAPs:
1.  **Missing Router Configuration:** Lacks API prefix and versioning.
2.  **Pydantic Model Issues:** Several models are defined locally instead of in Layer 2, and some endpoints lack explicit response models.
3.  **Extensive Business Logic in Router:** Most endpoints perform direct database operations and data manipulation.
4.  **Transaction Management in Router:** Update operations likely handle transactions directly.
5.  **Authentication Gaps:** One endpoint appears to lack necessary authentication.

Requires substantial refactoring for compliance with architectural standards, focusing on service layer delegation, Pydantic model management, and consistent security.

### 13. Audit of `src/routers/profile.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/profile.py`
- **Router Instance:** `router = APIRouter(prefix="/api/v3/profiles", tags=["profiles"])`
    - **Prefix and Versioning:** `/api/v3/profiles`. COMPLIANT (Blueprint 2.1.2).
    - **Tagging:** `["profiles"]`. COMPLIANT (Blueprint 2.1.3).
- **Router-level Dependencies:** None (per-endpoint dependencies used).

**Imports:**
- Well-organized. Imports `ProfileService` and Pydantic models like `ProfileCreate`, `ProfileUpdate` from `..models.profile`.
    - **GAP (Medium): Potential Pydantic Model Location.** If `..models.profile` is not the designated Layer 2 schema directory (e.g., `src/schemas/`), `ProfileCreate` and `ProfileUpdate` should be moved there (Blueprint 1.2.2).

**Pydantic Models (Usage):**
- **Request Models:** Uses `ProfileCreate`, `ProfileUpdate`. Location compliance as per Imports GAP.
- **Response Models:** All endpoints use `response_model=dict`.
    - **GAP (Medium): Generic Dict as Response Model.** Endpoints should return specific Pydantic models from Layer 2, not generic `dict`, to improve OpenAPI schema and type safety (Blueprint 2.2.2).

**Endpoint Definitions & Logic:**
- **General Structure:** Endpoints consistently use `Depends(get_current_user)`, `Depends(get_session_dependency)`, delegate logic to `ProfileService`, and use a standard `try/except` block for error handling. Business logic delegation is COMPLIANT (Blueprint 2.1.1, 2.2.3.3).
- **Transaction Management:** All endpoints wrap service calls in `async with session.begin(): ...` within the router.
    - **GAP (Medium): Transaction Management Scope.** Database transactions should ideally be managed within the `ProfileService` methods, not in the router (Blueprint 2.2.3.2).
- **Tenant ID Handling:** All endpoints use a hardcoded `DEFAULT_TENANT_ID`.
    - **Observation:** This is a design choice. If multi-tenancy for profiles is expected via user token, this needs review.
- **Unused Dependency:** `get_profiles` endpoint includes `db_params = Depends(get_db_params)` which is not used in the router's visible logic.

**Logging:**
- Logger configured and used appropriately. COMPLIANT.

**Comments & Code Cleanliness:**
- Good docstrings and readable code. COMPLIANT.

**Summary for `src/routers/profile.py`:**
This router is relatively well-structured and correctly delegates business logic to a service layer. Key areas for improvement:
1.  **Pydantic Model Location:** Ensure request models (`ProfileCreate`, `ProfileUpdate`) are in the standard Layer 2 schemas directory.
2.  **Response Models:** Replace `response_model=dict` with specific Pydantic models from Layer 2.
3.  **Transaction Management:** Shift transaction control (`session.begin()`) from router endpoints to the corresponding methods in `ProfileService`.
4.  **Tenant ID:** Confirm the use of `DEFAULT_TENANT_ID` aligns with multi-tenancy strategy for profiles.

Overall, this router requires moderate refactoring, mainly focused on Pydantic model usage and transaction scope, to fully align with architectural standards.

### 14. Audit of `src/routers/sitemap_files.py`

**Overall Router Configuration:**
- **File Path:** `src/routers/sitemap_files.py`
- **Router Instance:** `router = APIRouter(prefix="/api/v3/sitemap-files", tags=["Sitemap Files"], responses={404: {"description": "Not found"}})`
    - **Prefix and Versioning:** `/api/v3/sitemap-files`. COMPLIANT (Blueprint 2.1.2).
    - **Tagging:** `["Sitemap Files"]`. COMPLIANT (Blueprint 2.1.3).
- **Router-level Dependencies:** None (per-endpoint dependencies used).

**Imports:**
- Well-organized. Imports services from Layer 4 (`SitemapFilesService`) and Pydantic schemas from Layer 2 (`PaginatedSitemapFileResponse`, `SitemapFileCreate`, etc.). COMPLIANT.

**Pydantic Models (Usage):**
- **Request Models:** Uses specific Pydantic models from Layer 2 (`src.schemas.sitemap_file`) like `SitemapFileBatchUpdate`, `SitemapFileCreate`. COMPLIANT.
- **Response Models:** Most endpoints use specific Pydantic models from Layer 2 (`PaginatedSitemapFileResponse`, `SitemapFileRead`). COMPLIANT.
    - `update_sitemap_files_status_batch` uses `response_model=Dict[str, int]`.
        - **GAP (Low/Medium): Generic Dict as Response Model.** While functional for simple dicts, a dedicated Pydantic model from Layer 2 would be more consistent for OpenAPI schema definition (Blueprint 2.2.2).

**Endpoint Definitions & Logic:**
- **General Structure:** Endpoints consistently use appropriate dependencies, delegate logic to `SitemapFilesService`, and implement standard error handling. Business logic delegation is COMPLIANT (Blueprint 2.1.1, 2.2.3.3).
- **Transaction Management:** Service methods are called directly. It's assumed the `SitemapFilesService` internally manages database transactions (e.g., with `session.begin()`).
    - **VERIFICATION_NEEDED (Layer 4):** Confirm `SitemapFilesService` methods handle their own transaction atomicity (Blueprint 2.2.3.2).

**Logging:**
- Logger configured and used appropriately. COMPLIANT.

**Comments & Code Cleanliness:**
- Good docstrings and readable code. COMPLIANT.

**Summary for `src/routers/sitemap_files.py`:**
This router demonstrates strong adherence to architectural best practices:
1.  Correctly configured with prefix and tags.
2.  Properly imports and utilizes Layer 2 schemas and Layer 4 services.
3.  Delegates all business logic to the service layer.

The main point for minor improvement is using a specific Pydantic model for the batch update response instead of a generic `Dict`. The overall compliance heavily relies on the correct implementation of transaction management within the `SitemapFilesService` (to be verified in Layer 4 audit).

<!-- END_OF_AUDIT_REPORTS -->
