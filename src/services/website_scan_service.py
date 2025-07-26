import logging
import uuid
from typing import Optional

from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import TaskStatus
from src.models.job import Job
from src.models.tenant import DEFAULT_TENANT_ID

logger = logging.getLogger(__name__)


class WebsiteScanService:
    """
    Service to handle the business logic of initiating a website scan.
    """

    async def initiate_scan(
        self,
        domain_id: uuid.UUID,
        user_id: uuid.UUID,
        session: AsyncSession,
    ) -> Job:
        """
        Initiates a scan by creating a Job record.

        Checks for existing PENDING or RUNNING jobs for the same domain.
        If found, returns the existing job.
        Otherwise, creates a new job and returns it.
        """
        # Check for existing PENDING or RUNNING jobs for this domain
        stmt_existing = (
            select(Job)
            .where(Job.domain_id == domain_id)
            .where(cast(Job.status, String).in_([TaskStatus.PENDING.value, TaskStatus.RUNNING.value]))
            .order_by(Job.created_at.desc())
            .limit(1)
        )
        result_existing = await session.execute(stmt_existing)
        existing_job = result_existing.scalar_one_or_none()

        if existing_job:
            logger.info(
                f"Found existing active job {existing_job.id} for domain {domain_id}. Returning existing job."
            )
            return existing_job

        # Create a new job if no active one is found
        new_job = Job(
            job_type="website_scan",  # Added: Required job_type field
            domain_id=domain_id,
            created_by=user_id,  # Fixed: Changed user_id to created_by to match Job model
            tenant_id=DEFAULT_TENANT_ID,  # Assuming default tenant
            status=TaskStatus.PENDING,
        )
        session.add(new_job)
        await session.flush()  # Flush to get the new job's ID
        await session.refresh(new_job)
        logger.info(f"Created new job {new_job.id} for domain {domain_id}.")

        return new_job
