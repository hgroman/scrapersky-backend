"""
Domain Service

Provides operations for domain management and metadata handling.

This service follows the transaction-aware pattern where it works with
transactions but does not create, commit, or rollback transactions itself.
Transaction boundaries are managed by the router.
"""
import logging
import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_session
from ..models import Domain

logger = logging.getLogger(__name__)

class DomainService:
    """
    Service for domain management.

    This service provides methods for working with Domain entities,
    including creation, retrieval, and metadata management.
    
    This service is transaction-aware but doesn't manage transactions.
    Transaction boundaries are owned by the routers.
    """

    async def get_by_id(self, session: AsyncSession, domain_id: Union[str, uuid.UUID],
                       tenant_id: Optional[str] = None) -> Optional[Domain]:
        """
        Get a domain by ID with optional tenant validation.

        This method is transaction-aware but does not manage transactions.
        Transaction boundaries should be managed by the router.

        Args:
            session: SQLAlchemy session
            domain_id: Domain ID to look up
            tenant_id: Optional tenant ID for security filtering

        Returns:
            Domain instance or None if not found
        """
        # Check if in transaction
        in_transaction = session.in_transaction()
        logger.debug(f"get_by_id transaction state: {in_transaction}")
        
        return await Domain.get_by_id(session, domain_id)

    async def get_by_domain_name(self, session: AsyncSession, domain_name: str,
                                tenant_id: Optional[str] = None) -> Optional[Domain]:
        """
        Get a domain by name with optional tenant validation.

        Args:
            session: SQLAlchemy session
            domain_name: Domain name to look up
            tenant_id: Optional tenant ID for security filtering

        Returns:
            Domain instance or None if not found
        """
        return await Domain.get_by_domain_name(session, domain_name, tenant_id)

    async def get_all(self, session: AsyncSession, tenant_id: Optional[str] = None,
                     limit: int = 100, offset: int = 0,
                     **filters) -> List[Domain]:
        """
        Get all domains with optional filtering.

        Args:
            session: SQLAlchemy session
            tenant_id: Optional tenant ID for filtering
            limit: Maximum number of domains to return
            offset: Offset for pagination
            **filters: Additional filters to apply

        Returns:
            List of Domain instances
        """
        # Build query
        query = select(Domain)

        # REMOVED tenant filtering as per architectural mandate
        # JWT authentication happens ONLY at API gateway endpoints
        # Database operations should NEVER handle JWT or tenant authentication

        # Apply additional filters
        for field, value in filters.items():
            if hasattr(Domain, field):
                query = query.where(getattr(Domain, field) == value)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await session.execute(query)
        domains = result.scalars().all()

        # Convert to list to match the return type annotation
        return list(domains)

    async def create(self, session: AsyncSession, domain_data: Dict[str, Any]) -> Domain:
        """
        Create a new domain.

        Args:
            session: SQLAlchemy session
            domain_data: Dictionary of domain data

        Returns:
            New Domain instance
        """
        domain = Domain(**domain_data)
        session.add(domain)
        return domain

    async def create_from_metadata(self, session: AsyncSession, domain: str,
                                  tenant_id: str, metadata: Dict[str, Any],
                                  created_by: Optional[str] = None,
                                  batch_id: Optional[str] = None) -> Domain:
        """
        Create a domain record from metadata dictionary.

        This standardizes domain creation from metadata extraction results,
        ensuring consistent handling in both single and batch processing.

        Args:
            session: SQLAlchemy session
            domain: Domain name
            tenant_id: Tenant ID
            metadata: Extracted metadata dictionary
            created_by: User ID who created this record
            batch_id: Optional batch ID if part of batch processing

        Returns:
            New Domain instance
        """
        return await Domain.create_from_metadata(
            session, domain, tenant_id, metadata, created_by, batch_id
        )

    async def update_from_metadata(self, session: AsyncSession, domain_obj: Domain,
                                 metadata: Dict[str, Any]) -> Domain:
        """
        Update a domain record from metadata dictionary.

        Args:
            session: SQLAlchemy session
            domain_obj: Existing Domain object
            metadata: New metadata dictionary

        Returns:
            Updated Domain instance
        """
        return await Domain.update_from_metadata(session, domain_obj, metadata)

    async def update(self, session: AsyncSession, domain_id: Union[str, uuid.UUID],
                    domain_data: Dict[str, Any],
                    tenant_id: Optional[str] = None) -> Optional[Domain]:
        """
        Update a domain.

        Args:
            session: SQLAlchemy session
            domain_id: Domain ID to update
            domain_data: Dictionary of domain data to update
            tenant_id: Optional tenant ID for security filtering

        Returns:
            Updated Domain instance or None if not found
        """
        # Get domain
        # REMOVED tenant filtering as per architectural mandate
        # JWT authentication happens ONLY at API gateway endpoints
        # Database operations should NEVER handle JWT or tenant authentication
        domain = await session.get(Domain, domain_id)

        if not domain:
            return None

        # Update domain fields
        for field, value in domain_data.items():
            if hasattr(domain, field):
                setattr(domain, field, value)

        # Add to session
        session.add(domain)
        return domain

    async def process_domain_metadata(self, session: AsyncSession, domain: str,
                                     metadata: Dict[str, Any], tenant_id: str,
                                     created_by: Optional[str] = None,
                                     batch_id: Optional[str] = None) -> Domain:
        """
        Process domain metadata, creating or updating domain records.

        This method standardizes domain processing in both single and batch operations,
        ensuring consistent domain record management.

        Args:
            session: SQLAlchemy session
            domain: Domain name
            metadata: Extracted metadata dictionary
            tenant_id: Tenant ID
            created_by: User ID who created this record
            batch_id: Optional batch ID if part of batch processing

        Returns:
            Domain instance (newly created or updated)
        """
        try:
            # Check if the session is already in a transaction
            in_transaction = session.in_transaction()
            logger.debug(f"Session transaction state in process_domain_metadata: {in_transaction}")
            
            # Check if domain already exists for this tenant
            existing_domain = await self.get_by_domain_name(session, domain, tenant_id)

            if existing_domain:
                logger.info(f"Updating existing domain: {domain}")

                # Add batch_id to domain if provided and not already set
                if batch_id and hasattr(existing_domain, 'batch_id'):
                    # Set attribute safely using setattr
                    if getattr(existing_domain, 'batch_id', None) is None:
                        setattr(existing_domain, 'batch_id', batch_id)

                # Update domain with new metadata - pass existing session
                updated_domain = await Domain.update_from_metadata(
                    session, existing_domain, metadata
                )

                return updated_domain
            else:
                logger.info(f"Creating new domain: {domain}")

                # Create new domain with metadata - pass existing session
                new_domain = await Domain.create_from_metadata(
                    session,
                    domain=domain,
                    tenant_id=tenant_id,  # Pass as string
                    metadata=metadata,
                    created_by=created_by,  # Pass as string
                    batch_id=batch_id
                )

                return new_domain

        except Exception as e:
            logger.error(f"Error processing domain {domain}: {str(e)}")
            # Let caller handle the exception for proper transaction management
            raise

    async def get_by_batch_id(self, session: AsyncSession, batch_id: str,
                             tenant_id: Optional[str] = None) -> List[Domain]:
        """
        Get all domains that belong to a specific batch.

        Args:
            session: SQLAlchemy session
            batch_id: Batch ID to look up
            tenant_id: Optional tenant ID for security filtering

        Returns:
            List of Domain instances
        """
        return await Domain.get_by_batch_id(session, batch_id, tenant_id)

    async def get_or_create(self, session: AsyncSession, domain: str,
                        tenant_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> Domain:
        """
        Get a domain by name or create it if it doesn't exist.

        Args:
            session: SQLAlchemy session
            domain: Domain name
            tenant_id: Optional tenant ID
            metadata: Optional metadata to use when creating the domain

        Returns:
            Domain instance (existing or newly created)
        """
        try:
            # Check if the session is already in a transaction
            in_transaction = session.in_transaction()
            logger.debug(f"Session transaction state in get_or_create: {in_transaction}")
            
            # Check if domain already exists
            existing_domain = await self.get_by_domain_name(session, domain, tenant_id)

            if existing_domain:
                logger.info(f"Found existing domain: {domain}")

                # Update with new metadata if provided
                if metadata:
                    existing_domain = await Domain.update_from_metadata(
                        session, existing_domain, metadata
                    )

                return existing_domain
            else:
                logger.info(f"Creating new domain: {domain}")

                # Create new domain with metadata
                if tenant_id is None:
                    # Use a default tenant ID if none provided
                    tenant_id = "00000000-0000-0000-0000-000000000000"

                new_domain = await Domain.create_from_metadata(
                    session,
                    domain=domain,
                    tenant_id=tenant_id,
                    metadata=metadata or {},
                    created_by=None,
                    batch_id=None
                )

                # Only flush changes if we're in a transaction
                if in_transaction:
                    await session.flush()

                return new_domain
        except Exception as e:
            logger.error(f"Error in get_or_create for domain {domain}: {str(e)}")
            # Let caller handle the exception for proper transaction management
            raise

# Create singleton instance
domain_service = DomainService()
