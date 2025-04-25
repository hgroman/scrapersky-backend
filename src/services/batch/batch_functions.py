"""
Batch Processor Functions

This module contains the core functions for batch processing operations.
It's separated from the main batch processor service to avoid circular dependencies.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Optional, cast

from sqlalchemy import func

from ...models import BatchJob
from ...session.async_session import get_background_session
from ..page_scraper.domain_processor import process_domain_with_own_session
from .types import (
    BATCH_STATUS_COMPLETED,
    BATCH_STATUS_ERROR,
    BATCH_STATUS_FAILED,
    BATCH_STATUS_PENDING,
    BATCH_STATUS_PROCESSING,
    BATCH_STATUS_UNKNOWN,
    BatchId,
    BatchOptions,
    BatchResult,
    BatchStatus,
    DomainList,
    Session,
    UserId,
)

logger = logging.getLogger(__name__)


async def create_batch(
    session: Session,
    batch_id: BatchId,
    domains: DomainList,
    user_id: UserId,
    options: Optional[BatchOptions] = None,
) -> BatchResult:
    """
    Create a new batch with the provided domains.

    This method is transaction-aware but does not manage transactions.
    Transaction boundaries should be managed by the router.

    Args:
        session: AsyncSession for database operations
        batch_id: UUID for the batch (string format, will be converted to UUID)
        domains: List of domains to process
        user_id: User ID creating the batch
        options: Optional configuration for batch processing

    Returns:
        BatchResult with batch information
    """
    logger.info(f"Creating batch {batch_id} with {len(domains)} domains")

    # Default options
    if options is None:
        options = cast(BatchOptions, {"max_concurrent": 5, "test_mode": False})

    max_concurrent = options.get("max_concurrent", 5)

    # Convert batch_id string to UUID object
    batch_id_uuid = uuid.UUID(str(batch_id))

    # Create batch record using the class method
    batch = await BatchJob.create_new_batch(
        session=session,
        batch_id=batch_id_uuid,
        processor_type="domain_batch",
        total_domains=len(domains),
        created_by=str(user_id),
        options={"max_concurrent": max_concurrent},
        metadata={"domain_count": len(domains)},
    )

    await session.flush()

    return cast(
        BatchResult,
        {
            "batch_id": str(batch_id),
            "status": BATCH_STATUS_PENDING,
            "total_domains": len(domains),
            "completed_domains": 0,
            "failed_domains": 0,
            "results": [],
            "error": None,
        },
    )


async def get_batch_status(session: Session, batch_id: BatchId) -> BatchStatus:
    """
    Get the status of a batch.

    This method is transaction-aware but does not manage transactions.
    Transaction boundaries should be managed by the router.

    Args:
        session: AsyncSession for database operations
        batch_id: Batch ID to check (string that will be converted to UUID)

    Returns:
        BatchStatus with batch status information
    """
    logger.info(f"Getting status for batch {batch_id}")

    try:
        # Convert batch_id to UUID object if needed
        batch_uuid = batch_id
        if isinstance(batch_id, str):
            try:
                batch_uuid = uuid.UUID(batch_id)
            except ValueError:
                logger.warning(f"Invalid UUID format for batch_id: {batch_id}")
                return cast(
                    BatchStatus,
                    {
                        "batch_id": str(batch_id),
                        "status": BATCH_STATUS_ERROR,
                        "total_domains": 0,
                        "completed_domains": 0,
                        "failed_domains": 0,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "error": f"Invalid UUID format: {batch_id}",
                    },
                )

        # Get batch using the class method
        batch = await BatchJob.get_by_batch_id(session, batch_uuid)

        if not batch:
            logger.warning(f"Batch {batch_id} not found")
            return cast(
                BatchStatus,
                {
                    "batch_id": str(batch_id),
                    "status": BATCH_STATUS_UNKNOWN,
                    "total_domains": 0,
                    "completed_domains": 0,
                    "failed_domains": 0,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "error": "Batch not found",
                },
            )

        # Use to_dict to handle SQLAlchemy Column types
        batch_dict = batch.to_dict()

        # Calculate progress percentage
        total = batch_dict.get("total_domains", 0)
        completed = batch_dict.get("completed_domains", 0)
        failed = batch_dict.get("failed_domains", 0)

        progress = 0.0
        if total > 0:
            progress = (completed + failed) / total

        # Calculate processing time if possible
        processing_time = None
        start_time = batch_dict.get("start_time")
        end_time = batch_dict.get("end_time")

        if start_time:
            if end_time:
                # Calculate from start to end time
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(
                        start_time.replace("Z", "+00:00")
                    )
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                processing_time = (end_time - start_time).total_seconds()
            else:
                # Calculate from start to now
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(
                        start_time.replace("Z", "+00:00")
                    )
                processing_time = (datetime.utcnow() - start_time).total_seconds()

        # Extract domain statuses from metadata
        domain_statuses = {}
        metadata = batch_dict.get("batch_metadata", {}) or {}
        if isinstance(metadata, dict) and "domain_results" in metadata:
            domain_statuses = metadata["domain_results"]

        return cast(
            BatchStatus,
            {
                "batch_id": str(batch_dict["batch_id"]),
                "status": batch_dict["status"],
                "total_domains": total,
                "completed_domains": completed,
                "failed_domains": failed,
                "progress": progress,
                "created_at": batch_dict.get("created_at", datetime.utcnow()),
                "updated_at": batch_dict.get("updated_at", datetime.utcnow()),
                "start_time": start_time,
                "end_time": end_time,
                "processing_time": processing_time,
                "domain_statuses": domain_statuses,
                "error": batch_dict.get("error"),
                "metadata": metadata,
            },
        )
    except Exception as e:
        logger.error(f"Error getting batch status: {str(e)}", exc_info=True)
        return cast(
            BatchStatus,
            {
                "batch_id": str(batch_id),
                "status": BATCH_STATUS_ERROR,
                "total_domains": 0,
                "completed_domains": 0,
                "failed_domains": 0,
                "progress": 0.0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "error": str(e),
            },
        )


async def process_batch_with_own_session(
    batch_id: BatchId, domains: DomainList, user_id: UserId, max_pages: int = 1000
) -> None:
    """
    Process a batch of domains with its own database session.
    This function creates its own session and manages its own transaction boundaries.

    When called from FastAPI's BackgroundTasks, it ensures proper SQLAlchemy async context.

    Args:
        batch_id: Batch ID to process
        domains: List of domains to process
        user_id: User ID processing the batch
        max_pages: Maximum pages to process per domain
    """
    logger.info(f"Starting batch processing for {len(domains)} domains")
    logger.info(f"DEBUGGING DOMAINS LIST: {domains}")

    # Create diagnostic file for debugging
    diagnostic_dir = "/tmp/scraper_sky_task_markers"
    os.makedirs(diagnostic_dir, exist_ok=True)
    diagnostic_file = f"{diagnostic_dir}/batch_processor_{batch_id}.txt"

    with open(diagnostic_file, "w") as f:
        f.write(f"Starting batch processing at {datetime.utcnow().isoformat()}\n")
        f.write(f"batch_id: {batch_id}\n")
        f.write(f"domain_count: {len(domains)}\n")
        f.write(f"domains: {','.join(domains)}\n")
        f.write(f"user_id: {user_id}\n")
        f.write(f"max_pages: {max_pages}\n")

    # First, update the batch status to processing
    try:
        # First try to get and update the batch status to processing
        async with get_background_session() as session:
            batch = await BatchJob.get_by_batch_id(session, batch_id)
            if batch:
                batch.status = BATCH_STATUS_PROCESSING
                batch.start_time = func.now()
                await session.flush()
                logger.info(f"Updated batch {batch_id} status to processing")
    except Exception as e:
        logger.error(
            f"Error updating batch status to processing: {str(e)}", exc_info=True
        )
        # Continue processing even if update fails

    # Track domain processing results
    domain_results = {}
    start_time = datetime.utcnow().isoformat()

    # Define domain processor function
    async def process_single_domain(domain: str):
        domain_start_time = datetime.utcnow()
        try:
            # Process domain with its own session
            job_id = str(uuid.uuid4())
            await process_domain_with_own_session(
                domain=domain, job_id=job_id, user_id=str(user_id), max_pages=max_pages
            )

            # Domain processed successfully
            domain_end_time = datetime.utcnow()
            processing_time = (domain_end_time - domain_start_time).total_seconds()

            # Store comprehensive result information
            result = {
                "status": "completed",
                "job_id": job_id,
                "start_time": domain_start_time.isoformat(),
                "end_time": domain_end_time.isoformat(),
                "processing_time": processing_time,
                "error": None,
            }
            logger.info(
                f"Successfully processed domain {domain} in {processing_time:.2f} seconds"
            )
            return (domain, result, True)  # True means success

        except Exception as e:
            # Domain processing failed
            domain_end_time = datetime.utcnow()
            processing_time = (domain_end_time - domain_start_time).total_seconds()

            # Store comprehensive error information
            result = {
                "status": "failed",
                "job_id": job_id if "job_id" in locals() else None,
                "start_time": domain_start_time.isoformat(),
                "end_time": domain_end_time.isoformat(),
                "processing_time": processing_time,
                "error": str(e),
            }
            logger.error(f"Error processing domain {domain}: {str(e)}", exc_info=True)
            return (domain, result, False)  # False means failure

    # Process domains concurrently with a limit on concurrency
    max_concurrent = 5  # Limit concurrent processing
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(domain):
        async with semaphore:
            return await process_single_domain(domain)

    # Start concurrent processing
    tasks = [process_with_semaphore(domain) for domain in domains]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    completed_count = 0
    failed_count = 0

    for result in results:
        if isinstance(result, Exception) or isinstance(result, BaseException):
            # Handle task exceptions
            logger.error(f"Task exception: {str(result)}")
            failed_count += 1
            continue

        domain, domain_result, success = result
        domain_results[domain] = domain_result

        if success:
            completed_count += 1
        else:
            failed_count += 1

        # Update batch progress periodically
        try:
            async with get_background_session() as session:
                batch = await BatchJob.get_by_batch_id(session, batch_id)
                if batch:
                    batch.update_progress(
                        completed=completed_count, failed=failed_count
                    )

                    # Update metadata with results
                    batch_dict = batch.to_dict()
                    metadata = batch_dict.get("batch_metadata") or {}
                    if not isinstance(metadata, dict):
                        metadata = {}
                    metadata["domain_results"] = domain_results
                    metadata["last_updated"] = datetime.utcnow().isoformat()
                    batch.batch_metadata = metadata

                    # Store the most recent error if any
                    if not success:
                        error_msg = domain_result.get("error", "Unknown error")
                        batch.error = f"Error processing domain {domain}: {error_msg}"

                    await session.flush()
        except Exception as update_error:
            logger.error(
                f"Error updating batch progress for {domain}: {str(update_error)}"
            )

    # Update final batch status
    try:
        async with get_background_session() as session:
            batch = await BatchJob.get_by_batch_id(session, batch_id)
            if batch:
                # Determine final status
                if completed_count > 0 and failed_count == 0:
                    final_status = BATCH_STATUS_COMPLETED
                elif completed_count == 0 and failed_count > 0:
                    final_status = BATCH_STATUS_FAILED
                else:
                    final_status = BATCH_STATUS_COMPLETED  # Partial success

                # Update batch
                batch.status = final_status
                batch.end_time = func.now()

                # Update metadata with domain results
                batch_dict = batch.to_dict()
                metadata = batch_dict.get("batch_metadata") or {}
                if not isinstance(metadata, dict):
                    metadata = {}
                metadata["domain_results"] = domain_results
                metadata["last_updated"] = datetime.utcnow().isoformat()
                batch.batch_metadata = metadata

                await session.flush()
                logger.info(
                    f"Batch {batch_id} processing complete: {completed_count} succeeded, {failed_count} failed"
                )
    except Exception as e:
        logger.error(f"Error updating final batch status: {str(e)}", exc_info=True)

    logger.info(f"Batch processing completed for batch {batch_id}")
