"""
Database operations for the domains table.

This module provides a transaction-aware handler for domain-related database operations.
It follows the standardized pattern where it accepts a session parameter and does not
create, commit, or rollback transactions itself.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from ..services.core.db_service import db_service


class DomainDBHandler:
    """Handles all database operations for the domains table."""

    @staticmethod
    async def insert_domain_data(
        session: AsyncSession, domain_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert new domain data into the domains table.

        Args:
            session: An active database session
            domain_data: Dictionary containing domain metadata

        Returns:
            Dict containing the inserted record

        Raises:
            ValueError: If the insert fails or no row is returned
        """
        # Convert dict fields to JSON strings
        if isinstance(domain_data.get("tech_stack"), dict):
            domain_data["tech_stack"] = json.dumps(domain_data["tech_stack"])
        if isinstance(domain_data.get("meta_json"), dict):
            domain_data["meta_json"] = json.dumps(domain_data["meta_json"])

        # Use the standardized db_service for the insert
        try:
            result = await db_service.create_record(
                "domains",
                {
                    "domain": domain_data.get("domain"),
                    "tenant_id": domain_data.get("tenant_id"),
                    "created_by": domain_data.get("created_by"),
                    "status": domain_data.get("status", "pending"),
                    "title": domain_data.get("title"),
                    "description": domain_data.get("description"),
                    "is_wordpress": domain_data.get("is_wordpress"),
                    "tech_stack": domain_data.get("tech_stack"),
                    "contact_email": domain_data.get("contact_email"),
                    "contact_phone": domain_data.get("contact_phone"),
                    "facebook_url": domain_data.get("facebook_url"),
                    "twitter_url": domain_data.get("twitter_url"),
                    "linkedin_url": domain_data.get("linkedin_url"),
                    "instagram_url": domain_data.get("instagram_url"),
                    "meta_json": domain_data.get("meta_json"),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            )

            if not result:
                raise ValueError("Failed to insert domain data - no row returned")
            return result
        except Exception as e:
            logging.error(f"Error inserting domain data: {str(e)}")
            raise

    @staticmethod
    async def update_domain_data(
        session: AsyncSession, domain: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing domain data.

        Args:
            session: An active database session
            domain: Domain to update
            update_data: Dictionary containing fields to update

        Returns:
            Dict containing the updated record

        Raises:
            ValueError: If the domain is not found or update fails
        """
        # Log the update operation
        logging.info(
            f"Updating domain {domain} with fields: {', '.join(update_data.keys())}"
        )

        # Ensure updated_at is part of the update data
        update_data["updated_at"] = datetime.utcnow()

        try:
            # Use SQLAlchemy's execute method with a parameterized query
            query = text(
                """
                UPDATE domains
                SET """
                + ", ".join([f"{key} = :{key}" for key in update_data.keys()])
                + """
                WHERE domain = :domain
                RETURNING *
            """
            )

            # Add domain to the parameters
            params = {**update_data, "domain": domain}

            # Execute the query
            result = await session.execute(query, params)
            row = result.fetchone()

            if not row:
                logging.error(f"Domain not found during update: {domain}")
                raise ValueError(f"Domain not found: {domain}")

            logging.info(f"Successfully updated domain: {domain}")
            return dict(row)
        except Exception as e:
            logging.error(f"Error updating domain data for {domain}: {str(e)}")
            # Log the query for debugging
            logging.error(f"Failed updating domain: {domain}")
            raise

    @staticmethod
    async def get_domain_data(session: AsyncSession, domain: str) -> Dict[str, Any]:
        """
        Retrieve domain data from the domains table.

        Args:
            session: An active database session
            domain: Domain name to retrieve

        Returns:
            Dict containing the domain data

        Raises:
            ValueError: If the domain is not found
        """
        try:
            # Use db_service's fetch_one method for standardization
            result = await session.execute(
                text("SELECT * FROM domains WHERE domain = :domain"), {"domain": domain}
            )
            row = result.fetchone()
            if not row:
                raise ValueError(f"Domain not found: {domain}")
            return dict(row)
        except Exception as e:
            logging.error(f"Error retrieving domain data: {str(e)}")
            raise

    @staticmethod
    async def domain_exists(session: AsyncSession, domain: str, tenant_id: str) -> bool:
        """
        Check if a domain exists for a tenant.

        Args:
            session: An active database session
            domain: Domain name to check
            tenant_id: Tenant ID

        Returns:
            True if domain exists, False otherwise
        """
        query = """
        SELECT EXISTS(
            SELECT 1 FROM domains
            WHERE domain = :domain AND tenant_id = :tenant_id
        ) as exists
        """

        try:
            row = await session.execute(
                text(query), {"domain": domain, "tenant_id": tenant_id}
            )
            result = row.fetchone()
            # Convert to dict and check if 'exists' key is present
            result_dict = dict(result) if result else {}
            return result_dict.get("exists", False)
        except Exception as e:
            logging.error(f"Error checking if domain exists: {str(e)}")
            return False

    @staticmethod
    async def update_domain_status(
        session: AsyncSession,
        domain: str,
        tenant_id: str,
        status: str,
        updated_at: datetime,
    ) -> bool:
        """
        Update the status of a domain.

        Args:
            session: An active database session
            domain: Domain name
            tenant_id: Tenant ID
            status: New status
            updated_at: Update timestamp

        Returns:
            True if update was successful, False otherwise
        """
        query = """
        UPDATE domains
        SET status = :status, updated_at = :updated_at
        WHERE domain = :domain AND tenant_id = :tenant_id
        """

        try:
            await session.execute(
                text(query),
                {
                    "domain": domain,
                    "tenant_id": tenant_id,
                    "status": status,
                    "updated_at": updated_at,
                },
            )
            # No commit or rollback - the router owns the transaction
            return True
        except Exception as e:
            logging.error(f"Error updating domain status: {str(e)}")
            # No rollback - the router will handle transaction errors
            return False

    @staticmethod
    async def mark_domain_completed(
        session: AsyncSession, domain: str, tenant_id: str
    ) -> bool:
        """
        Mark a domain as completed.

        Args:
            session: An active database session
            domain: Domain name
            tenant_id: Tenant ID

        Returns:
            True if update was successful, False otherwise
        """
        now = datetime.utcnow()
        return await DomainDBHandler.update_domain_status(
            session, domain, tenant_id, "completed", now
        )

    async def insert_domain(
        self, session: AsyncSession, domain: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Insert a new domain with metadata."""
        try:
            # Convert metadata to database format
            domain_data = self._prepare_domain_data(domain, metadata)

            # Insert into database using the session parameter
            result = await session.execute(
                text("""
                INSERT INTO domains (
                    domain, meta_json, status, created_at, updated_at
                ) VALUES (:domain, :meta_json, :status, :timestamp, :timestamp)
                RETURNING *
                """),
                {
                    "domain": domain,
                    "meta_json": json.dumps(metadata),
                    "status": "completed",
                    "timestamp": datetime.utcnow(),
                },
            )
            row = result.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            logging.error(f"Error inserting domain {domain}: {str(e)}")
            raise

    async def update_domain(
        self, session: AsyncSession, domain: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing domain metadata."""
        try:
            # Convert metadata to database format
            domain_data = self._prepare_domain_data(domain, metadata)

            # Update database using the session parameter
            result = await session.execute(
                text("""
                UPDATE domains
                SET meta_json = :meta_json,
                    status = :status,
                    updated_at = :timestamp
                WHERE domain = :domain
                RETURNING *
                """),
                {
                    "domain": domain,
                    "meta_json": json.dumps(metadata),
                    "status": "completed",
                    "timestamp": datetime.utcnow(),
                },
            )
            row = result.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            logging.error(f"Error updating domain {domain}: {str(e)}")
            raise

    def _prepare_domain_data(
        self, domain: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare domain data for database insertion/update."""
        return {
            "domain": domain,
            "meta_json": metadata,
            "status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
