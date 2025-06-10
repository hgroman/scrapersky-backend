#!/usr/bin/env python3
"""
Directory approval management for ScraperSky document registry.
Allows controlled, systematic scanning of directories.
"""

import os
import sys
import asyncio
import asyncpg
import argparse
import logging
from datetime import datetime
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

async def approve_directory(directory_path):
    """Approve a directory for scanning."""
    conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
    try:
        # Normalize path
        if not directory_path.endswith('/'):
            directory_path += '/'
            
        # Ensure directory exists
        if not os.path.isdir(directory_path):
            logger.error(f"Directory does not exist: {directory_path}")
            return False
            
        # Check if directory already exists in table
        existing = await conn.fetchval('''
        SELECT COUNT(*) FROM approved_scan_directories 
        WHERE directory_path = $1
        ''', directory_path)
        
        if existing > 0:
            # Update existing record
            await conn.execute('''
            UPDATE approved_scan_directories
            SET active = true
            WHERE directory_path = $1
            ''', directory_path)
        else:
            # Insert new record
            await conn.execute('''
            INSERT INTO approved_scan_directories 
            (directory_path, active)
            VALUES ($1, true)
            ''', directory_path)
        
        logger.info(f"Directory approved for scanning: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Error approving directory: {e}")
        return False
    finally:
        await conn.close()

async def unapprove_directory(directory_path):
    """Remove approval for a directory."""
    conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
    try:
        # Normalize path
        if not directory_path.endswith('/'):
            directory_path += '/'
            
        # Mark as inactive
        await conn.execute('''
        UPDATE approved_scan_directories
        SET active = false
        WHERE directory_path = $1
        ''', directory_path)
        
        logger.info(f"Directory unapproved: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Error unapproving directory: {e}")
        return False
    finally:
        await conn.close()

async def list_approved_directories():
    """List all approved directories."""
    conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
    try:
        records = await conn.fetch('''
        SELECT 
          directory_path, 
          active
        FROM approved_scan_directories
        ORDER BY id DESC
        ''')
        
        print("\nApproved Scan Directories:")
        print("-" * 60)
        print(f"{'Directory':<50} {'Status':<10}")
        print("-" * 60)
        
        for r in records:
            status = "ACTIVE" if r['active'] else "INACTIVE"
            print(f"{r['directory_path']:<50} {status:<10}")
            
        print("-" * 60)
        return records
    finally:
        await conn.close()

async def show_directory_status():
    """Show status of approved directories with file counts."""
    conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
    try:
        # Get all active approved directories
        records = await conn.fetch('''
        SELECT 
          directory_path, 
          active
        FROM approved_scan_directories
        ORDER BY active DESC, directory_path
        ''')
        
        print("\nDirectory Status:")
        print("-" * 80)
        print(f"{'Directory':<50} {'Status':<10} {'Files':<5} {'v_ Files':<8}")
        print("-" * 80)
        
        for r in records:
            status = "ACTIVE" if r['active'] else "INACTIVE"
            dir_path = r['directory_path']
            
            # Count files in directory
            total_files = 0
            v_files = 0
            
            if os.path.isdir(dir_path):
                for _, _, files in os.walk(dir_path):
                    for file in files:
                        if file.endswith('.md'):
                            total_files += 1
                            if file.startswith('v_'):
                                v_files += 1
            
            print(f"{dir_path:<50} {status:<10} {total_files:<5} {v_files:<8}")
            
        print("-" * 80)
        return records
    finally:
        await conn.close()

async def list_candidates(directory_path):
    """List potential vectorization candidates in a directory."""
    if not os.path.isdir(directory_path):
        logger.error(f"Directory does not exist: {directory_path}")
        return []
        
    print(f"\nPotential Vectorization Candidates in {directory_path}:")
    print("-" * 80)
    
    candidates = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.md') and not file.startswith('v_'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, os.getcwd())
                candidates.append((rel_path, file))
                
    # Print results
    if not candidates:
        print("No vectorization candidates found.")
    else:
        print(f"Found {len(candidates)} potential candidates:")
        for i, (path, name) in enumerate(candidates, 1):
            print(f"{i}. {name} - {path}")
            
    print("-" * 80)
    return candidates

async def main():
    parser = argparse.ArgumentParser(
        description="Manage directory approvals for document registry scanning"
    )
    parser.add_argument('--approve', help='Approve directory for scanning')
    parser.add_argument('--unapprove', help='Unapprove directory')
    parser.add_argument('--list-approved', action='store_true', help='List approved directories')
    parser.add_argument('--list-candidates', help='List vectorization candidates in directory')
    # NEW: Added status command
    parser.add_argument('--status', action='store_true', help='Show approved directories with file counts')
    
    args = parser.parse_args()
    
    if args.approve:
        await approve_directory(args.approve)
        
    if args.unapprove:
        await unapprove_directory(args.unapprove)
        
    if args.list_approved:
        await list_approved_directories()
        
    if args.list_candidates:
        await list_candidates(args.list_candidates)
    
    # NEW: Handle status command
    if args.status:
        await show_directory_status()
        
    if len(sys.argv) == 1:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())