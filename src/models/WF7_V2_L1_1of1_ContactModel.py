from sqlalchemy import Column, String, ForeignKey, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModel
from .enums import (
    ContactCurationStatus,
    ContactEmailTypeEnum,
    ContactProcessingStatus,
    HubSpotProcessingStatus,
    HubSpotSyncStatus,
)


class Contact(Base, BaseModel):
    __tablename__ = "contacts"

    # id, created_at, updated_at inherited from BaseModel
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    page_id = Column(UUID(as_uuid=True), ForeignKey("pages.id"), nullable=False, index=True)

    email = Column(String, nullable=False, index=True)
    email_type = Column(Enum(ContactEmailTypeEnum, create_type=False, native_enum=True), nullable=True)
    has_gmail = Column(Boolean, default=False, nullable=True)
    context = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    source_job_id = Column(UUID(as_uuid=True), nullable=True)

    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    contact_curation_status = Column(
        Enum(ContactCurationStatus, create_type=False, native_enum=True),
        nullable=False,
        default=ContactCurationStatus.New,
        index=True,
    )
    contact_processing_status = Column(
        Enum(ContactProcessingStatus, create_type=False, native_enum=True),
        nullable=True,
        index=True,
    )
    contact_processing_error = Column(Text, nullable=True)

    hubspot_sync_status = Column(
        Enum(HubSpotSyncStatus, create_type=False, native_enum=True),
        nullable=False,
        default=HubSpotSyncStatus.New,
        index=True,
    )
    hubspot_processing_status = Column(
        Enum(HubSpotProcessingStatus, create_type=False, native_enum=True),
        nullable=True,
        index=True,
    )
    hubspot_processing_error = Column(Text, nullable=True)

    page = relationship("Page", back_populates="contacts")
