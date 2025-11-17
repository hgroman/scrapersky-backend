# WF4→WF5→WF7 Complete Pipeline Documentation Index
**Created:** November 17, 2025 1:59 AM  
**Status:** ✅ COMPLETE - All workflows documented and verified operational  
**Related Work Orders:** WO-004 Multi-Scheduler Split, WO-004 Hotfix Post-Mortem

---

## Documentation Structure

This is the master index for the complete WF4→WF5→WF7 pipeline documentation. All moving parts, relationships, and data flows are documented across multiple files for clarity and maintainability.

---

## Core Documentation Files

### 1. [PIPELINE_OVERVIEW.md](./WF4_WF5_WF7_PIPELINE_OVERVIEW.md)
**Purpose:** High-level overview and quick reference

**Contents:**
- Executive summary
- Complete data flow diagram
- Critical status fields
- Dual-status pattern explanation
- Quick reference for common operations
- Critical fix summary (Commit 9f091f6)

**When to use:** Start here for big-picture understanding

---

### 2. [DATABASE_SCHEMA.md](./WF4_WF5_WF7_DATABASE_SCHEMA.md)
**Purpose:** Complete database schema documentation

**Contents:**
- Table structures (domains, sitemap_files, pages, jobs)
- Field definitions and types
- Indexes and constraints
- Relationships and foreign keys
- Status value enumerations
- Typical record lifecycles
- Cross-table query examples
- Schema gaps and issues

**When to use:** 
- Designing new features
- Writing database queries
- Understanding data relationships
- Troubleshooting data issues

---

### 3. [SERVICES.md](./WF4_WF5_WF7_SERVICES.md)
**Purpose:** Service layer architecture and patterns

**Contents:**
- Service overview and responsibilities
- DomainToSitemapAdapterService (WF4)
- SitemapProcessingService (WF4→WF5)
- SitemapImportService (WF5)
- PageCurationService (WF7)
- JobService (supporting)
- Service communication patterns (✅ correct vs ❌ wrong)
- Dependencies graph
- Configuration and settings
- Testing recommendations

**When to use:**
- Implementing new services
- Debugging service issues
- Understanding service dependencies
- Refactoring code

---

### 4. [GAPS_IMPROVEMENTS.md](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md)
**Purpose:** Identified issues and enhancement opportunities

**Contents:**
- Critical issues (P0) - Fix immediately
- High priority (P1) - Fix this sprint
- Medium priority (P2) - Fix next sprint
- Low priority (P3) - Nice to have
- GUI improvements needed
- Architecture improvements
- Estimated effort and sprint planning

**When to use:**
- Sprint planning
- Prioritizing work
- Understanding technical debt
- Planning improvements

---

## Supporting Documentation

### 5. [WO-004_HOTFIX_POSTMORTEM.md](../Work_Orders/WO-004_HOTFIX_POSTMORTEM.md)
**Purpose:** Post-mortem of Nov 17, 2025 hotfix

**Contents:**
- Complete timeline (April 2025 → Nov 17, 2025)
- Root cause analysis
- Architecture diagrams (before/after)
- Why it was painful
- Lessons learned
- Action items
- Verification checklist

**When to use:**
- Understanding historical context
- Learning from mistakes
- Onboarding new team members
- Preventing similar issues

---

### 6. [WO-004_DEPLOYMENT_MONITORING.md](../Work_Orders/WO-004_DEPLOYMENT_MONITORING.md)
**Purpose:** Deployment guide and monitoring

**Contents:**
- Deployment checklist
- Monitoring queries
- Rollback procedures
- Health check endpoints

**When to use:**
- Deploying changes
- Monitoring production
- Troubleshooting deployments

---

## Quick Navigation

### By Workflow

**WF4: Domain Curation**
- [Database Schema](./WF4_WF5_WF7_DATABASE_SCHEMA.md#table-domains)
- [Services](./WF4_WF5_WF7_SERVICES.md#wf4-services)
- [Critical Fix](./WF4_WF5_WF7_PIPELINE_OVERVIEW.md#critical-fix-nov-17-2025)

**WF5: Sitemap Import**
- [Database Schema](./WF4_WF5_WF7_DATABASE_SCHEMA.md#table-sitemap_files)
- [Services](./WF4_WF5_WF7_SERVICES.md#wf5-services)
- [Known Issues](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#1-sitemap-files-not-auto-queued)

**WF7: Page Curation**
- [Database Schema](./WF4_WF5_WF7_DATABASE_SCHEMA.md#table-pages)
- [Services](./WF4_WF5_WF7_SERVICES.md#wf7-services)
- [Auto-Selection Rules](./WF4_WF5_WF7_DATABASE_SCHEMA.md#auto-selection-rules)

### By Component

**Database Tables:**
- [domains](./WF4_WF5_WF7_DATABASE_SCHEMA.md#table-domains)
- [sitemap_files](./WF4_WF5_WF7_DATABASE_SCHEMA.md#table-sitemap_files)
- [pages](./WF4_WF5_WF7_DATABASE_SCHEMA.md#table-pages)
- [jobs](./WF4_WF5_WF7_DATABASE_SCHEMA.md#table-jobs)

**Services:**
- [DomainToSitemapAdapterService](./WF4_WF5_WF7_SERVICES.md#domaintositemapadapterservice)
- [SitemapProcessingService](./WF4_WF5_WF7_SERVICES.md#sitemapprocessingservice)
- [SitemapImportService](./WF4_WF5_WF7_SERVICES.md#sitemapimportservice)
- [PageCurationService](./WF4_WF5_WF7_SERVICES.md#pagecurationservice)

**Schedulers:**
- Domain Sitemap Submission (1 min interval)
- Sitemap Import (configurable)
- Page Curation (configurable)

**Status Fields:**
- [sitemap_analysis_status](./WF4_WF5_WF7_DATABASE_SCHEMA.md#status-values)
- [sitemap_import_status](./WF4_WF5_WF7_DATABASE_SCHEMA.md#status-values-1)
- [page_processing_status](./WF4_WF5_WF7_DATABASE_SCHEMA.md#status-values-2)

### By Task

**Implementing New Features:**
1. Check [GAPS_IMPROVEMENTS.md](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md) for known issues
2. Review [DATABASE_SCHEMA.md](./WF4_WF5_WF7_DATABASE_SCHEMA.md) for data model
3. Study [SERVICES.md](./WF4_WF5_WF7_SERVICES.md) for patterns
4. Follow service communication patterns

**Debugging Issues:**
1. Check [PIPELINE_OVERVIEW.md](./WF4_WF5_WF7_PIPELINE_OVERVIEW.md) for data flow
2. Review [DATABASE_SCHEMA.md](./WF4_WF5_WF7_DATABASE_SCHEMA.md) for queries
3. Check [HOTFIX_POSTMORTEM.md](../Work_Orders/WO-004_HOTFIX_POSTMORTEM.md) for similar issues
4. Use monitoring queries from [DEPLOYMENT_MONITORING.md](../Work_Orders/WO-004_DEPLOYMENT_MONITORING.md)

**Onboarding New Team Members:**
1. Start with [PIPELINE_OVERVIEW.md](./WF4_WF5_WF7_PIPELINE_OVERVIEW.md)
2. Read [HOTFIX_POSTMORTEM.md](../Work_Orders/WO-004_HOTFIX_POSTMORTEM.md) for context
3. Study [DATABASE_SCHEMA.md](./WF4_WF5_WF7_DATABASE_SCHEMA.md)
4. Review [SERVICES.md](./WF4_WF5_WF7_SERVICES.md)
5. Check [GAPS_IMPROVEMENTS.md](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md) for current work

---

## Key Concepts

### Dual-Status Pattern

Many tables have TWO status fields:
1. **Curation Status** - User decision (New/Selected/Rejected)
2. **Processing Status** - System state (Queued/Processing/Complete/Error)

**Rule:** When curation status → "Selected", processing status → "Queued"

**Examples:**
- domains: `sitemap_curation_status` → `sitemap_analysis_status`
- pages: `page_curation_status` → `page_processing_status`
- sitemap_files: ⚠️ Missing curation status (see [Gap #2](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#2-missing-sitemap_curation_status-field))

### Auto-Selection (Honeybee)

High-value pages are automatically selected during sitemap import:

**Criteria:**
- Category: CONTACT_ROOT, CAREER_CONTACT, or LEGAL_ROOT
- Confidence: >= 0.6
- Depth: <= 2

**Result:**
- `page_curation_status = 'Selected'`
- `page_processing_status = 'Queued'`
- `priority_level = 1`

### Service Communication Pattern

**✅ CORRECT: Direct Service Calls**
```python
service = SomeService()
result = await service.process(item_id, session)
```

**❌ WRONG: HTTP Calls Between Services**
```python
async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8000/api/...")
```

**Why:** HTTP calls don't trigger background tasks, add complexity, and create failure points.

---

## Critical Fixes Documented

### Fix #1: Background Task Trigger (Commit 9f091f6)
**Date:** November 17, 2025  
**Problem:** Jobs created but never processed  
**Solution:** Added `asyncio.create_task()` to trigger processing  
**Details:** [SERVICES.md - DomainToSitemapAdapterService](./WF4_WF5_WF7_SERVICES.md#critical-fix-commit-9f091f6---nov-17-2025)

### Fix #2: Direct Service Calls (Commit 1ffa371)
**Date:** November 17, 2025  
**Problem:** HTTP authentication failures after security fix  
**Solution:** Replaced HTTP calls with direct service calls  
**Details:** [HOTFIX_POSTMORTEM.md](../Work_Orders/WO-004_HOTFIX_POSTMORTEM.md#the-fix-commit-9f091f6)

### Fix #3: Sitemap Job Processor Disabled (Sept 9, 2025)
**Date:** September 9, 2025  
**Problem:** Scheduler disabled without replacement  
**Impact:** Silent failure for 2+ months  
**Details:** [HOTFIX_POSTMORTEM.md - Timeline](../Work_Orders/WO-004_HOTFIX_POSTMORTEM.md#timeline-of-events)

---

## Monitoring & Health Checks

### Key Metrics to Track

**Queue Depths:**
```sql
-- Domains waiting for sitemap discovery
SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued';

-- Sitemaps waiting for URL extraction
SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued';

-- Pages waiting for scraping
SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Queued';
```

**Stuck Jobs:**
```sql
-- Jobs stuck in pending > 5 minutes
SELECT COUNT(*) FROM jobs 
WHERE status = 'pending' 
AND created_at < NOW() - INTERVAL '5 minutes';
```

**Processing Rates:**
```sql
-- Pages processed in last hour
SELECT COUNT(*) FROM pages 
WHERE page_processing_status = 'Complete' 
AND updated_at > NOW() - INTERVAL '1 hour';
```

### Health Check Queries

See [DEPLOYMENT_MONITORING.md](../Work_Orders/WO-004_DEPLOYMENT_MONITORING.md) for complete monitoring guide.

---

## Common Troubleshooting Scenarios

### "Domains not being processed"

1. Check domain status: `SELECT sitemap_analysis_status FROM domains WHERE domain = 'example.com';`
2. If `NULL` → Not queued yet (set curation status to 'Selected')
3. If `queued` → Check scheduler is running
4. If `submitted` → Check for sitemap_files records
5. If `failed` → Check sitemap_analysis_error

**Reference:** [DATABASE_SCHEMA.md - Domains Lifecycle](./WF4_WF5_WF7_DATABASE_SCHEMA.md#typical-record-lifecycle)

### "Sitemaps discovered but not processed"

1. Check sitemap status: `SELECT sitemap_import_status FROM sitemap_files WHERE url = '...';`
2. If `NULL` → **Known Issue** - See [Gap #1](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#1-sitemap-files-not-auto-queued)
3. If `Queued` → Check scheduler is running
4. If `Processing` → Check for stuck job
5. If `Error` → Check sitemap_import_error

### "Pages not being scraped"

1. Check page status: `SELECT page_processing_status, page_curation_status FROM pages WHERE url = '...';`
2. If curation = `New` → Set to 'Selected' to trigger processing
3. If processing = `Queued` → Check scheduler is running
4. If processing = `Processing` → Check for stuck job
5. If processing = `Error` → Check page_processing_error

**Reference:** [SERVICES.md - PageCurationService](./WF4_WF5_WF7_SERVICES.md#pagecurationservice)

### "No contacts found in scraped pages"

1. Check page type: `SELECT page_type FROM pages WHERE url = '...';`
2. If `unknown` or product-related → Expected (product pages don't have contacts)
3. Check if contact pages were imported: `SELECT * FROM pages WHERE page_type LIKE '%CONTACT%';`
4. If no contact pages → Check if page-sitemap.xml was processed
5. Verify scraped_content: `SELECT scraped_content FROM pages WHERE page_processing_status = 'Complete';`

**Reference:** [DATABASE_SCHEMA.md - Auto-Selection Rules](./WF4_WF5_WF7_DATABASE_SCHEMA.md#auto-selection-rules)

---

## File Locations

### Source Code
```
src/
├── services/
│   ├── domain_to_sitemap_adapter_service.py (WF4)
│   ├── sitemap/
│   │   └── processing_service.py (WF4→WF5)
│   ├── sitemap_import_service.py (WF5)
│   ├── WF7_V2_L4_1of2_PageCurationService.py (WF7)
│   ├── domain_sitemap_submission_scheduler.py
│   ├── sitemap_import_scheduler.py
│   └── WF7_V2_L4_2of2_PageCurationScheduler.py
├── routers/
│   └── v3/
│       ├── WF4_V3_L3_1of1_DomainsRouter.py
│       ├── WF5_V3_L3_1of1_SitemapRouter.py
│       └── WF7_V3_L3_1of1_PagesRouter.py
└── models/
    ├── domain.py
    ├── sitemap.py
    └── page.py
```

### Documentation
```
Documentation/
├── Architecture/
│   ├── WF4_WF5_WF7_COMPLETE_INDEX.md (this file)
│   ├── WF4_WF5_WF7_PIPELINE_OVERVIEW.md
│   ├── WF4_WF5_WF7_DATABASE_SCHEMA.md
│   ├── WF4_WF5_WF7_SERVICES.md
│   └── WF4_WF5_WF7_GAPS_IMPROVEMENTS.md
└── Work_Orders/
    ├── WO-004_HOTFIX_POSTMORTEM.md
    └── WO-004_DEPLOYMENT_MONITORING.md
```

---

## Change Log

### November 17, 2025
- **Created:** Complete pipeline documentation (all files)
- **Fixed:** Background task trigger (Commit 9f091f6)
- **Fixed:** Service communication pattern (Commit 1ffa371)
- **Verified:** End-to-end pipeline operational
- **Documented:** 15 identified gaps and improvements

### September 9, 2025
- **Disabled:** Sitemap job processor in sitemap_scheduler.py
- **Impact:** Silent failure for 2+ months (undiscovered until Nov 17)

### April 24, 2025
- **Created:** domain_to_sitemap_adapter_service.py (with original bug)

---

## Next Steps

### Immediate (This Week)
1. Fix sitemap auto-queue issue ([Gap #1](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#1-sitemap-files-not-auto-queued))
2. Add sitemap_curation_status field ([Gap #2](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#2-missing-sitemap_curation_status-field))
3. Implement stuck job monitoring ([Gap #4](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#4-no-monitoring-for-stuck-jobs))

### Next Sprint
1. Add missing indexes ([Gap #6](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#6-missing-indexes-for-common-queries))
2. Implement retry logic ([Gap #8](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#8-no-retry-logic-for-failed-jobs))
3. Add GUI improvements ([Gaps #11-13](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#gui-improvements-needed))

### Future
1. Job table cleanup ([Gap #3](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#3-job-table-cleanup))
2. Progress tracking ([Gap #9](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#9-no-progress-tracking-for-long-jobs))
3. Page deduplication ([Gap #10](./WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#10-no-deduplication-of-pages))

---

## Contact & Ownership

**Documentation Owner:** Engineering Team  
**Last Updated By:** Cascade AI  
**Review Frequency:** After each major change  
**Next Review:** After Sprint 1 fixes complete

---

## Related Documentation

- [05_SCHEDULERS_WORKFLOWS.md](./05_SCHEDULERS_WORKFLOWS.md) - Original scheduler documentation
- [WO-001 & WO-002](../Work_Orders/) - Security fixes that exposed the bug
- [Honeybee Documentation](./honeybee/) - URL categorization system

---

**END OF INDEX**

For questions or updates, refer to the specific documentation files linked above.
