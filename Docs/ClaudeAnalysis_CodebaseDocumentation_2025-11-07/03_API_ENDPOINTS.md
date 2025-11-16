# API Endpoints - Complete Reference

**Analysis Date:** November 7, 2025
**API Version:** v3 (primary), v2 (legacy)
**Total Routers:** 20 files
**Total Endpoints:** 80+ endpoints
**Authentication:** JWT-based (dependency injection pattern)

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Endpoint Categories](#endpoint-categories)
3. [Authentication Patterns](#authentication-patterns)
4. [Request/Response Patterns](#requestresponse-patterns)
5. [Complete Endpoint Reference](#complete-endpoint-reference)

---

## API Overview

### Base URL Structure

```
Production: https://your-domain.render.com
Development: http://localhost:8000

API Endpoints: /api/v3/{resource}
Legacy Endpoints: /api/v2/{resource}
Documentation: /docs (Swagger UI)
Alternative Docs: /redoc (ReDoc)
```

### Router Inclusion Patterns

ScraperSky follows two router prefix patterns:

**Pattern 1 - Full Prefix in Router:**
```python
router = APIRouter(prefix="/api/v3/domains", tags=["domains"])
app.include_router(router)  # Include without prefix
```

**Pattern 2 - Resource-Only Prefix:**
```python
router = APIRouter(prefix="/batch_page_scraper", tags=["batch"])
app.include_router(router, prefix="/api/v3")  # Add API prefix
```

---

## Endpoint Categories

### 1. Domain Management (3 endpoints)

**Router:** `domains.py`
**Base:** `/api/v3/domains`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v3/domains` | ✓ | List domains with pagination, filtering, sorting |
| PUT | `/api/v3/domains/sitemap-curation/status` | ✓ | Batch update sitemap curation status |
| PUT | `/api/v3/domains/sitemap-curation/status/filtered` | ✓ | Update domains matching filter criteria |

**Key Features:**
- Pagination: `page`, `size` (default 20, max 100)
- Sorting: `sort_by` (domain, created_at, updated_at, status), `sort_desc` boolean
- Filters: `sitemap_curation_status`, `domain_filter` (partial match)
- Dual-status: Setting to "Selected" auto-queues for sitemap analysis

---

### 2. Local Business Management (3 endpoints)

**Router:** `local_businesses.py`
**Base:** `/api/v3/local-businesses`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v3/local-businesses` | ✓ | List businesses with pagination/filtering |
| PUT | `/api/v3/local-businesses/status` | ✓ | Batch update business status |
| PUT | `/api/v3/local-businesses/status/filtered` | ✓ | Update businesses matching filters |

**Dual-status:** Setting to "Selected" queues for domain extraction

---

### 3. Sitemap Processing (12+ endpoints)

**Routers:** `modernized_sitemap.py`, `batch_sitemap.py`, `sitemap_files.py`

#### Single Sitemap Scan (`modernized_sitemap.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v3/sitemap/scan` | Dev bypass | Initiate sitemap scan |
| GET | `/api/v3/sitemap/status/{job_id}` | No | Check job status |

#### Batch Sitemap Scan (`batch_sitemap.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v3/sitemap/batch/create` | ✓ | Create batch sitemap processing |
| GET | `/api/v3/sitemap/batch/status/{batch_id}` | ✓ | Get batch status |

#### Sitemap Files CRUD (`sitemap_files.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v3/sitemap-files/` | ✓ | List sitemap files (paginated) |
| POST | `/api/v3/sitemap-files/` | ✓ | Create new sitemap file |
| GET | `/api/v3/sitemap-files/{id}` | ✓ | Get single sitemap file |
| PUT | `/api/v3/sitemap-files/{id}` | ✓ | Update sitemap file |
| DELETE | `/api/v3/sitemap-files/{id}` | ✓ | Delete sitemap file |
| PUT | `/api/v3/sitemap-files/sitemap_import_curation/status` | ✓ | Batch update curation status |
| PUT | `/api/v3/sitemap-files/sitemap_import_curation/status/filtered` | ✓ | Update files matching filters |

**Filters:** `domain_id`, `deep_scrape_curation_status`, `url_contains`, `sitemap_type`, `discovery_method`

---

### 4. Page Scraping (8+ endpoints)

**Routers:** `modernized_page_scraper.py`, `batch_page_scraper.py`, `v3/WF7_V3_L3_1of1_PagesRouter.py`

#### Single Page Scraper (`modernized_page_scraper.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v3/modernized_page_scraper/scan` | ✓ | Scan single domain |
| POST | `/api/v3/modernized_page_scraper/batch` | ✓ | Batch scan multiple domains |
| GET | `/api/v3/modernized_page_scraper/status/{job_id}` | ✓ | Get job status |
| GET | `/api/v3/modernized_page_scraper/batch/{batch_id}/status` | ✓ | Get batch status |

#### Batch Page Scraper (`batch_page_scraper.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v3/batch_page_scraper/scan` | ✓ | Scan single domain (raw SQL) |
| GET | `/api/v3/batch_page_scraper/status/{job_id}` | ✓ | Get job status (raw SQL) |
| POST | `/api/v3/batch_page_scraper/batch` | ✓ | Create batch |
| GET | `/api/v3/batch_page_scraper/batch/{batch_id}/status` | ✓ | Get batch status |
| GET | `/api/v3/batch_page_scraper/health` | No | Health check |

#### Page Curation (`v3/WF7_V3_L3_1of1_PagesRouter.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v3/pages/` | ✓ | List pages with filtering |
| PUT | `/api/v3/pages/status` | ✓ | Batch update page curation status |
| PUT | `/api/v3/pages/status/filtered` | ✓ | Update pages matching filters |

**Filters:** `page_curation_status`, `page_processing_status`, `page_type`, `url_contains`

---

### 5. Google Maps / Places (10+ endpoints)

**Routers:** `google_maps_api.py`, `places_staging.py`

#### Google Maps API (`google_maps_api.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v3/localminer-discoveryscan/search/places` | ✓ | Search for places |
| GET | `/api/v3/localminer-discoveryscan/search/status/{job_id}` | ✓ | Get search job status |
| GET | `/api/v3/localminer-discoveryscan/places/staging` | ✓ | Get places from staging |
| POST | `/api/v3/localminer-discoveryscan/places/staging/status` | ✓ | Update place status |
| POST | `/api/v3/localminer-discoveryscan/places/staging/batch` | ✓ | Batch update places |
| GET | `/api/v3/localminer-discoveryscan/health` | No | Health check |
| GET | `/api/v3/localminer-discoveryscan/results/{job_id}` | ✓ | Get job results |
| GET | `/api/v3/localminer-discoveryscan/search/history` | ✓ | Get search history |
| GET | `/api/v3/localminer-discoveryscan/debug/info` | ✓ Dev | Debug info |

#### Places Staging (`places_staging.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/places/staging` | ✓ | List all staged places |
| GET | `/places/staging/{job_id}` | No | List places for discovery job |
| PUT | `/places/staging/status` | ✓ | Batch update place status |
| PUT | `/places/staging/queue-deep-scan` | ✓ | Queue places for deep scan |
| PUT | `/places/staging/status/filtered` | ✓ | Update places matching filters |

---

### 6. Contact Management (7 endpoints)

**Router:** `v3/contacts_router.py`
**Base:** `/api/v3/contacts`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v3/contacts/` | ✓ | Create new contact |
| GET | `/api/v3/contacts/{contact_id}` | ✓ | Get single contact |
| PUT | `/api/v3/contacts/{contact_id}` | ✓ | Update contact |
| DELETE | `/api/v3/contacts/{contact_id}` | ✓ | Delete contact |
| GET | `/api/v3/contacts` | ✓ | List contacts with filtering |
| PUT | `/api/v3/contacts/status` | ✓ | Batch update contact status |
| PUT | `/api/v3/contacts/status/filtered` | ✓ | Update contacts matching filters |

**Filters:** `contact_curation_status`, `contact_processing_status`, `hubspot_sync_status`, `email_type`, `domain_id`, `page_id`, `email_contains`, `name_contains`, `has_gmail`

---

### 7. Database & Utilities (20+ endpoints)

#### DB Portal (`db_portal.py`) ⚠️ NO AUTHENTICATION
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v3/db-portal/tables` | **NO** | List all database tables |
| GET | `/api/v3/db-portal/tables/{table_name}` | **NO** | Get table schema |
| GET | `/api/v3/db-portal/tables/{table_name}/sample` | **NO** | Get sample data |
| POST | `/api/v3/db-portal/query` | **NO** | Execute read-only SQL |
| POST | `/api/v3/db-portal/tables/{table_name}/validate` | **NO** | Validate schema |
| GET | `/api/v3/db-portal/tables/{table_name}/model` | **NO** | Generate Pydantic model |
| GET | `/api/v3/db-portal/health` | **NO** | Health check |

**⚠️ CRITICAL SECURITY ISSUE:** This router has NO authentication on any endpoint, including arbitrary SQL execution.

#### Dev Tools (`dev_tools.py`)
| Method | Path | Auth | Dev Only | Description |
|--------|------|----------|----------|-------------|
| POST | `/api/v3/dev-tools/container/rebuild` | ✓ | ✓ | Rebuild Docker container |
| POST | `/api/v3/dev-tools/container/restart` | ✓ | ✓ | Restart container |
| GET | `/api/v3/dev-tools/container/health` | No | No | Check container health |
| GET | `/api/v3/dev-tools/server/status` | ✓ | No | Get server status |
| GET | `/api/v3/dev-tools/logs` | ✓ | No | Get filtered logs |
| GET | `/api/v3/dev-tools/schema` | ✓ | No | Get database schema |
| GET | `/api/v3/dev-tools/routes` | ✓ | No | Get route information |
| GET | `/api/v3/dev-tools/scheduler_status` | ✓ | ✓ | Get APScheduler status |
| POST | `/api/v3/dev-tools/trigger-sitemap-import/{id}` | No | No | Trigger sitemap import |

**15+ additional dev tool endpoints** - see router file for complete list

#### Profiles (`profile.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v3/profiles` | ✓ | List profiles |
| GET | `/api/v3/profiles/{id}` | ✓ | Get single profile |
| POST | `/api/v3/profiles` | ✓ | Create profile |
| PUT | `/api/v3/profiles/{id}` | ✓ | Update profile |
| DELETE | `/api/v3/profiles/{id}` | ✓ | Delete profile |

#### Vector DB (`vector_db_ui.py`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v3/vector-db/patterns` | No | Get all patterns |
| POST | `/api/v3/vector-db/search` | No | Search patterns by similarity |
| GET | `/api/v3/vector-db/pattern/{id}` | No | Get detailed pattern info |

---

## Authentication Patterns

### JWT Authentication

**Implementation:** Dependency-based using `get_current_user` from `src/auth/jwt_auth.py`

```python
from src.auth.jwt_auth import get_current_user

@router.get("/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    # current_user contains: id, user_id, email, tenant_id, roles, permissions
    pass
```

**Token Header:**
```
Authorization: Bearer <jwt_token>
```

**Development Token (works in all environments):**
```
Token: "scraper_sky_2024"
```

⚠️ **CRITICAL:** Development token works in production (known security issue)

### Public Endpoints (No Auth Required)

- `/health`
- `/health/database`
- `/docs`, `/redoc`, `/openapi.json`
- `/api/v3/db-portal/*` (⚠️ SECURITY ISSUE)
- `/api/v3/vector-db/*`
- Some dev-tools endpoints
- Sitemap status check endpoints

### Development Mode Bypass

Some routers check `SCRAPER_SKY_DEV_MODE=true` and bypass authentication:
- `modernized_sitemap.py` - scan endpoint
- `modernized_page_scraper.py` - scan endpoint
- `google_maps_api.py` - some endpoints

---

## Request/Response Patterns

### Pagination Pattern

**Standard Query Parameters:**
```
?page=1&size=20          # Page-based (page 1-indexed)
?offset=0&limit=100      # Offset-based
```

**Standard Response:**
```json
{
  "items": [...],
  "total": 1234,
  "page": 1,
  "size": 20,
  "pages": 62
}
```

### Filtering Pattern

**Enum-based filters:**
```
?status_filter=New
?page_curation_status=Selected
?contact_processing_status=Queued
```

**Text search filters:**
```
?domain_filter=example.com      # Partial match (ILIKE)
?url_contains=contact           # URL substring
?email_contains=@gmail          # Email substring
```

**Boolean filters:**
```
?has_gmail=true
?is_active=true
```

### Sorting Pattern

```
?sort_by=updated_at&sort_desc=true    # Descending
?sort_by=domain&sort_dir=asc          # Ascending
```

**Allowed sort fields (validated to prevent SQL injection):**
- Common: `created_at`, `updated_at`, `status`
- Domain-specific: varies by endpoint

### Batch Update Pattern

**Batch by IDs:**
```json
POST /resource/status
{
  "ids": ["uuid1", "uuid2", "uuid3"],
  "status": "Selected"
}
```

**Response:**
```json
{
  "updated_count": 3,
  "queued_count": 3  // If dual-status, how many queued for processing
}
```

**Batch by Filter:**
```json
PUT /resource/status/filtered
{
  "status": "Selected",
  "status_filter": "New",
  "domain_filter": "example"
}
```

### Job Status Pattern

**Initiate Job:**
```json
POST /resource/scan
{
  "base_url": "https://example.com",
  "max_pages": 1000
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status_url": "/resource/status/uuid",
  "created_at": "2025-11-07T..."
}
```

**Check Status:**
```json
GET /resource/status/{job_id}

Response:
{
  "job_id": "uuid",
  "status": "running",
  "progress": 0.5,
  "created_at": "...",
  "updated_at": "...",
  "metadata": {...}
}
```

### Error Response Pattern

**Standard Error:**
```json
{
  "detail": "Error message"
}
```

**Detailed Error:**
```json
{
  "detail": {
    "message": "Human-readable error",
    "error": "Technical detail"
  }
}
```

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error": true
}
```

---

## HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 202 | Accepted | Background task accepted |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input, enum mismatch |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Dev-only endpoint in non-dev mode |
| 404 | Not Found | Resource not found, no filter matches |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Database errors, unexpected exceptions |

---

## API Best Practices

### ✅ Well-Designed Patterns

1. **Dual-Status Auto-Queue** - Setting curation status to "Selected" automatically queues processing
2. **Pagination Consistency** - Standard `page`/`size` or `offset`/`limit` across all list endpoints
3. **Filter Validation** - Enum filters prevent invalid values
4. **Batch Operations** - Both ID-based and filter-based batch updates supported
5. **Job Tracking** - Consistent job_id + status_url pattern for async operations
6. **Error Standardization** - Consistent JSON error responses

### ⚠️ Security Concerns

1. **DB Portal Exposed** - `/api/v3/db-portal/query` allows arbitrary SQL with NO authentication
2. **Development Token** - `"scraper_sky_2024"` works in production
3. **Inconsistent Auth** - Easy to forget `Depends(get_current_user)` on new endpoints
4. **No Rate Limiting** - No protection against brute force or abuse
5. **Exception Details** - Full exception messages may leak sensitive info

---

## Related Documentation

- **Complete Endpoint Reference** - See exploration results in conversation history for detailed endpoint documentation
- **Authentication** - See `06_AUTHENTICATION_SECURITY.md`
- **Service Layer** - See `04_SERVICE_LAYER.md` for business logic behind endpoints
- **Database** - See `02_DATABASE_SCHEMA.md` for data models

---

*This is a summary reference. For complete endpoint-by-endpoint documentation with request/response examples, see the API endpoint exploration results in the conversation history above.*
