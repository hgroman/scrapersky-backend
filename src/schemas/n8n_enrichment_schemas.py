"""
WO-021: n8n Enrichment Return Data Schemas

Pydantic schemas for receiving enriched contact data from n8n workflows.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class AddressData(BaseModel):
    """Contact address information"""

    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None


class SocialProfiles(BaseModel):
    """Social media profile URLs"""

    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    github: Optional[str] = None


class CompanyData(BaseModel):
    """Company information"""

    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None


class EnrichedData(BaseModel):
    """Enriched contact data from n8n workflow"""

    phone: Optional[str] = None
    address: Optional[AddressData] = None
    social_profiles: Optional[SocialProfiles] = None
    company: Optional[CompanyData] = None
    additional_emails: Optional[List[str]] = None
    confidence_score: Optional[int] = Field(None, ge=0, le=100, description="Quality score 0-100")
    sources: Optional[List[str]] = None

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('confidence_score must be between 0 and 100')
        return v


class EnrichmentMetadata(BaseModel):
    """Metadata about the enrichment process"""

    enrichment_duration_seconds: Optional[float] = None
    api_calls_made: Optional[int] = None
    cost_estimate: Optional[float] = None


class EnrichmentCompleteRequest(BaseModel):
    """
    Request payload when n8n POSTs enrichment results back to ScraperSky.

    Example:
    {
        "contact_id": "123e4567-e89b-12d3-a456-426614174000",
        "enrichment_id": "enrich-run-12345",
        "status": "complete",
        "timestamp": "2025-11-19T10:30:00Z",
        "enriched_data": {...},
        "metadata": {...}
    }
    """

    contact_id: str = Field(..., description="UUID of contact to update")
    enrichment_id: str = Field(..., description="Unique ID for this enrichment run (idempotency)")
    status: str = Field(..., description="Enrichment status: complete, partial, or failed")
    timestamp: datetime = Field(..., description="When enrichment completed")
    enriched_data: Optional[EnrichedData] = None
    metadata: Optional[EnrichmentMetadata] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ['complete', 'partial', 'failed']
        if v not in allowed_statuses:
            raise ValueError(f'status must be one of: {", ".join(allowed_statuses)}')
        return v


class EnrichmentCompleteResponse(BaseModel):
    """
    Response sent back to n8n after processing enrichment data.

    Example:
    {
        "success": true,
        "contact_id": "123e4567-e89b-12d3-a456-426614174000",
        "enrichment_id": "enrich-run-12345",
        "message": "Enrichment data saved successfully",
        "updated_fields": ["enriched_phone", "enriched_address"]
    }
    """

    success: bool
    contact_id: str
    enrichment_id: str
    message: str
    updated_fields: Optional[List[str]] = None


class EnrichmentErrorResponse(BaseModel):
    """Error response when enrichment processing fails"""

    success: bool = False
    error: str
    contact_id: Optional[str] = None
    enrichment_id: Optional[str] = None
