# Layer 3 Fix Pattern: Standardize Response Models

## Pattern Details

*   **Title:** Standardize Response Models
*   **Problem Type:** standards
*   **Code Type:** router, schema
*   **Severity:** MEDIUM-STANDARDS (Can be High depending on data sensitivity)
*   **Tags:** ["standards", "pydantic", "response-model", "api-design", "layer-2", "layer-3"]
*   **Layers:** [2, 3]
*   **Workflows:** ["global"]
*   **File Types:** ["py"]
*   **Problem Description:** API endpoints use generic types like `Dict[str, Any]` or `List[Dict[str, Any]]`, or use SQLAlchemy ORM models directly as `response_model`, instead of defining and using explicit Pydantic models from Layer 2 (`src/schemas/`). This leads to poor API documentation (OpenAPI schema) and lack of clear data contracts.
*   **Solution Steps:**
    1.  Identify the endpoint(s) using a generic type or ORM model for `response_model`.
    2.  Determine the required structure of the response data.
    3.  Create a new, explicit Pydantic model in the appropriate Layer 2 schema file (`src/schemas/`), following naming conventions (e.g., `{Entity}Read`, `{Workflow}Response`).
    4.  Update the endpoint definition(s) in the router file to use the new Layer 2 Pydantic model in the `response_model` argument of the `@router.<method>` decorator.
    5.  Ensure the data returned by the endpoint handler function conforms to the structure of the new Pydantic response model.
*   **Verification Steps:**
    1.  Verify the endpoint decorator now uses the explicit Layer 2 Pydantic model for `response_model`.
    2.  Check the generated OpenAPI documentation (e.g., `/docs` or `/redoc`) to confirm the response schema for the endpoint is now detailed and correct.
    3.  Run relevant tests or manually test the API endpoint to ensure the response data is correctly serialized according to the new model.
*   **Learnings:**
    1.  Using explicit Pydantic models for `response_model` provides clear API contracts, improves documentation, and enables automatic data serialization and validation by FastAPI.
    2.  SQLAlchemy ORM models should not be used directly as API response models; dedicated Pydantic schemas provide better separation of concerns and control over the API surface.
*   **Prevention Guidance:** Always define and use explicit Pydantic models from Layer 2 (`src/schemas/`) for API response models. Never use generic types (`dict`, `list`) or SQLAlchemy ORM models directly for `response_model`.
*   **Created By:** Architect Persona (Documented by Roo)
*   **Reviewed:** false (Needs formal review)
*   **Description:** Pattern for standardizing API response models by replacing generic types or ORM models with explicit Pydantic models from the Layer 2 schemas directory.

## Related Information

*   **Relevant Standards:**
    *   Layer 3 Blueprint (`Docs/Docs_10_Final_Audit/Layer-3.1-Routers_Blueprint.md`) - Section 2.2.3 (Response Model)
    *   Layer 2 Schemas Blueprint (Conceptual/Referenced) - Defines standards for schemas.
    *   API Standardization Guide (`Docs/Docs_1_AI_GUIDES/15-LAYER3_API_STANDARDIZATION_GUIDE.md`) - Section 2 (Response Structure Standardization)
    *   Conventions and Patterns Guide (`Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md`) - Section 3 (Layer 2: Schemas)
*   **Related Audit Findings:** Layer 3 Routers Audit Report (`Docs/Docs_10_Final_Audit/Audit Reports Layer 3/Layer3_Routers_Audit_Report.md`) - Section 2.3 (Medium Severity Gaps - Generic `dict` or Missing Explicit Response Models, Using ORM Model as Response Model), detailed findings for numerous router files.