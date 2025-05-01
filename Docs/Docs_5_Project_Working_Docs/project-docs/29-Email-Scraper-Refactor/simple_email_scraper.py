import re
import sys
import argparse
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict, Any, Tuple
import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime

# --- Email detection patterns ---
EMAIL_PATTERNS = {
    'service': r'(?i)(info|support|sales|contact|help|admin|webmaster|service)@[\w\.-]+\.\w+',
    'general': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    # More specific pattern to catch obfuscated emails with entities
    'obfuscated': r'[a-zA-Z0-9._%+-]+\s*(?:&#64;|@|at|\[at\]|\(at\))\s*[a-zA-Z0-9.-]+\s*(?:&#46;|\.|\.|dot|\[dot\]|\(dot\))\s*[a-zA-Z]{2,}'
}

# --- User agent for requests ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Test data ---
TEST_HTML = """
<html>
<body>
    <p>Contact us at info@example.com or support@example.com.</p>
    <p>For sales inquiries: <a href="mailto:sales@example.com">Click here</a></p>
    <div>Reach our admin at admin [at] example [dot] com</div>
    <span>developer&#64;example&#46;com</span>
    <form>
        <input type="hidden" name="contactEmail" value="hidden@example.com">
    </form>
</body>
</html>
"""

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
        return "SERVICE"
    elif is_corporate_email(email_lower, domain_lower):
        return "CORPORATE"
    elif is_gmail_email(email_lower) or ('@' in email_lower and not is_corporate_email(email_lower, domain_lower)):
        return "FREE"
    return "UNKNOWN"

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
            if href and href.startswith('mailto:'):
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
            field_name = field.get('name', '').lower()
            field_id = field.get('id', '').lower()
            field_value = field.get('value', '')

            # If it seems to be an email field and has a value
            if (any(name in field_name for name in email_field_names) or
                any(name in field_id for name in email_field_names)) and '@' in field_value:
                context = f"Found in form field: {field}"
                emails.append((field_value, context))

    # 3. Check for contact info in meta tags
    for meta in soup.find_all('meta'):
        if isinstance(meta, Tag):
            content = meta.get('content', '')
            if '@' in content and '.' in content:
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
                if href is not None and not href.startswith('mailto:'):
                    url = urljoin(base_url, str(href))
                    if is_valid_url(url, base_domain_netloc):
                        links.add(url)
        except Exception as e:
            print(f"Error processing link: {e}")

    return links

def process_url(url: str, domain: str) -> Tuple[List[Dict[str, Any]], Set[str]]:
    """Process a single URL for emails and return new links
    Returns (list of emails found, new links found)"""
    found_emails = []
    new_links = set()

    try:
        print(f"Processing URL: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract emails from multiple sources
        text_content = soup.get_text()
        emails_from_text = extract_emails_from_text(text_content)
        emails_from_html = extract_emails_from_soup(soup)

        # Combine all emails found
        all_extracted_emails = emails_from_text + emails_from_html

        # Get base URL and find links for next pages
        base_url = get_base_url(url)
        new_links = find_links(soup, base_url)

        # Process found emails
        unique_emails = set()  # Track unique emails to avoid duplicates

        for email, context in all_extracted_emails:
            email_lower = email.lower()

            # Skip if we've already processed this email for this URL
            if email_lower in unique_emails:
                continue

            unique_emails.add(email_lower)
            email_type = classify_email_type(email_lower, domain)

            found_emails.append({
                'email': email_lower,
                'type': email_type,
                'is_gmail': is_gmail_email(email_lower),
                'context': context,
                'source_url': url,
                'found_at': datetime.now().isoformat()
            })

            print(f"Found email: {email_lower} ({email_type}) on page {url}")

    except requests.RequestException as e:
        print(f"Request error for {url}: {str(e)}")
    except Exception as e:
        print(f"Unexpected error processing {url}: {str(e)}")

    return found_emails, new_links

def crawl_website(start_url: str, max_pages: int = 10, verbose: bool = False) -> List[Dict[str, Any]]:
    """Crawl a website starting from start_url and extract emails
    Returns a list of all emails found"""
    if not start_url.startswith(('http://', 'https://')):
        start_url = 'https://' + start_url

    # Extract domain from URL
    domain = urlparse(start_url).netloc

    print(f"Starting crawl of {start_url} (domain: {domain}) with max_pages={max_pages}")

    visited = set()
    to_visit = {start_url}
    all_emails = []
    pages_scanned = 0

    while to_visit and pages_scanned < max_pages:
        current_url = to_visit.pop()
        if current_url in visited:
            continue

        visited.add(current_url)
        pages_scanned += 1

        if verbose:
            print(f"[{pages_scanned}/{max_pages}] Processing: {current_url}")

        emails, new_links = process_url(current_url, domain)
        all_emails.extend(emails)

        # Add new links to visit (but don't revisit what we've seen)
        to_visit.update(new_links - visited)

        if verbose:
            print(f"Found {len(emails)} emails, {len(new_links)} new links. " +
                  f"Total emails so far: {len(all_emails)}. Queue size: {len(to_visit)}")

    print(f"Crawl complete. Scanned {pages_scanned} pages, found {len(all_emails)} emails.")
    return all_emails

def run_test() -> None:
    """Run a test on the sample HTML data"""
    print("Running test with sample HTML...")
    soup = BeautifulSoup(TEST_HTML, 'html.parser')

    print("\nExtract from text content:")
    text_emails = extract_emails_from_text(soup.get_text())
    for email, context in text_emails:
        print(f"- {email}: {context}")

    print("\nExtract from HTML structure:")
    html_emails = extract_emails_from_soup(soup)
    for email, context in html_emails:
        print(f"- {email}: {context}")

    all_emails = text_emails + html_emails
    print(f"\nTotal unique emails: {len(set(email for email, _ in all_emails))}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple Email Scraper')
    parser.add_argument('url', nargs='?', help='URL to scrape emails from')
    parser.add_argument('--max-pages', type=int, default=10, help='Maximum number of pages to crawl')
    parser.add_argument('--output', help='Output file to save results (JSON format)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--test', action='store_true', help='Run test on sample HTML data')

    args = parser.parse_args()

    # Run test if --test flag is provided
    if args.test:
        run_test()
        sys.exit(0)

    # Validate URL was provided if not in test mode
    if not args.url:
        parser.error("URL is required unless --test is specified")

    try:
        emails = crawl_website(args.url, args.max_pages, args.verbose)

        # Print summary of results
        print("\n--- Email Scraping Results ---")
        print(f"Total emails found: {len(emails)}")

        # Count by type
        email_types = {}
        for email in emails:
            email_type = email['type']
            email_types[email_type] = email_types.get(email_type, 0) + 1

        for email_type, count in email_types.items():
            print(f"- {email_type}: {count}")

        # Print some sample emails
        if emails:
            print("\nSample emails found:")
            for email in emails[:5]:  # Show up to 5 emails
                print(f"- {email['email']} ({email['type']}) from {email['source_url']}")

            if len(emails) > 5:
                print(f"...and {len(emails) - 5} more")

        # Save to file if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(emails, f, indent=2)
            print(f"\nResults saved to {args.output}")

    except KeyboardInterrupt:
        print("\nCrawl interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
