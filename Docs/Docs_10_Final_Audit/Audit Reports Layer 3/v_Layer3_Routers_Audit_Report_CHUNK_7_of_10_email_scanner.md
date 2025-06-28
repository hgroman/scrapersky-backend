# Layer 3: Routers - AI Audit Summary (Chunk)

_This is a segment of the full Layer 3 audit report, focusing on a specific component._

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

