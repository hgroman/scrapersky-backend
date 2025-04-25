"""
Sitemap analyzer module for parsing and extracting data from XML sitemaps.

This module provides functionality to:
1. Discover sitemap files from a domain through various methods
2. Parse XML sitemaps and extract URLs and metadata
3. Support different sitemap types (standard, index, image, news, video)
4. Follow sitemap best practices and robots.txt directives
"""

import gzip
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

import aiohttp
from bs4 import BeautifulSoup, Tag

from ..models import DiscoveryMethod, SitemapType  # type: ignore
from ..scraper.domain_utils import get_domain_url, standardize_domain
from ..scraper.utils import validate_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# XML namespace mappings
NAMESPACES = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
    "video": "http://www.google.com/schemas/sitemap-video/1.1",
    "xhtml": "http://www.w3.org/1999/xhtml",
}

# Common sitemap paths to check
COMMON_SITEMAP_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/sitemap-index.xml",
    "/sitemap.php",
    "/sitemap.txt",
    "/sitemap/sitemap.xml",
    "/wp-sitemap.xml",
    "/wp-sitemap-index.xml",
    "/wp-sitemap-posts-post-1.xml",
    "/sitemap-posts-post-1.xml",
    "/sitemap-pages-post-1.xml",
    "/sitemap-categories-1.xml",
    "/sitemap/index.xml",
    "/post-sitemap.xml",
    "/page-sitemap.xml",
    "/product-sitemap.xml",
    "/category-sitemap.xml",
    "/sitemapindex.xml",
]


class SitemapAnalyzer:
    """Class for analyzing and extracting data from XML sitemaps."""

    def __init__(self):
        """Initialize the SitemapAnalyzer."""
        self.session: Optional[aiohttp.ClientSession] = None
        self._robots_cache: Dict[str, str] = {}
        self._sitemap_urls_cache: Dict[str, List[str]] = {}
        self.processed_urls: Set[str] = set()

    async def ensure_session(self) -> aiohttp.ClientSession:
        """Ensure aiohttp session exists and return it."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def close_session(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def discover_sitemaps(
        self, domain: str, follow_robots_txt: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Discover sitemap files for a domain using multiple methods.

        Args:
            domain: Domain to analyze (e.g., example.com)
            follow_robots_txt: Whether to check robots.txt for sitemap directives

        Returns:
            List of discovered sitemap URLs with metadata
        """
        # Standardize domain and ensure it's valid
        try:
            clean_domain = standardize_domain(domain)
            base_url = get_domain_url(clean_domain)
            logger.info(
                f"SITEMAP DEBUG: Starting discovery for {clean_domain}, base URL: {base_url}"
            )
        except ValueError as e:
            logger.error(f"Invalid domain: {domain}, error: {str(e)}")
            return []

        # Initialize results list
        discovered_sitemaps = []
        sitemap_urls = set()

        # Get session
        session = await self.ensure_session()

        # Method 1: Check robots.txt if enabled
        if follow_robots_txt:
            logger.info(f"SITEMAP DEBUG: Checking robots.txt for {base_url}")
            robot_sitemaps = await self._extract_sitemaps_from_robots(base_url)
            logger.info(
                f"SITEMAP DEBUG: Found {len(robot_sitemaps)} sitemaps in robots.txt"
            )
            for sitemap_url in robot_sitemaps:
                if sitemap_url not in sitemap_urls:
                    sitemap_urls.add(sitemap_url)
                    discovered_sitemaps.append(
                        {
                            "url": sitemap_url,
                            "discovery_method": DiscoveryMethod.ROBOTS_TXT,
                            "domain": clean_domain,
                        }
                    )
                    logger.info(
                        f"SITEMAP DEBUG: Added sitemap from robots.txt: {sitemap_url}"
                    )

        # Method 2: Check common sitemap paths
        logger.info(
            f"SITEMAP DEBUG: Checking {len(COMMON_SITEMAP_PATHS)} common sitemap paths"
        )
        for path in COMMON_SITEMAP_PATHS:
            sitemap_url = urljoin(base_url, path)
            if sitemap_url in sitemap_urls:
                continue

            try:
                # Check if sitemap exists at this URL
                logger.info(f"SITEMAP DEBUG: Checking common path: {sitemap_url}")
                is_valid, meta = await self._validate_sitemap_url(sitemap_url)
                if is_valid:
                    sitemap_urls.add(sitemap_url)
                    discovered_sitemaps.append(
                        {
                            "url": sitemap_url,
                            "discovery_method": DiscoveryMethod.COMMON_PATH,
                            "domain": clean_domain,
                            **meta,
                        }
                    )
                    logger.info(
                        f"SITEMAP DEBUG: Valid sitemap found at common path: {sitemap_url}"
                    )
                else:
                    logger.info(
                        f"SITEMAP DEBUG: Invalid sitemap at common path: {sitemap_url}, reason: {meta.get('error', 'unknown')}"
                    )
            except Exception as e:
                logger.warning(f"Error checking sitemap at {sitemap_url}: {str(e)}")
                logger.info(
                    f"SITEMAP DEBUG: Exception checking common path: {sitemap_url}, error: {str(e)}"
                )

        # Method 3: Look for sitemap links in HTML
        try:
            html_sitemaps = await self._extract_sitemaps_from_html(base_url)
            for sitemap_url in html_sitemaps:
                if sitemap_url not in sitemap_urls:
                    sitemap_urls.add(sitemap_url)
                    discovered_sitemaps.append(
                        {
                            "url": sitemap_url,
                            "discovery_method": DiscoveryMethod.HTML_LINK,
                            "domain": clean_domain,
                        }
                    )
        except Exception as e:
            logger.warning(f"Error extracting sitemaps from HTML: {str(e)}")

        # Validate and add metadata for sitemaps found in robots.txt and HTML
        for i, sitemap in enumerate(discovered_sitemaps):
            if "sitemap_type" not in sitemap:
                try:
                    is_valid, meta = await self._validate_sitemap_url(sitemap["url"])
                    if is_valid:
                        discovered_sitemaps[i].update(meta)
                    else:
                        # Mark invalid sitemaps but keep them in results
                        discovered_sitemaps[i]["is_valid"] = False
                        discovered_sitemaps[i]["error"] = meta.get(
                            "error", "Invalid sitemap format"
                        )
                except Exception as e:
                    logger.warning(
                        f"Error validating sitemap {sitemap['url']}: {str(e)}"
                    )
                    discovered_sitemaps[i]["is_valid"] = False
                    discovered_sitemaps[i]["error"] = str(e)

        return discovered_sitemaps

    async def _extract_sitemaps_from_robots(self, base_url: str) -> List[str]:
        """
        Extract sitemap URLs from robots.txt.

        Args:
            base_url: Base URL of the domain

        Returns:
            List of sitemap URLs found in robots.txt
        """
        robots_url = urljoin(base_url, "/robots.txt")
        sitemaps = []

        # Return cached results if available
        if robots_url in self._sitemap_urls_cache:
            return self._sitemap_urls_cache[robots_url]

        # Get session
        session = await self.ensure_session()

        try:
            start_time = time.time()
            async with session.get(
                robots_url, allow_redirects=True, timeout=10
            ) as response:
                response_time = time.time() - start_time

                if response.status != 200:
                    logger.info(
                        f"No robots.txt found at {robots_url} (status: {response.status})"
                    )
                    self._sitemap_urls_cache[robots_url] = []
                    return []

                robots_content = await response.text()

                # Store robots.txt content in cache
                self._robots_cache[base_url] = robots_content

                # Extract Sitemap: directives
                sitemap_matches = re.findall(r"(?i)Sitemap:\s*([^\s]+)", robots_content)

                # Validate and normalize URLs
                for url in sitemap_matches:
                    url = url.strip()
                    if validate_url(url):
                        sitemaps.append(url)
                    else:
                        # Try to join with base_url if it's a relative path
                        full_url = urljoin(base_url, url)
                        if validate_url(full_url):
                            sitemaps.append(full_url)

                # Cache the results
                self._sitemap_urls_cache[robots_url] = sitemaps
                return sitemaps

        except Exception as e:
            logger.warning(f"Error retrieving robots.txt from {robots_url}: {str(e)}")
            self._sitemap_urls_cache[robots_url] = []
            return []

    async def _extract_sitemaps_from_html(self, base_url: str) -> List[str]:
        """
        Extract sitemap URLs from HTML page.

        Args:
            base_url: Base URL of the domain

        Returns:
            List of sitemap URLs found in HTML
        """
        sitemaps = []

        # Get session
        session = await self.ensure_session()

        try:
            async with session.get(
                base_url, allow_redirects=True, timeout=15
            ) as response:
                if response.status != 200:
                    logger.info(
                        f"Could not get HTML from {base_url} (status: {response.status})"
                    )
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Look for sitemap links in <link> tags
                for link in soup.find_all("link", {"rel": "sitemap"}):
                    if isinstance(link, Tag) and "href" in link.attrs:
                        href_value = link.attrs["href"]
                        if isinstance(href_value, str):
                            sitemap_url = urljoin(base_url, href_value)
                            if validate_url(sitemap_url):
                                sitemaps.append(sitemap_url)

                # Look for common sitemap reference patterns in HTML
                sitemap_patterns = [
                    r'<a\s+[^>]*href=[\'"]((?:https?:)?//[^\'"]*/sitemap[^\'"]*)[\'""][^>]*>',
                    r'sitemap:\s+[\'"]?(https?://[^\'"\s]+)',
                    r'sitemapUrl[\'"]?\s*(?:=|:)\s*[\'"]?(https?://[^\'"\s]+)',
                ]

                for pattern in sitemap_patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    for match in matches:
                        sitemap_url = urljoin(base_url, match)
                        if (
                            validate_url(sitemap_url)
                            and "/sitemap" in sitemap_url.lower()
                        ):
                            sitemaps.append(sitemap_url)

                # Deduplicate
                return list(set(sitemaps))

        except Exception as e:
            logger.warning(
                f"Error extracting sitemaps from HTML at {base_url}: {str(e)}"
            )
            return []

    async def _validate_sitemap_url(self, url: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a sitemap URL and extract basic metadata.

        Args:
            url: Sitemap URL to validate

        Returns:
            Tuple of (is_valid, metadata_dict)
        """
        # Get session
        session = await self.ensure_session()
        logger.info(f"SITEMAP DEBUG: Validating sitemap URL: {url}")

        metadata = {
            "sitemap_type": SitemapType.STANDARD,
            "is_gzipped": False,
            "response_time_ms": 0,
            "size_bytes": 0,
            "status_code": 0,
        }

        try:
            start_time = time.time()
            async with session.get(url, allow_redirects=True, timeout=20) as response:
                metadata["response_time_ms"] = int((time.time() - start_time) * 1000)
                metadata["status_code"] = response.status
                logger.info(
                    f"SITEMAP DEBUG: Response status for {url}: {response.status}"
                )

                if response.status != 200:
                    logger.info(
                        f"SITEMAP DEBUG: Sitemap rejected - non-200 status: {response.status}"
                    )
                    return False, {"error": f"HTTP status {response.status}"}

                # Get content length if available
                if "Content-Length" in response.headers:
                    metadata["size_bytes"] = int(response.headers["Content-Length"])
                    logger.info(
                        f"SITEMAP DEBUG: Content-Length: {metadata['size_bytes']} bytes"
                    )

                # Check content type
                content_type = response.headers.get("Content-Type", "").lower()
                logger.info(f"SITEMAP DEBUG: Content-Type for {url}: {content_type}")
                is_xml = (
                    "xml" in content_type
                    or "text/plain" in content_type
                    or "text/html" in content_type
                )
                metadata["is_gzipped"] = "gzip" in content_type or url.endswith(".gz")

                # Accept sitemap by URL pattern regardless of content type
                if url.endswith((".xml", ".gz")) or "sitemap" in url.lower():
                    logger.info(
                        f"SITEMAP DEBUG: Accepting potential sitemap at {url} despite content type: {content_type}"
                    )
                    is_xml = True

                if (
                    not is_xml
                    and not metadata["is_gzipped"]
                    and not url.endswith((".xml", ".gz"))
                ):
                    logger.info(
                        f"SITEMAP DEBUG: Rejecting sitemap due to content type: {content_type}"
                    )
                    return False, {"error": f"Not a sitemap: {content_type}"}

                # Get content (handle gzip if needed)
                if metadata["is_gzipped"] or url.endswith(".gz"):
                    content_bytes = await response.read()
                    try:
                        content = gzip.decompress(content_bytes).decode(
                            "utf-8", errors="ignore"
                        )
                    except Exception as e:
                        # If decompression fails, try normal content
                        logger.info(
                            f"SITEMAP DEBUG: Gzip decompression failed: {str(e)}"
                        )
                        content = content_bytes.decode("utf-8", errors="ignore")
                else:
                    content = await response.text(errors="ignore")

                # Record actual content size
                metadata["size_bytes"] = len(content)
                logger.info(
                    f"SITEMAP DEBUG: Actual content size: {metadata['size_bytes']} bytes"
                )
                logger.info(
                    "SITEMAP DEBUG: Content preview: "
                    + content[:200].replace("\n", " ")
                    + "..."
                )

                # Identify XML patterns
                has_xml_decl = "<?xml" in content
                has_urlset = "<urlset" in content
                has_sitemapindex = "<sitemapindex" in content
                has_url_tag = "<url>" in content
                has_loc_tag = "<loc>" in content
                logger.info(
                    f"SITEMAP DEBUG: XML validation - has XML decl: {has_xml_decl}, has urlset: {has_urlset}, has sitemapindex: {has_sitemapindex}, has_url_tag: {has_url_tag}, has_loc_tag: {has_loc_tag}"
                )

                # SUPER RELAXED VALIDATION: Accept any file with sitemap-like content
                if (
                    "sitemap" in url.lower()
                    or has_urlset
                    or has_sitemapindex
                    or has_loc_tag
                    or has_url_tag
                ):
                    logger.info(
                        f"SITEMAP DEBUG: Forcing acceptance due to sitemap-like content in URL: {url}"
                    )
                    # Set a default type
                    metadata["sitemap_type"] = SitemapType.STANDARD

                    # Try to determine type from content
                    if has_sitemapindex:
                        metadata["sitemap_type"] = SitemapType.INDEX
                    elif has_urlset or has_url_tag:
                        if "image:image" in content:
                            metadata["sitemap_type"] = SitemapType.IMAGE
                        elif "news:news" in content:
                            metadata["sitemap_type"] = SitemapType.NEWS
                        elif "video:video" in content:
                            metadata["sitemap_type"] = SitemapType.VIDEO
                        else:
                            metadata["sitemap_type"] = SitemapType.STANDARD

                    metadata["has_lastmod"] = "<lastmod>" in content
                    metadata["has_priority"] = "<priority>" in content
                    metadata["has_changefreq"] = "<changefreq>" in content

                    return True, metadata

                if (
                    not has_xml_decl
                    and not has_urlset
                    and not has_sitemapindex
                    and not has_loc_tag
                ):
                    logger.info(
                        "SITEMAP DEBUG: Rejecting - Missing XML declarations and sitemap tags"
                    )
                    # Dump first 200 chars of content for debugging
                    content_preview = content[:200].replace("\n", " ").replace("\r", "")
                    logger.info(f"SITEMAP DEBUG: Content preview: {content_preview}...")
                    return False, {"error": "Missing XML declarations"}

                # Detect sitemap type
                if has_sitemapindex:
                    metadata["sitemap_type"] = SitemapType.INDEX
                elif has_urlset:
                    if "image:image" in content:
                        metadata["sitemap_type"] = SitemapType.IMAGE
                    elif "news:news" in content:
                        metadata["sitemap_type"] = SitemapType.NEWS
                    elif "video:video" in content:
                        metadata["sitemap_type"] = SitemapType.VIDEO
                    else:
                        metadata["sitemap_type"] = SitemapType.STANDARD
                else:
                    return False, {"error": "Not a standard sitemap format"}

                # Get last modified time from header
                if "Last-Modified" in response.headers:
                    last_modified_str = response.headers["Last-Modified"]
                    try:
                        # Parse HTTP date format
                        last_modified = datetime.strptime(
                            last_modified_str, "%a, %d %b %Y %H:%M:%S %Z"
                        )
                        metadata["last_modified"] = last_modified.isoformat()
                    except Exception:
                        pass

                # Check for specific sitemap features
                metadata["has_lastmod"] = "<lastmod>" in content
                metadata["has_priority"] = "<priority>" in content
                metadata["has_changefreq"] = "<changefreq>" in content

                # Try to determine what generated the sitemap
                generators = {
                    "Yoast SEO": ["yoast", "wordpress"],
                    "WordPress": [
                        "wp-sitemap",
                        "wordpress",
                        "generated using wordpress",
                    ],
                    "Wix": ["wix.com", "wixsite"],
                    "Shopify": ["shopify"],
                    "Squarespace": ["squarespace"],
                    "NextJS": ["next-sitemap", "next.js"],
                    "Drupal": ["drupal"],
                    "Joomla": ["joomla"],
                    "Webflow": ["webflow"],
                }

                for generator, patterns in generators.items():
                    if any(pattern in content.lower() for pattern in patterns):
                        metadata["generator"] = generator
                        break

                return True, metadata

        except Exception as e:
            logger.warning(f"Error validating sitemap at {url}: {str(e)}")
            return False, {"error": str(e)}

    async def parse_sitemap(self, url: str, max_urls: int = 10000) -> Dict[str, Any]:
        """
        Parse a sitemap and extract URLs.

        Args:
            url: Sitemap URL to parse
            max_urls: Maximum number of URLs to extract

        Returns:
            Dictionary with parsed sitemap data including URLs
        """
        # Get session
        session = await self.ensure_session()
        logger.info(f"SITEMAP DEBUG: Parsing sitemap: {url}")

        result = {
            "url": url,
            "sitemap_type": None,
            "urls": [],
            "error": None,
            "url_count": 0,
            "has_lastmod": False,
            "has_priority": False,
            "has_changefreq": False,
            "response_time_ms": 0,
        }

        if url in self.processed_urls:
            result["error"] = "Already processed this URL"
            return result

        self.processed_urls.add(url)

        try:
            # Fetch the sitemap content
            start_time = time.time()
            async with session.get(url, allow_redirects=True, timeout=30) as response:
                logger.info(
                    f"SITEMAP DEBUG: Response status for parse_sitemap {url}: {response.status}"
                )
                result["response_time_ms"] = int((time.time() - start_time) * 1000)

                if response.status != 200:
                    result["error"] = f"HTTP status {response.status}"
                    return result

                # Get content type for debugging
                content_type = response.headers.get("Content-Type", "").lower()
                logger.info(
                    f"SITEMAP DEBUG: Content-Type for parse_sitemap {url}: {content_type}"
                )

                # Handle gzipped content
                is_gzipped = "gzip" in content_type or url.endswith(".gz")

                if is_gzipped:
                    content_bytes = await response.read()
                    try:
                        content = gzip.decompress(content_bytes).decode(
                            "utf-8", errors="ignore"
                        )
                    except Exception as e:
                        logger.warning(
                            f"SITEMAP DEBUG: Gzip decompression failed: {str(e)}"
                        )
                        content = content_bytes.decode("utf-8", errors="ignore")
                else:
                    content = await response.text(errors="ignore")

                if not content or len(content) < 30:
                    result["error"] = "Empty or too small content"
                    return result

                logger.info(
                    f"SITEMAP DEBUG: Got sitemap content length: {len(content)} chars"
                )
                logger.info(
                    "SITEMAP DEBUG: Content preview: "
                    + content[:200].replace("\n", " ")
                    + "..."
                )

                # Check for key sitemap patterns
                has_xml_decl = "<?xml" in content
                has_urlset = "<urlset" in content
                has_sitemapindex = "<sitemapindex" in content
                has_url_tag = "<url>" in content
                has_loc_tag = "<loc>" in content

                logger.info(
                    f"SITEMAP DEBUG: XML patterns - has XML decl: {has_xml_decl}, has urlset: {has_urlset}, has sitemapindex: {has_sitemapindex}, has_url_tag: {has_url_tag}, has_loc_tag: {has_loc_tag}"
                )

                # Extract URLs using regex for robustness - try multiple patterns
                if (
                    "sitemap" in url.lower()
                    or has_urlset
                    or has_sitemapindex
                    or has_loc_tag
                    or has_url_tag
                ):
                    # Try regex-based extraction for flexibility
                    logger.info(
                        f"SITEMAP DEBUG: Using fallback URL extraction for {url}"
                    )

                    # Extract URLs from simple sitemap
                    if has_urlset or has_url_tag or has_loc_tag or not has_sitemapindex:
                        # Match loc tags: <loc>URL</loc>
                        loc_pattern = r"<loc>\s*(.*?)\s*</loc>"
                        urls = re.findall(loc_pattern, content, re.IGNORECASE)

                        # If no URLs found with standard pattern, try alternative patterns
                        if not urls and "https://" in content:
                            logger.info(
                                "SITEMAP DEBUG: No URLs found with standard pattern, trying alternatives"
                            )

                            # Try to find any URLs in the content
                            alt_pattern = (
                                r'https?://[^\s<>"\']+\.[^\s<>"\']+(/[^\s<>"\']*)?'
                            )
                            urls = re.findall(alt_pattern, content)

                            logger.info(
                                f"SITEMAP DEBUG: Found {len(urls)} URLs with alternative pattern"
                            )

                        # Extract lastmod, changefreq, priority if available
                        for url_value in urls:
                            url_data = {"loc": url_value}

                            # Try to extract lastmod
                            lastmod_pattern = f"<loc>\\s*{re.escape(url_value)}\\s*</loc>.*?<lastmod>\\s*(.*?)\\s*</lastmod>"
                            lastmod_match = re.search(
                                lastmod_pattern, content, re.DOTALL | re.IGNORECASE
                            )
                            if lastmod_match:
                                url_data["lastmod"] = lastmod_match.group(1)
                                result["has_lastmod"] = True

                            # Try to extract priority
                            priority_pattern = f"<loc>\\s*{re.escape(url_value)}\\s*</loc>.*?<priority>\\s*(.*?)\\s*</priority>"
                            priority_match = re.search(
                                priority_pattern, content, re.DOTALL | re.IGNORECASE
                            )
                            if priority_match:
                                url_data["priority"] = priority_match.group(1)
                                result["has_priority"] = True

                            # Try to extract changefreq
                            changefreq_pattern = f"<loc>\\s*{re.escape(url_value)}\\s*</loc>.*?<changefreq>\\s*(.*?)\\s*</changefreq>"
                            changefreq_match = re.search(
                                changefreq_pattern, content, re.DOTALL | re.IGNORECASE
                            )
                            if changefreq_match:
                                url_data["changefreq"] = changefreq_match.group(1)
                                result["has_changefreq"] = True

                            result["urls"].append(url_data)
                            if len(result["urls"]) >= max_urls:
                                break

                        result["url_count"] = len(result["urls"])
                        result["sitemap_type"] = SitemapType.STANDARD
                        logger.info(
                            f"SITEMAP DEBUG: Extracted {result['url_count']} URLs using regex from {url}"
                        )
                        return result

                # Standard XML parsing (fallback only if regex extraction didn't work)
                try:
                    # Handle potential XML namespace issues
                    if "<?xml" in content and (
                        "xmlns" in content or "xmlns:" in content
                    ):
                        # Use ElementTree for proper namespace handling
                        root = ET.fromstring(content)

                        # Check if it's a sitemap index
                        if root.tag.endswith("sitemapindex"):
                            result["sitemap_type"] = SitemapType.INDEX

                            # Extract child sitemaps
                            for sitemap in root.findall(
                                ".//sm:sitemap", NAMESPACES
                            ) or root.findall(".//sitemap"):
                                loc_elem = sitemap.find(
                                    ".//sm:loc", NAMESPACES
                                ) or sitemap.find(".//loc")
                                if loc_elem is not None and loc_elem.text:
                                    child_url = loc_elem.text.strip()

                                    # Get lastmod if available
                                    lastmod_elem = sitemap.find(
                                        ".//sm:lastmod", NAMESPACES
                                    ) or sitemap.find(".//lastmod")
                                    lastmod = (
                                        lastmod_elem.text.strip()
                                        if lastmod_elem is not None
                                        and lastmod_elem.text
                                        else None
                                    )

                                    if lastmod:
                                        result["has_lastmod"] = True

                                    result["urls"].append(
                                        {
                                            "loc": child_url,
                                            "lastmod": lastmod,
                                            "type": "sitemap",
                                        }
                                    )

                                    if len(result["urls"]) >= max_urls:
                                        break

                        # Check if it's a standard sitemap
                        elif root.tag.endswith("urlset"):
                            if "image" in content:
                                result["sitemap_type"] = SitemapType.IMAGE
                            elif "news" in content:
                                result["sitemap_type"] = SitemapType.NEWS
                            elif "video" in content:
                                result["sitemap_type"] = SitemapType.VIDEO
                            else:
                                result["sitemap_type"] = SitemapType.STANDARD

                            # Extract URLs
                            for url_elem in root.findall(
                                ".//sm:url", NAMESPACES
                            ) or root.findall(".//url"):
                                loc_elem = url_elem.find(
                                    ".//sm:loc", NAMESPACES
                                ) or url_elem.find(".//loc")
                                if loc_elem is not None and loc_elem.text:
                                    page_url = loc_elem.text.strip()

                                    # Extract metadata
                                    url_data = {"loc": page_url}

                                    # Get lastmod
                                    lastmod_elem = url_elem.find(
                                        ".//sm:lastmod", NAMESPACES
                                    ) or url_elem.find(".//lastmod")
                                    if lastmod_elem is not None and lastmod_elem.text:
                                        url_data["lastmod"] = lastmod_elem.text.strip()
                                        result["has_lastmod"] = True

                                    # Get changefreq
                                    changefreq_elem = url_elem.find(
                                        ".//sm:changefreq", NAMESPACES
                                    ) or url_elem.find(".//changefreq")
                                    if (
                                        changefreq_elem is not None
                                        and changefreq_elem.text
                                    ):
                                        url_data["changefreq"] = (
                                            changefreq_elem.text.strip()
                                        )
                                        result["has_changefreq"] = True

                                    # Get priority
                                    priority_elem = url_elem.find(
                                        ".//sm:priority", NAMESPACES
                                    ) or url_elem.find(".//priority")
                                    if priority_elem is not None and priority_elem.text:
                                        url_data["priority"] = (
                                            priority_elem.text.strip()
                                        )
                                        result["has_priority"] = True

                                    # Get image data if present
                                    image_elements = url_elem.findall(
                                        ".//image:image", NAMESPACES
                                    ) or url_elem.findall(".//image")
                                    if image_elements:
                                        url_data["images"] = []  # type: ignore
                                        for img in image_elements:
                                            img_loc = img.find(
                                                ".//image:loc", NAMESPACES
                                            ) or img.find(".//loc")
                                            img_url = (
                                                img_loc.text.strip()
                                                if img_loc is not None and img_loc.text
                                                else None
                                            )
                                            if img_url:
                                                url_data["images"].append(
                                                    {"loc": img_url}
                                                )  # type: ignore

                                        url_data["image_count"] = len(
                                            url_data.get("images", [])
                                        )  # type: ignore

                                    # Get video data if present
                                    video_elements = url_elem.findall(
                                        ".//video:video", NAMESPACES
                                    ) or url_elem.findall(".//video")
                                    if video_elements:
                                        url_data["videos"] = []  # type: ignore
                                        for video in video_elements:
                                            video_loc = video.find(
                                                ".//video:content_loc", NAMESPACES
                                            ) or video.find(".//content_loc")
                                            video_url = (
                                                video_loc.text.strip()
                                                if video_loc is not None
                                                and video_loc.text
                                                else None
                                            )
                                            if video_url:
                                                url_data["videos"].append(
                                                    {"loc": video_url}
                                                )  # type: ignore

                                        url_data["video_count"] = len(
                                            url_data.get("videos", [])
                                        )  # type: ignore

                                    # Get news data if present
                                    news_elements = url_elem.findall(
                                        ".//news:news", NAMESPACES
                                    ) or url_elem.findall(".//news")
                                    if news_elements:
                                        url_data["news"] = True  # type: ignore

                                    # Add page type based on URL pattern
                                    url_parts = urlparse(page_url)
                                    path = url_parts.path.lower()

                                    if path.endswith(
                                        (".jpg", ".jpeg", ".png", ".gif", ".webp")
                                    ):
                                        url_data["page_type"] = "image"
                                    elif path.endswith(
                                        (".mp4", ".avi", ".mov", ".wmv")
                                    ):
                                        url_data["page_type"] = "video"
                                    elif path.endswith(".pdf"):
                                        url_data["page_type"] = "pdf"
                                    elif "/product/" in path or "/products/" in path:
                                        url_data["page_type"] = "product"
                                    elif "/category/" in path or "/categories/" in path:
                                        url_data["page_type"] = "category"
                                    elif "/tag/" in path or "/tags/" in path:
                                        url_data["page_type"] = "tag"
                                    elif (
                                        "/blog/" in path
                                        or "/blogs/" in path
                                        or "/post/" in path
                                        or "/posts/" in path
                                    ):
                                        url_data["page_type"] = "post"
                                    else:
                                        url_data["page_type"] = "page"

                                    result["urls"].append(url_data)

                                    if len(result["urls"]) >= max_urls:
                                        break
                        else:
                            result["error"] = f"Unknown sitemap format: {root.tag}"

                    else:
                        # Fallback to regex-based parsing for simpler sitemaps
                        if "<sitemapindex" in content:
                            result["sitemap_type"] = SitemapType.INDEX
                            sitemap_urls = re.findall(r"<loc>(.*?)</loc>", content)

                            for child_url in sitemap_urls:
                                result["urls"].append(
                                    {"loc": child_url, "type": "sitemap"}
                                )

                                if len(result["urls"]) >= max_urls:
                                    break

                        elif "<urlset" in content:
                            result["sitemap_type"] = SitemapType.STANDARD
                            page_urls = re.findall(r"<loc>(.*?)</loc>", content)

                            for page_url in page_urls:
                                url_data = {"loc": page_url, "page_type": "page"}

                                # Try to determine page type
                                url_parts = urlparse(page_url)
                                path = url_parts.path.lower()

                                if path.endswith(
                                    (".jpg", ".jpeg", ".png", ".gif", ".webp")
                                ):
                                    url_data["page_type"] = "image"
                                elif path.endswith((".mp4", ".avi", ".mov", ".wmv")):
                                    url_data["page_type"] = "video"
                                elif path.endswith(".pdf"):
                                    url_data["page_type"] = "pdf"
                                elif "/product/" in path or "/products/" in path:
                                    url_data["page_type"] = "product"
                                elif "/category/" in path or "/categories/" in path:
                                    url_data["page_type"] = "category"
                                elif "/tag/" in path or "/tags/" in path:
                                    url_data["page_type"] = "tag"
                                elif (
                                    "/blog/" in path
                                    or "/blogs/" in path
                                    or "/post/" in path
                                    or "/posts/" in path
                                ):
                                    url_data["page_type"] = "post"

                                result["urls"].append(url_data)

                                if len(result["urls"]) >= max_urls:
                                    break
                        else:
                            result["error"] = "Could not identify sitemap format"

                        # Check for features
                        result["has_lastmod"] = "<lastmod>" in content
                        result["has_priority"] = "<priority>" in content
                        result["has_changefreq"] = "<changefreq>" in content

                except Exception as parse_error:
                    result["error"] = f"XML parsing error: {str(parse_error)}"

                # Set URL count
                result["url_count"] = len(result["urls"])

                return result

        except Exception as e:
            result["error"] = f"Error fetching sitemap: {str(e)}"
            return result

    async def analyze_domain_sitemaps(
        self,
        domain: str,
        follow_robots_txt: bool = True,
        extract_urls: bool = True,
        max_urls_per_sitemap: int = 10000,
    ) -> Dict[str, Any]:
        """
        Analyze all sitemaps for a domain.

        Args:
            domain: Domain to analyze
            follow_robots_txt: Whether to check robots.txt
            extract_urls: Whether to extract URLs from sitemaps
            max_urls_per_sitemap: Maximum URLs to extract per sitemap

        Returns:
            Dictionary with analysis results
        """
        try:
            clean_domain = standardize_domain(domain)
            logger.info(f"SITEMAP DEBUG: Analyzing domain sitemaps for {clean_domain}")
        except ValueError as e:
            logger.error(f"SITEMAP DEBUG: Invalid domain: {domain}, error: {str(e)}")
            return {
                "domain": domain,
                "error": f"Invalid domain: {str(e)}",
                "sitemaps": [],
                "total_sitemaps": 0,
                "total_urls": 0,
            }

        # Discover sitemaps
        sitemaps = await self.discover_sitemaps(clean_domain, follow_robots_txt)
        logger.info(
            f"SITEMAP DEBUG: Discovered {len(sitemaps)} sitemaps for {clean_domain}"
        )

        # Critical debug logging for each sitemap
        for i, sitemap in enumerate(sitemaps):
            logger.info(
                f"SITEMAP DEBUG: Sitemap #{i+1}: URL={sitemap.get('url')}, method={sitemap.get('discovery_method')}"
            )

        result = {
            "domain": clean_domain,
            "sitemaps": sitemaps,
            "total_sitemaps": len(sitemaps),
            "total_urls": 0,
            "discovery_methods": {},
            "sitemap_types": {},
            "urls": [],
        }

        # Count discovery methods
        for sitemap in sitemaps:
            method = sitemap.get("discovery_method", "unknown")
            if method in result["discovery_methods"]:
                result["discovery_methods"][method] += 1
            else:
                result["discovery_methods"][method] = 1

        # Process each sitemap if URL extraction is enabled
        if extract_urls and sitemaps:
            # Reset processed URLs set
            self.processed_urls = set()

            # Process each sitemap
            for i, sitemap in enumerate(result["sitemaps"]):
                # Skip invalid sitemaps
                if sitemap.get("is_valid") is False:
                    continue

                # Parse sitemap
                parsed = await self.parse_sitemap(sitemap["url"], max_urls_per_sitemap)

                # Add parsing results to the sitemap data
                result["sitemaps"][i].update(
                    {
                        "sitemap_type": parsed.get("sitemap_type"),
                        "url_count": parsed.get("url_count", 0),
                        "has_lastmod": parsed.get("has_lastmod", False),
                        "has_priority": parsed.get("has_priority", False),
                        "has_changefreq": parsed.get("has_changefreq", False),
                        "error": parsed.get("error"),
                    }
                )

                # Count sitemap type
                sitemap_type = parsed.get("sitemap_type", "unknown")
                if sitemap_type:
                    if sitemap_type in result["sitemap_types"]:
                        result["sitemap_types"][sitemap_type] += 1
                    else:
                        result["sitemap_types"][sitemap_type] = 1

                # Add URLs to result
                result["urls"].extend(parsed.get("urls", []))
                result["total_urls"] += parsed.get("url_count", 0)

                # If it's a sitemap index, also process child sitemaps
                if parsed.get("sitemap_type") == SitemapType.INDEX:
                    child_urls = [
                        url["loc"]
                        for url in parsed.get("urls", [])
                        if url.get("type") == "sitemap"
                    ]

                    for child_url in child_urls:
                        # Skip if already processed
                        if child_url in self.processed_urls:
                            continue

                        # Parse child sitemap
                        child = await self.parse_sitemap(
                            child_url, max_urls_per_sitemap
                        )

                        # Add to sitemaps list
                        result["sitemaps"].append(
                            {
                                "url": child_url,
                                "discovery_method": DiscoveryMethod.SITEMAP_INDEX,
                                "sitemap_type": child.get("sitemap_type"),
                                "url_count": child.get("url_count", 0),
                                "has_lastmod": child.get("has_lastmod", False),
                                "has_priority": child.get("has_priority", False),
                                "has_changefreq": child.get("has_changefreq", False),
                                "error": child.get("error"),
                                "domain": clean_domain,
                            }
                        )

                        # Count sitemap type
                        child_type = child.get("sitemap_type", "unknown")
                        if child_type:
                            if child_type in result["sitemap_types"]:
                                result["sitemap_types"][child_type] += 1
                            else:
                                result["sitemap_types"][child_type] = 1

                        # Add URLs to result
                        result["urls"].extend(child.get("urls", []))
                        result["total_urls"] += child.get("url_count", 0)
                        result["total_sitemaps"] += 1

        # Close session
        await self.close_session()

        return result
