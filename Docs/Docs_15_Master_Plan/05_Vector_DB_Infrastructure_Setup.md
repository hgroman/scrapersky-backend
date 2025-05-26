# 05: Vector DB Infrastructure Setup

## Component Overview

This component defines the necessary steps and configurations to set up the PostgreSQL database that will serve as the Vector DB Knowledge System, including enabling the vector extension and creating the required tables.

## Purpose

To provide a clear and repeatable process for establishing the foundational database infrastructure required to store and manage the AI agents' knowledge base.

## Key Considerations

*   **Database System:** Utilizing PostgreSQL as the chosen database system.
*   **Vector Extension:** Ensuring the `vector` extension is enabled to support vector data types and operations.
*   **Table Schema:** Defining the schema for the `fix_patterns` table (and potentially other tables for Architect/system memory) with appropriate columns and data types, including the `vector` type for embeddings.
*   **Connection Details:** Documenting the necessary connection parameters (URL, credentials, SSL requirements).
*   **Scalability and Performance:** Considering database configuration for future growth and query performance.
*   **Backup and Recovery:** High-level consideration for database backup and recovery strategies.

## Setup Steps

1.  **Provision PostgreSQL Database:** Ensure a PostgreSQL database instance is available and accessible.
2.  **Connect to Database:** Establish a connection to the database using appropriate tools (e.g., `psql`, database management tools, or scripts).
3.  **Enable Vector Extension:** Execute the SQL command to enable the `vector` extension:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```
4.  **Create `fix_patterns` Table:** Execute the SQL commands to create the `fix_patterns` table with the defined schema. The schema should include columns for:
    *   `id` (UUID, Primary Key)
    *   `title` (TEXT)
    *   `problem_type` (TEXT)
    *   `code_type` (TEXT)
    *   `severity` (TEXT)
    *   `tags` (TEXT[])
    *   `layers` (INTEGER[])
    *   `workflows` (TEXT[])
    *   `file_types` (TEXT[])
    *   `problem_description` (TEXT)
    *   `solution_steps` (TEXT)
    *   `code_before` (TEXT) - *Note: May contain placeholders or be omitted if code is stored in DART.*
    *   `code_after` (TEXT) - *Note: May contain placeholders or be omitted if code is stored in DART.*
    *   `verification_steps` (TEXT)
    *   `learnings` (TEXT)
    *   `prevention_guidance` (TEXT)
    *   `dart_task_ids` (TEXT[])
    *   `dart_document_urls` (TEXT[])
    *   `applied_count` (INTEGER, default 0)
    *   `success_rate` (NUMERIC, default 1.0)
    *   `confidence_score` (NUMERIC, default 0.8 or 0.9)
    *   `content_embedding` (VECTOR(1536))
    *   `code_embedding` (VECTOR(1536))
    *   `problem_embedding` (VECTOR(1536))
    *   `pattern_vector` (VECTOR(1536))
    *   `created_by` (TEXT)
    *   `reviewed` (BOOLEAN, default false)
    *   `description` (TEXT)
    *   `created_at` (TIMESTAMP with time zone, default NOW())
    *   `updated_at` (TIMESTAMP with time zone, default NOW())
    *   `reviewer_notes` (TEXT)
    *   `related_files` (TEXT[])
    *   `source_file_audit_id` (INTEGER)
    *   `applied_to_files` (INTEGER[])
    *   `avg_time_saved` (INTEGER, default 0)
    *   `knowledge_type` (TEXT) - To distinguish 'pattern' from 'exemplar'.
5.  **Configure Connection:** Document the `DATABASE_URL` format and any necessary SSL or pooling configurations (e.g., for Supavisor).

## Required Outputs

*   Clear documentation outlining the steps to set up the Vector DB infrastructure.
*   The SQL schema for the `fix_patterns` table.

## Dependencies

*   Access to a PostgreSQL database instance.
*   Database credentials and connection details.

## Responsible Role

*   **Architect Persona (Roo):** Defines the database schema and documents the setup process.

## Notes

Setting up the database is a foundational, typically one-time task. Ensuring the schema is correct and includes all necessary fields for pattern data and embeddings is critical for the functionality of the Vector DB Knowledge System. We should also consider creating a separate table for Architect/system-level memory and strategic insights in the future.