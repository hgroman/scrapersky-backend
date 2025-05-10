# WF1-SingleSearch: Linear Workflow Steps (Editable, Line-by-Line)

> **Protocol Notice:**
> If a workflow change requires modifying database columns or ENUMs, the AI pairing module must provide a ready-to-run SQL script for the change. Manual execution is required because Alembic and migrations are broken in this project. Do not attempt to use Alembic for schema changes.

Each step includes placeholders for Source Table and Destination Table. Use 'N/A' if not applicable for this workflow.

---

**1.1 [UI Interaction]**
- File: static/js/single-search-tab.js
- Action: User enters query/location, clicks "Search"
- Source Table: N/A
- Destination Table: N/A
- Principles: API Standardization (all UI/API calls must use standardized endpoints and response formats as described in the API Standardization Guide), Clear User Feedback
- **[GUIDE]**: [API Standardization Guide](../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md)
- Notes: Verify JS details

**1.2 [API Routing: JWT Authentication]**
- File: src/routers/google_maps_api.py (leverages src/auth/jwt_auth.py)
- Action: JWT authentication is performed on the incoming request using logic imported from src/auth/jwt_auth.py (no tenant isolation; user identity only)
- Source Table: N/A
- Destination Table: N/A
- Principles: Authentication Boundary (JWT authentication must ONLY occur at the API router level—never in services or database operations, as described in the Authentication Boundary Guide); No Tenant Isolation
- **[GUIDE]**: [Authentication Boundary Guide](../Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md)
- Notes: JWT logic (token validation, user extraction) lives in src/auth/jwt_auth.py. The router imports and uses this logic to enforce authentication and extract user_id. Do not use tenant_id.
- **[SHARED FILE]**: Authentication logic is shared and centralized in src/auth/jwt_auth.py

**1.3 [API Routing: Request Validation & ENUM Handling]**
- File: src/routers/google_maps_api.py (references src/models/enums.py)
- Action: Endpoint POST /api/v3/localminer-discoveryscan/search/places receives request, validates input, checks ENUMs (e.g., PlaceStatusEnum from src/models/enums.py)
- Source Table: N/A
- Destination Table: N/A
- Principles: API Std, Enum Handling (validate against PlaceStatusEnum), Conn Mgmt, Txn Boundary, Code Org, UUID Std
- Notes: ENUMs are defined in src/models/enums.py and must be validated here if present in request
- **[SHARED FILE]**: Validation helpers may be leveraged from src/services/core/validation_service.py

**1.4 [API Routing: Service Delegation]**
- File: src/routers/google_maps_api.py (delegates to src/services/places/places_search_service.py)
- Action: Router delegates business logic to PlacesSearchService.search_and_store
- Source Table: N/A
- Destination Table: N/A
- Principles: Delegation, Code Organization
- Notes: No business logic in the router; all heavy lifting is in the service layer.

**1.5 [Service: Search & Store Logic]**
- File: src/services/places/places_search_service.py (uses src/models/enums.py, src/models/api_models.py)
- Action: Handles:
    - ENUM validation (re-validates as needed)
    - Input validation (location, business_type, etc.)
    - Data cleansing/standardization (may use helpers)
    - Error handling (structured error messages, logs)
    - Orchestration of downstream storage (calls PlacesStorageService)
- Source Table: N/A
- Destination Table: Place, PlaceSearch
- Principles: Validation, Enum Handling, Error Handling, Code Organization, ORM Required
- Notes: All business logic, validation, and error handling are centralized here. ENUMs are validated before DB interaction. Helpers may be used for data cleansing/standardization. ORM models are used for all DB access (src/models/api_models.py).
- **[SHARED FILE]**: Validation logic and helpers may be imported from src/services/core/validation_service.py, database helpers from src/utils/db_helpers.py

**1.6 [Service: Storage Logic]**
- File: src/services/places/places_storage_service.py (uses src/models/api_models.py, src/models/place.py)
- Action: Stores places and search results in DB using ORM models. **ALL storage logic is performed using SQLAlchemy ORM only. Raw SQL is absolutely prohibited.**
- Source Table: N/A
- Destination Table: Place, PlaceSearch
- Principles: ORM Required, Error Handling, Code Organization
- Notes: All DB inserts/updates use ORM models defined in src/models/api_models.py and src/models/place.py. Handles batch operations and error logging. **This step strictly enforces the architectural rule described in [Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md).**
- **[GUIDE]**: [Absolute ORM Requirement](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)

**1.7 [Service: Error Handling & Status Update]**
- File: src/services/places/places_search_service.py
- Action: Handles all exceptions and updates PlaceSearch job status to 'failed' on error; logs errors.
- Source Table: PlaceSearch
- Destination Table: PlaceSearch
- Principles: Error Handling, Code Organization
- Notes: All error handling follows the project error handling conventions. (Guide reference pending: Docs_1_AI_GUIDES/22-ERROR_HANDLING_GUIDE.md does not exist.)
- **[GUIDE]**: _(Guide missing)_

**1.8 [Database Models: PlaceSearch & Place]**
- File: src/models/place_search.py, src/models/place.py
- Action: Defines SQLAlchemy models for PlaceSearch (search job) and Place (place result)
- Source Table: PlaceSearch, Place
- Destination Table: PlaceSearch, Place
- Principles: ORM Required, Code Organization
- Notes: Models must use SQLAlchemy ORM and match DB schema. Enums for status are defined in src/models/place.py.
- **[GUIDE]**: [Absolute ORM Requirement](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)

**1.9 [ENUM Handling: PlaceStatusEnum]**
- File: src/models/place.py, src/models/api_models.py
- Action: All status fields for Place and PlaceSearch must use the defined Enum classes (PlaceStatusEnum, PlaceStagingStatusEnum)
- Source Table: Place, PlaceSearch
- Destination Table: Place, PlaceSearch
- Principles: Enum Handling, Validation, Code Organization
- Notes: Enum validation is performed in routers/services. (Guide reference pending: Docs_1_AI_GUIDES/20-ENUM_HANDLING_GUIDE.md does not exist.)
- **[GUIDE]**: _(Guide missing)_

**1.10 [Configuration: API Key]**
- File: .env, docker-compose.yml
- Action: Stores GOOGLE_MAPS_API_KEY used by PlacesService
- Source Table: N/A
- Destination Table: N/A
- Principles: Secure Configuration, Code Organization
- Notes: API key must never be hardcoded in source files. Use environment variables.
- **[GUIDE]**: _(Best practices, no local guide)_

---

### Workflow Table (Atomic Steps Reference)

| Step  | Description                  | File(s)                                 | Action/Responsibility                                                                 | Principles & Guides                                                                                 | Notes/Helpers                       |
|-------|------------------------------|-----------------------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|--------------------------------------|
| 1.1   | UI Interaction               | static/js/single-search-tab.js          | User enters query/location, clicks "Search"                                          | API Standardization ([Guide](../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md)), Clear User Feedback | Verify JS details                    |
| 1.2   | API Routing: JWT Auth        | src/routers/google_maps_api.py, src/auth/jwt_auth.py | JWT authentication, user extraction, no tenant isolation                              | Auth Boundary ([Guide](../Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md)), No Tenant Isolation      | JWT logic is shared/centralized      |
| 1.3   | Request Validation & ENUM    | src/routers/google_maps_api.py, src/models/enums.py | Validates input, checks ENUMs                                                         | API Std, Enum Handling, Validation, Code Org ([Guide](../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md)) | Validation helpers in core service   |
| 1.4   | Service Delegation           | src/routers/google_maps_api.py, src/services/places/places_search_service.py | Router delegates to PlacesSearchService                                               | Delegation, Code Organization                                                        | No business logic in router          |
| 1.5   | Search & Store Logic         | src/services/places/places_search_service.py, src/models/enums.py, src/models/api_models.py | Orchestrates search, validation, error handling, calls storage                        | Validation, Enum Handling, Error Handling, ORM Req ([Guide](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)) | Uses helpers, ORM models             |
| 1.6   | Storage Logic                | src/services/places/places_storage_service.py, src/models/api_models.py, src/models/place.py | Stores results, ORM-only, batch ops, error logging                                    | ORM Required ([Guide](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)), Error Handling           | Strict ORM, batch ops, error logs    |
| 1.7   | Error Handling & Status      | src/services/places/places_search_service.py         | Handles exceptions, updates job status                                                | Error Handling (Guide missing), Code Organization                                    | Logs errors, updates status          |
| 1.8   | DB Models: PlaceSearch/Place | src/models/place_search.py, src/models/place.py      | Defines ORM models                                                                    | ORM Required ([Guide](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)), Code Org                  | Models match DB, enums in place.py   |
| 1.9   | ENUM Handling                | src/models/place.py, src/models/api_models.py        | Enum classes used/validated for status fields                                         | Enum Handling (Guide missing), Validation, Code Organization                         | Enum validation in router/service    |
| 1.10  | Config: API Key              | .env, docker-compose.yml                           | Stores GOOGLE_MAPS_API_KEY for PlacesService                                          | Secure Config (Best practices, no guide)                                              | Never hardcode keys                  |

---

_Add additional steps as needed. Insert or renumber steps to reflect changes in the workflow. This format is optimized for collaborative discussion and editing._

_Last updated: 2025-05-04 09:20 PDT_

| 1.1   | UI Interaction              | static/js/single-search-tab.js         | User enters query/location, clicks "Search"                                                               | API Standardization, Clear User Feedback                            | Verify JS details         |
| 2.1   | API Routing                 | src/routers/google_maps_api.py         | Endpoint POST /api/v3/localminer-discoveryscan/search/places receives request, validates                   | API Std, Auth Boundary, Conn Mgmt, Txn Boundary, Code Org, UUID Std, Enum Handling |                           |
| 2.2   | API Routing                 | src/routers/google_maps_api.py         | Calls PlacesSearchService.search_and_store (background task)                                               | Auth Boundary (user_id passed), Txn Boundary (session passed), Code Org (delegation) |                           |
| 3.1   | Service Delegation & Logic  | src/services/places/places_search_service.py | search_and_store calls PlacesService.search_places and PlacesStorageService.store_places                  | Auth Boundary (agnostic), Txn Boundary (aware), ORM Req, Code Org, UUID Std, Enum Handling |                           |

<!-- Add further steps and phases as needed for deeper audit granularity -->

---

_Last updated: 2025-05-04 08:42 PDT_
