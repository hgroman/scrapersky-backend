"""
Database operations for the domains table.
"""
from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging
from ..db.async_sb_connection import async_db

class DomainDBHandler:
    """Handles all database operations for the domains table."""

    @staticmethod
    async def insert_domain_data(domain_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert new domain data into the domains table.

        Args:
            domain_data: Dictionary containing domain metadata

        Returns:
            Dict containing the inserted record

        Raises:
            ValueError: If the insert fails or no row is returned
        """
        # Convert dict fields to JSON strings
        if isinstance(domain_data.get('tech_stack'), dict):
            domain_data['tech_stack'] = json.dumps(domain_data['tech_stack'])
        if isinstance(domain_data.get('meta_json'), dict):
            domain_data['meta_json'] = json.dumps(domain_data['meta_json'])

        query = """
            INSERT INTO domains (
                tenant_id,
                domain,
                title,
                description,
                favicon_url,
                logo_url,
                language,
                is_wordpress,
                wordpress_version,
                has_elementor,
                email_addresses,
                phone_numbers,
                facebook_url,
                twitter_url,
                linkedin_url,
                instagram_url,
                youtube_url,
                tech_stack,
                content_scrape_status,
                content_scrape_at,
                first_scan,
                last_scan,
                meta_json
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                $11, $12, $13, $14, $15, $16, $17, $18,
                'complete', now(), now(), now(), $19
            )
            RETURNING *;
        """

        async with async_db.get_connection() as conn:
            try:
                values = [
                    domain_data.get('tenant_id'),
                    domain_data.get('domain'),
                    domain_data.get('title'),
                    domain_data.get('description'),
                    domain_data.get('favicon_url'),
                    domain_data.get('logo_url'),
                    domain_data.get('language'),
                    domain_data.get('is_wordpress'),
                    domain_data.get('wordpress_version'),
                    domain_data.get('has_elementor'),
                    domain_data.get('email_addresses'),
                    domain_data.get('phone_numbers'),
                    domain_data.get('facebook_url'),
                    domain_data.get('twitter_url'),
                    domain_data.get('linkedin_url'),
                    domain_data.get('instagram_url'),
                    domain_data.get('youtube_url'),
                    domain_data.get('tech_stack'),
                    domain_data.get('meta_json')
                ]
                row = await conn.fetchrow(query, *values)
                if not row:
                    raise ValueError("Failed to insert domain data - no row returned")
                return dict(row)
            except Exception as e:
                logging.error(f"Error inserting domain data: {str(e)}")
                raise

    @staticmethod
    async def update_domain_data(domain: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing domain data.

        Args:
            domain: Domain to update
            update_data: Dictionary containing fields to update

        Returns:
            Dict containing the updated record

        Raises:
            ValueError: If the domain is not found or update fails
        """
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        param_count = 1

        # Log the update operation
        logging.info(f"Updating domain {domain} with fields: {', '.join(update_data.keys())}")

        for key, value in update_data.items():
            update_fields.append(f"{key} = ${param_count}")
            values.append(value)
            param_count += 1

        update_fields.append("updated_at = now()")
        update_string = ", ".join(update_fields)

        query = f"""
            UPDATE domains
            SET {update_string}
            WHERE domain = ${param_count}
            RETURNING *;
        """
        values.append(domain)

        async with async_db.get_connection() as conn:
            try:
                row = await conn.fetchrow(query, *values)
                if not row:
                    logging.error(f"Domain not found during update: {domain}")
                    raise ValueError(f"Domain not found: {domain}")
                logging.info(f"Successfully updated domain: {domain}")
                return dict(row)
            except Exception as e:
                logging.error(f"Error updating domain data for {domain}: {str(e)}")
                # Log the query for debugging
                safe_values = [str(v)[:50] + '...' if isinstance(v, str) and len(str(v)) > 50 else v for v in values]
                logging.error(f"Failed query: {query}")
                logging.error(f"Values: {safe_values}")
                raise

    @staticmethod
    async def get_domain_data(domain: str) -> Dict[str, Any]:
        """
        Retrieve domain data.

        Args:
            domain: Domain to retrieve

        Returns:
            Dict containing the domain record

        Raises:
            ValueError: If the domain is not found
        """
        query = """
            SELECT * FROM domains
            WHERE domain = $1;
        """

        async with async_db.get_connection() as conn:
            try:
                row = await conn.fetchrow(query, domain)
                if not row:
                    raise ValueError(f"Domain not found: {domain}")
                return dict(row)
            except Exception as e:
                logging.error(f"Error retrieving domain data: {str(e)}")
                raise

    @staticmethod
    async def domain_exists(domain: str) -> bool:
        """
        Check if a domain already exists in the database.

        Args:
            domain: Domain to check

        Returns:
            bool: True if domain exists, False otherwise
        """
        query = """
            SELECT EXISTS(SELECT 1 FROM domains WHERE domain = $1) AS exists;
        """

        async with async_db.get_connection() as conn:
            try:
                row = await conn.fetchrow(query, domain)
                return row['exists'] if row else False
            except Exception as e:
                logging.error(f"Error checking if domain exists: {str(e)}")
                return False

    async def insert_domain(self, domain: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Insert new domain metadata."""
        try:
            # Convert metadata to database format
            domain_data = self._prepare_domain_data(domain, metadata)

            # Insert into database
            async with async_db.pool.acquire() as conn:
                result = await conn.fetchrow(
                    """
                    INSERT INTO domains (
                        domain, meta_json, status, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $4)
                    RETURNING *
                    """,
                    domain,
                    json.dumps(metadata),
                    'completed',
                    datetime.utcnow()
                )
                return dict(result) if result else {}
        except Exception as e:
            logging.error(f"Error inserting domain {domain}: {str(e)}")
            raise

    async def update_domain(self, domain: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing domain metadata."""
        try:
            # Convert metadata to database format
            domain_data = self._prepare_domain_data(domain, metadata)

            # Update database
            async with async_db.pool.acquire() as conn:
                result = await conn.fetchrow(
                    """
                    UPDATE domains
                    SET meta_json = $2,
                        status = $3,
                        updated_at = $4
                    WHERE domain = $1
                    RETURNING *
                    """,
                    domain,
                    json.dumps(metadata),
                    'completed',
                    datetime.utcnow()
                )
                return dict(result) if result else {}
        except Exception as e:
            logging.error(f"Error updating domain {domain}: {str(e)}")
            raise

    def _prepare_domain_data(self, domain: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare domain data for database insertion/update."""
        return {
            "domain": domain,
            "meta_json": metadata,
            "status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
