# Layer 3: Routers - AI Audit Summary (Chunk)

_This is a segment of the full Layer 3 audit report, focusing on a specific component._

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

