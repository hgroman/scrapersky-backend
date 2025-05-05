# HANDOVER: ScraperSky Background Services Audit & Documentation

## 1. Context & Objective
- **Project:** ScraperSky Backend (FastAPI, SQLAlchemy 2.0, APScheduler, Supabase/Supavisor, Docker)
- **Primary Objective:** Comprehensive audit and documentation of all background services (schedulers, workers, async jobs) and their relationship to routers, workflows, and business outcomes.
- **Mandate:** No backend process or dependency should be undocumented or unclear. All automation, triggers, and supporting files must be mapped in the main documentation.
- **Current State:** Backend workflow logic ~80% complete, frontend ~40%, overall MVP 65-70%. Frontend integration with backend status polling is pending.

## 2. Key Documentation & Resources
- **Single Source of Truth:** `CONTEXT_GUIDE.md` (consolidates all onboarding, rationale, protocol, compliance, artifact references, and best practices from README.md and AUDIT_TOOLKIT.md)
- **Router Map:** `Docs_7_Workflow_Canon/1-main_routers.md` (lists routers, some background services as sub-items)
- **Background Services Architecture:** `Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md`
- **Work Orders & Audit History:** `Docs_5_Project_Working_Docs/46-***Bulletproof Background Services Deep Audit/46.1-Work-Order.md`
- **Functional Dependency Map:** `functional_dependency_map.json` (AST-based mapping of src/ to business functions)
- **Unused/Archived Code:** `archived_code_candidates.md`, `_Archive_4.13.25/Code-Archive-25.04.19/`
- **Static Analysis:** `all_used_modules.json`, `unused_candidates.json`, custom AST/grep tools in `tools/`
- **Critical Audit Mandates:** See all memories tagged with `database_connection`, `tenant_removal`, `api_versioning`, `manual_verification`, `technical_debt`, `code_audit`.

## 3. Architectural & Technical Background
- **Tech Stack:** FastAPI, SQLAlchemy 2.0, APScheduler (for background jobs), Supabase (with RLS), Docker.
- **Database:** All access via standardized session factory. No direct/legacy connections allowed. Tenant isolation is fully removed (see 41-TENANT-ISOLATION-REMOVAL-IMPLEMENTATION.md).
- **API:** All endpoints must use `/api/v3/*` prefix. No legacy endpoints should remain.
- **Error Handling:** Custom ErrorService was removed; FastAPI native error handling is now used.
- **Transaction Boundaries:** Routers own transactions, services are transaction-aware, background jobs manage their own sessions/transactions.
- **Technical Debt:** Raw SQL in `core/db_service.py` is still in use for some features (BatchProcessing, ContentMap, DBPortal, DevTool). Manual review required for all unmapped/unused code.
- **Supabase Connection:** Requires special username format, SSL context, statement cache disabled. RLS may cause hidden tenant filtering at infra level.

## 4. Known Background Service Files (Schedulers/Workers)
Located in `/src/services/`:
- `domain_scheduler.py` – Processes domains with 'pending' status, extracts homepage metadata (title, description, emails, phones, etc.)
- `domain_sitemap_submission_scheduler.py` – Handles queued sitemap submission jobs for domains
- `sitemap_import_scheduler.py` – Manages importing and processing of sitemap files
- `sitemap_scheduler.py` – Schedules and manages sitemap scans for domains
- **Other possible background/utility files:**
    - `page_scraper/domain_processor.py` (domain-level enrichment)
    - Any file with `*_scheduler.py`, `*_worker.py`, async job logic
- **Supporting/Related Files:**
    - `scraper/metadata_extractor.py` (core metadata extraction logic)
    - `session/async_session.py` (session factory)
    - `core/db_service.py` (raw SQL, technical debt)
    - `models/`, `api_models/`, `enums/` (data models, enums)
    - `main.py` (router registration, scheduler init)

## 5. What Needs To Be Done (Next AI/Engineer Instructions)
### A. Enumerate & Document All Background Services
- Identify ALL background services, not just those already in the router map.
- For each, document:
    - File name & path
    - Main class/function names
    - What triggers it (endpoint, status change, timer)
    - Technical operation (what it does, e.g., homepage scan, sitemap import, enrichment)
    - Business outcome (what value it delivers, e.g., data enrichment, workflow automation)
    - All files/modules it imports or calls (trace import chain)
- Cross-check with `1-main_routers.md` and flag any missing services or dependencies.
- Reference static analysis outputs (`functional_dependency_map.json`, `unused_candidates.json`) and update as needed.

### B. Update Documentation
- Propose/insert a dedicated section in `1-main_routers.md` for background services (not just as sub-items under routers).
- Ensure every background service and its dependencies are visible in the workflow documentation.
- Recommend clear, concise, and actionable descriptions for maintainers.
- Update `Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md` as needed.

### C. Maintain Audit Trail
- Log all findings, changes, and recommendations in the appropriate work order and audit docs.
- Update `archived_code_candidates.md` and static analysis artifacts as code is removed or refactored.
- Manual review is mandatory for any code flagged as unused or for removal.

### D. Special Audit Topics & Known Issues
- **Tenant Filtering:** All tenant-related logic must be removed from DB queries. JWT auth only at API gateway. See memories for scripts and debugging tools.
- **Database Connection:** All code must use the session factory from `session/async_session.py`. No direct/legacy connections.
- **API Versioning:** All endpoints must use `/api/v3/*`. No deprecated endpoints.
- **Error Handling:** Use FastAPI native error handling only.
- **Technical Debt:** Raw SQL in `core/db_service.py` is a known issue. Refactor to ORM where possible.
- **Testing:** Endpoints must be tested for correct transaction patterns, validation, and error handling. See debug scripts (e.g., `debug_sitemap_flow.py`).
- **Frontend Integration:** Remaining work includes integrating frontend tabs, status polling, and end-to-end workflow verification.

## 6. Critical Memories & Mandates (Do Not Lose)
- All onboarding, rationale, and compliance info is in `CONTEXT_GUIDE.md`.
- Database connections must use the standardized session factory ONLY.
- No tenant isolation or JWT in DB ops.
- All endpoints must use `/api/v3/*`.
- Manual review is mandatory for any code flagged as unused or for removal.
- Reference all audit, code cleanup, and technical debt findings in memories and docs.
- Use `functional_dependency_map.json` and static analysis for all dependency mapping and cleanup.

## 7. Supplemental Background & Key Findings
- **Unused Code Audit:** 24 files flagged, 14 archived, 8 pending verification. Hybrid AST + grep approach used. See `archived_code_candidates.md` and memories for details.
- **Component Usage:** 74 used `src/` files mapped to business functions. 10 features, 28 shared/core, 13 unmapped (manual review required).
- **Database Consolidation:** Only `db/sitemap_handler.py` fully updated. 82% router compliance, 11% service compliance. See progress in memories.
- **Supabase/RLS Issues:** RLS may enforce tenant filtering at infra level. Correct username/SSL config required for pooler.
- **Error Handling:** Custom error handler caused 422 errors, reverted to FastAPI native handling.
- **API Standardization:** All endpoints must use `/api/v3/*`, no legacy versions.
- **Frontend Gap:** UI/integration ~40% complete; placeholder features (FrontendScout, SiteHarvest, ContactLaunchpad) need scope definition.

## 8. Final Note
If you discover any background service, utility, or supporting file not currently mapped in the main documentation, **flag it and recommend documentation updates immediately**. The goal is to leave no backend process or dependency undocumented or unclear.

---

**This handoff is designed to maximize continuity, auditability, and onboarding for the next AI or engineer.**
