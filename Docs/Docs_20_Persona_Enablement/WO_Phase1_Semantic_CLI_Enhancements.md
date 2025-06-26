# Work Order: Semantic CLI Enhancements (Phase 1)

**Document Purpose:** This work order details the plan, technical specifications, and success criteria for the initial phase of enhancements to the `semantic_query_cli.py` tool. The goal is to provide a clear, standalone guide that another engineer or AI could use to understand and execute the required changes.

---

## 1. Executive Summary & Purpose

**The Why:** The overarching goal is to enable the development of specialized AI Personas, each an expert on a specific layer of the ScraperSky architecture. These personas will be instrumental in proactively identifying and managing technical debt. To be effective, they require a tool that allows them to query the project's vectorized knowledge base with precision.

**The What:** This work order focuses on the most critical, high-impact enhancements to the existing `semantic_query_cli.py` tool. We will introduce two key capabilities:

1.  **Metadata Filtering:** Allow queries to be filtered by metadata fields (e.g., `layer`, `tags`, `document_source`). This is the core requirement for personas to focus their analysis on their specific domain.
2.  **Structured Output:** Provide a machine-readable output format (JSON) so the results can be programmatically consumed by personas or other automated tooling.

**The Strategy:** We are deliberately phasing this rollout to avoid scope creep and deliver immediate value. This work order covers **Phase 1 only**, which modifies the existing RPC-based infrastructure. A future phase will refactor the implementation to use the more abstract `supabase-py vecs` library for improved maintainability.

---

## 2. Technical Implementation Plan

This phase involves two primary changes: modifying the backend SQL function and updating the frontend Python CLI script.

### Step 2.1: Enhance the PostgreSQL Function

The existing `perform_semantic_search_direct` function will be replaced with a new version that accepts an optional `jsonb` parameter for filtering.

**Action:** Execute the following SQL command using a database client or the `mcp4_execute_sql` tool.

```sql
CREATE OR REPLACE FUNCTION perform_semantic_search_direct(
    query_embedding_param halfvec(1536),
    match_threshold_param double precision,
    match_count_param integer,
    metadata_filter_param jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (id INTEGER, title TEXT, content TEXT, similarity REAL)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pd.id,
        pd.title,
        pd.content,
        CAST(1 - (pd.embedding <=> query_embedding_param) AS REAL) AS similarity
    FROM
        project_docs AS pd
    WHERE
        (metadata @> metadata_filter_param OR jsonb_typeof(metadata_filter_param) = 'null' OR metadata_filter_param = '{}'::jsonb)
    AND 
        1 - (pd.embedding <=> query_embedding_param) > match_threshold_param
    ORDER BY
        pd.embedding <=> query_embedding_param
    LIMIT 
        match_count_param;
END;
$$;
```

**Key Changes in the SQL:**
*   **`metadata_filter_param jsonb`:** A new, optional parameter to accept a JSON object for filtering.
*   **`DEFAULT '{}'::jsonb`:** Ensures the function remains backward compatible; if no filter is provided, it defaults to an empty JSON object, matching all records.
*   **`WHERE (metadata @> metadata_filter_param ...)`:** This is the core filtering logic. It uses the JSONB `contains` operator (`@>`) to find documents whose `metadata` field contains the key-value pairs specified in the filter.

### Step 2.2: Upgrade `semantic_query_cli.py`

The Python script needs to be updated to support the new command-line arguments and pass them to the enhanced SQL function.

**File to Modify:** `Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py`

**Action:** Modify the script to include:

1.  **Argument Parsing:** Use `argparse` to add two new optional arguments:
    *   `--filter`: A string that will be parsed as a JSON object.
    *   `--format`: A string that accepts `text` (default) or `json`.

2.  **Function Call Logic:**
    *   Update the `supabase.rpc()` call to pass the `metadata_filter` parameter to the SQL function.
    *   If the `--filter` argument is provided, parse the string into a Python dictionary.
    *   If not provided, pass an empty dictionary.

3.  **Output Formatting:**
    *   If `--format json` is specified, print the list of result dictionaries directly to `stdout` using `json.dumps()`.
    *   Otherwise, retain the existing human-readable text output.

---

## 3. Definition of Success

This work is considered complete when the following command-line executions run successfully and produce the expected output.

**1. Standard Query (Backward Compatibility):**
*   **Command:** `python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "What is the purpose of the document registry?"`
*   **Expected Result:** The script returns human-readable text results, functionally identical to the current implementation.

**2. Filtered Query:**
*   **Command:** `python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "What are the rules for database connections?" --filter '{"source_document": "v_db_connectivity_async_4_vector_ops.md"}'`
*   **Expected Result:** The script returns results *only* from the specified source document.

**3. Structured Output Query:**
*   **Command:** `python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "What is the purpose of the document registry?" --format json`
*   **Expected Result:** The script prints a well-formed JSON array of result objects to standard output.

**4. Filtered, Structured Query:**
*   **Command:** `python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "What are the rules for database connections?" --filter '{"source_document": "v_db_connectivity_async_4_vector_ops.md"}' --format json`
*   **Expected Result:** The script prints a JSON array containing results *only* from the specified source document.

---

## 4. Future Phases (Out of Scope for this Work Order)

*   **Phase 2:** Refactor the CLI to use the `supabase-py vecs` library, deprecating the custom SQL function.
*   **Phase 3:** Implement further quality-of-life improvements, such as batch querying and simplified filter flags (e.g., `--layer services`).
