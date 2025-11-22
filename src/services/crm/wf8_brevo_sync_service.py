# WF8 – The Connector
# Purpose: Contact validation, enrichment, and delivery to external systems
# NEVER put page-scraping logic here – that belongs in WF7

"""
WO-015: Brevo CRM Integration Service

WHAT THIS DOES:
Synchronizes ScraperSky contacts to Brevo CRM using their REST API.
Implements the Dual-Status Adapter Pattern for reliable, retryable CRM sync.

PURPOSE:
Send validated contact data to Brevo for email marketing campaigns and CRM management.

THE DUAL-STATUS PATTERN (Critical Architecture):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status Tracking (2 fields):
  • brevo_sync_status (CRMSyncStatus) - User selection: New/Selected/Queued/Complete/Error/Skipped
  • brevo_processing_status (CRMProcessingStatus) - System state: NULL/Queued/Processing/Complete/Error

Retry Fields (3 fields):
  • retry_count (int) - Number of retry attempts (max 3)
  • next_retry_at (timestamp) - When to retry failed syncs
  • brevo_processing_error (text) - Error message for debugging

Metadata (1 field):
  • brevo_contact_id (varchar) - Brevo's ID for the contact (returned from API)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WORKFLOW:
1. Scheduler queries contacts WHERE brevo_processing_status = 'Queued'
2. Service fetches contact and validates required fields (email, first_name, last_name)
3. Service calls Brevo API: POST /v3/contacts (upsert via updateEnabled=true)
4. On success: Set brevo_sync_status='Complete', brevo_processing_status='Complete'
5. On failure: Increment retry_count, set next_retry_at with exponential backoff (5→10→20 min)
6. After 3 failures: Set brevo_sync_status='Error', stop retrying

SCHEDULER CONFIGURATION:
• Interval: 1 minute (dev) / 5 minutes (prod)
• Batch size: 10 contacts per cycle
• Environment variable: BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES

BREVO API DETAILS:
• Endpoint: POST https://api.brevo.com/v3/contacts
• Authentication: api-key header (BREVO_API_KEY)
• Upsert: updateEnabled=true (creates or updates by email)
• List assignment: Uses BREVO_LIST_ID for contact organization
• Rate limit: 10 requests/second (handled by batch size)

EXAMPLE PAYLOAD:
{
  "email": "contact@example.com",
  "attributes": {
    "FIRSTNAME": "John",
    "LASTNAME": "Doe",
    "DOMAIN_ID": "uuid-string",
    "PAGE_ID": "uuid-string"
  },
  "listIds": [123],
  "updateEnabled": true
}

RETRY LOGIC (Exponential Backoff):
• Attempt 1 fails → retry in 5 minutes
• Attempt 2 fails → retry in 10 minutes  
• Attempt 3 fails → retry in 20 minutes
• After 3 attempts → mark as Error, stop retrying

RELATED FILES:
• Scheduler: src/services/crm/brevo_sync_scheduler.py
• Model: src/models/WF7_V2_L1_1of1_ContactModel.py (brevo_* fields)
• Enums: src/models/enums.py (CRMSyncStatus, CRMProcessingStatus)
• Docs: Documentation/Guides/brevo_crm_user_guide.md
• Docs: Documentation/Operations/brevo_crm_maintenance.md

MAINTENANCE:
• Check logs: docker logs scraper-sky-backend-scrapersky-1 | grep -i brevo
• Monitor success: SELECT COUNT(*) FROM contacts WHERE brevo_sync_status='Complete' AND updated_at > NOW() - INTERVAL '24 hours'
• Check failures: SELECT email, brevo_processing_error, retry_count FROM contacts WHERE brevo_sync_status='Error'
• Reset failed: UPDATE contacts SET brevo_processing_status='Queued', retry_count=0 WHERE brevo_sync_status='Error'

IMPLEMENTED: 2025-11-15 (WO-015 Phase 2)
API DOCS: https://developers.brevo.com/reference/createcontact
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.settings import settings
from src.models.wf8_contact import Contact
from src.models.enums import CRMSyncStatus, CRMProcessingStatus

logger = logging.getLogger(__name__)


class BrevoSyncService:
    """Service for syncing contacts to Brevo CRM"""

    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.list_id = settings.BREVO_LIST_ID
        self.base_url = settings.BREVO_API_BASE_URL

        if not self.api_key:
            logger.warning("⚠️ BREVO_API_KEY not configured - Brevo sync will fail")

    async def process_single_contact(
        self, contact_id: UUID, session: AsyncSession
    ) -> None:
        """
        Process a single contact for Brevo sync.

        SDK-compatible method signature: (contact_id: UUID, session: AsyncSession)
        Called by scheduler via run_job_loop pattern.

        This is the entry point called by the SDK scheduler. It fetches the contact
        and delegates to the core sync logic.

        Args:
            contact_id: Contact UUID to process
            session: Async database session (managed by SDK)

        Raises:
            Exception: Re-raises any exceptions for SDK to handle
        """
        logger.info(f"🚀 Starting Brevo sync for contact {contact_id}")

        # Fetch contact from database
        stmt = select(Contact).where(Contact.id == contact_id)
        result = await session.execute(stmt)
        contact = result.scalar_one_or_none()

        if not contact:
            logger.error(f"❌ Contact {contact_id} not found - skipping")
            return

        try:
            # Core sync logic
            await self._sync_contact_to_brevo(contact, session)

        except Exception as e:
            logger.exception(f"❌ Failed to sync contact {contact_id}: {e}")
            # Re-raise for SDK to handle (will mark as failed)
            raise

    async def _sync_contact_to_brevo(
        self, contact: Contact, session: AsyncSession
    ) -> None:
        """
        Core business logic to sync one contact to Brevo.

        Handles:
        - Validation
        - Status transitions (Processing → Complete/Error)
        - API call
        - Retry logic with exponential backoff
        - Error tracking

        Args:
            contact: Contact model instance
            session: Async database session

        Note: This method does NOT raise exceptions - it handles all errors
        internally and updates contact status accordingly.
        """
        logger.info(f"📧 Processing Brevo sync for {contact.email}")

        try:
            # Validate contact has email
            if not contact.email:
                raise ValueError("Contact has no email address")

            # Status: Processing
            contact.brevo_sync_status = CRMSyncStatus.Processing.value
            contact.brevo_processing_status = CRMProcessingStatus.Processing.value
            await session.commit()  # Immediate visibility

            # Call Brevo API
            brevo_contact_id = await self._call_brevo_api(contact)

            # Status: Complete
            contact.brevo_sync_status = CRMSyncStatus.Complete.value
            contact.brevo_processing_status = CRMProcessingStatus.Complete.value
            contact.brevo_processing_error = None
            contact.brevo_contact_id = brevo_contact_id
            contact.retry_count = 0  # Reset retry count
            contact.next_retry_at = None
            contact.last_failed_crm = None

            await session.commit()
            logger.info(f"✅ Successfully synced {contact.email} to Brevo")

        except Exception as e:
            error_msg = str(e)
            logger.exception(f"❌ Brevo sync failed for {contact.email}: {error_msg}")

            # Retry logic
            should_retry = contact.retry_count < settings.BREVO_SYNC_MAX_RETRIES

            if should_retry:
                # Calculate exponential backoff delay
                delay_minutes = self._calculate_retry_delay(contact.retry_count)
                next_retry = datetime.utcnow() + timedelta(minutes=delay_minutes)

                # Status: Queued for retry (with Error processing status)
                contact.brevo_sync_status = CRMSyncStatus.Queued.value
                contact.brevo_processing_status = CRMProcessingStatus.Error.value
                contact.brevo_processing_error = error_msg[:500]  # Truncate
                contact.retry_count += 1
                contact.last_retry_at = datetime.utcnow()
                contact.next_retry_at = next_retry
                contact.last_failed_crm = "brevo"

                logger.info(
                    f"🔄 Scheduled retry {contact.retry_count}/{settings.BREVO_SYNC_MAX_RETRIES} "
                    f"for {contact.email} at {next_retry} (in {delay_minutes} minutes)"
                )
            else:
                # Status: Error (max retries exceeded)
                contact.brevo_sync_status = CRMSyncStatus.Error.value
                contact.brevo_processing_status = CRMProcessingStatus.Error.value
                contact.brevo_processing_error = (
                    f"Max retries exceeded ({settings.BREVO_SYNC_MAX_RETRIES}). "
                    f"Last error: {error_msg[:400]}"
                )
                contact.last_failed_crm = "brevo"

                logger.error(
                    f"💀 Contact {contact.email} failed after {contact.retry_count} retries. "
                    f"Marked as Error."
                )

            await session.commit()
            # Don't re-raise - let processing continue for other contacts

    def _calculate_retry_delay(self, retry_count: int) -> int:
        """
        Calculate retry delay with exponential backoff.

        Examples (base=5 minutes):
        - Retry 0 (1st retry): 5 minutes  (5 * 2^0 = 5)
        - Retry 1 (2nd retry): 10 minutes (5 * 2^1 = 10)
        - Retry 2 (3rd retry): 20 minutes (5 * 2^2 = 20)

        Args:
            retry_count: Number of retries so far (0-indexed)

        Returns:
            Delay in minutes
        """
        base_delay = settings.BREVO_SYNC_RETRY_DELAY_MINUTES

        if settings.BREVO_SYNC_RETRY_EXPONENTIAL:
            # Exponential backoff: base * 2^retry_count
            return base_delay * (2**retry_count)
        else:
            # Linear backoff: base * (retry_count + 1)
            return base_delay * (retry_count + 1)

    async def _call_brevo_api(self, contact: Contact) -> str:
        """
        Make HTTP request to Brevo API to create/update contact.

        API Documentation: https://developers.brevo.com/reference/createcontact

        Endpoint: POST /v3/contacts
        Authentication: api-key header

        Response Codes:
        - 201: Contact created
        - 204: Contact updated (already exists)
        - 400: Bad request (invalid data)
        - 401: Unauthorized (invalid API key)
        - 429: Too many requests (rate limit)

        Args:
            contact: Contact model instance

        Returns:
            Brevo contact ID (email address - Brevo uses email as primary key)

        Raises:
            ValueError: If BREVO_API_KEY not configured or API returns 400
            httpx.HTTPError: If API request fails (timeout, network error, etc.)
        """
        if not self.api_key:
            raise ValueError("BREVO_API_KEY not configured")

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Build Brevo contact payload
        payload = {
            "email": contact.email,
            "attributes": {},
            "updateEnabled": True,  # Idempotent: update if contact already exists
        }

        # Optional: Name (split into FIRSTNAME/LASTNAME)
        if contact.name:
            name_parts = contact.name.strip().split(maxsplit=1)
            payload["attributes"]["FIRSTNAME"] = name_parts[0]
            if len(name_parts) > 1:
                payload["attributes"]["LASTNAME"] = name_parts[1]

        # Optional: Phone number (Brevo uses SMS attribute)
        if contact.phone_number:
            payload["attributes"]["SMS"] = contact.phone_number

        # Custom ScraperSky attributes (stored in Brevo contact attributes)
        if contact.domain_id:
            payload["attributes"]["DOMAIN_ID"] = str(contact.domain_id)
        if contact.page_id:
            payload["attributes"]["PAGE_ID"] = str(contact.page_id)
        if contact.email_type:
            payload["attributes"]["EMAIL_TYPE"] = contact.email_type
        if contact.source_url:
            payload["attributes"]["SOURCE_URL"] = contact.source_url
        if contact.has_gmail is not None:
            payload["attributes"]["HAS_GMAIL"] = str(contact.has_gmail)

        # Optional: Add to Brevo list
        if self.list_id:
            try:
                payload["listIds"] = [int(self.list_id)]
            except ValueError:
                logger.warning(
                    f"⚠️ Invalid BREVO_LIST_ID: {self.list_id} - "
                    f"syncing without list assignment"
                )

        logger.debug(f"📤 Brevo API payload: {payload}")

        # Make HTTP request
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/contacts",
                headers=headers,
                json=payload,
            )

            # Success: 201 (created) or 204 (updated)
            if response.status_code in [201, 204]:
                logger.debug(
                    f"📥 Brevo API response: {response.status_code} - "
                    f"Contact {'created' if response.status_code == 201 else 'updated'}"
                )
                return contact.email  # Brevo uses email as contact ID

            # Bad request (invalid data)
            if response.status_code == 400:
                try:
                    error_detail = response.json().get("message", response.text)
                except Exception:
                    error_detail = response.text
                raise ValueError(f"Brevo API error (400): {error_detail}")

            # Other HTTP errors (401, 429, 500, etc.)
            response.raise_for_status()

            # Fallback (shouldn't reach here)
            logger.warning(
                f"⚠️ Unexpected Brevo API response: {response.status_code} - {response.text}"
            )
            return contact.email
