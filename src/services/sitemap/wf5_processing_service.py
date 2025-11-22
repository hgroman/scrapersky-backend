"""
Sitemap Processing Service

This module provides services for handling sitemap scanning, processing, and domain metadata extraction.
It leverages the SitemapAnalyzer class for the actual sitemap discovery and processing.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, HTTPException

# Import models directly to avoid circular imports
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...scraper.sitemap_analyzer import SitemapAnalyzer  # Import the SitemapAnalyzer
from ..core.validation_service import validation_service

# Configure logger
logger = logging.getLogger(__name__)

# REMOVED tenant ID constants as per architectural mandate
# JWT authentication happens ONLY at API gateway endpoints
# Database operations should NEVER handle JWT or tenant authentication

# In-memory job status tracking
_job_statuses: Dict[str, Dict[str, Any]] = {}


# Define simplified models for this service
class SitemapScrapingRequest(BaseModel):
    base_url: str
    max_pages: int = 1000
    # tenant_id removed from request model


class SitemapScrapingResponse(BaseModel):
    job_id: str
    status: str
    status_url: str


class JobStatusResponse(BaseModel):
    status: str
    job_id: str
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    domain: Optional[str] = None
    total_sitemaps: Optional[int] = None
    total_urls: Optional[int] = None
    progress: Optional[float] = None
    discovery_methods: Optional[Dict[str, int]] = None
    sitemap_types: Optional[Dict[str, int]] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class SitemapProcessingService:
    """
    Service for handling sitemap-related operations.

    This service processes domains, extracts metadata, and manages scan jobs.
    It leverages the SitemapAnalyzer class for the actual sitemap analysis.

    This service follows the transaction-aware pattern where it works with
    transactions but does not create, commit, or rollback transactions itself.
    Transaction boundaries are managed by the router.

    Background tasks are an exception to this rule, as they run asynchronously
    and must create their own sessions and manage their own transactions.
    """

    def __init__(self):
        """Initialize the service with a SitemapAnalyzer instance."""
        self.analyzer = SitemapAnalyzer()

    async def initiate_domain_scan(
        self,
        request: SitemapScrapingRequest,
        background_tasks: BackgroundTasks,
        session: AsyncSession,
        current_user: Optional[Dict[str, Any]] = None,
    ) -> SitemapScrapingResponse:
        """
        Initiate a scan for a domain.

        This method is transaction-aware and can be called from within an existing
        transaction or without a transaction. It will not start a new transaction.
        The caller (typically a router) is responsible for managing transaction boundaries.

        Args:
            request: The request containing domain scan parameters
            background_tasks: FastAPI background tasks handler
            session: Database session
            # tenant_id parameter removed
            current_user: Current authenticated user information

        Returns:
            Response with job ID and status URL

        Raises:
            ValueError: If request parameters are invalid
            HTTPException: If scan fails to initiate
        """
        # Check if the session is already in a transaction
        in_transaction = session.in_transaction()
        logger.debug(
            f"Session transaction state in initiate_domain_scan: {in_transaction}"
        )

        # Validate request parameters
        self._validate_scan_request(request)

        # Create new job_id with standard UUID format
        job_id = str(uuid.uuid4())
        logger.info(f"Generated job ID: {job_id}")

        # Start tracking job status in memory
        job_status = {
            "job_id": job_id,
            "status": "running",
            "domain": request.base_url,
            "started_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "progress": 0.0,
            "metadata": {"sitemaps": []},
        }

        # Store in memory tracking
        _job_statuses[job_id] = job_status

        # Create a job record in the database - convert job_id to UUID if it's a string
        job_id_obj = uuid.UUID(job_id) if isinstance(job_id, str) else job_id

        # Create job in database
        job_data = {
            "job_id": job_id_obj,
            "job_type": "sitemap_scan",
            "status": "running",
            "domain_id": None,
            "progress": 0.0,
            "job_metadata": {"domain": request.base_url},
        }

        try:
            # Add the processing task to background tasks using the compliant method
            # This uses process_domain_with_own_session which properly creates its own session
            background_tasks.add_task(
                process_domain_with_own_session,
                job_id=job_id,
                domain=request.base_url,
                user_id=current_user.get("user_id") if current_user else None,
                max_urls=request.max_pages,
            )

            # Return immediate response with job ID
            status_url = f"/api/v3/sitemap/status/{job_id}"
            return SitemapScrapingResponse(
                job_id=job_id, status="started", status_url=status_url
            )

        except Exception as e:
            logger.error(f"Failed to initiate scan: {str(e)}")
            # Update job status on error
            if job_id in _job_statuses:
                _job_statuses[job_id]["status"] = "failed"
                _job_statuses[job_id]["error"] = str(e)
                _job_statuses[job_id]["completed_at"] = datetime.utcnow().isoformat()

            raise HTTPException(
                status_code=500, detail=f"Failed to initiate scan: {str(e)}"
            )

    def _validate_scan_request(self, request: SitemapScrapingRequest) -> None:
        """
        Validate scan request parameters.

        Args:
            request: The request to validate

        Raises:
            ValueError: If any parameters are invalid
        """
        # Validate base_url
        try:
            validation_service.validate_string_length(
                request.base_url, field_name="base_url", min_length=2, max_length=255
            )
        except ValueError as e:
            raise ValueError(f"Invalid base URL: {str(e)}")

        # Validate max_pages using a simple check since validate_number_range doesn't exist
        if request.max_pages < 1:
            raise ValueError("max_pages must be at least 1")
        if request.max_pages > 10000:
            raise ValueError("max_pages cannot exceed 10000")

    def _update_job_failure(self, job_id: str, error_msg: str) -> None:
        """
        Update job status to failed with the given error message.

        Args:
            job_id: The job identifier
            error_msg: Error message to store
        """
        if job_id in _job_statuses:
            _job_statuses[job_id]["status"] = "failed"
            _job_statuses[job_id]["error"] = error_msg
            _job_statuses[job_id]["completed_at"] = datetime.utcnow().isoformat()
            _job_statuses[job_id]["progress"] = 0.0

    # _process_domain method removed - it was non-compliant with database connection standards
    # All background processing should use process_domain_with_own_session which follows
    # the proper pattern for background tasks with its own session management

    async def get_job_status(
        self,
        job_id: str,
        session: AsyncSession,
    ) -> JobStatusResponse:
        """
        Get the status of a job.

        Args:
            job_id: The job ID to check
            session: Database session

        Returns:
            JobStatusResponse with job status and details
        """
        logger.debug(f"Getting status for job: {job_id}")

        # Check transaction state for debugging
        in_transaction = session.in_transaction()
        logger.debug(f"Session transaction state in get_job_status: {in_transaction}")

        try:
            # Try to get the job from in-memory cache first
            if job_id in _job_statuses:
                job_data = _job_statuses[job_id]
                logger.debug(
                    f"Found job in memory: {job_id}, status: {job_data.get('status')}"
                )

                # Create response using in-memory data
                return JobStatusResponse(
                    job_id=job_id,
                    status=job_data.get("status", "unknown"),
                    domain=job_data.get("domain"),
                    progress=job_data.get("progress", 0.0),
                    created_at=job_data.get("created_at"),
                    metadata=job_data.get("metadata", {}),
                    error=job_data.get("error"),
                )

            # If not in memory, try to get from database
            try:
                # Get job from database using SQLAlchemy ORM
                from sqlalchemy import select

                from ...models.job import Job

                # REMOVED: tenant_id filter to prevent tenant-related errors
                query = select(Job).where(Job.job_id == job_id)

                result = await session.execute(
                    query,
                    execution_options={
                        "no_parameters": True,
                        "statement_cache_size": 0,
                    },
                )
                job = result.scalar_one_or_none()

                if job:
                    logger.debug(
                        f"Found job in database: {job_id}, status: {job.status}"
                    )

                    # Create response using database data
                    return JobStatusResponse(
                        job_id=str(job.job_id),
                        status=str(job.status),
                        domain=job.metadata.get("domain") if job.metadata else None,
                        progress=0.0
                        if job.progress is None
                        else float(str(job.progress)),
                        created_at=job.created_at.isoformat()
                        if job.created_at
                        else None,
                        metadata=job.metadata or {},
                        error=None if job.error is None else str(job.error),
                    )
            except Exception as db_error:
                logger.error(f"Error getting job from database: {str(db_error)}")

            # If we get here, job wasn't found in memory or database
            logger.warning(f"Job not found: {job_id}")
            return JobStatusResponse(
                job_id=job_id,
                status="not_found",
                message=f"Job {job_id} not found",
                progress=0.0,  # Ensure progress is always a valid float
            )

        except Exception as e:
            logger.error(f"Error retrieving job status: {str(e)}")
            raise ValueError(f"Error retrieving job status: {str(e)}")


# Singleton instance
sitemap_processing_service = SitemapProcessingService()


async def _update_job_failure(
    session: AsyncSession, job_id: str, error_message: str
) -> None:
    """
    Update job status to failed with the given error message.
    This is a helper function used in background tasks.

    Args:
        session: AsyncSession for database interaction
        job_id: The job identifier
        error_message: Error message to store
    """
    # Memory-based status update
    if job_id in _job_statuses:
        _job_statuses[job_id]["status"] = "failed"
        _job_statuses[job_id]["error"] = error_message
        _job_statuses[job_id]["completed_at"] = datetime.utcnow().isoformat()
        _job_statuses[job_id]["progress"] = 0.0

    # Add ORM-based job status update here if needed
    # This would update the jobs table directly
    try:
        from sqlalchemy import update

        from ...models.job import Job

        # Update job record with error information
        await session.execute(
            update(Job)
            .where(Job.job_id == job_id)
            .values(
                status="failed",
                error=error_message,
                progress=0.0,
                updated_at=datetime.utcnow(),
            ),
            execution_options={"no_parameters": True, "statement_cache_size": 0},
        )
        await session.flush()
        logger.debug(f"Updated job {job_id} status to failed in database")
    except Exception as e:
        logger.error(f"Failed to update job status in database: {str(e)}")


async def process_domain_with_own_session(
    job_id: str, domain: str, user_id: Optional[str] = None, max_urls: int = 100
):
    """
    Process domain with its own dedicated session for background task reliability.

    This function follows the proper transaction management pattern for background tasks:
    1. Creates its own dedicated session using get_background_session()
    2. Manages its own transaction boundaries
    3. Handles errors with proper transaction awareness
    4. Updates job status appropriately

    Args:
        job_id: Unique job identifier
        domain: Domain to process
        user_id: User ID who initiated the request
        max_urls: Maximum number of URLs to process per sitemap
    """
    # Import the proper session factory that works with Supabase - this is the ONE AND ONLY ONE acceptable method
    from sqlalchemy import select, update

    from ...models.wf4_domain import Domain
    from ...models.wf5_sitemap_file import (
        SitemapFile,
        SitemapUrl,
        SitemapFileStatusEnum,
        SitemapUrlStatusEnum,
    )
    from ...scraper.domain_utils import standardize_domain
    from ...session.async_session import get_background_session

    logger.info(
        f"Starting dedicated background processing for domain: {domain}, job_id: {job_id}"
    )

    # Add critical debug logging
    logger.info(f"Job parameters: user_id={user_id}")

    # Use a valid test user ID if we're using the zero UUID (which doesn't exist in the database)
    # This prevents foreign key constraint violations
    if not user_id or user_id == "00000000-0000-0000-0000-000000000000":
        # Use the test user ID that we know exists in the database
        user_id = "5905e9fe-6c61-4694-b09a-6602017b000a"  # Hank Groman test user
        logger.info(f"Using test user ID for zero UUID: {user_id}")

    # Update job status to running - in memory only, no transaction needed
    if job_id in _job_statuses:
        _job_statuses[job_id]["status"] = "running"
        _job_statuses[job_id]["started_at"] = datetime.utcnow().isoformat()
        _job_statuses[job_id]["progress"] = 0.1

    # Initialize analyzer outside the session scope to manage its resources properly
    analyzer = SitemapAnalyzer()

    # Tracking variables for final status
    job_completed = False
    error_message = None
    stored_sitemaps = []
    total_url_count = 0

    try:
        # Standardize domain - ensure URL has http/https prefix
        if not domain.startswith(("http://", "https://")):
            domain = "https://" + domain

        clean_domain = standardize_domain(domain)
        logger.info(f"Standardized domain: {clean_domain}")

        # Convert user_id to UUID
        user_uuid = None
        if user_id:
            try:
                user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                logger.info(f"Successfully converted user_id to UUID: {user_uuid}")
            except ValueError:
                logger.error(f"Invalid UUID format for user_id: {user_id}")
                user_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
        else:
            logger.warning("No user_id provided. Using system user.")
            user_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")

        # Run the analyzer to discover sitemaps outside the transaction
        # to avoid long-running HTTP requests inside transaction boundaries
        logger.info(f"Analyzing domain sitemaps for: {clean_domain}")
        result = await analyzer.analyze_domain_sitemaps(
            domain=clean_domain,
            follow_robots_txt=True,
            extract_urls=True,
            max_urls_per_sitemap=max_urls,
        )

        # Get discovered sitemaps
        sitemaps = result.get("sitemaps", [])
        logger.info(f"Found {len(sitemaps)} sitemaps for domain: {clean_domain}")

        # ADDITIONAL DEBUG LOGGING
        if len(sitemaps) == 0:
            logger.warning(f"No sitemaps found for domain: {clean_domain}")
            discovery_methods = result.get("discovery_methods", {})
            sitemap_types = result.get("sitemap_types", {})
            error = result.get("error", "No error specified")
            logger.warning(
                f"Discovery methods: {discovery_methods}, Sitemap types: {sitemap_types}, Error: {error}"
            )

            # Let's directly try the most common sitemap URL
            direct_url = f"https://{clean_domain}/sitemap.xml"
            logger.warning(f"Directly testing sitemap URL: {direct_url}")

            # Test the direct sitemap URL
            try:
                is_valid, meta = await analyzer._validate_sitemap_url(direct_url)
                logger.warning(
                    f"Direct sitemap test result: is_valid={is_valid}, metadata={meta}"
                )

                if is_valid:
                    logger.warning(
                        "Sitemap is valid but wasn't discovered in the normal process! Adding it manually."
                    )
                    sitemaps.append(
                        {
                            "url": direct_url,
                            "discovery_method": "manual_test",
                            "domain": clean_domain,
                            **meta,
                        }
                    )
            except Exception as e:
                logger.error(f"Error testing direct sitemap URL: {e}")
        else:
            # Log details about discovered sitemaps
            for i, sitemap in enumerate(sitemaps):
                logger.info(
                    f"Sitemap #{i + 1}: URL={sitemap.get('url')}, type={sitemap.get('sitemap_type')}, method={sitemap.get('discovery_method')}"
                )

        # STEP 1: Check or create domain record with dedicated session
        domain_obj = None
        try:
            async with get_background_session() as session:
                async with session.begin():
                    logger.info("Started transaction for domain lookup/creation")

                    # Check if domain exists or create it
                    domain_query = select(Domain).where(Domain.domain == clean_domain)
                    domain_result = await session.execute(domain_query)
                    domain_obj = domain_result.scalars().first()

                    if not domain_obj:
                        logger.debug(f"Creating new domain record for: {clean_domain}")
                        domain_obj = Domain(
                            domain=clean_domain, created_by=user_uuid, status="active"
                        )
                        session.add(domain_obj)
                        # Explicitly flush to get the domain ID
                        await session.flush()
                        logger.debug(f"Created domain record with ID: {domain_obj.id}")
                    else:
                        logger.debug(
                            f"Found existing domain record with ID: {domain_obj.id}"
                        )
                        # Update the domain user
                        await session.execute(
                            update(Domain)
                            .where(Domain.id == domain_obj.id)
                            .values(created_by=user_uuid)
                        )
                        await session.flush()
                        logger.debug("Updated existing domain record user")
        except Exception as domain_error:
            logger.error(f"Error in domain lookup/creation: {str(domain_error)}")
            error_message = f"Failed to process domain record: {str(domain_error)}"
            raise

        # Early exit if no sitemaps found
        if not domain_obj:
            logger.error("Domain object could not be created or found")
            error_message = "Domain object could not be created or found"
            raise ValueError("Domain object could not be created or found")

        if not sitemaps:
            logger.warning(f"No sitemaps found for domain: {clean_domain}")

            # STEP 2: Update domain with zero counts in dedicated session
            try:
                async with get_background_session() as session:
                    async with session.begin():
                        # Update domain record with zero counts
                        await session.execute(
                            update(Domain)
                            .where(Domain.id == domain_obj.id)
                            .values(
                                total_sitemaps=0,
                                sitemap_urls=0,
                                last_scan=datetime.utcnow(),
                            )
                        )
                        logger.info("Updated domain with zero sitemap counts")
            except Exception as update_error:
                logger.error(
                    f"Error updating domain with zero counts: {str(update_error)}"
                )
                error_message = f"Error updating domain: {str(update_error)}"
                # Continue anyway since this is not critical

            # Mark job as completed even with no sitemaps
            job_completed = True
            stored_sitemaps = []
            return

        # STEP 3: Process each sitemap with its own transaction
        from ...models.tenant import DEFAULT_TENANT_ID

        for sitemap in sitemaps:
            try:
                async with get_background_session() as session:
                    async with session.begin():
                        sitemap_url = sitemap.get("url", "")
                        sitemap_type = sitemap.get("sitemap_type", "standard")
                        # CRITICAL: Convert enum to string if needed (handles SitemapType.INDEX -> "index")
                        if hasattr(sitemap_type, 'value'):
                            sitemap_type = sitemap_type.value
                        elif sitemap_type is None:
                            sitemap_type = "standard"
                        discovery_method = sitemap.get("discovery_method", "unknown")
                        url_count = sitemap.get("url_count", 0)
                        sitemap_size = sitemap.get("size_bytes", 0)
                        sitemap_urls = sitemap.get("urls", [])
                        logger.info(
                            f"SITEMAP DEBUG: sitemap.get('urls') returned {len(sitemap_urls) if sitemap_urls else 0} URLs for {sitemap_url}"
                        )
                        if sitemap_urls and len(sitemap_urls) > 0:
                            logger.info(
                                f"SITEMAP DEBUG: First URL data: {sitemap_urls[0] if sitemap_urls else 'None'}"
                            )

                        # Update the total URL count
                        total_url_count += url_count

                        # Check for metadata flags
                        has_lastmod = any(
                            url.get("lastmod") for url in sitemap_urls if url
                        )
                        has_priority = any(
                            url.get("priority") for url in sitemap_urls if url
                        )
                        has_changefreq = any(
                            url.get("changefreq") for url in sitemap_urls if url
                        )

                        logger.info(f"Creating sitemap record for URL: {sitemap_url}")

                        # Make sure URL isn't too long for the database
                        if sitemap_url and len(sitemap_url) > 2000:
                            sitemap_url = sitemap_url[:2000]
                            logger.warning(
                                f"Truncated sitemap URL to 2000 chars: {sitemap_url[:50]}..."
                            )

                        # Create the sitemap record
                        sitemap_obj = SitemapFile(
                            domain_id=domain_obj.id,
                            url=sitemap_url,
                            sitemap_type=sitemap_type,
                            discovery_method=discovery_method,
                            size_bytes=sitemap_size,
                            has_lastmod=has_lastmod,
                            has_priority=has_priority,
                            has_changefreq=has_changefreq,
                            created_by=user_uuid,
                            job_id=uuid.UUID(job_id)
                            if isinstance(job_id, str)
                            else job_id,
                            url_count=url_count,
                            tenant_id=uuid.UUID(DEFAULT_TENANT_ID),
                            status=SitemapFileStatusEnum.Completed,
                        )
                        session.add(sitemap_obj)
                        # Explicitly flush to get the sitemap ID
                        await session.flush()
                        logger.info(f"Created sitemap record with ID: {sitemap_obj.id}")

                        # Track successfully stored sitemaps
                        stored_sitemaps.append(
                            {
                                "id": str(sitemap_obj.id),
                                "url": sitemap_url,
                                "type": sitemap_type,
                                "url_count": url_count,
                            }
                        )

                        # Process URLs in batches
                        if sitemap_urls:
                            batch_size = 100
                            total_urls = len(sitemap_urls)
                            logger.info(
                                f"SITEMAP PROCESSING: Starting to process {total_urls} URLs in batches of {batch_size}"
                            )

                            for i in range(0, total_urls, batch_size):
                                try:
                                    batch_urls = sitemap_urls[i : i + batch_size]
                                    url_batch = []

                                    for url_data in batch_urls:
                                        try:
                                            if not url_data:
                                                continue

                                            # Handle both 'url' and 'loc' fields from sitemap
                                            url_value = None
                                            if "loc" in url_data and url_data["loc"]:
                                                url_value = url_data["loc"]
                                            elif "url" in url_data and url_data["url"]:
                                                url_value = url_data["url"]

                                            if not url_value:
                                                continue

                                            # Extract metadata
                                            lastmod_str = url_data.get("lastmod")
                                            lastmod = None
                                            if lastmod_str:
                                                try:
                                                    # Convert string to datetime object
                                                    lastmod = datetime.fromisoformat(lastmod_str.replace('Z', '+00:00'))
                                                except (ValueError, AttributeError) as e:
                                                    logger.warning(f"Invalid lastmod format '{lastmod_str}': {e}")
                                                    lastmod = None
                                            
                                            changefreq = url_data.get("changefreq")
                                            priority_str = url_data.get("priority")
                                            priority_value = float(priority_str) if priority_str else None

                                            # Create URL record
                                            url_obj = SitemapUrl(
                                                sitemap_id=sitemap_obj.id,
                                                domain_id=domain_obj.id,
                                                url=url_value,
                                                loc_text=url_value,
                                                lastmod=lastmod,
                                                changefreq=changefreq,
                                                priority_value=priority_value,
                                                status=SitemapUrlStatusEnum.Pending,
                                                tenant_id=uuid.UUID(DEFAULT_TENANT_ID),
                                                created_by=user_uuid,
                                            )
                                            url_batch.append(url_obj)

                                        except Exception as url_error:
                                            logger.error(
                                                f"Error processing URL data: {str(url_error)}"
                                            )
                                            # Continue with next URL
                                            continue

                                    # Bulk add URL batch
                                    if url_batch:
                                        session.add_all(url_batch)
                                        # Flush after each batch for better performance
                                        await session.flush()
                                        logger.info(
                                            f"Successfully added batch of {len(url_batch)} URLs to database"
                                        )

                                except Exception as batch_error:
                                    logger.error(
                                        f"Error processing URL batch: {str(batch_error)}"
                                    )
                                    await session.rollback()
                                    # Continue with next batch
                                    continue
                        else:
                            logger.warning(
                                f"SITEMAP PROCESSING: No URLs found in sitemap data for {sitemap_url}"
                            )
            except Exception as sitemap_error:
                logger.error(f"Error processing sitemap: {str(sitemap_error)}")
                # Continue with next sitemap, this one failed
                continue

        # STEP 4: Update domain record with final counts in dedicated session
        try:
            async with get_background_session() as session:
                async with session.begin():
                    if domain_obj:
                        await session.execute(
                            update(Domain)
                            .where(Domain.id == domain_obj.id)
                            .values(
                                total_sitemaps=len(stored_sitemaps),
                                sitemap_urls=total_url_count,
                                last_scan=datetime.utcnow(),
                            )
                        )
                        logger.info(
                            f"Updated domain with sitemap counts: {len(stored_sitemaps)} sitemaps, {total_url_count} URLs"
                        )
        except Exception as update_error:
            logger.error(
                f"Error updating domain with final counts: {str(update_error)}"
            )
            error_message = f"Error updating domain: {str(update_error)}"
            # Continue anyway since this is not critical

        # Mark as completed if we got here
        job_completed = True
        logger.info(
            f"Sitemap processing completed successfully, stored {len(stored_sitemaps)} sitemaps"
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in process_domain_with_own_session: {error_message}")
    finally:
        # Always close the analyzer session
        try:
            await analyzer.close_session()
        except Exception as close_error:
            logger.error(f"Error closing analyzer session: {str(close_error)}")

        # STEP 5: Update final job status in a separate session
        try:
            if job_id in _job_statuses:
                if job_completed:
                    _job_statuses[job_id]["status"] = "complete"
                    _job_statuses[job_id]["progress"] = 1.0
                    _job_statuses[job_id]["completed_at"] = (
                        datetime.utcnow().isoformat()
                    )
                    _job_statuses[job_id]["metadata"] = {"sitemaps": stored_sitemaps}
                    logger.info(
                        f"Updated job status to complete, stored {len(stored_sitemaps)} sitemaps"
                    )
                else:
                    _job_statuses[job_id]["status"] = "failed"
                    _job_statuses[job_id]["error"] = error_message
                    _job_statuses[job_id]["completed_at"] = (
                        datetime.utcnow().isoformat()
                    )
                    logger.error(f"Updated job status to failed: {error_message}")

                # Also update the job status in the database
                try:
                    from ...services.job_service import job_service

                    async with get_background_session() as db_session:
                        async with db_session.begin():
                            # Try to get the numeric job ID from UUID
                            from sqlalchemy import select

                            from ...models.job import Job

                            query = select(Job).where(Job.job_id == job_id)
                            result = await db_session.execute(query)
                            job_record = result.scalars().first()

                            if job_record:
                                # Get the job ID from the record's dictionary representation
                                job_dict = job_record.to_dict()
                                db_job_id = job_dict["id"]

                                if job_completed:
                                    await job_service.update_status(
                                        db_session,
                                        job_id=db_job_id,
                                        status="complete",
                                        progress=1.0,
                                        result_data={"sitemaps": stored_sitemaps},
                                    )
                                    logger.info(
                                        f"Updated job {db_job_id} status to 'complete' in database"
                                    )
                                else:
                                    await job_service.update_status(
                                        db_session,
                                        job_id=db_job_id,
                                        status="failed",
                                        error=error_message,
                                    )
                                    logger.info(
                                        f"Updated job {db_job_id} status to 'failed' in database"
                                    )
                            else:
                                logger.warning(
                                    f"Could not find job with UUID {job_id} in database for status update"
                                )
                except Exception as db_update_error:
                    logger.error(
                        f"Error updating job status in database: {str(db_update_error)}"
                    )
        except Exception as status_error:
            logger.error(f"Error updating job status: {str(status_error)}")
