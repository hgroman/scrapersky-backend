# WF8 – The Connector
# Purpose: Contact validation, enrichment, and delivery to external systems
# NEVER put page-scraping logic here – that belongs in WF7

"""
Contact Validation Schemas (WO-018)

Pydantic models for DeBounce email validation API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============================================================================
# Request Schemas
# ============================================================================


class ValidateContactsRequest(BaseModel):
    """Request to validate selected contacts."""

    contact_ids: List[str] = Field(
        ...,
        description="List of contact UUIDs to validate",
        min_length=1,
        max_length=100,
        examples=[["8ef2449f-d3eb-4831-b85e-a385332b6475"]],
    )


class ContactFilters(BaseModel):
    """Filters for contact selection."""

    curation_status: Optional[str] = Field(
        None,
        description="Filter by curation status (e.g., 'Skipped', 'Selected')",
        examples=["Skipped"],
    )
    validation_status: Optional[str] = Field(
        None,
        description="Filter by validation status: 'valid', 'invalid', 'disposable', 'pending', 'not_validated'",
        examples=["not_validated"],
    )
    search_email: Optional[str] = Field(
        None, description="Search by email address", examples=["test@example.com"]
    )
    search_name: Optional[str] = Field(
        None, description="Search by first or last name", examples=["John"]
    )
    domain_id: Optional[str] = Field(
        None, description="Filter by domain UUID", examples=None
    )
    page_id: Optional[str] = Field(None, description="Filter by page UUID", examples=None)


class ValidateAllContactsRequest(BaseModel):
    """Request to validate all contacts matching filters."""

    filters: ContactFilters = Field(
        ..., description="Filters to select contacts for validation"
    )
    max_contacts: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of contacts to queue (safety limit)",
        examples=[100],
    )


# ============================================================================
# Response Schemas
# ============================================================================


class ContactValidationDetail(BaseModel):
    """Detailed validation status for a single contact."""

    id: str = Field(..., description="Contact UUID")
    email: str = Field(..., description="Contact email address")
    status: str = Field(
        ...,
        description="Status: 'queued', 'already_processing', 'already_validated'",
    )


class ValidateContactsResponse(BaseModel):
    """Response from validating selected contacts."""

    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Human-readable message")
    queued_count: int = Field(..., description="Number of contacts queued for validation")
    already_processing: int = Field(
        default=0, description="Number of contacts already being processed"
    )
    already_validated: int = Field(
        default=0, description="Number of contacts already validated"
    )
    invalid_ids: List[str] = Field(
        default_factory=list, description="Contact IDs that were not found"
    )
    details: Optional[dict] = Field(
        None, description="Optional detailed breakdown of contacts"
    )


class ValidateAllContactsResponse(BaseModel):
    """Response from validating all filtered contacts."""

    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Human-readable message")
    queued_count: int = Field(..., description="Number of contacts queued for validation")
    already_processing: int = Field(
        default=0, description="Number of contacts already being processed"
    )
    already_validated: int = Field(
        default=0, description="Number of contacts already validated"
    )
    total_matched: int = Field(
        ..., description="Total number of contacts matching filters"
    )
    filters_applied: dict = Field(..., description="Filters that were applied")


class ContactValidationStatus(BaseModel):
    """Current validation status for a contact."""

    id: str = Field(..., description="Contact UUID")
    email: str = Field(..., description="Contact email address")
    validation_status: str = Field(
        ...,
        description="Validation status: 'Queued', 'Complete', 'Error'",
        examples=["Complete"],
    )
    processing_status: str = Field(
        ...,
        description="Processing status: 'Queued', 'Processing', 'Complete', 'Error'",
        examples=["Complete"],
    )
    result: Optional[str] = Field(
        None,
        description="Validation result: 'valid', 'invalid', 'disposable', 'catch-all', 'unknown'",
        examples=["valid"],
    )
    score: Optional[int] = Field(
        None, description="Validation confidence score (0-100)", examples=[100]
    )
    reason: Optional[str] = Field(
        None, description="Reason for validation result", examples=["Deliverable"]
    )
    suggestion: Optional[str] = Field(
        None, description="Suggested correction (did you mean...)", examples=[""]
    )
    validated_at: Optional[datetime] = Field(
        None, description="Timestamp when validation completed"
    )
    error: Optional[str] = Field(
        None, description="Error message if validation failed"
    )


class ValidationStatusResponse(BaseModel):
    """Response with validation status for multiple contacts."""

    success: bool = Field(..., description="Whether the operation succeeded")
    contacts: List[ContactValidationStatus] = Field(
        ..., description="Validation status for each contact"
    )


class ValidationBreakdown(BaseModel):
    """Breakdown of validation results."""

    total: int = Field(..., description="Total validated contacts")
    valid: int = Field(..., description="Number of valid emails")
    invalid: int = Field(..., description="Number of invalid emails")
    disposable: int = Field(..., description="Number of disposable emails")
    catch_all: int = Field(..., description="Number of catch-all emails")
    unknown: int = Field(..., description="Number of unknown status emails")


class ValidationSummary(BaseModel):
    """Aggregate validation statistics."""

    total_contacts: int = Field(..., description="Total number of contacts")
    validated: ValidationBreakdown = Field(
        ..., description="Breakdown of validated contacts"
    )
    not_validated: int = Field(..., description="Number of contacts not yet validated")
    pending_validation: int = Field(
        ..., description="Number of contacts pending validation (Queued/Processing)"
    )
    validation_rate: float = Field(
        ..., description="Percentage of contacts that have been validated"
    )
    valid_rate: float = Field(
        ..., description="Percentage of validated contacts that are valid"
    )
    last_updated: datetime = Field(..., description="Timestamp of last validation")


class ValidationSummaryResponse(BaseModel):
    """Response with validation summary statistics."""

    success: bool = Field(..., description="Whether the operation succeeded")
    summary: ValidationSummary = Field(..., description="Validation statistics")
    filters_applied: dict = Field(..., description="Filters that were applied")
