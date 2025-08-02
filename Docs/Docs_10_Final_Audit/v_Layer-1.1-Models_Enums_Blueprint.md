# Layer 1: Models & ENUMs - Architectural Blueprint

**Version:** 2.0 - CONSOLIDATED
**Date:** 2025-08-01
**Consolidated From:**

- `v_1.0-ARCH-TRUTH-Definitive_Reference.md` (Core architectural principles & layer responsibilities)
- `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Master naming conventions & structural patterns)
- `Docs/CONSOLIDATION_WORKSPACE/Layer1_Models_Enums/v_Layer-1.1-Models_Enums_Blueprint.md` (Layer-specific implementation details & technical debt)
- `Docs/CONSOLIDATION_WORKSPACE/Layer1_Models_Enums/v_Layer-1.1-Models_Enums_Blueprint.md` (Detailed Layer 1 conventions)
- `Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Foundational naming patterns)

**Contextual References:**

- `Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` (Structural template and quality benchmark)
- Current codebase (`src/models/`)

---

## Preamble: Relation to Core Architectural Principles

The standards herein for Layer 1 directly support and implement the Core Architectural Principles outlined in `1.0-ARCH-TRUTH-Definitive_Reference.md`, particularly:

- **Strict Database Access Patterns:** By mandating ORM-only usage.
- **Layered Architectural Awareness:** By defining clear responsibilities, structures, and naming conventions for data foundation components.

This Blueprint translates those high-level principles into specific, auditable criteria for SQLAlchemy models and Python ENUMs.

---

## 1. Core Principle(s) for Layer 1: Data Foundation & Standardization

Layer 1 is designated as "The Data Foundation." Its core principles are:

- **Define Truth:** To serve as the single source of truth for data structure, types, relationships, and permissible states within the application.
- **Standardization:** To enforce consistent naming, structure, and patterns for all database models and enumerated types, facilitating clarity and maintainability.
- **ORM Exclusivity:** To ensure all database entity definitions and interactions are managed through the SQLAlchemy ORM, abstracting raw SQL.
- **Schema Management:** ALL SCHEMA CHANGES MUST BE MANAGED VIA SUPABASE MCP with version control and audit trails.
- **Transaction Neutrality:** Database operations NEVER handle JWT or tenant authentication - authentication is handled at Layer 3.

---

## 2. Standard Pattern: SQLAlchemy Models & Python ENUMs

This is the **sole and mandatory pattern** for defining data entities and controlled vocabularies in Layer 1.

### 2.1. Definition & Scope

- **Purpose:**
  - **Models:** To define the schema, attributes, relationships, and persistence logic for database entities.
  - **ENUMs:** To define named sets of constant values, typically for status tracking, type classification, or any field requiring a restricted set of string-based options.
- **Location & File Naming (Strict Conventions from `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 2):**
  - **SQLAlchemy Models:**
    - File: `src/models/{source_table_name}.py` (singular, snake_case). Example: `src/models/page.py`.
  - **Python ENUMs:**
    - Primarily defined within the relevant model's file (e.g., `PageCurationStatus` in `src/models/page.py`) or in a shared enum file like `src/models/enums.py` if truly generic and widely used across unrelated models (though workflow-specific enums belong with their model).
- **Responsibilities:**
  - **Models:**
    - Defining table structure (`__tablename__`, columns with SQLAlchemy types).
    - Establishing relationships between entities (`relationship()`).
    - (Optionally) Providing model-specific helper methods or properties that operate on an instance's data.
  - **ENUMs:**
    - Providing a controlled, typed vocabulary for specific model fields.
    - Ensuring data consistency for status fields and classifications.

### 2.2. Key Compliance Criteria for Layer 1 Components

These criteria are primarily derived from `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Section 2) and `1.0-ARCH-TRUTH-Definitive_Reference.md`.

#### 2.2.1. SQLAlchemy Models

- **Naming & Location:**
  1.  **File Name:** Must be `src/models/{source_table_name}.py` (singular, snake_case).
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
  2.  **Class Name:** Must be `{SourceTableTitleCase}` (e.g., `Page` for `page.py`).
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
- **Base Class & Table Definition:**
  1.  Must inherit from the project's standard base model class (e.g., `Base`, `BaseModel` as observed in `src/models/base.py`).
  2.  `__tablename__` must be defined and should typically be the plural snake_case version of the model name (e.g., `pages`).
- **Columns:**
  1.  All attributes representing database columns must use `sqlalchemy.Column` with appropriate SQLAlchemy types (e.g., `String`, `Integer`, `Boolean`, `DateTime`, `UUID`, `JSONB`, `Text`, `sqlalchemy.dialects.postgresql.ENUM` for PgEnum).
  2.  Column names must be `snake_case`.
  3.  Primary keys should be consistently named (e.g., `id`).
  4.  Foreign keys must be correctly defined using `ForeignKey` and follow a consistent pattern (e.g., `{related_model_singular}_id`).
  5.  `ondelete` behavior for foreign keys must be explicitly defined and appropriate for the relationship (e.g., `"CASCADE"`, `"SET NULL"`).
- **Relationships:**
  1.  Relationships must be defined using `sqlalchemy.orm.relationship`.
  2.  `back_populates` (or `backref` for simpler bidirectional relationships) must be correctly specified to link related models.
  3.  `uselist=False` must be used for one-to-one relationships.
- **ORM Exclusivity:**
  1.  No raw SQL strings for defining model behavior or in any helper methods within the model file. All data interaction logic (if any exists directly in model files, which should be minimal) must use ORM constructs.
      - _Source:_ `1.0-ARCH-TRUTH-Definitive_Reference.md` (Strict Database Access Patterns).
- **Tenant ID / Legacy Fields:**
  1.  No `tenant_id` fields or related logic. (Reflects removal as per ARCH-TRUTH).
  2.  Review for other legacy fields mentioned in ARCH-TRUTH technical debt for Layer 1; new models should not introduce them.
- **Docstrings:**
  1.  Model classes should have a docstring explaining their purpose.
  2.  Non-obvious columns or relationships should have comments or be clearly named.

#### 2.2.2. Python ENUMs (Status ENUMs & General ENUMs)

- **Naming & Definition (Strict Conventions for Status ENUMs):**
  1.  **Workflow-Specific Status Enum Class Names:** Must be `{WorkflowNameTitleCase}CurationStatus` or `{WorkflowNameTitleCase}ProcessingStatus`.
      - _Example:_ `PageCurationStatus`, `PageProcessingStatus`.
      - _Rationale:_ Ensures clear association with specific workflow and maintains universal consistency.
  2.  **Base Class:** Must inherit from `(str, Enum)`. (e.g., `class PageCurationStatus(str, Enum):`). The "Enum" suffix on the class name itself is discouraged.
      - _Technical Debt:_ Existing deviations like `SitemapImportCurationStatusEnum` using "Enum" suffix are non-compliant.
  3.  **Location:** **CONFLICT EXISTS** - Blueprint allows model files OR `src/models/enums.py`, but `src/models/enums.py` header mandates centralization. **Current reality**: Enums scattered between both locations.

- **Standard Values (Mandatory for New Workflow Status ENUMs):**
  1.  **`{WorkflowNameTitleCase}CurationStatus`** members **MUST** include: 
      - `New = "New"`, `Queued = "Queued"`, `Processing = "Processing"`, `Complete = "Complete"`, `Error = "Error"`, `Skipped = "Skipped"`
      - **No custom additions** to this primary curation enum are permitted.
  2.  **`{WorkflowNameTitleCase}ProcessingStatus`** members **MUST** include:
      - `Queued = "Queued"`, `Processing = "Processing"`, `Complete = "Complete"`, `Error = "Error"`

- **Model Column Association (for Status ENUMs):**
  1.  **Curation Status Column**: `{workflow_name}_curation_status`
      - **Type Example**: `Column(PgEnum(PageCurationStatus, name="pagecurationstatus", create_type=False), nullable=False, server_default=PageCurationStatus.New.value, index=True)`
  2.  **Processing Status Column**: `{workflow_name}_processing_status`
      - **Type Example**: `Column(PgEnum(PageProcessingStatus, name="pageprocessingstatus", create_type=False), nullable=True, index=True)`
  3.  **Processing Error Column**: `{workflow_name}_processing_error` (Type: `Text`, nullable=True)

- **General ENUMs (Non-Status):**
  1.  Should inherit from `(str, Enum)` for string-based database storage
  2.  Naming: Clear PascalCase (e.g., `UserRole`, `TaskType`)
  3.  Values: Meaningful strings

- **Handling Justified Non-Standard User States (Additional Status Fields):**
  1.  **CRITICAL**: **MUST NOT** modify standard `{WorkflowNameTitleCase}CurationStatus` or `{WorkflowNameTitleCase}ProcessingStatus` Enums
  2.  **Solution**: Create new, separate status field with dedicated Python Enum class
  3.  **Naming Pattern**: 
      - Column: `{workflow_name}_{status_purpose}_status`
      - Enum Class: `{WorkflowNameTitleCase}{StatusPurpose}Status`
  4.  **Requires**: Significant justification, formal review, and approval
  5.  **Strongly discouraged** to maintain system simplicity

---

## 3. Documented Exception Patterns

For Layer 1 (Models & ENUMs), the "Standard Pattern" described in Section 2 is comprehensive and mandatory. There are no documented "exception patterns" in the sense of alternative ways to define core data structures.

Deviations from the criteria in Section 2.2 are to be considered technical debt. The handling of "Justified Non-Standard User States" (Section 2.2.2) is a specific, rule-bound extension within the standard pattern, not an exception pattern itself.

---

## 3. Critical Implementation Context

### 3.1. Base Identifiers Foundation

All Layer 1 components must derive from standardized base identifiers:

- **`workflow_name`**: `snake_case` format (e.g., `page_curation`, `domain_curation`)
  - Defines core workflow purpose
  - Must follow `{entity}_curation` or `{entity}_import` patterns
  - Avoid SQL reserved words and system conflicts

- **`source_table_name`**: Singular `snake_case` (e.g., `page`, `domain`, `sitemap_file`)
  - Represents primary database table
  - Corresponds directly to model file naming
  - Must avoid SQL reserved words

- **Derived Formats**:
  - `{WorkflowNameTitleCase}`: `PageCuration`, `DomainCuration`
  - `{SourceTableTitleCase}`: `Page`, `Domain`, `SitemapFile`
  - `source_table_plural_name`: `pages`, `domains`, `sitemap_files`

### 3.2. The ENUM Technical Debt Crisis

**CRITICAL CONTEXT**: Layer 1 previously experienced "The ENUM Catastrophe" where autonomous enum refactoring broke the entire system for a week. This has resulted in:

- **Location Conflict**: 
  - Blueprint allows enums in model files OR `src/models/enums.py`
  - `src/models/enums.py` header mandates "All enums MUST be defined here"
  - **Reality**: Enums are scattered between both locations

- **SQLAlchemy Enum Conversion Issue** (P1 Technical Debt):
  - SQLAlchemy converting enum values ("Queued") to names ("QUEUED")
  - Causing background scheduler errors
  - Documented in `TECHNICAL_DEBT_ENUM_CONVERSION.md`
  - Temporary workarounds not fully effective

- **Legacy Technical Debt**:
  - `SitemapCurationStatusEnum` (uses "Enum" suffix - non-compliant)
  - `SitemapImportCurationStatusEnum` (uses "Enum" suffix - non-compliant)
  - Non-standard enum values ("Selected" vs "Queued")

**Advisory Mandate**: Layer 1 must remain advisory-only. NEVER attempt autonomous enum refactoring.

### 3.3. Current Architecture Status

- **Compliance Level**: ~80% compliant with architectural standards
- **Tenant Isolation**: Completely removed from system - no tenant filtering in database operations
- **Authentication Boundary**: Database operations are authentication-neutral
- **Connection Pattern**: Supavisor pooling with specific SQLAlchemy 2.0 configurations
- **Reference Implementation**: `src/models/page.py` with `PageCurationStatus` and `PageProcessingStatus`

---

## 4. Audit & Assessment Guidance

**Core Philosophy:** The primary goal of auditing Layer 1 components is to identify **all deviations from the ideal architectural standards** defined in this Blueprint (Section 2.2), thereby cataloging technical debt. While existing, functional code ("Code is King") is acknowledged as the current reality, this assessment measures it against the defined ideal to guide future refactoring efforts towards consistency and maintainability.

When auditing Layer 1 components (`src/models/*.py` files and ENUM definitions):

1.  **Identify Component Type:** Determine if the component under review is an SQLAlchemy Model or a Python ENUM.

2.  **Assess Against Specific Criteria (Section 2.2):**

    - **For SQLAlchemy Models:** Systematically check the model against each criterion listed in Section 2.2.1 (Naming & Location, Base Class, Columns, Relationships, ORM Exclusivity, Tenant ID/Legacy, Docstrings).
    - **For Python ENUMs:** Systematically check the ENUM against each criterion listed in Section 2.2.2 (Naming & Definition, Standard Values for status enums, Model Column Association, rules for General ENUMs, and rules for Non-Standard User States if applicable).

3.  **Document Technical Debt:** For **any deviation** from the compliance criteria in Section 2.2, clearly document this in the "Gap Analysis" of the relevant audit sheet or report. This includes:

    - Incorrect file or class naming.
    - Missing or incorrect base class inheritance for models.
    - Improper column definitions (type, naming, keys).
    - Incorrect relationship definitions.
    - Use of raw SQL.
    - Presence of `tenant_id` or unapproved legacy fields in new code.
    - Non-compliant ENUM naming, base class, values, or associated model column definitions.
    - Introduction of non-standard user states without following the strict justification and implementation protocol.
    - Missing or inadequate docstrings/comments.

4.  **Prescribe Refactoring Actions:** Based on the identified gaps, suggest refactoring actions. These actions should aim to align the component with the Layer 1 Blueprint. Examples:
    - "Rename model class X to Y to comply with `{SourceTableTitleCase}` convention."
    - "Refactor ENUM Z to inherit from `(str, Enum)` and use standard status values."
    - "Update foreign key A in model B to include `ondelete` behavior."
    - "Remove raw SQL query from helper method in model C."

---
