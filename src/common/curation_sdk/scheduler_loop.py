# src/common/curation_sdk/scheduler_loop.py

"""Provides a reusable job loop for scheduler tasks polling for queued items."""

import logging
from enum import Enum
from typing import Any, Callable, Coroutine, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import Column, ColumnElement, asc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect as sqlainspect
from sqlalchemy.orm import DeclarativeBase

# Assuming database module is accessible from src
# from src.db.database import (
#     get_background_session,  # Linter might flag this, assume project structure is correct
# )
from src.db.session import get_session

# from src.common.curation_sdk.status_queue_helper import set_processing, set_failed # Potential usage

logger = logging.getLogger(__name__)


# Define a generic type variable constrained to models with an 'id' attribute
# Using Any for Column type to simplify generic typing, actual type is UUID
class HasId(DeclarativeBase):
    id: Column[Any]


T = TypeVar("T", bound=HasId)


async def run_job_loop(
    model: Type[T],
    status_enum: Type[Enum],
    queued_status: Enum,
    processing_status: Enum,
    completed_status: Enum,  # Passed for potential use in processing_function
    failed_status: Enum,
    processing_function: Callable[
        [UUID, AsyncSession], Coroutine[Any, Any, None]
    ],  # Expects ID, session
    batch_size: int,
    order_by_column: Optional[ColumnElement] = None,  # e.g., model.updated_at
    status_field_name: str = "status",
    error_field_name: str = "error",
) -> None:
    """Generic loop to fetch items, mark as processing, then process each individually."""
    fetch_session: Optional[AsyncSession] = None
    items_to_process_ids: List[UUID] = []
    initial_item_count = 0
    items_processed_successfully = 0
    items_failed = 0

    try:
        # Phase 1: Fetch and Mark as Processing (Single Transaction)
        fetch_session = await get_session()
        if fetch_session is None:
            logger.error(
                "SCHEDULER_LOOP: Failed to obtain background database session "
                "for fetching."
            )
            return

        async with fetch_session.begin():
            stmt = (
                select(model.id)  # Select only IDs initially
                .where(getattr(model, status_field_name) == queued_status)
                .limit(batch_size)
            )
            mapper = sqlainspect(model)
            has_updated_at = "updated_at" in mapper.columns

            if order_by_column is not None:
                stmt = stmt.order_by(order_by_column)
            elif has_updated_at:
                stmt = stmt.order_by(asc(model.updated_at))  # type: ignore

            result = await fetch_session.execute(stmt)
            items_to_process_ids = list(result.scalars().all())
            initial_item_count = len(items_to_process_ids)

            if not items_to_process_ids:
                logger.debug(
                    f"SCHEDULER_LOOP: No {model.__name__} items found with status "
                    f"{queued_status}. Loop finished."
                )
                return

            logger.info(
                f"SCHEDULER_LOOP: Found {initial_item_count} {model.__name__} items with "
                f"status {queued_status}. Marking as Processing."
            )

            # Mark selected items as Processing
            if items_to_process_ids:
                update_stmt = (
                    update(model)
                    .where(model.id.in_(items_to_process_ids))
                    .values(
                        **{
                            status_field_name: processing_status,
                            error_field_name: None,  # Clear previous error
                        }
                    )
                    .execution_options(
                        synchronize_session=False
                    )  # Important for bulk update
                )
                await fetch_session.execute(update_stmt)
                # Commit happens automatically on exiting fetch_session.begin()

    except Exception as fetch_err:
        logger.exception(
            f"SCHEDULER_LOOP: Error during fetch/mark phase for "
            f"{model.__name__}: {fetch_err}"
        )
        # Do not proceed if fetching/marking failed
        return
    finally:
        if fetch_session:
            await fetch_session.close()

    # Phase 2: Process Each Item Individually (Separate Transactions)
    logger.info(
        f"SCHEDULER_LOOP: Starting individual processing for "
        f"{initial_item_count} {model.__name__} items."
    )
    for item_id in items_to_process_ids:
        item_session: Optional[AsyncSession] = None
        try:
            item_session = await get_session()
            if item_session is None:
                logger.error(
                    f"SCHEDULER_LOOP: Failed to get session for processing item "
                    f"{item_id}. Skipping."
                )
                items_failed += 1
                continue

            logger.info(f"SCHEDULER_LOOP: Processing {model.__name__} ID: {item_id}")
            # The processing_function is responsible for its own transaction(s)
            # and setting the final Completed status internally.
            await processing_function(item_id, item_session)
            items_processed_successfully += 1

        except Exception as process_err:
            items_failed += 1
            # Use logger.exception to include traceback
            logger.exception(
                f"SCHEDULER_LOOP: Error processing {model.__name__} ID "
                f"{item_id}: {process_err}"
            )
            # Attempt to mark as Failed in a *separate* error-handling transaction
            error_session: Optional[AsyncSession] = None
            try:
                error_session = await get_session()
                if error_session is None:
                    logger.error(
                        f"SCHEDULER_LOOP: Failed to get error session for item "
                        f"{item_id}. Cannot mark as Failed."
                    )
                    continue  # Skip marking failed if we can't get a session

                async with error_session.begin():
                    failed_item_update_stmt = (
                        update(model)
                        .where(model.id == item_id)
                        .values(
                            **{
                                status_field_name: failed_status,
                                error_field_name: str(process_err)[:1024],  # Truncate
                            }
                        )
                        .execution_options(synchronize_session=False)
                    )
                    await error_session.execute(failed_item_update_stmt)
                logger.warning(
                    f"SCHEDULER_LOOP: Marked {model.__name__} ID {item_id} as "
                    f"Failed due to error."
                )
            except Exception as update_err:
                logger.exception(
                    f"SCHEDULER_LOOP: CRITICAL - Failed to mark {model.__name__} "
                    f"ID {item_id} as Failed: {update_err}"
                )
            finally:
                if error_session:
                    await error_session.close()
        finally:
            # Ensure the main processing session for the item is closed
            if item_session:
                await item_session.close()

    logger.info(
        f"SCHEDULER_LOOP: Finished processing batch for {model.__name__}. "
        f"Success: {items_processed_successfully}, Failed: {items_failed}, "
        f"Total Attempted: {initial_item_count}."
    )


# Example Usage (Conceptual - requires actual models/enums/service)
# async def my_processing_function(item_id: UUID, session: AsyncSession):
#     async with session.begin():
#         item = await session.get(MyModel, item_id)
#         # ... do work ...
#         item.status = MyStatusEnum.Completed
#
# async def schedule_my_job():
#     await run_job_loop(
#         model=MyModel,
#         status_enum=MyStatusEnum,
#         queued_status=MyStatusEnum.Queued,
#         processing_status=MyStatusEnum.Processing,
#         completed_status=MyStatusEnum.Completed,
#         failed_status=MyStatusEnum.Failed,
#         processing_function=my_processing_function,
#         batch_size=10,
#         order_by_column=asc(MyModel.updated_at)
#     )
