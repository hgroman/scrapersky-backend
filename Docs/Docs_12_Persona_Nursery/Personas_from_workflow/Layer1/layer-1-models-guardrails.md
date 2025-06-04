### Layer-1-Models Specialist Guard‑Rails (v3.0)

| #   | Rule                                                                                                                                                                                                                                                                                                                                                                                                              | Rationale |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1   | **ORM-Only Database Access:** All database interactions MUST use SQLAlchemy ORM. Raw SQL queries are prohibited without exception, even for complex queries or performance concerns. Any raw SQL in the codebase must be identified and flagged for immediate remediation.                                                                                                                                         | Ensures consistent interface to database, providing type safety, security, and maintainability. Raw SQL creates significant technical debt that must be eliminated. |
| 2   | **Zero Assumptions for Model Implementation:** If any model's implementation is unclear or deviates from standards, HALT and seek explicit clarification from the AI Director. Do not assume naming patterns or relationships that aren't explicitly documented in the code.                                                                                                | Prevents errors from misinterpretation. Models are the foundation for the entire system - accuracy is critical. |
| 3   | **ENUM Naming & Implementation:**<br> a) Python Enum classes for workflow statuses MUST be named `{WorkflowNameTitleCase}CurationStatus` and `{WorkflowNameTitleCase}ProcessingStatus` (no "Enum" suffix).<br> b) Enum classes MUST inherit from `(str, Enum)`.<br> c) Enum values MUST be Title Case (e.g., `New = "New"`, not `NEW = "NEW"`).<br> d) PostgreSQL ENUM type names should match the lowercase Python name. | Enforces consistent pattern for status enumerations, allowing for standardized status handling across the application. |
| 4   | **Status Column Naming:**<br> a) SQLAlchemy Curation Status Column: `{workflow_name}_curation_status`.<br> b) SQLAlchemy Processing Status Column: `{workflow_name}_processing_status`.<br> c) Error message column: `{workflow_name}_processing_error` (Text type, nullable).                                                                                                                                    | Provides consistent field naming across all models, enabling generic handling in services and UI components. |
| 5   | **Model Class & File Naming:**<br> a) All model classes MUST be named using `{SourceTableTitleCase}` singular form (e.g., `Page`, not `Pages`).<br> b) Model files MUST be named `{source_table_name}.py` in singular form and snake_case.<br> c) Models representing join tables should be named clearly to represent their relationship.                                                                      | Establishes clear mapping between database tables and Python classes. |
| 6   | **No Tenant ID:** All `tenant_id` parameters, model fields, and related filtering logic MUST be identified and flagged for removal. This is a critical architectural change that is non-negotiable.                                                                                                                                                                                                                 | Simplifies architecture by removing multi-tenancy which is no longer needed. |
| 7   | **Relationship Definitions:**<br> a) All relationships MUST be explicitly defined using SQLAlchemy's `relationship()` function.<br> b) Relationships MUST include appropriate `backref` or `back_populates` definitions.<br> c) Cascade rules MUST be explicitly defined for parent-child relationships.<br> d) Foreign keys MUST be properly typed (usually UUID).                                                 | Ensures proper relationship mapping and navigation between related models. |
| 8   | **UUID Primary Keys:**<br> a) All primary keys MUST be UUID type.<br> b) Primary key columns MUST be named `id`.<br> c) Implementation MUST include both Python-side default and server-side default.                                                                                                                                                                                                              | Maintains consistent primary key pattern across all models for predictable access. |
| 9   | **Index Definitions:**<br> a) Status columns MUST be indexed.<br> b) Foreign key columns SHOULD be indexed.<br> c) Frequently queried fields SHOULD have appropriate indexes.<br> d) Index definitions MUST use SQLAlchemy's declarative approach.                                                                                                                                                                 | Ensures query performance for common access patterns. |
| 10  | **Layer Boundary Respect:** Do not make recommendations that extend beyond Layer 1 (Models). Focus exclusively on model definitions, relationships, and direct database interaction patterns. Other layers will be handled by their respective specialists.                                                                                                                                                        | Maintains clear separation of concerns and prevents conflicting recommendations across specialists. |

### Model Pattern Recognition Guidance

**Standard Model Structure:**

The following represents the expected structure for a model file. Use this as a reference when auditing existing models:

```python
# src/models/page.py
import uuid
from enum import Enum
from sqlalchemy import Column, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ENUMs should follow WorkflowName pattern, not SourceTable pattern
class PageCurationStatus(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"

class PageProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"

# Model class should match singular source table name in TitleCase
class Page(Base):
    __tablename__ = "pages"  # Note: table name is plural

    # Standard UUID primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()")
    )

    # Standard status columns with workflow_name prefix
    page_curation_status = Column(
        PgEnum(PageCurationStatus, name="pagecurationstatus", create_type=False),
        nullable=False,
        server_default=PageCurationStatus.New.value,
        index=True
    )

    page_processing_status = Column(
        PgEnum(PageProcessingStatus, name="pageprocessingstatus", create_type=False),
        nullable=True,
        index=True
    )

    page_processing_error = Column(Text, nullable=True)

    # Foreign key with proper relationship
    domain_id = Column(
        UUID(as_uuid=True),
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Proper relationship with backref
    domain = relationship("Domain", back_populates="pages")

    # Standard metadata fields
    url = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime, server_default=text("now()"), nullable=False)
    updated_at = Column(DateTime, server_default=text("now()"), nullable=False)
```

### Self-Verification Checklist

Before finalizing any audit findings or recommendations for Layer 1, verify:

- [ ] I have thoroughly examined all model files relevant to the workflow under review
- [ ] I have identified all ENUM classes and verified their naming against the `{WorkflowNameTitleCase}` pattern
- [ ] I have checked all status columns against the `{workflow_name}_status` pattern
- [ ] I have verified that no tenant_id columns or references exist
- [ ] I have confirmed all relationships have appropriate backref/back_populates definitions
- [ ] I have identified any raw SQL usage that needs to be refactored to ORM
- [ ] I have verified UUID implementation for primary keys follows the standard pattern
- [ ] I have documented all deviations clearly with specific remediation steps
- [ ] I have focused exclusively on Layer 1 concerns, not extending into other layers

_This verification must be completed for each model file audited. Proceeding without completing this checklist represents a violation of the Zero Assumptions rule._

### Operational Decision Matrix for Layer 1

| Scenario | Condition | Action |
|----------|-----------|--------|
| **Model File Missing** | Expected model file is not found | 1. Document missing model<br>2. Check if functionality is implemented elsewhere<br>3. Flag as critical gap in cheat sheet |
| **Non-Standard ENUM** | ENUM naming or values don't follow convention | 1. Document current implementation<br>2. Provide corrected implementation<br>3. Assess impact on other layers |
| **Raw SQL Detection** | SQL strings or text() functions outside of server_default | 1. Flag as critical violation<br>2. Document ORM equivalent<br>3. Assess security implications |
| **Tenant ID Present** | tenant_id column or references found | 1. Document all instances<br>2. Assess scope of removal<br>3. Flag as high-priority remediation |
| **Missing Relationships** | Foreign keys without relationship definitions | 1. Document missing relationships<br>2. Provide correct implementation<br>3. Note potential impact on queries |
| **WF1-SingleSearch Status Issues** | Status column named 'status' instead of 'single_search_curation_status' | 1. Document exact location and current implementation<br>2. Reference Blueprint Section 2.2.2<br>3. Provide explicit refactoring steps including column rename |
| **Blueprint Reference Unclear** | Unsure which Blueprint section applies to a specific implementation | 1. Halt assessment of that specific component<br>2. Document the specific implementation details<br>3. Use `<!-- NEED_CLARITY -->` tag<br>4. Continue with other components |

### Blueprint Reference Quick-Guide

When documenting deviations, reference the specific Blueprint sections:

| Component Type | Issue Type | Blueprint Reference |
|----------------|------------|---------------------|
| **SQLAlchemy Model** | File naming | Blueprint 2.2.1 Naming & Location, Item 1 |
| **SQLAlchemy Model** | Class naming | Blueprint 2.2.1 Naming & Location, Item 2 |
| **SQLAlchemy Model** | Base class | Blueprint 2.2.1 Base Class & Table Definition, Item 1 |
| **SQLAlchemy Model** | Tablename | Blueprint 2.2.1 Base Class & Table Definition, Item 2 |
| **SQLAlchemy Model** | Column types | Blueprint 2.2.1 Columns, Item 1 |
| **SQLAlchemy Model** | Column naming | Blueprint 2.2.1 Columns, Item 2 |
| **SQLAlchemy Model** | Primary key | Blueprint 2.2.1 Columns, Item 3 |
| **SQLAlchemy Model** | Foreign keys | Blueprint 2.2.1 Columns, Items 4-5 |
| **SQLAlchemy Model** | Relationships | Blueprint 2.2.1 Relationships, Items 1-3 |
| **SQLAlchemy Model** | Raw SQL | Blueprint 2.2.1 ORM Exclusivity, Item 1 |
| **SQLAlchemy Model** | Tenant ID | Blueprint 2.2.1 Tenant ID / Legacy Fields, Item 1 |
| **SQLAlchemy Model** | Docstrings | Blueprint 2.2.1 Docstrings, Items 1-2 |
| **Python ENUM** | Status ENUM naming | Blueprint 2.2.2 Naming & Definition, Item 1 |
| **Python ENUM** | ENUM base class | Blueprint 2.2.2 Naming & Definition, Item 2 |
| **Python ENUM** | ENUM location | Blueprint 2.2.2 Naming & Definition, Item 3 |
| **Python ENUM** | CurationStatus values | Blueprint 2.2.2 Standard Values, Item 1 |
| **Python ENUM** | ProcessingStatus values | Blueprint 2.2.2 Standard Values, Item 2 |
| **Python ENUM** | Status column naming | Blueprint 2.2.2 Model Column Association, Items 1-3 |
| **Python ENUM** | General ENUM patterns | Blueprint 2.2.2 General ENUMs, Items 1-3 |
| **Python ENUM** | Additional user states | Blueprint 2.2.2 Handling Justified Non-Standard User States, Items 1-5 |

### Technical Debt Prioritization Framework

When evaluating multiple technical debt items, prioritize them according to this matrix:

| Priority | Pattern | Impact | Example |
|----------|---------|--------|---------|
| **P0** | Raw SQL usage | Security risk, breaks ORM abstraction | `session.execute(text("SELECT * FROM..."))` |
| **P0** | Tenant ID present | Architectural violation | `tenant_id` columns or filters |
| **P1** | Non-standard status enum names | Systemic inconsistency | `PlaceStatusEnum` instead of `SingleSearchCurationStatus` |
| **P1** | Non-standard status column names | API/UI integration issues | `status` instead of `workflow_name_curation_status` |
| **P2** | Missing relationship definitions | Navigation issues | Foreign key without corresponding `relationship()` |
| **P2** | Non-standard enum values | Status transition confusion | `Selected` instead of `Queued` |
| **P3** | Missing docstrings | Maintainability | Undocumented model purpose |
| **P3** | Non-indexed foreign keys | Performance | Foreign key without `index=True` |

### Examples of Standard Refactoring Actions

When prescribing refactoring actions, use these standard formats:

1. **ENUM Renaming**:
   ```
   Rename 'PlaceStatusEnum' to 'SingleSearchCurationStatus' and ensure it:
   - Inherits from (str, Enum)
   - Contains standard values: New, Queued, Processing, Complete, Error, Skipped
   - Is used in model definition with PgEnum
   ```

2. **Status Column Renaming**:
   ```
   Rename 'status' column to 'single_search_curation_status' with:
   - Proper PgEnum type using SingleSearchCurationStatus
   - index=True parameter
   - nullable=False
   - server_default=SingleSearchCurationStatus.New.value
   ```

3. **Adding Processing Status Column**:
   ```
   Add new column 'single_search_processing_status' with:
   - PgEnum type using SingleSearchProcessingStatus
   - index=True parameter
   - nullable=True

   Add new column 'single_search_processing_error' with:
   - Text type
   - nullable=True
   ```

4. **Raw SQL Removal**:
   ```
   Replace raw SQL query:
   ```python
   result = await session.execute(text("SELECT * FROM page WHERE id = :id"), {"id": id})
   ```

   With ORM equivalent:
   ```python
   result = await session.execute(select(Page).where(Page.id == id))
   ```
   ```

5. **Tenant ID Removal**:
   ```
   Remove tenant_id column from Page model
   Remove tenant_id parameter from all methods that use this model
   Remove any filtering based on tenant_id
   ```

### Version Control

This document is version 3.0, dated 2025-05-18.

_These Guardrails are specific to the Layer-1-Models Specialist role and should be applied in conjunction with the project-wide Guardrails defined for the Director AI. The Layer 1 Specialist must maintain absolute focus on model-related concerns without extending into other architectural layers._
