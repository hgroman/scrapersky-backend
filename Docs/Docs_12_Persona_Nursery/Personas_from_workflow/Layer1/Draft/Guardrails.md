<!--
IMPORTANT: This document contains a copy of the UNIVERSAL guardrails.
Review and CUSTOMIZE the rules below to be SPECIFIC to Layer 1: Models & ENUMs.
Remove any universal rules that are not relevant to Layer 1.
Add new Layer 1-specific guardrails derived from `CONVENTIONS_AND_PATTERNS_GUIDE.md` and any `Layer-1-Models_Blueprint.md`.
-->

### Absolute Guard‑Rails (v2.0) - Layer 1: Models & ENUMs (NEEDS CUSTOMIZATION)

| #   | Rule                                                                                                                                                                                                                                                                                                                                                                                                              | Rationale (Internal - Not for direct AI consumption unless for context)                                                                                          |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **ORM-Only Database Access:** All database interactions MUST use SQLAlchemy ORM. Raw SQL queries are prohibited.                                                                                                                                                                                                                                                                                                  | Ensures data access consistency, security, and leverages ORM benefits. Aligns with `Layer-4-Services_Blueprint.md` Sec 2.2 & 3.2.                                |
| 2   | **Zero Assumptions/Verify Rule Compliance:** If any proposed action might conflict with a documented convention, Blueprint, SOP, or these Guardrails, HALT and seek explicit clarification from the user/Director AI before proceeding.                                                                                                                                                                           | Prevents errors from misinterpretation or outdated information. Core collaborative principle.                                                                    |
| 3   | **Session & Transaction Handling:**<br> a) API Routers typically manage transaction boundaries (e.g., commit/rollback) for API-initiated actions.<br> b) Services (except schedulers) MUST accept an `AsyncSession` as a parameter and MUST NOT create their own sessions for routine operations.<br> c) Top-level scheduler functions MUST use `get_background_session()` to manage their own session lifecycle. | Accurately reflects nuanced session/transaction rules from `Layer-4-Services_Blueprint.md` Sec 2.2 & 3.2, superseding previous simpler rule.                     |
| 4   | **Status Enum & Column Naming:**<br> a) Python Enum classes for workflow statuses: `{WorkflowNameTitleCase}CurationStatus`, `{WorkflowNameTitleCase}ProcessingStatus` (no "Enum" suffix).<br> b) SQLAlchemy Curation Status Column: `{workflow_name}_curation_status`.<br> c) SQLAlchemy Processing Status Column: `{workflow_name}_processing_status`.                                                           | Enforces standard naming for dual-status system components. Aligns with `CONVENTIONS_AND_PATTERNS_GUIDE.md` Sec 2.                                               |
| 5   | **Scheduler Registration & Naming:**<br> a) Each workflow requiring background processing MUST have a dedicated scheduler file: `src/services/{workflow_name}_scheduler.py`.<br> b) Each scheduler file MUST implement `setup_{workflow_name}_scheduler()`, which is imported and called in `src/main.py` lifespan.                                                                                               | Ensures standardized scheduler implementation and registration. Aligns with `Layer-4-Services_Blueprint.md` Sec 2.2 & `CONVENTIONS_AND_PATTERNS_GUIDE.md` Sec 5. |
| 6   | **Core Directory Structure:** Routers in `src/routers/`, Services in `src/services/`, Schemas in `src/schemas/`, Models in `src/models/`, Tests in `tests/`.                                                                                                                                                                                                                                                      | Defines standard project layout for key components. Expanded to include `src/models/`.                                                                           |
| 7   | **Documentation File Naming:** Adhere to specified file naming prefixes (e.g., JE*, WO*, HO\_) for documentation as defined in the `CONVENTIONS_AND_PATTERNS_GUIDE.md` or other project-specific documentation guides.                                                                                                                                                                                            | Maintains consistency for project management and historical tracking documents.                                                                                  |
| 8   | **No Tenant ID:** All `tenant_id` parameters, model fields, and related filtering logic MUST be absent from the codebase.                                                                                                                                                                                                                                                                                         | Critical architectural decision for simplification. Reinforced by multiple documents.                                                                            |
| 9   | **No Hardcoding:** Business-critical values (API keys, secret keys, dynamic thresholds) MUST NOT be hardcoded. Use the `settings` object (from `src/config/settings.py`) for configuration.                                                                                                                                                                                                                       | Standard security and configuration best practice. Reinforced by `Layer-4-Services_Blueprint.md`.                                                                |

_These Guardrails are a concise summary. Always defer to the detailed specifications in the `CONVENTIONS_AND_PATTERNS_GUIDE.md` and relevant Layer Blueprints/SOPs for complete context and nuanced application._
