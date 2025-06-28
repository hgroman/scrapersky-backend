# Layer 1: Models & ENUMs - Audit Report (Chunk)

_This is a segment of the full Layer 1 audit report, focusing on a specific component._

### File: `src/models/enums.py`

This file serves as a centralized location for some ENUM definitions, aligning with Blueprint 2.2.1.1.

#### 1. ENUM: `SitemapAnalysisStatusEnum` (in `enums.py`)
- **Current State Summary:** Defines statuses: `pending`, `queued`, `processing`, `submitted`, `failed`. Inherits `(str, enum.Enum)`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.2.1.2 (Duplication & Consistency):** Critically, this Enum is **also defined differently** in `src/models/domain.py` (which uses `enum.Enum` base and values `Queued`, `Processing`, `Completed`, `Error`). The `Domain` model currently uses the `domain.py` definition for its `sitemap_analysis_status` column.
        -   `<!-- STOP_FOR_REVIEW: SitemapAnalysisStatusEnum has conflicting definitions in enums.py and domain.py. The Domain model uses the one from domain.py. This must be reconciled to a single, consistent definition (ideally in enums.py and imported into domain.py). -->`
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Reconcile the two definitions of `SitemapAnalysisStatusEnum`. Choose one definition (base class, values, semantics), place it in `enums.py`, and update `domain.py` to import and use it. Ensure `Domain.sitemap_analysis_status` column reflects this, including a snake_case DB ENUM type name.

#### 2. ENUM: `DomainStatusEnum`
- **Current State Summary:** Defines statuses: `pending`, `processing`, `completed`, `error`. Inherits `(str, enum.Enum)`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint Compliance:** Compliant (Base Class, Naming, Values, Location).
    - **Usage Context:** The `Domain.status` column in `src/models/domain.py` is currently a `String`. This `DomainStatusEnum` is a suitable candidate for refactoring that column.
        -   `<!-- INFO: DomainStatusEnum (in enums.py) is a good candidate to replace the String-based Domain.status column in domain.py. -->`
- **Prescribed Refactoring Actions:**
    - During refactoring, update `Domain.status` in `domain.py` to use `SQLAlchemyEnum(DomainStatusEnum, name="domain_status_enum", create_type=False)`.

---

