# Example File: src/services/{workflow_name}_service.py
import logging
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.{source_table_name} import {SourceTableTitleCase}
from src.models.{source_table_name} import {WorkflowNameTitleCase}ProcessingStatus
# If creating new records (Option B), import destination model and its TitleCase version:
# from src.models.{destination_table_name} import {DestinationTableTitleCase}
# import uuid # Needed for Option B
# from typing import List, Dict # For perform_custom_extraction type hint

logger = logging.getLogger(__name__)

async def process_single_{source_table_name}_for_{workflow_name}(
    session: AsyncSession,
    record_id: UUID,
) -> None:
    """
    Processes a single {source_table_name} record for the {workflow_name} workflow.
    Handles transaction management for this specific record.
    """
    try:
        stmt = select({SourceTableTitleCase}).where({SourceTableTitleCase}.id == record_id)
        result = await session.execute(stmt)
        source_record = result.scalars().first()

        if not source_record:
            logger.warning(f"{workflow_name} processing: {SourceTableTitleCase} with ID {record_id} not found.")
            return

        if source_record.{workflow_name}_processing_status != {WorkflowNameTitleCase}ProcessingStatus.Processing:
            logger.warning(f"{workflow_name} processing: {SourceTableTitleCase} {record_id} status changed "
                           f"to {source_record.{workflow_name}_processing_status}. Skipping.")
            return

        logger.debug(f"Performing {workflow_name} processing for {source_table_name} {record_id}...")
        # extracted_data = await perform_custom_extraction(source_record)

        async with session.begin():
            logger.debug(f"Updating {source_table_name} {record_id} status to Completed for {workflow_name}.")
            final_update_stmt = (
                update({SourceTableTitleCase})
                .where({SourceTableTitleCase}.id == record_id)
                .values(
                    {workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Completed,
                    {workflow_name}_processing_error=None
                    # {workflow_name}_curation_status = {WorkflowNameTitleCase}CurationStatus.Processed
                )
            )
            await session.execute(final_update_stmt)

            # --- Option B: Create New Records in Destination Table ---
            # import uuid # Ensure uuid is imported if this option is used
            # logger.debug(f"Creating {destination_table_name} records for {source_table_name} {record_id}...")
            # for item_data in extracted_data: # extracted_data from perform_custom_extraction
            #     new_record = {DestinationTableTitleCase}(
            #         id=uuid.uuid4(),
            #         {source_table_name}_id=record_id,
            #         **item_data
            #     )
            #     session.add(new_record)
            #
            # final_update_stmt_option_b = (
            #     update({SourceTableTitleCase})
            #     .where({SourceTableTitleCase}.id == record_id)
            #     .values(
            #         {workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Completed,
            #         {workflow_name}_processing_error=None
            #     )
            # )
            # await session.execute(final_update_stmt_option_b)
            # --- End Option B ---

    except Exception as e:
        logger.error(f"Error during process_single_{source_table_name}_for_{workflow_name} for ID {record_id}: {e}")
        raise

# --- Helper function for custom logic ---
# from typing import List, Dict
# async def perform_custom_extraction(source_record: {SourceTableTitleCase}) -> List[Dict]:
#     # Implement your specific extraction/processing logic here.
#     # Example:
#     # import asyncio
#     # logger.info(f"Extracting data from {source_record.id}...")
#     # await asyncio.sleep(1) # Simulate work
#     # return [{{"field1": "value1", "field2": 123}}]
#     return []
