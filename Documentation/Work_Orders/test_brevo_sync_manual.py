"""
Manual test script for Brevo sync service (WO-015 Phase 2 Step 1)

Usage:
    python test_brevo_sync_manual.py <contact_id>

Example:
    python test_brevo_sync_manual.py 123e4567-e89b-12d3-a456-426614174000
"""

import sys
import asyncio
import logging
from uuid import UUID

# Add project root to path
sys.path.insert(0, "/home/user/scrapersky-backend")

from src.services.crm.brevo_sync_service import BrevoSyncService
from src.db.session import get_db_session

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_sync_single_contact(contact_id: str):
    """
    Test syncing a single contact to Brevo.

    Args:
        contact_id: UUID of contact to sync
    """
    try:
        contact_uuid = UUID(contact_id)
    except ValueError:
        logger.error(f"❌ Invalid UUID: {contact_id}")
        return False

    logger.info("=" * 80)
    logger.info(f"🧪 MANUAL BREVO SYNC TEST - Contact: {contact_uuid}")
    logger.info("=" * 80)

    # Initialize service
    service = BrevoSyncService()

    # Check API key configured
    if not service.api_key:
        logger.error("❌ BREVO_API_KEY not configured in .env!")
        logger.error("   Please add BREVO_API_KEY to your .env file")
        return False

    logger.info(f"✅ Brevo API Key: {'*' * 10}{service.api_key[-4:]}")
    logger.info(f"✅ Brevo Base URL: {service.base_url}")
    if service.list_id:
        logger.info(f"✅ Brevo List ID: {service.list_id}")
    else:
        logger.info("ℹ️  Brevo List ID: Not set (contacts will sync without list)")

    # Get database session
    async for session in get_db_session():
        try:
            logger.info("\n" + "-" * 80)
            logger.info("🚀 Starting sync process...")
            logger.info("-" * 80 + "\n")

            # Call the service (this is what the scheduler will call)
            await service.process_single_contact(contact_uuid, session)

            logger.info("\n" + "-" * 80)
            logger.info("✅ SYNC COMPLETED SUCCESSFULLY!")
            logger.info("-" * 80)
            logger.info("\nNext steps:")
            logger.info("1. Check database for updated status (see below)")
            logger.info("2. Check Brevo dashboard for new contact")
            logger.info("3. Run database verification query\n")

            return True

        except Exception as e:
            logger.error("\n" + "-" * 80)
            logger.error("❌ SYNC FAILED!")
            logger.error("-" * 80)
            logger.exception(f"Error: {e}")
            logger.error("\nTroubleshooting:")
            logger.error("1. Check BREVO_API_KEY is valid")
            logger.error("2. Check contact exists in database")
            logger.error("3. Check contact has valid email address")
            logger.error("4. Check network connectivity to Brevo API\n")
            return False


def print_verification_queries(contact_id: str):
    """Print SQL queries for manual verification"""
    print("\n" + "=" * 80)
    print("DATABASE VERIFICATION QUERIES")
    print("=" * 80 + "\n")

    print("-- Query 1: Check contact status")
    print(
        f"""
SELECT
    id,
    email,
    name,
    brevo_sync_status,
    brevo_processing_status,
    brevo_processing_error,
    brevo_contact_id,
    retry_count,
    next_retry_at
FROM contacts
WHERE id = '{contact_id}';
"""
    )

    print("\n-- Expected result after successful sync:")
    print(
        """
brevo_sync_status:       'Complete'  ✅
brevo_processing_status: 'Complete'  ✅
brevo_processing_error:  NULL        ✅
brevo_contact_id:        '<email>'   ✅
retry_count:             0           ✅
next_retry_at:           NULL        ✅
"""
    )

    print("\n-- Query 2: Check all Brevo-synced contacts")
    print(
        """
SELECT
    COUNT(*) as total_complete,
    COUNT(CASE WHEN brevo_processing_status = 'Error' THEN 1 END) as total_errors
FROM contacts
WHERE brevo_sync_status != 'New';
"""
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_brevo_sync_manual.py <contact_id>")
        print("\nExample:")
        print(
            "  python test_brevo_sync_manual.py 123e4567-e89b-12d3-a456-426614174000"
        )
        sys.exit(1)

    contact_id = sys.argv[1]

    # Run test
    success = asyncio.run(test_sync_single_contact(contact_id))

    # Print verification queries
    print_verification_queries(contact_id)

    # Exit code
    sys.exit(0 if success else 1)
