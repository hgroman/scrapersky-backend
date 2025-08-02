# Layer 3 Fix Pattern: Direct Service Internal Access

## Pattern Details

*   **Title:** Direct Service Internal Access
*   **Problem Type:** architecture
*   **Code Type:** router, service
*   **Severity:** HIGH-ARCHITECTURE
*   **Tags:** ["architecture", "encapsulation", "service-internals", "layer-3", "layer-4"]
*   **Layers:** [3, 4]
*   **Workflows:** ["global"]
*   **File Types:** ["py"]
*   **Problem Description:** Router endpoints directly access or manipulate internal variables or attributes of Layer 4 service instances instead of interacting with the service only through its public methods.
*   **Solution Steps:**
    1.  Identify the code in the router endpoint that directly accesses or modifies a service's internal variable.
    2.  Determine the intended purpose of accessing/modifying this internal state.
    3.  If the service needs to expose this information or functionality, create a new public method in the Layer 4 service that provides controlled access or performs the required operation.
    4.  Update the router endpoint to call the new public service method instead of directly accessing the internal variable.
    5.  If the internal variable was being modified, ensure the new service method handles the state change internally and correctly.
*   **Verification Steps:**
    1.  Verify that the router endpoint no longer directly accesses the service's internal variable.
    2.  Confirm that the new service method (if created) correctly provides the necessary access or functionality.
    3.  Run relevant tests or manually test the API endpoint to ensure functionality is preserved and the fix works as expected, respecting the service's encapsulation.
*   **Learnings:**
    1.  Services should encapsulate their internal state and expose functionality only through well-defined public methods.
    2.  Routers should interact with services solely through their public interfaces to maintain a clear separation of concerns and improve maintainability.
*   **Prevention Guidance:** Never access attributes or variables of a service instance directly from a router. If a service's internal state or functionality is needed, request the service author to expose it via a public method.
*   **Created By:** Architect Persona (Documented by Roo)
*   **Reviewed:** false (Needs formal review)
*   **Description:** Pattern for refactoring router endpoints that violate service encapsulation by directly accessing service internal variables, ensuring interaction occurs only through public service methods.

## Related Information

*   **Relevant Standards:**
    *   Layer 3 Blueprint (`Docs/Docs_10_Final_Audit/Layer-3.1-Routers_Blueprint.md`) - Section 2.2.5 (Logic & Delegation - implies interaction via service interface)
    *   Layer 4 Services Blueprint (Conceptual/Referenced) - Defines service responsibilities and encapsulation.
    *   Conventions and Patterns Guide (`Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md`) - Reinforces layered architecture and encapsulation principles.
*   **Related Audit Findings:** Layer 3 Routers Audit Report (`Docs/Docs_10_Final_Audit/Audit Reports Layer 3/Layer3_Routers_Audit_Report.md`) - Section 2.2 (High Severity Gaps - Direct Internal Variable Access/Manipulation (from Services)), detailed findings for specific router files.