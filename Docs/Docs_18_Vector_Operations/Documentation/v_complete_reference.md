# ScraperSky Vector Database: Complete Reference Guide

**Date:** 2025-06-09  
**Version:** 1.2  
**Status:** Active  

## Purpose

This document serves as the comprehensive reference guide for the ScraperSky Vector Database system. It consolidates references to all key documents, scripts, and tools related to the vector database, ensuring that all AI pairing partners and personas have a complete understanding of the system.

## Vector Database Overview

The ScraperSky Vector Database is a semantic search system built on Supabase PostgreSQL with the pgvector extension. It stores embeddings of architectural documents, enabling semantic search across the codebase's architectural standards, patterns, and guidelines.

## Key Documents & Systems Reference

This section lists the primary authoritative documents and systems. For a curated list of essential reading, always refer to `Docs/Docs_18_Vector_Operations/v_key_documents.md`.

### I. Core Architectural & System Guides

1.  **Vector Ingestion Pipeline Developer Guide:** [`v_vector_ingestion_pipeline_dev_guide.md`](../../Docs_19_File-2-Vector-Registry-System/v_vector_ingestion_pipeline_dev_guide.md)
    *   **Description:** The primary entry point for understanding the entire document ingestion, vectorization, and registry pipeline. Details architecture, components, end-to-end workflow, and core principles.
2.  **Vector Operations Overview (README):** [`v_Docs_18_Vector_Operations_README.md`](../v_Docs_18_Vector_Operations_README.md)
    *   **Description:** Provides an overview of the `Docs_18_Vector_Operations` directory, its purpose, current goals, roadmap, naming conventions, and technical debt strategy.
3.  **Document Registry Source of Truth:** The `document_registry` table in the Supabase PostgreSQL database.
    *   **Description:** This table is the single source of truth for all documents intended for vectorization, including their metadata, file paths, and processing status (e.g., `queue`, `active`, `archived`, `orphan`). It is managed by the Registry Management script suite.

### II. AI Personas & Operational Directives

4.  **Registry Librarian Persona & System Overview:** [`0-registry_librarian_persona.md`](../../Docs_19_File-2-Vector-Registry-System/0-registry_librarian_persona.md)
    *   **Description:** Details the AI persona, responsibilities, tools, and operational workflows for the Document Registry Management system, including scripts `1-registry-directory-manager.py` through `7-registry-orphan-purger.py`.
5.  **Vector DB Knowledge Librarian Persona:** [`v_knowledge_librarian_persona_v2.md`](../v_knowledge_librarian_persona_v2.md)
    *   **Description:** Defines the operational parameters, responsibilities, and mandatory reading for the AI persona responsible for direct Vector DB interactions, including using `insert_architectural_docs.py`.

### III. Connectivity & Procedural Guides

6.  **Asyncpg Connectivity for Vector Ops:** [`v_db_connectivity_async_4_vector_ops.md`](./v_db_connectivity_async_4_vector_ops.md)
    *   **Description:** Comprehensive guide for programmatic database connections using `asyncpg`, primarily for scripts performing vector operations.
7.  **MCP Connectivity for Manual Ops:** [`v_db_connectivity_mcp_4_manual_ops.md`](./v_db_connectivity_mcp_4_manual_ops.md)
    *   **Description:** Focused guide for using the MCP method (`mcp4_execute_sql`) for manual database operations and AI-driven queries.

### IV. Maintenance & Troubleshooting

8.  **Maintenance Procedures:** [`v_maintenance_procedures.md`](./v_maintenance_procedures.md)
    *   **Description:** Outlines key maintenance tasks for the Vector DB, including API key rotation, performance checks, and re-embedding procedures.
9.  **Troubleshooting Guide:** [`v_troubleshooting_guide.md`](./v_troubleshooting_guide.md)
    *   **Description:** Provides quick solutions and a cheatsheet for common issues encountered with the Vector Database.

### V. Core Scripts (Primary Operations)

10. **Document Insertion Script:** [`insert_architectural_docs.py`](../Scripts/insert_architectural_docs.py)
    *   **Description:** Primary script for fetching documents marked 'queue' from `document_registry`, generating embeddings using OpenAI, and inserting/updating them into the `project_docs` table in the Vector DB. Uses `asyncpg`.
11. **Vector DB Test Script:** [`simple_test.py`](../Scripts/simple_test.py)
    *   **Description:** Script for testing vector database search functionality. Performs semantic search and verifies results. Uses `asyncpg`.

### VI. Diagnostics & Historical Information

12. **NaN Issue Resolution:** [`v_nan_issue_resolution.md`](./v_nan_issue_resolution.md)
    *   **Description:** Historical document detailing the resolution of the "Similarity: nan" issue, which involved vector normalization.

## CRITICAL: MCP Server Integration

To query the vector database, you **MUST** use the following specific parameters:

1. **Function Name:** `mcp4_execute_sql` (not just "execute_sql")
2. **Project ID:** `ddfldwzhdhhzhxywqnyz` (always use this exact ID)

Example of performing semantic search:

1.  **Client-Side Embedding Generation:** First, generate an embedding for your search query (e.g., 'your search query') using the OpenAI API (model `text-embedding-ada-002`). This will produce a vector like `[0.01, -0.02, ...]`. Format this vector as a string compatible with SQL, e.g., `'[0.01,-0.02,...]'`.

2.  **MCP Query for Similarity Search:**
    ```javascript
    // Assume 'client_generated_embedding_string' holds the formatted vector string.
    mcp4_execute_sql({
      "project_id": "ddfldwzhdhhzhxywqnyz",
      "query": `SELECT title, content, 1 - (embedding <=> '${client_generated_embedding_string}'::vector) AS similarity FROM public.project_docs ORDER BY similarity DESC LIMIT 5;`
    })
    ```
Refer to `v_db_connectivity_mcp_4_manual_ops.md` for a more detailed example.

## Document Registry Management

The document registry is maintained within the `document_registry` database table. This table is the single source of truth for documents intended for vectorization, their metadata, and current status.

Management of the registry is performed using a suite of Python scripts located in `Docs/Docs_19_File-2-Vector-Registry-System/`:
- **`1-registry-directory-manager.py`**: Approves or unapproves directories for scanning, lists candidate files, and reports status on approved directories (total vs. `v_` prefixed files).
- **`2-registry-document-scanner.py`**: Marks individual files with a `v_` prefix (and adds minimal registry entry), and scans approved directories for `v_*.md` files to fully populate or update their metadata in the `document_registry` table.
- **`3-registry-update-manager.py`**: Manages the `needs_update` flag in the registry to signal that a document requires re-vectorization.
- **`4-registry-archive-manager.py`**: Identifies and manages documents listed in the registry that are no longer found on the filesystem, allowing them to be marked as 'archived'.

**Typical Workflow Snippets:**

To approve a directory for scanning:
```bash
python Docs/Docs_19_File-2-Vector-Registry-System/1-registry-directory-manager.py --approve /path/to/your/docs_subdir
```

To scan approved directories and update the `document_registry` table:
```bash
python Docs/Docs_19_File-2-Vector-Registry-System/2-registry-document-scanner.py --scan
```

To see which documents are marked for update:
```bash
python Docs/Docs_19_File-2-Vector-Registry-System/3-registry-update-manager.py --list-updates
```

To list files in the registry that are missing from the filesystem:
```bash
python Docs/Docs_19_File-2-Vector-Registry-System/4-registry-archive-manager.py --list-missing
```

Consult `Docs/Docs_19_File-2-Vector-Registry-System/0-registry_librarian_persona.md` for detailed workflows and command options for these scripts.

## Test Questions

The following questions can be used to test understanding of the vector database system:

1. **MCP Query Test**: "How do I query the vector database to find documents related to transaction management?"
   - Expected: 
     1. Generate an embedding for 'transaction management' client-side (e.g., using OpenAI API).
     2. Use `mcp4_execute_sql` with project ID `ddfldwzhdhhzhxywqnyz` and an SQL query performing a vector similarity search against `public.project_docs` using the generated embedding. For example: `SELECT title, 1 - (embedding <=> '[CLIENT_GENERATED_EMBEDDING]'::vector) AS similarity FROM public.project_docs ORDER BY similarity DESC LIMIT 5;` (replacing `[CLIENT_GENERATED_EMBEDDING]` with the actual vector string).

2. **Registry Check**: "How can I determine which documents are intended for vectorization, their current processing status (e.g., pending, completed, needs update, archived), and compare this with what's actually present in the `project_docs` vector database?"
   - Expected: Query the `document_registry` table (checking fields like `title`, `file_path`, `embedding_status` (e.g., 'queue', 'active', 'archived', 'orphan'), `needs_update`). Compare its contents with queries against the `project_docs` table. Utilize scripts like `1-registry-directory-manager.py --status` for directory-level insights and review outputs from `2-registry-document-scanner.py --scan` and `4-registry-archive-manager.py --list-missing` or `--list-archived`.

3. **Registry Update**: "After new `v_` prefixed documents are added to approved directories on the filesystem, or existing ones are modified, what is the primary script to run to ensure these changes are reflected in the `document_registry` table with full metadata?"
   - Expected: Run `python Docs/Docs_19_File-2-Vector-Registry-System/2-registry-document-scanner.py --scan`. This processes `v_` files in active, approved directories and updates their entries in the `document_registry` table. Subsequently, `insert_architectural_docs.py` processes items from the registry queue into the vector DB.

4. **Project ID Verification**: "What is the correct project ID to use when querying the vector database through the MCP server?"
   - Expected: `ddfldwzhdhhzhxywqnyz`

5. **Document Count & Status**: "How can I get a count of documents in the `document_registry` table, and how can I ascertain the number of documents actually present in the `project_docs` (vector database) table?"
   - Expected: To count entries in the registry: `SELECT COUNT(*) FROM document_registry;`. To count entries in the vector database: `SELECT COUNT(*) FROM project_docs;`. The `document_registry` table's `embedding_status` field provides further detail on the vectorization status of registered documents.
