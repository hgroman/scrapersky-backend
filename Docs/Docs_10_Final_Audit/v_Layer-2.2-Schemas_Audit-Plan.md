# Layer 2 (Schemas) - Actionable Audit Plan

**Date:** 2025-05-20
**Version:** 1.0
**Author:** AuditPlanArchitect (Cascade)

## Purpose

This document provides a practical, actionable audit plan for Layer 2 (Pydantic Schemas) of the ScraperSky backend. It is organized by schema file, with specific principles to verify for each file. The goal is to systematically identify and address technical debt while ensuring compliance with architectural standards defined in `Layer-2.1-Schemas_Blueprint.md`.

## Layer 2 Audit Principles

Based on the `Layer-2.1-Schemas_Blueprint.md`, `CONVENTIONS_AND_PATTERNS_GUIDE.md`, and Pydantic best practices, these are the key principles to verify for each schema file:

1.  **Pydantic Usage**: Schemas must be Pydantic models, serving as the sole pattern for API contracts.
2.  **File Naming**: Files must be in `src/schemas/` and named `{entity_name}.py` (singular, snake_case).
3.  **Class Naming**: Schema class names must be PascalCase and use `Base`/`Create`/`Update`/`Read` (or similar appropriate suffixes like `Filter`, `Response`) to indicate purpose and follow entity-specific naming (e.g., `UserBase`, `ItemCreate`).
4.  **Base Class Inheritance**: All schema classes must inherit from `pydantic.BaseModel`.
5.  **Field Typing**: All fields within schemas must have explicit Python type hints (e.g., `str`, `int`, `Optional[List[UUID]]`).
6.  **Field Naming**: All field names within schemas must be `snake_case`.
7.  **Optional Fields**: Use `Optional[...]` (or `... | None` in Python 3.10+) for fields that are not strictly required.
8.  **Configuration (`Config` / `model_config`)**: 
    *   Response schemas derived from ORM models (Layer 1) **MUST** include `orm_mode = True` (Pydantic v1) or `from_attributes = True` (Pydantic v2).
    *   Use `alias` or `alias_generator` if API field names must differ from internal Python field names (though `snake_case` is preferred for API consistency if possible).
9.  **Validator Scope**: Pydantic validators (`@validator` / `@field_validator`) should be used sparingly and focus on format/type validation (e.g., email, URL). Complex business logic validation belongs in Layer 4 (Services).
10. **Schema Variations (CRUD Pattern)**: Where applicable for entities involved in CRUD operations, employ the Base/Create/Update/Read inheritance pattern to clearly define data shapes for different operations and minimize redundancy.
11. **ENUM Usage**: Fields representing controlled vocabularies (e.g., status, type) **MUST** use the corresponding `Enum` defined in Layer 1 (`src/models/`). The Enum should be imported and used as the type hint.
12. **Docstrings & Descriptions**: Schema classes should have a clear docstring explaining their purpose. Individual fields can have a `description` in `Field(..., description="...")` to improve clarity for OpenAPI documentation.

## Audit Process

For each file being audited by the Cascade Schema Sentinel persona:

1.  **Open the file** and review its contents.
2.  **Iterate through each Pydantic model class** within the file.
3.  **For each model, check every applicable principle** from the "Layer 2 Audit Principles" list above.
4.  **Document findings** meticulously in `Docs/Docs_10_Final_Audit/Audit Reports Layer 2/Layer2_Schemas_Audit_Report.md`. Documentation for each schema should include:
    *   File Path
    *   Component Name (Schema class name)
    *   Gap Analysis (listing each deviation with specific Blueprint/Principle reference)
    *   Use `<!-- NEED_CLARITY: [question] -->` for ambiguities.
    *   Use `<!-- STOP_FOR_REVIEW -->` for items requiring human judgment.
5.  **No code changes** are to be made by the auditor. Findings are for documentation and later remediation.

### Handling the 200-Line Limitation with AI (Cascade Schema Sentinel)

When Cascade Schema Sentinel is viewing files:

1.  **For files under 200 lines**: Use `view_file` with StartLine=0 and EndLine=200 (or actual end line) to view the entire file.
2.  **For files over 200 lines** (unlikely for most schema files but possible):
    *   **Option 1:** Use multiple `view_file` calls with different line ranges.
    *   **Option 2:** Use `view_code_item` to focus on specific Pydantic model class definitions if their names are known or can be inferred.
3.  **Recommended approach for Layer 2 audit**:
    *   Start with `view_file` for the first 200 lines.
    *   If the file is larger or contains many distinct schemas, use `view_code_item` for each specific Pydantic model class to ensure focused review against the principles.
    *   Document line ranges or specific items viewed to ensure complete coverage.

## Technical Debt Resolution Priority (General Guidance)

1.  **High Priority**: 
    *   Incorrect `orm_mode`/`from_attributes` settings leading to runtime errors or incorrect data serialization.
    *   Missing or incorrect Layer 1 ENUM usage leading to data inconsistency.
    *   Grossly incorrect field typing.
    *   Security-sensitive information inappropriately exposed in response schemas.
2.  **Medium Priority**: 
    *   Failure to use Base/Create/Update/Read patterns where clearly applicable, leading to redundancy or ambiguity.
    *   Inconsistent naming conventions (file, class, field).
    *   Validators performing business logic.
3.  **Low Priority**: 
    *   Missing docstrings or field descriptions (unless leading to significant ambiguity).
    *   Minor deviations in optionality or default values if not causing immediate issues.

## Next Steps After Layer 2 Audit

After the Cascade Schema Sentinel completes the Layer 2 audit and populates `Layer2_Schemas_Audit_Report.md`:

1.  **Review the Audit Report**: Human review of findings, particularly `NEED_CLARITY` and `STOP_FOR_REVIEW` tags.
2.  **Create Remediation Plan**: Develop `Layer-2.5-Schemas_Remediation_Planning.md` detailing tasks, priorities, and assignments for addressing identified technical debt.
3.  **Implement Fixes**: Execute the remediation plan.
4.  **Update Workflow Cheat Sheets**: Ensure relevant findings and fixes are reflected in `WFn-WorkflowName_Cheat_Sheet.md` documents.
5.  **Proceed to Next Layer Audit** (e.g., Layer 3 - Routers).

## Audit Checklist by Schema File

This section lists the schema files to be audited. For each file, and for each Pydantic model within that file, all principles from the "Layer 2 Audit Principles" section must be checked.

### 1. `src/schemas/email_scan.py`

*   **File Audited:** [ ]
*   **Models within file (list them as identified):**
    *   Schema Name: `[ModelName]` - Audited: [ ]
        *   Principle 1 (Pydantic Usage): [ ]
        *   Principle 2 (File Naming - *applies to file*): [ ]
        *   Principle 3 (Class Naming): [ ]
        *   Principle 4 (Base Class): [ ]
        *   Principle 5 (Field Typing): [ ]
        *   Principle 6 (Field Naming): [ ]
        *   Principle 7 (Optional Fields): [ ]
        *   Principle 8 (Config `from_attributes`): [ ]
        *   Principle 9 (Validator Scope): [ ]
        *   Principle 10 (Schema Variations): [ ]
        *   Principle 11 (ENUM Usage): [ ]
        *   Principle 12 (Docstrings): [ ]
*   **Overall File Findings:**

### 2. `src/schemas/job.py`

*   **File Audited:** [ ]
*   **Models within file (list them as identified):**
    *   Schema Name: `[ModelName]` - Audited: [ ]
        *   (Repeat checklist for principles 1, 3-12 for each model)
*   **Overall File Findings:**

### 3. `src/schemas/page_curation.py`

*   **File Audited:** [ ]
*   **Models within file (list them as identified):**
    *   Schema Name: `[ModelName]` - Audited: [ ]
        *   (Repeat checklist for principles 1, 3-12 for each model)
*   **Overall File Findings:**

### 4. `src/schemas/sitemap_file.py`

*   **File Audited:** [ ]
*   **Models within file (list them as identified):**
    *   Schema Name: `[ModelName]` - Audited: [ ]
        *   (Repeat checklist for principles 1, 3-12 for each model)
*   **Overall File Findings:**

---

## References

-   `Docs/Docs_10_Final_Audit/Layer-2.1-Schemas_Blueprint.md`
-   `Docs/Docs_10_Final_Audit/Layer-2.3-Schemas_AI_Audit_SOP.md`
-   `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
-   `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
-   `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`

