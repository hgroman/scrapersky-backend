# Work Order: Modify `insert_architectural_docs.py`

**Date:** 2025-06-08
**Assignee:** Cascade AI
**Reporter:** USER

## 1. Why (Purpose of Change)

The current `insert_architectural_docs.py` script uses a hardcoded list of documents to process for vectorization and insertion into the `public.project_docs` table. This is disconnected from the `document_registry` table, which is managed by `1-registry-directory-manager.py` and `2-registry-document-scanner.py` and is intended to be the source of truth for which documents need vectorization.

This modification aims to integrate `insert_architectural_docs.py` with the `document_registry` system to create a cohesive, registry-driven workflow for document vectorization and ingestion.

## 2. What (Scope of Change)

The `insert_architectural_docs.py` script will be modified to:

*   Remove the hardcoded `ARCHITECTURAL_DOCUMENTS` list.
*   Query the `document_registry` table for documents that need processing (e.g., where `is_vectorized = FALSE` or `needs_update = TRUE`).
*   For each identified document:
    *   Read its content using the `file_path` from the `document_registry`.
    *   Generate an embedding.
    *   Insert or update the document in the `public.project_docs` table.
    *   Update the corresponding record in the `document_registry` table to reflect its new status (e.g., set `is_vectorized = TRUE`, `needs_update = FALSE`, `embedding_status = 'completed'`, `last_embedded_at = NOW()`).

## 3. How (Implementation Details)

*   **Database Connection**: Utilize the existing `asyncpg` connection to interact with both `public.project_docs` and `document_registry` tables.
*   **Query `document_registry`**: Construct an SQL query to select necessary fields (e.g., `id`, `title`, `file_path`) from `document_registry` for records matching the criteria (`is_vectorized = FALSE` OR `needs_update = TRUE`).
*   **Loop and Process**: Iterate through the fetched records.
    *   File reading, embedding generation, and insertion into `public.project_docs` logic will largely remain the same, but adapted to use data from the `document_registry` query results.
*   **Update `document_registry`**: After a document is successfully processed and inserted/updated in `public.project_docs`, execute an `UPDATE` SQL statement on the `document_registry` table for that document's ID or title, setting the appropriate status flags and timestamps.
*   **Error Handling**: Ensure robust error handling for database operations, file operations, and API calls.
*   **Logging**: Maintain or enhance logging to track the script's progress and any issues encountered.

## 4. Where (Affected Files/Modules)

*   **Primary:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py`
*   **Related (for context/consistency, but not directly modified by this WO):**
    *   `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_19_File-2-Vector-Registry-System/2-registry-document-scanner.py`
    *   `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_18_Vector_Operations/v_knowledge_librarian_persona_v2.md` (will need updating after this script is modified)

## 5. Verification (How to Confirm Success)

*   **Pre-condition**: Have documents in the `document_registry` table marked as `is_vectorized = FALSE` or `needs_update = TRUE` by `2-registry-document-scanner.py`.
*   Run the modified `insert_architectural_docs.py` script.
*   **Post-condition Check 1**: Verify that the processed documents are present in the `public.project_docs` table with correct content and non-null embeddings.
*   **Post-condition Check 2**: Verify that the corresponding records in the `document_registry` table have been updated (e.g., `is_vectorized = TRUE`, `needs_update = FALSE`, `embedding_status = 'completed'`, `last_embedded_at` is recent).
*   **Post-condition Check 3**: Verify that documents not meeting the criteria in `document_registry` were not processed.
*   **Logging**: Review logs for successful operations and absence of errors for processed documents.

## 6. Rollback Plan

*   Restore `insert_architectural_docs.py` from its backup: `insert_architectural_docs.py.bak`.
