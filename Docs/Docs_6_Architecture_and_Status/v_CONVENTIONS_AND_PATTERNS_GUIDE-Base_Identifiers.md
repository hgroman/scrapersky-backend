# ScraperSky Naming & Structural Conventions Guide - Base Identifiers

**Date:** 2025-05-11
**Version:** 1.0

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy for architectural alignment
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis.md)** - Comprehensive analysis of layer classification
- **[Q&A_Key_Insights.md](./Q&A_Key_Insights.md)** - Clarifications on implementation standards

**Objective:** This document serves as the definitive guide for all naming and structural conventions within the ScraperSky backend project. It is synthesized from existing project documentation, code examples, and canonical workflow definitions. Adherence to these conventions is crucial for maintaining consistency, readability, and maintainability across the codebase.

---

## Core Principle

Consistency is paramount. Most names are derived from a `workflow_name` (snake_case) and/or a `source_table_name` (singular, snake_case). This guide explicitly details these derivations.

---

## 1. Base Identifiers

These are the foundational names from which many others are derived. Every new workflow should clearly define these upfront, **ideally during the planning phase and documented in the workflow's canonical YAML or initial planning documents (e.g., in `/Docs/Docs_4_Planning/`).**

- **`workflow_name`**

  - **Format:** `snake_case` (e.g., `page_curation`, `single_search`, `domain_curation`).
  - **Derivation & Authority:** Defined by the core purpose of the workflow. **While there isn't a formal, documented approval step specifically for `workflow_name` in cheat sheets or YAML files, new workflow names are typically reviewed informally during planning meetings or pull request reviews by senior developers. This review ensures clarity, consistency with existing workflows (e.g., the recommended patterns `{entity}_curation` or `{entity}_import`), and helps prevent conflicts. The name should be descriptive of the workflow's primary function.**
    - **Example of derivation (`workflow_name = sitemap_import`):** Core purpose: Importing URLs from sitemap files. Direct derivation: "sitemap" (data source) + "import" (action).
  - **Prohibited Patterns/Keywords:** **Avoid names that are SQL reserved words or could cause conflicts with existing system components. Adherence to common patterns like `{entity}_curation` or `{entity}_import` is strongly recommended for consistency and clarity.**
  - **Example:** For a workflow curating pages, `workflow_name` is `page_curation`.

- **`{WorkflowNameTitleCase}`**

  - **Format:** The `workflow_name` converted to `TitleCase` (first letter of each word capitalized, no spaces).
  - **Derivation:** From `workflow_name`.
  - **Example:** If `workflow_name` is `page_curation`, then `{WorkflowNameTitleCase}` is `PageCuration`.

- **`{workflowNameCamelCase}`**

  - **Format:** The `workflow_name` converted to `camelCase` (first letter of first word lowercase, subsequent words capitalized, no spaces).
  - **Derivation:** From `workflow_name`.
  - **Example:** If `workflow_name` is `page_curation`, then `{workflowNameCamelCase}` is `pageCuration`.

- **`source_table_name`**

  - **Format:** Singular, `snake_case`. Represents the primary database table the workflow interacts with or is centered around.
  - **Derivation & Authority:** Determined by the primary data entity of the workflow. **If a new table is required, its name is decided during the preliminary database design phase, which occurs before formal workflow implementation begins. The SQLAlchemy model file (e.g., `src/models/new_entity.py`) is typically created and committed before the workflow implementation, effectively solidifying this name.**
    - **Example (`source_table_name = sitemap_file` for the `sitemap_import` workflow):** This `source_table_name` directly corresponds to the model file `src/models/sitemap_file.py` and the SQLAlchemy model class `SitemapFile`.
  - **Prohibited Patterns/Keywords:** **Avoid names that are SQL reserved words. Always check existing database table names to prevent conflicts.**
  - **Example:** `page`, `domain`, `place`, `sitemap_file`, `local_business`.

- **`{SourceTableTitleCase}`**

  - **Format:** The `source_table_name` converted to `TitleCase`.
  - **Derivation:** From `source_table_name`.
  - **Example:** If `source_table_name` is `page`, then `{SourceTableTitleCase}` is `Page`.

- **`source_table_plural_name`**
  - **Format:** Plural, `snake_case`.
  - **Derivation:** From `source_table_name`. Standard English pluralization rules apply (e.g., `page` → `pages`, `sitemap_file` → `sitemap_files`). **Crucially, ensure consistency with the actual database table names (e.g., if the database table is named `sitemaps`, then `source_table_plural_name` for the `sitemap` entity should be `sitemaps`).**
  - **Example (`source_table_name = page`):** `pages`.
  - **Example (`source_table_name = sitemap_file`):** `sitemap_files`.
