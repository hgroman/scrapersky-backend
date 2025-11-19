#!/usr/bin/env python3
"""
Manual test script for DeBounce validation service (WO-017 Phase 1)

Usage:
    python test_manual_debounce.py <contact_id> [<contact_id2> ...]

Example:
    python test_manual_debounce.py 123e4567-e89b-12d3-a456-426614174000

This script:
1. Validates one or more contacts using DeBounce.io API
2. Updates database with validation results
3. Optionally auto-queues valid emails for CRM sync (if configured)
"""

import asyncio
import sys
from uuid import UUID
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.services.email_validation.debounce_service import DeBounceValidationService
from src.session.async_session import get_session
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_manual_validation(contact_ids: list):
    """
    Manually validate contacts using DeBounce service.

    Args:
        contact_ids: List of contact UUID strings

    Returns:
        bool: True if validation succeeded, False otherwise
    """
    try:
        contact_uuids = [UUID(id) for id in contact_ids]
    except ValueError as e:
        logger.error(f"❌ Invalid UUID format: {e}")
        return False

    service = DeBounceValidationService()

    if not service.api_key:
        logger.error("❌ DEBOUNCE_API_KEY not configured in .env!")
        logger.error("   Please add: DEBOUNCE_API_KEY=db_xxxxxxxx")
        return False

    logger.info(f"📧 Preparing to validate {len(contact_uuids)} contact(s)")

    async with get_session() as session:
        try:
            await service.process_batch_validation(contact_uuids, session)
            logger.info("✅ VALIDATION COMPLETED SUCCESSFULLY!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Check contact records in database for validation results")
            logger.info("2. Review debounce_result, debounce_score, and debounce_validated_at fields")
            if service.api_key:
                logger.info("3. Valid emails may have been auto-queued for CRM sync (check settings)")
            return True
        except Exception as e:
            logger.exception(f"❌ VALIDATION FAILED: {e}")
            logger.error("")
            logger.error("Troubleshooting:")
            logger.error("- Verify DEBOUNCE_API_KEY is valid")
            logger.error("- Check that contact IDs exist in database")
            logger.error("- Ensure contacts have valid email addresses")
            logger.error("- Review DeBounce API quota (free tier: 100 validations)")
            return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: No contact IDs provided")
        print("")
        print("Usage: python test_manual_debounce.py <contact_id> [<contact_id2> ...]")
        print("")
        print("Example:")
        print("  python test_manual_debounce.py 123e4567-e89b-12d3-a456-426614174000")
        print("")
        print("Multiple contacts:")
        print("  python test_manual_debounce.py UUID1 UUID2 UUID3")
        sys.exit(1)

    contact_ids = sys.argv[1:]
    success = asyncio.run(test_manual_validation(contact_ids))
    sys.exit(0 if success else 1)
