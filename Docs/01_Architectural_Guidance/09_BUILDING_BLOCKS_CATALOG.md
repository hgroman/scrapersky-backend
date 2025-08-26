# Building Blocks Catalog

**Version:** 1.0  
**Owner:** The Architect  
**Created:** 2025-08-25  
**Purpose:** Battle-tested, production-verified code patterns for repeated implementation

**Authority:** Constitutional repository for all repeatable implementation patterns. Every pattern documented here has been proven in production or extracted from production incidents.

---

## CRUD Operations

### Pattern: PostgreSQL ENUM CRUD Endpoints

**Origin:** WF7 Production Incident (2025-08-25) - 404 errors on /api/v3/pages affecting 4,157 records

**The Problem:**
```python
# ❌ FAILED IN PRODUCTION - PostgreSQL ENUMs don't have .value
"curation_status": page.page_curation_status.value if page.page_curation_status else None,
```

**The Solution:**
```python
# ✅ PRODUCTION VERIFIED - str() casting works with PostgreSQL ENUMs
"curation_status": str(page.page_curation_status) if page.page_curation_status is not None else None,
```

**Complete Pattern:**
```python
@router.get("/", status_code=status.HTTP_200_OK)
async def get_items(
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0
):
    # Separate count query for accurate pagination
    count_stmt = select(YourModel)
    count_result = await session.execute(count_stmt)
    total_count = len(count_result.scalars().all())
    
    # Paginated data query
    stmt = select(YourModel).offset(offset).limit(limit)
    result = await session.execute(stmt)
    items = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(item.id),  # UUID to string
                "enum_field": str(item.enum_field) if item.enum_field is not None else None,  # PostgreSQL ENUM handling
                "nullable_field": item.nullable_field if item.nullable_field else None,
                "timestamp": item.timestamp.isoformat() if item.timestamp else None
            }
            for item in items
        ],
        "total": total_count,  # Accurate count, not len(items)
        "offset": offset,
        "limit": limit
    }
```

**MCP Verification Script:**
```python
# Always verify schema before implementation
mcp__supabase_mcp_server__execute_sql(
    project_id="your_project_id",
    query="SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'your_table' ORDER BY ordinal_position;"
)
```

**Production Deployment Checklist:**
- [ ] MCP schema verification completed
- [ ] PostgreSQL ENUM serialization tested with `str()`
- [ ] Boolean evaluation uses `is not None` for SQLAlchemy columns
- [ ] Separate count query implemented for accurate pagination
- [ ] Authentication dependency included
- [ ] Error handling with HTTPException

---

### Pattern: Server-Side Filtering Enhancement

**Origin:** WF7 Scalability Enhancement (2025-08-26) - Frontend bottleneck with millions of records

**The Problem:**
```javascript
// ❌ FAILED - Frontend trying to filter millions of records client-side
const allPages = await fetch('/api/v3/pages/?limit=1000000');
const filtered = allPages.filter(page => page.status === 'Selected'); // Browser crashes
```

**The Solution:**
```python
# ✅ PRODUCTION VERIFIED - Server-side filtering with Query parameters
@router.get("/", status_code=status.HTTP_200_OK)
async def get_items_filtered(
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
    # Server-side filter parameters
    status_filter: Optional[YourStatusEnum] = Query(None, description="Filter by status"),
    text_contains: Optional[str] = Query(None, description="Filter by text content (case-insensitive)"),
    foreign_key_filter: Optional[uuid.UUID] = Query(None, description="Filter by related entity")
):
    # Build conditional filters
    filters = []
    if status_filter is not None:
        filters.append(YourModel.status_field == status_filter)
    if text_contains:
        filters.append(YourModel.text_field.ilike(f"%{text_contains}%"))
    if foreign_key_filter:
        filters.append(YourModel.foreign_key == foreign_key_filter)
    
    # Apply filters to count query
    count_stmt = select(YourModel)
    if filters:
        count_stmt = count_stmt.where(*filters)
    count_result = await session.execute(count_stmt)
    total_count = len(count_result.scalars().all())
    
    # Apply filters to data query
    stmt = select(YourModel).offset(offset).limit(limit)
    if filters:
        stmt = stmt.where(*filters)
    result = await session.execute(stmt)
    items = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(item.id),
                "status": str(item.status_field) if item.status_field is not None else None,
                "text_field": item.text_field,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            for item in items
        ],
        "total": total_count,
        "offset": offset,
        "limit": limit,
        # Debugging metadata
        "filters_applied": {
            "status_filter": str(status_filter) if status_filter else None,
            "text_contains": text_contains,
            "foreign_key_filter": str(foreign_key_filter) if foreign_key_filter else None
        }
    }
```

**Key Implementation Details:**
1. **All filters optional**: Default `None` values maintain backwards compatibility
2. **Conditional WHERE clauses**: Only applied when filter parameters provided
3. **Database indexes utilized**: Enum and foreign key columns should be indexed
4. **Case-insensitive text search**: Use `ilike()` for PostgreSQL
5. **Filter debugging**: Include `filters_applied` in response for frontend debugging

**Performance Optimization:**
- Separate count and data queries for accuracy
- Leverage existing database indexes on enum and foreign key columns
- Use `*filters` unpacking for clean conditional WHERE application

**Frontend Usage:**
```javascript
// ✅ Efficient server-side filtering
const filtered = await fetch('/api/v3/items/?status_filter=Selected&text_contains=electric&limit=50');
const data = await filtered.json();
console.log(`Found ${data.total} matches, showing ${data.items.length}`);
```

**Production Deployment Checklist:**
- [ ] All filter parameters have `Optional[Type] = Query(None)` signature
- [ ] Database indexes exist on filtered columns
- [ ] Backwards compatibility verified (no required parameters added)
- [ ] OpenAPI documentation auto-generates parameter descriptions
- [ ] Case-insensitive text search tested with `ilike()`
- [ ] `filters_applied` metadata included for debugging

---

### Pattern: Batch Status Updates with Dual-Status Pattern

**Origin:** WF7 Router Implementation - Pages curation workflow

**The Pattern:**
```python
@router.put("/status", response_model=BatchUpdateResponse, status_code=status.HTTP_200_OK)
async def update_batch_status(
    request: BatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    updated_count = 0
    triggered_count = 0

    # Router owns transaction boundary (Layer 3 Constitutional requirement)
    async with session.begin():
        stmt = select(YourModel).where(YourModel.id.in_(request.item_ids))
        result = await session.execute(stmt)
        items_to_update = result.scalars().all()

        if not items_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No items found with the provided IDs.",
            )

        for item in items_to_update:
            item.primary_status = request.status
            updated_count += 1

            # Dual-Status Update Pattern - trigger secondary workflow
            if request.status == PrimaryStatus.Queued:
                item.processing_status = ProcessingStatus.Queued
                item.processing_error = None
                triggered_count += 1

    return BatchUpdateResponse(
        updated_count=updated_count,
        triggered_count=triggered_count
    )
```

---

## Model Patterns

### Pattern: PostgreSQL ENUM Integration

**The Truth:** PostgreSQL ENUMs in SQLAlchemy require `create_type=False` and `str()` serialization.

```python
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

class YourModel(Base):
    status_field: Column[YourEnum] = Column(
        PgEnum(YourEnum, name="your_enum_type", create_type=False),
        nullable=False,
        default=YourEnum.DefaultValue,
        index=True,
    )
```

**Serialization Method:**
```python
# In router responses
"status": str(item.status_field) if item.status_field is not None else None
```

**Database Verification:**
```sql
-- Verify ENUM type exists in production
SELECT typname FROM pg_type WHERE typtype = 'e';
```

---

### Pattern: UUID Primary Keys with Frontend Compatibility

**The Truth:** UUIDs must be converted to strings for JSON serialization.

```python
from sqlalchemy.dialects.postgresql import UUID as PGUUID

class YourModel(Base):
    id: Column[uuid.UUID] = Column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
```

**Serialization:**
```python
"id": str(item.id)  # Always convert UUID to string for API responses
```

---

## Adapter Patterns

### Pattern: Database-to-API Response Mapping

**The Truth:** Never assume field names or types. Always verify with MCP first.

**Verification Process:**
1. Use MCP to get actual table schema
2. Map each database field to API response field
3. Handle nullable fields explicitly
4. Test with production data

**Standard Mapping:**
```python
{
    "id": str(db_item.id),  # UUID conversion
    "required_text": db_item.required_field,  # Direct mapping
    "optional_text": db_item.optional_field if db_item.optional_field else None,
    "enum_value": str(db_item.enum_field) if db_item.enum_field is not None else None,
    "timestamp": db_item.timestamp.isoformat() if db_item.timestamp else None,
    "foreign_key": str(db_item.foreign_key_id) if db_item.foreign_key_id else None
}
```

---

## Batch Operations

### Pattern: High-Volume Data Processing

**The Truth:** Separate count queries are required for accurate pagination with large datasets.

```python
# ❌ WRONG - Returns limit (100), not total count (4,157)
items = result.scalars().all()
total = len(items)

# ✅ CORRECT - Separate count query
count_stmt = select(YourModel)
count_result = await session.execute(count_stmt)
total_count = len(count_result.scalars().all())
```

---

## Constitutional Integration

### Layer 3 Router Guardian Requirements

**Transaction Boundaries:**
- Routers MUST own transaction boundaries with `async with session.begin()`
- Services MUST accept `AsyncSession` parameters, never create their own transactions

**Authentication:**
- All endpoints MUST include `current_user: Dict = Depends(get_current_user)`

**Error Handling:**
- Use `HTTPException` with proper status codes
- Provide meaningful error messages

### MCP Verification Protocol

**Before ANY database-dependent implementation:**
1. Verify table exists and has expected data
2. Check column names, types, and nullable status  
3. Test enum serialization in isolation
4. Validate foreign key relationships

**Never assume. Always verify.**

---

## Production Incident Learnings

### WF7 CRUD Endpoint Failure (2025-08-25)

**What Happened:** 404 errors on /api/v3/pages affecting React frontend access to 4,157 pages

**Root Cause:** PostgreSQL ENUM fields accessed with `.value` instead of `str()` casting

**The Fix:** Lines 60-61 in WF7_V3_L3_1of1_PagesRouter.py - changed `.value` to `str()`

**Never Again:** All ENUM serialization must use `str()` casting, documented in this catalog

---

**Constitutional Authority:** This catalog represents battle-tested truth extracted from production systems. Every pattern has been verified under fire.