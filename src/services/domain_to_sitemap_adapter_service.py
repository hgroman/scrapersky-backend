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
from typing import Optional
from uuid import UUID

import httpx  # Required for making HTTP requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.settings import settings  # Assuming settings holds API key/base URL

# Project specifics
from src.models.domain import Domain, SitemapAnalysisStatusEnum

# from src.db.session import get_session # Not needed directly if session passed in

logger = logging.getLogger(__name__)

# Define the base URL for the internal API call
# TODO: Consider moving this to settings or making it more robust (e.g., env var)
INTERNAL_API_BASE_URL = (
    "http://localhost:8000"  # Or appropriate service name in Docker network
)


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

            # 2. Prepare payload
            scan_payload = {
                "base_url": domain.domain,
                # Add other parameters like max_pages if needed/configurable
                # "max_pages": 1000
            }

            # 3. Make HTTP POST request
            api_key = settings.dev_token or "scraper_sky_2024"  # Fallback to dev token
            if not api_key:
                logger.error("Adapter Service: dev_token not found in settings.")
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.failed  # type: ignore
                domain.sitemap_analysis_error = (
                    "Configuration Error: dev_token missing."  # type: ignore
                )
                return False

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            scan_endpoint = f"{INTERNAL_API_BASE_URL}/api/v3/sitemap/scan"

            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Adapter Service: Calling {scan_endpoint} for domain {domain.domain} ({domain_id})"
                )
                response = await client.post(
                    scan_endpoint, json=scan_payload, headers=headers, timeout=30.0
                )

            # 4. Check response and update status IN MEMORY
            if response.status_code == 202:
                logger.info(
                    f"Adapter Service: Successfully submitted domain {domain.domain} ({domain_id}). Status code: {response.status_code}"
                )
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.submitted  # type: ignore
                domain.sitemap_analysis_error = None  # type: ignore
                return True
            else:
                error_detail = "Unknown error"
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                logger.error(
                    f"Adapter Service: Failed to submit domain {domain.domain} ({domain_id}). Status code: {response.status_code}. Response: {error_detail}"
                )
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.failed  # type: ignore
                domain.sitemap_analysis_error = f"API Call Failed. Status: {response.status_code}. Detail: {error_detail[:500]}"  # type: ignore
                return False

        except httpx.RequestError as http_err:
            logger.error(
                f"Adapter Service: HTTP request error submitting domain {domain.domain if domain else domain_id}: {http_err}",
                exc_info=True,
            )
            if domain:
                domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.failed  # type: ignore
                domain.sitemap_analysis_error = (
                    f"HTTP Request Error: {str(http_err)[:500]}"  # type: ignore
                )
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
