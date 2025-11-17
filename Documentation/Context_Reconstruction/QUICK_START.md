# ScraperSky Backend - Quick Start Guide
**Read Time:** 5 minutes  
**Purpose:** Immediate orientation to the system  
**Last Updated:** November 17, 2025

---

## What This System Does (1 minute)

ScraperSky is a **business intelligence platform** that:
1. Extracts business data from Google Maps
2. Discovers company websites and sitemaps
3. Scrapes web pages for contact information
4. Curates and validates data through 7 workflows

**End Goal:** Provide clean, verified contact data for businesses

---

## The 7 Workflows (2 minutes)

### WF1: Single Search
**Purpose:** Search Google Maps for a single business  
**Input:** Search query (e.g., "eye doctors in Honolulu")  
**Output:** Place records with Google Maps data  
**Table:** `places`

### WF2: Deep Scan
**Purpose:** Enrich Place records with additional details  
**Input:** Place record  
**Output:** Enriched Place with photos, reviews, hours  
**Table:** `places` (updated)

### WF3: Domain Extraction
**Purpose:** Extract website domains from Place records  
**Input:** Place record with website  
**Output:** LocalBusiness → Domain records  
**Tables:** `local_business`, `domains`

### WF4: Sitemap Discovery
**Purpose:** Find sitemap files for domains  
**Input:** Domain record  
**Output:** SitemapFile records  
**Tables:** `domains` → `sitemap_files`  
**Scheduler:** Every 1 minute

### WF5: Sitemap Import
**Purpose:** Extract individual page URLs from sitemaps  
**Input:** SitemapFile record  
**Output:** Page records with Honeybee categorization  
**Tables:** `sitemap_files` → `pages`  
**Scheduler:** Configurable interval

### WF6: [Status Unknown - Needs Documentation]

### WF7: Page Curation / Contact Extraction
**Purpose:** Scrape pages and extract contact information  
**Input:** Page record  
**Output:** Contacts stored in `scraped_content` (JSONB)  
**Table:** `pages` (updated)  
**Scheduler:** Configurable interval

---

## Key Files (1 minute)

### Services (Business Logic)
```
src/services/
├── domain_to_sitemap_adapter_service.py (WF4)
├── sitemap/processing_service.py (WF4→WF5)
├── sitemap_import_service.py (WF5)
├── WF7_V2_L4_1of2_PageCurationService.py (WF7)
├── domain_sitemap_submission_scheduler.py
├── sitemap_import_scheduler.py
└── WF7_V2_L4_2of2_PageCurationScheduler.py
```

### API Routes
```
src/routers/v3/
├── WF4_V3_L3_1of1_DomainsRouter.py
├── WF5_V3_L3_1of1_SitemapRouter.py
└── WF7_V3_L3_1of1_PagesRouter.py
```

### Database Models
```
src/models/
├── place.py
├── local_business.py
├── domain.py
├── sitemap.py
└── page.py
```

### Documentation
```
Documentation/
├── RECONSTRUCT_CONTEXT.md (start here!)
├── Architecture/
│   ├── WF4_WF5_WF7_COMPLETE_INDEX.md
│   ├── WF4_WF5_WF7_DATABASE_SCHEMA.md
│   └── WF4_WF5_WF7_SERVICES.md
└── Work_Orders/
    ├── WO-004_HOTFIX_POSTMORTEM.md
    └── WO-005_KNOWLEDGE_REPOSITORY.md
```

---

## Essential Commands (1 minute)

### Check System Health
```sql
-- Via Supabase MCP tools
-- Queue depths
SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued';
SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued';
SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Queued';

-- Stuck jobs
SELECT COUNT(*) FROM jobs WHERE status = 'pending' 
AND created_at < NOW() - INTERVAL '5 minutes';

-- Recent activity
SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Complete' 
AND updated_at > NOW() - INTERVAL '1 hour';
```

### View Logs
- **Render.com:** https://dashboard.render.com (production logs)
- **Local:** Check terminal output when running locally

### Git History
```bash
# Recent changes
git log --oneline --since="7 days ago"

# Find specific changes
git log --all --grep="sitemap"

# See what changed
git show <commit-hash>
```

### Run Tests
```bash
# [Add test commands when available]
pytest tests/
```

---

## Critical Concepts

### Dual-Status Pattern
Tables have TWO status fields:
- **Curation Status:** User decision (New/Selected/Rejected)
- **Processing Status:** System state (Queued/Processing/Complete/Error)

**Rule:** When curation → "Selected", processing → "Queued"

**Example:**
- User selects domain → `sitemap_curation_status = 'Selected'`
- System auto-sets → `sitemap_analysis_status = 'queued'`
- Scheduler picks up and processes

### Auto-Selection (Honeybee)
High-value pages are automatically selected during import:
- **Criteria:** CONTACT_ROOT, CAREER_CONTACT, or LEGAL_ROOT
- **Confidence:** >= 0.6
- **Depth:** <= 2
- **Result:** Auto-set to "Selected" and "Queued" for processing

### Service Communication
**✅ CORRECT:** Direct service calls
```python
service = SomeService()
result = await service.process(item_id, session)
```

**❌ WRONG:** HTTP calls between services
```python
# DON'T DO THIS
async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8000/api/...")
```

---

## Common Issues

### "Jobs stuck in pending"
- **Cause:** Background task not triggered
- **Fix:** Ensure `asyncio.create_task()` is called after job creation
- **Reference:** INCIDENT-2025-11-17-sitemap-jobs-not-processing

### "No sitemaps found"
- **Cause:** Sitemap files created with NULL status
- **Fix:** Set `sitemap_import_status = 'Queued'`
- **Reference:** WF4_WF5_WF7_GAPS_IMPROVEMENTS.md #1

### "Pages not processing"
- **Cause:** Page not selected or scheduler not running
- **Fix:** Set `page_curation_status = 'Selected'`
- **Verify:** Check scheduler logs in Render.com

---

## Next Steps

### For Debugging
1. Read [HEALTH_CHECKS.md](./HEALTH_CHECKS.md)
2. Check [INCIDENTS/](../INCIDENTS/) for similar issues
3. Review [PATTERNS.md](./PATTERNS.md) for anti-patterns

### For Development
1. Read [SYSTEM_MAP.md](./SYSTEM_MAP.md) for architecture
2. Study [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md)
3. Check [PATTERNS.md](./PATTERNS.md) for correct patterns
4. Review [WF4_WF5_WF7_GAPS_IMPROVEMENTS.md](../Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md)

### For Onboarding
1. Complete [RECONSTRUCT_CONTEXT.md](./RECONSTRUCT_CONTEXT.md) checklist
2. Read all Phase 1 and Phase 2 documents
3. Run through health checks
4. Review recent incidents

---

## External Services

- **Database:** Supabase PostgreSQL (accessed via MCP)
- **Deployment:** Render.com (Docker containers)
- **Scraping:** ScraperAPI (costs 1 credit per page)
- **Categorization:** Honeybee (URL classification)

---

## Key Metrics

- **Tables:** 6 core tables (places, local_business, domains, sitemap_files, pages, jobs)
- **Services:** 6+ core services
- **Schedulers:** 3 main schedulers (1 min, configurable, configurable)
- **API Endpoints:** 12+ across 3 workflow routers
- **Status Fields:** 8+ tracking different stages

---

## Getting Help

1. **Check Documentation:** Start with RECONSTRUCT_CONTEXT.md
2. **Search Incidents:** Look in INCIDENTS/ for similar issues
3. **Review Patterns:** Check PATTERNS.md for correct approaches
4. **Investigate History:** Use ARCHAEOLOGY.md to trace code changes
5. **Check Decisions:** Read DECISIONS/ to understand "why"

---

**You now have enough context to start exploring the system. For deeper understanding, continue with [SYSTEM_MAP.md](./SYSTEM_MAP.md).**
