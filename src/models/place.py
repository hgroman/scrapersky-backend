"""
SQLAlchemy model for places from the Google Places API.

This module defines the database model for the places_staging table.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from .base import Base
from .tenant import DEFAULT_TENANT_ID


# Define the enum for the ORIGINAL user-facing place status
# Values MUST match the database enum values exactly (case-sensitive)
class PlaceStatusEnum(enum.Enum):
    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"
    Archived = "Archived"


# --- Define the NEW enum specifically for deep scan status --- #
# Values MUST match the database enum labels exactly (case-sensitive)
class DeepScanStatusEnum(enum.Enum):
    Queued = "Queued"  # Changed from "queued"
    Processing = "Processing"  # Changed from "processing"
    Completed = "Completed"  # Changed from "complete"
    Error = "Error"  # Changed from "failed"


# ------------------------------------------------------------- #


class Place(Base):
    """
    SQLAlchemy model for places_staging table.

    This table stores place data from Google Places API searches.
    """

    __tablename__ = "places_staging"

    id = Column(Integer, primary_key=True, autoincrement=True)
    place_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    formatted_address = Column(String(512))
    business_type = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    vicinity = Column(String(512))
    rating = Column(Float)
    user_ratings_total = Column(Integer)
    price_level = Column(Integer)
    # Use the extended enum, assuming native DB enum type exists (Reverting to standard)
    # Ensure the default matches the new enum value
    status = Column(
        Enum(
            PlaceStatusEnum,
            name="place_status_enum",
            create_type=False,
            native_enum=True,
        ),
        default=PlaceStatusEnum.New,
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        UUID(as_uuid=True), nullable=False, index=True, default=DEFAULT_TENANT_ID
    )
    created_by = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    user_name = Column(String(255))
    search_job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    search_query = Column(String(255))
    search_location = Column(String(255))
    raw_data = Column(JSONB)
    search_time = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    priority = Column(Integer, default=0)
    tags = Column(ARRAY(String))
    revisit_date = Column(DateTime)
    processed = Column(Boolean, default=False)
    processed_time = Column(DateTime)
    updated_by = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow)
    # New field to store deep scan errors
    deep_scan_error = Column(Text, nullable=True)

    # --- Add the NEW column for deep scan status --- #
    deep_scan_status = Column(
        Enum(
            DeepScanStatusEnum,
            name="deep_scan_status_enum",
            create_type=False,
            native_enum=True,
        ),
        nullable=True,  # Allow null for places not involved in deep scan
        index=True,  # Index for efficient querying by scheduler
    )
    # ------------------------------------------------- #

    def __repr__(self):
        return f"<Place(id={self.id}, name={self.name}, place_id={self.place_id})>"
