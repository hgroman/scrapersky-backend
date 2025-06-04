#!/usr/bin/env python3
"""
Script to load all vector database documentation into the vector database itself.
This ensures that all documentation about the vector database is searchable within the vector database.
"""

import asyncio
import os
from pathlib import Path

import asyncpg
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
# Fix the database URL if it uses postgresql+asyncpg scheme
if DATABASE_URL and DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Key documents to load - only those with v_ prefix are meant to be vectorized
KEY_DOCUMENTS = [
    {
        "path": "README_Vector_DB.md",
        "description": "Entry point for vector database information"
    },
    {
        "path": "Docs/Docs_18_Vector_Operations/Documentation/v_living_document.md",
        "description": "Technical reference for vector database"
    },
    {
        "path": "Docs/Docs_18_Vector_Operations/Documentation/v_mcp_guide.md",
        "description": "MCP server integration guide"
    },
    {
        "path": "Docs/Docs_18_Vector_Operations/Documentation/v_knowledge_librarian_persona.md",
        "description": "Knowledge Librarian persona instructions"
    },
    {
        "path": "Docs/Docs_1_AI_GUIDES/35-LAYER5_VECTOR_DATABASE_REFERENCE.md",
        "description": "AI guides reference for vector database"
    },
    {
        "path": "Docs/Docs_18_Vector_Operations/Documentation/v_key_documents.md",
        "description": "List of key vector database documents"
    },
    {
        "path": "Docs/Docs_18_Vector_Operations/Documentation/v_nan_issue_resolution.md",
        "description": "Resolution for 'Similarity: nan' issue"
    }
]

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


async def generate_embedding(text):
    """Generate an embedding for the given text using OpenAI API."""
    try:
        # Use the new OpenAI client format
        client = openai.Client(api_key=OPENAI_API_KEY)
        response = await asyncio.to_thread(
            lambda: client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
        )
        # Normalize the embedding vector
        embedding = response.data[0].embedding
        magnitude = sum(x * x for x in embedding) ** 0.5
        normalized_embedding = [x / magnitude for x in embedding]
        
        # Convert the embedding to a string representation
        embedding_str = str(normalized_embedding)
        return embedding_str
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


async def load_document(conn, doc_path, description):
    """Load a document into the vector database."""
    full_path = PROJECT_ROOT / doc_path.lstrip('/')
    
    if not full_path.exists():
        print(f"Document not found: {full_path}")
        return False
    
    try:
        # Read document content
        content = full_path.read_text(encoding='utf-8')
        title = full_path.name
        
        # Check if document already exists
        existing = await conn.fetchrow(
            "SELECT id FROM project_docs WHERE title = $1",
            title
        )
        
        if existing:
            print(f"Document already exists: {title}")
            # Update existing document
            embedding = await generate_embedding(content)
            if embedding:
                await conn.execute(
                    """
                    UPDATE project_docs 
                    SET content = $1, embedding = $2
                    WHERE title = $3
                    """,
                    content, embedding, title
                )
                print(f"Updated document: {title}")
                return True
        else:
            # Insert new document
            embedding = await generate_embedding(content)
            if embedding:
                await conn.execute(
                    """
                    INSERT INTO project_docs (title, content, embedding)
                    VALUES ($1, $2, $3)
                    """,
                    title, content, embedding
                )
                print(f"Inserted document: {title}")
                return True
        
        return False
    except Exception as e:
        print(f"Error loading document {doc_path}: {e}")
        return False


async def main():
    """Main function to load all documents."""
    print("Starting to load vector database documentation...")
    
    try:
        # Connect to the database with statement_cache_size=0 to avoid pgbouncer issues
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        
        # Ensure the vector extension is enabled
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("Vector extension enabled")
        except Exception as e:
            print(f"Error enabling vector extension: {e}")
        
        # Load each document
        success_count = 0
        for doc in KEY_DOCUMENTS:
            if await load_document(conn, doc["path"], doc["description"]):
                success_count += 1
        
        print(f"Successfully loaded {success_count} of {len(KEY_DOCUMENTS)} documents")
        
        # Generate document registry
        print("Generating document registry...")
        registry_script = PROJECT_ROOT / "Docs/Docs_18_Vector_Operations/Scripts/generate_document_registry.py"
        if registry_script.exists():
            os.system(f"python {registry_script}")
            print("Document registry updated")
        else:
            # Try the old path as fallback
            old_registry_script = PROJECT_ROOT / "Docs/Docs_16_ScraperSky_Code_Canon/0.7-generate_document_registry.py"
            if old_registry_script.exists():
                os.system(f"python {old_registry_script}")
                print("Document registry updated using legacy script")
            else:
                print("Document registry script not found")
        
        # Close the connection
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
