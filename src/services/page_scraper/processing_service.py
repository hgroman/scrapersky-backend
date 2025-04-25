"""
Page Processing Service

This service handles the processing of web pages, including:
- Domain validation and standardization
- Single domain scanning
- Batch domain scanning
- Job and batch status tracking

This service follows the transaction-aware pattern where it works with
transactions but does not create, commit, or rollback transactions itself.
Transaction boundaries are managed by the router.
"""

import logging
import traceback
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models import BatchJob, Domain, Job
from ...scraper.domain_utils import get_domain_url, standardize_domain
from ...scraper.metadata_extractor import detect_site_metadata
from ...services.core.validation_service import validation_service
from ...services.job_service import job_service

# Configure logger
logger = logging.getLogger(__name__)

class PageProcessingService:
    """
    Service for processing web pages, extracting metadata, and managing
    the scanning process for both individual domains and batches.

    This service is transaction-aware but doesn't manage transactions.
    Transaction boundaries are owned by the routers.
    """

    RESOURCE_TYPE = "sitemap"

    async def validate_domain(self, url: str) -> Tuple[bool, str, Optional[Domain]]:
        """
        Validate a domain URL and return a standardized Domain object.
        This is a PURE VALIDATION function that does no database queries.

        Args:
            url: The URL to validate

        Returns:
            Tuple containing (is_valid, message, domain_object)
        """
        try:
            # Validate URL format
            if not validation_service.validate_domain(url):
                return False, "Invalid domain format", None

            # Standardize domain - use the function from domain_utils directly
            # This is just string manipulation, no DB queries
            std_domain = standardize_domain(url)
            domain_url = get_domain_url(std_domain)

            # Create domain object IN MEMORY ONLY (not persisted to DB)
            # This will be used later to either look up or create the domain
            domain = Domain(
                domain=domain_url,
                status="pending"
            )

            return True, "Domain validated successfully", domain

        except Exception as e:
            logger.error(f"Error validating domain {url}: {str(e)}")
            return False, f"Domain validation error: {str(e)}", None

    async def initiate_domain_scan(
        self,
        session: AsyncSession,
        base_url: str,
        user_id: str,
        max_pages: int = 10,
        raw_sql: bool = True,
        no_prepare: bool = True,
        statement_cache_size: int = 0
    ) -> Dict[str, Any]:
        """
        Initiate a domain scan process.

        This method is transaction-aware but does not manage transactions.
        Transaction boundaries should be managed by the router.

        Args:
            session: Database session
            base_url: Base URL to scan
            user_id: User ID initiating the scan
            max_pages: Maximum number of pages to scan
            raw_sql: Use raw SQL instead of ORM
            no_prepare: Disable prepared statements
            statement_cache_size: Set statement cache size

        Returns:
            Dictionary with job_id and status_url
        """
        # Check if in transaction
        in_transaction = session.in_transaction()
        logger.debug(f"initiate_domain_scan transaction state: {in_transaction}")

        if not in_transaction:
            logger.warning("initiate_domain_scan called without an active transaction; the router should handle transactions")

        try:
            # Apply Supavisor compatibility options to the session
            logger.debug(f"Using Supavisor compatibility: no_prepare={no_prepare}, statement_cache_size={statement_cache_size}")

            # Ensure session has proper execution options for Supavisor compatibility
            execution_options = {
                "no_parameters": no_prepare,  # Disable prepared statements for Supavisor
                "statement_cache_size": statement_cache_size  # Disable statement caching
            }

            # Validate domain
            is_valid, message, domain_obj = await self.validate_domain(base_url)
            if not is_valid or not domain_obj:
                raise ValueError(message)

            # Check if domain already exists in database
            domain_url = domain_obj.domain

            # Use raw SQL text query instead of ORM to avoid prepared statement issues
            existing_domain_query = text("""
                SELECT * FROM domains
                WHERE domain = :domain_url
                LIMIT 1
            """)

            # Apply execution options to the query
            result = await session.execute(
                existing_domain_query,
                {"domain_url": domain_url},
                execution_options={
                    "no_parameters": no_prepare,
                    "statement_cache_size": statement_cache_size
                }
            )

            # Get first row if any
            row = result.first()
            if row:
                # Convert row to Domain object
                existing_domain = Domain()
                for key, value in row._mapping.items():
                    if hasattr(existing_domain, key):
                        setattr(existing_domain, key, value)
                logger.info(f"Domain {domain_url} already exists, using existing record")
                domain = existing_domain
                # Update status to pending for the new scan
                setattr(domain, 'status', "pending")
            else:
                logger.info(f"Creating new domain record for {domain_url}")
                domain = domain_obj
                session.add(domain)

            # Flush to ensure domain has an ID but don't commit - router owns transaction
            await session.flush()
            logger.debug(f"Domain id: {domain.id if domain else 'unknown'}")

            # Create job
            job = await job_service.create_for_domain(
                session=session,
                job_type=self.RESOURCE_TYPE,
                domain_id=domain.id if domain else None,
                created_by=user_id
            )

            # Extract job UUID - ONLY use job_id (UUID), never the numeric ID
            job_uuid = str(job.job_id) if job and hasattr(job, 'job_id') else None

            if not job_uuid:
                raise ValueError("Failed to generate valid job UUID")

            logger.debug(f"Job created with UUID: {job_uuid}")

            # Return job information with UUID
            # The actual domain processing will be handled by a background task in the router
            return {
                "job_id": job_uuid,
                "status_url": f"/api/v3/batch_page_scraper/status/{job_uuid}"
            }
        except Exception as e:
            logger.error(f"Error processing domain scan: {str(e)}")
            # Let the exception propagate to ensure proper transaction handling at the router level
            raise

    async def initiate_batch_scan(
        self,
        session: AsyncSession,
        domains: List[str],
        user_id: str = "system",
        max_pages: int = 1000,
        batch_id: Optional[str] = None,
        raw_sql: bool = True,
        no_prepare: bool = True,
        statement_cache_size: int = 0
    ) -> Dict[str, Any]:
        """
        Initiate a batch scan process.

        This method is transaction-aware but does not manage transactions.
        Transaction boundaries should be managed by the router.

        Args:
            session: Database session
            domains: List of domains to scan
            user_id: User ID initiating the scan
            max_pages: Maximum number of pages to scan
            batch_id: Optional batch ID (generated if not provided)
            raw_sql: Use raw SQL instead of ORM
            no_prepare: Disable prepared statements
            statement_cache_size: Set statement cache size

        Returns:
            Dictionary with batch_id and status_url
        """
        # Check if in transaction
        in_transaction = session.in_transaction()
        logger.debug(f"initiate_batch_scan transaction state: {in_transaction}")

        if not in_transaction:
            logger.warning("initiate_batch_scan called without an active transaction; the router should handle transactions")

        try:
            # Validate domains
            valid_domains = []
            for domain in domains:
                is_valid, message, domain_obj = await self.validate_domain(domain)
                if is_valid and domain_obj:
                    valid_domains.append(domain_obj.domain)
                else:
                    logger.warning(f"Invalid domain {domain}: {message}")

            if not valid_domains:
                raise ValueError("No valid domains provided")

            # Generate batch ID if not provided
            if not batch_id:
                batch_id = str(uuid.uuid4())

            logger.info(f"Creating batch {batch_id} with {len(valid_domains)} domains")

            # Create batch directly using BatchJob model instead of batch_functions.create_batch
            batch_uuid = uuid.UUID(str(batch_id))
            batch = await BatchJob.create_new_batch(
                session=session,
                batch_id=batch_uuid,
                processor_type="domain_batch",
                total_domains=len(valid_domains),
                created_by=str(user_id),
                options={"max_concurrent": 5},
                metadata={"domain_count": len(valid_domains)}
            )

            await session.flush()

            # Return batch information
            return {
                "batch_id": str(batch_id),
                "status_url": f"/api/v3/batch_page_scraper/batch/{batch_id}/status",
                "domains": valid_domains,
                "total_domains": len(valid_domains)
            }

        except Exception as e:
            logger.error(f"Error processing batch scan: {str(e)}")
            # Let the exception propagate to ensure proper transaction handling
            raise

    async def get_job_status(
        self,
        session: AsyncSession,
        job_id: Union[str, uuid.UUID, int]
    ) -> Dict[str, Any]:
        """
        Get the status of a job.

        Args:
            session: Database session
            job_id: ID of the job to check (can be string, UUID or integer)

        Returns:
            Dictionary with job status information
        """
        # Check if in transaction
        in_transaction = session.in_transaction()
        logger.debug(f"get_job_status transaction state: {in_transaction}")

        if not in_transaction:
            logger.warning("get_job_status called without an active transaction; the router should handle transactions")

        try:
            # Validate job ID
            try:
                if isinstance(job_id, str):
                    validation_service.validate_string_length(
                        job_id,
                        field_name="job_id",
                        min_length=1,
                        max_length=64
                    )
            except ValueError as e:
                raise ValueError(str(e))

            # Get job status from job service
            if isinstance(job_id, int) or (isinstance(job_id, str) and job_id.isdigit()):
                # Handle numeric job IDs with the direct numeric lookup
                numeric_id = int(job_id) if isinstance(job_id, str) else job_id
                job = await job_service.get_by_numeric_id(
                    session=session,
                    job_id=numeric_id,
                    load_relationships=True
                )
            elif isinstance(job_id, str) and len(job_id) >= 32 and '-' in job_id:
                # Looks like a UUID string, use the specialized UUID lookup
                job = await job_service.get_by_uuid(
                    session=session,
                    job_uuid=job_id
                )
            else:
                # Handle UUID or string job IDs with the regular lookup
                job = await job_service.get_by_id(
                    session=session,
                    job_id=job_id,
                    load_relationships=True
                )

            if not job:
                raise ValueError(f"Job not found: {job_id}")

            # Convert job object to dictionary
            progress_value = 0.0
            if hasattr(job, 'progress') and job.progress is not None:
                try:
                    # Convert progress to string first to handle Column types
                    progress_str = str(job.progress)
                    progress_value = float(progress_str)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert progress value to float: {job.progress}")

            # Handle metadata - ensure it's a dictionary
            metadata = {}
            if hasattr(job, 'metadata') and job.metadata:
                if isinstance(job.metadata, dict):
                    metadata = job.metadata
                else:
                    try:
                        # Try converting to dict if it's a MetaData object or similar
                        metadata = dict(job.metadata)
                    except (TypeError, ValueError):
                        logger.warning(f"Could not convert metadata to dictionary: {type(job.metadata)}")
                        metadata = {"original_type": str(type(job.metadata))}

            status = {
                "job_id": str(job.id),
                "status": job.status,
                "domain": job.domain.domain if hasattr(job, 'domain') and job.domain else None,
                "progress": progress_value,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                "result": job.result if hasattr(job, 'result') else None,
                "error": job.error if hasattr(job, 'error') else None,
                "metadata": metadata
            }

            return status

        except ValueError as ve:
            logger.error(f"Error getting job status: {str(ve)}")
            raise

        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            raise

    async def get_batch_status(
        self,
        session: AsyncSession,
        batch_id: str,
        raw_sql: bool = True,
        no_prepare: bool = True,
        statement_cache_size: int = 0
    ) -> Dict[str, Any]:
        """
        Get batch status.

        This method is transaction-aware but does not manage transactions.
        Transaction boundaries should be managed by the router.

        Args:
            session: Database session
            batch_id: Batch ID to check
            raw_sql: Use raw SQL instead of ORM
            no_prepare: Disable prepared statements
            statement_cache_size: Set statement cache size

        Returns:
            Dictionary with batch status information
        """
        # Check if in transaction
        in_transaction = session.in_transaction()
        logger.debug(f"get_batch_status transaction state: {in_transaction}")

        if not in_transaction:
            logger.warning("get_batch_status called without an active transaction; the router should handle transactions")

        try:
            # Convert batch_id to UUID
            batch_uuid = batch_id
            if isinstance(batch_id, str):
                try:
                    batch_uuid = uuid.UUID(batch_id)
                except ValueError:
                    logger.warning(f"Invalid UUID format for batch_id: {batch_id}")
                    return {
                        "batch_id": str(batch_id),
                        "status": "error",
                        "error": f"Invalid UUID format: {batch_id}"
                    }

            # Get batch using BatchJob class method instead of batch_functions.get_batch_status
            batch = await BatchJob.get_by_batch_id(session, batch_uuid)

            if not batch:
                logger.warning(f"Batch {batch_id} not found")
                return {
                    "batch_id": str(batch_id),
                    "status": "unknown",
                    "error": "Batch not found"
                }

            # Convert batch to dictionary
            batch_dict = batch.to_dict()

            return {
                "batch_id": batch_dict["batch_id"],
                "status": batch_dict["status"],
                "total_domains": batch_dict["total_domains"],
                "completed_domains": batch_dict["completed_domains"],
                "failed_domains": batch_dict["failed_domains"],
                "created_at": batch_dict.get("created_at"),
                "updated_at": batch_dict.get("updated_at"),
                "error": batch_dict.get("error")
            }

        except Exception as e:
            logger.error(f"Error getting batch status: {str(e)}")
            return {
                "batch_id": str(batch_id),
                "status": "error",
                "error": str(e)
            }

# Initialize the service
page_processing_service = PageProcessingService()
