# Work Order: Create Architectural Blueprints & AI Audit SOPs

This document outlines the tasks for creating architectural blueprints and AI Audit Standard Operating Procedures (SOPs) for various layers of the ScraperSky backend system.

## Layer 1: Models & ENUMs

### 1. Architectural Blueprint

#### 1.1. Overview

Layer 1 encompasses the core data structures of the application, specifically the database models and enumerated types (ENUMs). These components define the schema, relationships, and permissible values for the data handled by the system.

- **Location:**
  - Models: `src/models/`
  - ENUMs: `src/models/enums.py`
  - Base model definitions: `src/models/base.py`
  - API-specific models/schemas may also exist in `src/models/api_models.py` or `src/schemas/`.

#### 1.2. Models

- **Technology:** SQLAlchemy ORM.
- **Base Classes:** Models inherit from common base classes (e.g., `Base`, `BaseModel`) found in `src/models/base.py`, which likely provide common fields (e.g., `id`, `created_at`, `updated_at`) and utility methods.
- **Structure:**
  - Each model is typically defined in its own Python file within `src/models/` (e.g., `job.py`, `domain.py`).
  - `__tablename__` attribute defines the corresponding database table.
  - Columns are defined using `sqlalchemy.Column` with appropriate SQLAlchemy types (e.g., `Integer`, `String`, `UUID`, `JSONB`, `Float`, `ForeignKey`).
  - Relationships between models (one-to-one, one-to-many, many-to-many) are defined using `sqlalchemy.orm.relationship`.
  - Models may include:
    - Instance methods for specific logic related to an object (e.g., `to_dict()`, `update_progress()`).
    - Class methods for common queries or creation patterns (e.g., `get_by_id()`, `create_for_domain()`).
- **Key Characteristics:**
  - Extensive use of type hinting.
  - Centralized definition of data entities.
  - Clear separation of concerns, with models focusing on data representation and persistence.

#### 1.3. ENUMs

- **Location:** Primarily defined in `src/models/enums.py`.
- **Technology:** Standard Python `enum.Enum`.
- **Structure:**
  - ENUMs inherit from `str` and `enum.Enum` (e.g., `class MyEnum(str, enum.Enum):`). This makes their values string-based, suitable for database storage and API communication.
  - Used to define a set of named constants for specific attributes, ensuring consistency and restricting possible values (e.g., `SitemapAnalysisStatusEnum`, `DomainStatusEnum`).
- **Usage:**
  - Imported and used as types for model fields.
  - Referenced in business logic to check or set statuses, types, etc.

### 2. AI Audit SOPs for Layer 1

#### 2.1. Audit Objectives

- Ensure consistency and correctness of model definitions.
- Verify proper use and definition of ENUMs.
- Identify potential issues related to data integrity, relationships, and naming conventions.
- Assess adherence to architectural guidelines for models and ENUMs.

#### 2.2. Audit Procedures & AI Applications

1.  **Model Structure and Naming Conventions:**

    - **Procedure:**
      - Verify that model class names are singular and PascalCase (e.g., `User`, `JobOrder`).
      - Verify that `__tablename__` is plural and snake_case (e.g., `users`, `job_orders`).
      - Check that column names are snake_case.
      - Ensure primary keys are consistently named (e.g., `id`).
      - Ensure foreign keys follow a consistent pattern (e.g., `related_model_id`).
    - **AI Application:**
      - Use static analysis tools or custom scripts (potentially AI-generated) to parse model files and check adherence to naming conventions.
      - LLMs can be prompted with model code snippets to identify deviations from specified naming conventions.

2.  **Data Type Consistency and Appropriateness:**

    - **Procedure:**
      - Review data types used for each column (`String`, `Integer`, `Boolean`, `DateTime`, `UUID`, `JSONB`, etc.) to ensure they are appropriate for the data they store.
      - Check for consistent use of `UUID` for primary and foreign keys where applicable.
      - Verify that `String` columns have reasonable length constraints if necessary (though often handled by DB or implicitly).
    - **AI Application:**
      - AI tools can analyze patterns of data types across similar models or fields to flag inconsistencies.
      - LLMs can review model definitions and suggest more appropriate data types based on field names and context.

3.  **Relationship Integrity:**

    - **Procedure:**
      - Verify that `ForeignKey` constraints are correctly defined and point to existing tables/columns.
      - Check `relationship` definitions for correctness (e.g., `back_populates` or `backref` correctly specified, correct use of `uselist=False` for one-to-one).
      - Ensure `ondelete` behavior for foreign keys is appropriate (e.g., `CASCADE`, `SET NULL`, `RESTRICT`).
    - **AI Application:**
      - Code analysis scripts (potentially assisted by AI for pattern recognition) can trace relationships and flag potential issues like missing `back_populates` or incorrect configurations.
      - LLMs can analyze relationship definitions and provide an English explanation of the defined relationship, which can then be cross-verified.

4.  **ENUM Definition and Usage:**

    - **Procedure:**
      - Ensure all ENUMs are defined in `src/models/enums.py` or a designated central location.
      - Verify ENUMs inherit from `str` and `enum.Enum`.
      - Check that ENUM members are appropriately named (e.g., uppercase or lowercase based on convention) and have meaningful string values.
      - Ensure ENUMs are used for fields where a limited set of predefined string values is expected.
      - Check for unused or deprecated ENUMs/ENUM members.
    - **AI Application:**
      - Static analysis to find all usages of ENUMs and ensure they are used as field types where appropriate.
      - LLMs can review ENUM definitions for clarity, completeness, and adherence to best practices. They can also help identify ENUMs that could be consolidated or fields that should be converted to use an ENUM.

5.  **Base Model Inheritance and Utilization:**

    - **Procedure:**
      - Confirm all models inherit from the designated base model(s) (e.g., `BaseModel`).
      - Verify that common fields provided by the base model are not unnecessarily re-declared.
      - Check for consistent use of utility methods provided by the base model.
    - **AI Application:**
      - AI-powered code analysis can verify inheritance chains and identify deviations.

6.  **Presence of Docstrings and Comments:**

    - **Procedure:**
      - Ensure models and their non-obvious fields have clear docstrings explaining their purpose.
      - Verify complex relationships or non-standard choices are commented.
    - **AI Application:**
      - LLMs can be used to generate draft docstrings for models and fields based on their names and types, which can then be reviewed by developers.
      - Code analysis tools can flag models/fields missing docstrings.

7.  **Code Duplication in Model Logic:**
    - **Procedure:**
      - Identify any repetitive C.R.U.D. logic or helper methods within models that could be abstracted to base classes or utility functions.
    - **AI Application:**
      - Semantic code similarity tools (some leveraging AI) can help detect duplicated or near-duplicated code blocks across different model files.

#### 2.3. Audit Reporting

- Document all findings, categorizing them by severity (e.g., Critical, High, Medium, Low).
- For each finding, provide:
  - Description of the issue.
  - Location (file and line number).
  - Suggested remediation.
  - Potential impact if not addressed.
- Maintain a summary of audit activities and overall health of Layer 1.

---

<!-- Placeholder for Layer 2 -->

---

<!-- Placeholder for Layer 3 -->

---

<!-- Placeholder for Layer 5 -->

---

<!-- Placeholder for Layer 6 -->

---

<!-- Placeholder for Layer 7 -->
