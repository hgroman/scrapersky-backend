#!/usr/bin/env python3
"""
Registry Orphan Detector Script

Identifies and lists entries in the project_docs (vector) table that do not have
a corresponding valid entry in the document_registry table based on their id.
These are considered "orphaned" vector embeddings.
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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

class OrphanDetector:
    def __init__(self, conn):
        self.conn = conn

    async def detect_orphans(self):
        """Detects and lists orphaned entries in project_docs."""
        logger.info("Detecting orphaned entries in project_docs...")
        try:
            orphans = await self.conn.fetch("""
                SELECT pd.id, pd.title
                FROM project_docs pd
                LEFT JOIN document_registry dr ON pd.id = dr.id
                WHERE dr.id IS NULL
                ORDER BY pd.id;
            """)

            if orphans:
                logger.info(f"Found {len(orphans)} orphaned entries in project_docs:")
                print("\n=== Detected Orphaned Vector DB Entries ===")
                header = "Vector DB ID | Title                              "
                print(header)
                print("-" * len(header))
                for orphan in orphans:
                    # Ensure title is not excessively long for display
                    title_display = (orphan['title'][:35] + '...') if orphan['title'] and len(orphan['title']) > 38 else orphan['title']
                    print(f"{orphan['id']:<12} | {title_display:<35}")
                print("\n")
            else:
                logger.info("No orphaned entries found in project_docs.")
            
            return orphans
        except Exception as e:
            logger.error(f"An error occurred while detecting orphans: {e}")
            return []

async def main():
    parser = argparse.ArgumentParser(description="Detects orphaned entries in the vector database (project_docs).")
    # No arguments needed for detection itself, but parser is good for consistency
    args = parser.parse_args()

    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        detector = OrphanDetector(conn)
        await detector.detect_orphans()
    except Exception as e:
        logger.error(f"Failed to connect to the database or run detection: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
