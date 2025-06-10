# Vector Database Maintenance Procedures

This document outlines key maintenance tasks for the ScraperSky Vector Database.

## 1. OpenAI API Key Rotation

- **Frequency:** Every 90 days or immediately upon suspected compromise.
- **Command:**
  ```sql
  SELECT ai.openai_api_key_set('your-new-openai-api-key');
  ```

## 2. Performance Check

- **Frequency:** Monthly, or as needed.
- **Command:** To analyze search performance:
  First, you would need a sample query embedding. Let's assume you have generated an embedding for 'test query' client-side and have it as a SQL-formatted vector string, e.g., `'[0.01,-0.02,...]'` (let's call this `[SAMPLE_QUERY_EMBEDDING_STRING]`).
  ```sql
  EXPLAIN ANALYZE SELECT title, content, 1 - (embedding <=> '[SAMPLE_QUERY_EMBEDDING_STRING]'::vector) AS similarity 
  FROM public.project_docs 
  ORDER BY similarity DESC 
  LIMIT 10;
  ```
  This analyzes the performance of a direct vector similarity search.

## 3. Null-Embedding Scan

- **Frequency:** After bulk loads or if search results are unexpectedly sparse.
- **Command:** To find documents with null embeddings:
  ```sql
  SELECT id, title FROM public.project_docs WHERE embedding IS NULL;
  ```

## 4. Re-embed Documents on Model Upgrade

- **Context:** If the underlying embedding model (e.g., `text-embedding-ada-002`) is upgraded or changed, existing embeddings may need to be regenerated.
- **Command (Example for a single document):**
  ```sql
  UPDATE project_docs
  SET embedding = ai.openai_embed_production('text-embedding-ada-002', content)::vector
  WHERE title = 'document_to_update.md';
  ```
- **Note:** For bulk re-embedding, a script would be more appropriate. This typically involves iterating through documents, generating new embeddings, and updating the records.
