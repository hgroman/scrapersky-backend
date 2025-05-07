"""
SQLAlchemy Model for the 'pages' table.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


# --- Page Curation Workflow Enums ---
class PageCurationStatus(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"


class PageProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"


class Page(Base, BaseModel):
    __tablename__ = "pages"

    # From simple_inspect output:
    # id uuid NO gen_random_uuid() ✓
    # tenant_id uuid NO  -- NOTE: Assuming tenant isolation removed,
    #                      but copying schema for now
    # domain_id uuid NO → domains.id
    # url text NO
    # title text YES
    # description text YES
    # h1 text YES
    # canonical_url text YES
    # meta_robots text YES
    # has_schema_markup boolean YES false
    # schema_types ARRAY YES
    # has_contact_form boolean YES false
    # has_comments boolean YES false
    # word_count integer YES
    # inbound_links ARRAY YES
    # outbound_links ARRAY YES
    # last_modified timestamp with time zone YES
    # last_scan timestamp with time zone YES
    # page_type text YES
    # lead_source text YES
    # additional_json jsonb YES '{}'::jsonb
    # created_at timestamp with time zone YES now() -- Handled by BaseModel
    # updated_at timestamp with time zone YES now() -- Handled by BaseModel

    id: Column[uuid.UUID] = Column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Column[uuid.UUID] = Column(PGUUID(as_uuid=True), nullable=False)
    domain_id: Column[uuid.UUID] = Column(
        PGUUID(as_uuid=True), ForeignKey("domains.id"), nullable=False
    )
    url: Column[str] = Column(Text, nullable=False)
    title: Column[Optional[str]] = Column(Text, nullable=True)  # type: ignore
    description: Column[Optional[str]] = Column(Text, nullable=True)  # type: ignore
    h1: Column[Optional[str]] = Column(Text, nullable=True)  # type: ignore
    canonical_url: Column[Optional[str]] = Column(Text, nullable=True)  # type: ignore
    meta_robots: Column[Optional[str]] = Column(Text, nullable=True)  # type: ignore
    has_schema_markup: Column[Optional[bool]] = Column(  # type: ignore
        Boolean, default=False, nullable=True
    )
    schema_types: Column[Optional[List[Optional[str]]]] = Column(  # type: ignore
        ARRAY(String), nullable=True
    )
    has_contact_form: Column[Optional[bool]] = Column(  # type: ignore
        Boolean, default=False, nullable=True
    )
    has_comments: Column[Optional[bool]] = Column(Boolean, default=False, nullable=True)  # type: ignore
    word_count: Column[Optional[int]] = Column(Integer, nullable=True)  # type: ignore
    inbound_links: Column[Optional[List[Optional[str]]]] = Column(  # type: ignore
        ARRAY(String), nullable=True
    )
    outbound_links: Column[Optional[List[Optional[str]]]] = Column(  # type: ignore
        ARRAY(String), nullable=True
    )
    last_modified: Column[Optional[datetime]] = Column(  # type: ignore
        DateTime(timezone=True), nullable=True
    )
    last_scan: Column[Optional[datetime]] = Column(  # type: ignore
        DateTime(timezone=True), nullable=True
    )
    page_type: Column[Optional[str]] = Column(Text, nullable=True)  # type: ignore
    lead_source: Column[Optional[str]] = Column(Text, nullable=True)  # type: ignore
    additional_json: Column[Optional[dict]] = Column(JSONB, default=dict, nullable=True)  # type: ignore

    # Foreign key to track the source sitemap file (optional)
    sitemap_file_id: Column[Optional[uuid.UUID]] = Column(  # type: ignore
        PGUUID(as_uuid=True), ForeignKey("sitemap_files.id"), nullable=True, index=True
    )

    # --- Page Curation Workflow Columns ---
    page_curation_status: Column[PageCurationStatus] = Column(  # type: ignore
        PgEnum(PageCurationStatus, name="pagecurationstatus", create_type=False),
        nullable=False,
        default=PageCurationStatus.New,
        index=True,
    )
    page_processing_status: Column[Optional[PageProcessingStatus]] = Column(  # type: ignore
        PgEnum(PageProcessingStatus, name="pageprocessingstatus", create_type=False),
        nullable=True,
        index=True,
    )
    page_processing_error: Column[Optional[str]] = Column(Text, nullable=True)  # type: ignore

    # Relationships
    domain = relationship("Domain", back_populates="pages")
    contacts = relationship(
        "Contact", back_populates="page", cascade="all, delete-orphan"
    )
