"""
SQLAlchemy Model for the 'pages' table.
"""

import uuid
from datetime import datetime
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class Page(Base, BaseModel):
    __tablename__ = "pages"

    # From simple_inspect output:
    # id uuid NO gen_random_uuid() ✓
    # tenant_id uuid NO  -- NOTE: Assuming tenant isolation removed, but copying schema for now
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
    tenant_id: Column[Optional[uuid.UUID]] = Column(
        PGUUID(as_uuid=True), nullable=False
    )  # TODO: Confirm if needed post-tenant removal
    domain_id: Column[Optional[uuid.UUID]] = Column(
        PGUUID(as_uuid=True), ForeignKey("domains.id"), nullable=False
    )
    url: Column[str] = Column(Text, nullable=False)
    title: Column[Optional[str]] = Column(Text, nullable=True)
    description: Column[Optional[str]] = Column(Text, nullable=True)
    h1: Column[Optional[str]] = Column(Text, nullable=True)
    canonical_url: Column[Optional[str]] = Column(Text, nullable=True)
    meta_robots: Column[Optional[str]] = Column(Text, nullable=True)
    has_schema_markup: Column[Optional[bool]] = Column(
        Boolean, default=False, nullable=True
    )
    schema_types: Column[Optional[List[Optional[str]]]] = Column(
        ARRAY(String), nullable=True
    )
    has_contact_form: Column[Optional[bool]] = Column(
        Boolean, default=False, nullable=True
    )
    has_comments: Column[Optional[bool]] = Column(Boolean, default=False, nullable=True)
    word_count: Column[Optional[int]] = Column(Integer, nullable=True)
    inbound_links: Column[Optional[List[Optional[str]]]] = Column(
        ARRAY(String), nullable=True
    )
    outbound_links: Column[Optional[List[Optional[str]]]] = Column(
        ARRAY(String), nullable=True
    )
    last_modified: Column[Optional[datetime]] = Column(
        DateTime(timezone=True), nullable=True
    )
    last_scan: Column[Optional[datetime]] = Column(
        DateTime(timezone=True), nullable=True
    )
    page_type: Column[Optional[str]] = Column(Text, nullable=True)
    lead_source: Column[Optional[str]] = Column(Text, nullable=True)
    additional_json: Column[Optional[dict]] = Column(JSONB, default=dict, nullable=True)

    # Relationships
    domain = relationship("Domain", back_populates="pages")
    contacts = relationship(
        "Contact", back_populates="page", cascade="all, delete-orphan"
    )
