# Layer 1 Remediation Summary

This document provides a comprehensive summary of the technical debt identified and remediated within Layer 1 (Models & ENUMs) of the ScraperSky backend. The process involved a sequential audit of all model files, followed by immediate, evidence-based refactoring to align with the canonical architectural blueprints.

## Overarching Goal

The primary objective was to systematically eliminate architectural violations, enforce data model consistency, and establish a solid, compliant foundation for all subsequent application layers.

## Summary of Anti-Patterns Identified & Remediated

The audit revealed several recurring anti-patterns across the Layer 1 codebase. The following is a categorized list of these patterns and the corrective actions taken.

### 1. A-P 1: Improper Model Inheritance

*   **Description:** Models were found inheriting from both SQLAlchemy's declarative `Base` and our custom `BaseModel`. This resulted in redundant columns (`id`, `created_at`, `updated_at`), schema conflicts, and a violation of the "single source of truth" principle for base model definitions.
*   **Corrective Action:** All models were refactored to inherit *only* from `BaseModel`. This ensures every model correctly inherits the standardized UUID primary key and timestamp columns without conflict.
*   **Affected Files:** `contact.py`, `job.py`, `sitemap.py`, `profile.py`, `page.py`.

### 2. A-P 2: Decentralized and Inconsistent ENUMs

*   **Description:** ENUMs, particularly for status fields, were defined locally within the model files where they were used. This led to significant code duplication, conflicting status definitions across models, and non-standard naming conventions (e.g., `PascalCase` instead of `UPPER_SNAKE_CASE` for members).
*   **Corrective Action:** A single, authoritative `src/models/enums.py` file was established. All ENUMs were centralized into this file, standardized to inherit from `(str, Enum)`, and refactored to use consistent naming. All models were updated to import their ENUMs from this central source.
*   **Affected Files:** `api_models.py`, `batch_job.py`, `contact.py`, `domain.py`, `job.py`, `local_business.py`, `page.py`, `place_search.py`, `sitemap.py`.

### 3. A-P 3: Deficient Foreign Key and Relationship Integrity

*   **Description:** Foreign key implementation was a major source of inconsistency. Issues included missing `ForeignKey` constraints, keys pointing to non-primary-key columns, inconsistent naming (`user_id` vs. `created_by_id`), and a failure to universally enforce tenant isolation via a `tenant_id` foreign key.
*   **Corrective Action:** All foreign key columns were standardized to use the `_id` suffix. `ForeignKey` constraints were added or corrected to point to the `id` primary key of the parent table. Tenant isolation is now enforced on all relevant models with a non-nullable `tenant_id` that defaults to a standard value and references `tenants.id`.
*   **Affected Files:** `batch_job.py`, `contact.py`, `domain.py`, `job.py`, `local_business.py`, `page.py`, `profile.py`, `place_search.py`, `sitemap.py`.

### 4. A-P 4: Non-Standard Naming Conventions

*   **Description:** Violations of naming conventions were found in table names and database ENUM type names. For example, `__tablename__` was set to `places_staging` instead of `places`, and the `name` parameter for `SQLAlchemyEnum` used `PascalCase` instead of the required `snake_case`.
*   **Corrective Action:** All table names were corrected to be plural and `snake_case`. All database-level ENUM type names were refactored to `snake_case` to ensure consistency and prevent potential mapping issues.
*   **Affected Files:** `place.py`, `domain.py`, `contact.py`, `sitemap.py`.

### 5. A-P 5: Redundant Primary Key Definitions

*   **Description:** Several models explicitly defined an `id` primary key column, despite `BaseModel` already providing a standardized UUID primary key.
*   **Corrective Action:** All redundant `id` column definitions were removed from the models.
*   **Affected Files:** `contact.py`, `page.py`.

## Conclusion

The successful remediation of these anti-patterns has significantly improved the structural integrity and maintainability of Layer 1. The codebase is now simpler, more consistent, and strictly aligned with its architectural design. This provides a stable foundation for the subsequent verification and refactoring of higher application layers.
