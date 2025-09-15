# ScraperSky Dual Adapter System Technical Guide
**For AI Partners & Developers**
**Last Updated:** 2025-09-14
**Status:** Production Critical

---

## ⚠️ CRITICAL UNDERSTANDING REQUIRED

**This document contains PRODUCTION TRUTH based on actual code inspection and database analysis. Everything here has been verified against running code and live database schema. Theatre = Failure. Code = Truth.**

---

## What is a Dual Adapter?

A **dual adapter** is a two-field database pattern that controls workflow progression in ScraperSky:

1. **Curation Field** - User-facing status (New, Selected, etc.) - Set by UI/user action
2. **Processing Field** - Background processing status (NULL, Queued, Processing, etc.) - Set by system

**The Pattern:**
```
User sets curation_field="Selected" → System sets processing_field="Queued" → Scheduler processes items with processing_field="Queued"
```

**Purpose:** Decouple user curation decisions from background processing while maintaining workflow control.

---

## Complete Workflow Chain

```
WF1 → WF2 → WF3 → WF4 → WF5 → WF6 → WF7 → WF8
Places Search → Deep Scan → Local Business → Domain → Sitemap → Pages → Page Processing → Contacts
```

**Dual Adapters:** WF2, WF3, WF4, WF5, WF6, WF7 (6 total)

---

## Dual Adapter Configurations (VERIFIED)

### WF2: Places → Deep Scan ✅ FIXED
- **Table:** `places_staging`
- **Model:** `src/models/place.py`
- **Curation Field:** `status` (PlaceStatusEnum: New, Selected, Maybe, Not a Fit, Archived)
- **Processing Field:** `deep_scan_status` (GcpApiDeepScanStatusEnum: Queued, Processing, Completed, Error)
- **Router:** `src/routers/places_staging.py` (lines 363, 440, 653)
- **Scheduler:** `src/services/sitemap_scheduler.py` (line 228)
- **Trigger Logic:** `status="Selected"` → `deep_scan_status="Queued"`
- **Database Enums:** `place_status_enum`, `gcp_api_deep_scan_status`
- **Status:** ✅ **FIXED** - `default=None` (was auto-queuing with `default=Queued`)

### WF3: Local Business → Domain ✅ FIXED
- **Table:** `local_businesses`
- **Model:** `src/models/local_business.py`
- **Curation Field:** `status` (PlaceStatusEnum: New, Selected, etc.)
- **Processing Field:** `domain_extraction_status` (DomainExtractionStatusEnum: Queued, Processing, Completed, Error)
- **Router:** `src/routers/local_businesses.py` (lines 320-330)
- **Scheduler:** `src/services/sitemap_scheduler.py` (processes domain extractions)
- **Trigger Logic:** `status="Selected"` → `domain_extraction_status="Queued"`
- **Status:** ✅ **FIXED** - `default=None` (was auto-queuing with `default=Queued`)

### WF4: Domain → Sitemap Analysis ✅ CORRECT
- **Table:** `domains`
- **Model:** `src/models/domain.py`
- **Curation Field:** `sitemap_curation_status` (SitemapCurationStatusEnum: New, Selected, etc.)
- **Processing Field:** `sitemap_analysis_status` (SitemapAnalysisStatusEnum: queued, processing, submitted, failed)
- **Router:** `src/routers/domains.py` (lines 485-495)
- **Scheduler:** `src/services/domain_sitemap_submission_scheduler.py`
- **Trigger Logic:** `sitemap_curation_status="Selected"` → `sitemap_analysis_status="queued"`
- **Status:** ✅ **CORRECT** - Proper NULL defaults

### WF5: Sitemap Files → Import ✅ CORRECT
- **Table:** `sitemap_files`
- **Model:** `src/models/sitemap.py` (SitemapFile class)
- **Curation Field:** `deep_scrape_curation_status` (SitemapImportCurationStatusEnum: New, Selected, etc.)
- **Processing Field:** `sitemap_import_status` (SitemapImportProcessStatusEnum: Queued, Processing, Complete, Error)
- **Service:** `src/services/sitemap_files_service.py` (lines 336-348)
- **Scheduler:** `src/services/sitemap_import_scheduler.py`
- **Trigger Logic:** `deep_scrape_curation_status="Selected"` → `sitemap_import_status="Queued"`
- **Status:** ✅ **CORRECT** - Proper NULL defaults

### WF6: Pages Creation → Processing ✅ FIXED
- **Table:** `pages`
- **Model:** `src/models/page.py`
- **Curation Field:** `page_curation_status` (PageCurationStatus: New, Selected, etc.)
- **Processing Field:** `page_processing_status` (PageProcessingStatus: Queued, Processing, Complete, Error)
- **Service:** `src/services/sitemap_import_service.py` (lines 211-232)
- **Scheduler:** `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`
- **Trigger Logic:** `page_curation_status="Selected"` → `page_processing_status="Queued"`
- **Status:** ✅ **FIXED** - Was auto-queuing all pages, now requires manual selection

### WF7: Page Processing → Contact Extraction ✅ CORRECT (Special Case)
- **Table:** `pages`
- **Model:** `src/models/page.py`
- **Curation Field:** `page_curation_status`
- **Processing Field:** `page_processing_status`
- **Router:** `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py` (lines 144-148)
- **Scheduler:** `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`
- **Status:** ✅ **CORRECT** - Auto-selects contact pages (business requirement exception)

---

## Database Schema Truth (VERIFIED)

### Enum Values (Queried from Production DB)

**`gcp_api_deep_scan_status` enum:**
- `Queued` (sort order 1)
- `Processing` (sort order 2)
- `Completed` (sort order 3)
- `Error` (sort order 4)

**`place_status_enum` enum:**
- `New` (sort order 1)
- `Selected` (sort order 2)
- `Maybe` (sort order 3)
- `Not a Fit` (sort order 4)
- `Archived` (sort order 5)

**`place_status` enum (different enum!):**
- `New`, `Queued`, `Processing`, `Complete`, `Error`, `Skipped`, `Selected`, `Archived`

---

## Critical Files by Layer

### Models (Layer 1)
- `src/models/place.py` - WF2 dual adapter fields
- `src/models/local_business.py` - WF3 dual adapter fields
- `src/models/domain.py` - WF4 dual adapter fields
- `src/models/sitemap.py` - WF5 dual adapter fields
- `src/models/page.py` - WF6/WF7 dual adapter fields

### Routers (Layer 3)
- `src/routers/places_staging.py` - WF2 curation endpoints
- `src/routers/local_businesses.py` - WF3 curation endpoints
- `src/routers/domains.py` - WF4 curation endpoints
- `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py` - WF7 curation endpoints

### Services (Layer 4)
- `src/services/sitemap_scheduler.py` - WF2 & WF3 background processing
- `src/services/domain_sitemap_submission_scheduler.py` - WF4 background processing
- `src/services/sitemap_import_scheduler.py` - WF5 background processing
- `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py` - WF6/WF7 background processing
- `src/services/sitemap_files_service.py` - WF5 dual adapter logic
- `src/services/sitemap_import_service.py` - WF6 dual adapter logic

---

## Auto-Queuing Anti-Pattern (CRITICAL)

**THE PROBLEM:** Setting processing field defaults to "Queued" instead of NULL causes automatic workflow progression without user curation.

**Broken Pattern:**
```python
# ❌ WRONG - Auto-queues new records
processing_status = Column(
    Enum(ProcessingStatusEnum),
    default=ProcessingStatusEnum.Queued,  # BAD!
    nullable=True
)
```

**Correct Pattern:**
```python
# ✅ CORRECT - Requires manual curation
processing_status = Column(
    Enum(ProcessingStatusEnum),
    default=None,  # NULL until manually queued
    nullable=True
)
```

**Historical Issues Fixed:**
- **WF2:** `deep_scan_status` was `default=Queued` → Fixed to `default=None`
- **WF3:** `domain_extraction_status` was `default=Queued` → Fixed to `default=None`
- **WF6:** Sitemap import service was auto-queuing all pages → Fixed to require manual selection

---

## Audit Checklist for Future AI Partners

### 1. Identify Dual Adapter Fields
```sql
-- Find processing status fields (should be NULL by default)
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name IN ('places_staging', 'local_businesses', 'domains', 'sitemap_files', 'pages')
AND column_name LIKE '%_status';
```

### 2. Check Model Defaults
Look for these patterns in `src/models/*.py`:
```python
# Look for processing status fields with bad defaults
default=SomeEnum.Queued  # ❌ BAD - Auto-queuing issue
default=None             # ✅ GOOD - Manual curation required
```

### 3. Verify Scheduler Queries
Schedulers should ONLY process items with `processing_status = "Queued"`:
```python
# ✅ CORRECT scheduler pattern
.where(Model.processing_status == ProcessingStatusEnum.Queued)
```

### 4. Test Dual Adapter Logic
Check that routers properly implement the dual update:
```python
# ✅ CORRECT dual adapter pattern
if curation_status == Selected:
    item.processing_status = Queued
```

---

## Debugging Commands

### Check Current Processing Queues
```sql
-- WF2: Deep scan queue
SELECT COUNT(*) FROM places_staging WHERE deep_scan_status = 'Queued';

-- WF3: Domain extraction queue
SELECT COUNT(*) FROM local_businesses WHERE domain_extraction_status = 'Queued';

-- WF4: Sitemap analysis queue
SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued';

-- WF5: Sitemap import queue
SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued';

-- WF6/WF7: Page processing queue
SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Queued';
```

### Identify Auto-Queuing Issues
```sql
-- Find records with processing_status set but curation_status still New
SELECT status, deep_scan_status, COUNT(*)
FROM places_staging
WHERE status = 'New' AND deep_scan_status IS NOT NULL
GROUP BY status, deep_scan_status;
```

---

## Configuration for Auto-Mode (Future)

When implementing configurable auto/manual modes per the PRD:

**Manual Mode (Current):**
- New records: `curation_status="New"`, `processing_status=NULL`
- User action required: Set `curation_status="Selected"` → triggers `processing_status="Queued"`

**Auto Mode (Future):**
- New records: `curation_status="New"`, `processing_status=NULL`
- Quality evaluation: If criteria met → Set both `curation_status="Selected"` AND `processing_status="Queued"`

**Key Rule:** NEVER set processing_status="Queued" without also setting curation_status="Selected"

---

## Emergency Procedures

### If Auto-Queuing Detected:
1. **Immediate:** Change model default from `Queued` to `None`
2. **Database Fix:** Update existing records: `UPDATE table SET processing_status = NULL WHERE curation_status = 'New'`
3. **Commit Fix:** Deploy model change to prevent new auto-queued records
4. **Monitor:** Check scheduler logs for unexpected processing volume

### Critical Files to Never Delete:
- Any file with "scheduler" in the name
- Any router file handling status updates
- Model files defining dual adapter fields

---

## Success Indicators

✅ **Healthy Dual Adapter System:**
- New records have processing_status=NULL
- Only "Selected" items have processing_status="Queued"
- Schedulers process expected volumes
- Manual curation controls workflow progression

❌ **Broken Auto-Flow System:**
- New records automatically get processing_status="Queued"
- Background schedulers process all new items immediately
- No manual curation step required
- Workflow progression without user control

---

**Remember: The database and running code are the source of truth. When in doubt, query the actual database and read the actual model definitions. Theatre = Failure. Code = Truth.**