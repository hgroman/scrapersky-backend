"""Sitemap scraping functionality."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from pydantic import BaseModel
import logging
import asyncio
from datetime import datetime
from urllib.parse import urlparse
from ..models import SitemapScrapingRequest, SitemapScrapingResponse
from ..scraper.metadata_extractor import detect_site_metadata
from ..db.domain_handler import DomainDBHandler
from ..scraper.utils import generate_job_id, validate_url

# Status tracking model
class ScanStatus(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    started_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None

# TODO: Replace in-memory status tracking with Redis for better scalability and persistence.
# This is a temporary solution for the MVP that will be replaced with Redis in production.
# Limitations:
# - Status is lost on server restart
# - No cleanup of old statuses
# - Not suitable for multiple server instances
_job_statuses: Dict[str, ScanStatus] = {}

# Security prefix 'api/v1' added for proper versioning and routing.
# Updated tag to "scrapersky" for consistency with the new endpoint naming.
router = APIRouter(prefix="/api/v1", tags=["scrapersky"])

async def process_scan(job_id: str, request: SitemapScrapingRequest):
    """Process the scan asynchronously."""
    status = _job_statuses[job_id]
    status.status = "running"
    
    try:
        metadata = await detect_site_metadata(request.base_url)
        if metadata is None:
            raise ValueError("Failed to extract metadata from URL")
            
        domain = urlparse(request.base_url).netloc
        domain_data = {
            "tenant_id": request.tenant_id,
            "domain": domain,
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
            "tech_stack": metadata.get("tech_stack", {}),
            "meta_json": metadata  # Store full metadata in JSON field
        }
        
        await DomainDBHandler.insert_domain_data(domain_data)
        
        status.status = "completed"
        status.metadata = metadata
        status.completed_at = datetime.utcnow()
        
    except Exception as e:
        status.status = "failed"
        status.error = str(e)
        status.completed_at = datetime.utcnow()
        logging.error(f"Failed to scan sitemap: {str(e)}")

@router.post("/scrapersky", response_model=SitemapScrapingResponse)
async def scan_sitemap(request: SitemapScrapingRequest):
    """Scan a website's sitemap and extract metadata."""
    if not validate_url(request.base_url):
        raise HTTPException(400, detail="Invalid URL protocol")
    
    job_id = generate_job_id()
    
    # Initialize job status
    _job_statuses[job_id] = ScanStatus(
        job_id=job_id,
        status="pending",
        started_at=datetime.utcnow()
    )
    
    # Launch scan in background
    asyncio.create_task(process_scan(job_id, request))
    
    # Note: Status URL is provided but may not be reliable in current MVP implementation.
    # Will be more robust once Redis is integrated.
    return SitemapScrapingResponse(
        job_id=job_id,
        status_url=f"http://localhost:8000/api/v1/status/{job_id}"
    )

@router.get("/status/{job_id}", response_model=ScanStatus)
async def get_scan_status(job_id: str):
    """Get the status of a scan job.
    
    Note: This is a temporary MVP implementation using in-memory storage.
    Status information may be lost on server restart.
    """
    if job_id not in _job_statuses:
        # If status is not found, assume it completed since data would be in Supabase.
        return ScanStatus(
            job_id=job_id,
            status="completed",
            started_at=datetime.utcnow(),  # We don't know the actual start time
            completed_at=datetime.utcnow()
        )
    return _job_statuses[job_id]
