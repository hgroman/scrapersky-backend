# Layer 3 Fix Pattern: Incorrect Pydantic Model Location

## Pattern Details

*   **Title:** Incorrect Pydantic Model Location
*   **Problem Type:** standards
*   **Code Type:** router, schema
*   **Severity:** MEDIUM-STANDARDS
*   **Tags:** ["standards", "pydantic", "schema-management", "layer-2", "layer-3"]
*   **Layers:** [2, 3]
*   **Workflows:** ["global"]
*   **File Types:** ["py"]
*   **Problem Description:** Pydantic request or response models are defined directly within Layer 3 router files (`src/routers/*.py`) or imported from incorrect locations (e.g., `src/models/`) instead of residing in the designated Layer 2 schemas directory (`src/schemas/`).
*   **Solution Steps:**
    1.  Identify the Pydantic model definition(s) located incorrectly within the router file.
    2.  Determine the appropriate location for the model in the Layer 2 schemas directory, following the conventions (e.g., `src/schemas/{workflow_name}.py` for workflow-specific schemas, `src/schemas/{source_table_name}.py` for generic entity schemas).
    3.  Move the Pydantic model definition(s) to the correct Layer 2 schema file.
    4.  Update the import statement(s) in the router file to import the model from its new, correct Layer 2 location.
    5.  Verify that the model is correctly imported and used in the router endpoint definitions (`response_model`, request body type hints).
*   **Verification Steps:**
    1.  Verify the Pydantic model definition is removed from the router file.
    2.  Confirm the model definition is correctly placed in the appropriate Layer 2 schema file.
    3.  Ensure the import statement in the router file is updated and correct.
    4.  Verify the router endpoint(s) still correctly reference the model.
    5.  Run relevant tests or manually test the API endpoint(s) to ensure request validation and response serialization work as expected.
*   **Learnings:**
    1.  Centralizing Pydantic models in Layer 2 (`src/schemas/`) improves modularity, reusability, and maintainability.
    2.  Adhering to schema location conventions ensures a clear separation of concerns between API contracts (Layer 2) and API endpoints (Layer 3).
*   **Prevention Guidance:** Always define Pydantic request and response models in the `src/schemas/` directory, following the established naming and file conventions. Never define Pydantic models directly within router files.
*   **Created By:** Architect Persona (Documented by Roo)
*   **Reviewed:** false (Needs formal review)
*   **Description:** Pattern for refactoring router files by moving incorrectly located Pydantic model definitions to the standard Layer 2 schemas directory.

## Related Information

*   **Relevant Standards:**
    *   Layer 3 Blueprint (`Docs/Docs_10_Final_Audit/Layer-3.1-Routers_Blueprint.md`) - Section 2.2.3 (Response Model), Section 2.2.4 (Request Body/Query Schemas)
    *   Layer 2 Schemas Blueprint (Conceptual/Referenced) - Defines standards for schemas.
    *   Conventions and Patterns Guide (`Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`) - Section 3 (Layer 2: Schemas)
*   **Related Audit Findings:** Layer 3 Routers Audit Report (`Docs/Docs_10_Final_Audit/Audit Reports Layer 3/Layer3_Routers_Audit_Report.md`) - Section 2.3 (Medium Severity Gaps - Incorrect Pydantic Model Location/Definition), detailed findings for numerous router files.