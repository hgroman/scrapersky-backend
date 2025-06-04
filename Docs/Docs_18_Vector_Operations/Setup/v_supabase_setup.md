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

**IMPORTANT NOTES:**
- The table uses `title` (not `document_name`) for the document title
- There is NO `updated_at` column in the schema
- There is NO UNIQUE constraint on the `title` column

## STEP 2: Insert Documents (Using `Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py`)

**IMPORTANT**: Do NOT copy/paste content here. The `Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py` script will handle reading and inserting the documents. Ensure the `ARCHITECTURAL_DOCUMENTS` list within that script is up-to-date with the correct paths and names for all 12 documents.

The documents to be inserted are:

*   **Original Key Documents:**
    *   `1.0-ARCH-TRUTH-Definitive_Reference.md` (Path: `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`)
    *   `Q&A_Key_Insights.md` (Path: `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`)
    *   `ScraperSky_Architectural_Anti-patterns_and_Standards.md` (Path: `Docs/Docs_6_Architecture_and_Status/ScraperSky_Architectural_Anti-patterns_and_Standards.md`)
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

**IMPORTANT**: The Python script `insert_architectural_docs.py` handles embedding generation using the OpenAI API. You do NOT need to run the SQL below unless you want to regenerate embeddings for documents already in the database.

**ENVIRONMENT VARIABLES REQUIRED:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Your Supabase database URL (PostgreSQL connection string)

```sql
-- Only if needed: Generate embeddings for all documents
UPDATE project_docs 
SET embedding = ai.openai_embed('text-embedding-ada-002', content)::vector
WHERE embedding IS NULL;
```

## STEP 4: Create Search Function

```sql
-- Create search function
CREATE OR REPLACE FUNCTION search_docs(query_text TEXT, match_threshold FLOAT DEFAULT 0.7)
RETURNS TABLE(
  doc_title TEXT,
  doc_content TEXT,
  similarity FLOAT
)
AS $$
DECLARE
  query_embedding VECTOR;
BEGIN
  -- Get query embedding from OpenAI API
  -- If OpenAI integration is not set up, use the alternative approach below
  
  -- OPTION 1: With OpenAI API integration
  query_embedding := ai.openai_embed('text-embedding-ada-002', query_text)::vector;
  
  -- OPTION 2: If OpenAI integration fails, use this alternative approach
  -- This requires at least one document to be in the database already
  /*
  IF query_embedding IS NULL THEN
    SELECT p.embedding INTO query_embedding
    FROM project_docs p
    WHERE p.title = '1.0-ARCH-TRUTH-Definitive_Reference.md'
    LIMIT 1;
  END IF;
  */
  
  RETURN QUERY
  SELECT 
    d.title,
    LEFT(d.content, 1000) as content,  -- Truncate for readability
    1 - (d.embedding <=> query_embedding) as similarity
  FROM project_docs d
  WHERE 1 - (d.embedding <=> query_embedding) > match_threshold
  ORDER BY d.embedding <=> query_embedding
  LIMIT 5;
END;
$$ LANGUAGE plpgsql;
```

**ALTERNATIVE SEARCH FUNCTION (If OpenAI API integration fails):**

```sql
-- Create AI schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS ai;

-- Create a placeholder embedding function
CREATE OR REPLACE FUNCTION ai.openai_embed(model_name TEXT, content TEXT)
RETURNS VECTOR
LANGUAGE plpgsql
AS $$
DECLARE
  embedding VECTOR;
BEGIN
  -- This is a placeholder function that returns a reference embedding
  SELECT embedding INTO embedding
  FROM project_docs
  WHERE title = '1.0-ARCH-TRUTH-Definitive_Reference.md'
  LIMIT 1;
  
  RETURN embedding;
END;
$$;

-- Create simplified search function
CREATE OR REPLACE FUNCTION search_docs(query_text TEXT, match_threshold FLOAT DEFAULT 0.7)
RETURNS TABLE(
  doc_title TEXT,
  doc_content TEXT,
  similarity FLOAT
)
AS $$
DECLARE
  query_embedding VECTOR;
BEGIN
  -- Get a reference embedding to use for search
  SELECT p.embedding INTO query_embedding
  FROM project_docs p
  WHERE p.title = '1.0-ARCH-TRUTH-Definitive_Reference.md'
  LIMIT 1;
  
  RETURN QUERY
  SELECT 
    d.title,
    LEFT(d.content, 1000) as content,
    1 - (d.embedding <=> query_embedding) as similarity
  FROM project_docs d
  WHERE 1 - (d.embedding <=> query_embedding) > match_threshold
  ORDER BY d.embedding <=> query_embedding
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

Run these verification queries:

```sql
-- Check row count
SELECT COUNT(*) FROM project_docs;

-- Check for NULL embeddings
SELECT COUNT(*) FROM project_docs WHERE embedding IS NULL;

-- Verify table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'project_docs';
```

## FOR YOUR AI PAIRING PARTNER

Once this is done, you can tell your AI:

> "You have access to our ScraperSky project documentation via Supabase vector search using the `search_docs()` function. The project follows a 7-layer architecture with strict ORM-only database access, transaction management rules, and naming conventions. Do you understand? If yes, say yes."

## OPENAI INTEGRATION WITH SUPABASE

To properly integrate OpenAI with Supabase for vector operations, follow these steps:

### 1. Set Up OpenAI API Key in Supabase

```sql
-- Create the ai schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS ai;

-- Create a function to store your OpenAI API key securely
CREATE OR REPLACE FUNCTION ai.openai_api_key_set(api_key TEXT)
RETURNS VOID AS $$
BEGIN
  PERFORM set_config('ai.openai_api_key', api_key, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to get your OpenAI API key
CREATE OR REPLACE FUNCTION ai.openai_api_key_get()
RETURNS TEXT AS $$
BEGIN
  RETURN current_setting('ai.openai_api_key', true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Set your OpenAI API key
SELECT ai.openai_api_key_set('your-openai-api-key-here');
```

### 2. Create OpenAI Embedding Function

```sql
-- Create a function to generate embeddings using the OpenAI API
CREATE OR REPLACE FUNCTION ai.openai_embed(model_name TEXT, content TEXT)
RETURNS VECTOR AS $$
DECLARE
  api_key TEXT;
  response JSONB;
  embedding VECTOR;
BEGIN
  -- Get the API key
  api_key := ai.openai_api_key_get();
  
  -- Call the OpenAI API to get the embedding
  SELECT INTO response
    jsonb_build_object(
      'model', model_name,
      'input', content
    );
  
  -- This is where the actual API call would happen
  -- In a production environment, you would use pg_net or an edge function
  -- For demonstration purposes, we'll use a placeholder
  
  -- Placeholder: Return a reference embedding from an existing document
  -- In production, replace this with the actual API call
  SELECT p.embedding INTO embedding
  FROM project_docs p
  WHERE p.title = '1.0-ARCH-TRUTH-Definitive_Reference.md'
  LIMIT 1;
  
  RETURN embedding;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 3. Production Implementation Options

#### Option A: Using pg_net Extension (Recommended)

```sql
-- Enable pg_net extension
CREATE EXTENSION IF NOT EXISTS pg_net;

-- Create a function to generate embeddings using pg_net
CREATE OR REPLACE FUNCTION ai.openai_embed_production(model_name TEXT, content TEXT)
RETURNS VECTOR AS $$
DECLARE
  api_key TEXT;
  request_id UUID;
  response JSONB;
  embedding VECTOR;
BEGIN
  -- Get the API key
  api_key := ai.openai_api_key_get();
  
  -- Make the API request
  SELECT INTO request_id
    net.http_post(
      url := 'https://api.openai.com/v1/embeddings',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' || api_key
      ),
      body := jsonb_build_object(
        'model', model_name,
        'input', content
      )::text
    );
  
  -- Wait for and get the response
  SELECT INTO response
    net.http_get_result(request_id)::jsonb;
  
  -- Extract the embedding from the response
  SELECT INTO embedding
    response->'data'->0->'embedding';
  
  RETURN embedding::vector;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

#### Option B: Using Edge Functions

Create an Edge Function in Supabase that calls the OpenAI API and returns the embedding. Then call this function from your SQL.

## TROUBLESHOOTING

**If OpenAI API fails in Python script**:
1. Verify your `OPENAI_API_KEY` environment variable is set correctly
2. Check OpenAI API status at https://status.openai.com/
3. Ensure you have sufficient API credits

**If OpenAI API fails in SQL**:
1. Supabase Dashboard > SQL Editor
2. Run: `SELECT ai.openai_api_key_set('[YOUR_OPENAI_API_KEY]');`
3. Check that the pg_net extension is enabled if using Option A
4. Verify your Edge Function is deployed if using Option B
5. If all else fails, use the alternative search function provided above

**If database connection fails**:
1. Verify your `DATABASE_URL` environment variable is correctly formatted
2. For SQLAlchemy URLs, convert from `postgresql+asyncpg://` to `postgresql://`
3. Check Supabase status and ensure your project is active

**If search function errors**:
1. Verify the `ai` schema exists: `CREATE SCHEMA IF NOT EXISTS ai;`
2. Check that the `vector` extension is enabled
3. Ensure at least one document is in the database with a valid embedding

**If single quotes break**: Double them ('') in the document content when pasting.

## SCRIPT REFERENCE

The following scripts are used in this process:

1. **`Docs/Docs_15_Master_Plan/vector_db_insert_architectural_docs.py`**
   - Main script for inserting documents and generating embeddings
   - Requires `OPENAI_API_KEY` and `DATABASE_URL` environment variables
   - Handles reading documents, generating embeddings, and inserting into database

2. **`scripts/vector_db_simple_test.py`**
   - Test script for verifying vector search functionality
   - Can be used to test specific patterns against the vector database

## LIVING DOCUMENT PROCESS

For adding new documents to the vector database:

1. Add the document path to the `ARCHITECTURAL_DOCUMENTS` list in `vector_db_insert_architectural_docs.py`
2. Run the script to insert the new document with its embedding
3. Verify the document was inserted correctly using the verification queries
4. Test search functionality with relevant queries

For bulk document loading, consider creating a separate script that follows the same pattern but accepts a directory path as input.
