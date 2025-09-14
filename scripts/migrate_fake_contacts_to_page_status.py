#!/usr/bin/env python3
"""
Migration Script: Convert Fake Contact Records to Page Status
Migrates fake "notfound_*" contact records to contact_scrape_status on pages table.

Usage: python scripts/migrate_fake_contacts_to_page_status.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, delete, func

from src.db.session import get_db_session
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.page import Page
from src.models.enums import ContactScrapeStatus


async def migrate_fake_contacts():
    """
    1. Find all fake contact records (email LIKE 'notfound_%@%')
    2. Extract page_id from each fake contact
    3. Update corresponding page.contact_scrape_status = 'NoContactFound'
    4. Report results (NO DELETION until verified)
    """

    async for session in get_db_session():
        try:
            print("Starting fake contact migration...")

            # Find all fake contact records
            fake_contacts_query = select(Contact).where(
                Contact.email.like('notfound_%@%')
            )
            result = await session.execute(fake_contacts_query)
            fake_contacts = result.scalars().all()

            if not fake_contacts:
                print("No fake contact records found.")
                return

            print(f"Found {len(fake_contacts)} fake contact records to migrate")

            # Group by page_id
            page_ids_to_update = set()

            for contact in fake_contacts:
                page_ids_to_update.add(contact.page_id)
                print(f"  - Page {contact.page_id}: {contact.email}")

            print(f"\nUpdating {len(page_ids_to_update)} pages to 'NoContactFound' status...")

            # Update pages in batches
            batch_size = 100
            page_id_list = list(page_ids_to_update)

            for i in range(0, len(page_id_list), batch_size):
                batch = page_id_list[i:i + batch_size]

                # Get pages in this batch
                pages_query = select(Page).where(Page.id.in_(batch))
                pages_result = await session.execute(pages_query)
                pages = pages_result.scalars().all()

                # Update contact_scrape_status
                for page in pages:
                    page.contact_scrape_status = ContactScrapeStatus.NoContactFound.value

                print(f"  Updated batch {i//batch_size + 1}: {len(pages)} pages")

            # Commit page updates
            await session.commit()
            print("✅ Page status updates committed")

            print("\n🛑 STOPPING HERE - No contacts deleted yet")
            print("   Verify page statuses before running deletion script")

            # Verification queries
            print("\nVerification:")

            # Count remaining fake contacts
            remaining_fake = await session.execute(
                select(func.count(Contact.id)).where(Contact.email.like('notfound_%@%'))
            )
            fake_count = remaining_fake.scalar()

            # Count pages with NoContactFound status
            updated_pages = await session.execute(
                select(func.count(Page.id)).where(Page.contact_scrape_status == ContactScrapeStatus.NoContactFound.value)
            )
            no_contact_count = updated_pages.scalar()

            print(f"  - Remaining fake contacts: {fake_count}")
            print(f"  - Pages with 'NoContactFound' status: {no_contact_count}")

            if no_contact_count > 0:
                print("✅ Page status migration completed successfully!")
                print(f"📋 Next step: Verify {no_contact_count} pages have correct status, then run deletion script")
            else:
                print("⚠️  Warning: No pages were updated")

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            await session.rollback()
            raise

        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(migrate_fake_contacts())