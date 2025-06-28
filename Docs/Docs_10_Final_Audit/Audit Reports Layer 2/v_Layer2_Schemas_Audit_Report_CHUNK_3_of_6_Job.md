# Layer 2 Schemas Audit Report: Job schemas audit

## 2. File: `src/schemas/job.py`

**Audited on:** 2025-05-20
**Auditor:** Cascade Schema Sentinel

### 2.1. Model: `JobSubmissionResponse`

*   **Principle 1 (Pydantic Usage)**: COMPLIANT.
*   **Principle 2 (File Naming - applies to file)**: COMPLIANT. (`job.py` is singular snake_case in `src/schemas/`)
*   **Principle 3 (Class Naming)**: COMPLIANT. (`JobSubmissionResponse` is PascalCase with clear purpose).
*   **Principle 4 (Base Class Inheritance)**: COMPLIANT. (Inherits from `pydantic.BaseModel`).
*   **Principle 5 (Field Typing)**: COMPLIANT. (`job_id: uuid.UUID`).
*   **Principle 6 (Field Naming)**: COMPLIANT. (`job_id` is snake_case).
*   **Principle 7 (Optional Fields)**: COMPLIANT. (`job_id` is implicitly required).
*   **Principle 8 (Configuration `from_attributes`)**: COMPLIANT / NOT APPLICABLE. (Not an ORM-derived response model requiring `from_attributes`).
*   **Principle 9 (Validator Scope)**: COMPLIANT / NOT APPLICABLE. (No validators present).
*   **Principle 10 (Schema Variations CRUD)**: COMPLIANT. (Specific response type, CRUD pattern not directly applicable).
*   **Principle 11 (ENUM Usage)**: COMPLIANT / NOT APPLICABLE. (No enum fields present).
*   **Principle 12 (Docstrings & Descriptions)**:
    *   Class Docstring: COMPLIANT.
    *   Field `job_id` description: **GAP (Minor)** - Field `job_id` lacks a `description` attribute via `Field(..., description="...")` for enhanced OpenAPI clarity (Blueprint: "Fields can have a `description`...").

### 2.2. Model: `JobStatusResponse`

*   **Principle 1 (Pydantic Usage)**: COMPLIANT.
*   **Principle 3 (Class Naming)**: COMPLIANT. (`JobStatusResponse` is PascalCase with clear purpose, analogous to a `Read` schema).
*   **Principle 4 (Base Class Inheritance)**: COMPLIANT. (Inherits from `pydantic.BaseModel`).
*   **Principle 5 (Field Typing)**: Mostly COMPLIANT. See Principle 11 for `status` field.
    *   All other fields (`job_id`, `progress`, `domain_id`, `created_by`, `result_data`, `error`, `job_metadata`, `created_at`, `updated_at`) have explicit and appropriate types.
*   **Principle 6 (Field Naming)**: COMPLIANT. (All fields are snake_case).
*   **Principle 7 (Optional Fields)**: COMPLIANT. (Appropriate use of `Optional` and defaults).
*   **Principle 8 (Configuration `from_attributes`)**: COMPLIANT. (`class Config: from_attributes = True` is present and correct).
*   **Principle 9 (Validator Scope)**: COMPLIANT / NOT APPLICABLE. (No validators present).
*   **Principle 10 (Schema Variations CRUD)**: COMPLIANT. (Functions as a 'Read' schema for job status).
*   **Principle 11 (ENUM Usage)**:
    *   **GAP (High Priority)**: The `status` field is `str` but should use a Layer 1 Enum (e.g., `TaskStatus` or `JobStatus`). Blueprint Principle 11 mandates use of Layer 1 Enums for controlled vocabularies. Code comments explicitly note this (`# Use the actual Enum type if possible... # status: TaskStatus...`). `<!-- STOP_FOR_REVIEW --> This deviation is explicitly hinted at in the code comments and is a critical point for data integrity and consistency. Failure to use an Enum here directly violates a 'MUST' requirement in the Blueprint.`
*   **Principle 12 (Docstrings & Descriptions)**: COMPLIANT. (Class docstring is present, and all fields have descriptions via `Field(...)`).

---