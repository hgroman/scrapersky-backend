# Vector Registry System - Design Specification

## 1. Overview

This document outlines the design and architecture of the ScraperSky Vector Registry System. This system is responsible for tracking documents, managing their ingestion into a vector database, handling their lifecycle (including archival), and ensuring data integrity between the document registry and the vector store.

## 2. System Architecture

*   [Placeholder for a high-level diagram showing scripts, database tables, and data flow.]

## 3. Data Model

### 3.1. `document_registry` Table

*   **Purpose:** Acts as the source of truth for all documents known to the system, their metadata, and their processing status.
*   **Key Fields:**
    *   `id` (INTEGER, Primary Key): Unique identifier for the document record.
    *   `file_path` (TEXT): Absolute path to the source document file.
    *   `title` (TEXT): Document title, often derived from the filename.
    *   `status` (TEXT): Overall status (e.g., 'pending', 'processed', 'error', 'archived_fs', 'archived_user').
    *   `embedding_status` (TEXT): Status related to vector embedding (e.g., 'pending', 'embedded', 'archived', 'error').
    *   `created_at` (TIMESTAMP): Timestamp of record creation.
    *   `updated_at` (TIMESTAMP): Timestamp of last record update.
    *   `last_processed_at` (TIMESTAMP): Timestamp of last processing attempt.
    *   `checksum` (TEXT): MD5 checksum of the file content.
    *   `metadata_json` (JSONB): Additional metadata.

### 3.2. `project_docs` Table (Vector Table)

*   **Purpose:** Stores the vector embeddings and associated content chunks for documents.
*   **Key Fields (Conceptual - actual may vary by vector DB provider):
    *   `id` (INTEGER): Foreign key, ideally referencing `document_registry.id`.
    *   `title` (TEXT): Document title.
    *   `content` (TEXT): Text chunk.
    *   `embedding` (VECTOR): The vector embedding for the content chunk.
    *   `metadata` (JSONB): Metadata associated with the chunk/document.
    *   `updated_at` (TIMESTAMP): Timestamp of last update.

## 4. Script Responsibilities & Logic

### 4.1. `1-registry-init.py`
*   **Responsibility:** Initializes the `document_registry` table if it doesn't exist.
*   **Logic:** Executes DDL SQL to create the table schema.

### 4.2. `2-registry-document-scanner.py`
*   **Responsibility:** Scans specified directories for new/modified documents (matching `v_*.md` pattern) and adds/updates their records in the `document_registry`.
*   **Logic:** Compares filesystem state with registry, calculates checksums, updates `status` and `embedding_status` to 'pending' for new/changed files.

### 4.3. `3-registry-embedding-manager.py`
*   **Responsibility:** Processes documents marked 'pending' in `document_registry`, generates embeddings, and stores them in `project_docs`. Updates `embedding_status` to 'embedded'.
*   **Logic:** Fetches pending documents, calls embedding API, inserts into vector table.

### 4.4. `4-registry-archive-manager.py`
*   **Responsibility:** Identifies documents in the registry that are no longer present on the filesystem or are manually marked for archival. Updates their `embedding_status` to 'archived'.
*   **Logic:** Compares registry file paths with filesystem; provides commands to mark for archival.

### 4.5. `5-vector-db-cleanup-manager.py`
*   **Responsibility:** Removes entries from `project_docs` for documents that are marked with `embedding_status = 'archived'` in the `document_registry`.
*   **Logic:** Joins `document_registry` and `project_docs` on `id`, finds 'archived' items, and deletes corresponding rows from `project_docs`.

### 4.6. `6-registry-orphan-detector.py` (Proposed)
*   **Responsibility:** Identifies entries in `project_docs` that do not have a corresponding valid entry in `document_registry` (orphans).
*   **Logic:** Uses a `LEFT JOIN` from `project_docs` to `document_registry` on `id`, filters for `document_registry.id IS NULL`.

### 4.7. `7-registry-orphan-purger.py` (Proposed)
*   **Responsibility:** Removes orphaned entries from `project_docs` after user confirmation.
*   **Logic:** Fetches orphans (similar to script 6), then deletes from `project_docs` with confirmation.

## 5. Workflow Definitions

### 5.1. New Document Ingestion
1.  `2-registry-document-scanner.py --scan`: Adds new `v_*.md` files to `document_registry` with `embedding_status='pending'`.
2.  `3-registry-embedding-manager.py --process`: Generates embeddings for 'pending' documents and updates status to 'embedded'.

### 5.2. Document Archival & Cleanup
1.  File is deleted from filesystem / User decides to archive.
2.  `4-registry-archive-manager.py --scan` (or `--mark-archived --id <ID>`): Updates `embedding_status` to 'archived' in `document_registry`.
3.  `5-vector-db-cleanup-manager.py --cleanup`: Removes corresponding entries from `project_docs`.

### 5.3. Orphan Cleanup (Proposed)
1.  `6-registry-orphan-detector.py`: Lists orphaned entries in `project_docs`.
2.  `7-registry-orphan-purger.py [--auto-approve]`: Removes listed orphans from `project_docs`.

## 6. Key Design Principles

*   **Separation of Concerns:** Each script has a distinct, well-defined responsibility.
*   **Idempotency:** Scripts should be runnable multiple times without adverse effects where possible.
*   **Stable Identifiers:** Use `id` columns for reliable linking between tables.
*   **User Confirmation:** Destructive operations require user confirmation unless explicitly bypassed.
*   **Configuration Management:** Use environment variables for sensitive data (e.g., `DATABASE_URL`).
*   **Logging:** Comprehensive logging for traceability and debugging.
