# Layer 1: Models & ENUMs - Audit Report (Chunk)

_This is a segment of the full Layer 1 audit report, focusing on a specific component._

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

