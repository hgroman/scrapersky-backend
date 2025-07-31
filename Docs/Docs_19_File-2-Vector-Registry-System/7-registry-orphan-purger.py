#!/usr/bin/env python3
"""
Registry Orphan Purger Script

Removes orphaned entries from the project_docs (vector) table.
Orphans are entries in project_docs that do not have a corresponding
valid entry in the document_registry table based on their id.
"""

import os
import sys
import asyncio
import asyncpg
import argparse
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set.")
    sys.exit(1)


class OrphanPurger:
    def __init__(self, conn):
        self.conn = conn

    async def get_orphans(self):
        """Retrieves a list of orphaned entries from project_docs."""
        try:
            orphans = await self.conn.fetch("""
                SELECT pd.id, pd.title
                FROM project_docs pd
                LEFT JOIN document_registry dr ON pd.id = dr.id
                WHERE dr.embedding_status != 'active' OR dr.id IS NULL
                ORDER BY pd.id;
            """)
            return orphans
        except Exception as e:
            logger.error(f"An error occurred while fetching orphans: {e}")
            return []

    async def purge_orphans(self, auto_approve=False):
        """Purges orphaned entries from project_docs after confirmation."""
        orphans = await self.get_orphans()

        if not orphans:
            logger.info("No orphaned entries found in project_docs to purge.")
            return

        logger.info(
            f"Found {len(orphans)} orphaned entries in project_docs scheduled for purging:"
        )
        print("\n=== Detected Orphaned Vector DB Entries for Purging ===")
        header = "Vector DB ID | Title                              "
        print(header)
        print("-" * len(header))
        for orphan in orphans:
            title_display = (
                (orphan["title"][:35] + "...")
                if orphan["title"] and len(orphan["title"]) > 38
                else orphan["title"]
            )
            print(f"{orphan['id']:<12} | {title_display:<35}")
        print("\n")

        if not auto_approve:
            confirm = input(
                f"Are you sure you want to PERMANENTLY DELETE these {len(orphans)} entries from project_docs? [y/N]: "
            )
            if confirm.lower() != "y":
                logger.info("Purge operation cancelled by user.")
                return

        logger.info("Proceeding with purging orphaned entries...")
        deleted_count = 0
        async with self.conn.transaction():
            for orphan in orphans:
                try:
                    await self.conn.execute(
                        "DELETE FROM project_docs WHERE id = $1", orphan["id"]
                    )
                    logger.info(
                        f"Successfully deleted orphan with ID {orphan['id']} ('{orphan['title']}') from project_docs."
                    )
                    deleted_count += 1
                except Exception as e:
                    logger.error(
                        f"Failed to delete orphan with ID {orphan['id']} ('{orphan['title']}'): {e}"
                    )

        logger.info(
            f"Successfully purged {deleted_count} out of {len(orphans)} targeted orphaned entries."
        )


async def main():
    parser = argparse.ArgumentParser(
        description="Purges orphaned entries from the vector database (project_docs)."
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve the purge operation without interactive confirmation.",
    )
    args = parser.parse_args()

    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        purger = OrphanPurger(conn)
        await purger.purge_orphans(auto_approve=args.auto_approve)
    except Exception as e:
        logger.error(f"Failed to connect to the database or run purge: {e}")
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
