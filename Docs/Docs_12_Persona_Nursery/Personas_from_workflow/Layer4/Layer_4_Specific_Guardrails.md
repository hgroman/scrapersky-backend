# Layer 4 (Services & Schedulers) Specific Guardrails

**Document Version:** 1.0
**Date:** 2025-05-16
**Purpose:** To provide a concise list of the most critical, Layer 4-specific operational rules and architectural principles for the ScraperSky Layer 4 Audit Specialist Persona. These guardrails are derived from the `Layer-4-Services_Blueprint.md` and the `CONVENTIONS_AND_PATTERNS_GUIDE.md`.

---

## Core Layer 4 Principles:

1.  **Primary Logic Location:** Business logic, workflow orchestration, and interactions with external systems primarily belong in dedicated service files (`src/services/{workflow_name}_service.py`).
2.  **ORM-Only Database Access:** All database interactions within services and schedulers MUST use SQLAlchemy ORM. Raw SQL queries are strictly prohibited.
3.  **No Hardcoding:** Business-critical values (API keys, secret keys, dynamic thresholds, etc.) MUST NOT be hardcoded in services or schedulers. Use the `settings` object (from `src/config/settings.py`).
4.  **Tenant ID Removed:** All `tenant_id` parameters, model fields, and related filtering logic MUST be absent.

## Service File Specifics (`src/services/{workflow_name}_service.py`):

5.  **Session Handling (Services):**
    - Services MUST accept an `AsyncSession` object as a parameter from the calling layer (typically a router or another service).
    - Services MUST NOT create their own database sessions for routine operations.
6.  **Transaction Awareness (Services):**
    - Services are transaction-aware but generally MUST NOT manage transaction boundaries (commit/rollback) themselves. Transaction management is typically handled by the calling router or the top-level background task function.
7.  **Function Naming (Processing Services):**
    - The primary function for processing a single item for a workflow MUST be named: `async def process_single_{source_table_name}_for_{workflow_name}(...)`.

## Scheduler File Specifics (`src/services/{workflow_name}_scheduler.py`):

8.  **Dedicated Scheduler File:** Each workflow requiring background processing MUST have its own dedicated scheduler file: `src/services/{workflow_name}_scheduler.py`.
9.  **Session Handling (Schedulers):**
    - Top-level functions in scheduler files (e.g., `process_{workflow_name}_queue()`) that serve as entry points for background tasks MUST use `get_background_session()` to create and manage their own session lifecycle and transaction boundaries.
10. **Scheduler Setup & Registration:**
    - Each scheduler file MUST implement a setup function: `def setup_{workflow_name}_scheduler() -> None:`.
    - This `setup_{workflow_name}_scheduler()` function MUST be imported into `src/main.py` and called within the `lifespan` context manager.
11. **Standard Polling Pattern:**
    - Schedulers should typically utilize the `run_job_loop` helper function (from `src/common/curation_sdk/scheduler_loop.py`) for standard database polling patterns.
12. **Configuration via Settings:**
    - Job parameters for schedulers (e.g., interval, batch size) MUST be read from the `settings` object and defined in `src/config/settings.py` / `.env.example` using the convention: `{WORKFLOW_NAME_UPPERCASE}_SCHEDULER_{PARAMETER_NAME}`.
13. **Function Naming (Scheduler Jobs):**
    - The main polling function within a scheduler should typically be named: `async def process_{workflow_name}_queue():`.

## Router-Handled Logic (Documented Exception for Layer 4-like behavior in Routers):

14. **Bounded Router Logic:** If a router implements the "Router-Handled CRUD & Dual-Status Updates" pattern (e.g., in a `{workflow}_CRUD.py` file):
    - The business logic within that router MUST be strictly confined to CRUD operations and the immediate, synchronous dual-status update for the router's primary entity.
    - Logic exceeding this scope (e.g., complex orchestration, significant interaction with other models/services, external API calls not related to simple entity lookups) is a critical deviation and MUST be refactored into a dedicated service.
    - Such routers WILL manage their own transaction boundaries.

---

_This document is intended as a quick reference. Always defer to the full `Layer-4-Services_Blueprint.md` and `CONVENTIONS_AND_PATTERNS_GUIDE.md` for complete details and context._
