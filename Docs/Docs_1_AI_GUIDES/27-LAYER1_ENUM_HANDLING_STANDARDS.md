# 27: Enum Handling Standards

## 1. Purpose

This document defines the **MANDATORY** standard for all Enum definitions and usage within the ScraperSky project. Adherence to this standard is crucial for maintaining code clarity, preventing errors related to Enum mismatches (like those encountered in Work Order 29), and ensuring consistency across the codebase.

## 2. Core Principle: User-Facing vs. Backend Separation

Enums must be clearly designated as either **User-Facing** or **Backend/Database**.

- **User-Facing Enums:**

  - **Location:** Defined in API models (`src/models/api_models.py`) or specific Pydantic schemas (`src/schemas/*.py`).
  - **Purpose:** Used in API request/response models. Define the "public contract" for statuses or types visible to the frontend UI or external API consumers.
  - **Content:** Should use simple, user-friendly terms relevant to the API interaction.
  - **Example:** Statuses a user can select from a dropdown (`New`, `Selected`, `Archived`).

- **Backend/Database Enums:**

  - **Location:** Defined in SQLAlchemy models (`src/models/*.py`).
  - **Purpose:** Map directly to PostgreSQL ENUM types in the database. Represent internal system states or technical statuses.
  - **Content:** Can use more technical terms relevant to backend processes.
  - **Example:** Job processing states (`Queued`, `Processing`, `Completed`, `Error`).

- **CRITICAL Separation Rule:** Fields representing user-selectable status (e.g., `places_staging.status`, `domains.sitemap_curation_status`) **MUST** use the corresponding **User-Facing Enum** definition in API models. Fields representing internal technical states (e.g., `places_staging.deep_scan_status`, `jobs.status`) **MUST** use distinct **Backend/Database Enum** definitions. **DO NOT** mix members from one type into the other's definition (e.g., do not add `Processing` to a user-facing status Enum).

## 3. Mandatory Naming and Casing Conventions

Consistency is paramount. **ALL** Enums defined in this project **MUST** follow these conventions:

1.  **Enum Class Names:** `PascalCase`, ending with `Enum`.

    - _Correct:_ `PlaceStatusEnum`, `DeepScanStatusEnum`, `TaskStatusEnum`
    - _Incorrect:_ `place_status_enum`, `TASK_STATUS`, `Status`

2.  **Enum Member Names:** **`PascalCase`**.

    - _Correct:_ `NotAFit`, `DeepScanError`, `InProgress`, `EmailChangeTokenNew`
    - _Incorrect:_ `not_a_fit`, `deep_scan_error`, `IN_PROGRESS`, `email_change_token_new`

3.  **Enum String Values:** Must **EXACTLY** match the `PascalCase` Member Name.
    - _Correct:_
      ```python
      class TaskStatusEnum(str, Enum):
          InProgress = "InProgress"
          ManualReview = "ManualReview"
      ```
    - _Incorrect:_
      ```python
      # Incorrect: Value doesn't match member case/name
      class TaskStatusEnum(str, Enum):
          InProgress = "in_progress"
          MANUAL_REVIEW = "manual_review"
      ```
    - **Rationale:** This strict 1:1 mapping eliminates any ambiguity between the Python code representation and the database/string representation.

## 4. Database ENUM Type Definition

- When creating a corresponding ENUM type in the PostgreSQL database (manually or via migration), the defined labels **MUST** match the `PascalCase` string values defined in the Python Enum class.
  ```sql
  -- Example DB ENUM type
  CREATE TYPE task_status_enum AS ENUM (
      'Queued',
      'InProgress',
      'Completed',
      'Error',
      'ManualReview',
      'Cancelled',
      'Paused'
  );
  ```

## 5. SQLAlchemy Model Definition

- When defining an Enum column in a SQLAlchemy model (`src/models/*.py`):

  - Use `sqlalchemy.Enum`.
  - Reference the correct Python Enum class.
  - Specify the database `name` accurately.
  - Use `create_type=False` as we manage DB types manually.
  - Set `native_enum=True`.
  - Include `values_callable=lambda obj: [e.value for e in obj]` to ensure compatibility.

  ```python
  from sqlalchemy import Enum as SQLAlchemyEnum # Avoid naming collision
  from .base import Base
  # Assume TaskStatusEnum is defined elsewhere in models following the standard

  class Job(Base):
      # ... other columns ...
      status = Column(
          SQLAlchemyEnum(
              TaskStatusEnum,
              name="task_status_enum", # Actual name of the TYPE in PostgreSQL
              create_type=False,
              native_enum=True,
              values_callable=lambda obj: [e.value for e in obj]
          ),
          nullable=False,
          default=TaskStatusEnum.Queued # Use Enum member for default
      )
      # ... other columns ...
  ```

## 6. Usage in Code

- **Imports:** Always import the specific Enum class needed (e.g., `from ..models.place import PlaceStatusEnum`).
- **Comparisons:** Use the Enum member directly for comparisons (e.g., `if job.status == TaskStatusEnum.Completed:`).
- **Assignments:** Assign using the Enum member (e.g., `place.status = PlaceStatusEnum.Selected`).
- **SQLAlchemy Filtering/Updates:**
  - Prefer direct member comparison where supported: `.where(Place.status == PlaceStatusEnum.Selected)`
  - If the string value is explicitly needed (less common with modern SQLAlchemy): `.where(Place.status == PlaceStatusEnum.Selected.value)` or `.values(status=TaskStatusEnum.Completed.value)`. Verify necessity before using `.value`.
- **API Models (Pydantic):** Use the Enum class directly as the type hint. Pydantic handles validation against the member names/values.

## 7. Ensuring Consistency: Alignment Checklist

To prevent errors, it's crucial that Enum definitions and usage are consistent across different layers of the application. Use this table as a checklist:

| Layer                      | Location Example                                   | Standard Element     | Example (`PlaceStatusEnum` / `PlaceStagingStatusEnum`)                  | Consistency Requirement                                                                                                                                                                                                                                                                                                                            |
| :------------------------- | :------------------------------------------------- | :------------------- | :---------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Database Type              | PostgreSQL `CREATE TYPE`                           | Labels               | `place_status_enum` TYPE with LABELS 'New', 'Selected', 'NotAFit', etc. | DB Labels **MUST** match Backend Enum **Values**. (`PascalCase`)                                                                                                                                                                                                                                                                                   |
| Backend/DB Enum (Python)   | `src/models/place.py::PlaceStatusEnum`             | Class/Member/Value   | `PlaceStatusEnum` class, `NotAFit = "NotAFit"` member                   | **MUST** map 1:1 to DB Labels. **MUST** follow `PascalCase`.                                                                                                                                                                                                                                                                                       |
| API Enum (Python)          | `src/models/api_models.py::PlaceStagingStatusEnum` | Class/Member/Value   | `PlaceStagingStatusEnum` class, `Not_a_Fit = "Not a Fit"`               | Defines API contract. **MUST** map correctly to Backend Enum (often identical for user-facing status). **MUST** follow `PascalCase` for members (Note: Pydantic uses member _name_ for input validation by default, value for output). **Crucially**, only include members relevant to the specific API contract (e.g., no backend-only statuses). |
| Code Usage (Backend Logic) | `src/routers/*.py`, `src/services/*.py`            | Member Access/Assign | `if status == PlaceStatusEnum.Selected:`                                | **MUST** reference the correct Python **Backend/DB Enum** member.                                                                                                                                                                                                                                                                                  |
| Code Usage (API Layer)     | `src/routers/*.py`                                 | Type Hint/Validation | `update_req: LBStatusUpdate`, `status: LocalBusinessApiStatusEnum`      | **MUST** use the correct Python **API Enum** for request/response schemas and validation.                                                                                                                                                                                                                                                          |

**Key Takeaway:** A mismatch in casing or definition between the Database Labels, the Backend Python Enum, the API Python Enum, and the Code Usage **WILL** lead to errors.

## 8. Current Database Enum Inventory (As of 2025-04-14)

The following Enums were found in the database. **Note:** Several of these **DO NOT** conform to the `PascalCase` standard defined above and **SHOULD BE REFACTORED** when the relevant code/tables are next modified.

```json
[
  {
    "enum_type": "DomainExtractionStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "queued"
  },
  {
    "enum_type": "DomainExtractionStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "processing"
  },
  {
    "enum_type": "DomainExtractionStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "completed"
  },
  {
    "enum_type": "DomainExtractionStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "failed"
  },
  {
    "enum_type": "SitemapAnalysisStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "queued"
  },
  {
    "enum_type": "SitemapAnalysisStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "processing"
  },
  {
    "enum_type": "SitemapAnalysisStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "completed"
  },
  {
    "enum_type": "SitemapAnalysisStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "failed"
  },
  {
    "enum_type": "SitemapAnalysisStatusEnum", // Refactor Needed (lowercase)
    "enum_value": "submitted"
  },
  {
    "enum_type": "SitemapCurationStatusEnum", // Conforms (PascalCase/User-Friendly)
    "enum_value": "New"
  },
  {
    "enum_type": "SitemapCurationStatusEnum", // Conforms
    "enum_value": "Selected"
  },
  {
    "enum_type": "SitemapCurationStatusEnum", // Conforms
    "enum_value": "Maybe"
  },
  {
    "enum_type": "SitemapCurationStatusEnum", // Conforms (Note: DB Value has space) - Standard prefers 'NotAFit'
    "enum_value": "Not a Fit"
  },
  {
    "enum_type": "SitemapCurationStatusEnum", // Conforms
    "enum_value": "Archived"
  },
  {
    "enum_type": "aal_level", // Outside Project Scope? (auth schema)
    "enum_value": "aal1"
  },
  {
    "enum_type": "aal_level", // Outside Project Scope? (auth schema)
    "enum_value": "aal2"
  },
  {
    "enum_type": "aal_level", // Outside Project Scope? (auth schema)
    "enum_value": "aal3"
  },
  {
    "enum_type": "action", // Outside Project Scope? (audit schema?) - Needs PascalCase
    "enum_value": "INSERT"
  },
  {
    "enum_type": "action", // Outside Project Scope? - Needs PascalCase
    "enum_value": "UPDATE"
  },
  {
    "enum_type": "action", // Outside Project Scope? - Needs PascalCase
    "enum_value": "DELETE"
  },
  {
    "enum_type": "action", // Outside Project Scope? - Needs PascalCase
    "enum_value": "TRUNCATE"
  },
  {
    "enum_type": "action", // Outside Project Scope? - Needs PascalCase
    "enum_value": "ERROR"
  },
  {
    "enum_type": "app_role", // Refactor Needed (snake_case) -> PascalCase
    "enum_value": "basic"
  },
  {
    "enum_type": "app_role", // Refactor Needed (snake_case) -> PascalCase
    "enum_value": "admin"
  },
  {
    "enum_type": "app_role", // Refactor Needed (snake_case) -> PascalCase
    "enum_value": "super_admin"
  },
  {
    "enum_type": "app_role", // Refactor Needed (snake_case) -> PascalCase
    "enum_value": "system_admin"
  },
  {
    "enum_type": "code_challenge_method", // Outside Project Scope? (auth schema)
    "enum_value": "s256"
  },
  {
    "enum_type": "code_challenge_method", // Outside Project Scope? (auth schema)
    "enum_value": "plain"
  },
  {
    "enum_type": "contact_email_type_enum", // Refactor Needed (lowercase) -> PascalCase
    "enum_value": "service"
  },
  {
    "enum_type": "contact_email_type_enum", // Refactor Needed (lowercase) -> PascalCase
    "enum_value": "corporate"
  },
  {
    "enum_type": "contact_email_type_enum", // Refactor Needed (lowercase) -> PascalCase
    "enum_value": "free"
  },
  {
    "enum_type": "contact_email_type_enum", // Refactor Needed (lowercase) -> PascalCase
    "enum_value": "unknown"
  },
  {
    "enum_type": "deep_scan_status_enum", // Conforms (PascalCase/Backend)
    "enum_value": "Queued"
  },
  {
    "enum_type": "deep_scan_status_enum", // Conforms
    "enum_value": "Processing"
  },
  {
    "enum_type": "deep_scan_status_enum", // Conforms
    "enum_value": "Completed"
  },
  {
    "enum_type": "deep_scan_status_enum", // Conforms
    "enum_value": "Error"
  },
  {
    "enum_type": "equality_op", // Outside Project Scope? (realtime schema)
    "enum_value": "eq"
  },
  {
    "enum_type": "equality_op", // Outside Project Scope?
    "enum_value": "neq"
  },
  {
    "enum_type": "equality_op", // Outside Project Scope?
    "enum_value": "lt"
  },
  {
    "enum_type": "equality_op", // Outside Project Scope?
    "enum_value": "lte"
  },
  {
    "enum_type": "equality_op", // Outside Project Scope?
    "enum_value": "gt"
  },
  {
    "enum_type": "equality_op", // Outside Project Scope?
    "enum_value": "gte"
  },
  {
    "enum_type": "equality_op", // Outside Project Scope?
    "enum_value": "in"
  },
  {
    "enum_type": "factor_status", // Outside Project Scope? (auth schema)
    "enum_value": "unverified"
  },
  {
    "enum_type": "factor_status", // Outside Project Scope? (auth schema)
    "enum_value": "verified"
  },
  {
    "enum_type": "factor_type", // Outside Project Scope? (auth schema)
    "enum_value": "totp"
  },
  {
    "enum_type": "factor_type", // Outside Project Scope? (auth schema)
    "enum_value": "webauthn"
  },
  {
    "enum_type": "factor_type", // Outside Project Scope? (auth schema)
    "enum_value": "phone"
  },
  {
    "enum_type": "feature_priority", // Refactor Needed (snake_case) -> PascalCase
    "enum_value": "urgent"
  },
  {
    "enum_type": "feature_priority", // Refactor Needed
    "enum_value": "need_to_have"
  },
  {
    "enum_type": "feature_priority", // Refactor Needed
    "enum_value": "nice_to_have"
  },
  {
    "enum_type": "feature_priority", // Refactor Needed
    "enum_value": "someday"
  },
  {
    "enum_type": "feature_status", // Refactor Needed (lowercase/snake_case) -> PascalCase
    "enum_value": "new"
  },
  {
    "enum_type": "feature_status", // Refactor Needed
    "enum_value": "reviewed"
  },
  {
    "enum_type": "feature_status", // Refactor Needed
    "enum_value": "next_round"
  },
  {
    "enum_type": "feature_status", // Refactor Needed
    "enum_value": "back_burner"
  },
  {
    "enum_type": "feature_status", // Refactor Needed
    "enum_value": "someday"
  },
  {
    "enum_type": "feature_status", // Refactor Needed
    "enum_value": "in_progress"
  },
  {
    "enum_type": "feature_status", // Refactor Needed
    "enum_value": "completed"
  },
  {
    "enum_type": "feature_status", // Refactor Needed
    "enum_value": "rejected"
  },
  {
    "enum_type": "key_status", // Outside Project Scope? (pgsodium schema?)
    "enum_value": "default"
  },
  {
    "enum_type": "key_status", // Outside Project Scope?
    "enum_value": "valid"
  },
  {
    "enum_type": "key_status", // Outside Project Scope?
    "enum_value": "invalid"
  },
  {
    "enum_type": "key_status", // Outside Project Scope?
    "enum_value": "expired"
  },
  {
    "enum_type": "key_type", // Outside Project Scope? (pgsodium schema?)
    "enum_value": "aead-ietf"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "aead-det"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "hmacsha512"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "hmacsha256"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "auth"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "shorthash"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "generichash"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "kdf"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "secretbox"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "secretstream"
  },
  {
    "enum_type": "key_type", // Outside Project Scope?
    "enum_value": "stream_xchacha20"
  },
  {
    "enum_type": "one_time_token_type", // Refactor Needed (snake_case) -> PascalCase
    "enum_value": "confirmation_token"
  },
  {
    "enum_type": "one_time_token_type", // Refactor Needed
    "enum_value": "reauthentication_token"
  },
  {
    "enum_type": "one_time_token_type", // Refactor Needed
    "enum_value": "recovery_token"
  },
  {
    "enum_type": "one_time_token_type", // Refactor Needed
    "enum_value": "email_change_token_new"
  },
  {
    "enum_type": "one_time_token_type", // Refactor Needed
    "enum_value": "email_change_token_current"
  },
  {
    "enum_type": "one_time_token_type", // Refactor Needed
    "enum_value": "phone_change_token"
  },
  {
    "enum_type": "place_status_enum", // Conforms (PascalCase/User-Friendly)
    "enum_value": "New"
  },
  {
    "enum_type": "place_status_enum", // Conforms
    "enum_value": "Selected"
  },
  {
    "enum_type": "place_status_enum", // Conforms
    "enum_value": "Maybe"
  },
  {
    "enum_type": "place_status_enum", // Conforms (Note: DB Value has space) - Standard prefers 'NotAFit'
    "enum_value": "Not a Fit"
  },
  {
    "enum_type": "place_status_enum", // Conforms
    "enum_value": "Archived"
  },
  {
    "enum_type": "sitemap_file_status_enum", // Conforms (PascalCase/Backend)
    "enum_value": "Pending"
  },
  {
    "enum_type": "sitemap_file_status_enum", // Conforms
    "enum_value": "Processing"
  },
  {
    "enum_type": "sitemap_file_status_enum", // Conforms
    "enum_value": "Completed"
  },
  {
    "enum_type": "sitemap_file_status_enum", // Conforms
    "enum_value": "Error"
  },
  {
    "enum_type": "task_status", // Refactor Needed (lowercase/snake_case) -> PascalCase
    "enum_value": "queued"
  },
  {
    "enum_type": "task_status", // Refactor Needed
    "enum_value": "in_progress"
  },
  {
    "enum_type": "task_status", // Refactor Needed
    "enum_value": "complete"
  },
  {
    "enum_type": "task_status", // Refactor Needed
    "enum_value": "error"
  },
  {
    "enum_type": "task_status", // Refactor Needed
    "enum_value": "manual_review"
  },
  {
    "enum_type": "task_status", // Refactor Needed
    "enum_value": "cancelled"
  },
  {
    "enum_type": "task_status", // Refactor Needed
    "enum_value": "paused"
  }
]
```

## 9. Enforcement

- **New Code:** All new Enum definitions and usage **MUST** strictly adhere to this standard.
- **Existing Code:** When modifying existing code that uses non-compliant Enums (e.g., those marked "Refactor Needed" above), the Enums **MUST** be refactored to comply with this standard as part of the change. This includes:
  - Updating the Python Enum definition (class name, member names, values).
  - Updating the corresponding SQLAlchemy model definitions.
  - Updating all code locations that reference the old Enum members/values.
  - **Potentially** updating the database ENUM type definition itself (e.g., `ALTER TYPE ... RENAME VALUE ...`, `ALTER TYPE ... ADD VALUE ...`) if labels need changing, although simply updating the Python code to use `PascalCase` members mapping to existing DB labels might be sufficient if changing DB labels is too disruptive. **Prioritize aligning Python code first.**
- **Code Reviews:** Adherence to this standard should be checked during code reviews.

This guide establishes a clear, unambiguous, and strict standard to prevent future confusion.
