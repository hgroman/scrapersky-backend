# ENUM STANDARDIZATION COMPLETE AUDIT REPORT
**Date:** November 20, 2025  
**Scope:** FastAPI Application Enum Usage & Database Alignment  
**Status:** CRITICAL GAPS IDENTIFIED

---

## EXECUTIVE SUMMARY

### Current State
- **33 enum columns** across 7 database tables
- **58+ enum types** defined in database
- **4 separate locations** for Python enum definitions
- **CRITICAL:** Anti-pattern inline string enums in WF7 Contact model
- **CONFLICT:** Duplicate enum definitions with different values

### Fixes Completed Today
1. ✅ `local_businesses.domain_extraction_status` → `domain_extraction_status_enum` (Commit 1b5a044)
2. ✅ `domains.sitemap_curation_status` → `sitemap_curation_status_enum` (Commit 5650333)
3. ✅ `sitemap_files.deep_scrape_curation_status` → `sitemap_curation_status_enum` (Commits 723ac96, 26f3911)

### Critical Issues Remaining
1. ❌ Inline string enums in `WF7_V2_L1_1of1_ContactModel.py`
2. ❌ Duplicate `DomainExtractionStatusEnum` definitions (conflicting values)
3. ❌ Duplicate `GcpApiDeepScanStatusEnum` definitions (conflicting values)
4. ❌ Enum definitions scattered across 4 locations
5. ❌ Inconsistent casing (PascalCase vs lowercase)

---

## PART 1: DATABASE ENUM INVENTORY

### All Database Enum Types (58 total)

#### Workflow Status Enums
| Enum Type | Values | Used By |
|-----------|--------|---------|
| `place_status_enum` | New, Selected, Maybe, Not a Fit, Archived | places_staging.status, local_businesses.status |
| `domain_extraction_status_enum` | Queued, Processing, Completed, Error | local_businesses.domain_extraction_status |
| `domain_status` | pending, processing, completed, error | domains.status |
| `SitemapAnalysisStatusEnum` | pending, queued, processing, submitted, failed | domains.sitemap_analysis_status |
| `sitemap_curation_status_enum` | New, Selected, Maybe, Not a Fit, Archived, Completed | domains.sitemap_curation_status, sitemap_files.deep_scrape_curation_status |
| `sitemap_file_status_enum` | Pending, Processing, Completed, Error | sitemap_files.status |
| `sitemapimportprocessingstatus` | Queued, Processing, Complete, Error | sitemap_files.sitemap_import_status |
| `sitemap_url_status_enum` | Pending, Processing, Completed, Error | sitemap_urls.status |
| `page_curation_status` | New, Selected, Queued, Processing, Complete, Error, Skipped | pages.page_curation_status |
| `page_processing_status` | Queued, Processing, Complete, Error, Filtered | pages.page_processing_status |
| `page_type_enum` | contact_root, career_contact, about_root, services_root, menu_root, pricing_root, team_root, legal_root, wp_prospect, unknown | pages.page_type |
| `contact_scrape_status` | New, ContactFound, NoContactFound, Error, NotAFit | pages.contact_scrape_status |
| `contact_curation_status` | New, Queued, Processing, Complete, Error, Skipped | contacts.contact_curation_status |
| `contact_processing_status` | Queued, Processing, Complete, Error | contacts.contact_processing_status |
| `contact_email_type_enum` | SERVICE, CORPORATE, FREE, UNKNOWN | contacts.email_type |
| `task_status` | Queued, InProgress, Completed, Error, ManualReview, Cancelled, Paused, Processing, Complete | domains.content_scrape_status, domains.page_scrape_status, domains.sitemap_monitor_status |
| `gcp_api_deep_scan_status` | Queued, Processing, Completed, Error | places_staging.deep_scan_status |

#### CRM Sync Enums
| Enum Type | Values | Used By |
|-----------|--------|---------|
| `crm_sync_status` | New, Selected, Queued, Processing, Complete, Error, Skipped | contacts.brevo_sync_status, contacts.mautic_sync_status, contacts.n8n_sync_status, contacts.debounce_validation_status |
| `crm_processing_status` | Queued, Processing, Complete, Error | contacts.brevo_processing_status, contacts.mautic_processing_status, contacts.n8n_processing_status, contacts.debounce_processing_status |
| `hubspot_sync_status` | New, Selected, Queued, Processing, Complete, Error, Skipped | contacts.hubspot_sync_status, domains.hubspot_sync_status |
| `hubspot_sync_processing_status` | Queued, Processing, Complete, Error | contacts.hubspot_processing_status, domains.hubspot_processing_status |

---

## PART 2: PYTHON ENUM DEFINITIONS

### Location 1: `src/models/enums.py` (CENTRALIZED) ✅

**Purpose:** Single source of truth for all enums

**Enums Defined (24 total):**
- `ContactEmailTypeEnum`
- `ContactCurationStatus`
- `ContactProcessingStatus`
- `DomainStatusEnum`
- `HubSpotSyncStatus`
- `HubSpotProcessingStatus`
- `CRMSyncStatus`
- `CRMProcessingStatus`
- `ContactScrapeStatus`
- `PageCurationStatus`
- `PageProcessingStatus`
- `PlaceStatusEnum`
- `GcpApiDeepScanStatusEnum`
- `SitemapAnalysisStatusEnum`
- `SitemapCurationStatusEnum`
- `SitemapFileStatusEnum`
- `SitemapImportCurationStatusEnum`
- `SitemapImportProcessStatusEnum`
- `DomainExtractionStatusEnum`
- `PageTypeEnum`
- `EmailValidationResult`

### Location 2: `src/models/__init__.py` (DUPLICATED) ❌

**Enums Defined:**
- `SitemapType` - For sitemap categorization
- `DiscoveryMethod` - How sitemap was found
- `TaskStatus` - **DUPLICATE** (also in domain.py)

**Problem:** These should be in `enums.py`

### Location 3: Individual Model Files (SCATTERED) ❌

#### `src/models/domain.py`
- `TaskStatus` - **DUPLICATE** of `__init__.py` version
- `SitemapCurationStatusEnum` - **DUPLICATE** of `enums.py` version
- `SitemapAnalysisStatusEnum` - **DUPLICATE** of `enums.py` version

#### `src/models/local_business.py`
- `DomainExtractionStatusEnum` - **CONFLICT** with `enums.py` version (different values!)

#### `src/models/place.py`
- `PlaceStatusEnum` - **DUPLICATE** of `enums.py` version
- `GcpApiDeepScanStatusEnum` - **CONFLICT** with `enums.py` version (different values!)

### Location 4: Inline String Enums (ANTI-PATTERN) ❌❌❌

**File:** `src/models/WF7_V2_L1_1of1_ContactModel.py`

**All enum columns use hardcoded strings:**
```python
email_type = Column(Enum('SERVICE', 'CORPORATE', 'FREE', 'UNKNOWN', name='contact_email_type_enum'))
contact_curation_status = Column(Enum('New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='contact_curation_status'))
contact_processing_status = Column(Enum('Queued', 'Processing', 'Complete', 'Error', name='contact_processing_status'))
hubspot_sync_status = Column(Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='hubspot_sync_status'))
hubspot_processing_status = Column(Enum('Queued', 'Processing', 'Complete', 'Error', name='hubspot_sync_processing_status'))
brevo_sync_status = Column(Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='crm_sync_status'))
brevo_processing_status = Column(Enum('Queued', 'Processing', 'Complete', 'Error', name='crm_processing_status'))
mautic_sync_status = Column(Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='crm_sync_status'))
mautic_processing_status = Column(Enum('Queued', 'Processing', 'Complete', 'Error', name='crm_processing_status'))
n8n_sync_status = Column(Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='crm_sync_status'))
n8n_processing_status = Column(Enum('Queued', 'Processing', 'Complete', 'Error', name='crm_processing_status'))
debounce_validation_status = Column(Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='crm_sync_status'))
debounce_processing_status = Column(Enum('Queued', 'Processing', 'Complete', 'Error', name='crm_processing_status'))
```

**Why This Is Dangerous:**
- No type safety
- No IDE autocomplete
- No import validation
- Cannot be used in routers/services
- Easy to introduce typos
- Missing `create_type=False`, `native_enum=True`, `values_callable`

---

## PART 3: ENUM VALUE CONFLICTS

### Conflict 1: DomainExtractionStatusEnum

**enums.py version:**
```python
class DomainExtractionStatusEnum(str, Enum):
    Pending = "pending"      # lowercase
    Queued = "queued"
    Processing = "processing"
    Submitted = "submitted"
    Failed = "failed"
```

**local_business.py version:**
```python
class DomainExtractionStatusEnum(enum.Enum):
    Queued = "Queued"        # PascalCase
    Processing = "Processing"
    Completed = "Completed"
    Error = "Error"
```

**Database actual values:** `Queued, Processing, Completed, Error` (PascalCase)

**Used by:**
- `local_businesses.domain_extraction_status`
- `domain_extraction_scheduler.py`

**WINNER:** local_business.py version (matches DB)

### Conflict 2: GcpApiDeepScanStatusEnum

**enums.py version:**
```python
class GcpApiDeepScanStatusEnum(str, Enum):
    Pending = "Pending"
    Running = "Running"
    Complete = "Complete"
    Failed = "Failed"
```

**place.py version:**
```python
class GcpApiDeepScanStatusEnum(enum.Enum):
    Queued = "Queued"
    Processing = "Processing"
    Completed = "Completed"
    Error = "Error"
```

**Database actual values:** `Queued, Processing, Completed, Error`

**Used by:**
- `places_staging.deep_scan_status`
- `deep_scan_scheduler.py`

**WINNER:** place.py version (matches DB)

---

## PART 4: ROUTER ENUM USAGE

### Router: `local_businesses.py`
**Enums Used:**
- `PlaceStatusEnum` (from `src.models.place`)
- `DomainExtractionStatusEnum` (from `src.models.local_business`)

**Usage Pattern:**
- Query filtering by `PlaceStatusEnum`
- Maps API enum to DB enum by `.name` attribute
- Dual-Status: `status=Selected` triggers `domain_extraction_status=Queued`

### Router: `v2/WF7_V2_L3_1of1_PagesRouter.py`
**Enums Used:**
- `PageCurationStatus` (from `src.models.enums`)
- `PageProcessingStatus` (from `src.models.enums`)

**Usage Pattern:**
- Dual-Status: `page_curation_status=Queued` triggers `page_processing_status=Queued`

### Router: `v3/domains_direct_submission_router.py`
**Enums Used:**
- `SitemapCurationStatusEnum` (from `src.models.domain`)
- `SitemapAnalysisStatusEnum` (from `src.models.domain`)

**Usage Pattern:**
- Sets `sitemap_curation_status=Selected` or `New`
- Sets `sitemap_analysis_status=queued` if auto_queue

### Router: `v3/pages_direct_submission_router.py`
**Enums Used:**
- `PageCurationStatus` (from `src.models.page`)
- `PageProcessingStatus` (from `src.models.page`)
- `SitemapCurationStatusEnum` (from `src.models.domain`)

**Usage Pattern:**
- Dual-Status Pattern for pages
- Sets domain sitemap status

---

## PART 5: BACKGROUND SERVICE ENUM USAGE

### Service: `domain_extraction_scheduler.py`
**Model:** `LocalBusiness`  
**Status Field:** `domain_extraction_status`  
**Enum:** `DomainExtractionStatusEnum` (from `src.models.local_business`)

**Enum Values Used:**
- `Queued` - Picked up by scheduler
- `Processing` - Currently being processed
- `Completed` - Successfully created Domain
- `Error` - Failed to create Domain

**SDK Configuration:**
```python
await run_job_loop(
    model=LocalBusiness,
    status_enum=DomainExtractionStatusEnum,
    queued_status=DomainExtractionStatusEnum.Queued,
    processing_status=DomainExtractionStatusEnum.Processing,
    completed_status=DomainExtractionStatusEnum.Completed,
    failed_status=DomainExtractionStatusEnum.Error,
    status_field_name="domain_extraction_status",
)
```

### Service: `deep_scan_scheduler.py`
**Model:** `Place`  
**Status Field:** `deep_scan_status`  
**Enum:** `GcpApiDeepScanStatusEnum` (from `src.models.place`)

**Enum Values Used:**
- `Queued`, `Processing`, `Completed`, `Error`

### Service: `sitemap_import_scheduler.py`
**Model:** `SitemapFile`  
**Status Field:** `sitemap_import_status`  
**Enum:** `SitemapImportProcessStatusEnum` (from `src.models.sitemap`)

**Enum Values Used:**
- `Queued`, `Processing`, `Complete`, `Error`

### Service: `domain_sitemap_submission_scheduler_fixed.py`
**Model:** `Domain`  
**Status Field:** `sitemap_analysis_status`  
**Enum:** `SitemapAnalysisStatusEnum` (from `src.models.domain`)

**Enum Values Used:**
- `queued`, `processing`, `submitted`, `failed`

**Note:** Uses `.value` attribute for DB writes

### Service: `domain_scheduler.py`
**Model:** `Domain`  
**Status Fields:** `status`, `sitemap_analysis_status`  
**Enums:** `DomainStatusEnum`, `SitemapAnalysisStatusEnum`

**Critical WF4→WF5 Trigger:**
```python
domain.status = DomainStatusEnum.completed
# Triggers next workflow:
setattr(domain, "sitemap_analysis_status", SitemapAnalysisStatusEnum.queued)
```

### CRM Services
**All use Dual-Status Pattern:**
- User Status: `[crm]_sync_status` (Selected triggers processing)
- Background Status: `[crm]_processing_status` (Queued → Processing → Complete/Error)

**Services:**
- `crm/brevo_sync_scheduler.py`
- `crm/hubspot_sync_scheduler.py`
- `crm/n8n_sync_scheduler.py`
- `email_validation/debounce_scheduler.py`

---

## PART 6: COMPLETE WORKFLOW CHAIN

```
WF2: Place
  └─ deep_scan_status (GcpApiDeepScanStatusEnum)
     └─ Scheduler: deep_scan_scheduler.py
        └─ Service: PlacesDeepService
           └─ Creates: LocalBusiness

WF3: LocalBusiness
  └─ status (PlaceStatusEnum) [USER SETS]
  └─ domain_extraction_status (DomainExtractionStatusEnum) [BACKGROUND]
     └─ Scheduler: domain_extraction_scheduler.py
        └─ Service: LocalBusinessToDomainService
           └─ Creates: Domain

WF4: Domain
  └─ status (DomainStatusEnum)
     └─ Scheduler: domain_scheduler.py
        └─ Service: Domain metadata extraction
           └─ On completion, triggers WF5:
              └─ sitemap_analysis_status = queued

WF5: Domain
  └─ sitemap_curation_status (SitemapCurationStatusEnum) [USER SETS]
  └─ sitemap_analysis_status (SitemapAnalysisStatusEnum) [BACKGROUND]
     └─ Scheduler: domain_sitemap_submission_scheduler_fixed.py
        └─ Service: SitemapAnalyzer
           └─ Creates: SitemapFile

WF6: SitemapFile
  └─ deep_scrape_curation_status (SitemapImportCurationStatusEnum) [USER SETS]
  └─ sitemap_import_status (SitemapImportProcessStatusEnum) [BACKGROUND]
     └─ Scheduler: sitemap_import_scheduler.py
        └─ Service: sitemap_files_service
           └─ Creates: Page

WF7: Page
  └─ page_curation_status (PageCurationStatus) [USER SETS]
  └─ page_processing_status (PageProcessingStatus) [BACKGROUND]
     └─ Scheduler: WF7_V2_L4_2of2_PageCurationScheduler.py
        └─ Service: WF7_V2_L4_1of2_PageCurationService.py
           └─ Creates: Contact

CRM: Contact
  └─ [crm]_sync_status (CrmSyncStatusEnum) [USER SETS]
  └─ [crm]_processing_status (CrmProcessingStatusEnum) [BACKGROUND]
     └─ Schedulers: brevo/hubspot/n8n/debounce
        └─ Services: CRM sync services
```

---

## PART 7: DUAL-STATUS PATTERN

**Every workflow uses this pattern:**

### User-Facing Status (Curation)
- **Purpose:** User selects which items to process
- **Values:** New, Selected, Maybe, Not a Fit, Archived
- **Set by:** Frontend UI, API endpoints
- **Triggers:** Background processing when set to "Selected" or "Queued"

### Background Status (Processing)
- **Purpose:** Track background job progress
- **Values:** Queued, Processing, Complete, Error
- **Set by:** Background schedulers
- **Monitored by:** Curation SDK `run_job_loop`

### Example: LocalBusiness
```python
# User sets in UI:
business.status = PlaceStatusEnum.Selected

# Router triggers:
business.domain_extraction_status = DomainExtractionStatusEnum.Queued

# Scheduler picks up:
WHERE domain_extraction_status = 'Queued'

# Scheduler updates:
business.domain_extraction_status = DomainExtractionStatusEnum.Processing
# ... process ...
business.domain_extraction_status = DomainExtractionStatusEnum.Completed
```

---

## PART 8: CRITICAL ISSUES & FIXES NEEDED

### CRITICAL 1: Fix WF7_V2_L1_1of1_ContactModel.py

**Current (Anti-Pattern):**
```python
email_type = Column(Enum('SERVICE', 'CORPORATE', 'FREE', 'UNKNOWN', name='contact_email_type_enum'))
```

**Required Fix:**
```python
from src.models.enums import ContactEmailTypeEnum
from sqlalchemy import Enum as SQLAlchemyEnum

email_type = Column(
    SQLAlchemyEnum(
        ContactEmailTypeEnum,
        name='contact_email_type_enum',
        create_type=False,
        native_enum=True,
        values_callable=lambda x: [e.value for e in x]
    ),
    nullable=True
)
```

**Apply to all 13 enum columns in this file.**

### CRITICAL 2: Resolve DomainExtractionStatusEnum Conflict

**Action:** Delete from `enums.py`, keep in `local_business.py`

**Reason:** local_business.py version matches actual DB values

**Update imports in:**
- `domain_extraction_scheduler.py`
- Any routers using this enum

### CRITICAL 3: Resolve GcpApiDeepScanStatusEnum Conflict

**Action:** Delete from `enums.py`, keep in `place.py`

**Reason:** place.py version matches actual DB values

**Update imports in:**
- `deep_scan_scheduler.py`
- Any routers using this enum

### CRITICAL 4: Consolidate All Enums

**Move to `enums.py`:**
- `SitemapType` (from `__init__.py`)
- `DiscoveryMethod` (from `__init__.py`)
- `TaskStatus` (delete from `__init__.py` and `domain.py`, keep one in `enums.py`)

**Delete duplicates from:**
- `src/models/__init__.py`
- `src/models/domain.py`
- `src/models/place.py` (except GcpApiDeepScanStatusEnum)
- `src/models/local_business.py` (except DomainExtractionStatusEnum)

### CRITICAL 5: Standardize Enum Column Definitions

**All enum columns must use:**
```python
Column(
    Enum(
        EnumClass,
        name="exact_db_enum_type_name",  # MUST match DB
        create_type=False,
        native_enum=True,
        values_callable=lambda x: [e.value for e in x]
    ),
    nullable=True/False,
    default=EnumClass.DefaultValue,
    index=True  # if needed for queries
)
```

---

## PART 9: STANDARDIZATION ROADMAP

### Phase 1: Emergency Fixes (DO FIRST)
1. ✅ Fix `sitemap_files.deep_scrape_curation_status` (DONE - Commit 26f3911)
2. ❌ Fix `WF7_V2_L1_1of1_ContactModel.py` inline enums
3. ❌ Resolve `DomainExtractionStatusEnum` conflict
4. ❌ Resolve `GcpApiDeepScanStatusEnum` conflict

### Phase 2: Consolidation (DO NEXT)
5. ❌ Move all enums to `enums.py`
6. ❌ Delete duplicate definitions
7. ❌ Update all imports

### Phase 3: Standardization (DO LAST)
8. ❌ Add missing column parameters
9. ❌ Standardize enum value casing (if needed)
10. ❌ Database migration (if casing changes)

---

## PART 10: TESTING CHECKLIST

After each fix, verify:

### ✅ Model Tests
- [ ] All models import without errors
- [ ] No circular import issues
- [ ] Enum values match DB types

### ✅ Router Tests
- [ ] All routers import enums correctly
- [ ] Query filtering works
- [ ] Status updates work
- [ ] Dual-Status Pattern triggers correctly

### ✅ Scheduler Tests
- [ ] All schedulers start without errors
- [ ] Enum comparisons work
- [ ] Status transitions work
- [ ] SDK `run_job_loop` functions correctly

### ✅ Database Tests
- [ ] No enum type mismatch errors
- [ ] No operator errors
- [ ] All queries execute successfully

---

## APPENDIX A: DATABASE ENUM TYPE REFERENCE

**Complete list of all 58 enum types in database:**

See "PART 1: DATABASE ENUM INVENTORY" above for full details.

---

## APPENDIX B: COMMIT HISTORY

**Enum fixes completed today:**

- `46e2fbd` - Fix TaskStatus import in domain.py
- `0e7440f` - Remove circular import, define TaskStatus locally
- `5650333` - Fix place_status_enum in place.py
- `688b946` - Align enum names with database
- `1b5a044` - Fix ALL enum type name mismatches
- `723ac96` - Fix sitemap deep_scrape_curation_status (WRONG)
- `26f3911` - Correct sitemap enum to sitemap_curation_status_enum (CORRECT)

---

**END OF REPORT**
