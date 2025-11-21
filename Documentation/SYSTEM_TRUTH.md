# System Truth: ScraperSky Backend
> **Status**: Living Document
> **Last Updated**: 2025-11-20
> **Purpose**: To serve as the single, comprehensive source of truth for the ScraperSky backend, capturing varying altitudes of perspective from high-level strategy to low-level implementation reality.

---

## Altitude 1: Strategic & Architectural Truth
**The "Why" and "What"**

### Core Objective
ScraperSky is a high-throughput, automated intelligence gathering platform designed to:
1.  **Discover** digital assets (Domains, Sitemaps, Pages) at scale.
2.  **Extract** structured data (Business details, Contacts) from those assets.
3.  **Enrich** that data using external providers (Google Maps, n8n, DeBounce).
4.  **Sync** high-value intelligence to CRM systems (HubSpot, Brevo, Mautic).

### Architectural Pillars
*   **FastAPI & Asyncio**: Built for concurrency to handle massive I/O bound scraping operations.
*   **PostgreSQL & SQLAlchemy**: Relational data integrity with a standardized schema.
*   **Job-Based Processing**: Long-running tasks (Scraping, Scanning) are offloaded to background workers, tracked via Job IDs.
*   **Service-Oriented Logic**: Business logic is encapsulated in Services (e.g., `PageProcessingService`, `PlacesSearchService`), keeping Routers thin (mostly).
*   **Dual-Status State Machine**: A recurring pattern where a "Curation Status" (User intent) drives a "Processing Status" (System action).

---

## Altitude 2: Operational Truth
**The "How" - Key Patterns & Workflows**

### The Dual-Status Pattern
Across the system, entities (Domains, Sitemaps, Contacts) utilize a pair of status fields to coordinate user action with system execution:
*   **Curation Status**: `New` -> `Selected` -> `Skipped`. (Set by User/API).
*   **Processing Status**: `None` -> `Queued` -> `Processing` -> `Complete` / `Error`. (Managed by System).
*   **Trigger**: Setting Curation Status to `Selected` automatically sets Processing Status to `Queued`.

### The "Run Job Loop" SDK
A standardized approach to background processing:
1.  **Initiate**: API creates a `Job` record and returns 202 Accepted.
2.  **Offload**: `BackgroundTasks` or `asyncio.create_task` triggers the worker.
3.  **Isolate**: Worker runs in its own `process_domain_with_own_session` to ensure transaction isolation.
4.  **Update**: Worker updates Job status and Entity status upon completion.

### Data Flow Pipeline
1.  **Discovery**: Google Maps (`google_maps_api.py`) or CSV Import -> **Places Staging**.
2.  **Promotion**: Staged Place -> **Domain** (via Deep Scan or Selection).
3.  **Expansion**: Domain -> **Sitemaps** (Discovery) -> **Pages** (Extraction).
4.  **Extraction**: Page -> **Contacts** (Email/Phone).
5.  **Validation**: Contact -> **DeBounce** (Validation).
6.  **Enrichment**: Contact -> **n8n** (Enrichment).
7.  **Sync**: Contact -> **CRM** (HubSpot/Brevo).

---

## Altitude 3: Implementation Truth
**The "Where" - Component Catalog**

### Router Catalog (The "9 Versions" of Entry)
The system exposes functionality through a diverse set of routers, reflecting its evolution:

#### 1. Sitemap Management
*   `modernized_sitemap.py`: Single-domain scans.
*   `batch_sitemap.py`: Batch processing.
*   `v3/sitemaps_direct_submission_router.py`: Direct URL entry (Auto-queues).
*   `v3/sitemaps_csv_import_router.py`: Bulk CSV import (Auto-queues).
*   `sitemap_files.py`: CRUD & Status Management.

#### 2. Domain & Page Management
*   `modernized_domain_router.py`: Domain operations & background tasks.
*   `batch_page_scraper.py`: Batch page scraping.
*   `v3/domains_csv_import_router.py`: Bulk Domain CSV (No auto-queue).
*   `v3/pages_csv_import_router.py`: Bulk Page CSV (No auto-queue).
*   `v3/domains_router.py` / `v3/pages_router.py`: Standard CRUD.

#### 3. Scraping & Intelligence
*   `google_maps_api.py`: Google Maps integration & Place Staging.
*   `email_scanner.py`: Email extraction status.
*   `places_staging.py`: Staging area management & Deep Scan triggering.

#### 4. CRM & Utilities
*   `contacts_router.py`: Contact management & CRM Sync selection.
*   `contacts_validation_router.py`: Email validation (DeBounce).
*   `n8n_webhook_router.py`: Inbound enrichment data.
*   `db_portal.py`: Schema inspection & validation.
*   `vector_db_ui.py`: AI Pattern search & Vector operations.

---

## Altitude 4: The "Honest" Truth
**Technical Debt, Redundancy, and Reality**

### 1. Router Redundancy ("The 9 Versions")
There is significant overlap in how data enters the system.
*   **Sitemaps**: Can be submitted via `modernized`, `batch`, `direct_submission`, or `csv_import`. Logic is largely duplicated.
*   **Scraping**: `modernized_page_scraper.py` and `batch_page_scraper.py` perform nearly identical tasks.
*   **Schema Tools**: `dev_tools.py` and `db_portal.py` both offer schema inspection, with `db_portal.py` being the more robust, modern choice.

### 2. Inconsistent Queueing Patterns
*   **Sitemap Routers**: consistently implement "Auto-Queue" (User submits -> System Queues).
*   **CSV Import Routers (Domains/Pages)**: Do **NOT** auto-queue. They import as `New`, requiring a second manual step to trigger processing. This inconsistency can lead to user confusion ("Why isn't my CSV import running?").

### 3. Database Access Patterns
*   Most of the system uses the standard SQLAlchemy `AsyncSession`.
*   **Vector DB**: Bypasses ORM to use `asyncpg` directly for vector similarity searches, creating a hidden dependency on the underlying driver and connection string format.

### 4. Authentication & Security
*   RBAC (Role Based Access Control) has been largely stripped out in favor of simple JWT authentication (`get_current_user`).
*   `DEFAULT_TENANT_ID` is hardcoded in many places, effectively making the system single-tenant in practice despite a multi-tenant schema.
*   `n8n_webhook_router` uses a separate shared secret (`N8N_WEBHOOK_SECRET`) rather than standard JWT.

### 5. Evolution Artifacts
*   File names like `WF7_V3_L3_1of1_PagesRouter.py` indicate a legacy "Workflow" naming convention that is being phased out in favor of semantic names (`pages_router.py`), but both exist in the codebase, potentially confusing developers.

---

> **Recommendation**: Use this document as the baseline for future refactoring. Prioritize consolidating the "9 Versions" of entry points into unified, robust services that handle both single, batch, and file-based inputs consistently.
