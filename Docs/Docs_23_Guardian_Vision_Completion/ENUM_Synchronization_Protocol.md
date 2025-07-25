# ENUM Synchronization Protocol

**Version:** 1.0
**Date:** 2025-06-30
**Owner:** L1 Guardian (Models/Enums)

## 1. Purpose

This document provides the official, non-negotiable protocol for creating, modifying, and migrating ENUM types from the application codebase to the Supabase PostgreSQL database. Its purpose is to prevent database/codebase drift, which was a primary source of technical debt and runtime errors identified during the Guardian Vision Boot Sequence.

Adherence to this protocol is mandatory for any change involving `src/models/enums.py`.

## 2. The Golden Rule

**The `src/models/enums.py` file is the absolute and only source of truth for all ENUM definitions.** The database MUST reflect the state of this file. Never create or alter ENUM types directly in the database.

## 3. The Protocol: A Step-by-Step Guide

### Step 1: Modify the Source of Truth

All changes begin in the codebase.

- **To Create a New ENUM**: Add your new class to `src/models/enums.py`, inheriting from `(str, Enum)`.
- **To Add a Value to an Existing ENUM**: Add the new member to the appropriate ENUM class in the file.
- **To Rename an ENUM**: This is a multi-step process. See Section 4.
- **To Remove a Value**: This is a destructive action. See Section 4.

### Step 2: Generate the Migration Script

Once your changes are complete in `enums.py`, you are responsible for creating the corresponding database migration.

1.  **Identify the Project ID**: Use the `mcp3_list_projects` tool if you are unsure of the project ID.
2.  **Formulate the SQL Command**:
    -   **For a new ENUM**: `CREATE TYPE new_enum_name AS ENUM ('value1', 'value2', 'value3');`
    -   **To add a new value**: `ALTER TYPE existing_enum_name ADD VALUE IF NOT EXISTS 'new_value';`

3.  **Wrap it in a Migration**: Use the `mcp3_apply_migration` tool. Give your migration a descriptive, `snake_case` name.

    ```xml
    <mcp3_apply_migration>
    {
        "project_id": "your_project_id",
        "name": "add_new_status_to_task_status_enum",
        "query": "ALTER TYPE task_status ADD VALUE IF NOT EXISTS 'NewStatus';"
    }
    </mcp3_apply_migration>
    ```

### Step 3: Apply and Verify

1.  Execute the tool call.
2.  If the migration succeeds, your work is complete. If it fails, carefully read the error message. It is likely that the ENUM already exists or the value is already present. Do not force changes.

## 4. Handling Complex & Destructive Changes

Renaming an ENUM or removing a value is a complex database operation that can lead to data loss if not handled correctly. These actions require a more careful, multi-step migration process that is beyond the scope of this standard protocol.

**If you need to rename an ENUM or remove a value, you MUST:**

1.  Create a DART task for the L4 Guardian (Services).
2.  Title it: `L4_ACTION: Data migration required for ENUM change {enum_name}`.
3.  In the task, detail the requested change and await guidance on a safe data migration strategy before proceeding.

Failure to follow this step for destructive changes will be considered a critical violation of this protocol.
