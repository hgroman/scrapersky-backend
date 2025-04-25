"""
Scrape Executor Service

This service centralizes all scraping operations across the platform.
It provides a standardized interface for executing different types of scrapes
with consistent error handling, validation, and result formatting.
"""

import asyncio
import json
import logging
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, cast
from urllib.parse import urljoin, urlparse, urlsplit

# External libraries for scraping
import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag

# Import ScraperAPI client
from ...utils.scraper_api import ScraperAPIClient
from ..core.auth_service import auth_service

# Import other services
from ..core.db_service import db_service
from ..job_service import job_service
from ..validation.validation_service import validation_service

# Removed custom error service import in favor of FastAPI's built-in error handling

logger = logging.getLogger(__name__)

class ScrapeExecutorService:
    """
    Service for executing various types of scraping operations.
    Centralizes scraping logic across different modules.
    """

    # Constants
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; ScraperSky/1.0; +https://scrapersky.com/bot)"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    # Cache for recently scraped data
    _metadata_cache = {}
    _cache_ttl = 3600  # 1 hour

    @classmethod
    async def execute_sitemap_analysis(
        cls,
        domain: str,
        tenant_id: str,
        user_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute sitemap analysis for a domain.

        Args:
            domain: Domain to analyze
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution
            options: Optional configuration (follow_robots_txt, max_urls, etc.)

        Returns:
            Analysis results with sitemaps and metadata
        """
        try:
            # Standardize domain and options
            domain = cls._standardize_domain(domain)
            options = options or {}

            # Default options
            follow_robots = options.get('follow_robots_txt', True)
            max_urls = options.get('max_urls', 1000)
            include_metadata = options.get('include_metadata', True)

            logger.info(f"Starting sitemap analysis for {domain} (tenant: {tenant_id})")

            # Step 1: Find potential sitemap locations
            sitemap_locations = await cls._find_sitemap_locations(domain, follow_robots)

            # Step 2: Fetch and parse sitemaps
            sitemaps = []
            total_urls = 0
            for location in sitemap_locations:
                sitemap_data = await cls._fetch_and_parse_sitemap(location, max_urls - total_urls)
                if sitemap_data:
                    sitemaps.append(sitemap_data)
                    total_urls += len(sitemap_data.get('urls', []))

                    # Stop if we've reached the maximum URLs
                    if total_urls >= max_urls:
                        break

            # Step 3: Extract metadata if requested
            metadata = {}
            if include_metadata:
                metadata = await cls.execute_metadata_extraction(
                    f"https://{domain}",
                    tenant_id,
                    user_id
                )

            # Prepare result
            result = {
                'domain': domain,
                'sitemaps': sitemaps,
                'total_sitemaps': len(sitemaps),
                'total_urls': total_urls,
                'metadata': metadata,
                'analyzed_at': datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Error analyzing sitemap for {domain}: {str(e)}")
            # Return partial results if available
            return {
                'domain': domain,
                'sitemaps': [],
                'total_sitemaps': 0,
                'total_urls': 0,
                'metadata': {},
                'error': str(e),
                'analyzed_at': datetime.utcnow().isoformat()
            }

    @classmethod
    async def execute_metadata_extraction(
        cls,
        url: str,
        tenant_id: str,
        user_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute metadata extraction for a URL.

        Args:
            url: URL to analyze
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution
            options: Optional configuration

        Returns:
            Extracted metadata (title, description, tech stack, etc.)
        """
        try:
            # Validate and normalize URL
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"

            # Check cache first
            cache_key = f"metadata:{url}"
            cached_data = cls._metadata_cache.get(cache_key)
            if cached_data and (datetime.utcnow() - cached_data.get('timestamp', datetime.min)).total_seconds() < cls._cache_ttl:
                logger.info(f"Using cached metadata for {url}")
                return cached_data.get('data', {})

            logger.info(f"Extracting metadata from {url} (tenant: {tenant_id})")

            # Fetch page content with retries
            html_content = await cls._fetch_with_retry(url)
            if not html_content:
                raise ValueError(f"Failed to fetch content from {url}")

            # Parse metadata
            metadata = cls._extract_metadata_from_html(html_content, url)

            # Additional metadata parsing based on options
            options = options or {}
            if options.get('extract_tech_stack', False):
                metadata['tech_stack'] = cls._extract_tech_stack(html_content)

            if options.get('extract_links', False):
                metadata['links'] = cls._extract_links(html_content, url)

            # Cache the result
            cls._metadata_cache[cache_key] = {
                'data': metadata,
                'timestamp': datetime.utcnow()
            }

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata from {url}: {str(e)}")
            # Return empty metadata with error
            return {
                'url': url,
                'title': '',
                'description': '',
                'keywords': [],
                'error': str(e)
            }

    @classmethod
    async def execute_places_search(
        cls,
        location: str,
        business_type: str,
        tenant_id: str,
        user_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute Google Places search.

        Args:
            location: Location to search
            business_type: Type of business
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution
            options: Optional configuration (radius_km, etc.)

        Returns:
            List of places with standardized format
        """
        try:
            # Process options
            options = options or {}
            radius_km = options.get('radius_km', 10)
            max_results = options.get('max_results', 20)

            # Verify we have an API key
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_MAPS_API_KEY environment variable not set")

            logger.info(f"Searching for {business_type} in {location} (tenant: {tenant_id})")

            # Convert km to meters for the API
            radius_meters = radius_km * 1000

            # Format the query for Google Places API Text Search
            query = f"{business_type} in {location}"

            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "radius": radius_meters,
                "key": api_key
            }

            all_results = []

            # Make the API request with pagination support
            async with aiohttp.ClientSession() as session:
                # First page
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"Google Places API request failed with status {response.status}")

                    data = await response.json()
                    if data.get("status") != "OK":
                        error_message = data.get("error_message", "Unknown error")
                        raise ValueError(f"Google Places API error: {error_message}")

                    all_results.extend(data.get("results", []))

                    # Handle pagination with next_page_token if it exists
                    next_page_token = data.get("next_page_token")

                    # Google requires a delay before using next_page_token
                    while next_page_token and len(all_results) < max_results:
                        await asyncio.sleep(2)  # Wait for token to be valid

                        next_params = {
                            "pagetoken": next_page_token,
                            "key": api_key
                        }

                        async with session.get(url, params=next_params) as next_response:
                            if next_response.status != 200:
                                break

                            next_data = await next_response.json()
                            if next_data.get("status") != "OK":
                                break

                            all_results.extend(next_data.get("results", []))
                            next_page_token = next_data.get("next_page_token")

                            # Stop if we've reached the maximum results
                            if len(all_results) >= max_results:
                                break

                            # If we have next_page_token, wait again before using it
                            if next_page_token:
                                await asyncio.sleep(2)

            # Limit results if needed
            if len(all_results) > max_results:
                all_results = all_results[:max_results]

            # Standardize result format
            standardized_results = [cls._standardize_place_result(place) for place in all_results]

            return standardized_results

        except Exception as e:
            logger.error(f"Error searching Google Places for {business_type} in {location}: {str(e)}")
            return []

    @classmethod
    async def execute_contact_extraction(
        cls,
        url: str,
        tenant_id: str,
        user_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract contact information from a URL.

        Args:
            url: URL to analyze
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution
            options: Optional configuration

        Returns:
            Extracted contact information
        """
        try:
            # Validate and normalize URL
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"

            logger.info(f"Extracting contacts from {url} (tenant: {tenant_id})")

            # Fetch page content
            html_content = await cls._fetch_with_retry(url)
            if not html_content:
                raise ValueError(f"Failed to fetch content from {url}")

            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract emails
            emails = cls._extract_emails(html_content)

            # Extract phone numbers
            phones = cls._extract_phone_numbers(html_content)

            # Extract social media links
            social_media = cls._extract_social_media(soup, url)

            # Extract contact page URL
            contact_page = cls._find_contact_page(soup, url)

            # Extract additional contact info if contact page found
            additional_contacts = {}
            if contact_page and contact_page != url:
                try:
                    contact_html = await cls._fetch_with_retry(contact_page)
                    if contact_html:
                        additional_emails = cls._extract_emails(contact_html)
                        additional_phones = cls._extract_phone_numbers(contact_html)

                        # Merge with existing results
                        emails = list(set(emails + additional_emails))
                        phones = list(set(phones + additional_phones))

                        additional_contacts = {
                            'contact_page_url': contact_page,
                            'contact_page_emails': additional_emails,
                            'contact_page_phones': additional_phones
                        }
                except Exception as contact_error:
                    logger.warning(f"Error fetching contact page {contact_page}: {str(contact_error)}")

            # Prepare result
            result = {
                'url': url,
                'emails': emails,
                'phones': phones,
                'social_media': social_media,
                'contact_page': contact_page,
                'additional_contacts': additional_contacts,
                'extracted_at': datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Error extracting contacts from {url}: {str(e)}")
            # Return empty result with error
            return {
                'url': url,
                'emails': [],
                'phones': [],
                'social_media': {},
                'error': str(e),
                'extracted_at': datetime.utcnow().isoformat()
            }

    # Helper methods
    @classmethod
    def _standardize_domain(cls, domain: str) -> str:
        """
        Standardize a domain name.

        Args:
            domain: Domain name to standardize

        Returns:
            Standardized domain name
        """
        # Remove protocol
        if domain.startswith(('http://', 'https://')):
            domain = urlparse(domain).netloc

        # Remove www
        if domain.startswith('www.'):
            domain = domain[4:]

        # Remove trailing slash
        if domain.endswith('/'):
            domain = domain[:-1]

        # Remove path
        domain = domain.split('/')[0]

        return domain.lower()

    @classmethod
    async def _fetch_with_retry(cls, url: str, max_retries: Optional[int] = None) -> Optional[str]:
        """
        Fetch a URL with retry logic.

        Args:
            url: URL to fetch
            max_retries: Maximum number of retries (defaults to cls.MAX_RETRIES)

        Returns:
            HTML content or None if failed
        """
        if max_retries is None:
            max_retries = cls.MAX_RETRIES

        # Try using ScraperAPI first
        try:
            async with ScraperAPIClient() as scraper_client:
                return await scraper_client.fetch(url, retries=max_retries)
        except Exception as e:
            logger.warning(f"ScraperAPI fetch failed for {url}: {str(e)}. Falling back to direct fetch.")

            # Fall back to direct fetch if ScraperAPI fails
            headers = {
                'User-Agent': cls.DEFAULT_USER_AGENT
            }

            for attempt in range(max_retries + 1):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            url,
                            headers=headers,
                            timeout=cls.DEFAULT_TIMEOUT,
                            ssl=False  # Disable SSL verification as a fallback
                        ) as response:
                            if response.status == 200:
                                return await response.text()
                            elif response.status == 404:
                                logger.warning(f"URL not found: {url}")
                                return None
                            else:
                                logger.warning(f"HTTP error {response.status} for {url}")

                except asyncio.TimeoutError:
                    logger.warning(f"Timeout fetching {url} (attempt {attempt+1}/{max_retries+1})")
                except Exception as e:
                    logger.warning(f"Error fetching {url}: {str(e)} (attempt {attempt+1}/{max_retries+1})")

                # Sleep before retry if this wasn't the last attempt
                if attempt < max_retries:
                    await asyncio.sleep(cls.RETRY_DELAY * (attempt + 1))  # Exponential backoff

            return None

    @classmethod
    async def _find_sitemap_locations(cls, domain: str, follow_robots: bool = True) -> List[str]:
        """
        Find potential sitemap locations for a domain.

        Args:
            domain: Domain to search
            follow_robots: Whether to check robots.txt for sitemap locations

        Returns:
            List of potential sitemap URLs
        """
        locations = []

        # Common sitemap locations
        common_paths = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/sitemap.php",
            f"https://{domain}/sitemap.txt"
        ]

        # Add locations from robots.txt if requested
        if follow_robots:
            robots_url = f"https://{domain}/robots.txt"
            robots_content = await cls._fetch_with_retry(robots_url)

            if robots_content:
                # Extract sitemap directives
                sitemap_matches = re.findall(r'(?i)Sitemap:\s*(.+)', robots_content)
                for match in sitemap_matches:
                    sitemap_url = match.strip()
                    if sitemap_url:
                        locations.append(sitemap_url)

        # Add common locations if not already found
        for path in common_paths:
            if path not in locations:
                locations.append(path)

        return locations

    @classmethod
    async def _fetch_and_parse_sitemap(cls, sitemap_url: str, max_urls: int = 1000) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse a sitemap.

        Args:
            sitemap_url: Sitemap URL to fetch
            max_urls: Maximum number of URLs to extract

        Returns:
            Parsed sitemap data or None if failed
        """
        try:
            # Fetch sitemap content
            content = await cls._fetch_with_retry(sitemap_url)
            if not content:
                return None

            # Check if it's an XML sitemap
            is_xml = '<urlset' in content or '<sitemapindex' in content

            # Parse according to type
            urls = []
            is_index = False
            sub_sitemaps = []

            if is_xml:
                # Parse XML sitemap
                soup = BeautifulSoup(content, 'xml')

                # Check if it's a sitemap index
                sitemapindex = soup.find('sitemapindex')
                if sitemapindex:
                    is_index = True
                    sitemap_tags = cast(Tag, sitemapindex).find_all('sitemap')

                    for sitemap_tag in sitemap_tags:
                        loc_tag = cast(Tag, sitemap_tag).find('loc')
                        if loc_tag and cast(Tag, loc_tag).text:
                            sub_sitemaps.append(cast(Tag, loc_tag).text.strip())
                else:
                    # Regular sitemap
                    urlset = soup.find('urlset')
                    if urlset:
                        url_tags = cast(Tag, urlset).find_all('url')

                        for url_tag in url_tags[:max_urls]:
                            loc_tag = cast(Tag, url_tag).find('loc')
                            if not loc_tag or not cast(Tag, loc_tag).text:
                                continue

                            url_data = {
                                'url': cast(Tag, loc_tag).text.strip()
                            }

                            # Extract other fields if available
                            lastmod_tag = cast(Tag, url_tag).find('lastmod')
                            if lastmod_tag and cast(Tag, lastmod_tag).text:
                                url_data['lastmod'] = cast(Tag, lastmod_tag).text.strip()

                            changefreq_tag = cast(Tag, url_tag).find('changefreq')
                            if changefreq_tag and cast(Tag, changefreq_tag).text:
                                url_data['changefreq'] = cast(Tag, changefreq_tag).text.strip()

                            priority_tag = cast(Tag, url_tag).find('priority')
                            if priority_tag and cast(Tag, priority_tag).text:
                                try:
                                    url_data['priority'] = float(cast(Tag, priority_tag).text.strip())
                                except (ValueError, TypeError):
                                    pass

                            urls.append(url_data)
            else:
                # Try simple text format (one URL per line)
                lines = content.strip().split('\n')
                for line in lines[:max_urls]:
                    line = line.strip()
                    if line and line.startswith('http'):
                        urls.append({'url': line})

            # If it's a sitemap index, fetch up to 3 sub-sitemaps
            if is_index and sub_sitemaps:
                for i, sub_url in enumerate(sub_sitemaps[:3]):  # Limit to first 3
                    sub_sitemap = await cls._fetch_and_parse_sitemap(sub_url, max_urls - len(urls))
                    if sub_sitemap and sub_sitemap.get('urls'):
                        urls.extend(sub_sitemap['urls'])

                        # Stop if we've reached the maximum
                        if len(urls) >= max_urls:
                            break

            # Prepare result
            result = {
                'sitemap_url': sitemap_url,
                'is_index': is_index,
                'sub_sitemaps': sub_sitemaps if is_index else [],
                'urls': urls[:max_urls],  # Ensure we don't exceed max_urls
                'total_urls': len(urls[:max_urls]),
                'fetched_at': datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {str(e)}")
            return None

    @classmethod
    def _extract_metadata_from_html(cls, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extract metadata from HTML content.

        Args:
            html_content: HTML content to parse
            url: URL of the page

        Returns:
            Extracted metadata
        """
        try:
            # Default values
            metadata = {
                'url': url,
                'title': '',
                'description': '',
                'keywords': [],
                'og_title': '',
                'og_description': '',
                'og_image': '',
                'twitter_card': '',
                'twitter_title': '',
                'twitter_description': '',
                'twitter_image': '',
                'content_length': len(html_content),
                'language': '',
                'extracted_at': datetime.utcnow().isoformat()
            }

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract meta tags
            for meta in soup.find_all('meta'):
                meta_tag = cast(Tag, meta)
                name = str(meta_tag.get('name', '')).lower()
                property = str(meta_tag.get('property', '')).lower()
                content = str(meta_tag.get('content', ''))

                if not content:
                    continue

                # Standard meta tags
                if name == 'description':
                    metadata['description'] = content
                elif name == 'keywords':
                    metadata['keywords'] = [k.strip() for k in content.split(',') if k.strip()]
                elif name == 'language':
                    metadata['language'] = content

                # OpenGraph meta tags
                elif property == 'og:title':
                    metadata['og_title'] = content
                elif property == 'og:description':
                    metadata['og_description'] = content
                elif property == 'og:image':
                    metadata['og_image'] = content

                # Twitter meta tags
                elif name == 'twitter:card':
                    metadata['twitter_card'] = content
                elif name == 'twitter:title':
                    metadata['twitter_title'] = content
                elif name == 'twitter:description':
                    metadata['twitter_description'] = content
                elif name == 'twitter:image':
                    metadata['twitter_image'] = content

            # Extract headings (h1, h2)
            h1_tags = soup.find_all('h1')
            if h1_tags:
                metadata['h1'] = [cast(Tag, h).get_text().strip() for h in h1_tags]

            h2_tags = soup.find_all('h2')
            if h2_tags:
                metadata['h2'] = [cast(Tag, h).get_text().strip() for h in h2_tags]

            # Extract canonical URL
            canonical = soup.find('link', rel='canonical')
            if canonical and cast(Tag, canonical).get('href'):
                metadata['canonical_url'] = cast(Tag, canonical)['href']

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata from HTML: {str(e)}")
            return {
                'url': url,
                'title': '',
                'description': '',
                'keywords': [],
                'error': str(e)
            }

    @classmethod
    def _extract_tech_stack(cls, html_content: str) -> List[Dict[str, str]]:
        """
        Extract technology stack indicators from HTML.

        Args:
            html_content: HTML content to analyze

        Returns:
            List of detected technologies
        """
        technologies = []

        # Simple tech detection patterns - this could be expanded
        tech_patterns = [
            {'name': 'WordPress', 'pattern': r'wp-content|wp-include'},
            {'name': 'Shopify', 'pattern': r'cdn\.shopify\.com|shopify\.com'},
            {'name': 'Wix', 'pattern': r'wix\.com|wixsite\.com'},
            {'name': 'jQuery', 'pattern': r'jquery'},
            {'name': 'React', 'pattern': r'react|reactjs'},
            {'name': 'Angular', 'pattern': r'ng-|angular'},
            {'name': 'Vue.js', 'pattern': r'vue\.js|vue@'},
            {'name': 'Bootstrap', 'pattern': r'bootstrap'},
            {'name': 'Gatsby', 'pattern': r'gatsby'},
            {'name': 'Google Analytics', 'pattern': r'google-analytics\.com|gtag'},
            {'name': 'Google Tag Manager', 'pattern': r'googletagmanager'},
            {'name': 'Facebook Pixel', 'pattern': r'connect\.facebook\.net|fbq\('},
            {'name': 'Cloudflare', 'pattern': r'cloudflare'},
            {'name': 'Font Awesome', 'pattern': r'fontawesome'},
            {'name': 'HubSpot', 'pattern': r'hubspot'}
        ]

        for tech in tech_patterns:
            if re.search(tech['pattern'], html_content, re.IGNORECASE):
                technologies.append({
                    'name': tech['name'],
                    'confidence': 'medium'  # A simple indicator
                })

        return technologies

    @classmethod
    def _extract_links(cls, html_content: str, base_url: str) -> Dict[str, List[str]]:
        """
        Extract links from HTML content.

        Args:
            html_content: HTML content to parse
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary of internal and external links
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract domain from base_url
            base_domain = urlparse(base_url).netloc
            if base_domain.startswith('www.'):
                base_domain = base_domain[4:]

            internal_links = set()
            external_links = set()

            # Process all links
            for a_tag in soup.find_all('a', href=True):
                a_tag_as_tag = cast(Tag, a_tag)
                href = str(a_tag_as_tag['href']).strip()

                # Skip empty, javascript and anchor links
                if not href or href.startswith(('javascript:', '#', 'mailto:', 'tel:')):
                    continue

                # Resolve relative URLs
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)

                # Parse the URL
                parsed_url = urlparse(href)
                domain = parsed_url.netloc

                if not domain:
                    continue

                if domain.startswith('www.'):
                    domain = domain[4:]

                # Classify as internal or external
                if domain == base_domain:
                    internal_links.add(href)
                else:
                    external_links.add(href)

            return {
                'internal': list(internal_links)[:100],  # Limit to 100 links
                'external': list(external_links)[:100]   # Limit to 100 links
            }

        except Exception as e:
            logger.error(f"Error extracting links: {str(e)}")
            return {
                'internal': [],
                'external': []
            }

    @classmethod
    def _standardize_place_result(cls, place: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize a Google Places API result.

        Args:
            place: Place result from Google Places API

        Returns:
            Standardized place data
        """
        return {
            'place_id': place.get('place_id', ''),
            'name': place.get('name', ''),
            'formatted_address': place.get('formatted_address', ''),
            'latitude': place.get('geometry', {}).get('location', {}).get('lat'),
            'longitude': place.get('geometry', {}).get('location', {}).get('lng'),
            'vicinity': place.get('vicinity', ''),
            'rating': place.get('rating'),
            'user_ratings_total': place.get('user_ratings_total'),
            'price_level': place.get('price_level'),
            'types': place.get('types', []),
            'raw_data': json.dumps(place)  # Store the raw JSON for future reference
        }

    @classmethod
    def _extract_emails(cls, content: str) -> List[str]:
        """
        Extract email addresses from content.

        Args:
            content: Content to search for emails

        Returns:
            List of unique email addresses
        """
        # Pattern for email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = set(re.findall(email_pattern, content))

        # Filter out invalid/unlikely emails
        filtered_emails = []
        for email in emails:
            # Skip emails with invalid characters
            if re.search(r'[^\w.@+-]', email):
                continue

            # Skip very short domain parts
            domain_part = email.split('@')[-1]
            if len(domain_part) < 4:  # a.bc is minimum valid domain
                continue

            # Skip emails with obvious placeholders
            if any(x in email.lower() for x in ['example', 'youremail', 'sample', 'test@']):
                continue

            filtered_emails.append(email.lower())

        return filtered_emails

    @classmethod
    def _extract_phone_numbers(cls, content: str) -> List[str]:
        """
        Extract phone numbers from content.

        Args:
            content: Content to search for phone numbers

        Returns:
            List of standardized phone numbers
        """
        # Various phone number patterns
        patterns = [
            r'\+\d{1,3}\s?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International format
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format (123) 456-7890
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # Simple 10-digit
        ]

        phone_numbers = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            phone_numbers.update(matches)

        # Standardize and filter
        standardized = []
        for phone in phone_numbers:
            # Remove all non-digit characters for comparison
            digits_only = re.sub(r'\D', '', phone)

            # Skip very short numbers
            if len(digits_only) < 7:
                continue

            # Skip very long numbers
            if len(digits_only) > 15:
                continue

            standardized.append(phone)

        return standardized

    @classmethod
    def _extract_social_media(cls, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """
        Extract social media links from a webpage.

        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary of social media profiles
        """
        social_networks = {
            'facebook': r'facebook\.com',
            'twitter': r'twitter\.com|x\.com',
            'instagram': r'instagram\.com',
            'linkedin': r'linkedin\.com',
            'youtube': r'youtube\.com',
            'pinterest': r'pinterest\.com',
            'tiktok': r'tiktok\.com'
        }

        social_media = {}

        # Find all links
        for a_tag in soup.find_all('a', href=True):
            a_tag_as_tag = cast(Tag, a_tag)
            href = str(a_tag_as_tag['href']).strip()

            # Skip empty links
            if not href:
                continue

            # Resolve relative URLs
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)

            # Check against social networks
            for network, pattern in social_networks.items():
                if re.search(pattern, href, re.IGNORECASE):
                    social_media[network] = href
                    break

        return social_media

    @classmethod
    def _find_contact_page(cls, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """
        Find a contact page link.

        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for resolving relative links

        Returns:
            URL of the contact page or None if not found
        """
        contact_keywords = ['contact', 'kontakt', 'contacto', 'contactenos', 'get in touch', 'reach us']

        # Check link text and href
        for a_tag in soup.find_all('a', href=True):
            a_tag_as_tag = cast(Tag, a_tag)
            href = str(a_tag_as_tag['href']).strip()
            text = a_tag_as_tag.get_text().lower().strip()

            # Skip empty links and anchors
            if not href or href.startswith(('#', 'javascript:')):
                continue

            # Check if it's a contact page
            if any(keyword in text for keyword in contact_keywords) or any(keyword in href.lower() for keyword in contact_keywords):
                # Resolve URL
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)

                return href

        return None

# Create singleton instance
scrape_executor_service = ScrapeExecutorService()
