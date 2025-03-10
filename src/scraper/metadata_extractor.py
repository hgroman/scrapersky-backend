"""Website metadata extraction module."""
import logging
import re
from typing import Dict, Any, Optional, List, Union, cast
import aiohttp
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement
from urllib.parse import urljoin
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global session manager
class SessionManager:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
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

async def detect_site_metadata(url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Extract metadata from a website with retry logic."""
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            session = await session_manager.get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                    if response.status >= 500:  # Server errors might be temporary
                        retry_count += 1
                        await asyncio.sleep(1 * retry_count)  # Exponential backoff
                        continue
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                metadata = {
                    "title": _extract_title(soup),
                    "description": _extract_description(soup),
                    "language": _extract_language(soup),
                    "is_wordpress": _detect_wordpress(soup, html),
                    "wordpress_version": _extract_wordpress_version(html) if _detect_wordpress(soup, html) else None,
                    "has_elementor": _detect_elementor(soup, html),
                    "favicon_url": _extract_favicon(soup, url),
                    "logo_url": _extract_logo(soup, url),
                    "contact_info": _extract_contact_info(soup, html),
                    "social_links": _extract_social_links(soup),
                    "tech_stack": _detect_tech_stack(soup, html),
                    "performance": _analyze_performance(soup)
                }

                return metadata

        except aiohttp.ClientError as e:
            last_error = e
            logger.error(f"Network error fetching {url} (attempt {retry_count+1}/{max_retries}): {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                await asyncio.sleep(1 * retry_count)  # Exponential backoff
        except Exception as e:
            logger.error(f"Error extracting metadata from {url}: {str(e)}")
            return None

    # All retries failed
    if last_error:
        logger.error(f"All {max_retries} attempts failed for {url}: {str(last_error)}")
    return None

def _extract_title(soup: BeautifulSoup) -> Optional[str]:
    """Extract page title."""
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        return cast(str, title_tag.string).strip()
    return None

def _extract_description(soup: BeautifulSoup) -> Optional[str]:
    """Extract meta description."""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and isinstance(meta_desc, Tag):
        content = meta_desc.get('content', '')
        if content:
            return str(content).strip()
    return None

def _extract_language(soup: BeautifulSoup) -> Optional[str]:
    """Extract page language."""
    html_tag = soup.find('html')
    if html_tag and isinstance(html_tag, Tag):
        lang = html_tag.get('lang', '')
        if lang:
            return str(lang).strip()
    return None

def _detect_wordpress(soup: BeautifulSoup, html: str) -> bool:
    """Detect if site is using WordPress."""
    wp_indicators = [
        'wp-content',
        'wp-includes',
        'wordpress',
        'Generated by WordPress'
    ]
    return any(indicator.lower() in html.lower() for indicator in wp_indicators)

def _extract_wordpress_version(html: str) -> Optional[str]:
    """Extract WordPress version if present."""
    version_pattern = r'meta name="generator" content="WordPress ([0-9.]+)"'
    if match := re.search(version_pattern, html):
        return match.group(1)
    return None

def _detect_elementor(soup: BeautifulSoup, html: str) -> bool:
    """Detect if site uses Elementor."""
    elementor_indicators = [
        'elementor',
        'elementor-widget',
        'e-con-inner'
    ]
    return any(indicator in html for indicator in elementor_indicators)

def _extract_favicon(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract favicon URL."""
    favicon_links = soup.find_all('link', rel=['icon', 'shortcut icon'])
    if favicon_links:
        favicon_href = favicon_links[0].get('href')
        return urljoin(base_url, favicon_href) if favicon_href else None
    return None

def _extract_logo(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract website logo URL."""
    logo_selectors = [
        {'class_': 'logo'},
        {'class_': 'site-logo'},
        {'id': 'logo'},
        {'alt': 'logo'}
    ]

    for selector in logo_selectors:
        if logo := soup.find('img', **selector):
            logo_src = logo.get('src')
            return urljoin(base_url, logo_src) if logo_src else None
    return None

def _extract_contact_info(soup: BeautifulSoup, html: str) -> Dict[str, List[str]]:
    """Extract contact information."""
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(email_pattern, html)))

    # Phone pattern (basic)
    phone_pattern = r'\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
    phones = list(set(re.findall(phone_pattern, html)))

    return {
        "email": emails[:5],  # Limit to first 5 unique emails
        "phone": phones[:3]   # Limit to first 3 unique phone numbers
    }

def _extract_social_links(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    """Extract social media links."""
    social_patterns = {
        'facebook': r'facebook\.com/[^"\'<>\s]+',
        'twitter': r'twitter\.com/[^"\'<>\s]+',
        'linkedin': r'linkedin\.com/[^"\'<>\s]+',
        'instagram': r'instagram\.com/[^"\'<>\s]+',
        'youtube': r'youtube\.com/[^"\'<>\s]+'
    }

    social_links = {}
    for platform, pattern in social_patterns.items():
        if link := soup.find('a', href=re.compile(pattern)):
            social_links[platform] = link.get('href')
        else:
            social_links[platform] = None

    return social_links

def _detect_tech_stack(soup: BeautifulSoup, html: str) -> Dict[str, List[str]]:
    """Detect technology stack used on the website."""
    tech_stack = {
        "cms": [],
        "frameworks": [],
        "analytics": [],
        "widgets": []
    }

    # CMS detection
    if _detect_wordpress(soup, html):
        tech_stack["cms"].append("WordPress")
        if _detect_elementor(soup, html):
            tech_stack["frameworks"].append("Elementor")

    # Analytics
    if 'google-analytics.com' in html or 'gtag' in html:
        tech_stack["analytics"].append("Google Analytics")
    if 'facebook.com/tr' in html:
        tech_stack["analytics"].append("Facebook Pixel")

    # Common frameworks
    framework_patterns = {
        'bootstrap': r'bootstrap(?:\.min)?\.(?:css|js)',
        'jquery': r'jquery(?:\.min)?\.js',
        'react': r'react(?:\.min)?\.js|react-dom',
        'vue': r'vue(?:\.min)?\.js',
        'angular': r'angular(?:\.min)?\.js'
    }

    for framework, pattern in framework_patterns.items():
        if re.search(pattern, html, re.I):
            tech_stack["frameworks"].append(framework.title())

    # Widgets and integrations
    widget_patterns = {
        'Intercom': r'intercom',
        'Drift': r'drift',
        'Zendesk': r'zendesk',
        'HubSpot': r'hubspot',
        'Mailchimp': r'mailchimp'
    }

    for widget, pattern in widget_patterns.items():
        if re.search(pattern, html, re.I):
            tech_stack["widgets"].append(widget)

    return tech_stack

def _analyze_performance(soup: BeautifulSoup) -> Dict[str, int]:
    """Analyze basic performance metrics."""
    return {
        "image_count": len(soup.find_all('img')),
        "script_count": len(soup.find_all('script')),
        "css_count": len(soup.find_all('link', rel='stylesheet')),
        "form_count": len(soup.find_all('form')),
        "link_count": len(soup.find_all('a')),
        "total_elements": len(soup.find_all())
    }
