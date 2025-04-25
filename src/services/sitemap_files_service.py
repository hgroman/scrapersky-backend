"""
Sitemap Files Service

Provides operations for managing sitemap file records.

This service follows the transaction-aware pattern where it works with
transactions but does not create, commit, or rollback transactions itself.
Transaction boundaries are managed by the router.
"""
import logging
import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

# Set logger level to DEBUG for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Corrected import path
from ..models.domain import Domain
from ..models.sitemap import (
    SitemapDeepCurationStatusEnum,
    SitemapDeepProcessStatusEnum,
    SitemapFile,
    SitemapFileStatusEnum,
)
from ..schemas.sitemap_file import PaginatedSitemapFileResponse, SitemapFileRead

# If get_session is needed later, import it:
# from ..db.session import get_session

class SitemapFilesService:
    """
    Service for Sitemap File management.

    Provides methods for CRUD operations on SitemapFile entities.
    This service is transaction-aware but doesn't manage transactions.
    Transaction boundaries are owned by the routers.
    """

    async def get_by_id(self, session: AsyncSession, sitemap_file_id: Union[str, uuid.UUID]) -> Optional[SitemapFile]:
        """
        Get a sitemap file by its ID.

        Args:
            session: SQLAlchemy AsyncSession
            sitemap_file_id: The UUID or string representation of the sitemap file ID.

        Returns:
            SitemapFile instance or None if not found.
        """
        logger.debug(f"Getting sitemap file by ID using SitemapFile.get_by_id: {sitemap_file_id}")
        try:
            # Use the model's classmethod - REMOVED tenant_id=None
            sitemap_file = await SitemapFile.get_by_id(session, sitemap_file_id)
            if sitemap_file:
                logger.debug(f"Found sitemap file using classmethod: {sitemap_file.id}")
            else:
                logger.debug(f"Sitemap file not found using classmethod with ID: {sitemap_file_id}")
            return sitemap_file
        except Exception as e:
            logger.error(f"Error retrieving sitemap file by ID {sitemap_file_id} using classmethod: {e}", exc_info=True)
            return None


    async def get_all(
        self,
        session: AsyncSession,
        page: int = 1,
        size: int = 15,
        domain_id: Optional[uuid.UUID] = None,
        deep_scrape_curation_status: Optional[SitemapDeepCurationStatusEnum] = None,
        url_contains: Optional[str] = None,
        sitemap_type: Optional[str] = None,
        discovery_method: Optional[str] = None,
    ) -> PaginatedSitemapFileResponse:
        """
        Get all sitemap files with filtering, pagination, and domain join.

        Args:
            session: SQLAlchemy AsyncSession
            page: Page number (1-indexed).
            size: Number of items per page.
            domain_id: Optional UUID to filter by domain.
            deep_scrape_curation_status: Optional Enum to filter by curation status.
            url_contains: Optional string to filter URL (case-insensitive).
            sitemap_type: Optional string to filter by sitemap type.
            discovery_method: Optional string to filter by discovery method.

        Returns:
            PaginatedSitemapFileResponse containing items and pagination info.
        """
        logger.debug(
            f"Getting all sitemap files page={page}, size={size}, filters="
            f"domain_id={domain_id}, curation_status={deep_scrape_curation_status}, "
            f"url_contains={url_contains}, type={sitemap_type}, discovery={discovery_method}"
        )
        try:
            # Base query with required join for domain name
            base_stmt = select(SitemapFile).options(joinedload(SitemapFile.domain))
            count_stmt = select(func.count(SitemapFile.id)) # No join needed for count if filters are on SitemapFile

            # Apply filters conditionally to both queries
            filters_applied = []
            if domain_id:
                filters_applied.append(SitemapFile.domain_id == domain_id)
                logger.debug(f"Applying filter: domain_id == {domain_id}")
            if deep_scrape_curation_status:
                # Compare against the .value of the Enum member for robustness
                filters_applied.append(SitemapFile.deep_scrape_curation_status == deep_scrape_curation_status.value)
                logger.debug(f"Applying filter: deep_scrape_curation_status == {deep_scrape_curation_status.value}") # Log value
            if url_contains:
                filters_applied.append(SitemapFile.url.ilike(f'%{url_contains}%'))
                logger.debug(f"Applying filter: url contains '{url_contains}'")
            if sitemap_type:
                filters_applied.append(SitemapFile.sitemap_type == sitemap_type)
                logger.debug(f"Applying filter: sitemap_type == {sitemap_type}")
            if discovery_method:
                filters_applied.append(SitemapFile.discovery_method == discovery_method)
                logger.debug(f"Applying filter: discovery_method == {discovery_method}")

            if filters_applied:
                base_stmt = base_stmt.where(*filters_applied)
                count_stmt = count_stmt.where(*filters_applied)


            # Get total count BEFORE pagination
            total_result = await session.execute(count_stmt)
            total = total_result.scalar_one()
            logger.debug(f"Total matching sitemap files: {total}")

            # Apply sorting (defaulting to updated_at descending)
            # Ensure this is applied *after* filtering and *before* pagination
            stmt = base_stmt.order_by(SitemapFile.updated_at.desc())

            # Apply pagination
            offset = (page - 1) * size
            stmt = stmt.offset(offset).limit(size)

            # Execute main query
            result = await session.execute(stmt)
            items_orm = result.scalars().all()
            logger.debug(f"Retrieved {len(items_orm)} sitemap files for page {page}.")

            # Convert ORM items to Pydantic Read schemas
            # Manually map domain name if necessary, or rely on Pydantic ORM mode
            items_dto = []
            for item in items_orm:
                item_dict = item.to_dict() # Assuming to_dict exists or use model_validate
                # Add domain name explicitly if not handled by ORM mode/schema correctly
                item_dict['domain_name'] = item.domain.domain if item.domain else None
                # Need SitemapFileRead imported
                items_dto.append(SitemapFileRead.model_validate(item_dict))


            pages = (total + size - 1) // size if size > 0 else 0

            return PaginatedSitemapFileResponse(
                items=items_dto,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
        except Exception as e:
            logger.error(f"Error retrieving paginated sitemap files: {e}", exc_info=True)
            raise # Propagate exception


    async def create(self, session: AsyncSession, sitemap_data: dict[str, Any], created_by: Optional[uuid.UUID] = None) -> SitemapFile:
        """
        Create a new sitemap file record.

        Args:
            session: SQLAlchemy AsyncSession
            sitemap_data: Dictionary containing the data for the new sitemap file.
            created_by: Optional UUID of the user creating the record.

        Returns:
            The newly created SitemapFile instance.
        """
        logger.debug(f"Creating new sitemap file with data: {sitemap_data}, created_by: {created_by}")
        try:
            # Ensure UUIDs are handled correctly if passed as strings
            # Add any other necessary validation or preprocessing here

            # Add created_by if provided (Req G)
            if created_by:
                sitemap_data['created_by'] = created_by
                logger.debug(f"Setting created_by to {created_by}")

            sitemap_file = SitemapFile(**sitemap_data)
            session.add(sitemap_file)
            # Note: The object won't have its ID populated until flush/commit,
            # but we return the instance added to the session.
            # If the ID is needed immediately, a session.flush() might be required,
            # but that deviates from the pattern of routers managing transactions.
            logger.info(f"Added new sitemap file to session (pending flush/commit).")
            return sitemap_file
        except Exception as e:
            logger.error(f"Error creating sitemap file: {e}", exc_info=True)
            # Consider raising the exception to be handled by the router's transaction management
            raise


    async def update(self, session: AsyncSession, sitemap_file_id: Union[str, uuid.UUID], update_data: dict[str, Any], updated_by: Optional[uuid.UUID] = None) -> Optional[SitemapFile]:
        """
        Update an existing sitemap file record.

        Args:
            session: SQLAlchemy AsyncSession
            sitemap_file_id: The ID of the sitemap file to update.
            update_data: Dictionary containing the fields to update.
            updated_by: Optional UUID of the user performing the update.

        Returns:
            The updated SitemapFile instance or None if not found.
        """
        logger.debug(f"Updating sitemap file ID {sitemap_file_id} with data: {update_data}, updated_by: {updated_by}")
        try:
            logger.debug(f"Entering SitemapFilesService.update for ID: {sitemap_file_id} with data: {update_data}")
            sitemap_file = await self.get_by_id(session, sitemap_file_id)

            if not sitemap_file:
                logger.warning(f"Sitemap file not found for update: ID {sitemap_file_id}")
                return None

            for field, value in update_data.items():
                if hasattr(sitemap_file, field):
                    setattr(sitemap_file, field, value)
                    # REMOVED Trigger Logic Here - Per Spec 23.5/23.6, this logic is now in batch update
                    # if field == 'deep_scrape_curation_status' and value == SitemapDeepCurationStatusEnum.Selected.value: # Compare against .value
                    #    logger.info(f"Deep scrape curation status set to Selected for sitemap file ID {sitemap_file_id}. Setting process status to Pending.")
                    #    setattr(sitemap_file, 'deep_scrape_process_status', SitemapFileStatusEnum.Pending)
                    #    # Optionally clear any previous error message
                    #    if hasattr(sitemap_file, 'deep_scrape_error'):
                    #       setattr(sitemap_file, 'deep_scrape_error', None)
                else:
                    logger.warning(f"Field '{field}' not found on SitemapFile model during update.")

            # Set updated_by if provided (Req G)
            if updated_by and hasattr(sitemap_file, 'updated_by'):
                setattr(sitemap_file, 'updated_by', updated_by)
                logger.debug(f"Setting updated_by to {updated_by}")
            elif updated_by:
                 logger.warning(f"Field 'updated_by' not found on SitemapFile model.")

            session.add(sitemap_file) # Add updated object to session
            logger.info(f"Updated sitemap file ID {sitemap_file_id} in session (pending flush/commit).")
            return sitemap_file
        except Exception as e:
            logger.error(f"Error updating sitemap file ID {sitemap_file_id}: {e}", exc_info=True)
            # Consider raising the exception
            raise


    async def update_curation_status_batch(
        self,
        session: AsyncSession,
        sitemap_file_ids: List[uuid.UUID],
        new_curation_status: SitemapDeepCurationStatusEnum,
        updated_by: Optional[uuid.UUID] = None # Added user tracking
    ) -> Dict[str, int]:
        """
        Batch update the deep_scrape_curation_status for multiple sitemap files.
        If the new status is 'Selected', also attempts to queue them for deep scrape
        by setting deep_scrape_process_status to 'Queued', unless they are already 'Processing'.

        Args:
            session: SQLAlchemy AsyncSession.
            sitemap_file_ids: A list of UUIDs for the records to update.
            new_curation_status: The new SitemapDeepCurationStatusEnum status to set.
            updated_by: Optional UUID of the user performing the update.

        Returns:
            A dictionary containing 'updated_count' (records with curation status changed)
            and 'queued_count' (records successfully set to 'queued' process status).
        """
        if not sitemap_file_ids:
            logger.warning("Batch curation status update called with empty ID list.")
            return {"updated_count": 0, "queued_count": 0}

        logger.debug(f"Batch updating curation status to {new_curation_status.name} for {len(sitemap_file_ids)} sitemap files, updated_by: {updated_by}")

        updated_count = 0
        queued_count = 0

        try:
            # Use transaction block for atomicity
            async with session.begin():
                # 1. Update curation status
                update_values_curation = {
                    # Explicitly use .value here too for robustness
                    "deep_scrape_curation_status": new_curation_status.value,
                    "updated_at": func.now() # Keep updated_at fresh
                }
                if updated_by:
                    update_values_curation["updated_by"] = updated_by

                update_stmt_curation = (
                    update(SitemapFile)
                    .where(SitemapFile.id.in_(sitemap_file_ids))
                    .values(**update_values_curation)
                    .execution_options(synchronize_session=False)
                )
                result_curation = await session.execute(update_stmt_curation)
                # Relying on rowcount, acknowledging potential driver issues mentioned in 23.6
                updated_count = result_curation.rowcount if result_curation.rowcount >= 0 else len(sitemap_file_ids)
                logger.debug(f"Curation status update query affected rowcount: {result_curation.rowcount}. Set updated_count to {updated_count}.")


                # 2. If selected, conditionally update process status to 'queued'
                if new_curation_status == SitemapDeepCurationStatusEnum.Selected:
                    update_values_process = {
                         # Use .value to ensure the correct string is sent to the DB
                         "deep_scrape_process_status": SitemapDeepProcessStatusEnum.Queued.value,
                         "updated_at": func.now() # Keep updated_at fresh
                         # Optionally clear previous error?
                         # "deep_scrape_error": None
                    }
                    # updated_by is already set by the first update, no need to repeat unless desired

                    update_stmt_process = (
                        update(SitemapFile)
                        .where(
                            SitemapFile.id.in_(sitemap_file_ids),
                            # Correctly handle NULL or != 'processing'
                            or_(
                                SitemapFile.deep_scrape_process_status == None, # Check if NULL
                                SitemapFile.deep_scrape_process_status != SitemapDeepProcessStatusEnum.Processing.value # Check if not processing
                            )
                        )
                        .values(**update_values_process)
                        .execution_options(synchronize_session=False)
                    )
                    result_process = await session.execute(update_stmt_process)
                    # Relying on rowcount
                    queued_count = result_process.rowcount if result_process.rowcount >= 0 else 0 # Default to 0 if rowcount is negative/unknown
                    logger.debug(f"Process status update to queued query affected rowcount: {result_process.rowcount}. Set queued_count to {queued_count}.")

            # Commit is automatic via 'async with session.begin()'
            logger.info(f"Batch curation status update completed. Updated: {updated_count}, Queued: {queued_count}")
            return {"updated_count": updated_count, "queued_count": queued_count}

        except Exception as e:
            logger.error(f"Error during batch curation status update: {e}", exc_info=True)
            # Exception will automatically trigger rollback due to 'async with session.begin()'
            raise # Re-raise for the router to handle

    async def delete(self, session: AsyncSession, sitemap_file_id: Union[str, uuid.UUID]) -> bool:
        """
        Delete a sitemap file record by its ID.

        Args:
            session: SQLAlchemy AsyncSession
            sitemap_file_id: The ID of the sitemap file to delete.

        Returns:
            True if the deletion was successful (or record didn't exist), False otherwise.
            Note: Actual deletion happens on commit. This checks if the object exists
            and issues the delete statement.
        """
        logger.debug(f"Attempting to delete sitemap file ID: {sitemap_file_id}")
        try:
            # Option 1: Get the object then delete (allows checking existence)
            # sitemap_file = await self.get_by_id(session, sitemap_file_id)
            # if not sitemap_file:
            #     logger.warning(f"Sitemap file not found for deletion: ID {sitemap_file_id}")
            #     return True # Or False, depending on desired semantics (idempotency)
            # await session.delete(sitemap_file)

            # Option 2: Issue a delete statement directly (more efficient if existence check isn't needed)
            stmt = delete(SitemapFile).where(SitemapFile.id == sitemap_file_id)
            result = await session.execute(stmt)

            if result.rowcount > 0:
                logger.info(f"Issued delete statement for sitemap file ID {sitemap_file_id} ({result.rowcount} row(s) matched).")
                return True
            else:
                logger.warning(f"Sitemap file not found for deletion: ID {sitemap_file_id}")
                return False # Record did not exist

        except Exception as e:
            logger.error(f"Error deleting sitemap file ID {sitemap_file_id}: {e}", exc_info=True)
            # Consider raising the exception
            raise

# Example of potential additional specific methods:
# async def get_by_url(self, session: AsyncSession, url: str) -> Optional[SitemapFile]: ...
# async def find_by_status(self, session: AsyncSession, status: str) -> List[SitemapFile]: ...
