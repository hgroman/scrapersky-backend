# MCP Server Integration Section

## 7. MCP Server Integration

### 7.1 Using Supabase MCP Server for Vector DB Queries

To query the vector database using the Supabase MCP server, you **MUST** use the following specific function and parameters:

```javascript
// CRITICAL: Use mcp4_execute_sql (not just execute_sql)
// CRITICAL: Always use this exact project_id: ddfldwzhdhhzhxywqnyz

// Example MCP server call to list all documents
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT id, title FROM public.project_docs;"
})

// Example MCP server call to get document content
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT content FROM public.project_docs WHERE title = 'DocumentTitle.md';"
})

// Example MCP server call for semantic search
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "SELECT * FROM search_docs('your search query', 0.5);"
})
```

**Important Notes:**
1. The function name **MUST** be `mcp4_execute_sql` (not just "execute_sql")
2. The project_id **MUST** be exactly `ddfldwzhdhhzhxywqnyz`
3. When using the `search_docs` function, results will be returned with columns named `doc_title`, `doc_content`, and `similarity`
4. SQL queries must be properly formatted with semicolons

### 7.2 Troubleshooting MCP Access

If you encounter issues when trying to query the vector database:

1. **Verify Project ID**: Always use `ddfldwzhdhhzhxywqnyz` as the project_id
2. **Check Function Name**: Must use `mcp4_execute_sql` (not just "execute_sql")
3. **Validate Query Syntax**: Ensure SQL queries are properly formatted with semicolons
4. **Column Name Awareness**: Use the correct column names in your queries:
   - Table columns: `id`, `title`, `content`, `embedding`, `created_at`
   - Search function returns: `doc_title`, `doc_content`, `similarity`
