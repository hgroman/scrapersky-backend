#!/usr/bin/env python
"""
Test script for email scraping with database integration.
"""

import asyncio
import argparse
import re
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict, Any, Optional, Tuple
import uuid
import logging

import requests
from bs4 import BeautifulSoup, Tag
from sqlalchemy import select, update
from sqlalchemy.future import select as future_select

# Import database models and session
from src.models.job import Job
from src.models.domain import Domain
from src.models.page import Page
from src.models.contact import Contact, ContactEmailTypeEnum
from src.models import TaskStatus
from src.session.async_session import get_background_session

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Email detection patterns ---
EMAIL_PATTERNS = {
    'service': r'(?i)(info|support|sales|contact|help|admin|webmaster|service)@[\w\.-]+\.\w+',
    'general': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'obfuscated': r'[a-zA-Z0-9._%+-]+\s*(?:&#64;|@|at|\[at\]|\(at\))\s*[a-zA-Z0-9.-]+\s*(?:&#46;|\.|\.|dot|\[dot\]|\(dot\))\s*[a-zA-Z]{2,}'
}

# --- User agent for requests ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Helper functions ---
def is_service_email(email: str) -> bool:
    """Check if an email matches service email patterns"""
    return bool(re.match(EMAIL_PATTERNS['service'], email, re.I))

def is_gmail_email(email: str) -> bool:
    """Check if an email is a Gmail address"""
    return email.lower().endswith('@gmail.com')

def is_corporate_email(email: str, domain: str) -> bool:
    """Check if an email matches the website's domain"""
    try:
        email_domain = email.lower().split('@')[1]
        return domain.lower() in email_domain
    except IndexError:
        return False

def classify_email_type(email: str, domain: str) -> str:
    """Determine the type of email address"""
    email_lower = email.lower()
    domain_lower = domain.lower()

    if is_service_email(email_lower):
        return ContactEmailTypeEnum.SERVICE
    elif is_corporate_email(email_lower, domain_lower):
        return ContactEmailTypeEnum.CORPORATE
    elif is_gmail_email(email_lower) or ('@' in email_lower and not is_corporate_email(email_lower, domain_lower)):
        return ContactEmailTypeEnum.FREE
    return ContactEmailTypeEnum.UNKNOWN

def clean_email(email: str) -> str:
    """Clean and normalize an email address from various formats"""
    # Replace obfuscation attempts
    email = email.replace('[at]', '@').replace('(at)', '@').replace(' at ', '@')
    email = email.replace('[dot]', '.').replace('(dot)', '.').replace(' dot ', '.')

    # Remove html entities
    email = email.replace('&#64;', '@').replace('&#46;', '.')

    # Remove spaces
    email = email.replace(' ', '')

    # Find the actual email pattern if it exists in the cleaned string
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email)
    if match:
        return match.group()

    return email

def extract_emails_from_text(text: str) -> List[Tuple[str, str]]:
    """Extract emails and their surrounding context from text"""
    emails = []

    # Find all email matches using multiple patterns
    patterns = [EMAIL_PATTERNS['general'], EMAIL_PATTERNS['obfuscated']]

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            raw_email = match.group()
            cleaned_email = clean_email(raw_email)

            # Skip if no valid email found after cleaning
            if '@' not in cleaned_email:
                continue

            # Get surrounding context (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()

            emails.append((cleaned_email, context))

    return emails

def extract_emails_from_soup(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    """Extract emails from various places in the HTML"""
    emails = []

    # 1. Check for mailto links
    for a_tag in soup.find_all('a'):
        if isinstance(a_tag, Tag):
            href = a_tag.get('href', '')
            if isinstance(href, str) and href.startswith('mailto:'):
                email = href[7:]  # Strip 'mailto:'

                # Remove any URL parameters
                if '?' in email:
                    email = email.split('?')[0]

                context = a_tag.get_text() or f"Found in mailto link: {a_tag}"
                emails.append((email, context))

    # 2. Check form fields that might contain emails
    email_field_names = ['email', 'mail', 'contact', 'contactEmail']
    for field in soup.find_all(['input', 'textarea']):
        if isinstance(field, Tag):
            field_name = field.get('name', '')
            field_id = field.get('id', '')
            field_value = field.get('value', '')

            if isinstance(field_name, str):
                field_name = field_name.lower()
            else:
                field_name = ''

            if isinstance(field_id, str):
                field_id = field_id.lower()
            else:
                field_id = ''

            # If it seems to be an email field and has a value
            if ((any(name in field_name for name in email_field_names) or
                any(name in field_id for name in email_field_names)) and
                isinstance(field_value, str) and '@' in field_value):
                context = f"Found in form field: {field}"
                emails.append((field_value, context))

    # 3. Check for contact info in meta tags
    for meta in soup.find_all('meta'):
        if isinstance(meta, Tag):
            content = meta.get('content', '')
            if isinstance(content, str) and '@' in content and '.' in content:
                # Try to extract email with regex
                for pattern in [EMAIL_PATTERNS['general'], EMAIL_PATTERNS['obfuscated']]:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        cleaned_email = clean_email(match)
                        if '@' in cleaned_email:
                            context = f"Found in meta tag: {meta}"
                            emails.append((cleaned_email, context))

    return emails

def get_base_url(url: str) -> str:
    """Get the base URL from a full URL"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def is_valid_url(url: str, base_domain_netloc: str) -> bool:
    """Check if a URL is valid and belongs to the same domain"""
    try:
        parsed = urlparse(url)
        return bool(
            parsed.netloc and
            base_domain_netloc in parsed.netloc and
            parsed.scheme in ['http', 'https'] and
            not any(ext in parsed.path.lower() for ext in ['.pdf', '.jpg', '.png', '.gif'])
        )
    except:
        return False

def find_links(soup: BeautifulSoup, base_url: str) -> Set[str]:
    """Find all valid links in a page"""
    links = set()
    base_domain_netloc = urlparse(base_url).netloc

    # Safely find and process links
    for element in soup.find_all('a'):
        try:
            # Only process Tag objects, skip NavigableString or other types
            if isinstance(element, Tag):
                href = element.get('href')
                if href is not None and isinstance(href, str) and not href.startswith('mailto:'):
                    url = urljoin(base_url, str(href))
                    if is_valid_url(url, base_domain_netloc):
                        links.add(url)
        except Exception as e:
            logger.warning(f"Error processing link: {e}")

    return links

async def scrape_url_and_store(
    url: str,
    domain_obj: Domain,
    job_obj: Job,
    visited: Set[str],
    session
) -> Tuple[int, Set[str]]:
    """Process a URL, extract emails, store them in the database, and return new links"""
    new_contacts_count = 0
    new_links = set()

    try:
        logger.info(f"Processing URL: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract emails from multiple sources
        text_content = soup.get_text()
        emails_from_text = extract_emails_from_text(text_content)
        emails_from_html = extract_emails_from_soup(soup)
        all_emails = emails_from_text + emails_from_html

        # Get new links
        base_url = get_base_url(url)
        new_links = find_links(soup, base_url) - visited

        # Database operations for storing pages and emails
        if all_emails:
            # Look up existing page using ORM
            page_query = select(Page).where(
                Page.domain_id == domain_obj.id,
                Page.url == url
            ).limit(1)

            page_result = await session.execute(page_query)
            page_obj = page_result.scalars().first()

            if not page_obj:
                # Create new Page
                page_obj = Page(
                    domain_id=domain_obj.id,
                    tenant_id=domain_obj.tenant_id,
                    url=url,
                    last_scan=datetime.utcnow(),
                    additional_json={'emails_found': len(all_emails), 'job_id': str(job_obj.job_id)}
                )
                session.add(page_obj)
                await session.flush()
                logger.info(f"Created new Page with ID: {page_obj.id}")
            else:
                # Update existing Page using ORM methods
                page_obj.last_scan = datetime.utcnow()
                if not page_obj.additional_json:
                    page_obj.additional_json = {}
                if isinstance(page_obj.additional_json, dict):
                    # Create a copy to ensure we're modifying a new dictionary
                    updated_json = dict(page_obj.additional_json)
                    updated_json["emails_found"] = len(all_emails)
                    updated_json["job_id"] = str(job_obj.job_id)
                    page_obj.additional_json = updated_json
                session.add(page_obj)
                await session.flush()
                logger.info(f"Updated existing Page with ID: {page_obj.id}")

            # Store emails as Contacts
            for email, context in all_emails:
                email_lower = email.lower()

                # Check if contact already exists using ORM
                contact_query = select(Contact.id).where(
                    Contact.domain_id == domain_obj.id,
                    Contact.email == email_lower
                ).limit(1)

                contact_result = await session.execute(contact_query)
                contact_exists = contact_result.scalar() is not None

                if not contact_exists:
                    # Classify email type
                    domain_name = str(domain_obj.domain)
                    email_type = classify_email_type(email_lower, domain_name)

                    # Create new Contact
                    new_contact = Contact(
                        domain_id=domain_obj.id,
                        page_id=page_obj.id,
                        email=email_lower,
                        email_type=email_type,
                        has_gmail=is_gmail_email(email_lower),
                        context=context,
                        source_url=url,
                        source_job_id=job_obj.job_id
                    )
                    session.add(new_contact)
                    new_contacts_count += 1
                    logger.info(f"Found new contact: {email_lower} ({email_type}) on page {url}")

            await session.flush()

    except requests.RequestException as e:
        logger.warning(f"Request error for {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {str(e)}", exc_info=True)

    return new_contacts_count, new_links

async def test_email_scraper(domain_name: str, max_pages: int = 10, verbose: bool = False):
    """Test the email scraper with database integration"""
    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting test on domain: {domain_name} with max_pages={max_pages}")

    async with get_background_session() as session:
        try:
            # Check if domain exists using ORM
            if hasattr(Domain, 'get_by_domain_name'):
                # Use model method if available
                domain_obj = await Domain.get_by_domain_name(session, domain_name)
            else:
                # Fallback to ORM query
                domain_query = select(Domain).where(Domain.domain == domain_name).limit(1)
                domain_result = await session.execute(domain_query)
                domain_obj = domain_result.scalars().first()

            if domain_obj:
                logger.info(f"Found existing domain: {domain_name} (ID: {domain_obj.id})")
            else:
                # Create a new domain
                logger.info(f"Domain {domain_name} not found. Creating new domain record.")
                domain_obj = Domain(
                    domain=domain_name,
                    status="active",
                    # Add other required fields based on your model
                )
                session.add(domain_obj)
                await session.flush()
                logger.info(f"Created new domain with ID: {domain_obj.id}")

            # Create a job for testing
            job_obj = Job(
                job_type="email_scan_test",
                status=TaskStatus.PENDING.value,
                domain_id=domain_obj.id,
                # Add other required fields based on your model
            )
            session.add(job_obj)
            await session.flush()
            job_id = job_obj.job_id
            logger.info(f"Created test job with ID: {job_id}")

            # Update job to RUNNING
            job_obj.status = TaskStatus.RUNNING.value
            await session.commit()

            # Set up for crawling
            if not domain_name.startswith(('http://', 'https://')):
                start_url = f"https://{domain_name}"
            else:
                start_url = domain_name

            visited = set()
            to_visit = {start_url}
            pages_scanned = 0
            total_contacts_found = 0

            # Crawl and extract emails
            while to_visit and pages_scanned < max_pages:
                current_url = to_visit.pop()
                if current_url in visited:
                    continue

                visited.add(current_url)
                pages_scanned += 1

                contacts_count, new_links = await scrape_url_and_store(
                    current_url, domain_obj, job_obj, visited, session
                )
                total_contacts_found += contacts_count

                # Add new links to visit
                to_visit.update(new_links - visited)

                if verbose:
                    logger.info(f"Processed page {pages_scanned}/{max_pages}: {current_url}")
                    logger.info(f"Found {contacts_count} new contacts, {len(new_links)} new links")
                    logger.info(f"Queue size: {len(to_visit)}")

            # Update job to COMPLETED
            job_obj.status = TaskStatus.COMPLETE.value
            setattr(job_obj, 'progress', 1.0)

            # Get final results for the job using ORM
            contact_query = select(Contact.email).where(
                Contact.source_job_id == job_id
            )
            contact_result = await session.execute(contact_query)
            contacts = contact_result.scalars().all()

            # Store results in the job
            setattr(job_obj, 'result_data', {"emails": list(contacts)})
            await session.commit()

            # Show final results
            logger.info("==== Email Scraping Results ====")
            logger.info(f"Domain: {domain_name}")
            logger.info(f"Pages scanned: {pages_scanned}")
            logger.info(f"Total emails found: {len(contacts)}")

            if contacts:
                logger.info("\nSample emails found:")
                for email in list(contacts)[:5]:
                    logger.info(f"- {email}")

                if len(contacts) > 5:
                    logger.info(f"...and {len(contacts) - 5} more")

            logger.info(f"\nTest complete. Results stored in database under job ID: {job_id}")

            return job_id

        except Exception as e:
            logger.error(f"Error during test: {e}", exc_info=True)
            await session.rollback()
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Email Scraper with Database Integration')
    parser.add_argument('domain', help='Domain to scan (e.g., "example.com")')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum number of pages to crawl')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    try:
        asyncio.run(test_email_scraper(args.domain, args.max_pages, args.verbose))
    except KeyboardInterrupt:
        logger.info("Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)
