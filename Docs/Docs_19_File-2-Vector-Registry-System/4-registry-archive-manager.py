#!/usr/bin/env python3
"""
Registry Archive Manager Script

This script identifies and manages documents in the registry that no longer exist at their specified file paths.
It allows users to review missing files and mark them as "archived" in the document registry.
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

class RegistryArchiveManager:
    def __init__(self, conn):
        self.conn = conn
    
    async def find_missing_files(self):
        """Find files in the registry that no longer exist at their specified paths."""
        script_path = Path(__file__).resolve()
        # Project root is three levels up from this script's location
        # .../scraper-sky-backend/Docs/Docs_19_File-2-Vector-Registry-System/4-registry-archive-manager.py
        # -> .../scraper-sky-backend/Docs/Docs_19_File-2-Vector-Registry-System/
        # -> .../scraper-sky-backend/Docs/
        # -> .../scraper-sky-backend/ (project root)
        project_root = script_path.parent.parent.parent

        records = await self.conn.fetch("""
            SELECT id, title, file_path, embedding_status
            FROM document_registry
            WHERE embedding_status NOT IN ('archived', 'orphan')
            ORDER BY title
        """)
        
        missing_files = []
        for record in records:
            relative_db_path = record['file_path']
            if not relative_db_path: # Skip if path is empty or None
                logger.warning(f"Record ID {record['id']} ('{record['title']}') has empty file_path, skipping.")
                continue
            
            # Construct absolute path from project_root and the relative path from DB
            absolute_file_path = project_root / relative_db_path
            
            if not absolute_file_path.exists():
                missing_files.append(record)
            elif not absolute_file_path.is_file():
                logger.warning(f"Path exists but is not a file for '{record['title']}': {absolute_file_path}")
        
        return missing_files
    
    async def list_missing_files(self):
        """List files that no longer exist at their specified paths."""
        missing_files = await self.find_missing_files()
        
        if not missing_files:
            logger.info("No missing files found in the registry.")
            return []
        
        print("\n=== Missing Files in Registry ===")
        print(f"{'ID':<5} | {'Title':<30} | {'Status':<15} | {'Path':<50}")
        print("-" * 100)
        
        for record in missing_files:
            print(f"{record['id']:<5} | {record['title']:<30} | {record['embedding_status']:<15} | {record['file_path']:<50}")
        
        print(f"\nTotal: {len(missing_files)} missing file(s).")
        return missing_files
    
    async def interactive_scan(self):
        """Scan for missing files and interactively mark them as archived."""
        missing_files = await self.find_missing_files()
        
        if not missing_files:
            logger.info("No missing files found in the registry.")
            return
        
        print("\n=== Missing Files in Registry ===")
        print(f"{'#':<3} | {'ID':<5} | {'Title':<30} | {'Status':<15}")
        print("-" * 60)
        
        for i, record in enumerate(missing_files, 1):
            print(f"{i:<3} | {record['id']:<5} | {record['title']:<30} | {record['embedding_status']:<15}")
        
        print(f"\nTotal: {len(missing_files)} missing file(s).")
        
        # Interactive mode
        while True:
            choice = input("\nOptions:\n"
                          "1. Mark all as archived\n"
                          "2. Mark specific files as archived (comma-separated numbers)\n"
                          "3. Exit without changes\n"
                          "Enter choice (1-3): ")
            
            if choice == '1':
                confirm = input(f"Are you sure you want to mark ALL {len(missing_files)} files as archived? (y/n): ")
                if confirm.lower() == 'y':
                    for record in missing_files:
                        await self.mark_file_as_archived(record['id'])
                    logger.info(f"Marked {len(missing_files)} files as archived.")
                break
            
            elif choice == '2':
                selections = input("Enter file numbers to mark as archived (comma-separated, e.g., 1,3,5): ")
                try:
                    selected_indices = [int(x.strip()) for x in selections.split(',')]
                    for idx in selected_indices:
                        if 1 <= idx <= len(missing_files):
                            await self.mark_file_as_archived(missing_files[idx-1]['id'])
                            logger.info(f"Marked file {missing_files[idx-1]['title']} as archived.")
                        else:
                            logger.error(f"Invalid selection: {idx}")
                except ValueError:
                    logger.error("Invalid input. Please enter comma-separated numbers.")
                break
            
            elif choice == '3':
                logger.info("Exiting without changes.")
                break
            
            else:
                logger.error("Invalid choice. Please enter 1, 2, or 3.")
    
    async def mark_file_as_archived(self, file_id):
        """Mark a specific file as archived by ID."""
        result = await self.conn.fetchrow("""
            UPDATE document_registry
            SET embedding_status = 'archived'
            WHERE id = $1
            RETURNING id, title
        """, file_id)
        
        if result:
            logger.info(f"File '{result['title']}' (ID: {result['id']}) marked as archived.")
            return True
        else:
            logger.error(f"File with ID {file_id} not found in registry.")
            return False
    
    async def mark_file_as_archived_by_path(self, file_path):
        """Mark a specific file as archived by path."""
        # Normalize path
        file_path = os.path.abspath(file_path)
        
        result = await self.conn.fetchrow("""
            UPDATE document_registry
            SET embedding_status = 'archived'
            WHERE file_path = $1
            RETURNING id, title
        """, file_path)
        
        if not result:
            # Try with just the filename
            filename = os.path.basename(file_path)
            result = await self.conn.fetchrow("""
                UPDATE document_registry
                SET embedding_status = 'archived'
                WHERE title = $1
                RETURNING id, title
            """, filename)
        
        if result:
            logger.info(f"File '{result['title']}' (ID: {result['id']}) marked as archived.")
            return True
        else:
            logger.error(f"File not found in registry: {file_path}")
            return False
    
    async def list_archived_files(self):
        """List all files currently marked as archived."""
        records = await self.conn.fetch("""
            SELECT id, title, file_path
            FROM document_registry
            WHERE embedding_status IN ('archived', 'obsolete')
            ORDER BY title
        """)
        
        if not records:
            logger.info("No archived files found in the registry.")
            return []
        
        print("\n=== Archived Files in Registry ===")
        print(f"{'ID':<5} | {'Title':<30} | {'Path':<50}")
        print("-" * 90)
        
        for record in records:
            print(f"{record['id']:<5} | {record['title']:<30} | {record['file_path']:<50}")
        
        print(f"\nTotal: {len(records)} archived file(s).")
        return records

    async def list_all_files(self):
        """List all documents in the registry."""
        records = await self.conn.fetch("""
            SELECT id, title, file_path, embedding_status
            FROM document_registry
            ORDER BY id
        """)
        
        if not records:
            logger.info("The document registry is empty.")
            return []
        
        print("\n=== All Documents in Registry ===")
        print(f"{'ID':<5} | {'Title':<50} | {'Status':<15} | {'File Path'}")
        print("-" * 120)
        
        for record in records:
            print(f"{record['id']:<5} | {record['title']:<50} | {record['embedding_status']:<15} | {record['file_path']}")
            
        print(f"\nTotal: {len(records)} document(s) in the registry.")
        return records

    async def normalize_all_paths(self):
        """Convert all absolute file_paths in the document_registry to relative paths."""
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent

        records = await self.conn.fetch("""
            SELECT id, title, file_path
            FROM document_registry
        """)
        
        normalized_count = 0
        for record in records:
            if not record['file_path']:
                continue

            current_path = Path(record['file_path'])
            if current_path.is_absolute():
                try:
                    relative_path = current_path.relative_to(project_root)
                    await self.conn.execute("""
                        UPDATE document_registry
                        SET file_path = $1
                        WHERE id = $2
                    """, str(relative_path), record['id'])
                    logger.info(f"Normalized path for ID {record['id']} ('{record['title']}'): '{current_path}' -> '{relative_path}'")
                    normalized_count += 1
                except ValueError:
                    logger.warning(f"Could not make path relative for ID {record['id']} ('{record['title']}'): '{current_path}' is not under project root '{project_root}'. Skipping.")
        
        if normalized_count > 0:
            logger.info(f"Successfully normalized {normalized_count} absolute path(s).")
        else:
            logger.info("No absolute paths found requiring normalization.")
        return normalized_count

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Registry Archive Manager")
    parser.add_argument('--scan', action='store_true', help='Scan for missing files and interactively mark them as archived.')
    parser.add_argument('--list-missing', action='store_true', help='List files that no longer exist at their specified paths.')
    parser.add_argument('--mark-archived', type=int, metavar='FILE_ID', help='Mark a specific file as archived by its ID.')
    parser.add_argument('--mark-archived-by-path', type=str, metavar='FILE_PATH', help='Mark a specific file as archived by its path.')
    parser.add_argument('--list-archived', action='store_true', help='List all files currently marked as archived.')
    parser.add_argument('--list-all', action='store_true', help='List all documents in the registry.')
    parser.add_argument('--normalize-paths', action='store_true', help='Convert all absolute file_paths in the registry to relative paths.')

    args = parser.parse_args()

    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable not set.")
        sys.exit(1)

    conn = None
    try:
        # Setting statement_cache_size=0 to fix pgbouncer compatibility issue
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        manager = RegistryArchiveManager(conn)
        
        if args.scan:
            await manager.interactive_scan()
        elif args.list_missing:
            await manager.list_missing_files()
        elif args.mark_archived:
            await manager.mark_file_as_archived(args.mark_archived)
        elif args.mark_archived_by_path:
            await manager.mark_file_as_archived_by_path(args.mark_archived_by_path)
        elif args.list_archived:
            await manager.list_archived_files()
        elif args.list_all:
            await manager.list_all_files()
        elif args.normalize_paths:
            await manager.normalize_all_paths()
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
    finally:
        if conn:
            await conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
