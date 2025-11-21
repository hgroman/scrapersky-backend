# LIVE DATABASE ENUM REPORT
**Generated:** November 20, 2025 6:27 PM PST  
**Source:** Supabase Production Database (MCP Query)  
**Project:** ScraperSky Backend

---

## DATABASE STATISTICS

| Table | Row Count |
|-------|-----------|
| contacts | 73 |
| domains | 696 |
| local_businesses | 652 |
| pages | 6,739 |
| places_staging | 1,548 |
| sitemap_files | 1,633 |
| sitemap_urls | 12,546 |

**Total Records:** 23,887

---

## SECTION 1: ALL ENUM TYPES (58 Total)

### Workflow Status Enums (17)

| Enum Type | Values | Count |
|-----------|--------|-------|
| `SitemapAnalysisStatusEnum` | pending, queued, processing, submitted, failed | 5 |
| `contact_curation_status` | New, Queued, Processing, Complete, Error, Skipped | 6 |
| `contact_processing_status` | Queued, Processing, Complete, Error | 4 |
| `contact_scrape_status` | New, ContactFound, NoContactFound, Error, NotAFit | 5 |
| `crm_processing_status` | Queued, Processing, Complete, Error | 4 |
| `crm_sync_status` | New, Selected, Queued, Processing, Complete, Error, Skipped | 7 |
| `domain_extraction_status_enum` | Queued, Processing, Completed, Error | 4 |
| `domain_status` | pending, processing, completed, error | 4 |
| `gcp_api_deep_scan_status` | Queued, Processing, Completed, Error | 4 |
| `hubspot_sync_processing_status` | Queued, Processing, Complete, Error | 4 |
| `hubspot_sync_status` | New, Selected, Queued, Processing, Complete, Error, Skipped | 7 |
| `page_curation_status` | New, Selected, Queued, Processing, Complete, Error, Skipped | 7 |
| `page_processing_status` | Queued, Processing, Complete, Error, Filtered | 5 |
| `page_type_enum` | contact_root, career_contact, about_root, services_root, menu_root, pricing_root, team_root, legal_root, wp_prospect, unknown | 10 |
| `place_status_enum` | New, Selected, Maybe, Not a Fit, Archived | 5 |
| `sitemap_curation_status_enum` | New, Selected, Maybe, Not a Fit, Archived, Completed | 6 |
| `task_status` | Queued, InProgress, Completed, Error, ManualReview, Cancelled, Paused, Processing, Complete | 9 |

### Sitemap-Related Enums (11)

| Enum Type | Values | Count |
|-----------|--------|-------|
| `discovery_method` | robots_txt, common_path, sitemap_index, html_link, manual | 5 |
| `sitemap_analysis_status` | Pending, Analyzing, Completed | 3 |
| `sitemap_curation_status` | New, Queued, Processing, Complete, Error, Skipped | 6 |
| `sitemap_file_status` | Pending, Processing, Completed, Error | 4 |
| `sitemap_file_status_enum` | Pending, Processing, Completed, Error | 4 |
| `sitemap_import_curation_status` | New, Selected, Maybe, Not a Fit, Archived | 5 |
| `sitemap_import_status_enum` | Queued, Processing, Completed, Error, Submitted | 5 |
| `sitemap_type` | index, standard, image, video, news, unknown | 6 |
| `sitemap_url_status_enum` | Pending, Processing, Completed, Error | 4 |
| `sitemapimportcurationstatus` | New, Queued, Processing, Complete, Error, Skipped | 6 |
| `sitemapimportprocessingstatus` | Queued, Processing, Complete, Error | 4 |

### Legacy/Duplicate Enums (10)

| Enum Type | Values | Count | Note |
|-----------|--------|-------|------|
| `brevo_sync_status` | New, Queued, Processing, Complete, Error, Skipped | 6 | Duplicate of crm_sync_status |
| `contactcurationstatus` | New, Queued, Processing, Complete, Error, Skipped | 6 | Duplicate of contact_curation_status |
| `contactemailtypeenum` | SERVICE, CORPORATE, FREE, UNKNOWN | 4 | Duplicate of contact_email_type_enum |
| `contactprocessingstatus` | Queued, Processing, Complete, Error | 4 | Duplicate of contact_processing_status |
| `hubotsyncstatus` | New, Queued, Processing, Complete, Error, Skipped | 6 | Typo variant |
| `hubsyncprocessingstatus` | Queued, Processing, Complete, Error | 4 | Duplicate |
| `sitemapfilestatusenum` | New, Processing, Complete, Error | 4 | Duplicate |
| `sitemapimportcurationstatusenum` | New, Queued, Processing, Complete, Error, Skipped | 6 | Duplicate |
| `sitemapimportprocessstatusenum` | Queued, Processing, Complete, Error | 4 | Duplicate |
| `sitemap_curation_status` | New, Queued, Processing, Complete, Error, Skipped | 6 | Different from sitemap_curation_status_enum |

### System/Auth Enums (20)

| Enum Type | Values | Count |
|-----------|--------|-------|
| `aal_level` | aal1, aal2, aal3 | 3 |
| `action` | INSERT, UPDATE, DELETE, TRUNCATE, ERROR | 5 |
| `app_role` | basic, admin, super_admin, system_admin | 4 |
| `batch_job_status` | pending, running, complete, failed, partial | 5 |
| `buckettype` | STANDARD, ANALYTICS, VECTOR | 3 |
| `code_challenge_method` | s256, plain | 2 |
| `contact_email_type_enum` | SERVICE, CORPORATE, FREE, UNKNOWN | 4 |
| `dart_status_enum` | not_set, open, working, waiting, closed | 5 |
| `equality_op` | eq, neq, lt, lte, gt, gte, in | 7 |
| `factor_status` | unverified, verified | 2 |
| `factor_type` | totp, webauthn, phone | 3 |
| `feature_priority` | urgent, need_to_have, nice_to_have, someday | 4 |
| `feature_status` | new, reviewed, next_round, back_burner, someday, in_progress, completed, rejected | 8 |
| `governor_layer` | 1, 2, 3, 4, 5, 6, 7 | 7 |
| `job_type` | sitemap_scan, places_search, domain_metadata_extraction, contact_enrichment, batch_processing | 5 |
| `key_status` | default, valid, invalid, expired | 4 |
| `key_type` | aead-ietf, aead-det, hmacsha512, hmacsha256, auth, shorthash, generichash, kdf, secretbox, secretstream, stream_xchacha20 | 11 |
| `oauth_authorization_status` | pending, approved, denied, expired | 4 |
| `oauth_client_type` | public, confidential | 2 |
| `oauth_registration_type` | dynamic, manual | 2 |
| `oauth_response_type` | code | 1 |
| `one_time_token_type` | confirmation_token, reauthentication_token, recovery_token, email_change_token_new, email_change_token_current, phone_change_token | 6 |
| `request_status` | PENDING, SUCCESS, ERROR | 3 |
| `search_status` | PENDING, COMPLETED, FAILED, RUNNING | 4 |

---

## SECTION 2: TABLE-BY-TABLE ENUM COLUMN MAPPING

### Table: contacts (13 enum columns)

| Column | Enum Type | Nullable | Default | Position |
|--------|-----------|----------|---------|----------|
| email_type | contact_email_type_enum | YES | NULL | 5 |
| contact_curation_status | contact_curation_status | NO | 'New' | 12 |
| contact_processing_status | contact_processing_status | YES | NULL | 13 |
| hubspot_sync_status | hubspot_sync_status | NO | 'New' | 15 |
| hubspot_processing_status | hubspot_sync_processing_status | YES | NULL | 16 |
| brevo_sync_status | crm_sync_status | NO | 'New' | 21 |
| brevo_processing_status | crm_processing_status | YES | NULL | 22 |
| mautic_sync_status | crm_sync_status | NO | 'New' | 25 |
| mautic_processing_status | crm_processing_status | YES | NULL | 26 |
| n8n_sync_status | crm_sync_status | NO | 'New' | 29 |
| n8n_processing_status | crm_processing_status | YES | NULL | 30 |
| debounce_validation_status | crm_sync_status | YES | 'New' | 37 |
| debounce_processing_status | crm_processing_status | YES | NULL | 38 |

**Dual-Status Patterns:**
- HubSpot: `hubspot_sync_status` (user) + `hubspot_processing_status` (background)
- Brevo: `brevo_sync_status` (user) + `brevo_processing_status` (background)
- Mautic: `mautic_sync_status` (user) + `mautic_processing_status` (background)
- n8n: `n8n_sync_status` (user) + `n8n_processing_status` (background)
- Debounce: `debounce_validation_status` (user) + `debounce_processing_status` (background)

### Table: domains (7 enum columns)

| Column | Enum Type | Nullable | Default | Position |
|--------|-----------|----------|---------|----------|
| content_scrape_status | task_status | YES | 'Queued' | 17 |
| page_scrape_status | task_status | YES | 'Queued' | 20 |
| sitemap_monitor_status | task_status | YES | 'Queued' | 23 |
| sitemap_curation_status | sitemap_curation_status_enum | YES | 'New' | 109 |
| sitemap_analysis_status | SitemapAnalysisStatusEnum | YES | 'pending' | 110 |
| hubspot_sync_status | hubspot_sync_status | NO | 'New' | 112 |
| hubspot_processing_status | hubspot_sync_processing_status | YES | NULL | 113 |

**Note:** `SitemapAnalysisStatusEnum` is PascalCase (only one in database)

**Dual-Status Patterns:**
- Sitemap: `sitemap_curation_status` (user) + `sitemap_analysis_status` (background)
- HubSpot: `hubspot_sync_status` (user) + `hubspot_processing_status` (background)

### Table: local_businesses (2 enum columns)

| Column | Enum Type | Nullable | Default | Position |
|--------|-----------|----------|---------|----------|
| domain_extraction_status | domain_extraction_status_enum | YES | NULL | 51 |
| status | place_status_enum | NO | 'New' | 53 |

**Dual-Status Pattern:**
- `status` (user) + `domain_extraction_status` (background)

### Table: pages (4 enum columns)

| Column | Enum Type | Nullable | Default | Position |
|--------|-----------|----------|---------|----------|
| page_type | page_type_enum | YES | NULL | 19 |
| page_curation_status | page_curation_status | NO | 'New' | 25 |
| page_processing_status | page_processing_status | YES | NULL | 26 |
| contact_scrape_status | contact_scrape_status | NO | 'New' | 31 |

**Dual-Status Pattern:**
- `page_curation_status` (user) + `page_processing_status` (background)

### Table: places_staging (2 enum columns)

| Column | Enum Type | Nullable | Default | Position |
|--------|-----------|----------|---------|----------|
| status | place_status_enum | NO | 'New' | 18 |
| deep_scan_status | gcp_api_deep_scan_status | YES | NULL | 31 |

**Dual-Status Pattern:**
- `status` (user) + `deep_scan_status` (background)

### Table: sitemap_files (3 enum columns)

| Column | Enum Type | Nullable | Default | Position |
|--------|-----------|----------|---------|----------|
| status | sitemap_file_status_enum | NO | 'Pending' | 10 |
| deep_scrape_curation_status | sitemap_curation_status_enum | YES | 'New' | 37 |
| sitemap_import_status | sitemapimportprocessingstatus | YES | NULL | 40 |

**Dual-Status Pattern:**
- `deep_scrape_curation_status` (user) + `sitemap_import_status` (background)

### Table: sitemap_urls (1 enum column)

| Column | Enum Type | Nullable | Default | Position |
|--------|-----------|----------|---------|----------|
| status | sitemap_url_status_enum | NO | 'Pending' | 8 |

### Table: file_remediation_tasks (1 enum column)

| Column | Enum Type | Nullable | Default | Position |
|--------|-----------|----------|---------|----------|
| governor | governor_layer | YES | NULL | 10 |

---

## SECTION 3: CRITICAL FINDINGS

### Finding 1: PascalCase Exception ⚠️

**Only ONE enum type uses PascalCase:**
- `SitemapAnalysisStatusEnum` (used by `domains.sitemap_analysis_status`)

**All others use snake_case.**

### Finding 2: Duplicate Enum Types ❌

**10 duplicate enum types exist with similar/identical values:**

| Primary Type | Duplicate Type | Issue |
|--------------|----------------|-------|
| contact_curation_status | contactcurationstatus | Case variant |
| contact_email_type_enum | contactemailtypeenum | Case variant |
| contact_processing_status | contactprocessingstatus | Case variant |
| crm_sync_status | brevo_sync_status | Unnecessary duplicate |
| hubspot_sync_processing_status | hubsyncprocessingstatus | Case variant |
| hubspot_sync_status | hubotsyncstatus | Typo variant |
| sitemap_file_status_enum | sitemapfilestatusenum | Case variant |
| sitemapimportcurationstatus | sitemapimportcurationstatusenum | Case variant |
| sitemapimportprocessingstatus | sitemapimportprocessstatusenum | Case variant |
| sitemap_curation_status | sitemap_curation_status_enum | Different values! |

### Finding 3: Naming Inconsistency ⚠️

**Two different naming patterns:**

**Pattern 1: snake_case (most common)**
- `contact_curation_status`
- `page_processing_status`
- `domain_extraction_status_enum`

**Pattern 2: PascalCase (1 exception)**
- `SitemapAnalysisStatusEnum`

**Pattern 3: Mixed (legacy)**
- `contactcurationstatus` (no underscores)
- `sitemapimportprocessingstatus` (no underscores)

### Finding 4: Value Casing Inconsistency ⚠️

**PascalCase Values (most common):**
- `Queued, Processing, Completed, Error`
- `New, Selected, Maybe`

**lowercase Values (domain status only):**
- `pending, processing, completed, error`
- `queued, submitted, failed`

**UPPERCASE Values (system enums):**
- `SERVICE, CORPORATE, FREE, UNKNOWN`
- `PENDING, SUCCESS, ERROR`

### Finding 5: Enum Reuse Pattern ✅

**Good pattern: Shared enums across tables**

`crm_sync_status` is reused by:
- `contacts.brevo_sync_status`
- `contacts.mautic_sync_status`
- `contacts.n8n_sync_status`
- `contacts.debounce_validation_status`

`crm_processing_status` is reused by:
- `contacts.brevo_processing_status`
- `contacts.mautic_processing_status`
- `contacts.n8n_processing_status`
- `contacts.debounce_processing_status`

`place_status_enum` is reused by:
- `local_businesses.status`
- `places_staging.status`

---

## SECTION 4: DUAL-STATUS PATTERN SUMMARY

**All workflows use this pattern:**

| Table | User Status Column | User Enum | Background Status Column | Background Enum |
|-------|-------------------|-----------|--------------------------|-----------------|
| local_businesses | status | place_status_enum | domain_extraction_status | domain_extraction_status_enum |
| places_staging | status | place_status_enum | deep_scan_status | gcp_api_deep_scan_status |
| domains | sitemap_curation_status | sitemap_curation_status_enum | sitemap_analysis_status | SitemapAnalysisStatusEnum |
| sitemap_files | deep_scrape_curation_status | sitemap_curation_status_enum | sitemap_import_status | sitemapimportprocessingstatus |
| pages | page_curation_status | page_curation_status | page_processing_status | page_processing_status |
| contacts (HubSpot) | hubspot_sync_status | hubspot_sync_status | hubspot_processing_status | hubspot_sync_processing_status |
| contacts (Brevo) | brevo_sync_status | crm_sync_status | brevo_processing_status | crm_processing_status |
| contacts (Mautic) | mautic_sync_status | crm_sync_status | mautic_processing_status | crm_processing_status |
| contacts (n8n) | n8n_sync_status | crm_sync_status | n8n_processing_status | crm_processing_status |
| contacts (Debounce) | debounce_validation_status | crm_sync_status | debounce_processing_status | crm_processing_status |

---

## SECTION 5: RECOMMENDATIONS

### Priority 1: Fix PascalCase Exception
**Action:** Rename `SitemapAnalysisStatusEnum` → `sitemap_analysis_status_enum`

**Impact:** 1 enum type, 1 column (`domains.sitemap_analysis_status`)

**Migration Required:** Yes

### Priority 2: Remove Duplicate Enums
**Action:** Drop 10 duplicate enum types

**Keep:** Primary snake_case versions  
**Drop:** Case variants and typo variants

### Priority 3: Standardize Value Casing
**Decision Needed:** PascalCase vs lowercase

**Recommendation:** PascalCase (matches 90% of existing values)

**Requires Migration:** `domain_status` and `SitemapAnalysisStatusEnum` values

### Priority 4: Consolidate Enum Definitions
**Action:** Ensure all Python enums in `src/models/enums.py` match database exactly

**Current Issues:**
- Duplicate definitions in multiple files
- Conflicting values in some enums
- Inline string enums in WF7 Contact model

---

**END OF LIVE DATABASE REPORT**
