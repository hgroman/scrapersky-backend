> ⚠️ **SOURCE OF TRUTH**
> This document overrides any conflicting information in summaries.
> Code is final authority; update THIS doc if it diverges.

# Domain Content Extraction Service - Implementation Constitution

## 🔍 Zero Assumptions Mandate

⚠️ **CRITICAL REQUIREMENT: ZERO ASSUMPTIONS PERMITTED** ⚠️

This constitution establishes a **ZERO ASSUMPTIONS** policy. The implementing AI must:

1. Make NO assumptions about architectural patterns beyond explicit documentation
2. Request clarification for ANY ambiguity before proceeding
3. Never create "convenience" mechanisms that deviate from established patterns
4. Follow the document hierarchy for conflict resolution

## 📋 Document Hierarchy

| #   | Document                      | Authority               | Location                                                                                                                                                                   |
| --- | ----------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | AI Collaboration Constitution | Primary                 | [`../Docs_8_Document-X/8.0-AI-COLLABORATION-CONSTITUTION.md`](../Docs_8_Document-X/8.0-AI-COLLABORATION-CONSTITUTION.md)                                                   |
| 2   | Session Context Document      | Session-specific        | [`../Docs_8_Document-X/8.1-AI-SESSION-CONTEXT-PAGE-CURATION.md`](../Docs_8_Document-X/8.1-AI-SESSION-CONTEXT-PAGE-CURATION.md)                                             |
| 3   | Workflow Builder Cheat Sheet  | Implementation template | [`../Docs_8_Document-X/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md`](<../Docs_8_Document-X/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md>) |
| 4   | Core Architecture Guides      | Reference               | [`../Docs_1_AI_GUIDES/`](../Docs_1_AI_GUIDES/)                                                                                                                             |
| 5   | This Constitution             | Service-specific        | Current document                                                                                                                                                           |

**When conflicts arise between documents, the document with the LOWER NUMBER in this table takes precedence.**

## 🌐 Workflow Context

ScraperSky's progressive data enrichment follows a defined workflow sequence:

```
    Discovery → Triage → Business Curation → Domain Curation → Sitemap Curation → Results
                                               ^
                                               |
                         Domain Content Extraction Service (integrates here)
```

**Reference**: For complete workflow overview, see [`../Docs_6_Architecture_and_Status/00-30000-FT-PROJECT_OVERVIEW.md`](../Docs_6_Architecture_and_Status/00-30000-FT-PROJECT_OVERVIEW.md)

## 🔧 Implementation Requirements

Follow the standard 6-phase implementation process from the Workflow Builder Cheat Sheet:

**Phase 0: Exploratory Crawling & Field Discovery**
1. Run the quick‑prototype crawler against ≤ 10 domains.
2. Save raw HTML + parsed JSON to `./tmp/domain_content/extraction_results.json`.
3. Human (or higher‑context AI) reviews the JSON and approves a canonical field list.
4. ONLY AFTER approval, proceed to Phase 1.

**Phase 1: Database Schema**

• All DB code MUST follow the [ABSOLUTE ORM REQUIREMENT](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)

#### Schema Requirements

Implement the following database changes:

1. **Domains Table Extensions**:

   - `content_extraction_status` (ENUM): Tracks processing status
   - `content_extraction_error` (TEXT): Stores error message
   - `last_crawled` (TIMESTAMP): Records crawl timestamp
   - `metadata` (JSONB): Stores extracted metadata

2. **New Contacts Table**:

   - Primary key, domain reference, contact details fields

3. **New SocialMedia Table**:

   - Primary key, domain reference, platform details fields

4. **Required Enum Values**:
   - `Queued`
   - `Processing`
   - `Complete`
   - `Error`
   - `Skipped`

#### Migration File

Create a timestamped migration file in Supabase migrations directory:

```
supabase/migrations/YYYYMMDDHHMMSS_domain_content_extraction_schema.sql
```

**Reference**: For migration standards, see [`../Docs_1_AI_GUIDES/07-DATABASE-MIGRATIONS.md`](../Docs_1_AI_GUIDES/07-DATABASE-MIGRATIONS.md)

> Authority: Constitution > Session Context > Cheat-Sheet > This Section

### Phase 2: Service Layer

• All DB code MUST follow the [ABSOLUTE ORM REQUIREMENT](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)

`src/services/domain_content_service.py`

- `DomainContentService` class with methods:
  - `process_domain`: Process a single domain
  - `update_domain_status`: Update domain status
- Use `setup_logging()` from `src/config/logging_config.py`

1. `process_domain`: Main processing method that handles:

   - Domain record retrieval
   - Status updates (PROCESSING → PROCESSED/ERROR)
   - Content extraction
   - Results storage

2. Extraction methods:
   - `extract_emails`
   - `extract_social_media`
   - `extract_metadata`

**CRITICAL**: Services accept sessions but DO NOT create transactions.

**Logging Setup**: All service methods should implement proper logging:

```python
from src.config.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

# Use logging within methods
logger.info(f"Processing domain: {domain_id}")
logger.error(f"Error processing domain: {str(e)}")
```

**Reference**: For service layer patterns, see [`../Docs_1_AI_GUIDES/08-SERVICE-LAYER.md`](../Docs_1_AI_GUIDES/08-SERVICE-LAYER.md)

> Authority: Constitution > Session Context > Cheat-Sheet > This Section

### Phase 3: API Router Layer

Implement `DomainContentRouter` in `src/routers/domain_content.py` with:

1. `POST /api/v3/domain-content/process/{domain_id}`: Queue for processing
2. `GET /api/v3/domain-content/status/{domain_id}`: Check status
3. `GET /api/v3/domain-content/results/{domain_id}`: Get results

**CRITICAL**: Routers MUST own transaction boundaries with `async with session.begin()`.

**Logging Setup**: Use `setup_logging()` from `src/config/logging_config.py`

**Reference**: For router patterns, see [`../Docs_1_AI_GUIDES/09-API-ROUTERS.md`](../Docs_1_AI_GUIDES/09-API-ROUTERS.md)

> Authority: Constitution > Session Context > Cheat-Sheet > This Section

### Phase 4: Background Scheduler

Implement `DomainContentScheduler` in `/src/schedulers/domain_content_scheduler.py` with:

1. `process_pending_domains`: Poll for QUEUED domains and process them
2. `_process_single_domain`: Process individual domain

Configure scheduler settings in [`../../src/config/scheduler_settings.py`](../../src/config/scheduler_settings.py):

```python
# Import settings from the config file rather than using hard-coded values
from src.config.settings import settings

# Reference the configuration values
poll_interval_seconds = settings.DOMAIN_SCHEDULER_INTERVAL_SECONDS  # Default: 60
concurrency_limit = settings.DOMAIN_SCHEDULER_CONCURRENCY_LIMIT    # Default: 5
```

**CRITICAL**: Background tasks MUST manage their own sessions and transaction boundaries.

**Reference**: For scheduler architecture, see [`../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md`](../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md)

> Authority: Constitution > Session Context > Cheat-Sheet > This Section

### Phase 5: Application Integration

1. Register router in [`../../src/main.py`](../../src/main.py):

   ```python
   from src.routers.domain_content import router as domain_content_router
   app.include_router(domain_content_router)
   ```

2. Register scheduler in [`../../src/schedulers/__init__.py`](../../src/schedulers/__init__.py):
   ```python
   from src.schedulers.domain_content_scheduler import DomainContentScheduler
   domain_content_scheduler = DomainContentScheduler()
   scheduler.add_job(domain_content_scheduler.process_pending_domains, 'interval', seconds=60)
   ```

**Reference**: For application integration standards, see [`../Docs_1_AI_GUIDES/10-MAIN-APP-INTEGRATION.md`](../Docs_1_AI_GUIDES/10-MAIN-APP-INTEGRATION.md)

> Authority: Constitution > Session Context > Cheat-Sheet > This Section

## 📈 Implementation Decisions

For this specific implementation:

| Decision        | Value                             | Rationale                                 |
| --------------- | --------------------------------- | ----------------------------------------- |
| Concurrency     | 5 domains                         | Balance throughput with resource usage    |
| Crawl depth     | Homepage + direct links (depth 1) | Practical balance of data vs speed        |
| Rate limiting   | 2 seconds between requests        | Avoid overwhelming target servers         |
| Error handling  | Continue with partial results     | Maximize data extraction                  |
| Results storage | Hybrid: structured tables + JSONB | Balance query efficiency with flexibility |

## ✅ Verification Checklist

Before completion, verify:

- [ ] All database changes occur only after Phase 0 field‑list approval
- [ ] Service methods accept session parameters
- [ ] Routers own transaction boundaries
- [ ] Background scheduler creates its own sessions
- [ ] API endpoints follow v3 prefix standard
- [ ] All architectural patterns are followed

## 🔄 References to Architectural Principles

All implementation must adhere to these non-negotiable architectural principles:

1. **Producer-Consumer Pattern**: [`../Docs_1_AI_GUIDES/02-PRODUCER-CONSUMER-PATTERN.md`](../Docs_1_AI_GUIDES/02-PRODUCER-CONSUMER-PATTERN.md)
2. **Transaction Management**: [`../Docs_1_AI_GUIDES/03-DATABASE-TRANSACTIONS.md`](../Docs_1_AI_GUIDES/03-DATABASE-TRANSACTIONS.md)
3. **Database Connections**: [`../Docs_1_AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md`](../Docs_1_AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md)
4. **API Versioning**: [`../Docs_1_AI_GUIDES/05-API-VERSIONING.md`](../Docs_1_AI_GUIDES/05-API-VERSIONING.md)
5. **Authentication**: [`../Docs_1_AI_GUIDES/06-AUTHENTICATION.md`](../Docs_1_AI_GUIDES/06-AUTHENTICATION.md)
6. **Scheduler Architecture**: [`../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md`](../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md)

---

**Document Version**: 2.0
**Last Updated**: May 8, 2025
**Created By**: Henry Groman & Cascade

> Authority: Constitution > Session Context > Cheat-Sheet > This Document
