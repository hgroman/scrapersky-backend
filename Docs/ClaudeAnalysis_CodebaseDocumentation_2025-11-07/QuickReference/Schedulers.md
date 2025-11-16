# ScraperSky Scheduler - Quick Reference Summary

## Core Infrastructure

| Component | Details |
|-----------|---------|
| **Framework** | APScheduler (AsyncIOScheduler) |
| **Location** | `/src/scheduler_instance.py` |
| **Pattern** | Singleton shared instance |
| **Timezone** | UTC |
| **Lifecycle** | Started/shutdown via FastAPI lifespan |
| **Event Logging** | Yes (job_listener tracks execution) |

## Active Schedulers

| ID | Name | File | Workflow | Interval | Batch | Max Inst | Status |
|----|------|------|----------|----------|-------|---------|--------|
| `process_pending_domains` | Domain | `domain_scheduler.py` | WF3 | 1m | 50 | 3 | ✓ Active |
| `process_pending_jobs` | Sitemap Multi | `sitemap_scheduler.py` | WF2/WF3/WF5 | 1m | 25 | 3 | ⚠ High Risk |
| `process_pending_domain_sitemap_submissions` | Domain Sitemap | `domain_sitemap_submission_scheduler.py` | WF4 | 1m | 10 | 1 | ✓ Fixed |
| `process_sitemap_imports` | Sitemap Import | `sitemap_import_scheduler.py` | WF6 | 1m | 20 | 1 | ✓ Modern |
| `v2_page_curation_processor` | Page Curation | `WF7_V2_L4_2of2_PageCurationScheduler.py` | WF7 | 1m | 10 | 1 | ✓ Modern |

## Key Data Flows

### WF3 → WF4
```
domain_scheduler output:
  Domain.status = completed
  Domain.sitemap_analysis_status = queued ← QUEUE FOR WF4
```

### WF4 → WF5
```
domain_sitemap_submission_scheduler output:
  Domain.sitemap_analysis_status = submitted/failed

sitemap_import_scheduler processes:
  SitemapFile.sitemap_import_status = Queued
```

### WF5 → WF7
```
sitemap_import_scheduler creates:
  Page records with Page.page_processing_status = Queued

page_curation_scheduler processes:
  Page.page_processing_status = Queued
```

## Status Field Mapping

| Workflow | Model | Status Field | Enum | Values |
|----------|-------|--------------|------|--------|
| WF3 | Domain | status | DomainStatusEnum | pending, processing, completed, error |
| WF2 | Place | deep_scan_status | GcpApiDeepScanStatusEnum | Queued, Processing, Completed, Error |
| WF3 | LocalBusiness | domain_extraction_status | DomainExtractionStatusEnum | Queued, Processing, Submitted, Failed |
| WF4 | Domain | sitemap_analysis_status | SitemapAnalysisStatusEnum | pending, queued, processing, submitted, failed |
| WF5/WF6 | SitemapFile | sitemap_import_status | SitemapImportProcessStatusEnum | Queued, Processing, Complete, Error |
| WF7 | Page | page_processing_status | PageProcessingStatus | Queued, Processing, Complete, Error, Filtered |

## Critical Issues Summary

| Issue | Severity | File | Impact |
|-------|----------|------|--------|
| Multi-workflow single scheduler | HIGH | sitemap_scheduler.py | Single point of failure for WF2/WF3/WF5 |
| Duplicate scheduler versions | HIGH | domain_sitemap_submission_scheduler*.py | Code duplication, maintenance burden |
| Hardcoded system user ID | MEDIUM | sitemap_scheduler.py | Auditability, configurability |
| Missing zombie cleanup | MEDIUM | scheduler_loop.py | Stuck Processing records possible |
| Partial configuration | LOW | domain_sitemap_submission_scheduler.py | Inconsistent with other schedulers |
| Missing WF4 dedicated service | MEDIUM | routers/domains.py | Architectural deviation |

## Environment Variables

```bash
# Domain Processing
DOMAIN_SCHEDULER_INTERVAL_MINUTES=1
DOMAIN_SCHEDULER_BATCH_SIZE=50
DOMAIN_SCHEDULER_MAX_INSTANCES=3

# Sitemap Processing (Multi)
SITEMAP_SCHEDULER_INTERVAL_MINUTES=1
SITEMAP_SCHEDULER_BATCH_SIZE=25
SITEMAP_SCHEDULER_MAX_INSTANCES=3

# Domain Sitemap (WF4)
DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE=10
# Note: interval & max_instances hardcoded to 1

# Sitemap Import (WF6)
SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES=1
SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE=20
SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES=1

# Page Curation (WF7)
PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES=1
PAGE_CURATION_SCHEDULER_BATCH_SIZE=10
PAGE_CURATION_SCHEDULER_MAX_INSTANCES=1
```

## Race Condition Protection

```python
# Row-level locking prevents duplicate processing
.with_for_update(skip_locked=True)

# APScheduler overlap protection
max_instances=N          # Limit concurrent executions
coalesce=True           # Skip missed runs if backlog
misfire_grace_time=60   # 1-minute grace period
```

## Processing Patterns

### Pattern A: Domain Scheduler (3-Phase)
1. **Phase 1:** Fetch & mark processing (quick, seconds)
2. **Phase 2:** Slow operations without DB (releases connection)
3. **Phase 3:** Update results (quick, seconds)
**Benefit:** Prevents database connection hold during slow operations

### Pattern B: Sitemap Scheduler (Multi-Sub)
1. Process Deep Scans (Place records)
2. Process Domain Extractions (LocalBusiness → Domain)
3. Process Legacy Sitemaps (DISABLED)
**Issue:** Complex, interdependent, hard to maintain

### Pattern C: SDK Job Loop (Modern)
1. **Phase 1:** Atomic fetch & mark
2. **Phase 2:** Individual processing with separate sessions
3. **Auto-error handling:** Error sessions for failed items
**Benefit:** Generic, reusable, modern pattern

## Files to Know

| File | Purpose | Criticality |
|------|---------|------------|
| `src/scheduler_instance.py` | Core scheduler engine | NUCLEAR |
| `src/services/domain_scheduler.py` | WF3 domain processing | CRITICAL |
| `src/services/sitemap_scheduler.py` | WF2/WF3/WF5 multi-processor | CRITICAL (HIGH RISK) |
| `src/services/domain_sitemap_submission_scheduler.py` | WF4 queue processor | CRITICAL |
| `src/services/sitemap_import_scheduler.py` | WF6 URL extraction | CRITICAL |
| `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py` | WF7 page processing | CRITICAL |
| `src/common/curation_sdk/scheduler_loop.py` | Reusable job loop | SUPPORT |
| `src/main.py` | Scheduler registration | CRITICAL |

## Recommended Actions (Priority Order)

### Immediate (Do First)
1. Delete duplicate `domain_sitemap_submission_scheduler_fixed.py`
2. Document chosen session management pattern
3. Add monitoring for stuck Processing items
4. Move hardcoded system user ID to settings

### Short-term (Next Sprint)
1. Split `sitemap_scheduler.py` into 3 separate schedulers
2. Create `domain_curation_service.py` for WF4
3. Standardize configuration across all schedulers
4. Implement zombie record cleanup job

### Long-term (Architecture)
1. Add scheduler observability/metrics
2. Implement dead-letter queue pattern
3. Create formal workflow documentation
4. Add architecture decision records (ADRs)

---

**Document:** Full analysis available at `Docs/Scheduler_Architecture_Complete_Analysis_20251107.md`
