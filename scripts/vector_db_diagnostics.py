#!/usr/bin/env python
"""
Vector DB Diagnostics Script

This script runs diagnostic queries on the Supabase vector database
to troubleshoot the "Similarity: nan" issue.
"""

import os
import asyncio
import logging
from typing import List, Dict, Any

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

# Database configuration
# Convert SQLAlchemy connection string to asyncpg format
db_url = os.getenv("DATABASE_URL")
if db_url and "postgresql+asyncpg://" in db_url:
    # Convert SQLAlchemy format to asyncpg format
    DATABASE_URL = db_url.replace("postgresql+asyncpg://", "postgresql://")
else:
    DATABASE_URL = db_url

async def run_diagnostics():
    """Run diagnostic queries on the vector database."""
    logger.info("Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # 1. Check pgvector extension version
        logger.info("Checking pgvector extension version...")
        version = await conn.fetchval(
            "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
        )
        logger.info(f"pgvector extension version: {version}")
        
        # 2. Check if project_docs table exists and has data
        logger.info("Checking project_docs table...")
        try:
            count = await conn.fetchval("SELECT COUNT(*) FROM public.project_docs;")
            logger.info(f"Number of documents in project_docs: {count}")
            
            if count > 0:
                # Get a sample document
                sample = await conn.fetchrow(
                    "SELECT id, title, embedding FROM public.project_docs LIMIT 1;"
                )
                logger.info(f"Sample document: ID={sample['id']}, Title={sample['title']}")
                
                # Check embedding length
                embedding_str = sample['embedding']
                if embedding_str:
                    # Extract first few and last few values to avoid printing the entire vector
                    embedding_preview = f"[{embedding_str[:50]}...{embedding_str[-50:]}]"
                    logger.info(f"Sample embedding preview: {embedding_preview}")
                    
                    # Calculate L2 norm of the embedding
                    l2_norm = await conn.fetchval(
                        "SELECT sqrt(embedding <#> embedding) FROM public.project_docs WHERE id = $1;",
                        sample['id']
                    )
                    logger.info(f"L2 norm of sample embedding: {l2_norm}")
                else:
                    logger.warning("Sample embedding is NULL or empty")
            else:
                logger.warning("No documents found in project_docs table")
        except Exception as e:
            logger.error(f"Error checking project_docs table: {e}")
        
        # 3. Test cosine distance operator with simple vectors
        logger.info("Testing cosine distance operator...")
        try:
            same_vectors = await conn.fetchval("SELECT '[1,1,1]'::vector <=> '[1,1,1]'::vector;")
            logger.info(f"Cosine distance between identical vectors: {same_vectors}")
            
            diff_vectors = await conn.fetchval("SELECT '[1,2,3]'::vector <=> '[4,5,6]'::vector;")
            logger.info(f"Cosine distance between different vectors: {diff_vectors}")
            
            similarity = 1 - diff_vectors
            logger.info(f"Similarity between different vectors: {similarity}")
        except Exception as e:
            logger.error(f"Error testing cosine distance operator: {e}")
        
        # 4. Test search_docs function if it exists
        logger.info("Testing search_docs function...")
        try:
            search_results = await conn.fetch("SELECT * FROM search_docs('test pattern', 0.5) LIMIT 3;")
            if search_results:
                for i, result in enumerate(search_results):
                    logger.info(f"Search result {i+1}: Title={result['title']}, Similarity={result['similarity']}")
                    
                    # Check for NaN in similarity
                    if result['similarity'] != result['similarity']:  # NaN check
                        logger.error(f"NaN detected in similarity for document: {result['title']}")
            else:
                logger.warning("No results returned from search_docs function")
        except Exception as e:
            logger.error(f"Error testing search_docs function: {e}")
        
        # 5. Check for NaN values in embeddings
        logger.info("Checking for NaN values in embeddings...")
        try:
            # This is a simplified check - a more thorough check would parse the vector and check each element
            nan_check = await conn.fetch(
                """
                SELECT id, title FROM public.project_docs 
                WHERE embedding::text LIKE '%nan%' OR embedding::text LIKE '%NaN%'
                LIMIT 5;
                """
            )
            
            if nan_check:
                logger.error(f"Found {len(nan_check)} documents with potential NaN values in embeddings:")
                for doc in nan_check:
                    logger.error(f"  - ID={doc['id']}, Title={doc['title']}")
            else:
                logger.info("No obvious NaN values found in embeddings")
        except Exception as e:
            logger.error(f"Error checking for NaN values: {e}")
            
    finally:
        await conn.close()
        logger.info("Diagnostics complete")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
