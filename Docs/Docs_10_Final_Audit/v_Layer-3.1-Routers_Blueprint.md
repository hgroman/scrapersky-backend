# Layer 3: Routers - Architectural Blueprint

**Version:** 2.0 - CONSOLIDATED
**Date:** 2025-08-01
**Consolidated From:**

- `v_1.0-ARCH-TRUTH-Definitive_Reference.md` (Core architectural principles & transaction management)
- `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Master naming conventions & structural patterns)
- `Docs/CONSOLIDATION_WORKSPACE/Layer3_Routers/v_Layer-3.1-Routers_Blueprint.md` (Layer-specific implementation details & technical debt)
- `Docs/CONSOLIDATION_WORKSPACE/Layer3_Routers/v_Layer-3.1-Routers_Blueprint.md` (Detailed Layer 3 conventions)
- `Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Foundational naming patterns)

**Contextual References:**

- `Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` (Structural template, example of exception pattern documentation)
- `Docs/Docs_10_Final_Audit/Layer-1-Models_Enums_Blueprint.md` (For context on data layer)
- `Docs/Docs_10_Final_Audit/Layer-2-Schemas_Blueprint.md` (For context on API contracts)
- Current codebase (`src/routers/`)

---

## Preamble: Relation to Core Architectural Principles

The standards herein for Layer 3 directly support and implement the Core Architectural Principles outlined in `1.0-ARCH-TRUTH-Definitive_Reference.md`, particularly:

- **Strict Database Access Patterns:** By defining the router's role in initiating transaction boundaries.
- **Authentication Simplification:** By designating routers as the primary location for authentication checks.
- **API Standardization:** By enforcing consistent endpoint naming, versioning, and request/response handling.
- **Layered Architectural Awareness:** By defining the router's responsibility as the entry point and delegator to lower layers.

This Blueprint translates those high-level principles into specific, auditable criteria for FastAPI routers and endpoints.

---

## 1. Core Principle(s) for Layer 3: API Endpoint Definition & Request Handling

Layer 3 is designated as the "API Endpoints" layer. Its core principles are:

- **Define Endpoints:** To serve as the entry point for all API requests, defining paths, HTTP methods, and expected request/response formats.
- **Request Routing & Validation:** To route incoming requests to the appropriate handler function and leverage Layer 2 Schemas for request validation.
- **Transaction Management:** To **initiate and manage** the database transaction lifecycle for requests requiring database interaction.
- **Authentication & Authorization:** To enforce authentication and basic authorization checks at the API boundary.
- **Delegation:** To delegate core business logic processing to Layer 4 (Services) or Layer 5 (Configuration/Utilities) components.

---

## 2. Standard Pattern: FastAPI Routers & Endpoints

This is the **primary and ideal pattern** for defining API endpoints in Layer 3.

### 2.1. Definition & Scope

- **Purpose:** To define API routes, handle incoming HTTP requests, manage transactions, enforce authentication, validate input/output using Layer 2 Schemas, and delegate business logic to Layer 4.
- **Location & File Naming (Conventions from `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 4):**
  - **Router Files:** `src/routers/{entity_or_group_name}.py` (plural or descriptive snake_case). Example: `src/routers/pages.py`, `src/routers/users.py`, `src/routers/auth.py`.
  - **Router Instantiation:** Typically `router = APIRouter(prefix="/api/v3/{entity_plural}", tags=["{Entity TitleCase}"])`.
- **Responsibilities:**
  - Defining endpoints using `@router.<method>` decorators (e.g., `@router.post("/")`).
  - Specifying request (`body`, `Query`) and response (`response_model`) types using Layer 2 Schemas.
  - Injecting dependencies using `Depends()`, especially the database session (`db: AsyncSession = Depends(get_db)`).
  - **Initiating database transactions** using `async with db.begin():` for operations involving database writes/updates coordinated across Layer 4 calls.
  - Handling HTTP exceptions (`HTTPException`) for errors detected at the router level (e.g., authentication failures, not found).
  - Calling Layer 4 service functions to execute business logic.
  - Implementing authentication dependencies (`Depends(get_current_active_user)`).

### 2.2. Key Compliance Criteria for Layer 3 Components (Standard Pattern)

These criteria are primarily derived from `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Section 4), `1.0-ARCH-TRUTH-Definitive_Reference.md`, and FastAPI best practices.

- **Naming & Location:**
  1.  **File Name:** Must be `src/routers/{entity_or_group_name}.py` (plural/descriptive snake_case).
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
  2.  **Router Variable Name:** Typically `router`.
  3.  **Prefix:** Must follow `/api/v{version_number}/{entity_plural}` pattern (e.g., `/api/v3/pages`).
      - _Source:_ `1.0-ARCH-TRUTH-Definitive_Reference.md` (API Standardization)
  4.  **Tags:** Should be meaningful and consistently named (e.g., `tags=["Pages"]`).
- **Endpoints:**
  1.  Use appropriate HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`).
  2.  Path parameters should be clearly defined (e.g., `/{page_id}`).
  3.  Use `response_model` with the correct Layer 2 `Read` schema for responses.
  4.  Use explicit Layer 2 schemas for request bodies (`body: EntityCreate`) and query parameters (`params: EntityFilterParams = Depends()`).
  5.  Function names should clearly describe the action (e.g., `async def create_page(...)`).
- **Dependencies & Session Management:**
  1.  Database sessions **MUST** be injected using the standard dependency `db: AsyncSession = Depends(get_db)`.
      - _Source:_ `1.0-ARCH-TRUTH-Definitive_Reference.md` (Strict Database Access Patterns)
  2.  **Routers are responsible for initiating transactions** for write operations. Use `async with db.begin():` block. The `db.commit()` and `db.rollback()` should generally not be called explicitly within the router endpoint, as the `async with db.begin():` handles this.
      - _Source:_ `1.0-ARCH-TRUTH-Definitive_Reference.md` (Transaction Responsibility Pattern)
  3.  Layer 4 services **MUST** be called with the session obtained via dependency injection (`await service_function(db=db, ...)`).
- **Authentication & Authorization:**
  1.  Endpoints requiring authentication **MUST** include the standard authentication dependency (e.g., `current_user: UserRead = Depends(get_current_active_user)`).
      - _Source:_ `1.0-ARCH-TRUTH-Definitive_Reference.md` (Authentication Simplification)
  2.  Basic authorization checks (e.g., checking a user role if simple) can occur in the router, but complex permission logic belongs in Layer 4.
- **Logic & Delegation:**
  1.  **Routers MUST NOT contain complex business logic.** This belongs in Layer 4.
  2.  Router endpoint functions should primarily orchestrate: validating input (via schemas), starting transactions, calling service functions, handling router-level exceptions, and formatting the response (via `response_model`).
- **Error Handling:**
  1.  Use `fastapi.HTTPException` for errors originating or caught at the router level (auth errors, validation errors not caught by Pydantic, resource not found before calling service).
  2.  Business logic errors raised from Layer 4 should generally be allowed to propagate up unless specific HTTP status codes are needed.
- **Docstrings:**
  1.  Router endpoint functions should have docstrings explaining their purpose, parameters, and potential exceptions, aiding OpenAPI documentation.

---

## 3. Critical Implementation Context

### 3.1. Transaction Management Architecture

**Core Principle**: "Routers own transaction boundaries, services are transaction-aware but do not create transactions"

**Router Transaction Ownership**:
- Routers **MUST** own transaction boundaries using `async with session.begin()`
- Ensures atomicity of operations spanning multiple service calls
- Services accept session parameters but never create transactions
- Background tasks create their own sessions and manage transactions independently

**Standard Transaction Pattern**:
```python
@router.put("/status")
async def update_status_batch(
    request: BatchStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user)
):
    async with db.begin():
        result = await service_function(db=db, request=request)
        return result
```

### 3.2. Authentication & Authorization Boundaries

**JWT Authentication**:
- JWT authentication happens **ONLY** at API gateway endpoints (Layer 3)
- Database operations **NEVER** handle JWT or tenant authentication
- **No tenant isolation** across the system (completely removed)
- Authentication boundaries enforced at router layer, not services

**Standard Authentication Pattern**:
- Use `current_user: UserRead = Depends(get_current_active_user)` for authenticated endpoints
- Basic authorization checks can occur in router for simple role checks
- Complex permission logic belongs in Layer 4 services

### 3.3. API Versioning & Standardization

**Version Prefix**: All endpoints use `/api/v3/` prefix
- **Applied at**: Application level in `main.py` or parent router inclusion
- **Consistency**: Uniform versioning across all endpoints
- **Technical Debt**: Some endpoints still using `/v1/` prefix (non-compliant)

**Endpoint Naming Standards**:
- RESTful conventions with proper HTTP methods
- Dedicated endpoints for bulk operations (batch status updates)
- Query parameters for filtering, not path parameters
- Path parameters only for resource identifiers

### 3.4. Current Architecture Status

- **Compliance Level**: ~82% compliant with architectural standards
- **Reference Implementation**: `src/routers/google_maps_api.py` for transaction patterns
- **Error Handling**: FastAPI native error handling (custom ErrorService removed)
- **Response Structure**: Consistent response formatting across all endpoints

### 3.5. Known Technical Debt

- **API Versioning**: Some endpoints using outdated `/v1/` prefix
- **Transaction Boundaries**: Inconsistent implementation in older routers
- **Endpoint Paths**: Inconsistent path patterns in legacy routers
- **Function Naming**: Existing functions not following strict shortening rules
- **Authentication Documentation**: Some boundary documentation needs updates

---

## 4. Documented Exception Pattern(s)

(This section mirrors the structure from Layer 4's Blueprint, adapting it for Layer 3. Define any allowed, documented deviations here.)

Based on current documentation, there might be scenarios where simple CRUD operations that only involve direct interaction with a single model (and minimal logic) could potentially bypass a dedicated Layer 4 service function call, with the logic residing directly in the router. This requires careful consideration and should be explicitly documented if allowed.

### 3.1. Exception Pattern: Router-Handled Simple CRUD (Hypothetical - Needs Verification in Source Docs)

- **Definition & Scope:** Applies only to extremely simple Create, Read (single or list with basic filtering), Update (full), or Delete operations involving a single Layer 1 model, with **no significant business logic**, no interaction with other services/models, and no complex validation beyond what Layer 2 provides.
- **Responsibilities:** The router endpoint directly uses the injected `db` session and Layer 1 model operations (e.g., `db.add()`, `db.get()`, `db.delete()`, simple `select()` statements) within the standard transaction block (`async with db.begin():`).
- **Key Compliance Criteria for Exception Pattern:**
  1.  **Simplicity:** Must involve only one Layer 1 model.
  2.  **No Business Logic:** Logic must be confined to basic ORM operations.
  3.  **Standard Practices:** Must still adhere to all other Layer 3 standards (naming, auth, transaction management, schema usage, error handling).
  4.  **Bounded Scope:** Any logic beyond simple, direct ORM calls (e.g., conditional logic based on field values, calling utility functions, interacting with external systems) **violates** this exception and requires a move to the Standard Pattern (delegation to Layer 4).
- **Justification:** Potential optimization for trivial endpoints, reducing boilerplate Layer 4 functions.
- **Status:** Needs confirmation if this pattern is explicitly allowed or observed consistently and acceptably in the codebase/documentation.

---

## 4. Audit & Assessment Guidance

**Core Philosophy:** Auditing Layer 3 ensures API endpoints are correctly defined, secure, manage transactions properly, and correctly delegate business logic according to the layered architecture. Deviations represent technical debt, potentially leading to inconsistent API behavior, security vulnerabilities, or misplaced logic.

When auditing Layer 3 components (`src/routers/*.py` files):

1.  **Identify Implemented Pattern:** For each endpoint function, determine if it follows the **Standard Pattern** (delegating to Layer 4) or potentially the **Router-Handled Simple CRUD** exception pattern (if confirmed/defined).

2.  **Assess Against Ideal & Specific Criteria:**

    - **If Standard Pattern:** Check against all criteria in Section 2.2. Verify correct delegation to Layer 4, proper session passing, transaction management initiation, and absence of business logic.
    - **If Router-Handled Simple CRUD Exception Pattern (if applicable):** Check against the exception's criteria in Section 3.1. Ensure it strictly adheres to the simplicity and scope limitations. Verify it still meets general Layer 3 standards (naming, auth, schemas, etc.).

3.  **Document Technical Debt:** Clearly document deviations in the "Gap Analysis". This **MUST** include:

    - Violation of naming or location conventions.
    - Incorrect API prefix or tags.
    - Missing or incorrect `response_model` or request body/query schemas.
    - Incorrect dependency injection (especially `db` session or auth).
    - **Improper Transaction Management:** Missing `async with db.begin():` where required, or attempts to commit/rollback manually within the router.
    - **Business logic present in the router** (violates Standard Pattern).
    - Missing or incorrect authentication dependencies.
    - Use of the "Router-Handled Simple CRUD" pattern for logic exceeding its defined simple scope (requires refactoring to Standard Pattern).
    - Any other violation of criteria in Section 2.2 or Section 3.1.

4.  **Prescribe Refactoring Actions:** Suggest actions to align with the Blueprint.
    - **Prioritize fixing:** Improper transaction management, missing authentication, business logic in routers.
    - Examples:
      - "Move business logic from endpoint `X` to a new function in `src/services/y.py` and update endpoint to call the service function."
      - "Wrap database operations in endpoint `Z` with `async with db.begin():`."
      - "Add `Depends(get_current_active_user)` dependency to endpoint `A`."
      - "Refactor endpoint `B` (currently using Router-Handled CRUD inappropriately) to use the Standard Pattern with delegation to Layer 4."
      - "Add `response_model=PageRead` to endpoint `C`."

---
