"""
API models for sitemap scraper endpoints.

This module defines Pydantic models for API requests and responses.
"""
import enum
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import UUID4, BaseModel, Field, HttpUrl, validator


class SitemapScrapingRequest(BaseModel):
    """Request model for sitemap scraping endpoint."""
    base_url: str = Field(..., description="Domain URL to scan")
    max_pages: int = Field(1000, description="Maximum number of pages to scan")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for the scan")

class SitemapScrapingResponse(BaseModel):
    """Response model for sitemap scraping endpoint."""
    job_id: str = Field(..., description="Job ID for tracking the scan")
    status_url: str = Field(..., description="URL to check the status of the scan")
    created_at: Optional[str] = Field(None, description="When the job was created")

class BatchRequest(BaseModel):
    """Request model for batch scraping endpoint."""
    domains: List[str] = Field(..., description="List of domains to scan")
    max_pages: int = Field(1000, description="Maximum number of pages to scan per domain")
    max_concurrent: int = Field(5, description="Maximum number of concurrent jobs")
    batch_id: Optional[str] = Field(None, description="Optional batch ID (generated if not provided)")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for the scan")

class BatchResponse(BaseModel):
    """Response model for batch scraping endpoint."""
    batch_id: str = Field(..., description="Batch ID for tracking the scan")
    status_url: str = Field(..., description="URL to check the status of the batch")
    job_count: int = Field(..., description="Number of jobs in the batch")
    created_at: Optional[str] = Field(None, description="When the batch was created")

class BatchStatusResponse(BaseModel):
    """Response model for batch status endpoint."""
    batch_id: str = Field(..., description="Batch ID")
    status: str = Field(..., description="Batch status (pending, running, complete, failed, partial)")
    total_domains: int = Field(0, description="Total number of domains in the batch")
    completed_domains: int = Field(0, description="Number of completed domains")
    failed_domains: int = Field(0, description="Number of failed domains")
    progress: float = Field(0.0, description="Overall progress as a percentage (0-100)")
    created_at: Optional[str] = Field(None, description="When the batch was created")
    updated_at: Optional[str] = Field(None, description="When the batch was last updated")
    start_time: Optional[str] = Field(None, description="When processing started")
    end_time: Optional[str] = Field(None, description="When processing completed")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    domain_statuses: Optional[Dict[str, Any]] = Field(None, description="Status of individual domains")
    error: Optional[str] = Field(None, description="Error message if batch failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional batch metadata")

# Sitemap Analyzer Models

class SitemapExtractOptions(BaseModel):
    """Options for sitemap extraction."""
    follow_sitemapindex: bool = Field(True, description="Whether to follow sitemap index files")
    check_robots_txt: bool = Field(True, description="Whether to check robots.txt for sitemaps")
    max_depth: int = Field(3, description="Maximum depth to follow sitemap index files")
    max_sitemaps: int = Field(100, description="Maximum number of sitemaps to process")
    verify_ssl: bool = Field(True, description="Whether to verify SSL certificates")
    timeout_seconds: int = Field(60, description="Timeout for HTTP requests in seconds")
    extract_metadata: bool = Field(True, description="Whether to extract metadata from sitemaps")
    store_raw_xml: bool = Field(False, description="Whether to store raw XML content")

class SitemapType(str, Enum):
    """Types of sitemaps that can be encountered."""
    INDEX = "index"
    STANDARD = "standard"
    IMAGE = "image"
    VIDEO = "video"
    NEWS = "news"
    UNKNOWN = "unknown"

class DiscoveryMethod(str, Enum):
    """How a sitemap was discovered."""
    ROBOTS_TXT = "robots_txt"
    COMMON_PATH = "common_path"
    SITEMAP_INDEX = "sitemap_index"
    HTML_LINK = "html_link"
    MANUAL = "manual"

class SitemapAnalyzerRequest(BaseModel):
    """Request model for sitemap analyzer endpoint."""
    domain: str = Field(..., description="Domain to analyze")
    user_id: Optional[str] = Field(None, description="User ID performing the analysis")
    extract_options: Optional[SitemapExtractOptions] = Field(None, description="Options for sitemap extraction")
    include_content: bool = Field(False, description="Whether to include sitemap content in response")
    store_results: bool = Field(True, description="Whether to store results in database")
    # tenant_id field removed - using default tenant ID

    @validator('domain')
    def domain_must_be_valid(cls, v):
        """Validate domain format."""
        # Simple validation, could be more complex in production
        if not v or len(v) < 4 or '.' not in v:
            raise ValueError('Must be a valid domain')
        return v

class SitemapAnalyzerResponse(BaseModel):
    """Response model for sitemap analyzer endpoint."""
    job_id: str = Field(..., description="Job ID for tracking the analysis")
    status: str = Field(..., description="Status of the job (pending, running, complete, failed)")
    status_url: str = Field(..., description="URL to check the status of the analysis")
    domain: Optional[str] = Field(None, description="Domain being analyzed")
    created_at: Optional[str] = Field(None, description="When the job was created")

class SitemapFileResponse(BaseModel):
    """Response model for sitemap file data."""
    id: str = Field(..., description="Sitemap file ID")
    url: str = Field(..., description="URL of the sitemap file")
    sitemap_type: Optional[str] = Field(None, description="Type of sitemap (index, standard, etc.)")
    discovery_method: Optional[str] = Field(None, description="How the sitemap was discovered")
    page_count: Optional[int] = Field(None, description="Number of pages in the sitemap")
    size_bytes: Optional[int] = Field(None, description="Size of the sitemap in bytes")
    url_count: Optional[int] = Field(0, description="Number of URLs in the sitemap")
    last_modified: Optional[str] = Field(None, description="Last modified date of the sitemap")
    has_lastmod: Optional[bool] = Field(False, description="Whether the sitemap contains lastmod information")
    has_priority: Optional[bool] = Field(False, description="Whether the sitemap contains priority information")
    has_changefreq: Optional[bool] = Field(False, description="Whether the sitemap contains changefreq information")
    created_at: Optional[str] = Field(None, description="When the sitemap was processed")

    class Config:
        from_attributes = True

class SitemapUrlResponse(BaseModel):
    """Response model for sitemap URL data."""
    id: str = Field(..., description="URL entry ID")
    url: str = Field(..., description="The URL from the sitemap")
    lastmod: Optional[str] = Field(None, description="Last modified date from sitemap")
    changefreq: Optional[str] = Field(None, description="Change frequency from sitemap")
    priority: Optional[float] = Field(None, description="Priority from sitemap")
    created_at: Optional[str] = Field(None, description="When the URL was processed")

    class Config:
        from_attributes = True

class SitemapStatusResponse(BaseModel):
    """Response model for sitemap analysis status endpoint."""
    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status (pending, running, complete, failed)")
    progress: float = Field(0.0, description="Progress as a percentage (0-100)")
    domain: Optional[str] = Field(None, description="Domain being analyzed")
    created_at: Optional[str] = Field(None, description="When the job was created")
    updated_at: Optional[str] = Field(None, description="When the job was last updated")
    sitemap_count: Optional[int] = Field(0, description="Number of sitemaps found")
    url_count: Optional[int] = Field(0, description="Total number of URLs found")
    error: Optional[str] = Field(None, description="Error message if job failed")
    status_url: Optional[str] = Field(None, description="URL to check the status")
    results_url: Optional[str] = Field(None, description="URL to get the results if complete")

    class Config:
        from_attributes = True


# --- Models for Places Staging Selection --- #

class PlaceStagingStatusEnum(str, Enum):
    """Possible statuses for a place in the staging table. Mirrors DB PlaceStatusEnum."""
    NEW = "New" # Initial status after discovery
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"
    ARCHIVED = "Archived" # If user decides not to process

class PlaceStagingRecord(BaseModel):
    """Response model representing a single record from the places_staging table."""
    # Corresponds to Place model, adjust fields as needed for UI display
    place_id: str = Field(..., description="Google Place ID (Primary Key for Staging)")
    business_name: Optional[str] = Field(None, description="Business Name")
    address: Optional[str] = Field(None, description="Address")
    category: Optional[str] = Field(None, description="Primary Category")
    search_location: Optional[str] = Field(None, description="Location used for the search")
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    rating: Optional[float] = Field(None)
    reviews_count: Optional[int] = Field(None)
    price_level: Optional[int] = Field(None)
    status: Optional[PlaceStagingStatusEnum] = Field(PlaceStagingStatusEnum.NEW, description="Current status for deep scan selection")
    updated_at: datetime
    last_deep_scanned_at: Optional[datetime] = Field(None)
    search_job_id: UUID = Field(..., description="FK to the discovery Job")
    tenant_id: UUID

    class Config:
        from_attributes = True
        use_enum_values = True # Ensure enum values are used in response

class PlaceStagingListResponse(BaseModel):
    """Response model for listing staged places."""
    items: List[PlaceStagingRecord]
    total: int
    # Add pagination fields if needed (page, size, etc.)

class PlaceStatusUpdateRequest(BaseModel):
    """Request model to update the status of a staged place."""
    status: PlaceStagingStatusEnum = Field(..., description="The new status to set for the place")

# --- End Models for Places Staging Selection --- #


# --- Models for Local Businesses Selection --- #

class LocalBusinessApiStatusEnum(str, Enum):
    """Possible statuses for a local business, matching PlaceStatusEnum."""
    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit" # Ensure space is handled if API sends it
    Archived = "Archived"

class LocalBusinessBatchStatusUpdateRequest(BaseModel):
    """Request model to update the status for one or more local businesses."""
    local_business_ids: List[UUID] = Field(..., min_length=1, description="List of one or more Local Business UUIDs to update.")
    status: LocalBusinessApiStatusEnum = Field(..., description="The new main status to set.")

# --- End Models for Local Businesses Selection --- #


# --- Models for Domain Curation --- #

import enum  # Ensure enum is imported

from pydantic import UUID4  # Specific import for UUID4

# Import DB Enums required for response/request models
# Note: Adjust path if your models are structured differently
# try:
from .domain import SitemapAnalysisStatusEnum, SitemapCurationStatusEnum

# except ImportError:
#     # Fallback or specific handling if the import path differs
#     # This might happen if api_models.py is not in the same directory level as domain.py
#     # For now, assuming they are siblings or accessible via relative path
#     SitemapCurationStatusEnum = enum.Enum('SitemapCurationStatusEnum', {'New': 'New', 'Selected': 'Selected', 'Maybe': 'Maybe', 'Not_a_Fit': 'Not a Fit', 'Archived': 'Archived'})
#     SitemapAnalysisStatusEnum = enum.Enum('SitemapAnalysisStatusEnum', {'queued': 'queued', 'processing': 'processing', 'submitted': 'submitted', 'failed': 'failed'})


# Mirrors DB Enum SitemapCurationStatusEnum for API Input
class SitemapCurationStatusApiEnum(str, enum.Enum):
    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"
    Archived = "Archived"

# Request model for the batch update endpoint
class DomainBatchCurationStatusUpdateRequest(BaseModel):
    domain_ids: List[UUID4] = Field(..., min_length=1, description="List of one or more Domain UUIDs to update.")
    sitemap_curation_status: SitemapCurationStatusApiEnum = Field(..., description="The new curation status to set for the sitemap workflow.")

# Pydantic model mirroring Domain for API responses (adjust fields as needed for UI)
class DomainRecord(BaseModel):
    id: UUID4
    domain: str
    sitemap_curation_status: Optional[SitemapCurationStatusEnum] = None
    sitemap_analysis_status: Optional[SitemapAnalysisStatusEnum] = None
    sitemap_analysis_error: Optional[str] = None
    # Include other relevant Domain fields needed by the UI grid
    status: Optional[str] = None # Example: original domain status
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True # Return enum values as strings

# Standard paginated response wrapper
class PaginatedDomainResponse(BaseModel):
    items: List[DomainRecord]
    total: int
    page: int
    size: int
    pages: int

# --- End Models for Domain Curation --- #
