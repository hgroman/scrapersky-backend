#!/usr/bin/env python3
"""
File Discovery and Orphan Detection Tool for ScraperSky
=======================================================

This script scans the codebase for Python files and compares against
the Supabase file_audit registry to identify orphans and phantoms.

Orphans: Files that exist in the codebase but not in the database
Phantoms: Files that exist in the database but not in the codebase

Usage: python file_discovery.py [--export-yaml]
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
import asyncpg
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Database configuration (uses environment variables)
DB_HOST = os.getenv("SUPABASE_DB_HOST", "aws-0-us-west-1.pooler.supabase.com")
DB_PORT = os.getenv("SUPABASE_DB_PORT", "6543")
DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")
DB_USER = os.getenv("SUPABASE_DB_USER", "postgres.ddfldwzhdhhzhxywqnyz")  # Format: postgres.[project-ref]
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")  # Set in environment variable for security

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"

# Output directory for reports
REPORTS_DIR = PROJECT_ROOT / "reports"


async def get_database_files() -> List[Dict]:
    """Get all files from the file_audit table in the database."""
    try:
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl="require",
            server_settings={
                "raw_sql": "true",
                "no_prepare": "true",
                "statement_cache_size": "0"
            }
        )

        logger.info("Connected to database successfully")

        # Query all files from the file_audit table
        rows = await conn.fetch("""
            SELECT
                id,
                file_number,
                file_path,
                file_name,
                layer_number,
                layer_name,
                status,
                workflows,
                has_technical_debt,
                technical_debt,
                jira_tickets,
                audit_status
            FROM file_audit
            ORDER BY file_number
        """)

        # Convert to list of dictionaries
        result = [dict(row) for row in rows]
        logger.info(f"Retrieved {len(result)} files from database")

        await conn.close()
        return result

    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return []


def get_filesystem_files() -> List[str]:
    """Get all Python files from the src directory recursively."""
    python_files = []

    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(".py"):
                # Get relative path from project root
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                python_files.append(rel_path)

    logger.info(f"Found {len(python_files)} Python files in filesystem")
    return sorted(python_files)


def detect_orphans_and_phantoms(db_files: List[Dict], fs_files: List[str]) -> Tuple[List[str], List[Dict]]:
    """
    Compare database records with filesystem files to identify orphans and phantoms.

    Args:
        db_files: List of file records from the database
        fs_files: List of file paths from the filesystem

    Returns:
        Tuple of (orphaned_files, phantom_files)
    """
    # Extract file paths from database records
    db_file_paths = {file['file_path'] for file in db_files}

    # Convert filesystem paths to the same format as database paths
    fs_file_paths = set(fs_files)

    # Find orphans (in filesystem but not in database)
    orphans = sorted(list(fs_file_paths - db_file_paths))

    # Find phantoms (in database but not in filesystem)
    phantoms = [file for file in db_files if file['file_path'] not in fs_file_paths]

    return orphans, phantoms


def export_to_yaml(db_files: List[Dict], orphans: List[str], phantoms: List[Dict]) -> None:
    """Export data to YAML files for version control."""
    # Create reports directory if it doesn't exist
    REPORTS_DIR.mkdir(exist_ok=True)

    # Export database files
    with open(REPORTS_DIR / "file_registry.yaml", "w") as f:
        yaml.dump(db_files, f, default_flow_style=False, sort_keys=False)

    # Export orphans and phantoms
    report = {
        "timestamp": f"{__import__('datetime').datetime.now().isoformat()}",
        "total_db_files": len(db_files),
        "total_orphans": len(orphans),
        "total_phantoms": len(phantoms),
        "orphans": orphans,
        "phantoms": [file['file_path'] for file in phantoms]
    }

    with open(REPORTS_DIR / "orphan_phantom_report.yaml", "w") as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Exported reports to {REPORTS_DIR}")


async def main():
    """Main function to run the file discovery and orphan detection."""
    parser = argparse.ArgumentParser(description="File discovery and orphan detection tool")
    parser.add_argument("--export-yaml", action="store_true", help="Export results to YAML files")
    args = parser.parse_args()

    logger.info("Starting file discovery and orphan detection...")

    # Get files from database and filesystem
    db_files = await get_database_files()
    fs_files = get_filesystem_files()

    # Detect orphans and phantoms
    orphans, phantoms = detect_orphans_and_phantoms(db_files, fs_files)

    # Log results
    if orphans:
        logger.warning(f"Found {len(orphans)} orphaned files:")
        for orphan in orphans:
            logger.warning(f"  - {orphan}")
    else:
        logger.info("No orphaned files found. All files are properly registered!")

    if phantoms:
        logger.warning(f"Found {len(phantoms)} phantom files:")
        for phantom in phantoms:
            logger.warning(f"  - {phantom['file_path']} (File ID: {phantom['file_number']})")
    else:
        logger.info("No phantom files found. Database is in sync with the filesystem!")

    # Export to YAML if requested
    if args.export_yaml:
        export_to_yaml(db_files, orphans, phantoms)

    # Summary
    print("\n" + "=" * 80)
    print(f"SUMMARY: {len(db_files)} database files, {len(fs_files)} filesystem files")
    print(f"         {len(orphans)} orphans, {len(phantoms)} phantoms")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
