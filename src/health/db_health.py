"""
Database Health Check

This module provides health check functions for database connections.
"""
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def check_database_connection(session: AsyncSession) -> bool:
    """
    Check if the database connection is working.

    Args:
        session: SQLAlchemy async session

    Returns:
        True if connection is working, False otherwise
    """
    try:
        # Execute a simple query to check connection
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False
