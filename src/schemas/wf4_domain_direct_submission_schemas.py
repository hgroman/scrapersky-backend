"""
Pydantic schemas for direct domain submission (WO-010).

Allows users to submit domain URLs directly, bypassing WF1-WF2 (Google Maps workflows).
"""

from pydantic import BaseModel, Field, validator
from typing import List
from uuid import UUID
import re
from urllib.parse import urlparse


class DirectDomainSubmissionRequest(BaseModel):
    """Request schema for direct domain submission."""

    domains: List[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="List of domain names or URLs to submit",
    )

    auto_queue: bool = Field(
        default=False,
        description="If True, auto-queue for WF4 sitemap discovery",
    )

    @validator("domains", each_item=True)
    def validate_domain_format(cls, domain_str: str) -> str:
        """Validate and normalize domain."""
        # Remove protocol if present
        if "://" in domain_str:
            parsed = urlparse(domain_str)
            domain_str = parsed.netloc or parsed.path

        # Remove www. prefix
        domain_str = domain_str.replace("www.", "")

        # Remove trailing slashes and paths
        domain_str = domain_str.split("/")[0].rstrip("/")

        # Validate format
        domain_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
        if not re.match(domain_pattern, domain_str):
            raise ValueError(f"Invalid domain format: {domain_str}")

        return domain_str.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "domains": [
                    "example.com",
                    "https://www.another-example.org",
                    "third-example.net",
                ],
                "auto_queue": True,
            }
        }


class DirectDomainSubmissionResponse(BaseModel):
    """Response schema for direct domain submission."""

    submitted_count: int
    domain_ids: List[UUID]
    auto_queued: bool
    normalized_domains: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "submitted_count": 3,
                "domain_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001",
                    "123e4567-e89b-12d3-a456-426614174002",
                ],
                "auto_queued": True,
                "normalized_domains": [
                    "example.com",
                    "another-example.org",
                    "third-example.net",
                ],
            }
        }
