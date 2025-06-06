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
from src.schemas.email_scan import EmailScanRequest  # Correct path
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


@router.post(
    "/scan/website",
    response_model=JobSubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def scan_website_for_emails_api(
    scan_request: EmailScanRequest,  # Use the new request schema
    background_tasks: BackgroundTasks,
    session: AsyncSession = SessionDep,
    current_user: Dict[str, Any] = CurrentUserDep,
):
    """
    Initiate an email scan for a given domain ID, creating a Job record.

    Checks for existing PENDING or RUNNING jobs for the same domain.
    If found, returns the existing job ID.
    Otherwise, creates a new job, queues the background task, and returns the new job ID.
    """
    domain_id = scan_request.domain_id
    user_id_str = current_user.get("id")  # Get the ID string from the token payload
    user_id: Optional[uuid.UUID] = None

    # Validate and convert user ID string to UUID object
    if user_id_str:
        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, TypeError) as e:  # Add 'as e' for B904 fix
            logger.error(
                f"Could not convert user ID '{user_id_str}' to UUID. "
                f"User info: {current_user}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token.",
            ) from e  # Add 'from e' for B904
    else: # Handle case where user_id_str is None or empty
         logger.error(
            f"Could not get valid user ID from current_user. User info: {current_user}"
        )
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user context."
        ) from None


    # Requirement #6: Check for existing PENDING or RUNNING jobs for this domain
    try:
        # Query for jobs associated with the domain_id and in specific states
        stmt = (
            select(Job)
            .where(Job.domain_id == domain_id)
            .where(cast(Job.status, String).in_([TaskStatus.PENDING.value, TaskStatus.RUNNING.value]))  # noqa
            .order_by(
                Job.created_at.desc()
            )  # Get the most recent one if multiple somehow exist
        )
        result = await session.execute(stmt)
        existing_job = result.scalars().first()

        if existing_job:
            logger.info(
                f"Active scan job ({existing_job.job_id}) already exists for domain "
                f"{domain_id}. Returning existing job ID."
            )
            # Access the actual UUID value
            existing_job_id_value = existing_job.job_id
            return JobSubmissionResponse(job_id=existing_job_id_value)  # noqa

    except Exception as e:
        logger.error(
            f"Database error checking for existing jobs for domain {domain_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking for existing jobs.",
        ) from e  # Add 'from e' for B904

    # Verify domain exists (optional but good practice)
    domain_obj = await session.get(Domain, domain_id)
    if not domain_obj:
        logger.error(f"Domain with ID {domain_id} not found.")
        # No original exception here, so 'from None' is appropriate for B904
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found."
        ) from None

    # Requirement #5: Create a new Job record
    try:
        # Use the Job model's class method to create the job instance
        job = Job(
            job_type="email_scan",
            status=TaskStatus.PENDING.value,
            created_by=user_id,
            domain_id=domain_id,
            tenant_id_uuid=uuid.UUID(DEFAULT_TENANT_ID),  # Ensure UUID tenant is set
            # job_id is generated by default by the model
        )
        session.add(job)
        await session.flush()  # Flush to get the generated job.job_id
        await session.commit()  # Commit the new job record
        logger.info(
            f"Created new email scan job {job.job_id} for domain {domain_id} "
            f"by user {user_id}"
        )

        # Extract the generated UUID job_id AFTER flush/commit
        # Access the actual UUID value from the job object
        new_job_id_value = job.job_id

    except Exception as e:
        logger.error(
            f"Database error creating job for domain {domain_id}: {e}", exc_info=True
        )
        await session.rollback()  # Rollback on error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating scan job record.",
        ) from e  # Add 'from e' for B904

    # Add the background task, passing the new job's UUID value
    # Ensure the task function signature matches (job_id, user_id)
    background_tasks.add_task(
        scan_website_for_emails,
        job_id=new_job_id_value,
        user_id=user_id,  # noqa
    )
    logger.info(
        f"Queued background task scan_website_for_emails for job {new_job_id_value}"
    )

    # Return the actual UUID value
    return JobSubmissionResponse(job_id=new_job_id_value)  # noqa


@router.get("/scan/status/{job_id}", response_model=JobStatusResponse)
async def get_scan_status_api(
    job_id: uuid.UUID,  # Use UUID type hint for path parameter
    session: AsyncSession = SessionDep,
    current_user: Dict[str, Any] = CurrentUserDep # Auth usually needed here too
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
