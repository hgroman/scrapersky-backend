# ScraperSky Vector DB MCP Server Guide

**Date:** 2025-06-02  
**Version:** 1.0  
**Status:** Active  

## Purpose

This document provides specific instructions for AI pairing partners on how to access and query the ScraperSky Vector Database using the Supabase MCP server. It addresses gaps in existing documentation and provides working examples.

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
  "query": "SELECT id, title FROM public.project_docs ORDER BY id;"
})
```

### 2. Get Document Content by Title

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT content FROM public.project_docs WHERE title = 'DocumentTitle.md';"
})
```

### 3. Perform Semantic Search

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT * FROM search_docs('your search query', 0.5);"
})
```

**Important**: When using the `search_docs` function, results will be returned with columns named `doc_title`, `doc_content`, and `similarity`.

## Advanced MCP Query Patterns

### 1. Count Documents in Vector DB

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT COUNT(*) FROM public.project_docs;"
})
```

### 2. Find Documents with Similar Titles

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT id, title FROM public.project_docs WHERE title ILIKE '%pattern%';"
})
```

### 3. Check for Duplicate Documents

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT title, COUNT(*) FROM public.project_docs GROUP BY title HAVING COUNT(*) > 1;"
})
```

## Troubleshooting MCP Access

If you encounter issues when trying to query the vector database:

1. **Verify Project ID**: Always use `ddfldwzhdhhzhxywqnyz` as the project_id
2. **Check Function Name**: Must use `mcp4_execute_sql` (not just "execute_sql")
3. **Validate Query Syntax**: Ensure SQL queries are properly formatted with semicolons
4. **Column Name Awareness**: Use the correct column names in your queries:
   - Table columns: `id`, `title`, `content`, `embedding`, `created_at`
   - Search function returns: `doc_title`, `doc_content`, `similarity`

## Integration with Librarian Persona

When operating as the ScraperSky Librarian persona, you should:

1. Use these MCP patterns directly without requiring user intervention
2. Handle all technical aspects of querying the vector database
3. Present search results in a clear, actionable format
4. Track which documents have been loaded into the Vector DB
5. Support code refactoring by identifying applicable patterns

## Related Documentation

- `Docs/Docs_16_ScraperSky_Code_Canon/0.2-vector_db_living_document.md` - Main vector DB documentation
- `Docs/Vector_Operations/vector_db_nan_issue_resolution.md` - Resolution for "Similarity: nan" issue
- `Docs/Vector_Operations/0.4-vector_db_simple_test_updated.py` - Updated test script
