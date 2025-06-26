# ScraperSky: Semantic Search Development Guidelines & Best Practices

**Version:** 1.0
**Date:** 2025-06-19
**Status:** Active

## 1. Purpose

This document outlines the critical development guidelines, architectural principles, approved patterns, and known anti-patterns for working with the ScraperSky semantic search system. Adherence to these guidelines is mandatory to prevent regression, ensure system stability, and build upon the robust foundation established.

This system was developed through an arduous process. These guidelines capture the hard-won lessons to ensure that effort is not wasted and that future development is efficient and correct.

## 2. Core Architectural Principles

1.  **Separation of Concerns:**
    *   **Embedding Generation & Storage:** Handled by a dedicated Python pipeline (primarily `Docs/Docs_18_Vector_Operations/Scripts/insert_architectural_docs.py`). This process reads document content, calls the OpenAI API for embeddings, and writes the content and vector to `public.project_docs` using `asyncpg`.
    *   **Semantic Search (Querying):** Handled by a dedicated Python CLI tool (`Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py`). This tool manages query embedding generation and executes searches via RPC calls to a PostgreSQL function.

2.  **Native Data Handling via RPC:** For complex data types like vectors, direct RPC calls to database functions (e.g., using `supabase-py`) are the approved method. This avoids data corruption and interpretation issues inherent in less direct methods.

3.  **Database as the Source of Truth for Content:** Semantic search should retrieve and allow reasoning over the *content* stored within the `project_docs` table, not merely use the database as an index to find local file paths.

## 3. Critical Anti-Patterns (THE "DON'TS")

These practices have been proven to cause significant issues and MUST be avoided:

1.  **DO NOT Pass Vectors as String Literals via `mcp4_execute_sql` for Search:**
    *   **Reason:** This is a major architectural anti-pattern. Large floating-point vectors are susceptible to truncation, misinterpretation, and character encoding issues when passed as raw strings in SQL queries. This was the root cause of persistent `dimension mismatch` errors (e.g., `expected 1536 dimensions, got 287`).
    *   **Impact:** Unreliable search, incorrect results, significant debugging time.

2.  **DO NOT Assume Database Schema Details (Especially Column Types):**
    *   **Reason:** Incorrect assumptions about data types (e.g., `id` column being `uuid` or `bigint` when it was `integer`) lead to `SQLSTATE: 42804` (type mismatch) errors in SQL function definitions and calls.
    *   **Corrective Action:** Always verify schema details directly (e.g., using `information_schema` or `\d table_name` in `psql`) before writing or modifying SQL functions or queries.

3.  **DO NOT Create New Database Functions Without Thoroughly Checking for Existing Ones:**
    *   **Reason:** Duplicating function names, even with different signatures if not handled carefully, can lead to function overloading ambiguity (`PGRST203` errors or unexpected behavior).
    *   **Corrective Action:** Always check for existing functions that might serve the purpose or could be modified. If creating a new version, ensure the old one is properly deprecated or dropped if it's being replaced.

4.  **DO NOT Use Semantic Search Merely to Find Local File Paths for AI to Read:**
    *   **Reason:** This underutilizes the vector database and defeats the purpose of storing rich content. The AI should reason over the content retrieved *directly from the database* via the semantic search function itself.
    *   **Impact:** Inefficient workflow, missed opportunity for deeper understanding by the AI.

## 4. Approved Good Patterns (THE "DO'S")

1.  **ALWAYS Use `semantic_query_cli.py` for All Semantic Search Operations:**
    *   **Location:** `Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py`
    *   **Reason:** This script encapsulates the correct end-to-end process: query embedding generation (via OpenAI API), connection to Supabase (via `supabase-py`), and RPC call to the `perform_semantic_search_direct` PostgreSQL function, passing the vector natively.
    *   **Benefits:** Robust, reliable, avoids data transport issues, supports parameterized queries (`--mode`, `--limit`, `--threshold`) for flexible, multi-step reasoning.

2.  **ALWAYS Use Appropriate Client Libraries (e.g., `supabase-py`) for Programmatic Database Interaction Involving Complex Data or RPC:**
    *   **Reason:** These libraries handle connection management, data type conversion, and RPC invocation correctly.

3.  **DESIGN Database Functions to Accept Native Vector Types:**
    *   **Example:** `perform_semantic_search_direct(query_embedding_param halfvec(1536), ...)`
    *   **Reason:** This allows the database to work with vectors in its optimized internal format.

4.  **ENSURE SQL Function Return Types Precisely Match Expected Client-Side Types:**
    *   **Reason:** Mismatches (e.g., SQL function returning `double precision` when Python expects `float` or `REAL` for similarity scores) can cause errors or data misinterpretation.
    *   **Corrective Action:** Use explicit casting in SQL if necessary (e.g., `(1 - (embedding <=> query_embedding_param))::REAL AS similarity`).

5.  **MAINTAIN Clear, Accurate, and Up-to-Date Documentation:**
    *   **Reason:** As this project has shown, clear documentation is vital for preventing errors, onboarding new developers (or AI), and preserving institutional knowledge.

## 5. Key Lessons Learned from the Journey

*   **Data Transport is Critical:** How data (especially large, complex data like vectors) is passed between systems (Python script to database) is as important as the operations performed on that data. String-based transport for vectors is fragile and error-prone.
*   **Verification Over Assumption:** Never assume schema details or system behavior. Always verify through direct inspection or testing.
*   **Incremental Testing:** Test each component of a pipeline (embedding generation, database connection, SQL function logic, client-side script) incrementally to isolate issues faster.
*   **Understand the True Objective:** Ensure that technical implementations align with the strategic goals. A working component that doesn't solve the right problem is still a failure.
*   **Precision in SQL:** SQL is a strongly-typed language. Pay close attention to data types in table definitions, function signatures, and query casts.

By adhering to these guidelines, we can build upon the current semantic search system with confidence and avoid repeating past mistakes.
