"""
SQLAlchemy Models Package

This package contains all the SQLAlchemy ORM models for the application.
It provides a centralized location for database schema definitions and
relationships between models.
"""

# Import all models for easy access
# Enum exports for easier import in other modules
# import enum # Removed unused import
# import uuid # Removed unused import
from enum import Enum  # Kept Enum, removed auto

# RBAC models - imports commented out as part of RBAC removal
# These model definitions are preserved in their respective files for future reintegration
# but are not actively imported to prevent their use in the current codebase
#
# from .rbac import Role, Permission, RolePermission, UserRole, FeatureFlag, TenantFeature
# from .sidebar import SidebarFeature
#
# Note: While the relationship definitions with these models remain in other models,
# they will not be active since the models themselves are not imported
# Import custom data types and base classes
# Restore imports needed by other modules
from .api_models import (
    BatchRequest,
    BatchResponse,
    BatchStatusResponse,
    SitemapScrapingRequest,
    SitemapScrapingResponse,
)
from .base import Base, BaseModel, model_to_dict
from .batch_job import BatchJob
from .contact import Contact
from .domain import Domain
from .job import Job
from .page import Page
from .place import Place
from .place_search import PlaceSearch

# Import sitemap models
from .sitemap import SitemapFile, SitemapUrl
from .tenant import Tenant


class SitemapType(str, Enum):
    """Types of sitemaps that can be processed."""

    INDEX = "index"
    STANDARD = "standard"
    IMAGE = "image"
    VIDEO = "video"
    NEWS = "news"


class DiscoveryMethod(str, Enum):
    """How a sitemap was discovered."""

    ROBOTS_TXT = "robots_txt"
    COMMON_PATH = "common_path"
    SITEMAP_INDEX = "sitemap_index"
    HTML_LINK = "html_link"
    MANUAL = "manual"


class TaskStatus(str, Enum):
    """Status values mapped to task_status in database (MUST MATCH DB DEFINITION)"""

    # Values MUST match database exactly: {Queued,InProgress,Completed,Error,ManualReview,Cancelled,Paused,Processing,Complete}
    PENDING = "Queued"
    RUNNING = "InProgress"
    COMPLETE = "Completed"
    FAILED = "Error"
    MANUAL_REVIEW = "ManualReview"  # MISSING: Was causing runtime errors
    CANCELLED = "Cancelled"
    PAUSED = "Paused"              # MISSING: Was causing runtime errors
    PROCESSING = "Processing"       # MISSING: Was causing runtime errors
    COMPLETE_ALT = "Complete"      # MISSING: Alternative Complete status


# Export all models
__all__ = [
    # Base models
    "Base",
    "BaseModel",
    "model_to_dict",
    # API models (add restored ones here)
    "BatchRequest",
    "BatchResponse",
    "BatchStatusResponse",
    "SitemapScrapingRequest",
    "SitemapScrapingResponse",
    # Core models
    "Job",
    "Domain",
    "BatchJob",
    "Place",
    "PlaceSearch",
    "Tenant",
    "Page",
    "Contact",
    # Sitemap models
    "SitemapFile",
    "SitemapUrl",
    # RBAC models - commented out as part of RBAC removal
    # These exports are preserved for future reintegration but commented out
    # to prevent their use in the current codebase
    # "Role", "Permission", "UserRole", "FeatureFlag",
    # "TenantFeature", "SidebarFeature",
    # Enums
    "SitemapType",
    "DiscoveryMethod",
    "TaskStatus",
]
