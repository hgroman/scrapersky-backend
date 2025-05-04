# src/common/curation_sdk/status_queue_helper.py

"""
Helpers for standardized status updates in curation workflows, particularly
for the initial queuing step often triggered by API routers.

Note: When implementing helpers that perform direct database updates
(e.g., using SQLAlchemy Core or raw SQL outside the ORM), ensure that
Enum members are passed as their `.value` attribute to avoid database
compatibility issues. See `Docs/Docs_1_AI_GUIDES/26-Supplemental.md`.
The ORM typically handles Enum conversion automatically when setting attributes.
"""

import logging
from enum import Enum
from typing import Any, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import select

logger = logging.getLogger(__name__)


# Define a generic type variable constrained to models with an 'id' attribute
class HasIdRequired(DeclarativeBase):
    id: Column[Any]
    # Add other potentially common fields if needed, e.g., updated_at, updated_by


T = TypeVar("T", bound=HasIdRequired)


async def update_status_and_queue(
    session: AsyncSession,
    model_class: Type[T],
    item_ids: List[UUID],
    curation_status_field: str,
    curation_status_value: Enum,
    queue_status_field: str,
    queue_status_value: Enum,
    error_field: Optional[str] = None,  # Optional field to clear errors
    # user_id: Optional[UUID] = None # Optional user performing the action
) -> int:
    """
    Updates the curation status and queues items by setting a queue status.

    Designed for use primarily within API router transactions when a user action
    (like setting status to 'Selected') should trigger background processing.

    Args:
        session: The active SQLAlchemy AsyncSession (managed by the caller, typically router).
        model_class: The SQLAlchemy model class to update.
        item_ids: A list of primary key UUIDs for the items to update.
        curation_status_field: The name of the main status field being set (e.g., 'status').
        curation_status_value: The Enum member for the main status (e.g., PlaceStatusEnum.Selected).
        queue_status_field: The name of the field indicating queue status for the next step (e.g., 'domain_extraction_status').
        queue_status_value: The Enum member to set the queue status to (e.g., DomainExtractionStatusEnum.Queued).
        error_field: Optional name of an error message field to clear during queueing.
        # user_id: Optional UUID of the user performing the update (for updated_by field).

    Returns:
        The number of items successfully updated (or attempted).
    """
    if not item_ids:
        return 0

    updated_count = 0
    try:
        # Fetch items to update first
        stmt = select(model_class).where(model_class.id.in_(item_ids))
        result = await session.execute(stmt)
        items_to_update: List[T] = list(result.scalars().all())

        if not items_to_update:
            logger.warning(
                f"No items found for IDs {item_ids} in {model_class.__name__} for status update."
            )
            return 0

        for item in items_to_update:
            setattr(item, curation_status_field, curation_status_value)
            setattr(item, queue_status_field, queue_status_value)
            if error_field and hasattr(item, error_field):
                setattr(item, error_field, None)
            # TODO: Add logic for updated_at, updated_by if fields exist and user_id is passed
            # if user_id and hasattr(item, 'updated_by'):
            #     setattr(item, 'updated_by', user_id)
            # if hasattr(item, 'updated_at'):
            #     setattr(item, 'updated_at', func.now()) # Use func.now() for DB timestamp
            updated_count += 1

        # Changes are flushed automatically by the calling router's session.begin() context manager
        # or require an explicit flush if needed before commit.
        # await session.flush() # Only if subsequent logic in the same transaction needs it

        logger.info(
            f"Prepared {updated_count}/{len(item_ids)} items of {model_class.__name__} for status update and queueing."
        )
        return updated_count

    except Exception as e:
        logger.exception(
            f"Error during update_status_and_queue for {model_class.__name__} IDs {item_ids}: {e}"
        )
        # Do not rollback here, let the calling router handle transaction rollback.
        raise  # Re-raise the exception


# TODO: Implement helper functions if needed, e.g.:
# async def set_processing(session: AsyncSession, item: Any, status_field: str, processing_status: Enum):
#     # ... Ensure processing_status.value is used if not using ORM attribute setting
#     pass
# async def set_completed(session: AsyncSession, item: Any, status_field: str, completed_status: Enum):
#     # ... Ensure completed_status.value is used if not using ORM attribute setting
#     pass
# async def set_failed(session: AsyncSession, item: Any, status_field: str, error_field: str, failed_status: Enum, error_message: str):
#     # ... Ensure failed_status.value is used if not using ORM attribute setting
#     pass

pass  # Placeholder
