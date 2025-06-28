# Layer 1: Models & ENUMs - Audit Report (Chunk)

_This is a segment of the full Layer 1 audit report, focusing on a specific component._

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

