# Layer 1 Architectural Blueprint

## 1. Guiding Principle: Simplicity, Consistency, and Compliance

This document defines the canonical architectural patterns for Layer 1 (Models & ENUMs) of the ScraperSky backend. Its purpose is to serve as the "Golden Path" for all future development and a reference for maintaining architectural integrity. Adherence to these patterns is mandatory to prevent technical debt and ensure a scalable, maintainable codebase.

---

## 2. The Golden Path: Correct Implementation Patterns

### 2.1. Model Inheritance

*   **Rule:** All ORM models **MUST** inherit from `src.models.base.BaseModel` and **ONLY** from `BaseModel`.
*   **Rationale:** `BaseModel` provides the standardized `id` (UUID), `created_at`, and `updated_at` columns. Inheriting from any other base (like SQLAlchemy's `Base`) introduces schema conflicts and violates the DRY principle.

    ```python
    # CORRECT
    from .base import BaseModel

    class Contact(BaseModel):
        __tablename__ = "contacts"
        # ... model columns ...
    ```

### 2.2. Primary & Foreign Keys

*   **Rule:** Foreign key columns **MUST** be named with an `_id` suffix (e.g., `tenant_id`, `created_by_id`). They **MUST** use `ForeignKey` to point to the `id` column of the parent table.
*   **Rationale:** This convention provides immediate clarity on the nature of the column and its relationship to other tables. It is essential for database integrity and predictable query patterns.

    ```python
    # CORRECT
    from sqlalchemy import Column, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID as PGUUID

    # Tenant isolation is mandatory
    tenant_id = Column(PGUUID, ForeignKey("tenants.id"), nullable=False, index=True)

    # Ownership tracking
    created_by_id = Column(PGUUID, ForeignKey("profiles.id"), nullable=True)
    ```

### 2.3. ENUM Definitions

*   **Rule:** All ENUMs **MUST** be defined in the central `src.models.enums.py` file. They **MUST** inherit from `(str, Enum)`. The database-level type name **MUST** be `snake_case`.
*   **Rationale:** Centralization prevents code duplication and conflicting definitions. Standardizing on `(str, Enum)` and `snake_case` names ensures consistency and compatibility with our database schema.

    ```python
    # CORRECT (in enums.py)
    from enum import Enum

    class TaskStatus(str, Enum):
        PENDING = "Pending"
        RUNNING = "Running"
        COMPLETE = "Complete"

    # CORRECT (in a model file)
    from .enums import TaskStatus
    from sqlalchemy import Enum as SQLAlchemyEnum

    status = Column(
        SQLAlchemyEnum(TaskStatus, name="task_status", create_type=False),
        nullable=False,
        default=TaskStatus.PENDING
    )
    ```

### 2.4. Naming Conventions

*   **Rule:** Table names (`__tablename__`) **MUST** be plural and `snake_case` (e.g., `batch_jobs`, `sitemap_files`).
*   **Rationale:** This is a standard, widely-accepted convention that makes the database schema easy to read and understand.

---

## 3. Anti-Patterns: Violations to Actively Prevent

This section documents the specific anti-patterns discovered and remediated in Layer 1. These are architectural violations and **MUST** be avoided in all future code.

### 3.1. A-P 1: Dual Inheritance

*   **Description:** Inheriting from both `Base` and `BaseModel`.
*   **Consequence:** Redundant columns, schema conflicts.
*   **Resolution:** Inherit only from `BaseModel`.

    ```python
    # INCORRECT
    from .base import Base, BaseModel

    class Contact(Base, BaseModel): # This is wrong
        # ...
    ```

### 3.2. A-P 2: Local ENUM Definitions

*   **Description:** Defining ENUMs inside a model file instead of the central `enums.py`.
*   **Consequence:** Code duplication, risk of inconsistent status values for the same logical state.
*   **Resolution:** Move all ENUMs to `src.models.enums.py` and import them.

### 3.3. A-P 3: Inconsistent Foreign Keys

*   **Description:** Using names without the `_id` suffix or failing to include a `ForeignKey` constraint.
*   **Consequence:** Broken relationships, loss of database integrity, inability to perform joins correctly.
*   **Resolution:** Always use the `_id` suffix and a `ForeignKey` constraint pointing to the parent's `id`.

### 3.4. A-P 4: Improper Naming

*   **Description:** Using non-standard table names (e.g., `PascalCase` or singular) or database ENUM type names.
*   **Consequence:** An inconsistent and hard-to-navigate schema.
*   **Resolution:** Strictly adhere to `snake_case` and pluralization rules.
