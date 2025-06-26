# Layer 4 (Services & Schedulers) - Actionable Audit Plan

**Date:** 2025-05-19
**Version:** 1.0
**Author:** Cascade

## Purpose

This document provides a practical, actionable audit plan for Layer 4 (Services & Schedulers) of the ScraperSky backend. It is organized by workflow, with specific files to audit and principles to verify for each file. The goal is to systematically identify and address technical debt while ensuring compliance with architectural standards.

## Layer 4 Audit Principles

Based on the Blueprint, SOP, and Conventions Guide, these are the key principles to verify for each service and scheduler file:

1. **Session Handling** - Services must accept an AsyncSession object as a parameter
2. **No Raw SQL** - No direct SQL queries (text(), execute(), etc.)
3. **Tenant Isolation** - All queries must include tenant ID filtering
4. **Error Handling** - Consistent error handling with appropriate logging
5. **File Structure & Naming** - `src/services/{workflow_name}_service.py` and `src/services/{workflow_name}_scheduler.py`
6. **Method Naming** - Consistent method naming conventions
7. **External API Usage** - All external API calls properly isolated and abstracted
8. **Scheduler Configuration** - Schedulers use settings for intervals and batch sizes
9. **Standardized Polling** - Use of `run_job_loop` helper for polling patterns
10. **Documentation** - Services properly documented with docstrings

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

1. **For files under 200 lines**:
   - Use `view_file` with StartLine=0 and EndLine=200 to view the entire file

2. **For files over 200 lines**:
   - **Option 1:** Use multiple `view_file` calls with different line ranges
     - First call: Lines 0-200
     - Second call: Lines 201-400
     - And so on until the entire file is reviewed
   - **Option 2:** Use `codebase_search` to find specific areas of concern
     - Search for raw SQL indicators: "text(", "execute(", etc.
     - Search for session handling: "AsyncSession", "session.", etc.

### Special Focus Areas

Based on known issues in the Layer 4 Services implementation, pay special attention to:

1. **Session Handling**:
   - Look for instances where a new session is created instead of accepting one as a parameter
   - Example: `session_scope()` or `get_session()` calls inside service methods

2. **Raw SQL Usage**:
   - Look for `text()` or `execute()` functions
   - Example: `existing_domain_query = text("""SELECT * FROM domains WHERE domain = :domain_url LIMIT 1""")`

3. **Scheduler Configuration**:
   - Verify schedulers are properly pulling configuration from settings
   - Example: `settings.scheduler.{workflow_name}_interval_minutes`

## Technical Debt Prioritization

When identifying technical debt in the services layer, use the following prioritization guidelines:

1. **High Priority** - Issues that affect system stability, security, or data integrity:
   - Raw SQL usage
   - Missing tenant isolation
   - Improper session handling
   - Critical error handling gaps

2. **Medium Priority** - Issues that affect consistency and maintainability:
   - Inconsistent method naming
   - Non-standard scheduler implementation
   - File structure/naming deviations
   - Insufficient error handling

3. **Low Priority** - Issues that are primarily stylistic or documentation-related:
   - Missing or incomplete docstrings
   - Minor naming inconsistencies
   - Non-critical logging issues

## Conclusion

This audit plan provides a systematic approach to reviewing Layer 4 (Services & Schedulers) components of the ScraperSky backend. By following this plan, we can ensure that all services and schedulers adhere to the architectural standards defined in the Blueprint and Conventions Guide, ultimately improving the maintainability and quality of the codebase.

## Audit Checklist by Workflow

### WF1-SingleSearch

#### `src/services/places/places_search_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **External API Usage:** Check Google Places API integration patterns
- [ ] **Documentation:** Confirm thorough documentation

#### `src/services/places/places_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Documentation:** Confirm thorough documentation

#### `src/services/places/places_storage_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Documentation:** Confirm thorough documentation

### WF2-StagingEditor

#### `src/services/places/places_staging_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Documentation:** Confirm thorough documentation

#### `src/services/places/places_staging_scheduler.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Scheduler Configuration:** Verify use of settings for intervals and batch sizes
- [ ] **Standardized Polling:** Check for use of `run_job_loop` helper
- [ ] **Documentation:** Confirm thorough documentation

### WF3-LocalBusinessCuration

#### `src/services/places/local_business_curation_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Documentation:** Confirm thorough documentation

#### `src/services/places/local_business_scheduler.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Scheduler Configuration:** Verify use of settings for intervals and batch sizes
- [ ] **Standardized Polling:** Check for use of `run_job_loop` helper
- [ ] **Documentation:** Confirm thorough documentation

### WF4-DomainCuration

#### `src/services/domain/domain_curation_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Documentation:** Confirm thorough documentation

#### `src/services/domain/domain_scheduler.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Scheduler Configuration:** Verify use of settings for intervals and batch sizes
- [ ] **Standardized Polling:** Check for use of `run_job_loop` helper
- [ ] **Documentation:** Confirm thorough documentation

### WF5-SitemapCuration

#### `src/services/sitemap/sitemap_curation_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Documentation:** Confirm thorough documentation

#### `src/services/sitemap/sitemap_scheduler.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Scheduler Configuration:** Verify use of settings for intervals and batch sizes
- [ ] **Standardized Polling:** Check for use of `run_job_loop` helper
- [ ] **Documentation:** Confirm thorough documentation

### WF6-SitemapImport

#### `src/services/sitemap/sitemap_import_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Documentation:** Confirm thorough documentation

#### `src/services/sitemap/sitemap_import_scheduler.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Scheduler Configuration:** Verify use of settings for intervals and batch sizes
- [ ] **Standardized Polling:** Check for use of `run_job_loop` helper
- [ ] **Documentation:** Confirm thorough documentation

### WF7-PageCuration

#### `src/services/page/page_curation_service.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Documentation:** Confirm thorough documentation

#### `src/services/page/page_scheduler.py`

- [ ] **Session Handling:** Verify service methods accept session parameter
- [ ] **No Raw SQL:** Check for absence of raw SQL queries
- [ ] **Tenant Isolation:** Verify tenant ID filtering in all queries
- [ ] **Error Handling:** Confirm proper error handling and logging
- [ ] **File Structure & Naming:** Evaluate file location and naming
- [ ] **Method Naming:** Verify consistent method naming patterns
- [ ] **Scheduler Configuration:** Verify use of settings for intervals and batch sizes
- [ ] **Standardized Polling:** Check for use of `run_job_loop` helper
- [ ] **Documentation:** Confirm thorough documentation

## Reference Documents

- **Blueprint:** [Layer-4-Services_Blueprint.md](/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md)
- **SOP:** [Layer-4-Services_AI_Audit_SOP.md](/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_10_Final_Audit/Layer-4-Services_AI_Audit_SOP.md)
- **Conventions:** [CONVENTIONS_AND_PATTERNS_GUIDE.md](/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md)
