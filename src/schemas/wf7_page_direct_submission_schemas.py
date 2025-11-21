"""
Schema definitions for direct page submission endpoint (WO-009).

This module provides Pydantic schemas for the /api/v3/pages/direct-submit endpoint,
enabling users to bypass WF1-WF5 and submit page URLs directly for WF7 processing.
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from uuid import UUID


class DirectPageSubmissionRequest(BaseModel):
    """Request schema for direct page submission."""

    urls: list[HttpUrl] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of page URLs to submit (1-100 URLs)",
    )
    auto_queue: bool = Field(
        default=False,
        description=(
            "If True, sets page_curation_status='Selected' and "
            "page_processing_status='Queued' for immediate WF7 processing. "
            "If False, sets page_curation_status='New' and "
            "page_processing_status=NULL for manual curation."
        ),
    )
    priority_level: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Priority level (1=highest, 10=lowest)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://example.com/contact",
                    "https://example.com/about",
                ],
                "auto_queue": True,
                "priority_level": 3,
            }
        }


class DirectPageSubmissionResponse(BaseModel):
    """Response schema for direct page submission."""

    submitted_count: int
    page_ids: list[UUID]
    auto_queued: bool

    class Config:
        json_schema_extra = {
            "example": {
                "submitted_count": 2,
                "page_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001",
                ],
                "auto_queued": True,
            }
        }
