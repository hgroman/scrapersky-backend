"""
🚨 CRITICAL WF4 COMPONENT - Domain to Sitemap Adapter
=====================================================
⚠️  SERVES: WF4 Domain Curation (Heart of the workflow)
⚠️  DELETION BREAKS: Complete WF4 → WF5 pipeline
⚠️  GUARDIAN DOC: WF4_Domain_Curation_Guardian_v3.md
⚠️  MODIFICATION REQUIRES: WF4 architecture understanding

🔒 DISASTER HISTORY: DELETED June 28, 2025 by "rogue agent" - RESTORED July 28, 2025
🔒 PROTECTION LEVEL: CRITICAL - Already caused complete pipeline failure once
🔒 BUSINESS LOGIC: Submits domain.domain to /api/v3/sitemap/scan endpoint
🔒 STATUS UPDATES: Sets sitemap_analysis_status from 'queued' to 'submitted'/'failed'

NEVER DELETE: This service was deleted once, breaking entire WF4. Restoration
required emergency 4+ hour debugging session. File is CRITICAL to domain curation.

Service to adapt the Domain Curation workflow to the legacy Sitemap Job system.

Fetches domains marked for sitemap analysis and submits them via HTTP POST
to the existing internal /api/v3/sitemap/scan endpoint.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Project specifics
from src.models.wf4_domain import Domain, SitemapAnalysisStatusEnum
from src.services.job_service import job_service

logger = logging.getLogger(__name__)


class DomainToSitemapAdapterService:
    """
    Service to bridge the Domain Curation status with the legacy Sitemap Job system.
    It fetches domains queued for sitemap analysis and submits them to the
    POST /api/v3/sitemap/scan endpoint.
    """

    async def submit_domain_to_legacy_sitemap(
        self, domain_id: UUID, session: AsyncSession
    ) -> bool:
        """
        Fetches a Domain, calls the legacy POST /api/v3/sitemap/scan endpoint,
        and updates the domain's sitemap_analysis_status IN MEMORY based on the outcome.
        The caller is responsible for committing the session.

        Args:
            domain_id: The UUID of the Domain record.
            session: The SQLAlchemy AsyncSession (transaction managed by caller).

        Returns:
            True if the domain submission API call was accepted (HTTP 202),
            False otherwise (domain not found, validation error, API call failed).
        """
        logger.info(
            f"Adapter Service: Processing domain {domain_id} for sitemap submission."
        )
        domain: Optional[Domain] = None
        try:
            # 1. Fetch the Domain record
            stmt = select(Domain).where(Domain.id == domain_id)
            result = await session.execute(stmt)
            domain = result.scalar_one_or_none()

            if not domain:
                logger.error(f"Adapter Service: Domain not found for id: {domain_id}")
                return False

            if not domain.domain:  # type: ignore
                logger.error(
                    f"Adapter Service: Domain record {domain_id} has no domain name."
                )
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.failed  # type: ignore
                domain.sitemap_analysis_error = (
                    "Domain record is missing the domain name."  # type: ignore
                )
                return False

            # 2. Create sitemap job directly using job_service (no HTTP call needed)
            job_id = str(uuid.uuid4())
            
            logger.info(
                f"Adapter Service: Creating sitemap job for domain {domain.domain} ({domain_id}), job_id: {job_id}"
            )
            
            # 3. Call job_service directly (same pattern as deep_scan_scheduler)
            job_data = {
                "job_id": job_id,
                "job_type": "sitemap",
                "status": "pending",
                "created_by": None,  # System-initiated job
                "result_data": {
                    "domain": domain.domain,
                    "max_pages": 1000,  # Default max pages
                },
            }
            
            job = await job_service.create(session, job_data)
            
            # 4. Initialize job in memory (required for background processing)
            from src.services.sitemap.processing_service import _job_statuses
            
            _job_statuses[job_id] = {
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "domain": domain.domain,
                "progress": 0.0,
                "metadata": {"sitemaps": []},
            }
            
            # 5. Trigger background processing (this is what the HTTP endpoint does)
            import asyncio
            from src.services.sitemap.processing_service import process_domain_with_own_session
            
            # Start background task without waiting for it
            asyncio.create_task(
                process_domain_with_own_session(
                    job_id=job_id,
                    domain=domain.domain,
                    user_id=None,  # System-initiated
                    max_urls=1000,
                )
            )
            
            # 6. Check result and update status IN MEMORY
            if job:
                logger.info(
                    f"Adapter Service: Successfully created and started sitemap job for domain {domain.domain} ({domain_id}), job_id: {job_id}"
                )
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.submitted  # type: ignore
                domain.sitemap_analysis_error = None  # type: ignore
                return True
            else:
                logger.error(
                    f"Adapter Service: Failed to create sitemap job for domain {domain.domain} ({domain_id})"
                )
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.failed  # type: ignore
                domain.sitemap_analysis_error = "Failed to create sitemap job"  # type: ignore
                return False
            return False
        except Exception as e:
            logger.error(
                f"Adapter Service: Unexpected error processing domain {domain.domain if domain else domain_id}: {e}",
                exc_info=True,
            )
            if domain:
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.failed  # type: ignore
                domain.sitemap_analysis_error = (
                    f"Unexpected Adapter Error: {str(e)[:500]}"  # type: ignore
                )
            return False
