# Example File: src/services/{workflow_name}_scheduler.py
import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_background_session
from src.config.settings import settings

from src.models.{source_table_name} import {SourceTableTitleCase}
from src.models.{source_table_name} import {WorkflowNameTitleCase}ProcessingStatus
from src.services.{workflow_name}_service import process_single_{source_table_name}_for_{workflow_name}

logger = logging.getLogger(__name__)

SCHEDULER_BATCH_SIZE = getattr(settings, f"{{workflow_name.upper()}}_SCHEDULER_BATCH_SIZE", 10)

async def process_{workflow_name}_queue():
    """
    Scheduler job to find {source_table_name} records queued for {workflow_name} processing
    and trigger the processing for each.
    """
    session: AsyncSession = await get_background_session()
    processed_ids = []
    try:
        async with session.begin():
            stmt = (
                select({SourceTableTitleCase})
                .where({SourceTableTitleCase}.{workflow_name}_processing_status == {WorkflowNameTitleCase}ProcessingStatus.Queued)
                .with_for_update(skip_locked=True)
                .limit(SCHEDULER_BATCH_SIZE)
            )
            result = await session.execute(stmt)
            records_to_process = result.scalars().all()

            if not records_to_process:
                return

            record_ids = [record.id for record in records_to_process]
            logger.info(f"Found {len(record_ids)} {source_table_name}s queued for {workflow_name}. Locking and marking as Processing.")

            update_stmt = (
                update({SourceTableTitleCase})
                .where({SourceTableTitleCase}.id.in_(record_ids))
                .values({workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Processing)
            )
            await session.execute(update_stmt)
            processed_ids = record_ids

        logger.info(f"Processing {len(processed_ids)} {source_table_name} records for {workflow_name}...")
        for record_id in processed_ids:
            item_session: AsyncSession = await get_background_session()
            try:
                await process_single_{source_table_name}_for_{workflow_name}(item_session, record_id)
                logger.debug(f"Successfully processed {source_table_name} {record_id} for {workflow_name}.")
            except Exception as item_error:
                logger.exception(f"Error processing {source_table_name} {record_id} for {workflow_name}: {item_error}", exc_info=True)
                try:
                    async with item_session.begin():
                        error_stmt = (
                            update({SourceTableTitleCase})
                            .where({SourceTableTitleCase}.id == record_id)
                            .values(
                                {workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Error,
                                {workflow_name}_processing_error=str(item_error)[:1000]
                            )
                        )
                        await item_session.execute(error_stmt)
                except Exception as update_err:
                     logger.error(f"Failed to update error status for {source_table_name} {record_id}: {update_err}")
            finally:
                 await item_session.close()

    except Exception as main_error:
        logger.exception(f"Error in {workflow_name} scheduler main loop: {main_error}", exc_info=True)
    finally:
        await session.close()

from apscheduler.schedulers.asyncio import AsyncIOScheduler

def setup_{workflow_name}_scheduler(scheduler: AsyncIOScheduler) -> None:
    """
    Adds the {workflow_name} processing job to the APScheduler instance.
    """
    job_id = f"{workflow_name}_scheduler"
    interval_minutes = getattr(settings, f"{{workflow_name.upper()}}_SCHEDULER_INTERVAL_MINUTES", 1)

    scheduler.add_job(
        process_{workflow_name}_queue,
        trigger='interval',
        minutes=interval_minutes,
        id=job_id,
        replace_existing=True,
        max_instances=1
    )
    logger.info(f"Scheduled job '{job_id}' to run every {interval_minutes} minutes.")
