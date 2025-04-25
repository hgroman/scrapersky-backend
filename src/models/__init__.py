"""
SQLAlchemy Models Package

This package contains all the SQLAlchemy ORM models for the application.
It provides a centralized location for database schema definitions and
relationships between models.
"""

# Import all models for easy access
# Enum exports for easier import in other modules
from enum import Enum, auto

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
from .api_models import (
    BatchRequest,
    BatchResponse,
    BatchStatusResponse,
    SitemapScrapingRequest,
    SitemapScrapingResponse,
)
from .base import Base, BaseModel, model_to_dict
from .batch_job import BatchJob
from .domain import Domain
from .job import Job
from .page import Page
from .contact import Contact
from .place import Place
from .place_search import PlaceSearch

# Import sitemap models
from .sitemap import SitemapFile, SitemapUrl
from .tenant import Tenant
from .user import User


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
    """Common status values for tasks and jobs."""
    PENDING = "Queued"
    RUNNING = "InProgress"
    COMPLETE = "Completed"
    FAILED = "Error"
    CANCELLED = "Cancelled"

# Export all models
__all__ = [
    # Base models
    "Base", "BaseModel", "model_to_dict",

    # Core models
    "Job", "Domain", "BatchJob", "User", "Place", "PlaceSearch", "Tenant",
    "Page", "Contact",

    # Sitemap models
    "SitemapFile", "SitemapUrl",

    # RBAC models - commented out as part of RBAC removal
    # These exports are preserved for future reintegration but commented out
    # to prevent their use in the current codebase
    # "Role", "Permission", "UserRole", "FeatureFlag", "TenantFeature", "SidebarFeature",

    # Enums
    "SitemapType", "DiscoveryMethod", "TaskStatus"
]
