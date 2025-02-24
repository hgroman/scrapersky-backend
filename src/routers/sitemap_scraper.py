"""
Sitemap scraping functionality.

This module provides endpoints for scanning domains and extracting metadata.
It supports both single domain scanning and batch processing.

Endpoints:
- POST /api/v1/scrapersky: Scan a single domain
- GET /api/v1/status/{job_id}: Check the status of a scan

The module handles:
- Domain validation and standardization
- Metadata extraction
- Database storage
- Status tracking
- Error handling
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Optional, Any
from pydantic import BaseModel
import logging
import asyncio
from datetime import datetime
from ..models import SitemapScrapingRequest, SitemapScrapingResponse
from ..scraper.metadata_extractor import detect_site_metadata
from ..db.domain_handler import DomainDBHandler
from ..scraper.domain_utils import standardize_domain, get_domain_url
from ..scraper.utils import generate_job_id
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Status tracking model
class ScanStatus(BaseModel):
    """Model for tracking scan status."""
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    started_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None
    progress: Optional[Dict] = None

# Redis will be used in production for better scalability
_job_statuses: Dict[str, ScanStatus] = {}

# Security prefix 'api/v1' added for proper versioning and routing.
# Updated tag to "scrapersky" for consistency with the new endpoint naming.
router = APIRouter(prefix="/api/v1", tags=["scrapersky"])

class ScanResponse(BaseModel):
    """Response model for scan operations."""
    job_id: str
    status: str
    message: str

class DomainData(BaseModel):
    """Model for domain data."""
    metadata: Dict[str, Any]
    status: str = "completed"
    error: Optional[str] = None

@router.post("/scrapersky", response_model=SitemapScrapingResponse)
async def scan_domain(request: SitemapScrapingRequest) -> SitemapScrapingResponse:
    """
    Scan a domain and extract metadata.

    This endpoint initiates a scan of the provided domain and extracts metadata
    such as title, description, technology stack, and contact information.

    Args:
        request: The request containing the domain to scan and tenant ID

    Returns:
        A response containing the job ID and status URL

    Raises:
        HTTPException: If the domain is invalid or the scan fails to initiate
    """
    try:
        # Generate unique job ID
        job_id = generate_job_id()

        # Initialize status tracking
        _job_statuses[job_id] = ScanStatus(
            job_id=job_id,
            status="pending",
            started_at=datetime.utcnow()
        )

        # Validate and standardize domain
        try:
            domain = standardize_domain(request.base_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Start background task
        asyncio.create_task(process_domain_scan(job_id, domain, request.tenant_id))

        return SitemapScrapingResponse(
            job_id=job_id,
            status_url=f"/api/v1/status/{job_id}"
        )

    except Exception as e:
        logger.error(f"Error initiating scan: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))

async def process_domain_scan(job_id: str, domain: str, tenant_id: str):
    """
    Process domain scan in background.

    This function handles the actual domain scanning process as a background task.
    It extracts metadata from the domain, stores it in the database, and updates
    the scan status throughout the process.

    The function follows these steps:
    1. Update status to "running"
    2. Extract metadata from the domain
    3. Format the data for database storage
    4. Store the data in the database (handling duplicates)
    5. Update the status to "completed" or "failed"

    Args:
        job_id: The unique identifier for this scan job
        domain: The standardized domain to scan
        tenant_id: The tenant ID associated with this scan

    Note:
        This function is designed to be run as a background task and does not return a value.
        It updates the global _job_statuses dictionary with the scan results.
    """
    try:
        status = _job_statuses[job_id]
        status.status = "running"
        status.progress = {"step": "starting", "message": "Initializing scan"}

        # Extract metadata
        url = get_domain_url(domain)
        status.progress = {"step": "extracting", "message": f"Extracting metadata from {url}"}

        metadata = await detect_site_metadata(url)
        if not metadata:
            raise Exception("Failed to extract metadata")

        # Format domain data for database
        domain_data = {
            "domain": domain,
            "tenant_id": tenant_id,
            "title": metadata.get("title"),
            "description": metadata.get("description"),
            "favicon_url": metadata.get("favicon_url"),
            "logo_url": metadata.get("logo_url"),
            "language": metadata.get("language"),
            "is_wordpress": metadata.get("is_wordpress", False),
            "wordpress_version": metadata.get("wordpress_version"),
            "has_elementor": metadata.get("has_elementor", False),
            "email_addresses": metadata.get("contact_info", {}).get("email", []),
            "phone_numbers": metadata.get("contact_info", {}).get("phone", []),
            "facebook_url": metadata.get("social_links", {}).get("facebook"),
            "twitter_url": metadata.get("social_links", {}).get("twitter"),
            "linkedin_url": metadata.get("social_links", {}).get("linkedin"),
            "instagram_url": metadata.get("social_links", {}).get("instagram"),
            "youtube_url": metadata.get("social_links", {}).get("youtube"),
            "tech_stack": json.dumps(metadata.get("tech_stack", {})),
            "meta_json": json.dumps(metadata)
        }

        # Update database - handle duplicates gracefully
        status.progress = {"step": "storing", "message": "Storing domain data"}
        db_handler = DomainDBHandler()

        # Check if domain already exists
        domain_exists = await db_handler.domain_exists(domain)

        if domain_exists:
            logger.info(f"Domain {domain} already exists, updating record")
            # Update all relevant fields
            update_data = {
                "meta_json": json.dumps(metadata),
                "title": metadata.get("title"),
                "description": metadata.get("description"),
                "favicon_url": metadata.get("favicon_url"),
                "logo_url": metadata.get("logo_url"),
                "language": metadata.get("language"),
                "is_wordpress": metadata.get("is_wordpress", False),
                "wordpress_version": metadata.get("wordpress_version"),
                "has_elementor": metadata.get("has_elementor", False),
                "email_addresses": metadata.get("contact_info", {}).get("email", []),
                "phone_numbers": metadata.get("contact_info", {}).get("phone", []),
                "facebook_url": metadata.get("social_links", {}).get("facebook"),
                "twitter_url": metadata.get("social_links", {}).get("twitter"),
                "linkedin_url": metadata.get("social_links", {}).get("linkedin"),
                "instagram_url": metadata.get("social_links", {}).get("instagram"),
                "youtube_url": metadata.get("social_links", {}).get("youtube"),
                "tech_stack": json.dumps(metadata.get("tech_stack", {})),
                "tenant_id": tenant_id
            }
            await db_handler.update_domain_data(domain, update_data)
        else:
            logger.info(f"Inserting new domain: {domain}")
            try:
                # Insert new domain
                await db_handler.insert_domain_data(domain_data)
            except Exception as db_error:
                # Fallback to update if insert fails (race condition)
                if "duplicate key value" in str(db_error):
                    logger.warning(f"Race condition detected for {domain}, falling back to update")
                    update_data = {
                        "meta_json": json.dumps(metadata),
                        "title": metadata.get("title"),
                        "description": metadata.get("description"),
                        "favicon_url": metadata.get("favicon_url"),
                        "logo_url": metadata.get("logo_url"),
                        "language": metadata.get("language"),
                        "is_wordpress": metadata.get("is_wordpress", False),
                        "wordpress_version": metadata.get("wordpress_version"),
                        "has_elementor": metadata.get("has_elementor", False),
                        "email_addresses": metadata.get("contact_info", {}).get("email", []),
                        "phone_numbers": metadata.get("contact_info", {}).get("phone", []),
                        "facebook_url": metadata.get("social_links", {}).get("facebook"),
                        "twitter_url": metadata.get("social_links", {}).get("twitter"),
                        "linkedin_url": metadata.get("social_links", {}).get("linkedin"),
                        "instagram_url": metadata.get("social_links", {}).get("instagram"),
                        "youtube_url": metadata.get("social_links", {}).get("youtube"),
                        "tech_stack": json.dumps(metadata.get("tech_stack", {})),
                        "tenant_id": tenant_id
                    }
                    await db_handler.update_domain_data(domain, update_data)
                else:
                    raise db_error

        # Update status
        status.status = "completed"
        status.completed_at = datetime.utcnow()
        status.metadata = metadata
        status.progress = {"step": "completed", "message": "Scan completed successfully"}

    except Exception as e:
        logger.error(f"Error processing domain {domain}: {str(e)}")
        status.status = "failed"
        status.error = str(e)
        status.completed_at = datetime.utcnow()
        status.progress = {"step": "failed", "message": f"Scan failed: {str(e)}"}

@router.get("/status/{job_id}")
async def get_scan_status(job_id: str):
    """
    Get the status of a scan job.

    This endpoint retrieves the current status of a domain scan job.
    It returns detailed information about the scan progress, including
    any extracted metadata if the scan has completed.

    Args:
        job_id: The unique identifier of the scan job

    Returns:
        The current status of the scan job, including metadata if available

    Raises:
        HTTPException: If the job ID is not found
    """
    if job_id not in _job_statuses:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_statuses[job_id]
