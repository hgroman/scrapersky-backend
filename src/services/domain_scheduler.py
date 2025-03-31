"""
Domain Scheduler Service

This module provides a scheduling service that periodically processes domains
with 'pending' status in the database.
"""
import logging
import os
from datetime import datetime
import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import text
import asyncio
import sys
import json
from typing import List, Dict, Any

from ..session.async_session import get_background_session
from ..scraper.metadata_extractor import detect_site_metadata
from ..scraper.domain_utils import standardize_domain, get_domain_url
from ..config.settings import Settings

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Create settings instance
settings = Settings()

# Create diagnostic directory from settings
DIAGNOSTIC_DIR = settings.DIAGNOSTIC_DIR
os.makedirs(DIAGNOSTIC_DIR, exist_ok=True)

def log_diagnostic_info(message):
    """Log diagnostic information to file and logger."""
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"{timestamp} - {message}")

    try:
        filename = f"{DIAGNOSTIC_DIR}/domain_scheduler_{datetime.utcnow().strftime('%Y%m%d')}.log"
        with open(filename, "a") as f:
            f.write(f"{timestamp} - {message}\n")
    except Exception as e:
        logger.error(f"Error writing diagnostic log: {str(e)}")

async def process_pending_domains(limit: int = 10):
    """
    Process pending domains that have been queued for processing.

    Args:
        limit: Maximum number of domains to process in one batch
    """
    job_id = f"domain_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    logger.debug("--------------------------------------------------")
    logger.debug(f"STARTING DOMAIN PROCESSING JOB {job_id} ({limit} domains max)")
    logger.debug("--------------------------------------------------")

    domains_processed = 0
    domains_successful = 0

    # Log the current time to verify this function is actually being called by the scheduler
    now = datetime.utcnow()
    logger.info(f"*** DOMAIN PROCESSOR EXECUTING AT {now.isoformat()} ***")
    logger.info(f"*** SCHEDULER STATE: Running={scheduler.running}, Jobs={len(scheduler.get_jobs())} ***")

    for job in scheduler.get_jobs():
        logger.info(f"*** REGISTERED JOB: {job.id}, Next run: {job.next_run_time} ***")

    # Step 1: Fetch pending domains
    pending_domains = []
    try:
        # Use background session with appropriate async settings for fetching domains
        async with get_background_session() as fetch_session:
            logger.debug(f"Got session for fetching pending domains: {fetch_session}")

            try:
                # Set the supavisor options for this session
                logger.debug("Setting session options for Supavisor compatibility")

                # Required Supavisor parameters
                options = [
                    ("SET statement_timeout = 90000", "90 seconds timeout"),
                    ("SET idle_in_transaction_session_timeout = 120000", "120 seconds idle timeout"),
                    ("SET statement_cache_size = 0", "Required for Supavisor compatibility")
                ]

                for sql, description in options:
                    set_option = text(sql)
                    set_option = set_option.execution_options(prepared=False)
                    await fetch_session.execute(set_option)
                    logger.debug(f"Set session option: {description}")
            except Exception as e:
                logger.error(f"Error setting session options: {str(e)}")
                logger.debug(traceback.format_exc())

            try:
                # Query for pending domains with proper execution options
                logger.debug(f"Querying for up to {limit} pending domains...")
                query = text("""
                SELECT * FROM domains
                WHERE status = 'pending'
                ORDER BY updated_at ASC
                LIMIT :limit
                """)
                # Apply Supavisor-compatible execution options
                query = query.execution_options(prepared=False)
                result = await fetch_session.execute(query.bindparams(limit=limit))

                for row in result.mappings():
                    domain_dict = dict(row)
                    domain_id = domain_dict.get('id')
                    url = domain_dict.get('domain')
                    logger.debug(f"Found pending domain: ID={domain_id}, URL={url}")
                    pending_domains.append(domain_dict)

                logger.debug(f"Found {len(pending_domains)} pending domain(s)")
            except Exception as query_error:
                logger.error(f"Error querying pending domains: {str(query_error)}")
                logger.debug(traceback.format_exc())
                return  # Exit if we can't fetch domains

    except Exception as session_error:
        logger.error(f"Error getting session for fetching domains: {str(session_error)}")
        logger.debug(traceback.format_exc())
        return  # Exit if session creation fails

    # Step 2: Process each domain individually
    for domain_dict in pending_domains:
        domain_id = domain_dict.get('id')
        url = domain_dict.get('domain')
        domains_processed += 1

        # Step 2.1: Update domain to processing status
        try:
            async with get_background_session() as update_session:
                # Set Supavisor options
                try:
                    logger.debug("Setting session options for update session")

                    # Required Supavisor parameters
                    options = [
                        ("SET statement_timeout = 90000", "90 seconds timeout"),
                        ("SET idle_in_transaction_session_timeout = 120000", "120 seconds idle timeout"),
                        ("SET statement_cache_size = 0", "Required for Supavisor compatibility")
                    ]

                    for sql, description in options:
                        set_option = text(sql)
                        set_option = set_option.execution_options(prepared=False)
                        await update_session.execute(set_option)
                        logger.debug(f"Set session option: {description}")
                except Exception as e:
                    logger.error(f"Error setting session options for update session: {str(e)}")
                    logger.debug(traceback.format_exc())

                async with update_session.begin():
                    logger.debug(f"Updating domain {domain_id} status to 'processing'")
                    update_query = text("""
                    UPDATE domains
                    SET status = 'processing', updated_at = NOW()
                    WHERE id = :id
                    """)
                    update_query = update_query.execution_options(prepared=False)
                    await update_session.execute(update_query.bindparams(id=domain_id))
                    logger.debug(f"Updated domain {domain_id} status to 'processing'")
        except Exception as status_error:
            logger.error(f"Error updating domain {domain_id} to processing status: {str(status_error)}")
            logger.debug(traceback.format_exc())
            continue  # Skip to next domain if we can't update status

        # Step 2.2: Extract metadata - SEPARATE TRY/EXCEPT BLOCK
        metadata = None
        try:
            # Process the domain using metadata extractor
            logger.debug(f"Standardizing domain: {url}")
            std_domain = standardize_domain(url)

            if not std_domain:
                raise ValueError(f"Invalid domain format: {url}")

            # Convert domain to proper URL for scraping
            domain_url = get_domain_url(std_domain)
            logger.debug(f"Converted domain to URL for scraping: {domain_url}")

            logger.debug(f"Extracting metadata for domain: {std_domain}")
            metadata = await detect_site_metadata(domain_url, max_retries=3)
            logger.debug(f"Metadata extraction complete for {std_domain}")

            if metadata is None:
                raise ValueError(f"Failed to extract metadata from {std_domain}")

        except Exception as extraction_error:
            # Handle metadata extraction errors separately
            error_message = str(extraction_error)
            logger.error(f"Error extracting metadata for domain {domain_id}: {error_message}")
            logger.debug(traceback.format_exc())
            await handle_domain_error(domain_id, error_message)
            continue  # Skip to next domain

        # Step 2.3: Update domain with results - SEPARATE TRY/EXCEPT BLOCK
        try:
            async with get_background_session() as result_session:
                # Set Supavisor options
                try:
                    # Set the supavisor options for this session
                    logger.debug("Setting session options for result session")

                    # Required Supavisor parameters
                    options = [
                        ("SET statement_timeout = 90000", "90 seconds timeout"),
                        ("SET idle_in_transaction_session_timeout = 120000", "120 seconds idle timeout"),
                        ("SET statement_cache_size = 0", "Required for Supavisor compatibility")
                    ]

                    for sql, description in options:
                        set_option = text(sql)
                        set_option = set_option.execution_options(prepared=False)
                        await result_session.execute(set_option)
                        logger.debug(f"Set session option: {description}")
                except Exception as e:
                    logger.error(f"Error setting session options for result session: {str(e)}")
                    logger.debug(traceback.format_exc())

                async with result_session.begin():
                    logger.debug(f"Updating domain {domain_id} with extracted metadata")

                    # Prepare metadata for storage
                    metadata_json = json.dumps(metadata)
                    tech_stack = metadata.get('tech_stack', {})

                    # Update all relevant fields
                    update_query = text("""
                    UPDATE domains
                    SET
                        status = 'completed',
                        updated_at = NOW(),
                        title = :title,
                        description = :description,
                        favicon_url = :favicon_url,
                        logo_url = :logo_url,
                        language = :language,
                        email_addresses = :email_addresses,
                        phone_numbers = :phone_numbers,
                        facebook_url = :facebook_url,
                        twitter_url = :twitter_url,
                        linkedin_url = :linkedin_url,
                        instagram_url = :instagram_url,
                        youtube_url = :youtube_url,
                        domain_metadata = :metadata,
                        tech_stack = :tech_stack,
                        is_wordpress = :is_wordpress,
                        wordpress_version = :wordpress_version,
                        has_elementor = :has_elementor
                    WHERE id = :id
                    """)

                    # Apply Supavisor-compatible execution options
                    update_query = update_query.execution_options(prepared=False)

                    # Extract values from metadata with proper fallbacks
                    contact_info = metadata.get('contact_info', {})
                    social_links = metadata.get('social_links', {})

                    # Execute the update with all parameters
                    await result_session.execute(update_query.bindparams(
                        id=domain_id,
                        title=metadata.get('title', ''),
                        description=metadata.get('description', ''),
                        favicon_url=metadata.get('favicon_url', ''),
                        logo_url=metadata.get('logo_url', ''),
                        language=metadata.get('language', ''),
                        email_addresses=contact_info.get('email', []),
                        phone_numbers=contact_info.get('phone', []),
                        facebook_url=social_links.get('facebook', ''),
                        twitter_url=social_links.get('twitter', ''),
                        linkedin_url=social_links.get('linkedin', ''),
                        instagram_url=social_links.get('instagram', ''),
                        youtube_url=social_links.get('youtube', ''),
                        metadata=metadata_json,
                        tech_stack=json.dumps(tech_stack),
                        is_wordpress=metadata.get('is_wordpress', False),
                        wordpress_version=metadata.get('wordpress_version', None),
                        has_elementor=metadata.get('has_elementor', False)
                    ))

                    logger.debug(f"Successfully updated domain {domain_id} with metadata and status 'completed'")
                    domains_successful += 1

        except Exception as db_error:
            # Handle database update errors
            error_message = str(db_error)
            logger.error(f"Error updating domain {domain_id} with metadata: {error_message}")
            logger.debug(traceback.format_exc())
            await handle_domain_error(domain_id, error_message)

    # Log completion statistics
    logger.debug("--------------------------------------------------")
    logger.debug(f"DOMAIN PROCESSING JOB {job_id} COMPLETE")
    logger.debug(f"Processed: {domains_processed} domains, Successful: {domains_successful}")
    logger.debug("--------------------------------------------------")

async def handle_domain_error(domain_id, error_message):
    """
    Helper function to update domain status to error.
    Uses a separate session to ensure error updates succeed even if main processing fails.
    """
    try:
        async with get_background_session() as error_session:
            # Set Supavisor options
            try:
                logger.debug("Setting session options for error handling session")

                # Required Supavisor parameters
                options = [
                    ("SET statement_timeout = 90000", "90 seconds timeout"),
                    ("SET idle_in_transaction_session_timeout = 120000", "120 seconds idle timeout"),
                    ("SET statement_cache_size = 0", "Required for Supavisor compatibility")
                ]

                for sql, description in options:
                    set_option = text(sql)
                    set_option = set_option.execution_options(prepared=False)
                    await error_session.execute(set_option)
                    logger.debug(f"Set session option: {description}")
            except Exception as e:
                logger.error(f"Error setting session options for error handling: {str(e)}")
                logger.debug(traceback.format_exc())

            async with error_session.begin():
                error_query = text("""
                    UPDATE domains
                    SET status = 'error',
                        last_error = :error,
                        updated_at = NOW()
                    WHERE id = :domain_id
                """)

                error_query = error_query.execution_options(prepared=False)

                await error_session.execute(
                    error_query.bindparams(domain_id=domain_id, error=error_message)
                )

                logger.info(f"Updated domain {domain_id} status to 'error' with message: {error_message}")
    except Exception as e:
        logger.error(f"Failed to update domain status after error: {str(e)}")
        logger.debug(traceback.format_exc())

def setup_domain_scheduler():
    """Set up the scheduler with the domain processing job"""
    logger.info("Setting up domain processing scheduler")

    # Debug scheduler state before setup
    logger.info(f"Scheduler state before setup: Running={scheduler.running}, Jobs={len(scheduler.get_jobs())}")

    # Add job to process pending domains every 1 minute
    job = scheduler.add_job(
        process_pending_domains,
        IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES),
        id="process_pending_domains",
        replace_existing=True,
        kwargs={"limit": settings.SCHEDULER_BATCH_SIZE}  # Use batch size from settings
    )

    logger.info(f"Added job with ID: {job.id}, interval: {settings.SCHEDULER_INTERVAL_MINUTES} minute(s), batch size: {settings.SCHEDULER_BATCH_SIZE}")

    # Start the scheduler if it's not running
    if not scheduler.running:
        scheduler.start()
        logger.info("Domain processing scheduler started")

    # Debug scheduler state after setup - only AFTER the scheduler is started
    logger.info(f"Scheduler state after setup: Running={scheduler.running}, Jobs={len(scheduler.get_jobs())}")
    for job in scheduler.get_jobs():
        logger.info(f"Job {job.id} scheduled, Next run: {job.next_run_time}")

    logger.info("Domain processing scheduler set up successfully")
    return scheduler

def shutdown_domain_scheduler():
    """Shutdown the scheduler gracefully"""
    logger.info("Shutting down domain processing scheduler")
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Domain processing scheduler shut down successfully")
    else:
        logger.info("Domain processing scheduler was not running")
