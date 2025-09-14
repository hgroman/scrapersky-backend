#!/usr/bin/env python3
"""
Quick Fix Script: Populate Contact source_url from Pages
Updates existing contact records with the correct source_url from their linked page.

Usage: python scripts/populate_contact_source_urls.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from src.db.session import get_db_session
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.page import Page


async def populate_contact_urls():
    """
    Update all contacts with missing source_url by fetching from their linked page.
    """

    async for session in get_db_session():
        try:
            print("Populating contact source URLs from pages...")

            # Find contacts with missing or empty source_url
            contacts_query = select(Contact).where(
                (Contact.source_url.is_(None)) | (Contact.source_url == '')
            )
            result = await session.execute(contacts_query)
            contacts = result.scalars().all()

            if not contacts:
                print("All contacts already have source URLs populated.")
                return

            print(f"Found {len(contacts)} contacts missing source URLs")

            updated_count = 0

            for contact in contacts:
                # Get the linked page
                page_query = select(Page).where(Page.id == contact.page_id)
                page_result = await session.execute(page_query)
                page = page_result.scalar_one_or_none()

                if page and page.url:
                    # Update contact with page URL
                    contact.source_url = page.url
                    updated_count += 1
                    print(f"  Updated contact {contact.id}: {contact.email} -> {page.url}")
                elif page:
                    print(f"  Warning: Page {contact.page_id} has no URL")
                else:
                    print(f"  Error: Page {contact.page_id} not found for contact {contact.id}")

            # Commit all updates
            await session.commit()
            print(f"✅ Updated {updated_count} contact records with source URLs")

            # Verification
            remaining_empty = await session.execute(
                select(func.count(Contact.id)).where(
                    (Contact.source_url.is_(None)) | (Contact.source_url == '')
                )
            )
            empty_count = remaining_empty.scalar()

            print(f"\nVerification:")
            print(f"  - Contacts with empty source_url: {empty_count}")
            print(f"  - Contacts updated: {updated_count}")

            if empty_count == 0:
                print("🎉 All contacts now have source URLs!")

        except Exception as e:
            print(f"❌ Error during URL population: {e}")
            await session.rollback()
            raise

        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(populate_contact_urls())