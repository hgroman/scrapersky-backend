# Layer 3 Fix Pattern: Incorrect Transaction Management

## Pattern Details

*   **Title:** Incorrect Transaction Management in Router
*   **Problem Type:** architecture
*   **Code Type:** router, service
*   **Severity:** MEDIUM-ARCHITECTURE
*   **Tags:** ["architecture", "transaction-management", "session-handling", "layer-3", "layer-4"]
*   **Layers:** [3, 4]
*   **Workflows:** ["global"]
*   **File Types:** ["py"]
*   **Problem Description:** Router endpoints incorrectly manage database sessions (e.g., creating sessions directly) or handle transaction boundaries (`session.commit()`, `session.rollback()`) instead of using the standard injected session dependency and `async with session.begin():` for transaction scope. Services might also incorrectly manage transactions.
*   **Solution Steps:**
    1.  Identify where the router endpoint incorrectly creates or manages database sessions/transactions.
    2.  Ensure the endpoint uses the standard injected session dependency (`session: AsyncSession = Depends(get_session_dependency)`).
    3.  Wrap database write operations within the router endpoint with `async with session.begin():` to define the transaction boundary.
    4.  Remove any explicit `session.commit()`, `session.rollback()`, or `session.close()` calls from the router endpoint, as the dependency and `async with` block handle this.
    5.  Verify that Layer 4 service methods accept the session as a parameter and use it without managing their own transaction boundaries.
*   **Verification Steps:**
    1.  Verify the router endpoint uses the standard session dependency.
    2.  Confirm `async with session.begin():` is correctly used for transaction scope in the router.
    3.  Ensure no incorrect session/transaction management calls remain in the router.
    4.  Verify that called service methods correctly use the provided session.
    5.  Run relevant tests or manually test the API endpoint to confirm data persistence and error handling within transactions work as expected.
*   **Learnings:**
    1.  Routers are responsible for initiating and managing the transaction lifecycle using the injected session and `async with session.begin():`.
    2.  Services should be transaction-aware (use the session) but not transaction-creating or managing.
    3.  Using the standard session dependency (`get_session_dependency`) ensures proper session handling and cleanup.
*   **Prevention Guidance:** Always use `Depends(get_session_dependency)` for database sessions in routers. Always wrap database write operations in routers with `async with session.begin():`. Never create sessions or manage transactions (`commit`, `rollback`, `close`) within service methods.
*   **Created By:** Architect Persona (Documented by Roo)
*   **Reviewed:** false (Needs formal review)
*   **Description:** Pattern for correcting incorrect database session and transaction management practices in Layer 3 router endpoints and ensuring proper delegation of session usage to Layer 4 services.

## Related Information

*   **Relevant Standards:**
    *   Layer 3 Blueprint (`Docs/Docs_10_Final_Audit/Layer-3.1-Routers_Blueprint.md`) - Section 1 (Transaction Management), Section 2.2.3.2 (Transaction Management)
    *   Standard Dependency Injection Patterns (`Docs/Docs_1_AI_GUIDES/30-LAYER3_STANDARD_DEPENDENCY_INJECTION_PATTERNS.md`) - Section 1 (Database Session Dependency)
    *   Conventions and Patterns Guide (`Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`) - Reinforces layered architecture and session handling.
*   **Related Audit Findings:** Layer 3 Routers Audit Report (`Docs/Docs_10_Final_Audit/Audit Reports Layer 3/Layer3_Routers_Audit_Report.md`) - Section 2.3 (Medium Severity Gaps - Transaction Management in Router), detailed findings for numerous router files.