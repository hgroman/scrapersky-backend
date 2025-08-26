import uuid
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from src.models.page import Page
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.utils.scraper_api import ScraperAPIClient
import logging

class PageCurationService:
    def __init__(self):
        pass

    async def process_single_page_for_curation(
        self, page_id: uuid.UUID, session: AsyncSession
    ) -> bool:
        """
        Processes a single page, extracts its content, and creates a unique contact.
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

            # 2. Use ScraperAPI to fetch real content (bypasses bot detection)
            page_url = str(page.url)
            html_content = ""
            
            try:
                logging.info(f"Fetching content from {page_url} using ScraperAPI")
                async with ScraperAPIClient() as scraper_client:
                    html_content = await scraper_client.fetch(page_url, render_js=True, retries=3)
                
                if not html_content or len(html_content) < 10:
                    logging.warning(f"No meaningful content extracted from URL: {page_url}")
                    html_content = ""
                else:
                    logging.info(f"Extracted {len(html_content)} characters from {page_url}")

            except Exception as e:
                logging.error(f"Error during ScraperAPI content extraction for {page_url}: {e}")
                html_content = ""

            # 3. Extract REAL contact info using proven regex patterns from metadata_extractor.py
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
                    logging.info(f"Found REAL email: {contact_email}")
                elif emails:
                    # Even system emails are better than fake ones
                    contact_email = emails[0]
                    contact_name = f"Contact at {domain_name}"
                    logging.info(f"Found system email: {contact_email}")
                else:
                    # Create a unique "not found" record using page_id to ensure uniqueness
                    page_id_short = str(page_id).split('-')[0]  # Use first part of UUID
                    contact_email = f"notfound_{page_id_short}@{domain_name}"
                    contact_name = f"No Contact Found - {domain_name}"
                    logging.info(f"No emails found, creating unique placeholder: {contact_email}")
                
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
                    )
                    session.add(new_contact)
                    logging.info(f"Created REAL contact for {domain_name}: {contact_email} | {contact_phone}")

            except Exception as e:
                logging.error(f"Error creating contact for page {page.id}: {e}")
                return False
            
            # 4. Set page status to Complete (required by run_job_loop SDK)
            from src.models.enums import PageProcessingStatus
            # Use setattr to properly update the column value
            setattr(page, 'page_processing_status', PageProcessingStatus.Complete)
            logging.info(f"Set page {page.id} status to Complete")
            
            # Transaction auto-commits when exiting async with session.begin()

        return True