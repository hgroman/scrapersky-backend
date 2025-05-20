# Layer 4 Audit Report: WF4-DomainCuration

**Workflow Audited:** WF4-DomainCuration
**Date of Audit:** 2025-05-20
**Auditor:** Cascade (AI Agent)

---

## 1. Files Audited

- `src/routers/domains.py` (acting as primary logic handler for WF4)
- `MISSING: src/services/domain_curation_service.py` (dedicated workflow service for WF4)
- `src/services/domain_scheduler.py` (existing general domain scheduler, **not** for WF4's `sitemap_analysis_status`)
- `MISSING: src/services/domain_curation_scheduler.py` (dedicated workflow scheduler for WF4's `sitemap_analysis_status` queue)

---

## 2. Consolidated Summary of Findings

The Layer 4 implementation for `WF4-DomainCuration` relies on `src/routers/domains.py` for its primary logic. There is **no dedicated `domain_curation_service.py`**. Furthermore, while a `domain_scheduler.py` exists, it services a general domain processing lifecycle based on `Domain.status` and **does not handle the `sitemap_analysis_status` queue specific to `WF4-DomainCuration`**. Thus, `WF4-DomainCuration` effectively **lacks its own dedicated scheduler** for its background tasks.

`src/routers/domains.py` implements logic for listing and batch-updating domain sitemap curation statuses. It correctly uses SQLAlchemy ORM and session dependency. Notably, it does not perform explicit tenant_id filtering, which aligns with potential global nature of `Domain` entities or RLS-based/removed tenant isolation (Memory `50f678e2-3197-40c2-8bd7-45f7b4d08098`). The router's `list_domains` endpoint, with dynamic sorting via a map and multiple filter conditions, **likely exceeds the 'simple CRUD' operations** intended for Pattern B routers. The batch update endpoint correctly handles dual-status updates (`sitemap_curation_status` and `sitemap_analysis_status`), aligning with Pattern B.

**Key Blueprint Violations and Technical Debt for WF4-DomainCuration:**

1.  **Missing Dedicated Service (`domain_curation_service.py`):** Business logic (especially complex listing query) is not encapsulated (violates Blueprint Section 2.1.A).
2.  **Missing Dedicated Scheduler (`domain_curation_scheduler.py`):** The workflow's `sitemap_analysis_status` queue is not processed by any existing scheduler, representing a critical functional gap for its dual-status design (violates Blueprint Section 2.2.D.1).
3.  **Router Scope (`domains.py`):** The `list_domains` endpoint's complexity exceeds Pattern B scope (Blueprint Section 3.2.A).
4.  **Transaction Management:** Implicit transaction boundaries in the router for complex operations instead of explicit service-layer management.

---

## 3. Detailed Findings per File (Referencing `WF4-DomainCuration_Cheat_Sheet.md`)

### 3.1 `MISSING: src/services/domain_curation_service.py`

*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Primary Deviation:** Absence means business logic (complex listing) is not encapsulated per Pattern A (Blueprint Section 2.1.A).
    *   Logic currently in `src/routers/domains.py`.

### 3.2 `MISSING: src/services/domain_curation_scheduler.py` (for `sitemap_analysis_status`)

*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Critical Deviation:** `WF4-DomainCuration`'s background processing queue (domains with `sitemap_analysis_status = QUEUED`) is not serviced. This breaks the workflow's intended dual-status processing flow (Blueprint Section 2.2.D.1).

### 3.3 `src/routers/domains.py` (Handles WF4 Layer 4 logic)

*   **Implemented Pattern:** Router-Handled Logic (Pattern B).
*   **Gap Analysis (from Cheat Sheet & Blueprint):**
    *   **Listing Logic Complexity:** `list_domains` endpoint (dynamic sort map, multiple filters) exceeds Pattern B scope (Blueprint Section 3.2.A).
    *   **Dual-Status Update:** `update_domain_sitemap_curation_status_batch` correctly handles dual-status update for `sitemap_analysis_status`, aligning with Pattern B (Blueprint Section 3.2.A).
    *   **ORM & Session:** Correctly uses SQLAlchemy ORM and session dependency (Blueprint Section 3.2.C.1, 3.2.C.2).
    *   **Tenant ID:** No explicit `tenant_id` filtering observed. This is an observation in line with potential architectural changes towards reduced application-layer tenant filtering for certain entities.

### 3.4 `src/services/domain_scheduler.py` (Existing General Scheduler)

*   **Assessment:** This scheduler is **not for `WF4-DomainCuration`'s specific needs.**
    *   It processes domains based on `Domain.status` and `DomainStatusEnum`.
    *   It does **not** query or act upon `Domain.sitemap_analysis_status` or `SitemapAnalysisStatusEnum`.
    *   **Compliance (as a general scheduler):** Adheres to Blueprint for session management (`get_background_session()`) and registration (shared `scheduler_instance`). Its generic name `domain_scheduler.py` is acceptable if it's a general utility.

---

## 4. Key Areas Requiring Attention (for Remediation Persona for WF4-DomainCuration)

1.  **Create `src/services/domain_curation_service.py`:** Extract business logic, especially the complex query logic from `list_domains` in `src/routers/domains.py`, into this new service. Ensure adherence to Blueprint criteria (session passing, ORM, error handling).
2.  **Create `src/services/domain_curation_scheduler.py`:** This is a **critical new file**. Implement logic to:
    *   Query for domains where `sitemap_analysis_status == SitemapAnalysisStatusEnum.QUEUED`.
    *   Perform the sitemap analysis/extraction task.
    *   Update `sitemap_analysis_status` to `PROCESSING`, then `COMPLETED` or `ERROR` (using `SitemapAnalysisStatusEnum`).
    *   Use `get_background_session()` and register with the shared `scheduler_instance` in `main.py`.
3.  **Refactor `src/routers/domains.py`:** Simplify `list_domains` to delegate to the new service. The dual-status update logic in `update_domain_sitemap_curation_status_batch` can remain if Pattern B is partially retained for this specific function (and documented), or move to the service.
4.  **Ensure Clear Transaction Management:** Define transaction boundaries within the new service methods.
