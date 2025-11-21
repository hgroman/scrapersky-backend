"""
Schema definitions for direct sitemap submission endpoint (WO-011).

This module provides Pydantic schemas for the /api/v3/sitemaps/direct-submit endpoint,
enabling users to bypass WF1-WF4 and submit sitemap URLs directly for WF5 processing.
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional
from uuid import UUID
from urllib.parse import urlparse


class DirectSitemapSubmissionRequest(BaseModel):
    """Request schema for direct sitemap submission."""

    sitemap_urls: list[HttpUrl] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of sitemap URLs to submit (1-50 URLs)",
    )
    auto_import: bool = Field(
        default=False,
        description="If True, auto-queue for WF5 import",
    )
    domain_id: Optional[UUID] = Field(
        default=None,
        description="Optional domain to associate sitemaps with",
    )

    @field_validator("sitemap_urls")
    def validate_sitemap_urls(cls, urls):
        """Validate sitemap URL format."""
        for url in urls:
            url_str = str(url)
            parsed = urlparse(url_str)

            # Validate it looks like a sitemap
            if not (parsed.path.endswith(".xml") or "sitemap" in parsed.path.lower()):
                raise ValueError(f"URL must be a sitemap file (.xml): {url_str}")

        return urls

    class Config:
        json_schema_extra = {
            "example": {
                "sitemap_urls": [
                    "https://example.com/sitemap.xml",
                    "https://example.com/sitemap_index.xml",
                ],
                "auto_import": True,
                "domain_id": None,
            }
        }


class DirectSitemapSubmissionResponse(BaseModel):
    """Response schema for direct sitemap submission."""

    submitted_count: int
    sitemap_ids: list[UUID]
    auto_queued: bool

    class Config:
        json_schema_extra = {
            "example": {
                "submitted_count": 2,
                "sitemap_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001",
                ],
                "auto_queued": True,
            }
        }
