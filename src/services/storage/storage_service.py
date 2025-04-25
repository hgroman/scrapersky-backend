"""
Storage Service

This service handles all data storage operations across the platform,
providing a standardized interface for storing and retrieving different
types of data with consistent tenant isolation and error handling.
"""

import asyncio
import json
import logging
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from ..core.auth_service import auth_service

# Import other services
from ..core.db_service import db_service

logger = logging.getLogger(__name__)

class StorageService:
    """
    Service for standardized data storage operations.
    """

    # Constants
    DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000000"

    # Cache for domain IDs to reduce database queries
    _domain_id_cache: Dict[str, Dict[str, str]] = {}

    @classmethod
    async def store_domain_metadata(
        cls,
        domain: str,
        metadata: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Store domain metadata.

        Args:
            domain: Domain
            metadata: Metadata to store
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution

        Returns:
            Stored record
        """
        try:
            # Standardize domain
            domain = cls._standardize_domain(domain)

            # Ensure tenant_id is valid
            tenant_id = cls._validate_tenant_id(tenant_id)

            # Initialize query
            query = """
                INSERT INTO domains (
                    domain, tenant_id, metadata, created_by, created_at, updated_at
                ) VALUES (
                    %(domain)s, %(tenant_id)s, %(metadata)s::jsonb, %(user_id)s, NOW(), NOW()
                ) ON CONFLICT (domain, tenant_id) DO UPDATE SET
                    metadata = %(metadata)s::jsonb,
                    updated_by = %(user_id)s,
                    updated_at = NOW()
                RETURNING *
            """

            # Prepare parameters
            params = {
                'domain': domain,
                'tenant_id': tenant_id,
                'metadata': json.dumps(metadata),
                'user_id': user_id
            }

            # Execute query
            result = await db_service.execute_returning(query, params)

            # Update domain ID cache
            if result:
                domain_id = result.get('id')
                if domain_id:
                    if tenant_id not in cls._domain_id_cache:
                        cls._domain_id_cache[tenant_id] = {}
                    cls._domain_id_cache[tenant_id][domain] = str(domain_id)

            logger.info(f"Stored metadata for domain {domain} (tenant: {tenant_id})")

            return result or {}

        except Exception as e:
            logger.error(f"Error storing domain metadata for {domain}: {str(e)}")
            logger.error(traceback.format_exc())

            # Return partial result with error
            return {
                'domain': domain,
                'tenant_id': tenant_id,
                'error': str(e),
                'success': False
            }

    @classmethod
    async def store_sitemap_data(
        cls,
        domain: str,
        sitemap_url: str,
        sitemap_data: Dict[str, Any],
        urls: Optional[List[Dict[str, Any]]] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store sitemap data.

        Args:
            domain: Domain
            sitemap_url: Sitemap URL
            sitemap_data: Sitemap metadata
            urls: Optional list of URLs from the sitemap
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution

        Returns:
            Stored record
        """
        try:
            # Standardize domain
            domain = cls._standardize_domain(domain)

            # Ensure tenant_id is valid
            tenant_id = cls._validate_tenant_id(tenant_id)

            # If user_id not provided, use system user
            if not user_id:
                user_id = "system"

            # First, get or create domain record
            domain_id = await cls._get_or_create_domain_id(domain, tenant_id, user_id)

            if not domain_id:
                raise ValueError(f"Failed to create domain record for {domain}")

            # Next, insert or update sitemap record
            sitemap_query = """
                INSERT INTO sitemaps (
                    domain_id, tenant_id, url, last_scan, total_urls, is_index, metadata
                ) VALUES (
                    %(domain_id)s, %(tenant_id)s, %(url)s, NOW(), %(total_urls)s, %(is_index)s, %(metadata)s::jsonb
                ) ON CONFLICT (domain_id, url) DO UPDATE SET
                    last_scan = NOW(),
                    total_urls = %(total_urls)s,
                    is_index = %(is_index)s,
                    metadata = %(metadata)s::jsonb
                RETURNING id
            """

            sitemap_params = {
                'domain_id': domain_id,
                'tenant_id': tenant_id,
                'url': sitemap_url,
                'total_urls': sitemap_data.get('total_urls', 0),
                'is_index': sitemap_data.get('is_index', False),
                'metadata': json.dumps(sitemap_data)
            }

            sitemap_result = await db_service.execute_returning(sitemap_query, sitemap_params)

            # If we have sitemap URLs, store them (in batches)
            stored_urls = 0
            if urls and sitemap_result and sitemap_result.get('id'):
                sitemap_id = sitemap_result.get('id')

                # Make sure sitemap_id is a string
                if sitemap_id is not None:
                    # Process in batches of 100
                    batch_size = 100
                    for i in range(0, len(urls), batch_size):
                        batch = urls[i:i+batch_size]
                        await cls._batch_insert_sitemap_urls(str(sitemap_id), tenant_id, batch)
                        stored_urls += len(batch)

            # Prepare response
            sitemap_response = {
                'domain': domain,
                'domain_id': domain_id,
                'sitemap_url': sitemap_url,
                'sitemap_id': sitemap_result.get('id') if sitemap_result else None,
                'total_urls': sitemap_data.get('total_urls', 0),
                'stored_urls': stored_urls,
                'success': True
            }

            logger.info(f"Stored sitemap {sitemap_url} with {stored_urls} URLs for domain {domain} (tenant: {tenant_id})")

            return sitemap_response

        except Exception as e:
            logger.error(f"Error storing sitemap data for {domain}, {sitemap_url}: {str(e)}")
            logger.error(traceback.format_exc())

            # Return partial result with error
            return {
                'domain': domain,
                'sitemap_url': sitemap_url,
                'tenant_id': tenant_id,
                'error': str(e),
                'success': False
            }

    @classmethod
    async def store_places_data(
        cls,
        places: List[Dict[str, Any]],
        search_params: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Store Google Places data.

        Args:
            places: List of places to store
            search_params: Search parameters
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution

        Returns:
            Storage results
        """
        try:
            # Ensure tenant_id is valid
            tenant_id = cls._validate_tenant_id(tenant_id)

            # If no places, return early
            if not places:
                return {
                    'success': True,
                    'tenant_id': tenant_id,
                    'message': 'No places to store',
                    'stored_count': 0
                }

            # Get key search parameters
            location = search_params.get('location', 'unknown')
            business_type = search_params.get('business_type', 'unknown')

            # Create a search record first
            search_query = """
                INSERT INTO place_searches (
                    tenant_id, user_id, location, business_type, params, created_at
                ) VALUES (
                    %(tenant_id)s, %(user_id)s, %(location)s, %(business_type)s, %(params)s::jsonb, NOW()
                ) RETURNING id
            """

            search_params = {
                'tenant_id': tenant_id,
                'user_id': user_id,
                'location': location,
                'business_type': business_type,
                'params': json.dumps(search_params)
            }

            search_result = await db_service.execute_returning(search_query, search_params)
            search_id = search_result.get('id') if search_result else None

            if not search_id:
                raise ValueError("Failed to create search record")

            # Store places in batches
            stored_count = 0
            failed_places = []

            # Process in batches of 50
            batch_size = 50
            for i in range(0, len(places), batch_size):
                batch = places[i:i+batch_size]
                stored, failed = await cls._batch_insert_places(batch, search_id, tenant_id, user_id)
                stored_count += stored
                failed_places.extend(failed)

            # Return result
            result = {
                'success': len(failed_places) == 0,
                'tenant_id': tenant_id,
                'search_id': search_id,
                'total_places': len(places),
                'stored_count': stored_count,
                'failed_count': len(failed_places),
                'message': f"Stored {stored_count} of {len(places)} places"
            }

            if failed_places:
                result['failed_places'] = failed_places[:10]  # Include first 10 failures

            logger.info(f"Stored {stored_count} places for search {search_id} (tenant: {tenant_id})")

            return result

        except Exception as e:
            logger.error(f"Error storing places data: {str(e)}")
            logger.error(traceback.format_exc())

            # Return error result
            return {
                'success': False,
                'tenant_id': tenant_id,
                'error': str(e),
                'total_places': len(places),
                'stored_count': 0
            }

    @classmethod
    async def store_contact_data(
        cls,
        domain: str,
        contacts: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Store contact information for a domain.

        Args:
            domain: Domain
            contacts: Contact information
            tenant_id: Tenant ID for isolation
            user_id: User ID for attribution

        Returns:
            Storage results
        """
        try:
            # Standardize domain
            domain = cls._standardize_domain(domain)

            # Ensure tenant_id is valid
            tenant_id = cls._validate_tenant_id(tenant_id)

            # Get or create domain record
            domain_id = await cls._get_or_create_domain_id(domain, tenant_id, user_id)

            if not domain_id:
                raise ValueError(f"Failed to create domain record for {domain}")

            # Extract contact components
            emails = contacts.get('emails', [])
            phones = contacts.get('phones', [])
            social_media = contacts.get('social_media', {})
            source_url = contacts.get('url', f"https://{domain}")

            # Store emails
            stored_emails = await cls._store_domain_emails(domain_id, emails, source_url, tenant_id, user_id)

            # Store phones
            stored_phones = await cls._store_domain_phones(domain_id, phones, source_url, tenant_id, user_id)

            # Store social media
            stored_social = await cls._store_domain_social_media(domain_id, social_media, tenant_id, user_id)

            # Update domain record with contact scan time
            update_query = """
                UPDATE domains
                SET
                    contact_scanned_at = NOW(),
                    updated_at = NOW(),
                    updated_by = %(user_id)s
                WHERE id = %(domain_id)s
            """

            await db_service.execute(update_query, {
                'domain_id': domain_id,
                'user_id': user_id
            })

            # Prepare response
            result = {
                'success': True,
                'domain': domain,
                'domain_id': domain_id,
                'tenant_id': tenant_id,
                'stored_emails': stored_emails,
                'stored_phones': stored_phones,
                'stored_social': stored_social,
                'message': f"Stored {stored_emails} emails, {stored_phones} phones, and {stored_social} social media links"
            }

            logger.info(f"Stored contact data for domain {domain} (tenant: {tenant_id})")

            return result

        except Exception as e:
            logger.error(f"Error storing contact data for {domain}: {str(e)}")
            logger.error(traceback.format_exc())

            # Return error result
            return {
                'success': False,
                'domain': domain,
                'tenant_id': tenant_id,
                'error': str(e)
            }

    @classmethod
    async def get_domain_data(
        cls,
        domain: str,
        tenant_id: str,
        include_sitemaps: bool = False,
        include_contacts: bool = False
    ) -> Dict[str, Any]:
        """
        Get all data for a domain.

        Args:
            domain: Domain
            tenant_id: Tenant ID for isolation
            include_sitemaps: Whether to include sitemap data
            include_contacts: Whether to include contact data

        Returns:
            Domain data
        """
        try:
            # Standardize domain
            domain = cls._standardize_domain(domain)

            # Ensure tenant_id is valid
            tenant_id = cls._validate_tenant_id(tenant_id)

            # Query domain record
            query = """
                SELECT * FROM domains
                WHERE domain = %(domain)s AND tenant_id = %(tenant_id)s
            """

            params = {
                'domain': domain,
                'tenant_id': tenant_id
            }

            domain_data = await db_service.fetch_one(query, params)

            if not domain_data:
                return {
                    'success': False,
                    'domain': domain,
                    'tenant_id': tenant_id,
                    'message': 'Domain not found'
                }

            # Convert metadata to object if it's JSON string
            metadata = domain_data.get('metadata')
            if metadata and isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                    domain_data['metadata'] = metadata
                except (json.JSONDecodeError, TypeError):
                    pass

            # Format result
            result = {
                'success': True,
                'domain': domain,
                'tenant_id': tenant_id,
                'domain_data': domain_data
            }

            # Include sitemaps if requested
            if include_sitemaps:
                domain_id = domain_data.get('id')
                if domain_id:
                    sitemaps = await cls._get_domain_sitemaps(domain_id, tenant_id)
                    result['sitemaps'] = sitemaps

            # Include contacts if requested
            if include_contacts:
                domain_id = domain_data.get('id')
                if domain_id:
                    contacts = await cls._get_domain_contacts(domain_id, tenant_id)
                    result['contacts'] = contacts

            return result

        except Exception as e:
            logger.error(f"Error getting domain data for {domain}: {str(e)}")
            logger.error(traceback.format_exc())

            # Return error result
            return {
                'success': False,
                'domain': domain,
                'tenant_id': tenant_id,
                'error': str(e)
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
        if not domain:
            return ""

        # Remove protocol
        if domain.startswith(('http://', 'https://')):
            domain = urlparse(domain).netloc

        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        # Remove trailing slash
        if domain.endswith('/'):
            domain = domain[:-1]

        # Remove path and query parameters
        domain = domain.split('/')[0]
        domain = domain.split('?')[0]
        domain = domain.split('#')[0]

        return domain.lower()

    @classmethod
    def _validate_tenant_id(cls, tenant_id: Optional[str]) -> str:
        """
        Always returns the default tenant ID.

        Args:
            tenant_id: Ignored

        Returns:
            Default tenant ID
        """
        return cls.DEFAULT_TENANT_ID

    @classmethod
    async def _get_or_create_domain_id(
        cls,
        domain: str,
        tenant_id: str,
        user_id: str
    ) -> Optional[str]:
        """
        Get or create a domain record and return its ID.

        Args:
            domain: Domain
            tenant_id: Tenant ID
            user_id: User ID

        Returns:
            Domain ID or None if failed
        """
        # Check cache first
        if tenant_id in cls._domain_id_cache and domain in cls._domain_id_cache[tenant_id]:
            return cls._domain_id_cache[tenant_id][domain]

        # Query domain record
        query = """
            SELECT id FROM domains
            WHERE domain = %(domain)s AND tenant_id = %(tenant_id)s
        """

        params = {
            'domain': domain,
            'tenant_id': tenant_id
        }

        domain_data = await db_service.fetch_one(query, params)

        if domain_data and domain_data.get('id'):
            domain_id = domain_data.get('id')

            # Update cache
            if tenant_id not in cls._domain_id_cache:
                cls._domain_id_cache[tenant_id] = {}
            cls._domain_id_cache[tenant_id][domain] = str(domain_id)

            return domain_id

        # Domain not found, create it
        create_query = """
            INSERT INTO domains (
                domain, tenant_id, created_by, created_at, updated_at
            ) VALUES (
                %(domain)s, %(tenant_id)s, %(user_id)s, NOW(), NOW()
            ) RETURNING id
        """

        create_params = {
            'domain': domain,
            'tenant_id': tenant_id,
            'user_id': user_id
        }

        try:
            result = await db_service.execute_returning(create_query, create_params)

            if result and result.get('id'):
                domain_id = result.get('id')

                # Update cache
                if tenant_id not in cls._domain_id_cache:
                    cls._domain_id_cache[tenant_id] = {}
                cls._domain_id_cache[tenant_id][domain] = str(domain_id)

                return domain_id

            return None

        except Exception as e:
            logger.error(f"Error creating domain record for {domain}: {str(e)}")
            return None

    @classmethod
    async def _batch_insert_sitemap_urls(
        cls,
        sitemap_id: str,
        tenant_id: str,
        urls: List[Dict[str, Any]]
    ) -> int:
        """
        Insert a batch of sitemap URLs.

        Args:
            sitemap_id: Sitemap ID
            tenant_id: Tenant ID
            urls: List of URL records

        Returns:
            Number of URLs inserted
        """
        if not urls:
            return 0

        try:
            # Prepare values and parameters
            value_parts = []
            params = {'sitemap_id': sitemap_id, 'tenant_id': tenant_id}

            for i, url_data in enumerate(urls):
                url = url_data.get('url')
                if not url:
                    continue

                param_prefix = f"url_{i}"
                url_param = f"{param_prefix}_url"
                lastmod_param = f"{param_prefix}_lastmod"
                priority_param = f"{param_prefix}_priority"
                changefreq_param = f"{param_prefix}_changefreq"

                value_parts.append(f"(%({url_param})s, %(sitemap_id)s, %(tenant_id)s, %({lastmod_param})s, %({priority_param})s, %({changefreq_param})s)")

                # Add parameters with proper type handling
                params[url_param] = str(url)

                # Handle potentially None values
                lastmod = url_data.get('lastmod')
                priority = url_data.get('priority')
                changefreq = url_data.get('changefreq')

                # Use empty string instead of None for database parameters
                params[lastmod_param] = str(lastmod) if lastmod is not None else ''
                params[priority_param] = str(priority) if priority is not None else ''
                params[changefreq_param] = str(changefreq) if changefreq is not None else ''

            if not value_parts:
                return 0

            # Construct query
            query = f"""
                INSERT INTO sitemap_urls (
                    url, sitemap_id, tenant_id, lastmod, priority, changefreq
                ) VALUES
                {', '.join(value_parts)}
                ON CONFLICT (sitemap_id, url) DO UPDATE SET
                    lastmod = EXCLUDED.lastmod,
                    priority = EXCLUDED.priority,
                    changefreq = EXCLUDED.changefreq
            """

            # Execute query
            await db_service.execute(query, params)

            return len(value_parts)

        except Exception as e:
            logger.error(f"Error batch inserting sitemap URLs: {str(e)}")
            return 0

    @classmethod
    async def _batch_insert_places(
        cls,
        places: List[Dict[str, Any]],
        search_id: str,
        tenant_id: str,
        user_id: str
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Insert a batch of places.

        Args:
            places: List of place records
            search_id: Search ID
            tenant_id: Tenant ID
            user_id: User ID

        Returns:
            Tuple of (number of places inserted, list of failed places)
        """
        if not places:
            return 0, []

        stored_count = 0
        failed_places = []

        # Process each place individually for better error handling
        for place in places:
            try:
                place_id = place.get('place_id')
                if not place_id:
                    failed_places.append({
                        'place': place.get('name', 'Unknown'),
                        'error': 'Missing place_id'
                    })
                    continue

                # Prepare raw_data as JSON if it's not already
                raw_data = place.get('raw_data')
                if raw_data and not isinstance(raw_data, str):
                    raw_data = json.dumps(raw_data)
                elif not raw_data:
                    raw_data = json.dumps(place)

                # Insert query with upsert
                query = """
                    INSERT INTO places_staging (
                        place_id, name, formatted_address, business_type,
                        latitude, longitude, vicinity, rating,
                        user_ratings_total, price_level, tenant_id,
                        created_by, user_id, search_job_id,
                        search_query, search_location, raw_data, search_time
                    ) VALUES (
                        %(place_id)s, %(name)s, %(formatted_address)s, %(business_type)s,
                        %(latitude)s, %(longitude)s, %(vicinity)s, %(rating)s,
                        %(user_ratings_total)s, %(price_level)s, %(tenant_id)s,
                        %(user_id)s, %(user_id)s, %(search_id)s,
                        %(search_query)s, %(search_location)s, %(raw_data)s, NOW()
                    ) ON CONFLICT (place_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        formatted_address = EXCLUDED.formatted_address,
                        business_type = EXCLUDED.business_type,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        vicinity = EXCLUDED.vicinity,
                        rating = EXCLUDED.rating,
                        user_ratings_total = EXCLUDED.user_ratings_total,
                        price_level = EXCLUDED.price_level,
                        search_job_id = EXCLUDED.search_job_id,
                        search_query = EXCLUDED.search_query,
                        search_location = EXCLUDED.search_location,
                        search_time = NOW(),
                        raw_data = EXCLUDED.raw_data
                    RETURNING id
                """

                params = {
                    'place_id': place_id,
                    'name': place.get('name', ''),
                    'formatted_address': place.get('formatted_address', ''),
                    'business_type': place.get('business_type', ''),
                    'latitude': place.get('latitude'),
                    'longitude': place.get('longitude'),
                    'vicinity': place.get('vicinity', ''),
                    'rating': place.get('rating'),
                    'user_ratings_total': place.get('user_ratings_total'),
                    'price_level': place.get('price_level'),
                    'tenant_id': tenant_id,
                    'user_id': user_id,
                    'search_id': search_id,
                    'search_query': place.get('search_query', ''),
                    'search_location': place.get('search_location', ''),
                    'raw_data': raw_data
                }

                result = await db_service.execute_returning(query, params)

                if result:
                    stored_count += 1
                else:
                    failed_places.append({
                        'place': place.get('name', 'Unknown'),
                        'error': 'Insert returned no result'
                    })

            except Exception as e:
                logger.error(f"Error inserting place {place.get('name', 'Unknown')}: {str(e)}")
                failed_places.append({
                    'place': place.get('name', 'Unknown'),
                    'error': str(e)
                })

        return stored_count, failed_places

    @classmethod
    async def _store_domain_emails(
        cls,
        domain_id: str,
        emails: List[str],
        source_url: str,
        tenant_id: str,
        user_id: str
    ) -> int:
        """
        Store emails for a domain.

        Args:
            domain_id: Domain ID
            emails: List of email addresses
            source_url: Source URL where emails were found
            tenant_id: Tenant ID
            user_id: User ID

        Returns:
            Number of emails stored
        """
        if not emails:
            return 0

        stored_count = 0

        for email in emails:
            if not email:
                continue

            try:
                query = """
                    INSERT INTO contacts (
                        domain_id, tenant_id, email, source_url, created_by, discovered_at, last_updated
                    ) VALUES (
                        %(domain_id)s, %(tenant_id)s, %(email)s, %(source_url)s, %(user_id)s, NOW(), NOW()
                    ) ON CONFLICT (domain_id, email) DO UPDATE SET
                        last_updated = NOW(),
                        source_url = COALESCE(contacts.source_url, EXCLUDED.source_url)
                    RETURNING id
                """

                params = {
                    'domain_id': domain_id,
                    'tenant_id': tenant_id,
                    'email': email,
                    'source_url': source_url,
                    'user_id': user_id
                }

                result = await db_service.execute_returning(query, params)

                if result:
                    stored_count += 1

            except Exception as e:
                logger.error(f"Error storing email {email} for domain {domain_id}: {str(e)}")

        return stored_count

    @classmethod
    async def _store_domain_phones(
        cls,
        domain_id: str,
        phones: List[str],
        source_url: str,
        tenant_id: str,
        user_id: str
    ) -> int:
        """
        Store phone numbers for a domain.

        Args:
            domain_id: Domain ID
            phones: List of phone numbers
            source_url: Source URL where phones were found
            tenant_id: Tenant ID
            user_id: User ID

        Returns:
            Number of phones stored
        """
        if not phones:
            return 0

        stored_count = 0

        for phone in phones:
            if not phone:
                continue

            try:
                query = """
                    INSERT INTO phones (
                        domain_id, tenant_id, phone_number, source_url, created_by, discovered_at, last_updated
                    ) VALUES (
                        %(domain_id)s, %(tenant_id)s, %(phone_number)s, %(source_url)s, %(user_id)s, NOW(), NOW()
                    ) ON CONFLICT (domain_id, phone_number) DO UPDATE SET
                        last_updated = NOW(),
                        source_url = COALESCE(phones.source_url, EXCLUDED.source_url)
                    RETURNING id
                """

                params = {
                    'domain_id': domain_id,
                    'tenant_id': tenant_id,
                    'phone_number': phone,
                    'source_url': source_url,
                    'user_id': user_id
                }

                result = await db_service.execute_returning(query, params)

                if result:
                    stored_count += 1

            except Exception as e:
                logger.error(f"Error storing phone {phone} for domain {domain_id}: {str(e)}")

        return stored_count

    @classmethod
    async def _store_domain_social_media(
        cls,
        domain_id: str,
        social_media: Dict[str, str],
        tenant_id: str,
        user_id: str
    ) -> int:
        """
        Store social media links for a domain.

        Args:
            domain_id: Domain ID
            social_media: Dictionary of platform -> URL
            tenant_id: Tenant ID
            user_id: User ID

        Returns:
            Number of social media links stored
        """
        if not social_media:
            return 0

        stored_count = 0

        for platform, url in social_media.items():
            if not platform or not url:
                continue

            try:
                query = """
                    INSERT INTO social_media (
                        domain_id, tenant_id, platform, url, created_by, discovered_at, last_updated
                    ) VALUES (
                        %(domain_id)s, %(tenant_id)s, %(platform)s, %(url)s, %(user_id)s, NOW(), NOW()
                    ) ON CONFLICT (domain_id, platform) DO UPDATE SET
                        last_updated = NOW(),
                        url = EXCLUDED.url
                    RETURNING id
                """

                params = {
                    'domain_id': domain_id,
                    'tenant_id': tenant_id,
                    'platform': platform,
                    'url': url,
                    'user_id': user_id
                }

                result = await db_service.execute_returning(query, params)

                if result:
                    stored_count += 1

            except Exception as e:
                logger.error(f"Error storing social media {platform} for domain {domain_id}: {str(e)}")

        return stored_count

    @classmethod
    async def _get_domain_sitemaps(
        cls,
        domain_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get sitemaps for a domain.

        Args:
            domain_id: Domain ID
            tenant_id: Tenant ID

        Returns:
            List of sitemap records
        """
        try:
            query = """
                SELECT id, url, total_urls, is_index, metadata
                FROM sitemaps
                WHERE domain_id = %(domain_id)s
                ORDER BY last_scan DESC
                LIMIT 1
            """

            params = {
                'domain_id': domain_id
            }

            sitemaps = await db_service.fetch_all(query, params)

            # Convert metadata to objects if they're JSON strings
            for sitemap in sitemaps:
                metadata = sitemap.get('metadata')
                if metadata and isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                        sitemap['metadata'] = metadata
                    except (json.JSONDecodeError, TypeError):
                        pass

            return sitemaps

        except Exception as e:
            logger.error(f"Error getting sitemaps for domain {domain_id}: {str(e)}")
            return []

    @classmethod
    async def _get_domain_contacts(
        cls,
        domain_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get all contact information for a domain.

        Args:
            domain_id: Domain ID
            tenant_id: Tenant ID

        Returns:
            Dictionary of contact information
        """
        try:
            # Get emails
            email_query = """
                SELECT * FROM contacts
                WHERE domain_id = %(domain_id)s AND tenant_id = %(tenant_id)s
                ORDER BY discovered_at DESC
            """

            # Get phones
            phone_query = """
                SELECT * FROM phones
                WHERE domain_id = %(domain_id)s AND tenant_id = %(tenant_id)s
                ORDER BY discovered_at DESC
            """

            # Get social media
            social_query = """
                SELECT * FROM social_media
                WHERE domain_id = %(domain_id)s AND tenant_id = %(tenant_id)s
                ORDER BY discovered_at DESC
            """

            params = {
                'domain_id': domain_id,
                'tenant_id': tenant_id
            }

            # Execute all queries concurrently
            emails_future = db_service.fetch_all(email_query, params)
            phones_future = db_service.fetch_all(phone_query, params)
            social_future = db_service.fetch_all(social_query, params)

            emails, phones, social = await asyncio.gather(
                emails_future,
                phones_future,
                social_future
            )

            # Organize social media by platform
            social_media = {}
            for item in social:
                platform = item.get('platform')
                url = item.get('url')
                if platform and url:
                    social_media[platform] = url

            return {
                'emails': emails,
                'phones': phones,
                'social_media': social_media
            }

        except Exception as e:
            logger.error(f"Error getting contacts for domain {domain_id}: {str(e)}")
            return {
                'emails': [],
                'phones': [],
                'social_media': {}
            }

# Create singleton instance
storage_service = StorageService()
