# ScraperSky System Map
**Purpose:** Complete architecture overview  
**Last Updated:** November 17, 2025  
**Version:** 2.0 (Added ENUM Registry & Model Constraints)

---

## Complete Data Flow (All 7 Workflows)

### Visual Flow Diagram

```mermaid
graph TD
    A[WF1: Single Search] -->|Google Maps API| B[Place Records]
    B --> C[WF2: Deep Scan]
    C -->|Enrich details| D[Place enriched]
    D --> E[WF3: Domain Extraction]
    E -->|Extract website| F[LocalBusiness]
    F -->|Create| G[Domain Records]
    G --> H[WF4: Sitemap Discovery]
    H -->|Find sitemap.xml| I[SitemapFile Records]
    I --> J[WF5: Sitemap Import]
    J -->|Parse XML + Honeybee| K[Page Records]
    K --> L[WF7: Page Curation]
    L -->|ScraperAPI scrape| M[Contact Data]

    style A fill:#e1f5ff
    style C fill:#e1f5ff
    style E fill:#e1f5ff
    style H fill:#fff3cd
    style J fill:#fff3cd
    style L fill:#d4edda
```

### Text Flow

```
WF1: Single Search (Google Maps)
    ↓ Google Maps API
Place (Google Maps data)
    ↓
WF2: Deep Scan (enrichment)
    ↓ Additional API calls
Place (enriched with photos, reviews, hours)
    ↓
WF3: Domain Extraction
    ↓ Extract website field
LocalBusiness → Domain
    ↓
WF4: Sitemap Discovery/Curation
    ↓ Try common sitemap paths
Domain → SitemapFile (1:N)
    ↓
WF5: Sitemap Import
    ↓ Parse XML, extract URLs, Honeybee categorization
SitemapFile → Page (1:N)
    ↓
WF7: Page Curation / Contact Extraction
    ↓ ScraperAPI + regex extraction
Page → Contacts (in scraped_content JSONB)
```

**Note:** There is NO WF6 workflow. References to "WF6" in code comments are outdated. WF5 handles all sitemap import functionality.

---

## Database Tables

### Core Tables
1. **places** - Google Maps data (WF1, WF2)
2. **local_business** - Extracted business info (WF3)
3. **domains** - Discovered domains (WF3, WF4)
4. **sitemap_files** - Discovered sitemaps (WF4, WF5)
5. **pages** - Individual URLs (WF5, WF7)
6. **jobs** - Background job tracking (WF4)

### Relationships
```
places (1) → (N) local_business
local_business (1) → (N) domains
domains (1) → (N) sitemap_files
sitemap_files (1) → (N) pages
```

**Detailed Schema:** [WF4_WF5_WF7_DATABASE_SCHEMA.md](../Architecture/WF4_WF5_WF7_DATABASE_SCHEMA.md)

---

## Core Model File Map

**Purpose:** Single source of truth for model locations (prevents "couldn't find file" errors)

| Model | File Path | Primary Table |
|-------|-----------|---------------|
| Domain | `src/models/wf4_domain.py` | `domains` |
| SitemapFile | `src/models/wf5_sitemap_file.py` | `sitemap_files` |
| Page | `src/models/wf7_page.py` | `pages` |
| LocalBusiness | `src/models/wf3_local_business.py` | `local_businesses` |
| Place | `src/models/wf1_place_staging.py` | `places` |
| Contact | `src/models/wf7_contact.py` | `contacts` |
| Job | `src/models/wf4_job.py` | `jobs` |

---

## Critical Model Constraints (Database Rules)

**Purpose:** Document non-obvious, show-stopping database constraints that AIs must not violate

### Page Model (`src/models/page.py`)

**CRITICAL CONSTRAINT:**
```python
# Line 58-60
domain_id: Column[uuid.UUID] = Column(
    PGUUID(as_uuid=True), ForeignKey("domains.id"), nullable=False  # ← NOT NULL
)
```

**Impact:** All Page records MUST be associated with a Domain. Direct page submissions must "get-or-create" a Domain record first.

**Nullable Fields:**
- `sitemap_file_id` - CAN be NULL (for direct submissions)
- `page_category` - CAN be NULL (no Honeybee categorization)
- `priority_level` - Defaults to 5 if NULL

---

### SitemapFile Model (`src/models/sitemap.py`)

**CRITICAL CONSTRAINT #1:**
```python
# Line 104
domain_id = Column(PGUUID, ForeignKey("domains.id"), nullable=False, index=True)  # ← NOT NULL
```

**Impact:** All SitemapFile records MUST be associated with a Domain. Direct sitemap submissions must "get-or-create" a Domain record first.

**CRITICAL CONSTRAINT #2:**
```python
# Line 106
sitemap_type = Column(Text, nullable=False)  # ← NOT NULL
```

**Impact:** All SitemapFile records MUST have a sitemap_type. For direct submissions, use "STANDARD".

**Valid sitemap_type Values:** "INDEX", "STANDARD", "IMAGE", "VIDEO", "NEWS"

**Example:**
```python
sitemap_file = SitemapFile(
    domain_id=domain.id,  # REQUIRED
    url=sitemap_url,
    sitemap_type="STANDARD",  # REQUIRED - default for direct submission
    ...
)
```

**Nullable Fields:**
- `url_count` - CAN be NULL (populated after import)
- `last_modified` - CAN be NULL
- `size_bytes` - CAN be NULL
- `discovery_method` - CAN be NULL

---

### Domain Model (`src/models/domain.py`)

**CRITICAL CONSTRAINT:**
```python
# Line 117-123
tenant_id = Column(
    PGUUID,
    ForeignKey("tenants.id"),
    nullable=False,  # ← NOT NULL
    index=True,
    default=lambda: uuid.UUID(DEFAULT_TENANT_ID),
)
```

**Impact:** All Domain records MUST have a tenant_id. For direct submissions, use DEFAULT_TENANT_ID.

**DEFAULT_TENANT_ID:** `"550e8400-e29b-41d4-a716-446655440000"` (from `src/models/tenant.py:16`)

**Example:**
```python
from src.models.tenant import DEFAULT_TENANT_ID

domain = Domain(
    domain=domain_name,
    tenant_id=uuid.UUID(DEFAULT_TENANT_ID),  # REQUIRED
    local_business_id=None,  # NULL OK
    ...
)
```

**Nullable Foreign Keys:**
```python
# Line 169-174
local_business_id = Column(
    PGUUID,
    ForeignKey("local_businesses.id", ondelete="SET NULL"),
    index=True,
    nullable=True,  # ← CAN be NULL (for direct submissions)
)
```

**Impact:** Domains CAN exist without a LocalBusiness (e.g., from direct page/sitemap submission).

---

## Core ENUM Registry (Single Source of Truth)

**Purpose:** Prevent "inconsistent casing" false alarms and ENUM catastrophes

### Domain Model ENUMs (`src/models/domain.py`)

#### SitemapCurationStatusEnum
**Location:** `src/models/domain.py:36-46`  
**Casing:** PascalCase values  
**Database Type:** `SitemapCurationStatusEnum`

```python
class SitemapCurationStatusEnum(enum.Enum):
    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"  # Space in value is intentional
    Archived = "Archived"
    Completed = "Completed"
```

#### SitemapAnalysisStatusEnum
**Location:** `src/models/domain.py:52-61`  
**Casing:** lowercase values (INTENTIONAL - matches database)  
**Database Type:** `SitemapAnalysisStatusEnum`

```python
class SitemapAnalysisStatusEnum(enum.Enum):
    """Values MUST match database exactly (lowercase)"""
    pending = "pending"
    queued = "queued"
    processing = "processing"
    submitted = "submitted"
    failed = "failed"
```

**⚠️ NOTE:** The lowercase casing is CORRECT and intentional. This is NOT an error.

---

### Page Model ENUMs (`src/models/page.py`)

#### PageCurationStatus
**Location:** `src/models/page.py` (imported from `src/models/enums.py`)  
**Casing:** PascalCase values  
**Database Type:** `page_curation_status`

```python
class PageCurationStatus(str, Enum):
    New = "New"
    Selected = "Selected"
    Rejected = "Rejected"
```

#### PageProcessingStatus
**Location:** `src/models/page.py` (imported from `src/models/enums.py`)  
**Casing:** PascalCase values  
**Database Type:** `page_processing_status`

```python
class PageProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
```

---

### SitemapFile Model ENUMs (`src/models/sitemap.py`)

#### SitemapImportCurationStatusEnum
**Location:** `src/models/sitemap.py:54-62`  
**Casing:** PascalCase values  
**Database Type:** `SitemapCurationStatusEnum` (note: different from class name)

```python
class SitemapImportCurationStatusEnum(enum.Enum):
    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"  # Space in value is intentional
    Archived = "Archived"
```

#### SitemapImportProcessStatusEnum
**Location:** `src/models/sitemap.py:65-74`  
**Casing:** PascalCase values  
**Database Type:** `sitemapimportprocessingstatus`

```python
class SitemapImportProcessStatusEnum(enum.Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"  # NOT "Completed"
    Error = "Error"
```

**⚠️ NOTE:** The value is "Complete" not "Completed" - this is intentional.

---

## ENUM Usage Rules (ADR-005)

**CRITICAL:** Never create, modify, or rename ENUMs without understanding cross-layer dependencies.

### Safe Operations
✅ Use existing ENUM values  
✅ Query using `.value` (e.g., `PageCurationStatus.New.value`)  
✅ Import ENUMs from Layer 1 (models) to Layer 2 (schemas)

### Forbidden Operations
❌ Create new ENUM values  
❌ Change existing ENUM values  
❌ Rename ENUM classes  
❌ Change ENUM casing  
❌ Use `use_enum_values=True` in Pydantic (deprecated)

**Reference:** [ADR-005: ENUM Catastrophe Prevention](../Architecture/ADR-005_ENUM_CATASTROPHE.md)

---

## Services by Workflow

### WF1: Single Search
**Status:** Needs documentation  
**Tables:** places  
**Find services:** `find src/ -name "*WF1*" -o -name "*single*search*"`

### WF2: Deep Scan
**Status:** Needs documentation  
**Tables:** places  
**Find services:** `find src/ -name "*WF2*" -o -name "*deep*scan*"`

### WF3: Domain Extraction
**Status:** Needs documentation  
**Tables:** local_business, domains  
**Find services:** `find src/ -name "*WF3*" -o -name "*domain*extract*"`

### WF4: Sitemap Discovery
**Services:**
- `wf4_domain_to_sitemap_adapter_service` - Bridges WF3→WF4
- `wf5_processing_service` - Discovers sitemaps

**Tables:** domains → sitemap_files  
**Scheduler:** wf4_sitemap_discovery_scheduler (1 min)  
**Details:** [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md#wf4-services)

### WF5: Sitemap Import
**Services:**
- `wf5_sitemap_import_service` - Extracts URLs from sitemaps

**Tables:** sitemap_files → pages
**Scheduler:** wf5_sitemap_import_scheduler (configurable)
**Details:** [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md#wf5-services)

**Note:** There is no WF6. The numbering skips from WF5 to WF7.

### WF7: Page Curation
**Services:**
- `wf7_page_curation_service` - Scrapes pages, extracts contacts

**Tables:** pages (updates scraped_content)  
**Scheduler:** wf7_page_curation_scheduler (configurable)  
**Details:** [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md#wf7-services)

---

## Schedulers

| Scheduler | Interval | Processes | Creates | Status Field |
|-----------|----------|-----------|---------|--------------|
| Domain Sitemap Submission | 1 min | domains (queued) | jobs, sitemap_files | sitemap_analysis_status |
| Sitemap Import | Config | sitemap_files (Queued) | pages | sitemap_import_status |
| Page Curation | Config | pages (Queued) | scraped_content | page_processing_status |

**Configuration:** See `src/config/settings.py` for intervals and batch sizes

---

## API Endpoints

### WF4: Domain Curation
- `GET /api/v3/domains` - List domains
- `PUT /api/v3/domains/status` - Batch update
- `PUT /api/v3/domains/status/filtered` - Update all matching filters

**Router:** `src/routers/v3/WF4_V3_L3_1of1_DomainsRouter.py`

### WF5: Sitemap Curation
- `GET /api/v3/sitemaps` - List sitemaps
- `PUT /api/v3/sitemaps/status` - Batch update

**Router:** `src/routers/v3/WF5_V3_L3_1of1_SitemapRouter.py`

### WF7: Page Curation
- `GET /api/v3/pages` - List pages
- `PUT /api/v3/pages/status` - Batch update
- `PUT /api/v3/pages/status/filtered` - Update all matching filters

**Router:** `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py`

---

## Status Fields & State Machines

### domains.sitemap_analysis_status
```
NULL → queued → submitted → (terminal)
  ↓                ↓
failed ←──────────┘
```

### sitemap_files.sitemap_import_status
```
NULL → Queued → Processing → Complete
  ↓       ↓          ↓
  └───────┴──────────→ Error
```

### pages.page_processing_status
```
NULL → Queued → Processing → Complete
  ↓       ↓          ↓
  └───────┴──────────→ Error
```

**Dual-Status Pattern:** Each also has a `*_curation_status` field (New/Selected/Rejected)

**Details:** [GLOSSARY.md](./GLOSSARY.md#dual-status-pattern)

---

## Critical Paths

### User Selects Domain for Processing
1. User clicks "Select" in WF4 GUI
2. `PUT /api/v3/domains/status` with `status='Selected'`
3. Router sets `sitemap_curation_status='Selected'` AND `sitemap_analysis_status='queued'`
4. Scheduler picks up (within 1 min)
5. `DomainToSitemapAdapterService.submit_domain_to_legacy_sitemap()`
6. Creates Job + initializes memory + triggers `asyncio.create_task()`
7. `SitemapProcessingService.process_domain_with_own_session()` discovers sitemaps
8. Creates `SitemapFile` records
9. Domain status → 'submitted'

### Sitemap Files Auto-Process (⚠️ Gap)
**Current:** Created with `sitemap_import_status=NULL`  
**Should:** Auto-set to 'Queued'  
**Reference:** [WF4_WF5_WF7_GAPS_IMPROVEMENTS.md #1](../Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#1-sitemap-files-not-auto-queued)

### Pages Auto-Selected (Honeybee)
1. `SitemapImportService` extracts URLs
2. For each URL, runs Honeybee categorization
3. If category=CONTACT_ROOT/CAREER_CONTACT/LEGAL_ROOT AND confidence>=0.6 AND depth<=2:
   - Sets `page_curation_status='Selected'`
   - Sets `page_processing_status='Queued'`
   - Sets `priority_level=1`
4. Scheduler picks up queued pages
5. `PageCurationService` scrapes and extracts contacts

---

## External Dependencies

### ScraperAPI
- **Used By:** PageCurationService (WF7)
- **Purpose:** Fetch page HTML for scraping
- **Cost:** 1 credit per page
- **Rate Limit:** Unknown (needs verification)
- **Failure Mode:** page_processing_status='Error'
- **Config:** `settings.scraper_api_key`

### Supabase
- **Type:** PostgreSQL database
- **Access:** Via MCP (Model Context Protocol) tools
- **Tables:** All 6 core tables
- **Connection:** Environment variable
- **Backups:** [Document backup strategy]

### Render.com
- **Type:** Deployment platform
- **Environment:** Production
- **Logs:** Web dashboard
- **Deployment:** Automatic on git push to main
- **Docker:** Container-based

### Honeybee
- **Type:** URL categorization system
- **Used By:** SitemapImportService (WF5)
- **Purpose:** Classify pages by type
- **Categories:** CONTACT_ROOT, CAREER_CONTACT, LEGAL_ROOT, etc.
- **Output:** category, confidence, depth
- **Auto-Selection:** confidence >= 0.6, depth <= 2

**Details:** [DEPENDENCY_MAP.md](./DEPENDENCY_MAP.md)

---

## File Locations

src/
├── services/
│   ├── wf4_domain_to_sitemap_adapter_service.py (WF4)
│   ├── sitemap/
│   │   └── wf5_processing_service.py (WF4→WF5)
│   ├── wf5_sitemap_import_service.py (WF5)
│   ├── wf7_page_curation_service.py (WF7)
│   ├── background/
│   │   ├── wf4_sitemap_discovery_scheduler.py
│   │   ├── wf5_sitemap_import_scheduler.py
│   │   └── wf7_page_curation_scheduler.py
├── routers/v3/
│   ├── WF4_V3_L3_1of1_DomainsRouter.py
│   ├── WF5_V3_L3_1of1_SitemapRouter.py
│   └── WF7_V3_L3_1of1_PagesRouter.py
└── models/
    ├── wf1_place_staging.py
    ├── wf3_local_business.py
    ├── wf4_domain.py
    ├── wf5_sitemap_file.py
    └── wf7_page.py

---

## Service Communication Pattern

**✅ CORRECT:** Direct service calls
```python
service = SomeService()
result = await service.process(item_id, session)
```

**❌ WRONG:** HTTP calls between services  
**Reference:** [PATTERNS.md](./PATTERNS.md#pattern-1-service-communication)

---

## Key Metrics

- **Tables:** 6 core tables
- **Services:** 6+ documented services
- **Schedulers:** 3 main schedulers
- **API Endpoints:** 12+ across 3 routers
- **Status Fields:** 8+ tracking different stages
- **Workflows:** 7 (WF1-WF7)

---

## Investigation Starting Points

**For WF1-3 (Not Yet Documented):**
```bash
# Find WF1 services
find src/ -name "*WF1*" -o -name "*single*" -o -name "*search*"

# Find WF2 services
find src/ -name "*WF2*" -o -name "*deep*" -o -name "*scan*"

# Find WF3 services
find src/ -name "*WF3*" -o -name "*domain*extract*"

# Search for Place model usage
grep -r "from.*models.*place import" src/
```

---

## Related Documentation

- **Detailed Architecture:** [WF4_WF5_WF7_COMPLETE_INDEX.md](../Architecture/WF4_WF5_WF7_COMPLETE_INDEX.md)
- **Database Schema:** [WF4_WF5_WF7_DATABASE_SCHEMA.md](../Architecture/WF4_WF5_WF7_DATABASE_SCHEMA.md)
- **Services:** [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md)
- **Patterns:** [PATTERNS.md](./PATTERNS.md)
- **Glossary:** [GLOSSARY.md](./GLOSSARY.md)

---

**Note:** This map focuses on WF4-7 which are fully documented. WF1-3 need investigation and documentation. Use the investigation commands above to explore those workflows.
