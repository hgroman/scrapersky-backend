# Producer-Consumer Workflow Pattern

_Created: 2025-05-05T08:50:00-07:00_  
_Author: Cascade AI_  
_Status: AUTHORITATIVE_

## Overview

This document defines the authoritative pattern for implementing producer-consumer workflows in the ScraperSky backend. This pattern ensures consistent implementation of workflows that process data in stages, with each workflow consuming data from an upstream workflow and producing data for a downstream workflow.

## Pattern Definition

### 1. Core Components

Each producer-consumer workflow consists of the following components:

1. **Database Schema**:
   - Entity table (e.g., `places`, `sitemap_urls`, `page_contents`)
   - Status field with a corresponding Enum (e.g., `status`, `page_curation_status`)
   - Error message field (e.g., `error_message`, `page_scrape_error`)
   - Timestamp fields (e.g., `created_at`, `updated_at`, `page_curation_updated_at`)

2. **API Endpoints**:
   - Listing endpoint (`GET /api/v3/{entity}-curation/list`)
   - Batch status update endpoint (`PUT /api/v3/{entity}-curation/status`)

3. **Background Services**:
   - Scheduler that polls for records with status='Queued'
   - Processing service that handles the actual business logic

4. **UI Components**:
   - Tab in the main interface
   - Data table with selection and batch action controls
   - Status filtering and pagination

### 2. Database Pattern

```python
# Entity Status Enum
class EntityCurationStatusEnum(str, Enum):
    New = "new"             # Initial state
    Selected = "selected"   # Manually selected for processing
    Queued = "queued"       # Queued for background processing
    Processing = "processing" # Currently being processed
    Complete = "complete"   # Successfully processed
    Error = "error"         # Error during processing
    Skipped = "skipped"     # Manually skipped/ignored

# Entity Table
class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    # ... entity-specific fields ...
    entity_curation_status = Column(String, default=EntityCurationStatusEnum.New)
    entity_curation_updated_at = Column(DateTime)
    entity_processing_error = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

### 3. API Endpoint Pattern

```python
# Router Definition
router = APIRouter(
    tags=["Entity Curation"],
    responses={404: {"description": "Not found"}},
)

# Listing Endpoint
@router.get(
    "/entity-curation/list",
    response_model=PaginatedEntityCurationResponse,
    summary="List All Entity Curation Items (Paginated)",
)
async def list_all_entity_curation_items(
    status_filter: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PaginatedEntityCurationResponse:
    # Implementation details...
```

### 4. Status Update Pattern

```python
# Status Update Endpoint
@router.put(
    "/entity-curation/status",
    status_code=status.HTTP_200_OK,
)
async def update_entity_curation_status_batch(
    request_body: EntityCurationBatchStatusUpdateRequest = Body(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    # Implementation with transaction management
    async with session.begin():
        # Fetch entities
        # Update status
        # Handle dual-update pattern for triggering background processing
```

### 5. Background Processing Pattern

```python
# Scheduler Function
async def process_pending_entity_processes(limit: int = 10):
    """Process pending entity processes fetched from the database."""
    async with get_background_session() as session:
        # Query for entities with status=Queued
        # Process each entity
        # Update status to Complete or Error
```

### 6. Producer-Consumer Connection Pattern

## ⚠️ MANDATORY DATABASE TABLE SPECIFICATION ⚠️

All workflow documentation MUST include explicit connection points to upstream and downstream workflows using the **workflow_connections** section in the canonical YAML file. This section MUST explicitly identify the exact database tables that serve as the communication medium between workflows. **NO EXCEPTIONS**.

**Critical Requirements:**
1. Every workflow connection must specify the exact database table name
2. Status fields and values must be explicitly documented
3. Connection details must describe the database operations involved
4. Table schemas must be referenced in model dependencies

```yaml
workflow_connections:
  as_consumer:
    - producer_workflow: WFX-ProducerWorkflow
      # Database table that this workflow consumes data from (MANDATORY)
      interface_table: producer_entities  # Explicit table name from database schema
      # Field that contains the status signal this workflow looks for
      handoff_field: entity_curation_status
      # Value that triggers consumption
      consumed_value: EntityCurationStatusEnum.New
      # Explicit database operation that reads from the producer table
      consumption_query: "SELECT * FROM producer_entities WHERE entity_curation_status = 'New'"
      
  as_producer:
    - consumer_workflow: WFZ-ConsumerWorkflow
      # Database table that this workflow writes to for the next workflow (MANDATORY)
      interface_table: consumer_entities  # Explicit table name from database schema
      # Field that contains the status signal for the next workflow
      handoff_field: status
      # Value that signals readiness for the next workflow
      produced_value: ConsumerEntityStatusEnum.New
      # Explicit database operation that updates the producer table
      production_operation: "UPDATE consumer_entities SET status = 'New' WHERE ..."
```

**IMPORTANT: Database tables must be explicitly identified in all workflow documentation.**

The database tables serve as the communication medium between workflows. Failing to explicitly specify table names creates ambiguity and maintenance challenges. Every workflow connection must clearly document exactly which database table it reads from (as consumer) and writes to (as producer).

## Implementation Workflow

For any new producer-consumer workflow, follow these steps:

1. **Define Database Schema**:
   - Add necessary ENUMs
   - Add status and timestamp fields to existing tables or create new tables
   - Add relationships between tables

2. **Implement API Endpoints**:
   - Create router file with listing and batch status update endpoints
   - Register router in main.py

3. **Implement Background Service**:
   - Create scheduler file with polling and processing functions
   - Create service file with business logic
   - Register scheduler in main.py

4. **Implement UI**:
   - Create JS file for the tab functionality
   - Update HTML to include the new tab
   - Implement data table with selection and actions

5. **Create Documentation**:
   - Create dependency trace document
   - Create linear steps document
   - Create canonical YAML
   - Update python_file_status_map.md

## Architectural Requirements

All producer-consumer workflows must adhere to the following architectural requirements:

1. **API Versioning**: All endpoints must use the `/api/v3/` prefix.
2. **ORM Usage**: All database operations must use SQLAlchemy ORM (no raw SQL).
3. **Transaction Management**: Routers must own transaction boundaries.
4. **JWT Authentication**: Authentication must happen at API gateway level only.
5. **Error Handling**: Implement proper error handling and status updates.
6. **Logging**: Include comprehensive logging throughout the workflow.
7. **Testing**: Provide comprehensive test coverage for all components.

## Example Workflows

The following workflows follow this pattern:

1. **WF1-SingleSearch**: Produces Place records consumed by WF2-StagingEditor
2. **WF2-StagingEditor**: Consumes Place records, produces LocalBusiness records
3. **WF5-SitemapCuration**: Produces DomainExtractions consumed by WF6-SitemapImport
4. **WF6-SitemapImport**: Consumes DomainExtractions, produces SitemapUrl records
5. **WF7-PageCuration**: Consumes SitemapUrl records, produces PageContent records
6. **WFX-ContactCuration**: (Future) Will consume PageContent records

## Related Documentation

- [WORKFLOW_AUDIT_JOURNAL.md](./WORKFLOW_AUDIT_JOURNAL.md) - Records of all workflow audits
- [ABSOLUTE_ORM_REQUIREMENT.md](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md) - ORM requirements
- [TRANSACTION_PATTERNS_REFERENCE.md](../Docs_1_AI_GUIDES/07-TRANSACTION_PATTERNS_REFERENCE.md) - Transaction patterns

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-05-05 | Cascade AI | Initial creation |

---

**Author**: Cascade AI  
**Creation Date**: 2025-05-05T08:50:00-07:00  
**Status**: AUTHORITATIVE
