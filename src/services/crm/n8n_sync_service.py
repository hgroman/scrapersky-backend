"""
n8n Webhook Integration Service (WO-020)

Handles sending contact data to n8n webhook for external enrichment processing.
This is a fire-and-forget integration that pushes contacts to n8n workflows.

Architecture: SDK-compatible service for use with run_job_loop pattern.
Pattern Reference: src/services/crm/brevo_sync_service.py

Note: This service only sends data to n8n. Receiving enriched data back
is handled by a separate endpoint (future work order).
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.settings import settings
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import CRMSyncStatus, CRMProcessingStatus

logger = logging.getLogger(__name__)


class N8nSyncService:
    """Service for sending contacts to n8n webhook for enrichment"""

    def __init__(self):
        self.webhook_url = settings.N8N_WEBHOOK_URL
        self.webhook_secret = settings.N8N_WEBHOOK_SECRET

        if not self.webhook_url:
            logger.warning("⚠️ N8N_WEBHOOK_URL not configured - n8n sync will fail")

    async def process_single_contact(
        self, contact_id: UUID, session: AsyncSession
    ) -> None:
        """
        Process a single contact for n8n webhook sync.

        SDK-compatible method signature: (contact_id: UUID, session: AsyncSession)
        Called by scheduler via run_job_loop pattern.

        This is the entry point called by the SDK scheduler. It fetches the contact
        and delegates to the core webhook send logic.

        Args:
            contact_id: Contact UUID to process
            session: Async database session (managed by SDK)

        Raises:
            Exception: Re-raises any exceptions for SDK to handle
        """
        logger.info(f"🚀 Starting n8n webhook send for contact {contact_id}")

        # Fetch contact from database
        stmt = select(Contact).where(Contact.id == contact_id)
        result = await session.execute(stmt)
        contact = result.scalar_one_or_none()

        if not contact:
            logger.error(f"❌ Contact {contact_id} not found - skipping")
            return

        try:
            # Core webhook send logic
            await self._send_contact_to_webhook(contact, session)

        except Exception as e:
            logger.exception(f"❌ Failed to send contact {contact_id} to n8n: {e}")
            # Re-raise for SDK to handle (will mark as failed)
            raise

    async def _send_contact_to_webhook(
        self, contact: Contact, session: AsyncSession
    ) -> None:
        """
        Core business logic to send one contact to n8n webhook.

        Handles:
        - Validation
        - Status transitions (Processing → Complete/Error)
        - Webhook POST
        - Retry logic with exponential backoff
        - Error tracking

        Args:
            contact: Contact model instance
            session: Async database session

        Note: This method does NOT raise exceptions - it handles all errors
        internally and updates contact status accordingly.
        """
        logger.info(f"📧 Sending contact {contact.email} to n8n webhook")

        try:
            # Validate contact has email
            if not contact.email:
                raise ValueError("Contact has no email address")

            # Status: Processing
            contact.n8n_sync_status = CRMSyncStatus.Processing.value
            contact.n8n_processing_status = CRMProcessingStatus.Processing.value
            await session.commit()  # Immediate visibility

            # Call n8n webhook
            await self._post_to_webhook(contact)

            # Status: Complete
            contact.n8n_sync_status = CRMSyncStatus.Complete.value
            contact.n8n_processing_status = CRMProcessingStatus.Complete.value
            contact.n8n_processing_error = None
            contact.retry_count = 0  # Reset retry count
            contact.next_retry_at = None
            contact.last_failed_crm = None

            await session.commit()
            logger.info(f"✅ Successfully sent {contact.email} to n8n webhook")

        except Exception as e:
            error_msg = str(e)
            logger.exception(f"❌ n8n webhook send failed for {contact.email}: {error_msg}")

            # Retry logic
            should_retry = contact.retry_count < settings.N8N_SYNC_MAX_RETRIES

            if should_retry:
                # Calculate exponential backoff delay
                delay_minutes = self._calculate_retry_delay(contact.retry_count)
                next_retry = datetime.utcnow() + timedelta(minutes=delay_minutes)

                # Status: Queued for retry (with Error processing status)
                contact.n8n_sync_status = CRMSyncStatus.Queued.value
                contact.n8n_processing_status = CRMProcessingStatus.Error.value
                contact.n8n_processing_error = error_msg[:500]  # Truncate
                contact.retry_count += 1
                contact.last_retry_at = datetime.utcnow()
                contact.next_retry_at = next_retry
                contact.last_failed_crm = "n8n"

                logger.info(
                    f"🔄 Scheduled retry {contact.retry_count}/{settings.N8N_SYNC_MAX_RETRIES} "
                    f"for {contact.email} at {next_retry} (in {delay_minutes} minutes)"
                )
            else:
                # Status: Error (max retries exceeded)
                contact.n8n_sync_status = CRMSyncStatus.Error.value
                contact.n8n_processing_status = CRMProcessingStatus.Error.value
                contact.n8n_processing_error = error_msg[:500]
                contact.last_failed_crm = "n8n"

                logger.error(
                    f"❌ Max retries ({settings.N8N_SYNC_MAX_RETRIES}) exceeded for {contact.email}"
                )

            await session.commit()

    async def _post_to_webhook(self, contact: Contact) -> None:
        """
        POST contact data to n8n webhook.

        Args:
            contact: Contact model instance

        Raises:
            httpx.HTTPError: If webhook request fails
            ValueError: If webhook returns non-success status
        """
        # Build webhook payload
        payload = {
            "contact_id": str(contact.id),
            "email": contact.email,
            "name": contact.name,
            "scrapersky_domain_id": str(contact.domain_id) if contact.domain_id else None,
            "scrapersky_page_id": str(contact.page_id) if contact.page_id else None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Build headers
        headers = {"Content-Type": "application/json"}
        if self.webhook_secret:
            headers["Authorization"] = f"Bearer {self.webhook_secret}"

        logger.info(f"📤 POSTing to n8n webhook: {self.webhook_url}")
        logger.debug(f"Payload: {payload}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )

                # Check response status
                if response.status_code not in [200, 201, 202]:
                    raise ValueError(
                        f"Webhook returned non-success status: {response.status_code} - {response.text}"
                    )

                logger.info(
                    f"✅ Webhook accepted contact {contact.email} (HTTP {response.status_code})"
                )

            except httpx.TimeoutException:
                raise ValueError("Webhook request timed out after 30 seconds")
            except httpx.HTTPError as e:
                raise ValueError(f"Webhook HTTP error: {str(e)}")

    def _calculate_retry_delay(self, retry_count: int) -> int:
        """
        Calculate exponential backoff delay in minutes.

        Args:
            retry_count: Current retry attempt (0-indexed)

        Returns:
            Delay in minutes

        Examples:
            Retry 0 → 5 minutes
            Retry 1 → 10 minutes
            Retry 2 → 20 minutes
            Retry 3 → 40 minutes
            Retry 4 → 80 minutes (capped at 120)
        """
        base_delay = 5  # Start with 5 minutes
        max_delay = 120  # Cap at 2 hours
        delay = base_delay * (2**retry_count)
        return min(delay, max_delay)
