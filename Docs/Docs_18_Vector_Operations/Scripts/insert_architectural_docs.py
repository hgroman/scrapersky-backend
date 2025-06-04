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

# Base directory for all document paths
BASE_DIR = "/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend"

# List of documents to embed in the vector database
# This list includes both the 21 foundational architectural documents
# and the 7 new documents from the Docs_18_Vector_Operations directory
# All documents are prepended with 'v_' to signify their vectorized status.
ARCHITECTURAL_DOCUMENTS = [
    # Original 21 foundational architectural documents
    {"name": "v_00-30000-FT-PROJECT-OVERVIEW.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_00-30000-FT-PROJECT-OVERVIEW.md"},
    {"name": "v_0.1_ScraperSky_Architecture_Flow_and_Components-Enhanced.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_0.1_ScraperSky_Architecture_Flow_and_Components-Enhanced.md"},
    {"name": "v_0.2_ScraperSky_Architecture_and_Implementation_Status.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_0.2_ScraperSky_Architecture_and_Implementation_Status.md"},
    {"name": "v_0.4_Curation Workflow Operating Manual.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_0.4_Curation Workflow Operating Manual.md"},
    {"name": "v_0.6-AI_Synthesized_Architectural_Overview.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_0.6-AI_Synthesized_Architectural_Overview.md"},
    {"name": "v_1.0-ARCH-TRUTH-Definitive_Reference.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_1.0-ARCH-TRUTH-Definitive_Reference.md"},
    {"name": "v_2.0-ARCH-TRUTH-Implementation_Strategy.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_2.0-ARCH-TRUTH-Implementation_Strategy.md"},
    {"name": "v_3.0-ARCH-TRUTH-Layer_Classification_Analysis_Concise.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_3.0-ARCH-TRUTH-Layer_Classification_Analysis_Concise.md"},
    {"name": "v_4.0-ARCH-TRUTH-State_of_the_Nation_May_2025.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_4.0-ARCH-TRUTH-State_of_the_Nation_May_2025.md"},
    {"name": "v_CONVENTIONS_AND_PATTERNS_GUIDE-Base_Identifiers.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_CONVENTIONS_AND_PATTERNS_GUIDE-Base_Identifiers.md"},
    {"name": "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer1_Models_Enums.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer1_Models_Enums.md"},
    {"name": "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer2_Schemas.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer2_Schemas.md"},
    {"name": "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer3_Routers.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer3_Routers.md"},
    {"name": "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer4_Services.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer4_Services.md"},
    {"name": "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer5_Configuration.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer5_Configuration.md"},
    {"name": "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer6_UI_Components.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer6_UI_Components.md"},
    {"name": "v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer7_Testing.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_CONVENTIONS_AND_PATTERNS_GUIDE-Layer7_Testing.md"},
    {"name": "v_Q&A_Key_Insights.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_Q&A_Key_Insights.md"},
    {"name": "v_ScraperSky_Architectural_Anti-patterns_and_Standards.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_ScraperSky_Architectural_Anti-patterns_and_Standards.md"},
    {"name": "v_Synthesized Project Evolution by Architectural Layer.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_Synthesized Project Evolution by Architectural Layer.md"},
    {"name": "v_WO5.0-ARCH-TRUTH-Code_Implementation_Work_Order.md", "path": f"{BASE_DIR}/Docs/Docs_6_Architecture_and_Status/v_WO5.0-ARCH-TRUTH-Code_Implementation_Work_Order.md"},
    
    # New documents from Docs_18_Vector_Operations directory
    {"name": "v_complete_reference.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_complete_reference.md"},
    {"name": "v_key_documents.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_key_documents.md"},
    {"name": "v_knowledge_librarian_persona_v2.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_knowledge_librarian_persona_v2.md"},
    {"name": "v_living_document.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_living_document.md"},
    {"name": "v_nan_issue_resolution.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_nan_issue_resolution.md"},
    {"name": "v_supabase_setup.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Setup/v_supabase_setup.md"},
    
    # New connectivity and documentation files
    {"name": "v_Add_docs_to_register_and_vector_db.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_Add_docs_to_register_and_vector_db.md"},
    {"name": "v_db_connectivity_mcp_4_manual_ops.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_mcp_4_manual_ops.md"},
    {"name": "v_db_connectivity_async_4_vector_ops.md", "path": f"{BASE_DIR}/Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_async_4_vector_ops.md"},
    
    # Updated reference documents
    {"name": "README_Vector_DB.md", "path": f"{BASE_DIR}/README_Vector_DB.md"},
    {"name": "35-LAYER5_VECTOR_DATABASE_REFERENCE.md", "path": f"{BASE_DIR}/Docs/Docs_1_AI_GUIDES/35-LAYER5_VECTOR_DATABASE_REFERENCE.md"}
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


async def insert_document(conn: asyncpg.Connection, title: str, content: str, embedding: List[float]) -> None:
    """Insert or update a document with its embedding into the public.project_docs table."""
    embedding_str = f"[{','.join(map(str, embedding))}]"
    try:
        # Check if document already exists
        existing = await conn.fetchrow(
            "SELECT id FROM public.project_docs WHERE title = $1",
            title
        )
        
        if existing:
            # Update existing document
            await conn.execute(
                """
                UPDATE public.project_docs 
                SET content = $1, embedding = $2::vector
                WHERE title = $3
                """,
                content, embedding_str, title
            )
            logger.info(f"Document '{title}' updated successfully.")
        else:
            # Insert new document
            await conn.execute(
                """
                INSERT INTO public.project_docs (title, content, embedding)
                VALUES ($1, $2, $3::vector);
                """,
                title,
                content,
                embedding_str
            )
            logger.info(f"Document '{title}' inserted successfully.")
    except Exception as e:
        logger.error(f"Error inserting/updating document '{title}': {e}")


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
