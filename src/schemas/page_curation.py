from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

# Import the standardized Python Enum from the models directory
from src.models.page import PageCurationStatus


class PageCurationUpdateRequest(BaseModel):
    page_ids: List[UUID] = Field(
        ..., min_length=1, description="List of one or more Page UUIDs to update."
    )
    curation_status: PageCurationStatus = Field(
        ..., description="The target curation status to apply to the selected pages."
    )


class PageCurationUpdateResponse(BaseModel):
    message: str = Field(
        ..., description="A summary message indicating the result of the operation."
    )
    updated_count: int = Field(
        ..., description="The number of pages successfully updated."
    )
    # Optionally, include a list of IDs that were updated or failed,
    # if detailed feedback is needed.
    # updated_ids: List[UUID] = Field(default_factory=list)
    # failed_ids: List[UUID] = Field(default_factory=list)
