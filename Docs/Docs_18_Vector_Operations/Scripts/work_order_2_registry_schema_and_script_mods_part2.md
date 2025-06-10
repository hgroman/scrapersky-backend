# Work Order: Modify `document_registry` Schema via MCP and Update Script (Part Two)

**Date:** 2025-06-08
**Assignee:** Cascade AI
**Reporter:** USER
**Status:** Proposed

## 1. Why (Purpose of Change)

To restore and fully implement robust data tracking for document vectorization within the `public.document_registry` table. This ensures the `insert_architectural_docs.py` script accurately reflects the intended workflow, including tracking when documents explicitly need updates (`needs_update`) and when they were last successfully embedded (`last_embedded_at`). This work order corrects previous shortcuts where functionality was removed instead of ensuring necessary database schema elements were present and properly utilized.

## 2. What (Scope of Change)

### 2.1. Database Schema Modification (`public.document_registry` on Supabase via MCP)
The following columns will be added to the `public.document_registry` table. These modifications are to be performed using an MCP (Model Context Protocol) facilitated mechanism for accessing and altering the Supabase database schema:

*   Add new column: `needs_update BOOLEAN DEFAULT FALSE NOT NULL`
    *   Purpose: To explicitly flag documents that require re-processing/re-embedding even if previously processed.
*   Add new column: `last_embedded_at TIMESTAMPTZ NULL`
    *   Purpose: To store the timestamp of the last successful embedding generation for a document.

### 2.2. Script Modification (`insert_architectural_docs.py`)
The script will be updated to correctly utilize the new and existing schema fields:

*   **Query Logic (`get_vectorization_candidates` function):**
    *   Modify the SQL query to select documents where `(should_be_vectorized = TRUE AND embedding_status != 'completed') OR needs_update = TRUE`.
*   **Status Update Logic (`update_document_registry_status` function):**
    *   Upon successful embedding and insertion into `project_docs`:
        *   Set `embedding_status = 'completed'`.
        *   Set `should_be_vectorized = FALSE`.
        *   Set `needs_update = FALSE`.
        *   Set `last_embedded_at` to the current UTC timestamp.
        *   Set `error_message = NULL`.
    *   Upon processing error (e.g., file not found, embedding generation failure):
        *   Set `embedding_status` to an appropriate error code (e.g., `error_file_not_found`, `error_embedding_failed`).
        *   Set `error_message` to a description of the error.
        *   Ensure `should_be_vectorized` remains `TRUE` (as the document still requires processing).
        *   `last_embedded_at` should remain unchanged or be set to NULL if appropriate for the error.
        *   `needs_update` should remain unchanged by error handling itself (it's an input flag).

## 3. How (Implementation Details)

### Step 1: Modify Database Schema via MCP for Supabase
1.  Identify and utilize the appropriate MCP tool or interface designated for schema modifications on the Supabase instance (connected via `DATABASE_URL`).
2.  Execute the following DDL commands through the MCP mechanism:
    *   `ALTER TABLE public.document_registry ADD COLUMN IF NOT EXISTS needs_update BOOLEAN DEFAULT FALSE NOT NULL;`
    *   `ALTER TABLE public.document_registry ADD COLUMN IF NOT EXISTS last_embedded_at TIMESTAMPTZ NULL;`
3.  Verify successful execution and schema update via MCP or Supabase interface.

### Step 2: Update `insert_architectural_docs.py` Script
1.  Modify the Python script `insert_architectural_docs.py` to implement the logic described in section 2.2.
2.  This involves changing the SQL queries in `get_vectorization_candidates` and the SQL UPDATE statements and logic within `update_document_registry_status`.

## 4. Where (Affected Systems/Files)

*   **Database Table:** `public.document_registry` (on Supabase, accessed via MCP)
*   **Python Script:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py`

## 5. Verification (How to Confirm Success)

1.  **Schema Verification:**
    *   Using an MCP-based database inspection tool or the Supabase SQL editor, confirm that the `needs_update` and `last_embedded_at` columns exist in `public.document_registry` with the specified types and defaults.
2.  **Script Functionality Verification:**
    *   **Scenario 1 (Update Existing):**
        *   Manually set `needs_update = TRUE` and `should_be_vectorized = FALSE`, `embedding_status = 'completed'` for a document in `document_registry` that was previously processed successfully.
        *   Run the modified `insert_architectural_docs.py`.
        *   **Expected:** The document is re-processed. In `document_registry`, `embedding_status` remains `'completed'`, `should_be_vectorized` becomes `FALSE`, `needs_update` becomes `FALSE`, and `last_embedded_at` is updated to a recent timestamp. `project_docs` is updated.
    *   **Scenario 2 (New Document):**
        *   Ensure a new document is marked with `should_be_vectorized = TRUE` and `embedding_status = 'pending'` (and `needs_update = FALSE`).
        *   Run the script.
        *   **Expected:** The document is processed. In `document_registry`, `embedding_status` becomes `'completed'`, `should_be_vectorized` becomes `FALSE`, `needs_update` remains `FALSE`, and `last_embedded_at` is set. `project_docs` contains the new entry.
    *   **Scenario 3 (Error Handling):**
        *   Ensure a document is marked `should_be_vectorized = TRUE` but its `file_path` is invalid.
        *   Run the script.
        *   **Expected:** In `document_registry`, `embedding_status` becomes `'error_file_not_found'`, `error_message` is populated, `should_be_vectorized` remains `TRUE`. `last_embedded_at` is not updated.

## 6. Rollback Plan

*   **Database Schema (MCP Modifications):**
    *   If MCP-based schema modification fails or causes issues, investigate MCP logs.
    *   If DDL rollback is necessary (to be performed via MCP or manually if MCP rollback isn't feasible):
        *   `ALTER TABLE public.document_registry DROP COLUMN IF EXISTS needs_update;`
        *   `ALTER TABLE public.document_registry DROP COLUMN IF EXISTS last_embedded_at;`
        *   (Data in these columns would be lost).
*   **Script (`insert_architectural_docs.py`):**
    *   Revert the script to its previous state using version control.
    *   Alternatively, use the backup `insert_architectural_docs.py.bak` (note: this backup is from before the initial modifications and would not include the first round of registry integration changes). A more targeted revert of the specific changes from this work order would be preferable.
