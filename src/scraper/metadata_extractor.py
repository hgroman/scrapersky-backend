"""Website metadata extraction module."""

import logging
import re
from typing import Any, Dict, List, Optional, cast
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup, Tag

from ..utils.scraper_api import ScraperAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global session manager
class SessionManager:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            logger.info("Created new aiohttp ClientSession")
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            logger.info("Closing aiohttp ClientSession")
            await self._session.close()
            self._session = None
            logger.info("aiohttp ClientSession closed successfully")
        else:
            logger.info("No active aiohttp ClientSession to close")


session_manager = SessionManager()


async def detect_site_metadata(
    domain: str,
    max_retries: int = 3,
    use_test_html: bool = False,
    test_html_content: Optional[str] = None,
):
    """
    Detect metadata from a website, including CMS, emails, and social media links.

    Args:
        domain: The domain to scan (without http/https)
        max_retries: Number of retries for network requests
        use_test_html: Whether to use provided test HTML instead of making network requests
        test_html_content: HTML content to use for testing (only used if use_test_html is True)

    Returns:
        Dictionary with metadata
    """
    logger.info(f"Starting metadata extraction for {domain}")

    metadata = {
        "title": None,
        "description": None,
        "language": None,
        "is_wordpress": False,
        "wordpress_version": None,
        "wordpress_theme": None,
        "has_elementor": False,
        "elementor_version": None,
        "has_divi": False,
        "has_woocommerce": False,
        "has_contact_form7": False,
        "has_yoast_seo": False,
        "has_wpforms": False,
        "favicon_url": None,
        "logo_url": None,
        "contact_info": {"email": [], "phone": []},
        "social_links": {},
    }

    # Skip network requests if we're using test HTML
    if use_test_html and test_html_content:
        logger.info(
            "Using provided test HTML content instead of making network requests"
        )
        html_content = test_html_content
    else:
        # Try to get the page content using ScraperAPI
        try:
            logger.info(f"Using ScraperAPI to fetch content for {domain}")
            scraper_api = ScraperAPIClient()

            # Ensure all connections use HTTPS for security
            if domain.startswith("http://"):
                # Convert HTTP to HTTPS
                url = "https://" + domain[7:]
                logger.info(f"Upgrading HTTP to HTTPS: {domain} → {url}")
            elif domain.startswith("https://"):
                # Already HTTPS, use as-is
                url = domain
            else:
                # No protocol specified, add HTTPS
                url = f"https://{domain}"

            logger.info(f"Fetching URL: {url}")
            # Only enable JS rendering if explicitly configured  
            enable_js = os.getenv('SCRAPER_API_ENABLE_JS_RENDERING', 'false').lower() == 'true'
            max_retries = int(os.getenv('SCRAPER_API_MAX_RETRIES', '1'))
            html_content = await scraper_api.fetch(
                url, render_js=enable_js, retries=max_retries
            )
            logger.info(f"Successfully fetched content for {domain} using ScraperAPI")
            await scraper_api.close()
        except Exception as e:
            logger.error(f"ScraperAPI error fetching {domain}: {str(e)}")
            return None

    # Get title and description
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract title
    title_tag = soup.find("title")
    if title_tag and isinstance(title_tag, Tag):
        title_content = title_tag.get_text() if hasattr(title_tag, "get_text") else None
        if title_content:
            metadata["title"] = title_content.strip()

    # Extract description
    description_meta = soup.find("meta", {"name": "description"}) or soup.find(
        "meta", {"property": "og:description"}
    )
    if (
        description_meta
        and isinstance(description_meta, Tag)
        and description_meta.get("content")
    ):
        metadata["description"] = str(description_meta.get("content", "")).strip()

    # Extract language
    lang_attr = soup.html.get("lang") if soup.html else None
    if lang_attr:
        metadata["language"] = str(lang_attr)

    # Detect WordPress
    is_wordpress = _detect_wordpress(soup, html_content)
    if is_wordpress:
        metadata["is_wordpress"] = True

        # Get WordPress version
        wp_version = _extract_wordpress_version(html_content)
        if wp_version:
            metadata["wordpress_version"] = wp_version

        # Detect Elementor
        has_elementor = _detect_elementor(soup, html_content)
        if has_elementor:
            metadata["has_elementor"] = True

    # Extract favicon
    favicon = _extract_favicon(soup, domain)
    if favicon:
        metadata["favicon_url"] = favicon

    # Extract logo
    logo = _extract_logo(soup, domain)
    if logo:
        metadata["logo_url"] = logo

    # Extract emails
    emails = _extract_contact_info(soup, html_content)["email"]
    if emails:
        metadata["contact_info"]["email"] = emails

    # Extract phone numbers
    phones = _extract_contact_info(soup, html_content)["phone"]
    if phones:
        metadata["contact_info"]["phone"] = phones

    # Extract social media links
    social_links = _extract_social_links(soup)
    if social_links:
        metadata["social_links"] = social_links

    return metadata


def _extract_title(soup: BeautifulSoup) -> Optional[str]:
    """Extract page title."""
    title_tag = soup.find("title")
    if title_tag and isinstance(title_tag, Tag):
        title_content = title_tag.get_text() if hasattr(title_tag, "get_text") else None
        if title_content:
            return title_content.strip()
    return None


def _extract_description(soup: BeautifulSoup) -> Optional[str]:
    """Extract meta description."""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and isinstance(meta_desc, Tag):
        content = meta_desc.get("content", "")
        if content:
            return str(content).strip()
    return None


def _extract_language(soup: BeautifulSoup) -> Optional[str]:
    """Extract page language."""
    html_tag = soup.find("html")
    if html_tag and isinstance(html_tag, Tag):
        lang = html_tag.get("lang", "")
        if lang:
            return str(lang).strip()
    return None


def _detect_wordpress(soup: BeautifulSoup, html: str) -> bool:
    """Detect if site is using WordPress."""
    wp_indicators = ["wp-content", "wp-includes", "wordpress", "Generated by WordPress"]
    return any(indicator.lower() in html.lower() for indicator in wp_indicators)


def _extract_wordpress_version(html: str) -> Optional[str]:
    """Extract WordPress version if present."""
    version_pattern = r'meta name="generator" content="WordPress ([0-9.]+)"'
    if match := re.search(version_pattern, html):
        return match.group(1)
    return None


def _detect_elementor(soup: BeautifulSoup, html: str) -> bool:
    """Detect if site uses Elementor."""
    elementor_indicators = ["elementor", "elementor-widget", "e-con-inner"]
    return any(indicator in html for indicator in elementor_indicators)


def _extract_favicon(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract favicon URL."""
    favicon_links = soup.find_all("link", rel=["icon", "shortcut icon"])
    if favicon_links:
        # Use cast to tell type checker this is a Tag
        favicon = cast(Tag, favicon_links[0])
        favicon_href = favicon.get("href")
        if favicon_href:
            return urljoin(base_url, str(favicon_href))
    return None


def _extract_logo(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract website logo URL."""
    logo_selectors = [
        {"class_": "logo"},
        {"class_": "site-logo"},
        {"id": "logo"},
        {"alt": "logo"},
    ]

    for selector in logo_selectors:
        # Use find with proper typing
        logo = soup.find("img", attrs=cast(Dict[str, Any], selector))
        if logo:
            # Use cast to tell type checker this is a Tag
            logo_tag = cast(Tag, logo)
            logo_src = logo_tag.get("src")
            if logo_src:
                return urljoin(base_url, str(logo_src))
    return None


def _extract_contact_info(soup: BeautifulSoup, html: str) -> Dict[str, List[str]]:
    """Extract contact information."""
    # Email pattern
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = list(set(re.findall(email_pattern, html)))

    # Phone pattern (basic)
    phone_pattern = r"\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"
    phones = list(set(re.findall(phone_pattern, html)))

    return {
        "email": emails[:5],  # Limit to first 5 unique emails
        "phone": phones[:3],  # Limit to first 3 unique phone numbers
    }


def _extract_social_links(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    """Extract social media links."""
    social_patterns = {
        "facebook": r'facebook\.com/[^"\'<>\s]+',
        "twitter": r'twitter\.com/[^"\'<>\s]+',
        "linkedin": r'linkedin\.com/[^"\'<>\s]+',
        "instagram": r'instagram\.com/[^"\'<>\s]+',
        "youtube": r'youtube\.com/[^"\'<>\s]+',
    }

    social_links = {}
    for platform, pattern in social_patterns.items():
        link = soup.find("a", href=re.compile(pattern))
        if link:
            # Use cast to tell type checker this is a Tag
            link_tag = cast(Tag, link)
            href = link_tag.get("href")
            social_links[platform] = str(href) if href else None
        else:
            social_links[platform] = None

    return social_links


def _detect_tech_stack(soup: BeautifulSoup, html: str) -> Dict[str, List[str]]:
    """Detect technology stack used on the website."""
    tech_stack = {"cms": [], "frameworks": [], "analytics": [], "widgets": []}

    # CMS detection
    if _detect_wordpress(soup, html):
        tech_stack["cms"].append("WordPress")
        if _detect_elementor(soup, html):
            tech_stack["frameworks"].append("Elementor")

    # Analytics
    if "google-analytics.com" in html or "gtag" in html:
        tech_stack["analytics"].append("Google Analytics")
    if "facebook.com/tr" in html:
        tech_stack["analytics"].append("Facebook Pixel")

    # Common frameworks
    framework_patterns = {
        "bootstrap": r"bootstrap(?:\.min)?\.(?:css|js)",
        "jquery": r"jquery(?:\.min)?\.js",
        "react": r"react(?:\.min)?\.js|react-dom",
        "vue": r"vue(?:\.min)?\.js",
        "angular": r"angular(?:\.min)?\.js",
    }

    for framework, pattern in framework_patterns.items():
        if re.search(pattern, html, re.I):
            tech_stack["frameworks"].append(framework.title())

    # Widgets and integrations
    widget_patterns = {
        "Intercom": r"intercom",
        "Drift": r"drift",
        "Zendesk": r"zendesk",
        "HubSpot": r"hubspot",
        "Mailchimp": r"mailchimp",
    }

    for widget, pattern in widget_patterns.items():
        if re.search(pattern, html, re.I):
            tech_stack["widgets"].append(widget)

    return tech_stack


def _analyze_performance(soup: BeautifulSoup) -> Dict[str, int]:
    """Analyze basic performance metrics."""
    return {
        "image_count": len(soup.find_all("img")),
        "script_count": len(soup.find_all("script")),
        "css_count": len(soup.find_all("link", rel="stylesheet")),
        "form_count": len(soup.find_all("form")),
        "link_count": len(soup.find_all("a")),
        "total_elements": len(soup.find_all()),
    }
