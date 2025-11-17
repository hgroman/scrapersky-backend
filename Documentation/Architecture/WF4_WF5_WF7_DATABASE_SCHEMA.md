# WF4→WF5→WF7 Database Schema
**Part of:** Complete Pipeline Documentation  
**Last Updated:** November 17, 2025

---

## Table Relationships

```
local_business (WF3 - upstream)
    ↓ (1:N)
domains (WF4)
    ↓ (1:N)
sitemap_files (WF5)
    ↓ (1:N)
pages (WF7)
```

---

## Table: `domains`

### Purpose
Stores extracted domains from LocalBusiness records for sitemap discovery

### Schema
```sql
CREATE TABLE domains (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core Fields
    domain VARCHAR(255) UNIQUE NOT NULL,
    local_business_id UUID REFERENCES local_business(id),
    sitemap_url TEXT,
    
    -- WF4 Status Tracking
    sitemap_analysis_status VARCHAR(50),  -- queued, submitted, failed
    sitemap_analysis_error TEXT,
    
    -- Curation Fields
    sitemap_curation_status VARCHAR(50),  -- New, Selected, Rejected
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_domains_sitemap_analysis_status ON domains(sitemap_analysis_status);
CREATE INDEX idx_domains_sitemap_curation_status ON domains(sitemap_curation_status);
CREATE INDEX idx_domains_local_business_id ON domains(local_business_id);
CREATE UNIQUE INDEX idx_domains_domain ON domains(domain);
```

### Field Definitions

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `domain` | VARCHAR(255) | NO | Domain name (e.g., "example.com") |
| `local_business_id` | UUID | YES | FK to local_business table |
| `sitemap_url` | TEXT | YES | Discovered sitemap URL |
| `sitemap_analysis_status` | VARCHAR(50) | YES | Processing status for sitemap discovery |
| `sitemap_analysis_error` | TEXT | YES | Error message if discovery failed |
| `sitemap_curation_status` | VARCHAR(50) | YES | User curation decision |
| `created_at` | TIMESTAMP | NO | Record creation time |
| `updated_at` | TIMESTAMP | NO | Last update time |

### Status Values

**sitemap_analysis_status:**
- `queued` - Ready for sitemap discovery
- `submitted` - Job created, processing started
- `failed` - Discovery failed (see sitemap_analysis_error)
- `NULL` - Not yet queued

**sitemap_curation_status:**
- `New` - Newly created, awaiting review
- `Selected` - Approved for processing (triggers queued status)
- `Rejected` - Excluded from processing
- `NULL` - No curation decision yet

### Relationships
- **Parent:** `local_business.id` → `domains.local_business_id` (Many-to-One)
- **Children:** `domains.id` → `sitemap_files.domain_id` (One-to-Many)

### Typical Record Lifecycle
1. Created with `sitemap_curation_status = 'New'`
2. User sets to `'Selected'` → triggers `sitemap_analysis_status = 'queued'`
3. Scheduler picks up → calls adapter service
4. Adapter creates job → sets `sitemap_analysis_status = 'submitted'`
5. Job completes → creates sitemap_files records
6. Status remains `'submitted'` (no further updates)

---

## Table: `sitemap_files`

### Purpose
Stores discovered sitemap URLs from domains for URL extraction

### Schema
```sql
CREATE TABLE sitemap_files (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core Fields
    url TEXT NOT NULL,
    domain_id UUID REFERENCES domains(id) ON DELETE CASCADE,
    
    -- WF5 Status Tracking
    sitemap_import_status VARCHAR(50),  -- Queued, Processing, Complete, Error
    sitemap_import_error TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_sitemap_files_domain_id ON sitemap_files(domain_id);
CREATE INDEX idx_sitemap_files_import_status ON sitemap_files(sitemap_import_status);
```

### Field Definitions

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `url` | TEXT | NO | Full sitemap URL |
| `domain_id` | UUID | YES | FK to domains table |
| `sitemap_import_status` | VARCHAR(50) | YES | Processing status for URL extraction |
| `sitemap_import_error` | TEXT | YES | Error message if extraction failed |
| `created_at` | TIMESTAMP | NO | Record creation time |
| `updated_at` | TIMESTAMP | NO | Last update time |

### Status Values

**sitemap_import_status:**
- `Queued` - Ready for URL extraction
- `Processing` - Currently extracting URLs
- `Complete` - URLs extracted successfully
- `Error` - Extraction failed (see sitemap_import_error)
- `NULL` - Not yet queued

### Relationships
- **Parent:** `domains.id` → `sitemap_files.domain_id` (Many-to-One)
- **Children:** `sitemap_files.id` → `pages.sitemap_file_id` (One-to-Many)

### Typical Record Lifecycle
1. Created by sitemap discovery job with `sitemap_import_status = NULL`
2. ⚠️ **GAP:** No automatic queuing mechanism (needs manual curation or auto-queue logic)
3. User/system sets to `'Queued'`
4. Scheduler picks up → calls SitemapImportService
5. Service sets to `'Processing'`
6. URLs extracted → Page records created
7. Status set to `'Complete'`

### Known Issues
- **Missing curation_status field:** Unlike domains and pages, sitemap_files may lack a `sitemap_curation_status` field
- **No auto-queue:** Sitemaps created with NULL status, requiring manual intervention

---

## Table: `pages`

### Purpose
Stores individual page URLs extracted from sitemaps for contact extraction

### Schema
```sql
CREATE TABLE pages (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core Fields
    url TEXT NOT NULL,
    sitemap_file_id UUID REFERENCES sitemap_files(id) ON DELETE CASCADE,
    
    -- Honeybee Categorization
    page_type VARCHAR(100),      -- Honeybee category
    priority_level INTEGER,      -- 1=high, 2=medium, 3=low
    
    -- WF7 Status Tracking
    page_processing_status VARCHAR(50),  -- Queued, Processing, Complete, Error
    page_processing_error TEXT,
    
    -- Curation Fields
    page_curation_status VARCHAR(50),  -- New, Selected, Rejected
    
    -- Extracted Data
    scraped_content JSONB,  -- Stores emails, phones, addresses, etc.
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_pages_sitemap_file_id ON pages(sitemap_file_id);
CREATE INDEX idx_pages_processing_status ON pages(page_processing_status);
CREATE INDEX idx_pages_curation_status ON pages(page_curation_status);
CREATE INDEX idx_pages_page_type ON pages(page_type);
CREATE INDEX idx_pages_priority_level ON pages(priority_level);
CREATE INDEX idx_pages_url ON pages USING gin(url gin_trgm_ops);  -- For URL search
```

### Field Definitions

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `url` | TEXT | NO | Full page URL |
| `sitemap_file_id` | UUID | YES | FK to sitemap_files table |
| `page_type` | VARCHAR(100) | YES | Honeybee category (e.g., CONTACT_ROOT) |
| `priority_level` | INTEGER | YES | Priority: 1=high, 2=medium, 3=low |
| `page_processing_status` | VARCHAR(50) | YES | Processing status for scraping |
| `page_processing_error` | TEXT | YES | Error message if scraping failed |
| `page_curation_status` | VARCHAR(50) | YES | User curation decision |
| `scraped_content` | JSONB | YES | Extracted contact data |
| `created_at` | TIMESTAMP | NO | Record creation time |
| `updated_at` | TIMESTAMP | NO | Last update time |

### Status Values

**page_processing_status:**
- `Queued` - Ready for scraping
- `Processing` - Currently being scraped
- `Complete` - Scraping finished (may or may not have contacts)
- `Error` - Scraping failed (see page_processing_error)
- `NULL` - Not yet queued

**page_curation_status:**
- `New` - Newly created, awaiting review
- `Selected` - Approved for processing (triggers Queued status)
- `Rejected` - Excluded from processing
- `NULL` - No curation decision yet

**page_type (Honeybee Categories):**
- `CONTACT_ROOT` - Main contact page
- `CAREER_CONTACT` - Careers/jobs page
- `LEGAL_ROOT` - Legal/privacy pages
- `unknown` - Not categorized or low-confidence
- Many others (see Honeybee documentation)

**priority_level:**
- `1` - High priority (auto-selected pages)
- `2` - Medium priority
- `3` - Low priority (product pages, etc.)

### Scraped Content Structure (JSONB)

```json
{
  "emails": ["contact@example.com", "info@example.com"],
  "phones": ["+1-555-0100", "(555) 555-0200"],
  "addresses": ["123 Main St, City, ST 12345"],
  "business_info": {
    "hours": "Mon-Fri 9-5",
    "description": "..."
  },
  "extraction_timestamp": "2025-11-17T09:52:00Z",
  "scraper_metadata": {
    "status_code": 200,
    "scraper_api_credits": 1
  }
}
```

### Relationships
- **Parent:** `sitemap_files.id` → `pages.sitemap_file_id` (Many-to-One)

### Typical Record Lifecycle
1. Created by SitemapImportService with Honeybee categorization
2. High-value pages auto-selected: `page_curation_status = 'Selected'`, `page_processing_status = 'Queued'`
3. Low-value pages: `page_curation_status = 'New'`, `page_processing_status = NULL`
4. User can manually select → triggers `page_processing_status = 'Queued'`
5. Scheduler picks up → calls PageCurationService
6. Service sets to `'Processing'`
7. Page scraped → contacts extracted → stored in `scraped_content`
8. Status set to `'Complete'`

### Auto-Selection Rules

Pages are automatically selected if ALL conditions met:
- `page_type` in {CONTACT_ROOT, CAREER_CONTACT, LEGAL_ROOT}
- Honeybee confidence >= 0.6
- Depth <= 2

When auto-selected:
- `page_curation_status = 'Selected'`
- `page_processing_status = 'Queued'`
- `priority_level = 1`

---

## Table: `jobs`

### Purpose
Tracks background job execution (sitemap discovery, deep scans, etc.)

### Schema
```sql
CREATE TABLE jobs (
    -- Primary Key
    job_id UUID PRIMARY KEY,
    
    -- Core Fields
    job_type VARCHAR(50),    -- 'sitemap', 'deep_scan', etc.
    status VARCHAR(50),      -- 'pending', 'running', 'complete', 'failed'
    created_by UUID,         -- User ID or NULL for system jobs
    result_data JSONB,       -- Job-specific data
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_jobs_type_status ON jobs(job_type, status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

### Field Definitions

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `job_id` | UUID | NO | Primary key (generated by caller) |
| `job_type` | VARCHAR(50) | YES | Type of job |
| `status` | VARCHAR(50) | YES | Current job status |
| `created_by` | UUID | YES | User ID or NULL for system |
| `result_data` | JSONB | YES | Job-specific parameters/results |
| `created_at` | TIMESTAMP | NO | Job creation time |
| `updated_at` | TIMESTAMP | NO | Last status update |

### Status Values

**status:**
- `pending` - Job created, waiting to start
- `running` - Job currently executing
- `complete` - Job finished successfully
- `failed` - Job encountered error

### Job Types

**sitemap:**
- Discovers sitemap URLs for a domain
- `result_data`: `{"domain": "example.com", "max_pages": 1000}`

**deep_scan:**
- Deep scan of Place records (WF2)
- `result_data`: Place-specific data

### Result Data Structure (Sitemap Jobs)

```json
{
  "domain": "example.com",
  "max_pages": 1000,
  "sitemaps_found": 5,
  "error": null
}
```

### Relationships
- No direct FK relationships (jobs are ephemeral)
- Jobs reference domains/places via result_data

### Typical Lifecycle (Sitemap Job)
1. Created by DomainToSitemapAdapterService with `status = 'pending'`
2. Immediately processed by background task (asyncio.create_task)
3. Status updated to `'running'` (in-memory, may not persist)
4. Sitemap discovery completes
5. Status updated to `'complete'`
6. Job record remains for audit trail

### Known Issues
- Jobs may accumulate over time (no cleanup mechanism)
- Status updates may not always persist to database (in-memory tracking)

---

## Cross-Table Queries

### Get all pages for a domain
```sql
SELECT p.*
FROM pages p
JOIN sitemap_files sf ON p.sitemap_file_id = sf.id
JOIN domains d ON sf.domain_id = d.id
WHERE d.domain = 'example.com';
```

### Get domains with failed sitemap discovery
```sql
SELECT d.domain, d.sitemap_analysis_error, d.updated_at
FROM domains d
WHERE d.sitemap_analysis_status = 'failed'
ORDER BY d.updated_at DESC;
```

### Get high-priority pages ready for processing
```sql
SELECT p.url, p.page_type, p.priority_level
FROM pages p
WHERE p.page_processing_status = 'Queued'
  AND p.priority_level = 1
ORDER BY p.created_at ASC;
```

### Get pages with extracted contacts
```sql
SELECT p.url, p.scraped_content->'emails' as emails
FROM pages p
WHERE p.page_processing_status = 'Complete'
  AND p.scraped_content->'emails' IS NOT NULL
  AND jsonb_array_length(p.scraped_content->'emails') > 0;
```

### Get sitemap processing statistics by domain
```sql
SELECT 
    d.domain,
    COUNT(DISTINCT sf.id) as sitemap_count,
    COUNT(DISTINCT p.id) as page_count,
    COUNT(DISTINCT CASE WHEN p.page_processing_status = 'Complete' THEN p.id END) as processed_count
FROM domains d
LEFT JOIN sitemap_files sf ON d.id = sf.domain_id
LEFT JOIN pages p ON sf.id = p.sitemap_file_id
GROUP BY d.domain
ORDER BY page_count DESC;
```

---

## Schema Gaps & Issues

### 1. Missing sitemap_curation_status field
**Table:** `sitemap_files`  
**Issue:** No curation status field like domains and pages have  
**Impact:** Cannot track user curation decisions for sitemaps  
**Recommendation:** Add field and update GUI

### 2. No auto-queue mechanism for sitemaps
**Table:** `sitemap_files`  
**Issue:** Created with NULL status, not automatically queued  
**Impact:** Requires manual intervention to process sitemaps  
**Recommendation:** Auto-set to 'Queued' when created, or add trigger

### 3. Job table cleanup
**Table:** `jobs`  
**Issue:** Jobs accumulate indefinitely  
**Impact:** Database bloat over time  
**Recommendation:** Add cleanup job or TTL policy

### 4. Missing indexes for common queries
**Tables:** Various  
**Issue:** Some common filter combinations lack composite indexes  
**Impact:** Slower queries on large datasets  
**Recommendation:** Add indexes based on query patterns

### 5. No cascade delete for orphaned records
**Tables:** Various  
**Issue:** Deleting a domain doesn't cascade to all related records  
**Impact:** Orphaned sitemap_files and pages  
**Recommendation:** Review and add CASCADE where appropriate
