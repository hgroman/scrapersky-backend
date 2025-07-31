#!/usr/bin/env python3
"""
Vector Database Cleanup Manager Script

This script compares the document registry with the vector database (project_docs table)
and identifies/removes entries that should no longer be in the vector database.
"""

import os
import sys
import asyncio
import asyncpg
import argparse
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Supabase Project ID (from persona)
SUPABASE_PROJECT_ID = "ddfldwzhdhhzhxywqnyz"  # Hardcoded from persona for direct use


class VectorDBCleanupManager:
    def __init__(self, conn):
        self.conn = conn

    async def get_archived_in_registry_for_cleanup(self):
        """
        Identifies documents in project_docs that correspond to entries marked 'archived'
        in the document_registry. These are candidates for cleanup.
        """
        records = await self.conn.fetch("""
            SELECT pd.id, pd.title, dr.file_path as registry_file_path
            FROM project_docs pd
            JOIN document_registry dr ON pd.id = dr.id 
            WHERE dr.embedding_status = 'archived'
            ORDER BY pd.id
        """)
        return records

    async def list_cleanup_candidates(self):
        """List vector DB entries that are marked as 'archived' in the registry."""
        candidates = await self.get_archived_in_registry_for_cleanup()

        if not candidates:
            logger.info(
                "No vector DB entries found corresponding to 'archived' documents in the registry."
            )
            return []

        print(
            "\n=== Vector DB Entries Marked for Cleanup (Status 'archived' in Registry) ==="
        )
        print(f"{'Vector DB ID':<15} | {'Title':<70} | {'Registry Path':<70}")
        print("-" * 160)

        for record in candidates:
            print(
                f"{record['id']:<15} | {record['title']:<70} | {record['registry_file_path']:<70}"
            )

        print(f"\nTotal: {len(candidates)} entry/entries eligible for cleanup.")
        return candidates

    async def remove_vector_entry(self, entry_id):
        """Remove a specific entry from the project_docs table by its ID."""
        result = await self.conn.fetchrow(
            """
            DELETE FROM project_docs
            WHERE id = $1
            RETURNING id, title
        """,
            entry_id,
        )

        if result:
            logger.info(
                f"Entry '{result['title']}' (Vector DB ID: {result['id']}) removed from the vector database."
            )
            return True
        else:
            logger.error(
                f"Entry with Vector DB ID {entry_id} not found in the vector database."
            )
            return False

    async def remove_archived_from_vector_db(self, auto_approve=False):
        """
        Removes entries from project_docs if their corresponding entry in document_registry
        has embedding_status = 'archived'.
        """
        candidates = await self.get_archived_in_registry_for_cleanup()

        if not candidates:
            logger.info(
                "No vector DB entries to remove based on 'archived' status in registry."
            )
            return 0

        print("\n=== Cleaning Up Vector DB Entries (Status 'archived' in Registry) ===")
        print(f"{'Vector DB ID':<15} | {'Title':<70} | {'Registry Path':<70}")
        print("-" * 160)

        for record in candidates:
            print(
                f"{record['id']:<15} | {record['title']:<70} | {record['registry_file_path']:<70}"
            )

        print(f"\nFound {len(candidates)} entries to remove from the vector database.")

        if not auto_approve:
            confirm = input(
                f"Are you sure you want to remove these {len(candidates)} entries? (y/n): "
            )
            if confirm.lower() != "y":
                logger.info("Operation cancelled by user.")
                return 0
        else:
            logger.info("Auto-approving removal of entries.")

        removed_count = 0
        for record in candidates:
            success = await self.remove_vector_entry(record["id"])
            if success:
                removed_count += 1

        logger.info(
            f"Successfully removed {removed_count} out of {len(candidates)} targeted entries from the vector database."
        )
        return removed_count


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Vector Database Cleanup Manager - Removes entries from vector DB if marked 'archived' in registry."
    )
    parser.add_argument(
        "action",
        choices=["list_candidates", "cleanup"],
        help=(
            "Action to perform: "
            "'list_candidates' - Show vector DB entries corresponding to 'archived' registry items. "
            "'cleanup' - Remove these entries from the vector DB."
        ),
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve removals for the 'cleanup' action (use with caution).",
    )

    args = parser.parse_args()

    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable not set.")
        sys.exit(1)

    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        manager = VectorDBCleanupManager(conn)

        if args.action == "list_candidates":
            await manager.list_cleanup_candidates()
        elif args.action == "cleanup":
            await manager.remove_archived_from_vector_db(auto_approve=args.auto_approve)

    except asyncpg.exceptions.PostgresConnectionError as e:
        logger.error(f"Database connection failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        if conn:
            await conn.close()
            logger.debug("Database connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
