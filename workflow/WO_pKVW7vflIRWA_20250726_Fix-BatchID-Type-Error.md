# Work Order: Fix DatatypeMismatchError for batch_id

- **DART Task ID:** `pKVW7vflIRWA`
- **DART Task URL:** https://app.dartai.com/t/pKVW7vflIRWA-Fix-DatatypeMismatchError-for

## 1. Objective/Goal

Resolve the `sqlalchemy.exc.ProgrammingError: (DatatypeMismatchError) <class 'asyncpg.exceptions.DatatypeMismatchError'>: column "batch_id" is of type uuid but expression is of type character varying` that occurs during the creation of new `Job` records.

## 2. Background/Context

The error was triggered in the `domain_sitemap_submission_scheduler` when attempting to create a `Job` record. The `batch_id` column, which is a `UUID`, was receiving a `None` value that SQLAlchemy incorrectly inferred as a string (`character varying`) instead of a `NULL` UUID, leading to a database type mismatch error.

## 3. Scope of Work / Detailed Tasks

- [x] Investigate the `Job` creation logic within the `website_scan_service`.
- [x] Identify that the `initiate_scan` method did not accept a `batch_id`.
- [x] Modify `website_scan_service.py` to allow `initiate_scan` to accept an optional `batch_id` of type `UUID`.
- [x] Update the `Job` constructor within `initiate_scan` to pass this `batch_id`.
- [x] Modify `domain_sitemap_submission_scheduler.py` to generate a `UUID` for each batch.
- [x] Update the call to `initiate_scan` to pass the newly generated `batch_uuid`.
- [x] Commit and push the code changes.
- [x] Create this Work Order and the corresponding Journal Entry and Handoff Document.

## 4. Expected Deliverables/Outputs

- **Modified Files:**
  - `src/services/website_scan_service.py`
  - `src/services/domain_sitemap_submission_scheduler.py`
- **New Documentation Files:**
  - `workflow/WO_pKVW7vflIRWA_20250726_Fix-BatchID-Type-Error.md` (this file)
  - `workflow/HO_20250726_220500_pKVW7vflIRWA_BatchID-Fix-Complete.md`
- **DART Artifacts:**
  - A new Journal Entry document in DART linked to task `pKVW7vflIRWA`.

## 5. Completion Checklist

- [x] Code changes implemented and tested.
- [x] Code changes committed and pushed to `origin/main`.
- [x] DART Task created and set to 'Done'.
- [x] Work Order created.
- [x] Journal Entry created in DART.
- [x] Handoff Document created.
