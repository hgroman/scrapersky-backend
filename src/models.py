from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

# Chat Models
class ChatRequest(BaseModel):
    message: str
    
class ChatResponse(BaseModel):
    response: str
    model_used: str

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
    QUEUED = 'queued'
    IN_PROGRESS = 'in_progress'
    COMPLETE = 'complete'
    ERROR = 'error'
    MANUAL_REVIEW = 'manual_review'
    CANCELLED = 'cancelled'
    PAUSED = 'paused'

class SiteMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    # Core Identification
    url: HttpUrl
    tenant_id: str = Field(default='550e8400-e29b-41d4-a716-446655440000')
    lead_source: Optional[str] = None

    # Basic Info
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    status: str = 'active'

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
    tenant_id: str = Field(default='550e8400-e29b-41d4-a716-446655440000')
    max_pages: int = Field(default=1000)

class SitemapScrapingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: str
    status_url: str

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