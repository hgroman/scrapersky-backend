# WF4→WF5→WF7 Complete Pipeline Map
**Last Updated:** November 17, 2025 1:59 AM  
**Status:** OPERATIONAL - All workflows verified end-to-end  
**Related:** WO-004 Hotfix Post-Mortem

---

## Executive Summary

### Pipeline Purpose
Extract domains from local businesses → Find sitemaps → Import URLs → Process pages for contact extraction

### Current State (Nov 17, 2025)
✅ **OPERATIONAL** - All three workflows functioning end-to-end after security fixes

### Key Metrics
- **Tables:** 4 (local_business, domains, sitemap_files, pages)
- **Services:** 6 core + 3 schedulers
- **API Endpoints:** 12 across 3 routers
- **Status Fields:** 8 tracking different stages
- **Background Jobs:** 3 schedulers on intervals

---

## Complete Data Flow

```
WF3: LocalBusiness
        ↓
WF4: Domain Extraction
        ↓
    domains table
    (sitemap_analysis_status: queued → submitted)
        ↓
    Domain Sitemap Submission Scheduler (1 min)
        ↓
    DomainToSitemapAdapterService
        ├─ Creates Job record
        ├─ Initializes _job_statuses
        └─ Triggers asyncio.create_task()
            ↓
        process_domain_with_own_session()
            ↓
WF5: Sitemap Discovery
        ↓
    sitemap_files table
    (sitemap_import_status: Queued → Complete)
        ↓
    Sitemap Import Scheduler
        ↓
    SitemapImportService
        ├─ Fetches sitemap XML
        ├─ Runs Honeybee categorization
        └─ Creates Page records
            ↓
WF7: Page Processing
        ↓
    pages table
    (page_processing_status: Queued → Complete)
        ↓
    Page Curation Scheduler
        ↓
    PageCurationService
        ├─ Scrapes via ScraperAPI
        ├─ Extracts contacts
        └─ Stores in scraped_content
```

---

## See Detailed Documentation

This overview is split into detailed documents:

1. **[DATABASE_SCHEMA.md](./WF4_WF5_WF7_DATABASE_SCHEMA.md)** - Complete table structures, relationships, indexes
2. **[SERVICES.md](./WF4_WF5_WF7_SERVICES.md)** - Service layer architecture, methods, dependencies
3. **[API_ROUTES.md](./WF4_WF5_WF7_API_ROUTES.md)** - All endpoints, request/response schemas
4. **[SCHEDULERS.md](./WF4_WF5_WF7_SCHEDULERS.md)** - Job timing, queries, configurations
5. **[STATUS_MACHINES.md](./WF4_WF5_WF7_STATUS_MACHINES.md)** - State transitions for all status fields
6. **[GAPS_IMPROVEMENTS.md](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md)** - Identified issues and enhancement opportunities

---

## Quick Reference

### Critical Status Fields

**domains table:**
- `sitemap_analysis_status`: queued → submitted → (stays submitted)
- `sitemap_curation_status`: New → Selected/Rejected

**sitemap_files table:**
- `sitemap_import_status`: Queued → Processing → Complete/Error
- `sitemap_curation_status`: New → Selected/Rejected (⚠️ may not exist)

**pages table:**
- `page_processing_status`: Queued → Processing → Complete/Error
- `page_curation_status`: New → Selected/Rejected

### Dual-Status Pattern

When user sets curation status to "Selected":
- **Domains:** Sets sitemap_analysis_status = "queued"
- **Pages:** Sets page_processing_status = "Queued"
- **Sitemaps:** ⚠️ May need implementation

### Auto-Selection Rules (Honeybee)

Pages auto-selected if:
- Category: CONTACT_ROOT, CAREER_CONTACT, or LEGAL_ROOT
- Confidence: >= 0.6
- Depth: <= 2
- Result: page_curation_status = "Selected", page_processing_status = "Queued", priority_level = 1

---

## Critical Fix (Nov 17, 2025)

**Problem:** Jobs created but never processed (silent failure since Sept 9)

**Root Cause:** DomainToSitemapAdapterService only created Job records, didn't trigger processing

**Solution:** Added background task trigger matching HTTP endpoint pattern:
1. Create Job in database
2. Initialize in _job_statuses (memory)
3. Call asyncio.create_task(process_domain_with_own_session())

**Commit:** 9f091f6
