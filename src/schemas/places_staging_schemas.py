from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.api_models import PlaceStagingRecord, PlaceStagingStatusEnum


# Add a new response model for paginated results
class PaginatedPlaceStagingResponse(BaseModel):
    items: List[PlaceStagingRecord]
    total: int
    page: int
    size: int
    pages: int


# Model for the direct queueing endpoint
class QueueDeepScanRequest(BaseModel):
    # Prioritize place_ids as the primary input
    place_ids: List[str] = Field(
        ..., description="List of Google Place IDs to queue for deep scan."
    )
    # Keep staging_ids as optional secondary identifier if needed, or remove if place_ids are sufficient
    # staging_ids: List[int] = Field(default_factory=list, description="List of internal integer IDs from places_staging to queue.")


# Model for the unified batch/single status update endpoint
class PlaceBatchStatusUpdateRequest(BaseModel):
    place_ids: List[str] = Field(
        ..., min_length=1, description="List of one or more Google Place IDs to update."
    )
    status: PlaceStagingStatusEnum = Field(
        ..., description="The new main status to set."
    )
    error_message: Optional[str] = Field(
        None, description="Optional error message to set when status is Error."
    )


class PlaceStagingFilteredUpdateRequest(BaseModel):
    """
    Request schema for filter-based batch place staging updates.
    Enables 'Select All' functionality without explicit place ID lists.
    """
    status: PlaceStagingStatusEnum = Field(
        ..., description="The new status to set for all matching places."
    )
    status_filter: Optional[PlaceStagingStatusEnum] = Field(
        None, description="Filter by current status (e.g., NEW, Selected, Maybe)"
    )
    discovery_job_id: Optional[UUID] = Field(
        None, description="Filter by specific discovery job ID"
    )


class PlaceStagingBatchUpdateResponse(BaseModel):
    """Response schema for place staging batch update operations."""
    updated_count: int = Field(..., description="Number of places updated")
    queued_count: int = Field(..., description="Number of places queued for deep scan")
