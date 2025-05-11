# Example File: src/schemas/{workflow_name}_schemas.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

# Import the CURATION and PROCESSING enums from their domain-based location
from src.models.{source_table_name} import {WorkflowNameTitleCase}CurationStatus, {WorkflowNameTitleCase}ProcessingStatus

# Convention: {WorkflowNameTitleCase}SelectionSchema
# Example Name (for page_curation): PageCurationSelectionSchema
class {WorkflowNameTitleCase}SelectionSchema(BaseModel):
    ids: List[UUID] = Field(..., min_length=1, description="List of one or more {SourceTableTitleCase} UUIDs to select.")
    status: {WorkflowNameTitleCase}CurationStatus = Field(..., description="The target curation status for the selected items.")

    model_config = ConfigDict(from_attributes=True)

# Convention: {WorkflowNameTitleCase}DetailSchema
# Example Name (for page_curation): PageCurationDetailSchema
class {WorkflowNameTitleCase}DetailSchema(BaseModel):
    id: UUID
    {workflow_name}_curation_status: {WorkflowNameTitleCase}CurationStatus
    {workflow_name}_processing_status: Optional[{WorkflowNameTitleCase}ProcessingStatus]
