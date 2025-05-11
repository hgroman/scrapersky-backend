# Guide: Database Enum Isolation Pattern

**Document ID:** 29
**Date:** 2024-07-27
**Status:** Active

## Purpose

This guide documents the critical importance of using **distinct database enum types** for status fields associated with **different logical workflows or tables**, even if the status values themselves (e.g., 'Queued', 'Processing', 'Error') appear similar.

Sharing the same database enum type across unrelated status columns can lead to unexpected breakage during refactoring, particularly when using `ALTER TYPE ... RENAME`.

## The Problem: Unintended Coupling via Shared Enums

Consider two distinct background processing workflows:

1.  **Sitemap Import:** Tracks status in `sitemap_files.sitemap_import_status`.
2.  **Place Deep Scan:** Tracks status in `places_staging.deep_scan_status`.

Both might use states like `Queued`, `Processing`, `Completed`, `Error`. It might seem efficient initially to create a single database enum type (e.g., `processing_status_enum`) and use it for both columns.

However, this creates a hidden dependency. If Workflow 1 is refactored and its status enum needs renaming (e.g., `ALTER TYPE processing_status_enum RENAME TO sitemap_import_status_enum;`), this database change **will break Workflow 2**, because its code (models, services) will still be trying to reference the old type name (`processing_status_enum`) which no longer exists in the database for the `places_staging.deep_scan_status` column.

## Case Study: `deep_scan_status_enum` Conflict (July 2024)

This exact issue occurred during the refactoring of the "Deep Scrape" feature into the "Sitemap Import" workflow (WF-06).

- **Initial State:** Both `sitemap_files.deep_scrape_process_status` and `places_staging.deep_scan_status` potentially used the same underlying DB enum type (originally named `deep_scan_status_enum`).
- **Refactoring Step:** As part of renaming `deep_scrape` to `sitemap_import`, the database enum was renamed: `ALTER TYPE deep_scan_status_enum RENAME TO sitemap_import_status_enum;`.
- **Side Effect:** This fixed the enum for the `sitemap_files` table and the new sitemap import workflow. However, it **broke** the separate deep scan workflow, which started throwing `ProgrammingError: type "deep_scan_status_enum" does not exist` because the `places_staging` table's `deep_scan_status` column was still linked to the now-nonexistent type name in the Python code accessing it.
- **Resolution:**
  1.  A **new, distinct** database enum type (`gcp_api_deep_scan_status_enum`) was created specifically for the `places_staging.deep_scan_status` column.
  2.  The `places_staging.deep_scan_status` column was altered to use this new type.
  3.  Python code related to the deep scan workflow (`models/place.py`, `services/sitemap_scheduler.py`, `routers/places_staging.py`) was updated to use the new `GcpApiDeepScanStatusEnum`.

## The Solution: Isolate Enum Types per Workflow/Table

**Rule:** Create and use a **separate, explicitly named database enum type** for each distinct status field, especially those managed by different workflows or stored in different tables.

- **Example:**
  - For `sitemap_files.sitemap_import_status`, use DB type `sitemap_import_status_enum`.
  - For `places_staging.deep_scan_status`, use DB type `gcp_api_deep_scan_status_enum`.
  - For `local_businesses.domain_extraction_status`, use DB type `domain_extraction_status_enum`.

**Benefits:**

- **Decoupling:** Changes to one workflow's status enum (renaming, adding/removing values) do not affect unrelated workflows.
- **Clarity:** Explicit type names improve code readability and understanding of which status belongs to which process.
- **Maintainability:** Refactoring becomes significantly safer and less prone to unexpected side effects.

While it might seem like slight duplication, the safety and clarity gained by isolating enum types far outweigh the perceived cost.

## See Also

- `27-ENUM_HANDLING_STANDARDS.md`: General enum standards.
- `Docs/Docs_5_Project_Working_Docs/43-Sitemap-Parser/43.6-WO-Progress.md`: Detailed log of the refactoring and debugging session where this issue was resolved.
