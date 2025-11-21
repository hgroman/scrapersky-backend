import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_auth import get_current_user  # Import user dependency
from src.models import TaskStatus  # Import TaskStatus
from src.models.job import Job  # Import Job model
from src.models.tenant import DEFAULT_TENANT_ID  # <-- Add this import

# Import Schemas
from src.schemas.wf7_email_scan_schemas import EmailScanRequest  # Correct path
from src.schemas.job import JobStatusResponse, JobSubmissionResponse  # Correct path

# from ..db.sb_connection import db  # Supabase connection from sb_connection.py
from src.session.async_session import get_session_dependency  # Correct function name

from ..models import Domain  # Import models
from ..tasks.email_scraper import scan_website_for_emails

router = APIRouter()
logger = logging.getLogger(__name__)

# Define dependencies outside function signatures to satisfy B008
SessionDep = Depends(get_session_dependency)
CurrentUserDep = Depends(get_current_user)


class EmailScanningResponse(BaseModel):
    domain_id: uuid.UUID
    domain: str
    total_pages: int = 100  # Keep placeholder logic for now
    pages_scanned: int = 0
    contacts_found: int = 0
    scan_timestamp: str
    status: str = "pending"  # Default status
    progress: float = 0.0  # Add progress
    error: Optional[str] = None  # Add error field
    result: Optional[Dict[str, Any]] = None  # Add result field


# Temporary in-memory storage for scan statuses (MVP solution)
# scan_jobs: Dict[uuid.UUID, EmailScanningResponse] = {}


@router.get("/scan/status/{job_id}", response_model=JobStatusResponse)
async def get_scan_status_api(
    job_id: uuid.UUID,  # Use UUID type hint for path parameter
    session: AsyncSession = SessionDep,
    current_user: Dict[str, Any] = CurrentUserDep,  # Auth usually needed here too
):
    """Retrieve the status and results of a specific email scan job by its UUID."""
    # Add authentication check if needed based on requirements
    # user_id = current_user.get("id")
    # if not user_id: ... raise HTTPException ...

    try:
        # Fetch the job using the new get_by_job_id method
        job = await Job.get_by_job_id(session, job_id)

        if not job:
            logger.warning(f"Job with ID {job_id} not found.")
            # No original exception here, so 'from None' is appropriate for B904
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scan job not found"
            ) from None

        # Optional: Add authorization check - e.g., does this user own this job?
        # if job.created_by != user_id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this job")

        # Return the job details using the Pydantic model
        # The model should handle converting Job model fields (like status string)
        # to the appropriate response schema types (like TaskStatus enum member).
        # Ensure JobStatusResponse uses `from_attributes = True` in its Config.
        return JobStatusResponse.model_validate(
            job
        )  # Use model_validate for Pydantic v2

    except HTTPException:
        raise  # Re-raise HTTPExceptions directly
    except Exception as e:
        logger.error(f"Error retrieving status for job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving job status.",
        ) from e  # Add 'from e' for B904


# --- Remove or Comment Out Old Endpoints ---

# @router.get("/api/v3/email-scanner/domains", ...)
# async def get_available_domains(...): ... # Keep if needed, otherwise remove

# @router.post("/api/v3/email-scanner/scan/{domain_id}", ...)
# async def scan_domain(...): ... # Remove old endpoint

# @router.get("/api/v3/email-scanner/scan/{domain_id}/status", ...)
# async def get_scan_status(...): ... # Remove old endpoint

# --- End Removal ---
