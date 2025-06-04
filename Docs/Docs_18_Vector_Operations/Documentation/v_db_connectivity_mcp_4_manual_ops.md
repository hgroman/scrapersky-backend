# ScraperSky Vector DB MCP Server Integration Guide

**Date:** 2025-06-02  
**Version:** 1.1  
**Status:** Active  

## Purpose

This document provides comprehensive instructions for AI pairing partners on how to access and query the ScraperSky Vector Database using the Supabase MCP server. It consolidates all essential information about MCP server integration into a single authoritative source.

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

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT * FROM search_docs('your search query', 0.5);"
})
```

The `search_docs` function returns a table with the following columns:
- `doc_title`: The title of the document
- `doc_content`: The content of the document (truncated to 1000 characters)
- `similarity`: The similarity score between the query and the document (higher is better)

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

## Current Database Status

As of 2025-06-03, the vector database contains 21 documents, including:
- All core architectural truth documents
- All layer-specific conventions and patterns guides
- Key overview documents and synthesized architectural documents

### Document Registry Management

The document registry is maintained using the `0.7-generate_document_registry.py` script, which:
- Connects directly to the vector database using asyncpg
- Generates a markdown table of all documents in the database
- Identifies documents that are not yet ingested
- Prevents documents from being listed in both categories
- Outputs the registry to `0.5-vector_db_document_registry.md`

To update the document registry:

```bash
python Docs/Docs_18_Vector_Operations/Scripts/generate_document_registry.py
```

The complete list of current documents can be found in `Docs/Docs_18_Vector_Operations/Registry/document_registry.md`.
