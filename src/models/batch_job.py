"""
BatchJob SQLAlchemy Model

Represents batch processing jobs in ScraperSky.
"""

import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import UUID, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, BaseModel, model_to_dict
from .tenant import DEFAULT_TENANT_ID


class BatchJob(Base, BaseModel):
    """
    BatchJob model representing batch processing operations.

    This model tracks the overall status of batch operations, including
    metadata about the batch and relationships to individual jobs.

    Fields:
        id: Integer primary key (overriding UUID from BaseModel)
        batch_id: UUID identifier for the batch (standardized from string)
        tenant_id: The tenant ID field (always using default tenant ID)
        processor_type: Type of processing (sitemap, metadata, contacts, etc.)
        status: Current batch status (pending, running, complete, failed, partial)
        created_by: The user who initiated this batch job

        # Progress tracking
        total_domains: Total number of domains in the batch
        completed_domains: Number of successfully processed domains
        failed_domains: Number of failed domain processing attempts
        progress: Overall progress as a float (0.0-1.0)

        # Metadata and options
        batch_metadata: JSON field for additional batch metadata
        options: Processing options passed to the batch

        # Performance metrics
        start_time: When the batch processing started
        end_time: When the batch processing completed
        processing_time: Total processing time in seconds
    """

    __tablename__ = "batch_jobs"

    # Override id with Integer primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # UUID identifier (missing column that's causing the error)
    id_uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True
    )

    # Core identifiers - Updated batch_id to UUID type
    batch_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True)
    tenant_id = Column(
        PGUUID, nullable=False, index=True, default=lambda: uuid.UUID(DEFAULT_TENANT_ID)
    )
    processor_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_by = Column(PGUUID)

    # Progress tracking
    total_domains = Column(Integer, default=0)
    completed_domains = Column(Integer, default=0)
    failed_domains = Column(Integer, default=0)
    progress = Column(Float, default=0.0)

    # Metadata and options
    batch_metadata = Column(JSONB)
    options = Column(JSONB)

    # Performance metrics
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    processing_time = Column(Float)

    # Error tracking
    error = Column(String)

    # Relationships
    jobs = relationship("Job", back_populates="batch")
    domains = relationship("Domain", back_populates="batch")

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch job to dictionary with proper serialization."""
        data = model_to_dict(self)
        # Convert UUID to string for serialization
        if self.batch_id and isinstance(self.batch_id, uuid.UUID):
            data["batch_id"] = str(self.batch_id)
        return data

    def calculate_progress(self) -> float:
        """Calculate current progress based on completed and total domains."""
        if not self.total_domains:
            return 0.0
        return (self.completed_domains + self.failed_domains) / self.total_domains

    def update_progress(
        self, completed: Optional[int] = None, failed: Optional[int] = None
    ) -> None:
        """
        Update progress tracking fields.

        Args:
            completed: Number of completed domains (if changed)
            failed: Number of failed domains (if changed)
        """
        if completed is not None:
            self.completed_domains = completed
        if failed is not None:
            self.failed_domains = failed

        # Recalculate progress
        self.progress = self.calculate_progress()

        # Update status based on progress
        if self.progress >= 1.0:
            if self.failed_domains == self.total_domains:
                self.status = "failed"
            elif self.failed_domains > 0:
                self.status = "partial"
            else:
                self.status = "complete"

            # Set end time if not already set
            if not self.end_time:
                self.end_time = func.now()
                if self.start_time:
                    # This will be calculated properly at database level
                    # due to func.now() and stored procedures
                    self.processing_time = 0.0

    @classmethod
    async def create_new_batch(
        cls,
        session,
        batch_id: Union[str, uuid.UUID],
        processor_type: str,
        total_domains: int,
        created_by: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "BatchJob":
        """
        Create a new batch job using default tenant ID.

        Args:
            session: SQLAlchemy session
            batch_id: Unique batch identifier (UUID)
            processor_type: Type of processing
            total_domains: Total number of domains in batch
            created_by: User ID of creator
            options: Processing options
            metadata: Additional batch metadata

        Returns:
            New BatchJob instance
        """
        # Convert batch_id to UUID if it's a string
        if isinstance(batch_id, str):
            batch_id = uuid.UUID(batch_id)

        # Convert created_by to UUID if it's a string
        created_by_uuid = None
        if created_by:
            if isinstance(created_by, str):
                created_by_uuid = uuid.UUID(created_by)
            else:
                created_by_uuid = created_by

        batch_job = cls(
            batch_id=batch_id,
            tenant_id=uuid.UUID(DEFAULT_TENANT_ID),
            processor_type=processor_type,
            status="pending",
            created_by=created_by_uuid,
            total_domains=total_domains,
            completed_domains=0,
            failed_domains=0,
            progress=0.0,
            batch_metadata=metadata or {},
            options=options or {},
            start_time=func.now(),
        )

        session.add(batch_job)
        return batch_job

    @classmethod
    async def get_by_batch_id(
        cls, session, batch_id: Union[str, uuid.UUID]
    ) -> Optional["BatchJob"]:
        """
        Get batch job by batch ID using default tenant ID.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to look up (UUID)

        Returns:
            BatchJob instance or None if not found
        """
        from sqlalchemy import select

        # Convert batch_id to UUID if it's a string
        if isinstance(batch_id, str):
            try:
                batch_id = uuid.UUID(batch_id)
            except ValueError:
                return None

        # Build query with default tenant ID
        query = select(cls).where(
            cls.batch_id == batch_id, cls.tenant_id == uuid.UUID(DEFAULT_TENANT_ID)
        )

        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_recent_batches(cls, session, limit: int = 10) -> List["BatchJob"]:
        """
        Get recent batch jobs using default tenant ID.

        Args:
            session: SQLAlchemy session
            limit: Maximum number of batches to return

        Returns:
            List of BatchJob instances
        """
        from sqlalchemy import select

        # Build query with default tenant ID
        query = (
            select(cls)
            .where(cls.tenant_id == uuid.UUID(DEFAULT_TENANT_ID))
            .order_by(cls.created_at.desc())
            .limit(limit)
        )

        result = await session.execute(query)
        return result.scalars().all()
