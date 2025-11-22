# Architecture Decision Records (ADRs)

**Status:** LAW
**Purpose:** These documents explain the "Why" behind our architectural mandates. They are not suggestions; they are recorded decisions that define the system's constraints.

## The Decisions

*   **[ADR-001-Supavisor-Requirements.md](ADR-001-Supavisor-Requirements.md)**: Why we MUST use specific connection parameters for Supabase pooling.
*   **[ADR-002-Removed-Tenant-Isolation.md](ADR-002-Removed-Tenant-Isolation.md)**: Why we moved away from strict tenant isolation.
*   **[ADR-003-Dual-Status-Workflow.md](ADR-003-Dual-Status-Workflow.md)**: The theory behind the Curation/Processing status split.
*   **[ADR-004-Transaction-Boundaries.md](ADR-004-Transaction-Boundaries.md)**: Why Routers commit and Services flush.
*   **[ADR-005-ENUM-Catastrophe.md](ADR-005-ENUM-Catastrophe.md)**: The lesson on why Enums must be centralized and consistent.

## How to Use
If you question a mandate in the `AI_CHEAT_SHEET.md`, read the corresponding ADR here to understand the history and rationale.
