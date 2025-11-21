from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.models.wf3_local_business import DomainExtractionStatusEnum
from src.models.wf1_place_staging import PlaceStatusEnum


# Define a Pydantic model that mirrors the LocalBusiness SQLAlchemy model
# This ensures API responses have a defined schema.
# Include fields needed by the frontend grid.
class LocalBusinessRecord(BaseModel):
    id: UUID
    business_name: Optional[str] = None
    full_address: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    status: Optional[PlaceStatusEnum] = None  # Use the DB enum here
    domain_extraction_status: Optional[DomainExtractionStatusEnum] = None
    created_at: datetime
    updated_at: datetime
    tenant_id: UUID

    class Config:
        from_attributes = True  # Enable ORM mode for conversion (Updated from orm_mode)
        use_enum_values = True  # Ensure enum values are used in response


# Response model for paginated results
class PaginatedLocalBusinessResponse(BaseModel):
    items: List[LocalBusinessRecord]
    total: int
    page: int
    size: int
    pages: int
