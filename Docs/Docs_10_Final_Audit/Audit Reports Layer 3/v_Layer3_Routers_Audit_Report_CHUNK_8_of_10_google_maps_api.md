# Layer 3: Routers - AI Audit Summary (Chunk)

_This is a segment of the full Layer 3 audit report, focusing on a specific component._

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

