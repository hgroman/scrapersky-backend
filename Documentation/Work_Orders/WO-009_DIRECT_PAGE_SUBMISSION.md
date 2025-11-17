# WO-009: Direct Page Submission Endpoint
**Created:** November 17, 2025
**Priority:** HIGH
**Estimated Effort:** 3-4 hours
**Risk Level:** MEDIUM (touches critical WF7 processing)

---

## Objective

Implement `/api/v3/pages/direct-submit` endpoint to allow users to submit individual page URLs directly, bypassing WF1→WF5 (Google Maps → Sitemap Import).

**Entry Point:** WF7 (Page Curation)
**Bypass:** WF1, WF2, WF3, WF4, WF5
**Benefit:** Enables targeted scraping without requiring Google Maps search or sitemap discovery

---

## Background

**Current Flow:**
```
WF1 (Google Maps) → WF2 (Deep Scan) → WF3 (Domain Extraction) →
WF4 (Sitemap Discovery) → WF5 (Sitemap Import) → WF7 (Page Curation)
```

**New Flow:**
```
Direct API Call → Page Record Created → WF7 (Page Curation)
```

**Use Case:** User has specific URLs to scrape (e.g., competitor contact pages, industry directories) without needing Google Maps data.

---

## Technical Analysis

### Layer 1: Model Analysis (Page)

**File:** `src/models/page.py`

**Critical Fields:**
```python
class Page(Base):
    __tablename__ = "pages"

    # Primary Key
    id: UUID (required)

    # Core Fields
    url: String (required, unique)
    domain_id: UUID (optional - can be NULL for direct submission)
    sitemap_file_id: UUID (optional - NULL for direct submission)

    # DUAL-STATUS PATTERN (CRITICAL)
    page_curation_status: PageCurationStatus (ENUM)
    page_processing_status: PageProcessingStatus (ENUM)

    # Honeybee Fields
    page_category: String (nullable)
    category_confidence: Float (nullable)
    depth: Integer (nullable)
    priority_level: Integer (default=5)

    # Processing Results
    scraped_content: JSONB (nullable)
    scraped_at: DateTime (nullable)

    # Metadata
    created_at: DateTime (required)
    updated_at: DateTime (required)
    user_id: UUID (nullable)
```

### ENUM Dependencies (CRITICAL - ADR-005)

**PageCurationStatus (Layer 1):**
```python
# File: src/models/page.py
class PageCurationStatus(str, Enum):
    New = "New"
    Selected = "Selected"
    Rejected = "Rejected"
```

**PageProcessingStatus (Layer 1):**
```python
# File: src/models/page.py
class PageProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
```

**Schema Layer ENUMs (Layer 2):**
```python
# File: src/schemas/WF7_V3_L2_1of1_PageCurationSchemas.py
# Must match Layer 1 exactly (uses same imports)
from src.models.page import PageCurationStatus, PageProcessingStatus
```

**⚠️ CRITICAL:** Any ENUM changes MUST be coordinated across all 4 layers (ADR-005: ENUM Catastrophe)

---

## Field Dependencies & Constraints

### Required Fields (Direct Submission)
1. ✅ `id` - Client-side UUID generation (consistent with WF7 pattern)
2. ✅ `url` - User-provided URL (must validate)
3. ✅ `page_curation_status` - Set based on `auto_queue` flag
4. ✅ `page_processing_status` - Set based on `auto_queue` flag
5. ✅ `created_at` - `datetime.utcnow()`
6. ✅ `user_id` - From JWT token

### Optional Fields (Can be NULL)
1. ⚠️ `domain_id` - NULL for direct submission (not from WF3 flow)
2. ⚠️ `sitemap_file_id` - NULL for direct submission (not from WF5)
3. ✅ `page_category` - NULL initially (no Honeybee for direct submission)
4. ✅ `category_confidence` - NULL initially
5. ✅ `depth` - NULL initially
6. ✅ `priority_level` - Default to 5 (medium priority)

### Constraints to Verify
```sql
-- Check unique constraint
SELECT conname, contype
FROM pg_constraint
WHERE conrelid = 'pages'::regclass;

-- Expected: UNIQUE constraint on url
-- If constraint exists on (url, domain_id) composite, we have a problem
```

**⚠️ CRITICAL CHECK:** Verify `url` uniqueness constraint allows NULL `domain_id`

---

## Risk Assessment

### HIGH RISK: Existing Workflow Interference

**Risk:** Direct submission pages might conflict with WF5-imported pages

**Scenarios:**
1. User submits `example.com/contact` directly
2. Later, WF5 imports sitemap containing same URL
3. **Potential Conflict:** Duplicate URL or constraint violation

**Mitigation:**
```python
# Check if URL already exists before creating
existing_page = await session.execute(
    select(Page).where(Page.url == url)
)
if existing_page.scalar_one_or_none():
    raise HTTPException(409, "Page already exists")
```

### MEDIUM RISK: Missing domain_id

**Risk:** Pages without `domain_id` might break domain-based queries

**Impact Areas:**
```bash
# Find queries that assume domain_id exists
grep -r "domain_id IS NOT NULL" src/
grep -r "JOIN domains" src/services/
```

**Mitigation:** Review all domain-based queries, add NULL handling

### LOW RISK: Honeybee Integration

**Risk:** Direct submission pages lack Honeybee categorization

**Impact:** Auto-selection logic won't work (requires category + confidence)

**Mitigation:** Document that direct submissions require manual curation unless user specifies `auto_queue=True`

---

## Implementation Plan

### Phase 1: Pre-Implementation Verification (30 min)

**Task 1.1: Verify Database Constraints**
```sql
-- Check unique constraints
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'pages'::regclass;

-- Check NULL handling
SELECT COUNT(*) FROM pages WHERE domain_id IS NULL;
SELECT COUNT(*) FROM pages WHERE sitemap_file_id IS NULL;
```

**Expected Results:**
- Unique constraint on `url` only (not composite with `domain_id`)
- Some pages already have NULL `domain_id` (confirms NULL is allowed)

**Task 1.2: Audit Existing Queries**
```bash
# Find all queries that JOIN on domain_id
grep -rn "JOIN domains ON" src/services/
grep -rn "domain_id IS NOT NULL" src/

# Document findings in this work order
```

**Task 1.3: Verify WF7 Scheduler Compatibility**
```bash
# Check if scheduler filters require domain_id
cat src/services/WF7_V2_L4_2of2_PageCurationScheduler.py | grep -A 5 "WHERE"
```

**✅ CHECKPOINT:** All verifications pass before proceeding

---

### Phase 2: Layer 2 - Schema Creation (30 min)

**File:** `src/schemas/pages_direct_submission_schemas.py` (NEW)

```python
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from uuid import UUID

class DirectPageSubmissionRequest(BaseModel):
    """Request schema for direct page submission."""

    urls: list[HttpUrl] = Field(
        ...,
        min_items=1,
        max_items=100,  # Prevent abuse
        description="List of page URLs to submit"
    )

    auto_queue: bool = Field(
        default=False,
        description="If True, auto-select and queue for WF7 processing"
    )

    priority_level: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Priority level (1=highest, 10=lowest)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://example.com/contact",
                    "https://example.com/about"
                ],
                "auto_queue": True,
                "priority_level": 3
            }
        }


class DirectPageSubmissionResponse(BaseModel):
    """Response schema for direct page submission."""

    submitted_count: int
    page_ids: list[UUID]
    auto_queued: bool

    class Config:
        json_schema_extra = {
            "example": {
                "submitted_count": 2,
                "page_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001"
                ],
                "auto_queued": True
            }
        }
```

**✅ CHECKPOINT:** Schema passes pydantic validation tests

---

### Phase 3: Layer 3 - Router Implementation (60 min)

**File:** `src/routers/v3/pages_direct_submission_router.py` (NEW)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from src.db.session import get_db_session
from src.auth.dependencies import get_current_user
from src.models.page import Page, PageCurationStatus, PageProcessingStatus
from src.schemas.pages_direct_submission_schemas import (
    DirectPageSubmissionRequest,
    DirectPageSubmissionResponse
)

router = APIRouter(
    prefix="/api/v3/pages",
    tags=["V3 - Pages Direct Submission"]
)


@router.post("/direct-submit", response_model=DirectPageSubmissionResponse)
async def submit_pages_directly(
    request: DirectPageSubmissionRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit page URLs directly for WF7 processing, bypassing WF1-WF5.

    **Use Case:**
    - User has specific URLs to scrape
    - Bypass Google Maps and sitemap discovery
    - Direct entry to WF7 (Page Curation)

    **Auto-Queue Behavior:**
    - `auto_queue=True`: Sets status to Selected + Queued (WF7 picks up immediately)
    - `auto_queue=False`: Sets status to New + NULL (requires manual curation)

    **Constraints:**
    - Maximum 100 URLs per request
    - Duplicate URLs are rejected with 409 Conflict
    - Requires authentication

    **Status Initialization:**
    - `page_curation_status`: "Selected" if auto_queue, else "New"
    - `page_processing_status`: "Queued" if auto_queue, else NULL
    - `domain_id`: NULL (not from domain workflow)
    - `sitemap_file_id`: NULL (not from sitemap workflow)
    """
    page_ids = []

    async with session.begin():
        for url in request.urls:
            url_str = str(url)

            # Check for duplicates
            existing_check = await session.execute(
                select(Page).where(Page.url == url_str)
            )
            existing_page = existing_check.scalar_one_or_none()

            if existing_page:
                raise HTTPException(
                    status_code=409,
                    detail=f"Page already exists: {url_str} (ID: {existing_page.id})"
                )

            # Create page with proper status initialization
            page = Page(
                id=uuid.uuid4(),
                url=url_str,

                # NULL foreign keys (not from WF3/WF5)
                domain_id=None,
                sitemap_file_id=None,

                # DUAL-STATUS PATTERN (CRITICAL)
                page_curation_status=(
                    PageCurationStatus.Selected if request.auto_queue
                    else PageCurationStatus.New
                ),
                page_processing_status=(
                    PageProcessingStatus.Queued if request.auto_queue
                    else None
                ),

                # Metadata
                priority_level=request.priority_level,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                user_id=current_user.get("user_id"),

                # Honeybee fields (NULL for direct submission)
                page_category=None,
                category_confidence=None,
                depth=None,
            )

            session.add(page)
            page_ids.append(page.id)

    return DirectPageSubmissionResponse(
        submitted_count=len(page_ids),
        page_ids=page_ids,
        auto_queued=request.auto_queue
    )
```

**✅ CHECKPOINT:** Router passes unit tests with mock session

---

### Phase 4: Layer 4 - Service Layer (Optional, 15 min)

**Decision:** Direct submission doesn't need service layer - router handles everything

**Rationale:**
- No complex business logic
- Simple CRUD operation
- Transaction owned by router (ADR-004)

**If needed later:** Extract duplicate checking to service method

---

### Phase 5: Integration with main.py (10 min)

**File:** `src/main.py`

```python
# Add import
from src.routers.v3.pages_direct_submission_router import router as pages_direct_router

# Add router inclusion
app.include_router(pages_direct_router)  # No prefix needed (router defines full path)
```

**✅ CHECKPOINT:** Application starts without errors

---

### Phase 6: Testing (60 min)

**Test 1: Basic Submission (auto_queue=False)**
```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": ["https://example.com/contact"],
    "auto_queue": false,
    "priority_level": 5
  }'
```

**Expected Result:**
```json
{
  "submitted_count": 1,
  "page_ids": ["uuid-here"],
  "auto_queued": false
}
```

**Verification:**
```sql
SELECT id, url, page_curation_status, page_processing_status, domain_id
FROM pages
WHERE url = 'https://example.com/contact';

-- Expected:
-- page_curation_status = 'New'
-- page_processing_status = NULL
-- domain_id = NULL
```

---

**Test 2: Auto-Queue Submission (auto_queue=True)**
```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": ["https://example.com/about"],
    "auto_queue": true,
    "priority_level": 3
  }'
```

**Verification:**
```sql
SELECT id, url, page_curation_status, page_processing_status
FROM pages
WHERE url = 'https://example.com/about';

-- Expected:
-- page_curation_status = 'Selected'
-- page_processing_status = 'Queued'
```

**Wait 5 minutes (WF7 scheduler interval), then check:**
```sql
SELECT id, url, page_processing_status, scraped_at, scraped_content IS NOT NULL
FROM pages
WHERE url = 'https://example.com/about';

-- Expected:
-- page_processing_status = 'Complete'
-- scraped_at = recent timestamp
-- scraped_content IS NOT NULL = true
```

**✅ CHECKPOINT:** WF7 scheduler picks up and processes auto-queued page

---

**Test 3: Duplicate Detection**
```bash
# Submit same URL twice
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": ["https://example.com/contact"],
    "auto_queue": false
  }'
```

**Expected Result:**
```json
{
  "detail": "Page already exists: https://example.com/contact (ID: ...)"
}
```

**Status Code:** 409 Conflict

---

**Test 4: Batch Submission**
```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://site1.com/contact",
      "https://site2.com/about",
      "https://site3.com/careers"
    ],
    "auto_queue": true,
    "priority_level": 2
  }'
```

**Expected Result:**
```json
{
  "submitted_count": 3,
  "page_ids": ["uuid1", "uuid2", "uuid3"],
  "auto_queued": true
}
```

---

**Test 5: Existing WF7 Queries (Regression)**
```bash
# Verify existing /api/v3/pages endpoint still works
curl http://localhost:8000/api/v3/pages \
  -H "Authorization: Bearer $JWT_TOKEN"

# Should return pages including direct submissions
```

**Verification:**
```sql
-- Check that domain-based queries handle NULL domain_id
SELECT p.id, p.url, d.domain
FROM pages p
LEFT JOIN domains d ON p.domain_id = d.id
WHERE p.page_curation_status = 'Selected'
LIMIT 10;

-- Should work with LEFT JOIN (not INNER JOIN)
```

**✅ CHECKPOINT:** All tests pass

---

## Rollback Plan

**If implementation fails:**

1. **Remove router from main.py**
```python
# Comment out:
# app.include_router(pages_direct_router)
```

2. **Delete created pages**
```sql
DELETE FROM pages
WHERE domain_id IS NULL
AND sitemap_file_id IS NULL
AND created_at > '2025-11-17 00:00:00';
```

3. **Remove new files**
```bash
rm src/routers/v3/pages_direct_submission_router.py
rm src/schemas/pages_direct_submission_schemas.py
```

4. **Restart application**
```bash
docker compose restart app
```

**Time to rollback:** < 5 minutes

---

## Success Criteria

- ✅ Direct page submission creates valid Page records
- ✅ Auto-queue flag properly sets dual-status fields
- ✅ WF7 scheduler picks up auto-queued pages
- ✅ Duplicate URLs are rejected with 409
- ✅ Existing /api/v3/pages queries work unchanged
- ✅ No errors in application logs
- ✅ All existing WF7 workflows continue to function

---

## Documentation Updates

**After successful implementation:**

1. Update `Documentation/Context_Reconstruction/EXTENSIBILITY_PATTERNS.md`
   - Mark Pattern 1 as "✅ IMPLEMENTED"
   - Add actual endpoint path and examples

2. Update `Documentation/Workflows/README.md`
   - Add note about direct page submission option

3. Add to API documentation (Swagger/OpenAPI)
   - Endpoint auto-documented via FastAPI

---

## Related Work

- **ADR-003:** Dual-Status Workflow Pattern (MUST follow)
- **ADR-004:** Transaction Boundaries (Router owns transaction)
- **ADR-005:** ENUM Catastrophe (Coordinate ENUM changes across layers)
- **EXTENSIBILITY_PATTERNS.md:** Original design documentation
- **WF7 Implementation:** Reference for status handling patterns

---

**Status:** READY FOR REVIEW
**Blocked By:** None
**Blocking:** WO-010, WO-011 (similar patterns)
