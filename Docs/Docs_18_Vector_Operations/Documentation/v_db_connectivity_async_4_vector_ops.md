# ScraperSky Vector Database Connectivity Guide

## Table of Contents
1. [Overview](#overview)
2. [MCP Method](#mcp-method)
3. [Asyncpg Method](#asyncpg-method)
4. [When to Use Each Method](#when-to-use-each-method)
5. [Technical Requirements](#technical-requirements)
6. [Common Issues](#common-issues)

## Overview

The ScraperSky vector database system uses two distinct connectivity methods, each with specific use cases and technical requirements. This guide documents both methods to ensure proper usage.

## MCP Method

### Description
The MCP method uses the `mcp4_execute_sql` function to execute SQL queries against the database.

### Implementation

```javascript
mcp4_execute_sql({
  "project_id": "ddfldwzhdhhzhxywqnyz",
  "query": "YOUR SQL QUERY HERE"
})
```

### Technical Requirements
- Requires valid project ID: `ddfldwzhdhhzhxywqnyz`
- SQL query must be properly formatted as a string
- Cannot handle specialized connection parameters
- Does not support direct transaction control

## Asyncpg Method

### Description
The asyncpg method uses direct database connections via the asyncpg Python library, with specific configuration parameters required for proper operation.

### Implementation

```python
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Convert connection string if needed
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Remove query parameters if present
if "?" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

# Connect to database with required parameters
conn = await asyncpg.connect(
    DATABASE_URL,
    ssl="require",
    statement_cache_size=0  # Required for pgbouncer compatibility
)

# Ensure vector extension is enabled
await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
```

### Technical Requirements
- Requires `DATABASE_URL` environment variable
- Requires connection string conversion from SQLAlchemy format
- Requires specific connection parameters:
  - SSL/TLS encryption is handled by the Supabase connection pooler by default (verified by `SHOW ssl;` returning `on`). Explicitly setting `ssl='require'` in the `asyncpg` client connection may cause connection failures with the current Supabase/pgbouncer configuration. For this environment, omit the `ssl` parameter in the `asyncpg.connect()` call; the connection will still be encrypted.
  - `statement_cache_size=0` for pgbouncer compatibility
- May need to enable vector extension

## When to Use Each Method

### Use MCP Method For:
- Manual database operations (checking status, updating registry entries)
- Simple queries that don't require specialized connection parameters
- Ad-hoc operations performed directly by AI assistants or users
- When you don't need transaction control or specialized PostgreSQL features

### Use Asyncpg Method For:
- Vector database ingestion scripts that require:
  - OpenAI API integration for embedding generation
  - Vector extension operations
  - pgbouncer compatibility
  - Fine-grained transaction control
  - Specialized connection parameters
- Existing scripts like:
  - `insert_architectural_docs.py`
  - `simple_test.py`

## Technical Requirements

### Environment Variables
Both methods require proper environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Required for scripts that generate embeddings

### Connection String Format
The asyncpg method requires conversion of SQLAlchemy connection strings:
```python
# Convert SQLAlchemy format to asyncpg format
if DATABASE_URL and "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
```

### Query Parameters
The asyncpg method requires removal of query parameters:
```python
# Remove query parameters for asyncpg compatibility
if "?" in DATABASE_URL:
    base_url = DATABASE_URL.split("?")[0]
    DATABASE_URL = base_url
```

## Common Issues

### "NaN" Similarity Values
If you encounter "NaN" similarity values in vector searches, refer to `v_nan_issue_resolution.md` for troubleshooting.

### Connection Errors
- Verify environment variables are set correctly
- Ensure connection string is properly formatted
- Check that pgbouncer is configured correctly if using asyncpg method

### Vector Extension Missing
The asyncpg method should ensure the vector extension is enabled:
```python
await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
```
