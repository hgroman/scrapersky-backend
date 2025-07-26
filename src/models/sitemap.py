"""
Sitemap SQLAlchemy Models

This module defines the database models for sitemap files and URLs,
providing an ORM interface for interacting with the sitemap_files and sitemap_urls tables.
"""

import enum
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, model_to_dict

logger = logging.getLogger(__name__)


# Enum definitions to match database
class SitemapFileStatusEnum(enum.Enum):
    """Status values for sitemap_file_status_enum in database"""

    Pending = "Pending"
    Processing = "Processing"
    Completed = "Completed"
    Error = "Error"


# Rename Enum related to Sitemap Curation status
class SitemapImportCurationStatusEnum(enum.Enum):
    """Status values for Sitemap Import Curation Status"""

    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"
    Archived = "Archived"


# Rename Enum related to Sitemap Processing status
class SitemapImportProcessStatusEnum(enum.Enum):
    """Status values mapped to sitemapimportprocessingstatus in database (MUST MATCH DB DEFINITION)"""

    # Setting values to match actual DB schema
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"  # Match DB: "Complete" not "Completed"
    Error = "Error"
    # Note: "Submitted" removed - not present in actual DB enum


class SitemapFile(Base, BaseModel):
    """
    SitemapFile model representing sitemap XML files discovered and processed by the system.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        domain_id: Domain ID this sitemap belongs to
        url: URL of the sitemap file
        sitemap_type: Type of sitemap (INDEX, STANDARD, IMAGE, VIDEO, NEWS)
        discovery_method: How this sitemap was discovered (ROBOTS_TXT, COMMON_PATH, etc.)
        page_count: Number of pages in the sitemap
        size_bytes: Size of the sitemap file in bytes
        has_lastmod: Whether the sitemap contains lastmod information
        has_priority: Whether the sitemap contains priority information
        has_changefreq: Whether the sitemap contains changefreq information
        last_modified: When the sitemap was last modified according to HTTP headers
        url_count: Number of URLs in the sitemap
        tenant_id: The tenant this sitemap belongs to (for multi-tenancy)
        created_by: The user who created this sitemap record
        job_id: Associated job ID if created by a background job
        status: Processing status of the sitemap
        tags: JSON field for additional tags and categorization
        notes: Optional text notes about this sitemap
    """

    __tablename__ = "sitemap_files"

    # Core fields (id comes from BaseModel)
    domain_id = Column(PGUUID, ForeignKey("domains.id"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    sitemap_type = Column(Text, nullable=False)
    discovery_method = Column(Text, nullable=True)

    # Metadata fields
    page_count = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    is_gzipped = Column(Boolean, nullable=True)
    has_lastmod = Column(Boolean, nullable=True, default=False)
    has_priority = Column(Boolean, nullable=True, default=False)
    has_changefreq = Column(Boolean, nullable=True, default=False)
    last_modified = Column(DateTime(timezone=True), nullable=True)
    url_count = Column(Integer, nullable=True, default=0)
    priority = Column(Integer, nullable=True, default=5)
    generator = Column(Text, nullable=True)
    lead_source = Column(Text, nullable=True)

    # Security and ownership
    tenant_id = Column(
        PGUUID,
        nullable=True,
        index=True,
        default="550e8400-e29b-41d4-a716-446655440000",
    )
    created_by = Column(PGUUID, nullable=True)
    updated_by = Column(PGUUID, nullable=True)
    user_id = Column(PGUUID, nullable=True)
    user_name = Column(Text, nullable=True)

    # Process tracking
    job_id = Column(PGUUID, nullable=True, index=True)
    status = Column(
        SQLAlchemyEnum(
            SitemapFileStatusEnum, name="sitemap_file_status_enum", create_type=False
        ),
        nullable=False,
        default=SitemapFileStatusEnum.Pending,
        index=True,
    )
    is_active = Column(Boolean, nullable=True, default=True)
    process_after = Column(DateTime(timezone=True), nullable=True)
    last_processed_at = Column(DateTime(timezone=True), nullable=True)

    # Renamed section comment: Sitemap Import columns (previously Deep Scrape)
    # Note: deep_scrape_curation_status column potentially needs DB migration/rename later
    deep_scrape_curation_status = Column(
        SQLAlchemyEnum(
            SitemapImportCurationStatusEnum,  # Use renamed Enum
            name="sitemap_import_curation_status",  # Fix DB name
            create_type=False,
        ),
        nullable=True,
        default=SitemapImportCurationStatusEnum.New,  # Use renamed Enum
        index=True,
    )
    sitemap_import_error = Column(Text, name="sitemap_import_error", nullable=True)
    sitemap_import_status = Column(
        SQLAlchemyEnum(
            SitemapImportProcessStatusEnum,  # Use renamed Enum
            name="sitemap_import_status_enum",  # Fix DB enum type name
            create_type=False,
        ),
        nullable=True,
        index=True,
        name="sitemap_import_status",
    )

    # Additional metadata
    tags = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    urls = relationship(
        "SitemapUrl", back_populates="sitemap", cascade="all, delete-orphan"
    )
    domain = relationship("Domain", back_populates="sitemap_files")

    def to_dict(self) -> Dict[str, Any]:
        """Convert sitemap file to dictionary with proper serialization."""
        return model_to_dict(self)

    @classmethod
    async def create_new(
        cls,
        session,
        domain_id: str,
        url: str,
        sitemap_type: Optional[str] = None,
        discovery_method: Optional[str] = None,
        tenant_id: Optional[str] = None,
        created_by: Optional[str] = None,
        job_id: Optional[str] = None,
        **kwargs,
    ) -> "SitemapFile":
        """
        Create a new sitemap file record.

        Args:
            session: SQLAlchemy session
            domain_id: Domain ID this sitemap belongs to
            url: URL of the sitemap file
            sitemap_type: Type of sitemap (INDEX, STANDARD, etc)
            discovery_method: How this sitemap was discovered
            tenant_id: Tenant ID for security
            created_by: User ID of creator
            job_id: Associated job ID if any
            **kwargs: Additional fields to set on the sitemap file

        Returns:
            New SitemapFile instance
        """
        try:
            # Convert string UUIDs to UUID objects if provided
            tenant_id_obj = None
            if tenant_id:
                try:
                    tenant_id_obj = uuid.UUID(tenant_id)
                except (ValueError, TypeError) as err:
                    logger.warning(f"Invalid UUID format for tenant_id: {tenant_id}")
                    raise ValueError(f"Invalid UUID format for tenant_id: {tenant_id}") from err

            created_by_obj = None
            if created_by:
                try:
                    created_by_obj = uuid.UUID(created_by)
                except (ValueError, TypeError) as err:
                    logger.warning(f"Invalid UUID format for created_by: {created_by}")
                    raise ValueError(f"Invalid UUID format for created_by: {created_by}") from err

            # Create the sitemap file
            sitemap_file = cls(
                domain_id=domain_id,
                url=url,
                sitemap_type=sitemap_type,
                discovery_method=discovery_method,
                tenant_id=tenant_id_obj,
                created_by=created_by_obj,
                job_id=job_id,
                status="pending",
                **kwargs,
            )

            session.add(sitemap_file)
            return sitemap_file

        except Exception as e:
            logger.error(f"Error creating sitemap file: {str(e)}")
            raise

    @classmethod
    async def get_by_id(
        cls, session, sitemap_id: Union[str, uuid.UUID]
    ) -> Optional["SitemapFile"]:
        """
        Get a sitemap file by its ID.

        Args:
            session: SQLAlchemy session
            sitemap_id: Sitemap ID (UUID or string)

        Returns:
            SitemapFile instance or None if not found
        """
        from sqlalchemy import select

        # Convert string UUID to UUID object if needed
        if isinstance(sitemap_id, str):
            try:
                sitemap_id = uuid.UUID(sitemap_id)
            except ValueError:
                logger.warning(f"Invalid UUID format for sitemap_id: {sitemap_id}")
                return None

        query = select(cls).where(cls.id == sitemap_id)

        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_domain_id(cls, session, domain_id: str) -> List["SitemapFile"]:
        """
        Get all sitemap files for a domain.

        Args:
            session: SQLAlchemy session
            domain_id: Domain ID to get sitemaps for

        Returns:
            List of SitemapFile instances
        """
        from sqlalchemy import select

        query = (
            select(cls)
            .where(cls.domain_id == domain_id)
            .order_by(cls.created_at.desc())
        )

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_job_id(cls, session, job_id: str) -> List["SitemapFile"]:
        """
        Get all sitemap files for a specific job.

        Args:
            session: SQLAlchemy session
            job_id: Job ID to get sitemaps for

        Returns:
            List of SitemapFile instances
        """
        from sqlalchemy import select

        query = select(cls).where(cls.job_id == job_id).order_by(cls.created_at.desc())

        result = await session.execute(query)
        return result.scalars().all()


class SitemapUrl(Base, BaseModel):
    """
    SitemapUrl model representing URLs found in sitemaps.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        sitemap_id: Foreign key to the parent sitemap file
        url: The URL found in the sitemap
        lastmod: Last modified date from sitemap (if available)
        changefreq: Change frequency from sitemap (if available)
        priority: Priority value from sitemap (if available)
        tenant_id: The tenant this URL belongs to (for multi-tenancy)
        created_by: The user who created this record
        tags: JSON field for additional tags and categorization
        notes: Optional text notes about this URL
    """

    __tablename__ = "sitemap_urls"

    # Core fields (id comes from BaseModel)
    sitemap_id = Column(
        PGUUID,
        ForeignKey("sitemap_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url = Column(Text, nullable=False)

    # Metadata fields from sitemap
    lastmod = Column(DateTime(timezone=True), nullable=True)
    changefreq = Column(String, nullable=True)
    priority = Column(Float, nullable=True)

    # Security and ownership
    tenant_id = Column(
        PGUUID,
        nullable=True,
        index=True,
        default="550e8400-e29b-41d4-a716-446655440000",
    )
    created_by = Column(PGUUID, nullable=True)
    updated_by = Column(PGUUID, nullable=True)

    # Additional metadata
    tags = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    sitemap = relationship("SitemapFile", back_populates="urls")

    def to_dict(self) -> Dict[str, Any]:
        """Convert sitemap URL to dictionary with proper serialization."""
        return model_to_dict(self)

    @classmethod
    async def create_new(
        cls,
        session,
        sitemap_id: Union[str, uuid.UUID],
        url: str,
        tenant_id: str,
        lastmod: Optional[datetime] = None,
        changefreq: Optional[str] = None,
        priority: Optional[float] = None,
        created_by: Optional[str] = None,
        **kwargs,
    ) -> "SitemapUrl":
        """
        Create a new sitemap URL record.

        Args:
            session: SQLAlchemy session
            sitemap_id: ID of the parent sitemap
            url: The URL from the sitemap
            tenant_id: Tenant ID for security
            lastmod: Last modified date if available
            changefreq: Change frequency if available
            priority: Priority if available
            created_by: User ID of creator
            **kwargs: Additional fields to set

        Returns:
            New SitemapUrl instance
        """
        try:
            # Convert string UUIDs to UUID objects if needed
            sitemap_id_obj = sitemap_id
            if isinstance(sitemap_id, str):
                try:
                    sitemap_id_obj = uuid.UUID(sitemap_id)
                except ValueError:
                    logger.warning(f"Invalid UUID format for sitemap_id: {sitemap_id}")
                    raise ValueError(
                        f"Invalid UUID format for sitemap_id: {sitemap_id}"
                    )

            tenant_id_obj = None
            if tenant_id:
                try:
                    tenant_id_obj = uuid.UUID(tenant_id)
                except (ValueError, TypeError) as err:
                    logger.warning(f"Invalid UUID format for tenant_id: {tenant_id}")
                    raise ValueError(f"Invalid UUID format for tenant_id: {tenant_id}") from err

            created_by_obj = None
            if created_by:
                try:
                    created_by_obj = uuid.UUID(created_by)
                except (ValueError, TypeError) as err:
                    logger.warning(f"Invalid UUID format for created_by: {created_by}")
                    raise ValueError(f"Invalid UUID format for created_by: {created_by}") from err

            # Create the sitemap URL
            sitemap_url = cls(
                sitemap_id=sitemap_id_obj,
                url=url,
                lastmod=lastmod,
                changefreq=changefreq,
                priority=priority,
                tenant_id=tenant_id_obj,
                created_by=created_by_obj,
                **kwargs,
            )

            session.add(sitemap_url)
            return sitemap_url

        except Exception as e:
            logger.error(f"Error creating sitemap URL: {str(e)}")
            raise

    @classmethod
    async def get_by_sitemap_id(
        cls,
        session,
        sitemap_id: Union[str, uuid.UUID],
        tenant_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List["SitemapUrl"]:
        """
        Get URLs for a specific sitemap with pagination.

        Args:
            session: SQLAlchemy session
            sitemap_id: Sitemap ID to get URLs for
            tenant_id: Optional tenant ID for security filtering
            limit: Maximum number of URLs to return
            offset: Starting offset for pagination

        Returns:
            List of SitemapUrl instances
        """
        from sqlalchemy import select

        # Convert string UUID to UUID object if needed
        sitemap_id_obj = sitemap_id
        if isinstance(sitemap_id, str):
            try:
                sitemap_id_obj = uuid.UUID(sitemap_id)
            except ValueError:
                logger.warning(f"Invalid UUID format for sitemap_id: {sitemap_id}")
                return []

        query = select(cls).where(cls.sitemap_id == sitemap_id_obj)

        if tenant_id:
            try:
                tenant_id_obj = uuid.UUID(tenant_id)
                query = query.where(cls.tenant_id == tenant_id_obj)
            except ValueError:
                logger.warning(f"Invalid UUID format for tenant_id: {tenant_id}")
                return []

        query = query.order_by(cls.created_at).limit(limit).offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def count_by_sitemap_id(
        cls, session, sitemap_id: Union[str, uuid.UUID], tenant_id: Optional[str] = None
    ) -> int:
        """
        Count URLs for a specific sitemap.

        Args:
            session: SQLAlchemy session
            sitemap_id: Sitemap ID to count URLs for
            tenant_id: Optional tenant ID for security filtering

        Returns:
            Count of URLs
        """
        from sqlalchemy import func, select

        # Convert string UUID to UUID object if needed
        sitemap_id_obj = sitemap_id
        if isinstance(sitemap_id, str):
            try:
                sitemap_id_obj = uuid.UUID(sitemap_id)
            except ValueError:
                logger.warning(f"Invalid UUID format for sitemap_id: {sitemap_id}")
                return 0

        query = (
            select(func.count())
            .select_from(cls)
            .where(cls.sitemap_id == sitemap_id_obj)
        )

        if tenant_id:
            try:
                tenant_id_obj = uuid.UUID(tenant_id)
                query = query.where(cls.tenant_id == tenant_id_obj)
            except ValueError:
                logger.warning(f"Invalid UUID format for tenant_id: {tenant_id}")
                return 0

        result = await session.execute(query)
        return result.scalar() or 0
