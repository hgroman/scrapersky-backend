# Layer 3 Fix Pattern: Business Logic in Router

## Pattern Details

*   **Title:** Business Logic in Router
*   **Problem Type:** architecture
*   **Code Type:** router, service
*   **Severity:** HIGH-ARCHITECTURE
*   **Tags:** ["architecture", "business-logic", "service-delegation", "layer-3", "layer-4", "global"]
*   **Layers:** [3, 4]
*   **Workflows:** ["global"]
*   **File Types:** ["py"]
*   **Problem Description:** Router endpoints contain complex business logic, such as direct database queries (SQLAlchemy ORM or raw SQL), data transformations, or complex conditional processing, instead of delegating these operations to Layer 4 services.
*   **Solution Steps:**
    1.  Identify the specific business logic block(s) within the router endpoint function.
    2.  Create or identify the appropriate Layer 4 service file (e.g., `src/services/{workflow_name}_service.py`).
    3.  Create a new method within the Layer 4 service to encapsulate the extracted business logic. This method should accept necessary parameters, including the database session (`AsyncSession`).
    4.  Move the business logic code from the router endpoint to the new service method.
    5.  Update the router endpoint function to call the new Layer 4 service method, passing the database session and any required input data.
    6.  Ensure the router endpoint handles the transaction boundary (`async with session.begin():`) if the service method involves database writes, and the service method uses the provided session without managing its own transaction boundary.
*   **Verification Steps:**
    1.  Verify that the router endpoint no longer contains the extracted business logic.
    2.  Confirm that the new service method correctly encapsulates the logic and uses the provided session.
    3.  Ensure the router endpoint correctly calls the service method and handles the response.
    4.  Run relevant tests or manually test the API endpoint to confirm functionality is preserved and the fix works as expected.
*   **Learnings:**
    1.  Adhering to the layered architecture by delegating business logic to Layer 4 services keeps routers focused on API concerns (request handling, validation, authentication, transaction boundaries).
    2.  Encapsulating logic in services improves code organization, reusability, testability, and maintainability.
*   **Prevention Guidance:** Always create dedicated Layer 4 service methods for any non-trivial business logic. Routers should primarily orchestrate calls to services, not implement the core logic themselves.
*   **Created By:** Architect Persona (Documented by Roo)
*   **Reviewed:** false (Needs formal review)
*   **Description:** Pattern for refactoring router endpoints that incorrectly contain business logic by extracting that logic into dedicated Layer 4 service methods.

## Related Information

*   **Relevant Standards:**
    *   Layer 3 Blueprint (`Docs/Docs_10_Final_Audit/Layer-3.1-Routers_Blueprint.md`) - Section 2.1 (Delegation), Section 2.2.5 (Logic & Delegation)
    *   Layer 4 Services Blueprint (Conceptual/Referenced) - Defines where business logic should reside.
    *   Conventions and Patterns Guide (`Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`) - Reinforces layered architecture.
*   **Related Audit Findings:** Layer 3 Routers Audit Report (`Docs/Docs_10_Final_Audit/Audit Reports Layer 3/Layer3_Routers_Audit_Report.md`) - Section 2.2 (High Severity Gaps - Business Logic in Router), detailed findings for numerous router files.