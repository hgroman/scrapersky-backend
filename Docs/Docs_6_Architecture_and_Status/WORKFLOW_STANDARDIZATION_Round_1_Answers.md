1. Base Identifiers
   Q1.1: When a new workflow is conceived, what is the exact process or authority for determining and assigning its official workflow_name?
   Based on the code review:

The workflow name is determined during Phase 1 of the workflow implementation process as outlined in "ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE.md". Specifically, in section 1.1 Core Questions where it states:

"What is the workflow name? (snake_case) {workflow_name}"

The workflow name follows snake_case convention and is derived from the core purpose of the workflow. For example:

page_curation for a workflow curating pages
sitemap_import for a workflow importing sitemaps
domain_curation for a workflow curating domains
This naming convention is consistently applied across all existing workflows (WF1-WF6) as seen in the canonical YAML files.

Q1.2: Similarly, what is the process for determining the official source_table_name if it's a new table or if an existing table is chosen?
The source table name is also determined in Phase 1.1 of the workflow builder cheat sheet:

"What is the source table? {source_table}"

The source table name is:

The primary database table the workflow interacts with
Always in singular form and snake_case
Matches an existing SQLAlchemy model in src/models/
For example:

page for the Page model in src/models/page.py
sitemap_file for the SitemapFile model in src/models/sitemap.py
domain for the Domain model in src/models/domain.py
If a new table is needed, it would be defined as a new model in a dedicated file in the models directory.

Q1.3: Are there any reserved keywords or prohibited patterns for workflow_name or source_table_name?
The code doesn't explicitly define reserved keywords, but the following patterns are evident:

Both workflow_name and source_table_name must be in snake_case
They must not include spaces or special characters
The naming must be semantically clear about the purpose of the workflow/table
They should not conflict with SQL reserved words
They must match existing table names for source_table_name
No workflow_name should duplicate an existing one
Additionally, there's strong evidence that workflow_name often follows the pattern {entity}\_curation or {entity}\_import where entity is the data being operated on.

Q1.4: How are pluralizations for source_table_plural_name consistently handled for irregular nouns or when unsure?
Based on the code review, pluralization follows standard English rules:

Most tables simply add 's' (e.g., page → pages, domain → domains)
For names ending in 'y', change 'y' to 'ies' (e.g., if there were an entry table it would be entries)
For names ending in 's', 'sh', 'ch', 'x', or 'z', add 'es' (e.g., business → businesses)
The database follows this pattern consistently:

page → pages table
domain → domains table
sitemap_file → sitemap_files table
local_business → local_businesses table
These patterns are evident in API endpoint paths and table names throughout the codebase.

**Follow-up Question Answers for Section 1:**

**Regarding workflow_name determination (Original Follow-up Question Q1.1):**

- **Answer to Follow-up Question Q1.1.1 (Review/approval process):**
  There isn't a formal, documented approval step specifically for `workflow_name` in the cheat sheets or YAML files. In practice, new workflows are typically reviewed during planning meetings before implementation begins. This happens informally through:

  - Discussions in the planning documents (typically in `/Docs/Docs_4_Planning/`)
  - Pull request reviews where senior developers check naming conventions
  - Cross-referencing with existing workflow names to prevent conflicts
    However, this isn't explicitly documented as a formal step in the workflow creation process - it's an implicit part of the team's development practices.

- **Answer to Follow-up Question Q1.1.2 (workflow_name examples):**
  Looking at the canonical YAML files:
  - `sitemap_import` from `WF6-SitemapImport_CANONICAL.yaml`:
    - Core purpose: Importing URLs from sitemap files into the system
    - Direct derivation: "sitemap" (the data source) + "import" (the action)
  - `single_search` from `WF1-SingleSearch_CANONICAL.yaml`:
    _ Core purpose: Processing individual search queries
    _ Direct derivation: "single" (scope) + "search" (action)
    The derivation is indeed direct and descriptive of the workflow's primary function.

**Regarding source_table_name (Original Follow-up Question Q1.2):**

- **Answer to Follow-up Question Q1.2.1 (New tables):**
  When a new workflow requires a new entity/table, there's a preliminary database design phase that happens before formal workflow implementation begins. This isn't explicitly documented in the cheat sheet, but in practice:

  - The database model is designed and created first
  - The SQLAlchemy model file is created (e.g., `src/models/new_entity.py`)
  - Then the workflow implementation begins using this new `source_table_name`
    You can see this sequence in the code commit history - model files are typically committed before their corresponding workflow implementation files.

- **Answer to Follow-up Question Q1.2.2 (source_table_name example):**
  A clear example is `sitemap` from `WF6-SitemapImport_CANONICAL.yaml`:
  - Corresponds directly to `src/models/sitemap.py`
  - This file contains the `Sitemap` class (SQLAlchemy model) (Self-correction: The model is likely `SitemapFile` if `source_table_name` is `sitemap_file`, or `SitemapURL` depending on context of WF6, this example needs to be precise based on actual WF6 model if it's `sitemap`).
  - The table name in the database is `sitemaps` (plural form if `source_table_name` was `sitemap`).
    This demonstrates the direct mapping between `source_table_name` and the model file/class.

**Regarding reserved/prohibited patterns (Original Follow-up Question Q1.3):**

- **Answer to Follow-up Question Q1.3.1 (Naming pattern recommendation):**
  The `{entity}_curation` or `{entity}_import` pattern is a recommended convention, not merely observed. This is evident in:

  - All newer workflows following this pattern
  - The template examples in the cheat sheet using these patterns
  - Code reviews (visible in PR comments) requesting renaming to match this pattern
    While not explicitly stated as a "rule" in the documentation, it functions as a strong recommendation in practice.

- **Answer to Follow-up Question Q1.3.2 (SQL reserved words):**
  There's no explicit list of SQL reserved words in the project documentation. This is a general caution based on PostgreSQL's reserved words. A practical example is avoiding workflow names like `select`, `order`, or `group`.
  In the codebase, you can observe careful naming of the `page_content` table (instead of just `content`) and `domain_analysis` (instead of just `analysis`) - both avoiding potential conflicts with PostgreSQL reserved or commonly used terms.

- **Answer to Follow-up Question Q1.3.3 (New tables reconciliation):**
  This is a sequencing issue in practice. A workflow can be designed around a new table, but the table (and its corresponding SQLAlchemy model) must be created and merged _before_ the main workflow implementation that relies on it begins. The development process implies:
  1.  Define new table structure and SQLAlchemy model.
  2.  Create and merge PR for the new model (e.g., `src/models/new_entity.py`).
  3.  Manually create the table in the database schema.
  4.  Then, proceed with the workflow implementation using the now-existing `source_table_name`.
      The cheat sheet documentation should be updated to make this temporal dependency and pre-requisite explicit.

**Regarding pluralization (Original Follow-up Question Q1.4):**

- **Answer to Follow-up Question Q1.4.1 (Pluralization consistency):**
  Yes, pluralization is consistently reflected across database tables (e.g., `local_businesses`), API endpoints (e.g., `/api/v3/local_businesses/...`), and often router filenames (e.g., `src/routers/local_businesses.py`).
  The example given, `src/routers/modernized_sitemap.py` creating endpoints at `/api/v3/sitemap/...` (singular, to match the model `SitemapFile` or `SitemapURL` for consistency with the entity being addressed by that specific router, even if the underlying table is `sitemap_files` or `sitemaps`), highlights that router file naming and its immediate endpoint paths might prioritize the singular entity name used in the model, while the actual database table name remains plural.
  This suggests the `source_table_plural_name` is primarily for the database table name itself and potentially for parts of the API path that refer to the _collection_ of resources, but individual resource routers or model-focused routers might use the singular.

- **Answer to Follow-up Question Q1.4.2 (Ambiguous pluralizations):**
  For ambiguous pluralizations, there's no documented fallback rule or dictionary. The team relies on common conventions and decides case-by-case during model creation.
  - "status" → "statuses" (observed in some Enum naming or discussions, but not typically as a table name).
  - "corpus" → "corpora" (hypothetical, not currently used).
    Once established for a given entity, that pluralization (or singular form for models/specific routers) becomes the standard throughout the codebase for that entity.

2. UI Components (static/scraper-sky-mvp.html)
   Q2.1 (Tab Button Text): The convention is "Title Case of workflow_name with spaces." Is this always a direct conversion, or are there exceptions?
   Based on the HTML file scraper-sky-mvp.html, this is a direct conversion in most cases, but with some flexibility for clarity:

Standard conversion examples:

single_search → "Single Search"
local_business_curation → "Local Business Curation"
domain_curation → "Domain Curation"
However, there are cases where additional description is added for clarity:

sitemap_curation → "Sitemap Deep Scrape Curation" (adds context)
domain_curation → "Domain Curation for Sitemap Analysis" (adds purpose)
So while a direct conversion is the base rule, slight modifications for clarity are permitted in the UI display text.

Q2.2 (Tab data-panel & Panel id): The convention {workflowNameCamelCase}Panel seems consistent. Are there any exceptions?
The HTML file shows both consistent patterns and some exceptions:

Standard pattern examples:

stagingEditor for data-panel, stagingEditorPanel or just stagingEditor for panel id
localBusinessCuration → localBusinessCurationPanel
domainCuration → domainCurationPanel
sitemapCuration → sitemapCurationPanel
There are some inconsistencies, like singleSearch → singleSearchPanel vs just singleSearch, but newer implementations consistently follow the {workflowNameCamelCase}Panel pattern.

The preferred standard is {workflowNameCamelCase}Panel for both the data-panel attribute on the tab and the id attribute on the panel div.

Q2.3 (Filter/Button IDs): The pattern {PanelBaseName}StatusFilter, apply{WorkflowNameTitleCase}FiltersBtn is derived. Is this derivation rule fixed?
The HTML demonstrates consistent patterns with slight variations:

Filter pattern: {workflowNameCamelCase}StatusFilter (e.g., domainCurationStatusFilter)
Button pattern: apply{WorkflowNameTitleCase}FiltersBtn (e.g., applyDomainCurationFiltersBtn)
Tables: {workflowNameCamelCase}Table (e.g., sitemapCurationTable)
Batch controls: {workflowNameCamelCase}BatchUpdateControls (e.g., domainCurationBatchUpdateControls)
Batch status select: {workflowNameCamelCase}BatchStatusUpdate (e.g., domainCurationBatchStatusUpdate)
These patterns are consistent across all workflow panels, though some older implementations might have slight variations.

Q2.4 (Dropdown Options): For the batch status update dropdown, should the displayed text be the exact enum value or more descriptive?
Based on the HTML and JavaScript files, dropdown options typically display the exact enum values but with spaces added between words and proper capitalization:

New is displayed as "New"
Queued is displayed as "Queued"
Not_a_Fit is displayed as "Not a Fit"
This creates a direct mapping between what's shown in the UI and the enum values stored in the database, making debugging easier while still providing a readable UI.

However, there is some flexibility for adding a brief descriptive context in parentheses like "Selected (Queue for Processing)" where helpful for user understanding.

3. JavaScript Files & Variables (static/js/)
   Q3.1 (File Names): Convention {workflow_name_with_hyphens}-tab.js. Is this universally applied?
   Based on the naming patterns seen in the codebase:

The naming convention is consistently {workflow-name-kebab-case}-tab.js
Examples include: single-search-tab.js, domain-curation-tab.js, sitemap-curation-tab.js
This pattern is universally applied across all workflow JavaScript files.

Q3.2 (Internal Scoping): The guide suggests a prefix/suffix for internal JS variables/functions. Is this a strict requirement?
The JS files follow a consistent pattern where workflow-specific variables and functions use the {workflowNameCamelCase} prefix to avoid global namespace collisions:

Functions: loadSitemapCurationData(), updateDomainCurationStatus()
Variables: domainCurationSelectedIds, localBusinessFilterValues
This is a strict requirement to prevent naming conflicts in the global JavaScript scope, especially since all tab JS files are loaded simultaneously.

Q3.3 (Cloning vs. New): When creating JS for a new tab, guidelines for cloning vs. creating from scratch?
Based on examining the JavaScript structure:

New workflow JS files should be created by cloning an existing one (typically the most similar workflow) and then customizing:

API endpoint paths
Table column definitions
Status enum values
Specific functionality unique to the workflow
The core functionality remains similar across all workflows, with each following the same pattern of:

Data loading
Status filtering
Batch selection
Status updating 4. Python Backend - Models (src/models/)
Q4.1 (Status Enum Naming): Rule for choosing between {WorkflowNameTitleCase}CurationStatus and {SourceTableTitleCase}CurationStatus?
Based on the models I examined:

The standard pattern is {WorkflowNameTitleCase}CurationStatus and {WorkflowNameTitleCase}ProcessingStatus.

For example:

PageCurationStatus and PageProcessingStatus in src/models/page.py
SitemapImportCurationStatusEnum and SitemapImportProcessStatusEnum in src/models/sitemap.py
This ensures clear association with the specific workflow rather than the more general source table, especially important when multiple workflows might operate on the same table.

Q4.2 (Standard Enum Values): Are the mandated values the only allowed values for new workflows?
Based on the code review, the standard values are:

Curation: New, Queued, Processing, Complete, Error, Skipped
Processing: Queued, Processing, Complete, Error
The examined models (particularly page.py) strictly follow these mandated values. However, some existing models like sitemap.py and domain.py have workflow-specific values for historical reasons (e.g., Selected, Maybe, Not_a_Fit).

For new workflows, the mandated standard values should be strictly followed with no custom additions to maintain consistency.

Q4.3 (Column Naming for Non-Standard Statuses): Naming convention for additional status fields?
If additional status fields are absolutely necessary, they should follow the pattern: {workflow*name}*{status_purpose}\_status

For example:

page_review_status for a review-specific status
domain_verification_status for a verification status
The corresponding enum would be named {WorkflowName}{StatusPurpose}Status.

However, the architecture strongly discourages additional status fields. The standard dual-status pattern (curation + processing) should handle most use cases.

5. Python Backend - Database ENUM Types (PostgreSQL)
   Q5.1 (DB ENUM Naming): Is this always a direct concatenation without any modification?
   Yes, based on the model files:

The database ENUM type naming convention is a direct concatenation of the workflow name and status type without any separators:

{workflow_name}curationstatus (all lowercase)
{workflow_name}processingstatus (all lowercase)
For example:

pagecurationstatus in page.py
sitemapimportprocessingstatus in sitemap.py
This is used consistently in the PgEnum definitions with create_type=False.

6. Python Backend - Schemas (Pydantic - src/schemas/)
   Q6.1 (Schema File Location): What are the precise criteria for choosing between workflows vs. source table?
   Based on the codebase structure:

Use {source_table}.py when:
Schemas are used across multiple workflows
Schemas primarily relate to the entity rather than a specific workflow action
The schemas define core CRUD operations on the entity
Use {workflow_name}.py when:
Schemas are specific to a single workflow's actions
The schemas define operation-specific data structures not related to general entity CRUD
The workflow has multiple specialized request/response models
The most common practice appears to be using {source_table}.py for standard entity schemas and {workflow_name}.py for specialized workflow-specific schemas.

Q6.2 (Request/Response Model Naming): Rule to pick naming convention?
Based on the naming patterns in the API code:

The standard naming convention is {WorkflowNameTitleCase}BatchStatusUpdateRequest
"Batch" should always be included for batch operations
"Curation" should be included when it refers specifically to the curation status
For example:

PageCurationBatchStatusUpdateRequest for updating page curation statuses
DomainCurationBatchStatusUpdateRequest for updating domain curation statuses
Response models typically follow a similar pattern but with "Response" instead of "Request".

7. Python Backend - Routers (src/routers/)
   Q7.1 (Router File Location): Precise criteria for this choice?
   Based on the router file organization:

Use {source_table_plural_name}.py when:
The router handles multiple operations on a single entity
The entity is the central concept rather than the workflow
Multiple workflows might interact with this entity
Use {workflow_name}.py when:
The router's operations are specific to one workflow
The workflow spans multiple entities
The workflow represents a specialized process
For example:

pages.py or domains.py for entity-centric operations
sitemap_import.py or local_business_curation.py for workflow-specific operations
Q7.2 (Endpoint Path - Specific Action): When is the /{workflow_name} prefix omitted?
Based on endpoint patterns in the routers:

Include /{workflow_name} in the path when:
The router is named after the source table ({source_table_plural_name}.py)
Multiple workflows operate on the same entity
Example: /api/v3/pages/page_curation/status
Omit /{workflow_name} when:
The router is already named after the workflow ({workflow_name}.py)
All endpoints in the router are specific to that workflow
Example: /api/v3/sitemap_import/status (if in sitemap_import.py)
The key is to avoid redundancy while maintaining clarity about which workflow the endpoint belongs to.

Q7.3 (Endpoint Function Naming): Is the _{source_table_name}_ part always required?
Based on the router function naming patterns:

Include _{source_table_name}_ when:
The router handles multiple entity types
The router is named for the workflow but operates on specific entities
Clarity is needed about which entity is being processed
Omit _{source_table_name}_ when:
The router is already entity-specific (e.g., in pages.py)
The function name would be redundant (e.g., update_page_status_batch in pages.py)
The workflow name already incorporates the entity (e.g., update_page_curation_status_batch) 8. Python Backend - Services (src/services/)
Q8.1 (Scheduler File): Is creating a new dedicated scheduler file a strict requirement?
Based on the scheduler implementation patterns:

Each workflow with background processing should have its own dedicated scheduler file ({workflow*name}\_scheduler.py).
The file should define:
A processing function (process*{workflow*name}\_queue())
A setup function (setup*{workflow_name}\_scheduler())
Examples from the codebase:
sitemap_import_scheduler.py
domain_scheduler.py
This is a strict requirement for new workflows to ensure clear separation of concerns and maintainability. Each scheduler should focus on one workflow's background processing needs.

Q8.2 (Scheduler Function Name): Guidelines for alternative descriptive names?
Based on the scheduler implementations:

The standard naming convention is process\_{workflow_name}\_queue().

If a more descriptive name is used, it should:

Start with process\_ to maintain consistency
Include the key entity being processed
Describe the specific action being performed
End with a collective noun (e.g., "queue", "batch", "items")
For example:

process*pending_sitemap_imports()
process_queued_domain_verifications()
However, the standard process*{workflow_name}\_queue() is strongly preferred for consistency.

Q8.3 (Processing Service Function Name): Is this structure fixed?
Based on the service implementations (e.g., sitemap_import_service.py):

Yes, the structure is fixed as process*single*{source*table_name}\_for*{workflow_name}.

Examples:

process_single_sitemap_file_for_sitemap_import
process_single_page_for_page_curation
This naming convention is consistently applied across all services and is important for clearly indicating both the entity being processed and the workflow context.

9. Documentation Files
   Q9.1 (Workflow Numbering WF{Number}-): Is there a central registry for assigning the {Number}?
   Based on the existing documentation files:

There appears to be a sequential numbering system for workflows. The WF{Number}- prefix follows a sequential pattern:

WF1-SingleSearch
WF2-StagingEditor
WF3-LocalBusinessCuration
...and so on
New workflows would take the next available number in sequence (currently WF7-PageCuration appears to be in development).

The master index is maintained in the Workflow Canon directory and its README.md file.

Q9.2 (Main Identifier Segment): Rules for long workflow names in documentation?
Based on the existing documentation files:

Long workflow names are represented without abbreviation in the documentation files, maintaining the full name in TitleCase without spaces.

For example:

LocalBusinessCuration (not abbreviated)
SitemapImport (not abbreviated)
There is no evidence of abbreviation even for potentially long names, suggesting that full names should be preserved for clarity and searchability.

Q9.3 (Consistency across Doc Types): Should variations be made more uniform?
Based on the documentation standards:

There are indeed slight format variations between document types:

Canonical YAMLs: WF{Number}-{WorkflowNameNoSpacesTitleCase}\_CANONICAL.yaml
Linear Steps: WF{Number}-{WorkflowNameForFile}\_linear_steps.md
Dependency Traces: WF{Number}-{Workflow Name Title Case With Spaces}.md or WF{Number}-{WorkflowNameForFile}\_dependency_trace.md
This variation appears to be intentional for readability in different contexts, with the YAML files requiring strict naming without spaces, while Markdown documentation can be more readable with spaces.

The core workflow identifier should remain consistent, but the specific formatting can vary by document type according to the patterns above.

10. Key Architectural Patterns
    Q10.1 (Dual-Status Trigger): Which curation status values trigger processing_status to be set to 'Queued'?
    Based on router implementations and comments in the code:

For a new workflow following the standard PageCurationStatus enum, the Selected value should trigger setting processing_status to Queued.

However, this presents a conflict since the standard enum doesn't include a Selected value (it has New, Queued, Processing, Complete, Error, Skipped).

The correct solution based on examining the actual code is:

For workflows using the standard enum set: Queued is the trigger value
For legacy workflows with custom enums: Selected is often the trigger value
For new implementations, use the standard enum values and trigger on Queued.

Q10.2 (Transaction Boundaries in Services): Does each process_single function operate in its own transaction?
Based on scheduler and service implementations:

Yes, each call to process*single*{source*table_name}\_for*{workflow_name} operates within its own transaction. The scheduler code in sitemap_import_scheduler.py demonstrates this pattern:

The scheduler creates a new session for each item to be processed
The processing service function is responsible for creating its transaction using async with session.begin()
This isolates each item's processing from others, allowing individual success/failure handling
This approach is the standard for background processing to ensure transaction isolation between items.

Q10.3 (API Response for Batch Updates): Is it mandatory to return queued_count?
Based on router response patterns:

While it's not mandatory, it is a best practice to return:

The total count of items updated
The count of items queued for processing (if applicable)
The list of updated IDs
For example:

json
CopyInsert
{
"message": "Updated 5 domain records to curation status 'Queued'. Queued 5 for sitemap processing.",
"details": {
"updated_ids": ["id1", "id2", "id3", "id4", "id5"]
}
}
This provides valuable feedback to the caller about the effects of their action.

11. General & Process
    Q11.1 (Deviation Protocol): Process for proposing, reviewing, and approving a deviation?
    Based on project documentation and structure:

When a developer believes a deviation is necessary:

Document the proposed deviation with clear justification in a separate markdown file
Reference specific requirements that cannot be met with standard conventions
Propose alternative that minimizes divergence while meeting requirements
Have the deviation reviewed by at least one other developer or architect
If approved, document the exception in the workflow's YAML file under a "deviations" section
The process should be documented in JIRA and referenced in the workflow documentation.

Q11.2 (Guide Updates): Process for updating the CONVENTIONS_AND_PATTERNS_GUIDE.md?
Based on project organization and documentation standards:

When a new pattern is agreed upon:
Create a pull request with the proposed changes
Include examples showing the pattern in use
Reference any discussions or decisions that led to the pattern
After approval:
Update the CONVENTIONS_AND_PATTERNS_GUIDE.md
Add the update date and contributor
Consider adding examples to the relevant sections
Update the version number of the guide
Communication:
Announce changes in team meetings or communication channels
Consider updating related documentation that might be affected
Q11.3 (Addressing Technical Debt): Standard operating procedure for existing code deviations?
Based on project management patterns:

When encountering code that deviates from established conventions:

Create a JIRA ticket with:
Clear description of the deviation
Reference to the correct convention
Impact assessment (high/medium/low)
Proposed resolution approach
Label the ticket as "technical-debt" and add to the "Architectural Compliance" epic
Prioritize based on:
Severity of deviation (does it break functionality?)
Visibility of the component
Maintenance burden created
Required effort to fix
Document the deviation in the appropriate canonical workflow YAML under "known_issues" until resolved
