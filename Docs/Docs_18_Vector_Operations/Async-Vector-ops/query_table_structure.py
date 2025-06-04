#!/usr/bin/env python
"""
Query Table Structure

This script queries the structure of the fix_patterns table to understand its columns and constraints.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
import asyncpg

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def main():
    """Query the structure of the fix_patterns table."""
    logger.info("Querying fix_patterns table structure")
    
    try:
        # Connect to the database
        conn = await asyncpg.connect(
            DATABASE_URL,
            ssl="require",
            statement_cache_size=0  # Disable statement cache for pgbouncer compatibility
        )
        logger.info("Connected to database")
        
        # Query table structure
        columns = await conn.fetch("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM 
                information_schema.columns 
            WHERE 
                table_name = 'fix_patterns' 
            ORDER BY 
                ordinal_position
        """)
        
        logger.info("fix_patterns table structure:")
        for col in columns:
            nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
            default = f"DEFAULT {col['column_default']}" if col["column_default"] else ""
            logger.info(f"{col['column_name']}: {col['data_type']}, {nullable} {default}")
        
        # Close connection
        await conn.close()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error(f"Error querying database: {e}")


if __name__ == "__main__":
    asyncio.run(main())
