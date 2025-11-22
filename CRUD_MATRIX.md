# ScraperSky CRUD Matrix - Gap Analysis & Standardization Plan

> **Purpose**: Map all table CRUD operations, identify gaps, and standardize features across all entities.

---

## Current State Matrix

| Feature | Domains (WF4) | Local Biz (WF3) | Places (WF1) | Sitemaps (WF5) | Pages (WF7) | Contacts (WF7) |
|---------|:-------------:|:---------------:|:------------:|:--------------:|:-----------:|:--------------:|
| **LIST (paginated)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **GET by ID** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **CREATE** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **UPDATE single** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **DELETE** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **BATCH status update** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **FILTERED update** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **SORTING** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Filter by status** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Filter by text/name** | ✅ domain | ✅ name | ❌ | ✅ url | ✅ url | ✅ |
| **Filter by parent** | N/A | ❌ | ✅ job_id | ✅ domain_id | ❌ domain_id | ❌ page_id |
| **ARCHIVE soft-delete** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Gap Summary

### High Priority (80/20)
1. **Sorting** - Missing on 4/6 tables (Places, Sitemaps, Pages, Contacts)
2. **Filter by parent entity** - Missing on Pages (by domain), Contacts (by page)
3. **Soft Delete/Archive** - Missing on ALL tables

### Medium Priority
4. **GET by ID** - Missing on 4/6 tables
5. **UPDATE single record** - Missing on 4/6 tables

### Lower Priority (workflow-specific)
6. **CREATE** - Only needed where manual record creation makes sense

---

## Standard CRUD Interface Specification

### Every entity SHOULD have these endpoints:

```
GET    /{entity}                    # List with pagination, sorting, filtering
GET    /{entity}/{id}               # Get single by ID
PUT    /{entity}/{id}               # Update single record
DELETE /{entity}/{id}               # Soft delete (archive) or hard delete
PUT    /{entity}/status             # Batch status update by ID list
PUT    /{entity}/status/filtered    # Batch status update by filter criteria
```

### Standard Query Parameters for LIST endpoints:

```python
# Pagination
page: int = Query(1, ge=1)
size: int = Query(50, ge=1, le=200)

# Sorting (NEW STANDARD)
sort_by: str = Query("updated_at", description="Field to sort by")
sort_order: str = Query("desc", enum=["asc", "desc"])

# Status filtering
status: Optional[StatusEnum] = Query(None)

# Text search
search: Optional[str] = Query(None, description="Search text fields")

# Parent entity filter (where applicable)
domain_id: Optional[UUID] = Query(None)  # for pages, sitemaps
page_id: Optional[UUID] = Query(None)    # for contacts
```

### Standard Response Format:

```python
{
    "items": [...],           # Array of records
    "total": 1000,            # Total matching records
    "page": 1,                # Current page
    "size": 50,               # Page size
    "pages": 20,              # Total pages
    "sort_by": "updated_at",  # Applied sort field
    "sort_order": "desc"      # Applied sort direction
}
```

---

## Delete vs Archive Strategy

### Recommendation: **Soft Delete with Archive Status**

**Rationale:**
- Preserves data integrity and audit trail
- Allows recovery of accidentally deleted records
- Maintains referential integrity (no orphaned foreign keys)
- Supports "blacklist" functionality (archived = don't reprocess)

### Implementation Pattern:

```python
# Add to all models that need it:
is_archived: bool = Column(Boolean, default=False, index=True)
archived_at: Optional[datetime] = Column(DateTime, nullable=True)
archived_by: Optional[UUID] = Column(UUID, nullable=True)

# Or use existing status enum:
class StatusEnum(str, Enum):
    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"
    Archived = "Archived"  # <- Already exists in most enums!
```

### Delete Endpoint Behavior:

```python
@router.delete("/{id}")
async def delete_record(id: UUID, hard_delete: bool = Query(False)):
    """
    Soft delete by default (sets status to Archived).
    Pass hard_delete=true to permanently remove (admin only).
    """
    if hard_delete:
        # Requires elevated permissions
        await service.hard_delete(id)
        return Response(status_code=204)
    else:
        # Soft delete - just archive
        await service.archive(id)
        return {"message": "Record archived", "id": str(id)}
```

---

## Implementation Roadmap

### Phase 1: Add Sorting (Quick Win)
Add `sort_by` and `sort_order` params to:
- [ ] `wf1_place_staging_router.py` - Places LIST
- [ ] `wf5_sitemap_file_router.py` - Sitemaps LIST
- [ ] `WF7_V3_L3_1of1_PagesRouter.py` - Pages LIST
- [ ] `contacts_router.py` - Contacts LIST

### Phase 2: Add Parent Filters (Quick Win)
- [ ] Pages: Add `domain_id` filter
- [ ] Contacts: Add `page_id` filter
- [ ] Local Businesses: Add `place_id` filter (link back to source)

### Phase 3: Standardize DELETE/Archive
- [ ] Define archive pattern (use existing Archived status vs new flag)
- [ ] Add DELETE endpoint to all routers that lack it
- [ ] Default to soft delete, optional hard delete for admins

### Phase 4: Fill CRUD Gaps
- [ ] Add GET by ID to: Domains, Local Biz, Places, Pages
- [ ] Add UPDATE single to: Domains, Local Biz, Places, Pages
- [ ] (CREATE only where it makes sense - most records are system-generated)

---

## Quick Reference: Current Router Endpoints

### WF1 - Places (`/api/v3/localminer-discoveryscan/*` + `/places/staging/*`)
```
GET    /places/staging                    # List all staged places
GET    /places/staging/{job_id}           # List by discovery job
PUT    /places/staging/status             # Batch update status
PUT    /places/staging/status/filtered    # Filtered batch update
PUT    /places/staging/queue-deep-scan    # Direct queue action
```

### WF3 - Local Businesses (`/api/v3/local-businesses/*`)
```
GET    /                    # List with pagination, sorting, filtering
PUT    /status              # Batch update status
PUT    /status/filtered     # Filtered batch update
```

### WF4 - Domains (`/api/v3/domains/*`)
```
GET    /                                   # List with pagination, sorting, filtering
PUT    /sitemap-curation/status            # Batch update curation status
PUT    /sitemap-curation/status/filtered   # Filtered batch update
```

### WF5 - Sitemap Files (`/api/v3/sitemap-files/*`)
```
GET    /                                          # List with filtering
GET    /{id}                                      # Get by ID
POST   /                                          # Create
PUT    /{id}                                      # Update
DELETE /{id}                                      # Delete (hard)
PUT    /sitemap_import_curation/status            # Batch update
PUT    /sitemap_import_curation/status/filtered   # Filtered batch update
```

### WF7 - Pages (`/api/v3/pages/*`)
```
GET    /                    # List with filtering
PUT    /status              # Batch update curation status
PUT    /status/filtered     # Filtered batch update
```

### WF7 - Contacts (`/api/v3/contacts/*`)
```
GET    /                    # List
GET    /{id}                # Get by ID
POST   /                    # Create
PUT    /{id}                # Update
DELETE /{id}                # Delete
PUT    /status              # Batch update
PUT    /status/filtered     # Filtered batch update
PUT    /crm/select          # CRM-specific action
```

---

## Sortable Fields by Entity

| Entity | Sortable Fields |
|--------|-----------------|
| **Domains** | `domain`, `created_at`, `updated_at`, `sitemap_curation_status`, `status` |
| **Local Biz** | `business_name`, `status`, `updated_at`, `created_at`, `city`, `state` |
| **Places** | `name`, `status`, `updated_at`, `search_time`, `rating` |
| **Sitemaps** | `url`, `status`, `url_count`, `created_at`, `last_processed_at` |
| **Pages** | `url`, `title`, `page_curation_status`, `created_at`, `updated_at`, `last_scan` |
| **Contacts** | `email`, `created_at`, `updated_at`, `curation_status` |

---

*Last updated: 2025-11-22*
