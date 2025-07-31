#!/usr/bin/env python3
"""
Supabase Connection Test

This script tests the direct connection to Supabase using the correct username format.
"""

import asyncio
import logging
import os
from sqlalchemy import text
from src.db.direct_session import get_direct_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("supabase_test")


async def test_connection():
    """Test connection to Supabase."""
    logger.info("Testing connection to Supabase...")

    try:
        # Use the direct session that works with Supabase
        async with get_direct_session() as session:
            # Execute a simple query
            result = await session.execute(
                text("SELECT current_database(), current_user")
            )
            row = result.fetchone()

            logger.info(f"✅ Successfully connected to Supabase!")
            logger.info(f"Database: {row[0]}, User: {row[1]}")

            # List tables in public schema
            result = await session.execute(
                text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
                )
            )
            tables = result.fetchall()

            logger.info(f"Available tables in public schema:")
            for table in tables:
                logger.info(f"- {table[0]}")

            return True
    except Exception as e:
        logger.error(f"❌ Failed to connect to Supabase: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        logger.info("Connection test completed successfully.")
    else:
        logger.error("Connection test failed.")
