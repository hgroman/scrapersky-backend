# ScraperSky Vector DB MCP Server Integration Guide

**Date:** 2025-06-09  
**Version:** 1.2  
**Status:** Active  

## Purpose

This document provides comprehensive instructions for AI pairing partners on how to access and query the ScraperSky Vector Database using the Supabase MCP server. It consolidates all essential information about MCP server integration into a single authoritative source.

> **Technical Context:** While the main ScraperSky backend uses SQLAlchemy with FastAPI, vector database operations intentionally use direct SQL via MCP (for manual queries) or asyncpg (for scripts with vector operations) instead of ORM models. This approach provides better compatibility with pgvector and simplifies internal-facing operations.

## MCP Server Access Requirements

To successfully query the vector database using the MCP server, you need:

1. **Correct MCP Function Name**: Use `mcp4_execute_sql` (not just "execute_sql")
2. **Supabase Project ID**: Always use `ddfldwzhdhhzhxywqnyz` as the project_id parameter
3. **Proper SQL Query Format**: Follow the SQL patterns shown below

## Basic MCP Query Patterns

### 1. List All Documents in Vector DB

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT id, title FROM public.project_docs ORDER BY title;"
})
```

### 2. Get Document Content by Title

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT title, content FROM public.project_docs WHERE title = 'DocumentTitle.md';"
})
```

### 3. Perform Semantic Search

Semantic search involves two main steps:
1.  **Generate Query Embedding Client-Side:** Use the appropriate embedding model (e.g., OpenAI's `text-embedding-ada-002`) to convert your textual search query into a vector embedding. This step is performed in your client application (e.g., Python script).
2.  **Execute Similarity Search Query:** Use the generated query embedding in an SQL query to find similar document embeddings in the `project_docs` table.

**Example Workflow:**

*   **Client-Side (Python Example using OpenAI API - conceptual):**
    ```python
    # Assume 'openai_client' is an initialized OpenAI API client
    # and 'your_search_query' is the text you want to search for.
    response = openai_client.embeddings.create(
        input=[your_search_query],
        model="text-embedding-ada-002"
    )
    query_embedding = response.data[0].embedding
    # query_embedding is now a list of floats, e.g., [0.01, -0.02, ...]
    # Convert this list to a string format suitable for SQL: '[0.01,-0.02,...]'
    query_embedding_sql_string = f"[{','.join(map(str, query_embedding))}]"
    ```

*   **MCP Call (using the `query_embedding_sql_string` from above):**
    ```javascript
    // Assume query_embedding_sql_string contains the vector like '[0.01,-0.02,...]'
    mcp4_execute_sql({
      "project_id": "ddfldwzhdhhzhxywqnyz",
      "query": `SELECT title, content, 1 - (embedding <=> '${query_embedding_sql_string}'::vector) AS similarity FROM public.project_docs ORDER BY similarity DESC LIMIT 10;`
    })
    ```

This query returns the `title`, `content`, and `similarity` score for the top 10 most similar documents. Adjust `LIMIT` as needed.

The `project_docs` table (queried above) typically has columns like:
- `id`: The primary key identifier for the document chunk in the vector store.
- `title`: The original document title.
- `content`: The text chunk that was embedded.
- `embedding`: The vector embedding of the content.
- `similarity`: The calculated similarity score (cosine similarity, where 1 is most similar, 0 is unrelated). Higher is better.

## Advanced Query Patterns

### 1. Get Document Count

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT COUNT(*) FROM public.project_docs;"
})
```

### 2. Filter Documents by Title Pattern

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT title FROM public.project_docs WHERE title LIKE '%ARCH-TRUTH%';"
})
```

### 3. Get Most Recent Documents

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT title, created_at FROM public.project_docs ORDER BY created_at DESC LIMIT 5;"
})
```

## Common Issues and Troubleshooting

### CRITICAL: Database Connection Requirements

#### Statement Cache Size Setting

**IMPORTANT:** When connecting to the ScraperSky vector database using asyncpg, you **MUST** set `statement_cache_size=0` to avoid pgbouncer prepared statement issues. This is a non-negotiable requirement for all database connections.

```python
# Correct way to connect to the database
conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)

# INCORRECT way (will fail with prepared statement errors)
# conn = await asyncpg.connect(DATABASE_URL)
```

Failure to set `statement_cache_size=0` will result in errors like:
```
prepared statement "__asyncpg_stmt_1__" already exists
HINT: pgbouncer with pool_mode set to "transaction" or "statement" does not support prepared statements properly.
```

### "Similarity: nan" Issue

If you encounter "Similarity: nan" in search results, this indicates a vector normalization issue. This has been fixed in the database, but if it recurs, refer to `Docs/Docs_18_Vector_Operations/Documentation/v_nan_issue_resolution.md` for the detailed resolution.

### Connection Errors

If you receive connection errors when using the MCP server:
1. Verify you're using the correct function name: `mcp4_execute_sql`
2. Verify you're using the correct project ID: `ddfldwzhdhhzhxywqnyz`
3. Check that your SQL query syntax is valid

### Table Schema and Column Names

**IMPORTANT:** When querying the vector database tables, be aware of the exact column names to avoid errors.

#### project_docs Table Columns

```sql
SELECT column_name FROM information_schema.columns WHERE table_name = 'project_docs' AND table_schema = 'public';
```

The `project_docs` table has these columns:
- `id` (not doc_id) - The primary key identifier
- `title` - The document title
- `content` - The document content
- `embedding` - The vector embedding
- `created_at` (not last_updated_at) - Timestamp when the document was created

#### document_registry Table Columns

The `document_registry` table has these columns:
- `id` - The primary key identifier
- `title` - The document title (typically v_filename.md)
- `file_path` - The absolute path to the document
- `should_be_vectorized` - Boolean flag indicating if the document should be vectorized
- `embedding_status` - Status of the embedding process (e.g., 'completed', 'pending', error codes)
- `error_message` - Any error message from the embedding process
- `last_checked` - When the document was last checked

Always verify column names if you encounter "column does not exist" errors.

## Current Database Status

The number of documents in the vector database is dynamic. You can get the current count using the MCP query pattern provided in the "Advanced Query Patterns" section (Get Document Count).

### Document Registry Management

The `document_registry` table in the ScraperSky Vector Database is the source of truth for document metadata, tracking which files should be vectorized, their ingestion status, and file paths. It is managed by a suite of Python scripts:

- **`2-registry-document-scanner.py`**:
  - Scans predefined approved directories for documentation files.
  - Adds new documents found to the `document_registry` table.
  - Updates existing entries if file paths or `last_modified` times change.
  - Sets `should_be_vectorized = true` for files following the `v_*.md` naming convention within approved vectorization paths.
  - Records the `last_checked` timestamp.

- **`3-registry-update-manager.py`** (Conceptual - confirm exact script name and functionality if different):
  - Monitors the main `project_docs` table (where successfully vectorized documents reside).
  - Updates the `is_vectorized` (boolean) and `embedding_status` (e.g., 'completed', 'pending', 'error') fields in the `document_registry` table based on the actual ingestion status.
  - May log errors from the embedding/ingestion process to the `error_message` field.

- **`4-registry-archive-manager.py`**:
  - Handles documents that have been archived.
  - Updates the `document_registry` by setting `should_be_vectorized = false`, `is_vectorized = false`, and `embedding_status = 'archived'` for specified archived documents.
  - Ensures archived documents are no longer candidates for ingestion.

These scripts work together to maintain an accurate and up-to-date registry, forming the backbone of the document ingestion and management pipeline. The `document_registry` table itself, queried via MCP or asyncpg, provides the most current list and status of all tracked documents.
