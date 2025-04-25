"""
Domain SQLAlchemy Model

Represents website domains being processed by ScraperSky.
"""
import enum
import logging
import uuid
from typing import Any, Dict, List, Optional, Union, cast

from sqlalchemy import (
    ARRAY,
    JSON,
    UUID,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, BaseModel, model_to_dict
from .tenant import DEFAULT_TENANT_ID

logger = logging.getLogger(__name__)

# Python Enum for USER curation status
class SitemapCurationStatusEnum(enum.Enum):
    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit" # Match API potentially needed space
    Archived = "Archived"

# Define the enum for the sitemap analysis background process status
class SitemapAnalysisStatusEnum(enum.Enum):
    Queued = "Queued"
    Processing = "Processing"
    Completed = "Completed"  # Using Completed instead of submitted as per standardization
    Error = "Error"  # Using Error instead of failed as per standardization

class Domain(Base, BaseModel):
    """
    Domain model representing websites being processed.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        domain: The website domain/URL being processed
        tenant_id: The tenant ID field (always using default tenant ID)
        created_by: The user who created this domain record
        status: Current processing status (pending, running, complete, failed)
        domain_metadata: JSON field for additional data and results
        notes: Optional text notes about this domain

        # Metadata fields from extraction
        title: Website title
        description: Website description
        favicon_url: URL of the website favicon
        logo_url: URL of the website logo
        language: Detected language

        # Technology detection
        is_wordpress: Whether the site is WordPress
        wordpress_version: WordPress version if detected
        has_elementor: Whether Elementor is used
        tech_stack: JSON field with detected technologies

        # Contact information
        email_addresses: Array of detected email addresses
        phone_numbers: Array of detected phone numbers

        # Social media
        facebook_url: Facebook URL if detected
        twitter_url: Twitter URL if detected
        linkedin_url: LinkedIn URL if detected
        instagram_url: Instagram URL if detected
        youtube_url: YouTube URL if detected

        # Tracking and analytics
        last_scan: When the domain was last scanned
        sitemap_urls: Number of URLs in sitemap
        total_sitemaps: Number of sitemaps found

        # User-Triggered Sitemap Analysis
        sitemap_analysis_status: Status of the sitemap analysis
        sitemap_analysis_error: Error message for failed analysis

        # Sitemap Curation and Analysis
        sitemap_curation_status: Curation status of the sitemap
    """
    __tablename__ = "domains"

    # Core fields
    domain = Column(String, nullable=False, index=True, unique=True)
    tenant_id = Column(PGUUID, ForeignKey("tenants.id"), nullable=False, index=True, default=lambda: uuid.UUID(DEFAULT_TENANT_ID))

    # Status and metadata
    created_by = Column(PGUUID)
    status = Column(String, nullable=False, default="active")
    domain_metadata = Column(JSONB, name="meta_json")
    notes = Column(Text)

    # Metadata fields
    title = Column(String)
    description = Column(Text)
    favicon_url = Column(String)
    logo_url = Column(String)
    language = Column(String)

    # Technology detection
    is_wordpress = Column(Boolean, default=False)
    wordpress_version = Column(String)
    has_elementor = Column(Boolean, default=False)
    tech_stack = Column(JSONB)

    # Contact information
    email_addresses = Column(ARRAY(String), default=[])
    phone_numbers = Column(ARRAY(String), default=[])

    # Social media
    facebook_url = Column(String)
    twitter_url = Column(String)
    linkedin_url = Column(String)
    instagram_url = Column(String)
    youtube_url = Column(String)

    # Tracking and analytics
    last_scan = Column(DateTime, default=func.now())
    sitemap_urls = Column(Integer, default=0)
    total_sitemaps = Column(Integer, default=0)

    # Batch processing reference
    batch_id = Column(PGUUID, ForeignKey("batch_jobs.batch_id", ondelete="SET NULL"), index=True, nullable=True)

    # Foreign key back to the originating local business (if created via that workflow)
    local_business_id = Column(PGUUID, ForeignKey("local_businesses.id", ondelete="SET NULL"), index=True, nullable=True)

    # --- New fields for User-Triggered Sitemap Analysis --- #
    sitemap_analysis_status = Column(SQLAlchemyEnum(SitemapAnalysisStatusEnum, name="SitemapAnalysisStatusEnum", create_type=False), nullable=True, index=True)
    sitemap_analysis_error = Column(Text, nullable=True)
    # ------------------------------------------------------- #

    # --- New fields for Sitemap Curation and Analysis --- #
    sitemap_curation_status = Column(SQLAlchemyEnum(SitemapCurationStatusEnum, name="SitemapCurationStatusEnum", create_type=False), nullable=True, default=SitemapCurationStatusEnum.New, index=True)
    # ---------------------------------------------------- #

    # Relationships
    jobs = relationship("Job", back_populates="domain", lazy="selectin")
    batch = relationship("BatchJob", back_populates="domains")
    tenant = relationship("Tenant")
    sitemap_files = relationship("SitemapFile", back_populates="domain", cascade="all, delete-orphan")
    pages = relationship("Page", back_populates="domain", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="domain", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert domain to dictionary with proper serialization.

        Returns:
            Dictionary representation of the domain with serialized values
        """
        result = model_to_dict(self)

        # Add convenience derived fields
        domain_value = getattr(self, 'domain', None)
        if domain_value:
            result["domain_url"] = f"https://{domain_value}"
        else:
            result["domain_url"] = None

        # Format timestamp for easier client-side handling
        last_scan = getattr(self, 'last_scan', None)
        if last_scan:
            result["last_scan_iso"] = last_scan.isoformat()

        # Check for successful scans
        domain_metadata = getattr(self, 'domain_metadata', None)
        result["has_metadata"] = bool(domain_metadata)

        return result

    def update_batch_info(self, batch_id: str) -> None:
        """
        Update domain's batch information.

        Args:
            batch_id: Batch ID to associate with this domain
        """
        # Use setattr to avoid SQLAlchemy Column access issues
        setattr(self, 'batch_id', batch_id)

    def mark_scanned(self) -> None:
        """
        Mark domain as successfully scanned.
        """
        setattr(self, 'status', 'scanned')
        setattr(self, 'last_scan', func.now())

    def mark_failed(self, error_message: Optional[str] = None) -> None:
        """
        Mark domain scan as failed with optional error message.

        Args:
            error_message: Optional error message explaining failure
        """
        setattr(self, 'status', 'failed')
        setattr(self, 'last_scan', func.now())

        # Store error in metadata if provided
        if error_message and hasattr(self, 'domain_metadata'):
            metadata = getattr(self, 'domain_metadata', {}) or {}
            if not isinstance(metadata, dict):
                metadata = {}
            metadata['error'] = error_message
            setattr(self, 'domain_metadata', metadata)

    @classmethod
    async def create_from_metadata(cls, session, domain: str,
                                  metadata: Dict[str, Any], created_by: Optional[str] = None,
                                  batch_id: Optional[str] = None) -> "Domain":
        """
        Create a domain record from metadata dictionary.

        This standardizes domain creation from metadata extraction results,
        ensuring consistent handling in both single and batch processing.

        Args:
            session: SQLAlchemy session
            domain: Domain name
            metadata: Extracted metadata dictionary
            created_by: User ID who created this record (string UUID)
            batch_id: Optional batch ID if part of batch processing

        Returns:
            New Domain instance
        """
        # No tenant filtering as per architectural mandate
        # We still need to set tenant_id in the model as it's a non-nullable field
        # but we no longer filter queries by tenant_id
        from .tenant import DEFAULT_TENANT_ID
        tenant_id_uuid = uuid.UUID(DEFAULT_TENANT_ID)

        # Convert created_by to UUID if provided
        created_by_uuid = None
        if created_by:
            try:
                created_by_uuid = uuid.UUID(created_by)
            except (ValueError, TypeError):
                logger.warning(f"Invalid UUID format for created_by: {created_by}, using None")
                # Leave as None if invalid

        # Extract contact info and social links from nested structure
        contact_info = metadata.get("contact_info", {})
        social_links = metadata.get("social_links", {})

        # Create domain object with all available metadata
        domain_obj = cls(
            domain=domain,
            tenant_id=tenant_id_uuid,
            created_by=created_by_uuid,
            status="active",
            domain_metadata=metadata,

            # Basic metadata
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            favicon_url=metadata.get("favicon_url"),
            logo_url=metadata.get("logo_url"),
            language=metadata.get("language"),

            # Technology
            is_wordpress=metadata.get("is_wordpress", False),
            wordpress_version=metadata.get("wordpress_version"),
            has_elementor=metadata.get("has_elementor", False),
            tech_stack=metadata.get("tech_stack", {}),

            # Contact info - use empty lists as defaults to avoid None
            email_addresses=contact_info.get("email", []) or [],
            phone_numbers=contact_info.get("phone", []) or [],

            # Social media
            facebook_url=social_links.get("facebook"),
            twitter_url=social_links.get("twitter"),
            linkedin_url=social_links.get("linkedin"),
            instagram_url=social_links.get("instagram"),
            youtube_url=social_links.get("youtube"),

            # Sitemap data
            sitemap_urls=metadata.get("total_urls", 0),
            total_sitemaps=metadata.get("total_sitemaps", 0),

            # Batch reference
            batch_id=batch_id,

            # Update timestamp
            last_scan=func.now()
        )

        # Save to database
        session.add(domain_obj)

        return domain_obj

    @classmethod
    async def update_from_metadata(cls, session, domain_obj: "Domain",
                                  metadata: Dict[str, Any]) -> "Domain":
        """
        Update a domain record from metadata dictionary.

        Args:
            session: SQLAlchemy session
            domain_obj: Existing Domain object
            metadata: New metadata dictionary

        Returns:
            Updated Domain instance
        """
        # Extract contact info and social links from nested structure
        contact_info = metadata.get("contact_info", {})
        social_links = metadata.get("social_links", {})

        # Update fields - use setattr for safe attribute setting
        setattr(domain_obj, 'domain_metadata', metadata)
        setattr(domain_obj, 'title', metadata.get("title", domain_obj.title))
        setattr(domain_obj, 'description', metadata.get("description", domain_obj.description))
        setattr(domain_obj, 'favicon_url', metadata.get("favicon_url", domain_obj.favicon_url))
        setattr(domain_obj, 'logo_url', metadata.get("logo_url", domain_obj.logo_url))
        setattr(domain_obj, 'language', metadata.get("language", domain_obj.language))

        setattr(domain_obj, 'is_wordpress', metadata.get("is_wordpress", domain_obj.is_wordpress))
        setattr(domain_obj, 'wordpress_version', metadata.get("wordpress_version", domain_obj.wordpress_version))
        setattr(domain_obj, 'has_elementor', metadata.get("has_elementor", domain_obj.has_elementor))
        setattr(domain_obj, 'tech_stack', metadata.get("tech_stack", domain_obj.tech_stack))

        # Use empty lists as defaults to avoid None values
        setattr(domain_obj, 'email_addresses', contact_info.get("email", domain_obj.email_addresses) or [])
        setattr(domain_obj, 'phone_numbers', contact_info.get("phone", domain_obj.phone_numbers) or [])

        setattr(domain_obj, 'facebook_url', social_links.get("facebook", domain_obj.facebook_url))
        setattr(domain_obj, 'twitter_url', social_links.get("twitter", domain_obj.twitter_url))
        setattr(domain_obj, 'linkedin_url', social_links.get("linkedin", domain_obj.linkedin_url))
        setattr(domain_obj, 'instagram_url', social_links.get("instagram", domain_obj.instagram_url))
        setattr(domain_obj, 'youtube_url', social_links.get("youtube", domain_obj.youtube_url))

        setattr(domain_obj, 'sitemap_urls', metadata.get("total_urls", domain_obj.sitemap_urls))
        setattr(domain_obj, 'total_sitemaps', metadata.get("total_sitemaps", domain_obj.total_sitemaps))
        setattr(domain_obj, 'last_scan', func.now())
        setattr(domain_obj, 'status', 'scanned')  # Update status to show successful scan

        # Add to session
        session.add(domain_obj)

        return domain_obj

    @classmethod
    async def get_by_id(cls, session, domain_id: Union[str, uuid.UUID]) -> Optional["Domain"]:
        """
        Get domain by ID.

        Args:
            session: SQLAlchemy session
            domain_id: UUID of the domain to retrieve (string or UUID)

        Returns:
            Domain instance or None if not found
        """
        # Convert string to UUID if needed
        domain_id_uuid = None
        if isinstance(domain_id, str):
            try:
                domain_id_uuid = uuid.UUID(domain_id)
            except ValueError:
                logger.warning(f"Invalid UUID format for domain_id: {domain_id}")
                return None
        else:
            domain_id_uuid = domain_id

        return await session.get(cls, domain_id_uuid)

    @classmethod
    async def get_by_domain_name(cls, session, domain_name: str) -> Optional["Domain"]:
        """
        Get domain by name without tenant filtering.

        Args:
            session: SQLAlchemy session
            domain_name: Domain name to look up

        Returns:
            Domain instance or None if not found
        """
        # Import here to avoid circular imports
        from sqlalchemy import select

        # Normalize domain name
        domain_name = domain_name.lower().strip()

        # Build query without tenant filtering
        query = select(cls).where(cls.domain == domain_name)

        # Execute query
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_batch_id(cls, session, batch_id: str) -> List["Domain"]:
        """
        Get all domains that belong to a specific batch without tenant filtering.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to look up

        Returns:
            List of Domain instances
        """
        from sqlalchemy import select

        query = select(cls).where(cls.batch_id == batch_id)

        result = await session.execute(query)
        return result.scalars().all()
