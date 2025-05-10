# ScraperSky Workflow Audit Journal

_Last updated: 2025-05-05T08:10:30-07:00_

This journal serves as the authoritative record of all findings, issues, patterns, and technical debt discovered during workflow audits. Each entry is timestamped and cross-referenced to the relevant workflow(s) and files.

## Table of Contents

1. [Purpose](#purpose)
2. [Entry Format](#entry-format)
3. [Critical Findings Registry](#critical-findings-registry)
4. [Workflow-Specific Findings](#workflow-specific-findings)
5. [Architectural Patterns Discovered](#architectural-patterns-discovered)
6. [Technical Debt Registry](#technical-debt-registry)
7. [Remediation Tracking](#remediation-tracking)

---

## Purpose

This journal provides:

- A chronological record of all workflow audit findings
- Cross-references between findings and specific workflows/files
- Tracking of technical debt and architectural non-compliance
- Documentation of architectural patterns discovered during audits
- A central registry for remediation planning and status tracking

All entries must include timestamps (ISO8601 with timezone) and attribution.

---

## Entry Format

Each journal entry should follow this format:

```markdown
### [YYYY-MM-DD] Finding Title

- **Workflow**: WF# - Name
- **Files**: /path/to/file.py
- **Severity**: [CRITICAL|HIGH|MEDIUM|LOW]
- **Type**: [ORM Violation|API Inconsistency|Architectural Pattern|Security Issue|...]
- **Discovered By**: [Name/AI]
- **Timestamp**: YYYY-MM-DDThh:mm:ssZ

**Description**:
Detailed description of the finding...

**Impact**:
How this impacts the system, security, maintenance, etc.

**Remediation Plan**:

1. Step one...
2. Step two...

**Reference(s)**:

- JIRA: TICKET-123
- Canonical YAML: /path/to/YAML
- Related PR: #123
```

---

## Critical Findings Registry

This section tracks all CRITICAL and HIGH severity findings across all workflows.

### [2025-05-04] Raw SQL in places_staging.py violates Absolute ORM Requirement

- **Workflow**: WF2 - Staging Editor
- **Files**: src/routers/places_staging.py
- **Severity**: CRITICAL
- **Type**: ORM Violation
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-04T23:43:15-07:00

**Description**:
The `update_places_status_batch` function in places_staging.py uses raw SQL statements for updating place status and deep_scan_status. This violates the architectural mandate for ORM-only database access specified in the Absolute ORM Requirement document.

**Impact**:

- Bypasses SQLAlchemy ORM safeguards and type checking
- Creates inconsistent patterns across the codebase
- Increases maintenance overhead for schema changes
- Potential SQL injection vulnerability if parameters aren't properly sanitized

**Remediation Plan**:

1. Replace direct SQL with SQLAlchemy ORM queries
2. Use proper relationship loading with session.query(Place).filter(...)
3. Update models as needed if relationships are missing
4. Add test coverage to verify refactored functionality

**Reference(s)**:

- JIRA: SCRSKY-224
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF2-StagingEditor_CANONICAL.yaml
- Architectural Mandate: /Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md

### [2025-05-04] Unused trigger_deep_scan parameter creates misleading API contract

- **Workflow**: WF2 - Staging Editor
- **Files**: src/routers/places_staging.py
- **Severity**: MEDIUM
- **Type**: API Inconsistency
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-04T23:43:30-07:00

**Description**:
The API defines a query parameter `trigger_deep_scan: bool` that is completely ignored by the implementation. The queuing logic is based solely on the status being 'Selected', making this parameter misleading for API consumers.

**Impact**:

- Creates a misleading API contract
- Confuses developers using the API
- Documentation will be inconsistent with actual behavior

**Remediation Plan**:

1. Remove the unused parameter OR
2. Implement the parameter's functionality OR
3. Document clearly that the parameter is deprecated

**Reference(s)**:

- JIRA: SCRSKY-225
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF2-StagingEditor_CANONICAL.yaml

---

## Workflow-Specific Findings

### WF1 - Single Search

**Workflow Description**:
Users initiate a business discovery search via the "Single Search" UI tab, resulting in backend processing via the Google Maps API and storage of results in the database for later processing in WF2-Staging Editor.

**Micro-Work Order**: /Docs_7_Workflow_Canon/Micro-Work-Orders/WF1-SingleSearch_micro_work_order.md

#### [2025-05-05] Raw SQL Query in places_storage_service.py

- **Workflow**: WF1 - Single Search Discovery
- **Files**: src/services/places/places_storage_service.py
- **Severity**: HIGH
- **Type**: ORM Violation
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T08:05:10-07:00

**Description**:
The storage service uses raw SQL queries for place data insertion and updates, violating the ABSOLUTE_ORM_REQUIREMENT architectural principle. This is particularly concerning because it creates an inconsistent pattern across the codebase and bypasses SQLAlchemy's protections.

**Impact**:

- Violates architectural principles
- Potential SQL injection vectors if parameters are not properly sanitized
- Increased maintenance overhead for schema changes
- Inconsistent patterns across the codebase

**Remediation Plan**:

1. Replace raw SQL with SQLAlchemy ORM queries
2. Add proper relationship handling through ORM models
3. Add tests to verify functionality after refactoring

**Reference(s)**:

- JIRA: SCRSKY-225
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF1-SingleSearch_CANONICAL.yaml
- Architectural Mandate: /Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md

#### [2025-05-05] Missing Transaction Boundary in API Router

- **Workflow**: WF1 - Single Search Discovery
- **Files**: src/routers/google_maps_api.py
- **Severity**: MEDIUM
- **Type**: Transaction Management
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T08:15:20-07:00

**Description**:
The API router lacks explicit transaction boundary using 'async with session.begin()' as required by architectural principles. According to our architectural guidelines, routers should own transaction boundaries while services should be transaction-aware but not create transactions themselves.

**Impact**:

- Inconsistent transaction handling pattern
- Potential for orphaned records if background processing fails
- Risk of partial updates being committed

**Remediation Plan**:

1. Refactor router to use explicit 'async with session.begin()'
2. Pass transaction session to services
3. Update service code to work with provided transaction
4. Add tests to verify transaction rollback on errors

**Reference(s)**:

- JIRA: SCRSKY-250
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF1-SingleSearch_CANONICAL.yaml

#### [2025-05-05] Undocumented Workflow Connection

- **Workflow**: WF1 - Single Search Discovery
- **Files**: src/models/place.py
- **Severity**: MEDIUM
- **Type**: Documentation
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T08:25:35-07:00

**Description**:
The producer-consumer relationship between WF1 and WF2 was not documented in the canonical YAML or dependency trace. Place records created by WF1 with status='New' are consumed by WF2-Staging Editor, but this integration was not explicitly documented.

**Impact**:

- Missing critical workflow integration information
- Risk of breaking changes to the status field breaking downstream workflows
- Difficulty understanding the complete system flow

**Remediation Plan**:

1. Add workflow_connections section to WF1 YAML (DONE)
2. Add producer-consumer annotations to place.py (DONE)
3. Update the linear steps document to note the workflow connection
4. Create a visual workflow integration map

**Reference(s)**:

- JIRA: SCRSKY-252
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF1-SingleSearch_CANONICAL.yaml

### WF2 - Staging Editor

#### [2025-05-04] JobService integration incomplete in PlacesDeepService

- **Workflow**: WF2 - Staging Editor
- **Files**: src/services/places_deep_service.py
- **Severity**: LOW
- **Type**: Integration Inconsistency
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-04T23:44:15-07:00

**Description**:
The background job progress tracking is not fully integrated with the JobService, resulting in limited observability for job status.

**Impact**:

- Reduced visibility into job progress
- Limited ability to track and troubleshoot processing issues

**Remediation Plan**:

1. Update PlacesDeepService to use JobService for tracking
2. Add proper job status updates
3. Update UI to display job status

**Reference(s)**:

- JIRA: SCRSKY-226
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF2-StagingEditor_CANONICAL.yaml

### WF3 - Local Business

#### [2025-05-05] No eligibility check before queueing domain extraction

- **Workflow**: WF3 - Local Business Curation
- **Files**: src/routers/local_businesses.py
- **Severity**: MEDIUM
- **Type**: Business Logic Gap
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T00:15:30-07:00

**Description**:
Currently, all local businesses with status="Selected" are automatically queued for domain extraction, regardless of whether they have a valid website_url. This could lead to unnecessary processing and errors.

**Impact**:

- Wasted processing resources on businesses without websites
- Potential errors in downstream processing
- Confusing error messages

**Remediation Plan**:

1. Add preliminary validation in the router to check if website_url exists
2. Only queue items with a non-empty website_url
3. Add appropriate error message for items without website URLs

**Reference(s)**:

- JIRA: SCRSKY-230
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF3-LocalBusinessCuration_CANONICAL.yaml

#### [2025-05-05] Naming confusion in sitemap_scheduler.py

- **Workflow**: WF3 - Local Business Curation
- **Files**: src/services/sitemap_scheduler.py
- **Severity**: LOW
- **Type**: Code Organization
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T00:15:30-07:00

**Description**:
Despite being named "sitemap_scheduler.py", this file handles multiple types of background processing, including domain extraction. This naming can be confusing for new developers.

**Impact**:

- Reduced code discoverability
- Increased onboarding time for new developers
- Potential confusion about module responsibilities

**Remediation Plan**:

1. Consider renaming to "background_scheduler.py" or similar
2. Alternatively, split into domain-specific schedulers
3. Update documentation to clarify multi-purpose nature

**Reference(s)**:

- JIRA: SCRSKY-231
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF3-LocalBusinessCuration_CANONICAL.yaml

### WF4 - Domain Curation (2025-05-05)

**Workflow Description**:
Domain objects are marked with `sitemap_curation_status` = 'Selected' in the Domain Curation UI tab, resulting in them being queued for sitemap analysis/processing in the backend.

**Micro-Work Order**: /Docs_7_Workflow_Canon/Micro-Work-Orders/WF4-DomainCuration_micro_work_order.md

#### [2025-05-05] Direct API call to internal endpoint

- **Workflow**: WF4 - Domain Curation
- **Files**: src/services/domain_to_sitemap_adapter_service.py
- **Severity**: LOW
- **Type**: Architectural Pattern
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T00:26:15-07:00

**Description**:
The domain_to_sitemap_adapter_service.py makes a direct HTTP call to another internal endpoint (/api/v3/sitemap/scan) rather than using a more direct service-to-service communication pattern. This creates an unnecessary network hop for what could be a direct function call.

**Impact**:

- Additional network latency
- Potential for network-related failures
- Redundant authentication overhead
- More difficult to trace and debug

**Remediation Plan**:

1. Refactor to use direct service call instead of HTTP request
2. Create a proper service interface for sitemap scanning
3. Update scheduler to use the refactored service

**Reference(s)**:

- JIRA: SCRSKY-232
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF4-DomainCuration_CANONICAL.yaml

#### [2025-05-05] Hardcoded internal API URL

- **Workflow**: WF4 - Domain Curation
- **Files**: src/services/domain_to_sitemap_adapter_service.py
- **Severity**: LOW
- **Type**: Configuration Issue
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T00:26:30-07:00

**Description**:
The adapter service contains a hardcoded INTERNAL_API_BASE_URL for API calls. This makes it difficult to use different configurations for different environments.

**Impact**:

- Reduced flexibility for deployment
- Potential issues in different environments (dev, test, prod)
- Difficult to modify without code changes

**Remediation Plan**:

1. Move INTERNAL_API_BASE_URL to configuration settings
2. Use environment variables for overrides
3. Update documentation with configuration instructions

**Reference(s)**:

- JIRA: SCRSKY-233
- Canonical YAML: /Docs_7_Workflow_Canon/workflows/WF4-DomainCuration_CANONICAL.yaml

### WF5 - Sitemap Curation (2025-05-05)

**Workflow Description**:
Sitemap file objects are marked with `deep_scrape_curation_status` = 'Selected' in the Sitemap Curation UI tab, resulting in them being queued for deep scrape processing in the backend.

**Micro-Work Order**: /Docs_7_Workflow_Canon/Micro-Work-Orders/WF5-SitemapCuration_micro_work_order.md

#### [2025-05-05] Missing scheduler implementation for sitemap files (RESOLVED)

- **Workflow**: WF5 - Sitemap Curation
- **Files**: src/routers/sitemap_files.py, src/services/sitemap_scheduler.py
- **Severity**: CRITICAL
- **Type**: Implementation Gap
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-04T22:45:30-07:00

**Description**:
During the audit of the WF5-Sitemap Curation workflow, a critical gap was discovered: there is no implementation for background processing of SitemapFile records that have been queued for URL extraction. The UI allows marking files for processing, but there is no scheduler job to pick up these queued files.

**Impact**:

- SitemapFile records marked for URL extraction remain in a queued state indefinitely
- No URLs are extracted from sitemap files, breaking the data pipeline
- The feature appears to be available in the UI but doesn't function

**Investigation**:
Reviewed sitemap_scheduler.py and found it handles domain extraction but not sitemap processing. The deep_scrape_curation_status field in SitemapFile model is properly implemented, but there is no corresponding consumer for the "Queued" status.

**Status Update**: RESOLVED. Investigation revealed that this functionality is implemented in a separate workflow (WF6-Sitemap Import) that integrates with WF5. The implementation exists in src/services/sitemap_import_scheduler.py and src/services/sitemap_import_service.py. These components poll for sitemap files with sitemap_import_status = Queued, process them, and create Page records for URLs. Complete documentation has been created for WF6.

**Remediation Plan**:
Original remediation plan no longer needed as implementation exists. Updated workflow documentation to clearly show the connection between WF5 and WF6.

**Reference(s)**:

- SitemapFile model with status fields: src/models/sitemap.py
- UI implementation: src/routers/sitemap_files.py
- Status update method: src/routers/sitemap_files.py:update_sitemap_files_status_batch
- WF6 implementation: src/services/sitemap_import_scheduler.py, src/services/sitemap_import_service.py
- WF6 documentation: /Docs_7_Workflow_Canon/workflows/WF6-SitemapImport_CANONICAL.yaml

#### [2025-05-05] Direct API call to internal endpoint

- **Workflow**: WF4 - Domain Curation
- **Files**: src/services/domain_to_sitemap_adapter_service.py
  {{ ... }}

**Reference(s)**:

- JIRA: SCRSKY-235
- Remediation Target: 2025-05-20

---

## Workflow-Specific Findings

### WF6 - Sitemap Import

#### [2025-05-05] WF6-Sitemap Import Workflow Audit

- **Workflow**: WF6 - Sitemap Import
- **Files**: src/services/sitemap_import_scheduler.py, src/services/sitemap_import_service.py
- **Severity**: MEDIUM
- **Type**: Architectural Pattern, Transaction Management, Documentation
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T02:15:30-07:00

**Description**:
Complete audit of the WF6-Sitemap Import workflow revealed a well-designed background service that processes queued sitemap files, extracts URLs, and creates Page records. This workflow is a critical component that integrates with WF5-Sitemap Curation but was previously undocumented in the workflow canon.

**Impact**:

- Provides essential background processing for sitemap files queued in WF5
- Creates Page records that may be used by downstream processes
- Follows most architectural principles with minor exceptions

**Key Findings**:

1. **Transaction Management Partially Compliant**: Service handles transactions appropriately, but dev_tools.py endpoints should own transaction boundaries according to architectural principles.
2. **Documentation Gap**: WF6 was not previously documented in the main workflow documentation despite being a critical component.
3. **No Retry Mechanism**: The workflow lacks an automatic retry mechanism for transient network failures when fetching sitemap files.

**Technical Debt Identified**:

1. **Incomplete Error Tracking**: While errors are logged, there's no centralized error tracking or alerting.
2. **Limited URL Validation**: URLs extracted from sitemaps undergo minimal validation before being stored.
3. **No Processing Metrics**: The workflow doesn't track metrics like processing time, success rates, or URL counts.

**Architectural Compliance**:

- ORM Usage: Compliant
- API Versioning: Compliant
- Transaction Management: Partially Compliant
- JWT Authentication Boundaries: Compliant

**Documentation Created**:

1. Dependency Trace: /Docs/Docs_7_Workflow_Canon/Dependency_Traces/WF6-SitemapImport_dependency_trace.md
2. Linear Steps: /Docs/Docs_7_Workflow_Canon/Linear-Steps/WF6-SitemapImport_linear_steps.md
3. Canonical YAML: /Docs/Docs_7_Workflow_Canon/workflows/WF6-SitemapImport_CANONICAL.yaml
4. Micro Work Order: /Docs/Docs_7_Workflow_Canon/Micro-Work-Orders/WF6-SitemapImport_micro_work_order.md

**Remediation Plan**:

1. Update dev_tools.py to follow transaction boundary ownership pattern
2. Update 1-main_routers.md and 1.1-background-services.md with WF6 references
3. Implement retry mechanism for HTTP requests with exponential backoff
4. Add metrics collection for operational monitoring

**Reference(s)**:

- Connection to WF5: `Docs_7_Workflow_Canon/workflows/WF5-SitemapCuration_CANONICAL.yaml`
- Code components: `src/services/sitemap_import_service.py` and `src/services/sitemap_import_scheduler.py`
- API versioning standards memory: `33b0290b-5be6-459e-ac03-12b1acfd2055`
- Transaction management principles memory: `c7d8082c-3ff0-48e3-b5be-0d462ec8584a`

---

## Architectural Patterns Discovered

### [2025-05-05] Producer-Consumer Workflow Pattern

- **Current State**: The pattern is largely adhered to, but some workflows exhibit tight coupling or direct function calls instead of relying purely on status-based triggers.
- **Reference**: See [PRODUCER_CONSUMER_WORKFLOW_PATTERN.md](../../PRODUCER_CONSUMER_WORKFLOW_PATTERN.md) for details.
- **Action**: Review and refactor workflows to strictly follow the decoupled producer/consumer pattern using status field triggers.

```
┌───────────┐          ┌───────────┐          ┌───────────┐          ┌───────────┐
│           │ produces  │           │ produces  │           │ produces  │           │
│    WF1    ├───────────▶    WF2    ├───────────▶    WF3    ├───────────▶    WF4    │
│           │  places   │           │  places   │           │local_biz  │           │
└─────┬─────┘  table    └─────┬─────┘  table    └─────┬─────┘  table    └─────┬─────┘
      │                        │                       │                       │
      │        ┌───────────────┘                      │                       │
      │        │                ┌──────────────────────┘                      │
      │        ▼                ▼                                             ▼
      │    consumes        consumes                                       consumes
      └──────┐ from WF1      from WF2                                       from WF3
             │
  No upstream
   consumer
```

**Impact**:

- Provides a clear, standardized pattern for creating new workflows
- Establishes clean boundaries between different processing stages
- Enables asynchronous processing with clear state tracking
- Supports scaling individual workflow components independently

**Implementation Details**:
Each workflow follows this common implementation pattern:

1. **Router**: Contains endpoint that updates primary status field and may trigger secondary status update
2. **Background Service**: Polls for records with secondary status="Queued"
3. **Processing Service**: Contains business logic to process the record
4. **Database Models**: Include appropriate status fields and transition states

**Reference(s)**:

- [PRODUCER_CONSUMER_WORKFLOW_PATTERN.md](../../PRODUCER_CONSUMER_WORKFLOW_PATTERN.md)
- All workflow canonical YAML files in `/Docs/Docs_7_Workflow_Canon/workflows/`

---

### SHARED - All Workflows

#### [2025-05-05] Duplicate enum definitions across model files

- **Workflow**: ALL (SHARED)
- **Files**: src/models/enums.py, src/models/domain.py, src/models/sitemap.py, src/models/page.py, src/models/place.py
- **Severity**: MEDIUM
- **Type**: Technical Debt, Code Organization
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-05T09:50:00-07:00

**Description**:
During the workflow documentation audit, we discovered that several enum classes are defined in multiple places in the codebase. For example, `SitemapAnalysisStatusEnum` is defined both in `src/models/domain.py` and `src/models/enums.py`. This creates confusion about which enum definition is authoritative and could lead to inconsistencies if definitions drift apart over time.

**Impact**:

- Violates DRY (Don't Repeat Yourself) principle
- Creates maintenance burden when enum values need to be updated
- Introduces risk of divergence between duplicate definitions
- Causes developer confusion about which definition to use

**Examples of Duplications**:

- `SitemapAnalysisStatusEnum`: Defined in both `src/models/domain.py` and `src/models/enums.py`
- Other potential duplicates exist across model files and enums.py

**Remediation Plan**:

1. Audit all enum definitions across the codebase to identify all duplicates
2. Determine a standardized location pattern (either all in model files or all in central enums.py)
3. Consolidate duplicate definitions to a single location
4. Update all references to use the single canonical definition
5. Add documentation in PRODUCER_CONSUMER_WORKFLOW_PATTERN.md to specify the standard location for enum definitions

**Reference(s)**:

- JIRA: SCRSKY-260
- Related Files: All workflow YAML files that reference enums

---

#### [2025-05-06] Inconsistent enum naming patterns and non-standard enum values

- **Workflow**: ALL (SHARED)
- **Files**: src/models/sitemap.py, src/models/domain.py, src/models/page.py
- **Severity**: HIGH
- **Type**: Technical Debt, Naming Conventions, Standardization
- **Discovered By**: Cascade AI
- **Timestamp**: 2025-05-06T17:15:00-07:00

**Description**:
During standardization research, we identified inconsistent naming patterns and non-standard values in status enum classes across workflow models. These deviations from the established standards create confusion and maintenance challenges:

1. **Enum naming inconsistencies**:

   - Standard pattern is `{WorkflowNameTitleCase}CurationStatus` and `{WorkflowNameTitleCase}ProcessingStatus` as seen in `PageCurationStatus` and `PageProcessingStatus`
   - Non-standard implementations found in:
     - `SitemapImportCurationStatusEnum` (should be `SitemapImportCurationStatus` without "Enum" suffix)
     - `SitemapCurationStatusEnum` (uses source table rather than workflow name pattern)

2. **Non-standard enum values**:

   - Standard CurationStatus values: `New, Queued, Processing, Complete, Error, Skipped`
   - Standard ProcessingStatus values: `Queued, Processing, Complete, Error`
   - Non-standard implementations found in:
     - `SitemapImportCurationStatusEnum`: Uses `Selected` instead of `Queued`, adds `Maybe`, `Not_a_Fit`, `Archived`
     - `SitemapImportProcessStatusEnum`: Uses `Completed` (instead of `Complete`), adds non-standard `Submitted`
     - `SitemapCurationStatusEnum`: Uses `Selected` instead of `Queued`, adds `Maybe`, `Not_a_Fit`, `Archived`
     - `SitemapAnalysisStatusEnum`: Uses `Completed` instead of `Complete`

3. **Base class inconsistencies**:
   - Standard pattern uses `str, Enum` (seen in `PageCurationStatus`)
   - Legacy implementations use `enum.Enum` (all non-standard enums)

**Impact**:

- Violates the standardized dual-status update pattern, creating inconsistency in how workflows interact
- Creates confusion for developers implementing new workflows without clear naming standards
- Makes it difficult to create generic utilities that work across all workflows
- Increases risk of errors when modifying or extending existing workflows
- Complicates API documentation and integration due to inconsistent status value names

**Remediation Plan**:

1. Document all non-standard enum implementations in a comprehensive inventory
2. Determine migration approach for each non-standard enum:
   - Rename enum classes to follow `{WorkflowNameTitleCase}CurationStatus` pattern
   - Standardize base class to `str, Enum`
   - Map legacy status values to standard values (e.g., `Selected` → `Queued`)
3. Create database migration scripts for enum type changes
4. Update all code references to use new enum names and values
5. Update API documentation to reflect standardized values
6. Add validation in CI/CD pipeline to enforce standard enum naming and values

**Reference(s)**:

- JIRA: SCRSKY-NEW (To be created)
- Related documentation: WORKFLOW_STANDARDIZATION_Q&A FU4 - Python Backend - Models.md
- Reference implementation: src/models/page.py (PageCurationStatus, PageProcessingStatus)

---

## Remediation Tracking

| Issue ID | Description                                            | Severity | JIRA       | Target Date | Status   | Completed Date                             |
| -------- | ------------------------------------------------------ | -------- | ---------- | ----------- | -------- | ------------------------------------------ |
| WF2-1    | Raw SQL in places_staging.py                           | CRITICAL | SCRSKY-224 | 2025-05-15  | OPEN     | -                                          |
| WF2-2    | Unused trigger_deep_scan parameter                     | MEDIUM   | SCRSKY-225 | 2025-05-20  | OPEN     | -                                          |
| WF2-3    | Incomplete JobService integration                      | LOW      | SCRSKY-226 | 2025-05-30  | OPEN     | -                                          |
| WF3-1    | No eligibility check before queueing domain extraction | MEDIUM   | SCRSKY-230 | 2025-05-20  | OPEN     | -                                          |
| WF3-2    | Naming confusion in sitemap_scheduler.py               | LOW      | SCRSKY-231 | 2025-05-30  | OPEN     | -                                          |
| WF4-1    | Direct API call to internal endpoint                   | LOW      | SCRSKY-232 | 2025-05-30  | OPEN     | -                                          |
| WF4-2    | Hardcoded internal API URL                             | LOW      | SCRSKY-233 | 2025-05-30  | OPEN     | -                                          |
| WF1-1    | Raw SQL query in places_storage_service.py             | HIGH     | SCRSKY-225 | 2025-05-10  | OPEN     | -                                          |
| WF1-2    | Hardcoded connection params in places_service.py       | MEDIUM   | SCRSKY-226 | 2025-05-15  | OPEN     | -                                          |
| WF1-3    | Missing transaction boundary in API router             | MEDIUM   | SCRSKY-250 | 2025-05-15  | OPEN     | -                                          |
| WF1-4    | Insufficient error handling for API failures           | MEDIUM   | SCRSKY-251 | 2025-05-18  | OPEN     | -                                          |
| WF1-5    | Inconsistent documentation structure                   | HIGH     | SCRSKY-252 | 2025-05-10  | RESOLVED | Fixed YAML structure with actionable TODOs |
| WF5-1    | Missing scheduler implementation for sitemap files     | CRITICAL | SCRSKY-234 | 2025-05-15  | RESOLVED | Identified as WF6-Sitemap Import workflow  |
| WF6-1    | Transaction boundaries owned by service not router     | MEDIUM   | SCRSKY-235 | 2025-05-20  | OPEN     | -                                          |
| WF6-2    | No retry mechanism for HTTP failures                   | MEDIUM   | SCRSKY-236 | 2025-05-25  | OPEN     | -                                          |
| WF6-3    | Limited URL validation before database insertion       | LOW      | SCRSKY-237 | 2025-06-05  | OPEN     | -                                          |
| WF5-2    | Missing deep scrape service implementation             | HIGH     | SCRSKY-235 | 2025-05-20  | OPEN     | -                                          |
| SHARED-1 | Duplicate enum definitions in codebase                 | MEDIUM   | SCRSKY-260 | 2025-06-10  | OPEN     | -                                          |
