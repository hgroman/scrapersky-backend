"""
HubSpot Contact Sync Service (WO-016 Phase 1)

Synchronizes ScraperSky contacts to HubSpot CRM using HubSpot API v3.

Key Features:
- 2-step upsert pattern (search → create/update)
- Exponential backoff retry logic
- Custom property mapping (domain_id, page_id)
- SDK-compatible signature: process_single_contact(contact_id, session)

Architecture Pattern: WO-015 (Brevo) validated pattern
HubSpot API Docs: https://developers.hubspot.com/docs/api/crm/contacts
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import CRMProcessingStatus, CRMSyncStatus

logger = logging.getLogger(__name__)


class HubSpotSyncService:
    """
    Service for syncing contacts to HubSpot CRM.

    Follows 2-step upsert pattern:
    1. Search for contact by email
    2. Create new contact OR update existing contact

    This is required because HubSpot API doesn't have built-in upsert like Brevo.
    """

    def __init__(self):
        self.api_key = settings.HUBSPOT_API_KEY
        self.base_url = settings.HUBSPOT_API_BASE_URL
        self.portal_id = settings.HUBSPOT_PORTAL_ID

        # Custom property names
        self.prop_domain_id = settings.HUBSPOT_CUSTOM_PROPERTY_DOMAIN_ID
        self.prop_page_id = settings.HUBSPOT_CUSTOM_PROPERTY_PAGE_ID
        self.prop_sync_date = settings.HUBSPOT_CUSTOM_PROPERTY_SYNC_DATE

    async def process_single_contact(
        self, contact_id: UUID, session: AsyncSession
    ) -> None:
        """
        Process a single contact for HubSpot sync.

        SDK-compatible method signature: (contact_id: UUID, session: AsyncSession)
        Called by scheduler via run_job_loop pattern.

        Args:
            contact_id: UUID of contact to sync
            session: Async database session

        Raises:
            Exception: Re-raises all exceptions for SDK error handling
        """
        logger.info(f"🚀 Starting HubSpot sync for contact {contact_id}")

        # Fetch contact from database
        stmt = select(Contact).where(Contact.id == contact_id)
        result = await session.execute(stmt)
        contact = result.scalar_one_or_none()

        if not contact:
            logger.error(f"❌ Contact {contact_id} not found - skipping")
            return

        try:
            await self._sync_contact_to_hubspot(contact, session)
        except Exception as e:
            logger.exception(f"❌ Failed to sync contact {contact_id}: {e}")
            raise  # Re-raise for SDK to handle

    async def _sync_contact_to_hubspot(
        self, contact: Contact, session: AsyncSession
    ) -> None:
        """
        Core business logic to sync one contact to HubSpot.

        Flow:
        1. Validate contact has email
        2. Set status to Processing
        3. Search for existing contact in HubSpot
        4. Create new OR update existing contact
        5. Set status to Complete (or Error with retry)

        Args:
            contact: Contact model instance
            session: Async database session
        """
        try:
            # Validation
            if not contact.email:
                raise ValueError("Contact has no email address")

            # Status: Processing
            contact.hubspot_sync_status = CRMSyncStatus.Processing.value
            contact.hubspot_processing_status = CRMProcessingStatus.Processing.value
            await session.commit()

            logger.info(f"📧 Syncing {contact.email} to HubSpot")

            # Call HubSpot API (2-step upsert)
            hubspot_contact_id = await self._upsert_contact_to_hubspot(contact)

            # Status: Complete
            contact.hubspot_sync_status = CRMSyncStatus.Complete.value
            contact.hubspot_processing_status = CRMProcessingStatus.Complete.value
            contact.hubspot_processing_error = None
            contact.hubspot_contact_id = hubspot_contact_id
            contact.retry_count = 0
            contact.next_retry_at = None
            await session.commit()

            logger.info(
                f"✅ HubSpot sync complete for {contact.email} "
                f"(HubSpot ID: {hubspot_contact_id})"
            )

        except Exception as e:
            # Error handling with retry logic
            error_msg = str(e)
            logger.error(f"❌ HubSpot sync failed for {contact.email}: {error_msg}")

            should_retry = contact.retry_count < settings.HUBSPOT_SYNC_MAX_RETRIES

            if should_retry:
                # Calculate next retry time with exponential backoff
                delay_minutes = self._calculate_retry_delay(contact.retry_count)
                next_retry = datetime.utcnow() + timedelta(minutes=delay_minutes)

                contact.hubspot_sync_status = CRMSyncStatus.Queued.value
                contact.hubspot_processing_status = CRMProcessingStatus.Error.value
                contact.hubspot_processing_error = error_msg[:500]
                contact.retry_count += 1
                contact.next_retry_at = next_retry
                contact.last_retry_at = datetime.utcnow()
                contact.last_failed_crm = "hubspot"

                logger.info(
                    f"🔄 Retry {contact.retry_count}/{settings.HUBSPOT_SYNC_MAX_RETRIES} "
                    f"scheduled in {delay_minutes} minutes for {contact.email}"
                )
            else:
                # Max retries exceeded - permanent error
                contact.hubspot_sync_status = CRMSyncStatus.Error.value
                contact.hubspot_processing_status = CRMProcessingStatus.Error.value
                contact.hubspot_processing_error = error_msg[:500]
                contact.last_failed_crm = "hubspot"

                logger.error(
                    f"❌ Max retries exceeded for {contact.email} - "
                    f"marking as permanent error"
                )

            await session.commit()
            raise  # Re-raise for SDK

    async def _upsert_contact_to_hubspot(self, contact: Contact) -> str:
        """
        2-step upsert: Search for existing contact, then create or update.

        HubSpot doesn't have built-in upsert, so we must:
        1. Search for contact by email
        2. If found: Update existing contact
        3. If not found: Create new contact

        Args:
            contact: Contact model instance

        Returns:
            HubSpot contact ID (numeric string like "12345678901")

        Raises:
            httpx.HTTPStatusError: If API call fails
            ValueError: If response is invalid
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Search for existing contact by email
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": contact.email,
                            }
                        ]
                    }
                ],
                "properties": ["email", "firstname", "lastname", "phone"],
            }

            search_response = await client.post(
                f"{self.base_url}/crm/v3/objects/contacts/search",
                headers=headers,
                json=search_payload,
            )

            if search_response.status_code != 200:
                logger.error(
                    f"HubSpot search failed (HTTP {search_response.status_code}): "
                    f"{search_response.text}"
                )
                search_response.raise_for_status()

            search_data = search_response.json()
            existing_contact_id = None

            if search_data.get("total", 0) > 0:
                existing_contact_id = search_data["results"][0]["id"]
                logger.info(f"📋 Found existing HubSpot contact: {existing_contact_id}")

            # Step 2: Build properties object
            properties = self._build_contact_properties(contact)

            # Step 3: Create or Update
            if existing_contact_id:
                # Update existing contact
                update_response = await client.patch(
                    f"{self.base_url}/crm/v3/objects/contacts/{existing_contact_id}",
                    headers=headers,
                    json={"properties": properties},
                )

                if update_response.status_code not in [200, 204]:
                    logger.error(
                        f"HubSpot update failed (HTTP {update_response.status_code}): "
                        f"{update_response.text}"
                    )
                    update_response.raise_for_status()

                logger.info(f"✅ Updated HubSpot contact {existing_contact_id}")
                return existing_contact_id

            else:
                # Create new contact
                create_response = await client.post(
                    f"{self.base_url}/crm/v3/objects/contacts",
                    headers=headers,
                    json={"properties": properties},
                )

                if create_response.status_code != 201:
                    logger.error(
                        f"HubSpot create failed (HTTP {create_response.status_code}): "
                        f"{create_response.text}"
                    )
                    create_response.raise_for_status()

                create_data = create_response.json()
                new_contact_id = create_data["id"]
                logger.info(f"✅ Created new HubSpot contact {new_contact_id}")
                return new_contact_id

    def _build_contact_properties(self, contact: Contact) -> dict:
        """
        Build HubSpot properties object from ScraperSky contact.

        Maps ScraperSky fields to HubSpot properties:
        - contact.email → email
        - contact.name → firstname/lastname (split on space)
        - contact.phone_number → phone
        - contact.domain_id → scrapersky_domain_id (custom property)
        - contact.page_id → scrapersky_page_id (custom property)

        Args:
            contact: Contact model instance

        Returns:
            Dictionary of HubSpot properties
        """
        properties = {
            "email": contact.email,
        }

        # Split name into firstname/lastname
        if contact.name:
            name_parts = contact.name.strip().split(maxsplit=1)
            properties["firstname"] = name_parts[0]
            if len(name_parts) > 1:
                properties["lastname"] = name_parts[1]

        # Phone number
        if contact.phone_number:
            properties["phone"] = contact.phone_number

        # Custom ScraperSky properties (must be pre-created in HubSpot)
        if contact.domain_id:
            properties[self.prop_domain_id] = str(contact.domain_id)

        if contact.page_id:
            properties[self.prop_page_id] = str(contact.page_id)

        # Sync timestamp
        properties[self.prop_sync_date] = datetime.utcnow().isoformat()

        return properties

    def _calculate_retry_delay(self, retry_count: int) -> int:
        """
        Calculate retry delay in minutes with exponential backoff.

        Exponential backoff formula: base_delay * 2^retry_count
        - Retry 1: 5 minutes
        - Retry 2: 10 minutes
        - Retry 3: 20 minutes

        Linear fallback: base_delay * (retry_count + 1)

        Args:
            retry_count: Current retry attempt (0-indexed)

        Returns:
            Delay in minutes
        """
        base_delay = settings.HUBSPOT_SYNC_RETRY_DELAY_MINUTES

        if settings.HUBSPOT_SYNC_RETRY_EXPONENTIAL:
            return base_delay * (2**retry_count)
        else:
            return base_delay * (retry_count + 1)
