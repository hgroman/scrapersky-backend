"""
CORRECTED Domain Sitemap Submission Scheduler Service

This module fixes the critical disconnection where Tab 4 (Domain Curation) was
calling email scraping instead of sitemap analysis.

ORIGINAL BROKEN FLOW (June 28, 2025):
Tab 4 → domain_sitemap_submission_scheduler.py → WebsiteScanService → scan_website_for_emails() → EMAIL SCRAPING

FIXED CORRECT FLOW:
Tab 4 → domain_sitemap_submission_scheduler.py → SitemapAnalyzer → analyze_domain_sitemaps() → SITEMAP DISCOVERY
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
from src.scraper.sitemap_analyzer import SitemapAnalyzer
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

    sitemap_analyzer = SitemapAnalyzer()
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
        logger.error(f"❌ Error fetching domains for sitemap analysis: {fetch_error}", exc_info=True)
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
                    setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.processing)
                    await session_inner.flush()
                    logger.info(f"🔄 Processing sitemap analysis for domain {domain_id}")

                    # PERFORM REAL SITEMAP ANALYSIS (NOT EMAIL SCRAPING!)
                    domains_processed += 1
                    domain_url = getattr(locked_domain, 'domain', None)

                    if not domain_url:
                        logger.error(f"❌ Domain {domain_id} has no URL")
                        setattr(locked_domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.failed)
                        setattr(locked_domain, 'sitemap_analysis_error', "No domain URL available")
                        domains_failed += 1
                        continue

                    try:
                        # THIS IS THE CORRECT CODE: Use SitemapAnalyzer for sitemap discovery
                        logger.info(f"🔍 Analyzing sitemaps for: {domain_url}")
                        sitemap_results = await sitemap_analyzer.analyze_domain_sitemaps(str(domain_url))

                        if sitemap_results and not sitemap_results.get('error'):
                            # Successfully found sitemaps!
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
    logger.info(f"   ⏱️  Duration: {batch_duration:.2f}s")


def setup_corrected_sitemap_scheduler():
    """Setup the CORRECTED domain sitemap analysis scheduler."""
    try:
        job_id = "process_pending_domain_sitemap_submissions"
        interval_minutes = 1  # Check every minute

        logger.info(f"🔧 Setting up CORRECTED sitemap scheduler (runs every {interval_minutes} minute)")

        # Remove broken job if exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"🗑️  Removed old broken job '{job_id}'")

        # Add corrected job
        scheduler.add_job(
            process_pending_domain_sitemap_submissions,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            name="CORRECTED Domain Sitemap Analysis",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60,
        )

        logger.info(f"✅ Added CORRECTED job '{job_id}' - now uses SitemapAnalyzer instead of email scraping!")

    except Exception as e:
        logger.error(f"💥 Error setting up corrected sitemap scheduler: {e}", exc_info=True)
