# Asyncpg Vector Operations

This directory contains scripts for vector database operations that require the asyncpg connectivity method.

## Connectivity Method

These scripts use the **Asyncpg Method** for database connectivity:
- Direct connection via asyncpg with specific connection parameters
- Used for vector database scripts requiring OpenAI API integration
- Provides full control over connection parameters and explicit transaction management
- Requires specific connection parameters for pgbouncer compatibility

## Scripts in this Directory

1. **fix_vector_embeddings.py**
   - Identifies and fixes problematic vector embeddings in the database
   - Resolves "Similarity: nan" issues by normalizing vectors

2. **vector_db_diagnostics.py**
   - Runs diagnostic queries on the Supabase vector database
   - Checks pgvector extension, table existence, and embedding quality

3. **vector_db_insert_final.py**
   - Inserts patterns into the fix_patterns table with proper vector embeddings
   - Includes vector search testing functionality

4. **query_table_structure.py**
   - Queries the structure of database tables to understand columns and constraints
   - Useful for schema verification and debugging

## When to Use These Scripts

Use scripts in this directory when:
- Working with vector embeddings that require OpenAI API integration
- Performing batch operations for document insertion
- Executing complex vector operations
- Requiring fine-grained transaction control

## Reference Documentation

For detailed guidance on the asyncpg connectivity method, refer to:
- [v_db_connectivity_async_4_vector_ops.md](/Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_async_4_vector_ops.md)

## Implementation Example

```python
# Using asyncpg for vector operations
async def insert_document(title, content, embedding):
    conn = await asyncpg.connect(
        DATABASE_URL,
        statement_cache_size=0,
        max_cached_statement_lifetime=0
    )
    try:
        await conn.execute(
            "INSERT INTO public.project_docs (title, content, embedding) VALUES ($1, $2, $3)",
            title, content, embedding
        )
    finally:
        await conn.close()
```
