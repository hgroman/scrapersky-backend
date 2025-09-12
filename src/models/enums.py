"""
Centralized Enum Definitions

This module contains all enum definitions used in the application.
All enums MUST be defined here to prevent duplication and inconsistency.
"""

from enum import Enum


class ContactEmailTypeEnum(str, Enum):
    """Status values mapped to contact_email_type_enum in database"""

    SERVICE = "SERVICE"
    CORPORATE = "CORPORATE"
    FREE = "FREE"
    UNKNOWN = "UNKNOWN"


class ContactCurationStatus(str, Enum):
    """Status values for contact curation workflow"""

    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"


class ContactProcessingStatus(str, Enum):
    """Status values for contact processing workflow"""

    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"


class DomainStatusEnum(str, Enum):
    """Status values for domain processing workflow"""

    pending = "pending"  # Ready for metadata extraction
    processing = "processing"  # Metadata extraction in progress
    completed = "completed"  # Metadata extraction successful
    error = "error"  # Metadata extraction failed


class HubSpotSyncStatus(str, Enum):
    """Status values for HubSpot sync workflow"""

    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"


class HubSpotProcessingStatus(str, Enum):
    """Status values for HubSpot processing workflow"""

    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"


class PageCurationStatus(str, Enum):
    """Status values for page curation workflow"""

    New = "New"
    Selected = "Selected"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"


class PageProcessingStatus(str, Enum):
    """Status values for page processing workflow"""

    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Filtered = "Filtered"


class PlaceStatusEnum(str, Enum):
    """Status values for places"""

    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"  # Note: database uses space, not underscore
    Archived = "Archived"


class GcpApiDeepScanStatusEnum(str, Enum):
    """Status values for GCP API deep scan"""

    Pending = "Pending"
    Running = "Running"
    Complete = "Complete"
    Failed = "Failed"


class SitemapAnalysisStatusEnum(Enum):
    """Status values for sitemap analysis background process (MUST MATCH DOMAIN.PY)"""

    pending = "pending"  # Initial state when domain is created/reset
    queued = "queued"  # Scheduler picked it up, waiting for adapter
    processing = "processing"  # Adapter sent to API
    submitted = "submitted"  # API accepted (202)
    failed = "failed"  # Adapter or API call failed


class SitemapCurationStatusEnum(str, Enum):
    """Status values for sitemap curation workflow"""

    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"  # Match API potentially needed space
    Archived = "Archived"
    Completed = "Completed"


class SitemapFileStatusEnum(str, Enum):
    """Status values for sitemap files"""

    New = "New"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"


class SitemapImportCurationStatusEnum(str, Enum):
    """Status values for sitemap import curation workflow"""

    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"


class SitemapImportProcessStatusEnum(str, Enum):
    """Status values for sitemap import process workflow"""

    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"


class DomainExtractionStatusEnum(str, Enum):
    """Status values for domain extraction workflow"""

    Pending = "pending"
    Queued = "queued"
    Processing = "processing"
    Submitted = "submitted"
    Failed = "failed"


class PageTypeEnum(str, Enum):
    """Page types identified by Honeybee categorization system"""
    
    # Contact categories (current)
    CONTACT_ROOT = "contact_root"
    CAREER_CONTACT = "career_contact"
    
    # Business categories (extensible)
    ABOUT_ROOT = "about_root"
    SERVICES_ROOT = "services_root"
    MENU_ROOT = "menu_root"  # For restaurants/hospitality
    PRICING_ROOT = "pricing_root"
    TEAM_ROOT = "team_root"
    
    # Legal/compliance
    LEGAL_ROOT = "legal_root"
    
    # Technical indicators  
    WP_PROSPECT = "wp_prospect"
    
    # Default
    UNKNOWN = "unknown"
