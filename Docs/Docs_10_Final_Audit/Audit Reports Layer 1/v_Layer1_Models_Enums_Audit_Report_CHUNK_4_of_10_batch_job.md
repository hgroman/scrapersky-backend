# Layer 1: Models & ENUMs - Audit Report (Chunk)

_This is a segment of the full Layer 1 audit report, focusing on a specific component._

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

