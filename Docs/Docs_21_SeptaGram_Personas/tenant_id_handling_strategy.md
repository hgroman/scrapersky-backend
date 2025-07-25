# ScraperSky Tenant ID Handling Strategy

**Date:** 2025-07-01
**Version:** 1.0
**Author:** Cline (AI Assistant)

## 1. Purpose

This document consolidates the authoritative strategy for handling `tenant_id` within the ScraperSky backend. It clarifies the architectural shift from explicit application-layer tenant filtering to a more centralized and robust approach, primarily leveraging Supabase's Row Level Security (RLS). This is critical knowledge for all developers and AI partners working on the codebase.

## 2. The Core Architectural Shift: From Application-Filtered to Database-Enforced

Historically, multi-tenancy might have involved explicit `tenant_id` checks in every application query. ScraperSky has moved away from this anti-pattern to simplify application logic and enhance security.

### 2.1. Key Principles

*   **Application-Layer Simplification:** Services and routers should **NOT** contain explicit `tenant_id` filtering logic in their database queries (e.g., `WHERE tenant_id = ...`).
*   **Centralized Model Handling:** The `tenant_id` column is still present in relevant database tables and is managed by the `BaseModel` for all SQLAlchemy ORM models.
*   **Database-Enforced Isolation (RLS):** Tenant isolation is primarily enforced at the database level using Supabase's Row Level Security (RLS). This means the database itself ensures that a user can only access data belonging to their `tenant_id`.
*   **JWT as Context Source:** The `tenant_id` is extracted from the authenticated user's JSON Web Token (JWT) at the API gateway/router level.

### 2.2. How `tenant_id` is Handled in Practice

1.  **Authentication Layer (API Gateway/Routers):**
    *   The `tenant_id` is retrieved from the authenticated user's JWT token (e.g., `current_user.get("tenant_id")`).
    *   This `tenant_id` is then available in the `current_user` dictionary for use in creating new records.

2.  **Model Layer (`BaseModel`):**
    *   All SQLAlchemy models that require `tenant_id` (i.e., most data-bearing entities) inherit from `BaseModel`.
    *   `BaseModel` defines the `tenant_id` column as a `PGUUID` with a `ForeignKey("tenants.id")`, ensuring referential integrity.
    *   When a new record is created via the ORM, the `tenant_id` from the `current_user` context is passed to the model's constructor (e.g., `PlaceSearch(tenant_id=user_info.get("tenant_id"), ...) `).

3.  **Service Layer:**
    *   Service methods **MUST NOT** accept `tenant_id` as a parameter for filtering.
    *   Service methods **MUST NOT** include `tenant_id` in their `WHERE` clauses for data retrieval or updates.
    *   Any hardcoded `DEFAULT_TENANT_ID` values in service logic should be removed, as `tenant_id` is either provided by `BaseModel` on creation or handled by RLS.

4.  **Database Layer (Supabase RLS):**
    *   Supabase's Row Level Security (RLS) policies are configured on tables to automatically filter rows based on the `tenant_id` associated with the authenticated database user or session. This is the primary enforcement mechanism for multi-tenancy.

## 3. Why This Strategy?

*   **Security:** RLS provides a robust, database-enforced security layer, preventing accidental data leakage across tenants.
*   **Simplicity:** Removes repetitive `tenant_id` filtering logic from hundreds of application queries, making the codebase cleaner and less error-prone.
*   **Maintainability:** Changes to multi-tenancy rules can often be managed at the database level (RLS policies) rather than requiring application code deployments.

## 4. Finding More Information (Semantic Search)

This document provides a high-level overview. For deeper insights into specific implementations or related architectural decisions, use the `semantic_query_cli.py` tool.

**How to use semantic query:**
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "Your natural language question here"
```

**Example Search Terms:**
*   `"Supabase Row Level Security"`
*   `"tenant isolation removal strategy"`
*   `"BaseModel tenant_id foreign key"`
*   `"application layer tenant filtering"`
*   `"JWT authentication tenant_id"`

By leveraging semantic search, you can quickly find relevant audit reports, architectural blueprints, and Q&A documents that discuss these concepts in detail. This empowers you to internalize and synthesize the information yourself, fostering a deeper understanding of the project's design.
