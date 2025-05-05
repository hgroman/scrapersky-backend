# WF2-StagingEditor: Linear Workflow Steps

_Last verified & updated: 2025-05-04T23:45:30-07:00 by Cascade AI_

> **Protocol Notice:**
> If a workflow change requires modifying database columns or ENUMs, the AI pairing module must provide a ready-to-run SQL script for the change. Manual execution is required because Alembic and migrations are broken in this project. Do not attempt to use Alembic for schema changes.

Each step includes Source Table and Destination Table to track data flow through the workflow. Use 'N/A' if not applicable.

---

## Workflow: Staging Editor "Selected" Status to Deep Scan Queueing

This workflow documents the precise sequence from a user selecting items in the Staging Editor UI and setting their status to "Selected", through the dual-status update pattern, to background task execution. This is a critical workflow that transitions items from manual review to automated deep scanning.

### Key Model & Enum Dependencies

- **Models**: `src/models/place.py::Place`
- **Enums**: `src/models/place.py::PlaceStatusEnum`, `src/models/place.py::DeepScanStatusEnum`, `src/models/api_models.py::PlaceStagingStatusEnum`

### Data Flow Summary

1. **Source Trigger**: User action in UI sets `Place.status = Selected`
2. **Coupled Status Change**: API automatically sets `Place.deep_scan_status = Queued`
3. **Background Processing**: Scheduler polls for `Place.deep_scan_status = Queued` records and processes them

---

**2.1 [UI Interaction]**
- File: static/js/staging-editor-tab.js
- Action: User selects rows, sets status="Selected", clicks "Update X Selected"
- Source Table: N/A
- Destination Table: N/A
- Principles: API Standardization (all UI/API calls must use standardized endpoints and response formats as described in the API Standardization Guide), Clear User Feedback
- **[GUIDE]**: [API Standardization Guide](../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md)
- Notes: Verify JS details

**2.2 [API Routing: JWT Authentication]**
- File: src/routers/places_staging.py [NOVEL]
- Action: JWT authentication is performed on the incoming request using logic imported from src/auth/jwt_auth.py (no tenant isolation; user identity only)
- Source Table: N/A
- Destination Table: N/A
- Principles: Authentication Boundary (JWT authentication must ONLY occur at the API router level—never in services or database operations, as described in the Authentication Boundary Guide); No Tenant Isolation
- **[GUIDE]**: [Authentication Boundary Guide](../Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md)
- Notes: JWT logic (token validation, user extraction) lives in src/auth/jwt_auth.py. The router imports and uses this logic to enforce authentication and extract user_id. Do not use tenant_id.

**2.3 [API Routing: Request Validation & ENUM Handling]**
- File: src/routers/places_staging.py [NOVEL], src/models/api_models.py [SHARED]
- Action: Endpoint PUT /api/v3/places/staging/status receives request, validates input, checks ENUMs (e.g., PlaceStagingStatusEnum from src/models/api_models.py)
- Source Table: N/A
- Destination Table: N/A
- Principles: API Std, Enum Handling (validate against PlaceStagingStatusEnum), Conn Mgmt, Txn Boundary, Code Org, UUID Std
- Notes: ENUMs are defined in src/models/api_models.py and must be validated here if present in request

**2.4 [API Routing: Service Delegation]**
- File: src/routers/places_staging.py [NOVEL]
- Action: Router delegates business logic to places_staging_service.update_places_status (or performs inline logic)
- Source Table: N/A
- Destination Table: N/A
- Principles: Delegation, Code Organization
- Notes: No business logic in the router; all heavy lifting is in the service layer or inline in router if service missing.

**2.5 [Service: Status Update Logic]**
- File: src/services/places_staging_service.py [SHARED]
- Action: Handles:
    - ENUM validation (re-validates as needed)
    - Input validation (place_ids, status)
    - Data cleansing/standardization (may use helpers)
    - Error handling (structured error messages, logs)
    - Orchestration of downstream status update (calls ORM)
- Source Table: N/A
- Destination Table: Place
- Principles: Validation, Enum Handling, Error Handling, Code Organization, ORM Required
- Notes: All business logic, validation, and error handling are centralized here. ENUMs are validated before DB interaction. Helpers may be used for data cleansing/standardization. ORM models are used for all DB access (src/models/api_models.py, src/models/place.py).

**2.6 [Service: Dual-Status Update]**
- File: src/services/places_staging_service.py [SHARED], src/models/place.py [SHARED]
- Action: Updates place.status=Selected, place.deep_scan_status=Queued using ORM
- Source Table: Place
- Destination Table: Place
- Principles: ORM Required, Error Handling, Code Organization
- Notes: All DB inserts/updates use ORM models defined in src/models/api_models.py and src/models/place.py. Handles batch operations and error logging. **This step strictly enforces the architectural rule described in [Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md).**

**2.7 [Background Task: Queue Trigger]**
- File: src/services/places_staging_service.py [SHARED]
- Action: Setting deep_scan_status = 'Queued' acts as trigger for background job
- Source Table: Place
- Destination Table: Place
- Principles: Decoupling, Atomicity
- Notes: Status-based queuing

**2.8 [Background Task: Scheduler Poll]**
- File: src/services/sitemap_scheduler.py [SHARED], src/scheduler_instance.py [SHARED]
- Action: Polls DB for Place with deep_scan_status='Queued', schedules jobs
- Source Table: Place
- Destination Table: Place
- Principles: Bg Task Pattern, Conn Mgmt, Txn Boundary, ORM Required, Code Org, Error Handling
- Notes: Scheduler picks up queued jobs and delegates to PlacesDeepService

**2.9 [Background Task: Deep Scan Execution]**
- File: src/services/places_deep_service.py [SHARED]
- Action: Processes the deep scan for the place (fetches, analyzes, updates Place)
- Source Table: Place
- Destination Table: Place
- Principles: Bg Task Pattern, Txn Boundary, ORM Required
- Notes: All DB operations must use ORM. No raw SQL permitted. Logs progress and errors.

**2.10 [Database Models: Place]**
- File: src/models/place.py [SHARED]
- Action: Defines SQLAlchemy model for Place (status, deep_scan_status, etc.)
- Source Table: Place
- Destination Table: Place
- Principles: ORM Required, Code Organization
- Notes: Models must use SQLAlchemy ORM and match DB schema. Enums for status are defined in src/models/place.py.
- **[GUIDE]**: [Absolute ORM Requirement](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)

**2.11 [ENUM Handling: PlaceStatusEnum, DeepScanStatusEnum]**
- File: src/models/place.py [SHARED], src/models/api_models.py [SHARED]
- Action: All status fields for Place must use the defined Enum classes (PlaceStatusEnum, DeepScanStatusEnum)
- Source Table: Place
- Destination Table: Place
- Principles: Enum Handling, Validation, Code Organization
- Notes: Enum validation is performed in routers/services. (Guide reference pending: Docs_1_AI_GUIDES/20-ENUM_HANDLING_GUIDE.md does not exist.)

**2.12 [Configuration: Scheduler Settings]**
- File: docker-compose.yml, src/config/settings.py
- Action: Stores scheduler interval, batch size, and max instances
- Source Table: N/A
- Destination Table: N/A
- Principles: Secure Configuration, Code Organization
- Notes: Never hardcode keys; use environment variables

---

| Step  | Phase/Action                  | File(s)                                           | Description                                                                  | Principles/Guides                                              | Notes                                      |
|-------|-------------------------------|---------------------------------------------------|------------------------------------------------------------------------------|---------------------------------------------------------------|--------------------------------------------|
| 2.1   | UI Interaction                | static/js/staging-editor-tab.js                   | User selects rows, sets status, triggers update                              | API Std ([Guide](../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md)), Feedback | Verify JS details                         |
| 2.2   | API Routing: JWT Auth         | src/routers/places_staging.py [NOVEL]             | JWT auth at router only                                                      | Auth Boundary ([Guide](../Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md))      | Uses src/auth/jwt_auth.py                 |
| 2.3   | API Routing: Validation/ENUM  | src/routers/places_staging.py [NOVEL], src/models/api_models.py [SHARED] | Validates input, checks ENUMs                                                | API Std, Enum Handling, Conn Mgmt, Txn Boundary, Code Org, UUID Std             | ENUMs in api_models.py                    |
| 2.4   | API Routing: Delegation       | src/routers/places_staging.py [NOVEL]             | Delegates to service or inline logic                                         | Delegation, Code Org                                                         | Service preferred, else inline            |
| 2.5   | Service: Status Update Logic  | src/services/places_staging_service.py [SHARED]   | Validates, cleans, orchestrates status update                                | Validation, Enum Handling, Error Handling, Code Org, ORM Req                    | Centralizes logic, uses ORM               |
| 2.6   | Service: Dual-Status Update   | src/services/places_staging_service.py [SHARED], src/models/place.py [SHARED] | Updates place.status, deep_scan_status with ORM                               | ORM Req ([Guide](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)), Error Handling | Batch ops, error logging                  |
| 2.7   | Bg Task: Queue Trigger        | src/services/places_staging_service.py [SHARED]   | Setting deep_scan_status = 'Queued' triggers scheduler                       | Decoupling, Atomicity                                                         | Status-based queuing                      |
| 2.8   | Bg Task: Scheduler Poll       | src/services/sitemap_scheduler.py [SHARED], src/scheduler_instance.py [SHARED] | Polls for queued jobs, schedules work                                        | Bg Task Pattern, Conn Mgmt, Txn Boundary, ORM Req, Code Org, Error Handling      | Scheduler delegates to PlacesDeepService  |
| 2.9   | Bg Task: Deep Scan Execution  | src/services/places_deep_service.py [SHARED]      | Processes deep scan, updates Place                                           | Bg Task Pattern, Txn Boundary, ORM Req                                         | ORM only, logs progress/errors            |
| 2.10  | DB Models: Place              | src/models/place.py [SHARED]                      | Defines ORM model for Place                                                  | ORM Req ([Guide](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)), Code Org  | Models match DB, enums in place.py        |
| 2.11  | ENUM Handling                 | src/models/place.py [SHARED], src/models/api_models.py [SHARED] | Enum classes for Place/DeepScanStatus fields                                 | Enum Handling, Validation, Code Org                                            | Enum validation in router/service         |
| 2.12  | Config: Scheduler Settings    | docker-compose.yml, src/config/settings.py         | Scheduler interval, batch size, max instances                                | Secure Config, Code Org                                                        | Use env vars, never hardcode              |
