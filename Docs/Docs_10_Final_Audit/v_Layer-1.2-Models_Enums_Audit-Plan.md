# Layer 1 (Models & ENUMs) - Actionable Audit Plan

**Date:** 2025-05-19
**Version:** 2.0
**Author:** Cascade
**Last Updated:** 2025-05-19 (Updated with Supabase File Registry numbers)

## Purpose

This document provides a practical, actionable audit plan for Layer 1 (Models & ENUMs) of the ScraperSky backend. It is organized by workflow, with specific files to audit and principles to verify for each file. The goal is to systematically identify and address technical debt while ensuring compliance with architectural standards.

> **SUPABASE FILE AUDIT INTEGRATION**: This audit plan has been enhanced with file numbers from the Supabase File Audit System. Each file now includes its unique identifier (e.g., `[FILE:0100]`) that can be used to query the database for additional metadata and track audit progress.

## Layer 1 Audit Principles

Based on the Blueprint, SOP, and Conventions Guide, these are the key principles to verify for each file:

1. **ORM Usage** - All database access must use SQLAlchemy ORM exclusively
2. **File Naming** - `src/models/{source_table_name}.py` (singular, snake_case)
3. **Class Naming** - `{SourceTableTitleCase}` for models
4. **ENUM Naming** - `{EntityName}StatusEnum` for status enums
5. **Status Fields** - Should follow `{workflow_name}_{type}_status` pattern
6. **No Tenant IDs** - No direct tenant ID references in models
7. **Table Names** - Table names should match `source_table_plural_name`
8. **Column Types** - Appropriate SQLAlchemy types for columns
9. **Relationships** - Properly defined SQLAlchemy relationships
10. **Documentation** - Classes and methods properly documented



## Audit Process

For each file, follow this process:

1. **Open the file** and review its contents
2. **Check each principle** listed in the checklist
3. **Document findings** including:
   - Compliance status (Compliant/Non-compliant)
   - Issues identified
   - Recommended changes
4. **Create Jira tickets** for any issues that need to be addressed
5. **Update the checklist** with the audit results

### Handling the 200-Line Limitation with AI

When using AI to assist with the audit, be aware of the 200-line limitation when viewing files:

1. **For files under 200 lines** (most Layer 1 models should be):
   - Use `view_file` with StartLine=0 and EndLine=200 to view the entire file

2. **For files over 200 lines**:
   - **Option 1:** Use multiple `view_file` calls with different line ranges
     - First call: Lines 0-200
     - Second call: Lines 201-400
     - And so on until the entire file is reviewed

   - **Option 2:** Use `view_code_item` to focus on specific classes or methods
     - Example: `view_code_item` with File="/path/to/file.py" and NodePaths=["ClassName", "ClassName.method_name"]
     - This is more efficient for targeted reviews of specific components

3. **Recommended approach for Layer 1 audit**:
   - Start with `view_file` for the first 200 lines
   - If the file is larger, check the file structure and use `view_code_item` for specific models and ENUMs
   - Document line ranges viewed to ensure complete coverage

## Technical Debt Resolution Priority

Based on the impact and effort required, here's the recommended order for addressing technical debt:

1. **High Priority** - Issues that violate core architectural principles:
   - Non-ORM database access
   - Direct tenant ID references
   - Missing or incorrect relationships

2. **Medium Priority** - Issues that affect consistency and maintainability:
   - Incorrect status field naming
   - Incorrect ENUM naming
   - Incorrect table names

3. **Low Priority** - Issues that are primarily cosmetic:
   - Documentation improvements
   - Minor naming inconsistencies

## Next Steps After Layer 1 Audit

After completing the Layer 1 audit:

1. **Compile findings** into a summary report
2. **Prioritize technical debt** based on severity and impact
3. **Create a remediation plan** with specific tasks and timelines
4. **Move to Layer 3 (Routers) audit** using a similar approach
5. **Update the comprehensive file mapping** with audit findings

This approach ensures that we systematically address technical debt while maintaining a clear focus on making tangible progress rather than just producing documentation.

## Audit Checklist by Workflow

### WF1: SingleSearch (Google Maps Integration)

#### Files to Audit:

- [ ] `src/models/place.py` [FILE:0100]
- [ ] `src/models/place_search.py` [FILE:0101]

- [ ] **ORM Usage:** Verify exclusive use of SQLAlchemy ORM
- [ ] **Class Naming:** Confirm class name is `PlaceSearch`
- [ ] **ENUM Naming:** Verify `PlaceSearchStatusEnum` follows convention
- [ ] **Status Fields:** Check if status fields follow `{workflow_name}_{type}_status` pattern
  - Current: `status`
  - Should be: `business_search_curation_status` and `business_search_processing_status`
- [ ] **No Tenant IDs:** Confirm no direct tenant ID references
- [ ] **Table Name:** Verify table name is `place_searches`
- [ ] **Column Types:** Check appropriate SQLAlchemy types
- [ ] **Relationships:** Verify properly defined relationships to `Place`
- [ ] **Documentation:** Confirm classes and methods are documented

#### Checklist for `src/models/place.py` [FILE:0100]:

- [ ] **ORM Usage:** Verify file uses SQLAlchemy ORM exclusively
- [ ] **File Naming:** Confirm file name is `place.py`
- [ ] **Class Naming:** Confirm class name is `Place`
- [ ] **ENUM Naming:** Verify `PlaceStatusEnum` follows convention
- [ ] **Status Fields:** Check if status fields follow `{workflow_name}_{type}_status` pattern
  - Current: `status`
  - Should be: `business_search_curation_status` and `business_search_processing_status`
- [ ] **File Header:** Add standardized file header with FILE_NUMBER: 0100
- [ ] **No Tenant IDs:** Confirm no direct tenant ID references
- [ ] **Table Name:** Verify table name is `places`
- [ ] **Column Types:** Check appropriate SQLAlchemy types
- [ ] **Relationships:** Verify properly defined relationships
- [ ] **Documentation:** Confirm classes and methods are documented

### WF2: StagingEditor (Places Staging)

#### Files to Audit:

- [ ] `src/models/place.py` [FILE:0100] (shared with WF1)
- [ ] `src/models/profile.py` [FILE:0113]

- [ ] **Status Fields:** Check if additional status fields for WF2 follow convention
  - Current: `deep_scan_status`
  - Should be: `staging_curation_status` and `staging_processing_status`
- [ ] **ENUM Naming:** Verify `DeepScanStatusEnum` follows convention
  - Should be: `StagingProcessingStatusEnum`

### WF3: LocalBusinessCuration

#### Files to Audit:

- [ ] `src/models/place.py` [FILE:0100] (shared with WF1, WF2)
- [ ] `src/models/local_business.py` [FILE:0102]

- [ ] **ORM Usage:** Verify exclusive use of SQLAlchemy ORM
- [ ] **Class Naming:** Confirm class name is `LocalBusiness`
- [ ] **ENUM Naming:** Verify status enums follow convention
- [ ] **Status Fields:** Check if status fields follow `{workflow_name}_{type}_status` pattern
  - Current: `status`, `domain_extraction_status`
  - Should be: `local_business_curation_status` and `local_business_processing_status`
- [ ] **No Tenant IDs:** Confirm no direct tenant ID references
- [ ] **Table Name:** Verify table name is `local_businesses`
- [ ] **Column Types:** Check appropriate SQLAlchemy types
- [ ] **Relationships:** Verify properly defined relationships
- [ ] **Documentation:** Confirm classes and methods are documented

### WF4: DomainCuration

#### Files to Audit:

- [ ] `src/models/domain.py` [FILE:0103]
- [ ] `src/models/contact.py` [FILE:0110]

- [ ] **ORM Usage:** Verify exclusive use of SQLAlchemy ORM
- [ ] **Class Naming:** Confirm class name is `Domain`
- [ ] **ENUM Naming:** Verify `SitemapCurationStatusEnum` and `SitemapAnalysisStatusEnum` follow convention
  - Should be: `DomainCurationStatusEnum` and `DomainProcessingStatusEnum`
- [ ] **Status Fields:** Check if status fields follow `{workflow_name}_{type}_status` pattern
  - Current: `sitemap_curation_status`, `sitemap_analysis_status`
  - Should be: `domain_curation_status` and `domain_processing_status`
- [ ] **No Tenant IDs:** Confirm no direct tenant ID references
- [ ] **Table Name:** Verify table name is `domains`
- [ ] **Column Types:** Check appropriate SQLAlchemy types
- [ ] **Relationships:** Verify properly defined relationships
- [ ] **Documentation:** Confirm classes and methods are documented

### WF5: SitemapCuration

#### Files to Audit:

- [ ] `src/models/sitemap.py` [FILE:0104]
- [ ] `src/models/sitemap_file.py` [FILE:0112]

- [ ] **ORM Usage:** Verify exclusive use of SQLAlchemy ORM
- [ ] **Class Naming:** Confirm class name is `Sitemap`
- [ ] **ENUM Naming:** Verify `SitemapImportCurationStatusEnum` and `SitemapImportProcessStatusEnum` follow convention
  - Should be: `SitemapCurationStatusEnum` and `SitemapProcessingStatusEnum`
- [ ] **Status Fields:** Check if status fields follow `{workflow_name}_{type}_status` pattern
  - Current: `deep_scrape_curation_status`, `sitemap_import_status`
  - Should be: `sitemap_curation_status` and `sitemap_processing_status`
- [ ] **No Tenant IDs:** Confirm no direct tenant ID references
- [ ] **Table Name:** Verify table name is `sitemap_files`
- [ ] **Column Types:** Check appropriate SQLAlchemy types
- [ ] **Relationships:** Verify properly defined relationships
- [ ] **Documentation:** Confirm classes and methods are documented

### WF6: SitemapImport

#### Files to Audit:

- [ ] `src/models/sitemap.py` [FILE:0104] (shared with WF5)
- [ ] `src/models/job.py` [FILE:0111]

- [ ] **Status Fields:** Check if additional status fields for WF6 follow convention
  - Current: `sitemap_import_status`
  - Should be: `sitemap_import_curation_status` and `sitemap_import_processing_status`

#### `src/models/page.py`

- [ ] **ORM Usage:** Verify exclusive use of SQLAlchemy ORM
- [ ] **Class Naming:** Confirm class name is `Page`
- [ ] **ENUM Naming:** Verify `PageStatusEnum` follows convention
- [ ] **Status Fields:** Check if status fields follow `{workflow_name}_{type}_status` pattern
  - Current: `status`
  - Should be: `page_import_status` or similar
- [ ] **No Tenant IDs:** Confirm no direct tenant ID references
- [ ] **Table Name:** Verify table name is `pages`
- [ ] **Column Types:** Check appropriate SQLAlchemy types
- [ ] **Relationships:** Verify properly defined relationships
- [ ] **Documentation:** Confirm classes and methods are documented

### WF7: PageCuration

#### `src/models/page.py` (shared with WF6)

- [ ] **ENUM Naming:** Verify `PageCurationStatus` follows convention
  - Should be: `PageCurationStatusEnum`
- [ ] **Status Fields:** Check if status fields follow `{workflow_name}_{type}_status` pattern
  - Current: `page_curation_status`, `page_processing_status`
  - This is compliant with the convention

## Reference Documents

- **Blueprint:** [Layer-1.1-Models_Enums_Blueprint.md](/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_10_Final_Audit/Layer-1.1-Models_Enums_Blueprint.md)
- **SOP:** [Layer-1.3-Models_Enums_AI_Audit_SOP.md](/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_10_Final_Audit/Layer-1.3-Models_Enums_AI_Audit_SOP.md)
- **Conventions:** [CONVENTIONS_AND_PATTERNS_GUIDE.md](../../Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md)
- **File Audit System:** [Database Queries](/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/tools/database_queries.sql)

## Database Integration

To update the audit status of files in this audit plan, use the following SQL query:

```sql
-- Update audit status for a file
UPDATE file_audit
SET
  audit_status = 'IN_PROGRESS', -- Options: 'NOT_STARTED', 'IN_PROGRESS', 'COMPLETED'
  updated_at = NOW()
WHERE file_number = '0100'; -- Replace with target file number
```

You can generate a report of Layer 1 audit progress using:

```sql
SELECT
  file_number,
  file_path,
  audit_status,
  audited_by,
  audit_date
FROM file_audit
WHERE layer_number = 1
ORDER BY file_number;
