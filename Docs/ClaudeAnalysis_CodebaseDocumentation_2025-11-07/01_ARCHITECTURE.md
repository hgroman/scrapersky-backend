# ScraperSky Backend - Complete Architecture Documentation

**Version:** 3.0.0
**Last Updated:** 2025-11-07
**Status:** Production

This document provides a comprehensive overview of the ScraperSky backend architecture, serving as the entry point to all detailed technical documentation.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Layers](#architecture-layers)
4. [Data Flow & Workflows](#data-flow--workflows)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)
7. [Documentation Index](#documentation-index)
8. [Quick Start Guide](#quick-start-guide)
9. [Critical Information](#critical-information)

---

## Executive Summary

ScraperSky is a **FastAPI-based web scraping and metadata extraction service** designed for large-scale domain analysis. The system discovers businesses via Google Places API, extracts website metadata, analyzes sitemaps, and curates contact information through a multi-workflow pipeline.

### Key Capabilities
- **Google Places Discovery:** Search and deep-scan local businesses
- **Domain Analysis:** Extract website metadata (tech stack, CMS detection, contact info)
- **Sitemap Processing:** Discover, parse, and analyze XML sitemaps at scale
- **Page Curation:** Intelligent page categorization and contact extraction
- **Batch Operations:** Process hundreds of domains concurrently
- **Background Jobs:** APScheduler-driven workflow automation

### Architecture Characteristics
- **Async-First:** All I/O operations use asyncio patterns
- **Database:** PostgreSQL (Supabase) with Supavisor connection pooling
- **API Design:** RESTful with versioned endpoints (v3 primary)
- **Job Processing:** Event-driven background schedulers (5 active workflows)
- **Authentication:** JWT-based with dependency injection
- **Deployment:** Docker containers on Render.com

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  Web Dashboard • API Clients • Background Jobs • Webhooks        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│  FastAPI • CORS • JWT Auth • Rate Limiting (missing)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│   ROUTER LAYER       │      │  SCHEDULER LAYER     │
│  20 Router Modules   │      │  5 Active Schedulers │
│  API v2/v3 Endpoints │      │  APScheduler Jobs    │
└──────┬───────────────┘      └──────┬───────────────┘
       │                              │
       └──────────────┬───────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│  Business Logic • External API Integration • Data Transformation │
│  ├── Batch Processing Services                                   │
│  ├── Google Maps/Places Services                                 │
│  ├── Sitemap Services                                            │
│  ├── Page Scraper Services                                       │
│  └── Utility Services                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│   DATABASE LAYER     │      │  EXTERNAL APIS       │
│  PostgreSQL/Supabase │      │  • Google Maps       │
│  • 14 Tables         │      │  • ScraperAPI        │
│  • Vector Extension  │      │  • OpenAI (vectors)  │
│  • Supavisor Pooler  │      └──────────────────────┘
└──────────────────────┘
```

### Request Flow

**Synchronous API Request:**
```
Client → CORS Check → JWT Auth → Router → Service → Database → Response
```

**Background Job Flow:**
```
Scheduler Trigger → Fetch Pending Records → Mark as Processing
                 → Release DB Connection → Heavy Computation
                 → Quick DB Update → Next Batch
```

---

## Architecture Layers

### 1. API/Router Layer (`src/routers/`)

**Purpose:** Handle HTTP requests, validate input, manage transactions

**Key Patterns:**
- **Transaction Ownership:** Routers own transaction boundaries
- **Dependency Injection:** Services receive session as parameter
- **Dual-Status Updates:** Primary status change auto-queues processing
- **Pagination:** Offset/limit with separate count queries
- **Filtering:** Enum-based with query parameter validation

**Router Categories:**
- Domain Management (`domains.py`, `local_businesses.py`)
- Sitemap Processing (`modernized_sitemap.py`, `batch_sitemap.py`, `sitemap_files.py`)
- Page Scraping (`modernized_page_scraper.py`, `batch_page_scraper.py`)
- Google Maps (`google_maps_api.py`, `places_staging.py`)
- Contact Management (`v3/contacts_router.py`)
- Utilities (`db_portal.py`, `dev_tools.py`, `profile.py`, `vector_db_ui.py`)

**Total Endpoints:** 80+ across 20 router files

**See:** Comprehensive endpoint documentation in exploration results above

---

### 2. Service Layer (`src/services/`)

**Purpose:** Business logic, external API integration, data transformation

**Design Principles:**
- **Transaction-Aware:** Work within transactions but don't manage them
- **Exception:** Background tasks create own sessions
- **Async-First:** All I/O operations use asyncio
- **Error Handling:** Graceful degradation with detailed logging

**Service Categories:**

#### Batch Processing (`batch/`)
- `batch_functions.py` - Core batch operations
- `batch_processor_service.py` - High-level orchestration
- `types.py` - Shared type definitions

**Pattern:** Concurrent processing with semaphore (max 25), periodic progress updates

#### Google Maps/Places (`places/`)
- `places_service.py` - Database operations
- `places_search_service.py` - Text Search API integration
- `places_storage_service.py` - Persistence layer
- `places_deep_service.py` - Place Details API integration

**External API Cost:**
- Text Search: ~$7 per 1,000 requests
- Place Details: ~$17 per 1,000 requests

#### Sitemap (`sitemap/`)
- `sitemap_processing_service.py` - Orchestrate discovery
- `sitemap_import_service.py` - Parse and import URLs
- `sitemap_files_service.py` - CRUD operations

**Discovery Methods:** robots.txt, common paths, sitemap index, HTML links, manual

#### Page Scraper (`page_scraper/`)
- `processing_service.py` - Coordinate page scanning
- `domain_processor.py` - Background session processing

**Metadata Extracted:** Title, CMS detection, WordPress version, Elementor, contact info, social links

#### Schedulers
- `domain_scheduler.py` - Domain metadata extraction (WF3)
- `sitemap_scheduler.py` - Multi-workflow processor (WF2/WF3/WF5) ⚠️
- `domain_sitemap_submission_scheduler.py` - Submit to sitemap scan (WF4)
- `sitemap_import_scheduler.py` - Import sitemap URLs (WF6)
- `WF7_V2_L4_2of2_PageCurationScheduler.py` - Page processing (WF7)

**See:** `Docs/Scheduler_Architecture_Complete_Analysis_20251107.md` for full details

---

### 3. Database/Model Layer (`src/models/`)

**Purpose:** Define schema, relationships, and database operations

**Database:** PostgreSQL 15+ via Supabase with pgvector extension

**Core Models:**

| Model | Table | Purpose | Key Relationships |
|-------|-------|---------|-------------------|
| Domain | domains | Website entities | → Pages, SitemapFiles, Jobs |
| Page | pages | Individual URLs | → Domain, Contacts |
| Contact | contacts | Email/contact info | → Page |
| SitemapFile | sitemap_files | Sitemap metadata | → Domain, SitemapUrls |
| SitemapUrl | sitemap_urls | URLs from sitemaps | → SitemapFile |
| LocalBusiness | local_businesses | Google Places data | → Domain |
| Place | places_staging | Places staging area | → PlaceSearch |
| Job | jobs | Job tracking | → Domain, BatchJob |
| BatchJob | batch_jobs | Batch tracking | → Jobs, Domains |

**Total Tables:** 14 active (+ removed RBAC tables)

**Key Patterns:**
- **BaseModel Mixin:** All models inherit id, created_at, updated_at
- **Workflow Status:** Dual-stage (curation + processing status)
- **JSONB Metadata:** Flexible additional_json fields
- **PostgreSQL Arrays:** Used for tags, categories, links
- **UUID Primary Keys:** Except Job, BatchJob, Place (integer)

**Enums:** 18+ defined in `models/enums.py`

**See:** Complete schema documentation in exploration results above

---

### 4. Configuration Layer (`src/config/`)

**Purpose:** Environment variables, settings, logging configuration

**Key Files:**
- `settings.py` - Pydantic BaseSettings (80+ environment variables)
- `logging_config.py` - Logging setup (currently hardcoded to DEBUG ⚠️)

**Critical Environment Variables:**

**Required (no defaults):**
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_DB_PASSWORD=xxxxx
JWT_SECRET_KEY=xxxxx  # App crashes without this
```

**Database Connection:**
```bash
SUPABASE_POOLER_HOST=xxx.pooler.supabase.com
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=postgres.xxx
```

**External APIs:**
```bash
GOOGLE_MAPS_API_KEY=xxxxx
SCRAPER_API_KEY=xxxxx
OPENAI_API_KEY=xxxxx  # For vector embeddings
```

**Scheduler Configuration (per scheduler):**
```bash
{NAME}_SCHEDULER_INTERVAL_MINUTES=1
{NAME}_SCHEDULER_BATCH_SIZE=50
{NAME}_SCHEDULER_MAX_INSTANCES=3
```

**See:** `Docs/CONFIGURATION_*.md` for complete reference

---

### 5. External Integration Layer

**Purpose:** Interface with external services and APIs

**Primary Integrations:**

#### 1. Supabase PostgreSQL
- **Connection:** Supavisor pooler (mandatory, port 6543)
- **Pool Size:** 5 (dev) / 10 (prod)
- **Critical Parameters:** `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`
- **Vector Extension:** pgvector for semantic search
- **Files:** `src/db/engine.py`, `src/session/async_session.py`

#### 2. Google Maps Platform
- **Text Search API:** Business discovery by location + type
- **Place Details API:** Deep metadata (15+ fields)
- **Client:** googlemaps Python SDK + aiohttp
- **Rate Limiting:** 2-second delay between pagination tokens
- **Files:** `src/services/places/`

#### 3. ScraperAPI
- **Purpose:** Web scraping with proxy rotation
- **Base URL:** `http://api.scraperapi.com`
- **Cost Control:** Premium features disabled by default
- **Client:** Dual-method (aiohttp primary, SDK fallback)
- **Files:** `src/utils/scraper_api.py`

#### 4. OpenAI
- **Purpose:** Vector embeddings for semantic search
- **Model:** text-embedding-ada-002
- **Usage:** Vector database pattern storage
- **Files:** `src/routers/vector_db_ui.py`

**HTTP Clients:**
- **aiohttp:** Primary async HTTP (Google, ScraperAPI, web scraping)
- **httpx:** Alternative async (vector searches)
- **requests:** Legacy sync (email scraper)

**See:** `Docs/EXTERNAL_INTEGRATIONS*.md` for complete details

---

## Data Flow & Workflows

### Workflow Overview

ScraperSky implements 7 distinct workflows (WF1-WF7) orchestrated by schedulers and API endpoints:

```
┌─────────────────────────────────────────────────────────────────┐
│  WF1: Google Places Search                                       │
│  API → Search Places → Store in places_staging → Mark "New"     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  WF2: Deep Scan (Place Details)                                  │
│  Scheduler → Fetch "Selected" Places → Google Details API       │
│           → Upsert to local_businesses                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  WF3: Domain Extraction                                          │
│  Scheduler → Fetch local_businesses with website                │
│           → Extract domain → Create pending Domain               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  WF4: Domain Sitemap Submission                                  │
│  Scheduler → Fetch Domains with status="Selected"               │
│           → Submit to /api/v3/sitemap/scan                       │
│           → Update sitemap_analysis_status="submitted"           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  WF5: Sitemap Discovery (Legacy - being replaced by WF6)        │
│  Background → Discover sitemaps → Parse XML                      │
│            → Store SitemapFile + SitemapUrl records              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  WF6: Sitemap Import (Modern)                                    │
│  Scheduler → Fetch SitemapFiles "Selected"                       │
│           → Download XML → Parse URLs                            │
│           → Categorize pages → Create Page records               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  WF7: Page Curation                                              │
│  Scheduler → Fetch Pages "Selected"                              │
│           → Extract contact info → Create Contact records        │
│           → Categorize page type → Update status                 │
└─────────────────────────────────────────────────────────────────┘
```

### Status State Machines

**Domain Workflow:**
```
New → Selected (user) → queued (auto) → processing (scheduler)
                                      → submitted (success)
                                      → failed (error)
```

**Page Workflow:**
```
New → Selected (user) → Queued (auto) → Processing (scheduler)
                                      → Complete (success)
                                      → Error (failure)
```

**Contact Workflow:**
```
New → Queued (auto) → Processing (scheduler) → Complete/Error
```

### Critical Handoff Points

**Dual-Status Pattern:** Setting primary curation status to "Selected" automatically queues the item for processing by setting the processing status to "Queued".

**Implementation:**
- Domains: `sitemap_curation_status='Selected'` → `sitemap_analysis_status='queued'`
- Pages: `page_curation_status='Selected'` → `page_processing_status='Queued'`
- Contacts: `contact_curation_status='Queued'` → `contact_processing_status='Queued'`
- SitemapFiles: `deep_scrape_curation_status='Selected'` → `sitemap_import_status='Queued'`

---

## Technology Stack

### Core Framework
- **FastAPI** 0.104+ - Async web framework
- **Uvicorn** - ASGI server
- **Pydantic** 2.0+ - Data validation
- **Python** 3.11+ - Runtime

### Database
- **SQLAlchemy** 2.0+ - ORM (async)
- **asyncpg** - PostgreSQL driver (async)
- **psycopg** - PostgreSQL driver (sync fallback)
- **Alembic** - Database migrations
- **PostgreSQL** 15+ - Database server
- **pgvector** - Vector similarity extension

### Background Jobs
- **APScheduler** 3.10+ - Job scheduling
- **AsyncIOScheduler** - Async job executor

### HTTP Clients
- **aiohttp** - Primary async HTTP
- **httpx** - Alternative async HTTP
- **requests** - Legacy sync HTTP
- **googlemaps** - Google Maps SDK

### Web Scraping
- **BeautifulSoup4** - HTML parsing
- **lxml** - XML parsing
- **validators** - URL/email validation

### External Services
- **Supabase** - PostgreSQL hosting + auth
- **Google Maps Platform** - Places API
- **ScraperAPI** - Web scraping proxy
- **OpenAI** - Vector embeddings

### Development Tools
- **Docker** / **Docker Compose** - Containerization
- **pytest** - Testing framework
- **ruff** - Linting and formatting
- **pre-commit** - Git hooks
- **MyPy** - Type checking

### Deployment
- **Render.com** - Cloud hosting
- **Docker** - Production containers
- **GitHub Actions** - CI/CD (if configured)

---

## Deployment Architecture

### Container Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Container (scrapersky)                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Uvicorn Server (Port 8000)                                │ │
│  │  ├── FastAPI App                                           │ │
│  │  ├── APScheduler (5 background jobs)                       │ │
│  │  ├── Static File Server (/static)                          │ │
│  │  └── Health Check Endpoint (/health)                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Environment Variables: .env file or Render config               │
│  Persistent Storage: None (stateless)                            │
│  Networking: Bridge mode, port 8000 exposed                      │
└─────────────────────────────────────────────────────────────────┘
          ↓ Database Connections (5-10 pooled)
┌─────────────────────────────────────────────────────────────────┐
│            Supabase (External Service)                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Supavisor Connection Pooler (Port 6543)                   │ │
│  │  └── PostgreSQL 15 + pgvector                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Production Deployment (Render.com)

**Service Type:** Web Service (Docker)

**Configuration:**
- **Build Command:** `docker build -t scrapersky .`
- **Start Command:** `uvicorn src.main:app --host 0.0.0.0 --port 8000`
- **Health Check:** `GET /health` (30s interval, 3 retries)
- **Auto-Deploy:** Enabled from main branch
- **Instance Type:** Configurable (Standard or higher recommended)

**Environment Variables:** Set in Render dashboard from `Docs/CONFIGURATION_QUICK_REFERENCE.md`

**Scaling:**
- **Horizontal:** Multiple instances behind load balancer
- **Vertical:** Increase instance CPU/memory
- **Database:** Connection pool limits (max 10 per instance)

### Development Deployment (Docker Compose)

**Files:**
- `docker-compose.yml` - Development setup
- `docker-compose.prod.yml` - Production-like local setup

**Usage:**
```bash
# Development (with volume mounts for hot reload)
docker compose up --build

# Production simulation
docker compose -f docker-compose.prod.yml up -d
```

**Volumes:**
- `./src` → `/app/src` (code hot reload)
- `./static` → `/app/static` (static files)
- `./logs` → `/app/logs` (persistent logs)

---

## Documentation Index

### Core Documentation (Generated)

1. **Application Structure**
   - Main entry point analysis (in exploration results)
   - Router mapping (in exploration results)
   - Middleware configuration (in exploration results)

2. **Database Schema**
   - Complete model documentation (in exploration results)
   - Relationship mapping (in exploration results)
   - Enum definitions (in exploration results)

3. **API Endpoints**
   - Complete endpoint reference (in exploration results)
   - Request/response patterns (in exploration results)
   - Authentication requirements (in exploration results)

4. **Service Layer**
   - Service architecture (in exploration results)
   - Business logic documentation (in exploration results)
   - External API integration (in exploration results)

5. **Schedulers & Background Jobs**
   - `Docs/Scheduler_Architecture_Complete_Analysis_20251107.md` - Full details
   - `Docs/Scheduler_Quick_Reference_20251107.md` - Quick reference
   - Workflow orchestration (in exploration results)

6. **Authentication & Security**
   - JWT implementation analysis (in exploration results)
   - Security concerns and gaps (in exploration results)

7. **Configuration & Environment**
   - `Docs/CONFIGURATION_ANALYSIS.md` - Complete reference
   - `Docs/CONFIGURATION_CODE_EXAMPLES.md` - Implementation patterns
   - `Docs/CONFIGURATION_QUICK_REFERENCE.md` - Quick lookup

8. **External Integrations**
   - `Docs/EXTERNAL_INTEGRATIONS.md` - Technical reference
   - `Docs/EXTERNAL_INTEGRATIONS_QUICKREF.md` - Quick reference

### Project Documentation (Existing)

- `CLAUDE.md` - Development guidance for AI assistant
- `.env.example` - Environment variable template
- `README.md` - Project overview (if exists)
- `Docs/` - Additional documentation directory

---

## Quick Start Guide

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Supabase Account** with PostgreSQL database
- **Google Maps API Key** (for Places features)
- **ScraperAPI Key** (optional, for enhanced scraping)

### 5-Minute Setup

1. **Clone and Configure:**
```bash
git clone <repository-url>
cd scrapersky-backend
cp .env.example .env
nano .env  # Add your Supabase and API credentials
```

2. **Required Environment Variables:**
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_POOLER_HOST=xxx.pooler.supabase.com
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=postgres.xxx
SUPABASE_DB_PASSWORD=your_password
JWT_SECRET_KEY=your_secret_key_here
GOOGLE_MAPS_API_KEY=your_google_api_key
```

3. **Start Development Server:**
```bash
docker compose up --build
```

4. **Verify Deployment:**
```bash
# Health check
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/database

# API documentation
open http://localhost:8000/docs
```

5. **Test API:**
```bash
# Get JWT token (using development token)
TOKEN="scraper_sky_2024"

# Test endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v3/domains?page=1&size=10
```

### Common Tasks

**View Logs:**
```bash
docker compose logs -f app
```

**Run Tests:**
```bash
pytest -q
```

**Format Code:**
```bash
ruff format .
ruff check .
```

**Database Shell:**
```bash
# Via Supabase dashboard SQL editor
# Or use psql with connection string
```

---

## Critical Information

### ⚠️ Critical Requirements

1. **Supavisor Parameters (MANDATORY)**
   - `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`
   - Never modify these - system will break
   - Location: `src/session/async_session.py`, `src/db/engine.py`

2. **JWT_SECRET_KEY (REQUIRED)**
   - App crashes on startup without this
   - Must be strong, random, unique per environment
   - No default value provided

3. **Tenant Isolation (REMOVED)**
   - Do NOT re-add tenant filtering
   - Do NOT re-add RBAC middleware
   - System is single-tenant by design

### ⚠️ Known Issues

1. **Multi-Workflow Scheduler (`sitemap_scheduler.py`)**
   - Single point of failure for 3 workflows
   - Recommended: Split into separate schedulers
   - Severity: HIGH

2. **Development Token in Production**
   - Token `"scraper_sky_2024"` works in all environments
   - Background job authentication requirement
   - Severity: CRITICAL

3. **DB Portal Security Exposure**
   - `/api/v3/db-portal/query` has NO authentication
   - Allows arbitrary SQL execution
   - Severity: CATASTROPHIC
   - Recommendation: Add authentication immediately

4. **Logging Configuration**
   - Hardcoded to DEBUG level
   - Ignores `LOG_LEVEL` environment variable
   - No log rotation (disk space risk)
   - Severity: MEDIUM

5. **Missing Rate Limiting**
   - No protection against brute force
   - No API quota enforcement
   - Severity: HIGH

### 📋 Best Practices

1. **Transaction Boundaries**
   - Routers own transactions
   - Services are transaction-aware
   - Background tasks create own sessions

2. **Error Handling**
   - Graceful degradation (continue on individual failures)
   - Detailed logging with exc_info=True
   - Store errors in database for investigation

3. **Async Patterns**
   - Use asyncio.Semaphore for concurrency limits
   - Release DB connections during heavy computation
   - Use background sessions for long-running tasks

4. **Database Queries**
   - Use parameterized queries (SQL injection prevention)
   - Apply execution options for Supavisor compatibility
   - Separate count queries for pagination

5. **External API Integration**
   - Sanitize logs (prevent API key leakage)
   - Handle rate limits and quotas
   - Implement retry logic with exponential backoff

### 🔗 Quick Links

- **API Documentation:** http://localhost:8000/docs
- **Database Portal:** http://localhost:8000/db-portal
- **Health Check:** http://localhost:8000/health
- **Sitemap Viewer:** http://localhost:8000/sitemap-viewer

### 📞 Support Resources

- **Configuration Issues:** See `Docs/CONFIGURATION_QUICK_REFERENCE.md`
- **Scheduler Issues:** See `Docs/Scheduler_Quick_Reference_20251107.md`
- **Integration Issues:** See `Docs/EXTERNAL_INTEGRATIONS_QUICKREF.md`
- **Development Guidance:** See `CLAUDE.md`

---

## Version History

**v3.0.0 (Current)**
- Removed tenant isolation and RBAC
- Added 5 background schedulers
- Implemented dual-status workflow pattern
- Added comprehensive documentation

**v2.0.0**
- Multi-tenant architecture
- RBAC middleware
- Basic workflow implementation

**v1.0.0**
- Initial release
- Single-tenant prototype

---

**Document Status:** ✅ Complete
**Last Review:** 2025-11-07
**Next Review:** As needed for major changes

---

*This architecture documentation was generated through comprehensive codebase exploration and analysis. All information is based on actual code inspection as of 2025-11-07.*
