import re
from typing import List, Optional, Dict, Any, Set
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from datetime import datetime
from enum import Enum
from ..config.settings import Settings
from ..db.sb_connection import db

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
    email_domain = email.split('@')[1].lower()
    return domain.lower() in email_domain

class EmailType(Enum):
    SERVICE = "service"
    CORPORATE = "corporate"
    FREE = "free"
    UNKNOWN = "unknown"

def get_email_type(email: str, domain: str) -> EmailType:
    """Determine the type of email address"""
    if is_service_email(email):
        return EmailType.SERVICE
    elif is_corporate_email(email, domain):
        return EmailType.CORPORATE
    elif is_gmail_email(email) or '@' in email and not is_corporate_email(email, domain):
        return EmailType.FREE
    return EmailType.UNKNOWN

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

def is_valid_url(url: str, base_domain: str) -> bool:
    """Check if a URL is valid and belongs to the same domain"""
    try:
        parsed = urlparse(url)
        return bool(
            parsed.netloc and
            base_domain in parsed.netloc and
            parsed.scheme in ['http', 'https'] and
            not any(ext in parsed.path.lower() for ext in ['.pdf', '.jpg', '.png', '.gif'])
        )
    except:
        return False

def find_links(soup: BeautifulSoup, base_url: str) -> Set[str]:
    """Find all valid links in a page"""
    links = set()
    for a in soup.find_all('a', href=True):
        url = urljoin(base_url, a['href'])
        if is_valid_url(url, urlparse(base_url).netloc):
            links.add(url)
    return links

async def process_url(url: str, website_id: int, visited: Set[str]) -> tuple[int, Set[str]]:
    """Process a single URL for emails and return new links
    Returns (number of new contacts, new links found)"""
    try:
        print(f"Processing: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        
        # Find emails
        emails_found = extract_emails_from_text(text_content)
        new_contacts = 0
        new_links = set()
        
        if emails_found:
            # Get website info
            website = db.query(Website).filter_by(id=website_id).first()
            if not website:
                print(f"Website {website_id} not found")
                return 0, set()
            
            try:
                # Create page first
                with db.get_cursor() as cur:
                    cur.execute("""
                        INSERT INTO pages (website_id, url, last_scan, page_metadata)
                        VALUES (%(website_id)s, %(url)s, %(last_scan)s, %(metadata)s)
                        RETURNING id
                    """, {
                        'website_id': website_id,
                        'url': url,
                        'last_scan': datetime.utcnow(),
                        'metadata': {'emails_found': len(emails_found)}
                    })
                    page_id = cur.fetchone()[0]
                
                # Now add contacts with valid page_id
                for email, context in emails_found:
                    with db.get_cursor() as cur:
                        # Check if contact exists
                        cur.execute("""
                            SELECT id FROM contacts 
                            WHERE website_id = %(website_id)s AND email = %(email)s
                        """, {
                            'website_id': website_id,
                            'email': email
                        })
                        
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO contacts 
                                (website_id, page_id, email, email_type, has_gmail, context)
                                VALUES (
                                    %(website_id)s, %(page_id)s, %(email)s, 
                                    %(email_type)s, %(has_gmail)s, %(context)s
                                )
                            """, {
                                'website_id': website_id,
                                'page_id': page_id,
                                'email': email,
                                'email_type': get_email_type(email, website['domain']).value,
                                'has_gmail': is_gmail_email(email),
                                'context': context
                            })
                            new_contacts += 1
                            print(f"Found new email: {email}")
                
                # Find new links
                base_url = get_base_url(url)
                new_links = find_links(soup, base_url) - visited
                
                # Report progress
                if new_contacts > 0:
                    print(f"Found {new_contacts} new contacts from {url}")
                    
            except Exception as e:
                print(f"Database error for {url}: {str(e)}")
                return 0, new_links
                
        return new_contacts, new_links
        
    except requests.RequestException as e:
        print(f"Request error for {url}: {str(e)}")
        return 0, set()
    except Exception as e:
        print(f"Unexpected error processing {url}: {str(e)}")
        return 0, set()

async def scan_website_for_emails(website_id: int):
    """Crawl a website and scan for emails"""
    from ..routers.email_scanner import scan_jobs
    
    try:
        # Get website info from Supabase
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, domain, tenant_id 
                FROM domains 
                WHERE id = %(website_id)s
            """, {'website_id': website_id})
            website = cur.fetchone()
            
        if not website:
            print(f"Website {website_id} not found")
            scan_jobs[website_id].status = "error"
            scan_jobs[website_id].error = "Website not found"
            return
            
        # Initialize crawl
        start_url = f"https://{website['domain']}"
        visited = set()
        to_visit = {start_url}
        total_contacts = 0
        pages_scanned = 0
        
        print(f"Starting scan of {website['domain']}")
        scan_jobs[website_id].status = "scanning"
        
        # Crawl pages
        while to_visit and pages_scanned < 100:  # Limit to 100 pages for safety
            url = to_visit.pop()
            if url in visited:
                continue
                
            try:
                # Process the page
                new_contacts, new_links = await process_url(url, website_id, db, visited)
                visited.add(url)
                to_visit.update(new_links)
                
                # Update progress
                total_contacts += new_contacts
                pages_scanned += 1
                
                if website_id in scan_jobs:
                    scan_jobs[website_id].pages_scanned = pages_scanned
                    scan_jobs[website_id].contacts_found = total_contacts
                    print(f"Progress: {pages_scanned} pages, {total_contacts} contacts")
                    
            except Exception as e:
                print(f"Error on page {url}: {str(e)}")
                continue
        
        # Update website record
        try:
            website.last_scan = datetime.utcnow()
            db.commit()
        except Exception as e:
            print(f"Error updating website: {str(e)}")
            db.rollback()
        
        # Mark as complete
        if website_id in scan_jobs:
            scan_jobs[website_id].status = "completed"
            scan_jobs[website_id].pages_scanned = pages_scanned
            scan_jobs[website_id].contacts_found = total_contacts
            print(f"Scan complete: {pages_scanned} pages, {total_contacts} contacts")
            
    except Exception as e:
        print(f"Scan failed: {str(e)}")
        if website_id in scan_jobs:
            scan_jobs[website_id].status = "error"
            scan_jobs[website_id].error = str(e)
            
    finally:
        try:
            db.close()
        except Exception as e:
            print(f"Error closing database: {str(e)}")

def classify_email_type(email: str, domain: str) -> EmailType:
    """Determine the type of an email address"""
    if is_service_email(email):
        return EmailType.SERVICE
    elif is_corporate_email(email, domain):
        return EmailType.CORPORATE
    elif is_gmail_email(email) or '@' in email and not is_corporate_email(email, domain):
        return EmailType.FREE
    return EmailType.UNKNOWN
