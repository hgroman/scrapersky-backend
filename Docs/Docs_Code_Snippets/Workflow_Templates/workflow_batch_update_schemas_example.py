# Example File: src/schemas/{workflow_name}.py
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
# Import the CURATION enum from its domain-based location
from src.models.{source_table_name} import {WorkflowNameTitleCase}CurationStatus

# Convention: {WorkflowNameTitleCase}BatchStatusUpdateRequest
# Example Name (for page_curation): PageCurationBatchStatusUpdateRequest
class {WorkflowNameTitleCase}BatchStatusUpdateRequest(BaseModel):
    ids: List[UUID] = Field(..., min_length=1, description="List of one or more {SourceTableTitleCase} UUIDs to update.")
    status: {WorkflowNameTitleCase}CurationStatus = Field(..., description="The target curation status for the selected items.")

# Convention: {WorkflowNameTitleCase}BatchStatusUpdateResponse
# Example Name (for page_curation): PageCurationBatchStatusUpdateResponse
class {WorkflowNameTitleCase}BatchStatusUpdateResponse(BaseModel):
    message: str
    updated_ids: List[UUID]
    # count: int # Or updated_count, ensure consistency with API implementation
