import asyncio
import asyncpg
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def verify_document_status():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        logger.error("DATABASE_URL environment variable not set.")
        return

    # Ensure DATABASE_URL is compatible with asyncpg
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    conn = None
    try:
        conn = await asyncpg.connect(database_url)
        logger.info("Successfully connected to the database.")

        doc_title_to_check = 'v_34-DART_MCP_GUIDE.md'

        # Query 1: Check document_registry
        logger.info(f"Querying document_registry for title: {doc_title_to_check}")
        registry_row = await conn.fetchrow(
            """
            SELECT id, title, file_path, should_be_vectorized, embedding_status, error_message
            FROM public.document_registry
            WHERE title = $1;
            """,
            doc_title_to_check
        )

        if registry_row:
            logger.info(f"Found in document_registry: ID={registry_row['id']}, Title='{registry_row['title']}', Path='{registry_row['file_path']}', ShouldBeVectorized={registry_row['should_be_vectorized']}, EmbeddingStatus='{registry_row['embedding_status']}', ErrorMessage='{registry_row['error_message']}'")
        else:
            logger.warning(f"Document '{doc_title_to_check}' NOT FOUND in document_registry.")

        # Query 2: Check project_docs
        logger.info(f"Querying project_docs for title: {doc_title_to_check}")
        project_doc_row = await conn.fetchrow(
            """
            SELECT doc_id, doc_title, doc_source_path, last_updated_at, embedding IS NOT NULL AS has_embedding
            FROM public.project_docs
            WHERE doc_title = $1;
            """,
            doc_title_to_check
        )

        if project_doc_row:
            logger.info(f"Found in project_docs: ID={project_doc_row['doc_id']}, Title='{project_doc_row['doc_title']}', Path='{project_doc_row['doc_source_path']}', LastUpdatedAt='{project_doc_row['last_updated_at']}', HasEmbedding={project_doc_row['has_embedding']}")
        else:
            logger.warning(f"Document '{doc_title_to_check}' NOT FOUND in project_docs.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if conn:
            await conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(verify_document_status())
