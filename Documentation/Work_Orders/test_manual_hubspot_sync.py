#!/usr/bin/env python3
"""
Manual test script for HubSpot sync core service.
Tests Step 1 (core service) independently of scheduler.

Usage:
    python test_manual_hubspot_sync.py <contact_id>

Example:
    python test_manual_hubspot_sync.py 12345678-1234-1234-1234-123456789abc
"""

import asyncio
import logging
import sys
from uuid import UUID

from src.services.crm.hubspot_sync_service import HubSpotSyncService
from src.session.async_session import get_db_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_manual_sync(contact_id: str):
    """Manually sync one contact to HubSpot."""
    try:
        contact_uuid = UUID(contact_id)
    except ValueError:
        logger.error(f"❌ Invalid UUID: {contact_id}")
        return False

    service = HubSpotSyncService()

    if not service.api_key:
        logger.error("❌ HUBSPOT_API_KEY not configured in .env!")
        logger.error("   Set HUBSPOT_API_KEY to your HubSpot private app token")
        logger.error("   Example: HUBSPOT_API_KEY=pat-na1-xxxxx")
        return False

    logger.info(f"🧪 Starting manual sync test for contact: {contact_id}")
    logger.info(f"📡 HubSpot API Base URL: {service.base_url}")
    logger.info(f"🔑 API Key configured: {service.api_key[:15]}...")

    async for session in get_db_session():
        try:
            await service.process_single_contact(contact_uuid, session)
            logger.info("✅ MANUAL SYNC COMPLETED SUCCESSFULLY!")
            return True
        except Exception as e:
            logger.exception(f"❌ MANUAL SYNC FAILED: {e}")
            return False


def print_verification_queries(contact_id: str):
    """Print SQL queries for verifying sync results."""
    print("\n" + "=" * 80)
    print("VERIFICATION QUERIES (Run in MCP Supabase):")
    print("=" * 80)
    print(
        f"""
-- Check contact status after sync:
SELECT
    id,
    email,
    name,
    hubspot_sync_status,
    hubspot_processing_status,
    hubspot_processing_error,
    hubspot_contact_id,
    retry_count,
    updated_at
FROM contacts
WHERE id = '{contact_id}';

-- Expected if successful:
-- hubspot_sync_status: 'Complete'
-- hubspot_processing_status: 'Complete'
-- hubspot_processing_error: NULL
-- hubspot_contact_id: numeric ID (e.g., '12345678901')
-- retry_count: 0

-- Check HubSpot contact in dashboard:
-- 1. Go to https://app.hubspot.com/
-- 2. Navigate to Contacts → All Contacts
-- 3. Search for the email address
-- 4. Verify contact details and custom properties
"""
    )
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_manual_hubspot_sync.py <contact_id>")
        print()
        print("Example:")
        print(
            "  python test_manual_hubspot_sync.py 12345678-1234-1234-1234-123456789abc"
        )
        sys.exit(1)

    contact_id = sys.argv[1]
    success = asyncio.run(test_manual_sync(contact_id))

    if success:
        print_verification_queries(contact_id)

    sys.exit(0 if success else 1)
