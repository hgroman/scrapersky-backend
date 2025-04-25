"""
Sidebar Model

This module defines SQLAlchemy ORM model for sidebar navigation features.

NOTE: Multi-tenant and RBAC functionality have been removed from the application.
This model is maintained for database compatibility only.
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .tenant import DEFAULT_TENANT_ID


class SidebarFeature(Base):
    """Sidebar feature model for UI navigation."""
    __tablename__ = 'sidebar_features'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_id = Column(UUID(as_uuid=True), ForeignKey('feature_flags.id', ondelete="CASCADE"), nullable=True)
    sidebar_name = Column(Text, nullable=False)
    url_path = Column(Text, nullable=False)
    icon = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    requires_permission = Column(Text, nullable=True)
    requires_feature = Column(UUID(as_uuid=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete="SET NULL"), nullable=True, default=DEFAULT_TENANT_ID)
    group_name = Column(Text, nullable=True)  # Added to support grouping sidebar items