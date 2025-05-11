# Example File: src/routers/{workflow_name}.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update # `select` might not be needed for this specific endpoint
from sqlalchemy.ext.asyncio import AsyncSession

from src.session.async_session import get_session_dependency
# Import source model
from src.models.{source_table_name} import {SourceTableTitleCase}
# Import Curation and Processing enums from model file
from src.models.{source_table_name} import {WorkflowNameTitleCase}CurationStatus, {WorkflowNameTitleCase}ProcessingStatus
# Import request and response schemas from their location
from src.schemas.{workflow_name} import {WorkflowNameTitleCase}BatchStatusUpdateRequest, {WorkflowNameTitleCase}BatchStatusUpdateResponse
from src.auth.dependencies import get_current_active_user # Assuming this is the standard auth dep
# from src.auth.jwt_auth import UserInToken # Ensure UserInToken or equivalent is used if get_current_active_user returns it

router = APIRouter() # Example: router = APIRouter()
logger = logging.getLogger(__name__)

# Convention (from CONVENTIONS_AND_PATTERNS_GUIDE.md Sec 7): update_{source_table_name}_status_batch
# Example (for page_curation): update_page_status_batch
# Endpoint path is /status; full path /api/v3/{source_table_plural_name}/status comes from router prefixing.
@router.put("/status", response_model={WorkflowNameTitleCase}BatchStatusUpdateResponse)
async def update_{source_table_name}_status_batch(
    request: {WorkflowNameTitleCase}BatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: UserInToken = Depends(get_current_active_user) # Replace UserInToken with actual type from auth dep
):
    """
    Update the {workflow_name}_curation_status for a batch of {source_table_name}s.

    If the target curation status is '{WorkflowNameTitleCase}CurationStatus.Queued',
    also updates the {workflow_name}_processing_status to '{WorkflowNameTitleCase}ProcessingStatus.Queued'.
    """
    try:
        target_curation_status = request.status
        logger.info(
            f"User {current_user.sub} updating {len(request.ids)} {source_table_name}s "
            f"to curation status {target_curation_status.value}"
        )

        # --- Determine if queueing for background processing is needed ---
        # This MUST use the Queued status for the curation enum as per CONVENTIONS_AND_PATTERNS_GUIDE.md
        should_queue_processing = (target_curation_status == {WorkflowNameTitleCase}CurationStatus.Queued)

        async with session.begin():
            update_values = {
                "{workflow_name}_curation_status": target_curation_status
            }

            if should_queue_processing:
                logger.debug(f"Queueing {source_table_name}s {request.ids} for {workflow_name} processing.")
                update_values["{workflow_name}_processing_status"] = {WorkflowNameTitleCase}ProcessingStatus.Queued
                update_values["{workflow_name}_processing_error"] = None
            else:
                 pass

            stmt = (
                update({SourceTableTitleCase})
                .where({SourceTableTitleCase}.id.in_(request.ids))
                .values(**update_values)
                .returning({SourceTableTitleCase}.id)
            )
            result = await session.execute(stmt)
            updated_ids = result.scalars().all()
            count = len(updated_ids)

            if count != len(request.ids):
                 logger.warning(f"Requested {len(request.ids)} updates, but only {count} were found/updated.")

        response_message = f"Updated {count} {source_table_name} records to curation status '{target_curation_status.value}'."
        if should_queue_processing and count > 0:
             response_message += f" Queued {count} for {workflow_name} processing."

        return {WorkflowNameTitleCase}BatchStatusUpdateResponse(message=response_message, updated_ids=updated_ids)

    except Exception as e:
        logger.exception(
            f"Error updating {source_table_name} status for IDs {request.ids} by user {current_user.sub}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Error updating {source_table_name} status.")
