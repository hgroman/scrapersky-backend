"""
Batch processor service for handling batch scraping operations.

This module provides high-level business logic for batch processing,
coordinating between components and managing background tasks.
"""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional, cast
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.batch.batch_functions import (
    create_batch,
    get_batch_status,
    process_batch_with_own_session,
)
from src.services.batch.types import (
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
    DomainResult,
    Session,
    UserId,
)

logger = logging.getLogger(__name__)

async def initiate_batch_processing(
    session: Session,
    domains: DomainList,
    user_id: UserId,
    options: Optional[BatchOptions] = None,
) -> BatchResult:
    """
    Initiate batch processing for a list of domains.

    Args:
        session: Database session
        domains: List of domains to process
        user_id: User ID initiating the batch
        options: Optional batch processing options

    Returns:
        BatchResult containing batch ID and initial status
    """
    try:
        # Generate new batch ID
        batch_id = str(uuid.uuid4())

        # Create batch record
        batch_result = await create_batch(
            session=session,
            batch_id=batch_id,
            domains=domains,
            user_id=user_id,
            options=options,
        )

        # Note: Background processing is now handled by the router
        # to ensure proper async context for SQLAlchemy operations

        return batch_result

    except Exception as e:
        logger.error(f"Failed to initiate batch processing: {str(e)}")
        raise

async def get_batch_progress(
    session: Session,
    batch_id: BatchId,
) -> BatchStatus:
    """
    Get the current progress of a batch job.

    Args:
        session: Database session
        batch_id: UUID of the batch job

    Returns:
        BatchStatus containing current status and progress
    """
    try:
        return await get_batch_status(
            session=session,
            batch_id=batch_id,
        )

    except Exception as e:
        logger.error(f"Failed to get batch progress: {str(e)}")
        raise

async def cancel_batch(
    session: Session,
    batch_id: BatchId,
) -> BatchStatus:
    """
    Cancel a batch job.

    Args:
        session: Database session
        batch_id: UUID of the batch job

    Returns:
        BatchStatus containing final status
    """
    try:
        # Get current status
        batch = await get_batch_status(
            session=session,
            batch_id=batch_id,
        )

        # Only allow cancellation of pending or processing jobs
        if batch["status"] not in [BATCH_STATUS_PENDING, BATCH_STATUS_PROCESSING]:
            raise ValueError(f"Cannot cancel batch in status: {batch['status']}")

        # Update status to error
        batch["status"] = BATCH_STATUS_ERROR
        batch["error"] = "Batch cancelled by user"

        return batch

    except Exception as e:
        logger.error(f"Failed to cancel batch: {str(e)}")
        raise
