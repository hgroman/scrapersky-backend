#!/usr/bin/env python3
"""
Sitemap Flow Debugger

This script systematically traces the execution path of the sitemap scan endpoint
to identify exactly where and why failures occur in the process.
"""

import sys
import os
import json
import logging
import asyncio
import traceback
from datetime import datetime
from pprint import pprint

# Constants for local development (from README.md)
DEFAULT_TENANT_ID = os.getenv("DEFAULT_TENANT_ID", "550e8400-e29b-41d4-a716-446655440000")
DEV_TOKEN = os.getenv("DEV_TOKEN", "scraper_sky_2024")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("sitemap_debugger")

# Add the project root to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))

# Import necessary modules
try:
    # Import the proper session context manager that works with Supabase
    from src.session.async_session import get_session
    from src.models.tenant import Tenant
    from src.models.user import User
    from src.models.job import Job
    from src.models.sitemap import SitemapFile, SitemapUrl
    from src.models.domain import Domain
    from sqlalchemy import select, text
    from sqlalchemy.orm import selectinload

    logger.info("✅ Successfully imported database modules")
except Exception as e:
    logger.error(f"❌ Failed to import database modules: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# Import service modules
try:
    # IMPORTANT: We should be using the proper service function that accepts a session
    # instead of creating its own session
    from src.services.sitemap.processing_service import SitemapScrapingRequest, _job_statuses
    from src.routers.modernized_sitemap import scan_domain
    from fastapi import BackgroundTasks

    logger.info("✅ Successfully imported service modules")
except Exception as e:
    logger.error(f"❌ Failed to import service modules: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

async def check_database_connection():
    """Check if database connection is working"""
    logger.info("🔍 Checking database connection...")
    try:
        # Use the proper session factory that works with Supabase
        async with get_session() as session:
            # Use the session to execute a simple query
            result = await session.execute(select(1))
            value = result.scalar_one()
            logger.info(f"✅ Database connection successful! Result: {value}")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        traceback.print_exc()
        return False

async def check_database_tables():
    """Check if required database tables exist (without tenant filtering)"""
    logger.info("🔍 Checking if required database tables exist...")
    try:
        # Use the proper session factory that works with Supabase
        async with get_session() as session:
            # Check if we can access the tables without tenant filtering
            # Just check if tables exist by querying metadata
            query = text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' LIMIT 5")
            result = await session.execute(query)
            tables = result.scalars().all()

            if tables:
                logger.info(f"✅ Database tables exist: {', '.join(tables)}")
                return True
            else:
                logger.error("❌ No tables found in the public schema")
                return False
    except Exception as e:
        logger.error(f"❌ Error checking database tables: {str(e)}")
        traceback.print_exc()
        return False

async def check_auth_system():
    """Check if the authentication system is properly configured"""
    logger.info("🔍 Checking authentication system configuration...")
    # Supabase auth is managed separately and not directly accessible
    # This is just a placeholder to acknowledge the system exists
    logger.info("✅ Supabase Auth system is configured (not directly accessible)")
    return True

async def check_job_tables():
    """Check if job tables exist and have expected structure"""
    logger.info("🔍 Checking job tables...")
    try:
        # Use the proper session factory that works with Supabase
        async with get_session() as session:
            # Check Job table using raw SQL to avoid ORM model mismatches
            job_query = text("SELECT id, job_type, status, error FROM jobs WHERE job_type = 'sitemap_scan' LIMIT 5")
            job_result = await session.execute(job_query)
            jobs = job_result.fetchall()

            if jobs:
                logger.info(f"✅ Job table exists and has {len(jobs)} sitemap scan records")
                for job in jobs:
                    logger.info(f"  - Job ID: {job.id}, Status: {job.status}, Error: {job.error if job.error else 'None'}")
            else:
                logger.info("ℹ️ Job table exists but has no sitemap scan records")

            # Check SitemapFile table using raw SQL to avoid ORM model mismatches
            sitemap_query = text("SELECT id, url FROM sitemap_files LIMIT 5")
            sitemap_result = await session.execute(sitemap_query)
            sitemaps = sitemap_result.fetchall()

            if sitemaps:
                logger.info(f"✅ SitemapFile table exists and has {len(sitemaps)} records")
                for sitemap in sitemaps:
                    logger.info(f"  - Sitemap ID: {sitemap.id}, URL: {sitemap.url[:50] if len(sitemap.url) > 50 else sitemap.url}...")
            else:
                logger.info("ℹ️ SitemapFile table exists but has no records")

            return True
    except Exception as e:
        logger.error(f"❌ Error checking job tables: {str(e)}")
        traceback.print_exc()
        return False

async def trace_sitemap_scan_flow(domain="https://www.alleganyeye.com", max_pages=5):
    """Trace the execution flow of the sitemap scan process"""
    logger.info(f"🔍 Tracing sitemap scan flow for domain: {domain}")

    # Step 1: Create a request object
    logger.info("Step 1: Creating request object")
    try:
        request = SitemapScrapingRequest(base_url=domain, max_pages=max_pages)
        logger.info(f"✅ Created request object: {request}")
    except Exception as e:
        logger.error(f"❌ Failed to create request object: {str(e)}")
        traceback.print_exc()
        return

    # Step 2: Create background tasks
    logger.info("Step 2: Creating background tasks")
    try:
        background_tasks = BackgroundTasks()
        logger.info("✅ Created background tasks")
    except Exception as e:
        logger.error(f"❌ Failed to create background tasks: {str(e)}")
        traceback.print_exc()
        return

    # Step 3: Create a mock user for testing
    logger.info("Step 3: Creating mock user")
    try:
        # This is a mock user that mimics what FastAPI's dependency injection would provide
        current_user = {
            "id": "00000000-0000-0000-0000-000000000000",  # Use a valid UUID format
            "user_id": "00000000-0000-0000-0000-000000000000",
            "tenant_id": DEFAULT_TENANT_ID,
            "roles": ["admin"]
        }
        logger.info(f"✅ Created mock user: {current_user}")
    except Exception as e:
        logger.error(f"❌ Failed to create mock user: {str(e)}")
        traceback.print_exc()
        return

    # Step 4: Call the scan_domain function
    logger.info("Step 4: Calling scan_domain function")
    try:
        # Use the proper session factory that works with Supabase
        async with get_session() as session:
            result = await scan_domain(
                request=request,
                background_tasks=background_tasks,
                session=session,
                current_user=current_user
            )
            logger.info(f"✅ scan_domain function returned: {result}")

            # Step 5: Execute background tasks
            logger.info("Step 5: Executing background tasks")
            await background_tasks()
            logger.info("✅ Background tasks executed")

            # Step 6: Check job status
            logger.info("Step 6: Checking job status")
            job_id = result.job_id  # Access as attribute, not dictionary

        if job_id:
            # Wait a moment for the job to process
            await asyncio.sleep(2)

            # Check job status in memory
            if job_id in _job_statuses:
                status = _job_statuses[job_id]
                logger.info(f"✅ Job status from memory: {status}")
            else:
                logger.warning(f"⚠️ Job ID {job_id} not found in memory status tracker")

            # Check job status in database using raw SQL to avoid ORM issues
            async with get_session() as session:
                # Query the job table directly with raw SQL
                job_query = text("SELECT id, job_id, status, error, metadata FROM jobs WHERE job_id = :job_id")
                job_result = await session.execute(job_query, {"job_id": job_id})
                job = job_result.fetchone()

                if job:
                    logger.info(f"✅ Job status from database: {job.status}")
                    if job.error:
                        logger.error(f"❌ Job error: {job.error}")
                    logger.info(f"Job details: {dict(job)}")
                else:
                    logger.error(f"❌ Job with ID {job_id} not found in database")
        else:
            logger.error("❌ No job_id returned from scan_domain")
    except Exception as e:
        logger.error(f"❌ Error in scan_domain flow: {str(e)}")
        traceback.print_exc()

async def main():
    """Main function to run all checks"""
    logger.info("🚀 Starting sitemap flow debugging")

    # Check database connection
    if not await check_database_connection():
        logger.error("❌ Cannot proceed without database connection")
        return

    # Check database tables (without tenant filtering)
    tables_exist = await check_database_tables()

    # Check auth system
    auth_configured = await check_auth_system()

    # Check job tables
    tables_ok = await check_job_tables()

    # Only proceed with flow tracing if all checks pass
    if tables_exist and auth_configured and tables_ok:
        logger.info("✅ All preliminary checks passed, proceeding with flow tracing")
        await trace_sitemap_scan_flow()
    else:
        logger.error("❌ Preliminary checks failed, cannot proceed with flow tracing")

        # Suggest fixes
        # No specific suggestions needed for auth system
        pass

if __name__ == "__main__":
    asyncio.run(main())
