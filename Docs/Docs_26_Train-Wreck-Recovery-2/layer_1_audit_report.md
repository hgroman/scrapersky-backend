# Layer 1 Audit Report: Local Models & ENUMs vs. Supabase Schema

**Date:** 2024-07-26
**Audit ID:** QACOtGpTqhOI

## 1. Executive Summary

This audit provides a detailed, evidence-based comparison of the local SQLAlchemy models and Python ENUM definitions against the live Supabase database schema. The goal was to identify all discrepancies to enable a comprehensive, targeted remediation plan.

The audit revealed **significant and critical discrepancies** between the local application code and the database. Key issues include missing columns in local models, incorrect foreign key definitions, widespread nullability mismatches, and conflicting or decentralized ENUM definitions. These issues are severe enough to cause application failures, data corruption, and broken referential integrity.

Remediation is required to realign the local Layer 1 definitions with the database schema.

## 2. Overall Findings

- **Decentralized ENUMs**: The canonical `src/models/enums.py` is not the single source of truth. Most ENUMs are defined inline within their respective model files, leading to conflicts and code duplication.
- **Systemic Nullability Mismatches**: Many columns defined as non-nullable in local models (often with defaults) are nullable in the database. This suggests a fundamental disconnect between application-level assumptions and database reality.
- **Missing Foreign Key Columns**: Several tables have `created_by_id` or `tenant_id` columns in the database that are completely missing from the corresponding local models, breaking relationships.
- **Incorrect Foreign Key Types**: At least one critical foreign key (`places_staging.search_job_id`) has a type mismatch (`UUID` vs. `Integer`), rendering the relationship invalid.
- **Inconsistent Naming Conventions**: Supabase ENUM types use `lowercase` naming, while local Python classes use `PascalCase`. While SQLAlchemy handles this, it adds unnecessary cognitive load.

## 3. Detailed Model-to-Table Comparison

### 3.1 `batch_jobs` (Model: `BatchJob`)
- **Status**: ⚠️ **Mismatch**
- **Discrepancies**:
  - `total_domains` (local) vs. `total_urls` (DB): Name mismatch.
  - `id_uuid` (local): Missing in the database.
  - `total_domains`, `processed_domains`, `failed_domains`: Nullable in DB, non-nullable in model.

### 3.2 `contacts` (Model: `Contact`)
- **Status**: ❌ **Mismatch**
- **Discrepancies**:
  - `created_by_id`: Missing in the local model.
  - `tenant_id`: Missing in the local model.

### 3.3 `domains` (Model: `Domain`)
- **Status**: ❌ **Mismatch**
- **Discrepancies**:
  - `created_by_id`: Missing in the local model.
  - `status`: Nullable in DB, non-nullable in model.

### 3.4 `jobs` (Model: `Job`)
- **Status**: ❌ **Critical Mismatch**
- **Discrepancies**:
  - `batch_id`: `String` in model, `uuid` in DB.
  - `tenant_id`: Split into two fields in model (`String`, `UUID`), single `uuid` in DB.
  - `id`: `Integer` in DB, but referenced by other models as `UUID`.

### 3.5 `local_businesses` (Model: `LocalBusiness`)
- **Status**: ❌ **Mismatch**
- **Discrepancies**:
  - `created_by_id`: Missing in the local model.

### 3.6 `pages` (Model: `Page`)
- **Status**: ❌ **Mismatch**
- **Discrepancies**:
  - `created_by_id`: Missing in the local model.

### 3.7 `places_staging` (Model: `Place`)
- **Status**: ❌ **Critical Mismatch**
- **Discrepancies**:
  - `search_job_id`: `UUID` in model, but FK to `jobs.id` which is `Integer`. Relationship is broken.
  - `created_at`: Missing in the local model.
  - `search_time`, `priority`, `processed`, `updated_at`: Nullable in DB, non-nullable in model.

### 3.8 `sitemap_files` (Model: `SitemapFile`)
- **Status**: ❌ **Mismatch**
- **Discrepancies**:
  - `created_by_id`: Missing in the local model.
  - `file_path`: Missing in the local model.
  - `tenant_id`: Nullable in model, non-nullable in DB.
  - `deep_scrape_curation_status`: ENUM name mismatch (`SitemapCurationStatusEnum` vs. `sitemapcurationstatusenum`).

### 3.9 `tenants` (Model: `Tenant`)
- **Status**: ✅ **Match**
- **Discrepancies**: None.

## 4. Detailed ENUM Comparison

| Supabase ENUM Type | Local Python ENUM Class | Status | Notes |
| :--- | :--- | :--- | :--- |
| `contact_email_type` | `ContactEmailTypeEnum` | ❌ **Mismatch** | DB values are `lowercase`, local are `UPPERCASE`. |
| `sitemapanalysisstatus` | `SitemapAnalysisStatusEnum` | ⚠️ **Conflict** | Two conflicting local definitions exist (`domain.py` vs. `enums.py`). |
| `contactcurationstatus` | `ContactCurationStatus` | ✅ **Match** | |
| `contactprocessingstatus` | `ContactProcessingStatus` | ✅ **Match** | |
| `hubotsyncstatus` | `HubotSyncStatus` | ✅ **Match** | |
| `hubsyncprocessingstatus` | `HubSyncProcessingStatus` | ✅ **Match** | |
| `sitemapcurationstatus` | `SitemapCurationStatusEnum` | ✅ **Match** | |
| `place_status_enum` | `PlaceStatusEnum` | ✅ **Match** | |
| `domainextractionstatusenum` | `DomainExtractionStatusEnum` | ✅ **Match** | |
| `pagecurationstatus` | `PageCurationStatus` | ✅ **Match** | |
| `pageprocessingstatus` | `PageProcessingStatus` | ✅ **Match** | |
| `gcp_api_deep_scan_status_enum` | `GcpApiDeepScanStatusEnum` | ✅ **Match** | |
| `sitemap_file_status_enum` | `SitemapFileStatusEnum` | ✅ **Match** | |
| `sitemap_import_status_enum` | `SitemapImportProcessStatusEnum` | ✅ **Match** | |

## 5. Recommendations & Next Steps

Based on these findings, the following high-level actions are recommended:

1.  **Centralize ENUMs**: Consolidate all ENUM definitions into `src/models/enums.py` and remove inline definitions from model files.
2.  **Correct ENUM Values**: Fix the casing mismatch in `ContactEmailTypeEnum`.
3.  **Align Models with DB Schema**: Update all local SQLAlchemy models to match the database schema, including:
    - Adding missing columns (`created_by_id`, `tenant_id`, etc.).
    - Correcting data types (e.g., `jobs.batch_id`).
    - Fixing broken foreign key relationships (e.g., `places_staging.search_job_id`).
    - Aligning nullability constraints.
4.  **Create Thematic DART Tasks**: Group the required changes into logical, thematic DART tasks for organized remediation.

This report concludes the audit phase. The next step is to present these findings and plan the remediation effort.
