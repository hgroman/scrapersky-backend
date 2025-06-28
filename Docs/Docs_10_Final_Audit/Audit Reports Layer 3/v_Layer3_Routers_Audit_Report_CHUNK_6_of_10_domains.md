# Layer 3: Routers - AI Audit Summary (Chunk)

_This is a segment of the full Layer 3 audit report, focusing on a specific component._

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

