# WO-011: Direct Sitemap Submission Endpoint
**Created:** November 17, 2025
**Priority:** MEDIUM
**Estimated Effort:** 2.5-3 hours
**Risk Level:** MEDIUM (interacts with WF5 sitemap import)

---

## Objective

Implement `/api/v3/sitemaps/direct-submit` endpoint to allow users to submit sitemap URLs directly, bypassing WF1→WF4 (Google Maps → Sitemap Discovery).

**Entry Point:** WF5 (Sitemap Import)
**Bypass:** WF1, WF2, WF3, WF4
**Benefit:** Enables direct sitemap import when user already knows sitemap URLs

---

## Background

**Current Flow:**
```
WF1 (Google Maps) → WF2 (Deep Scan) → WF3 (Domain Extraction) →
WF4 (Sitemap Discovery) → WF5 (Sitemap Import) → WF7 (Page Curation)
```

**New Flow:**
```
Direct API Call → SitemapFile Record Created → WF5 (Sitemap Import) → WF7
```

**Use Case:** User knows specific sitemap URLs to import (e.g., `example.com/sitemap.xml`, `site.com/sitemap_index.xml`)

---

## Technical Analysis

### Layer 1: Model Analysis (SitemapFile)

**File:** `src/models/sitemap.py` (or similar)

**Critical Fields:**
```python
class SitemapFile(Base):
    __tablename__ = "sitemap_files"

    # Primary Key
    id: UUID (required)

    # Core Fields
    url: String (required, unique)
    domain_id: UUID (optional - can be NULL or matched)

    # STATUS FIELDS (Check actual model for exact pattern)
    sitemap_curation_status: SitemapCurationStatus (ENUM)
    sitemap_import_status: SitemapImportStatus (ENUM)

    # Sitemap Metadata (populated after import)
    url_count: Integer (nullable)
    last_modified: DateTime (nullable)
    file_size: Integer (nullable)

    # Timestamps
    created_at: DateTime (required)
    updated_at: DateTime (required)
    user_id: UUID (nullable)
```

**⚠️ CRITICAL PRE-VERIFICATION REQUIRED:**
```bash
# MUST verify actual model structure before implementation
cat src/models/sitemap.py | grep -A 5 "class SitemapFile"
cat src/models/sitemap.py | grep "status"
```

### ENUM Dependencies (CRITICAL - ADR-005)

**⚠️ VERIFICATION REQUIRED - Check actual model:**
```python
# Expected pattern (verify against code):
class SitemapCurationStatus(str, Enum):
    New = "New"
    Selected = "Selected"
    Rejected = "Rejected"

class SitemapImportStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
```

**ACTION REQUIRED:** Document actual ENUM definitions before proceeding

---

## Field Dependencies & Constraints

### Required Fields (Direct Submission)
1. ✅ `id` - UUID generation
2. ✅ `url` - User-provided sitemap URL (must validate)
3. ✅ `sitemap_curation_status` - Set based on `auto_import` flag
4. ✅ `sitemap_import_status` - Set based on `auto_import` flag
5. ✅ `created_at` - `datetime.utcnow()`
6. ✅ `user_id` - From JWT token

### Optional Fields
1. ⚠️ `domain_id` - **DECISION REQUIRED:**
   - **Option A:** NULL (not matched to domain)
   - **Option B:** Auto-match domain from sitemap URL
   - **Option C:** User-provided domain_id (optional parameter)

2. ✅ `url_count` - NULL initially (populated after import)
3. ✅ `last_modified` - NULL initially
4. ✅ `file_size` - NULL initially

### Sitemap URL Validation
```python
from urllib.parse import urlparse

def validate_sitemap_url(url_str: str) -> str:
    """
    Validate sitemap URL.

    Must:
    - Be valid HTTP/HTTPS URL
    - End with .xml (or be sitemap_index.xml)
    - Be accessible (optional: pre-fetch check)

    Returns: Normalized URL
    """
    if not url_str.startswith(("http://", "https://")):
        raise ValueError("Sitemap URL must start with http:// or https://")

    parsed = urlparse(url_str)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid URL format")

    # Optional: Validate .xml extension
    if not (parsed.path.endswith(".xml") or "sitemap" in parsed.path.lower()):
        raise ValueError("URL must be a sitemap file (.xml)")

    return url_str
```

### Domain Matching Logic (If Implemented)
```python
def extract_domain_from_sitemap_url(sitemap_url: str) -> str:
    """
    Extract domain from sitemap URL.

    Example:
    - https://example.com/sitemap.xml → example.com
    - https://www.site.org/sitemaps/index.xml → site.org
    """
    parsed = urlparse(sitemap_url)
    domain = parsed.netloc.replace("www.", "")
    return domain.lower()
```

---

## Risk Assessment

### MEDIUM RISK: Domain Matching Decision

**Risk:** Ambiguity in how to handle `domain_id` field

**Options:**
1. **NULL domain_id** (simplest, lowest risk)
   - Pros: No domain matching logic, no conflicts
   - Cons: Sitemaps not linked to domains

2. **Auto-match domain** (medium complexity)
   - Pros: Maintains domain relationships
   - Cons: What if domain doesn't exist? Create it automatically?

3. **User-provided domain_id** (most flexible)
   - Pros: User controls relationship
   - Cons: Requires user to know domain_id

**RECOMMENDED DECISION:**
- **Phase 1:** NULL domain_id (defer matching)
- **Phase 2:** Optional `domain_id` parameter
- **Phase 3:** Auto-match with auto-create option

**For this work order, implement Option 1 (NULL domain_id)**

---

### LOW RISK: Duplicate Sitemap URLs

**Risk:** User submits sitemap URL that already exists

**Mitigation:**
```python
# Check for duplicates
existing_sitemap = await session.execute(
    select(SitemapFile).where(SitemapFile.url == sitemap_url)
)
if existing_sitemap.scalar_one_or_none():
    raise HTTPException(409, "Sitemap already exists")
```

---

### LOW RISK: WF5 Scheduler Compatibility

**Risk:** Scheduler might assume domain_id exists

**Verification Required:**
```bash
# Check WF5 scheduler query
grep -A 20 "sitemap_import_status" src/services/sitemap_import_scheduler.py
```

**Expected:** Filters on status, not domain_id

---

## Implementation Plan

### Phase 0: Critical Pre-Verification (30 min)

**⚠️ MUST COMPLETE BEFORE PROCEEDING**

**Task 0.1: Document Actual Model Structure**
```bash
# Read actual SitemapFile model
cat src/models/sitemap.py > /tmp/sitemap_model.txt

# Document:
# 1. Exact class name (SitemapFile? Sitemap? SitemapURL?)
# 2. Exact status field names
# 3. Exact ENUM definitions
# 4. domain_id: nullable or required?
```

**Task 0.2: Document Actual ENUMs**
```bash
# Find ENUM definitions
grep -A 5 "class.*Sitemap.*Status" src/models/sitemap.py

# Document exact values and casing
```

**Task 0.3: Verify WF5 Scheduler Query**
```bash
# Check scheduler logic
cat src/services/sitemap_import_scheduler.py | grep -A 30 "def process"
```

**Task 0.4: Check Existing Sitemaps**
```sql
-- Check if NULL domain_id is allowed
SELECT COUNT(*) FROM sitemap_files WHERE domain_id IS NULL;

-- Check unique constraints
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'sitemap_files'::regclass;
```

**✅ CHECKPOINT:** Document findings in this work order before proceeding

**UPDATE THIS SECTION WITH FINDINGS:**
```
ACTUAL MODEL STRUCTURE:
- Class name: _____________
- Status field 1: _____________
- Status field 2: _____________
- ENUM 1 values: _____________
- ENUM 2 values: _____________
- domain_id nullable: YES / NO
- Unique constraint: _____________
```

---

### Phase 1: Layer 2 - Schema Creation (25 min)

**File:** `src/schemas/sitemaps_direct_submission_schemas.py` (NEW)

```python
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional
from uuid import UUID
from urllib.parse import urlparse


class DirectSitemapSubmissionRequest(BaseModel):
    """Request schema for direct sitemap submission."""

    sitemap_urls: list[HttpUrl] = Field(
        ...,
        min_items=1,
        max_items=50,  # Lower limit than pages/domains (sitemaps are larger)
        description="List of sitemap XML URLs"
    )

    auto_import: bool = Field(
        default=False,
        description="If True, auto-queue for WF5 import"
    )

    domain_id: Optional[UUID] = Field(
        default=None,
        description="Optional domain to associate sitemaps with"
    )

    @validator('sitemap_urls', each_item=True)
    def validate_sitemap_url(cls, url: HttpUrl) -> HttpUrl:
        """Validate sitemap URL format."""
        url_str = str(url)
        parsed = urlparse(url_str)

        # Validate it looks like a sitemap
        if not (parsed.path.endswith('.xml') or 'sitemap' in parsed.path.lower()):
            raise ValueError(
                f"URL must be a sitemap file (.xml): {url_str}"
            )

        return url

    class Config:
        json_schema_extra = {
            "example": {
                "sitemap_urls": [
                    "https://example.com/sitemap.xml",
                    "https://example.com/sitemap_index.xml"
                ],
                "auto_import": True,
                "domain_id": None
            }
        }


class DirectSitemapSubmissionResponse(BaseModel):
    """Response schema for direct sitemap submission."""

    submitted_count: int
    sitemap_ids: list[UUID]
    auto_queued: bool

    class Config:
        json_schema_extra = {
            "example": {
                "submitted_count": 2,
                "sitemap_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001"
                ],
                "auto_queued": True
            }
        }
```

**✅ CHECKPOINT:** Schema validation passes

---

### Phase 2: Layer 3 - Router Implementation (45 min)

**File:** `src/routers/v3/sitemaps_direct_submission_router.py` (NEW)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from src.db.session import get_db_session
from src.auth.dependencies import get_current_user
# ⚠️ UPDATE IMPORT BASED ON PHASE 0 FINDINGS:
from src.models.sitemap import SitemapFile, SitemapCurationStatus, SitemapImportStatus
from src.schemas.sitemaps_direct_submission_schemas import (
    DirectSitemapSubmissionRequest,
    DirectSitemapSubmissionResponse
)

router = APIRouter(
    prefix="/api/v3/sitemaps",
    tags=["V3 - Sitemaps Direct Submission"]
)


@router.post("/direct-submit", response_model=DirectSitemapSubmissionResponse)
async def submit_sitemaps_directly(
    request: DirectSitemapSubmissionRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit sitemap URLs directly for WF5 import, bypassing WF1-WF4.

    **Use Case:**
    - User knows specific sitemap URLs to import
    - Bypass Google Maps, domain extraction, and sitemap discovery
    - Direct entry to WF5 (Sitemap Import)

    **Auto-Import Behavior:**
    - `auto_import=True`: Sets status to Selected + Queued (WF5 picks up immediately)
    - `auto_import=False`: Sets status to New + NULL (requires manual curation)

    **Domain Association:**
    - `domain_id=None`: Sitemap not linked to domain (default)
    - `domain_id=<uuid>`: Link sitemap to specific domain

    **Constraints:**
    - Maximum 50 sitemap URLs per request
    - URLs must end with .xml or contain 'sitemap'
    - Duplicate URLs are rejected with 409 Conflict
    - Requires authentication

    **Status Initialization:**
    - ⚠️ UPDATE BASED ON PHASE 0 FINDINGS
    """
    sitemap_ids = []

    async with session.begin():
        for sitemap_url in request.sitemap_urls:
            url_str = str(sitemap_url)

            # Check for duplicates
            existing_check = await session.execute(
                select(SitemapFile).where(SitemapFile.url == url_str)
            )
            existing_sitemap = existing_check.scalar_one_or_none()

            if existing_sitemap:
                raise HTTPException(
                    status_code=409,
                    detail=f"Sitemap already exists: {url_str} (ID: {existing_sitemap.id})"
                )

            # ⚠️ UPDATE FIELD NAMES BASED ON PHASE 0 FINDINGS
            sitemap_file = SitemapFile(
                id=uuid.uuid4(),
                url=url_str,

                # Domain association (NULL or user-provided)
                domain_id=request.domain_id,

                # DUAL-STATUS PATTERN (CRITICAL)
                # ⚠️ UPDATE STATUS FIELD NAMES AND ENUM VALUES
                sitemap_curation_status=(
                    SitemapCurationStatus.Selected if request.auto_import
                    else SitemapCurationStatus.New
                ),
                sitemap_import_status=(
                    SitemapImportStatus.Queued if request.auto_import
                    else None
                ),

                # Metadata (NULL initially, populated after import)
                url_count=None,
                last_modified=None,
                file_size=None,

                # Timestamps
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                user_id=current_user.get("user_id"),
            )

            session.add(sitemap_file)
            sitemap_ids.append(sitemap_file.id)

    return DirectSitemapSubmissionResponse(
        submitted_count=len(sitemap_ids),
        sitemap_ids=sitemap_ids,
        auto_queued=request.auto_import
    )
```

**⚠️ CRITICAL:** Update router code after Phase 0 findings

**✅ CHECKPOINT:** Router compiles without errors

---

### Phase 3: Integration with main.py (5 min)

**File:** `src/main.py`

```python
# Add import
from src.routers.v3.sitemaps_direct_submission_router import router as sitemaps_direct_router

# Add router inclusion
app.include_router(sitemaps_direct_router)
```

**✅ CHECKPOINT:** Application starts

---

### Phase 4: Testing (45 min)

**Test 1: Basic Submission (auto_import=False)**
```bash
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": ["https://example.com/sitemap.xml"],
    "auto_import": false
  }'
```

**Verification:**
```sql
-- ⚠️ UPDATE TABLE/FIELD NAMES BASED ON PHASE 0
SELECT id, url, sitemap_curation_status, sitemap_import_status, domain_id
FROM sitemap_files
WHERE url = 'https://example.com/sitemap.xml';

-- Expected:
-- sitemap_curation_status = 'New' (or equivalent)
-- sitemap_import_status = NULL
-- domain_id = NULL
```

---

**Test 2: Auto-Import Submission**
```bash
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": ["https://test-site.com/sitemap.xml"],
    "auto_import": true
  }'
```

**Verification:**
```sql
SELECT id, url, sitemap_import_status
FROM sitemap_files
WHERE url = 'https://test-site.com/sitemap.xml';

-- Expected:
-- sitemap_import_status = 'Queued' (or equivalent)
```

**Wait for WF5 scheduler (5 minutes), then check:**
```sql
SELECT sf.url, sf.sitemap_import_status, sf.url_count, COUNT(p.id) as pages_created
FROM sitemap_files sf
LEFT JOIN pages p ON p.sitemap_file_id = sf.id
WHERE sf.url = 'https://test-site.com/sitemap.xml'
GROUP BY sf.url, sf.sitemap_import_status, sf.url_count;

-- Expected:
-- sitemap_import_status = 'Complete' (or equivalent)
-- url_count > 0
-- pages_created > 0
```

**✅ CHECKPOINT:** WF5 scheduler picks up and processes auto-queued sitemap

---

**Test 3: Domain Association**
```bash
# First, get a domain_id
DOMAIN_ID=$(psql -c "SELECT id FROM domains LIMIT 1" -t)

curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d "{
    \"sitemap_urls\": [\"https://linked-site.com/sitemap.xml\"],
    \"auto_import\": false,
    \"domain_id\": \"$DOMAIN_ID\"
  }"
```

**Verification:**
```sql
SELECT url, domain_id
FROM sitemap_files
WHERE url = 'https://linked-site.com/sitemap.xml';

-- Expected: domain_id = provided UUID
```

---

**Test 4: Invalid URL Format**
```bash
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": ["https://example.com/not-a-sitemap.html"],
    "auto_import": false
  }'
```

**Expected:** 422 Unprocessable Entity (validation error)

---

**Test 5: Duplicate Detection**
```bash
# Submit same sitemap twice
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": ["https://example.com/sitemap.xml"],
    "auto_import": false
  }'
```

**Expected:** 409 Conflict

**✅ CHECKPOINT:** All tests pass

---

## Rollback Plan

1. **Remove router from main.py**
2. **Delete created sitemaps:**
```sql
DELETE FROM sitemap_files
WHERE domain_id IS NULL  -- If using NULL domain_id approach
AND created_at > '2025-11-17 00:00:00';
```
3. **Remove new files**
4. **Restart application**

---

## Success Criteria

- ✅ Direct sitemap submission creates valid SitemapFile records
- ✅ Auto-import flag properly sets status fields
- ✅ WF5 scheduler picks up auto-queued sitemaps
- ✅ Sitemap URLs are validated for .xml format
- ✅ Duplicate sitemaps are rejected
- ✅ Domain association works (if domain_id provided)
- ✅ Existing WF5 workflows continue to function
- ✅ No errors in logs

---

## Documentation Updates

1. Update `EXTENSIBILITY_PATTERNS.md` - Mark Pattern 3 as implemented
2. Update `Workflows/README.md` - Add direct sitemap submission note
3. Document actual model structure findings from Phase 0

---

## Open Questions (Resolve Before Implementation)

1. **What is the exact SitemapFile model structure?**
   - Answer in Phase 0 verification

2. **What are the exact ENUM definitions and values?**
   - Answer in Phase 0 verification

3. **Is NULL domain_id allowed?**
   - Answer in Phase 0 verification

4. **Should we auto-create domains if user provides domain in sitemap URL?**
   - Recommendation: No (defer to Phase 2)

---

## Related Work

- **ADR-003:** Dual-Status Workflow Pattern
- **ADR-005:** ENUM Catastrophe (verify ENUMs first!)
- **EXTENSIBILITY_PATTERNS.md:** Original design
- **WO-009:** Direct Page Submission (similar pattern)
- **WO-010:** Direct Domain Submission (similar pattern)

---

**Status:** REQUIRES PHASE 0 VERIFICATION
**Blocked By:** Need to verify actual model structure
**Blocking:** None
