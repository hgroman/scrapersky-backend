# Layer 1: Models & ENUMs - Audit Report (Chunk)

_This is a segment of the full Layer 1 audit report, focusing on a specific component._

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

