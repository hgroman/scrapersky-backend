"""
SQLAlchemy Model for the 'contacts' table.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


# Define Python Enum corresponding to DB Enum
class ContactEmailTypeEnum(str, enum.Enum):
    SERVICE = "service"
    CORPORATE = "corporate"
    FREE = "free"
    UNKNOWN = "unknown"


class Contact(Base, BaseModel):
    __tablename__ = "contacts"

    # Define columns based on the agreed schema
    id: Column[uuid.UUID] = Column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    domain_id: Column[uuid.UUID] = Column(
        PGUUID(as_uuid=True),
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_id: Column[uuid.UUID] = Column(
        PGUUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Column[str] = Column(Text, nullable=False, index=True)
    email_type: Column[Optional[ContactEmailTypeEnum]] = Column(
        SQLAlchemyEnum(
            ContactEmailTypeEnum, name="contact_email_type_enum", create_type=False
        ),
        nullable=True,
    )
    has_gmail: Column[Optional[bool]] = Column(Boolean, default=False, nullable=True)
    context: Column[Optional[str]] = Column(Text, nullable=True)
    source_url: Column[Optional[str]] = Column(Text, nullable=True)
    source_job_id: Column[Optional[uuid.UUID]] = Column(
        PGUUID(as_uuid=True), ForeignKey("jobs.job_id"), nullable=True
    )

    # Define relationships
    domain = relationship("Domain", back_populates="contacts")
    page = relationship("Page", back_populates="contacts")
    # Assuming Job model might have a collection of contacts found by it
    # If not, this can be a one-way relationship
    job = relationship(
        "Job"
    )  # Consider adding back_populates="contacts" to Job model if needed

    # Define table arguments for constraints
    __table_args__ = (
        UniqueConstraint("domain_id", "email", name="uq_contact_domain_email"),
        # Note: Indices from SQL DDL are typically handled by index=True on columns
    )
