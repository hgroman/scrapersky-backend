# Layer 1: Models & ENUMs - Audit Report (Chunk)

_This is a segment of the full Layer 1 audit report, focusing on a specific component._

### File: `src/models/local_business.py`

This file defines the `LocalBusiness` SQLAlchemy model and the `DomainExtractionStatusEnum` Python ENUM. It imports `PlaceStatusEnum`.

#### ENUM: `DomainExtractionStatusEnum` (in `local_business.py`)
- **Current State Summary:** Defines statuses: `Queued`, `Processing`, `Completed`, `Error`. Inherits `enum.Enum`.
- **Gap Analysis (Technical Debt Identification):**
    - **Base Class:** Inherits `enum.Enum`, not `(str, enum.Enum)` as preferred by Blueprint for string-based status enums.
        -   `<!-- NEED_CLARITY: DomainExtractionStatusEnum inherits enum.Enum, not (str, enum.Enum). Consider changing for consistency and easier DB mapping. -->`
    - **Naming:** `DomainExtractionStatusEnum` uses "Enum" suffix, non-standard.
        -   `<!-- STOP_FOR_REVIEW: Enum name DomainExtractionStatusEnum should be DomainExtractionStatus (remove 'Enum' suffix). -->`
    - **Location:** Defined locally. Could potentially be centralized if its a generic processing status.
- **Prescribed Refactoring Actions:**
    - Change base class to `(str, enum.Enum)`. Rename to `DomainExtractionStatus`.
    - Evaluate for centralization in `enums.py`.

#### MODEL: `LocalBusiness(Base)`
- **Component Name:** `MODEL: LocalBusiness`
- **Current State Summary:** Represents local businesses. Inherits `Base`, **not** `BaseModel`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4 (Inheritance):** CRITICAL VIOLATION. Does not inherit `BaseModel`, leading to non-standard `id`, `tenant_id`, and timestamp implementations.
        -   `<!-- STOP_FOR_REVIEW: LocalBusiness must inherit from BaseModel, not just Base, per Blueprint 2.1.4. -->`
    - **Blueprint 2.1.8.2 (Tenant ID):** Defines `tenant_id` (PGUUID) but lacks `ForeignKey('tenants.id')`. `BaseModel` provides this.
        -   `<!-- STOP_FOR_REVIEW: LocalBusiness.tenant_id is missing ForeignKey('tenants.id'). Should use BaseModel's tenant_id. -->`
    - **Blueprint 2.1.8.3 (ENUM Database Type Naming):**
        - `status` column uses `PlaceStatusEnum` with DB name `place_status_enum` (compliant).
        - `domain_extraction_status` column uses `DomainExtractionStatusEnum` with DB name `DomainExtractionStatusEnum` (PascalCase). CRITICAL VIOLATION.
            -   `<!-- STOP_FOR_REVIEW: LocalBusiness.domain_extraction_status uses SQLAlchemyEnum name 'DomainExtractionStatusEnum' (PascalCase). Must be snake_case, e.g., 'domain_extraction_status_enum'. -->`
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Change `LocalBusiness` to inherit from `BaseModel`. Remove manual definitions of `id`, `tenant_id`, `created_at`, `updated_at`.
    - **CRITICAL:** Change `SQLAlchemyEnum` `name` for `domain_extraction_status` to snake_case (e.g., `domain_extraction_status_enum`).
    - Address issues in `DomainExtractionStatusEnum` (base class, name suffix).
    - Ensure imported `PlaceStatusEnum` is audited.

---

