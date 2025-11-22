"""
WO-021: n8n Enrichment Service

Service for processing enriched contact data received from n8n workflows.
Handles validation, idempotency, and updating contact records with enrichment results.
"""

import logging
from uuid import UUID
from typing import Dict, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.wf7_contact import Contact
from src.schemas.n8n_enrichment_schemas import (
    EnrichmentCompleteRequest,
    EnrichedData,
    EnrichmentMetadata,
)

logger = logging.getLogger(__name__)


class N8nEnrichmentService:
    """Service for processing enriched data from n8n workflows"""

    async def process_enrichment(
        self, payload: EnrichmentCompleteRequest, session: AsyncSession
    ) -> Dict:
        """
        Process enriched data from n8n and update contact record.

        Steps:
        1. Validate contact exists
        2. Check idempotency (already processed this enrichment_id?)
        3. Update enriched data fields
        4. Update enrichment status
        5. Return success response

        Args:
            payload: Enrichment data from n8n
            session: Database session

        Returns:
            Dict with success status, contact_id, enrichment_id, message, updated_fields

        Raises:
            ValueError: If contact not found or validation fails
        """
        logger.info(
            f"📥 Processing enrichment for contact {payload.contact_id}, "
            f"enrichment_id: {payload.enrichment_id}, status: {payload.status}"
        )

        # Step 1: Validate contact exists
        contact = await self._validate_contact(payload.contact_id, session)

        # Step 2: Check idempotency
        if await self._check_idempotency(contact, payload.enrichment_id):
            logger.info(
                f"⏭️ Enrichment {payload.enrichment_id} already processed for contact {contact.id} - skipping"
            )
            return {
                "success": True,
                "contact_id": str(contact.id),
                "enrichment_id": payload.enrichment_id,
                "message": "Enrichment already processed (idempotent)",
                "updated_fields": [],
            }

        # Step 3: Update enriched data fields
        updated_fields = await self._update_enriched_data(
            contact, payload.enriched_data, session
        )

        # Step 4: Update enrichment status
        await self._update_enrichment_status(
            contact, payload.status, payload.enrichment_id, payload.metadata, session
        )

        # Step 5: Commit changes
        await session.commit()
        await session.refresh(contact)

        logger.info(
            f"✅ Enrichment complete for contact {contact.id}. "
            f"Updated {len(updated_fields)} fields: {updated_fields}"
        )

        return {
            "success": True,
            "contact_id": str(contact.id),
            "enrichment_id": payload.enrichment_id,
            "message": "Enrichment data saved successfully",
            "updated_fields": updated_fields,
        }

    async def _validate_contact(self, contact_id: str, session: AsyncSession) -> Contact:
        """
        Fetch and validate contact exists.

        Args:
            contact_id: UUID string of contact
            session: Database session

        Returns:
            Contact object

        Raises:
            ValueError: If contact not found or invalid UUID
        """
        try:
            contact_uuid = UUID(contact_id)
        except ValueError as e:
            logger.error(f"❌ Invalid contact UUID: {contact_id}")
            raise ValueError(f"Invalid contact_id format: {contact_id}") from e

        stmt = select(Contact).where(Contact.id == contact_uuid)
        result = await session.execute(stmt)
        contact = result.scalar_one_or_none()

        if not contact:
            logger.error(f"❌ Contact not found: {contact_uuid}")
            raise ValueError(f"Contact not found: {contact_id}")

        logger.info(f"✅ Contact validated: {contact.email} ({contact.id})")
        return contact

    async def _check_idempotency(self, contact: Contact, enrichment_id: str) -> bool:
        """
        Check if this enrichment_id was already processed.

        Prevents duplicate processing if n8n retries the webhook.

        Args:
            contact: Contact object
            enrichment_id: Unique enrichment run ID

        Returns:
            True if already processed, False otherwise
        """
        if contact.last_enrichment_id == enrichment_id:
            logger.info(
                f"🔄 Idempotency check: enrichment_id {enrichment_id} already processed"
            )
            return True

        return False

    async def _update_enriched_data(
        self,
        contact: Contact,
        enriched_data: Optional[EnrichedData],
        session: AsyncSession,
    ) -> List[str]:
        """
        Update contact with enriched data fields.

        Only updates fields that are provided (not None).
        Returns list of updated field names.

        Args:
            contact: Contact object to update
            enriched_data: Enriched data from n8n (may be None for failed enrichments)
            session: Database session

        Returns:
            List of field names that were updated
        """
        updated_fields = []

        if not enriched_data:
            logger.info("⚠️ No enriched_data provided - skipping field updates")
            return updated_fields

        # Update phone
        if enriched_data.phone is not None:
            contact.enriched_phone = enriched_data.phone
            updated_fields.append("enriched_phone")
            logger.debug(f"📞 Updated phone: {enriched_data.phone}")

        # Update address
        if enriched_data.address is not None:
            contact.enriched_address = enriched_data.address.model_dump(exclude_none=True)
            updated_fields.append("enriched_address")
            logger.debug(f"📍 Updated address: {enriched_data.address.city}, {enriched_data.address.state}")

        # Update social profiles
        if enriched_data.social_profiles is not None:
            contact.enriched_social_profiles = enriched_data.social_profiles.model_dump(
                exclude_none=True
            )
            updated_fields.append("enriched_social_profiles")
            logger.debug(f"👥 Updated social profiles")

        # Update company
        if enriched_data.company is not None:
            contact.enriched_company = enriched_data.company.model_dump(exclude_none=True)
            updated_fields.append("enriched_company")
            logger.debug(f"🏢 Updated company: {enriched_data.company.name}")

        # Update additional emails
        if enriched_data.additional_emails is not None:
            contact.enriched_additional_emails = enriched_data.additional_emails
            updated_fields.append("enriched_additional_emails")
            logger.debug(f"📧 Updated additional emails: {len(enriched_data.additional_emails)} found")

        # Update confidence score
        if enriched_data.confidence_score is not None:
            contact.enrichment_confidence_score = enriched_data.confidence_score
            updated_fields.append("enrichment_confidence_score")
            logger.debug(f"📊 Confidence score: {enriched_data.confidence_score}%")

        # Update sources
        if enriched_data.sources is not None:
            contact.enrichment_sources = enriched_data.sources
            updated_fields.append("enrichment_sources")
            logger.debug(f"🔍 Sources: {enriched_data.sources}")

        logger.info(f"✅ Updated {len(updated_fields)} enriched data fields")
        return updated_fields

    async def _update_enrichment_status(
        self,
        contact: Contact,
        status: str,
        enrichment_id: str,
        metadata: Optional[EnrichmentMetadata],
        session: AsyncSession,
    ) -> None:
        """
        Update enrichment status fields.

        Args:
            contact: Contact object to update
            status: Enrichment status (complete/partial/failed)
            enrichment_id: Unique enrichment run ID
            metadata: Enrichment metadata (duration, api calls, cost)
            session: Database session
        """
        # Update status
        contact.enrichment_status = status
        contact.enrichment_completed_at = datetime.utcnow()
        contact.last_enrichment_id = enrichment_id

        # Update metadata if provided
        if metadata:
            if metadata.enrichment_duration_seconds is not None:
                contact.enrichment_duration_seconds = metadata.enrichment_duration_seconds

            if metadata.api_calls_made is not None:
                contact.enrichment_api_calls = metadata.api_calls_made

            if metadata.cost_estimate is not None:
                contact.enrichment_cost_estimate = metadata.cost_estimate

            logger.debug(
                f"📈 Metadata: {metadata.enrichment_duration_seconds}s, "
                f"{metadata.api_calls_made} API calls, "
                f"${metadata.cost_estimate:.4f} cost"
            )

        logger.info(f"✅ Status updated to: {status}")
