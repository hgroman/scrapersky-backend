# Database Schema - Complete Reference

**Analysis Date:** November 7, 2025
**Database:** PostgreSQL 15+ (Supabase)
**ORM:** SQLAlchemy 2.0+ (Async)
**Total Tables:** 14 active tables
**Total Models:** 12 active models (+ removed RBAC models)

---

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Core Entity Models](#core-entity-models)
3. [Supporting Models](#supporting-models)
4. [Enum Definitions](#enum-definitions)
5. [Relationship Mapping](#relationship-mapping)
6. [Indexes and Constraints](#indexes-and-constraints)
7. [Database Patterns](#database-patterns)

---

## Schema Overview

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     CORE DOMAIN ENTITY                       │
│                      Domain                                  │
│  (1) ──jobs──→ Job (M)                                       │
│  (1) ──pages──→ Page (M)                                     │
│  (1) ──sitemap_files──→ SitemapFile (M)                     │
│  (M) ←──batch──(1) BatchJob                                  │
│  (M) ←──tenant──(1) Tenant                                   │
│  (M) ←──local_business_id──(1) LocalBusiness               │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────┐      ┌───────────┐     ┌──────────────┐
    │  Job   │      │   Page    │     │ SitemapFile  │
    │(Many)  │      │ (Many)    │     │   (Many)     │
    └────────┘      │           │     │              │
        │           │  (1)──────┼────→contacts      │
        │           │     Contact(1)  │              │
        │           │       (M)       │              │
        │           │           │     │  (1)──────┐  │
        │           │           │     │    SitemapUrl
        │           │           │     │     (Many) │
        │           └───────────┘     └──────────────┘
        │
        ▼
    ┌──────────────┐
    │  BatchJob    │ ◄─── One BatchJob contains Many Jobs
    │              │       One BatchJob contains Many Domains
    └──────────────┘
```

### Tables Summary

| Table | Rows (typical) | Primary Use | Key Relationships |
|-------|----------------|-------------|-------------------|
| domains | 1,000s | Website entities | → pages, sitemap_files, jobs |
| pages | 10,000s | Page URLs | → domain, contacts |
| contacts | 1,000s | Contact info | → page |
| sitemap_files | 1,000s | Sitemap metadata | → domain, sitemap_urls |
| sitemap_urls | 100,000s | URLs from sitemaps | → sitemap_file |
| local_businesses | 1,000s | Google Places | → domains (via domain_id) |
| places_staging | 1,000s | Places staging | → place_searches |
| jobs | 10,000s | Job tracking | → domain, batch_job |
| batch_jobs | 100s | Batch tracking | → jobs, domains |
| tenants | 1 (single tenant) | Legacy multi-tenant | None (isolation removed) |
| profiles | 10s | User profiles | None |
| place_searches | 100s | Search history | → places_staging |

---

## Core Entity Models

For complete details on all models including:
- All columns and their types
- Constraints (PK, FK, unique, nullable)
- Relationships with cascade behaviors
- Default values and server defaults
- Special columns (JSONB, Arrays, Enums)
- Class methods and utilities

**See the comprehensive database schema analysis in the conversation history above**, which includes:

### 1. Domain Model
- Table: `domains`
- 40+ columns including metadata, social links, tech stack detection
- Workflow status fields: sitemap_analysis_status, sitemap_curation_status, hubspot_sync_status
- JSONB fields: domain_metadata, tech_stack
- Array fields: email_addresses[], phone_numbers[]
- Relationships: 1:M with Jobs, Pages, SitemapFiles

### 2. Page Model
- Table: `pages`
- Page content and metadata
- Contact form detection, schema markup, word count
- Page type categorization (contact, about, services, etc.)
- Workflow status: page_curation_status, page_processing_status, contact_scrape_status
- JSONB fields: additional_json, honeybee_json
- Relationships: M:1 with Domain, 1:M with Contacts

### 3. Contact Model
- Table: `contacts`
- Email, phone, name, context
- Email type classification (SERVICE, CORPORATE, FREE, UNKNOWN)
- Workflow status: contact_curation_status, contact_processing_status, hubspot_sync_status
- Relationships: M:1 with Page

### 4. SitemapFile Model
- Table: `sitemap_files`
- Sitemap discovery and metadata
- Discovery method tracking (robots.txt, common paths, etc.)
- Sitemap type (INDEX, STANDARD, IMAGE, VIDEO, NEWS)
- Processing status, priority, url_count
- Workflow status: status, deep_scrape_curation_status, sitemap_import_status
- Relationships: M:1 with Domain, 1:M with SitemapUrls

### 5. SitemapUrl Model
- Table: `sitemap_urls`
- Individual URLs from sitemaps
- lastmod, changefreq, priority_value from sitemap XML
- Image, video, news counts
- Processing status and priority
- Relationships: M:1 with SitemapFile

### 6. LocalBusiness Model
- Table: `local_businesses`
- Rich Google Places data (40+ fields)
- Hours of operation (7 day fields)
- Service options, amenities, highlights arrays
- Status: PlaceStatusEnum, domain_extraction_status
- JSONB: additional_json
- Relationships: 1:M with Domains (via domain reference)

### 7. Place Model (Staging)
- Table: `places_staging`
- Initial Google Places search results
- Basic place info (name, address, rating)
- Status: PlaceStatusEnum, deep_scan_status
- JSONB: raw_data (full API response)
- Relationships: M:1 with PlaceSearch

### 8. Job Model
- Table: `jobs`
- Job tracking and progress
- Dual ID system: integer PK + UUID job_id
- Status: pending, running, complete, failed
- JSONB: result_data, job_metadata
- Relationships: M:1 with Domain and BatchJob

### 9. BatchJob Model
- Table: `batch_jobs`
- Batch processing tracking
- Dual ID system: integer PK + UUID batch_id
- Counters: total_domains, completed_domains, failed_domains
- Progress calculation: (completed + failed) / total
- JSONB: batch_metadata, options
- Relationships: 1:M with Jobs and Domains

---

## Enum Definitions

### Complete Enum List (18+ enums)

**Contact/Email Enums:**
- `ContactEmailTypeEnum`: SERVICE, CORPORATE, FREE, UNKNOWN
- `ContactCurationStatus`: New, Queued, Processing, Complete, Error, Skipped
- `ContactProcessingStatus`: Queued, Processing, Complete, Error

**Domain Enums:**
- `DomainStatusEnum`: pending, processing, completed, error
- `SitemapAnalysisStatusEnum`: pending, queued, processing, submitted, failed
- `SitemapCurationStatusEnum`: New, Selected, Maybe, Not a Fit, Archived, Completed
- `DomainExtractionStatusEnum`: Pending, Queued, Processing, Submitted, Failed

**Page Enums:**
- `PageTypeEnum`: CONTACT_ROOT, CAREER_CONTACT, ABOUT_ROOT, SERVICES_ROOT, MENU_ROOT, PRICING_ROOT, TEAM_ROOT, LEGAL_ROOT, WP_PROSPECT, UNKNOWN
- `PageCurationStatus`: New, Selected, Queued, Processing, Complete, Error, Skipped
- `PageProcessingStatus`: Queued, Processing, Complete, Error, Filtered
- `ContactScrapeStatus`: New, ContactFound, NoContactFound, Error, NotAFit

**Sitemap Enums:**
- `SitemapFileStatusEnum`: New, Processing, Complete, Error
- `SitemapImportCurationStatusEnum`: New, Queued, Processing, Complete, Error, Skipped
- `SitemapImportProcessStatusEnum`: Queued, Processing, Complete, Error
- `SitemapType`: INDEX, STANDARD, IMAGE, VIDEO, NEWS
- `DiscoveryMethod`: ROBOTS_TXT, COMMON_PATH, SITEMAP_INDEX, HTML_LINK, MANUAL

**Place Enums:**
- `PlaceStatusEnum`: New, Selected, Maybe, Not a Fit, Archived
- `GcpApiDeepScanStatusEnum`: Pending, Running, Complete, Failed

**HubSpot Enums:**
- `HubSpotSyncStatus`: New, Queued, Processing, Complete, Error, Skipped
- `HubSpotProcessingStatus`: Queued, Processing, Complete, Error

**Task Enums:**
- `TaskStatus`: PENDING, RUNNING, COMPLETE, FAILED, MANUAL_REVIEW, CANCELLED, PAUSED, PROCESSING, COMPLETE_ALT

---

## Relationship Mapping

### Foreign Key Relationships

| Parent Model | Relationship | Child Model | Cascade | Notes |
|--------------|--------------|-------------|---------|-------|
| Domain | 1:M | Job | None | Jobs reference domains |
| Domain | 1:M | Page | delete-orphan | Pages deleted with domain |
| Domain | 1:M | SitemapFile | delete-orphan | Sitemaps deleted with domain |
| Domain | M:1 | BatchJob | None | Many domains per batch |
| Page | 1:M | Contact | delete-orphan | Contacts deleted with page |
| SitemapFile | 1:M | SitemapUrl | delete-orphan | URLs deleted with sitemap |
| Job | M:1 | BatchJob | None | Many jobs per batch |
| Place | M:1 | PlaceSearch | None | Places from searches |
| LocalBusiness | 1:1 | Domain | None | Via domain_id reference |

### Indexes

**Heavily Indexed Tables:**
- **domains**: domain, tenant_id, batch_id, local_business_id, sitemap_analysis_status, sitemap_curation_status, hubspot_sync_status
- **pages**: domain_id, sitemap_file_id, page_type, page_curation_status, page_processing_status, contact_scrape_status, priority_level, path_depth
- **contacts**: domain_id, page_id, email, contact_curation_status, contact_processing_status, hubspot_sync_status, hubspot_processing_status
- **sitemap_files**: domain_id, job_id, status, deep_scrape_curation_status, sitemap_import_status, tenant_id
- **sitemap_urls**: sitemap_id, domain_id, status, tenant_id

### Unique Constraints

| Table | Unique Column(s) | Purpose |
|-------|------------------|---------|
| domains | domain | Prevent duplicate domains |
| local_businesses | place_id | Prevent duplicate Google Places |
| places_staging | place_id | Prevent duplicate staged places |
| batch_jobs | batch_id | External batch identifier |
| jobs | job_id | External job identifier |

---

## Database Patterns

### 1. BaseModel Mixin

All models inherit from `BaseModel` which provides:
```python
id = Column(UUID, primary_key=True, default=uuid.uuid4)
created_at = Column(DateTime, server_default=func.now())
updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

**Exceptions:** Job, BatchJob, Place use Integer PKs

### 2. Dual-Status Workflow Pattern

Many entities have two status fields:
- **Curation Status** (user-facing): New, Selected, Maybe, etc.
- **Processing Status** (internal): Queued, Processing, Complete, Error

**Examples:**
- Pages: `page_curation_status` + `page_processing_status`
- Contacts: `contact_curation_status` + `contact_processing_status`
- Sitemaps: `deep_scrape_curation_status` + `sitemap_import_status`

**Pattern:** Setting curation to "Selected" auto-queues processing status to "Queued"

### 3. Metadata Storage Pattern

JSONB fields for flexible data:
- Domain: `domain_metadata` (alias: meta_json), `tech_stack`
- Page: `additional_json`, `honeybee_json`
- SitemapFile: `tags`
- SitemapUrl: `tags`
- LocalBusiness: `additional_json`
- Place: `raw_data`
- Job: `result_data`, `job_metadata`
- BatchJob: `batch_metadata`, `options`

### 4. Array Field Pattern

PostgreSQL ARRAY types for lists:
- Domain: `email_addresses[]`, `phone_numbers[]`
- Page: `schema_types[]`, `inbound_links[]`, `outbound_links[]`
- LocalBusiness: `extra_categories[]`, `service_options[]`, `highlights[]`, `popular_for[]`, `accessibility[]`, `offerings[]`, `dining_options[]`, `amenities[]`, `atmosphere[]`
- Place: `tags[]`

### 5. Timestamp Conventions

```python
# Base timestamps (all models)
created_at = Column(DateTime, server_default=func.now())
updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# Activity timestamps
last_scan = Column(DateTime, default=func.now())
last_processed_at = Column(DateTime)
discovered_at = Column(DateTime)
last_checked_at = Column(DateTime)

# Workflow timestamps
start_time = Column(DateTime)
end_time = Column(DateTime)
search_time = Column(DateTime, default=datetime.utcnow)
```

### 6. Tenant Isolation (Removed)

**Historical Note:**
- All models still have `tenant_id` column
- **Default value:** `550e8400-e29b-41d4-a716-446655440000`
- **No enforcement:** Queries do not filter by tenant_id
- **RBAC removed:** Role-based access control models commented out
- **Single-tenant:** System now operates as single-tenant by design

**Do NOT re-add tenant isolation without architectural review.**

### 7. UUID Strategy

**UUID Primary Keys:**
- Domain, Page, Contact, SitemapFile, SitemapUrl, LocalBusiness, Profile use UUID PKs
- Generated via `uuid.uuid4()` (Python) or `gen_random_uuid()` (PostgreSQL)

**Dual ID Pattern:**
- Job: Integer PK + `job_id` UUID
- BatchJob: Integer PK + `batch_id` UUID
- Allows both internal integer references and external UUID references

**Exception:**
- Place: Integer PK (legacy Google Places integration)

### 8. Cascade Delete Behavior

**Delete Cascades:**
- Domain deletion cascades to: Pages, SitemapFiles
- Page deletion cascades to: Contacts
- SitemapFile deletion cascades to: SitemapUrls
- All use SQLAlchemy `cascade="all, delete-orphan"`

**SET NULL:**
- Job.domain_id SET NULL on Domain delete
- Job.batch_id SET NULL on BatchJob delete
- Domain.batch_id SET NULL on BatchJob delete

---

## Schema Best Practices

### ✅ Well-Designed Patterns

1. **Workflow Status Tracking** - Dual-status pattern enables user curation + automated processing
2. **Flexible Metadata** - JSONB fields allow schema evolution without migrations
3. **Proper Indexing** - Status fields, foreign keys, and lookup columns indexed
4. **Timestamp Tracking** - Comprehensive audit trail with multiple timestamp fields
5. **Cascade Deletes** - Proper cleanup of dependent records
6. **UUID External IDs** - Stable references for API clients

### ⚠️ Considerations

1. **Removed Tenant Isolation** - Columns remain but enforcement removed (intentional)
2. **Dual ID Systems** - Job/BatchJob have both integer and UUID IDs (historical)
3. **Array Fields** - PostgreSQL-specific (not portable to other databases)
4. **JSONB Heavy** - Many models use JSONB for extensibility (validate externally)
5. **Integer Place PKs** - Inconsistent with other models using UUIDs

---

## Database Connection

**CRITICAL:** This system uses Supavisor connection pooling with mandatory parameters:

```python
execution_options={
    "isolation_level": "READ COMMITTED",
    "no_prepare": True,
    "raw_sql": True,
}

connect_args={
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
}
```

**Never modify these parameters** - they are required for Supavisor compatibility.

**See:** `01_ARCHITECTURE.md` "Database Architecture" section and `07_CONFIGURATION.md` for connection details.

---

## Related Documentation

- **Complete Database Schema Analysis** - See exploration results in conversation history
- **Configuration** - See `07_CONFIGURATION.md` for connection settings
- **Architecture** - See `01_ARCHITECTURE.md` "Database/Model Layer" section
- **Service Layer** - See `04_SERVICE_LAYER.md` for database access patterns

---

*This is a summary reference. For complete field-by-field documentation of all 12 models, see the comprehensive database schema analysis in the exploration results above.*
