"""
Tenant Model - Simplified

This model is maintained for backward compatibility with the database schema
but has no functional purpose in the application.
"""

import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

# Default tenant ID used throughout the application
DEFAULT_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

class Tenant(Base):
    """
    Tenant model maintained for compatibility with the database schema.
    No functional purpose in the application.
    """
    __tablename__ = 'tenants'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # All relationships have been removed as part of tenant isolation removal
    # The model is kept only for database compatibility