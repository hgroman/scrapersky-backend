"""
Sitemap Batch Router

This module provides endpoints for batch processing of multiple domains for sitemap scanning.
It leverages the existing batch processing architecture to handle multiple domains efficiently.

Transaction Management Pattern:
- This module uses the get_session_dependency for FastAPI dependency injection
- The injected session is used directly without additional context managers
- For background processing, get_background_session() is used to create new sessions
- This follows the architectural principle: "Routers own transaction boundaries, services do not"
"""
import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypedDict

from ..auth.jwt_auth import DEFAULT_TENANT_ID, get_current_user
from ..config.settings import settings
from ..models.batch_job import BatchJob
from ..services.batch.batch_functions import (
    BATCH_STATUS_COMPLETED,
    BATCH_STATUS_FAILED,
    BATCH_STATUS_PROCESSING,
    create_batch,
    get_batch_status,
)
from ..services.sitemap.processing_service import process_domain_with_own_session
from ..session.async_session import get_background_session, get_session_dependency

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    tags=["sitemap-batch"],
    responses={404: {"description": "Not found"}},
)

# Define our own status response model using Pydantic
class BatchStatusResponse(BaseModel):
    batch_id: str
    status: str
    total_domains: int
    completed_domains: int
    failed_domains: int
    progress: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    processing_time: Optional[float] = None
    domain_statuses: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        from_attributes = True  # For SQLAlchemy model compatibility

# Development mode utilities
def is_development_mode() -> bool:
    """
    Checks if the application is running in development mode.
    Requires explicit opt-in through environment variable.
    """
    dev_mode = os.getenv("SCRAPER_SKY_DEV_MODE", "").lower() == "true"
    if dev_mode:
        logger.warning(
            "⚠️ Running in DEVELOPMENT mode - ALL AUTH CHECKS BYPASSED ⚠️"
        )
    return dev_mode or settings.environment.lower() in ["development", "dev"]

async def get_development_user():
    """
    Provide a mock user for local development with full access.
    This is only used when SCRAPER_SKY_DEV_MODE=true is set.
    """
    logger.info("Using development user with full access to sitemap batch")
    return {
        "id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "user_id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "email": "dev@example.com",
        "tenant_id": DEFAULT_TENANT_ID,
        "roles": ["admin"],
        "permissions": ["*"],
        "auth_method": "dev_mode",
        "is_admin": True
    }

# Choose the appropriate user dependency based on development mode
user_dependency = (
    get_development_user if is_development_mode() else get_current_user
)

# Request and response models
class SitemapBatchRequest(BaseModel):
    domains: List[str] = Field(..., description="List of domains to process")
    max_pages: int = Field(1000, description="Maximum pages to process per domain")

    @validator('domains')
    def validate_domains(cls, domains):
        # Basic validation of domains
        if not domains:
            raise ValueError("At least one domain is required")

        if len(domains) > 100:
            raise ValueError("Maximum 100 domains allowed per batch")

        for domain in domains:
            if not domain or len(domain) < 3:
                raise ValueError(f"Invalid domain: {domain}")

        return domains

    @validator('max_pages')
    def validate_max_pages(cls, max_pages):
        if max_pages < 1:
            raise ValueError("max_pages must be at least 1")
        if max_pages > 10000:
            raise ValueError("max_pages cannot exceed 10000")
        return max_pages

class SitemapBatchResponse(BaseModel):
    batch_id: str
    status: str
    total_domains: int
    status_url: str

@router.post("/api/v3/sitemap/batch/create", response_model=SitemapBatchResponse)
async def create_sitemap_batch(
    request: SitemapBatchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(user_dependency),
):
    """
    Create a batch of domains for sitemap processing.

    This endpoint accepts multiple domains and creates a batch job to process them.
    Each domain will be processed individually as part of the batch.
    """
    # Generate batch ID
    batch_id = str(uuid.uuid4())
    logger.info(f"Creating sitemap batch {batch_id} with {len(request.domains)} domains")

    try:
        # Router owns the transaction boundary - session is already managed by FastAPI dependency
        # Get user ID from current_user
        user_id = current_user.get("id", current_user.get("user_id"))
        if not user_id:
            user_id = "5905e9fe-6c61-4694-b09a-6602017b000a"  # Default to test user if no ID
            logger.warning(f"No user ID found, using default: {user_id}")

        # Create batch record using existing function
        batch_result = await create_batch(
            session=session,
            batch_id=batch_id,
            domains=request.domains,
            user_id=user_id,
            options={"max_concurrent": 5, "max_pages": request.max_pages}
        )

        # Add background task to process the batch
        background_tasks.add_task(
            process_sitemap_batch_with_own_session,
            batch_id=batch_id,
            domains=request.domains,
            user_id=str(user_id),
            max_pages=request.max_pages
        )

        # Return immediate response with batch details
        return SitemapBatchResponse(
            batch_id=batch_id,
            status="pending",
            total_domains=len(request.domains),
            status_url=f"/api/v3/sitemap/batch/status/{batch_id}"
        )
    except Exception as e:
        logger.error(f"Error creating sitemap batch: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create sitemap batch: {str(e)}"
        )

@router.get("/api/v3/sitemap/batch/status/{batch_id}", response_model=BatchStatusResponse)
async def get_sitemap_batch_status(
    batch_id: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(user_dependency),
):
    """
    Get the status of a sitemap batch processing job.

    Returns detailed information about the batch, including progress and results.
    """
    try:
        # Router owns the transaction boundary - session is already managed by FastAPI dependency
        logger.info(f"Getting status for sitemap batch {batch_id}")
        batch_status = await get_batch_status(
            session=session,
            batch_id=batch_id
        )

        # Convert dict to Pydantic model for validation and serialization
        return BatchStatusResponse(**batch_status)
    except Exception as e:
        logger.error(f"Error getting sitemap batch status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch status: {str(e)}"
        )

async def process_sitemap_batch_with_own_session(
    batch_id: str,
    domains: List[str],
    user_id: str,
    max_pages: int = 1000
) -> None:
    """
    Process a batch of domains for sitemap scanning with its own database session.

    This function creates its own session and manages its own transaction boundaries.
    It processes multiple domains concurrently with a maximum concurrency limit.

    Args:
        batch_id: Batch ID to process
        domains: List of domains to process
        user_id: User ID processing the batch
        max_pages: Maximum pages to process per domain
    """
    logger.info(f"Starting sitemap batch processing for {len(domains)} domains")

    # Update batch status to processing
    try:
        async with get_background_session() as session:
            # Session already manages its own transaction
            batch = await BatchJob.get_by_batch_id(session, batch_id)
            if batch:
                setattr(batch, "status", BATCH_STATUS_PROCESSING)
                setattr(batch, "start_time", func.now())
                await session.flush()
                logger.info(f"Updated batch {batch_id} status to processing")
    except Exception as e:
        logger.error(f"Error updating batch status to processing: {str(e)}", exc_info=True)

    # Track domain processing results
    domain_results = {}
    total_domains = len(domains)
    completed_count = 0
    failed_count = 0

    # Define domain processor function that uses the existing sitemap processor
    async def process_single_domain(domain: str):
        domain_start_time = datetime.utcnow()
        try:
            # Process domain with its own session
            job_id = str(uuid.uuid4())
            await process_domain_with_own_session(
                job_id=job_id,
                domain=domain,
                user_id=user_id,
                max_urls=max_pages
            )

            # Domain processed successfully
            domain_end_time = datetime.utcnow()
            processing_time = (domain_end_time - domain_start_time).total_seconds()

            result = {
                "status": "completed",
                "job_id": job_id,
                "start_time": domain_start_time.isoformat(),
                "end_time": domain_end_time.isoformat(),
                "processing_time": processing_time,
                "error": None
            }
            logger.info(f"Successfully processed domain {domain} in {processing_time:.2f} seconds")
            return (domain, result, True)

        except Exception as e:
            # Domain processing failed
            domain_end_time = datetime.utcnow()
            processing_time = (domain_end_time - domain_start_time).total_seconds()

            job_id_str = job_id if 'job_id' in locals() else None

            result = {
                "status": "failed",
                "job_id": job_id_str,
                "start_time": domain_start_time.isoformat(),
                "end_time": domain_end_time.isoformat(),
                "processing_time": processing_time,
                "error": str(e)
            }
            logger.error(f"Error processing domain {domain}: {str(e)}", exc_info=True)
            return (domain, result, False)

    # Process domains concurrently with a limit on concurrency
    max_concurrent = 5
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(domain):
        async with semaphore:
            return await process_single_domain(domain)

    # Start concurrent processing
    tasks = []
    for domain in domains:
        tasks.append(process_with_semaphore(domain))

    # Use gather with return_exceptions to avoid task cancellation
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results and update batch
    for i, result in enumerate(results):
        # Handle exceptions from gather
        if isinstance(result, (Exception, BaseException)):
            logger.error(f"Task exception for domain {domains[i] if i < len(domains) else 'unknown'}: {str(result)}", exc_info=True)
            failed_count += 1

            # Add error entry to domain_results
            domain_results[domains[i] if i < len(domains) else f"unknown_{i}"] = {
                "status": "failed",
                "error": str(result),
                "start_time": datetime.utcnow().isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "processing_time": 0
            }
            continue

        try:
            domain, domain_result, success = result
            domain_results[domain] = domain_result

            if success:
                completed_count += 1
            else:
                failed_count += 1
        except Exception as process_error:
            # Handle any unexpected errors in processing results
            logger.error(f"Error processing result for index {i}: {str(process_error)}", exc_info=True)
            failed_count += 1
            continue

        # Update batch progress periodically
        if (i + 1) % 5 == 0 or (i + 1) == len(results):
            try:
                async with get_background_session() as session:
                    # Session already manages its own transaction
                    batch = await BatchJob.get_by_batch_id(session, batch_id)
                    if batch:
                        batch.update_progress(completed=completed_count, failed=failed_count)

                        # Update metadata with results
                        batch_dict = batch.to_dict()
                        metadata = batch_dict.get("batch_metadata") or {}
                        if not isinstance(metadata, dict):
                            metadata = {}
                        metadata["domain_results"] = domain_results
                        metadata["last_updated"] = datetime.utcnow().isoformat()
                        metadata["progress_percentage"] = ((completed_count + failed_count) / total_domains) * 100
                        setattr(batch, "batch_metadata", metadata)

                        await session.flush()
                        logger.debug(f"Updated batch progress: {completed_count} completed, {failed_count} failed, {i+1}/{len(results)} processed")
            except Exception as update_error:
                logger.error(f"Error updating batch progress: {str(update_error)}", exc_info=True)

    # Update final batch status
    try:
        async with get_background_session() as session:
            # Session already manages its own transaction
            batch = await BatchJob.get_by_batch_id(session, batch_id)
            if batch:
                # Determine final status
                if completed_count > 0 and failed_count == 0:
                    final_status = BATCH_STATUS_COMPLETED
                elif completed_count == 0 and failed_count > 0:
                    final_status = BATCH_STATUS_FAILED
                else:
                    final_status = BATCH_STATUS_COMPLETED  # Partial success

                # Update batch
                setattr(batch, "status", final_status)
                setattr(batch, "end_time", func.now())

                # Update metadata with domain results
                batch_dict = batch.to_dict()
                metadata = batch_dict.get("batch_metadata") or {}
                if not isinstance(metadata, dict):
                    metadata = {}
                metadata["domain_results"] = domain_results
                metadata["last_updated"] = datetime.utcnow().isoformat()
                metadata["final_status"] = final_status
                metadata["completed_domains"] = completed_count
                metadata["failed_domains"] = failed_count
                metadata["total_domains"] = total_domains
                metadata["completion_percentage"] = 100.0
                setattr(batch, "batch_metadata", metadata)

                await session.flush()
                logger.info(f"Batch {batch_id} processing complete: {completed_count} succeeded, {failed_count} failed")
    except Exception as e:
        logger.error(f"Error updating final batch status: {str(e)}", exc_info=True)
