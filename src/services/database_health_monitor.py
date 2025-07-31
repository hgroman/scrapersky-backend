"""
Database Health Monitor Service

This service monitors for and automatically resolves "idle in transaction" connections
that can block database operations. It runs as a background scheduler job.

This is a defensive measure against the recurring database timeout issue where
connections get stuck in "idle in transaction" state and block UPDATE operations
on critical tables like 'domains'.
"""

import logging
import sys
from datetime import datetime, timezone

from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import text

from ..scheduler_instance import scheduler
from ..session.async_session import get_background_session

logger = logging.getLogger(__name__)


async def monitor_and_cleanup_database_connections():
    """
    Monitor for problematic database connections and automatically clean them up.

    This function:
    1. Identifies connections stuck in "idle in transaction" state for >2 minutes
    2. Terminates these blocking connections to prevent timeouts
    3. Logs the cleanup actions for monitoring
    """
    job_id = f"db_health_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    logger.debug(f"Starting database health check job {job_id}")

    try:
        async with get_background_session() as session:
            # Find connections stuck in "idle in transaction" for >2 minutes
            result = await session.execute(
                text("""
                SELECT 
                    pid,
                    usename,
                    application_name,
                    state,
                    query_start,
                    now() - query_start as duration,
                    client_addr
                FROM pg_stat_activity 
                WHERE state = 'idle in transaction'
                  AND datname = current_database()
                  AND now() - query_start > interval '2 minutes'
                ORDER BY query_start
            """)
            )

            blocking_connections = result.fetchall()

            if not blocking_connections:
                logger.debug("No problematic connections found - database health OK")
                return

            logger.warning(
                f"Found {len(blocking_connections)} idle in transaction connections"
            )

            # Terminate each blocking connection
            terminated_count = 0
            for conn in blocking_connections:
                logger.warning(
                    f"Terminating idle connection PID {conn.pid} "
                    f"(idle for {conn.duration}, client: {conn.client_addr})"
                )

                try:
                    result = await session.execute(
                        text(f"SELECT pg_terminate_backend({conn.pid})")
                    )
                    success = result.scalar()

                    if success:
                        terminated_count += 1
                        logger.info(
                            f"Successfully terminated blocking connection PID {conn.pid}"
                        )
                    else:
                        logger.error(f"Failed to terminate connection PID {conn.pid}")

                except Exception as term_error:
                    logger.error(f"Error terminating PID {conn.pid}: {term_error}")

            if terminated_count > 0:
                logger.warning(
                    f"Database health monitor terminated {terminated_count} blocking connections"
                )

            # Check if any locks remain on critical tables
            result = await session.execute(
                text("""
                SELECT COUNT(*) as lock_count
                FROM pg_locks l
                WHERE l.relation = 'domains'::regclass
                  AND l.mode IN ('RowShareLock', 'RowExclusiveLock')
            """)
            )

            lock_count = result.scalar()
            if lock_count > 0:
                logger.warning(
                    f"Still {lock_count} locks remaining on domains table after cleanup"
                )
            else:
                logger.info("All problematic locks cleared - domains table accessible")

    except Exception as error:
        logger.error(f"Database health monitor error: {error}", exc_info=True)

    finally:
        logger.debug(f"Database health check job {job_id} complete")


def setup_database_health_monitor():
    """
    Set up the database health monitoring scheduler job.

    This job runs every 2 minutes to proactively clean up any connections
    that get stuck in "idle in transaction" state.
    """
    try:
        job_id = "database_health_monitor"

        # Remove existing job if it exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Removed existing {job_id} job")

        # Add the health monitor job
        scheduler.add_job(
            monitor_and_cleanup_database_connections,
            trigger=IntervalTrigger(minutes=2),  # Run every 2 minutes
            id=job_id,
            name="Database Health Monitor",
            max_instances=1,  # Only one instance at a time
            coalesce=True,  # Skip missed runs
            replace_existing=True,
        )

        logger.info("Database health monitor scheduled (every 2 minutes)")

    except Exception as e:
        logger.error(f"Failed to setup database health monitor: {e}")
        raise


if __name__ == "__main__":
    """Direct execution for testing"""
    import asyncio

    logging.basicConfig(level=logging.DEBUG)

    async def test_monitor():
        await monitor_and_cleanup_database_connections()

    asyncio.run(test_monitor())
