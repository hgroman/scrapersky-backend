from sqlalchemy import Column, String, ForeignKey, Text, Boolean, Enum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSONB
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
        Enum('New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='contact_curation_status'),
        nullable=False,
        default='New',
        index=True,
    )
    contact_processing_status = Column(
        Enum('Queued', 'Processing', 'Complete', 'Error', name='contact_processing_status'),
        nullable=True,
        index=True,
    )
    contact_processing_error = Column(Text, nullable=True)

    hubspot_sync_status = Column(
        Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='hubspot_sync_status'),
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
    hubspot_contact_id = Column(String, nullable=True, index=True)

    # Brevo sync status fields
    brevo_sync_status = Column(
        Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='crm_sync_status'),
        nullable=False,
        default='New',
        index=True,
    )
    brevo_processing_status = Column(
        Enum('Queued', 'Processing', 'Complete', 'Error', name='crm_processing_status'),
        nullable=True,
        index=True,
    )
    brevo_processing_error = Column(Text, nullable=True)
    brevo_contact_id = Column(String, nullable=True, index=True)

    # Mautic sync status fields
    mautic_sync_status = Column(
        Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='crm_sync_status'),
        nullable=False,
        default='New',
        index=True,
    )
    mautic_processing_status = Column(
        Enum('Queued', 'Processing', 'Complete', 'Error', name='crm_processing_status'),
        nullable=True,
        index=True,
    )
    mautic_processing_error = Column(Text, nullable=True)
    mautic_contact_id = Column(String, nullable=True, index=True)

    # n8n sync status fields
    n8n_sync_status = Column(
        Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='crm_sync_status'),
        nullable=False,
        default='New',
        index=True,
    )
    n8n_processing_status = Column(
        Enum('Queued', 'Processing', 'Complete', 'Error', name='crm_processing_status'),
        nullable=True,
        index=True,
    )
    n8n_processing_error = Column(Text, nullable=True)
    n8n_workflow_id = Column(String, nullable=True, index=True)

    # Retry tracking fields (shared across all CRM syncs)
    retry_count = Column(Integer, nullable=False, default=0)
    last_retry_at = Column(TIMESTAMP(timezone=True), nullable=True)
    next_retry_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_failed_crm = Column(String, nullable=True)

    # DeBounce Email Validation (WO-017)
    # Reuses existing crm_sync_status and crm_processing_status ENUMs for consistency
    debounce_validation_status = Column(
        Enum('New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='crm_sync_status'),
        nullable=True,
        index=True,
    )
    debounce_processing_status = Column(
        Enum('Queued', 'Processing', 'Complete', 'Error', name='crm_processing_status'),
        nullable=True,
        index=True,
    )
    debounce_result = Column(String, nullable=True)  # valid/invalid/catch-all/unknown/disposable
    debounce_score = Column(Integer, nullable=True)  # 0-100 confidence score
    debounce_reason = Column(String(500), nullable=True)  # Explanation if invalid
    debounce_suggestion = Column(String, nullable=True)  # Did you mean suggestion
    debounce_processing_error = Column(Text, nullable=True)
    debounce_validated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # n8n Enrichment Fields (WO-021)
    # Enrichment status tracking
    enrichment_status = Column(String(20), nullable=True)  # pending/complete/partial/failed
    enrichment_started_at = Column(TIMESTAMP(timezone=True), nullable=True)
    enrichment_completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    enrichment_error = Column(Text, nullable=True)
    last_enrichment_id = Column(String(255), nullable=True)  # For idempotency

    # Enriched data fields (JSONB for flexible schema)
    enriched_phone = Column(String(50), nullable=True)
    enriched_address = Column(JSONB, nullable=True)  # {street, city, state, zip, country}
    enriched_social_profiles = Column(JSONB, nullable=True)  # {linkedin, twitter, facebook, etc}
    enriched_company = Column(JSONB, nullable=True)  # {name, website, industry, size}
    enriched_additional_emails = Column(JSONB, nullable=True)  # Array of additional emails
    enrichment_confidence_score = Column(Integer, nullable=True)  # 0-100 quality score
    enrichment_sources = Column(JSONB, nullable=True)  # Array of data sources used

    # Enrichment metadata
    enrichment_duration_seconds = Column(Float, nullable=True)
    enrichment_api_calls = Column(Integer, nullable=True)
    enrichment_cost_estimate = Column(Float, nullable=True)

    page = relationship("Page", back_populates="contacts")
