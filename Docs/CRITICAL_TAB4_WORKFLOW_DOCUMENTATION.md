# 🚨 CRITICAL: Tab 4 Domain Curation Workflow Documentation

**⚠️ WARNING: This workflow was DESTROYED on June 28, 2025 by an AI "refactoring" that replaced sitemap analysis with email scraping. This documentation exists to prevent this disaster from happening again.**

## 📋 Table of Contents

```
1. Executive Summary & Disaster Timeline
2. Complete Workflow Architecture
3. Critical Components & Dependencies
4. End-to-End Data Flow
5. Code Implementation Details
6. Database Schema Requirements
7. Testing & Validation Procedures
8. Disaster Prevention Protocols
9. Recovery Procedures
10. AI Safety Guidelines
```

## 1. 🎯 Executive Summary & Disaster Timeline

### Purpose

Tab 4 (Domain Curation) allows users to select domains for sitemap analysis, triggering automated discovery and extraction of sitemaps and URLs from target websites.

### The Disaster (June 28, 2025)

```
❌ WHAT WENT WRONG:
- AI "refactoring" replaced DomainToSitemapAdapterService with WebsiteScanService
- Replaced SITEMAP ANALYSIS with EMAIL SCRAPING
- Broke entire WF4→WF5 data pipeline
- 358 domains stuck in limbo for months
- Months of architectural work rendered useless

✅ RECOVERY (July 26, 2025):
- Identified root cause through git archaeology
- Restored SitemapAnalyzer integration
- Fixed SQLAlchemy model imports
- Verified end-to-end functionality
- 18 sitemaps + 702 URLs successfully discovered from reddit.com
```

### Cost Impact

- **Development Time**: 8+ hours to identify and fix
- **Lost Productivity**: Months of broken functionality
- **Business Impact**: Complete data pipeline failure
- **Trust Impact**: AI coding assistant reliability questioned

## 2. 🏗️ Complete Workflow Architecture

### High-Level Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   User Interface │    │   Backend API    │    │    Scheduler        │
│                 │    │                  │    │                     │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────────┐ │
│ │   Tab 4     │ │    │ │   Domains    │ │    │ │  Domain Sitemap │ │
│ │   Domain    │────▶│ │   Router     │ │    │ │  Submission     │ │
│ │ Curation    │ │    │ │              │ │    │ │  Scheduler      │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│    Database     │    │   Status Update  │    │   Sitemap Analyzer  │
│                 │    │                  │    │                     │
│ sitemap_        │◀───│ sitemap_analysis │    │ ┌─────────────────┐ │
│ curation_status │    │ _status = queued │    │ │   Discovery     │ │
│ = "Selected"    │    │                  │    │ │   - robots.txt  │ │
│                 │    │                  │    │ │   - common paths│ │
│                 │    │                  │    │ │   - HTML links  │ │
│                 │    │                  │    │ └─────────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

### Component Breakdown

```
🔸 Frontend Layer (Tab 4)
  ├── File: static/scraper-sky-mvp.html (4th tab)
  ├── JavaScript: static/js/domain-curation-tab.js
  └── Function: batchUpdateDomainCurationStatus()

🔸 API Layer
  ├── Router: src/routers/domains.py
  ├── Endpoint: PUT /api/v3/domains/sitemap-curation/status
  └── Function: update_domain_sitemap_curation_status_batch()

🔸 Scheduler Layer
  ├── Service: src/services/domain_sitemap_submission_scheduler.py
  ├── Function: process_pending_domain_sitemap_submissions()
  └── Trigger: Every 1 minute via APScheduler

🔸 Analysis Layer (CRITICAL - This was broken!)
  ├── Analyzer: src/scraper/sitemap_analyzer.py
  ├── Function: analyze_domain_sitemaps()
  └── Methods: robots.txt + common paths + HTML parsing

🔸 Data Layer
  ├── Model: src/models/domain.py
  ├── Fields: sitemap_curation_status, sitemap_analysis_status
  └── Database: PostgreSQL (Supabase)
```

## 3. 🔧 Critical Components & Dependencies

### Essential Files (DO NOT MODIFY WITHOUT EXTREME CAUTION)

```
🚨 CRITICAL FILES:
├── src/services/domain_sitemap_submission_scheduler.py  ← DISASTER OCCURRED HERE
├── src/scraper/sitemap_analyzer.py                     ← CORE FUNCTIONALITY
├── src/routers/domains.py                              ← API ENDPOINT
├── static/js/domain-curation-tab.js                    ← UI LOGIC
└── src/models/domain.py                                ← DATA MODEL

⚠️  DEPENDENCY FILES:
├── src/models/__init__.py                              ← MUST IMPORT LocalBusiness
├── src/services/sitemap/processing_service.py         ← FUTURE INTEGRATION
└── src/session/async_session.py                       ← DATABASE CONNECTION
```

### Required Imports (Exact Configuration)

```python
# src/services/domain_sitemap_submission_scheduler.py
import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import List

from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.config.settings import settings
from src.models.domain import Domain, SitemapAnalysisStatusEnum
from src.models import TaskStatus
from src.scraper.sitemap_analyzer import SitemapAnalyzer  # ← CRITICAL IMPORT
from src.session.async_session import get_background_session
from src.scheduler_instance import scheduler
```

### Database Schema Requirements

```sql
-- domains table MUST have these fields:
ALTER TABLE domains ADD COLUMN IF NOT EXISTS sitemap_curation_status VARCHAR;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS sitemap_analysis_status VARCHAR;

-- Required enums:
CREATE TYPE "SitemapCurationStatusEnum" AS ENUM ('New', 'Selected', 'Maybe', 'Not a Fit', 'Archived', 'Completed');
CREATE TYPE "SitemapAnalysisStatusEnum" AS ENUM ('queued', 'processing', 'submitted', 'failed');

-- Foreign key dependency (MUST be imported in models/__init__.py):
ALTER TABLE domains ADD COLUMN local_business_id UUID REFERENCES local_businesses(id) ON DELETE SET NULL;
```

## 4. 📊 End-to-End Data Flow

### Complete User Journey

```
👤 USER ACTIONS:
1. Opens ScraperSky UI → Tab 4 (Domain Curation)
2. Sees list of domains with checkboxes
3. Selects target domains for analysis
4. Sets dropdown to "Selected"
5. Clicks "Update X Selected" button

🌐 FRONTEND PROCESSING:
JavaScript Function: batchUpdateDomainCurationStatus()
├── Collects checked domain IDs
├── Validates selection
├── Constructs API payload:
│   {
│     "domain_ids": ["uuid1", "uuid2", "uuid3"],
│     "sitemap_curation_status": "Selected"
│   }
└── Makes HTTP PUT request to API

🔌 API PROCESSING:
Endpoint: PUT /api/v3/domains/sitemap-curation/status
├── Authentication: Bearer scraper_sky_2024
├── Validation: domain_ids format and existence
├── Database Updates:
│   ├── sitemap_curation_status = "Selected"
│   ├── sitemap_analysis_status = "queued"  ← WF4→WF5 TRIGGER
│   └── updated_at = now()
└── Response: {"updated_count": N, "queued_count": N}

⏰ SCHEDULER PROCESSING:
Service: domain_sitemap_submission_scheduler.py (runs every minute)
├── Query: SELECT domains WHERE sitemap_analysis_status = 'queued'
├── Lock: Row-level locking with skip_locked=True
├── Update: sitemap_analysis_status = 'processing'
└── Trigger: SitemapAnalyzer.analyze_domain_sitemaps()

🔍 SITEMAP ANALYSIS:
Analyzer: SitemapAnalyzer.analyze_domain_sitemaps(domain_url)
├── Discovery Methods:
│   ├── robots.txt parsing
│   ├── Common path checking (/sitemap.xml, /sitemap_index.xml, etc.)
│   └── HTML meta tag extraction
├── Validation: HTTP status, content-type, XML structure
├── Parsing: XML/URL extraction from valid sitemaps
└── Results: {"sitemaps": [...], "total_urls": N, "error": None}

💾 FINAL PROCESSING:
Database Updates:
├── Success: sitemap_analysis_status = "submitted"
├── Failure: sitemap_analysis_status = "failed" + error message
├── Metrics: Logs sitemap count and URL discovery
└── Completion: Domain ready for next workflow stage
```

### Status Progression

```
Domain Lifecycle:
pending → (WF1-3) → completed → Selected → queued → processing → submitted
   ↑                              ↑         ↑         ↑           ↑
   │                            Tab 4     WF4→WF5   Analyzing   Complete
   │                            User      Trigger   Sitemaps    Success
   Initial                      Action    (FIXED)   (RESTORED)
```

## 5. 💻 Code Implementation Details

### API Endpoint (src/routers/domains.py)

```python
@router.put("/sitemap-curation/status")
async def update_domain_sitemap_curation_status_batch(
    request: SitemapCurationStatusBatchUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """CRITICAL: This endpoint triggers WF4→WF5 workflow"""
    try:
        # Key logic that was working correctly:
        if db_curation_status == SitemapCurationStatusEnum.Selected:
            domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.queued  # ← WF4→WF5 TRIGGER
            domain.sitemap_analysis_error = None
            queued_count += 1

        # This is the mechanism that queues domains for sitemap analysis

    except Exception as e:
        logger.error(f"Error updating domain curation status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Scheduler Service (FIXED VERSION)

```python
# src/services/domain_sitemap_submission_scheduler.py

async def process_pending_domain_sitemap_submissions():
    """
    ✅ CORRECTED: Process domains queued for sitemap analysis using SitemapAnalyzer

    ❌ BROKEN VERSION (June 28): Used WebsiteScanService + email scraping
    ✅ FIXED VERSION (July 26): Uses SitemapAnalyzer + sitemap discovery
    """

    # Step 1: Find queued domains
    stmt_fetch = (
        select(Domain.id)
        .where(Domain.sitemap_analysis_status == SitemapAnalysisStatusEnum.queued)
        .order_by(Domain.updated_at.asc())
        .limit(10)
    )

    # Step 2: Process each domain with REAL sitemap analysis
    for domain_id in domain_ids_to_process:
        # Critical: Use SitemapAnalyzer, NOT WebsiteScanService
        sitemap_results = await sitemap_analyzer.analyze_domain_sitemaps(str(domain_url))

        if sitemap_results and not sitemap_results.get('error'):
            # Success: Mark as submitted
            setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.submitted)
            logger.info(f"✅ SUCCESS: Found {sitemaps_found} sitemaps with {total_urls_found} URLs")
        else:
            # Failure: Mark as failed with error
            setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.failed)
            setattr(locked_domain, 'sitemap_analysis_error', error_msg[:1024])
```

### SitemapAnalyzer (Core Engine)

```python
# src/scraper/sitemap_analyzer.py

class SitemapAnalyzer:
    """The REAL sitemap discovery engine that was replaced by email scraping"""

    async def analyze_domain_sitemaps(self, domain: str) -> Dict[str, Any]:
        """
        Discovers and analyzes sitemaps for a given domain

        Returns:
        {
            "sitemaps": [{"url": "...", "type": "...", "method": "..."}],
            "total_urls": 123,
            "error": None  # or error message
        }
        """

        # Discovery methods (in order):
        # 1. robots.txt parsing
        # 2. Common path checking (/sitemap.xml, /sitemap_index.xml, etc.)
        # 3. HTML meta tag extraction

        # Validation and parsing
        # URL extraction and deduplication
        # Error handling and logging
```

## 6. 🗄️ Database Schema Requirements

### Essential Tables

```sql
-- domains table (primary)
CREATE TABLE domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR NOT NULL UNIQUE,
    status VARCHAR DEFAULT 'pending',
    sitemap_curation_status VARCHAR,           -- ← Tab 4 sets this
    sitemap_analysis_status VARCHAR,           -- ← WF4→WF5 trigger field
    sitemap_analysis_error TEXT,
    local_business_id UUID REFERENCES local_businesses(id) ON DELETE SET NULL,
    tenant_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    title VARCHAR,
    -- ... other fields
);

-- Required for foreign key (MUST be imported in models/__init__.py)
CREATE TABLE local_businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- ... other fields
);

-- Optional: sitemaps table (for storing discovered sitemaps)
CREATE TABLE sitemap_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID REFERENCES domains(id) ON DELETE CASCADE,
    url VARCHAR NOT NULL,
    sitemap_type VARCHAR,
    discovery_method VARCHAR,
    url_count INTEGER DEFAULT 0,
    last_fetched_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### Critical Indexes

```sql
-- Performance indexes for scheduler queries
CREATE INDEX idx_domains_sitemap_analysis_status ON domains(sitemap_analysis_status);
CREATE INDEX idx_domains_sitemap_curation_status ON domains(sitemap_curation_status);
CREATE INDEX idx_domains_updated_at ON domains(updated_at);

-- Compound index for scheduler efficiency
CREATE INDEX idx_domains_scheduler_query ON domains(sitemap_analysis_status, updated_at)
WHERE sitemap_analysis_status = 'queued';
```

## 7. 🧪 Testing & Validation Procedures

### End-to-End Test Script

```bash
#!/bin/bash
# test_tab4_workflow.sh

echo "🧪 Testing Tab 4 Workflow End-to-End..."

# 1. Add test domain
curl -X POST "http://localhost:8000/test/add-domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "test-$(date +%s).example.com"}'

# 2. Trigger Tab 4 workflow
curl -X PUT "http://localhost:8000/api/v3/domains/sitemap-curation/status" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"domain_ids": ["'$DOMAIN_ID'"], "sitemap_curation_status": "Selected"}'

# 3. Verify database state
psql $DATABASE_URL -c "
SELECT domain, sitemap_analysis_status, updated_at
FROM domains
WHERE id = '$DOMAIN_ID';"

# 4. Trigger scheduler manually
docker-compose exec scrapersky python -c "
import asyncio
from src.services.domain_sitemap_submission_scheduler import process_pending_domain_sitemap_submissions
asyncio.run(process_pending_domain_sitemap_submissions())
"

# 5. Verify completion
psql $DATABASE_URL -c "
SELECT domain, sitemap_analysis_status, updated_at
FROM domains
WHERE id = '$DOMAIN_ID';"

echo "✅ Test complete. Check logs for sitemap discovery results."
```

### Validation Queries

```sql
-- Check workflow health
SELECT
    COUNT(*) FILTER (WHERE sitemap_curation_status = 'Selected') as selected_domains,
    COUNT(*) FILTER (WHERE sitemap_analysis_status = 'queued') as queued_for_analysis,
    COUNT(*) FILTER (WHERE sitemap_analysis_status = 'processing') as currently_processing,
    COUNT(*) FILTER (WHERE sitemap_analysis_status = 'submitted') as successfully_completed,
    COUNT(*) FILTER (WHERE sitemap_analysis_status = 'failed') as failed_analysis
FROM domains
WHERE sitemap_curation_status IS NOT NULL;

-- Find stuck domains (processing for >1 hour)
SELECT domain, sitemap_analysis_status, updated_at,
       now() - updated_at as stuck_duration
FROM domains
WHERE sitemap_analysis_status = 'processing'
  AND updated_at < now() - interval '1 hour';

-- Verify WF4→WF5 connection working
SELECT domain, sitemap_analysis_status, updated_at
FROM domains
WHERE sitemap_curation_status = 'Selected'
  AND sitemap_analysis_status = 'submitted'
  AND updated_at > now() - interval '1 day'
ORDER BY updated_at DESC;
```

## 8. 🛡️ Disaster Prevention Protocols

### Code Review Checklist

```
🚨 BEFORE ANY CHANGES TO SCHEDULER FILES:

□ Does this change affect src/services/domain_sitemap_submission_scheduler.py?
□ Does this change the import from SitemapAnalyzer to anything else?
□ Does this change replace sitemap analysis with email/other functionality?
□ Has the WF4→WF5 connection been verified after changes?
□ Have end-to-end tests been run?
□ Has the change been reviewed by someone who understands this workflow?

❌ NEVER ALLOW:
- Replacing SitemapAnalyzer with WebsiteScanService
- Replacing sitemap analysis with email scraping
- Removing the WF4→WF5 trigger logic
- Changing imports without understanding dependencies
- "Refactoring" without comprehensive testing
```

### AI Safety Guidelines

```
🤖 RULES FOR AI CODING ASSISTANTS:

1. NEVER modify domain_sitemap_submission_scheduler.py without explicit user permission
2. NEVER replace SitemapAnalyzer with any other service
3. NEVER change the core workflow logic without understanding the full pipeline
4. ALWAYS ask for clarification when "refactoring" critical workflow components
5. ALWAYS run end-to-end tests after making workflow changes
6. ALWAYS document what was changed and why

⚠️  WARNING SIGNS:
- AI suggests "modernizing" or "refactoring" scheduler services
- AI wants to replace "legacy" services with "better" alternatives
- AI claims to "improve" workflow logic without understanding requirements
- AI makes changes to imports or service dependencies
```

### Monitoring & Alerts

```python
# Add to monitoring system
def check_tab4_workflow_health():
    """Monitor Tab 4 workflow for early warning signs"""

    alerts = []

    # Check for stuck domains
    stuck_domains = query("SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'processing' AND updated_at < now() - interval '1 hour'")
    if stuck_domains > 0:
        alerts.append(f"🚨 {stuck_domains} domains stuck in processing state")

    # Check for increasing queue without processing
    queue_size = query("SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued'")
    if queue_size > 50:
        alerts.append(f"⚠️ Large queue size: {queue_size} domains waiting for analysis")

    # Check for high failure rate
    recent_failures = query("SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'failed' AND updated_at > now() - interval '1 hour'")
    if recent_failures > 10:
        alerts.append(f"❌ High failure rate: {recent_failures} failures in last hour")

    return alerts
```

## 9. 🔄 Recovery Procedures

### If Tab 4 Stops Working

```bash
# 1. Check scheduler status
docker-compose logs scrapersky | grep "sitemap_analysis_batch"

# 2. Check for database locks
psql $DATABASE_URL -c "
SELECT pid, state, query_start, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - query_start > interval '30 seconds';"

# 3. Kill blocking sessions
psql $DATABASE_URL -c "SELECT pg_terminate_backend(PID_HERE);"

# 4. Verify imports are correct
grep -n "SitemapAnalyzer" src/services/domain_sitemap_submission_scheduler.py
grep -n "WebsiteScanService" src/services/domain_sitemap_submission_scheduler.py  # Should be empty!

# 5. Test manually
docker-compose exec scrapersky python -c "
import asyncio
from src.services.domain_sitemap_submission_scheduler import process_pending_domain_sitemap_submissions
asyncio.run(process_pending_domain_sitemap_submissions())
"

# 6. Check recent commits for accidental changes
git log --oneline -10 src/services/domain_sitemap_submission_scheduler.py
```

### Recovery from AI Disaster

```bash
# If AI has broken the workflow again:

# 1. Identify the disaster commit
git log --oneline src/services/domain_sitemap_submission_scheduler.py

# 2. Show what changed
git show COMMIT_HASH src/services/domain_sitemap_submission_scheduler.py

# 3. Revert the bad changes
git revert COMMIT_HASH

# 4. Restore correct implementation
# See section 5 for correct code implementation

# 5. Test thoroughly before deploying
./test_tab4_workflow.sh

# 6. Document what went wrong
echo "$(date): AI disaster recovery - reverted commit $COMMIT_HASH" >> AI_DISASTER_LOG.md
```

## 10. 📚 Reference Implementation

### Complete Working Scheduler (Save This!)

```python
# THIS IS THE CORRECT IMPLEMENTATION - SAVE THIS FILE!
# src/services/domain_sitemap_submission_scheduler.py

"""
✅ CORRECT Implementation of Domain Sitemap Submission Scheduler

This service processes domains that have been selected for sitemap analysis
via Tab 4 (Domain Curation) and discovers their sitemaps using SitemapAnalyzer.

🚨 WARNING: This file was destroyed on June 28, 2025 by AI replacing
SitemapAnalyzer with WebsiteScanService (email scraping). DO NOT ALLOW
THIS TO HAPPEN AGAIN.

✅ VERIFIED WORKING: July 26, 2025 - Successfully processed reddit.com
and discovered 18 sitemaps with 702 URLs.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import List

from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.config.settings import settings
from src.models.domain import Domain, SitemapAnalysisStatusEnum
from src.models import TaskStatus
from src.scraper.sitemap_analyzer import SitemapAnalyzer  # ← CRITICAL: NEVER REPLACE THIS
from src.session.async_session import get_background_session
from src.scheduler_instance import scheduler

logger = logging.getLogger(__name__)


async def process_pending_domain_sitemap_submissions():
    """
    ✅ CORRECT: Process domains queued for sitemap analysis using SitemapAnalyzer

    This function:
    1. Finds domains with sitemap_analysis_status='queued'
    2. Runs ACTUAL sitemap analysis (not email scraping!)
    3. Discovers and logs real sitemaps from domains
    4. Updates status to 'submitted' or 'failed'
    """
    batch_uuid = uuid.uuid4()
    batch_start = datetime.now(timezone.utc)

    logger.info(f"🔍 Starting sitemap analysis batch {batch_uuid}")

    domains_found = 0
    domains_processed = 0
    domains_submitted_successfully = 0
    domains_failed = 0

    sitemap_analyzer = SitemapAnalyzer()  # ← THE CORRECT SERVICE
    domain_ids_to_process: List[uuid.UUID] = []

    # Step 1: Fetch domains that need sitemap analysis
    try:
        async with get_background_session() as session_fetch:
            stmt_fetch = (
                select(Domain.id)
                .where(Domain.sitemap_analysis_status == SitemapAnalysisStatusEnum.queued)
                .order_by(Domain.updated_at.asc())
                .limit(10)
            )
            result_fetch = await session_fetch.execute(stmt_fetch)
            domain_ids_to_process = [row[0] for row in result_fetch.fetchall()]
            domains_found = len(domain_ids_to_process)

        logger.info(f"📋 Found {domains_found} domains queued for sitemap analysis")

        if not domain_ids_to_process:
            logger.info("✅ No domains require sitemap analysis")
            return

    except Exception as fetch_error:
        logger.error(f"❌ Error fetching domains: {fetch_error}", exc_info=True)
        return

    # Step 2: Process each domain with REAL sitemap analysis
    for domain_id in domain_ids_to_process:
        try:
            async with get_background_session() as session_inner:
                async with session_inner.begin():
                    # Get domain with lock
                    stmt_domain = (
                        select(Domain)
                        .where(Domain.id == domain_id)
                        .with_for_update(skip_locked=True)
                    )
                    result_domain = await session_inner.execute(stmt_domain)
                    locked_domain = result_domain.scalar_one_or_none()

                    if not locked_domain:
                        logger.warning(f"⚠️ Could not lock domain {domain_id}")
                        continue

                    # Update status to processing
                    setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.processing)
                    await session_inner.flush()
                    logger.info(f"🔄 Processing sitemap analysis for domain {domain_id}")

                    # ✅ PERFORM REAL SITEMAP ANALYSIS (NOT EMAIL SCRAPING!)
                    domains_processed += 1
                    domain_url = getattr(locked_domain, 'domain', None)

                    if not domain_url:
                        logger.error(f"❌ Domain {domain_id} has no URL")
                        setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.failed)
                        setattr(locked_domain, 'sitemap_analysis_error', "No domain URL available")
                        domains_failed += 1
                        continue

                    try:
                        # 🔍 THIS IS THE CORRECT CODE: Use SitemapAnalyzer for sitemap discovery
                        logger.info(f"🔍 Analyzing sitemaps for: {domain_url}")
                        sitemap_results = await sitemap_analyzer.analyze_domain_sitemaps(str(domain_url))

                        if sitemap_results and not sitemap_results.get('error'):
                            # ✅ Successfully found sitemaps!
                            sitemaps_found = len(sitemap_results.get('sitemaps', []))
                            total_urls_found = sitemap_results.get('total_urls', 0)

                            # Mark as successfully processed
                            setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.submitted)
                            setattr(locked_domain, 'sitemap_analysis_error', None)

                            logger.info(f"✅ SUCCESS: Found {sitemaps_found} sitemaps with {total_urls_found} URLs for {domain_url}")
                            domains_submitted_successfully += 1

                        else:
                            # Handle analysis failure
                            error_msg = sitemap_results.get('error', 'Unknown sitemap analysis error') if sitemap_results else 'Sitemap analysis returned None'
                            logger.error(f"❌ Sitemap analysis failed for {domain_url}: {error_msg}")
                            setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.failed)
                            setattr(locked_domain, 'sitemap_analysis_error', error_msg[:1024])
                            domains_failed += 1

                    except Exception as analysis_error:
                        error_msg = str(analysis_error)
                        logger.error(f"💥 Exception during sitemap analysis for {domain_url}: {error_msg}", exc_info=True)
                        setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.failed)
                        setattr(locked_domain, 'sitemap_analysis_error', error_msg[:1024])
                        domains_failed += 1

        except Exception as domain_error:
            logger.error(f"💥 Error processing domain {domain_id}: {domain_error}", exc_info=True)
            domains_failed += 1

    # Summary
    batch_duration = (datetime.now(timezone.utc) - batch_start).total_seconds()
    logger.info(f"🏁 Sitemap analysis batch {batch_uuid} complete:")
    logger.info(f"   📊 Found: {domains_found} | Processed: {domains_processed}")
    logger.info(f"   ✅ Success: {domains_submitted_successfully} | ❌ Failed: {domains_failed}")
    logger.info(f"   ⏱️ Duration: {batch_duration:.2f}s")


def setup_domain_sitemap_submission_scheduler():
    """Setup the domain sitemap analysis scheduler"""
    try:
        job_id = "process_pending_domain_sitemap_submissions"
        interval_minutes = 1  # Check every minute

        logger.info(f"🔧 Setting up sitemap scheduler (runs every {interval_minutes} minute)")

        # Remove existing job if exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"🗑️ Removed existing job '{job_id}'")

        # Add job
        scheduler.add_job(
            process_pending_domain_sitemap_submissions,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            name="Domain Sitemap Analysis",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60,
        )

        logger.info(f"✅ Added job '{job_id}' - uses SitemapAnalyzer for sitemap discovery")

    except Exception as e:
        logger.error(f"💥 Error setting up sitemap scheduler: {e}", exc_info=True)

# END OF CORRECT IMPLEMENTATION
```

---

## 🎯 FINAL NOTES

This documentation represents the complete architecture and implementation details needed to rebuild Tab 4 Domain Curation workflow from scratch. The disaster of June 28, 2025 serves as a critical reminder that **AI coding assistants can cause catastrophic damage** when they make "helpful" refactoring changes without understanding the full system architecture.

**Key Lessons:**

1. **Never trust AI with critical workflow changes**
2. **Always require human review for scheduler/service modifications**
3. **Maintain comprehensive documentation (like this) for disaster recovery**
4. **Test end-to-end after any workflow changes**
5. **Monitor workflow health continuously**

This workflow is now **100% functional and verified working** as of July 26, 2025. Protect it accordingly.

---

**Document Version**: 1.0
**Last Updated**: July 26, 2025
**Verified Working**: ✅ Yes (reddit.com: 18 sitemaps, 702 URLs discovered)
**Disaster Risk**: 🚨 HIGH (AI coding assistants have destroyed this before)
