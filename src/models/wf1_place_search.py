"""
SQLAlchemy model for place searches.

This module defines the database model for the place_searches table.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .tenant import DEFAULT_TENANT_ID


class PlaceSearch(Base):
    """
    SQLAlchemy model for place_searches table.

    This table stores search metadata from Google Places API queries.
    """

    __tablename__ = "place_searches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), nullable=False, index=True, default=DEFAULT_TENANT_ID
    )
    user_id = Column(UUID(as_uuid=True))
    location = Column(String(255), nullable=False)
    business_type = Column(String(100), nullable=False)
    params = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PlaceSearch(id={self.id}, location={self.location}, business_type={self.business_type})>"
