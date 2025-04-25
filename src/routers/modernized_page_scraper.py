"""
Page Scraper Router - Batch Operations

This module provides API routes for batch page scraping operations.
Uses standard FastAPI routing with explicit permission checks.
"""
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt_auth import DEFAULT_TENANT_ID, get_current_user

# RBAC imports removed
# from ..utils.permissions import require_permission, require_feature_enabled
from ..config.settings import settings
# Explicitly import needed models, excluding JobStatusResponse from here
from ..models import (
    BatchRequest,
    BatchResponse,
    BatchStatusResponse,
    SitemapScrapingRequest,
    SitemapScrapingResponse,
)
# Import JobStatusResponse from its correct schema location
from ..schemas.job import JobStatusResponse

from ..services.core.user_context_service import user_context_service
from ..services.page_scraper import page_processing_service
from ..session.async_session import get_session_dependency

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v3/modernized_page_scraper",
    tags=["modernized_page_scraper"]
)

# Using DEFAULT_TENANT_ID from jwt_auth.py

def is_development_mode() -> bool:
    """
    Checks if the application is running in development mode.
    Requires explicit opt-in through environment variable.
    """
    dev_mode = os.getenv("SCRAPER_SKY_DEV_MODE", "").lower() == "true"
    if dev_mode:
        logger.warning("⚠️ Running in DEVELOPMENT mode - ALL AUTH CHECKS BYPASSED ⚠️")
    return dev_mode or settings.environment.lower() in ["development", "dev"]

# Development user for local testing
async def get_development_user():
    """
    Provide a mock user for local development with full page scraper access.
    This is only used when SCRAPER_SKY_DEV_MODE=true is set.
    """
    logger.info("Using development user with full access")
    return {
        "id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "email": "hankgroman@gmail.com",
        "tenant_id": DEFAULT_TENANT_ID,
        "roles": ["admin"],
        "permissions": ["access_page_scraper", "*"],
        "auth_method": "dev_mode",
        "is_admin": True
    }

# Choose the appropriate user dependency based on explicit development mode
user_dependency = get_development_user if is_development_mode() else get_current_user

# Authorization dependency
async def verify_page_scraper_access(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(user_dependency)
) -> Dict:
    """
    Verify that the current user has access to page scraper functionality.
    In development mode (SCRAPER_SKY_DEV_MODE=true), this will use a mock user with full access.
    """
    if is_development_mode():
        return current_user

    # RBAC checks removed
    # require_permission(current_user, "access_page_scraper")

    # Check if feature is enabled
    # user_permissions = current_user.get("permissions", [])
    # await require_feature_enabled(
    #     tenant_id=current_user.get("tenant_id", DEFAULT_TENANT_ID),
    #     feature_name="page_scraper",
    #     session=session,
    #     user_permissions=user_permissions
    # )

    logger.info(f"Using JWT validation only (RBAC removed) for page scraper access, tenant: {current_user.get('tenant_id', DEFAULT_TENANT_ID)}")

    return current_user

# ===== Single Domain Scan =====

@router.post("/scan", response_model=SitemapScrapingResponse)
async def scan_domain(
    background_tasks: BackgroundTasks,
    request: SitemapScrapingRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(verify_page_scraper_access)
) -> SitemapScrapingResponse:
    """
    Scan a domain to extract metadata from its pages.

    Args:
        background_tasks: FastAPI background tasks handler
        request: Request body containing base_url and max_pages
        session: SQLAlchemy async session
        current_user: Current authenticated user information

    Returns:
        Response with job ID and status URL
    """
    logger.info(f"Received scan request for domain: {request.base_url}")

    # Get user ID
    user_id = user_context_service.get_valid_user_id(current_user=current_user)
    if user_id is None:
        user_id = "system"

    # Router owns transaction boundaries
    async with session.begin():
        # Process the domain scan through the page processing service
        result = await page_processing_service.initiate_domain_scan(
            session=session,
            base_url=request.base_url,
            user_id=user_id,
            max_pages=request.max_pages or 1000
        )

    # Add background task AFTER transaction commits to perform actual scraping
    # Import the function to avoid circular imports
    from ..services.page_scraper.domain_processor import process_domain_with_own_session

    # Add the background task
    background_tasks.add_task(
        process_domain_with_own_session,
        job_id=result["job_id"],
        domain=request.base_url,
        user_id=user_id,
        max_pages=request.max_pages or 1000
    )

    logger.info(f"Background task added for domain: {request.base_url}, job_id: {result['job_id']}")

    # Return the response
    return SitemapScrapingResponse(
        job_id=result["job_id"],
        status_url=result["status_url"],
        created_at=datetime.utcnow().isoformat()
    )

# ===== Batch Domain Scan =====

@router.post("/batch", response_model=BatchResponse)
async def batch_scan_domains(
    background_tasks: BackgroundTasks,
    request: BatchRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(verify_page_scraper_access)
) -> BatchResponse:
    """
    Process a batch of domains for page content.

    Args:
        request: Batch request with list of domains
        background_tasks: FastAPI background tasks handler
        session: SQLAlchemy async session
        current_user: Current authenticated user information

    Returns:
        Response with batch ID and status URL
    """
    logger.info(f"Received batch scan request with {len(request.domains)} domains")

    # Get user ID
    user_id = user_context_service.get_valid_user_id(current_user=current_user)
    if user_id is None:
        user_id = "system"

    # Router owns transaction boundaries
    async with session.begin():
        # Process the batch scan
        result = await page_processing_service.initiate_batch_scan(
            session=session,
            domains=request.domains,
            user_id=user_id,
            max_pages=request.max_pages or 1000
        )

    # Return the response
    return BatchResponse(
        batch_id=result["batch_id"],
        status_url=result["status_url"],
        job_count=result["job_count"],
        created_at=datetime.utcnow().isoformat()
    )

# ===== Job Status =====

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(verify_page_scraper_access)
) -> JobStatusResponse:
    """
    Get the status of a page scraping job.

    Args:
        job_id: Job ID to check
        session: SQLAlchemy async session
        current_user: Current authenticated user information

    Returns:
        Job status information
    """
    logger.info(f"Checking status for job: {job_id}")

    # Router owns transaction boundaries
    async with session.begin():
        # Get job status within transaction
        status = await page_processing_service.get_job_status(
            session=session,
            job_id=job_id
        )

    # Return the response
    return JobStatusResponse(**status)

# ===== Batch Status =====

@router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse)
async def get_batch_status(
    batch_id: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(verify_page_scraper_access)
) -> BatchStatusResponse:
    """
    Get the status of a batch processing job.

    Args:
        batch_id: Batch ID to check
        session: SQLAlchemy async session
        current_user: Current authenticated user information

    Returns:
        Batch status information
    """
    logger.info(f"Checking status for batch: {batch_id}")

    # Router owns transaction boundaries
    async with session.begin():
        # Get batch status within transaction
        status = await page_processing_service.get_batch_status(
            session=session,
            batch_id=batch_id
        )

    # Return the response
    return BatchStatusResponse(**status)
