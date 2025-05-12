# Layer 2: Schemas - Architectural Blueprint

**Version:** 1.0
**Date:** 2025-05-14
**Derived From:**

- `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md` (Core Layer 2 Responsibilities & Architectural Principles)
- `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Primarily Section 3)
- `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md` (General principles, specific Layer 2 clarifications if present)

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

---

## 2. Standard Pattern: Pydantic Models

This is the **sole and mandatory pattern** for defining API request/response schemas and data transfer objects (DTOs) in Layer 2.

### 2.1. Definition & Scope

- **Purpose:** To define the expected shape, types, and validation rules for data exchanged via API endpoints.
- **Location & File Naming (Conventions from `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 3):**
  - **Schema Files:** `src/schemas/{entity_name}.py` (singular, snake_case). Example: `src/schemas/page.py`, `src/schemas/user.py`.
  - **Shared/Common Schemas:** Can be placed in `src/schemas/common.py` (e.g., for pagination, standard error responses).
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
  2.  **Class Name:** Must clearly indicate the entity and purpose, using PascalCase. Follow the Base/Create/Update/Read pattern where applicable:
      - `{EntityName}Base`: Common fields shared across create/update/read.
      - `{EntityName}Create`: Fields required for creation (inherits from Base).
      - `{EntityName}Update`: Fields allowed for update (inherits from Base, often all optional).
      - `{EntityName}Read` or `{EntityName}`: Fields returned in responses (inherits from Base, includes ID, timestamps, potentially related data schemas).
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`, Pydantic best practices.
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
- **ENUM Usage:**
  1.  Fields representing controlled vocabularies (like status) **MUST** use the corresponding `Enum` defined in Layer 1 (`src/models/`).
      - _Example:_ `status: PageCurationStatus` where `PageCurationStatus` is imported from `src/models/page.py` or `src/models/enums.py`.
      - _Source:_ `CONVENTIONS_AND_PATTERNS_GUIDE.md`, `1.0-ARCH-TRUTH-Definitive_Reference.md` (Layered Awareness principle).
- **Docstrings & Descriptions:**
  1.  Schema classes should have a docstring explaining their purpose (e.g., "Schema for creating a new user.").
  2.  Fields can have a `description` in `Field(..., description="...")` for OpenAPI documentation clarity.

---

## 3. Documented Exception Patterns

For Layer 2 (Schemas), the "Standard Pattern" using Pydantic `BaseModel` and the associated conventions (Section 2) is mandatory. There are no documented "exception patterns" for defining API contracts.

Deviations from the criteria in Section 2.2 are considered technical debt.

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
