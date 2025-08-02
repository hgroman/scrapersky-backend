# Layer 4: Services & Schedulers - Architectural Blueprint

**Version:** 3.0 - CONSOLIDATED
**Date:** 2025-08-01
**Consolidated From:**

- `v_1.0-ARCH-TRUTH-Definitive_Reference.md` (Core architectural principles & background processing)
- `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Master naming conventions & structural patterns)
- `v_1.0-ARCH-TRUTH-Layer4-Services-Schedulers-Excerpt.md` (Layer-specific implementation details)
- `Docs/CONSOLIDATION_WORKSPACE/Layer4_Services/v_Layer-4.1-Services_Blueprint.md` (Detailed Layer 4 conventions)
- `Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Foundational naming patterns)

**Contextual References:**

- `Docs/Docs_6_Architecture_and_Status/3.0-ARCH-TRUTH-Layer_Classification_Analysis.md` (Provides historical examples of Layer 4 components)

---

## Preamble: Relation to Core Architectural Principles

The standards herein for Layer 4 directly support and implement the Core Architectural Principles outlined in `1.0-ARCH-TRUTH-Definitive_Reference.md`, particularly those related to Database Access, Standardized Background Processing, and Layered Architectural Awareness. This Blueprint translates those high-level principles into specific, auditable criteria for services and schedulers.

---

## 1. Core Principles: Business Logic & Background Processing

Layer 4 is designated as the "Business Logic & Background Processing" layer. Its core principles are:

- **Separation of Concerns**: Business logic isolated from API routing and data access primitives
- **Transaction Awareness**: Services are transaction-aware but NEVER create transactions (routers own transaction boundaries)
- **Status-Driven Workflows**: Producer-consumer pattern driven by status changes
- **Standardized Background Processing**: Single shared APScheduler instance for all background tasks
- **Session Management**: Services accept session parameters, schedulers manage their own sessions
- **External System Integration**: Centralized interaction with external APIs and services

---

## 2. Standard Pattern: Dedicated Service Layer

This is the **preferred and most common pattern** for implementing workflow logic.

### 2.1. Definition & Scope

- **Purpose:** Services encapsulate the core business logic, complex data manipulations, state management, and coordination of tasks for a specific workflow or a cohesive set of functionalities.
- **File Naming (Strict Convention):**
  - Core processing logic for a workflow: `src/services/{workflow_name}_service.py`
  - Scheduler logic for a workflow: `src/services/{workflow_name}_scheduler.py`
- **Responsibilities:**
  - Implementing business rules and algorithms.
  - Orchestrating calls to other services or data access layers (if any beyond direct ORM use).
  - Managing complex state transitions for workflow entities.
  - Implementing and managing status-driven workflow logic (as per `1.0-ARCH-TRUTH-Definitive_Reference.md`).
  - Interacting with external APIs (e.g., Google Places API).
  - Enqueueing tasks for background processing.

### 2.2. Key Compliance Criteria for Dedicated Services

- **Session Handling:**
  - Must accept an `AsyncSession` object as a parameter from the calling layer (typically a router or another service).
  - Must **NOT** create its own database sessions for routine operations (e.g., no `get_session()` calls that initiate a new session with `session_scope()` or similar).
  - **Exception for Schedulers:** Top-level functions in `{workflow_name}_scheduler.py` (e.g., `process_{workflow_name}_queue()`) that serve as entry points for background tasks **MUST** use `get_background_session()` to create and manage their own session lifecycle.
- **Transaction Management:**
  - Must be transaction-aware but generally should **NOT** manage transaction boundaries (commit/rollback) themselves.
  - Transaction management is typically handled by the calling router (for API-initiated actions) or the top-level background task function within a scheduler.
- **ORM Usage (No Raw SQL):**
  - **MUST** use SQLAlchemy ORM for all database interactions.
  - **NO raw SQL strings** (e.g., `session.execute(text("SELECT ..."))`).
  - For DML (updates, deletes, inserts): Use ORM object manipulation (fetch, modify attributes, `session.add()`, `session.delete()`). Direct execution of SQLAlchemy Core DML constructs (e.g., `session.execute(update(Model)...)`) should be avoided in services and is considered technical debt (potential SCRSKY-225).
- **Tenant ID Isolation:**
  - Complete removal of all `tenant_id` parameters and filtering logic.
- **Configuration & Hardcoding:**
  - No hardcoded business-critical values (API keys, thresholds, etc.). Use `settings` object.
  - Correct import pattern for settings: `from ..config.settings import settings`.
- **Error Handling:**
  - Robust `try...except` blocks for external calls and complex operations.
  - Adequate logging of errors.
  - Clear error propagation strategy.
- **Function Naming & Structure (refer to Q&A Insights for details):**
  - Processing services: `process_single_{source_table_name}_for_{workflow_name}`.
  - Scheduler jobs: `process_{workflow_name}_queue()`.
  - Clear type hints and docstrings.
  - Separation of processing logic from scheduling logic.
- **Scheduler Specifics (for `{workflow_name}_scheduler.py`):**
  - Dedicated file per workflow (Absolute Rule).
  * `setup_{workflow_name}_scheduler()` function for registration in `main.py`.
  * Use `run_job_loop` helper for standard polling patterns.
  * Job parameters (interval, batch size) read from `settings`.

---

## 3. Documented Exception: Router-Handled CRUD & Dual-Status Updates

As per `Q&A_Key_Insights.md` (Layer 3: Routers), a specific pattern is acknowledged where routers can directly handle certain types of contained business logic. This is an **exception** to the general rule of placing all business logic in services and applies under specific conditions.

### 3.1. Definition & Scope

- **Purpose:** For workflows tightly coupled to a single primary entity, where the main "workflow" interactions involve direct CRUD operations on that entity and synchronous dual-status updates triggered by user actions via the API.
- **File Naming (from Q&A):** `src/routers/{workflow}_CRUD.py`. This naming explicitly signals the router's dual role.
- **Responsibilities (within the router function):**
  - Handling basic CRUD API endpoints for the primary entity.
  - Implementing the "Synchronous Secondary State Update" pattern (as described in `Docs/Docs_5_Project_Working_Docs/10-LAYER5_architectural-patterns/5-SYNCHRONOUS-SECONDARY-STATE-UPDATE-PATTERN.md`), where a primary status update triggers a conditional secondary status update within the same transaction.
  - Example: An endpoint that allows a user to set a record's `curation_status` to "Selected", which then synchronously sets its `processing_status` to "Queued".

### 3.2. Key Compliance Criteria for `{workflow}_CRUD.py` Routers (when implementing this pattern)

- **Bounded Logic:** The business logic within the router **MUST** be strictly confined to the CRUD operations and the immediate, synchronous dual-status update for that router's primary entity.
  - If logic becomes more complex (e.g., multi-step processing beyond the dual-status update, significant interaction with other models/services, calls to external APIs not directly related to the entity), it **MUST** be refactored into a dedicated service.
- **Session Handling:**
  - Router endpoint functions handling these operations will typically receive the `AsyncSession` via dependency injection.
  - They **WILL manage the transaction boundary** for the operations they contain (e.g., using `async with session.begin():`). This is different from routers that call separate services (where the service is transaction-aware but the router might still own the transaction overall for that request).
- **ORM Usage (No Raw SQL):**
  - **MUST** use SQLAlchemy ORM for all database interactions.
  - **NO raw SQL strings.**
  - For DML: Prefer ORM object manipulation. If SQLAlchemy Core DML constructs are used (e.g. `session.execute(update(Model)...)`), this should be for simple, direct updates related to the dual-status pattern. Complex conditional logic should ideally still use fetched ORM objects.
- **Tenant ID Isolation:**
  - Complete removal of all `tenant_id` parameters and filtering logic.
- **Configuration & Hardcoding:**
  - No hardcoded values. Use `settings` object.
- **Error Handling:**
  - Robust `try...except` blocks.
  - Adequate logging.
- **Function Naming (from Q&A):**
  - Status updates: `update_{workflow}_status_batch`.
  - CRUD operations: Standard `create_{entity}`, `get_{entity}`, etc.

---

## 4. Audit & Assessment Guidance

**Core Philosophy:** The primary goal of this audit is to identify **all deviations from the ideal architectural standards** defined in this Blueprint (Sections 2 and 3), thereby cataloging technical debt. While existing, functional code ("Code is King") is acknowledged as the current reality, this assessment measures it against the defined ideal to guide future refactoring efforts.

When auditing Layer 4 components:

1.  **Identify Implemented Pattern:** Determine if the workflow's core logic _currently_ most closely aligns with the **Standard Pattern (Dedicated Service Layer - Section 2)** or the **Exception Pattern (Router-Handled CRUD & Dual-Status Updates - Section 3)**. Reference `v_4_PATTERN_COMPARISON.yaml` or router/service filenames (e.g., `{workflow}_CRUD.py`) for this initial classification of the _current state_.

2.  **Assess Against Ideal & Specific Criteria:**

    - **If Ideal is Standard Pattern (Section 2):**
      - If current implementation _is_ Pattern A (Dedicated Service): Assess directly against criteria in Section 2.2. Deviations are technical debt.
      - If current implementation _is_ Pattern B (Router-Handled): This itself is a deviation from the ideal. Log this primary deviation. Then, _additionally_ assess the existing router logic against the specific criteria for Pattern B (Section 3.2) to identify further internal technical debt within that chosen pattern (e.g., logic exceeding scope, raw SQL).
    - **If Ideal allows for Exception Pattern (Section 3 for specific, bounded cases):**
      - If current implementation _is_ Pattern B (Router-Handled) AND it _meets all criteria_ in Section 3.2 (including bounded logic): This is compliant with the documented exception. No primary architectural technical debt, but ensure all sub-criteria are met.
      - If current implementation _is_ Pattern B BUT it _violates any criteria_ in Section 3.2 (e.g., logic exceeds bounded scope): This is technical debt. The primary gap is the violation of the exception's own rules.

3.  **Document Technical Debt:** For **any deviation** from the ideal standard (Section 2) or from the specific compliance criteria of a chosen pattern (Section 2.2 or 3.2), clearly document this in the "Gap Analysis" of the relevant cheat sheet. This includes:

    - Noting when the Router-Handled pattern is used where the Dedicated Service is the ideal.
    - Noting when a Router-Handled implementation exceeds its defined boundaries (Section 3.1, 3.2).
    - Noting all violations of specific compliance points (e.g., no raw SQL, session handling) for the implemented pattern.

4.  **Prescribe Refactoring Actions:** Based on the identified gaps, suggest refactoring actions. These actions should aim to move the component towards the ideal standard over time, prioritizing critical deviations (like raw SQL or unbounded router logic) first.

---
