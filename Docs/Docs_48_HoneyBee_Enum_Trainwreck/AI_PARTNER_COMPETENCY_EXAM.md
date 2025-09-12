# Welcome, AI Pairing Partner - Competency Exam

**Objective:** To test the effectiveness of the ScraperSky Architectural Toolshed.

---

## 1. Introduction & Instructions

Welcome to the ScraperSky project. You have been selected to participate in a competency exam to validate our documentation and architectural guidance system.

Your task is to answer the questions in Section 2 below. You must derive your answers **exclusively** from the documentation found within the `/Docs/01_Architectural_Guidance/` directory and its subdirectories. This is your single source of truth.

**Your Starting Point:** The root of all knowledge for this project is:
`Docs/01_Architectural_Guidance/TOOLSHED_TABLE_OF_CONTENTS.md`

**Instructions:**
1.  Begin by navigating the Toolshed to understand the project's structure and patterns.
2.  For each question below, find the correct answer within the documentation.
3.  Edit this file (`AI_PARTNER_COMPETENCY_EXAM.md`) and write your answer directly below each question.
4.  Your answers should be concise and demonstrate that you have found and understood the correct, battle-tested patterns.

---

## 2. Competency Exam Questions

**Question 1:**
I need to add a new column to a SQLAlchemy model that will store a value from a fixed set of string choices (e.g., "pending", "running", "complete"). This will be a PostgreSQL `ENUM` type in the database. What is the mandatory, battle-tested code pattern for defining this column in the SQLAlchemy model? Provide the code snippet.

**Your Answer:**
```python
from sqlalchemy import Column
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import Enum as SQLAlchemyEnum
from src.models.enums import YourNewEnum  # <-- 1. IMPORT your Python Enum

# ... inside your SQLAlchemy model class ...

your_column_name: Mapped[YourNewEnum] = Column(  # <-- 2. RENAME your column
    SQLAlchemyEnum(
        YourNewEnum,
        name="your_new_enum_name_in_db",  # <-- 3. DEFINE the PostgreSQL enum type name
        create_type=False,  # We manage the enum creation via migration scripts

        # CRITICAL: This ensures SQLAlchemy sends the enum's *value* (e.g., "contact_root")
        # to the database, not its *name* (e.g., "CONTACT_ROOT"). Omitting this
        # was the root cause of the Sept 12, 2025 incident.
        values_callable=lambda obj: [e.value for e in obj],

        # CRITICAL: This uses PostgreSQL's native ENUM type, which is more
        # efficient and type-safe than using a VARCHAR with a CHECK constraint.
        native_enum=True
    ),
    nullable=False,  # <-- 4. ADJUST nullability and default as needed
    index=True,
    # default=YourNewEnum.DEFAULT_VALUE
)
```

Source: `Docs/01_Architectural_Guidance/09_BUILDING_BLOCKS_MENU.yaml` under `building_blocks.database.sqlalchemy_enum_column`

---

**Question 2:**
I am debugging a service that makes an external API call. In my `except` block, I am logging the exception `e` to help with debugging. Is there a critical security pattern I must follow when doing this? If so, what is it?

**Your Answer:**
Yes, there is a critical security pattern that must be followed when logging exceptions from external API calls. You must sanitize the exception message before logging to prevent API keys and other sensitive credentials from being exposed in application logs.

The mandatory pattern is to use the `sanitize_exception_message()` function from `src/utils/log_sanitizer.py`:

```python
try:
    # External API call here
except Exception as e:
    # SECURITY: Sanitize before logging
    sanitized_error = sanitize_exception_message(e)
    exception_info = get_safe_exception_info(e)
    
    logger.error(f"API error: {sanitized_error}")  # ✅ Logs: "...?key=***REDACTED***"
    logger.error(f"Exception details: {exception_info}")
    
    raise ValueError(f"API error: {sanitized_error}")  # ✅ Safe error propagation
```

Source: `Docs/01_Architectural_Guidance/09_BUILDING_BLOCKS_CATALOG.md` - API Key Security Pattern

---

**Question 3:**
My AI partner has proposed a fix for a bug. The fix seems logical, but I am concerned it might repeat a past mistake. Where would I find a history of past implementation failures and the lessons learned from them, specifically regarding a "train wreck" involving Enum implementation? Provide the file path to the relevant document.

**Your Answer:**
`Docs/01_Architectural_Guidance/war_stories/WAR_STORY__Enum_Implementation_Train_Wreck__2025-09-12.md`

This document contains the complete history of the "train wreck" involving Enum implementation that occurred on September 12, 2025, including the cascade of failures caused by missing the `values_callable` parameter in SQLAlchemy Enum configuration.

---

**Question 4:**
I am writing a new `POST` endpoint in a FastAPI router. The endpoint needs to perform several database inserts. What is the mandatory project pattern for managing the database session and ensuring the database operations are atomic (all succeed or all fail together)?

**Your Answer:**
The mandatory project pattern for managing database sessions in FastAPI POST endpoints is that **routers own transactions, services accept sessions**. 

The correct pattern is:

```python
@router.post("/endpoint")
async def endpoint(
    request: RequestSchema,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(verify_token)  # Auth dependency
):
    async with session.begin():  # Router owns transaction
        result = await service_function(session, request)
        return result
        # Transaction automatically commits on success or rolls back on exception
```

Key principles:
- Router creates the transaction boundary using `async with session.begin()`
- Service functions accept the session as a parameter, never create their own
- All database operations within the transaction are atomic (all succeed or all fail together)
- Services use `await session.flush()` not `await session.commit()` - the router handles commit/rollback

Source: `Docs/01_Architectural_Guidance/03_ARCHITECTURAL_PATTERNS_LIBRARY.md` - Layer 3 Routers Pattern

---
