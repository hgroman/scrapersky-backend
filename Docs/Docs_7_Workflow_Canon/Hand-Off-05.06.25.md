# ScraperSky Workflow Standardization Project: Handoff Document

## Project Overview

We've been standardizing the ScraperSky workflow documentation to ensure consistent implementation across all current and future workflows. This project focuses on:

1. Accurately documenting enum locations and values
2. Establishing consistent patterns for workflow implementation
3. Creating practical cheat sheets for developers
4. Eliminating ambiguity in the documentation

## Current State

### Core Workflow Pattern

Every ScraperSky workflow follows this critical dual-status update pattern:

1. **UI Layer**: User selects "Selected" from a dropdown for `{workflow_name}_curation_status`
2. **API Layer**:
   - Updates `{workflow_name}_curation_status = "Selected"`
   - ALSO sets `{workflow_name}_processing_status = "Queued"`
3. **Background Service**: Processes records where `{workflow_name}_processing_status = "Queued"`

This producer-consumer pattern is fundamental to all workflows and must be implemented consistently.

### Key Documentation Files

1. **SUPER SHORT**: Minimal, practical implementation guide
   - Path: `/Docs/Docs_7_Workflow_Canon/ScraperSky Workflow Builder Cheat Sheet SUPER SHORT.md`
   - Purpose: Quick reference for experienced developers

2. **TEMPLATE**: Comprehensive guide with placeholders
   - Path: `/Docs/Docs_7_Workflow_Canon/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE.md`
   - Purpose: Starting point for new workflow implementation

3. **OVER-ENGINEERED**: Detailed guide with rationale
   - Path: `/Docs/Docs_7_Workflow_Canon/ScraperSky Workflow Builder Cheat Sheet OVER-ENGINEERED.md`
   - Purpose: Educational resource and deep reference

4. **Workflow Comparison**: Reference document mapping all workflows
   - Path: `/Docs/Docs_7_Workflow_Canon/workflow-comparison-detailed.md`
   - Purpose: Shows complete data flow across interrelated workflows

5. **Page Curation Workflow**: Specific workflow implementation example
   - Path: `/Docs/Docs_5_Project_Working_Docs/47-Page-Curation-Workflow-Creation/47.0-Workflow-Builder-Cheat-Sheet.md`
   - Purpose: Real-world implementation guide for WF7

### Standardized Enum Values

For consistency across all workflows, we've standardized on exact enum values:

#### Curation Status Enums
These include `New`, `Selected`, `Maybe`, `Not a Fit`, `Archived`

#### Processing Status Enums
These include `Queued`, `Processing`, `Complete`, `Error`

### Database Schema Implementation

1. **Manual SQL Execution**: ALL database changes are done via MANUAL SQL (NOT Alembic)
2. **Enum Type Creation**: Create enum types in PostgreSQL before creating columns
3. **Verification Queries**: Added SQL queries to verify successful creation
4. **Index Creation**: Created appropriate indexes for performance

## Important Implementation Details

### Domain-Based Enum Placement

Enums should reside in the same module as their related models. This domain-based placement strategy ensures:

1. Logical organization of code
2. Easier maintenance and updates
3. Clearer import paths

### Dual-Status Update Pattern Implementation

The critical dual-status update pattern is implemented in API endpoints using this code pattern:

```python
# Determine if queueing for background processing is needed
should_queue_processing = (target_curation_status == {WorkflowName}CurationStatus.Selected)

# Base update values
update_values = {
    "{workflow_name}_curation_status": target_curation_status
}

# Apply Dual-Status Update Logic
if should_queue_processing:
    update_values["{workflow_name}_processing_status"] = {WorkflowName}ProcessingStatus.Queued
    update_values["{workflow_name}_processing_error"] = None  # Clear previous errors
```

This pattern ensures that when a user selects "Selected" for curation status, the system automatically queues the record for processing.

### SQL Implementation Pattern

For creating enum types and adding columns:

```sql
-- Create enum type if not exists
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{workflow_name}curationstatus') THEN
        CREATE TYPE {workflow_name}curationstatus AS ENUM ('New', 'Selected', 'Maybe', 'Not a Fit', 'Archived');
    END IF;
END $$;

-- Create processing status enum if not exists
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{workflow_name}processingstatus') THEN
        CREATE TYPE {workflow_name}processingstatus AS ENUM ('Queued', 'Processing', 'Complete', 'Error');
    END IF;
END $$;

-- Add columns to table
ALTER TABLE {source_table}
    ADD COLUMN IF NOT EXISTS {workflow_name}_curation_status {workflow_name}curationstatus DEFAULT 'New',
    ADD COLUMN IF NOT EXISTS {workflow_name}_processing_status {workflow_name}processingstatus DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS {workflow_name}_processing_error TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS {workflow_name}_processing_at TIMESTAMPTZ DEFAULT NULL;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_{source_table}_{workflow_name}_curation_status ON {source_table} ({workflow_name}_curation_status);
CREATE INDEX IF NOT EXISTS idx_{source_table}_{workflow_name}_processing_status ON {source_table} ({workflow_name}_processing_status);
```

## Enum Mapping Across Workflows

For reference, here is the complete mapping of enum locations across all workflows:

| Workflow | Source Table | Status Enums | Location |
|----------|--------------|-------------|----------|
| WF1: Single Search → Place Create | `place_searches` | PlaceStatusEnum | src/models/place.py |
| WF2: Staging → Deep Scan | `places` | PlaceStagingStatusEnum (API)<br>GcpApiDeepScanStatusEnum (Processing) | src/models/api_models.py<br>src/models/place.py |
| WF3: Local Biz → Domain Extract | `local_businesses` | LocalBusinessApiStatusEnum (API)<br>DomainExtractionStatusEnum (Processing) | src/models/api_models.py<br>src/models/local_business.py |
| WF4: Domain → Sitemap Analysis | `domains` | SitemapCurationStatusEnum (Curation)<br>SitemapAnalysisStatusEnum (Processing) | src/models/domain.py<br>src/models/domain.py |
| WF5: Sitemap File → Import Queue | `sitemap_files` | SitemapFileStatusEnum<br>SitemapImportCurationStatusEnum<br>SitemapCurationStatusApiEnum (API) | src/models/sitemap.py<br>src/models/sitemap.py<br>src/models/api_models.py |
| WF6: Sitemap Import → Page Create | `sitemap_files` | SitemapImportProcessStatusEnum | src/models/sitemap.py |
| WF7: Page Curation → Processing | `pages` | PageCurationStatus<br>PageProcessingStatus | src/models/page.py |

## Challenges Encountered

1. **Inconsistent Legacy Naming**: Some older workflows use different naming patterns and status values. We've documented these but maintained them for compatibility.

2. **Multiple Possible Enum Locations**: Some enums are defined in multiple places (api_models.py vs. domain-specific files). We've standardized on domain-based placement going forward.

3. **Tools Limitations**: The `replace_file_content` tool has token limitations, requiring large documents to be updated in smaller chunks.

4. **Mixed Workflow Patterns**: Some workflows (like WF1) use internal tasks rather than separate schedulers, and others have shared schedulers.

## Next Steps

1. **Update the OVER-ENGINEERED version** with the index creation statements and verification queries that we've added to other documents.

2. **Create comprehensive examples** for each workflow pattern (create new records vs. update status).

3. **Verify the correct import path** for the SQLAlchemy `AsyncSession` dependency injection in all documentation.

4. **Ensure UI documentation** accurately reflects the dropdown values and their effects.

5. **Consider adding a dedicated section** on the dual-status update pattern to ALL documentation files for maximum clarity.

## Key Principles Reinforced

1. **Domain-Based Organization**: Enums belong with their related models
2. **Consistent Naming**: Follow established patterns for all new workflows
3. **Manual SQL Execution**: Use SQL scripts, not Alembic, for database changes
4. **Dual-Status Update Pattern**: Critical for proper workflow functioning
5. **Verification**: Always include verification steps in documentation

## Notes on Implementation Process

When implementing a new workflow:

1. Start with the TEMPLATE cheat sheet
2. Complete the placeholders with your specific workflow details
3. Follow the SQL implementation exactly, testing with verification queries
4. Implement the Python enums in the correct domain-based location
5. Create the API endpoint with the dual-status update pattern
6. Setup the background scheduler to process records
7. Test the full flow end-to-end

This pattern ensures consistent, reliable workflow implementation across the codebase.
