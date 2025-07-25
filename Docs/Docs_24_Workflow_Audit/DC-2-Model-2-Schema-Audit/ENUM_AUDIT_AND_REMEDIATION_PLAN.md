# ScraperSky ENUM Audit & Remediation Plan

**Date:** 2025-07-02

## 1. Introduction

This document outlines the findings of a comprehensive audit comparing the live PostgreSQL database ENUM types against the application's SQLAlchemy models and API schemas. It serves as the official work order for remediating all identified discrepancies.

The goal is to restore data layer integrity by ensuring a strict 1:1 alignment between the database (as the source of truth) and the application code, starting with the highest-priority issues.

## 2. Database ENUM Source of Truth

The following table represents the complete set of ENUM types and their values currently defined in the production database, as of the date of this report. All remediation decisions are based on this ground truth.

| Enum Type Name                      | Values                                                              |
| ----------------------------------- | ------------------------------------------------------------------- |
| `SitemapAnalysisStatusEnum`         | `{Queued,Processing,Completed,Error}`                               |
| `SitemapCurationStatusEnum`         | `{New,Selected,Maybe,"Not a Fit",Archived}`                         |
| `app_role`                          | `{basic,admin,super_admin,system_admin}`                            |
| `batch_job_status`                  | `{pending,running,complete,failed,partial}`                         |
| `contact_curation_status`           | `{New,Queued,Processing,Complete,Error,Skipped}`                    |
| `contact_email_type_enum`           | `{Service,Corporate,Free,Unknown}`                                  |
| `contact_processing_status`         | `{Queued,Processing,Complete,Error}`                                |
| `dart_status_enum`                  | `{not_set,open,working,waiting,closed}`                             |
| `discovery_method`                  | `{robots_txt,common_path,sitemap_index,html_link,manual}`           |
| `domain_extraction_status`          | `{Queued,Processing,Completed,Error}`                               |
| `domain_status`                     | `{pending,processing,completed,error}`                              |
| `feature_priority`                  | `{urgent,need_to_have,nice_to_have,someday}`                        |
| `feature_status`                    | `{new,reviewed,next_round,back_burner,someday,in_progress,completed,rejected}` |
| `gcp_api_deep_scan_status`          | `{Queued,Processing,Completed,Error}`                               |
| `governor_layer`                    | `{1,2,3,4,5,6,7}`                                                   |
| `hubspot_sync_processing_status`    | `{Queued,Processing,Complete,Error}`                                |
| `hubspot_sync_status`               | `{New,Queued,Processing,Complete,Error,Skipped}`                    |
| `job_type`                          | `{sitemap_scan,places_search,domain_metadata_extraction,contact_enrichment,batch_processing}` |
| `page_curation_status`              | `{New,Queued,Processing,Complete,Error,Skipped}`                    |
| `page_processing_status`            | `{Queued,Processing,Complete,Error}`                                |
| `place_status`                      | `{New,Queued,Processing,Complete,Error,Skipped,Selected}`           |
| `search_status`                     | `{PENDING,COMPLETED,FAILED,RUNNING}`                                |
| `sitemap_analysis_status`           | `{Pending,Analyzing,Completed}`                                     |
| `sitemap_curation_status`           | `{New,Queued,Processing,Complete,Error,Skipped}`                    |
| `sitemap_file_status`               | `{Pending,Processing,Completed,Error}`                              |
| `sitemap_import_curation_status`    | `{New,Selected,Maybe,"Not a Fit",Archived}`                         |
| `sitemap_type`                      | `{index,standard,image,video,news,unknown}`                         |
| `sitemapimportcurationstatus`       | `{New,Queued,Processing,Complete,Error,Skipped}`                    |
| `sitemapimportprocessingstatus`     | `{Queued,Processing,Complete,Error}`                                |
| `task_status`                       | `{Queued,InProgress,Completed,Error,ManualReview,Cancelled,Paused,Processing,Complete}` |


## 3. Remediation Plan by Workflow

---

### **Workflow 1: Places Staging (Priority: 0 - Critical)**

*   **Problem Statement:** The `places_staging` table's `status` column is incorrectly typed as `sitemap_import_curation_status` in the database, while the application model (`src/models/place.py`) correctly expects it to be `place_status`.
*   **Evidence:** The DB query confirms `place_status` and `sitemap_import_curation_status` are distinct types. The model code specifies `PlaceStatus` which maps to the `place_status` DB type.
*   **Blast Radius Assessment:** This is a severe data integrity risk but is isolated to the database schema. The application code is already correct. A database migration is the only required change and will have no negative downstream effects on the code; it will simply fix the broken link.
*   **Plan of Attack:**
    1.  Create a new Alembic migration script.
    2.  The migration will execute the following SQL: `ALTER TABLE places_staging ALTER COLUMN status TYPE place_status USING status::text::place_status;`
    3.  Apply and verify the migration.

---

### **Workflow 5: Sitemap File Model (Priority: 0 - Critical)**

*   **Problem Statement:** The `SitemapFile` SQLAlchemy model in `src/models/sitemap.py` is missing the `deep_scrape_curation_status` column, which exists in the database and is expected by API schemas.
*   **Evidence:** Previous audit work confirmed the column's presence in API schemas and its absence from the model, causing runtime errors.
*   **Blast Radius Assessment:** Low. Adding the missing column to the model is a self-contained fix that will resolve application errors and align the ORM with the database schema. Our `grep` search confirmed this field is expected and its absence is the anomaly.
*   **Plan of Attack:**
    1.  Edit `src/models/sitemap.py`.
    2.  Add the `deep_scrape_curation_status` column to the `SitemapFile` model, typing it with the `SitemapImportCurationStatus` enum.

---

### **Workflow 3: Local Business Status (Priority: 1 - High)**

*   **Problem Statement:** The `local_business` table uses the `place_status` enum for its `status` column, but this enum is missing the required `"Archived"` value. The application model (`src/models/local_business.py`) incorrectly assumes a non-existent `local_business_status` enum type.
*   **Evidence:** The DB query confirms that `local_business_status` does not exist and that `place_status` lacks an `"Archived"` value.
*   **Blast Radius Assessment:** High. Any code attempting to archive a `LocalBusiness` will fail. Furthermore, adding a value to the `place_status` enum will affect **all tables** that use this type (`places_staging`, `local_business`, etc.). However, adding a value is a non-breaking change for existing code that does not check for it.
*   **Plan of Attack:**
    1.  Create a new Alembic migration script to add the `"Archived"` value: `ALTER TYPE place_status ADD VALUE 'Archived';`
    2.  Edit `src/models/enums.py` and add `ARCHIVED = "Archived"` to the `PlaceStatus` Python enum.
    3.  Edit `src/models/local_business.py` to ensure its `status` column correctly points to the `place_status` DB type name.

---

### **Workflow 4: Sitemap Curation Status (Priority: 1 - High)**

*   **Problem Statement:** The `SitemapCurationStatus` enum in `src/models/enums.py` is missing the `"Maybe"` value, which exists in the corresponding `SitemapCurationStatusEnum` database type.
*   **Evidence:** The DB query confirms `"Maybe"` is a valid value for `SitemapCurationStatusEnum`. Code inspection shows a commented-out line that included this value, indicating it was intended.
*   **Blast Radius Assessment:** Minimal and positive. Our `grep` search showed that existing logic is not brittle and will not break. Adding the value will correctly expose this status to the application.
*   **Plan of Attack:**
    1.  Edit `src/models/enums.py`.
    2.  Add `MAYBE = "Maybe"` to the `SitemapCurationStatus` enum definition.

---

### **Workflow 6: Sitemap Import Status (Priority: 2 - Medium)**

*   **Problem Statement:** The codebase contains two conflicting enums: `SitemapImportProcessingStatus` and `SitemapImportProcessStatus`. The latter, redundant enum is used in the service layer. Additionally, the database contains a non-standard, all-lowercase enum type name: `sitemapimportprocessingstatus`.
*   **Evidence:** `grep` searches confirmed the usage of the redundant enum. The DB query confirmed the non-standard type name.
*   **Blast Radius Assessment:** Medium. This requires a careful, multi-step refactoring. First, the code must be changed to use the correct primary enum. Then, a database migration must be performed to fix the type name. Finally, the redundant code can be removed.
*   **Plan of Attack:**
    1.  **Code Refactor:** Edit `src/services/sitemap_files_service.py` to import and use the primary `SitemapImportProcessingStatus` enum.
    2.  **Database Migration:** Create a migration to rename the enum type: `ALTER TYPE sitemapimportprocessingstatus RENAME TO sitemap_import_processing_status;`
    3.  **Code Cleanup:** Delete the redundant `SitemapImportProcessStatus` enum from `src/models/enums.py`.
    4.  **Value Alignment:** Update the primary `SitemapImportProcessingStatus` enum to match the values in the database, removing any that are not present.
