# Report of Filename Standardization

**Date Created:** 2024-05-16
**Version:** 1.0
**Status:** Completed
**Assigned To:** AI Assistant
**Requestor:** Quarterback

**Summary:**
The following report details the analysis of each Markdown file in `Docs/Docs_1_AI_GUIDES/`, the determined primary architectural layer, a brief justification, the proposed new filename, and the `git mv` command for renaming. Files flagged for human review are noted.

The 7-Layer Architecture is defined as:

- Layer 1: Models & ENUMs
- Layer 2: Schemas
- Layer 3: Routers
- Layer 4: Services & Schedulers
- Layer 5: Configuration
- Layer 6: UI Components
- Layer 7: Testing

---

**File Analysis and Renaming Proposals:**

1.  **Original Filename:** `07-DATABASE_CONNECTION_STANDARDS.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide details the configuration and standards for database connectivity, pooling, and session management, which are foundational configuration aspects of the application.
    - **Proposed New Filename:** `07-LAYER5_DATABASE_CONNECTION_STANDARDS.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md" "Docs/Docs_1_AI_GUIDES/07-LAYER5_DATABASE_CONNECTION_STANDARDS.md"`

2.  **Original Filename:** `32-PRODUCER_CONSUMER_WORKFLOW_PATTERN.md`

    - **Determined Layer:** Layer 4
    - **Justification:** The guide defines a workflow pattern primarily implemented and driven by background services and schedulers, which manage the staged processing of data.
    - **Proposed New Filename:** `32-LAYER4_PRODUCER_CONSUMER_WORKFLOW_PATTERN.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/32-PRODUCER_CONSUMER_WORKFLOW_PATTERN.md" "Docs/Docs_1_AI_GUIDES/32-LAYER4_PRODUCER_CONSUMER_WORKFLOW_PATTERN.md"`

3.  **Original Filename:** `08-RBAC_SYSTEM_SIMPLIFIED.md`

    - **Determined Layer:** Layer 3
    - **Justification:** The guide describes the current JWT-based authentication system and its direct implementation and usage within API routers.
    - **Proposed New Filename:** `08-LAYER3_RBAC_SYSTEM_SIMPLIFIED.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/08-RBAC_SYSTEM_SIMPLIFIED.md" "Docs/Docs_1_AI_GUIDES/08-LAYER3_RBAC_SYSTEM_SIMPLIFIED.md"`

4.  **Original Filename:** `09-TENANT_ISOLATION_REMOVED.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide explains the removal of tenant isolation, which fundamentally changes data modeling and database interactions by removing `tenant_id` fields and related filtering, directly impacting Layer 1.
    - **Proposed New Filename:** `09-LAYER1_TENANT_ISOLATION_REMOVED.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/09-TENANT_ISOLATION_REMOVED.md" "Docs/Docs_1_AI_GUIDES/09-LAYER1_TENANT_ISOLATION_REMOVED.md"`

5.  **Original Filename:** `12-STRUCTURAL_CHANGES_SUMMARY.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide summarizes major architectural changes and current structural patterns, effectively describing the overall "configured" state and conventions of the application architecture.
    - **Proposed New Filename:** `12-LAYER5_STRUCTURAL_CHANGES_SUMMARY.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/12-STRUCTURAL_CHANGES_SUMMARY.md" "Docs/Docs_1_AI_GUIDES/12-LAYER5_STRUCTURAL_CHANGES_SUMMARY.md"`

6.  **Original Filename:** `25-SQLALCHEMY_MODEL_INTEGRITY_GUIDE.md`

    - **Determined Layer:** Layer 1 (Tentative, based on filename)
    - **Justification:** The filename suggests a focus on SQLAlchemy models (Layer 1). However, the file is empty, so content analysis is not possible. **Flagged for Human Review.**
    - **Proposed New Filename:** `25-LAYER1_SQLALCHEMY_MODEL_INTEGRITY_GUIDE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/25-SQLALCHEMY_MODEL_INTEGRITY_GUIDE.md" "Docs/Docs_1_AI_GUIDES/25-LAYER1_SQLALCHEMY_MODEL_INTEGRITY_GUIDE.md"`

7.  **Original Filename:** `MODULE_SPECIFIC_PROMPTS.md`

    - **Determined Layer:** Layer 5 (Tentative)
    - **Justification:** The guide provides prompt templates for AI-assisted development across various modules, acting as a configuration/guidance tool for the development process. **Flagged for Human Review due to outdated content and ambiguity of layer assignment.**
    - **Proposed New Filename:** `LAYER5_MODULE_SPECIFIC_PROMPTS.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/MODULE_SPECIFIC_PROMPTS.md" "Docs/Docs_1_AI_GUIDES/LAYER5_MODULE_SPECIFIC_PROMPTS.md"`

8.  **Original Filename:** `04-SIMPLIFICATION_OPPORTUNITIES.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide proposes multiple simplification opportunities, with the "Standardized Database Repositories" pattern being a significant proposal for Layer 1 (Models & ENUMs), the lowest layer detailed with a pattern. **Flagged for Human Review due to outdated content (references to tenant isolation).**
    - **Proposed New Filename:** `04-LAYER1_SIMPLIFICATION_OPPORTUNITIES.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/04-SIMPLIFICATION_OPPORTUNITIES.md" "Docs/Docs_1_AI_GUIDES/04-LAYER1_SIMPLIFICATION_OPPORTUNITIES.md"`

9.  **Original Filename:** `05-IMMEDIATE_ACTION_PLAN.md`

    - **Determined Layer:** Layer 7
    - **Justification:** The guide's primary prescriptive content focuses on establishing standardized testing approaches, test templates, and database integrity checks, all of which fall under Layer 7 (Testing). **Flagged for Human Review due to outdated content (references to RBAC and tenant isolation).**
    - **Proposed New Filename:** `05-LAYER7_IMMEDIATE_ACTION_PLAN.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/05-IMMEDIATE_ACTION_PLAN.md" "Docs/Docs_1_AI_GUIDES/05-LAYER7_IMMEDIATE_ACTION_PLAN.md"`

10. **Original Filename:** `06-COMPREHENSIVE_TEST_PLAN.md`

    - **Determined Layer:** Layer 7
    - **Justification:** The guide is a comprehensive test plan with detailed testing strategies and code examples for various application components, directly aligning with Layer 7 (Testing). **Flagged for Human Review due to outdated content (references to tenant isolation).**
    - **Proposed New Filename:** `06-LAYER7_COMPREHENSIVE_TEST_PLAN.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/06-COMPREHENSIVE_TEST_PLAN.md" "Docs/Docs_1_AI_GUIDES/06-LAYER7_COMPREHENSIVE_TEST_PLAN.md"`

11. **Original Filename:** `03-AI_MANAGEMENT_STRATEGY.md`

    - **Determined Layer:** Layer 5 (Tentative)
    - **Justification:** The guide outlines a strategy for AI-assisted development, which could be broadly seen as configuring the development process. **Flagged for Human Review due to ambiguity of layer assignment and outdated content.**
    - **Proposed New Filename:** `03-LAYER5_AI_MANAGEMENT_STRATEGY.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/03-AI_MANAGEMENT_STRATEGY.md" "Docs/Docs_1_AI_GUIDES/03-LAYER5_AI_MANAGEMENT_STRATEGY.md"`

12. **Original Filename:** `31.3-MCP-TROUBLESHOOTING.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide focuses on troubleshooting database migration processes and tools (Supabase MCP), which are used to define and modify the database schema, directly impacting Layer 1 (Models & ENUMs). It includes examples of schema changes and corresponding model updates.
    - **Proposed New Filename:** `31.3-LAYER1_MCP-TROUBLESHOOTING.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/31.3-MCP-TROUBLESHOOTING.md" "Docs/Docs_1_AI_GUIDES/31.3-LAYER1_MCP-TROUBLESHOOTING.md"`

13. **Original Filename:** `31.2-MCP-MIGRATION-EXAMPLE.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide provides a specific example of a database schema migration, including SQL and SQLAlchemy model creation, directly pertaining to Layer 1 (Models & ENUMs). **Flagged for Human Review due to outdated content (references to tenant isolation and RLS).**
    - **Proposed New Filename:** `31.2-LAYER1_MCP-MIGRATION-EXAMPLE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/31.2-MCP-MIGRATION-EXAMPLE.md" "Docs/Docs_1_AI_GUIDES/31.2-LAYER1_MCP-MIGRATION-EXAMPLE.md"`

14. **Original Filename:** `31.1-MCP-MIGRATION-GUIDE.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide explains the use of Supabase MCP for database schema management, a process that directly defines and modifies Layer 1 (Models & ENUMs). **Flagged for Human Review due to outdated content (references to tenant isolation and RLS).**
    - **Proposed New Filename:** `31.1-LAYER1_MCP-MIGRATION-GUIDE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/31.1-MCP-MIGRATION-GUIDE.md" "Docs/Docs_1_AI_GUIDES/31.1-LAYER1_MCP-MIGRATION-GUIDE.md"`

15. **Original Filename:** `30-STANDARD_DEPENDENCY_INJECTION_PATTERNS.md`

    - **Determined Layer:** Layer 3
    - **Justification:** The guide specifies the standard pattern for injecting database sessions into FastAPI router endpoints, which is a convention for Layer 3 (Routers).
    - **Proposed New Filename:** `30-LAYER3_STANDARD_DEPENDENCY_INJECTION_PATTERNS.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/30-STANDARD_DEPENDENCY_INJECTION_PATTERNS.md" "Docs/Docs_1_AI_GUIDES/30-LAYER3_STANDARD_DEPENDENCY_INJECTION_PATTERNS.md"`

16. **Original Filename:** `33-BACKGROUND_SERVICES_ARCHITECTURE.md`

    - **Determined Layer:** Layer 4
    - **Justification:** The guide provides an exhaustive description of the background services and scheduling architecture, which are key components of Layer 4.
    - **Proposed New Filename:** `33-LAYER4_BACKGROUND_SERVICES_ARCHITECTURE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/33-BACKGROUND_SERVICES_ARCHITECTURE.md" "Docs/Docs_1_AI_GUIDES/33-LAYER4_BACKGROUND_SERVICES_ARCHITECTURE.md"`

17. **Original Filename:** `00-Developer-Guides.md`

    - **Determined Layer:** Layer 5 (Highly Tentative)
    - **Justification:** The file is an index for other developer guides. Assigning an application architectural layer is ambiguous. Tentatively categorized under Layer 5 as broadly representing documentation organization/configuration. **Flagged for Human Review to determine appropriate classification for index/meta files.**
    - **Proposed New Filename:** `00-LAYER5_Developer-Guides.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/00-Developer-Guides.md" "Docs/Docs_1_AI_GUIDES/00-LAYER5_Developer-Guides.md"`

18. **Original Filename:** `29-DATABASE_ENUM_ISOLATION.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide provides critical advice on the pattern for defining database ENUM types to ensure isolation and prevent refactoring issues, directly pertaining to data modeling practices in Layer 1.
    - **Proposed New Filename:** `29-LAYER1_DATABASE_ENUM_ISOLATION.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/29-DATABASE_ENUM_ISOLATION.md" "Docs/Docs_1_AI_GUIDES/29-LAYER1_DATABASE_ENUM_ISOLATION.md"`

19. **Original Filename:** `24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md`

    - **Determined Layer:** Layer 4
    - **Justification:** The guide details the process for integrating new background tasks with the shared scheduler, which is a fundamental aspect of Layer 4 (Services & Schedulers).
    - **Proposed New Filename:** `24-LAYER4_SHARED_SCHEDULER_INTEGRATION_GUIDE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md" "Docs/Docs_1_AI_GUIDES/24-LAYER4_SHARED_SCHEDULER_INTEGRATION_GUIDE.md"`

20. **Original Filename:** `28-SCHEDULER_AND_SETTINGS_PATTERNS.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide provides critical patterns for application-wide settings import and usage (Layer 5), and also for scheduler registration which utilizes these settings. The settings pattern is a foundational aspect of configuration.
    - **Proposed New Filename:** `28-LAYER5_SCHEDULER_AND_SETTINGS_PATTERNS.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/28-SCHEDULER_AND_SETTINGS_PATTERNS.md" "Docs/Docs_1_AI_GUIDES/28-LAYER5_SCHEDULER_AND_SETTINGS_PATTERNS.md"`

21. **Original Filename:** `21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md`

    - **Determined Layer:** Layer 4
    - **Justification:** The guide details the patterns for creating and managing scheduled tasks using APScheduler, including their internal logic, database interactions, and integration, all of which are key aspects of Layer 4 (Services & Schedulers).
    - **Proposed New Filename:** `21-LAYER4_SCHEDULED_TASKS_APSCHEDULER_PATTERN.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md" "Docs/Docs_1_AI_GUIDES/21-LAYER4_SCHEDULED_TASKS_APSCHEDULER_PATTERN.md"`

22. **Original Filename:** `22-TESTING_CONVENTIONS_GUIDE.md`

    - **Determined Layer:** Layer 7
    - **Justification:** The guide provides conventions and setup instructions for automated testing, which is the definition of Layer 7 (Testing). **Flagged for Human Review due to its age and potential outdated references (e.g., `DEFAULT_TENANT_ID`) in light of architectural changes.**
    - **Proposed New Filename:** `22-LAYER7_TESTING_CONVENTIONS_GUIDE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/22-TESTING_CONVENTIONS_GUIDE.md" "Docs/Docs_1_AI_GUIDES/22-LAYER7_TESTING_CONVENTIONS_GUIDE.md"`

23. **Original Filename:** `11-Runtime-Import-Tracing.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide describes a runtime import tracing utility, which is a configurable diagnostic tool integrated into the application's startup and lifecycle, aiding in understanding the runtime environment. This aligns with Layer 5 (Configuration).
    - **Proposed New Filename:** `11-LAYER5_Runtime-Import-Tracing.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/11-Runtime-Import-Tracing.md" "Docs/Docs_1_AI_GUIDES/11-LAYER5_Runtime-Import-Tracing.md"`

24. **Original Filename:** `27-ENUM_HANDLING_STANDARDS.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide provides comprehensive standards for defining and managing ENUMs, especially at the database and SQLAlchemy model level, which is a core concern of Layer 1 (Models & ENUMs).
    - **Proposed New Filename:** `27-LAYER1_ENUM_HANDLING_STANDARDS.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md" "Docs/Docs_1_AI_GUIDES/27-LAYER1_ENUM_HANDLING_STANDARDS.md"`

25. **Original Filename:** `26-Supplemental.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide is a debugging cheat sheet that frequently traces issues back to mismatches and problems with database schemas, SQLAlchemy models, and Enum definitions, making Layer 1 (Models & ENUMs) the most impacted fundamental layer in its examples.
    - **Proposed New Filename:** `26-LAYER1_Supplemental_Debugging_Cheat_Sheet.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/26-Supplemental.md" "Docs/Docs_1_AI_GUIDES/26-LAYER1_Supplemental_Debugging_Cheat_Sheet.md"`

26. **Original Filename:** `15-API_STANDARDIZATION_GUIDE.md`

    - **Determined Layer:** Layer 3
    - **Justification:** The guide establishes standards for API versioning, URL structure, request/response formats, status endpoints, and error handling, all of which are key aspects of defining the API contract at Layer 3 (Routers).
    - **Proposed New Filename:** `15-LAYER3_API_STANDARDIZATION_GUIDE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md" "Docs/Docs_1_AI_GUIDES/15-LAYER3_API_STANDARDIZATION_GUIDE.md"`

27. **Original Filename:** `00-INDEX.md`

    - **Determined Layer:** Layer 5 (Highly Tentative)
    - **Justification:** The file is a master index for all AI guides, serving an organizational and navigational purpose for project documentation. Assigning an application architectural layer is ambiguous. Tentatively categorized under Layer 5 as broadly representing documentation structure and project guidance configuration. **Flagged for Human Review to determine appropriate classification for index/meta files.**
    - **Proposed New Filename:** `00-LAYER5_AI_GUIDE_INDEX.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/00-INDEX.md" "Docs/Docs_1_AI_GUIDES/00-LAYER5_AI_GUIDE_INDEX.md"`

28. **Original Filename:** `13-TRANSACTION_MANAGEMENT_GUIDE.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide defines critical, application-wide patterns for database transaction management, specifying how sessions are used and transactions are controlled by routers, services, and background tasks. This is a core aspect of the application's operational configuration for database interactions.
    - **Proposed New Filename:** `13-LAYER5_TRANSACTION_MANAGEMENT_GUIDE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md" "Docs/Docs_1_AI_GUIDES/13-LAYER5_TRANSACTION_MANAGEMENT_GUIDE.md"`

29. **Original Filename:** `23-FASTAPI_ROUTER_PREFIX_CONVENTION.md`

    - **Determined Layer:** Layer 3
    - **Justification:** The guide specifies the convention for defining and including FastAPI router prefixes in `main.py` to ensure correct API endpoint URL construction, directly pertaining to Layer 3 (Routers).
    - **Proposed New Filename:** `23-LAYER3_FASTAPI_ROUTER_PREFIX_CONVENTION.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/23-FASTAPI_ROUTER_PREFIX_CONVENTION.md" "Docs/Docs_1_AI_GUIDES/23-LAYER3_FASTAPI_ROUTER_PREFIX_CONVENTION.md"`

30. **Original Filename:** `PYTHON_PATH_TROUBLESHOOTING.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide addresses local development environment setup, specifically Python path configuration to resolve import errors. This is a form of environment configuration necessary for running and developing the application.
    - **Proposed New Filename:** `LAYER5_PYTHON_PATH_TROUBLESHOOTING.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/PYTHON_PATH_TROUBLESHOOTING.md" "Docs/Docs_1_AI_GUIDES/LAYER5_PYTHON_PATH_TROUBLESHOOTING.md"`

31. **Original Filename:** `01-ABSOLUTE_ORM_REQUIREMENT.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide mandates the exclusive use of SQLAlchemy ORM for all database operations, a core principle governing how Layer 1 (Models & ENUMs) is interacted with.
    - **Proposed New Filename:** `01-LAYER1_ABSOLUTE_ORM_REQUIREMENT.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md" "Docs/Docs_1_AI_GUIDES/01-LAYER1_ABSOLUTE_ORM_REQUIREMENT.md"`

32. **Original Filename:** `20-DATABASE_CONNECTION_ASYNCPG_COMPATIBILITY.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide details the architecture and configuration for database connections, particularly for background tasks, to ensure compatibility with `asyncpg` and Supavisor. This defines a core part of the application's connection management configuration.
    - **Proposed New Filename:** `20-LAYER5_DATABASE_CONNECTION_ASYNCPG_COMPATIBILITY.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/20-DATABASE_CONNECTION_ASYNCPG_COMPATIBILITY.md" "Docs/Docs_1_AI_GUIDES/20-LAYER5_DATABASE_CONNECTION_ASYNCPG_COMPATIBILITY.md"`

33. **Original Filename:** `02-ARCHITECTURE_QUICK_REFERENCE.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide provides a quick reference to the overall application architecture, summarizing key patterns, conventions, and configurations across various components (database, auth, APIs, deployment), making it a Layer 5 (Configuration) document.
    - **Proposed New Filename:** `02-LAYER5_ARCHITECTURE_QUICK_REFERENCE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/02-ARCHITECTURE_QUICK_REFERENCE.md" "Docs/Docs_1_AI_GUIDES/02-LAYER5_ARCHITECTURE_QUICK_REFERENCE.md"`

34. **Original Filename:** `17-CORE_ARCHITECTURAL_PRINCIPLES.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide outlines core architectural principles that define the overall established patterns, conventions, and "configured" way of building various components of the application, making it a Layer 5 (Configuration) document.
    - **Proposed New Filename:** `17-LAYER5_CORE_ARCHITECTURAL_PRINCIPLES.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md" "Docs/Docs_1_AI_GUIDES/17-LAYER5_CORE_ARCHITECTURAL_PRINCIPLES.md"`

35. **Original Filename:** `19-DEVELOPMENT_USER_UUID_STANDARDIZATION.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide standardizes the format and value of development user UUIDs to prevent database foreign key violations, directly impacting data integrity within Layer 1 (Models & ENUMs). **Flagged for Human Review due to potential outdated reference (`DEFAULT_TENANT_ID`).**
    - **Proposed New Filename:** `19-LAYER1_DEVELOPMENT_USER_UUID_STANDARDIZATION.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/19-DEVELOPMENT_USER_UUID_STANDARDIZATION.md" "Docs/Docs_1_AI_GUIDES/19-LAYER1_DEVELOPMENT_USER_UUID_STANDARDIZATION.md"`

36. **Original Filename:** `14-GOOGLE_MAPS_API_EXEMPLAR.md`

    - **Determined Layer:** Layer 5
    - **Justification:** The guide presents the Google Maps API implementation as an exemplar of how various architectural layers (Routers, Services, Models, Schedulers) should be correctly integrated and configured, making it a Layer 5 (Configuration) reference.
    - **Proposed New Filename:** `14-LAYER5_GOOGLE_MAPS_API_EXEMPLAR.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/14-GOOGLE_MAPS_API_EXEMPLAR.md" "Docs/Docs_1_AI_GUIDES/14-LAYER5_GOOGLE_MAPS_API_EXEMPLAR.md"`

37. **Original Filename:** `18-DATABASE_SCHEMA_CHANGE_GUIDE.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide details procedures and patterns for making database schema changes and ensuring SQLAlchemy models are updated accordingly, which is a core responsibility related to Layer 1 (Models & ENUMs).
    - **Proposed New Filename:** `18-LAYER1_DATABASE_SCHEMA_CHANGE_GUIDE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/18-DATABASE_SCHEMA_CHANGE_GUIDE.md" "Docs/Docs_1_AI_GUIDES/18-LAYER1_DATABASE_SCHEMA_CHANGE_GUIDE.md"`

38. **Original Filename:** `16-UUID_STANDARDIZATION_GUIDE.md`

    - **Determined Layer:** Layer 1
    - **Justification:** The guide standardizes the format, storage, and handling of UUIDs, which are fundamental data types for identifiers in database models and schemas, directly pertaining to Layer 1 (Models & ENUMs).
    - **Proposed New Filename:** `16-LAYER1_UUID_STANDARDIZATION_GUIDE.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/16-UUID_STANDARDIZATION_GUIDE.md" "Docs/Docs_1_AI_GUIDES/16-LAYER1_UUID_STANDARDIZATION_GUIDE.md"`

39. **Original Filename:** `11-AUTHENTICATION_BOUNDARY.md`

    - **Determined Layer:** Layer 3
    - **Justification:** The guide defines that JWT authentication occurs exclusively at the API router level, making services auth-agnostic. This is a primary convention for Layer 3 (Routers). **Flagged for Human Review due to outdated content (references to `DEFAULT_TENANT_ID` and the specific dev admin UUID).**
    - **Proposed New Filename:** `11-LAYER3_AUTHENTICATION_BOUNDARY.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md" "Docs/Docs_1_AI_GUIDES/11-LAYER3_AUTHENTICATION_BOUNDARY.md"`

40. **Original Filename:** `10-TEST_USER_INFORMATION.md`

    - **Determined Layer:** Layer 7
    - **Justification:** The guide provides information about test user accounts and how to use them for various testing scenarios, directly supporting Layer 7 (Testing). **Flagged for Human Review due to significant outdated content (references to RBAC and tenant isolation).**
    - **Proposed New Filename:** `10-LAYER7_TEST_USER_INFORMATION.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/10-TEST_USER_INFORMATION.md" "Docs/Docs_1_AI_GUIDES/10-LAYER7_TEST_USER_INFORMATION.md"`

41. **Original Filename:** `History.md`
    - **Determined Layer:** Layer 5 (Highly Tentative)
    - **Justification:** The file describes the historical evolution of the project's architecture, providing context for current patterns. Assigning an application architectural layer is ambiguous. Tentatively categorized under Layer 5 as broadly representing the configured understanding of the project's development history. **Flagged for Human Review to determine appropriate classification for historical/meta files.**
    - **Proposed New Filename:** `LAYER5_PROJECT_HISTORY.md`
    - **`git mv` command:** `git mv "Docs/Docs_1_AI_GUIDES/History.md" "Docs/Docs_1_AI_GUIDES/LAYER5_PROJECT_HISTORY.md"`

---

**Files Flagged for Human Review:**

The following files have been flagged for human review due to ambiguity in layer assignment, outdated content, or being empty:

1.  `25-SQLALCHEMY_MODEL_INTEGRITY_GUIDE.md` (Empty file)
2.  `MODULE_SPECIFIC_PROMPTS.md` (Outdated content: references removed RBAC/tenant isolation; Ambiguous layer assignment)
3.  `04-SIMPLIFICATION_OPPORTUNITIES.md` (Outdated content: references tenant isolation)
4.  `05-IMMEDIATE_ACTION_PLAN.md` (Outdated content: references RBAC/tenant isolation)
5.  `06-COMPREHENSIVE_TEST_PLAN.md` (Outdated content: references tenant isolation)
6.  `03-AI_MANAGEMENT_STRATEGY.md` (Outdated content: references removed RBAC/tenant isolation; Ambiguous layer assignment)
7.  `31.2-MCP-MIGRATION-EXAMPLE.md` (Outdated content: references tenant isolation and RLS)
8.  `31.1-MCP-MIGRATION-GUIDE.md` (Outdated content: references tenant isolation and RLS)
9.  `00-Developer-Guides.md` (Ambiguous layer assignment: index file)
10. `22-TESTING_CONVENTIONS_GUIDE.md` (Outdated content: potential reference to `DEFAULT_TENANT_ID` which may be outdated)
11. `00-INDEX.md` (Ambiguous layer assignment: master index file)
12. `19-DEVELOPMENT_USER_UUID_STANDARDIZATION.md` (Outdated content: potential reference to `DEFAULT_TENANT_ID`)
13. `11-AUTHENTICATION_BOUNDARY.md` (Outdated content: references `DEFAULT_TENANT_ID` and specific dev admin UUID that was changed)
14. `10-TEST_USER_INFORMATION.md` (Significant outdated content: references RBAC and tenant isolation)
15. `History.md` (Ambiguous layer assignment: historical/meta file)

</rewritten_file>
