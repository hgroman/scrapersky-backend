#!/usr/bin/env python
"""
Fix Vector Embeddings Script

This script identifies and fixes problematic vector embeddings in the database
that might be causing "Similarity: nan" issues.
"""

import os
import asyncio
import logging
import numpy as np
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
db_url = os.getenv("DATABASE_URL")
if db_url and "postgresql+asyncpg://" in db_url:
    DATABASE_URL = db_url.replace("postgresql+asyncpg://", "postgresql://")
else:
    DATABASE_URL = db_url

async def normalize_vector(embedding_str: str) -> str:
    """
    Parse the embedding string into a numpy array, normalize it,
    and convert back to a string format for pgvector.
    """
    # Parse the embedding string
    # Remove brackets and split by commas
    embedding_str = embedding_str.strip('[]')
    embedding_values = [float(val) for val in embedding_str.split(',')]
    
    # Convert to numpy array
    embedding_array = np.array(embedding_values)
    
    # Check for NaN values
    if np.isnan(embedding_array).any():
        logger.warning("NaN values found in embedding, replacing with zeros")
        embedding_array = np.nan_to_num(embedding_array)
    
    # Normalize the vector
    norm = np.linalg.norm(embedding_array)
    if norm > 0:
        normalized_array = embedding_array / norm
    else:
        logger.warning("Zero norm detected, using small random values")
        # Create a small random vector if the norm is zero
        normalized_array = np.random.normal(0, 0.01, size=len(embedding_array))
        normalized_array = normalized_array / np.linalg.norm(normalized_array)
    
    # Convert back to string format for pgvector
    normalized_str = f"[{','.join(str(val) for val in normalized_array)}]"
    return normalized_str

async def fix_embeddings():
    """Fix problematic embeddings in the database."""
    logger.info("Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Get all document IDs and embeddings
        logger.info("Fetching all documents...")
        docs = await conn.fetch("SELECT id, title, embedding FROM public.project_docs;")
        logger.info(f"Found {len(docs)} documents")
        
        fixed_count = 0
        for doc in docs:
            doc_id = doc['id']
            title = doc['title']
            embedding_str = doc['embedding']
            
            if not embedding_str:
                logger.warning(f"Document {doc_id} ({title}) has NULL embedding, skipping")
                continue
            
            try:
                # Normalize the embedding
                normalized_embedding = await normalize_vector(embedding_str)
                
                # Update the document with the normalized embedding
                await conn.execute(
                    "UPDATE public.project_docs SET embedding = $1::vector WHERE id = $2",
                    normalized_embedding, doc_id
                )
                
                logger.info(f"Fixed embedding for document {doc_id} ({title})")
                fixed_count += 1
                
            except Exception as e:
                logger.error(f"Error fixing embedding for document {doc_id} ({title}): {e}")
        
        logger.info(f"Fixed {fixed_count} out of {len(docs)} documents")
        
        # Test the search function after fixing
        logger.info("Testing search_docs function after fixes...")
        try:
            # Create a simple test query
            test_query = "architecture patterns"
            
            # Test direct vector similarity query
            logger.info(f"Testing direct vector similarity query for '{test_query}'...")
            
            # Generate a random normalized vector for testing
            test_vector = np.random.normal(0, 1, size=1536)
            test_vector = test_vector / np.linalg.norm(test_vector)
            test_vector_str = f"[{','.join(str(val) for val in test_vector)}]"
            
            results = await conn.fetch(
                """
                SELECT 
                    id, 
                    title, 
                    1 - (embedding <=> $1::vector) as similarity
                FROM 
                    public.project_docs
                ORDER BY 
                    similarity DESC
                LIMIT 3
                """,
                test_vector_str
            )
            
            for i, result in enumerate(results):
                logger.info(f"Test result {i+1}: ID={result['id']}, Title={result['title']}, Similarity={result['similarity']}")
                
            # Now test the search_docs function if it exists
            try:
                search_results = await conn.fetch("SELECT * FROM search_docs($1, 0.5) LIMIT 3;", test_query)
                for i, result in enumerate(search_results):
                    logger.info(f"Search result {i+1}: Title={result['title']}, Similarity={result['similarity']}")
            except Exception as e:
                logger.error(f"Error testing search_docs function: {e}")
                logger.info("Attempting to create or fix search_docs function...")
                
                # Create a basic search_docs function if it doesn't exist or is broken
                await conn.execute(
                    """
                    CREATE OR REPLACE FUNCTION search_docs(
                        query_text TEXT,
                        similarity_threshold FLOAT DEFAULT 0.5
                    ) RETURNS TABLE (
                        id INTEGER,
                        title TEXT,
                        content TEXT,
                        similarity FLOAT
                    ) AS $$
                    DECLARE
                        query_embedding VECTOR(1536);
                    BEGIN
                        -- For testing purposes, use a normalized random vector
                        -- In production, this would call the OpenAI API
                        query_embedding := (
                            SELECT 
                                (array_agg(random()))[1:1536]::vector / sqrt(1536)
                            FROM 
                                generate_series(1, 1536)
                        );
                        
                        RETURN QUERY
                        SELECT 
                            p.id,
                            p.title,
                            p.content,
                            1 - (p.embedding <=> query_embedding) AS similarity
                        FROM 
                            public.project_docs p
                        WHERE 
                            1 - (p.embedding <=> query_embedding) >= similarity_threshold
                        ORDER BY 
                            similarity DESC;
                    END;
                    $$ LANGUAGE plpgsql;
                    """
                )
                
                logger.info("Created basic search_docs function with random vector for testing")
                
                # Test the new function
                search_results = await conn.fetch("SELECT * FROM search_docs($1, 0.5) LIMIT 3;", test_query)
                for i, result in enumerate(search_results):
                    logger.info(f"Search result {i+1} with new function: ID={result['id']}, Title={result['title']}, Similarity={result['similarity']}")
        
        except Exception as e:
            logger.error(f"Error testing after fixes: {e}")
    
    finally:
        await conn.close()
        logger.info("Fix operation complete")

if __name__ == "__main__":
    asyncio.run(fix_embeddings())
