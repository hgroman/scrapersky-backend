# Architecture Evolution

This document outlines key architectural transitions in the ScraperSky backend, providing context for historical documentation and pointing to current standards.

| Era     | Deprecated Pattern / Old System      | Current Standard Guide                                                                         | Primary Risk if Old Pattern is Followed |
| ------- | ------------------------------------ | ---------------------------------------------------------------------------------------------- | --------------------------------------- |
| 2023-Q2 | Role-Based Access Control (RBAC)     | `08-LAYER3_RBAC_SYSTEM_SIMPLIFIED.md` (describes JWT) / `11-LAYER3_AUTHENTICATION_BOUNDARY.md` | Security Vulnerabilities, Auth Failure  |
| 2023-Q3 | Tenant Isolation                     | Single-tenant data models (explicitly removed)                                                 | Data Leaks, Incorrect Data Access       |
| 2024-Q1 | Alembic Migrations (previous system) | `31.1-LAYER1_MCP-MIGRATION-GUIDE.md`                                                           | Schema Drift, Migration Failures        |

**Notes:**

- If a guide is marked `[!DEPRECATED]`, it describes an old pattern. Refer to this evolution guide or the current standard guide linked in the deprecation notice.
- The numeric prefixes on filenames (e.g., `08-`, `11-`) are original and can help trace historical sequence but do not solely dictate deprecation status.
