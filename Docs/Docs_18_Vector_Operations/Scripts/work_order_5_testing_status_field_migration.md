# Work Order: Testing - Embedding Status Field Migration

**Date:** 2025-06-09
**Version:** 1.0
**Status:** Draft

## 1. Objective

To comprehensively test and verify the successful migration of the document status tracking system from dual fields (`should_be_vectorized`, `embedding_status` [old values]) to a single, standardized `embedding_status` field. This includes validating the correct functionality of all updated scripts (`insert_architectural_docs.py`, `4-registry-archive-manager.py`, `5-vector-db-cleanup-manager.py`) and the overall document lifecycle management under the new system.

## 2. Scope

End-to-end testing of the following lifecycle stages for a test document:
- Initial registration and marking for vectorization.
- Vectorization and status update to 'active'.
- Document content modification and re-vectorization.
- Document archival (filesystem deletion and registry update).
- Cleanup of archived document entries from the vector database.

## 3. Prerequisites

- **Database Schema:** All deprecated columns (`should_be_vectorized`, `is_vectorized`) must be removed from the `document_registry` table. The `embedding_status` column must be the sole status indicator using values: `'queue'`, `'active'`, `'archived'`, `'orphan'`.
- **Scripts:** All relevant Python scripts (`1-registry-directory-manager.py`, `2-registry-document-scanner.py`, `insert_architectural_docs.py`, `3-registry-update-flag-manager.py`, `4-registry-archive-manager.py`, `5-vector-db-cleanup-manager.py`) must be updated to reflect the new `embedding_status` logic and deployed to the testing environment.
- **Test Document:** A new markdown file named `v_test_lifecycle_doc.md` should be created with sample content. This file will be placed in an approved directory for scanning.
- **Approved Directory:** Ensure a directory (e.g., `Docs/Docs_X_Test_Bed/`) is approved for scanning using `1-registry-directory-manager.py --approve /path/to/Docs_X_Test_Bed/`.
- **Database Access:** Ability to execute SQL queries against the `document_registry` and `project_docs` tables using `mcp4_execute_sql` with project ID `ddfldwzhdhhzhxywqnyz`.
- **Environment Variables:** `DATABASE_URL` and `OPENAI_API_KEY` must be correctly set in the environment where scripts are run.

## 4. Test Cases

**Test Document:** `v_test_lifecycle_doc.md`
**Approved Test Directory:** (e.g., `scraper-sky-backend/Docs/Docs_X_Test_Bed/` - replace with actual path)

--- 

**Test Case 1: New Document Ingestion & Vectorization**

*   **Action 1.1:** Place `v_test_lifecycle_doc.md` into the approved test directory.
    ```markdown
    # v_test_lifecycle_doc.md - Initial Content

    This is the first version of the test document for lifecycle testing.
    It contains unique keywords: AlphaVersion, LifecycleTest.
    ```
*   **Action 1.2:** Run the document scanner.
    ```bash
    python Docs/Docs_19_File-2-Vector-Registry-System/2-registry-document-scanner.py --scan
    ```
*   **Verification 1.2:** Query `document_registry` for `v_test_lifecycle_doc.md`.
    *Expected:* Record exists, `embedding_status` = `'queue'`, `file_hash` is populated, `last_seen_at` is current, `needs_update` = `FALSE` (or `TRUE` if scanner sets it for new files, then `insert_architectural_docs` clears it).
    ```sql
    SELECT file_path, embedding_status, file_hash, last_seen_at, needs_update FROM document_registry WHERE file_path LIKE '%v_test_lifecycle_doc.md';
    ```
*   **Action 1.3:** Run the document insertion script.
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py
    ```
*   **Verification 1.3.1:** Query `document_registry` for `v_test_lifecycle_doc.md`.
    *Expected:* `embedding_status` = `'active'`, `last_embedded_at` is current, `needs_update` = `FALSE`.
    ```sql
    SELECT file_path, embedding_status, last_embedded_at, needs_update FROM document_registry WHERE file_path LIKE '%v_test_lifecycle_doc.md';
    ```
*   **Verification 1.3.2:** Query `project_docs` for `v_test_lifecycle_doc.md`.
    *Expected:* Record exists, `title` matches, `embedding` is not null.
    ```sql
    SELECT id, title, (embedding IS NOT NULL) as has_embedding FROM project_docs WHERE title = 'v_test_lifecycle_doc.md';
    ```
*   **Verification 1.3.3:** Perform semantic search for content from `v_test_lifecycle_doc.md`.
    *Expected:* `v_test_lifecycle_doc.md` appears in results for query 'AlphaVersion LifecycleTest'.
    ```javascript
    // MCP Call for semantic search. 
    // Step 1 (Client-side): Generate embedding for 'AlphaVersion LifecycleTest'. Let's call it 'embedding_vector_string_1'.
    // Step 2 (MCP Call):
    mcp4_execute_sql({
      "project_id": "ddfldwzhdhhzhxywqnyz",
      "query": `SELECT title, 1 - (embedding <=> '${embedding_vector_string_1}'::vector) AS similarity FROM public.project_docs ORDER BY similarity DESC LIMIT 5;`
    })
    // Ensure 'embedding_vector_string_1' is correctly formatted as a SQL vector string, e.g., '[0.1,0.2,...]'.
    ```

--- 

**Test Case 2: Document Modification & Re-vectorization**

*   **Action 2.1:** Modify the content of `v_test_lifecycle_doc.md` on the filesystem.
    ```markdown
    # v_test_lifecycle_doc.md - Updated Content

    This is the MODIFIED second version of the test document.
    It now contains new unique keywords: BetaVersion, RevectorizeTest.
    ```
*   **Action 2.2:** Run the document scanner.
    ```bash
    python Docs/Docs_19_File-2-Vector-Registry-System/2-registry-document-scanner.py --scan
    ```
*   **Verification 2.2:** Query `document_registry` for `v_test_lifecycle_doc.md`.
    *Expected:* `file_hash` is updated (different from Test Case 1), `needs_update` = `TRUE`, `embedding_status` = `'active'`. `last_seen_at` is current.
    ```sql
    SELECT file_path, embedding_status, file_hash, last_seen_at, needs_update FROM document_registry WHERE file_path LIKE '%v_test_lifecycle_doc.md';
    ```
*   **Action 2.3:** Run the document insertion script.
    ```bash
    python Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py
    ```
*   **Verification 2.3.1:** Query `document_registry` for `v_test_lifecycle_doc.md`.
    *Expected:* `embedding_status` = `'active'`, `last_embedded_at` is updated (more recent than Test Case 1), `needs_update` = `FALSE`.
    ```sql
    SELECT file_path, embedding_status, last_embedded_at, needs_update FROM document_registry WHERE file_path LIKE '%v_test_lifecycle_doc.md';
    ```
*   **Verification 2.3.2:** Perform semantic search for *new* content from `v_test_lifecycle_doc.md`.
    *Expected:* `v_test_lifecycle_doc.md` appears in results for query 'BetaVersion RevectorizeTest'. Search for 'AlphaVersion LifecycleTest' should yield lower or no relevance.
    ```javascript
    // MCP Call for semantic search.
    // Step 1 (Client-side): Generate embedding for 'BetaVersion RevectorizeTest'. Let's call it 'embedding_vector_string_2'.
    // Step 2 (MCP Call):
    mcp4_execute_sql({
      "project_id": "ddfldwzhdhhzhxywqnyz",
      "query": `SELECT title, 1 - (embedding <=> '${embedding_vector_string_2}'::vector) AS similarity FROM public.project_docs ORDER BY similarity DESC LIMIT 5;`
    })
    // Ensure 'embedding_vector_string_2' is correctly formatted as a SQL vector string.
    ```

--- 

**Test Case 3: Document Archival**

*   **Action 3.1:** Delete `v_test_lifecycle_doc.md` from the filesystem.
*   **Action 3.2:** Run the archive manager to list missing files.
    ```bash
    python Docs/Docs_19_File-2-Vector-Registry-System/4-registry-archive-manager.py --list-missing
    ```
*   **Verification 3.2:** `v_test_lifecycle_doc.md` should be listed as missing.
*   **Action 3.3:** Run the archive manager to mark missing files as archived.
    ```bash
    python Docs/Docs_19_File-2-Vector-Registry-System/4-registry-archive-manager.py --mark-missing-as-archived --auto-approve
    ```
*   **Verification 3.3:** Query `document_registry` for `v_test_lifecycle_doc.md`.
    *Expected:* `embedding_status` = `'archived'`. `last_seen_at` may or may not be updated by this script, check script logic.
    ```sql
    SELECT file_path, embedding_status, last_seen_at FROM document_registry WHERE file_path LIKE '%v_test_lifecycle_doc.md';
    ```

--- 

**Test Case 4: Vector DB Cleanup of Archived Document**

*   **Action 4.1:** Run the vector DB cleanup manager to list archived documents eligible for removal.
    ```bash
    python Docs/Docs_19_File-2-Vector-Registry-System/5-vector-db-cleanup-manager.py --list-archived
    ```
*   **Verification 4.1:** `v_test_lifecycle_doc.md` (or its ID from `project_docs`) should be listed.
*   **Action 4.2:** Run the vector DB cleanup manager to remove archived documents.
    ```bash
    python Docs/Docs_19_File-2-Vector-Registry-System/5-vector-db-cleanup-manager.py --remove-archived --auto-approve
    ```
*   **Verification 4.2.1:** Query `project_docs` for `v_test_lifecycle_doc.md`.
    *Expected:* Record is removed. Count should be 0.
    ```sql
    SELECT COUNT(*) FROM project_docs WHERE title = 'v_test_lifecycle_doc.md';
    ```
*   **Verification 4.2.2:** Query `document_registry` for `v_test_lifecycle_doc.md`.
    *Expected:* Record still exists, `embedding_status` = `'archived'`. This confirms the registry retains a record of the archived document.
    ```sql
    SELECT file_path, embedding_status FROM document_registry WHERE file_path LIKE '%v_test_lifecycle_doc.md';
    ```

## 5. Documentation of Results

- For each test case and action, record the exact command run.
- For each verification step, record the SQL query or MCP call made and its full output.
- Note any deviations from expected results, errors encountered, or unexpected behavior.
- Capture screenshots or log snippets if they help clarify an issue.

## 6. Expected Outcomes Summary

- All test cases pass successfully.
- The `embedding_status` field in `document_registry` accurately reflects the document's state throughout its lifecycle (`'queue'` -> `'active'` -> `'archived'`).
- The `needs_update` flag is correctly managed.
- Scripts execute without errors related to deprecated columns or incorrect status logic.
- The `project_docs` table (vector database) correctly reflects the presence or absence of documents based on their registry status and cleanup operations.
- Semantic search yields relevant results for active and updated documents.

