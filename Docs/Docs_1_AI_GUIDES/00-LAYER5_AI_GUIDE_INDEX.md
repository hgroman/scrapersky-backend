# ScraperSky AI Guide Index

This document serves as the master index for all AI guidance documents. These guides help AI assistants understand the project structure, architecture, and development patterns.

## Quick Reference Guides

| Guide                                                                      | Description                                           | Priority |
| -------------------------------------------------------------------------- | ----------------------------------------------------- | -------- |
| [01-MODULE_SPECIFIC_PROMPTS.md](./01-MODULE_SPECIFIC_PROMPTS.md)           | Instructions for specific functionality areas         | HIGH     |
| [02-ARCHITECTURE_QUICK_REFERENCE.md](./02-ARCHITECTURE_QUICK_REFERENCE.md) | High-level architecture overview                      | HIGH     |
| [11-AUTHENTICATION_BOUNDARY.md](./11-AUTHENTICATION_BOUNDARY.md)           | **CRITICAL** Authentication boundary and JWT handling | CRITICAL |

## Strategic Guides

| Guide                                                                      | Description                           | Priority |
| -------------------------------------------------------------------------- | ------------------------------------- | -------- |
| [03-AI_MANAGEMENT_STRATEGY.md](./03-AI_MANAGEMENT_STRATEGY.md)             | How to use AI for ongoing development | MEDIUM   |
| [04-SIMPLIFICATION_OPPORTUNITIES.md](./04-SIMPLIFICATION_OPPORTUNITIES.md) | Areas where code can be simplified    | MEDIUM   |
| [05-IMMEDIATE_ACTION_PLAN.md](./05-IMMEDIATE_ACTION_PLAN.md)               | Current priorities and actions        | HIGH     |

## Technical Implementation Guides

| Guide                                                                                  | Description                                                                            | Priority |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------- |
| [06-COMPREHENSIVE_TEST_PLAN.md](./06-COMPREHENSIVE_TEST_PLAN.md)                       | Testing strategy and implementation                                                    | HIGH     |
| [07-DATABASE_CONNECTION_STANDARDS.md](./07-DATABASE_CONNECTION_STANDARDS.md)           | **CRITICAL** database connection standards with **MANDATORY** Supavisor requirements   | CRITICAL |
| [08-RBAC_SYSTEM_REMOVED.md](./08-RBAC_SYSTEM_REMOVED.md)                               | **CRITICAL** RBAC system removal details                                               | CRITICAL |
| [09-TENANT_ISOLATION_REMOVED.md](./09-TENANT_ISOLATION_REMOVED.md)                     | Explains removal of tenant isolation for simpler architecture                          | CRITICAL |
| [10-TEST_USER_INFORMATION.md](./10-TEST_USER_INFORMATION.md)                           | Test user credentials and usage                                                        | HIGH     |
| [12-STRUCTURAL_CHANGES_SUMMARY.md](./12-STRUCTURAL_CHANGES_SUMMARY.md)                 | **CRITICAL** Summary of all major structural changes                                   | CRITICAL |
| [13-TRANSACTION_MANAGEMENT_GUIDE.md](./13-TRANSACTION_MANAGEMENT_GUIDE.md)             | Proper transaction boundary management                                                 | CRITICAL |
| [14-GOOGLE_MAPS_API_EXEMPLAR.md](./14-GOOGLE_MAPS_API_EXEMPLAR.md)                     | **CRITICAL** Google Maps API as exemplar implementation                                | CRITICAL |
| [15-API_STANDARDIZATION_GUIDE.md](./15-API_STANDARDIZATION_GUIDE.md)                   | **CRITICAL** API version and structure standardization                                 | CRITICAL |
| [16-UUID_STANDARDIZATION_GUIDE.md](./16-UUID_STANDARDIZATION_GUIDE.md)                 | **CRITICAL** UUID format and handling standards                                        | CRITICAL |
| [17-CORE_ARCHITECTURAL_PRINCIPLES.md](./17-CORE_ARCHITECTURAL_PRINCIPLES.md)           | Foundational architectural principles to follow                                        | CRITICAL |
| [22-TESTING_CONVENTIONS_GUIDE.md](./22-TESTING_CONVENTIONS_GUIDE.md)                   | Standards for writing unit and integration tests.                                      | CRITICAL |
| [23-FASTAPI_ROUTER_PREFIX_CONVENTION.md](./23-FASTAPI_ROUTER_PREFIX_CONVENTION.md)     | Convention for API router prefixes.                                                    | CRITICAL |
| [24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md](./24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md) | Step-by-step guide for adding new background tasks using the shared scheduler pattern. | CRITICAL |

## Usage Instructions

1. **For new AI sessions**: Start by referencing this index and the architecture quick reference.
2. **For specific tasks**: Reference the relevant technical implementation guide(s).
3. **For strategic direction**: Consult the strategic guides to understand priorities.

## Critical Guidelines

1. **Core Architectural Principles**: Follow the core architectural principles in [17-CORE_ARCHITECTURAL_PRINCIPLES.md](./17-CORE_ARCHITECTURAL_PRINCIPLES.md)
2. **Authentication Boundary**: JWT authentication must ONLY happen at the API router level. See [11-AUTHENTICATION_BOUNDARY.md](./11-AUTHENTICATION_BOUNDARY.md)
3. **Database Connections**: Always follow the database connection standards in [07-DATABASE_CONNECTION_STANDARDS.md](./07-DATABASE_CONNECTION_STANDARDS.md)
4. **Transaction Ownership**: Routers own transactions, services are transaction-aware. See [13-TRANSACTION_MANAGEMENT_GUIDE.md](./13-TRANSACTION_MANAGEMENT_GUIDE.md) for critical details
5. **API Standardization**: Follow the API versioning and structure standards in [15-API_STANDARDIZATION_GUIDE.md](./15-API_STANDARDIZATION_GUIDE.md)
6. **UUID Standardization**: Use proper UUID formats and handling as described in [16-UUID_STANDARDIZATION_GUIDE.md](./16-UUID_STANDARDIZATION_GUIDE.md)
7. **JWT Authentication Only**: RBAC and tenant isolation have been completely removed. See [12-STRUCTURAL_CHANGES_SUMMARY.md](./12-STRUCTURAL_CHANGES_SUMMARY.md)
8. **Exemplar Implementation**: Follow the Google Maps API implementation as the golden standard. See [14-GOOGLE_MAPS_API_EXEMPLAR.md](./14-GOOGLE_MAPS_API_EXEMPLAR.md)
9. **Testing**: Use real test user credentials from [10-TEST_USER_INFORMATION.md](./10-TEST_USER_INFORMATION.md)

## RBAC & Tenant Isolation Removal Alert

⚠️ **CRITICAL UPDATE**: RBAC system and tenant isolation have been completely removed from the project.

If you encounter any of the following in the codebase:

- Permission checks (`require_permission`, `has_permission`)
- Feature flag checks (`require_feature_enabled`)
- Role level checks (`require_role_level`)
- Tenant isolation code (tenant_id filtering, etc.)
- The constants file `src.constants.rbac`
- The utils file `src.utils.permissions`

**STOP IMMEDIATELY** and:

1. Note the location of the code
2. Report it to the project maintainer
3. Do not modify the code until receiving guidance

## Next Steps in Development

According to our standardization roadmap:

1. **Completed Work**:

   - Implemented proper database schema changes for the Google Maps API
   - Added comprehensive search history UI to the Google Maps frontend
   - Created search and results endpoints with proper transaction management
   - Created a standardization template for future API implementations
   - Fixed linter errors in the Google Maps API router
   - Documentation stored in work orders:
     - `project-docs/07-database-connection-audit/07-27-LOCALMINER-DISCOVERYSCAN-RESULTS-IMPLEMENTATION.md`
     - `project-docs/07-database-connection-audit/07-28-SEARCH-HISTORY-UI-IMPLEMENTATION.md`
     - `project-docs/07-database-connection-audit/07-29-GOOGLE-MAPS-API-STANDARDIZATION-TEMPLATE.md`
     - `project-docs/07-database-connection-audit/07-30-GOOGLE-MAPS-API-PROGRESS-AND-LINTER-FIX-WORK-ORDER.md`

2. **Current Focus**:

   - Apply the standardization template to the Sitemap API and Modernized Page Scraper
   - Address UI styling issues with consistent dark theme
   - Complete the work outlined in `07-27-MODERNIZED-PAGE-SCRAPER-FIX-WORK-ORDER-2025-03-26.md`

3. **UUID Standardization**:

   - Converting all job_id fields to proper UUID format
   - Updating the job service to use standard UUIDs
   - Checking domain service for UUID handling

4. **Testing Implementation**:

   - We've created test scripts for sitemap functionality in `scripts/testing/test_sitemap_with_user.py`
   - Started creating a test script for Google Maps API in `scripts/testing/test_google_maps_api.py`
   - Need to create a test script for the Modernized Page Scraper following the template
   - Continue creating test scripts for other key services

5. **Upcoming Work**:
   - Job Service standardization
   - Domain Service review and update
   - Core Services standardization
   - Error handling improvements

## Work Instructions for Next Session

1. **UUID Standardization**:
   | Document | Purpose |
   | -------------------------------------------------------------------------- | ------------------------------------------------------------- |
   | [01-MODULE_SPECIFIC_PROMPTS.md](01-MODULE_SPECIFIC_PROMPTS.md) | Template prompts for specific modules to focus AI sessions |
   | [02-ARCHITECTURE_QUICK_REFERENCE.md](02-ARCHITECTURE_QUICK_REFERENCE.md) | One-page architecture reference with patterns and conventions |
   | [03-AI_MANAGEMENT_STRATEGY.md](03-AI_MANAGEMENT_STRATEGY.md) | Strategy for managing AI assistants with specialized roles |
   | [04-SIMPLIFICATION_OPPORTUNITIES.md](04-SIMPLIFICATION_OPPORTUNITIES.md) | Incremental ways to simplify the codebase |
   | [05-IMMEDIATE_ACTION_PLAN.md](05-IMMEDIATE_ACTION_PLAN.md) | Practical step-by-step plan to complete the project |
   | [06-COMPREHENSIVE_TEST_PLAN.md](06-COMPREHENSIVE_TEST_PLAN.md) | Structured approach to testing critical functionality |
   | [07-DATABASE_CONNECTION_STANDARDS.md](07-DATABASE_CONNECTION_STANDARDS.md) | **CRITICAL** connection standards and Supavisor requirements |
   | [08-RBAC_SYSTEM_REMOVED.md](08-RBAC_SYSTEM_REMOVED.md) | **CRITICAL** details about RBAC system removal |
   | [09-TENANT_ISOLATION_REMOVED.md](09-TENANT_ISOLATION_REMOVED.md) | **CRITICAL** information about tenant isolation removal |
   | [10-TEST_USER_INFORMATION.md](10-TEST_USER_INFORMATION.md) | Information about test users |
   | [11-AUTHENTICATION_BOUNDARY.md](11-AUTHENTICATION_BOUNDARY.md) | **CRITICAL** authentication boundary principles |
   | [12-STRUCTURAL_CHANGES_SUMMARY.md](12-STRUCTURAL_CHANGES_SUMMARY.md) | **CRITICAL** summary of all major structural changes |
   | [13-TRANSACTION_MANAGEMENT_GUIDE.md](13-TRANSACTION_MANAGEMENT_GUIDE.md) | **CRITICAL** transaction management patterns and principles |
   | [14-GOOGLE_MAPS_API_EXEMPLAR.md](14-GOOGLE_MAPS_API_EXEMPLAR.md) | **CRITICAL** Google Maps API as exemplar implementation |
   | [15-API_STANDARDIZATION_GUIDE.md](15-API_STANDARDIZATION_GUIDE.md) | **CRITICAL** API version and structure standardization |
   | [16-UUID_STANDARDIZATION_GUIDE.md](16-UUID_STANDARDIZATION_GUIDE.md) | **CRITICAL** UUID format and handling standards |
   | [17-CORE_ARCHITECTURAL_PRINCIPLES.md](17-CORE_ARCHITECTURAL_PRINCIPLES.md) | **CRITICAL** core architectural principles and patterns |
   | [22-TESTING_CONVENTIONS_GUIDE.md](22-TESTING_CONVENTIONS_GUIDE.md) | Standards for writing unit and integration tests. |
   | [23-FASTAPI_ROUTER_PREFIX_CONVENTION.md](23-FASTAPI_ROUTER_PREFIX_CONVENTION.md) | Convention for API router prefixes. |
   | [24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md](24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md) | Step-by-step guide for adding new background tasks using the shared scheduler pattern. |

## How to Use These Guides

### For Starting New AI Sessions

1. Identify which module you're working on
2. Copy the relevant template from [01-MODULE_SPECIFIC_PROMPTS.md](01-MODULE_SPECIFIC_PROMPTS.md)
3. Choose the appropriate AI role from [03-AI_MANAGEMENT_STRATEGY.md](03-AI_MANAGEMENT_STRATEGY.md)
4. Include the architecture reference from [02-ARCHITECTURE_QUICK_REFERENCE.md](02-ARCHITECTURE_QUICK_REFERENCE.md)
5. Start your AI session with this context
6. Always follow the authentication boundary principle: JWT authentication ONLY at API gateway/router level

### For Project Planning

1. Follow the prioritized tasks in [05-IMMEDIATE_ACTION_PLAN.md](05-IMMEDIATE_ACTION_PLAN.md)
2. Consider the simplification opportunities in [04-SIMPLIFICATION_OPPORTUNITIES.md](04-SIMPLIFICATION_OPPORTUNITIES.md)
3. Implement tests according to [06-COMPREHENSIVE_TEST_PLAN.md](06-COMPREHENSIVE_TEST_PLAN.md)

### For Preventing Scope Creep

1. Use the task isolation strategies in [03-AI_MANAGEMENT_STRATEGY.md](03-AI_MANAGEMENT_STRATEGY.md)
2. Provide clear task boundaries in your prompts
3. Create new AI sessions for different modules or tasks
4. Document what was changed after each session

## Example AI Session Start

```
You are now a Database Expert for the ScraperSky project.

Please adhere to the core architectural principles and patterns:
[paste relevant section from 17-CORE_ARCHITECTURAL_PRINCIPLES.md]

Pay special attention to these critical areas:
[paste relevant section from 13-TRANSACTION_MANAGEMENT_GUIDE.md] (transaction management)
[paste relevant section from 16-UUID_STANDARDIZATION_GUIDE.md] (UUID handling)

Also be aware of the exemplary implementation patterns:
[paste relevant section from 14-GOOGLE_MAPS_API_EXEMPLAR.md]

I'm working on the sitemap_processing_service.py module. This module follows these strict database patterns:
[paste relevant section from 01-MODULE_SPECIFIC_PROMPTS.md]

My specific task is to fix the database insertion in the _process_domain method.

Here's the current implementation:
[paste code]

Please adhere strictly to these constraints:
- FOLLOW the Google Maps API exemplar pattern for implementation
- ENFORCE proper transaction boundaries: routers own transactions, services are transaction-aware
- USE standard UUID format without prefixes
- FOLLOW the v3 API standardization pattern
- NO DIRECT SQL statements unless absolutely necessary
- NO SESSION creation in service methods (except background tasks)
- ALWAYS use existing model helper methods (create_new, etc.)
- ENFORCE authentication boundary: JWT auth ONLY at router level, never in services
- REMEMBER: RBAC and tenant isolation have been completely removed
- REPORT any RBAC or tenant code you find, do not modify it without guidance
```

## Next Steps

1. Review these guides to understand the approach
2. Start using the specialized AI roles for focused tasks
3. Follow the immediate action plan to make progress
4. Implement the test plan to verify your changes
5. Consider the simplification opportunities as you progress
6. Maintain strict authentication boundaries: JWT handling only at API router level

## Core Architectural Documents

| Document                                                                   | Description                                                                          |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [02-ARCHITECTURE_QUICK_REFERENCE.md](02-ARCHITECTURE_QUICK_REFERENCE.md)   | Essential architecture patterns and rules at a glance                                |
| [07-DATABASE_CONNECTION_STANDARDS.md](07-DATABASE_CONNECTION_STANDARDS.md) | **CRITICAL** database connection standards with **MANDATORY** Supavisor requirements |
| [09-TENANT_ISOLATION_REMOVED.md](09-TENANT_ISOLATION_REMOVED.md)           | Explains removal of tenant isolation for simpler architecture                        |
| [13-TRANSACTION_MANAGEMENT_GUIDE.md](13-TRANSACTION_MANAGEMENT_GUIDE.md)   | Proper transaction boundary management                                               |
| [17-CORE_ARCHITECTURAL_PRINCIPLES.md](17-CORE_ARCHITECTURAL_PRINCIPLES.md) | Foundational architectural principles to follow                                      |
