# State of the Nation: ScraperSky Backend

**Date:** 2025-11-22
**Status:** CLEAN & STABLE
**Verdict:** The "Cleanup War" is Won.

---

## 1. The Executive Truth

**The codebase is clean.**

For months, we feared "ghosts" — orphan files, legacy code, and dead routers. We launched a comprehensive audit (WO-CLEANUP-001) to hunt them down.

**The Result:** We found **zero** real orphans.

Every file that looked suspicious proved to be either:
1.  **Brand New:** Created during recent standardization (e.g., `crud_base.py`).
2.  **Data-Backed:** Dormant code serving real database rows (e.g., `vector_db_ui.py` with 34 patterns).
3.  **Load-Bearing:** Critical infrastructure (e.g., `tenant.py` with 10 FK dependencies).

**The Lesson:** Stop looking for things to fix. There is no "technical debt" hiding in the file structure. The foundation is solid.

---

## 2. The Audit Verdict (Permanent Record)

*Preserved from WO-CLEANUP-001 for future reference.*

| File / Folder | What we thought | What is actually true | Verdict |
|------------------|-------------------------|-------------------------|--------|
| `crud_base.py` | “Orphan” | Written **2025-11-22** during flattening | **Keep** (New) |
| `vector_db_ui.py` | “Dead code” | Backs **34 fix-patterns** in DB | **Keep** (Data Exists) |
| `tenant.py` | “Maybe unused” | **10 Foreign Keys** depend on it | **Critical** (Do Not Touch) |
| `database_health_monitor.py` | “Unused” | Valid idea, never wired up | **Safe to delete later** |
| `storage/` folder | “Empty” | Empty | **Safe to delete later** |
| `async_session_fixed.py` | “Old fix” | Potential scheduler dependency | **Test before action** |

---

## 3. The Architecture "Now"

We have successfully transitioned from a "V2/V3" mix to a unified **V3 Standard**.

*   **Routers:** All flattened under `src/routers/`. No `v3/` subdirectories.
*   **API Prefix:** `/api/v3/` is the universal standard.
*   **Patterns:**
    *   **Dual-Status:** Curation (`Selected`) -> Processing (`Queued`).
    *   **Run Job Loop:** Standardized background processing.
    *   **Services:** Logic isolated from routers.

---

## 4. The "Do Not Touch" List

Future developers, **READ THIS**:

1.  **`src/models/tenant.py`**: Do not delete. It anchors the multi-tenant schema. Even if we act like a single tenant, the *database* enforces these constraints.
2.  **`src/routers/vector_db_ui.py`**: Do not delete without checking the `fix_patterns` table. It is the interface for that data.

---

## 5. The Next Frontier

With the backend cleanup complete, the focus shifts entirely to **Value Creation**:

*   **The "Brain" Tab:** The Admin UI needs to catch up to the backend's capabilities.
*   **Enrichment:** Leveraging the clean pipelines for n8n/CRM syncs.

**Current Directive:** Stop cleaning. Start building the UI.
