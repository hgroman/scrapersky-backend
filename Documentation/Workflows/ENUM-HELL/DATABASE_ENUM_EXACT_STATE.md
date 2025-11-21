# DATABASE ENUM EXACT STATE - 2025-11-20 14:41 PST

**Source:** Direct MCP query to production database  
**Purpose:** Map every enum column to routers/services that use it

---

## **CRITICAL FINDINGS**

### **🔴 DIFFERENT ENUM TYPES WITH SAME PURPOSE**

| Purpose | Type 1 | Type 2 | Values Different? |
|---------|--------|--------|-------------------|
| Place Status | `place_status` | `place_status_enum` | ✅ **YES - INCOMPATIBLE** |
| | Values: `{New,Queued,Processing,Complete,Error,Skipped,Selected,Archived}` | Values: `{New,Selected,Maybe,"Not a Fit",Archived}` | |

**This is the root cause of confusion.**

---

## **DATABASE GROUND TRUTH - ALL ENUM COLUMNS**

### **local_businesses (2 enum columns)**

| Column | Enum Type | Values | Nullable | Default |
|--------|-----------|--------|----------|---------|
| `status` | `place_status_enum` | `{New,Selected,Maybe,"Not a Fit",Archived}` | NOT NULL | `'New'` |
| `domain_extraction_status` | `domain_extraction_status` | `{Queued,Processing,Completed,Error}` | NULLABLE | NULL |

**Used by:**
- Router: `src/routers/local_businesses.py`
  - Sets `domain_extraction_status = DomainExtractionStatusEnum.Queued`
  - Filters by `status` for batch updates
- Service: `src/services/domain_extraction_scheduler.py`
  - WHERE `domain_extraction_status == 'Queued'`
  - Updates to `Completed` or `Error`

---

### **places_staging (2 enum columns)**

| Column | Enum Type | Values | Nullable | Default |
|--------|-----------|--------|----------|---------|
| `status` | `place_status` | `{New,Queued,Processing,Complete,Error,Skipped,Selected,Archived}` | NOT NULL | `'New'` |
| `deep_scan_status` | `gcp_api_deep_scan_status` | `{Queued,Processing,Completed,Error}` | NULLABLE | NULL |

**Used by:**
- Service: `src/services/places/places_storage_service.py`
  - Sets `status = PlaceStatusEnum.New`
  - WHERE `Place.status == status` (filter)
  - Updates `place.status = PlaceStatusEnum[status_name]`
- Service: `src/services/deep_scan_scheduler.py`
  - WHERE `deep_scan_status == 'Queued'`
  - Updates to `Completed` or `Error`

---

### **domains (6 enum columns)**

| Column | Enum Type | Values | Nullable | Default |
|--------|-----------|--------|----------|---------|
| `sitemap_analysis_status` | `SitemapAnalysisStatusEnum` | `{pending,queued,processing,submitted,failed}` | NULLABLE | `'pending'` |
| `sitemap_curation_status` | `SitemapCurationStatusEnum` | `{New,Selected,Maybe,"Not a Fit",Archived,Completed}` | NULLABLE | `'New'` |
| `hubspot_sync_status` | `hubspot_sync_status` | `{New,Selected,Queued,Processing,Complete,Error,Skipped}` | NOT NULL | `'New'` |
| `hubspot_processing_status` | `hubspot_sync_processing_status` | `{Queued,Processing,Complete,Error}` | NULLABLE | NULL |
| `content_scrape_status` | `task_status` | `{Queued,InProgress,Completed,Error,ManualReview,Cancelled,Paused,Processing,Complete}` | NULLABLE | `'Queued'` |
| `page_scrape_status` | `task_status` | (same as above) | NULLABLE | `'Queued'` |
| `sitemap_monitor_status` | `task_status` | (same as above) | NULLABLE | `'Queued'` |

**Used by:**
- Router: `src/routers/v3/domains_direct_submission_router.py`
  - Sets `sitemap_curation_status = SitemapCurationStatusEnum.Selected or .New`
  - Sets `sitemap_analysis_status = queued or NULL`
- Router: `src/routers/v3/domains_csv_import_router.py`
  - Sets `sitemap_curation_status = SitemapCurationStatusEnum.New`
- Service: (content_scrape_status, page_scrape_status, sitemap_monitor_status)
  - **NOT USED BY ANY SCHEDULER** (no WHERE clauses found)
  - Only used for status tracking

---

### **sitemap_files (3 enum columns)**

| Column | Enum Type | Values | Nullable | Default |
|--------|-----------|--------|----------|---------|
| `status` | `sitemap_file_status_enum` | `{Pending,Processing,Completed,Error}` | NOT NULL | `'Pending'` |
| `deep_scrape_curation_status` | `SitemapCurationStatusEnum` | `{New,Selected,Maybe,"Not a Fit",Archived,Completed}` | NULLABLE | `'New'` |
| `sitemap_import_status` | `sitemapimportprocessingstatus` | `{Queued,Processing,Complete,Error}` | NULLABLE | NULL |

**Used by:**
- Router: `src/routers/v3/sitemaps_direct_submission_router.py`
  - Sets `deep_scrape_curation_status = SitemapImportCurationStatusEnum.Selected or .New`
- Router: `src/routers/v3/sitemaps_csv_import_router.py`
  - Sets `deep_scrape_curation_status = SitemapImportCurationStatusEnum.New`
- Service: `src/services/sitemap_files_service.py`
  - WHERE `deep_scrape_curation_status == filter_value`
  - Batch updates `deep_scrape_curation_status`
- Service: `src/services/sitemap_import_scheduler.py`
  - WHERE `sitemap_import_status == 'Queued'`
  - Updates to `Complete` or `Error`

---

### **pages (4 enum columns)**

| Column | Enum Type | Values | Nullable | Default |
|--------|-----------|--------|----------|---------|
| `page_type` | `page_type_enum` | `{contact_root,career_contact,about_root,services_root,menu_root,pricing_root,team_root,legal_root,wp_prospect,unknown}` | NULLABLE | NULL |
| `contact_scrape_status` | `contact_scrape_status` | `{New,ContactFound,NoContactFound,Error,NotAFit}` | NOT NULL | `'New'` |
| `page_curation_status` | `page_curation_status` | `{New,Selected,Queued,Processing,Complete,Error,Skipped}` | NOT NULL | `'New'` |
| `page_processing_status` | `page_processing_status` | `{Queued,Processing,Complete,Error,Filtered}` | NULLABLE | NULL |

**Used by:**
- Router: `src/routers/v2/WF7_V2_L3_1of1_PagesRouter.py`
  - Updates `page.page_curation_status = request.status`
  - Sets `page.page_processing_status = PageProcessingStatus.Queued`
- Router: `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py`
  - WHERE `page_curation_status == filter`
  - WHERE `page_processing_status == filter`
  - WHERE `page_type == filter`
- Service: `src/services/WF7_V2_L4_1of2_PageCurationService.py`
  - Sets `page.contact_scrape_status = 'ContactFound' or 'NoContactFound'`
  - Sets `page.page_processing_status = PageProcessingStatus.Error or .Complete`
- Service: `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`
  - WHERE `page_processing_status == 'Queued'`
  - Updates to `Complete` or `Error`
- Service: `src/services/sitemap_import_service.py`
  - Sets `page_processing_status = PageProcessingStatus.Filtered`
  - Sets `page_curation_status = PageCurationStatus.New`

---

### **contacts (13 enum columns)**

| Column | Enum Type | Values | Nullable | Default |
|--------|-----------|--------|----------|---------|
| `email_type` | `contact_email_type_enum` | `{SERVICE,CORPORATE,FREE,UNKNOWN}` | NULLABLE | NULL |
| `contact_curation_status` | `contact_curation_status` | `{New,Queued,Processing,Complete,Error,Skipped}` | NOT NULL | `'New'` |
| `contact_processing_status` | `contact_processing_status` | `{Queued,Processing,Complete,Error}` | NULLABLE | NULL |
| `hubspot_sync_status` | `hubspot_sync_status` | `{New,Selected,Queued,Processing,Complete,Error,Skipped}` | NOT NULL | `'New'` |
| `hubspot_processing_status` | `hubspot_sync_processing_status` | `{Queued,Processing,Complete,Error}` | NULLABLE | NULL |
| `brevo_sync_status` | `crm_sync_status` | `{New,Selected,Queued,Processing,Complete,Error,Skipped}` | NOT NULL | `'New'` |
| `brevo_processing_status` | `crm_processing_status` | `{Queued,Processing,Complete,Error}` | NULLABLE | NULL |
| `mautic_sync_status` | `crm_sync_status` | (same) | NOT NULL | `'New'` |
| `mautic_processing_status` | `crm_processing_status` | (same) | NULLABLE | NULL |
| `n8n_sync_status` | `crm_sync_status` | (same) | NOT NULL | `'New'` |
| `n8n_processing_status` | `crm_processing_status` | (same) | NULLABLE | NULL |
| `debounce_validation_status` | `crm_sync_status` | (same) | NULLABLE | `'New'` |
| `debounce_processing_status` | `crm_processing_status` | (same) | NULLABLE | NULL |

**Used by:**
- Service: `src/services/crm/hubspot_sync_scheduler.py`
  - WHERE `hubspot_processing_status == 'Queued'`
- Service: `src/services/crm/brevo_sync_scheduler.py`
  - WHERE `brevo_processing_status == 'Queued'`
- Service: `src/services/crm/n8n_sync_scheduler.py`
  - WHERE `n8n_processing_status == 'Queued'`
- Service: `src/services/email_validation/debounce_scheduler.py`
  - WHERE `debounce_processing_status == 'Queued'`

---

## **CRITICAL WHERE CLAUSES (What Broke Production)**

All schedulers use this pattern from `scheduler_loop.py`:

```python
.where(getattr(model, status_field_name) == queued_status)
```

**This requires:**
1. Model enum type name MUST match database enum type name
2. Model MUST have `native_enum=True`
3. Model MUST have `values_callable=lambda x: [e.value for e in x]`

**Schedulers that use WHERE clauses:**

| Scheduler | Model | Field | DB Enum Type | Status |
|-----------|-------|-------|--------------|--------|
| domain_extraction_scheduler | LocalBusiness | domain_extraction_status | `domain_extraction_status` | ✅ |
| deep_scan_scheduler | Place | deep_scan_status | `gcp_api_deep_scan_status` | ✅ |
| sitemap_import_scheduler | SitemapFile | sitemap_import_status | `sitemapimportprocessingstatus` | ✅ |
| PageCurationScheduler | Page | page_processing_status | `page_processing_status` | ✅ |
| hubspot_sync_scheduler | Contact | hubspot_processing_status | `hubspot_sync_processing_status` | ✅ |
| brevo_sync_scheduler | Contact | brevo_processing_status | `crm_processing_status` | ✅ |
| n8n_sync_scheduler | Contact | n8n_processing_status | `crm_processing_status` | ✅ |
| debounce_scheduler | Contact | debounce_processing_status | `crm_processing_status` | ✅ |

---

## **THE PROBLEM**

### **places_staging.status**

**Database:** `place_status` with values `{New,Queued,Processing,Complete,Error,Skipped,Selected,Archived}`

**Model (user changed):** `place_status_enum`

**This is a MISMATCH and will break:**
- `places_storage_service.py` line 392: WHERE `Place.status == status`
- Any batch status updates

### **local_businesses.status**

**Database:** `place_status_enum` with values `{New,Selected,Maybe,"Not a Fit",Archived}`

**Model:** `place_status_enum` ✅ MATCHES

**But:** Uses DIFFERENT values than `places_staging.status`!

---

## **RECOMMENDATION**

**You have TWO different "place status" enums:**

1. **`place_status`** - Used by `places_staging` - Workflow statuses (Queued, Processing, etc.)
2. **`place_status_enum`** - Used by `local_businesses` - Curation statuses (Selected, Maybe, etc.)

**These serve DIFFERENT purposes and should have DIFFERENT names.**

**Option 1: Keep them separate (RECOMMENDED)**
- `places_staging.status` → Keep as `place_status`
- `local_businesses.status` → Keep as `place_status_enum`
- Update model to match database

**Option 2: Rename for clarity**
- `places_staging.status` → Rename to `place_workflow_status`
- `local_businesses.status` → Rename to `place_curation_status`
- Update both database and models

**DO NOT try to merge them - they have different values and purposes.**
