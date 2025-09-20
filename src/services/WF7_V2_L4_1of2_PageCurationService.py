import uuid
import re
import asyncio
import os
import time
import aiohttp
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from src.models.page import Page
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import PageProcessingStatus
from src.utils.scraper_api import ScraperAPIClient
from src.utils.simple_scraper import scrape_page_simple_async
import logging

class PageCurationService:
    def __init__(self):
        self.concurrent_semaphore = asyncio.Semaphore(
            int(os.getenv('WF7_SCRAPER_API_MAX_CONCURRENT', '10'))
        )
        self.enable_concurrent = os.getenv('WF7_ENABLE_CONCURRENT_PROCESSING', 'false').lower() == 'true'

    async def process_single_page_for_curation(
        self, page_id: uuid.UUID, session: AsyncSession
    ) -> bool:
        """
        Processes a single page, extracts its content, and creates a unique contact.
        Tries a robust direct HTTP fetch first, then falls back to ScraperAPI.
        Returns True on success, False on failure.
        
        NOTE: As per run_job_loop SDK requirements, this function manages its own
        transaction and sets the final page status to Complete on success.
        """
        logging.info(f"Starting curation for page_id: {page_id}")

        # SDK passes session but we manage our own transaction per SDK requirements
        async with session.begin():
            # 1. Fetch the Page object
            stmt = select(Page).where(Page.id == page_id)
            result = await session.execute(stmt)
            page = result.scalar_one_or_none()

            if not page:
                logging.error(f"Page with id {page_id} not found.")
                return False

            page_url = str(page.url)
            html_content = ""

            # 2. Fetch content using the simple, robust async scraper
            html_content = await scrape_page_simple_async(page_url)

            # 3. Final check and contact extraction
            if not html_content:
                logging.error(f"All attempts (direct and fallback) to fetch content for page {page_id} failed.")
                page.page_processing_status = PageProcessingStatus.Error
                return False

            # 4. Extract REAL contact info using proven regex patterns from metadata_extractor.py
            try:
                domain_name = page_url.split('//')[1].split('/')[0] if '//' in page_url else 'unknown'
                
                # Use proven contact extraction patterns from metadata_extractor.py
                # Email pattern - more robust
                email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                emails = list(set(re.findall(email_pattern, html_content)))
                
                # Phone pattern - more comprehensive (from metadata_extractor.py)
                phone_pattern = r"\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"
                phones = list(set(re.findall(phone_pattern, html_content)))
                
                # Filter out obviously fake emails
                real_emails = [email for email in emails if not any(fake in email.lower() for fake in ['noreply', 'donotreply', 'no-reply', 'example.com', 'test.com', 'dummy'])]
                
                # Use REAL extracted info or create unique "not found" record per page
                if real_emails:
                    contact_email = real_emails[0]  # Use first real email found
                    contact_name = f"Contact at {domain_name}"
                    # Mark page as having contact found - use existing database enum values
                    page.contact_scrape_status = 'ContactFound'
                    logging.info(f"Found REAL email: {contact_email}")
                elif emails:
                    # Even system emails are better than fake ones
                    contact_email = emails[0]
                    contact_name = f"Contact at {domain_name}"
                    # Mark page as having contact found - use existing database enum values
                    page.contact_scrape_status = 'ContactFound'
                    logging.info(f"Found system email: {contact_email}")
                else:
                    # No emails found - update page status instead of creating fake contact
                    page.contact_scrape_status = 'NoContactFound'
                    logging.info(f"No emails found, marked page {page_id} as NoContactFound")
                    # Skip contact creation but continue to set page processing status
                    contact_email = None
                
                # Only create contacts if we found email addresses
                if contact_email:
                    contact_phone = phones[0] if phones else "Phone not found"

                    # Check if contact already exists for this domain and email
                    existing_contact_stmt = select(Contact).where(
                        and_(
                            Contact.domain_id == page.domain_id,
                            Contact.email == contact_email
                        )
                    )
                    existing_result = await session.execute(existing_contact_stmt)
                    existing_contact = existing_result.scalar_one_or_none()

                    if existing_contact:
                        logging.info(f"Contact already exists for {domain_name}: {contact_email} (ID: {existing_contact.id})")
                        # Update phone if we found a better one
                        if contact_phone != "Phone not found" and existing_contact.phone_number == "Phone not found":
                            existing_contact.phone_number = contact_phone[:50]
                            logging.info(f"Updated existing contact phone: {contact_phone}")
                    else:
                        # Create new contact
                        new_contact = Contact(
                            domain_id=page.domain_id,
                            page_id=page.id,
                            name=contact_name,
                            email=contact_email,
                            phone_number=contact_phone[:50],  # Limit length
                            source_url=page.url,  # Populate from page URL
                        )
                        session.add(new_contact)
                        logging.info(f"Created REAL contact for {domain_name}: {contact_email} | {contact_phone}")

            except Exception as e:
                logging.error(f"Error creating contact for page {page.id}: {e}")
                page.page_processing_status = PageProcessingStatus.Error
                return False
            
            # 4. Set page status to Complete (required by run_job_loop SDK)
            page.page_processing_status = PageProcessingStatus.Complete
            logging.info(f"Set page {page.id} status to Complete")
            
            # Transaction auto-commits when exiting async with session.begin()

        return True

    async def process_single_page_with_semaphore(
        self, page_id: uuid.UUID, session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process a single page with semaphore rate limiting for concurrent execution.
        Returns dict with success status and details for monitoring.
        """
        async with self.concurrent_semaphore:
            start_time = time.time()
            try:
                success = await self.process_single_page_for_curation(page_id, session)
                processing_time = time.time() - start_time
                return {
                    'page_id': str(page_id),
                    'success': success,
                    'processing_time': processing_time,
                    'error': None
                }
            except Exception as e:
                processing_time = time.time() - start_time
                logging.error(f"Concurrent processing failed for page {page_id}: {e}")
                return {
                    'page_id': str(page_id),
                    'success': False,
                    'processing_time': processing_time,
                    'error': str(e)
                }

    async def process_pages_concurrently(
        self, page_ids: List[uuid.UUID], session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Process multiple pages concurrently with rate limiting and error isolation.
        Returns list of processing results for monitoring and debugging.
        """
        if not self.enable_concurrent or len(page_ids) <= 1:
            # Fall back to sequential processing
            logging.info(f"Processing {len(page_ids)} pages sequentially")
            results = []
            for page_id in page_ids:
                result = await self.process_single_page_with_semaphore(page_id, session)
                results.append(result)
            return results
        
        # Concurrent processing
        start_time = time.time()
        logging.info(f"Processing {len(page_ids)} pages CONCURRENTLY with max {self.concurrent_semaphore._value} concurrent")
        
        tasks = [
            self.process_single_page_with_semaphore(page_id, session)
            for page_id in page_ids
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'page_id': str(page_ids[i]),
                    'success': False,
                    'processing_time': 0,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in processed_results if r['success'])
        
        logging.info(f"WF7 CONCURRENT RESULTS: Processed {len(page_ids)} pages in {total_time:.2f}s, "
                    f"{success_count} successful, {len(page_ids) - success_count} failed, "
                    f"Average: {total_time/len(page_ids):.2f}s per page")
        
        return processed_results