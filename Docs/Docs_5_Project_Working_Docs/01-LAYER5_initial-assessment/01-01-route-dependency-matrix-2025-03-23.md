# SCRAPERSKY ROUTE DEPENDENCY MATRIX

## ACTIVE PRODUCTION ROUTES

| Router File | Endpoints | Direct Service Dependencies | Model Dependencies |
|-------------|-----------|---------------------------|-------------------|
| **modernized_sitemap.py** | `/api/v3/sitemap/scan` (POST)<br>`/api/v3/sitemap/status/{job_id}` (GET) | sitemap_processing_service<br>auth_service<br>batch_processor_service | domain.py<br>sitemap.py<br>job.py<br>api_models.py |
| **batch_page_scraper.py** | `/api/v3/batch_page_scraper/scan` (POST)<br>`/api/v3/batch_page_scraper/batch` (POST)<br>`/api/v3/batch_page_scraper/status/{job_id}` (GET)<br>`/api/v3/batch_page_scraper/batch/{batch_id}/status` (GET) | batch_processor_service<br>auth_service<br>user_context_service<br>page_processor | batch_job.py<br>job.py<br>user.py |
| **google_maps_api.py** | `/api/v3/google_maps_api/search` (POST)<br>`/api/v3/google_maps_api/status/{job_id}` (GET)<br>`/api/v3/google_maps_api/staging` (GET)<br>`/api/v3/google_maps_api/update-status` (POST) | places_service<br>places_search_service<br>auth_service<br>job_service<br>error_service | place.py<br>place_search.py<br>user.py |
| **dev_tools.py** | `/api/v3/dev-tools/container/*` (various)<br>`/api/v3/dev-tools/server/status` (GET)<br>`/api/v3/dev-tools/database/*` (various) | user_context_service<br>db_service | N/A |
| **profile.py** | `/api/v3/profiles` (GET)<br>`/api/v3/profiles/{profile_id}` (GET/PUT) | profile_service<br>tenant_isolation | profile.py |
| **sitemap_analyzer.py** | `/api/v1/sitemap-analyzer/analyze` (POST)<br>`/api/v1/sitemap-analyzer/batch` (POST)<br>`/api/v1/sitemap-analyzer/status/{job_id}` (GET) | sitemap_analyzer<br>db_service<br>error_service<br>storage_service<br>user_context_service | domain.py<br>sitemap.py |
| **db_portal.py** | `/api/v1/db-portal/tables` (GET)<br>`/api/v1/db-portal/query` (POST) | db_inspector | N/A |

## REDUNDANT/OBSOLETE ROUTES (SHOULD BE ARCHIVED)

| Router File | Status | Replacement | Notes |
|-------------|--------|-------------|-------|
| **sitemap.py** | OBSOLETE | modernized_sitemap.py | Only contains a deprecated health check endpoint |
| **page_scraper.py** | DEPRECATED | modernized_page_scraper.py | All endpoints redirect to modernized version |
| **modernized_sitemap.bak.3.21.25.py** | BACKUP | modernized_sitemap.py | Backup file with dated extension (.bak) |

## DUPLICATE SERVICE IMPLEMENTATIONS

| Service Type | Active Implementation | Duplicates (Should be Removed) | Notes |
|--------------|------------------------|--------------------------------|-------|
| Error Service | services/error/error_service.py | services/core/error_service.py<br>services/new/error_service.py | Most comprehensive with psycopg2 error handling |
| Validation Service | services/validation/validation_service.py | services/core/validation_service.py<br>services/new/validation_service.py | Used in page_scraper processing service |
| DB Service | services/core/db_service.py | services/db_service.py | Used in sitemap_handler and sitemap_analyzer |
| Sitemap Service | services/sitemap/sitemap_service.py | services/sitemap_service.py | ORM-based vs. simpler implementation |
| Auth Service | services/core/auth_service.py | auth/auth_service.py | Used in multiple router files |

## SIMPLIFIED DEPENDENCY STRUCTURE

```
FastAPI App (main.py)
  ↓
  ↓→ Router Files (modernized_*.py, *.py)
       ↓
       ↓→ Services (service implementations)
            ↓
            ↓→ Models (SQLAlchemy ORM models)
                 ↓
                 ↓→ Database (session, engine)
```

## RECOMMENDATIONS

1. **Router Simplification**:
   - Keep only the active router files
   - Archive or remove obsolete/backup routers

2. **Service Consolidation**:
   - Keep only one implementation per service type
   - Update imports in all dependent files

3. **Transaction Management**:
   - Ensure all endpoints follow the pattern: routers own transactions, services are transaction-aware

4. **Error Handling**:
   - Consolidate on services/error/error_service.py
   - Remove redundant error handlers

5. **Auth Flow**:
   - Standardize on services/core/auth_service.py
   - Remove tenant isolation code (already in progress)
