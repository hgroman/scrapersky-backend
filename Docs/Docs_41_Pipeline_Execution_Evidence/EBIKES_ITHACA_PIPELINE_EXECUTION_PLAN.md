# WF1-WF7 SEQUENTIAL PIPELINE EXECUTION PLAN: Ebikes in Ithaca, NY

**CRITICAL: THIS IS A SEQUENTIAL PIPELINE - EACH WORKFLOW DEPENDS ON THE PREVIOUS ONE'S RESULTS**

**Execution Date:** 2025-08-24  
**Target:** Complete end-to-end SEQUENTIAL pipeline test for ebike businesses in Ithaca, NY  
**Objective:** Prove full WF1-WF7 functionality with real data flowing through each stage

---

## Executive Summary

**SEQUENTIAL PIPELINE EXECUTION PLAN**

This is a SEQUENTIAL pipeline where:
- WF1 → produces places that feed into WF2
- WF2 → produces selected places that feed into WF3  
- WF3 → produces local businesses that feed into WF4
- WF4 → produces domains that feed into WF5
- WF5 → produces sitemap files that feed into WF6
- WF6 → produces pages that feed into WF7
- WF7 → produces final extracted content

**EACH WORKFLOW MUST COMPLETE AND PRODUCE FRUIT BEFORE THE NEXT CAN BEGIN**

The YAML tracker captures the OUTPUT of each workflow and uses it as INPUT for the next workflow. No skipping steps. No parallel execution. SEQUENTIAL ONLY.

---

## Phase 1: Infrastructure Setup

### 1.1 Authentication Setup
- **JWT Token Generation**: Using Docker container environment
- **Token**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwaXBlbGluZV90ZXN0X3VzZXIiLCJleHAiOjE3NTYwNTk0MDF9.lB0u-D1KFkZaUpP8B8PgIyfwdPgWv5pJfoesgDpyXyE`
- **Valid Until**: 2025-08-25 (1 hour from generation)

### 1.2 Database State Preparation
- **Pre-execution Table Counts**: Will be captured before each workflow
- **Post-execution Verification**: Record counts and status changes verified
- **Foreign Key Tracking**: Relationships between tables documented

---

## Phase 2: Sequential Workflow Execution

## WF1: Scout (Business Discovery)

**Purpose**: Discover ebike businesses in Ithaca, NY using Google Maps API

### API Configuration
- **Endpoint**: `POST /api/v3/localminer-discoveryscan/search/places`
- **Method**: POST
- **Authentication**: Bearer JWT token (OAuth2PasswordBearer)
- **Content-Type**: application/json
- **Request Schema**: PlacesSearchRequest
- **Response Schema**: Generic object (200) or HTTPValidationError (422)

### Request Schema (PlacesSearchRequest)
```json
{
  "business_type": "string" (required),
  "location": "string" (required),
  "radius_km": "integer" (optional, default: 10),
  "tenant_id": "string|null" (optional)
}
```

### Example Request
```json
{
  "business_type": "ebike bicycle electric bike shop",
  "location": "Ithaca, NY", 
  "radius_km": 10,
  "tenant_id": null
}
```

**SEQUENTIAL PIPELINE REQUIREMENT**: This workflow produces place IDs that are used as input for WF2.

### Response Schema
```json
{
  "job_id": "string",
  "status_url": "string"
}
```

### Database Impact
- **Primary Table**: `jobs` - New job record created
- **Secondary Table**: `places_staging` - Discovered places stored
- **Key Fields**:
  - `jobs.id` (UUID, primary key)
  - `jobs.status` (processing status)
  - `places_staging.search_job_id` (foreign key to jobs.id)
  - `places_staging.status` (default: "New")

### Verification Steps
1. Count records in `jobs` table before/after
2. Count records in `places_staging` table before/after
3. Verify search_job_id linkage between tables
4. Check job status progression through polling endpoint

---

## WF2: Analyst (Staging to Selection)

**Purpose**: Move discovered places from staging to selection for deeper processing

### API Configuration
- **Endpoint**: `POST /api/v3/localminer-discoveryscan/places/staging/status`
- **Method**: POST
- **Authentication**: Bearer JWT token (OAuth2PasswordBearer)
- **Content-Type**: application/json
- **Query Parameters**: status (required), tenant_id (optional)
- **Request Body**: Array of place IDs

### Request Schema
**Query Parameters:**
- `status`: string (required) - New status value
- `tenant_id`: string|null (optional) - Optional tenant ID

**Request Body:**
```json
["place_id_1", "place_id_2"]
```

### Example Request
```bash
POST /api/v3/localminer-discoveryscan/places/staging/status?status=Selected
Content-Type: application/json

["ChIJnU1g142B0IkRlVexMR238G4", "ChIJv353-yOB0IkRLq1OOEjlWp4"]
```

**SEQUENTIAL PIPELINE REQUIREMENT**: Use ACTUAL place IDs from WF1 results. This workflow produces selected places that trigger creation of local_business records used in WF3.

### Database Impact
- **Primary Table**: `places_staging`
- **Key Changes**: 
  - `status` field updated from "New" to "Selected"
  - `updated_at` timestamp updated
  - Records prepared for WF3 processing

### Verification Steps
1. Count places_staging records by status before/after
2. Verify specific place_ids status changes
3. Check updated_at timestamps

---

## WF3: Navigator (Business Curation)

**Purpose**: Process selected places into local_businesses table and queue for domain extraction

### API Configuration  
- **Endpoint**: `PUT /api/v3/local-businesses/status`
- **Method**: PUT
- **Authentication**: Bearer JWT token (OAuth2PasswordBearer)
- **Content-Type**: application/json
- **Request Schema**: LocalBusinessBatchStatusUpdateRequest
- **Response Schema**: Generic object (200) or HTTPValidationError (422)

### Request Schema (LocalBusinessBatchStatusUpdateRequest)
```json
{
  "local_business_ids": ["string (uuid format)"],
  "status": "LocalBusinessApiStatusEnum"
}
```

### LocalBusinessApiStatusEnum Values
- "New"
- "Selected"
- "Maybe"
- "Not a Fit"
- "Archived"

### Example Request
```json
{
  "local_business_ids": ["02a149f9-ee77-4b33-a227-7a536b784df8", "013d7ea2-79b9-4943-8a43-4f6340327f16"],
  "status": "Selected"
}
```

**SEQUENTIAL PIPELINE REQUIREMENT**: Use ACTUAL local_business_ids created from WF2 selected places. This workflow queues businesses for domain extraction and produces domain records used in WF4.

### Database Impact
- **Primary Table**: `local_businesses`
- **Key Changes**:
  - `status` updated to "Selected" 
  - `domain_extraction_status` set to "Queued"
  - `updated_at` timestamp updated
  - Triggers background domain extraction process

### Verification Steps
1. Count local_businesses records by status
2. Verify domain_extraction_status changes to "Queued"
3. Check background scheduler picks up queued businesses

---

## WF4: Surveyor (Domain Extraction & Curation)

**Purpose**: Extract domains from businesses and curate for sitemap analysis

### API Configuration
- **Endpoint**: `PUT /api/v3/domains/sitemap-curation/status`  
- **Method**: PUT
- **Authentication**: Bearer JWT token (OAuth2PasswordBearer)
- **Content-Type**: application/json
- **Request Schema**: DomainBatchCurationStatusUpdateRequest
- **Response Schema**: Object with integer counts (200) or HTTPValidationError (422)

### Request Schema (DomainBatchCurationStatusUpdateRequest)
```json
{
  "domain_ids": ["string (uuid4 format)"],
  "sitemap_curation_status": "SitemapCurationStatusApiEnum"
}
```

### SitemapCurationStatusApiEnum Values
- "New"
- "Selected"
- "Maybe"
- "Not a Fit"
- "Archived"

### Example Request
```json
{
  "domain_ids": ["12332a57-0c58-4c06-826f-e358636f5803", "cfe54fc0-54f2-4510-8f8b-52dd94cf7e55"],
  "sitemap_curation_status": "Selected"
}
```

**SEQUENTIAL PIPELINE REQUIREMENT**: Use ACTUAL domain_ids extracted from WF3 selected businesses. This workflow triggers sitemap analysis for the domains used in WF5.

### Database Impact
- **Primary Table**: `domains`
- **Key Changes**:
  - `sitemap_curation_status` updated to "Selected"
  - `sitemap_analysis_status` potentially triggered to "queued"
  - Background sitemap analysis initiated

### Verification Steps
1. Count domains by sitemap_curation_status
2. Verify sitemap_analysis_status changes
3. Monitor background sitemap analysis queue

---

## WF5: Flight Planner (Sitemap Analysis)

**Purpose**: Analyze domains for sitemap files and extract URL structure

### API Configuration
- **Endpoint**: `POST /api/v3/sitemap/scan`
- **Method**: POST  
- **Authentication**: None required
- **Content-Type**: application/json
- **Request Schema**: SitemapScrapingRequest
- **Response Schema**: SitemapScrapingResponse (202) or HTTPValidationError (422)

### Request Schema (SitemapScrapingRequest)
```json
{
  "base_url": "string" (required),
  "max_pages": "integer" (optional, default: 1000),
  "tenant_id": "string|null" (optional)
}
```

### Response Schema (SitemapScrapingResponse)
```json
{
  "job_id": "string" (required),
  "status_url": "string" (required),
  "created_at": "string|null" (optional)
}
```

### Example Request
```json
{
  "base_url": "https://fingerlakeselectricbikes.com",
  "max_pages": 1000,
  "tenant_id": null
}
```

**SEQUENTIAL PIPELINE REQUIREMENT**: Use ACTUAL domain URLs from WF4 selected domains. This workflow produces sitemap_file records with IDs used in WF6.

### Database Impact
- **Primary Tables**: 
  - `sitemap_files` - Discovered sitemap files
  - `sitemap_urls` - Individual URLs from sitemaps
- **Key Fields**:
  - `sitemap_files.url` (sitemap file URLs)
  - `sitemap_files.sitemap_type` (index, standard, etc.)
  - `sitemap_urls.url` (individual page URLs)

### Verification Steps
1. Count sitemap_files records before/after
2. Count sitemap_urls records before/after  
3. Verify domain relationships
4. Check sitemap file types discovered

---

## WF6: Recorder (Sitemap Import)

**Purpose**: Import sitemap files and create page records for content extraction

### API Configuration
- **Endpoint**: `PUT /api/v3/sitemap-files/sitemap_import_curation/status`
- **Method**: PUT
- **Authentication**: Bearer JWT token (OAuth2PasswordBearer)
- **Content-Type**: application/json
- **Request Schema**: SitemapFileBatchUpdate
- **Response Schema**: Object with integer counts (200), Not found (404), or HTTPValidationError (422)

### Request Schema (SitemapFileBatchUpdate)
```json
{
  "sitemap_file_ids": ["string (uuid format)"],
  "deep_scrape_curation_status": "SitemapImportCurationStatusEnum"
}
```

### SitemapImportCurationStatusEnum Values
- "New"
- "Selected"
- "Maybe"
- "Not a Fit"
- "Archived"

**CRITICAL**: Field is `deep_scrape_curation_status` NOT `sitemap_import_curation_status`

### Example Request
```json
{
  "sitemap_file_ids": ["c63ed0f7-e259-46bf-953e-0909d0b54dc3", "b665c6c6-9acd-4b6b-91e6-22f3ce4ad3b2"],
  "deep_scrape_curation_status": "Selected"
}
```

**SEQUENTIAL PIPELINE REQUIREMENT**: Use ACTUAL sitemap_file_ids discovered in WF5. This workflow creates page records with IDs used in WF7.

### Database Impact
- **Primary Tables**:
  - `sitemap_files` - Import status updated
  - `pages` - New page records created from sitemap URLs
- **Key Changes**:
  - `sitemap_import_curation_status` → "Selected" 
  - `pages` table populated with URLs from selected sitemaps
  - `pages.page_curation_status` set to initial state

### Verification Steps  
1. Count sitemap_files by import status
2. Count pages records before/after
3. Verify page-to-sitemap relationships
4. Check page URLs populated correctly

---

## WF7: Extractor (Content Processing)

**Purpose**: Extract content from curated pages using dual-status processing pattern

### API Configuration
- **Endpoint**: `PUT /api/v3/pages/status`
- **Method**: PUT
- **Authentication**: Bearer JWT token (OAuth2PasswordBearer)
- **Content-Type**: application/json
- **Request Schema**: PageCurationBatchStatusUpdateRequest
- **Response Schema**: PageCurationBatchUpdateResponse (200) or HTTPValidationError (422)

### Request Schema (PageCurationBatchStatusUpdateRequest)
```json
{
  "page_ids": ["string (uuid format)"],
  "status": "PageCurationStatus"
}
```

### PageCurationStatus Values
- "New"
- "Queued"
- "Processing"
- "Complete"
- "Error"
- "Skipped"

### Response Schema (PageCurationBatchUpdateResponse)
```json
{
  "updated_count": "integer",
  "queued_count": "integer"
}
```

### Example Request
```json
{
  "page_ids": ["uuid_1", "uuid_2"],
  "status": "Queued"
}
```

**SEQUENTIAL PIPELINE REQUIREMENT**: Use ACTUAL page_ids created from WF6 sitemap import. This workflow extracts content from the actual pages created by the pipeline.

### Database Impact
- **Primary Table**: `pages`
- **Key Changes** (Dual-Status Pattern):
  - `page_curation_status` → "Queued"
  - `page_processing_status` → "Queued" 
  - Background content extraction initiated
  - Extracted content stored in pages table

### Verification Steps
1. Count pages by curation status
2. Verify dual-status pattern implementation  
3. Monitor background processing queue
4. Check extracted content population

---

## Phase 3: Comprehensive Verification

### 3.1 End-to-End Data Flow Verification
- **Search → Places**: Jobs table to places_staging 
- **Places → Businesses**: places_staging to local_businesses
- **Businesses → Domains**: local_businesses to domains  
- **Domains → Sitemaps**: domains to sitemap_files/sitemap_urls
- **Sitemaps → Pages**: sitemap_files to pages
- **Pages → Content**: pages with extracted content

### 3.2 Pipeline Metrics Collection
- Total execution time for complete pipeline
- Record counts at each stage
- Success/failure rates
- Background processing completion rates
- Final content extraction samples

### 3.3 Error Handling Documentation
- API error responses captured
- Database constraint violations logged
- Background job failures tracked
- Recovery procedures documented

---

## Success Criteria

✅ **Complete Pipeline Execution**: All WF1-WF7 stages completed successfully  
✅ **Database State Verified**: Pre/post counts documented for all tables  
✅ **API Responses Captured**: All HTTP requests/responses logged  
✅ **Relationships Verified**: Foreign key relationships maintained throughout  
✅ **Background Processing**: Schedulers successfully process queued items  
✅ **Content Extraction**: Final extracted content proves ebike business data processed  

---

## Deliverables

1. **Live Execution YAML**: Real-time tracking document with all inputs/outputs
2. **Database Verification Report**: Before/after counts for all tables
3. **API Response Log**: Complete HTTP request/response documentation  
4. **Pipeline Performance Metrics**: Timing and throughput analysis
5. **Final Content Samples**: Extracted ebike business information as proof of success

**No scope creep. No hallucinations. Only verified, documented functionality.**

---

## Journal Entry - Pipeline State Management Discovery

**Date**: 2025-08-24  
**Context**: During WF6 execution after successful WF1-WF5 completion

### Issue Discovered
When attempting to execute WF6, initially tried to use sitemap file IDs from YAML tracker but encountered confusion about where to find the "current" pipeline state.

### Initial Misunderstanding
Assumed the system needed complex pipeline orchestration with execution tracking, state management, and cross-workflow result APIs. Believed this was a production architecture gap.

### Actual Reality - MVP Database State Pattern
**THE SYSTEM WORKS CORRECTLY FOR MVP USE:**

1. **Database State IS Pipeline State**: 
   - WF5 creates records in `sitemap_files` table with `deep_scrape_curation_status = "New"`
   - WF6 queries for "New" records, updates them to "Selected", creates `pages`
   - WF7 queries for "New" pages, updates them to "Queued" for processing

2. **Status-Based Workflow Orchestration**:
   - `New` → `Selected` → `Queued` status transitions ARE the pipeline flow
   - No external orchestration needed for single-tenant MVP
   - Database state management handles workflow sequencing

3. **Correct WF6 Execution Pattern**:
   ```sql
   -- Find records ready for WF6
   SELECT id FROM sitemap_files 
   WHERE deep_scrape_curation_status = 'New' 
   AND domain_name = 'fingerlakeselectricbikes.com'
   
   -- Use those IDs in WF6 API call
   ```

### Key Insight
For MVP with single user, **database record statuses provide sufficient workflow orchestration**. The confusion arose from expecting external pipeline tracking when the system correctly uses database state transitions to manage workflow progression.

**System Design is Appropriate**: Individual workflow APIs + database state management = functional sequential pipeline for MVP use case.