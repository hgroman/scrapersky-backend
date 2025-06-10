# ScraperSky Vector DB & Registry - Key Documents

**Date:** 2025-06-09
**Version:** 2.0
**Status:** Active

## I. Core System & Architectural Guides

1.  **`Docs/Docs_19_File-2-Vector-Registry-System/v_vector_ingestion_pipeline_dev_guide.md`**
    *   **Description:** Comprehensive developer guide detailing the architecture, components, end-to-end workflow, and core principles of the document ingestion, vectorization, and registry pipeline. **This is the primary entry point for understanding the entire system.**
2.  **`Docs/Docs_18_Vector_Operations/Documentation/v_complete_reference.md`**
    *   **Description:** A broader reference document for vector database related information. (Note: Review for outdated links; its "Test Questions" and "Document Registry Management" sections are most current.)
3.  **`Docs/Docs_19_File-2-Vector-Registry-System/0-registry_librarian_persona.md`**
    *   **Description:** Details the AI persona, responsibilities, tools, and operational workflows for the Document Registry Management system, including scripts `1-registry-directory-manager.py` through `7-registry-orphan-purger.py`.

## II. Connectivity & Procedural Guides

4.  **`Docs/Docs_18_Vector_Operations/Documentation/v_connectivity_patterns.md`**
    *   **Description:** Quick reference for approved MCP and Asyncpg database connection code snippets. Use for copy-pasting.
5.  **`Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_async_4_vector_ops.md`**
    *   **Description:** Comprehensive guide covering Asyncpg (for programmatic operations) connectivity methods. **Primary reference for programmatic DB connection.**
6.  **`Docs/Docs_18_Vector_Operations/Documentation/v_db_connectivity_mcp_4_manual_ops.md`**
    *   **Description:** Focused guide for using the MCP method for manual database operations and AI-driven queries.

## III. Core Scripts (Primary Operations)

### A. Automated Vectorization & Core Async Operations (Located in `Docs/Docs_18_Vector_Operations/Scripts/`)
7.  **`Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py`**
    *   **Description:** Primary script for fetching documents marked 'queue' from `document_registry`, generating embeddings, and inserting/updating them into `project_docs`. Uses Asyncpg.

### B. Registry Management (Located in `Docs/Docs_19_File-2-Vector-Registry-System/`)
8. **Registry Management Scripts Suite:**
    *   `1-registry-directory-manager.py`
    *   `2-registry-document-scanner.py`
    *   `3-registry-update-manager.py`
    *   `4-registry-archive-manager.py`
    *   `5-vector-db-cleanup-manager.py`
    *   `6-registry-orphan-detector.py`
    *   `7-registry-orphan-purger.py`

### C. Testing (Located in `Docs/Docs_18_Vector_Operations/Scripts/`)
9. **`Docs/Docs_18_Vector_Operations/Scripts/simple_test.py`**
    *   **Description:** Script for testing vector database search functionality. Uses Asyncpg.

## IV. Maintenance & Troubleshooting

10. **`Docs/Docs_18_Vector_Operations/Documentation/v_maintenance_procedures.md`**
    *   **Description:** Outlines key maintenance tasks for the Vector DB, including API key rotation, performance checks, and re-embedding procedures.
11. **`Docs/Docs_18_Vector_Operations/Documentation/v_troubleshooting_guide.md`**
    *   **Description:** Provides quick solutions and a cheatsheet for common issues encountered with the Vector Database.

## V. Diagnostics & Historical Information

12. **`Docs/Docs_18_Vector_Operations/Documentation/v_nan_issue_resolution.md`**
    *   **Description:** Historical document detailing the resolution of the "Similarity: nan" issue.

## VI. Notes

*   Deprecated documents and older system versions have been moved to `Docs/Docs_Archive/`.
*   The `Docs/Docs_16_ScraperSky_Code_Canon` directory is archived.
*   Individual `README.md` files within subdirectories like `MCP-Manual-ops/`, `Async-Vector-ops/`, and `Setup/` (if present and containing scripts) provide specific context for those scripts.

## VII. Key Project Constants

*   **Supabase Project ID:** `ddfldwzhdhhzhxywqnyz`
*   **MCP Function for SQL Execution:** `mcp4_execute_sql` (Used for direct database queries, often in `MCP-Manual-ops/` scripts)
*   **Primary Vector Database Table:** `public.project_docs` (Stores vectorized document content and embeddings. Uses the `pgvector` extension.)
