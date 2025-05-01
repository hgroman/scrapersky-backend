🟧 T - ScraperSky Platform Snapshot ← for architecture, reality, positioning

**Date:** 2024-04-18
**Version:** 1.0

**Objective:** This document provides a definitive technical and strategic assessment of the ScraperSky platform based on current codebase analysis, including dependency tracing, runtime behavior simulation, and architectural review.

---

### 1. System Functionality Summary

- **Core Functionality:** ScraperSky is an integrated platform for acquiring, processing, managing, and curating web data, with a strong focus on sitemap analysis, business location data (e.g., Google Places), and domain information. It combines automated scraping capabilities with data storage and workflow tools.

- **Supported Workflows:**

  - **Batch Data Processing:** Initiating and managing large-scale data acquisition tasks (e.g., sitemap analysis via "Batch Search" UI tab).
  - **Sitemap Curation:** Managing and analyzing sitemap files (`.xml`), likely involving fetching, parsing, and storing sitemap contents.
  - **Local Business Data Management:** Interacting with Google Maps API for place searches (`LocalMiner`), storing/managing place data, and potentially curating local business records (`LocalBusinessCuration`, `StagingEditor`).
  - **Domain Data Management:** Storing and potentially analyzing domain information (`DomainCuration`, `DomainScanning`).
  - **Background Task Execution:** Running scheduled jobs for data maintenance or acquisition (e.g., `domain_sitemap_submission_scheduler`, `sitemap_scheduler`).

- **Internal Tools & Modules:**
  - **Web Framework:** FastAPI provides the core API structure, routing, and request handling.
  - **Data Persistence:** Primarily PostgreSQL (inferred), accessed via SQLAlchemy ORM (`src/models/`, `src/db/session.py`) and a non-compliant raw SQL service (`src/services/core/db_service.py`).
  - **Authentication:** JWT-based authentication secures API endpoints (`src/auth/jwt_auth.py`).
  - **Scraping Utilities:** Modules for interacting with external scraper APIs (`src/utils/scraper_api.py`), parsing metadata (`src/scraper/metadata_extractor.py`), analyzing sitemaps (`src/scraper/sitemap_analyzer.py`), and handling domain specifics (`src/scraper/domain_utils.py`).
  - **Scheduling:** APScheduler (`scheduler_instance.py`) manages background tasks.
  - **Configuration:** Centralized settings (`src/config/settings.py`) and logging (`src/config/logging_config.py`).
  - **Admin/Developer Tools:** Dedicated interfaces (`DBPortal`, `DevTool`) for database inspection, task management, and potentially other internal operations, separate from the main user UI.

---

### 2. Technical Architecture

- **Frameworks & Libraries:**

  - **Backend:** FastAPI (Python)
  - **ORM:** SQLAlchemy (Python)
  - **Database Driver:** `psycopg` (Python for PostgreSQL)
  - **Database:** PostgreSQL (Inferred)
  - **Scheduling:** APScheduler (Python)
  - **Frontend:** HTML/JavaScript (Inferred from `admin-dashboard.html` references, specific framework like React/Vue unknown)
  - **Validation:** Pydantic (via FastAPI)

- **Data Flow:**

  1.  **Ingestion:** Data enters via API calls (frontend UI, external systems), direct interactions with external APIs (Google Maps, ScraperAPI), or batch processing triggers.
  2.  **Processing:** FastAPI routers (`src/routers/`) receive requests, delegate to service layer modules (`src/services/`). Services orchestrate scraping logic, data transformation, and validation. Background tasks are handled by APScheduler invoking specific service functions.
  3.  **Storage:** Processed data is persisted to PostgreSQL using primarily SQLAlchemy ORM session management (`src/session/async_session.py`, `src/db/session.py`). A significant subset of features (BatchProcessing, ContentMap, DBPortal, DevTool) incorrectly bypass the ORM and use raw SQL via `src/services/core/db_service.py`.
  4.  **Retrieval/Output:** Data is retrieved via FastAPI endpoints, formatted using Pydantic schemas (`src/schemas/`), and returned as API responses (JSON) to the frontend or other consumers. Batch processes may output results directly (details unspecified).

- **Hosting & Operations:**

  - **Containerization:** Docker is used (inferred from `Dockerfile`, `docker-compose.yml`).
  - **Database:** PostgreSQL instance (details of hosting - managed service vs. self-hosted - unknown).
  - **Deployment:** Likely deployed as container(s) on cloud infrastructure (AWS, GCP, Azure) or on-premise servers. Reverse proxy (Nginx, Traefik) probable but not confirmed.

- **Security & Boundaries:**
  - **Authentication:** API endpoints are secured using JWT.
  - **Authorization:** Assumed role/permission logic exists but details are not exposed by current analysis.
  - **Tenant Isolation:** Database models consistently include `tenant_id`, indicating multi-tenant capability enforced at the data layer.
  - **Integration Boundaries:** Clear separation between Frontend UI and Backend API. Interfaces exist with external services (Google Maps API, ScraperAPI). Internal boundary violations exist due to direct raw SQL usage by some features.

---

### 3. Usage Reality

- **Actively Used Features (Runtime Evidence/Tracing):**

  - Batch Search (BatchProcessing)
  - Sitemap Curation (SitemapCuration)
  - Local Business Curation (LocalBusinessCuration)
  - Staging Editor (StagingEditor)
  - Content Map / Sitemap Analysis (ContentMap)
  - Domain Curation (DomainCuration)
  - Local Data Mining (LocalMiner via Google Maps API)
  - Domain Scanning (DomainScanning via modernized_page_scraper)
  - Developer Tools (DevTool)
  - Database Portal (DBPortal)
  - Background Schedulers (`domain_sitemap_submission_scheduler`, `sitemap_scheduler`)

- **Component Status (Based on `functional_dependency_map.json`):**

  - **Shared (Core):** ~28 files are used across multiple distinct features (e.g., `settings.py`, `jwt_auth.py`, ORM models like `Domain`, `Place`, `Tenant`, utility modules). `db_service.py` is incorrectly used as a shared module by four features.
  - **Siloed:** ~15+ files are tied to single features (e.g., `src/routers/batch_sitemap.py` -> BatchProcessing; `src/services/places/places_search_service.py` -> LocalMiner).
  - **Orphaned/Unmapped:** ~13 files are identified as potentially unused or unmapped by current tracing (`reports/unused_candidates.json` and "Unmapped" list in `functional_dependency_map.json`). This includes routers like `batch_page_scraper.py`, `email_scanner.py`, `profile.py`, and various models/services. **Manual verification is mandatory for these candidates.**

- **Technical Debt & Fragility:**
  - **Dual Data Access Strategy:** The most significant tech debt is the coexistence of SQLAlchemy ORM and direct raw SQL via `db_service.py`. This increases complexity, violates the intended architecture, causes maintenance issues (current `psycopg` v3 incompatibility), and hinders refactoring.
  - **Potential Dead Code:** The "Unmapped" and "unused_candidates" files represent a non-trivial portion of the codebase that may be obsolete, increasing cognitive load and potential hidden bugs.
  - **Inconsistent Patterns:** The raw SQL usage bypasses standard ORM session management, potentially leading to transactional inconsistencies if not handled perfectly within `db_service.py`.
  - **Testing Gaps:** The difficulty in resolving the `db_service.py` linter errors suggests potential gaps in automated testing coverage, particularly around database interactions.

---

### 4. Strategic Posture

- **Extensibility:**

  - **Foundation:** The FastAPI + SQLAlchemy core provides a solid, modern foundation for extending API functionality and data models _if_ the ORM pattern is adhered to.
  - **Impediments:** The `db_service.py` dependency and associated raw SQL usage significantly hinder extensibility for affected features. Refactoring this is a prerequisite for clean expansion. Potential dead code also complicates understanding and extension.
  - **Structure:** The modular structure (`routers`, `services`, `models`) facilitates adding new, self-contained features following established patterns.

- **Well-Positioned For:**

  - Adding new scraping targets or data types that fit existing processing/storage patterns (ORM-based).
  - Enhancing UI workflows for existing, actively used features (Batch Search, Curation tools).
  - Improving data validation and enrichment within existing workflows.
  - Optimizing specific ORM-based database queries.

- **Not Ready For:**

  - Seamlessly extending or modifying the four features reliant on `db_service.py` without significant refactoring first.
  - Integrating systems requiring fundamentally different data storage paradigms (e.g., NoSQL, Graph DB) without architectural changes.
  - Large-scale, low-latency, real-time data processing without performance analysis and potential optimization.
  - Major architectural pivots until tech debt (dual data access, unused code) is addressed.

- **Unique Value Proposition:**
  - ScraperSky's uniqueness lies in its **integrated workflow approach** specifically tailored to acquiring and curating complex web data like sitemaps and business location details.
  - **vs. Commodity Scrapers:** It goes beyond simple data extraction by providing data management, analysis (sitemaps), batch processing, and curation tools within the same platform.
  - **vs. Generic CRMs:** While it manages business-related data, its focus is on the _acquisition and processing_ of web-derived data, not general customer relationship management, sales pipelines, or marketing automation.
  - **Niche:** It occupies a niche focused on structured web data acquisition pipelines combined with specialized management and curation workflows, particularly valuable for SEO, market research, or competitive analysis use cases requiring deep sitemap or location data insights.
