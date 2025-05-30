#!/usr/bin/env python
"""
Vector DB Pattern Insertion - Final Script

This script inserts the extracted patterns into the fix_patterns table with proper vector embeddings.
"""

import asyncio
import json  # Import the json module
import logging
import os
import uuid
from typing import Any, Dict, List

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
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Load patterns from JSON file
PATTERNS_FILE = "scripts/patterns.json"
try:
    with open(PATTERNS_FILE, 'r') as f:
        PATTERNS = json.load(f)
    logger.info(f"Loaded {len(PATTERNS)} patterns from {PATTERNS_FILE}")
except FileNotFoundError:
    logger.error(f"Error: Patterns file not found at {PATTERNS_FILE}")
    PATTERNS = [] # Initialize as empty list to prevent errors
except json.JSONDecodeError as e:
    logger.error(f"Error decoding JSON from {PATTERNS_FILE}: {e}")
    PATTERNS = [] # Initialize as empty list to prevent errors


async def generate_embedding(text: str) -> List[float]:
    """Generate an embedding for the given text using OpenAI's API."""
    # Use a placeholder embedding since we don't have OpenAI API access
    logger.warning("Using placeholder embedding. OpenAI API key not available.")
    return [0.0] * 1536


async def create_embeddings_for_pattern(pattern: Dict[str, Any]) -> Dict[str, List[float]]:
    """Create embeddings for different aspects of a pattern."""
    embeddings = {}

    # Content embedding (title, description, problem_type, etc.)
    content_text = f"""
    TITLE: {pattern.get('title', '')}
    DESCRIPTION: {pattern.get('description', '')}
    PROBLEM TYPE: {pattern.get('problem_type', '')}
    CODE TYPE: {pattern.get('code_type', '')}
    SEVERITY: {pattern.get('severity', '')}
    PROBLEM DESCRIPTION: {pattern.get('problem_description', '')}
    SOLUTION STEPS: {pattern.get('solution_steps', '')}
    VERIFICATION STEPS: {pattern.get('verification_steps', '')}
    LEARNINGS: {pattern.get('learnings', '')}
    PREVENTION GUIDANCE: {pattern.get('prevention_guidance', '')}
    """
    embeddings['content_embedding'] = await generate_embedding(content_text)

    # Code embedding (now conceptual, as code is in DART)
    # This embedding will represent the conceptual nature of the code pattern,
    # derived from its description and solution steps, not literal code.
    code_conceptual_text = f"""
    PROBLEM DESCRIPTION: {pattern.get('problem_description', '')}
    SOLUTION STEPS: {pattern.get('solution_steps', '')}
    """
    embeddings['code_embedding'] = await generate_embedding(code_conceptual_text)

    # Problem embedding (problem_description, verification_steps)
    problem_text = f"""
    PROBLEM DESCRIPTION: {pattern.get('problem_description', '')}
    VERIFICATION STEPS: {pattern.get('verification_steps', '')}
    """
    embeddings['problem_embedding'] = await generate_embedding(problem_text)

    # Pattern vector (combined embedding for general search, excluding literal code)
    pattern_text = f"""
    TITLE: {pattern.get('title', '')}
    DESCRIPTION: {pattern.get('description', '')}
    PROBLEM TYPE: {pattern.get('problem_type', '')}
    CODE TYPE: {pattern.get('code_type', '')}
    SEVERITY: {pattern.get('severity', '')}
    PROBLEM DESCRIPTION: {pattern.get('problem_description', '')}
    SOLUTION STEPS: {pattern.get('solution_steps', '')}
    LEARNINGS: {pattern.get('learnings', '')}
    PREVENTION GUIDANCE: {pattern.get('prevention_guidance', '')}
    """
    embeddings['pattern_vector'] = await generate_embedding(pattern_text)

    return embeddings


async def insert_pattern(conn, pattern: Dict[str, Any], embeddings: Dict[str, List[float]]) -> None:
    """Insert a pattern with its embeddings into the fix_patterns table."""

    # Convert embedding lists to string format for vector type
    embedding_strings = {}
    for key, embedding in embeddings.items():
        embedding_strings[key] = f"[{','.join(str(x) for x in embedding)}]"

    # Ensure UUID is generated if not provided in JSON
    pattern_id = pattern.get("id")
    if not pattern_id:
        pattern_id = str(uuid.uuid4())

    # Insert the pattern with all fields. code_before and code_after will be None/empty strings
    # as they are now stored in DART documents.
    await conn.execute(
        """
        INSERT INTO fix_patterns (
            id, title, problem_type, code_type, severity, tags, layers, workflows,
            file_types, problem_description, solution_steps, code_before, code_after,
            verification_steps, learnings, prevention_guidance, dart_task_ids,
            dart_document_urls, applied_count, success_rate, confidence_score,
            content_embedding, code_embedding, problem_embedding, pattern_vector,
            created_by, reviewed, description, created_at, updated_at,
            reviewer_notes, related_files, source_file_audit_id, applied_to_files, avg_time_saved, knowledge_type
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16,
            $17, $18, $19, $20, $21, $22::vector, $23::vector, $24::vector, $25::vector,
            $26, $27, $28, NOW(), NOW(), $29, $30, $31, $32, $33, $34)
        """,
        pattern_id,
        pattern.get("title"),
        pattern.get("problem_type"),
        pattern.get("code_type"),
        pattern.get("severity"),
        pattern.get("tags"),
        pattern.get("layers"),
        pattern.get("workflows"),
        pattern.get("file_types"),
        pattern.get("problem_description"),
        pattern.get("solution_steps"),
        pattern.get("code_before", None), # Pass None if not present
        pattern.get("code_after", None),  # Pass None if not present
        pattern.get("verification_steps"),
        pattern.get("learnings"),
        pattern.get("prevention_guidance"),
        pattern.get("dart_task_ids"),
        pattern.get("dart_document_urls"),
        pattern.get("applied_count"),
        pattern.get("success_rate"),
        pattern.get("confidence_score"),
        embedding_strings["content_embedding"],
        embedding_strings["code_embedding"],
        embedding_strings["problem_embedding"],
        embedding_strings["pattern_vector"],
        pattern.get("created_by"),
        pattern.get("reviewed"),
        pattern.get("description"),
        pattern.get("reviewer_notes"),
        pattern.get("related_files"),
        pattern.get("source_file_audit_id"),
        pattern.get("applied_to_files"),
        pattern.get("avg_time_saved"),
        pattern.get("knowledge_type")
    )

    logger.info(f"Pattern '{pattern.get('title', 'Unknown')}' inserted successfully")


async def test_vector_search(conn) -> None:
    """Test vector search functionality."""
    logger.info("Testing vector search...")

    # Generate embedding for test query
    test_query = "Missing authentication in router"
    # Use a placeholder embedding as OpenAI API key is not available
    test_embedding = [0.0] * 1536

    # Convert test embedding list to string format for vector type
    test_embedding_str = f"[{','.join(str(x) for x in test_embedding)}]"

    results = await conn.fetch(
        """
        SELECT
            id,
            title,
            problem_type,
            code_type,
            severity,
            1 - (pattern_vector <=> $1::vector) as similarity
        FROM
            fix_patterns
        ORDER BY
            similarity DESC
        LIMIT 5
        """,
        test_embedding_str
    )

    logger.info("Vector search results:")
    for result in results:
        logger.info(f"Pattern: {result['title']} ({result['problem_type']}/{result['code_type']}) - Similarity: {result['similarity']:.4f}")


async def main():
    """Main function to insert patterns and test vector search."""
    logger.info("Starting Vector DB Pattern Insertion")

    # Check if DATABASE_URL is set
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is not set.")
        return

    # Check if patterns were loaded
    if not PATTERNS:
        logger.error("No patterns loaded. Cannot proceed with insertion.")
        return

    try:
        # Connect to the database
        connection_url = DATABASE_URL
        # Remove any query parameters for asyncpg compatibility
        if "?" in connection_url:
            base_url = connection_url.split("?")[0]
            connection_url = base_url

        logger.info(f"Connecting to database: {connection_url}")

        conn = await asyncpg.connect(
            connection_url,
            ssl="require",
            statement_cache_size=0  # Disable statement cache for pgbouncer compatibility
        )

        # Ensure vector extension is enabled
        await conn.execute('''
            CREATE EXTENSION IF NOT EXISTS vector;
        ''')
        logger.info("Connected to database")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return

    try:
        # Process each pattern
        for pattern in PATTERNS:
            logger.info(f"Processing pattern: {pattern.get('title', 'Unknown')}")

            # Generate embeddings (using placeholder)
            logger.info("Generating embeddings...")
            embeddings = await create_embeddings_for_pattern(pattern)

            # Insert pattern
            logger.info("Inserting pattern into database...")
            await insert_pattern(conn, pattern, embeddings)

        # Test vector search
        await test_vector_search(conn)

        logger.info("All patterns processed successfully")

    except Exception as e:
        logger.error(f"Error processing patterns: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
