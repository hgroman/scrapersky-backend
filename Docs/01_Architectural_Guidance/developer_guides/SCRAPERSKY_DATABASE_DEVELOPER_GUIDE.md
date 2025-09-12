# SCRAPERSKY DATABASE DEVELOPER GUIDE
*Patterns, Conventions & Best Practices*

## OVERVIEW
This guide documents the established, battle-tested patterns for interacting with the database in the ScraperSky backend. Adherence to these patterns is mandatory to ensure data integrity, performance, and maintainability.

---

## 1. SQLAlchemy Enum Columns

### The Mandatory Pattern

The implementation of PostgreSQL `ENUM` types has a known "gotcha" that caused a critical production incident. Therefore, manual implementation is **FORBIDDEN**.

**To add an Enum column to a model, you MUST follow this process:**

1.  **Define the Enum in `src/models/enums.py`:**
    ```python
    class YourNewEnum(str, Enum):
        MEMBER_ONE = "member_one"
        MEMBER_TWO = "member_two"
    ```

2.  **Get the Verified Template from the Building Blocks Menu:**
    The official, machine-readable template for this component is stored in `Docs/01_Architectural_Guidance/09_BUILDING_BLOCKS_MENU.yaml` under the key `building_blocks.database.sqlalchemy_enum_column`.

3.  **Integrate and Modify:**
    Copy the code from the `template` key in the YAML file into your model in `src/models/` and modify the placeholder names (`YourNewEnum`, `your_column_name`, etc.).

### The "Why" - A Cautionary Tale

The parameters in this template (`native_enum=True`, `values_callable=...`) are not optional. They are the result of a painful production incident. Failure to use the template will be caught by the linter and will fail code review.

For the complete history and technical breakdown of why this pattern is so strict, all developers are required to read the following document:

**[WAR STORY: The Enum Implementation Train Wreck of 2025-09-12](/Docs/01_Architectural_Guidance/war_stories/WAR_STORY__Enum_Implementation_Train_Wreck__2025-09-12.md)**
