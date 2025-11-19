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

    async def process_single_contact(
        self, contact_id: UUID, session: AsyncSession
    ) -> None:
        """
        Process a single contact for email validation.

        SDK-compatible method signature: (contact_id: UUID, session: AsyncSession)
        Called by scheduler via run_job_loop pattern.

        This is the entry point called by the SDK scheduler. It delegates to
        the batch validation method with a single contact.

        Args:
            contact_id: Contact UUID to validate
            session: Async database session (managed by SDK)

        Raises:
            Exception: Re-raises any exceptions for SDK to handle
        """
        logger.info(f"🚀 Starting DeBounce validation for contact {contact_id}")

        # Delegate to batch validation with single contact
        await self.process_batch_validation([contact_id], session)

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

            # Step 3: Call DeBounce API (sequential validation)
            results = await self._call_debounce_api(emails)

            # Step 4: Map results back to contacts
            for result in results:
                email = result["email"]
                contact = email_to_contact.get(email)
                if not contact:
                    continue

                # Check if this email had an error
                if "error" in result:
                    contact.debounce_validation_status = CRMSyncStatus.Error.value
                    contact.debounce_processing_status = CRMProcessingStatus.Error.value
                    contact.debounce_processing_error = result["error"][:500]
                    logger.error(f"❌ Failed to validate {email}: {result['error']}")
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

    async def _call_debounce_api(self, emails: List[str]) -> List[dict]:
        """
        Call DeBounce.io real-time lookup API for each email.

        DeBounce does NOT have a bulk endpoint. We validate emails sequentially
        to respect the 5 concurrent call limit.

        Args:
            emails: List of email addresses to validate

        Returns:
            List of validation results in standardized format

        Raises:
            httpx.HTTPStatusError: If API call fails
        """
        results = []

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for email in emails:
                try:
                    # DeBounce API uses query parameters for auth and email
                    params = {"api": self.api_key, "email": email}

                    # GET request (not POST)
                    response = await client.get(
                        self.base_url, params=params, timeout=30.0
                    )

                    if response.status_code == 401:
                        logger.error("❌ Invalid DeBounce API key")
                        raise ValueError("Invalid DeBounce API key")

                    if response.status_code == 402:
                        logger.error("❌ DeBounce credits exhausted")
                        raise ValueError("DeBounce validation credits finished")

                    if response.status_code == 429:
                        logger.warning("⚠️ DeBounce rate limit exceeded - will retry")
                        raise ValueError("DeBounce rate limit exceeded")

                    if response.status_code != 200:
                        logger.error(
                            f"DeBounce API failed for {email} (HTTP {response.status_code}): {response.text}"
                        )
                        response.raise_for_status()

                    data = response.json()

                    # Check if request was successful
                    if data.get("success") == "1":
                        debounce_data = data.get("debounce", {})

                        # Map DeBounce response to our format
                        result = {
                            "email": email,
                            "result": self._map_debounce_result(
                                debounce_data.get("result")
                            ),
                            "score": self._calculate_score(debounce_data),
                            "reason": debounce_data.get("reason", ""),
                            "did_you_mean": debounce_data.get("did_you_mean", ""),
                            "code": debounce_data.get("code"),
                            "role": debounce_data.get("role") == "true",
                            "free_email": debounce_data.get("free_email") == "true",
                            "send_transactional": debounce_data.get(
                                "send_transactional"
                            )
                            == "1",
                        }
                        results.append(result)
                        logger.info(f"✅ Validated {email}: {result['result']}")
                    else:
                        # API returned success=0
                        error_msg = data.get("debounce", {}).get(
                            "error", "Unknown error"
                        )
                        logger.error(f"❌ DeBounce API error for {email}: {error_msg}")
                        results.append({"email": email, "error": error_msg})

                except Exception as e:
                    logger.error(f"❌ Failed to validate {email}: {e}")
                    results.append({"email": email, "error": str(e)})

        return results

    def _map_debounce_result(self, debounce_result: str) -> str:
        """
        Map DeBounce result strings to our standardized format.

        DeBounce Results:
        - "Safe to Send" → "valid"
        - "Deliverable" → "valid"
        - "Invalid" → "invalid"
        - "Risky" → "catch-all" or "unknown"
        - "Unknown" → "unknown"
        - "Disposable" → "disposable"

        Args:
            debounce_result: DeBounce result string

        Returns:
            Standardized result string
        """
        result_lower = (debounce_result or "").lower()

        if "safe" in result_lower or "deliverable" in result_lower:
            return "valid"
        elif "invalid" in result_lower:
            return "invalid"
        elif "risky" in result_lower:
            return "catch-all"
        elif "disposable" in result_lower:
            return "disposable"
        else:
            return "unknown"

    def _calculate_score(self, debounce_data: dict) -> int:
        """
        Calculate a 0-100 score from DeBounce data.

        DeBounce provides a "code" (string) and other indicators.
        We convert this to a 0-100 scale.

        Code meanings (from DeBounce API documentation):
        - 5: Safe to Send (100)
        - 4: Deliverable (90)
        - 3: Risky (50)
        - 2: Unknown (30)
        - 1: Invalid (10)
        - 0: Invalid (0)
        - 7: Role-based email (60) - info@, contact@, etc. (send_transactional=1)

        Args:
            debounce_data: DeBounce API response data

        Returns:
            Score from 0-100
        """
        try:
            code = int(debounce_data.get("code", 0))
        except (ValueError, TypeError):
            code = 0

        score_map = {
            5: 100,  # Safe to Send
            4: 90,   # Deliverable
            3: 50,   # Risky
            2: 30,   # Unknown
            1: 10,   # Invalid
            0: 0,    # Invalid
            7: 60,   # Role-based email (safe for transactional)
        }

        return score_map.get(code, 0)

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
