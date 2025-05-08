# src/services/sitemap_import_service.py

import logging
import uuid
from typing import List, Optional

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.sitemap_parser import SitemapParser, SitemapURL
from src.models.page import Page
from src.models.sitemap import SitemapFile, SitemapImportProcessStatusEnum

logger = logging.getLogger(__name__)


class SitemapImportService:
    """Service to handle the import of URLs from a single sitemap file."""

    def __init__(self):
        self.sitemap_parser = SitemapParser()

    async def process_single_sitemap_file(
        self, sitemap_file_id: uuid.UUID, session: AsyncSession
    ) -> None:
        """
        Processes a single sitemap file: fetches it, parses URLs, and saves them to the database.
        Updates the SitemapFile status upon completion or error.

        Args:
            sitemap_file_id: The ID of the SitemapFile record to process.
            session: The database session.
        """
        sitemap_file: Optional[SitemapFile] = await session.get(
            SitemapFile, sitemap_file_id
        )
        if not sitemap_file:
            logger.error(
                f"SitemapFile with id {sitemap_file_id} not found during processing."
            )
            return

        # --- REINSTATED STATUS CHECK --- #
        # Double-check status before processing ( belt-and-suspenders )
        if (
            sitemap_file.sitemap_import_status
            != SitemapImportProcessStatusEnum.Processing
        ):
            logger.warning(
                f"SitemapFile {sitemap_file_id} is not in Processing state "
                f"({sitemap_file.sitemap_import_status}). Skipping."
            )
            return
        # --- END REINSTATED STATUS CHECK --- #

        # Get the actual URL string value from the model instance
        sitemap_url_str = str(sitemap_file.url)

        logger.info(
            f"Starting URL import for SitemapFile {sitemap_file_id} "
            f"(URL: {sitemap_url_str})"
        )
        sitemap_file_to_fail: Optional[SitemapFile] = None  # For error handling

        try:
            # Fetch the sitemap content
            async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
                # Pass the string URL
                response = await client.get(sitemap_url_str)
                # Raise HTTPError for bad responses (4xx or 5xx)
                response.raise_for_status()
                sitemap_content = response.text

            # Parse the sitemap
            # Pass the string URL
            extracted_urls: list[SitemapURL] = self.sitemap_parser.parse(
                sitemap_content, sitemap_url_str
            )

            if not extracted_urls:
                logger.warning(
                    f"No URLs extracted from SitemapFile {sitemap_file_id} "
                    f"(URL: {sitemap_url_str})"
                )
                sitemap_file.sitemap_import_status = (
                    SitemapImportProcessStatusEnum.Completed  # type: ignore
                )
                sitemap_file.sitemap_import_error = None  # type: ignore
                await session.commit()
                return

            logger.info(
                f"Extracted {len(extracted_urls)} URLs from SitemapFile "
                f"{sitemap_file_id}. Storing..."
            )

            # --- Store extracted URLs in sitemap_urls table ---
            # # Delete existing URLs for this sitemap_id?
            # # Potentially complex if pages processed. Assume append.
            # await session.execute(
            #     delete(SitemapUrl).where(SitemapUrl.sitemap_id == sitemap_file.id)
            # )
            # await session.flush()

            # --- Store Pages in pages table ---
            domain_id = (
                sitemap_file.domain_id
            )  # Get domain_id from the sitemap_file record
            tenant_id = (
                sitemap_file.tenant_id
            )  # Get tenant_id from the sitemap_file record

            pages_to_insert: List[Page] = []
            processed_urls = set()  # Keep track of URLs already added from this sitemap
            for sitemap_url_record in extracted_urls:
                # Use .loc instead of .url
                page_url = str(sitemap_url_record.loc)

                # Avoid duplicates within the same sitemap batch
                if page_url in processed_urls:
                    continue

                # Create a new Page record
                page_data = {
                    "domain_id": domain_id,
                    "url": page_url,  # Renamed from sitemap_url_record.loc
                    "last_modified": sitemap_url_record.lastmod,  # Map from sitemap lastmod
                    "tenant_id": tenant_id,
                    "sitemap_file_id": sitemap_file.id,  # ADDED: Link page to its source sitemap
                    "lead_source": "sitemap_import",  # Add lead source
                    # Potentially map other fields if available in SitemapURL?
                    # "title": sitemap_url_record.title, # Example if available
                }

                # Remove None values before creating Page to avoid DB constraint errors
                page_data_cleaned = {
                    k: v for k, v in page_data.items() if v is not None
                }

                # Only create Page if url is present (basic validation)
                if page_data_cleaned.get("url"):
                    pages_to_insert.append(Page(**page_data_cleaned))
                    processed_urls.add(page_url)  # Renamed from sitemap_url_record.loc
                else:
                    logger.warning(
                        f"Skipping record with missing URL from sitemap "
                        f"{sitemap_file.id}"
                    )

            if not pages_to_insert:
                logger.warning(
                    f"SITEMAP_IMPORT: No new URLs found to insert for "
                    f"SitemapFile {sitemap_file_id}."
                )
                # Update status to Completed even if no URLs inserted
                sitemap_file.sitemap_import_status = (
                    SitemapImportProcessStatusEnum.Completed  # type: ignore
                )
                sitemap_file.sitemap_import_error = None  # type: ignore
                await session.commit()
                return

            if pages_to_insert:
                try:
                    session.add_all(pages_to_insert)
                    await (
                        session.flush()
                    )  # Flush to catch potential IntegrityErrors early
                    logger.info(
                        f"Successfully added {len(pages_to_insert)} Page records "
                        f"for SitemapFile {sitemap_file_id}."
                    )
                except IntegrityError as ie:
                    await session.rollback()  # Rollback the failed batch
                    logger.error(
                        f"IntegrityError adding pages for SitemapFile "
                        f"{sitemap_file_id}. Error: {ie}. Attempting individual inserts."
                    )
                    # Attempt individual inserts to salvage what we can
                    pages_added_count = 0
                    for page_rec in pages_to_insert:
                        try:
                            session.add(page_rec)
                            await session.flush()
                            pages_added_count += 1
                        except IntegrityError:
                            await session.rollback()
                            logger.warning(
                                f"Skipping duplicate/error page URL: {page_rec.url}"
                            )
                    logger.info(
                        f"Added {pages_added_count} pages individually after bulk "
                        f"insert failure for {sitemap_file_id}."
                    )
                except Exception as bulk_e:
                    await session.rollback()
                    logger.error(
                        f"Unexpected error during bulk insert for SitemapFile "
                        f"{sitemap_file_id}: {bulk_e}"
                    )
                    # Mark sitemap file as failed if bulk insert had non-IntegrityError
                    sitemap_file_to_fail = sitemap_file
                    raise  # Re-raise to trigger outer error handling

            # --- Update SitemapFile status ---
            if (
                not sitemap_file_to_fail
            ):  # Only mark complete if no fatal error occurred during page insert
                sitemap_file.sitemap_import_status = (
                    SitemapImportProcessStatusEnum.Completed  # type: ignore
                )
                sitemap_file.sitemap_import_error = None  # type: ignore
                logger.info(
                    f"Successfully completed URL import for SitemapFile "
                    f"{sitemap_file_id}."
                )

            await session.commit()

        except httpx.HTTPStatusError as e:
            await session.rollback()  # Rollback any potential partial changes
            logger.error(
                f"HTTP error fetching sitemap {sitemap_url_str} "  # Use string URL
                f"(SitemapFile {sitemap_file_id}): {e.response.status_code} - {e}"
            )
            sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Error  # type: ignore
            sitemap_file.sitemap_import_error = f"HTTP Error: {e.response.status_code}"  # type: ignore
            await session.commit()
        except httpx.RequestError as e:
            await session.rollback()
            logger.error(
                f"Request error fetching sitemap {sitemap_url_str} "  # Use string URL
                f"(SitemapFile {sitemap_file_id}): {e}"
            )
            sitemap_file.sitemap_import_status = SitemapImportProcessStatusEnum.Error  # type: ignore
            sitemap_file.sitemap_import_error = (
                f"Request Error: {str(e)[:1024]}"  # Truncate long errors # type: ignore
            )
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception(
                f"Error processing SitemapFile {sitemap_file_id} "
                f"(URL: {sitemap_url_str}): {e}"  # Use string URL
            )
            try:
                # Attempt to update the original record even if it wasn't assigned
                # to sitemap_file_to_fail
                # Get a fresh reference in case the session state is weird
                sitemap_file_in_error: Optional[SitemapFile] = await session.get(
                    SitemapFile, sitemap_file_id
                )
                if sitemap_file_in_error:
                    sitemap_file_in_error.sitemap_import_status = (
                        SitemapImportProcessStatusEnum.Error  # type: ignore
                    )
                    sitemap_file_in_error.sitemap_import_error = str(e)[:1024]  # type: ignore
                    await session.commit()
                else:
                    logger.error(
                        f"Could not find SitemapFile {sitemap_file_id} to mark as "
                        f"Error after exception."
                    )
            except Exception as update_e:
                logger.exception(
                    f"Failed to mark SitemapFile {sitemap_file_id} as Error "
                    f"after processing exception: {update_e}"
                )
                await session.rollback()  # Rollback the status update attempt
