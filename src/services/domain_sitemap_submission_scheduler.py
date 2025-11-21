"""
🚨 CRITICAL WF4 COMPONENT - Domain Sitemap Submission Scheduler
==============================================================
⚠️  SERVES: WF4 Domain Curation (Background Processing)
⚠️  DELETION BREAKS: Domain → Sitemap analysis pipeline
⚠️  GUARDIAN DOC: WF4_Domain_Curation_Guardian_v3.md
⚠️  MODIFICATION REQUIRES: Understanding of WF4 adapter architecture

🔒 DISASTER HISTORY: Broken June 28, 2025 - Fixed to use DomainToSitemapAdapterService
🔒 PROTECTION LEVEL: CRITICAL - Core WF4 background processing
🔒 BUSINESS LOGIC: Polls domains with sitemap_analysis_status='queued'
🔒 CALLS: DomainToSitemapAdapterService.submit_domain_to_legacy_sitemap()

NEVER MODIFY: Part of emergency WF4 restoration. Uses proper adapter service
instead of broken email scraping that was incorrectly substituted.

CORRECTED Domain Sitemap Submission Scheduler Service

This module fixes the critical disconnection where Tab 4 (Domain Curation) was
calling email scraping instead of sitemap analysis.

ORIGINAL BROKEN FLOW (June 28, 2025):
Tab 4 → domain_sitemap_submission_scheduler.py → WebsiteScanService → scan_website_for_emails() → EMAIL SCRAPING

FIXED CORRECT FLOW:
Tab 4 → domain_sitemap_submission_scheduler.py → SitemapAnalyzer → analyze_domain_sitemaps() → SITEMAP DISCOVERY
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import List

from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.future import select

from src.config.settings import settings
from src.models.wf4_domain import Domain, SitemapAnalysisStatusEnum
from src.services.domain_to_sitemap_adapter_service import DomainToSitemapAdapterService
from src.session.async_session import get_background_session
from src.scheduler_instance import scheduler

logger = logging.getLogger(__name__)


async def process_pending_domain_sitemap_submissions():
    """
    CORRECTED: Process domains queued for sitemap analysis using the real SitemapAnalyzer.

    This function fixes the critical WF4→WF5 disconnection by:
    1. Finding domains with sitemap_analysis_status='queued'
    2. Running ACTUAL sitemap analysis (not email scraping!)
    3. Discovering and logging real sitemaps from domains
    """
    batch_uuid = uuid.uuid4()
    batch_start = datetime.now(timezone.utc)

    logger.info(f"🔍 Starting CORRECTED sitemap analysis batch {batch_uuid}")

    domains_found = 0
    domains_processed = 0
    domains_submitted_successfully = 0
    domains_failed = 0
    stale_threshold_minutes = 15

    adapter_service = DomainToSitemapAdapterService()
    domain_ids_to_process: List[uuid.UUID] = []

    # Step 1: Fetch domains that need sitemap analysis
    try:
        async with get_background_session() as session_fetch:
            stmt_fetch = (
                select(Domain.id)
                .where(
                    Domain.sitemap_analysis_status == SitemapAnalysisStatusEnum.queued
                )
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
        logger.error(
            f"❌ Error fetching domains for sitemap analysis: {fetch_error}",
            exc_info=True,
        )
        return

    # Step 2: Process each domain with real sitemap analysis
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
                        logger.warning(f"⚠️  Could not lock domain {domain_id}")
                        continue

                    # Update status to processing
                    setattr(
                        locked_domain,
                        "sitemap_analysis_status",
                        SitemapAnalysisStatusEnum.processing,
                    )
                    await session_inner.flush()
                    logger.info(
                        f"🔄 Processing sitemap analysis for domain {domain_id}"
                    )

                    # Call the adapter service to submit to proper sitemap processing
                    domains_processed += 1
                    submitted_ok = (
                        await adapter_service.submit_domain_to_legacy_sitemap(
                            domain_id=locked_domain.id,
                            session=session_inner,
                        )
                    )

                    # Check adapter result
                    current_status_after_adapter = getattr(
                        locked_domain, "sitemap_analysis_status", None
                    )
                    if current_status_after_adapter not in [
                        SitemapAnalysisStatusEnum.submitted,
                        SitemapAnalysisStatusEnum.failed,
                    ]:
                        logger.error(
                            f"Adapter failed to update status for domain {domain_id}! Current status: {locked_domain.sitemap_analysis_status}. Forcing 'failed'."
                        )
                        setattr(
                            locked_domain,
                            "sitemap_analysis_status",
                            SitemapAnalysisStatusEnum.failed,
                        )
                        setattr(
                            locked_domain,
                            "sitemap_analysis_error",
                            "Adapter did not set final status",
                        )
                        await session_inner.flush()
                        domains_failed += 1
                    elif submitted_ok:
                        domains_submitted_successfully += 1
                        logger.info(
                            f"Domain {domain_id} marked as '{current_status_after_adapter}' by adapter."
                        )
                    else:
                        domains_failed += 1
                        logger.warning(
                            f"Domain {domain_id} marked as '{current_status_after_adapter}' by adapter. Error: {getattr(locked_domain, 'sitemap_analysis_error', 'N/A')}"
                        )

        except Exception as domain_error:
            logger.error(
                f"💥 Error processing domain {domain_id}: {domain_error}", exc_info=True
            )
            domains_failed += 1

    # Summary
    batch_duration = (datetime.now(timezone.utc) - batch_start).total_seconds()
    logger.info(f"🏁 Sitemap analysis batch {batch_uuid} complete:")
    logger.info(f"   📊 Found: {domains_found} | Processed: {domains_processed}")
    logger.info(
        f"   ✅ Success: {domains_submitted_successfully} | ❌ Failed: {domains_failed}"
    )
    logger.info(f"   ⏱️  Duration: {batch_duration:.2f}s")


def setup_domain_sitemap_submission_scheduler():
    """Setup the domain sitemap submission scheduler using the restored adapter service."""
    try:
        job_id = "process_pending_domain_sitemap_submissions"
        interval_minutes = 1  # Check every minute

        logger.info(
            f"🔧 Setting up domain sitemap submission scheduler (runs every {interval_minutes} minute)"
        )

        # Remove existing job if exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"🗑️  Removed existing job '{job_id}'")

        # Add the job
        scheduler.add_job(
            process_pending_domain_sitemap_submissions,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            name="Domain Sitemap Submission Scheduler",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60,
        )

        logger.info(
            f"✅ Added job '{job_id}' - uses DomainToSitemapAdapterService for proper storage"
        )

    except Exception as e:
        logger.error(
            f"💥 Error setting up domain sitemap submission scheduler: {e}",
            exc_info=True,
        )
