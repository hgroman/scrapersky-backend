# ScraperSky Lexicon - Quick Reference

> **Purpose**: Say "add sorting to pages" and I know exactly what you mean.

---

## Workflow Quick Reference

| WF# | Concept | Also Known As | DB Table | Model | Router |
|-----|---------|---------------|----------|-------|--------|
| **WF1** | Places/Google Maps | places, gmaps, staging, discovery scan, localminer | `places_staging` | `Place` | `wf1_google_maps_api_router`, `wf1_place_staging_router` |
| **WF3** | Local Businesses | businesses, local biz, LB | `local_businesses` | `LocalBusiness` | `wf3_local_business_router` |
| **WF4** | Domains | domain, sites, websites | `domains` | `Domain` | `wf4_domain_router` |
| **WF5** | Sitemaps | sitemap, sitemap files, XML | `sitemap_files`, `sitemap_urls` | `SitemapFile`, `SitemapUrl` | `wf5_sitemap_*` |
| **WF7** | Pages/Contacts | pages, contacts, page scraper | `pages`, `contacts` | `Page`, `Contact` | `wf7_page_*`, `wf7_email_*` |

---

## Table/Entity Aliases

### Pages Table (`pages` / WF7)
```
You say:              I understand:
-------------------------------------------
pages                 src/models/wf7_page.py → Page model
pages table           Table: pages
pages crud            wf7_page_*_router.py endpoints
page scraper          wf7_page_batch_scraper_router.py
page curation         PageCurationStatus enum
contact scrape        ContactScrapeStatus on Page model
honeybee              Page.honeybee_json, priority_level, path_depth
```

**Key Columns**: `url`, `title`, `page_type`, `page_curation_status`, `page_processing_status`, `contact_scrape_status`, `created_at`, `updated_at`, `last_scan`, `last_modified`

**Sortable Date Fields**: `created_at`, `updated_at`, `last_scan`, `last_modified`

---

### Domains Table (`domains` / WF4)
```
You say:              I understand:
-------------------------------------------
domains               src/models/wf4_domain.py → Domain model
domain crud           wf4_domain_router.py endpoints
sitemap curation      Domain.sitemap_curation_status
domain extraction     Domain.sitemap_analysis_status
hubspot sync          Domain.hubspot_sync_status
```

**Key Columns**: `domain`, `status`, `sitemap_curation_status`, `hubspot_sync_status`, `last_scan`, `created_at`, `updated_at`

**Sortable Date Fields**: `created_at`, `updated_at`, `last_scan`

---

### Places Table (`places_staging` / WF1)
```
You say:              I understand:
-------------------------------------------
places                src/models/wf1_place_staging.py → Place model
places staging        Same (table: places_staging)
gmaps results         Same
discovery scan        wf1_google_maps_api_router.py /search/places
deep scan             Place.deep_scan_status
```

**Key Columns**: `place_id`, `name`, `status`, `deep_scan_status`, `search_time`, `created_at`, `updated_at`

**Sortable Date Fields**: `search_time`, `updated_at`

---

### Local Businesses Table (`local_businesses` / WF3)
```
You say:              I understand:
-------------------------------------------
local businesses      src/models/wf3_local_business.py → LocalBusiness
LB                    Same
businesses            Same
domain extraction     LocalBusiness.domain_extraction_status
```

**Key Columns**: `business_name`, `status`, `domain_extraction_status`, `website_url`, `city`, `state`, `created_at`, `updated_at`

**Sortable Date Fields**: `created_at`, `updated_at`

---

### Sitemaps (`sitemap_files`, `sitemap_urls` / WF5)
```
You say:              I understand:
-------------------------------------------
sitemaps              src/models/wf5_sitemap_file.py → SitemapFile
sitemap files         Same
sitemap urls          SitemapUrl model
deep scrape           SitemapFile.deep_scrape_curation_status (legacy name)
sitemap import        SitemapFile.sitemap_import_status
```

**Key Columns**: `url`, `status`, `deep_scrape_curation_status`, `sitemap_import_status`, `url_count`, `created_at`, `last_processed_at`

**Sortable Date Fields**: `created_at`, `updated_at`, `last_processed_at`, `last_modified`

---

### Contacts (`contacts` / WF7)
```
You say:              I understand:
-------------------------------------------
contacts              src/models/wf7_contact.py → Contact
emails                Same (contacts have emails)
email scanner         wf7_email_scanner_router.py
```

---

## Router/Endpoint Aliases

### WF1 - Google Maps / Places
```
Endpoint Pattern:     /api/v3/localminer-discoveryscan/*
Router:               wf1_google_maps_api_router.py
Alt Router:           wf1_place_staging_router.py

You say:              Endpoint:
-------------------------------------------
search places         POST /search/places
staging list          GET /places/staging
update status         PUT /places/staging/status
batch update          POST /places/staging/batch
queue deep scan       PUT /places/staging/queue-deep-scan
```

### WF3 - Local Businesses
```
Endpoint Pattern:     /api/v3/local-businesses/*
Router:               wf3_local_business_router.py

You say:              Endpoint:
-------------------------------------------
list businesses       GET /
update status         PUT /status
batch update          PUT /status/filtered
```

### WF4 - Domains
```
Endpoint Pattern:     /api/v3/domains/*
Router:               wf4_domain_router.py

You say:              Endpoint:
-------------------------------------------
list domains          GET /
update curation       PUT /sitemap-curation/status
batch curation        PUT /sitemap-curation/status/filtered
```

### WF5 - Sitemaps
```
Endpoint Pattern:     /api/v3/sitemap/* OR /api/v3/sitemaps/* OR /api/v3/sitemap-files/*
Routers:              wf5_sitemap_*.py (multiple)

You say:              Endpoint:
-------------------------------------------
scan sitemap          POST /api/v3/sitemap/scan
sitemap status        GET /api/v3/sitemap/status/{job_id}
import csv            POST /api/v3/sitemaps/import-csv
direct submit         POST /api/v3/sitemaps/direct-submit
list sitemap files    GET /api/v3/sitemap-files/
```

### WF7 - Pages
```
Endpoint Pattern:     /api/v3/pages/* OR /api/v3/batch_page_scraper/* OR /api/v3/modernized_page_scraper/*
Routers:              wf7_page_*.py (multiple)

You say:              Endpoint:
-------------------------------------------
import pages csv      POST /api/v3/pages/import-csv
direct submit page    POST /api/v3/pages/direct-submit
batch scrape          POST /api/v3/batch_page_scraper/scan
scrape status         GET /api/v3/batch_page_scraper/status/{job_id}
```

---

## Status Enum Quick Reference

### User-Facing Curation Statuses (Most Tables)
```python
New → Selected → Maybe → "Not a Fit" → Archived → Completed
```

### Processing/Background Statuses
```python
Queued → Processing → Complete → Error
```

### Contact Scrape Status (Pages)
```python
New → ContactFound | NoContactFound | Error | NotAFit
```

### Page Curation Status
```python
New → Selected → Queued → Processing → Complete → Error → Skipped
```

---

## Common CRUD Operations - What You'd Say

| You Say | What I Do |
|---------|-----------|
| "add sorting by date to pages" | Add `sort_by`, `sort_order` params to `wf7_page_*` router GET endpoint |
| "filter domains by status" | Add `status` query param to `wf4_domain_router.py` GET endpoint |
| "pages table needs filtering" | Add filter params to page list endpoints |
| "sort sitemaps by url count" | Add `sort_by=url_count` to `wf5_sitemap_file_router.py` |
| "batch update local businesses" | Use `PUT /api/v3/local-businesses/status/filtered` |
| "add pagination to places" | Add `limit`, `offset` or `page`, `page_size` params |

---

## File Location Cheat Sheet

```
Models:     src/models/wf{N}_{entity}.py
Routers:    src/routers/wf{N}_{entity}_router.py
Schemas:    src/schemas/wf{N}_{entity}_schemas.py
Services:   src/services/{domain}/{service}.py
Enums:      src/models/enums.py (centralized)
```

---

## Typical CRUD Enhancement Pattern

When you say "add sorting/filtering to X table":

1. **Router** (`src/routers/wf{N}_{entity}_router.py`):
   - Add query params: `sort_by: str = None`, `sort_order: str = "desc"`, `filter_status: str = None`

2. **Apply to query**:
   ```python
   if sort_by:
       order_col = getattr(Model, sort_by, Model.created_at)
       query = query.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
   if filter_status:
       query = query.where(Model.status == filter_status)
   ```

3. **Schema** (if needed): Add to request/response Pydantic models

---

## Quick Terminology Decoder

| Term | Meaning |
|------|---------|
| Curation | User manually reviews/categorizes items (New → Selected → etc.) |
| Processing | Background job running on items |
| Staging | Temporary holding table before promotion |
| Deep scan/scrape | Intensive analysis (more API calls, more data) |
| Import | Bulk loading from CSV/external source |
| Direct submit | Single-item manual submission |
| Batch | Multiple items processed together |
| Honeybee | Page categorization system (contact pages, about pages, etc.) |

---

*Last updated: 2025-11-22*
