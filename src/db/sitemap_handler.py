"""
Database operations for sitemap-related tables.

This module provides functions for interacting with sitemap_files and
sitemap_urls tables, handling tenant isolation and proper SQL operations.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt_auth import DEFAULT_TENANT_ID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Utility function to validate and normalize tenant ID
def normalize_tenant_id(tenant_id: Optional[str]) -> str:
    """Basic tenant ID validation with fallback to default."""
    if not tenant_id:
        return DEFAULT_TENANT_ID
    try:
        # Ensure valid UUID format
        uuid_obj = uuid.UUID(tenant_id)
        return str(uuid_obj)
    except ValueError:
        logger.warning(f"Invalid tenant_id format: {tenant_id}, using default")
        return DEFAULT_TENANT_ID


class SitemapDBHandler:
    """Handles all database operations for sitemap tables."""

    async def create_sitemap_file(
        self, session: AsyncSession, sitemap_data: Dict[str, Any]
    ) -> str:
        """
        Create a new sitemap file record.

        Args:
            session: SQLAlchemy async session
            sitemap_data: Dictionary with sitemap file data

        Returns:
            ID of the created sitemap file
        """
        # Ensure tenant_id is valid
        tenant_id = normalize_tenant_id(sitemap_data.get("tenant_id"))
        sitemap_data["tenant_id"] = tenant_id

        # Set created_at and updated_at timestamps
        now = datetime.utcnow()
        sitemap_data["created_at"] = now
        sitemap_data["updated_at"] = now

        # Convert any JSON fields
        if "metadata" in sitemap_data and sitemap_data["metadata"] is not None:
            if isinstance(sitemap_data["metadata"], dict):
                sitemap_data["metadata"] = json.dumps(sitemap_data["metadata"])

        # Build query
        query = """
            INSERT INTO sitemap_files (
                url, domain_id, tenant_id, status, file_size_kb,
                url_count, created_at, updated_at, metadata, job_id
            ) VALUES (
                :url, :domain_id, :tenant_id, :status, :file_size_kb,
                :url_count, :created_at, :updated_at, :metadata, :job_id
            )
            RETURNING id
        """

        try:
            result = await session.execute(text(query), sitemap_data)
            sitemap_id = result.scalar_one()
            return str(sitemap_id)
        except Exception as e:
            logger.error(f"Error creating sitemap file: {str(e)}")
            raise

    async def update_sitemap_file(
        self,
        session: AsyncSession,
        sitemap_id: str,
        update_data: Dict[str, Any],
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Update existing sitemap file data.

        Args:
            session: SQLAlchemy async session
            sitemap_id: Sitemap ID to update
            update_data: Dictionary containing fields to update
            tenant_id: Tenant ID for security validation

        Returns:
            Dict containing the updated record

        Raises:
            ValueError: If the sitemap is not found or update fails
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        # Build dynamic update query based on provided fields
        update_fields = []
        values = {}

        # Add the ID and tenant_id to values
        values["id"] = sitemap_id
        values["tenant_id"] = tenant_id

        # Log the update operation
        logger.info(
            f"Updating sitemap file {sitemap_id} with fields: {', '.join(update_data.keys())}"
        )

        for key, value in update_data.items():
            if key == "tenant_id":
                # Prevent changing tenant_id for security
                continue

            # Convert dict/list fields to JSON strings if needed
            if isinstance(value, (dict, list)) and key in ["tags", "notes"]:
                value = json.dumps(value)

            update_fields.append(f"{key} = :{key}")
            values[key] = value

        # Add updated_at field
        update_fields.append("updated_at = :updated_at")
        values["updated_at"] = datetime.utcnow()

        update_string = ", ".join(update_fields)

        query = f"""
            UPDATE sitemap_files
            SET {update_string}
            WHERE id = :id AND tenant_id = :tenant_id
            RETURNING *
        """

        try:
            result = await session.execute(text(query), values)
            updated_row = result.fetchone()
            if not updated_row:
                raise ValueError(
                    f"Sitemap file not found or not accessible: {sitemap_id}"
                )
            return dict(updated_row)
        except Exception as e:
            logger.error(f"Error updating sitemap file {sitemap_id}: {str(e)}")
            raise

    async def get_sitemap_file(
        self, session: AsyncSession, sitemap_id: str, tenant_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve sitemap file data.

        Args:
            session: SQLAlchemy async session
            sitemap_id: Sitemap ID to retrieve
            tenant_id: Tenant ID for security validation

        Returns:
            Dict containing the sitemap file record

        Raises:
            ValueError: If the sitemap file is not found
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT * FROM sitemap_files
            WHERE id = :sitemap_id AND tenant_id = :tenant_id
        """

        try:
            result = await session.execute(
                text(query), {"sitemap_id": sitemap_id, "tenant_id": tenant_id}
            )
            record = result.fetchone()
            if not record:
                raise ValueError(
                    f"Sitemap file not found or not accessible: {sitemap_id}"
                )
            return dict(record)
        except Exception as e:
            logger.error(f"Error retrieving sitemap file data: {str(e)}")
            raise

    async def get_sitemap_files_for_domain(
        self, session: AsyncSession, domain_id: str, tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all sitemap files for a domain.

        Args:
            session: SQLAlchemy async session
            domain_id: Domain ID to get sitemaps for
            tenant_id: Tenant ID for security validation

        Returns:
            List of sitemap file records
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT * FROM sitemap_files
            WHERE domain_id = :domain_id AND tenant_id = :tenant_id
            ORDER BY created_at DESC
        """

        try:
            result = await session.execute(
                text(query), {"domain_id": domain_id, "tenant_id": tenant_id}
            )
            records = result.fetchall()
            return [dict(row) for row in records]
        except Exception as e:
            logger.error(
                f"Error retrieving sitemap files for domain {domain_id}: {str(e)}"
            )
            raise

    async def get_sitemap_files_by_job_id(
        self, session: AsyncSession, job_id: str, tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all sitemap files for a specific job.

        Args:
            session: SQLAlchemy async session
            job_id: Job ID to get sitemaps for
            tenant_id: Tenant ID for security validation

        Returns:
            List of sitemap file records
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT * FROM sitemap_files
            WHERE job_id = :job_id AND tenant_id = :tenant_id
            ORDER BY created_at DESC
        """

        try:
            result = await session.execute(
                text(query), {"job_id": job_id, "tenant_id": tenant_id}
            )
            records = result.fetchall()
            return [dict(row) for row in records]
        except Exception as e:
            logger.error(f"Error retrieving sitemap files for job {job_id}: {str(e)}")
            raise

    async def get_domain_by_name(
        self, session: AsyncSession, domain_name: str, tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get domain data by domain name.

        Args:
            session: SQLAlchemy async session
            domain_name: Domain name to look up
            tenant_id: Tenant ID for security validation

        Returns:
            Domain record as dictionary

        Raises:
            ValueError: If domain not found or not accessible
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT * FROM domains
            WHERE domain = :domain_name AND tenant_id = :tenant_id
        """

        try:
            result = await session.execute(
                text(query), {"domain_name": domain_name, "tenant_id": tenant_id}
            )
            record = result.fetchone()
            if not record:
                raise ValueError(f"Domain not found or not accessible: {domain_name}")
            return dict(record)
        except Exception as e:
            logger.error(f"Error retrieving domain data for {domain_name}: {str(e)}")
            raise

    async def get_domain_by_id(
        self, session: AsyncSession, domain_id: str, tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get domain data by ID.

        Args:
            session: SQLAlchemy async session
            domain_id: Domain ID to look up
            tenant_id: Tenant ID for security validation

        Returns:
            Domain record as dictionary

        Raises:
            ValueError: If domain not found or not accessible
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT * FROM domains
            WHERE id = :domain_id AND tenant_id = :tenant_id
        """

        try:
            result = await session.execute(
                text(query), {"domain_id": domain_id, "tenant_id": tenant_id}
            )
            record = result.fetchone()
            if not record:
                raise ValueError(f"Domain not found or not accessible: {domain_id}")
            return dict(record)
        except Exception as e:
            logger.error(f"Error retrieving domain data for ID {domain_id}: {str(e)}")
            raise

    async def get_domains_for_sitemap_analysis(
        self, session: AsyncSession, tenant_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get domains that are queued for sitemap analysis.

        Args:
            session: SQLAlchemy async session
            tenant_id: Tenant ID for security validation
            limit: Maximum number of domains to return

        Returns:
            List of domain records ready for sitemap analysis
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT id, domain, sitemap_url, tenant_id
            FROM domains
            WHERE tenant_id = :tenant_id AND is_active = TRUE
            AND (sitemap_monitor_status = 'queued' OR agency_sitemap_analysis_done = 'queued')
            LIMIT :limit
        """

        try:
            result = await session.execute(
                text(query), {"tenant_id": tenant_id, "limit": limit}
            )
            records = result.fetchall()
            return [dict(row) for row in records]
        except Exception as e:
            logger.error(f"Error retrieving domains for sitemap analysis: {str(e)}")
            raise

    async def update_domain_sitemap_status(
        self,
        session: AsyncSession,
        domain_id: str,
        status: str,
        tenant_id: str,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the sitemap monitoring status for a domain.

        Args:
            session: SQLAlchemy async session
            domain_id: Domain ID to update
            status: New status value
            tenant_id: Tenant ID for security validation
            error_message: Optional error message

        Returns:
            Updated domain record

        Raises:
            ValueError: If the domain is not found or update fails
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        try:
            # Create update data
            update_data = {
                "sitemap_monitor_status": status,
                "sitemap_monitor_at": datetime.utcnow(),
            }

            # Add error message if provided
            if error_message:
                update_data["sitemap_monitor_error"] = error_message[
                    :255
                ]  # Truncate to reasonable length

            query = """
                UPDATE domains
                SET sitemap_monitor_status = :sitemap_monitor_status,
                    sitemap_monitor_at = :sitemap_monitor_at
            """

            # Add error message to query if provided
            if error_message:
                query += ", sitemap_monitor_error = :sitemap_monitor_error"

            query += """
                WHERE id = :domain_id AND tenant_id = :tenant_id
                RETURNING *
            """

            params = {**update_data, "domain_id": domain_id, "tenant_id": tenant_id}

            result = await session.execute(text(query), params)
            updated_row = result.fetchone()
            if not updated_row:
                raise ValueError(
                    f"Domain with ID {domain_id} not found or update failed"
                )
            return dict(updated_row)

        except Exception as e:
            logger.error(f"Error updating domain sitemap status: {str(e)}")
            raise

    # Add alias for backward compatibility
    async def update_domain(
        self,
        session: AsyncSession,
        domain_id: str,
        status: str,
        tenant_id: str,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Alias for update_domain_sitemap_status for backward compatibility.

        Args:
            session: SQLAlchemy async session
            domain_id: Domain ID to update
            status: New status value
            tenant_id: Tenant ID for security validation
            error_message: Optional error message

        Returns:
            Updated domain record
        """
        return await self.update_domain_sitemap_status(
            session, domain_id, status, tenant_id, error_message
        )

    # Sitemap URL operations

    async def create_sitemap_url(
        self, session: AsyncSession, url_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new sitemap URL record.

        Args:
            session: SQLAlchemy async session
            url_data: Dictionary containing sitemap URL data

        Returns:
            Dict containing the inserted record

        Raises:
            ValueError: If the insert fails or no row is returned
        """
        # Normalize tenant_id for security
        url_data["tenant_id"] = normalize_tenant_id(url_data.get("tenant_id"))

        # Convert dict/list fields to JSON strings if needed
        for field in ["tags", "notes"]:
            if isinstance(url_data.get(field), (dict, list)):
                url_data[field] = json.dumps(url_data[field])

        # Generate UUID if not provided
        if "id" not in url_data:
            url_data["id"] = str(uuid.uuid4())

        # Build the columns and values
        columns = ", ".join(url_data.keys())
        placeholders = ", ".join([f":{key}" for key in url_data.keys()])

        query = f"""
            INSERT INTO sitemap_urls (
                {columns}
            ) VALUES (
                {placeholders}
            )
            RETURNING *
        """

        try:
            result = await session.execute(text(query), url_data)
            record = result.fetchone()
            if not record:
                raise ValueError("Failed to insert sitemap URL - no row returned")
            return dict(record)
        except Exception as e:
            logger.error(f"Error inserting sitemap URL: {str(e)}")
            raise

    async def get_sitemap_urls(
        self,
        session: AsyncSession,
        sitemap_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get URLs for a specific sitemap.

        Args:
            session: SQLAlchemy async session
            sitemap_id: Sitemap ID to get URLs for
            tenant_id: Tenant ID for security validation
            limit: Maximum number of records to return
            offset: Offset for pagination

        Returns:
            List of sitemap URL records
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT * FROM sitemap_urls
            WHERE sitemap_id = :sitemap_id AND tenant_id = :tenant_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """

        try:
            result = await session.execute(
                text(query),
                {
                    "sitemap_id": sitemap_id,
                    "tenant_id": tenant_id,
                    "limit": limit,
                    "offset": offset,
                },
            )
            records = result.fetchall()
            return [dict(row) for row in records]
        except Exception as e:
            logger.error(f"Error retrieving URLs for sitemap {sitemap_id}: {str(e)}")
            raise

    async def get_sitemap_urls_count(
        self, session: AsyncSession, sitemap_id: str, tenant_id: str
    ) -> int:
        """
        Get count of URLs for a specific sitemap.

        Args:
            session: SQLAlchemy async session
            sitemap_id: Sitemap ID to get count for
            tenant_id: Tenant ID for security validation

        Returns:
            Count of sitemap URL records
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT COUNT(*) FROM sitemap_urls
            WHERE sitemap_id = :sitemap_id AND tenant_id = :tenant_id
        """

        try:
            result = await session.execute(
                text(query), {"sitemap_id": sitemap_id, "tenant_id": tenant_id}
            )
            record = result.fetchone()
            return record[0] if record else 0
        except Exception as e:
            logger.error(
                f"Error retrieving URL count for sitemap {sitemap_id}: {str(e)}"
            )
            raise

    async def bulk_insert_sitemap_urls(
        self, session: AsyncSession, urls: List[Dict[str, Any]], tenant_id: str
    ) -> int:
        """
        Insert multiple sitemap URLs in a single transaction.

        Args:
            session: SQLAlchemy async session
            urls: List of URL dictionaries to insert
            tenant_id: Tenant ID for security validation

        Returns:
            Number of URLs inserted

        Raises:
            ValueError: If bulk insert fails
        """
        if not urls:
            return 0

        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        try:
            # Prepare URLs for insertion
            prepared_urls = []
            for url in urls:
                # Create a copy to avoid modifying the original
                prepared_url = url.copy()

                # Ensure tenant ID
                prepared_url["tenant_id"] = tenant_id

                # Generate UUID if not provided
                if "id" not in prepared_url:
                    prepared_url["id"] = str(uuid.uuid4())

                # Convert JSON fields
                for field in ["tags", "notes"]:
                    if isinstance(prepared_url.get(field), (dict, list)):
                        prepared_url[field] = json.dumps(prepared_url[field])

                prepared_urls.append(prepared_url)

            # Process in batches to avoid too many parameters
            batch_size = 100
            total_inserted = 0

            for i in range(0, len(prepared_urls), batch_size):
                batch = prepared_urls[i : i + batch_size]

                # Get all fields from the first URL
                sample_url = batch[0]
                fields = list(sample_url.keys())

                # Build the insert query
                columns = ", ".join(fields)
                placeholders = ", ".join([f":{field}" for field in fields])

                query = f"""
                    INSERT INTO sitemap_urls ({columns})
                    VALUES ({placeholders})
                    ON CONFLICT (id) DO NOTHING
                """

                # Execute the batch insert
                await session.execute(text(query), batch)
                # Since we can't reliably get rowcount, we'll assume the batch was inserted
                total_inserted += len(batch)

            return total_inserted

        except Exception as e:
            logger.error(f"Error in bulk insert of sitemap URLs: {str(e)}")
            raise ValueError(f"Failed to bulk insert sitemap URLs: {str(e)}")

    async def sitemap_file_exists(
        self, session: AsyncSession, url: str, domain_id: str, tenant_id: str
    ) -> bool:
        """
        Check if a sitemap file already exists for a domain and URL.

        Args:
            session: SQLAlchemy async session
            url: Sitemap URL
            domain_id: Domain ID
            tenant_id: Tenant ID for security validation

        Returns:
            bool: True if sitemap file exists, False otherwise
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT EXISTS(
                SELECT 1 FROM sitemap_files
                WHERE url = :url AND domain_id = :domain_id AND tenant_id = :tenant_id
            ) AS exists
        """

        try:
            result = await session.execute(
                text(query),
                {"url": url, "domain_id": domain_id, "tenant_id": tenant_id},
            )
            record = result.fetchone()
            # Convert to dict and check if 'exists' key is present
            result_dict = dict(record) if record else {}
            return result_dict.get("exists", False)
        except Exception as e:
            logger.error(f"Error checking if sitemap file exists: {str(e)}")
            return False

    async def get_sitemap_file_by_url(
        self, session: AsyncSession, url: str, domain_id: str, tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get sitemap file by URL.

        Args:
            session: SQLAlchemy async session
            url: Sitemap URL
            domain_id: Domain ID
            tenant_id: Tenant ID for security validation

        Returns:
            Sitemap file record

        Raises:
            ValueError: If sitemap file not found
        """
        # Normalize tenant_id for security
        tenant_id = normalize_tenant_id(tenant_id)

        query = """
            SELECT * FROM sitemap_files
            WHERE url = :url AND domain_id = :domain_id AND tenant_id = :tenant_id
        """

        try:
            result = await session.execute(
                text(query),
                {"url": url, "domain_id": domain_id, "tenant_id": tenant_id},
            )
            record = result.fetchone()
            if not record:
                raise ValueError(f"Sitemap file not found for URL: {url}")
            return dict(record)
        except Exception as e:
            logger.error(f"Error retrieving sitemap file by URL: {str(e)}")
            raise

    async def get_table_info(self, session: AsyncSession) -> list:
        """
        Get information about sitemap-related database tables

        Args:
            session: SQLAlchemy async session

        Returns:
            List of table information
        """
        tables = []

        try:
            # Get table info for each table separately
            for table in ["jobs", "domains", "sitemap_files", "sitemap_urls"]:
                # Query to get column count
                column_query = """
                    SELECT COUNT(*)
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = :table
                """
                column_result = await session.execute(
                    text(column_query), {"table": table}
                )

                # Query to get row count - using parameterized query properly
                row_query = f"SELECT COUNT(*) FROM {table}"
                row_result = await session.execute(text(row_query))

                if column_result and row_result:
                    # Process column result
                    columns_data = column_result.fetchall()
                    columns_count = len(columns_data) if columns_data else 0

                    # Process row result
                    row_data = row_result.fetchone()
                    row_count = row_data[0] if row_data else 0

                    tables.append(
                        {"name": table, "columns": columns_count, "rows": row_count}
                    )

            return tables
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            return []
