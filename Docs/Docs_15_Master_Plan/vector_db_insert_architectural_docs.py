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

# List of architectural documents to embed
ARCHITECTURAL_DOCUMENTS = [
    {"name": "1.0-ARCH-TRUTH-Definitive_Reference.md", "path": "Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md"},
    {"name": "CONVENTIONS_AND_PATTERNS_GUIDE-Base_Identifiers.md", "path": "Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE-Base_Identifiers.md"},
    {"name": "CONVENTIONS_AND_PATTERNS_GUIDE-Layer1_Models_Enums.md", "path": "Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE-Layer1_Models_Enums.md"},
    {"name": "CONVENTIONS_AND_PATTERNS_GUIDE-Layer2_Schemas.md", "path": "Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE-Layer2_Schemas.md"},
    {"name": "CONVENTIONS_AND_PATTERNS_GUIDE-Layer3_Routers.md", "path": "Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE-Layer3_Routers.md"},
    {"name": "CONVENTIONS_AND_PATTERNS_GUIDE-Layer4_Services.md", "path": "Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE-Layer4_Services.md"},
    {"name": "CONVENTIONS_AND_PATTERNS_GUIDE-Layer5_Configuration.md", "path": "Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE-Layer5_Configuration.md"},
    {"name": "CONVENTIONS_AND_PATTERNS_GUIDE-Layer6_UI_Components.md", "path": "Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE-Layer6_UI_Components.md"},
    {"name": "CONVENTIONS_AND_PATTERNS_GUIDE-Layer7_Testing.md", "path": "Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE-Layer7_Testing.md"},
    {"name": "Q&A_Key_Insights.md", "path": "Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md"},
    {"name": "ScraperSky_Architectural_Anti-patterns_and_Standards.md", "path": "Docs/Docs_6_Architecture_and_Status/ScraperSky_Architectural_Anti-patterns_and_Standards.md"},
    {"name": "00-30000-FT-PROJECT-OVERVIEW.md", "path": "Docs/Docs_6_Architecture_and_Status/00-30000-FT-PROJECT-OVERVIEW.md"}
]

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


async def insert_document(conn: asyncpg.Connection, document_name: str, content: str, embedding: List[float]) -> None:
    """Insert a document with its embedding into the public.project_docs table."""
    embedding_str = f"[{','.join(map(str, embedding))}]"
    try:
        await conn.execute(
            """
            INSERT INTO public.project_docs (document_name, content, embedding)
            VALUES ($1, $2, $3::vector)
            ON CONFLICT (document_name) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                updated_at = NOW();
            """,
            document_name,
            content,
            embedding_str
        )
        logger.info(f"Document '{document_name}' inserted/updated successfully.")
    except Exception as e:
        logger.error(f"Error inserting/updating document '{document_name}': {e}")


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
                document_name,
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
                logger.info(f"Document: {result['document_name']} - Similarity: {result['similarity']:.4f}")
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
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
        logger.info("Connected to database and ensured vector extension is enabled.")

        for doc_info in ARCHITECTURAL_DOCUMENTS:
            doc_name = doc_info["name"]
            doc_path = doc_info["path"]
            logger.info(f"Processing document: {doc_name} from {doc_path}")

            try:
                with open(doc_path, 'r') as f:
                    content = f.read()
                embedding = await generate_embedding(content)
                await insert_document(conn, doc_name, content, embedding)
            except FileNotFoundError:
                logger.error(f"Document file not found: {doc_path}. Skipping.")
            except Exception as e:
                logger.error(f"Error processing document {doc_name}: {e}. Skipping.")

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
