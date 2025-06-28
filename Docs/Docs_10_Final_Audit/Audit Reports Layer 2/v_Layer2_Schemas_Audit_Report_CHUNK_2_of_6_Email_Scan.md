# Layer 2 Schemas Audit Report: Email scan schemas audit

## 1. File: `src/schemas/email_scan.py`

**Audited on:** 2025-05-20
**Auditor:** Cascade Schema Sentinel

### 1.1. Model: `EmailScanRequest`

*   **Principle 1 (Pydantic Usage)**: COMPLIANT.
*   **Principle 2 (File Naming - applies to file)**: COMPLIANT. (`email_scan.py` is singular snake_case in `src/schemas/`)
*   **Principle 3 (Class Naming)**: COMPLIANT. (`EmailScanRequest` is PascalCase with a clear 'Request' suffix indicating purpose).
*   **Principle 4 (Base Class Inheritance)**: COMPLIANT. (Inherits from `pydantic.BaseModel`).
*   **Principle 5 (Field Typing)**: COMPLIANT. (`domain_id: uuid.UUID`).
*   **Principle 6 (Field Naming)**: COMPLIANT. (`domain_id` is snake_case).
*   **Principle 7 (Optional Fields)**: COMPLIANT. (`domain_id` is implicitly required).
*   **Principle 8 (Configuration `from_attributes`)**: COMPLIANT / NOT APPLICABLE. (Not a response model from ORM).
*   **Principle 9 (Validator Scope)**: COMPLIANT / NOT APPLICABLE. (No validators present).
*   **Principle 10 (Schema Variations CRUD)**: COMPLIANT. (Appropriate for a specific action request; full CRUD pattern not applicable here).
*   **Principle 11 (ENUM Usage)**: COMPLIANT / NOT APPLICABLE. (No enum fields present).
*   **Principle 12 (Docstrings & Descriptions)**:
    *   Class Docstring: COMPLIANT.
    *   Field `domain_id` description: **GAP (Minor)** - Field `domain_id` lacks a `description` attribute via `Field(..., description="...")` for enhanced OpenAPI clarity (Blueprint: "Fields can have a `description`...").

---