"""
DeBounce Email Validation Service (WO-017 Phase 1)

Validates email addresses using DeBounce.io API before CRM sync.

Key Features:
- Bulk validation (up to 50 emails per request)
- Pre-CRM quality gate
- Auto-queue valid emails for CRM sync (optional)
- Exponential backoff retry logic
- SDK-compatible signature: process_batch_validation(contact_ids, session)

Architecture Pattern: WO-015/WO-016 validated pattern
DeBounce API Docs: https://debounce.io/api-documentation/
"""

import logging
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import CRMSyncStatus, CRMProcessingStatus

logger = logging.getLogger(__name__)


class DeBounceValidationService:
    """
    Service for validating email addresses using DeBounce.io API.

    Bulk validation approach:
    1. Collect batch of contacts (up to 50)
    2. Extract emails
    3. Call DeBounce bulk API
    4. Update all contacts with results
    5. Optionally auto-queue valid emails for CRM sync
    """

    def __init__(self):
        self.api_key = settings.DEBOUNCE_API_KEY
        self.base_url = settings.DEBOUNCE_API_BASE_URL
        self.batch_size = settings.DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE

    async def process_batch_validation(
        self, contact_ids: List[UUID], session: AsyncSession
    ) -> None:
        """
        Process a batch of contacts for email validation.

        SDK-compatible method signature for scheduler integration.

        Args:
            contact_ids: List of contact UUIDs to validate
            session: Async database session

        Raises:
            Exception: Re-raises all exceptions for SDK error handling
        """
        logger.info(f"🚀 Starting DeBounce validation for {len(contact_ids)} contacts")

        # Fetch all contacts in batch
        stmt = select(Contact).where(Contact.id.in_(contact_ids))
        result = await session.execute(stmt)
        contacts = list(result.scalars().all())

        if not contacts:
            logger.error("❌ No contacts found - skipping")
            return

        try:
            await self._validate_contact_batch(contacts, session)
        except Exception as e:
            logger.exception(f"❌ Failed to validate batch: {e}")
            raise  # Re-raise for SDK to handle

    async def _validate_contact_batch(
        self, contacts: List[Contact], session: AsyncSession
    ) -> None:
        """
        Core business logic to validate a batch of contacts.

        Flow:
        1. Mark all as Processing
        2. Extract emails
        3. Call DeBounce bulk API
        4. Map results back to contacts
        5. Update statuses and optionally queue for CRM
        """
        try:
            # Step 1: Mark all as Processing
            for contact in contacts:
                contact.debounce_validation_status = CRMSyncStatus.Processing.value
                contact.debounce_processing_status = CRMProcessingStatus.Processing.value
            await session.commit()

            # Step 2: Extract emails (skip contacts without email)
            email_to_contact = {}
            emails = []
            for contact in contacts:
                if contact.email:
                    email_to_contact[contact.email] = contact
                    emails.append(contact.email)
                else:
                    # No email - mark as error
                    contact.debounce_validation_status = CRMSyncStatus.Error.value
                    contact.debounce_processing_status = CRMProcessingStatus.Error.value
                    contact.debounce_processing_error = "No email address"

            if not emails:
                logger.warning("No valid emails in batch")
                await session.commit()
                return

            logger.info(f"📧 Validating {len(emails)} emails via DeBounce API")

            # Step 3: Call DeBounce bulk API
            results = await self._call_debounce_bulk_api(emails)

            # Step 4: Map results back to contacts
            for result in results:
                email = result["email"]
                contact = email_to_contact.get(email)
                if not contact:
                    continue

                # Update validation fields
                contact.debounce_result = result["result"]
                contact.debounce_score = result.get("score", 0)
                contact.debounce_reason = result.get("reason", "")[:500]
                contact.debounce_suggestion = result.get("did_you_mean", "")
                contact.debounce_validated_at = datetime.utcnow()

                # Status: Complete
                contact.debounce_validation_status = CRMSyncStatus.Complete.value
                contact.debounce_processing_status = CRMProcessingStatus.Complete.value
                contact.debounce_processing_error = None
                contact.retry_count = 0
                contact.next_retry_at = None

                logger.info(
                    f"✅ Validated {email}: {result['result']} (score: {result.get('score', 0)})"
                )

                # Step 5: Auto-queue for CRM if valid (optional)
                if settings.DEBOUNCE_AUTO_QUEUE_VALID_EMAILS:
                    await self._auto_queue_for_crm(contact, result)

            await session.commit()
            logger.info(f"✅ Batch validation complete: {len(results)} emails processed")

        except Exception as e:
            # Error handling with retry logic
            error_msg = str(e)
            logger.error(f"❌ Batch validation failed: {error_msg}")

            for contact in contacts:
                should_retry = contact.retry_count < settings.DEBOUNCE_VALIDATION_MAX_RETRIES

                if should_retry:
                    delay_minutes = self._calculate_retry_delay(contact.retry_count)
                    next_retry = datetime.utcnow() + timedelta(minutes=delay_minutes)

                    contact.debounce_validation_status = CRMSyncStatus.Queued.value
                    contact.debounce_processing_status = CRMProcessingStatus.Error.value
                    contact.debounce_processing_error = error_msg[:500]
                    contact.retry_count += 1
                    contact.next_retry_at = next_retry
                    contact.last_retry_at = datetime.utcnow()

                    logger.info(
                        f"🔄 Retry {contact.retry_count}/{settings.DEBOUNCE_VALIDATION_MAX_RETRIES} "
                        f"scheduled in {delay_minutes} minutes for {contact.email}"
                    )
                else:
                    contact.debounce_validation_status = CRMSyncStatus.Error.value
                    contact.debounce_processing_status = CRMProcessingStatus.Error.value
                    contact.debounce_processing_error = error_msg[:500]

                    logger.error(
                        f"❌ Max retries exceeded for {contact.email} - "
                        f"marking as permanent error"
                    )

            await session.commit()
            raise

    async def _call_debounce_bulk_api(self, emails: List[str]) -> List[dict]:
        """
        Call DeBounce.io bulk validation API.

        Args:
            emails: List of email addresses to validate

        Returns:
            List of validation results

        Raises:
            httpx.HTTPStatusError: If API call fails
        """
        headers = {
            "Authorization": f"api-key {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {"emails": emails}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/validate/bulk",
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                logger.error(
                    f"DeBounce API failed (HTTP {response.status_code}): {response.text}"
                )
                response.raise_for_status()

            data = response.json()
            return data.get("results", [])

    async def _auto_queue_for_crm(self, contact: Contact, validation_result: dict):
        """
        Optionally auto-queue validated emails for CRM sync.

        Rules:
        - If result = 'valid' → Queue for CRM
        - If result = 'disposable' and SKIP_DISPOSABLE → Don't queue
        - If result = 'invalid' and SKIP_INVALID → Don't queue
        - If result = 'catch-all' and !QUEUE_CATCH_ALL → Don't queue

        Args:
            contact: Contact instance
            validation_result: DeBounce validation result
        """
        result = validation_result["result"]

        # Skip disposable if configured
        if result == "disposable" and settings.DEBOUNCE_SKIP_DISPOSABLE:
            logger.info(f"⏭️ Skipping disposable email: {contact.email}")
            return

        # Skip invalid if configured
        if result == "invalid" and settings.DEBOUNCE_SKIP_INVALID:
            logger.info(f"⏭️ Skipping invalid email: {contact.email}")
            return

        # Skip catch-all if configured
        if result == "catch-all" and not settings.DEBOUNCE_QUEUE_CATCH_ALL:
            logger.info(f"⏭️ Skipping catch-all email (manual review): {contact.email}")
            return

        # Queue for CRM if valid
        if result == "valid":
            crm = settings.DEBOUNCE_AUTO_QUEUE_DEFAULT_CRM
            logger.info(f"📤 Auto-queueing {contact.email} for {crm} sync")

            # Set CRM status dynamically
            setattr(contact, f"{crm}_sync_status", CRMSyncStatus.Queued.value)
            setattr(contact, f"{crm}_processing_status", CRMProcessingStatus.Queued.value)

    def _calculate_retry_delay(self, retry_count: int) -> int:
        """
        Calculate retry delay in minutes with exponential backoff.

        Args:
            retry_count: Current retry attempt (0-indexed)

        Returns:
            Delay in minutes
        """
        base_delay = settings.DEBOUNCE_VALIDATION_RETRY_DELAY_MINUTES

        if settings.DEBOUNCE_VALIDATION_RETRY_EXPONENTIAL:
            return base_delay * (2**retry_count)
        else:
            return base_delay * (retry_count + 1)
