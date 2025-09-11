# Post-Mortem: Sitemap Scheduler Failure

**Date:** September 8, 2025
**Status:** ✅ **FIXED**

## Executive Summary

A critical bug was identified that caused the sitemap import background job to fail, leaving all sitemap files stuck in the `Queued` status. The issue was traced back to a recent refactoring commit that removed a critical type hint from a service function signature, causing a type mismatch with the underlying scheduler SDK. The fix has been applied, and the scheduler is now functioning correctly.

## The Problem

The `sitemap_import_scheduler` was failing silently. No new sitemap files were being processed, and they remained in the `Queued` state indefinitely. This completely blocked the ingestion pipeline for new pages.

## Root Cause Analysis

The failure was caused by commit `0611775`, a refactoring that aimed to simplify code by removing what appeared to be an unused import.

In `src/services/sitemap_import_service.py`, the signature of the `process_single_sitemap_file` function was changed:

**Before (Correct):**
```python
import uuid
...
async def process_single_sitemap_file(self, sitemap_file_id: uuid.UUID, session: AsyncSession):
    ...
```

**After (Incorrect):**
```python
# import uuid <- This line was removed
...
async def process_single_sitemap_file(self, sitemap_file_id, session: AsyncSession):
    # The uuid.UUID type hint was removed from sitemap_file_id
    ...
```

The generic `run_job_loop` SDK, which powers all background schedulers, is strongly typed. It is designed to call a processing function that accepts a `UUID` object as its first parameter. By removing the `uuid.UUID` type hint, the function signature of `process_single_sitemap_file` no longer matched the signature expected by the `run_job_loop`.

This mismatch caused the `run_job_loop` to raise a `TypeError` internally when it tried to call the processing function. The error was caught by a top-level exception handler in the scheduler job, which logged the error and terminated the run. The result was a silent failure where no items were processed, and they remained in the `Queued` state.

## The Fix

The fix was to revert the breaking change in `src/services/sitemap_import_service.py`:

1.  **Restore the `uuid` import:** The line `import uuid` was added back to the top of the file.
2.  **Restore the type hint:** The function signature was changed back to its correct, explicitly-typed form:
    ```python
    async def process_single_sitemap_file(self, sitemap_file_id: uuid.UUID, session: AsyncSession):
    ```

These changes restore the function signature that the `run_job_loop` SDK expects, resolving the `TypeError` and allowing the scheduler to resume normal operation.

## Lessons Learned

The scheduler's `run_job_loop` SDK is a powerful tool for standardizing background jobs, but it relies on strict adherence to its expected function signatures. Seemingly minor refactoring, like removing a "unused" import, can have critical downstream effects if it changes the type signature of a function used by this SDK. Future development should include static analysis checks (e.g., MyPy) in the CI/CD pipeline to catch such breaking changes before they reach production.
