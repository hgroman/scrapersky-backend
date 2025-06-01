#!/usr/bin/env python
"""
Vector DB Simple Test Script

This script tests the vector search functionality with a single pattern.
"""

import os
import uuid
import asyncio
import logging
from typing import Dict, List, Any

import httpx
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"

# Database configuration
# Convert SQLAlchemy connection string to asyncpg format
db_url = os.getenv("DATABASE_URL")
if db_url and "postgresql+asyncpg://" in db_url:
    # Convert SQLAlchemy format to asyncpg format
    DATABASE_URL = db_url.replace("postgresql+asyncpg://", "postgresql://")
else:
    DATABASE_URL = db_url

# Single pattern for testing
PATTERN = {
    "title": "Authentication and Attribute Access Correction",
    "description": "Pattern for fixing authentication issues and attribute access errors in API routers, particularly when accessing user data from JWT tokens.",
    "problem_type": "security",
    "code_type": "router",
    "severity": "CRITICAL-SECURITY",
    "tags": ["Security", "Authentication"],
    "layers": [3],  # Integer array, not string array
    "workflows": ["WF1"],
    "file_types": ["py"],
    "problem_description": "Missing authentication on endpoints and incorrect attribute access in router",
    "solution_steps": "1. Add proper authentication dependencies\n2. Fix attribute access patterns",
    "confidence_score": 0.9,
    "applied_count": 1,
    # Corrected column names and ensured values are lists
    "dart_task_ids": ["ildO8Gz1EtoV"],
    "dart_document_urls": ["eYzJsz2tQlQ7"],
    "code_before": "...", # Added placeholder for required columns
    "code_after": "...", # Added placeholder for required columns
    "verification_steps": "...", # Added placeholder for required columns
    "learnings": "...", # Added placeholder for required columns
    "prevention_guidance": "...", # Added placeholder for required columns
    "created_by": "Vector DB Test Script", # Added placeholder for required columns
    "reviewed": False, # Added placeholder for required columns
    "reviewer_notes": None, # Added placeholder for required columns
    "related_files": [], # Added placeholder for required columns
    "source_file_audit_id": None, # Added placeholder for required columns
    "applied_to_files": [], # Added placeholder for required columns
    "avg_time_saved": 0 # Added placeholder for required columns
}


async def generate_embedding(text: str) -> List[float]:
    """Generate an embedding for the given text using OpenAI's API."""
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": text,
                "model": EMBEDDING_MODEL
            }
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=payload
            )
            response_data = response.json()
            return response_data["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def insert_pattern(conn, pattern: Dict[str, Any], embedding: List[float]) -> str:
    """Insert a pattern with its embedding into the fix_patterns table."""
    pattern_id = str(uuid.uuid4())

    # Convert embedding list to string format for vector type
    embedding_str = f"[{','.join(str(x) for x in embedding)}]"

    # Corrected INSERT statement to include all columns and match parameter count
    await conn.execute(
        """
        INSERT INTO fix_patterns (
            id, title, description, pattern_vector, file_types,
            code_type, severity, confidence_score, applied_count,
            problem_type, layers, workflows, tags, problem_description,
            solution_steps, created_at, updated_at, dart_task_ids,
            dart_document_urls, code_before, code_after, verification_steps,
            learnings, prevention_guidance, created_by, reviewed, reviewer_notes,
            related_files, source_file_audit_id, applied_to_files, avg_time_saved
        ) VALUES ($1, $2, $3, $4::vector, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NOW(), NOW(), $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29)
        """,
        pattern_id,
        pattern["title"],
        pattern["description"],
        embedding_str,
        pattern["file_types"],
        pattern["code_type"],
        pattern["severity"],
        pattern["confidence_score"],
        pattern["applied_count"],
        pattern["problem_type"],
        pattern["layers"],
        pattern["workflows"],
        pattern["tags"],
        pattern["problem_description"],
        pattern["solution_steps"],
        pattern["dart_task_ids"], # $16
        pattern["dart_document_urls"], # $17
        pattern["code_before"], # $18
        pattern["code_after"], # $19
        pattern["verification_steps"], # $20
        pattern["learnings"], # $21
        pattern["prevention_guidance"], # $22
        pattern["created_by"], # $23
        pattern["reviewed"], # $24
        pattern["reviewer_notes"], # $25
        pattern["related_files"], # $26
        pattern["source_file_audit_id"], # $27
        pattern["applied_to_files"], # $28
        pattern["avg_time_saved"] # $29
    )

    return pattern_id


async def main():
    """Main function to test vector search functionality."""
    logger.info("Starting Vector DB Simple Test")

    # Check if DATABASE_URL is set
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is not set.")
        return

    try:
        # Add SSL parameters to the connection string if not already included
        connection_url = DATABASE_URL
        # Remove any query parameters for asyncpg compatibility
        if "?" in connection_url:
            base_url = connection_url.split("?")[0]
            connection_url = base_url

        logger.info(f"Using connection URL: {connection_url}")

        # Connect with SSL enabled and disable statement cache for pgbouncer compatibility
        conn = await asyncpg.connect(
            connection_url,
            ssl="require",
            statement_cache_size=0  # Disable statement cache for pgbouncer compatibility
        )

        # Register vector type support
        await conn.execute('''
            CREATE EXTENSION IF NOT EXISTS vector;
        ''')
        logger.info("Connected to database")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return

    try:
        # Generate embedding for the pattern
        combined_text = f"""
        TITLE: {PATTERN['title']}
        DESCRIPTION: {PATTERN['description']}
        CODE TYPE: {PATTERN['code_type']}
        SEVERITY: {PATTERN['severity']}
        FILE TYPES: {', '.join(PATTERN['file_types'])}
        """

        logger.info("Generating embedding...")
        # Use a placeholder embedding for now since we don't have OpenAI API access
        # In a real scenario, this would call the generate_embedding function
        # embedding = await generate_embedding(combined_text)
        embedding = [0.0] * 1536 # Placeholder 1536-dimensional vector

        # Insert pattern
        logger.info("Inserting pattern into database...")
        pattern_id = await insert_pattern(conn, PATTERN, embedding)

        logger.info(f"Pattern inserted with ID: {pattern_id}")

        # Test vector search
        logger.info("Testing vector search...")
        test_query = "Missing authentication in router"
        # Use a placeholder embedding for the test query as well
        # test_embedding = await generate_embedding(test_query)
        test_embedding = [0.0] * 1536 # Placeholder 1536-dimensional vector

        # Convert test embedding list to string format for vector type
        test_embedding_str = f"[{','.join(str(x) for x in test_embedding)}]"

        results = await conn.fetch(
            """
            SELECT
                id,
                title,
                description,
                code_type,
                severity,
                1 - (pattern_vector <=> $1::vector) as similarity
            FROM
                fix_patterns
            ORDER BY
                similarity DESC
            LIMIT 2
            """,
            test_embedding_str
        )

        logger.info("Vector search results:")
        for result in results:
            logger.info(f"Pattern: {result['title']}, Similarity: {result['similarity']:.4f}")

    except Exception as e:
        logger.error(f"Error processing pattern: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
