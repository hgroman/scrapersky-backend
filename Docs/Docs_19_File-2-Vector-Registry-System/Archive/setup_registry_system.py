#!/usr/bin/env python3
"""
Setup script for the ScraperSky document registry system.
This initializes the database tables and approves initial directories.
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Add parent directory to path to import directory_approval
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import directory_approval

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

async def setup_system():
    """Initialize the registry system."""
    # Create the approval table
    logger.info("Creating approval table...")
    await directory_approval.create_approval_table()
    
    # Approve initial directories
    logger.info("Approving initial directories...")
    
    # Critical directories specifically requested for approval
    await directory_approval.approve_directory(
        "Docs/Docs_6_Architecture_and_Status",
        "Architecture documentation and system status",
        "system_init"
    )
    
    await directory_approval.approve_directory(
        "Docs/Docs_18_Vector_Operations",
        "Full vector operations directory",
        "system_init"
    )
    
    # Vector Operations Documentation
    await directory_approval.approve_directory(
        "Docs/Docs_18_Vector_Operations/Documentation",
        "Vector database documentation",
        "system_init"
    )
    
    # AI Guides
    await directory_approval.approve_directory(
        "Docs/Docs_1_AI_GUIDES",
        "AI guides and reference documentation",
        "system_init"
    )
    
    # List approved directories
    logger.info("Initial setup complete. Approved directories:")
    await directory_approval.list_approved_directories()
    
    logger.info("\nNext steps:")
    logger.info("1. Review and update approved directories with: python directory_approval.py --list-approved")
    logger.info("2. Scan approved directories: python manage_document_registry.py --scan --approved-only")
    logger.info("3. Generate a status report: python manage_document_registry.py --report")

if __name__ == "__main__":
    asyncio.run(setup_system())
