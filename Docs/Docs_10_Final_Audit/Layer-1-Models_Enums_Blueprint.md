# Layer 1: Models & ENUMs - Architectural Blueprint

**Version:** 1.0
**Date:** 2025-05-14
**Derived From:**

- `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md` (Core Layer 1 Responsibilities & Architectural Principles)
- `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Primarily Section 2)
- `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md` (General principles, specific Layer 1 clarifications if present)

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

- **Naming & Definition (Strict Conventions for Status ENUMs from `CONVENTIONS_AND_PATTERNS_GUIDE.md`):**
  1.  **Workflow-Specific Status Enum Class Names:** Must be `{WorkflowNameTitleCase}CurationStatus` or `{WorkflowNameTitleCase}ProcessingStatus`.
      - _Example:_ `PageCurationStatus`, `PageProcessingStatus`.
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
  2.  **Base Class:** Must inherit from `(str, Enum)`. (e.g., `class PageCurationStatus(str, Enum):`). The "Enum" suffix on the class name itself is discouraged by the guide (e.g. `PageCurationStatus` not `PageCurationStatusEnum`).
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md` (also `1.0-ARCH-TRUTH-Definitive_Reference.md` example `Status enums inherit from (str, Enum) without the "Enum" suffix`)
  3.  **Location:** Typically defined in the corresponding model's file (e.g., `PageCurationStatus` in `src/models/page.py`).
- **Standard Values (Mandatory for New Workflow Status ENUMs):**
  1.  `{WorkflowNameTitleCase}CurationStatus` members **MUST** include: `New = "New"`, `Queued = "Queued"`, `Processing = "Processing"`, `Complete = "Complete"`, `Error = "Error"`, `Skipped = "Skipped"`. No custom additions to this primary curation enum are permitted.
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
  2.  `{WorkflowNameTitleCase}ProcessingStatus` members **MUST** include: `Queued = "Queued"`, `Processing = "Processing"`, `Complete = "Complete"`, `Error = "Error"`.
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
- **Model Column Association (for Status ENUMs):**
  1.  Curation Status Column Name: `{workflow_name}_curation_status`.
      - _Type:_ `Column(PgEnum({WorkflowNameTitleCase}CurationStatus, name="{workflow_name}curationstatus", create_type=False), ...)`
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
  2.  Processing Status Column Name: `{workflow_name}_processing_status`.
      - _Type:_ `Column(PgEnum({WorkflowNameTitleCase}ProcessingStatus, name="{workflow_name}processingstatus", create_type=False), ...)`
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
  3.  Processing Error Column Name: `{workflow_name}_processing_error` (Type: `Text`).
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
- **General ENUMs (Non-Status):**
  1.  If not workflow-specific status ENUMs, should still inherit from `(str, Enum)` if string-based values are desired for database storage/API usage.
  2.  Naming should be clear and PascalCase (e.g., `UserRole`, `TaskType`).
  3.  Values should be meaningful strings.
- **Handling Justified Non-Standard User States (Additional Status Fields):**
  1.  **MUST NOT** modify the standard `{WorkflowNameTitleCase}CurationStatus` or `{WorkflowNameTitleCase}ProcessingStatus` Enums or their primary columns.
  2.  Requires a **new, separate status field** on the SQLAlchemy model and a **new, dedicated Python Enum class**.
  3.  Additional Status Column Name: `{workflow_name}_{status_purpose}_status`.
  4.  Additional Python Enum Class Name: `{WorkflowNameTitleCase}{StatusPurpose}Status`.
  5.  This is **strongly discouraged** and requires significant justification and approval.
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`

---

## 3. Documented Exception Patterns

For Layer 1 (Models & ENUMs), the "Standard Pattern" described in Section 2 is comprehensive and mandatory. There are no documented "exception patterns" in the sense of alternative ways to define core data structures.

Deviations from the criteria in Section 2.2 are to be considered technical debt. The handling of "Justified Non-Standard User States" (Section 2.2.2) is a specific, rule-bound extension within the standard pattern, not an exception pattern itself.

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
