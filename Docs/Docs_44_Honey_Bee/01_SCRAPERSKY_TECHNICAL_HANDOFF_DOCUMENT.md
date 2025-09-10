# ScraperSky Technical Handoff Document

**Date:** September 6, 2025  
**Purpose:** External AI Consultation on Page Categorization System  
**Status:** Production System Analysis

---

## Executive Summary

ScraperSky is a production FastAPI-based business intelligence platform that processes business websites through a 7-stage workflow pipeline. The system currently suffers from inefficient processing that creates database bloat by scraping ALL sitemap pages indiscriminately. This document provides factual technical specifications for implementing intelligent page categorization to optimize processing efficiency.

**Core Problem:** System processes every URL from business sitemaps regardless of intelligence value, causing 90%+ waste in database storage and ScraperAPI costs.

**Solution Goal:** Implement AI-powered page categorization to process only high-value pages (contact, about, services, pricing, team) while filtering out low-value content (blog posts, PDFs, images, archives).

---

## System Architecture Overview

### Technology Stack
- **Backend:** FastAPI with Python 3.11+
- **Database:** Supabase PostgreSQL with connection pooling via Supavisor (port 6543)
- **Web Scraping:** ScraperAPI integration with cost controls
- **Background Processing:** APScheduler with multiple workflow schedulers
- **Session Management:** AsyncPG with specific connection parameters

### Database Connection Pattern (CRITICAL)
```python
# MANDATORY connection parameters for Supavisor compatibility
postgresql+asyncpg://user:pass@host:6543/db?raw_sql=true&no_prepare=true&statement_cache_size=0
```

### 7-Layer Architecture
1. **Layer 0:** Documentation (Chronicle)
2. **Layer 1:** Models & ENUMs (Data persistence)
3. **Layer 2:** Schemas (Request/response validation)
4. **Layer 3:** Routers (HTTP endpoints)
5. **Layer 4:** Services & Schedulers (Business logic)
6. **Layer 5:** Configuration (Settings and environment)
7. **Layer 6:** UI Components (Frontend interfaces)
8. **Layer 7:** Testing (Quality assurance)

---

## Data Flow Pipeline

### Stage 1: Business Discovery (WF1-WF3)
1. **Google Maps API Search** → `/api/v3/google-maps-api/search/places`
2. **Places Storage** → `places_staging` table with curation status
3. **Local Business Curation** → User selects promising businesses

### Stage 2: Domain Extraction (WF4)
1. **Domain Extraction Service** processes selected places
2. **Domain Storage** → `domains` table with metadata
3. **Domain Curation** → User reviews and selects domains

### Stage 3: Sitemap Discovery (WF5-WF6)
1. **Sitemap Discovery Service** finds sitemaps for selected domains
2. **Sitemap Storage** → `sitemap_files` table
3. **Sitemap Import Service** extracts ALL URLs → `pages` table (**INEFFICIENCY SOURCE**)

### Stage 4: Contact Extraction (WF7)
1. **Page Curation Service** processes pages marked "Selected"
2. **ScraperAPI Integration** fetches page content
3. **Contact Extraction** creates contact records
4. **Database Storage** → `contacts` table

---

## Database Schema Specifications

### Core Tables

#### `domains` Table
```sql
-- Primary business domain tracking
id UUID PRIMARY KEY
domain TEXT UNIQUE NOT NULL  -- e.g., "example.com"
title TEXT
description TEXT
sitemap_curation_status ENUM('New','Selected','Maybe','Not a Fit','Archived','Completed')
hubspot_sync_status ENUM('New','Processing','Completed','Error')
-- Metadata fields for website analysis
email_addresses TEXT[]
phone_numbers TEXT[]
social_links JSONB
tech_stack JSONB
```

#### `pages` Table (**OPTIMIZATION TARGET**)
```sql
-- Individual page tracking - SOURCE OF BLOAT
id UUID PRIMARY KEY
domain_id UUID → domains.id
url TEXT NOT NULL  -- Full page URL
page_type TEXT     -- Current: unused, Target: categorization field
page_curation_status ENUM('New','Selected','Maybe','Not a Fit','Archived','Completed')
page_processing_status ENUM('Queued','Processing','Completed','Error')
sitemap_file_id UUID → sitemap_files.id
-- Content analysis fields
title TEXT
description TEXT
has_contact_form BOOLEAN
has_comments BOOLEAN
word_count INTEGER
additional_json JSONB
```

#### `contacts` Table
```sql
-- Extracted contact information
id UUID PRIMARY KEY
domain_id UUID → domains.id
page_id UUID → pages.id
name TEXT
email TEXT
phone_number TEXT
```

#### `places_staging` Table
```sql
-- Google Maps API results
place_id TEXT UNIQUE
name TEXT
formatted_address TEXT
business_type TEXT
status ENUM('New','Selected','Maybe','Not a Fit','Archived')
deep_scan_status ENUM('Queued','Processing','Completed','Error')
```

### Relationship Mapping
```
places_staging → domains (via domain extraction)
domains → sitemap_files (one-to-many)
sitemap_files → pages (one-to-many) ← BLOAT SOURCE
pages → contacts (one-to-many)
```

---

## Service Layer Analysis

### Critical Services

#### `SitemapImportService` (**PRIMARY OPTIMIZATION TARGET**)
**Location:** `src/services/sitemap_import_service.py:115-145`

**Current Logic (INEFFICIENT):**
```python
# Processes ALL URLs from sitemap without filtering
pages_to_insert: List[Page] = []
for sitemap_url_record in extracted_urls:
    page_url = str(sitemap_url_record.loc)
    page_data = {
        "domain_id": domain_id,
        "url": page_url,  # ALL URLs imported indiscriminately
        "lead_source": "sitemap_import"
    }
    pages_to_insert.append(Page(**page_data))
```

**Impact:** Creates Page records for every sitemap URL (typically 100-2000+ per domain)

#### `PageCurationService` (**COST CONTROL IMPLEMENTED**)
**Location:** `src/services/WF7_V2_L4_1of2_PageCurationService.py:22-100`

**Current Logic:**
```python
# Only processes pages marked "Selected" by user
# Uses ScraperAPI with cost controls
enable_js = os.getenv('WF7_ENABLE_JS_RENDERING', 'false').lower() == 'true'
async with ScraperAPIClient() as scraper_client:
    html_content = await scraper_client.fetch(page_url, render_js=enable_js)
    
# Extracts contacts or creates unique "notfound_" placeholders
if real_emails:
    contact_email = real_emails[0]
else:
    page_id_short = str(page_id).split('-')[0]
    contact_email = f"notfound_{page_id_short}@{domain_name}"
```

---

## API Endpoint Structure

### Current API Pattern: `/api/v3/{resource}`

#### Workflow Endpoints by Stage
**WF1-WF3: Business Discovery**
- `POST /api/v3/google-maps-api/search/places` - Start search
- `GET /api/v3/places/staging` - View results
- `PUT /api/v3/places/staging/status` - Curate selections

**WF4: Domain Processing**
- `GET /api/v3/domains` - List domains
- `PUT /api/v3/domains/status` - Update domain status

**WF5-WF6: Sitemap Processing**
- `GET /api/v3/sitemap-files/` - List sitemap files
- `PUT /api/v3/sitemap-files/sitemap_import_curation/status` - Batch status updates
- `POST /api/v3/sitemap/batch/create` - Batch processing

**WF7: Contact Extraction**
- `GET /api/v2/pages` - List pages for curation (V2 endpoint)
- `PUT /api/v2/pages/curation-status` - Mark pages "Selected"
- Background scheduler processes selected pages

### Router Architecture
**Location:** `src/routers/` with sub-versioning in `/v2/` and `/v3/`

**Main Application Setup:** `src/main.py` includes all routers with proper prefixing

---

## Background Processing Architecture

### Scheduler System
**Shared Instance:** `src/scheduler_instance.py` - Single APScheduler for all workflows

### Active Schedulers
1. **Domain Scheduler** - Processes domain discovery queue
2. **Sitemap Scheduler** - Discovers sitemaps for selected domains  
3. **Domain Sitemap Submission Scheduler** - Links domains to sitemaps
4. **Sitemap Import Scheduler** - Imports URLs from sitemaps (**BLOAT SOURCE**)
5. **Page Curation Scheduler** - Processes selected pages for contact extraction

### Processing Pattern
```python
# Universal Background Pattern
async def run_job_loop(session_func, job_func, batch_size=10):
    """Standard background processing loop"""
    while True:
        items = fetch_items_with_status("Queued", batch_size)
        for item in items:
            update_status(item, "Processing")
            try:
                result = await job_func(item, session)
                update_status(item, "Completed")
            except Exception as e:
                update_status(item, "Error")
```

---

## Current System Performance Metrics

### Database Bloat Evidence
- **Domain:** `newportortho.com` 
- **Pages Created:** ~500+ URLs from sitemap
- **Contact Results:** Majority "notfound_" placeholder contacts
- **Processing Efficiency:** <10% of pages yield real contact information
- **Storage Waste:** ~90% of Page records provide no business value

### ScraperAPI Cost Analysis
- **Base Cost:** 1 credit per request
- **Premium Features:** 5-10x multiplier (now disabled by default)
- **JavaScript Rendering:** 10-25x multiplier (configurable)
- **Volume Impact:** Processing 500 pages = 500+ credits per domain

---

## Proposed Page Categorization System

### Business Intelligence Categories

#### High-Value Pages (PROCESS)
- **Contact Pages** - `/contact`, `/contact-us`, `/get-in-touch`
- **About Pages** - `/about`, `/about-us`, `/team`, `/company`  
- **Service Pages** - `/services`, `/products`, `/solutions`
- **Pricing Pages** - `/pricing`, `/plans`, `/rates`
- **Location Pages** - `/locations`, `/offices`, `/store-locator`

#### Medium-Value Pages (SELECTIVE)
- **FAQ Pages** - `/faq`, `/help`, `/support`
- **Testimonials** - `/testimonials`, `/reviews`, `/case-studies`
- **Careers** - `/careers`, `/jobs`, `/employment`

#### Low-Value Pages (FILTER OUT)
- **Blog Content** - `/blog/`, `/news/`, `/articles/`
- **Media Files** - `.pdf`, `.jpg`, `.png`, `.mp4`
- **Legal Pages** - `/privacy`, `/terms`, `/legal`
- **Archive Pages** - `/archive/`, `/category/`, `/tag/`
- **Administrative** - `/admin/`, `/wp-admin/`, `/dashboard/`

### Implementation Requirements

#### Database Schema Enhancement
```sql
-- Add to pages table
ALTER TABLE pages ADD COLUMN page_category TEXT;
ALTER TABLE pages ADD COLUMN category_confidence FLOAT;
ALTER TABLE pages ADD COLUMN ai_classification_metadata JSONB;

-- Create enum for categories
CREATE TYPE page_category_enum AS ENUM (
    'contact', 'about', 'services', 'pricing', 'location',
    'faq', 'testimonials', 'careers', 
    'blog', 'media', 'legal', 'archive', 'administrative',
    'unknown'
);
```

#### Service Enhancement
```python
# Enhance SitemapImportService with categorization
class SitemapImportService:
    def __init__(self):
        self.categorizer = PageCategorizer()
    
    async def process_single_sitemap_file(self, sitemap_file_id, session):
        # Existing logic...
        for sitemap_url_record in extracted_urls:
            page_url = str(sitemap_url_record.loc)
            
            # NEW: Categorize before creating Page record
            category = self.categorizer.categorize_url(page_url)
            
            # Only create Page records for high/medium value categories
            if category in ['contact', 'about', 'services', 'pricing', 'location', 'faq', 'testimonials', 'careers']:
                page_data = {
                    "domain_id": domain_id,
                    "url": page_url,
                    "page_category": category,
                    "lead_source": "sitemap_import_filtered"
                }
                pages_to_insert.append(Page(**page_data))
```

---

## Configuration Management

### Environment Variables (Production)
```bash
# Database Connection (CRITICAL)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_POOLER_HOST=aws-0-us-east-1.pooler.supabase.com
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=postgres.xxx
SUPABASE_DB_PASSWORD=xxx

# ScraperAPI Cost Control
SCRAPER_API_ENABLE_PREMIUM=false
SCRAPER_API_ENABLE_JS_RENDERING=false
SCRAPER_API_MAX_RETRIES=1
SCRAPER_API_COST_CONTROL_MODE=true

# WF7 Processing Control
WF7_ENABLE_JS_RENDERING=false
WF7_SCRAPER_API_MAX_CONCURRENT=10

# Scheduler Configuration
SITEMAP_SCHEDULER_INTERVAL_MINUTES=60
SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE=5
PAGE_CURATION_SCHEDULER_BATCH_SIZE=10
```

### File System Structure
```
src/
├── models/           # Layer 1 - Database models
├── routers/          # Layer 3 - API endpoints  
├── services/         # Layer 4 - Business logic
├── config/           # Layer 5 - Configuration
├── scraper/          # Web scraping utilities
├── session/          # Database session management
└── utils/            # Shared utilities
```

---

## Production Deployment Context

### Docker Configuration
- **Base Image:** Python 3.11+ with FastAPI
- **Port:** 8000 (containerized)
- **Environment:** Production deployment on Render.com
- **Health Checks:** `/health/database` endpoint available

### Monitoring and Logging
- **Logging:** Structured logging via `src/config/logging_config.py`
- **Error Tracking:** Comprehensive exception handling per layer
- **Performance Metrics:** Database connection pooling monitoring

---

## Critical Implementation Notes

### Database Connection Requirements
The system **MUST** use Supavisor connection pooling with these exact parameters:
- `raw_sql=true` - Use raw SQL for complex queries
- `no_prepare=true` - Disable prepared statements
- `statement_cache_size=0` - Control statement caching

**VIOLATION OF THESE PARAMETERS WILL BREAK PRODUCTION**

### Authentication System
- JWT token-based authentication
- Dependency injection pattern (not middleware)
- Development mode bypass available
- RBAC system removed - no tenant isolation

### Scheduler Management
- All workflows share single APScheduler instance
- Background jobs use `run_job_loop` SDK pattern
- Status updates follow dual-status pattern (Queued → Processing → Completed/Error)

---

## Optimization Strategy Recommendations

### Phase 1: URL-Based Pre-Filtering
Implement intelligent URL pattern matching in `SitemapImportService` to filter out obvious low-value pages before database insertion.

### Phase 2: Content-Based Classification  
For ambiguous URLs, implement lightweight content analysis using ScraperAPI to determine page category before full processing.

### Phase 3: Machine Learning Enhancement
Train classification model on page content patterns to improve categorization accuracy over time.

### Expected Impact
- **Database Reduction:** 70-90% fewer Page records
- **Cost Reduction:** 70-90% fewer ScraperAPI calls
- **Processing Efficiency:** Focus resources on high-value content
- **Contact Quality:** Higher percentage of real vs. placeholder contacts

---

## Integration Points for External AI

### Recommended Approach
1. **Analyze existing SitemapImportService logic** for insertion points
2. **Design PageCategorizer service** following Layer 4 architectural patterns
3. **Implement URL pattern matching** with regex-based classification
4. **Add database fields** for category tracking and confidence scoring
5. **Update frontend interfaces** to display categorization results
6. **Monitor performance impact** through existing logging infrastructure

### API Integration Points
- Enhance `/api/v3/sitemap-files/` endpoints with categorization data
- Add filtering parameters to `/api/v2/pages` for category-based queries
- Implement categorization analytics in admin interfaces

---

**Document Status:** FACTUAL - Based on production codebase analysis  
**Next Action:** External AI can use this technical specification to design and implement page categorization optimization
