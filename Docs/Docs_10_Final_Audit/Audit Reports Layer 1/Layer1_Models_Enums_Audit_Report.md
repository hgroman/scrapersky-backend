# Layer 1: Models & ENUMs - Audit Report

**Version:** 1.0
**Date:** 2025-05-20
**Auditor:** Cascade AI Auditor

**Reference Documents:**
- `Layer-1.1-Models_Enums_Blueprint.md`
- `Layer-1.3-Models_Enums_AI_Audit_SOP.md`

---

## Audit Findings

This report details the findings of the Layer 1 (Models & ENUMs) audit. Each component within the `src/models/` directory has been assessed against the criteria defined in the Layer 1 Blueprint.

### File: `src/models/__init__.py`

This file primarily handles imports and defines the following ENUMs. No SQLAlchemy models are defined in this file.

#### 1. ENUM: `SitemapType`
- **Component Name:** `ENUM: SitemapType`
- **Current State Summary:** Defines types of sitemaps.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.2.2 (General ENUMs) - Base Class:** Compliant. Inherits from `(str, Enum)`.
    - **Blueprint 2.2.2 (General ENUMs) - Naming:** Compliant. Name is `SitemapType` (PascalCase).
    - **Blueprint 2.2.2 (General ENUMs) - Values:** Compliant. Values are meaningful strings (`index`, `standard`, `image`, `video`, `news`).
    - **Blueprint 2.2.1.3 (Location - for ENUMs):** Non-compliant. Blueprint prefers ENUMs in relevant model files or a shared `enums.py`. `__init__.py` is not standard for ENUM definitions.
        - `<!-- NEED_CLARITY: Is 'src/models/__init__.py' an acceptable location for generic Enums like SitemapType, or should it be moved to 'src/models/enums.py' or a relevant model file like 'sitemap.py'? -->`
- **Prescribed Refactoring Actions:**
    - Consider moving `SitemapType` to `src/models/enums.py` or a more specific model file (e.g., `sitemap.py`) after clarification.

#### 2. ENUM: `DiscoveryMethod`
- **Component Name:** `ENUM: DiscoveryMethod`
- **Current State Summary:** Defines how a sitemap was discovered.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.2.2 (General ENUMs) - Base Class:** Compliant. Inherits from `(str, Enum)`.
    - **Blueprint 2.2.2 (General ENUMs) - Naming:** Compliant. Name is `DiscoveryMethod` (PascalCase).
    - **Blueprint 2.2.2 (General ENUMs) - Values:** Compliant. Values are meaningful strings (`robots_txt`, `common_path`, `sitemap_index`, `html_link`, `manual`).
    - **Blueprint 2.2.1.3 (Location - for ENUMs):** Non-compliant. Blueprint prefers ENUMs in relevant model files or a shared `enums.py`.
        - `<!-- NEED_CLARITY: Is 'src/models/__init__.py' an acceptable location for generic Enums like DiscoveryMethod, or should it be moved to 'src/models/enums.py' or a relevant model file like 'sitemap.py'? -->`
- **Prescribed Refactoring Actions:**
    - Consider moving `DiscoveryMethod` to `src/models/enums.py` or a more specific model file (e.g., `sitemap.py`) after clarification.

#### 3. ENUM: `TaskStatus`
- **Component Name:** `ENUM: TaskStatus`
- **Current State Summary:** Defines common status values for tasks and jobs.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.2.2 (Base Class):** Compliant. Inherits from `(str, Enum)`.
    - **Blueprint 2.2.2 (Naming - General ENUMs):** Compliant. Name is `TaskStatus` (PascalCase).
    - **Blueprint 2.2.2 (Standard Values - Curation/Processing Status):** Potential non-compliance. Values (`PENDING = "Queued"`, `RUNNING = "InProgress"`, `COMPLETE = "Completed"`, `FAILED = "Error"`, `CANCELLED = "Cancelled"`) deviate from strictly defined `WorkflowNameTitleCaseCurationStatus` or `WorkflowNameTitleCaseProcessingStatus` standard values (e.g., Blueprint specifies `Processing = "Processing"`, `Complete = "Complete"`).
        - `<!-- NEED_CLARITY: TaskStatus seems like a general status enum. Does it need to conform to the strict values of 'WorkflowNameTitleCaseCurationStatus' or 'WorkflowNameTitleCaseProcessingStatus' (e.g., using 'Processing' instead of 'InProgress', 'Complete' instead of 'Completed')? Or is it acceptable as a general enum with these values? The blueprint is very specific about *workflow* status enums. -->`
    - **Blueprint 2.2.1.3 (Location - for ENUMs):** Non-compliant. Blueprint prefers ENUMs in relevant model files or a shared `enums.py`. This generic ENUM is a prime candidate for `src/models/enums.py`.
- **Prescribed Refactoring Actions:**
    - Clarify if `TaskStatus` values should align with standard Blueprint status values (e.g., "Processing", "Complete").
    - Move `TaskStatus` to `src/models/enums.py`.

---

### File: `src/models/api_models.py`

This file primarily contains Pydantic `BaseModel` classes, which are considered Layer 2 (Schemas) and are **out of scope** for this Layer 1 audit. However, the file also defines several Python ENUMs which are assessed below:

#### 1. ENUM: `SitemapType` (around line 100)
- **Component Name:** `ENUM: SitemapType`
- **Current State Summary:** Defines types of sitemaps that can be encountered. Includes `UNKNOWN`.
- **Gap Analysis (Technical Debt Identification):**
    - **Redefinition:** This Enum `SitemapType` is also defined in `src/models/__init__.py`. This is a clear duplication.
        - `<!-- STOP_FOR_REVIEW: SitemapType is defined in both src/models/__init__.py and src/models/api_models.py. This duplication needs to be resolved. Which one is authoritative or should they be consolidated? -->`
    - **Blueprint 2.2.2 (General ENUMs) - Base Class:** Compliant. Inherits from `(str, Enum)`.
    - **Blueprint 2.2.2 (General ENUMs) - Naming:** Compliant. Name is `SitemapType` (PascalCase).
    - **Blueprint 2.2.2 (General ENUMs) - Values:** Values are meaningful strings (`index`, `standard`, `image`, `video`, `news`, `unknown`). The `unknown` value is new compared to the `__init__.py` version.
    - **Blueprint 2.2.1.3 (Location - for ENUMs):** Non-compliant. If this is a data foundation Enum, it should ideally be in `src/models/enums.py` or a relevant SQLAlchemy model file. Pydantic model files (`api_models.py`) are not the standard location for Layer 1 Enums.
- **Prescribed Refactoring Actions:**
    - Resolve duplication with `SitemapType` in `src/models/__init__.py`. Consolidate into a single definition in an appropriate Layer 1 location (e.g., `src/models/enums.py` or `src/models/sitemap.py`).
    - Ensure the consolidated version includes all necessary values (e.g., `unknown`).

#### 2. ENUM: `DiscoveryMethod` (around line 111)
- **Component Name:** `ENUM: DiscoveryMethod`
- **Current State Summary:** Defines how a sitemap was discovered.
- **Gap Analysis (Technical Debt Identification):**
    - **Redefinition:** This Enum `DiscoveryMethod` is also defined in `src/models/__init__.py`. This is a clear duplication.
        - `<!-- STOP_FOR_REVIEW: DiscoveryMethod is defined in both src/models/__init__.py and src/models/api_models.py. This duplication needs to be resolved. Which one is authoritative or should they be consolidated? -->`
    - **Blueprint 2.2.2 (General ENUMs) - Base Class:** Compliant. Inherits from `(str, Enum)`.
    - **Blueprint 2.2.2 (General ENUMs) - Naming:** Compliant. Name is `DiscoveryMethod` (PascalCase).
    - **Blueprint 2.2.2 (General ENUMs) - Values:** Compliant. Values are meaningful strings (`robots_txt`, `common_path`, `sitemap_index`, `html_link`, `manual`).
    - **Blueprint 2.2.1.3 (Location - for ENUMs):** Non-compliant. If this is a data foundation Enum, it should ideally be in `src/models/enums.py` or a relevant SQLAlchemy model file.
- **Prescribed Refactoring Actions:**
    - Resolve duplication with `DiscoveryMethod` in `src/models/__init__.py`. Consolidate into a single definition in an appropriate Layer 1 location (e.g., `src/models/enums.py` or `src/models/sitemap.py`).

#### 3. ENUM: `PlaceStagingStatusEnum` (around line 239)
- **Component Name:** `ENUM: PlaceStagingStatusEnum`
- **Current State Summary:** "Possible statuses for a place in the staging table. Mirrors DB PlaceStatusEnum."
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.2.2 (Naming):** Non-compliant. Name ends with "Enum" (`PlaceStagingStatusEnum`). Blueprint discourages "Enum" suffix.
    - **Blueprint 2.2.2 (Base Class):** `<!-- NEED_CLARITY: Does PlaceStagingStatusEnum inherit from (str, Enum)? The outline does not show its base class explicitly. -->` (Assuming non-compliance if not `(str, Enum)`).
    - **Blueprint 2.2.2 (Standard Values):** Non-compliant. Values (`NEW = "New"`, `Selected = "Selected"`, `Maybe = "Maybe"`, `Not_a_Fit = "Not a Fit"`, `ARCHIVED = "Archived"`) deviate from standard Curation/Processing status values. Specifically, `"Selected"` is non-standard (vs. `"Queued"`), and `"Maybe"`, `"Not a Fit"`, `"Archived"` are custom additions not fitting the primary CurationStatus pattern without following the 'Justified Non-Standard User States' protocol.
        - `<!-- STOP_FOR_REVIEW: PlaceStagingStatusEnum uses non-standard values ('Selected', 'Maybe', 'Not a Fit', 'Archived') for what appears to be a curation status. This deviates significantly from Blueprint 2.2.2. How should this be reconciled? Does 'PlaceStaging' count as a distinct workflow requiring its own set of standard status enums, or should these custom states be handled via the 'Justified Non-Standard User States' protocol (separate field and Enum)? -->`
    - **Blueprint 2.2.1.3 (Location - for ENUMs):** Non-compliant. If it mirrors a DB Enum and is data foundation, it should be in `src/models/place.py` (or a `place_staging.py` model) or `src/models/enums.py`.
- **Prescribed Refactoring Actions:**
    - Rename to `PlaceStagingStatus`.
    - Confirm/change base class to `(str, Enum)`.
    - Address non-standard values per clarification from `STOP_FOR_REVIEW` (align with CurationStatus, or implement as justified non-standard state).
    - Move to the relevant SQLAlchemy model file or `src/models/enums.py`.

#### 4. ENUM: `LocalBusinessApiStatusEnum` (around line 300)
- **Component Name:** `ENUM: LocalBusinessApiStatusEnum`
- **Current State Summary:** "Possible statuses for a local business, matching PlaceStatusEnum."
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.2.2 (Naming):** Non-compliant. Ends with "Enum" and contains "Api".
    - **Blueprint 2.2.2 (Base Class):** `<!-- NEED_CLARITY: Does LocalBusinessApiStatusEnum inherit from (str, Enum)? -->`
    - **Blueprint 2.2.2 (Standard Values):** Non-compliant. Values (`New = "New"`, `Selected = "Selected"`, `Maybe = "Maybe"`, `Not_a_Fit = "Not a Fit"`, `Archived = "Archived"`) are non-standard for Curation/Processing status. Docstring implies linkage to `PlaceStatusEnum`, which also has issues.
        - `<!-- STOP_FOR_REVIEW: LocalBusinessApiStatusEnum has non-standard values and its name includes 'Api'. It also 'matches PlaceStatusEnum'. How should this be reconciled with Blueprint 2.2.2 and potentially with PlaceStagingStatusEnum? -->`
    - **Blueprint 2.2.1.3 (Location - for ENUMs):** Non-compliant. Should be with `local_business.py` model or in `src/models/enums.py`.
- **Prescribed Refactoring Actions:**
    - Rename to `LocalBusinessStatus` or similar.
    - Confirm/change base class to `(str, Enum)`.
    - Address non-standard values and potential redundancy per clarification.
    - Move to the relevant SQLAlchemy model file or `src/models/enums.py`.

#### 5. ENUM: `SitemapCurationStatusApiEnum` (around line 343)
- **Component Name:** `ENUM: SitemapCurationStatusApiEnum`
- **Current State Summary:** Seems to define curation statuses for sitemaps.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.2.2 (Naming):** Non-compliant. Ends with "ApiEnum". Expected format: `{WorkflowNameTitleCase}CurationStatus` (e.g., `SitemapCurationStatus`).
    - **Blueprint 2.2.2 (Base Class):** `<!-- NEED_CLARITY: Does SitemapCurationStatusApiEnum inherit from (str, Enum)? -->`
    - **Blueprint 2.2.2 (Standard Values):** Non-compliant. Values (`New = "New"`, `Selected = "Selected"`, `Maybe = "Maybe"`, `Not_a_Fit = "Not a Fit"`, `Archived = "Archived"`) are non-standard for a CurationStatus enum as per Blueprint (expects `New`, `Queued`, `Processing`, `Complete`, `Error`, `Skipped`).
        - `<!-- STOP_FOR_REVIEW: SitemapCurationStatusApiEnum uses non-standard values for a CurationStatus. How does this align with the mandatory values in Blueprint 2.2.2 for {WorkflowNameTitleCase}CurationStatus? -->`
    - **Blueprint 2.2.1.3 (Location - for ENUMs):** Non-compliant. Should be in `src/models/sitemap.py` or `src/models/enums.py`.
- **Prescribed Refactoring Actions:**
    - Rename to `SitemapCurationStatus`.
    - Confirm/change base class to `(str, Enum)`.
    - Align values with mandatory CurationStatus set or use 'Justified Non-Standard User States' protocol.
    - Move to `src/models/sitemap.py` or `src/models/enums.py`.

---

### File: `src/models/base.py`

This file defines the SQLAlchemy declarative base and a common `BaseModel` mixin. No direct table models or ENUMs are defined here. The `model_to_dict` utility function is out of scope for Layer 1 audit.

#### 1. Component: `Base = declarative_base()`
- **Component Name:** `SQLAlchemy Declarative Base`
- **Current State Summary:** Standard SQLAlchemy `declarative_base()` instantiation.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.1 (ORM Exclusivity):** Compliant. Uses SQLAlchemy.
    - **Blueprint 2.1.2 (Declarative Base):** Compliant. Uses `declarative_base()`.
- **Prescribed Refactoring Actions:** None.

#### 2. Component: `class BaseModel` (Mixin)
- **Component Name:** `CLASS: BaseModel (Mixin)`
- **Current State Summary:** A mixin class providing `id`, `created_at`, and `updated_at` columns for other models.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.3 (Common Base Model/Mixin):** Compliant. The file provides a `BaseModel` mixin.
    - **Blueprint 2.1.3.1 (Standard Fields in Mixin):** All fields (`id`, `created_at`, `updated_at`) are compliant with type, primary key, default, nullability, and auto-update requirements.
- **Prescribed Refactoring Actions:** None. `BaseModel` is fully compliant.

---

### File: `src/models/batch_job.py`

This file defines the `BatchJob` SQLAlchemy model. No Python ENUMs are defined in this file.

#### 1. MODEL: `BatchJob(Base, BaseModel)`
- **Component Name:** `MODEL: BatchJob`
- **Current State Summary:** Represents batch processing jobs, inheriting from `Base` and `BaseModel`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4 (Inheritance):** Compliant. Inherits from `Base` and `BaseModel`.
    - **Blueprint 2.1.5 (Table Name):** `__tablename__ = "batch_jobs"` - Compliant.
    - **Blueprint 2.1.6 (Primary Key - id):** Non-compliant. `BatchJob.id` is overridden to `Integer`, violating Blueprint 2.1.6.1 which mandates UUID primary keys. An additional `id_uuid` column exists.
        - `<!-- STOP_FOR_REVIEW: BatchJob.id overrides the standard UUID primary key from BaseModel with an Integer primary key. This violates Blueprint 2.1.6.1. This needs to be reconciled. Was this intentional for a specific reason not covered by the Blueprint? -->`
    - **Blueprint 2.1.7 (Relationships):** `jobs` and `domains` relationships appear compliant, assuming corresponding back-populating relationships exist in `Job` and `Domain` models.
    - **Blueprint 2.1.8 (Column Naming):** Generally compliant (snake_case). Specific points:
        - `id_uuid`: Non-standard and redundant if PK `id` were UUID.
        - `status`: Currently `String`. Should ideally be an Enum type if values are fixed.
            - `<!-- NEED_CLARITY: The 'status' column in BatchJob is a String with default 'pending'. The docstring mentions 'pending, running, complete, failed, partial'. Should this be an Enum (e.g., BatchJobStatus Enum) as per Blueprint 2.1.8.3 for columns with fixed sets of values? -->`
    - **Blueprint 2.1.8.1 (Foreign Keys):** `tenant_id` and `created_by` (both PGUUID) appear to be foreign keys. Their naming is acceptable under the `related_table_name_id` convention. `ForeignKey` constraints are not shown in the snippet.
        - `<!-- NEED_CLARITY: Are tenant_id and created_by actual foreign keys with constraints defined? The snippet doesn't show ForeignKey definitions. -->`
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Revert `BatchJob.id` primary key to use the UUID field provided by `BaseModel`. Remove the `id = Column(Integer, ...)` override and the redundant `id_uuid` column to comply with Blueprint 2.1.6.1.
    - Consider converting the `status` column to use a new Enum (e.g., `BatchJobStatus(str, Enum)`).
    - Clarify and ensure `ForeignKey` constraints are defined for `tenant_id` and `created_by` if they are indeed foreign keys.

---

### File: `src/models/contact.py`

This file defines the `Contact` SQLAlchemy model and several related Python ENUMs.

#### ENUMs in `src/models/contact.py`

1.  **ENUM: `ContactEmailTypeEnum`**: Compliant with Blueprint (Base Class, Naming, Values, Location).
    -   **Prescribed Refactoring Actions:** None.

2.  **ENUM: `ContactCurationStatus`**: Compliant (Base Class, Naming, Values, Location).
    -   **Prescribed Refactoring Actions:** None.

3.  **ENUM: `ContactProcessingStatus`**: Compliant (Base Class, Naming, Values, Location).
    -   **Prescribed Refactoring Actions:** None.

4.  **ENUM: `HubotSyncStatus`**:
    -   **Gap Analysis:** Potential typo in name ("Hubot" vs "HubSpot"). Otherwise compliant.
        -   `<!-- NEED_CLARITY: Is 'HubotSyncStatus' a typo? Should it be 'HubSpotSyncStatus' to match the likely workflow name 'HubSpot'? -->`
    -   **Prescribed Refactoring Actions:** Clarify and correct name if it's a typo.

5.  **ENUM: `HubSyncProcessingStatus`**:
    -   **Gap Analysis:** Potential typo/abbreviation in name ("HubSync" vs "HubSpotSync"). Otherwise compliant.
        -   `<!-- NEED_CLARITY: Is 'HubSyncProcessingStatus' a typo/abbreviation? Should it be 'HubSpotSyncProcessingStatus' for clarity and consistency with the likely workflow name 'HubSpot Sync'? -->`
    -   **Prescribed Refactoring Actions:** Clarify and correct name if it's a typo/abbreviation.

#### MODEL: `Contact(Base, BaseModel)`
- **Component Name:** `MODEL: Contact`
- **Current State Summary:** Represents contacts, inherits from `Base` and `BaseModel`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4 & 2.1.5 (Inheritance, Table Name):** Compliant.
    - **Blueprint 2.1.6 (Primary Key - id):** `Contact.id` redefines the `id` column from `BaseModel`. While compatible, this is redundant. Should rely on `BaseModel.id`.
        -   `<!-- NEED_CLARITY: Contact.id redefines the id column, though compatibly with BaseModel. Is this intentional or can it rely on BaseModel.id? -->`
    - **Blueprint 2.1.7 (Relationships):** `domain`, `page`, `job` relationships appear compliant.
    - **Blueprint 2.1.8 (Column Naming & Types):** Generally compliant.
    - **Blueprint 2.1.8.1 (Foreign Keys):** `domain_id`, `page_id` are compliant. `source_job_id` references `jobs.job_id`.
        -   `<!-- NEED_CLARITY: source_job_id ForeignKey refers to 'jobs.job_id'. Is 'job_id' the primary key of the 'jobs' table, or just a unique column? The standard PK is 'id'. -->`
    - **Blueprint 2.1.8.3 (ENUM Database Type Naming):** The `name` attribute for `SQLAlchemyEnum` (e.g., `contactcurationstatus`, `hubotsyncstatus`) is non-compliant (not snake_case).
        -   `<!-- STOP_FOR_REVIEW: The 'name' attribute for SQLAlchemyEnum in Contact model (e.g., 'contactcurationstatus', 'hubotsyncstatus') does not follow snake_case convention as per Blueprint 2.1.8.3. These should be updated (e.g., 'contact_curation_status'). This refers to the DB enum type name. -->`
    - **Blueprint 2.1.9 (Constraints):** `UniqueConstraint` is compliant.
- **Prescribed Refactoring Actions:**
    - Prefer relying on `BaseModel.id` instead of re-defining `Contact.id`.
    - If "Hubot"/"HubSync" are typos in Enum names, correct them and update related `SQLAlchemyEnum` `name` attributes (e.g., to `hubspot_sync_status`).
    - **CRITICAL:** Correct the `name` attribute in all `SQLAlchemyEnum` declarations to use snake_case (e.g., `contact_curation_status`, `contact_processing_status`, `hubspot_sync_status`, `hubspot_sync_processing_status`).
    - Clarify if `jobs.job_id` (referenced by `source_job_id`) is the PK of the `jobs` table; standard is `id`.

---

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

### File: `src/models/job.py`

This file defines the `Job` SQLAlchemy model. No Python ENUMs are defined in this file.

#### 1. MODEL: `Job(Base, BaseModel)`
- **Component Name:** `MODEL: Job`
- **Current State Summary:** Represents background processing tasks, inherits `Base`, `BaseModel`.
- **Gap Analysis (Technical Debt Identification):**
    - **Blueprint 2.1.4 & 2.1.5 (Inheritance, Table Name):** Compliant.
    - **Blueprint 2.1.6 (Primary Key - id):** CRITICAL VIOLATION. `Job.id` is overridden to `Integer`, violating Blueprint 2.1.6.1 (must be UUID). A separate `job_id` (UUID) column exists.
        -   `<!-- STOP_FOR_REVIEW: Job.id overrides BaseModel's UUID PK with an Integer PK. Critical violation of Blueprint 2.1.6.1. -->`
    - **Blueprint 2.1.8 (Column Naming & Types):**
        - `job_type`: `String`. Consider Enum if values are fixed.
            -   `<!-- NEED_CLARITY: Job.job_type is String. Consider Enum (e.g., JobTypeEnum) if fixed set of types. -->`
        - `tenant_id` (String) and `tenant_id_uuid` (PGUUID, no FK): CRITICAL VIOLATION. Non-compliant with Blueprint 2.1.8.2 (expects single PGUUID `tenant_id` with FK from `BaseModel`).
            -   `<!-- STOP_FOR_REVIEW: Job model has tenant_id (String) and tenant_id_uuid (PGUUID, no FK). Violates Blueprint 2.1.8.2. BaseModel should provide compliant tenant_id. -->`
        - `status`: `String`. Consider Enum (e.g., `TaskStatus` or `JobStatusEnum`).
            -   `<!-- NEED_CLARITY: Job.status is String. Consider using TaskStatus Enum or new JobStatusEnum. -->`
        - `batch_id`: `String`, FK to `batch_jobs.batch_id` (which is UUID). Type mismatch.
            -   `<!-- STOP_FOR_REVIEW: Job.batch_id (String) FKs to batch_jobs.batch_id (UUID). Job.batch_id should be PGUUID. -->`
    - **Blueprint 2.1.7 (Relationships):** `domain`, `batch` relationships appear compliant.
- **Prescribed Refactoring Actions:**
    - **CRITICAL:** Revert `Job.id` to use `BaseModel`'s UUID PK. Clarify role of existing `job_id` (UUID) column.
    - **CRITICAL:** Remove `job.tenant_id` (String) and `job.tenant_id_uuid`. Rely on `BaseModel`'s compliant `tenant_id`.
    - **CRITICAL:** Change `Job.batch_id` type from `String` to `PGUUID`.
    - Consider converting `job_type` and `status` columns to use Enums.

---

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
