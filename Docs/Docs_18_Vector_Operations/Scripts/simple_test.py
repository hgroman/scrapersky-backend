#!/usr/bin/env python
"""
Vector DB Simple Test Script (Updated Version)

This script tests the vector search functionality with proper OpenAI embeddings.
It demonstrates how to generate embeddings and perform semantic searches against
the Supabase vector database.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List

import asyncpg
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"

# Database configuration
# Convert SQLAlchemy connection string to asyncpg format
db_url = os.getenv("DATABASE_URL")
if db_url and "postgresql+asyncpg://" in db_url:
    # Convert SQLAlchemy format to asyncpg format
    DATABASE_URL = db_url.replace("postgresql+asyncpg://", "postgresql://")
else:
    DATABASE_URL = db_url

async def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding for the given text using OpenAI's API.
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        A list of floats representing the embedding
    """
    try:
        response = openai.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        # Fallback to placeholder embedding if OpenAI API fails
        logger.warning("Using placeholder embedding as fallback")
        return [0.0] * 1536

async def search_documents(conn: asyncpg.Connection, query: str, threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Search for documents similar to the query.
    
    Args:
        conn: Database connection
        query: The query text
        threshold: Similarity threshold (0-1)
        
    Returns:
        A list of documents with similarity scores
    """
    # Generate embedding for the query
    query_embedding = await generate_embedding(query)
    
    # Convert embedding to string format for pgvector
    embedding_str = f"[{','.join(map(str, query_embedding))}]"
    
    # Perform vector search
    results = await conn.fetch(
        """
        SELECT 
            id, 
            title, 
            content,
            1 - (embedding <=> $1::vector) as similarity
        FROM 
            public.project_docs
        WHERE 
            1 - (embedding <=> $1::vector) >= $2
        ORDER BY 
            similarity DESC
        LIMIT 5
        """,
        embedding_str,
        threshold
    )
    
    return [dict(r) for r in results]

async def test_vector_search():
    """Test vector search functionality."""
    logger.info("Connecting to database...")
    conn = await asyncpg.connect(
        DATABASE_URL,
        statement_cache_size=0  # Disable statement cache for pgbouncer compatibility
    )
    
    try:
        # First, try to directly query for the document by title
        logger.info("Checking if v_34-DART_MCP_GUIDE.md exists in project_docs table...")
        direct_check = await conn.fetch(
            """
            SELECT id, title, content FROM public.project_docs 
            WHERE title = 'v_34-DART_MCP_GUIDE.md'
            """
        )
        
        if direct_check:
            logger.info("✅ FOUND: v_34-DART_MCP_GUIDE.md exists in the vector database!")
            logger.info(f"Document ID: {direct_check[0]['id']}")
            logger.info(f"Content preview: {direct_check[0]['content'][:150]}...")
        else:
            logger.info("❌ NOT FOUND: v_34-DART_MCP_GUIDE.md does not exist in the vector database.")
        
        # Test pattern to search for DART MCP related content
        test_pattern = "DART MCP guide integration model context protocol"
        logger.info(f"Testing vector search with pattern: '{test_pattern}'")
        
        # Search for documents
        results = await search_documents(conn, test_pattern)
        
        if results:
            logger.info(f"Found {len(results)} matching documents:")
            for i, doc in enumerate(results):
                logger.info(f"Result {i+1}:")
                logger.info(f"  Title: {doc['title']}")
                logger.info(f"  Similarity: {doc['similarity']}")
                logger.info(f"  Content Preview: {doc['content'][:100]}...")
                logger.info("---")
        else:
            logger.warning("No matching documents found")
            
        # Test the search_docs database function if it exists
        logger.info("Testing search_docs database function specifically for DART MCP guide...")
        try:
            # First search pattern focused on DART MCP
            dart_pattern = "DART MCP integration guide"
            logger.info(f"Searching with pattern: '{dart_pattern}'")
            
            db_results = await conn.fetch(
                "SELECT * FROM search_docs($1, $2) LIMIT 5;",
                dart_pattern,
                0.5
            )
            
            if db_results:
                logger.info(f"Found {len(db_results)} matching documents using search_docs function:")
                for i, doc in enumerate(db_results):
                    logger.info(f"Result {i+1}:")
                    logger.info(f"  Title: {doc['doc_title']}")
                    logger.info(f"  Similarity: {doc['similarity']}")
                    logger.info(f"  Content Preview: {doc['doc_content'][:100]}...") # Add content preview for consistency
                    logger.info("---")
            else:
                logger.warning("No matching documents found using search_docs function")
                
        except Exception as e:
            logger.error(f"Error testing search_docs function: {e}")
            logger.info("You may need to update the search_docs function in the database.")
            
    finally:
        await conn.close()
        logger.info("Test complete")

if __name__ == "__main__":
    asyncio.run(test_vector_search())
