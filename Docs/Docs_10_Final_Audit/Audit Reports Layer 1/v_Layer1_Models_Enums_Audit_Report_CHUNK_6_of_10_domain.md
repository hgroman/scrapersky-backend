# Layer 1: Models & ENUMs - Audit Report (Chunk)

_This is a segment of the full Layer 1 audit report, focusing on a specific component._

### File: `src/models/domain.py`

This file defines the `Domain` SQLAlchemy model and several Python ENUMs.

#### ENUMs in `src/models/domain.py`

1.  **ENUM: `SitemapCurationStatusEnum`**:
    -   **Gap Analysis:** Inherits from `enum.Enum`, not `(str, enum.Enum)`. Values are Enum members, not strings. Name "Not_a_Fit" is unusual for an Enum member but valid Python.
        -   `<!-- NEED_CLARITY: SitemapCurationStatusEnum inherits from enum.Enum, not (str, enum.Enum). Is this intentional? Blueprint prefers (str, enum.Enum) for string-based enums. -->`
    -   **Prescribed Refactoring Actions:** Clarify inheritance and consider `(str, enum.Enum)` for consistency.

2.  **ENUM: `HubotSyncStatus` (in domain.py)**:
    -   **Gap Analysis:** Re-definition of Enum found in `contact.py`. Violates Blueprint 2.2.1.2 (Avoid Duplication). Potential typo "Hubot" vs "HubSpot".
        -   `<!-- STOP_FOR_REVIEW: HubotSyncStatus ENUM is re-defined in domain.py (also in contact.py). Consolidate to a single definition. -->`
        -   `<!-- NEED_CLARITY: (Repeated) Is 'HubotSyncStatus' a typo for 'HubSpotSyncStatus'? -->`
    -   **Prescribed Refactoring Actions:** **CRITICAL:** Consolidate definition. Clarify/correct name.

3.  **ENUM: `HubSyncProcessingStatus` (in domain.py)**:
    -   **Gap Analysis:** Re-definition of Enum found in `contact.py`. Violates Blueprint 2.2.1.2. Potential typo/abbreviation "HubSync" vs "HubSpotSync".
        -   `<!-- STOP_FOR_REVIEW: HubSyncProcessingStatus ENUM is re-defined in domain.py (also in contact.py). Consolidate. -->`
        -   `<!-- NEED_CLARITY: (Repeated) Is 'HubSyncProcessingStatus' a typo/abbreviation for 'HubSpotSyncProcessingStatus'? -->`
    -   **Prescribed Refactoring Actions:** **CRITICAL:** Consolidate definition. Clarify/correct name.

4.  **ENUM: `SitemapAnalysisStatusEnum`**:
    -   **Gap Analysis:** Inherits from `enum.Enum`, not `(str, enum.Enum)`. Values are Enum members.
        -   `<!-- NEED_CLARITY: SitemapAnalysisStatusEnum inherits from enum.Enum, not (str, enum.Enum). Is this intentional? -->`
    -   **Prescribed Refactoring Actions:** Clarify inheritance and consider `(str, enum.Enum)`.

#### MODEL: `Domain(Base, BaseModel)`
- **Component Name:** `MODEL: Domain`
- **Current State Summary:** Represents website domains.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4, 2.1.5, 2.1.6 (Inheritance, Table Name, PK):** Compliant.
    - **Blueprint 2.1.8 (Column Naming & Types):**
        - `status`: `String` type. Consider Enum if values are fixed.
            -   `<!-- NEED_CLARITY: Domain.status is a String. Consider Enum if values are fixed. -->`
        - `domain_metadata`: DB name `meta_json` is acceptable if justified.
        - `sitemap_analysis_status`: `SQLAlchemyEnum` uses `name="SitemapAnalysisStatusEnum"` (PascalCase) for DB type. Violates Blueprint 2.1.8.3 (snake_case).
            -   `<!-- STOP_FOR_REVIEW: Domain.sitemap_analysis_status uses SQLAlchemyEnum name 'SitemapAnalysisStatusEnum'. Should be snake_case, e.g., 'sitemap_analysis_status_enum'. -->`
        - `sitemap_curation_status`: `SQLAlchemyEnum` uses `name="SitemapCurationStatusEnum"` (PascalCase) for DB type. Violates Blueprint 2.1.8.3.
            -   `<!-- STOP_FOR_REVIEW: Domain.sitemap_curation_status uses SQLAlchemyEnum name 'SitemapCurationStatusEnum'. Should be snake_case, e.g., 'sitemap_curation_status_enum'. -->`
    - **Blueprint 2.1.8.1 (Foreign Keys):**
        - `tenant_id`, `local_business_id`: Compliant.
        - `batch_id`: FK to `batch_jobs.batch_id`. Highlights `BatchJob` PK inconsistency.
            -   `<!-- NEED_CLARITY: Domain.batch_id FK refers to 'batch_jobs.batch_id', linking to BatchJob's UUID 'batch_id' rather than its Integer PK 'id'. Reinforces BatchJob PK concerns. -->`
- **Prescribed Refactoring Actions:**
    - Clarify if `Domain.status` should be an Enum.
    - **CRITICAL:** Change `name` in `SQLAlchemyEnum` for `sitemap_analysis_status` and `sitemap_curation_status` to snake_case DB type names.
    - Resolve `BatchJob` PK strategy. Ensure Enums `SitemapCurationStatusEnum` & `SitemapAnalysisStatusEnum` use `(str, enum.Enum)` if string values are expected.

---

