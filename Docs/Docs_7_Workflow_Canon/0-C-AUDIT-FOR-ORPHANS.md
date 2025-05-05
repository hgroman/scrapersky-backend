# Orphaned Python Files Audit

This document lists Python files that exist in the source code but are not referenced in any workflow documentation. These files should be reviewed to determine if they are:

1. Actually needed but missing from workflow documentation
2. Legacy code that should be removed
3. Development/testing utilities not meant to be documented

## Remaining Orphaned/Misreferenced Files

(No remaining orphaned files from the initial list)

## Analysis

The audit revealed that most previously listed 'orphaned' files were essential system infrastructure or package structure files, which have now been documented in `1.0-System-Infrastructure-Layer.md`.

Three files were identified for archival:
1. `src/common/curation_sdk/router_base.py` (Moved to archive)
2. `src/common/curation_sdk/status_queue_helper.py` (Moved to archive)
3. `src/services/batch/simple_task_test.py` (Moved to archive)

The previously listed file `src/services/page_scraper/page_scraper_service.py` was found to not exist. Investigation suggests it was renamed to `src/services/page_scraper/processing_service.py`. This file needs to be reviewed and added to the appropriate workflow documentation or the System Infrastructure Layer.

## Recommendations

1. **Document `processing_service.py`:** Review `src/services/page_scraper/processing_service.py` and ensure it is properly referenced in the relevant workflow documentation (e.g., Page Scraping workflow) or added to the System Infrastructure Layer if deemed a core service.
2. **Confirm Archival:** Ensure the SDK and test files mentioned above have been moved to the designated archive location.

## Note on `__init__.py` Files

All `__init__.py` files are now documented in `1.0-System-Infrastructure-Layer.md` and are considered essential [SYSTEM] files.
