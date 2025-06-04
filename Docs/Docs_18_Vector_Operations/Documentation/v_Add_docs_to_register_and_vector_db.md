# ScraperSky Vector Database Cheat Sheet

## Table of Contents
1. [Identifying Documents for Vectorization](#identifying-documents-for-vectorization)
2. [Adding Documents to Registry](#adding-documents-to-registry)
3. [Loading Documents to Vector Database](#loading-documents-to-vector-database)
4. [Updating Registry Status](#updating-registry-status)
5. [Verifying Results](#verifying-results)

## Identifying Documents for Vectorization

1. Look for documents with `v_` prefix in target directory:
   ```
   # Example: Find v_ prefixed files in a directory
   find /path/to/directory -type f -name "v_*"
   ```

2. These are the documents that should be added to the vector database.

## Adding Documents to Registry

1. Use SQL to add documents to the `document_registry` table:
   ```sql
   INSERT INTO document_registry (
     title, 
     file_path,
     parent_directory,
     should_be_vectorized,
     is_vectorized,
     embedding_status
   ) VALUES (
     'v_document_name.md',
     '/full/path/to/v_document_name.md',
     '/full/path/to/parent_directory',
     true,
     false,
     'pending'
   );
   ```

2. Use MCP to execute the SQL:
   ```
   mcp4_execute_sql(
     project_id="ddfldwzhdhhzhxywqnyz",
     query="INSERT INTO document_registry..."
   )
   ```

## Loading Documents to Vector Database

1. Add document paths to `insert_architectural_docs.py` script:
   ```python
   # Add new documents to the ARCHITECTURAL_DOCUMENTS list
   ARCHITECTURAL_DOCUMENTS = [
     # Existing documents...
     {"name": "v_new_document.md", "path": f"{BASE_DIR}/path/to/v_new_document.md"}
   ]
   ```

2. Run the script to load documents into vector database:
   ```
   cd /path/to/Scripts
   python insert_architectural_docs.py
   ```

## Updating Registry Status

1. Use SQL to update the status of vectorized documents:
   ```sql
   UPDATE document_registry 
   SET is_vectorized = true, 
       embedding_status = 'completed', 
       updated_at = NOW() 
   WHERE title IN ('v_document1.md', 'v_document2.md');
   ```

2. Use MCP to execute the SQL:
   ```
   mcp4_execute_sql(
     project_id="ddfldwzhdhhzhxywqnyz",
     query="UPDATE document_registry..."
   )
   ```

## Verifying Results

1. Check document count in vector database and ensure it matches expectations (currently 28 documents total):
   ```sql
   SELECT COUNT(*) FROM public.project_docs;
   ```

2. Verify documents are properly marked in registry:
   ```sql
   SELECT title, is_vectorized, embedding_status 
   FROM document_registry 
   WHERE title IN ('v_document1.md', 'v_document2.md');
   ```

3. Ensure all documents with `v_` prefix are vectorized:
   ```sql
   SELECT COUNT(*) FROM document_registry 
   WHERE should_be_vectorized = true AND is_vectorized = false;
   ```

4. Verify that the document count in the registry matches the document count in the vector database:
   ```sql
   SELECT COUNT(*) FROM document_registry WHERE is_vectorized = true;
   SELECT COUNT(*) FROM public.project_docs;
   ```
   These two counts should match.

