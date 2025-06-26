# Layer 4 Audit Report: WF3-LocalBusinessCuration

**Workflow Audited:** WF3-LocalBusinessCuration
**Date of Audit:** 2025-05-20
**Auditor:** Cascade (AI Agent)

---

## 1. Files Audited

- `src/routers/local_businesses.py` (acting as primary logic handler)
- `MISSING: src/services/local_business_curation_service.py` (dedicated workflow service)
- `MISSING: src/services/local_business_curation_scheduler.py` (dedicated workflow scheduler)

---

## 2. Consolidated Summary of Findings

The Layer 4 implementation for `WF3-LocalBusinessCuration` primarily resides in `src/routers/local_businesses.py`, with **no dedicated workflow-specific service or scheduler files**. This is the main deviation from the `Layer-4-Services_Blueprint.md` which advocates for a Dedicated Service Layer (Pattern A) for business logic and schedulers for background tasks.

The existing router (`local_businesses.py`) implements logic for listing and batch-updating local businesses. While it correctly uses SQLAlchemy ORM and proper session dependency, its `list_local_businesses` endpoint contains dynamic filtering and sorting logic that **likely exceeds the 'simple CRUD' operations** intended for Pattern B (Router-Handled CRUD & Dual-Status Updates) routers.
The batch update endpoint correctly handles dual-status updates (`status` and `domain_extraction_status`), aligning with Pattern B's intent for such specific operations.

**Key Blueprint Violations and Technical Debt:**

1.  **Missing Dedicated Service:** The absence of `local_business_curation_service.py` means business logic (especially the complex listing query) is not encapsulated in a reusable, testable service layer (violates Blueprint Section 2.1.A).
2.  **Missing Dedicated Scheduler:** The `domain_extraction_status` implies a background process, but `local_business_curation_scheduler.py` is missing. This violates the 'Dedicated file per workflow' rule for schedulers if this workflow owns that background task (Blueprint Section 2.2.D.1).
3.  **Router Scope:** The `list_local_businesses` endpoint in `local_businesses.py`, with its dynamic sorting and multiple filter conditions, likely exceeds the intended scope for Pattern B routers (Blueprint Section 3.2.A).
4.  **Hardcoded Default Tenant ID:** `local_businesses.py` uses a hardcoded default tenant ID as a fallback, which is a compliance issue if not an approved system-wide default (Blueprint Section 2.2.B.1).
5.  **Transaction Management:** Without a dedicated service layer managing units of work, transaction boundaries for more complex operations are not explicitly controlled by a service.

---

## 3. Detailed Findings per File (Referencing `WF3-LocalBusinessCuration_Cheat_Sheet.md`)

### 3.1 `MISSING: src/services/local_business_curation_service.py`

*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Primary Deviation:** Absence of this file means business logic (especially complex listing queries) is not encapsulated as per Pattern A (Blueprint Section 2.1.A).
    *   Logic currently resides in `src/routers/local_businesses.py`.

### 3.2 `MISSING: src/services/local_business_curation_scheduler.py`

*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Critical Deviation:** If `WF3-LocalBusinessCuration` is responsible for processing items based on `domain_extraction_status`, the absence of a dedicated scheduler violates Blueprint Section 2.2.D.1.
    *   No standard polling pattern or registration is present for this workflow's background tasks.

### 3.3 `src/routers/local_businesses.py` (Currently handling Layer 4 logic)

*   **Implemented Pattern:** Router-Handled Logic (Pattern B).
*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Listing Logic Complexity:** The `list_local_businesses` endpoint includes dynamic sorting (on multiple fields) and filtering (including `ilike` for names), which makes its query construction logic more complex than 'simple CRUD' and likely exceeds the scope for Pattern B routers (Blueprint Section 3.2.A).
    *   **Dual-Status Update:** The `update_local_businesses_status_batch` method correctly handles the dual-status update for `domain_extraction_status` when `status` is 'Selected', aligning with Pattern B (Blueprint Section 3.2.A).
    *   **ORM & Session:** Correctly uses SQLAlchemy ORM and session dependency (Blueprint Section 3.2.C.1, 3.2.C.2).
    *   **Hardcoded Default Tenant ID:** Uses a hardcoded default `tenant_id` string as a fallback (violates Blueprint Section 2.2.B.1 if not approved system default).

---

## 4. Key Areas Requiring Attention (for Remediation Persona)

1.  **Create `src/services/local_business_curation_service.py`:** Extract business logic, especially the complex query logic from `list_local_businesses` in `local_businesses.py`, into this new service. Ensure adherence to Blueprint criteria (session passing, ORM, error handling).
2.  **Investigate & Implement `src/services/local_business_curation_scheduler.py`:**
    *   Clarify if `WF3-LocalBusinessCuration` is responsible for the background processing triggered by `domain_extraction_status`.
    *   If yes, create the scheduler file with standard queue processing, session management (`get_background_session`), and registration in `main.py`.
    *   If another workflow handles this, document the dependency clearly.
3.  **Refactor `src/routers/local_businesses.py`:**
    *   Simplify the `list_local_businesses` endpoint to delegate complex query logic to the new service.
    *   Address the hardcoded default tenant ID.
    *   The dual-status update logic in `update_local_businesses_status_batch` can remain if a hybrid Pattern B approach for this specific function is deemed acceptable and documented, or it can be moved to the service for full Pattern A alignment.
4.  **Ensure Clear Transaction Management:** Define transaction boundaries within the new service methods.
