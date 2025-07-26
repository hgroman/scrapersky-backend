"""
Job SQLAlchemy Model

Represents background processing jobs in ScraperSky.
"""

import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import (
    UUID,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, model_to_dict
from .tenant import DEFAULT_TENANT_ID


class Job(Base, BaseModel):
    """
    Job model representing background processing tasks.

    Fields:
        id: UUID primary key (inherited from BaseModel)
        job_type: Type of job (sitemap_scan, places_search, etc.)
        tenant_id: The tenant ID field (always using default tenant ID)
        created_by: The user who created this job
        status: Current job status (pending, running, complete, failed)
        domain_id: Optional reference to associated domain
        progress: Optional progress indicator (0.0-1.0)
        result_data: JSON field for job results
        error: Error message if job failed
        job_metadata: Additional job metadata
        batch_id: Optional batch ID if part of batch processing
    """

    __tablename__ = "jobs"

    # Override the id column to use an Integer primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # UUID identifier (missing column that's causing the error)
    job_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)

    # Core fields
    job_type = Column(String, nullable=False)
    tenant_id = Column(String, nullable=False, default=DEFAULT_TENANT_ID)
    tenant_id_uuid = Column(
        PGUUID, index=True, default=lambda: uuid.UUID(DEFAULT_TENANT_ID)
    )

    # Status and metadata
    created_by = Column(PGUUID)
    status = Column(String, nullable=False)
    domain_id = Column(PGUUID, ForeignKey("domains.id", ondelete="SET NULL"))
    progress = Column(Float, default=0.0)
    result_data = Column(JSONB)
    error = Column(String)
    job_metadata = Column(JSONB)

    # Batch processing field
    batch_id = Column(
        PGUUID, ForeignKey("batch_jobs.batch_id", ondelete="SET NULL"), index=True
    )

    # Relationships
    domain = relationship("Domain", back_populates="jobs")
    batch = relationship("BatchJob", back_populates="jobs")

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary with proper serialization."""
        return model_to_dict(self)

    def update_progress(
        self, progress_value: float, status: Optional[str] = None
    ) -> None:
        """
        Update job progress and optionally status.

        Args:
            progress_value: Progress value between 0.0 and 1.0
            status: Optional new status
        """
        self.progress = min(max(0.0, progress_value), 1.0)

        if status:
            self.status = status
        elif self.progress >= 1.0 and self.status not in ["complete", "failed"]:
            self.status = "complete"

    @classmethod
    async def create_for_domain(
        cls,
        session,
        job_type: str,
        domain_id: Optional[uuid.UUID] = None,
        created_by: Optional[uuid.UUID] = None,
        batch_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Job":
        """
        Create a new job for domain processing using default tenant ID.

        Args:
            session: SQLAlchemy session
            job_type: Type of job
            domain_id: Optional domain UUID
            created_by: User UUID of creator
            batch_id: Optional batch ID
            metadata: Job metadata

        Returns:
            New Job instance
        """
        job = cls(
            job_type=job_type,
            tenant_id=DEFAULT_TENANT_ID,
            tenant_id_uuid=uuid.UUID(DEFAULT_TENANT_ID),
            created_by=created_by,
            status="pending",
            domain_id=domain_id,
            progress=0.0,
            job_metadata=metadata or {},
            batch_id=batch_id,
        )

        session.add(job)
        return job

    @classmethod
    async def get_by_id(
        cls, session, job_id: Union[int, uuid.UUID, str]
    ) -> Optional["Job"]:
        """Get a job by its integer ID without tenant filtering.

        Args:
            session: Database session.
            job_id: Integer ID of the job.

        Returns:
            Optional[Job]: Job if found, None otherwise.
        """
        from sqlalchemy import select

        # Ensure we are querying by the integer primary key 'id'
        query = select(cls).where(cls.id == int(job_id))  # Convert to int just in case
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_job_id(cls, session, job_id: Union[uuid.UUID, str, int]) -> Optional["Job"]:
        """Get a job by its public UUID (job_id) without tenant filtering.

        Args:
            session: Database session.
            job_id: The identifier of the job, can be UUID, string, or integer.

        Returns:
            Optional[Job]: Job if found, None otherwise.
        """
        from sqlalchemy import select

        # Convert to UUID if needed
        if isinstance(job_id, int) or (isinstance(job_id, str) and job_id.isdigit()):
            # If it's an integer ID, use get_by_id instead
            return await cls.get_by_id(session, job_id)
        
        # Handle UUID or string UUID
        if isinstance(job_id, str):
            try:
                job_id = uuid.UUID(job_id)
            except ValueError:
                logger.error(f"Invalid UUID format for job_id: {job_id}")
                return None
                
        # Query by UUID
        query = select(cls).where(cls.job_id == job_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_recent_jobs(
        cls, session, job_type: Optional[str] = None, limit: int = 10
    ) -> List["Job"]:
        """Get recent jobs without tenant filtering.

        Args:
            session: Database session.
            job_type: Type of job to filter by.
            limit: Maximum number of jobs to return.

        Returns:
            List[Job]: List of jobs.
        """
        from sqlalchemy import select

        # Build query without tenant filtering
        query = select(cls).order_by(cls.created_at.desc()).limit(limit)

        if job_type:
            query = query.where(cls.job_type == job_type)

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_batch_id(cls, session, batch_id: str) -> List["Job"]:
        """
        Get all jobs that belong to a specific batch without tenant filtering.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to look up

        Returns:
            List of Job instances
        """
        from sqlalchemy import select

        # Build query without tenant filtering
        query = select(cls).where(cls.batch_id == batch_id)

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_domain_id(
        cls, session, domain_id: Union[str, uuid.UUID]
    ) -> List["Job"]:
        """
        Get all jobs for a specific domain without tenant filtering.

        Args:
            session: SQLAlchemy session
            domain_id: Domain ID to look up

        Returns:
            List of Job instances
        """
        from sqlalchemy import select

        # Build query without tenant filtering as per architectural mandate
        query = select(cls).where(cls.domain_id == domain_id)

        result = await session.execute(query)
        return result.scalars().all()
