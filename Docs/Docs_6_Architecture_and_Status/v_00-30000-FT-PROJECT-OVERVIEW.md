# ScraperSky Platform: 30,000-Foot Overview

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis_Concise.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis_Concise.md)** - Layer classification
- **[CONVENTIONS_AND_PATTERNS_GUIDE.md](./CONVENTIONS_AND_PATTERNS_GUIDE.md)** - Detailed conventions

## Platform Purpose

ScraperSky is a FastAPI-based web scraping and analytics platform that implements a progressive data enrichment workflow. The system discovers, processes, and enriches web data through a series of specialized workflow stages, each adding additional value to the underlying data.

## Core Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       ScraperSky Platform Architecture                   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
             ┌─────────────────────────────────────────────┐
             │             FastAPI Application             │
             └─────────────────────────────────────────────┘
                                     │
                 ┌──────────────────┴──────────────────┐
                 ▼                                      ▼
    ┌─────────────────────┐                 ┌─────────────────────┐
    │ Layer 3: API Routers│◄───────────────►│Layer 4: Background │
    │                     │                 │      Services       │
    └─────────────────────┘                 └─────────────────────┘
                 │                                     │
                 └──────────────────┬──────────────────┘
                                    ▼
                      ┌─────────────────────────┐
                      │  Layer 4: Services    │
                      └─────────────────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │Layer 1: Models & ENUMs│
                      │      (via ORM)        │
                      └─────────────────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │   Supabase/PostgreSQL   │
                      └─────────────────────────┘
```

### Key Components

1. **Layer 3: API Routers (API Router Layer)**: Handles HTTP requests, defines endpoints with `/api/v3/` prefix, owns transaction boundaries
2. **Layer 4: Background Services**: Implements scheduled tasks using APScheduler, processes queued workflow items asynchronously
3. **Layer 4: Services (Service Layer)**: Contains core business logic, implements workflow-specific processing, transaction-aware
4. **Layer 1: Models & ENUMs (via SQLAlchemy ORM)**: Provides type-safe database access, no raw SQL permitted
5. **Supabase/PostgreSQL**: Underlying database with Supavisor connection pooling

## Progressive Workflow Stages

The core of ScraperSky is its progressive data enrichment pipeline where data moves through defined workflows:

```
┌───────────┐    ┌────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌─────────┐
│ Discovery │ ─► │ Triage │ ─► │ Business Curation │ ─► │ Domain Curation │ ─► │ Sitemap Curation │ ─► │ Results │
└───────────┘    └────────┘    └──────────────────┘    └─────────────────┘    └──────────────────┘    └─────────┘
   [WF1/WF2]      [WF3]             [WF3]                   [WF4]                   [WF5]              [WF7]
```

### Workflow Stages Explained

1. **Discovery (WF1/WF2)**:

   - Initial data collection through Google Maps API integration
   - User-driven search and staging areas
   - Outputs: Basic business records, search history

2. **Triage (WF3)**:

   - Initial filtering and classification of discovered data
   - Determination of processing priority and viability
   - Outputs: Prioritized business records

3. **Business Curation (WF3)**:

   - Enrichment of business entities with additional metadata
   - Verification and normalization of business data
   - Outputs: Validated business records with enhanced attributes

4. **Domain Curation (WF4)**:

   - Domain identification and validation
   - Website discovery and basic analysis
   - Contact information extraction
   - Outputs: Validated domains linked to businesses

5. **Sitemap Curation (WF5)**:

   - Discovery and processing of website sitemaps
   - URL extraction and classification
   - Sitemap structure analysis
   - Outputs: Processed sitemap data and URL inventory

6. **Results (WF7)**:
   - Final processing and presentation of enriched data
   - Export capabilities and reporting
   - Analytics and insights generation
   - Outputs: Comprehensive data sets ready for consumption

## Status Flow Pattern

All workflows follow the Producer-Consumer pattern with consistent status transitions:

```
           ┌───────────┐
           │   IDLE    │◄────────────┐
           └─────┬─────┘             │
                 │                   │
                 ▼                   │
┌─────────┐    ┌───────────┐    ┌────────────┐
│ QUEUED  │───►│ PROCESSING│───►│  PROCESSED │
└─────────┘    └─────┬─────┘    └────────────┘
                     │
                     ▼
              ┌────────────┐
              │   ERROR    │
              └────────────┘
```

## Key Architectural Principles

1. **Producer-Consumer Pattern**: All workflows follow a status-driven pattern where:

   - API endpoints queue items for processing (QUEUED status)
   - Background schedulers process queued items (PROCESSING → PROCESSED/ERROR)

2. **Transaction Management**:

   - Layer 3: Routers own transaction boundaries using `async with session.begin()`
   - Layer 4: Services are transaction-aware but do not create transactions
   - Background tasks manage their own sessions and transactions

3. **Database Access**:

   - Layer 1: Models & ENUMs (via SQLAlchemy ORM) exclusively (NO raw SQL)
   - Connection pooling via Supavisor
   - FastAPI dependency injection for database sessions

4. **API Versioning**:
   - All endpoints use v3 prefix (`/api/v3/*`)
   - Standard FastAPI routing
   - JWT authentication at API gateway only

## Technology Stack

- **Backend**: FastAPI, Python 3.10+, APScheduler
- **ORM**: SQLAlchemy 2.0 with async support
- **Database**: PostgreSQL via Supabase
- **Connection Pooling**: Supavisor
- **Environment**: Docker (development and production)
- **Deployment**: Render.com

## Core Workflows Reference

| Workflow ID | Name                      | Purpose                            | Key Files                                     | Status      |
| ----------- | ------------------------- | ---------------------------------- | --------------------------------------------- | ----------- |
| WF1         | Single Search             | Google Maps API search             | `/src/routers/google_maps_api.py`             | Implemented |
| WF2         | Staging Editor            | Result staging and processing      | `/src/routers/staging_editor.py`              | Implemented |
| WF3         | Local Business Curation   | Business metadata enrichment       | `/src/routers/business_curation.py`           | Implemented |
| WF4         | Domain Curation           | Domain verification and processing | `/src/routers/domain_curation.py`             | Implemented |
| WF5         | Sitemap Curation          | Sitemap discovery and processing   | `/src/routers/modernized_sitemap.py`          | Implemented |
| WF6         | Sitemap Import            | Background sitemap processing      | `/src/schedulers/sitemap_import_scheduler.py` | Implemented |
| WF7         | Page Curation             | Page-level content analysis        | `/src/routers/page_curation.py`               | In Progress |
| WF8         | Domain Content Extraction | Domain crawling and extraction     | `/src/routers/domain_content.py`              | Planned     |

## Data Relationships

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Business   │────►│   Domain    │────►│   Sitemap   │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   Contact   │     │    Page     │
                    └─────────────┘     └─────────────┘
```

## Implementation Status

As of May 2025:

- Backend workflow logic: ~80% complete
- Frontend UI/integration: ~40% complete
- Overall MVP completion: 65-70%

## Additional Resources

For more detailed information, refer to:

- **Architectural Principles**: `/Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md`
- **Workflow Patterns**: `/Docs/Docs_7_Workflow_Canon/PRODUCER_CONSUMER_WORKFLOW_PATTERN.md`
- **Implementation Status**: `/Docs/Docs_6_Architecture_and_Status/0.2_ScraperSky_Architecture_and_Implementation_Status.md`
- **Workflow Cheat Sheet**: `/Docs/Docs_8_Document-X/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md`

---

_Document Version_: 1.0
_Created_: May 8, 2025
_Last Updated_: May 8, 2025
