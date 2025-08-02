# Layer 2: Schemas - Architectural Blueprint

**Version:** 2.0 - CONSOLIDATED
**Date:** 2025-08-01
**Consolidated From:**

- `v_1.0-ARCH-TRUTH-Definitive_Reference.md` (Core architectural principles & API standardization)
- `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Master naming conventions & structural patterns)
- `Docs/CONSOLIDATION_WORKSPACE/Layer2_Schemas/v_Layer-2.1-Schemas_Blueprint.md` (Layer-specific implementation details & technical debt)
- `Docs/CONSOLIDATION_WORKSPACE/Layer2_Schemas/v_Layer-2.1-Schemas_Blueprint.md` (Detailed Layer 2 conventions)
- `v_CONVENTIONS_AND_PATTERNS_GUIDE-Base_Identifiers.md` (Foundational naming patterns)

**Contextual References:**

- `Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` (Structural template and quality benchmark)
- `Docs/Docs_10_Final_Audit/Layer-1-Models_Enums_Blueprint.md` (Reference for ENUM usage)
- Current codebase (`src/schemas/`)

---

## Preamble: Relation to Core Architectural Principles

The standards herein for Layer 2 directly support and implement the Core Architectural Principles outlined in `1.0-ARCH-TRUTH-Definitive_Reference.md`, particularly:

- **API Standardization:** By defining strict rules for Pydantic models used in request/response validation and data transfer.
- **Layered Architectural Awareness:** By establishing clear responsibilities, structures, and naming conventions for API contract components.

This Blueprint translates those high-level principles into specific, auditable criteria for Pydantic schemas.

---

## 1. Core Principle(s) for Layer 2: API Contract Definition & Validation

Layer 2 is designated as the "API Contracts" layer. Its core principles are:

- **Define Contracts:** To serve as the single source of truth for the structure and data types of API requests and responses.
- **Validation:** To enforce data validation rules at the API boundary, ensuring data integrity before it reaches Layer 3 (Routers) or Layer 4 (Services).
- **Serialization/Deserialization:** To manage the transformation of data between Python objects (used internally) and JSON (used in API communication).
- **Clarity and Consistency:** To ensure schemas are clearly named, consistently structured, and easy to understand.
- **API Standardization:** Support uniform `/api/v3/` versioning prefix with consistent endpoint naming patterns.
- **Type Safety:** Leverage Pydantic's type system for compile-time safety and self-documenting contracts.

---

## 2. Standard Pattern: Pydantic Models

This is the **sole and mandatory pattern** for defining API request/response schemas and data transfer objects (DTOs) in Layer 2.

### 2.1. Definition & Scope

- **Purpose:** To define the expected shape, types, and validation rules for data exchanged via API endpoints.
- **Location & File Naming (Workflow-Centric Organization):**
  - **Primary Convention (Mandatory for New Workflows):** For workflow-specific actions (batch updates, workflow operations): `src/schemas/{workflow_name}.py`
    - **Rationale:** Aligns with clear separation of concerns and emphasizes workflow-specific nature
    - **Example**: `src/schemas/page_curation.py` contains `PageCurationUpdateRequest`, `PageCurationUpdateResponse`
  - **Secondary Convention (Generic Entity Schemas):** For generic CRUD operations unrelated to specific workflows: `src/schemas/{source_table_name}.py`
    - **Example**: `src/schemas/sitemap_file.py` contains `SitemapFileBase`, `SitemapFileCreate`, `SitemapFileRead`
  - **Shared/Common Schemas:** Common patterns in `src/schemas/common.py` (pagination, standard error responses)
- **Responsibilities:**
  - Defining input (request body/query parameters) and output (response body) structures.
  - Specifying data types for each field using Python type hints.
  - Implementing validation logic using Pydantic validators (where necessary and focused on format/type, not business rules).
  - Configuring serialization behavior (e.g., ORM mode, aliases).

### 2.2. Key Compliance Criteria for Layer 2 Components

These criteria are primarily derived from `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Section 3), `1.0-ARCH-TRUTH-Definitive_Reference.md`, and general Pydantic best practices.

#### 2.2.1. Pydantic Models (Schemas)

- **Naming & Location:**
  1.  **File Name:** Must be `src/schemas/{entity_name}.py` (singular, snake_case).
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`
  2.  **Class Name Patterns:**
      - **For Workflow-Specific Actions (Primary Pattern):**
        - **Prefix:** MUST use `{WorkflowNameTitleCase}` prefix (ensures clarity and consistency)
        - **Suffixes:** Request models MUST end with "Request", Response models MUST end with "Response"
        - **Structure:**
          - Request: `{WorkflowNameTitleCase}[ActionDescription][Batch]Request`
          - Response: `{WorkflowNameTitleCase}[ActionDescription][Batch]Response`
        - **Examples:**
          - `PageCurationBatchStatusUpdateRequest`
          - `PageCurationBatchStatusUpdateResponse`
          - `PageCurationUpdateRequest`
          - `PageCurationUpdateResponse`
      - **For Generic Entity CRUD (Secondary Pattern):**
        - `{EntityName}Base`: Common fields shared across operations
        - `{EntityName}Create`: Fields required for creation
        - `{EntityName}Update`: Fields allowed for update (often optional)
        - `{EntityName}Read`: Fields returned in responses (includes ID, timestamps)
      - **Technical Debt:** Existing schemas like `SitemapFileBatchUpdate` missing "Request"/"Response" suffix or wrong prefix are non-compliant
- **Base Class:**
  1.  Must inherit from `pydantic.BaseModel`.
- **Fields:**
  1.  All fields must have explicit Python type hints (e.g., `str`, `int`, `bool`, `datetime`, `UUID`, `List[str]`, `Optional[int]`).
  2.  Field names must be `snake_case`.
  3.  Use `Optional[...]` (or `... | None` in Python 3.10+) for fields that are not required.
  4.  Default values should be used appropriately.
- **Configuration (`class Config` / `model_config`):**
  1.  Schemas used for **responses** (e.g., `Read` schemas) that are generated from ORM models (Layer 1) **MUST** include `orm_mode = True` (Pydantic v1) or `from_attributes = True` (Pydantic v2) in their configuration.
      - _Source:_ Required for Pydantic<->SQLAlchemy integration.
  2.  Use `alias` or `alias_generator` if API field names need to differ from Python field names (e.g., `camelCase` in JSON), although `snake_case` is preferred for consistency.
- **Validators:**
  1.  Use Pydantic validators (`@validator` / `@field_validator`) sparingly.
  2.  Validators should primarily focus on **format validation** (e.g., email format, URL format) or simple cross-field validation **within the schema itself**.
  3.  **Complex business logic validation** belongs in Layer 4 (Services), not Layer 2 Schemas.
- **Schema Variations (CRUD Pattern):**
  1.  Employ the Base/Create/Update/Read inheritance pattern for CRUD operations to minimize repetition and clearly define different data shapes for different operations.
      - `Base` contains common fields.
      - `Create` inherits `Base`, adds creation-specific fields.
      - `Update` inherits `Base`, makes fields optional as needed.
      - `Read` inherits `Base`, adds read-only fields (like `id`, `created_at`) and potentially nested schemas for related data.
- **ENUM Usage (Layer Integration):**
  1.  Fields representing controlled vocabularies (like status) **MUST** use the corresponding `Enum` defined in Layer 1.
      - **Import Pattern**: Import from `src/models/page.py` or `src/models/enums.py`
      - **Example**: `status: PageCurationStatus` in schema
      - **Rationale**: Maintains layered architectural awareness and single source of truth
      - **Note**: Addresses the Layer 1 ENUM location conflict by accepting both import sources
- **Docstrings & Descriptions:**
  1.  Schema classes should have a docstring explaining their purpose (e.g., "Schema for creating a new user.").
  2.  Fields can have a `description` in `Field(..., description="...")` for OpenAPI documentation clarity.

---

## 3. Documented Exception Patterns

For Layer 2 (Schemas), the "Standard Pattern" using Pydantic `BaseModel` and the associated conventions (Section 2) is mandatory. There are no documented "exception patterns" for defining API contracts.

Deviations from the criteria in Section 2.2 are considered technical debt.

---

## 3. Critical Implementation Context

### 3.1. Schema Organization Strategy

**Workflow-Centric Approach**:
- **Primary Pattern**: Workflow-specific schemas belong in `src/schemas/{workflow_name}.py`
- **Rationale**: Clear separation of concerns, emphasizes workflow-specific nature of operations
- **Example**: `PageCurationUpdateRequest` belongs in `src/schemas/page_curation.py`, NOT `src/schemas/page.py`

**Entity-Centric Fallback**:
- **Secondary Pattern**: Generic CRUD operations in `src/schemas/{source_table_name}.py`
- **Use Case**: Genuinely generic schemas intended for reuse across multiple workflows
- **Example**: `SitemapFileBase`, `SitemapFileCreate`, `SitemapFileRead` in `src/schemas/sitemap_file.py`

### 3.2. Naming Convention Hierarchy

**Request/Response Naming Rules**:
1. **Workflow Actions**: `{WorkflowNameTitleCase}[Action][Batch]Request/Response`
2. **Generic CRUD**: `{EntityName}Base/Create/Update/Read`
3. **Batch Operations**: Include "Batch" in the name for bulk operations
4. **Version Compatibility**: Schema changes must maintain API compatibility

### 3.3. Current Architecture Status

- **Compliance Level**: ~75% compliant with architectural standards
- **Schema Migration**: Reorganization from api_models to dedicated schema files (mostly complete)
- **API Versioning**: Uniform `/api/v3/` prefix implementation
- **Reference Implementation**: `src/schemas/page_curation.py` with `PageCurationUpdateRequest`

### 3.4. Known Technical Debt

- **Missing Suffixes**: `SitemapFileBatchUpdate` lacks "Request" suffix
- **Wrong Organization**: Workflow-specific schemas in entity files instead of workflow files
- **Non-Workflow Prefixes**: Some schemas use entity prefixes instead of workflow prefixes
- **Validation Location**: Some business logic validation in schemas instead of Layer 4

---

## 4. Audit & Assessment Guidance

**Core Philosophy:** The primary goal of auditing Layer 2 components is to ensure the API contracts defined by Pydantic schemas are clear, consistent, correctly typed, and adhere to the established architectural standards (Section 2.2). Identifying deviations catalogs technical debt and guides refactoring towards robust and maintainable API interfaces.

When auditing Layer 2 components (`src/schemas/*.py` files):

1.  **Identify Component Type:** Confirm the component is a Pydantic Model class inheriting from `BaseModel`.

2.  **Assess Against Specific Criteria (Section 2.2):**

    - Systematically check the Pydantic model against each criterion listed in Section 2.2.1 (Naming & Location, Base Class, Fields, Configuration, Validators, Schema Variations, ENUM Usage, Docstrings).
    - Verify that the schema's purpose (e.g., request input, response output) aligns with its structure and configuration (e.g., `orm_mode` for responses, appropriate use of `Optional`).
    - Ensure validation logic is appropriately placed (format validation in Layer 2, business logic in Layer 4).

3.  **Document Technical Debt:** For **any deviation** from the compliance criteria in Section 2.2, clearly document this in the "Gap Analysis" of the relevant audit sheet or report. This includes:

    - Incorrect file or class naming (including lack of Base/Create/Update/Read pattern where appropriate).
    - Missing or incorrect base class inheritance.
    - Fields lacking type hints or using incorrect types.
    - Non-snake_case field names.
    - Missing `orm_mode`/`from_attributes` for response schemas generated from ORM models.
    - Overly complex validation logic better suited for Layer 4.
    - Failure to use Layer 1 ENUMs for status or type fields.
    - Lack of schema variations (Base/Create/Update/Read) leading to ambiguity or repetition.
    - Missing or inadequate docstrings.

4.  **Prescribe Refactoring Actions:** Based on the identified gaps, suggest refactoring actions. These actions should aim to align the component with the Layer 2 Blueprint. Examples:
    - "Rename schema class `X` to `XRead` to clarify its use as a response model."
    - "Refactor `UserSchema` into `UserBase`, `UserCreate`, `UserUpdate`, `UserRead` schemas."
    - "Add `orm_mode = True` to Config in `ProductRead` schema."
    - "Move validation logic for business rule X from `SchemaY` validator to the corresponding Layer 4 service."
    - "Update `status` field in `TaskSchema` to use `TaskStatus` Enum from `src/models/task.py`."
    - "Add type hints to all fields in `OrderCreate` schema."

---
