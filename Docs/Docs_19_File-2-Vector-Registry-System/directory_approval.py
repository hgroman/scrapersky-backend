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

async def create_approval_table():
    """Create the approved_scan_directories table if it doesn't exist."""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS approved_scan_directories (
          id SERIAL PRIMARY KEY,
          directory_path TEXT NOT NULL UNIQUE,
          description TEXT,
          active BOOLEAN DEFAULT true,
          approved_by TEXT,
          approved_at TIMESTAMP DEFAULT NOW()
        );
        ''')
        logger.info("Ensured approval table exists")
    finally:
        await conn.close()

async def approve_directory(directory_path, description="", approved_by="user"):
    """Approve a directory for scanning."""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Normalize path
        if not directory_path.endswith('/'):
            directory_path += '/'
            
        # Ensure directory exists
        if not os.path.isdir(directory_path):
            logger.error(f"Directory does not exist: {directory_path}")
            return False
            
        # Add to approved directories
        await conn.execute('''
        INSERT INTO approved_scan_directories 
        (directory_path, description, approved_by)
        VALUES ($1, $2, $3)
        ON CONFLICT (directory_path) 
        DO UPDATE SET 
          active = true,
          description = $2,
          approved_by = $3,
          approved_at = NOW()
        ''', directory_path, description, approved_by)
        
        logger.info(f"Directory approved for scanning: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Error approving directory: {e}")
        return False
    finally:
        await conn.close()

async def unapprove_directory(directory_path):
    """Remove approval for a directory."""
    conn = await asyncpg.connect(DATABASE_URL)
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
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        records = await conn.fetch('''
        SELECT 
          directory_path, 
          description, 
          approved_by, 
          approved_at,
          active
        FROM approved_scan_directories
        ORDER BY approved_at DESC
        ''')
        
        print("\nApproved Scan Directories:")
        print("-" * 80)
        print(f"{'Directory':<40} {'Status':<10} {'Approved By':<15} {'Approved At'}")
        print("-" * 80)
        
        for r in records:
            status = "ACTIVE" if r['active'] else "INACTIVE"
            print(f"{r['directory_path']:<40} {status:<10} {r['approved_by']:<15} {r['approved_at']}")
            
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
    parser.add_argument('--setup', action='store_true', help='Create approval table')
    parser.add_argument('--approve', help='Approve directory for scanning')
    parser.add_argument('--unapprove', help='Unapprove directory')
    parser.add_argument('--list-approved', action='store_true', help='List approved directories')
    parser.add_argument('--list-candidates', help='List vectorization candidates in directory')
    parser.add_argument('--description', default='', help='Description for approval')
    
    args = parser.parse_args()
    
    if args.setup:
        await create_approval_table()
        
    if args.approve:
        await approve_directory(args.approve, args.description)
        
    if args.unapprove:
        await unapprove_directory(args.unapprove)
        
    if args.list_approved:
        await list_approved_directories()
        
    if args.list_candidates:
        await list_candidates(args.list_candidates)
        
    if len(sys.argv) == 1:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
