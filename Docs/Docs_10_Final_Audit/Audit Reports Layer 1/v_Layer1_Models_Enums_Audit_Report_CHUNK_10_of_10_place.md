# Layer 1: Models & ENUMs - Audit Report (Chunk)

_This is a segment of the full Layer 1 audit report, focusing on a specific component._

### File: `src/models/place.py`

This file defines `PlaceStatusEnum`, `GcpApiDeepScanStatusEnum`, and the `Place` SQLAlchemy model.

#### ENUM: `PlaceStatusEnum` (in `place.py`)
- **Current State Summary:** Defines statuses: `New`, `Selected`, `Maybe`, `Not_a_Fit`, `Archived`. Inherits `enum.Enum`.
- **Gap Analysis (Technical Debt Identification):**
    - **Base Class:** Inherits `enum.Enum`, not `(str, enum.Enum)` as preferred.
        -   `<!-- NEED_CLARITY: PlaceStatusEnum should inherit (str, enum.Enum). -->`
    - **Naming:** `PlaceStatusEnum` uses "Enum" suffix (non-standard). Should be `PlaceStatus`.
        -   `<!-- STOP_FOR_REVIEW: Rename PlaceStatusEnum to PlaceStatus. -->`
    - **Values:** `Selected` (non-standard, prefer `Queued`). `Maybe`, `Not_a_Fit`, `Archived` are specific.
        -   `<!-- NEED_CLARITY: PlaceStatusEnum.Selected should ideally be Queued. Other values are workflow-specific. -->`
- **Prescribed Refactoring Actions:**
    - Change base class to `(str, enum.Enum)`. Rename to `PlaceStatus`. Consider standardizing `Selected` to `Queued`.

#### ENUM: `GcpApiDeepScanStatusEnum` (in `place.py`)
- **Current State Summary:** Statuses: `Queued`, `Processing`, `Completed`, `Error`. Inherits `enum.Enum`.
- **Gap Analysis (Technical Debt Identification):**
    - **Base Class:** Inherits `enum.Enum`, not `(str, enum.Enum)`.
        -   `<!-- NEED_CLARITY: GcpApiDeepScanStatusEnum should inherit (str, enum.Enum). -->`
    - **Naming:** `GcpApiDeepScanStatusEnum` uses "Enum" suffix. Should be `GcpApiDeepScanStatus`.
        -   `<!-- STOP_FOR_REVIEW: Rename GcpApiDeepScanStatusEnum to GcpApiDeepScanStatus. -->`
- **Prescribed Refactoring Actions:**
    - Change base class to `(str, enum.Enum)`. Rename to `GcpApiDeepScanStatus`. Evaluate for centralization.

#### MODEL: `Place(Base)`
- **Component Name:** `MODEL: Place`
- **Current State Summary:** Represents `places_staging`. Inherits `Base`, not `BaseModel`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4 (Inheritance):** CRITICAL VIOLATION. Must inherit `BaseModel`.
        -   `<!-- STOP_FOR_REVIEW: Place model must inherit from BaseModel. -->`
    - **Blueprint 2.1.6 (Primary Key):** `id` is `Integer` PK. CRITICAL VIOLATION. Must be UUID from `BaseModel`.
        -   `<!-- STOP_FOR_REVIEW: Place.id is Integer PK. Must be UUID from BaseModel. -->`
    - **Blueprint 2.1.8.2 (Tenant ID):** `tenant_id` (UUID) lacks `ForeignKey('tenants.id')`. CRITICAL VIOLATION.
        -   `<!-- STOP_FOR_REVIEW: Place.tenant_id lacks ForeignKey. Must use BaseModel's tenant_id. -->`
    - **Common Fields:** `updated_by` is `String`, mismatch with `BaseModel`'s PGUUID. Timestamps need reconciliation.
        -   `<!-- STOP_FOR_REVIEW: Place.updated_by (String) mismatches BaseModel (PGUUID). -->`
    - **Foreign Keys:** `search_job_id` (UUID) FKs to `jobs.id` (Integer). CRITICAL type mismatch.
        -   `<!-- STOP_FOR_REVIEW: Place.search_job_id (UUID) FKs to Job.id (Integer). Type mismatch. Job.id must be UUID. -->`
    - **Blueprint 2.1.8.3 (ENUM DB Naming):** DB names `place_status_enum`, `gcp_api_deep_scan_status_enum` are compliant.
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** `Place` to inherit `BaseModel`. Remove/reconcile `id`, `tenant_id`, `created_by`, `updated_by`, timestamps.
    - **CRITICAL:** Ensure `Job.id` becomes UUID for `search_job_id` FK integrity.
    - Address issues in `PlaceStatusEnum` and `GcpApiDeepScanStatusEnum`.

---

### File: `src/models/place_search.py`

This file defines the `PlaceSearch` SQLAlchemy model. No Python ENUMs are defined in this file.

#### MODEL: `PlaceSearch(Base)`
- **Component Name:** `MODEL: PlaceSearch`
- **Current State Summary:** Represents search metadata for Places API queries. Inherits `Base`, **not** `BaseModel`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4 (Inheritance):** CRITICAL VIOLATION. Must inherit `BaseModel`.
        -   `<!-- STOP_FOR_REVIEW: PlaceSearch model must inherit from BaseModel, not just Base. -->`
    - **Blueprint 2.1.6 (Primary Key):** `id` is `UUID(as_uuid=True)` with `default=uuid.uuid4`. `BaseModel` provides `id` as PGUUID with server default.
    - **Blueprint 2.1.8.2 (Tenant ID):** `tenant_id` (UUID) lacks `ForeignKey('tenants.id')`. CRITICAL VIOLATION.
        -   `<!-- STOP_FOR_REVIEW: PlaceSearch.tenant_id lacks ForeignKey. Must use BaseModel's tenant_id. -->`
    - **Status Column:** `status` is `String(50), default="pending"`. Should be an Enum.
        -   `<!-- NEED_CLARITY: PlaceSearch.status (String) should be an Enum (e.g., SearchStatusEnum) mapped via SQLAlchemyEnum. -->`
    - **Timestamps:** `created_at`, `updated_at` are manually defined. `BaseModel` provides these.
    - **User Tracking:** `user_id` (UUID). `BaseModel` offers `created_by` (PGUUID).
        - `<!-- NEED_CLARITY: Reconcile PlaceSearch.user_id with BaseModel.created_by. Ensure PGUUID if kept. -->`
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** `PlaceSearch` to inherit `BaseModel`. Remove/reconcile `id`, `tenant_id`, timestamps, and user tracking fields.
    - Define a new Enum (e.g., `SearchStatusEnum`) for the `status` field and use `SQLAlchemyEnum`.

---

### File: `src/models/page.py`

This file defines `PageCurationStatus`, `PageProcessingStatus` Enums and the `Page` SQLAlchemy model.

#### ENUM: `PageCurationStatus(str, Enum)`
- **Current State Summary:** Statuses for page curation. Inherits `(str, Enum)`.
- **Gap Analysis (Technical Debt Identification):**
    - **Values:** `Complete` is non-standard; should be `Completed`.
        -   `<!-- NEED_CLARITY: PageCurationStatus.Complete should be Completed. -->`
- **Prescribed Refactoring Actions:**
    - Change `PageCurationStatus.Complete` to `PageCurationStatus.Completed`.

#### ENUM: `PageProcessingStatus(str, Enum)`
- **Current State Summary:** Statuses for page processing. Inherits `(str, Enum)`.
- **Gap Analysis (Technical Debt Identification):**
    - **Values:** `Complete` is non-standard; should be `Completed`.
        -   `<!-- NEED_CLARITY: PageProcessingStatus.Complete should be Completed. -->`
- **Prescribed Refactoring Actions:**
    - Change `PageProcessingStatus.Complete` to `PageProcessingStatus.Completed`.

#### MODEL: `Page(Base, BaseModel)`
- **Component Name:** `MODEL: Page`
- **Current State Summary:** Represents crawled/processed pages. Inherits `Base`, `BaseModel`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4 (Inheritance):** Compliant.
    - **Blueprint 2.1.6 (Primary Key - id):** `Page` redefines `id`, differing from `BaseModel.id` (client vs. server default).
        -   `<!-- STOP_FOR_REVIEW: Page.id redefinition differs from BaseModel.id. Rely on BaseModel.id. -->`
    - **Blueprint 2.1.8.2 (Tenant ID):** `Page` redefines `tenant_id`, critically omitting `ForeignKey('tenants.id')` and `index=True` provided by `BaseModel`.
        -   `<!-- STOP_FOR_REVIEW: Page.tenant_id redefinition is missing ForeignKey and index. Critical. Rely on BaseModel.tenant_id. -->`
    - **Blueprint 2.1.8.3 (ENUM DB Naming):** Compliant for `page_curation_status` (`pagecurationstatus`) and `page_processing_status` (`pageprocessingstatus`).
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Remove explicit redefinitions of `id` and `tenant_id` in `Page`; rely on `BaseModel` versions.
    - Standardize Enum values (`Complete` to `Completed`) as noted above.

---

### File: `src/models/profile.py`

This file defines the `Profile` SQLAlchemy model. It also contains Pydantic models (out of scope for Layer 1 audit). No Python ENUMs are used directly in the SQLAlchemy model.

#### MODEL: `Profile(Base, BaseORMModel)`
- **Component Name:** `MODEL: Profile` (Note: `BaseORMModel` is an alias for `BaseModel`)
- **Current State Summary:** Represents user profiles. Inherits `Base`, `BaseORMModel`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4 & 2.1.5 & 2.1.6 (Inheritance, Table Name, ID):** Compliant. Inherits `BaseModel` and uses its `id`.
    - **Blueprint 2.1.8.2 (Tenant ID):** `Profile` redefines `tenant_id`, critically omitting `ForeignKey('tenants.id')` and `index=True` which are provided by `BaseModel` and essential for tenant isolation.
        -   `<!-- STOP_FOR_REVIEW: Profile.tenant_id redefinition omits ForeignKey and index from BaseModel. Critical deviation from tenant isolation strategy. Rely on BaseModel.tenant_id. -->`
    - **Other Columns:** `role` is `Text`. Consider Enum if roles are fixed.
        -   `<!-- NEED_CLARITY: Profile.role (Text). Consider Enum (e.g., UserRoleEnum) if roles are predefined. -->`
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Remove explicit redefinition of `tenant_id` in `Profile`; rely on `BaseModel`'s version.
    - Consider an Enum for the `role` field.

---

### File: `src/models/sitemap.py`

Defines 3 Enums (`SitemapFileStatusEnum`, `SitemapImportCurationStatusEnum`, `SitemapImportProcessStatusEnum`) and 2 Models (`SitemapFile`, `SitemapUrl`).

#### ENUMs in `sitemap.py` (General Issues)
- All three Enums inherit `enum.Enum` instead of `(str, enum.Enum)`.
    - `<!-- NEED_CLARITY: All Enums in sitemap.py should inherit (str, enum.Enum). -->`
- All three Enums use the "Enum" suffix in their Python names (e.g., `SitemapFileStatusEnum`).
    - `<!-- STOP_FOR_REVIEW: All Enums in sitemap.py should have "Enum" suffix removed from their Python names. -->`
- `SitemapImportCurationStatusEnum.Selected` value is non-standard (prefer `Queued`).
    - `<!-- NEED_CLARITY: SitemapImportCurationStatusEnum.Selected should be Queued. -->`

#### MODEL: `SitemapFile(Base, BaseModel)`
- **Gap Analysis:**
    - **`tenant_id`:** CRITICAL. Redefined, omitting `ForeignKey`, changing nullability to `True`, using hardcoded default. Must use `BaseModel.tenant_id`.
        -   `<!-- STOP_FOR_REVIEW: SitemapFile.tenant_id redefinition is critical. Must use BaseModel.tenant_id. -->`
    - **`created_by`, `updated_by`:** Redefined as nullable; `BaseModel` versions are non-nullable.
        -   `<!-- NEED_CLARITY: Reconcile SitemapFile.created_by/updated_by (nullable) with BaseModel versions (non-nullable). -->`
    - **ENUM DB Name:** `deep_scrape_curation_status` uses DB enum name `SitemapCurationStatusEnum` (PascalCase). CRITICAL. Must be snake_case.
        -   `<!-- STOP_FOR_REVIEW: SitemapFile.deep_scrape_curation_status DB enum name must be snake_case. -->`
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Use `BaseModel.tenant_id`. Reconcile `created_by`/`updated_by`.
    - **CRITICAL:** Fix `deep_scrape_curation_status` DB enum name.
    - Fix all Enum definitions as noted above.

#### MODEL: `SitemapUrl(Base, BaseModel)`
- **Gap Analysis:**
    - **`tenant_id`:** CRITICAL. Same issue as `SitemapFile.tenant_id`.
        -   `<!-- STOP_FOR_REVIEW: SitemapUrl.tenant_id redefinition is critical. Must use BaseModel.tenant_id. -->`
    - **`created_by`, `updated_by`:** Same issue as `SitemapFile`.
        -   `<!-- NEED_CLARITY: Reconcile SitemapUrl.created_by/updated_by (nullable) with BaseModel versions. -->`
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Use `BaseModel.tenant_id`. Reconcile `created_by`/`updated_by`.

---

### File: `src/models/tenant.py`

This file defines the `Tenant` SQLAlchemy model and a `DEFAULT_TENANT_ID` constant. No ENUMs.

#### MODEL: `Tenant(Base)`
- **Current State Summary:** Inherits `Base`. Comments claim it's a non-functional compatibility stub and tenant isolation is removed.
- **Gap Analysis (Technical Debt Identification):**
    - **Inheritance & Fields:** Does not inherit `BaseModel`. Redefines `id` (client-side default), `created_at`, `updated_at`. Lacks `created_by`, `updated_by` from `BaseModel`.
    - **Contradictory Purpose:**
        -   Comments stating "no functional purpose" and "tenant isolation removal" are CRITICALLY MISLEADING.
        -   `BaseModel` (used by most other models) enforces a `ForeignKey("tenants.id")` for its `tenant_id` field. This makes the `tenants` table (and this `Tenant` model) essential for referential integrity and the very tenant isolation `BaseModel` implements.
        -   `<!-- STOP_FOR_REVIEW: CRITICAL MISALIGNMENT. Tenant model comments contradict BaseModel's design. 'tenants' table is vital. Clarify multi-tenancy strategy and Tenant model's role. -->`
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Urgently review and clarify the multi-tenancy strategy and the `Tenant` model's intended role and definition. Reconcile comments with `BaseModel`'s actual behavior.
    - Consider aligning `Tenant` model with `BaseModel` standards (inheritance, `id` definition, inclusion of `created_by`/`updated_by`) if it is indeed a functional part of the system (which `BaseModel` implies).

---
