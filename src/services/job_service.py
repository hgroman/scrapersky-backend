"""
Job Service

Provides operations for job management and background task tracking using SQLAlchemy ORM.
This service is transaction-aware, meaning it checks if it's being called within an active
transaction and behaves accordingly. It follows the "routers own transaction boundaries,
services do not" pattern.
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.session import get_session
from ..models import BatchJob, Job
from ..models.tenant import DEFAULT_TENANT_ID

# NOTE: Removing managed_transaction import as part of transaction boundary standardization

logger = logging.getLogger(__name__)

class JobService:
    """
    Service for job management.

    This service provides standardized methods for working with Job entities,
    including creation, retrieval, and status updates using SQLAlchemy ORM.
    """

    # Job status constants
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETE = "complete"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    async def get_by_id(
        self,
        session: AsyncSession,
        job_id: Union[str, uuid.UUID, int],
        load_relationships: bool = False
    ) -> Optional[Job]:
        """
        Get a job by ID with optional relationship loading.

        This method is transaction-aware and can be called from within an existing
        transaction or without a transaction. It will not start a new transaction.

        Args:
            session: SQLAlchemy session (can be in transaction context or not)
            job_id: Job ID to look up (can be string, UUID, or integer)
            load_relationships: Whether to eagerly load relationships

        Returns:
            Job instance or None if not found
        """
        try:
            # Check if the session is already in a transaction
            in_transaction = session.in_transaction()
            logger.debug(f"Session transaction state in get_by_id: {in_transaction}")

            # Build base query
            query = select(Job)

            # Add eager loading if requested
            if load_relationships:
                query = query.options(
                    selectinload(Job.domain),
                    selectinload(Job.batch)
                )

            # Handle different job_id types
            if isinstance(job_id, int):
                # Numeric ID (primary key)
                query = query.where(Job.id == job_id)
                logger.debug(f"Looking up job by numeric ID: {job_id}")
            elif isinstance(job_id, uuid.UUID) or isinstance(job_id, str):
                # Try direct lookup by numeric ID first if it's a string
                if isinstance(job_id, str):
                    try:
                        numeric_id = int(job_id)
                        query = query.where(Job.id == numeric_id)
                        logger.debug(f"Looking up job by numeric string: {job_id} -> {numeric_id}")
                    except ValueError:
                        # It's not a numeric ID, so handle as UUID
                        try:
                            # Try as a UUID string
                            job_uuid = uuid.UUID(str(job_id))
                            job_uuid_str = str(job_uuid)

                            # Use string comparison to avoid type errors
                            query = select(Job).where(Job.job_id == job_uuid_str)
                            logger.debug(f"Looking up job by UUID string: {job_uuid_str}")
                        except ValueError:
                            logger.warning(f"Invalid UUID format for job_id: {job_id}")
                            # Try direct string comparison
                            query = select(Job).where(Job.job_id == str(job_id))
                            logger.debug(f"Looking up job by direct string match: {job_id}")
                else:
                    # It's already a UUID, convert to string to avoid type errors
                    job_uuid_str = str(job_id)
                    query = select(Job).where(Job.job_id == job_uuid_str)
                    logger.debug(f"Looking up job by UUID: {job_id}")
            else:
                logger.warning(f"Unsupported job_id type: {type(job_id)}")
                return None

            # Execute query - Just use the session as is, don't try to manage transactions
            result = await session.execute(
                query,
                execution_options={
                    "no_parameters": True,  # Disable prepared statements for Supavisor
                    "statement_cache_size": 0  # Disable statement caching
                }
            )
            job = result.scalars().first()

            if job is None:
                logger.debug(f"No job found for ID: {job_id}")
            else:
                logger.debug(f"Found job with ID: {job.id}, UUID: {job.job_id}")

            return job

        except Exception as e:
            logger.error(f"Error retrieving job by ID {job_id}: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def get_recent_jobs(
        self,
        session: AsyncSession,
        job_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Job]:
        """
        Get recent jobs.

        Args:
            session: SQLAlchemy session
            job_type: Optional job type to filter by
            limit: Maximum number of jobs to return

        Returns:
            List of Job instances
        """
        try:
            # Build query
            query = select(Job)

            # Add job type filter if provided
            if job_type:
                query = query.where(Job.job_type == job_type)

            # Add ordering and limit
            query = query.order_by(Job.created_at.desc()).limit(limit)

            # Execute query
            result = await session.execute(
                query,
                execution_options={
                    "no_parameters": True,  # Disable prepared statements for Supavisor
                    "statement_cache_size": 0  # Disable statement caching
                }
            )
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error retrieving recent jobs: {str(e)}")
            return []

    async def get_pending_jobs(
        self,
        session: AsyncSession,
        job_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Job]:
        """
        Get pending jobs for processing.

        This method is transaction-aware and can be called from within an existing
        transaction or without a transaction. It will not start a new transaction.

        Args:
            session: SQLAlchemy session
            job_type: Optional job type to filter by (e.g., 'sitemap')
            limit: Maximum number of jobs to return

        Returns:
            List of Job instances with 'pending' status
        """
        try:
            # Check if the session is already in a transaction
            in_transaction = session.in_transaction()
            logger.debug(f"Session transaction state in get_pending_jobs: {in_transaction}")

            # Build query
            query = select(Job).where(Job.status == self.STATUS_PENDING)

            # Add job type filter if provided
            if job_type:
                query = query.where(Job.job_type == job_type)

            # Add ordering and limit
            query = query.order_by(Job.created_at.asc()).limit(limit)

            # Execute query
            result = await session.execute(
                query,
                execution_options={
                    "no_parameters": True,  # Disable prepared statements for Supavisor
                    "statement_cache_size": 0  # Disable statement caching
                }
            )
            pending_jobs = list(result.scalars().all())
            logger.debug(f"Found {len(pending_jobs)} pending jobs of type {job_type or 'any'}")
            return pending_jobs

        except Exception as e:
            logger.error(f"Error retrieving pending jobs: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def create(
        self,
        session: AsyncSession,
        job_data: Dict[str, Any],
        **db_params: Any
    ) -> Optional[Job]:
        """
        Create a new job record in the database.

        This method is transaction-aware and can be called from within an existing
        transaction or without a transaction. It will not start a new transaction.
        The caller (typically a router) is responsible for managing transaction boundaries.

        Args:
            session: SQLAlchemy session
            job_data: Dictionary of job data
            db_params: Additional database parameters (raw_sql, no_prepare, statement_cache_size)

        Returns:
            New Job instance or None if creation failed
        """
        try:
            # Check if the session is already in a transaction
            in_transaction = session.in_transaction()
            logger.debug(f"Session transaction state in create: {in_transaction}")

            # Log creation attempt
            logger.debug(f"Creating job of type: {job_data.get('job_type', 'unknown')}")

            # Extract database parameters
            raw_sql = db_params.get("raw_sql", False)
            no_prepare = db_params.get("no_prepare", False)

            # Ensure job_id is set (critical for retrieving the job later)
            if "job_id" not in job_data:
                job_data["job_id"] = uuid.uuid4()
            elif isinstance(job_data["job_id"], str):
                job_data["job_id"] = uuid.UUID(job_data["job_id"])

            # Log the job_id we're creating
            logger.debug(f"Creating job with job_id: {job_data['job_id']}")

            # Create Job instance directly using SQLAlchemy ORM
            job = Job(
                job_type=job_data.get("job_type", "unknown"),
                status=job_data.get("status", self.STATUS_PENDING),
                domain_id=job_data.get("domain_id"),
                batch_id=job_data.get("batch_id"),
                created_by=job_data.get("created_by"),
                progress=job_data.get("progress", 0.0),
                result_data=job_data.get("result_data"),
                error=job_data.get("error"),
                job_metadata=job_data.get("job_metadata", {}),
                job_id=job_data.get("job_id")
            )

            # Add to session and flush changes
            session.add(job)
            await session.flush()

            logger.debug(f"Created job with numeric ID {job.id} and UUID {job.job_id}")

            return job

        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def create_for_domain(
        self,
        session: AsyncSession,
        job_type: str,
        domain_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Job:
        """
        Create a new job for a domain.

        Args:
            session: Database session
            job_type: Type of job
            domain_id: Optional domain ID
            created_by: User ID who created the job

        Returns:
            Created Job object
        """
        try:
            # Check if in transaction
            in_transaction = session.in_transaction()
            logger.debug(f"Session transaction state in create_for_domain: {in_transaction}")

            # Create job data dictionary
            job_data = {
                "job_type": job_type,
                "domain_id": domain_id,
                "created_by": created_by,
                "status": "pending",
                "progress": 0.0
            }

            # Create new job
            job = Job(**job_data)
            session.add(job)
            await session.flush()

            return job

        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            raise

    async def update_status(
        self,
        session: AsyncSession,
        job_id: Union[str, uuid.UUID, int],
        status: str,
        progress: Optional[float] = None,
        result_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Optional[Job]:
        """
        Update job status and related fields.

        This method is transaction-aware and can be called from within an existing
        transaction or without a transaction. It will not start a new transaction.
        The caller (typically a router) is responsible for managing transaction boundaries.

        Args:
            session: SQLAlchemy session
            job_id: Job ID to update
            status: New status
            progress: Optional progress value (0.0-1.0)
            result_data: Optional result data
            error: Optional error message
            tenant_id: Optional tenant ID for security filtering

        Returns:
            Updated Job instance or None if not found
        """
        try:
            # Check if the session is already in a transaction
            in_transaction = session.in_transaction()
            logger.debug(f"Session transaction state in update_status: {in_transaction}")

            # Try to convert job_id to UUID if it's a string to ensure type compatibility
            job_id_for_query = job_id
            if isinstance(job_id, str):
                try:
                    job_id_for_query = uuid.UUID(job_id)
                    logger.debug(f"Converted job_id string to UUID: {job_id} -> {job_id_for_query}")
                except ValueError:
                    logger.warning(f"Invalid UUID format for job_id: {job_id}, will try string comparison")

            # Get job
            job = await self.get_by_id(session, job_id_for_query)
            if not job:
                logger.warning(f"Job not found for status update: {job_id}")
                return None

            # Update status
            job.status = status

            # Update progress if provided
            if progress is not None:
                job.progress = min(max(0.0, progress), 1.0)

            # Update result data if provided
            if result_data is not None:
                # Use setattr to avoid linter errors with direct Column assignment
                setattr(job, "result_data", result_data)

            # Update error if provided
            if error is not None:
                # Use setattr to avoid linter errors with direct Column assignment
                setattr(job, "error", error)
                # Set status to failed if an error is provided and status isn't explicitly set
                if status != self.STATUS_FAILED:
                    job.status = self.STATUS_FAILED

            # Add to session and flush changes
            session.add(job)
            await session.flush()

            return job

        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
            # Propagate the exception for proper transaction handling by the caller
            raise

    async def update(
        self,
        session: AsyncSession,
        job_id: Union[str, uuid.UUID, int],
        job_data: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> Optional[Job]:
        """
        Update a job with multiple fields.

        Args:
            session: SQLAlchemy session
            job_id: Job ID to update
            job_data: Dictionary of job data to update
            tenant_id: Optional tenant ID for security filtering

        Returns:
            Updated Job instance or None if not found
        """
        try:
            # Get job
            job = await self.get_by_id(session, job_id)
            if not job:
                logger.warning(f"Job not found for update: {job_id}")
                return None

            # Update fields
            for field, value in job_data.items():
                if hasattr(job, field):
                    setattr(job, field, value)

            # Add to session and flush changes
            session.add(job)
            await session.flush()

            return job

        except Exception as e:
            logger.error(f"Error updating job: {str(e)}")
            return None

    async def get_by_batch_id(
        self,
        session: AsyncSession,
        batch_id: str,
        tenant_id: Optional[str] = None,
        load_relationships: bool = False
    ) -> Optional[BatchJob]:
        """
        Get batch job by batch ID.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to look up
            tenant_id: Optional tenant ID for security filtering (deprecated, ignored)
            load_relationships: Whether to eagerly load relationships

        Returns:
            BatchJob instance or None if not found
        """
        try:
            # Use the BatchJob class method which handles default tenant ID
            if load_relationships:
                # Build query
                query = select(BatchJob).where(BatchJob.batch_id == batch_id)

                # Add eager loading if requested
                query = query.options(
                    selectinload(BatchJob.jobs),
                    selectinload(BatchJob.domains)
                )

                # Execute query
                result = await session.execute(
                    query,
                    execution_options={
                        "no_parameters": True,  # Disable prepared statements for Supavisor
                        "statement_cache_size": 0  # Disable statement caching
                    }
                )
                return result.scalars().first()
            else:
                # Use the class method for simple lookups
                return await BatchJob.get_by_batch_id(session, batch_id)

        except Exception as e:
            logger.error(f"Error retrieving batch job by ID: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def get_by_domain_id(
        self,
        session: AsyncSession,
        domain_id: Union[str, uuid.UUID],
        tenant_id: Optional[str] = None,
        load_relationships: bool = False
    ) -> List[Job]:
        """
        Get all jobs for a specific domain.

        Args:
            session: SQLAlchemy session
            domain_id: Domain ID to look up
            tenant_id: Optional tenant ID for security filtering
            load_relationships: Whether to eagerly load relationships

        Returns:
            List of Job instances
        """
        try:
            # Convert domain_id to UUID if it's a string
            domain_id_uuid = None
            try:
                domain_id_uuid = domain_id if isinstance(domain_id, uuid.UUID) else uuid.UUID(str(domain_id))
            except ValueError:
                logger.warning(f"Invalid UUID format for domain_id: {domain_id}")
                return []

            # Build query
            query = select(Job).where(Job.domain_id == domain_id_uuid)

            # Add eager loading if requested
            if load_relationships:
                query = query.options(
                    selectinload(Job.batch)
                )

            # REMOVED tenant filtering as per architectural mandate
            # JWT authentication happens ONLY at API gateway endpoints
            # Database operations should NEVER handle JWT or tenant authentication

            # Execute query
            result = await session.execute(
                query,
                execution_options={
                    "no_parameters": True,  # Disable prepared statements for Supavisor
                    "statement_cache_size": 0  # Disable statement caching
                }
            )
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error retrieving jobs by domain ID: {str(e)}")
            return []

    async def get_by_numeric_id(
        self,
        session: AsyncSession,
        job_id: int,
        tenant_id: Optional[str] = None,
        load_relationships: bool = False
    ) -> Optional[Job]:
        """
        Get a job specifically by numeric ID (primary key).
        This simplifies lookup for job IDs that are known to be numeric.

        Args:
            session: SQLAlchemy session
            job_id: Job ID as integer
            tenant_id: Optional tenant ID for security filtering
            load_relationships: Whether to eagerly load relationships

        Returns:
            Job instance or None if not found
        """
        try:
            # Build query with direct primary key lookup
            query = select(Job).where(Job.id == job_id)

            # Add eager loading if requested
            if load_relationships:
                query = query.options(
                    selectinload(Job.domain),
                    selectinload(Job.batch)
                )

            # Execute query with compatibility options for Supavisor
            result = await session.execute(
                query,
                execution_options={
                    "no_parameters": True,
                    "statement_cache_size": 0
                }
            )
            job = result.scalars().first()

            if job is None:
                logger.debug(f"No job found for numeric ID: {job_id}")
            else:
                logger.debug(f"Found job with ID: {job.id}")

            return job

        except Exception as e:
            logger.error(f"Error retrieving job by numeric ID {job_id}: {str(e)}")
            raise

    async def get_by_uuid(
        self,
        session: AsyncSession,
        job_uuid: str,
        tenant_id: Optional[str] = None
    ) -> Optional[Job]:
        """
        Get a job specifically by UUID using raw SQL to avoid prepared statement issues.
        This works around SQLAlchemy async context issues when retrieving by UUID.

        Args:
            session: SQLAlchemy session
            job_uuid: Job UUID string
            tenant_id: Optional tenant ID for security filtering

        Returns:
            Job instance or None if not found
        """
        try:
            # Use raw SQL text query to avoid prepared statement issues
            from sqlalchemy import text

            # Direct SQL query avoiding type issues
            query_text = text("""
                SELECT * FROM jobs
                WHERE job_id = :job_uuid
                LIMIT 1
            """)

            # Execute with proper execution options for Supavisor
            result = await session.execute(
                query_text,
                {"job_uuid": job_uuid},
                execution_options={
                    "no_parameters": True,
                    "statement_cache_size": 0
                }
            )

            # Convert raw result to Job model
            row = result.first()
            if not row:
                logger.debug(f"No job found for UUID: {job_uuid}")
                return None

            # Create Job object from row
            job = Job()
            for key, value in row._mapping.items():
                if hasattr(job, key):
                    setattr(job, key, value)

            logger.debug(f"Found job with ID: {job.id}, UUID: {job.job_id}")
            return job

        except Exception as e:
            logger.error(f"Error retrieving job by UUID {job_uuid}: {str(e)}")
            # Propagate exception to caller for proper error handling
            raise

    # BatchJob methods

    async def create_batch(
        self,
        session: AsyncSession,
        batch_id: str,
        processor_type: str,
        total_domains: int,
        created_by: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[BatchJob]:
        """
        Create a new batch job using default tenant ID.

        This method is transaction-aware and can be called from within an existing
        transaction or without a transaction. It will not start a new transaction.
        The caller (typically a router) is responsible for managing transaction boundaries.

        Args:
            session: SQLAlchemy session
            batch_id: Unique batch identifier
            processor_type: Type of processing
            total_domains: Total number of domains in batch
            created_by: User ID of creator
            options: Processing options
            metadata: Additional batch metadata

        Returns:
            New BatchJob instance or None if creation failed
        """
        try:
            # Check if the session is already in a transaction
            in_transaction = session.in_transaction()
            logger.debug(f"Session transaction state in create_batch: {in_transaction}")

            # Use the BatchJob class method which already handles default tenant ID
            batch_job = await BatchJob.create_new_batch(
                session=session,
                batch_id=batch_id,
                processor_type=processor_type,
                total_domains=total_domains,
                created_by=created_by,
                options=options,
                metadata=metadata
            )

            await session.flush()
            logger.debug(f"Created batch job with ID {batch_job.id} and batch ID {batch_job.batch_id}")
            return batch_job

        except Exception as e:
            logger.error(f"Error creating batch job: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def update_batch_progress(
        self,
        session: AsyncSession,
        batch_id: str,
        completed: Optional[int] = None,
        failed: Optional[int] = None,
        tenant_id: Optional[str] = None  # Deprecated, ignored
    ) -> Optional[BatchJob]:
        """
        Update batch job progress.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to update
            completed: Number of completed domains
            failed: Number of failed domains
            tenant_id: Optional tenant ID (deprecated, ignored)

        Returns:
            Updated BatchJob instance or None if not found
        """
        try:
            # Get batch job using the default tenant ID
            batch_job = await BatchJob.get_by_batch_id(session, batch_id)
            if not batch_job:
                logger.warning(f"Batch job not found for progress update: {batch_id}")
                return None

            # Use the BatchJob model method to update progress
            batch_job.update_progress(completed=completed, failed=failed)

            # Add to session and flush changes
            session.add(batch_job)
            await session.flush()

            return batch_job

        except Exception as e:
            logger.error(f"Error updating batch progress: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def get_recent_batches(
        self,
        session: AsyncSession,
        limit: int = 10,
        load_relationships: bool = False
    ) -> List[BatchJob]:
        """
        Get recent batch jobs using default tenant ID.

        Args:
            session: SQLAlchemy session
            limit: Maximum number of batches to return
            load_relationships: Whether to eagerly load relationships

        Returns:
            List of BatchJob instances
        """
        try:
            # Use the BatchJob class method which handles default tenant ID
            if load_relationships:
                # Build query with default tenant ID
                query = select(BatchJob).where(
                    BatchJob.tenant_id == uuid.UUID(DEFAULT_TENANT_ID)
                )

                # Add eager loading
                query = query.options(
                    selectinload(BatchJob.jobs)
                )

                # Add ordering and limit
                query = query.order_by(BatchJob.created_at.desc()).limit(limit)

                # Execute query
                result = await session.execute(
                    query,
                    execution_options={
                        "no_parameters": True,  # Disable prepared statements for Supavisor
                        "statement_cache_size": 0  # Disable statement caching
                    }
                )
                return list(result.scalars().all())
            else:
                # Use the class method for simple lookups
                return await BatchJob.get_recent_batches(session, limit)

        except Exception as e:
            logger.error(f"Error retrieving recent batch jobs: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def complete_batch(
        self,
        session: AsyncSession,
        batch_id: str,
        result_data: Optional[Dict[str, Any]] = None
    ) -> Optional[BatchJob]:
        """
        Mark a batch job as complete.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to update
            result_data: Optional result data

        Returns:
            Updated BatchJob instance or None if not found
        """
        try:
            # Get batch job using the default tenant ID
            batch_job = await BatchJob.get_by_batch_id(session, batch_id)
            if not batch_job:
                logger.warning(f"Batch job not found for completion: {batch_id}")
                return None

            # Update status
            batch_job.status = self.STATUS_COMPLETE
            setattr(batch_job, "progress", 1.0)
            # Use setattr to avoid linter errors
            setattr(batch_job, "end_time", datetime.now())

            # Update result data if provided
            if result_data is not None:
                setattr(batch_job, "result_data", result_data)

            # Add to session and flush changes
            session.add(batch_job)
            await session.flush()

            return batch_job

        except Exception as e:
            logger.error(f"Error completing batch job: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def fail_batch(
        self,
        session: AsyncSession,
        batch_id: str,
        error: str
    ) -> Optional[BatchJob]:
        """
        Mark a batch job as failed.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to update
            error: Error message

        Returns:
            Updated BatchJob instance or None if not found
        """
        try:
            # Get batch job using the default tenant ID
            batch_job = await BatchJob.get_by_batch_id(session, batch_id)
            if not batch_job:
                logger.warning(f"Batch job not found for failure: {batch_id}")
                return None

            # Update status
            batch_job.status = self.STATUS_FAILED
            # Use setattr to avoid linter errors
            setattr(batch_job, "error", error)
            setattr(batch_job, "end_time", datetime.now())

            # Add to session and flush changes
            session.add(batch_job)
            await session.flush()

            return batch_job

        except Exception as e:
            logger.error(f"Error failing batch job: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

    async def get_batch_by_id(
        self,
        session: AsyncSession,
        batch_id: str,
        tenant_id: Optional[str] = None,  # Deprecated, ignored
        load_relationships: bool = False
    ) -> Optional[BatchJob]:
        """
        Get batch job by batch ID.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to look up
            tenant_id: Optional tenant ID for security filtering (deprecated, ignored)
            load_relationships: Whether to eagerly load relationships

        Returns:
            BatchJob instance or None if not found
        """
        try:
            # Use the BatchJob class method which handles default tenant ID
            if load_relationships:
                # Build query
                query = select(BatchJob).where(BatchJob.batch_id == batch_id)

                # Add eager loading if requested
                query = query.options(
                    selectinload(BatchJob.jobs),
                    selectinload(BatchJob.domains)
                )

                # Execute query
                result = await session.execute(
                    query,
                    execution_options={
                        "no_parameters": True,  # Disable prepared statements for Supavisor
                        "statement_cache_size": 0  # Disable statement caching
                    }
                )
                return result.scalars().first()
            else:
                # Use the class method for simple lookups
                return await BatchJob.get_by_batch_id(session, batch_id)

        except Exception as e:
            logger.error(f"Error retrieving batch job by ID: {str(e)}")
            # Propagate exception to caller for proper transaction handling
            raise

# Create singleton instance
job_service = JobService()
