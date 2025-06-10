#!/usr/bin/env python3
"""
Registry Update Flag Manager Script

This script manages the 'needs_update' flag in the document registry for ScraperSky's vector database system.
It allows marking documents for re-vectorization when their content has changed but filename remains the same.
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Supabase Project ID (from persona)
SUPABASE_PROJECT_ID = "ddfldwzhdhhzhxywqnyz"  # Hardcoded from persona for direct use

class RegistryUpdateManager:
    def __init__(self, conn):
        self.conn = conn
    
    async def ensure_needs_update_column_exists(self):
        """Ensure the needs_update column exists in the document_registry table."""
        column_exists = await self.conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'document_registry' 
            AND column_name = 'needs_update'
        """)
        
        if column_exists == 0:
            logger.info("Adding needs_update column to document_registry table...")
            await self.conn.execute("""
                ALTER TABLE public.document_registry 
                ADD COLUMN needs_update BOOLEAN DEFAULT FALSE NOT NULL
            """)
            logger.info("needs_update column added successfully.")
        else:
            logger.debug("needs_update column already exists.")
    
    async def mark_document_for_update(self, document_path):
        """Mark a specific document for update by path or title."""
        await self.ensure_needs_update_column_exists()
        
        # Normalize path
        document_path = os.path.abspath(document_path)
        
        # Try to find by path first
        result = await self.conn.fetchrow("""
            UPDATE public.document_registry
            SET needs_update = TRUE
            WHERE file_path = $1
            RETURNING id, title
        """, document_path)
        
        # If not found by path, try by title (filename)
        if not result:
            document_title = os.path.basename(document_path)
            result = await self.conn.fetchrow("""
                UPDATE public.document_registry
                SET needs_update = TRUE
                WHERE title = $1
                RETURNING id, title
            """, document_title)
        
        if result:
            logger.info(f"Document '{result['title']}' (ID: {result['id']}) marked for update.")
            return True
        else:
            logger.error(f"Document not found in registry: {document_path}")
            return False
    
    async def mark_directory_for_update(self, directory_path):
        """Mark all documents in a directory for update."""
        await self.ensure_needs_update_column_exists()
        
        # Normalize path
        directory_path = os.path.abspath(directory_path)
        if not directory_path.endswith(os.sep):
            directory_path += os.sep
        
        # Use LIKE query to match all documents in this directory
        result = await self.conn.execute("""
            UPDATE public.document_registry
            SET needs_update = TRUE
            WHERE file_path LIKE $1 || '%'
        """, directory_path)
        
        # Get count of affected rows
        count = await self.conn.fetchval("""
            SELECT COUNT(*) FROM public.document_registry
            WHERE needs_update = TRUE AND file_path LIKE $1 || '%'
        """, directory_path)
        
        if count > 10:
            logger.warning(f"You've marked {count} documents for update. This may impact system performance.")
        
        logger.info(f"Marked {count} document(s) in directory '{directory_path}' for update.")
        return count
    
    async def mark_pattern_for_update(self, pattern):
        """Mark all documents matching a pattern for update."""
        await self.ensure_needs_update_column_exists()
        
        # Use LIKE query with the provided pattern
        like_pattern = f"%{pattern}%"
        
        # Update documents where title matches pattern
        result = await self.conn.execute("""
            UPDATE public.document_registry
            SET needs_update = TRUE
            WHERE title LIKE $1 OR file_path LIKE $1
        """, like_pattern)
        
        # Get count of affected rows
        count = await self.conn.fetchval("""
            SELECT COUNT(*) FROM public.document_registry
            WHERE needs_update = TRUE AND (title LIKE $1 OR file_path LIKE $1)
        """, like_pattern)
        
        if count > 10:
            logger.warning(f"You've marked {count} documents for update. This may impact system performance.")
        
        logger.info(f"Marked {count} document(s) matching pattern '{pattern}' for update.")
        return count
    
    async def list_documents_for_update(self):
        """List all documents currently marked for update."""
        await self.ensure_needs_update_column_exists()
        
        records = await self.conn.fetch("""
            SELECT id, title, file_path, embedding_status, last_checked
            FROM public.document_registry
            WHERE needs_update = TRUE
            ORDER BY title
        """)
        
        if not records:
            logger.info("No documents are currently marked for update.")
            return []
        
        print("\n=== Documents Marked for Update ===")
        print(f"{'ID':<5} | {'Title':<30} | {'Status':<15} | {'Last Checked':<20}")
        print("-" * 80)
        
        for record in records:
            last_checked = record['last_checked'].strftime('%Y-%m-%d %H:%M') if record['last_checked'] else 'Never'
            print(f"{record['id']:<5} | {record['title']:<30} | {record['embedding_status']:<15} | {last_checked:<20}")
        
        print(f"\nTotal: {len(records)} document(s) marked for update.")
        return records
    
    async def clear_update_flag(self, document_path):
        """Clear the update flag for a specific document."""
        await self.ensure_needs_update_column_exists()
        
        # Normalize path
        document_path = os.path.abspath(document_path)
        
        # Try to find by path first
        result = await self.conn.fetchrow("""
            UPDATE public.document_registry
            SET needs_update = FALSE
            WHERE file_path = $1 AND needs_update = TRUE
            RETURNING id, title
        """, document_path)
        
        # If not found by path, try by title (filename)
        if not result:
            document_title = os.path.basename(document_path)
            result = await self.conn.fetchrow("""
                UPDATE public.document_registry
                SET needs_update = FALSE
                WHERE title = $1 AND needs_update = TRUE
                RETURNING id, title
            """, document_title)
        
        if result:
            logger.info(f"Update flag cleared for document '{result['title']}' (ID: {result['id']}).")
            return True
        else:
            logger.error(f"Document not found or not marked for update: {document_path}")
            return False
    
    async def clear_all_update_flags(self):
        """Clear update flags for all documents."""
        await self.ensure_needs_update_column_exists()
        
        # Get count before clearing
        count = await self.conn.fetchval("""
            SELECT COUNT(*) FROM public.document_registry
            WHERE needs_update = TRUE
        """)
        
        # Clear all flags
        await self.conn.execute("""
            UPDATE public.document_registry
            SET needs_update = FALSE
            WHERE needs_update = TRUE
        """)
        
        logger.info(f"Cleared update flags for {count} document(s).")
        return count

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Manage the 'needs_update' flag in the document registry for re-vectorization"
    )
    parser.add_argument('--mark-for-update', help='Mark a specific document for update by path or title')
    parser.add_argument('--mark-directory-for-update', help='Mark all documents in a directory for update')
    parser.add_argument('--mark-pattern-for-update', help='Mark documents matching a pattern for update')
    parser.add_argument('--list-updates', action='store_true', help='List documents currently marked for update')
    parser.add_argument('--clear-update', help='Clear update flag for a specific document')
    parser.add_argument('--clear-all-updates', action='store_true', help='Clear update flags for all documents')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    conn = None  # Initialize conn to None for the finally block
    try:
        # Connect to the database
        # Setting statement_cache_size=0 to fix pgbouncer compatibility issue
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        manager = RegistryUpdateManager(conn)
        
        if args.mark_for_update:
            await manager.mark_document_for_update(args.mark_for_update)
        
        if args.mark_directory_for_update:
            count = await manager.mark_directory_for_update(args.mark_directory_for_update)
            if count > 10:
                confirm = input(f"You're about to mark {count} documents for update. Continue? (y/n): ")
                if confirm.lower() != 'y':
                    logger.info("Operation cancelled.")
                    await manager.clear_all_update_flags()
        
        if args.mark_pattern_for_update:
            count = await manager.mark_pattern_for_update(args.mark_pattern_for_update)
            if count > 10:
                confirm = input(f"You're about to mark {count} documents for update. Continue? (y/n): ")
                if confirm.lower() != 'y':
                    logger.info("Operation cancelled.")
                    await manager.clear_all_update_flags()
        
        if args.list_updates:
            await manager.list_documents_for_update()
        
        if args.clear_update:
            await manager.clear_update_flag(args.clear_update)
        
        if args.clear_all_updates:
            count = await manager.clear_all_update_flags()
            if count > 0:
                logger.info(f"Successfully cleared update flags for {count} document(s).")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
    finally:
        if conn is not None:
            await conn.close()
            logger.debug("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
