#!/usr/bin/env python
"""
Vector DB Architectural Document Insertion Script

This script inserts key architectural documents into the project_docs table with OpenAI vector embeddings.
It is designed to be a dedicated tool for managing architectural knowledge within the vector database.
"""

import asyncio
import logging
import os
from typing import List
from datetime import datetime, timezone # Added for timestamping

import asyncpg
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
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
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

async def get_vectorization_candidates(conn: asyncpg.Connection) -> List[asyncpg.Record]:
    """Fetch documents from document_registry that need vectorization."""
    logger.info("Fetching candidate documents from document_registry...")
    try:
        records = await conn.fetch(
            """
            SELECT id, title, file_path
            FROM public.document_registry
            WHERE embedding_status = 'queue' OR needs_update = TRUE
            ORDER BY last_seen_at ASC;
            """
        )
        logger.info(f"Found {len(records)} candidate documents to process.")
        return records
    except Exception as e:
        logger.error(f"Error fetching vectorization candidates: {e}")
        return []

async def update_document_registry_status(conn: asyncpg.Connection, registry_id: int, status: str, error_message: str = None) -> None:
    """Update the status of a document in the document_registry table."""
    logger.info(f"Updating document_registry ID {registry_id} with status: {status}")
    try:
        if status == "completed":
            # Get current UTC time for last_embedded_at
            current_time = datetime.now(timezone.utc)
            await conn.execute(
                """
                UPDATE public.document_registry
                SET embedding_status = 'active',  -- Changed from 'completed' to 'active'
                    error_message = NULL,
                    needs_update = FALSE,
                    last_embedded_at = $2
                WHERE id = $1;
                """,
                registry_id, current_time
            )
            logger.info(f"Successfully updated document_registry ID {registry_id} to 'active' at {current_time}.")
        else: # Handle error statuses
            await conn.execute(
                """
                UPDATE public.document_registry
                SET embedding_status = $1,
                    error_message = $2
                WHERE id = $3;
                """,
                status, error_message, registry_id
            )
            logger.info(f"Updated document_registry ID {registry_id} with status '{status}'.")
    except Exception as e:
        logger.error(f"Error updating document_registry for ID {registry_id}: {e}")

async def generate_embedding(text: str) -> List[float]:
    """Generate an embedding for the given text using OpenAI's API."""
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY environment variable is not set. Cannot generate embeddings.")
        return [0.0] * 1536 # Return placeholder if API key is missing
    try:
        # Replace newlines with spaces for better embedding quality
        text = text.replace("\n", " ")
        response = await asyncio.to_thread(
            openai_client.embeddings.create, input=[text], model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return [0.0] * 1536 # Return placeholder on error


async def insert_document(conn: asyncpg.Connection, registry_id: int, title: str, content: str, embedding: List[float]) -> None:
    """Insert or update a document with its embedding into the public.project_docs table using registry_id as the key."""
    embedding_str = f"[{','.join(map(str, embedding))}]"
    try:
        # Check if document already exists by ID
        existing = await conn.fetchrow(
            "SELECT id FROM public.project_docs WHERE id = $1",
            registry_id
        )
        
        if existing:
            # Update existing document by ID, also update title in case it changed
            await conn.execute(
                """
                UPDATE public.project_docs 
                SET title = $1, content = $2, embedding = $3::vector
                WHERE id = $4
                """,
                title, content, embedding_str, registry_id
            )
            logger.info(f"Document ID {registry_id} ('{title}') updated successfully in project_docs.")
        else:
            # Insert new document with ID
            await conn.execute(
                """
                INSERT INTO public.project_docs (id, title, content, embedding)
                VALUES ($1, $2, $3, $4::vector);
                """,
                registry_id, title, content, embedding_str
            )
            logger.info(f"Document ID {registry_id} ('{title}') inserted successfully into project_docs.")
    except Exception as e:
        logger.error(f"Error inserting/updating document ID {registry_id} ('{title}') in project_docs: {e}")


async def test_vector_search(conn: asyncpg.Connection) -> None:
    """Test vector search functionality on project_docs table."""
    logger.info("Testing vector search on project_docs...")

    test_query = "ScraperSky backend architecture overview and compliance"
    test_embedding = await generate_embedding(test_query)

    if test_embedding == [0.0] * 1536:
        logger.warning("Skipping vector search test due to placeholder embedding (API key likely missing).")
        return

    test_embedding_str = f"[{','.join(map(str, test_embedding))}]"

    try:
        results = await conn.fetch(
            """
            SELECT
                title,
                1 - (embedding <=> $1::vector) as similarity
            FROM
                public.project_docs
            ORDER BY
                similarity DESC
            LIMIT 5
            """,
            test_embedding_str
        )

        logger.info("Vector search results from project_docs:")
        if results:
            for result in results:
                logger.info(f"Document: {result['title']} - Similarity: {result['similarity']:.4f}")
        else:
            logger.info("No search results found.")
    except Exception as e:
        logger.error(f"Error during vector search test: {e}")


async def main():
    """Main function to insert documents and test vector search."""
    logger.info("Starting Vector DB Architectural Document Insertion")

    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is not set. Exiting.")
        return

    conn = None
    try:
        connection_url = DATABASE_URL
        # Remove any query parameters for asyncpg compatibility
        if "?" in connection_url:
            base_url = connection_url.split("?")[0]
            connection_url = base_url

        logger.info(f"Connecting to database: {connection_url}")
        conn = await asyncpg.connect(
            connection_url,
            ssl="require",
            statement_cache_size=0 # Disable statement cache for pgbouncer compatibility
        )
        # Ensure vector extension is enabled
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;")
        logger.info("Ensured 'vector' extension is enabled in 'extensions' schema.")

        # Create project_docs table if it doesn't exist
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS public.project_docs (
                id bigserial PRIMARY KEY,
                title TEXT UNIQUE NOT NULL,
                content TEXT,
                embedding vector(1536),
                last_updated_at TIMESTAMPTZ DEFAULT now(),
                metadata JSONB
            );
            """
        )
        logger.info("Ensured 'project_docs' table exists in 'public' schema.")

        # Add error_message column to document_registry if it doesn't exist
        # This is to store any errors encountered during processing by this script
        try:
            await conn.execute(
                """ALTER TABLE public.document_registry ADD COLUMN IF NOT EXISTS error_message TEXT;"""
            )
            logger.info("Ensured 'error_message' column exists in 'document_registry' table.")
        except Exception as e:
            logger.warning(f"Could not ensure 'error_message' column in 'document_registry': {e}. This may be fine if permissions are restricted.")

        candidate_docs = await get_vectorization_candidates(conn)

        if not candidate_docs:
            logger.info("No documents found in the registry that require vectorization at this time.")
        else:
            for doc_record in candidate_docs:
                registry_id = doc_record["id"]
                doc_title = doc_record["title"] # This is typically v_filename.md
                doc_path = doc_record["file_path"]
                
                logger.info(f"Processing document from registry: ID={registry_id}, Title='{doc_title}', Path='{doc_path}'")
                
                if not doc_path: # Should not happen if 2-registry-document-scanner.py is working correctly
                    logger.error(f"Document ID {registry_id}, Title '{doc_title}' has no file_path in registry. Skipping.")
                    await update_document_registry_status(conn, registry_id, "error_missing_path", "File path missing in registry.")
                    continue

                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    embedding = await generate_embedding(content)
                    
                    if embedding != [0.0] * 1536: # Check for placeholder/error embedding
                        await insert_document(conn, registry_id, doc_title, content, embedding) # Inserts/updates in project_docs
                        await update_document_registry_status(conn, registry_id, "completed")
                    else:
                        logger.warning(f"Skipping insertion of '{doc_title}' (ID: {registry_id}) due to placeholder embedding (OpenAI API issue or empty content).")
                        await update_document_registry_status(conn, registry_id, "error_embedding_failed", "Placeholder embedding returned by OpenAI API.")
                
                except FileNotFoundError:
                    logger.error(f"File not found: {doc_path} (ID: {registry_id}, Title: '{doc_title}'). Skipping this document.")
                    await update_document_registry_status(conn, registry_id, "error_file_not_found", f"File not found at path: {doc_path}")
                except Exception as e:
                    logger.error(f"Error processing document ID {registry_id}, Title '{doc_title}': {e}")
                    await update_document_registry_status(conn, registry_id, "error_processing", str(e))

        # Test vector search after potential insertions
        await test_vector_search(conn)
        logger.info("All specified architectural documents processed and vector search tested.")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        if conn:
            await conn.close()
            logger.info("Database connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
