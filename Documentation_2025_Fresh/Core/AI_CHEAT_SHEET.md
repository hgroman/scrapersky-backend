# AI Partner Cheat Sheet (The "Rules of Engagement")

**Target Audience:** AI Coding Assistants (Claude, Cursor, Windsurf)
**Purpose:** To prevent "Context Bloat" mistakes by listing the non-negotiable mandates and patterns of this codebase.
**Status:** MANDATORY READING

---

## 1. The "Iron Mandates" (Non-Negotiable)

### 🛑 Database & ORM
*   **ORM ONLY:** Use `SQLAlchemy AsyncSession` for all writes.
*   **NO RAW SQL:** Unless specifically working on Vector Search (`vector_db_ui.py`).
*   **CONNECTION POOLING:** Required. We host on Render.com connecting to Supabase. Without pooling, the app dies.
    *   *Correct:* Use `src/db/session.py` which handles pooling.
    *   *Wrong:* Creating new engines or raw connections in scripts.
    *   *Deep Dive:* See **[Core/CRITICAL_PATTERNS.md](Core/CRITICAL_PATTERNS.md)** for exact Supavisor parameters.

### 🛑 Deployment & Runtime
*   **DOCKER IS TRUTH:** The app runs in Docker on Render.
*   **NO LOCALHOST HTTP:** Services must **NEVER** call each other via `http://localhost:8000`.
    *   *Correct:* `await service.process_item()` (Direct Python Call).
    *   *Wrong:* `httpx.post("http://localhost/api/...")` -> This causes silent failures and auth issues.

### 🛑 Architecture
*   **V3 ONLY:** There is no V1 or V2. All routers live in `src/routers/` and use `/api/v3/`.
*   **NO WF6:** Workflow numbering skips from WF5 to WF7. "WF6" is a ghost.

---

## 2. The Core Patterns (Do It This Way)

### ✅ The Dual-Status Pattern
**Context:** User Intent (`Curation`) vs. System Action (`Processing`).
**Rule:** When a user selects an item, you must update **BOTH** statuses.
```python
# CORRECT
item.curation_status = "Selected"
item.processing_status = "Queued"  # Trigger the system!

# WRONG
item.curation_status = "Selected"  # System will ignore this forever.
```

### ✅ The "Run Job Loop" SDK
**Context:** Background processing (Scraping, Syncing).
**Rule:** Do not write custom loops. Use the standardized SDK.
```python
await run_job_loop(
    model=Model,
    status_enum=StatusEnum,
    queued_status=StatusEnum.Queued,
    processing_function=service.process_single_item,
    ...
)
```

### ✅ Service Isolation
**Context:** Business logic location.
**Rule:** Routers are thin. Logic lives in `src/services/`.
*   *Router:* Parses request, calls Service.
*   *Service:* Handles DB, Logic, External APIs.

---

## 3. The Anti-Patterns (Instant Rejection)

### ❌ "The HTTP Call"
*   **What:** Calling internal APIs via HTTP.
*   **Why:** Breaks transaction isolation, fails in Docker, requires auth handling.
*   **Fix:** Import the Service class and call the method directly.

### ❌ "The Manual Commit"
*   **What:** `await session.commit()` inside a service method called by the Job Loop.
*   **Why:** The Job Loop SDK handles the transaction. Double commits cause errors.
*   **Fix:** Let the SDK manage the transaction.

### ❌ "The Hardcoded Scheduler"
*   **What:** `scheduler.add_job(..., minutes=5)`.
*   **Why:** We use a centralized `scheduler_instance.py` and settings.
*   **Fix:** Use `settings.SCHEDULER_INTERVAL_MINUTES`.

---

## 4. Critical File Locations

*   **Settings:** `src/config/settings.py` (Environment variables)
*   **DB Session:** `src/db/session.py` (The pooling engine)
*   **Routers:** `src/routers/` (Flat structure)
*   **Services:** `src/services/` (Grouped by domain)
*   **Models:** `src/models/` (SQLAlchemy definitions)

---

**Final Check:** Before writing code, ask: "Am I respecting the Iron Mandates?"
