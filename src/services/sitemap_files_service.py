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

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

# Set logger level to DEBUG for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Corrected import path
from ..models.wf5_sitemap_file import (
    SitemapFile,
    SitemapFileStatusEnum,
    SitemapImportCurationStatusEnum,
    SitemapImportProcessStatusEnum,
)
from ..schemas.wf5_sitemap_file_schemas import PaginatedSitemapFileResponse, SitemapFileRead

# If get_session is needed later, import it:
# from ..db.session import get_session


class SitemapFilesService:
    """
    Service for Sitemap File management.

    Provides methods for CRUD operations on SitemapFile entities.
    This service is transaction-aware but doesn't manage transactions.
    Transaction boundaries are owned by the routers.
    """

    async def get_by_id(
        self, session: AsyncSession, sitemap_file_id: Union[str, uuid.UUID]
    ) -> Optional[SitemapFile]:
        """
        Get a sitemap file by its ID.

        Args:
            session: SQLAlchemy AsyncSession
            sitemap_file_id: The UUID or string representation of the sitemap file ID.

        Returns:
            SitemapFile instance or None if not found.
        """
        logger.debug(
            f"Getting sitemap file by ID using SitemapFile.get_by_id: {sitemap_file_id}"
        )
        try:
            # Use the model's classmethod - REMOVED tenant_id=None
            sitemap_file = await SitemapFile.get_by_id(session, sitemap_file_id)
            if sitemap_file:
                logger.debug(f"Found sitemap file using classmethod: {sitemap_file.id}")
            else:
                logger.debug(
                    f"Sitemap file not found using classmethod with ID: {sitemap_file_id}"
                )
            return sitemap_file
        except Exception as e:
            logger.error(
                f"Error retrieving sitemap file by ID {sitemap_file_id} using classmethod: {e}",
                exc_info=True,
            )
            return None

    async def get_all(
        self,
        session: AsyncSession,
        page: int = 1,
        size: int = 15,
        domain_id: Optional[uuid.UUID] = None,
        deep_scrape_curation_status: Optional[SitemapImportCurationStatusEnum] = None,
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
            count_stmt = select(
                func.count(SitemapFile.id)
            )  # No join needed for count if filters are on SitemapFile

            # Apply filters conditionally to both queries
            filters_applied = []
            if domain_id:
                filters_applied.append(SitemapFile.domain_id == domain_id)
                logger.debug(f"Applying filter: domain_id == {domain_id}")
            if deep_scrape_curation_status:
                # Compare against the .value of the Enum member for robustness
                filters_applied.append(
                    SitemapFile.deep_scrape_curation_status
                    == deep_scrape_curation_status
                )
                logger.debug(
                    f"Applying filter: deep_scrape_curation_status == {deep_scrape_curation_status.value}"
                )  # Log value
            if url_contains:
                filters_applied.append(SitemapFile.url.ilike(f"%{url_contains}%"))
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
                item_dict = (
                    item.to_dict()
                )  # Assuming to_dict exists or use model_validate
                # Add domain name explicitly if not handled by ORM mode/schema correctly
                item_dict["domain_name"] = item.domain.domain if item.domain else None
                # Need SitemapFileRead imported
                items_dto.append(SitemapFileRead.model_validate(item_dict))

            pages = (total + size - 1) // size if size > 0 else 0

            return PaginatedSitemapFileResponse(
                items=items_dto, total=total, page=page, size=size, pages=pages
            )
        except Exception as e:
            logger.error(
                f"Error retrieving paginated sitemap files: {e}", exc_info=True
            )
            raise  # Propagate exception

    async def create(
        self,
        session: AsyncSession,
        sitemap_data: dict[str, Any],
        created_by: Optional[uuid.UUID] = None,
    ) -> SitemapFile:
        """
        Create a new sitemap file record.

        Args:
            session: SQLAlchemy AsyncSession
            sitemap_data: Dictionary containing the data for the new sitemap file.
            created_by: Optional UUID of the user creating the record.

        Returns:
            The newly created SitemapFile instance.
        """
        logger.debug(
            f"Creating new sitemap file with data: {sitemap_data}, created_by: {created_by}"
        )
        try:
            # Ensure UUIDs are handled correctly if passed as strings
            # Add any other necessary validation or preprocessing here

            # Add created_by if provided (Req G)
            if created_by:
                sitemap_data["created_by"] = created_by
                logger.debug(f"Setting created_by to {created_by}")

            sitemap_file = SitemapFile(**sitemap_data)
            session.add(sitemap_file)
            # Note: The object won't have its ID populated until flush/commit,
            # but we return the instance added to the session.
            # If the ID is needed immediately, a session.flush() might be required,
            # but that deviates from the pattern of routers managing transactions.
            logger.info("Added new sitemap file to session (pending flush/commit).")
            return sitemap_file
        except Exception as e:
            logger.error(f"Error creating sitemap file: {e}", exc_info=True)
            # Consider raising the exception to be handled by the router's transaction management
            raise

    async def update(
        self,
        session: AsyncSession,
        sitemap_file_id: Union[str, uuid.UUID],
        update_data: dict[str, Any],
        updated_by: Optional[uuid.UUID] = None,
    ) -> Optional[SitemapFile]:
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
        logger.debug(
            f"Updating sitemap file ID {sitemap_file_id} with data: {update_data}, updated_by: {updated_by}"
        )
        try:
            logger.debug(
                f"Entering SitemapFilesService.update for ID: {sitemap_file_id} with data: {update_data}"
            )
            sitemap_file = await self.get_by_id(session, sitemap_file_id)

            if not sitemap_file:
                logger.warning(
                    f"Sitemap file not found for update: ID {sitemap_file_id}"
                )
                return None

            for field, value in update_data.items():
                if hasattr(sitemap_file, field):
                    setattr(sitemap_file, field, value)
                    # REMOVED Trigger Logic Here - Per Spec 23.5/23.6, this logic is now in batch update
                    # if field == 'deep_scrape_curation_status' and value == SitemapImportCurationStatusEnum.Selected.value: # Compare against .value
                    #    logger.info(f"Deep scrape curation status set to Selected for sitemap file ID {sitemap_file_id}. Setting process status to Pending.")
                    #    setattr(sitemap_file, 'deep_scrape_process_status', SitemapFileStatusEnum.Pending)
                    #    # Optionally clear any previous error message
                    #    if hasattr(sitemap_file, 'deep_scrape_error'):
                    #       setattr(sitemap_file, 'deep_scrape_error', None)
                else:
                    logger.warning(
                        f"Field '{field}' not found on SitemapFile model during update."
                    )

            # Set updated_by if provided (Req G)
            if updated_by and hasattr(sitemap_file, "updated_by"):
                sitemap_file.updated_by = updated_by
                logger.debug(f"Setting updated_by to {updated_by}")
            elif updated_by:
                logger.warning("Field 'updated_by' not found on SitemapFile model.")

            session.add(sitemap_file)  # Add updated object to session
            logger.info(
                f"Updated sitemap file ID {sitemap_file_id} in session (pending flush/commit)."
            )
            return sitemap_file
        except Exception as e:
            logger.error(
                f"Error updating sitemap file ID {sitemap_file_id}: {e}", exc_info=True
            )
            # Consider raising the exception
            raise

    async def update_curation_status_batch(
        self,
        session: AsyncSession,
        sitemap_file_ids: List[uuid.UUID],
        new_curation_status: SitemapImportCurationStatusEnum,
        updated_by: Optional[uuid.UUID] = None,  # Added user tracking
    ) -> Dict[str, int]:
        """
        Batch update the deep_scrape_curation_status of sitemap files.
        If the new status is 'Selected', update the deep_scrape_process_status to 'Queued'.

        Args:
            session: SQLAlchemy AsyncSession
            sitemap_file_ids: List of SitemapFile UUIDs to update.
            new_curation_status: The new curation status enum value.
            updated_by: Optional UUID of the user performing the update.

        Returns:
            A dictionary containing 'updated_count' and 'queued_count'.
        """
        logger.info(
            f"Starting batch update: {len(sitemap_file_ids)} files, status={new_curation_status}, by={updated_by}"
        )

        # --- Begin Transaction --- (Managed by router, assumed here)
        # async with session.begin(): <-- Router should handle this

        # 1. Validate IDs (optional but good practice)
        if not sitemap_file_ids:
            logger.warning("Batch update called with empty sitemap_file_ids list.")
            return {"updated_count": 0, "queued_count": 0}

        # 2. Prepare update values dictionary
        update_values = {
            # Use renamed Enum property if DB column name wasn't changed
            SitemapFile.deep_scrape_curation_status: new_curation_status,
            SitemapFile.updated_at: func.now(),
            SitemapFile.updated_by: updated_by,  # Add user tracking
        }

        # 3. Conditionally add process status update
        queue_for_processing = (
            new_curation_status == SitemapImportCurationStatusEnum.Selected
        )
        if queue_for_processing:
            # Use renamed Enum for process status
            update_values[SitemapFile.sitemap_import_status] = (
                SitemapImportProcessStatusEnum.Queued
            )
            # Clear any previous error when re-queuing
            update_values[SitemapFile.sitemap_import_error] = None
            logger.info(
                f"New status is '{new_curation_status.value}', also setting process status to 'Queued'."
            )

        # 4. Build and execute the UPDATE statement
        stmt = (
            update(SitemapFile)
            .where(SitemapFile.id.in_(sitemap_file_ids))
            .values(update_values)
            .execution_options(synchronize_session=False)  # Important for bulk updates
        )

        try:
            result = await session.execute(stmt)
            updated_count = result.rowcount
            logger.info(f"Executed batch update, rowcount: {updated_count}")

            # Determine queued_count based on the flag and updated count
            queued_count = updated_count if queue_for_processing else 0

            # Optional: Check if updated_count matches len(sitemap_file_ids)?
            if updated_count != len(sitemap_file_ids):
                logger.warning(
                    f"Batch update affected {updated_count} rows, but {len(sitemap_file_ids)} IDs were provided. Some IDs might be invalid or already had the target status."
                )

            # --- Commit Transaction --- (Managed by router)
            # await session.commit() <-- Router handles commit/rollback

            return {"updated_count": updated_count, "queued_count": queued_count}

        except Exception as e:
            logger.error(
                f"Error during batch sitemap status update: {e}", exc_info=True
            )
            # --- Rollback Transaction --- (Managed by router)
            # await session.rollback() <-- Router handles commit/rollback
            raise  # Re-raise the exception to ensure router handles rollback

        # --- End Transaction --- (Managed by router)

    async def delete(
        self, session: AsyncSession, sitemap_file_id: Union[str, uuid.UUID]
    ) -> bool:
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
                logger.info(
                    f"Issued delete statement for sitemap file ID {sitemap_file_id} ({result.rowcount} row(s) matched)."
                )
                return True
            else:
                logger.warning(
                    f"Sitemap file not found for deletion: ID {sitemap_file_id}"
                )
                return False  # Record did not exist

        except Exception as e:
            logger.error(
                f"Error deleting sitemap file ID {sitemap_file_id}: {e}", exc_info=True
            )
            # Consider raising the exception
            raise


# Example of potential additional specific methods:
# async def get_by_url(self, session: AsyncSession, url: str) -> Optional[SitemapFile]: ...
# async def find_by_status(self, session: AsyncSession, status: str) -> List[SitemapFile]: ...
