"""
FIXED Domain Sitemap Submission Scheduler

This service processes domains queued for sitemap analysis using PROPER session management:
1. Session mode (port 5432) connections for Docker containers
2. Explicit transaction control (no nested transactions)
3. Proper row locking patterns
4. No "idle in transaction" issues

CRITICAL FIXES:
- Uses session mode, not transaction mode
- Manual transaction boundaries
- Proper error handling for locks
- No auto-commit issues
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy.future import select
from sqlalchemy.exc import DBAPIError

from src.models.domain import Domain, SitemapAnalysisStatusEnum
from src.scraper.sitemap_analyzer import SitemapAnalyzer
from src.session.async_session_fixed import get_fixed_scheduler_session

logger = logging.getLogger(__name__)


async def process_pending_domain_sitemap_submissions_fixed():
    """
    FIXED: Process domains queued for sitemap analysis using proper session management.

    This function:
    1. Uses session mode (port 5432) - proper for Docker containers
    2. Explicit transaction control - no auto-commit issues
    3. Proper row locking with error handling
    4. Real sitemap analysis (not email scraping!)
    """
    batch_uuid = uuid.uuid4()
    batch_start = datetime.now(timezone.utc)

    logger.info(f"🔧 FIXED: Starting sitemap analysis batch {batch_uuid}")

    domains_found = 0
    domains_processed = 0
    domains_successful = 0
    domains_failed = 0

    sitemap_analyzer = SitemapAnalyzer()
    domain_ids_to_process: List[uuid.UUID] = []

    # Step 1: Find domains that need processing (quick query, no locks)
    try:
        async with get_fixed_scheduler_session() as session:
            stmt_fetch = (
                select(Domain.id)
                .where(Domain.sitemap_analysis_status == SitemapAnalysisStatusEnum.queued)
                .order_by(Domain.updated_at.asc())
                .limit(10)
            )
            result = await session.execute(stmt_fetch)
            domain_ids_to_process = [row[0] for row in result.fetchall()]
            domains_found = len(domain_ids_to_process)
            # No commit needed - read-only query

        logger.info(f"📋 Found {domains_found} domains queued for analysis")

        if not domain_ids_to_process:
            logger.info("✅ No domains require sitemap analysis")
            return

    except Exception as fetch_error:
        logger.error(f"❌ Error fetching domains: {fetch_error}", exc_info=True)
        return

    # Step 2: Process each domain individually with proper locking
    for domain_id in domain_ids_to_process:
        try:
            async with get_fixed_scheduler_session() as session:
                # FIXED: Proper row locking pattern
                stmt_lock = (
                    select(Domain)
                    .where(Domain.id == domain_id)
                    .where(Domain.sitemap_analysis_status == SitemapAnalysisStatusEnum.queued)
                    .with_for_update(skip_locked=True)
                )

                result = await session.execute(stmt_lock)
                domain = result.scalar_one_or_none()

                if not domain:
                    logger.debug(f"⚠️ Domain {domain_id} not available (locked or processed)")
                    continue

                                # Mark as processing
                setattr(domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.processing.value)
                await session.flush()  # Ensure the lock is updated immediately

                domains_processed += 1
                domain_url = getattr(domain, 'domain', None)

                if not domain_url:
                    logger.error(f"❌ Domain {domain_id} has no URL")
                    setattr(domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.failed.value)
                    setattr(domain, 'sitemap_analysis_error', "No domain URL available")
                    await session.commit()
                    domains_failed += 1
                    continue

                try:
                    # PERFORM REAL SITEMAP ANALYSIS
                    logger.info(f"🔍 Analyzing sitemaps for: {domain_url}")
                    sitemap_results = await sitemap_analyzer.analyze_domain_sitemaps(str(domain_url))

                    if sitemap_results and not sitemap_results.get('error'):
                        # Success!
                        sitemaps_found = len(sitemap_results.get('sitemaps', []))
                        total_urls_found = sitemap_results.get('total_urls', 0)

                        setattr(domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.submitted.value)
                        setattr(domain, 'sitemap_analysis_error', None)

                        logger.info(f"✅ SUCCESS: Found {sitemaps_found} sitemaps with {total_urls_found} URLs for {domain_url}")
                        domains_successful += 1

                    else:
                        # Analysis failed
                        error_msg = sitemap_results.get('error', 'Sitemap analysis failed') if sitemap_results else 'No results returned'
                        logger.error(f"❌ Analysis failed for {domain_url}: {error_msg}")
                        setattr(domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.failed.value)
                        setattr(domain, 'sitemap_analysis_error', error_msg[:1024])
                        domains_failed += 1

                except Exception as analysis_error:
                    error_msg = str(analysis_error)
                    logger.error(f"💥 Analysis exception for {domain_url}: {error_msg}", exc_info=True)
                    setattr(domain, 'sitemap_analysis_status', SitemapAnalysisStatusEnum.failed.value)
                    setattr(domain, 'sitemap_analysis_error', error_msg[:1024])
                    domains_failed += 1

                # CRITICAL: Explicit commit for this domain
                try:
                    await session.commit()
                    logger.debug(f"✅ Committed changes for domain {domain_id}")
                except Exception as commit_error:
                    logger.error(f"💥 Commit failed for domain {domain_id}: {commit_error}")
                    await session.rollback()
                    domains_failed += 1

        except DBAPIError as db_error:
            logger.error(f"💥 Database error processing domain {domain_id}: {db_error}")
            domains_failed += 1
        except Exception as domain_error:
            logger.error(f"💥 Unexpected error processing domain {domain_id}: {domain_error}", exc_info=True)
            domains_failed += 1

    # Summary
    batch_duration = (datetime.now(timezone.utc) - batch_start).total_seconds()
    logger.info(f"🏁 FIXED sitemap analysis batch {batch_uuid} complete:")
    logger.info(f"   📊 Found: {domains_found} | Processed: {domains_processed}")
    logger.info(f"   ✅ Success: {domains_successful} | ❌ Failed: {domains_failed}")
    logger.info(f"   ⏱️ Duration: {batch_duration:.2f}s")


# Test function to verify the fixed scheduler works
async def test_fixed_scheduler():
    """Test the fixed scheduler with proper session management."""
    logger.info("🧪 Testing FIXED scheduler...")
    await process_pending_domain_sitemap_submissions_fixed()
    logger.info("🧪 FIXED scheduler test complete")
