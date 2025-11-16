# Vector Database Operations

**Purpose:** Semantic search across ScraperSky architectural documentation for pattern discovery and compliance verification.

**Project ID:** `ddfldwzhdhhzhxywqnyz`
**PostgreSQL Extension:** pgvector

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [How Semantic Search Works](#how-semantic-search-works)
3. [Using Semantic Search](#using-semantic-search)
4. [Critical Anti-Patterns](#critical-anti-patterns)
5. [Database Structure](#database-structure)
6. [Cost Considerations](#cost-considerations)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Perform a Semantic Search

```bash
# Basic search
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "authentication patterns in Layer 4"

# Search with custom limit
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "transaction management" --limit 10
```

**What this does:**
1. Converts your query to an embedding (using OpenAI API)
2. Performs vector similarity search in PostgreSQL
3. Returns most relevant documentation chunks

---

## How Semantic Search Works

### Architecture

```
Query Text
    ↓
[OpenAI Embeddings API] → Vector (1536 dimensions)
    ↓
[PostgreSQL RPC Function] → search_documents_by_embedding()
    ↓
[pgvector cosine similarity] → Top N similar document chunks
    ↓
Results (with similarity scores)
```

### Database Function

**PostgreSQL RPC:** `search_documents_by_embedding(query_embedding, match_limit)`

**What it does:**
- Compares query vector to all document vectors
- Uses cosine similarity (1 - cosine distance)
- Returns top N matches ordered by relevance
- Includes document metadata (file path, section, content)

---

## Using Semantic Search

### Command-Line Interface

**Script:** `Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py`

**Usage:**
```bash
# Basic search
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "your query here"

# With match limit
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "query" --limit 5

# Get help
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py --help
```

**Example Queries:**
```bash
# Find authentication patterns
python ...semantic_query_cli.py "JWT authentication implementation"

# Find transaction patterns
python ...semantic_query_cli.py "database transaction management routers vs services"

# Find specific workflow documentation
python ...semantic_query_cli.py "WF4 domain curation workflow"

# Find anti-patterns
python ...semantic_query_cli.py "database connection timeout issues"
```

### From Python Code

**NOT RECOMMENDED for most uses** - Use CLI instead.

If you must query from code:

```python
# WARNING: This is complex. Use CLI for normal searches.
from openai import OpenAI
import json

# Generate embedding
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="your query text"
)
query_embedding = response.data[0].embedding

# Execute RPC (using Supabase client or psycopg2)
result = supabase.rpc(
    'search_documents_by_embedding',
    {
        'query_embedding': query_embedding,
        'match_limit': 10
    }
).execute()

# Process results
for row in result.data:
    print(f"File: {row['file_path']}")
    print(f"Content: {row['content']}")
    print(f"Similarity: {row['similarity']}")
```

**Why CLI is better:**
- Handles embeddings correctly
- Manages API keys
- Formats output nicely
- Handles errors gracefully

---

## Critical Anti-Patterns

### ❌ NEVER Pass Vectors as String Literals

**WRONG - This WILL fail:**
```python
# DO NOT DO THIS
vector_str = str(embedding)  # "[0.1, 0.2, ...]"
sql = f"SELECT * FROM documents WHERE embedding <-> '{vector_str}' < 0.5"
result = execute_sql(sql)  # FAILS: Dimension mismatch, truncation
```

**Why it fails:**
- Vector truncated when passed as string
- Dimension mismatch errors (gets 384 instead of 1536)
- PostgreSQL can't parse vector correctly
- Silent data corruption

**CORRECT - Use RPC with native vector:**
```python
# DO THIS
result = supabase.rpc(
    'search_documents_by_embedding',
    {
        'query_embedding': embedding,  # Native Python list
        'match_limit': 10
    }
).execute()
```

### ❌ NEVER Hold Database Connections During Embedding Generation

**WRONG:**
```python
async with session.begin():
    # Generating embedding takes 1-2 seconds
    embedding = await openai.embeddings.create(...)  # ← CONNECTION HELD
    # Search
    result = await session.execute(...)
```

**CORRECT:**
```python
# Generate embedding WITHOUT database connection
embedding = await openai.embeddings.create(...)

# Then query database
async with session.begin():
    result = await session.execute(...)
```

**Why:** Embedding generation takes 1-2 seconds. Database connections timeout if held that long.

### ❌ NEVER Use Direct SQL for Vector Search

**WRONG:**
```sql
-- Don't execute this directly via psycopg2 or similar
SELECT * FROM documents
ORDER BY embedding <-> '[0.1, 0.2, ...]'
LIMIT 10;
```

**CORRECT:**
```python
# Use the RPC function
result = supabase.rpc('search_documents_by_embedding', {...})
```

**Why:** RPC function handles vector properly, SQL string doesn't.

---

## Database Structure

### Table: `documents`

**Location:** Supabase PostgreSQL
**Extension:** pgvector

**Schema:**
```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,              -- Source file path
    section_title TEXT,                   -- Section/heading
    content TEXT NOT NULL,                -- Actual content
    embedding VECTOR(1536),               -- Vector embedding
    token_count INTEGER,                  -- Token count for cost tracking
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for vector similarity search
CREATE INDEX documents_embedding_idx
ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### RPC Function: `search_documents_by_embedding`

**Definition:**
```sql
CREATE OR REPLACE FUNCTION search_documents_by_embedding(
    query_embedding VECTOR(1536),
    match_limit INT DEFAULT 10
)
RETURNS TABLE (
    id BIGINT,
    file_path TEXT,
    section_title TEXT,
    content TEXT,
    similarity FLOAT
)
LANGUAGE SQL
AS $$
    SELECT
        id,
        file_path,
        section_title,
        content,
        1 - (embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT match_limit;
$$;
```

**What it does:**
- Takes query embedding (1536 dimensions)
- Compares to all document embeddings using cosine distance (`<=>`)
- Returns similarity score (1 - distance)
- Limits results to top N matches

---

## Adding Documents to Vector Database

### Using Insert Script

**Script:** `Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py`

**Usage:**
```bash
# Add single document
python Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py \
    --file "Docs/MyNewDoc.md"

# Add multiple documents (batch)
python Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py \
    --directory "Docs/MyDocDirectory"
```

**What it does:**
1. Reads markdown file(s)
2. Splits into chunks (sections/paragraphs)
3. Generates embeddings for each chunk (OpenAI API)
4. Inserts into `documents` table
5. Updates registry

### Document Registry

**Purpose:** Track which documents are vectorized

**Location:** `Docs/Docs_18_Vector_Operations/Registry/`

**Process:**
1. Document added to registry with status
2. Script vectorizes document
3. Registry updated with completion status
4. Prevents duplicate vectorization

---

## Cost Considerations

### OpenAI Embedding Costs

**Model:** `text-embedding-3-small`
**Cost:** ~$0.0001 per query

**Typical Costs:**
- Single search query: $0.0001
- 100 search queries: $0.01
- Adding 1000-word document: ~$0.001 (chunked)

**Cost Control:**
- Use specific queries (not broad searches)
- Limit result count (`--limit 5` instead of default 10)
- Cache frequent queries if needed

### Database Costs

**Storage:** Minimal (vectors are small)
**Compute:** Search queries are fast (indexed)

---

## Troubleshooting

### Search Returns No Results

**Possible Causes:**
1. Query too specific or uses wrong terminology
2. Relevant documents not vectorized yet
3. Embedding model mismatch

**Solutions:**
- Try broader query terms
- Check what's in the database: `SELECT file_path FROM documents`
- Verify document was vectorized

### Dimension Mismatch Error

```
Error: dimension mismatch: expected 1536, got 384
```

**Cause:** Vector passed as string literal (truncated)

**Solution:** Use RPC function, don't pass vectors in SQL strings

### API Key Issues

```
Error: OpenAI API key not found
```

**Solution:**
```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Verify
echo $OPENAI_API_KEY
```

### Connection Timeout During Search

**Cause:** Holding database connection while generating embedding

**Solution:** Generate embedding first, then query database (see anti-patterns above)

---

## ScraperSky Librarian Persona (Optional)

**Purpose:** AI persona for managing vector database without technical knowledge

### Activating Librarian

```
Activate ScraperSky Librarian persona
```

### Librarian Commands

```
Find patterns about: [topic]
```

```
What's in the Vector DB now?
```

```
Compare this document against our Vector DB knowledge: [file path]
```

**Note:** This is an AI interaction pattern, not a technical tool. Use `semantic_query_cli.py` for direct searches.

---

## Related Documentation

- **Full Vector DB Documentation:** `Docs/Docs_18_Vector_Operations/v_Docs_18_Vector_Operations_README.md`
- **Complete Reference:** `Docs/Docs_18_Vector_Operations/Documentation/v_complete_reference.md`
- **Troubleshooting Guide:** `Docs/Docs_18_Vector_Operations/Documentation/v_troubleshooting_guide.md`
- **Connectivity Patterns:** `Docs/Docs_18_Vector_Operations/Documentation/v_connectivity_patterns.md`
- **Key Documents Index:** `Docs/Docs_18_Vector_Operations/v_key_documents.md`

---

## Summary: Vector Database Quick Reference

**Search for patterns:**
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "your query"
```

**Add documents:**
```bash
python Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py --file "path/to/doc.md"
```

**Critical Rules:**
- ✅ Use `semantic_query_cli.py` for searches
- ✅ Use RPC function for programmatic access
- ❌ Never pass vectors as string literals
- ❌ Never hold connections during embedding generation
- ❌ Never use direct SQL for vector search

**Cost:** ~$0.0001 per search query (OpenAI embeddings)

**Database:** Supabase PostgreSQL with pgvector extension
