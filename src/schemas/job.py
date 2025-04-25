"""
Pydantic models related to Job status and submission.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Assuming TaskStatus enum lives in src.models
# If not, adjust the import path
# from ..models import TaskStatus


class JobSubmissionResponse(BaseModel):
    """Response model for successful job submission.

    Contains the UUID of the created job.
    """
    job_id: uuid.UUID


# --- Moved from src/models/api_models.py --- #
class JobStatusResponse(BaseModel):
    """Response model for job status endpoint.

    Reflects the state of a Job record.
    """
    # Use UUID for job_id, as it's the primary identifier exposed
    job_id: uuid.UUID = Field(..., description="Job ID (UUID)")
    # Use the actual Enum type if possible for better validation/schema
    # status: TaskStatus = Field(..., description="Job status")
    # If using string representation:
    status: str = Field(..., description="Job status (pending, running, complete, failed)")
    progress: float = Field(default=0.0, description="Progress indicator (0.0 to 1.0)")
    # Optional fields from the Job model
    domain_id: Optional[uuid.UUID] = Field(None, description="Associated Domain ID")
    created_by: Optional[uuid.UUID] = Field(None, description="User who created the job")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Job result data if available")
    error: Optional[str] = Field(None, description="Error message if job failed")
    job_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional job metadata")
    created_at: Optional[datetime] = Field(None, description="When the job was created")
    updated_at: Optional[datetime] = Field(None, description="When the job was last updated")

    class Config:
        from_attributes = True # Enable ORM mode
# --- End Moved Section --- #
