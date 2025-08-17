# ScraperSky Naming & Structural Conventions Guide

**Date:** 2025-08-01
**Version:** 2.0 (Consolidated)

---

### **Note on this Document's Purpose**

This document has been updated as part of a significant documentation consolidation effort. It now serves two primary purposes:

1.  To define the **global, cross-layer naming conventions** (such as `workflow_name`, `source_table_name`, and their derivatives) that are foundational to all development.
2.  To act as a **central index**, directing developers to the authoritative blueprint for each architectural layer for detailed, layer-specific conventions.

For the most current and detailed standards for any specific layer, please refer to the linked blueprint documents.

---

## Related Documentation

- **[v_1.0-ARCH-TRUTH-Definitive_Reference.md](./v_1.0-ARCH-TRUTH-Definitive_Reference.md)** - The high-level architectural reference.
- **Layer-Specific Blueprints:** See links in the sections below for the authoritative source of truth for each layer's conventions.

**Objective:** This document provides the foundational naming conventions for the ScraperSky backend project and directs developers to the detailed, authoritative blueprints for layer-specific standards.

---

## Core Principle

Consistency is paramount. Most names are derived from a `workflow_name` (snake_case) and/or a `source_table_name` (singular, snake_case). This guide explicitly details these derivations.

---

## 1. Base Identifiers (Global Convention)

These are the foundational names from which many others are derived. Every new workflow should clearly define these upfront, **ideally during the planning phase and documented in the workflow's canonical YAML or initial planning documents.**

- **`workflow_name`**

  - **Format:** `snake_case` (e.g., `page_curation`, `single_search`, `domain_curation`).
  - **Derivation & Authority:** Defined by the core purpose of the workflow. New workflow names are typically reviewed informally during planning meetings or pull request reviews to ensure clarity and consistency.
  - **Example:** For a workflow curating pages, `workflow_name` is `page_curation`.

- **`{WorkflowNameTitleCase}`**

  - **Format:** The `workflow_name` converted to `TitleCase`.
  - **Derivation:** From `workflow_name`.
  - **Example:** If `workflow_name` is `page_curation`, then `{WorkflowNameTitleCase}` is `PageCuration`.

- **`{workflowNameCamelCase}`**

  - **Format:** The `workflow_name` converted to `camelCase`.
  - **Derivation:** From `workflow_name`.
  - **Example:** If `workflow_name` is `page_curation`, then `{workflowNameCamelCase}` is `pageCuration`.

- **`source_table_name`**

  - **Format:** Singular, `snake_case`. Represents the primary database table the workflow interacts with.
  - **Derivation & Authority:** Determined by the primary data entity of the workflow. The SQLAlchemy model file (e.g., `src/models/new_entity.py`) effectively solidifies this name.
  - **Example:** `page`, `domain`, `sitemap_file`.

- **`{SourceTableTitleCase}`**

  - **Format:** The `source_table_name` converted to `TitleCase`.
  - **Derivation:** From `source_table_name`.
  - **Example:** If `source_table_name` is `page`, then `{SourceTableTitleCase}` is `Page`.

- **`source_table_plural_name`**
  - **Format:** Plural, `snake_case`.
  - **Derivation:** From `source_table_name`. Standard English pluralization rules apply.
  - **Example (`source_table_name = page`):** `pages`.

---

## Layer-Specific Conventions

### 2. Layer 1: Models & ENUMs

The definitive conventions for this layer are now maintained in the **[Layer 1: Models & ENUMs - Architectural Blueprint](../../Docs_10_Final_Audit/v_Layer-1.1-Models_Enums_Blueprint.md)**.

---

### 3. Layer 2: Schemas

The definitive conventions for this layer are now maintained in the **[Layer 2: Schemas - Architectural Blueprint](../../Docs_10_Final_Audit/v_Layer-2.1-Schemas_Blueprint.md)**.

---

### 4. Layer 3: Routers

The definitive conventions for this layer are now maintained in the **[Layer 3: Routers - Architectural Blueprint](../../Docs_10_Final_Audit/v_Layer-3.1-Routers_Blueprint.md)**.

---

### 5. Layer 4: Services & Schedulers

The definitive conventions for this layer are now maintained in the **[Layer 4: Services & Schedulers - Architectural Blueprint](../../Docs_10_Final_Audit/v_Layer-4.1-Services_Blueprint.md)**.

---

### 6. Layer 5: Configuration

The definitive conventions for this layer are now maintained in the **[Layer 5: Configuration - Architectural Blueprint](../../Docs_10_Final_Audit/v_Layer-5.1-Configuration_Blueprint.md)**.

---

### 7. Layer 6: UI Components

The definitive conventions for this layer are now maintained in the **[Layer 6: UI Components - Architectural Blueprint](../../Docs_10_Final_Audit/v_Layer-6.1-UI_Components_Blueprint.md)**.

---

### 8. Layer 7: Testing

The definitive conventions for this layer are now maintained in the **[Layer 7: Testing - Architectural Blueprint](../../Docs_10_Final_Audit/v_Layer-7.1-Testing_Blueprint.md)**.

---

This guide is intended to be a living document. As new patterns emerge or existing ones are refined, this document and the linked blueprints should be updated to reflect the current best practices for the ScraperSky project.