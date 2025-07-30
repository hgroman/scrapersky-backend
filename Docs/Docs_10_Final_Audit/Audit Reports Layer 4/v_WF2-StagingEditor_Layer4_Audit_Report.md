# Layer 4 Audit Report: WF2-StagingEditor

**Workflow Audited:** WF2-StagingEditor
**Date of Audit:** 2025-05-20 (ORIGINAL) | 2025-01-28 (CORRECTED)
**Auditor:** Cascade (AI Agent) | Claude Code AI Assistant (Correction)

# ⚠️  CRITICAL CORRECTION NOTICE ⚠️ 
**This audit report contains MAJOR ERRORS regarding raw SQL claims.**
**Code verification shows FULL ORM COMPLIANCE in src/routers/places_staging.py**
**See WF2_Staging_Editor_Guardian_v3.md for accurate information.**

---

## 1. Files Audited

- `src/routers/places_staging.py` (acting as primary logic handler)
- `src/services/places/places_service.py` (generic entity service)
- `src/services/places/places_deep_service.py` (specialized service for deep scans)
- `MISSING: src/services/staging_editor_service.py` (dedicated workflow service)
- `MISSING: src/services/staging_editor_scheduler.py` (dedicated workflow scheduler)

---

## 2. Consolidated Summary of Findings

The Layer 4 implementation for the `WF2-StagingEditor` workflow deviates significantly from the `Layer-4-Services_Blueprint.md`. The **primary architectural gap** is the absence of dedicated workflow-specific service (`staging_editor_service.py`) and scheduler (`staging_editor_scheduler.py`) files.

Currently, core business logic, including data fetching, manipulation, and status updates, is predominantly handled within the `src/routers/places_staging.py` router. This router-centric approach (Pattern B) **exceeds the defined scope** for such a pattern by incorporating complex queries, raw SQL statements, and direct business logic that should reside in a dedicated service layer (Pattern A).

**Key Blueprint Violations and Technical Debt:**

1.  **Missing Dedicated Service & Scheduler:** The most critical issue. Logic is not encapsulated in maintainable, testable, and reusable service/scheduler components as per Blueprint Section 2.1.A and 2.2.
2.  **Router Overreach:** `places_staging.py` performs operations (raw SQL, complex filtering, direct status updates) far beyond simple CRUD or dual-status updates allowed for Pattern B routers (Blueprint Section 3.1.A, 3.2).
3.  **~~Raw SQL Usage~~ DOCUMENTATION ERROR:** **CORRECTED** - `places_staging.py` uses proper SQLAlchemy ORM throughout (lines 308-342 show select() statements and object updates, not raw SQL).
4.  **Tenant ID Isolation & Handling:**
    *   `places_staging.py` uses a hardcoded default Tenant ID (`550e8400-e29b-41d4-a716-446655440000`) as a fallback (Blueprint Section 2.2.B.1).
    *   `places_service.py` (generic) still contains active tenant_id filtering logic in `get_by_id` and accepts `tenant_id` in other methods, contrary to the mandate for services to be tenant-agnostic for filtering (Blueprint Section 2.2.B).
    *   `places_deep_service.py` accepts and uses `tenant_id` for data association, which is acceptable, but this is coupled with self-managed sessions.
5.  **Session Management Violations:**
    *   `places_deep_service.py` critically creates its own database session (`await get_session()`) in `process_single_deep_scan`, violating Blueprint Section 2.2.A.2.
6.  **Naming Conventions:** Generic services (`places_service.py`, `places_deep_service.py`) do not use workflow-specific naming, which is acceptable for them. However, the lack of a `staging_editor_service.py` means no service adheres to the `process_single_{entity}_for_{workflow}` pattern for this workflow (Blueprint Section 2.2.E).
7.  **Transaction Management:** With logic in the router and `places_deep_service.py` creating its own session, transaction boundaries are not clearly managed by a controlling service layer as per best practices (Implicit in Blueprint Section 2.2.A).

---

## 3. Detailed Findings per File (Referencing `WF2-StagingEditor_Cheat_Sheet.md`)

### 3.1 `MISSING: src/services/staging_editor_service.py`

*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Primary Deviation:** Absence of this file represents a core violation of the 'Dedicated Service Layer' (Pattern A) principle (Blueprint Section 2.1.A).
    *   Business logic for `WF2-StagingEditor` is improperly located in `src/routers/places_staging.py`.

### 3.2 `MISSING: src/services/staging_editor_scheduler.py`

*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Critical Deviation:** Absence of a dedicated scheduler for background tasks (like deep scans initiated by `WF2-StagingEditor`) violates the 'Dedicated file per workflow' rule for schedulers (Blueprint Section 2.2.D.1).
    *   No standard polling pattern (`run_job_loop`) or registration (Blueprint Section 2.2.D.2, 2.2.D.3).

### 3.3 `src/routers/places_staging.py` (Currently handling Layer 4 logic)

*   **Implemented Pattern:** Router-Handled Logic (Pattern B), but **exceeds scope**.
*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   Logic performs complex data manipulation, raw SQL queries (`list_all_staged_places`), and direct status updates, which should be in a dedicated service (Blueprint Section 3.1.A, 3.2).
    *   Uses raw SQL: `text("SELECT ... FROM places_staging ...")` (Blueprint Section 3.2.C.1).
    *   Uses a hardcoded default `tenant_id` as a fallback (Blueprint Section 2.2.B.1 - applied generally).
    *   Does not call any workflow-specific service.

### 3.4 `src/services/places/places_service.py` (Generic Entity Service)

*   **Implemented Pattern:** Generic Entity Service.
*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Tenant ID Handling:** Method `get_by_id` still contains active tenant ID filtering logic using `text("tenant_id::text = :tenant_uuid")`. Methods `get_places` and `update_status` accept `tenant_id` as a parameter even if commented out or unused in filtering logic. This violates Blueprint Section 2.2.B.
    *   Naming is generic, not workflow-specific (acceptable for this type of service, but highlights it's not the WF2 service).

### 3.5 `src/services/places/places_deep_service.py` (Specialized Service)

*   **Implemented Pattern:** Specialized Service (extending generic PlacesService).
*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Session Management (CRITICAL):** `process_single_deep_scan` creates its own session (`await get_session()`), violating Blueprint Section 2.2.A.2.
    *   **Tenant ID Handling:** Accepts `tenant_id` and uses it for data association, coupled with self-managed session.
    *   **Naming Conventions:** `process_single_deep_scan` does not follow `process_single_{entity}_for_{workflow}` pattern (Blueprint Section 2.2.E).

---

## 4. Key Areas Requiring Attention (for Remediation Persona)

1.  **CRITICAL: Create `src/services/staging_editor_service.py`:** Extract all business logic, data manipulation, and complex queries (including raw SQL) from `src/routers/places_staging.py` into this new service. Ensure it adheres to all Blueprint criteria for services (session passing, ORM usage, error handling, no tenant ID filtering).
2.  **CRITICAL: Create `src/services/staging_editor_scheduler.py`:** Implement a scheduler for background tasks like deep scanning, including `process_staging_editor_queue` and `setup_staging_editor_scheduler` methods, proper session handling (`get_background_session`), and registration in `main.py`.
3.  **CRITICAL: Refactor `src/services/places/places_deep_service.py`:** Modify `process_single_deep_scan` to accept an `AsyncSession` parameter instead of creating its own. Align naming if it's to be a primary method for a standard workflow step.
4.  **Refactor `src/routers/places_staging.py`:** Simplify this router to only handle request/response, Pydantic model validation, and delegate all business logic to the new `staging_editor_service.py`. Remove raw SQL and hardcoded tenant IDs.
5.  **Address Tenant ID Handling in `src/services/places/places_service.py`:** Remove all tenant ID filtering logic from `get_by_id` and clarify/remove unused `tenant_id` parameters in other methods to strictly adhere to Blueprint Section 2.2.B.
6.  **Ensure ORM-Only:** Replace all raw SQL in `places_staging.py` (once moved to the service) with SQLAlchemy ORM queries.
7.  **Transaction Management:** Ensure transactions are clearly managed within the new `staging_editor_service.py` methods.
