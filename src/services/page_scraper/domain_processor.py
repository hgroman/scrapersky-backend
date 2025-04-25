"""
Domain Processor Module

This module contains functions for processing individual domains.
It's separated from the main processing service to avoid circular dependencies.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.future import select

from ...models import Domain, Job
from ...models.tenant import DEFAULT_TENANT_ID
from ...scraper.domain_utils import get_domain_url, standardize_domain
from ...scraper.metadata_extractor import detect_site_metadata
from ...session.async_session import get_background_session

logger = logging.getLogger(__name__)


async def process_domain_with_own_session(
    job_id: str, domain: str, user_id: Optional[str] = None, max_pages: int = 10
) -> None:
    """
    Process a single domain with isolated database sessions using ORM.
    Each step uses its own dedicated session.
    Args:
        job_id: Job ID string to process
        domain: Domain to process
        user_id: User ID processing the domain
        max_pages: Maximum pages to process
    """
    logger.info(f"Starting domain processing for {domain} (job: {job_id})")
    start_time = datetime.now(timezone.utc)
    domain_obj: Optional[Domain] = None  # Hold the domain object

    try:
        # Standardize domain
        std_domain = standardize_domain(domain)
        if not std_domain:
            raise ValueError(f"Invalid domain format after standardization: {domain}")
        domain_url = get_domain_url(std_domain)
        if not domain_url:
            raise ValueError(
                f"Could not convert standardized domain to URL: {std_domain}"
            )

        # Step 1: Get or create domain record using ORM
        domain_obj = await get_or_create_domain_orm(domain_url)
        if not domain_obj or not domain_obj.id:
            raise ValueError(f"Failed to get or create Domain object for {domain_url}")

        # Step 2: Update job to processing status using ORM
        metadata = {
            "start_time": start_time.isoformat(),
            "domain": domain_url,
            "max_pages": max_pages,
            "user_id": user_id,
        }
        await update_job_status_orm(
            job_id, "processing", domain_id=domain_obj.id, metadata=metadata
        )

        # Step 3: Process domain and extract metadata
        site_metadata = await detect_site_metadata(domain_url, max_pages)

        # Calculate processing duration
        end_time = datetime.now(timezone.utc)
        processing_time = (end_time - start_time).total_seconds()

        # Step 4: Update job with results using ORM
        result_metadata = {
            "processing_metrics": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "processing_time": processing_time,
                "domain": domain_url,
                "max_pages": max_pages,
            }
        }
        if site_metadata is not None:
            result_metadata["site_data"] = site_metadata
            await update_job_status_orm(
                job_id, "completed", result_data=result_metadata
            )
        else:
            # Include timing even on metadata extraction failure
            await update_job_status_orm(
                job_id,
                "failed",
                last_error="Failed to extract metadata from domain",
                result_data=result_metadata,
            )

        logger.info(
            f"Successfully completed processing domain {domain_url} (job: {job_id}) in {processing_time:.2f} seconds"
        )

    except Exception as e:
        end_time = datetime.now(timezone.utc)
        processing_time = (end_time - start_time).total_seconds()
        error_message = str(e)
        logger.error(
            f"Error processing domain {domain}: {error_message}", exc_info=True
        )

        # Update job status to failed using ORM
        error_metadata = {
            "processing_metrics": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "processing_time": processing_time,
                "domain": domain,  # Original domain might be useful here
                "max_pages": max_pages,
            },
            "error_details": {"message": error_message, "type": e.__class__.__name__},
        }
        # Ensure job_id is a string for the update function
        job_id_str = str(job_id) if isinstance(job_id, uuid.UUID) else job_id
        await update_job_status_orm(
            job_id_str, "failed", last_error=error_message, result_data=error_metadata
        )


async def get_or_create_domain_orm(domain_url: str) -> Optional[Domain]:
    """
    Get an existing domain record or create a new one using ORM.
    Uses its own session. Attempts atomic insert using ON CONFLICT.
    Always uses DEFAULT_TENANT_ID.
    Args:
        domain_url: Standardized domain URL
    Returns:
        The fetched or newly created Domain ORM object, or None on error.
    """
    try:
        async with get_background_session() as session:
            # Attempt to fetch existing first
            stmt_select = select(Domain).where(Domain.domain == domain_url)
            result = await session.execute(stmt_select)
            domain_obj = result.scalar_one_or_none()

            if domain_obj:
                logger.info(
                    f"Found existing domain record for {domain_url}, id: {domain_obj.id}"
                )
                return domain_obj
            else:
                # Attempt to insert, handling potential race condition
                logger.info(f"Domain {domain_url} not found, attempting to create.")
                try:
                    # Use pg_insert for ON CONFLICT DO NOTHING (or DO UPDATE)
                    # Ensure your Domain model has a unique constraint on 'domain' column
                    insert_stmt = (
                        pg_insert(Domain)
                        .values(
                            domain=domain_url,
                            status="pending",  # Default status
                            tenant_id=DEFAULT_TENANT_ID,
                            created_at=datetime.now(timezone.utc),
                            updated_at=datetime.now(timezone.utc),
                        )
                        .on_conflict_do_nothing(index_elements=["domain"])
                    )
                    # If using ON CONFLICT DO UPDATE, syntax is different
                    # .on_conflict_do_update(index_elements=['domain'], set_=dict(updated_at=datetime.now(timezone.utc)))

                    await session.execute(insert_stmt)
                    await session.commit()  # Commit the insert attempt

                    # Re-fetch the domain, it should exist now either via insert or conflict
                    result_refetch = await session.execute(
                        stmt_select
                    )  # Reuse select statement
                    domain_obj_refetched = result_refetch.scalar_one_or_none()

                    if domain_obj_refetched:
                        logger.info(
                            f"Successfully created or found domain for {domain_url} after insert attempt, id: {domain_obj_refetched.id}"
                        )
                        return domain_obj_refetched
                    else:
                        logger.error(
                            f"CRITICAL: Domain {domain_url} not found even after INSERT attempt."
                        )
                        return None

                except Exception as insert_exc:
                    await session.rollback()  # Rollback on insert error
                    logger.error(
                        f"Error during domain insert for {domain_url}: {insert_exc}",
                        exc_info=True,
                    )
                    return None  # Indicate failure

    except Exception as e:
        logger.error(
            f"Error in get_or_create_domain_orm for {domain_url}: {e}", exc_info=True
        )
        return None


async def update_job_status_orm(
    job_id: str,
    status: str,
    domain_id: Optional[uuid.UUID] = None,
    metadata: Optional[Dict[str, Any]] = None,  # Added for consistency
    result_data: Optional[Dict[str, Any]] = None,
    last_error: Optional[str] = None,
) -> None:
    """
    Update job status, domain_id, metadata, result_data, and last_error using ORM.
    Uses its own session.
    Args:
        job_id: Job ID string to update.
        status: New status string.
        domain_id: Optional UUID of the associated Domain.
        metadata: Optional dict for the metadata field.
        result_data: Optional dict for the result_data field.
        last_error: Optional string for the last_error field.
    """
    try:
        # Ensure job_id is UUID if possible, handle potential errors
        job_uuid: Optional[uuid.UUID] = None
        try:
            job_uuid = uuid.UUID(job_id)
        except ValueError:
            logger.error(f"Invalid job_id format: {job_id}. Cannot update job.")
            return

        async with get_background_session() as session:
            async with session.begin():  # Use transaction block for the update
                stmt = select(Job).where(Job.job_id == job_uuid)
                result = await session.execute(stmt)
                job = result.scalar_one_or_none()

                if not job:
                    logger.error(f"Job not found with job_id: {job_id}")
                    return

                # Update fields selectively
                job.status = status
                job.updated_at = datetime.now(timezone.utc)
                if domain_id is not None:
                    job.domain_id = domain_id
                if metadata is not None:
                    job.metadata = metadata
                if result_data is not None:
                    job.result_data = result_data
                if last_error is not None:
                    job.last_error = last_error
                else:
                    # Clear last_error if status is not 'failed' or 'error'?
                    if status not in ["failed", "error"]:
                        job.last_error = None

                session.add(job)  # Mark job as dirty
                await (
                    session.flush()
                )  # Optional: flush to see changes immediately if needed

            # Session commits automatically here via session.begin()
            logger.debug(f"Updated job {job_id} status to {status}")

    except Exception as e:
        logger.error(f"Error updating job {job_id}: {e}", exc_info=True)
