# src/services/sitemap_import_service.py

import logging
import uuid
from typing import List, Optional

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.common.sitemap_parser import SitemapParser, SitemapURL
from src.models.page import Page
from src.models.sitemap import SitemapFile
from src.models.enums import SitemapImportProcessStatusEnum
from src.models.enums import PageCurationStatus, PageProcessingStatus
from src.utils.honeybee_categorizer import HoneybeeCategorizer

logger = logging.getLogger(__name__)


class SitemapImportService:
    """Service to handle the import of URLs from a single sitemap file."""

    def __init__(self):
        self.sitemap_parser = SitemapParser()
        self.honeybee = HoneybeeCategorizer()

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
                setattr(
                    sitemap_file,
                    "sitemap_import_status",
                    SitemapImportProcessStatusEnum.Complete,
                )
                setattr(sitemap_file, "sitemap_import_error", None)
                await session.commit()
                return

            # Check if this is a sitemap index by examining the content
            is_sitemap_index = "<sitemapindex" in sitemap_content
            
            if is_sitemap_index:
                logger.info(
                    f"Detected sitemap index with {len(extracted_urls)} child sitemaps. "
                    f"Fetching and processing child sitemaps for SitemapFile {sitemap_file_id}"
                )
                
                # For sitemap indexes, fetch each child sitemap and extract page URLs
                all_page_urls = []
                
                for child_sitemap_url in extracted_urls:
                    child_url_str = str(child_sitemap_url.loc)
                    logger.info(f"Fetching child sitemap: {child_url_str}")
                    
                    try:
                        # Fetch child sitemap content
                        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
                            child_response = await client.get(child_url_str)
                            child_response.raise_for_status()
                            child_content = child_response.text
                        
                        # Parse child sitemap for page URLs
                        child_urls = self.sitemap_parser.parse(child_content, child_url_str)
                        logger.info(f"Extracted {len(child_urls)} URLs from child sitemap: {child_url_str}")
                        all_page_urls.extend(child_urls)
                        
                    except Exception as e:
                        logger.error(f"Failed to fetch/parse child sitemap {child_url_str}: {e}")
                        continue
                
                # Replace extracted_urls with all page URLs from child sitemaps
                extracted_urls = all_page_urls
                logger.info(
                    f"Total page URLs extracted from sitemap index: {len(extracted_urls)}"
                )

            logger.info(
                f"Extracted {len(extracted_urls)} URLs from SitemapFile "
                f"{sitemap_file_id} (URL: {sitemap_url_str})"
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

                # Honeybee categorization - categorize ALL pages, never skip
                hb = self.honeybee.categorize(page_url)

                # Create a new Page record for ALL pages
                page_data = {
                    "domain_id": uuid.UUID(str(domain_id)) if domain_id else None,
                    "url": page_url,  # Renamed from sitemap_url_record.loc
                    "last_modified": sitemap_url_record.lastmod,  # Map from sitemap lastmod
                    "tenant_id": uuid.UUID(str(tenant_id)) if tenant_id else None,
                    "sitemap_file_id": uuid.UUID(str(sitemap_file.id)) if sitemap_file.id else None,  # ADDED: Link page to its source sitemap
                    "lead_source": "sitemap_import",  # Add lead source
                    # Honeybee fields
                    "page_type": hb["category"],
                    "path_depth": hb["depth"],
                    "priority_level": 1 if hb["confidence"] >= 0.6 else 3,
                    "honeybee_json": {
                        "v": 1,
                        "decision": {
                            "category": hb["category"],
                            "confidence": hb["confidence"],
                            "matched_regex": hb["matched"]
                        },
                        "exclusions": hb["exclusions"]
                    }
                }

                # Disposition instead of drop - mark processing status based on quality
                if hb["decision"] == "skip" or hb["confidence"] < 0.2:
                    page_data["page_processing_status"] = PageProcessingStatus.Filtered
                else:
                    page_data["page_processing_status"] = PageProcessingStatus.Queued

                # Auto-select only high-value, shallow paths
                if hb["category"] in {"contact_root", "career_contact", "legal_root"} and hb["confidence"] >= 0.6 and hb["depth"] <= 2:
                    page_data["page_curation_status"] = PageCurationStatus.Selected
                    page_data["priority_level"] = 1  # enforce

                # Remove None values before creating Page to avoid DB constraint errors
                page_data_cleaned = {
                    k: v for k, v in page_data.items() if v is not None
                }

                # Only create Page if url is present (basic validation)
                if page_data_cleaned.get("url"):
                    try:
                        page = Page(**page_data_cleaned)
                        pages_to_insert.append(page)
                        processed_urls.add(page_url)
                    except Exception as e:
                        logger.error(f"Failed to create Page object for {page_url}: {e}")
                        continue
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
                # Update status to Complete even if no URLs inserted
                setattr(
                    sitemap_file,
                    "sitemap_import_status",
                    SitemapImportProcessStatusEnum.Complete,
                )
                setattr(sitemap_file, "sitemap_import_error", None)
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
                    raise  # Re-raise to trigger outer error handling

            # --- Update SitemapFile status ---
            if (
                not sitemap_file_to_fail
            ):  # Only mark complete if no fatal error occurred during page insert
                setattr(
                    sitemap_file,
                    "sitemap_import_status",
                    SitemapImportProcessStatusEnum.Complete,
                )
                setattr(sitemap_file, "sitemap_import_error", None)
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
            setattr(
                sitemap_file,
                "sitemap_import_status",
                SitemapImportProcessStatusEnum.Error,
            )
            setattr(
                sitemap_file,
                "sitemap_import_error",
                f"HTTP Error: {e.response.status_code}",
            )
            await session.commit()
        except httpx.RequestError as e:
            await session.rollback()
            logger.error(
                f"Request error fetching sitemap {sitemap_url_str} "  # Use string URL
                f"(SitemapFile {sitemap_file_id}): {e}"
            )
            setattr(
                sitemap_file,
                "sitemap_import_status",
                SitemapImportProcessStatusEnum.Error,
            )
            setattr(
                sitemap_file, "sitemap_import_error", f"Request Error: {str(e)[:1024]}"
            )  # Truncate long errors
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
                    setattr(
                        sitemap_file_in_error,
                        "sitemap_import_status",
                        SitemapImportProcessStatusEnum.Error,
                    )
                    setattr(
                        sitemap_file_in_error, "sitemap_import_error", str(e)[:1024]
                    )
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
