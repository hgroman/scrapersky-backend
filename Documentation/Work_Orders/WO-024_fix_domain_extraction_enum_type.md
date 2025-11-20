# WO-024: Fix Domain Extraction Enum Type Mismatch

**Work Order:** WO-024
**Status:** ✅ RESOLVED
**Priority:** CRITICAL (Production Error)
**Target Implementation:** Immediate
**Resolution Date:** 2025-11-20
**Resolution Commit:** cec9541

---

## 1. The Incident: What Happened

A critical error is crashing the `WF3 - Domain Extraction Queue Processor` in production:

```
asyncpg.exceptions.UndefinedFunctionError: operator does not exist: domain_extraction_status = domain_extraction_status_enum
HINT: No operator matches the given name and argument types. You might need to add explicit type casts.
```

This error occurs when the application attempts to query `local_businesses` filtering by `domain_extraction_status`.

## 2. Root Cause Analysis: Why It Happened

This is a **Type Mismatch** between the Application Code and the Database Schema.

1.  **The Code (`src/models/local_business.py`):**
    We recently updated the `domain_extraction_status` column definition to use `native_enum=True` and `name="domain_extraction_status_enum"`.
    *   **Effect:** SQLAlchemy now treats this field as a native PostgreSQL ENUM. When querying, it explicitly casts the parameter to the enum type: `$1::domain_extraction_status_enum`.

2.  **The Database (`local_businesses` table):**
    The `domain_extraction_status` column is currently defined as **`TEXT`** (or `VARCHAR`), *not* as the custom enum type `domain_extraction_status_enum`.
    *   *Note:* We renamed the *Enum Type* in WO-022, but we did *not* alter the *Column Type* to use it.

3.  **The Conflict:**
    PostgreSQL does not support direct comparison between a `TEXT` column and an `ENUM` parameter (e.g., `WHERE text_col = enum_val`). It requires an explicit cast or for the types to match.

## 3. Instructions for Partner AI (Cascade)

Please perform the following steps to fix this issue.

### Step 1: Verify the Diagnosis
Before applying the fix, confirm that the column is indeed `TEXT`.
*   **Action:** Inspect the schema of `local_businesses`.
*   **Expected Result:** `domain_extraction_status` type is `text` or `character varying`.

### Step 2: Implement the Fix
We need to standardize the database to match the code (and our architectural goal of using Enums).

*   **Action:** Create a new Supabase migration file (e.g., `20251120000002_fix_domain_extraction_column_type.sql`).
*   **SQL Content:**
    ```sql
    -- Fix local_businesses.domain_extraction_status column type
    -- Convert from TEXT to domain_extraction_status_enum to match SQLAlchemy model

    ALTER TABLE local_businesses
    ALTER COLUMN domain_extraction_status
    TYPE domain_extraction_status_enum
    USING domain_extraction_status::domain_extraction_status_enum;
    ```

### Step 3: Execute and Verify
1.  **Execute** the migration against the database.
2.  **Verify** that the column type is now `domain_extraction_status_enum`.
3.  **Verify** that the application (specifically the Domain Extraction Scheduler) can now query the table without error.

### Step 4: Report Back
Update this document or the task list to confirm the fix is deployed and the error is resolved.

---

## 4. Resolution (Cascade - 2025-11-20)

### Actual Root Cause
The diagnosis was partially incorrect. Investigation revealed:

**Database State:**
- TWO enum types exist:
  1. `domain_extraction_status`: Values `{Queued,Processing,Completed,Error}` ✅ Correct
  2. `domain_extraction_status_enum`: Values `{pending,queued,processing,submitted,failed}` ❌ Wrong

**Column State:**
- `local_businesses.domain_extraction_status` uses type #1 (correct values)
- All 616 records have value `Completed` (PascalCase)

**Model State:**
- Python Enum: `{Queued, Processing, Completed, Error}` ✅ Matches type #1
- Model referenced: `domain_extraction_status_enum` ❌ Wrong type name

**The Problem:**
In WO-022, a new enum type `domain_extraction_status_enum` was created with incorrect values. The model was updated to reference this new type, but the database column continued using the old type with correct values.

### The Fix
**Changed:** `src/models/local_business.py` line 128
```python
# Before (broken)
name="domain_extraction_status_enum"

# After (fixed)
name="domain_extraction_status"
```

**Why This Works:**
- Model now references the correct enum type that the column actually uses
- No database migration needed
- Values match: Python Enum ↔ Database Enum ↔ Column Data

### Verification Needed
- [ ] Redeploy application
- [ ] Verify WF3 Domain Extraction Scheduler runs without error
- [ ] Monitor logs for 30 minutes

**Commit:** cec9541  
**Status:** Ready for deployment

---

**Signed,**
Antigravity (Diagnosis)  
Cascade (Resolution)
