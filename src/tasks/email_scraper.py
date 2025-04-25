import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, cast
from urllib.parse import urljoin, urlparse
import uuid
import logging
import asyncio # Import asyncio for timeouts

import requests
from bs4 import BeautifulSoup, Tag
from sqlalchemy import select, update # Import update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.settings import Settings
from ..session.async_session import get_background_session
from ..models.domain import Domain
from ..models.page import Page
from ..models.contact import Contact, ContactEmailTypeEnum
from ..models.job import Job # Import Job model
from ..models import TaskStatus # Import TaskStatus enum

logger = logging.getLogger(__name__)

# Load settings
settings = Settings()

# Common patterns for different types of emails
EMAIL_PATTERNS = {
    'service': r'(?i)(info|support|sales|contact|help|admin|webmaster|service)@[\w\.-]+\.\w+',
    'general': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
}

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': settings.user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

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

def get_email_type(email: str, domain_str: str) -> ContactEmailTypeEnum:
    """Determine the type of email address using ContactEmailTypeEnum"""
    email_lower = email.lower()
    domain_lower = domain_str.lower()
    if is_service_email(email_lower):
        return ContactEmailTypeEnum.SERVICE
    elif is_corporate_email(email_lower, domain_lower):
        return ContactEmailTypeEnum.CORPORATE
    elif is_gmail_email(email_lower) or ('@' in email_lower and not is_corporate_email(email_lower, domain_lower)):
        return ContactEmailTypeEnum.FREE
    return ContactEmailTypeEnum.UNKNOWN

def extract_emails_from_text(text: str) -> List[tuple[str, str]]:
    """Extract emails and their surrounding context from text"""
    emails = []

    # First find all email matches
    for match in re.finditer(EMAIL_PATTERNS['general'], text):
        email = match.group()

        # Get surrounding context (50 chars before and after)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].strip()

        emails.append((email, context))

    return emails

def scrape_page_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract basic metadata from the page"""
    metadata = {
        'page_metadata': {
            'title': soup.title.string if soup.title else None,
            'word_count': len(soup.get_text().split())
        }
    }
    return metadata

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

    # Safe implementation for BeautifulSoup type checking
    for element in soup.find_all('a'):
        try:
            # Only process Tag objects, skip NavigableString or other types
            if isinstance(element, Tag):
                href = element.get('href')
                if href is not None:
                    url = urljoin(base_url, str(href))
                    if is_valid_url(url, base_domain_netloc):
                        links.add(url)
        except Exception as e:
            logging.warning(f"Error processing link: {e}")

    return links

async def process_url(
    url: str,
    domain_obj: Domain,
    job_obj: Job,
    user_id: uuid.UUID,
    visited: Set[str],
    session: AsyncSession
) -> tuple[int, Set[str]]:
    """Process a single URL for emails and return new links
    Accepts Domain, Job objects, user_id and uses the passed session.
    Returns (number of new contacts, new links found)"""
    try:
        logger.debug(f"Job {job_obj.job_id}: Processing URL: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        emails_found = extract_emails_from_text(text_content)
        new_contacts_count = 0
        new_links = set()

        base_url = get_base_url(url)
        new_links = find_links(soup, base_url) - visited

        if emails_found:
            # Database operations within the *passed* session
            try:
                page_stmt = select(Page).where(Page.domain_id == domain_obj.id, Page.url == url).limit(1)
                page_result = await session.execute(page_stmt)
                page_obj = page_result.scalar_one_or_none()

                if not page_obj:
                    logger.debug(f"Job {job_obj.job_id}: Creating Page entry for URL: {url}")
                    new_page = Page(
                        domain_id=domain_obj.id,
                        tenant_id=domain_obj.tenant_id,
                        url=url,
                        last_scan=datetime.utcnow(),
                        additional_json={'emails_found': len(emails_found), 'job_id': str(job_obj.job_id)}
                    )
                    session.add(new_page)
                    await session.flush()
                    page_obj = new_page
                    logger.debug(f"Job {job_obj.job_id}: Created Page with ID: {page_obj.id}")
                else:
                    # Use setattr to avoid type errors with SQLAlchemy columns
                    setattr(page_obj, 'last_scan', datetime.utcnow())

                    # Safe dict handling for SQLAlchemy column
                    current_json = getattr(page_obj, 'additional_json', {}) or {}
                    if isinstance(current_json, dict):
                        updated_json = current_json.copy()
                        updated_json['job_id'] = str(job_obj.job_id)
                        setattr(page_obj, 'additional_json', updated_json)
                    else:
                        setattr(page_obj, 'additional_json', {'job_id': str(job_obj.job_id)})

                    session.add(page_obj)
                    await session.flush()
                    logger.debug(f"Job {job_obj.job_id}: Found existing Page with ID: {page_obj.id}")

                page_id = page_obj.id

                for email, context in emails_found:
                    email_lower = email.lower()
                    contact_check_stmt = select(Contact.id).where(
                        Contact.domain_id == domain_obj.id,
                        Contact.email == email_lower
                    ).limit(1)
                    contact_result = await session.execute(contact_check_stmt)
                    exists = contact_result.scalar_one_or_none() is not None

                    if not exists:
                        # Get domain string safely for get_email_type
                        domain_name = str(getattr(domain_obj, 'domain', ''))
                        email_type = get_email_type(email_lower, domain_name)

                        new_contact = Contact(
                            domain_id=domain_obj.id,
                            page_id=page_id,
                            email=email_lower,
                            email_type=email_type,
                            has_gmail=is_gmail_email(email_lower),
                            context=context,
                            source_url=url,
                            source_job_id=job_obj.job_id
                        )
                        session.add(new_contact)
                        new_contacts_count += 1
                        logger.info(f"Job {job_obj.job_id}: Found new contact: {email_lower} on page {url}")

                await session.flush()

            except Exception as e:
                logger.error(f"Job {job_obj.job_id}: DB error processing URL {url}: {e}", exc_info=True)
                raise

        if new_contacts_count > 0:
            logger.info(f"Job {job_obj.job_id}: Processed {url}. Found {new_contacts_count} new contacts.")
        return new_contacts_count, new_links

    except requests.RequestException as e:
        logger.warning(f"Job {job_obj.job_id}: Request error for {url}: {str(e)}")
        return 0, set()
    except Exception as e:
        logger.error(f"Job {job_obj.job_id}: Unexpected error processing {url}: {str(e)}", exc_info=True)
        return 0, set()

async def scan_website_for_emails(job_id: uuid.UUID, user_id: uuid.UUID):
    """Crawl a website and scan for emails, updating the Job record."""
    logger.info(f"***** TASK STARTED for job_id: {job_id}, initiated by user_id: {user_id} *****") # Initial log
    MAX_PAGES = 100 # Limit crawl depth

    async with get_background_session() as session:
        job: Optional[Job] = None
        domain_obj: Optional[Domain] = None
        error_message: Optional[str] = None
        final_status = TaskStatus.FAILED # Default to failed unless successful
        start_time = datetime.utcnow()
        pages_scanned = 0
        total_contacts_found = 0

        try:
            # 1. Fetch the Job record using job_id
            job = await Job.get_by_job_id(session, job_id)
            if not job:
                logger.error(f"Job {job_id} not found in database. Aborting task.")
                return

            # 2. Fetch associated Domain using job.domain_id
            domain_id = getattr(job, 'domain_id', None)
            if domain_id is None:
                error_message = f"Job {job_id} has no associated domain_id."
                logger.error(error_message)
                return # Just return early

            logger.info(f"***** Fetched Job {job_id}, associated domain_id: {domain_id} *****") # Log domain_id

            domain_obj = await session.get(Domain, domain_id)
            if not domain_obj:
                error_message = f"Domain with ID {domain_id} (from Job {job_id}) not found."
                logger.error(error_message)
                return # Just return early

            # 3. Update Job status to RUNNING
            logger.info(f"Job {job_id}: Setting status to RUNNING for domain {getattr(domain_obj, 'domain', 'unknown')}")
            setattr(job, 'status', TaskStatus.RUNNING.value)
            setattr(job, 'progress', 0.0) # Reset progress
            setattr(job, 'error', None) # Clear previous errors
            setattr(job, 'result_data', []) # Initialize result_data as empty list
            await session.commit() # Commit RUNNING status

            # 4. Perform the crawl and scrape
            start_url = f"https://{getattr(domain_obj, 'domain', '')}"
            if not start_url.startswith(('http://', 'https://')):
                start_url = 'http://' + start_url # Ensure scheme

            visited: Set[str] = set()
            to_visit: Set[str] = {start_url}
            total_contacts_found = 0
            pages_scanned = 0
            found_emails: Set[str] = set() # Store unique emails found

            while to_visit and pages_scanned < MAX_PAGES:
                current_url = to_visit.pop()
                if current_url in visited:
                    continue

                visited.add(current_url)
                pages_scanned += 1

                try:
                    contacts_count, new_links = await process_url(
                        current_url, domain_obj, job, user_id, visited, session
                    )
                    total_contacts_found += contacts_count
                    to_visit.update(new_links - visited) # Add new, unvisited links

                    # Update progress (simple version)
                    setattr(job, 'progress', min(pages_scanned / MAX_PAGES, 1.0))

                except Exception as url_proc_error:
                    # Log error from process_url but continue crawl if possible
                    logger.error(f"Job {job_id}: Error processing URL {current_url} within main loop: {url_proc_error}")
                    # Consider adding URL to job.error or metadata?

            # 5. Final Job Update (after loop)
            logger.info(f"Job {job_id}: Crawl finished. Pages Scanned={pages_scanned}, Total New Contacts={total_contacts_found}")

            # Fetch all unique contacts associated with this job_id
            contact_stmt = select(Contact.email).where(Contact.source_job_id == job_id).distinct()
            contact_result = await session.execute(contact_stmt)
            final_emails = [row.email for row in contact_result.all()]

            setattr(job, 'progress', 1.0)
            setattr(job, 'result_data', {"emails": final_emails}) # Store as JSON with a key
            final_status = TaskStatus.COMPLETE # Mark as complete if no critical error occurred

        except Exception as e:
            # Catch broad exceptions during setup or main loop logic
            error_message = f"Critical error during email scan for job {job_id}: {str(e)}"
            logger.error(error_message, exc_info=True)
            final_status = TaskStatus.FAILED
            # Try to update the job record with the error, even if partially failed
            if job:
                setattr(job, 'error', error_message[:1024]) # Truncate if needed
                setattr(job, 'status', final_status.value)
                try:
                    await session.commit()
                except Exception as commit_err:
                    logger.error(f"Job {job_id}: Failed to commit final FAILED status: {commit_err}")
                    await session.rollback() # Rollback if final commit fails
            return # Exit task on critical error

        finally:
            # Ensure final status update happens
            if job:
                setattr(job, 'status', final_status.value)
                # Ensure error field is cleared on success
                if final_status == TaskStatus.COMPLETE:
                    setattr(job, 'error', None)

                # Safe way to access result_data for logging
                result_count = 0
                result_data = getattr(job, 'result_data', None)
                if result_data and isinstance(result_data, dict) and 'emails' in result_data:
                    result_count = len(result_data['emails'])

                logger.info(f"Job {job_id}: Setting final status to {getattr(job, 'status', 'unknown')}. Result emails count: {result_count}")
                try:
                    await session.commit() # Commit final status, progress, results/error
                except Exception as final_commit_err:
                    logger.error(f"Job {job_id}: Failed to commit final job status update: {final_commit_err}")
                    await session.rollback()

            logger.info(f"Email scan task finished for job_id: {job_id}")

def classify_email_type(email: str, domain: str) -> ContactEmailTypeEnum:
    """Determine the type of an email address"""
    if is_service_email(email):
        return ContactEmailTypeEnum.SERVICE
    elif is_corporate_email(email, domain):
        return ContactEmailTypeEnum.CORPORATE
    elif is_gmail_email(email) or '@' in email and not is_corporate_email(email, domain):
        return ContactEmailTypeEnum.FREE
    return ContactEmailTypeEnum.UNKNOWN
