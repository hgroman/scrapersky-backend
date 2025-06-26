# Developer Guide: ScraperSky Document Vectorization & Registry Pipeline

**Version:** 1.0
**Last Updated:** {{YYYY-MM-DD}} <!-- I will insert today's date -->

## 1. Introduction & Purpose

This guide provides a comprehensive technical overview of the ScraperSky document ingestion, vectorization, and registry management pipeline. It is intended for developers involved in maintaining, extending, or troubleshooting this system. The focus is on the architectural design, the interaction between components, and the core principles that ensure its robustness, maintainability, and adaptability. This document aims to be a truthful and concise reference, avoiding unnecessary bloat while capturing the critical considerations embedded in its design.


**Important Note on Querying:** While this document details the *ingestion and vectorization* pipeline, the *querying* of these vectors for semantic search has its own set of critical development guidelines and anti-patterns. Please refer to:
*   **Semantic Search Development Guidelines:** [`../Docs_18_Vector_Operations/Documentation/v_semantic_search_dev_guidelines.md`](../Docs_18_Vector_Operations/Documentation/v_semantic_search_dev_guidelines.md)

Understanding both ingestion and querying best practices is essential for working with the full vector database system.

## 2. Core Architectural Principles

The pipeline is built upon several key principles:

*   **Separation of Concerns:** Each script in the pipeline has a distinct and well-defined responsibility. This modularity allows for easier understanding, testing, and modification of individual components without unintended side effects on others. For example, scanning for documents is separate from vectorizing them, which is separate from cleaning up orphaned data.
*   **Status-Driven Workflow:** The `document_registry.embedding_status` field (along with `needs_update`) acts as the central state machine for documents. Scripts query this status to determine which documents to process, and update it to reflect the outcome of their operations. This provides a clear, auditable trail and facilitates robust error handling and reprocessing.
*   **Data Integrity:**
    *   **Stable Identifiers:** The system relies on the stable `id` column in `document_registry` as the primary key and foreign key for linking to `project_docs`. This avoids issues with mutable fields like titles.
    *   **Transactional Updates:** Where appropriate, database operations are designed to ensure consistency.
*   **Atomicity of Operations:** Scripts are designed to perform their specific tasks efficiently and reliably.
*   **Explicit User Control for Destructive Operations:** Operations like purging orphaned embeddings (`7-registry-orphan-purger.py`) require explicit user confirmation by default, preventing accidental data loss.
*   **Configuration via Database:** The `approved_scan_directories` table allows for dynamic configuration of which content areas are actively processed.

## 3. Key Components

The pipeline consists of database tables and a suite of Python scripts.

### 3.1. Database Tables

*   **`public.document_registry`**:
    *   **Role:** The central nervous system of the pipeline. It tracks every document intended for, or processed by, the vectorization system.
    *   **Key Fields:**
        *   `id` (SERIAL PRIMARY KEY): Unique identifier for the registry entry. Used as the primary key in `project_docs`.
        *   `file_path` (TEXT): Absolute path to the source document file.
        *   `title` (TEXT): Extracted title of the document.
        *   `document_type` (TEXT): Type of document (e.g., 'markdown', 'python_script').
        *   `architectural_layer` (TEXT): Categorization within the project architecture.
        *   `embedding_status` (TEXT): Current state in the vectorization lifecycle (e.g., `queue`, `active`, `archived`, `error_processing`).
        *   `needs_update` (BOOLEAN): Flag indicating if an existing `active` document needs re-vectorization.
        *   `last_scanned_at` (TIMESTAMP): When the file was last processed by the scanner.
        *   `last_embedded_at` (TIMESTAMP): When the document was last successfully vectorized.
        *   `error_message` (TEXT): Stores details if `embedding_status` is `error_processing`.
*   **`public.project_docs`**:
    *   **Role:** The vector database table. Stores the actual content embeddings.
    *   **Key Fields:**
        *   `id` (INTEGER PRIMARY KEY): Foreign key referencing `document_registry.id`.
        *   `title` (TEXT): Document title (mirrored for convenience).
        *   `content` (TEXT): The raw text content that was embedded.
        *   `embedding` (vector): The numerical vector representation of the content.
*   **`public.approved_scan_directories`**:
    *   **Role:** Manages which base directories are actively scanned for documents.
    *   **Key Fields:** `id`, `directory_path`, `active` (BOOLEAN).

### 3.2. Core Scripts

Scripts are organized by their primary function within the pipeline.

*   **Vectorization Engine:**
    *   `Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py`:
        *   **Responsibility:** The core engine that processes documents flagged for vectorization.
        *   **Operation:** Queries `document_registry` for items with `embedding_status = 'queue'` or `needs_update = TRUE`. For each, it fetches content, generates an OpenAI embedding, and inserts/updates the record in `project_docs` (using `document_registry.id` as the key). Updates `embedding_status` to `active` or `error_processing` in `document_registry`.

*   **Document Registry Management Suite (`Docs/Docs_19_File-2-Vector-Registry-System/`):**
    1.  `1-registry-directory-manager.py`:
        *   **Responsibility:** Manages the `approved_scan_directories` table.
        *   **Operations:** Approving new directories for scanning, deactivating existing ones, listing approved/candidate directories, and providing status counts.
    2.  `2-registry-document-scanner.py`:
        *   **Responsibility:** Scans filesystem for documents, creates/updates entries in `document_registry`.
        *   **Operations:**
            *   `--mark`: Manually flags a single file (renames to `v_filename.md`) and creates a minimal registry entry.
            *   `--scan`: Processes `v_*.md` files in active approved directories, extracts metadata, and updates/creates full `document_registry` entries, setting `embedding_status` to `queue` for new/updated items.
    3.  `3-registry-update-flag-manager.py`:
        *   **Responsibility:** Manages the `needs_update` flag for re-vectorization.
        *   **Operations:** Marks specific documents, or all documents in a directory/matching a pattern, by setting `needs_update = TRUE` in `document_registry`.
    4.  `4-registry-archive-manager.py`:
        *   **Responsibility:** Handles documents that are no longer found on the filesystem.
        *   **Operations:** Scans `document_registry` for `active` or `queue` entries whose `file_path` no longer exists. Sets their `embedding_status` to `archived`.
    5.  `5-vector-db-cleanup-manager.py`:
        *   **Responsibility:** Removes vector embeddings for archived documents.
        *   **Operations:** Identifies entries in `document_registry` with `embedding_status = 'archived'`. For each, it deletes the corresponding record from `project_docs` using the `id`.
    6.  `6-registry-orphan-detector.py`:
        *   **Responsibility:** Identifies orphaned vector embeddings.
        *   **Operations:** Finds records in `project_docs` whose `id` does not exist in `document_registry`. Reports these orphans.
    7.  `7-registry-orphan-purger.py`:
        *   **Responsibility:** Deletes orphaned vector embeddings from `project_docs`.
        *   **Operations:** Uses the output of the orphan detector (or re-detects) and, after user confirmation (unless `--auto-approve`), deletes orphaned records from `project_docs`.

## 4. End-to-End Document Lifecycle

The following outlines the typical journey of a document through the pipeline:

1.  **Identification & Initial Marking:**
    *   A new document (e.g., `mydoc.md`) is created or identified in a relevant project directory.
    *   The directory (e.g., `/path/to/docs_subdir`) is approved using `1-registry-directory-manager.py --approve /path/to/docs_subdir`.
    *   The document can be individually marked using `2-registry-document-scanner.py --mark /path/to/docs_subdir/mydoc.md`. This renames it to `v_mydoc.md` and creates a basic registry entry.

2.  **Scanning & Registry Population:**
    *   `2-registry-document-scanner.py --scan` is run.
    *   The scanner processes `v_mydoc.md` (and other `v_` prefixed files in approved directories).
    *   It extracts metadata (title, type, layer) and updates the `document_registry` entry for `v_mydoc.md`, setting `embedding_status = 'queue'` and `needs_update = FALSE`.

3.  **Vectorization:**
    *   `insert_architectural_docs.py` is run.
    *   It finds `v_mydoc.md` in the registry (status `queue`).
    *   It reads the content of `v_mydoc.md`, generates an embedding via OpenAI.
    *   It inserts a new record into `project_docs` with the `id` from `document_registry`, title, content, and the new embedding.
    *   It updates the `document_registry` entry for `v_mydoc.md` to `embedding_status = 'active'` and sets `last_embedded_at`.

4.  **Document Update & Re-vectorization:**
    *   The content of `v_mydoc.md` is significantly changed.
    *   `3-registry-update-flag-manager.py --mark-for-update /path/to/docs_subdir/v_mydoc.md` is run. This sets `needs_update = TRUE` in `document_registry`.
    *   `insert_architectural_docs.py` is run again.
    *   It finds `v_mydoc.md` (status `active`, but `needs_update = TRUE`).
    *   It re-generates the embedding and *updates* the existing record in `project_docs` (based on `id`).
    *   It updates `last_embedded_at` in `document_registry` and sets `needs_update = FALSE`.

5.  **Document Archival:**
    *   The file `v_mydoc.md` is deleted from the filesystem.
    *   `4-registry-archive-manager.py` is run.
    *   It detects that `v_mydoc.md` is missing and updates its `embedding_status` in `document_registry` to `archived`.

6.  **Archived Embedding Cleanup:**
    *   `5-vector-db-cleanup-manager.py` is run.
    *   It finds `v_mydoc.md` with status `archived`.
    *   It deletes the corresponding record from `project_docs` using the `id`.

7.  **Orphan Detection & Purging (Periodic Maintenance):**
    *   `6-registry-orphan-detector.py` is run to identify any records in `project_docs` that don't have a valid parent in `document_registry` (e.g., due to manual DB operations or past inconsistencies).
    *   `7-registry-orphan-purger.py` is run to remove these detected orphans from `project_docs` after confirmation.

## 5. Database Connectivity & Environment

*   **Connectivity:**
    *   Most scripts in the `Docs/Docs_19_File-2-Vector-Registry-System/` suite and `insert_architectural_docs.py` use direct `asyncpg` connections to the PostgreSQL database. This allows for specific connection parameters (e.g., for PGBouncer compatibility if used), vector extension operations, and fine-grained transaction control.
    *   Manual operations or simple queries by an AI persona (like the Knowledge Librarian) typically use the `mcp4_execute_sql` tool, which abstracts some of these details.
*   **Environment Variables:**
    *   `DATABASE_URL`: Standard PostgreSQL connection string (e.g., `postgresql+asyncpg://user:pass@host:port/dbname`). Scripts are designed to handle the `postgresql+asyncpg://` prefix correctly.
    *   `OPENAI_API_KEY`: Required by `insert_architectural_docs.py` for generating embeddings.

## 6. Maintainability & Adaptability

The design of this pipeline prioritizes long-term maintainability:

*   **Modularity:** Changes to one script (e.g., improving metadata extraction in the scanner) are less likely to impact others (e.g., the vectorization engine), as long as the database schema and status contracts are respected.
*   **Checksum Verification:** Calculates a SHA256 hash of each file's content. If the hash has changed since the last scan, it flags the document for re-embedding, ensuring the vector database stays synchronized with the latest content.
*   **Recursive Scanning:** The script recursively scans all subdirectories within an approved directory using `os.walk()`. Approving a parent folder (e.g., `Docs/Docs_18_Vector_Operations/`) is sufficient to scan all `v_*.md` files within it and any of its sub-folders.
*   **Extensibility:**
    *   **New Document Types:** Supporting new file types would involve modifying `2-registry-document-scanner.py` to handle their parsing and potentially adding new `document_type` values. The core vectorization logic might remain unchanged if they produce text.
    *   **Metadata Expansion:** Adding new metadata fields would involve schema changes to `document_registry` and updates to `2-registry-document-scanner.py` to populate them.
    *   **Alternative Embedding Models:** `insert_architectural_docs.py` isolates the embedding generation logic. Swapping to a different model or provider would primarily impact this script.
*   **Testability:** Individual scripts can be tested more easily due to their focused nature.

This system, born from careful architectural planning and iterative refinement, provides a robust foundation for ScraperSky's knowledge base vectorization needs.