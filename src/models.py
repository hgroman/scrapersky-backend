import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# Chat Models - REMOVED


# Scraping Models
class ScrapingRequest(BaseModel):
    url: HttpUrl
    selectors: Optional[List[str]] = None
    max_depth: Optional[int] = 1


class ScrapingResponse(BaseModel):
    url: str
    content: str
    title: Optional[str] = None
    timestamp: str


# Sitemap Models
class SocialLinks(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None


class ContactInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_page_url: Optional[str] = None


class TechnologyStack(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cms: Optional[str] = None
    analytics: Optional[str] = None
    frameworks: List[str] = []


class TaskStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ERROR = "error"
    MANUAL_REVIEW = "manual_review"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class SiteMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Core Identification
    url: HttpUrl
    tenant_id: str = Field(default="550e8400-e29b-41d4-a716-446655440000")
    lead_source: Optional[str] = None

    # Basic Info
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    status: str = "active"

    # Task Status Tracking
    content_scrape_status: TaskStatus = TaskStatus.QUEUED
    content_scrape_at: Optional[datetime] = None
    content_scrape_error: Optional[str] = None

    page_scrape_status: TaskStatus = TaskStatus.QUEUED
    page_scrape_at: Optional[datetime] = None
    page_scrape_error: Optional[str] = None

    sitemap_monitor_status: TaskStatus = TaskStatus.QUEUED
    sitemap_monitor_at: Optional[datetime] = None
    sitemap_monitor_error: Optional[str] = None

    # SSL and Security
    has_ssl: Optional[bool] = None
    ssl_expiry_date: Optional[datetime] = None
    security_headers: Optional[Dict[str, Any]] = None
    ssl_issuer: Optional[str] = None
    ssl_version: Optional[str] = None

    # Server and Infrastructure
    server_type: Optional[str] = None
    ip_address: Optional[str] = None
    hosting_provider: Optional[str] = None
    country_code: Optional[str] = None
    server_response_time: Optional[int] = None
    dns_records: Optional[Dict[str, Any]] = None
    hosting_location: Optional[str] = None
    cdn_provider: Optional[str] = None

    # Content Insights
    last_modified: Optional[datetime] = None
    robots_txt: Optional[str] = None
    has_sitemap: Optional[bool] = None
    page_count: Optional[int] = None
    content_language: List[str] = Field(default_factory=list)
    feed_urls: Optional[Dict[str, Any]] = None
    average_page_size: Optional[int] = None
    total_images_count: Optional[int] = None
    crawler_hints: Optional[Dict[str, Any]] = None

    # Business Context
    business_category: Optional[str] = None
    estimated_traffic: Optional[Dict[str, Any]] = None
    has_ecommerce: Optional[bool] = None
    primary_language: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    payment_methods: List[str] = Field(default_factory=list)
    business_type: Optional[str] = None
    industry_vertical: Optional[str] = None
    competitor_group: Optional[str] = None
    market_segment: Optional[str] = None

    # Error and Performance
    last_error: Optional[str] = None
    error_count: int = 0
    last_successful_scan: Optional[datetime] = None
    average_response_time: Optional[int] = None
    uptime_percentage: Optional[float] = None
    error_history: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    monitoring_status: Optional[str] = None
    alert_threshold: Optional[Dict[str, Any]] = None

    # Site Technical Details
    sitemap_url: Optional[str] = None
    tech_stack: Optional[Dict[str, Any]] = None


class SitemapScrapingRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    base_url: str
    tenant_id: str = Field(default="550e8400-e29b-41d4-a716-446655440000")
    max_pages: int = Field(default=1000)


class SitemapScrapingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: str
    status_url: str


class BatchRequest(BaseModel):
    """Request model for batch domain scanning."""

    domains: List[str]
    tenant_id: str = Field(default="550e8400-e29b-41d4-a716-446655440000")


class BatchResponse(BaseModel):
    """Response model for batch scan operations."""

    batch_id: str
    status_url: str
    job_count: int


class PageType(str, Enum):
    HTML = "text/html"
    XML = "application/xml"
    PDF = "application/pdf"
    OTHER = "other"


class BatchJobStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str
    progress: float
    error: Optional[str] = None


class BatchSitemapRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    base_urls: List[HttpUrl]
    concurrency: int = Field(default=5, ge=1, le=10)
    depth_limit: int = Field(default=3, ge=1, le=5)
    priority: int = Field(default=1, ge=1, le=3)


class SitemapStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_pages: int
    success_count: int
    failure_count: int
    avg_response_time: float
    tech_stack_counts: Dict[str, int]


# Places Scraper Models
class PlacesSearchRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location: str  # Location to search (e.g., "Houston, TX")
    business_type: str  # Type of business to search (e.g., "ophthalmology")
    radius_km: int = Field(default=10, ge=1, le=50)
    max_results: int = Field(default=20, ge=1, le=100)
    tenant_id: str = Field(default="550e8400-e29b-41d4-a716-446655440000")


class PlacesSearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: str = "started"
    status_url: str


class PlacesStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    total_places: int = 0
    stored_places: int = 0
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    search_query: str
    search_location: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    error: Optional[str] = None


# Sitemap Analyzer Models
class SitemapType(str, Enum):
    INDEX = "index"
    STANDARD = "standard"
    IMAGE = "image"
    VIDEO = "video"
    NEWS = "news"


class DiscoveryMethod(str, Enum):
    ROBOTS_TXT = "robots_txt"
    COMMON_PATH = "common_path"
    SITEMAP_INDEX = "sitemap_index"
    HTML_LINK = "html_link"
    MANUAL = "manual"


class SitemapAnalyzerRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    domain: str
    tenant_id: str = Field(default="550e8400-e29b-41d4-a716-446655440000")
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    lead_source: Optional[str] = None
    follow_robots_txt: bool = True
    extract_urls: bool = True
    max_urls_per_sitemap: int = Field(default=10000, ge=1, le=50000)
    priority: int = Field(default=5, ge=1, le=10)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

    @property
    def domain_url(self) -> str:
        """Format domain as URL with https prefix if not already present."""
        if self.domain.startswith(("http://", "https://")):
            return self.domain
        return f"https://{self.domain}"


class SitemapAnalyzerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "started"
    status_url: str
    domain: str


class SitemapAnalyzerBatchRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    domains: List[str]
    tenant_id: str = Field(default="550e8400-e29b-41d4-a716-446655440000")
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    lead_source: Optional[str] = None
    follow_robots_txt: bool = True
    extract_urls: bool = True
    max_urls_per_sitemap: int = Field(default=10000, ge=1, le=50000)
    max_concurrent_jobs: int = Field(default=5, ge=1, le=10)
    priority: int = Field(default=5, ge=1, le=10)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class SitemapAnalyzerBatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status_url: str
    job_count: int
    domains: List[str]


class SitemapStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    domain: str
    status: str  # "pending", "running", "completed", "failed"
    total_sitemaps: int = 0
    total_urls: int = 0
    discovery_methods: Dict[str, int] = Field(default_factory=dict)
    sitemap_types: Dict[str, int] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    progress: Optional[float] = None
    sitemaps: List[Dict[str, Any]] = Field(default_factory=list)
    sitemaps_url: Optional[str] = None


class SitemapBatchStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    batch_id: str
    status: str  # "pending", "in_progress", "completed", "failed", "partial"
    total_domains: int
    completed_domains: int = 0
    failed_domains: int = 0
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    job_statuses: Dict[str, str] = Field(default_factory=dict)


class SitemapFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    domain_id: str
    url: str
    sitemap_type: str
    discovery_method: str
    page_count: Optional[int] = None
    size_bytes: Optional[int] = None
    has_lastmod: Optional[bool] = None
    has_priority: Optional[bool] = None
    has_changefreq: Optional[bool] = None
    last_modified: Optional[datetime] = None
    created_at: datetime
    status: str


class SitemapUrlsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    urls: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    has_more: bool
