# [ARCHIVED] WF8 Contacts Technical Research Report

---
**ARCHIVAL NOTE:** This document is for historical context only. The research and findings herein have been superseded by the corrected and verified `WORK ORDER- WF8 Contacts CRUD Endpoint Implementation.md`. Do not use this document as a source of truth for implementation.
---

**Date:** 2025-09-13

## Database Analysis

### Contacts Table Schema
**Source:** Supabase query `SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'contacts'`

| Field | Type | Nullable | Default |
|-------|------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| domain_id | uuid | NO | null |
| page_id | uuid | NO | null |
| email | text | NO | null |
| email_type | USER-DEFINED | YES | null |
| has_gmail | boolean | YES | false |
| context | text | YES | null |
| source_url | text | YES | null |
| source_job_id | uuid | YES | null |
| created_at | timestamp with time zone | NO | now() |
| updated_at | timestamp with time zone | NO | now() |
| contact_curation_status | USER-DEFINED | NO | 'New'::contact_curation_status |
| contact_processing_status | USER-DEFINED | YES | null |
| contact_processing_error | text | YES | null |
| hubspot_sync_status | USER-DEFINED | NO | 'New'::hubspot_sync_status |
| hubspot_processing_status | USER-DEFINED | YES | null |
| hubspot_processing_error | text | YES | null |
| name | character varying | YES | null |
| phone_number | character varying | YES | null |

### Enum Values
**Source:** Supabase queries on pg_enum table

**contact_curation_status enum:**
- New
- Queued
- Processing
- Complete
- Error
- Skipped

**contact_processing_status enum:**
- Queued
- Processing
- Complete
- Error

**hubspot_sync_status enum:**
- New
- Queued
- Processing
- Complete
- Error
- Skipped

**email_type enum:**
- (No values returned from query)

## Code Analysis

### WF4 domains.py Router Structure
**Source:** File `/src/routers/domains.py` lines 40-44

```python
router = APIRouter(
    prefix="/api/v3/domains",
    tags=["Domains"],
    # dependencies=[Depends(get_current_user)], # Apply auth to all routes if needed
)
```

### WF4 Imports
**Source:** File `/src/routers/domains.py` lines 12-36

```python
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.auth.jwt_auth import get_current_user
from src.db.session import get_db_session
from src.models.api_models import (
    DomainBatchCurationStatusUpdateRequest,
    DomainFilteredUpdateRequest,
    DomainBatchUpdateResponse,
    DomainRecord,
    PaginatedDomainResponse,
)
from src.models.domain import (
    Domain,
    SitemapAnalysisStatusEnum,
    SitemapCurationStatusEnum,
)
```

### WF4 Sort Fields Pattern
**Source:** File `/src/routers/domains.py` lines 48-55

```python
ALLOWED_SORT_FIELDS = {
    "domain": Domain.domain,
    "created_at": Domain.created_at,
    "updated_at": Domain.updated_at,
    "sitemap_curation_status": Domain.sitemap_curation_status,
    "sitemap_analysis_status": Domain.sitemap_analysis_status,
    "status": Domain.status,
}
```

### WF4 GET Endpoint Structure
**Source:** File `/src/routers/domains.py` lines 58-77

```python
@router.get("", response_model=PaginatedDomainResponse)
async def list_domains(
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    sort_by: Optional[str] = Query("updated_at", description=f"Field to sort by..."),
    sort_desc: bool = Query(True, description="Sort in descending order"),
    sitemap_curation_status: Optional[SitemapCurationStatusEnum] = Query(None, description="Filter by sitemap curation status"),
    domain_filter: Optional[str] = Query(None, description="Filter by domain name..."),
):
```

### WF4 Filter Building Pattern
**Source:** File `/src/routers/domains.py` lines 113-125

```python
filters = []
if sitemap_curation_status:
    filters.append(Domain.sitemap_curation_status == sitemap_curation_status)
if domain_filter:
    filters.append(Domain.domain.ilike(f"%{domain_filter}%"))

# Apply filters
if filters:
    base_query = base_query.where(*filters)
```

### WF5 sitemap_files.py Additional Patterns
**Source:** File `/src/routers/sitemap_files.py` lines 54-84

```python
@router.get("/", response_model=PaginatedSitemapFileResponse)
async def list_sitemap_files(
    domain_id: Optional[uuid.UUID] = Query(None, description="Filter by domain UUID"),
    deep_scrape_curation_status: Optional[SitemapImportCurationStatusEnum] = Query(None),
    url_contains: Optional[str] = Query(None, description="Filter by text contained in the sitemap URL"),
    sitemap_type: Optional[str] = Query(None, description="Filter by sitemap type"),
    discovery_method: Optional[str] = Query(None, description="Filter by discovery method"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(15, ge=1, le=200, description="Items per page"),
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
```

### WF5 Service Pattern
**Source:** File `/src/routers/sitemap_files.py` lines 47, 88-97

```python
sitemap_files_service = SitemapFilesService()

paginated_response = await sitemap_files_service.get_all(
    session=session,
    page=page,
    size=size,
    domain_id=domain_id,
    deep_scrape_curation_status=deep_scrape_curation_status,
    url_contains=url_contains,
    sitemap_type=sitemap_type,
    discovery_method=discovery_method,
)
```

### WF5 CRUD Operations
**Source:** File `/src/routers/sitemap_files.py` endpoints

- GET `/` (list with pagination/filtering)
- GET `/{sitemap_file_id}` (single record)
- POST `/` (create)
- PUT `/{sitemap_file_id}` (update)
- DELETE `/{sitemap_file_id}` (delete)
- PUT `/sitemap_import_curation/status` (batch status update)
- PUT `/sitemap_import_curation/status/filtered` (filtered status update)

## Required Adaptations for Contacts

### Enum Definitions Needed
**Based on:** Database enum queries above

```python
class ContactCurationStatusEnum(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"

class ContactProcessingStatusEnum(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"

class HubSpotSyncStatusEnum(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"
```

### Router Prefix Change Required
**Based on:** WF4/WF5 patterns and API v3 requirement

```python
router = APIRouter(
    prefix="/api/v3/contacts",  # Changed from /api/v3/domains
    tags=["Contacts"],          # Changed from ["Domains"]
    responses={404: {"description": "Not found"}},
)
```

### Model Import Changes Required
**Based on:** WF4 import pattern analysis

```python
# WF4 imports Domain-specific models:
from src.models.domain import Domain, SitemapAnalysisStatusEnum, SitemapCurationStatusEnum

# Contacts would need:
from src.models.contact import Contact  # Does not exist yet
from src.models.enums import ContactCurationStatusEnum, ContactProcessingStatusEnum, HubSpotSyncStatusEnum  # Do not exist yet
```

### Filter Parameters for Contacts
**Based on:** Contacts table schema and WF4/WF5 filter patterns

```python
# Applicable filters from schema:
domain_id: Optional[uuid.UUID] = Query(None)
page_id: Optional[uuid.UUID] = Query(None)
contact_curation_status: Optional[ContactCurationStatusEnum] = Query(None)
contact_processing_status: Optional[ContactProcessingStatusEnum] = Query(None)
hubspot_sync_status: Optional[HubSpotSyncStatusEnum] = Query(None)
email_contains: Optional[str] = Query(None)
name_contains: Optional[str] = Query(None)
has_gmail: Optional[bool] = Query(None)
source_url_contains: Optional[str] = Query(None)
```

## Files That Need Creation

### Required New Files
**Based on:** WF4/WF5 pattern analysis and missing Contact model

1. Contact model file (Contact model does not exist in codebase)
2. Contact enum definitions (ContactCurationStatusEnum, etc. do not exist)
3. Contact schema definitions for API models
4. Contacts router file

### Files That Exist and Work
**Based on:** WF4/WF5 successful implementations

- Authentication: `src/auth/jwt_auth.py`
- Database session: `src/db/session.py`
- Base FastAPI patterns
- Pagination logic
- Filter building patterns
