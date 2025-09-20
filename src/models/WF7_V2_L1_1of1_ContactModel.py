from sqlalchemy import Column, String, ForeignKey, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class Contact(Base, BaseModel):
    __tablename__ = "contacts"

    # id, created_at, updated_at inherited from BaseModel
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    page_id = Column(UUID(as_uuid=True), ForeignKey("pages.id"), nullable=False, index=True)

    email = Column(String, nullable=False, index=True)
    email_type = Column(Enum('SERVICE', 'CORPORATE', 'FREE', 'UNKNOWN', name='contact_email_type_enum'), nullable=True)
    has_gmail = Column(Boolean, default=False, nullable=True)
    context = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    source_job_id = Column(UUID(as_uuid=True), nullable=True)

    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    contact_curation_status = Column(
        Enum('New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='contactcurationstatus'),
        nullable=False,
        default='New',
        index=True,
    )
    contact_processing_status = Column(
        Enum('Queued', 'Processing', 'Complete', 'Error', name='contactprocessingstatus'),
        nullable=True,
        index=True,
    )
    contact_processing_error = Column(Text, nullable=True)

    hubspot_sync_status = Column(
        Enum('New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='hubspot_sync_status'),
        nullable=False,
        default='New',
        index=True,
    )
    hubspot_processing_status = Column(
        Enum('Queued', 'Processing', 'Complete', 'Error', name='hubspot_sync_processing_status'),
        nullable=True,
        index=True,
    )
    hubspot_processing_error = Column(Text, nullable=True)

    page = relationship("Page", back_populates="contacts")
