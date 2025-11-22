"""
Validation API Service (WO-018)

Business logic for DeBounce email validation API endpoints.

This service provides API-layer functionality for queuing contacts for validation
and retrieving validation status/statistics. It does NOT perform actual validation
- that's handled by the DeBounceValidationService and scheduler.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.future import select as future_select

from src.models.wf7_contact import Contact
from src.schemas.wf7_contact_validation_schemas import ContactFilters

logger = logging.getLogger(__name__)


class ValidationAPIService:
    """Service for validation API operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def queue_contacts_for_validation(
        self, contact_ids: List[str]
    ) -> Dict:
        """
        Queue contacts for DeBounce email validation.

        This method DOES NOT perform validation - it just updates the status
        to "Queued". The background scheduler will pick up queued contacts
        and perform actual validation.

        Args:
            contact_ids: List of contact UUID strings

        Returns:
            Dict with counts of queued, already_processing, already_validated, invalid_ids
        """
        logger.info(f"📋 Queueing {len(contact_ids)} contacts for validation")

        # Convert string IDs to UUIDs
        try:
            uuid_ids = [UUID(id_str) for id_str in contact_ids]
        except ValueError as e:
            logger.error(f"Invalid UUID format: {e}")
            return {
                "success": False,
                "message": "Invalid contact ID format",
                "queued_count": 0,
                "already_processing": 0,
                "already_validated": 0,
                "invalid_ids": contact_ids,
            }

        # Get contacts
        stmt = select(Contact).where(Contact.id.in_(uuid_ids))
        result = await self.session.execute(stmt)
        contacts = list(result.scalars().all())

        # Track results
        queued = []
        already_processing = []
        already_validated = []
        found_ids = {str(c.id) for c in contacts}
        invalid_ids = set(contact_ids) - found_ids

        # Process each contact
        for contact in contacts:
            if contact.debounce_processing_status == "Processing":
                already_processing.append(contact)
                logger.debug(f"⏭️ Skipping {contact.email} - already processing")
            elif contact.debounce_validation_status == "Complete":
                already_validated.append(contact)
                logger.debug(f"⏭️ Skipping {contact.email} - already validated")
            else:
                # Queue for validation
                contact.debounce_validation_status = "Queued"
                contact.debounce_processing_status = "Queued"
                contact.retry_count = 0  # Reset retry count
                contact.next_retry_at = None  # Clear retry timestamp
                contact.updated_at = datetime.utcnow()
                queued.append(contact)
                logger.debug(f"✅ Queued {contact.email} for validation")

        # Commit changes
        await self.session.commit()

        logger.info(
            f"✅ Queue operation complete: {len(queued)} queued, "
            f"{len(already_processing)} processing, {len(already_validated)} validated, "
            f"{len(invalid_ids)} invalid"
        )

        return {
            "success": True,
            "message": f"{len(queued)} contacts queued for validation",
            "queued_count": len(queued),
            "already_processing": len(already_processing),
            "already_validated": len(already_validated),
            "invalid_ids": list(invalid_ids),
        }

    async def queue_filtered_contacts_for_validation(
        self, filters: ContactFilters, max_contacts: int = 100
    ) -> Dict:
        """
        Queue all contacts matching filters for validation.

        Args:
            filters: Contact filters (status, domain, page, search)
            max_contacts: Maximum number of contacts to queue (safety limit)

        Returns:
            Dict with counts of queued, already_processing, already_validated, total_matched
        """
        logger.info(f"📋 Queueing filtered contacts for validation (max: {max_contacts})")

        # Build query
        stmt = select(Contact)

        # Apply filters
        if filters.curation_status:
            stmt = stmt.where(Contact.curation_status == filters.curation_status)

        if filters.validation_status:
            # Map validation status to database fields
            if filters.validation_status == "valid":
                stmt = stmt.where(Contact.debounce_result == "valid")
            elif filters.validation_status == "invalid":
                stmt = stmt.where(Contact.debounce_result == "invalid")
            elif filters.validation_status == "disposable":
                stmt = stmt.where(Contact.debounce_result == "disposable")
            elif filters.validation_status == "pending":
                stmt = stmt.where(
                    Contact.debounce_processing_status.in_(["Queued", "Processing"])
                )
            elif filters.validation_status == "not_validated":
                stmt = stmt.where(
                    or_(
                        Contact.debounce_validation_status.is_(None),
                        Contact.debounce_validation_status == "New",
                    )
                )

        if filters.search_email:
            stmt = stmt.where(Contact.email.ilike(f"%{filters.search_email}%"))

        if filters.search_name:
            stmt = stmt.where(
                or_(
                    Contact.first_name.ilike(f"%{filters.search_name}%"),
                    Contact.last_name.ilike(f"%{filters.search_name}%"),
                )
            )

        if filters.domain_id:
            stmt = stmt.where(Contact.domain_id == UUID(filters.domain_id))

        if filters.page_id:
            stmt = stmt.where(Contact.page_id == UUID(filters.page_id))

        # Limit results
        stmt = stmt.limit(max_contacts)

        # Execute query
        result = await self.session.execute(stmt)
        contacts = list(result.scalars().all())

        logger.info(f"📊 Found {len(contacts)} contacts matching filters")

        # Queue contacts using same logic as queue_contacts_for_validation
        queued = []
        already_processing = []
        already_validated = []

        for contact in contacts:
            if contact.debounce_processing_status == "Processing":
                already_processing.append(contact)
            elif contact.debounce_validation_status == "Complete":
                already_validated.append(contact)
            else:
                contact.debounce_validation_status = "Queued"
                contact.debounce_processing_status = "Queued"
                contact.retry_count = 0
                contact.next_retry_at = None
                contact.updated_at = datetime.utcnow()
                queued.append(contact)

        # Commit changes
        await self.session.commit()

        logger.info(
            f"✅ Filtered queue complete: {len(queued)} queued, "
            f"{len(already_processing)} processing, {len(already_validated)} validated"
        )

        return {
            "success": True,
            "message": f"{len(queued)} contacts queued for validation",
            "queued_count": len(queued),
            "already_processing": len(already_processing),
            "already_validated": len(already_validated),
            "total_matched": len(contacts),
            "filters_applied": filters.model_dump(exclude_none=True),
        }

    async def get_validation_status(self, contact_ids: List[str]) -> Dict:
        """
        Get current validation status for specific contacts.

        Used for real-time polling by frontend.

        Args:
            contact_ids: List of contact UUID strings

        Returns:
            Dict with success and list of contact validation statuses
        """
        logger.info(f"📊 Getting validation status for {len(contact_ids)} contacts")

        # Convert string IDs to UUIDs
        try:
            uuid_ids = [UUID(id_str) for id_str in contact_ids]
        except ValueError as e:
            logger.error(f"Invalid UUID format: {e}")
            return {"success": False, "contacts": []}

        # Get contacts
        stmt = select(Contact).where(Contact.id.in_(uuid_ids))
        result = await self.session.execute(stmt)
        contacts = list(result.scalars().all())

        # Build response
        contact_statuses = []
        for contact in contacts:
            contact_statuses.append(
                {
                    "id": str(contact.id),
                    "email": contact.email or "",
                    "validation_status": contact.debounce_validation_status or "New",
                    "processing_status": contact.debounce_processing_status or "New",
                    "result": contact.debounce_result,
                    "score": contact.debounce_score,
                    "reason": contact.debounce_reason,
                    "suggestion": contact.debounce_suggestion,
                    "validated_at": contact.debounce_validated_at,
                    "error": contact.debounce_processing_error,
                }
            )

        logger.debug(f"✅ Returning status for {len(contact_statuses)} contacts")

        return {"success": True, "contacts": contact_statuses}

    async def get_validation_summary(
        self,
        domain_id: Optional[str] = None,
        page_id: Optional[str] = None,
        curation_status: Optional[str] = None,
    ) -> Dict:
        """
        Get aggregate validation statistics.

        Args:
            domain_id: Optional filter by domain UUID
            page_id: Optional filter by page UUID
            curation_status: Optional filter by curation status

        Returns:
            Dict with validation summary statistics
        """
        logger.info("📊 Calculating validation summary statistics")

        # Build base query
        stmt = select(Contact)

        # Apply filters
        if domain_id:
            stmt = stmt.where(Contact.domain_id == UUID(domain_id))
        if page_id:
            stmt = stmt.where(Contact.page_id == UUID(page_id))
        if curation_status:
            stmt = stmt.where(Contact.curation_status == curation_status)

        # Get all contacts
        result = await self.session.execute(stmt)
        contacts = list(result.scalars().all())

        # Calculate statistics
        total = len(contacts)
        validated = [
            c for c in contacts if c.debounce_validation_status == "Complete"
        ]
        valid = [c for c in validated if c.debounce_result == "valid"]
        invalid = [c for c in validated if c.debounce_result == "invalid"]
        disposable = [c for c in validated if c.debounce_result == "disposable"]
        catch_all = [c for c in validated if c.debounce_result == "catch-all"]
        unknown = [c for c in validated if c.debounce_result == "unknown"]
        not_validated = [
            c
            for c in contacts
            if not c.debounce_validation_status
            or c.debounce_validation_status == "New"
        ]
        pending = [
            c
            for c in contacts
            if c.debounce_processing_status in ["Queued", "Processing"]
        ]

        # Get last validation timestamp
        validated_timestamps = [
            c.debounce_validated_at for c in validated if c.debounce_validated_at
        ]
        last_updated = max(validated_timestamps) if validated_timestamps else datetime.utcnow()

        # Calculate percentages
        validation_rate = (len(validated) / total * 100) if total > 0 else 0
        valid_rate = (len(valid) / len(validated) * 100) if len(validated) > 0 else 0

        logger.info(
            f"✅ Summary: {len(validated)}/{total} validated ({validation_rate:.1f}%), "
            f"{len(valid)} valid ({valid_rate:.1f}%)"
        )

        return {
            "success": True,
            "summary": {
                "total_contacts": total,
                "validated": {
                    "total": len(validated),
                    "valid": len(valid),
                    "invalid": len(invalid),
                    "disposable": len(disposable),
                    "catch_all": len(catch_all),
                    "unknown": len(unknown),
                },
                "not_validated": len(not_validated),
                "pending_validation": len(pending),
                "validation_rate": round(validation_rate, 2),
                "valid_rate": round(valid_rate, 2),
                "last_updated": last_updated,
            },
            "filters_applied": {
                "domain_id": domain_id,
                "page_id": page_id,
                "curation_status": curation_status,
            },
        }
