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
