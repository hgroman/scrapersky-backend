# LAYER5: Vector Database & Registry - Authoritative Pointers

**Status:** Active (Pointer Document)
**Version:** 2.0
**Last Updated:** 2025-06-09

## Purpose

This document serves as a high-level pointer to the authoritative sources of information for the ScraperSky Vector Database and Document Registry systems. It ensures all team members and AI partners use a consistent and correct set of documentation and tools.

**This document itself is not the source of truth; it directs you to it.**

---

## Master Index & Primary Entry Point

For a comprehensive, curated, and up-to-date list of all key documents, scripts, and operational guides, refer to the **master index**:

*   **Master Index:** [`Docs/Docs_18_Vector_Operations/v_key_documents.md`](./../../Docs_18_Vector_Operations/v_key_documents.md)

For a deep technical understanding of the end-to-end process, the primary developer guide is:

*   **Primary Dev Guide:** [`Docs/Docs_19_File-2-Vector-Registry-System/v_vector_ingestion_pipeline_dev_guide.md`](./../../Docs_19_File-2-Vector-Registry-System/v_vector_ingestion_pipeline_dev_guide.md)


## Core Process Overview

The system follows a strict, two-part process to ensure data integrity:

1.  **Document Registry (`document_registry` table):**
    *   A file is first registered in the `document_registry` table using the script suite in `Docs/Docs_19_File-2-Vector-Registry-System/`.
    *   This registry acts as the single source of truth for document status (e.g., `active`, `queued_for_embedding`, `archived`).
    *   Only files prefixed with `v_` are scanned for inclusion.

2.  **Vector Database (`project_docs` table):**
    *   The `insert_architectural_docs.py` script processes documents marked as `queued_for_embedding` in the registry.
    *   It generates vector embeddings for the content and inserts them into the `project_docs` table for semantic search.
    *   Cleanup scripts remove vectors for documents marked `archived`.

---

## Key Constants

*   **Supabase Project ID:** `ddfldwzhdhhzhxywqnyz`
*   **MCP Function for SQL:** `mcp4_execute_sql`
