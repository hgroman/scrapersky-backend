"""
Database Insertion Test Script

This script tests the database insertion part of domain processing,
following all architectural standards for background tasks.
"""

import asyncio
import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Correct import path
from src.session.async_session import get_background_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db-insertion-test')

# Mock data generation
def create_mock_metadata() -> Dict[str, Any]:
    """Create realistic-looking mock metadata for testing"""
    return {
        "title": "Test Company | Digital Solutions",
        "description": "Leading provider of digital transformation solutions for enterprise businesses.",
        "is_wordpress": True,
        "url": "https://testcompany.com",
        "phone_numbers": ["(555) 123-4567", "1-800-555-9876"],
        "email_addresses": ["contact@testcompany.com", "support@testcompany.com"],
        "social_media": {
            "twitter": "https://twitter.com/testcompany",
            "linkedin": "https://linkedin.com/company/testcompany"
        },
        "meta_tags": {
            "keywords": "digital solutions, enterprise software, cloud services"
        }
    }

# Database insertion - follows architectural principles
async def update_domain_with_metadata(domain_id: str, metadata: Dict[str, Any]) -> bool:
    """
    Update a domain record with extracted metadata.

    Args:
        domain_id: UUID of the domain to update
        metadata: Dictionary containing extracted metadata

    Returns:
        True if update was successful, False otherwise
    """
    try:
        # Get background session following architectural standards
        async with get_background_session() as session:
            # Set Supavisor options
            try:
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
                    await session.execute(set_option)
                    logger.debug(f"Set session option: {description}")
            except Exception as e:
                logger.error(f"Error setting session options: {str(e)}")
                return False

            # Begin transaction (background tasks manage their own transactions)
            async with session.begin():
                # Prepare SQL query with execution options for Supavisor
                query = text("""
                UPDATE domains
                SET status = 'test-processed',
                    title = :title,
                    description = :description,
                    is_wordpress = :is_wordpress,
                    phone_numbers = :phone_numbers,
                    email_addresses = :email_addresses,
                    domain_metadata = :metadata,
                    updated_at = NOW()
                WHERE id = :id
                RETURNING id, domain, status
                """)

                # Set execution options for Supavisor compatibility
                query = query.execution_options(prepared=False)

                # Execute query with parameters
                result = await session.execute(query, {
                    'id': domain_id,
                    'title': metadata.get('title', ''),
                    'description': metadata.get('description', ''),
                    'is_wordpress': metadata.get('is_wordpress', False),
                    'phone_numbers': metadata.get('phone_numbers', []),
                    'email_addresses': metadata.get('email_addresses', []),
                    'metadata': metadata
                })

                # Get the returned row (will be None if domain_id doesn't exist)
                returned_row = result.fetchone()

                if returned_row:
                    logger.info(f"Successfully updated domain {returned_row.domain} with status {returned_row.status}")
                    return True
                else:
                    logger.warning(f"No domain found with ID {domain_id}")
                    return False

    except Exception as e:
        logger.error(f"Error updating domain {domain_id}: {str(e)}")

        # Handle error recording in separate session/transaction
        try:
            async with get_background_session() as error_session:
                # Set Supavisor options for error session
                try:
                    for sql, description in options:
                        set_option = text(sql)
                        set_option = set_option.execution_options(prepared=False)
                        await error_session.execute(set_option)
                except Exception:
                    pass

                async with error_session.begin():
                    error_query = text("""
                    UPDATE domains
                    SET status = 'test-error',
                        last_error = :error_msg,
                        updated_at = NOW()
                    WHERE id = :id
                    """)

                    error_query = error_query.execution_options(prepared=False)

                    await error_session.execute(error_query, {
                        'id': domain_id,
                        'error_msg': str(e)
                    })
        except Exception as error_update_error:
            logger.error(f"Failed to record error state: {str(error_update_error)}")
        return False

# Main test function
async def run_test(domain_id: Optional[str] = None):
    """
    Run the database insertion test.

    Args:
        domain_id: Optional domain ID to test with. If not provided,
                  will create a new test domain.
    """
    # Create test domain if none provided
    if not domain_id:
        domain_id = await create_test_domain()
        if not domain_id:
            logger.error("Failed to create test domain. Aborting test.")
            return

    # Generate mock metadata
    metadata = create_mock_metadata()
    logger.info(f"Generated mock metadata for testing: {json.dumps(metadata, indent=2)}")

    # Update domain with metadata
    logger.info(f"Updating domain {domain_id} with mock metadata...")
    result = await update_domain_with_metadata(domain_id, metadata)

    # Check result
    if result:
        logger.info("✅ TEST PASSED: Successfully updated domain with metadata")
    else:
        logger.error("❌ TEST FAILED: Failed to update domain with metadata")

    # Verify the update in database
    await verify_domain_update(domain_id)

# Helper to create a test domain
async def create_test_domain() -> Optional[str]:
    """Create a test domain and return its ID"""
    try:
        async with get_background_session() as session:
            async with session.begin():
                query = text("""
                INSERT INTO domains (id, tenant_id, domain, status, created_at, updated_at)
                VALUES (:id, '550e8400-e29b-41d4-a716-446655440000', :domain, 'test-pending', NOW(), NOW())
                RETURNING id
                """)

                query = query.execution_options(prepared=False)

                import uuid
                domain_id = str(uuid.uuid4())
                result = await session.execute(query, {
                    'id': domain_id,
                    'domain': f'test-domain-{domain_id[:8]}.com'
                })

                returned_id = result.scalar_one()
                logger.info(f"Created test domain with ID: {returned_id}")
                return returned_id
    except Exception as e:
        logger.error(f"Error creating test domain: {str(e)}")
        return None

# Helper to verify the domain was updated
async def verify_domain_update(domain_id: str):
    """Verify the domain update by querying the database"""
    try:
        async with get_background_session() as session:
            query = text("""
            SELECT id, domain, status, title, description, is_wordpress, updated_at
            FROM domains
            WHERE id = :id
            """)

            query = query.execution_options(prepared=False)
            result = await session.execute(query, {'id': domain_id})
            domain = result.mappings().one_or_none()

            if domain:
                logger.info("Domain state after update:")
                for key, value in dict(domain).items():
                    logger.info(f"  {key}: {value}")
            else:
                logger.error(f"Domain {domain_id} not found in database")
    except Exception as e:
        logger.error(f"Error verifying domain update: {str(e)}")

# Command-line entry point
if __name__ == "__main__":
    domain_id = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_test(domain_id))
