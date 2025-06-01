# Supabase Vector DB Setup - Zero Bullshit

## WHAT WE'RE DOING
1. Create a simple table in Supabase
2. Dump the 12 key architectural documents into it (4 original + 8 split convention guide sections)
3. Enable vector search
4. Test it works

## STEP 1: Create Table (Supabase Dashboard > SQL Editor)

```sql
-- Create the table
CREATE TABLE IF NOT EXISTS project_docs (
  id SERIAL PRIMARY KEY,
  title TEXT,
  content TEXT,
  embedding VECTOR(1536),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable vector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;
```

## STEP 2: Insert Documents (Using `scripts/vector_db_insert_architectural_docs.py`)

**IMPORTANT**: Do NOT copy/paste content here. The `scripts/vector_db_insert_architectural_docs.py` script will handle reading and inserting the documents. Ensure the `ARCHITECTURAL_DOCUMENTS` list within that script is up-to-date with the correct paths and names for all 12 documents.

The documents to be inserted are:

*   **Original Key Documents:**
    *   `1.0-ARCH-TRUTH-Definitive_Reference.md` (Path: `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`)
    *   `Q&A_Key_Insights.md` (Path: `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`)
    *   `ScraperSky_Architectural_Anti-patterns_and_Standards.md` (Path: `Docs/Docs_15_Master_Plan/ScraperSky_Architectural_Anti-patterns_and_Standards.md`)
    *   `00-30000-FT-PROJECT-OVERVIEW.md` (Path: `Docs/Docs_6_Architecture_and_Status/00-30000-FT-PROJECT-OVERVIEW.md`)

*   **Split Conventions and Patterns Guide Documents (all paths are `Docs/Docs_6_Architecture_and_Status/`):**
    *   `CONVENTIONS_AND_PATTERNS_GUIDE-Base_Identifiers.md`
    *   `CONVENTIONS_AND_PATTERNS_GUIDE-Layer1_Models_Enums.md`
    *   `CONVENTIONS_AND_PATTERNS_GUIDE-Layer2_Schemas.md`
    *   `CONVENTIONS_AND_PATTERNS_GUIDE-Layer3_Routers.md`
    *   `CONVENTIONS_AND_PATTERNS_GUIDE-Layer4_Services.md`
    *   `CONVENTIONS_AND_PATTERNS_GUIDE-Layer5_Configuration.md`
    *   `CONVENTIONS_AND_PATTERNS_GUIDE-Layer6_UI_Components.md`
    *   `CONVENTIONS_AND_PATTERNS_GUIDE-Layer7_Testing.md`
```

## STEP 3: Generate Embeddings (OpenAI API Required)

**WHY OPENAI API**: Supabase uses OpenAI's embedding model for vector search. Your Gemini 2.5 is for conversation, OpenAI embeddings are for making the documents searchable.

```sql
-- Generate embeddings for all documents
UPDATE project_docs 
SET embedding = ai.openai_embed('text-embedding-ada-002', content)::vector
WHERE embedding IS NULL;
```

## STEP 4: Create Search Function

```sql
-- Create search function
CREATE OR REPLACE FUNCTION search_docs(query_text TEXT, match_threshold FLOAT DEFAULT 0.7)
RETURNS TABLE(
  title TEXT,
  content TEXT,
  similarity FLOAT
)
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    d.title,
    LEFT(d.content, 1000) as content,  -- Truncate for readability
    1 - (d.embedding <=> ai.openai_embed('text-embedding-ada-002', query_text)::vector) as similarity
  FROM project_docs d
  WHERE 1 - (d.embedding <=> ai.openai_embed('text-embedding-ada-002', query_text)::vector) > match_threshold
  ORDER BY d.embedding <=> ai.openai_embed('text-embedding-ada-002', query_text)::vector
  LIMIT 5;
END;
$$ LANGUAGE plpgsql;
```

## STEP 5: Test It Works

```sql
-- Test search
SELECT * FROM search_docs('transaction management rules');
SELECT * FROM search_docs('Layer 4 service patterns');
SELECT * FROM search_docs('naming conventions');
```

## VERIFICATION

After running all steps, you should see:
1. 12 rows in `project_docs` table
2. All rows have embeddings (not NULL)
3. Search queries return relevant results

## FOR YOUR AI PAIRING PARTNER

Once this is done, you can tell your AI:

> "You have access to our ScraperSky project documentation via Supabase vector search using the `search_docs()` function. The project follows a 7-layer architecture with strict ORM-only database access, transaction management rules, and naming conventions. Do you understand? If yes, say yes."

## TROUBLESHOOTING

**If OpenAI API fails**: You need to set up OpenAI integration in Supabase:
1. Supabase Dashboard > SQL Editor
2. Run: `SELECT ai.openai_api_key_set('[YOUR_OPENAI_API_KEY]');`

**If single quotes break**: Double them ('') in the document content when pasting.
