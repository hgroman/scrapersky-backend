#!/usr/bin/env python3
"""
Batch Status Monitor

This script monitors the status of a batch job until completion or timeout.

Usage:
    python monitor_test.py BATCH_ID [--interval SECONDS] [--timeout SECONDS]
"""

import asyncio
import sys
import os
import logging
import time
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("batch_monitor")

# Import app modules
from src.session.async_session import async_session_factory
from src.services.batch.batch_functions import get_batch_status

async def monitor_batch(batch_id, interval=2, max_time=60):
    """Monitor a batch until it completes or times out."""
    logger.info(f"Monitoring batch ID: {batch_id}")

    start_time = time.time()

    # Create a session for status checks
    session = async_session_factory()

    try:
        while True:
            # Check elapsed time
            elapsed = time.time() - start_time
            if elapsed > max_time:
                logger.error(f"Monitoring timed out after {elapsed:.1f} seconds")
                return False

            # Get batch status
            async with session.begin():
                status = await get_batch_status(
                    session=session,
                    batch_id=batch_id
                )

            if not status:
                logger.error(f"Failed to get status for batch {batch_id}")
                await asyncio.sleep(interval)
                continue

            # Log current status
            current_status = status.get("status", "unknown")
            progress = status.get("progress", 0) * 100
            logger.info(f"Batch status: {current_status} - Progress: {progress:.1f}%")

            # If completed or failed, exit loop
            if current_status in ["completed", "failed", "error"]:
                logger.info(f"Final batch status: {status}")
                return current_status == "completed"

            # Wait before checking again
            await asyncio.sleep(interval)

    except Exception as e:
        logger.error(f"Error monitoring batch: {str(e)}", exc_info=True)
        return False

    finally:
        await session.close()
        logger.info("Session closed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor batch processing status")
    parser.add_argument("batch_id", help="Batch ID to monitor")
    parser.add_argument("--interval", type=int, default=2, help="Check interval in seconds")
    parser.add_argument("--timeout", type=int, default=60, help="Max monitoring time in seconds")

    args = parser.parse_args()

    success = asyncio.run(monitor_batch(args.batch_id, args.interval, args.timeout))
    sys.exit(0 if success else 1)
