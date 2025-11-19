# WO-011: Direct Sitemap Submission Endpoint
**Created:** November 17, 2025
**Priority:** MEDIUM
**Estimated Effort:** 3.5-4 hours (+1h for domain handling)
**Risk Level:** LOW (critical constraints resolved)

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
    domain_id: UUID (REQUIRED - nullable=False) ⚠️ CRITICAL CONSTRAINT
    sitemap_type: String (REQUIRED - nullable=False) ⚠️ CRITICAL CONSTRAINT
                  # Values: INDEX, STANDARD, IMAGE, VIDEO, NEWS

    # STATUS FIELDS (verified from src/models/sitemap.py)
    deep_scrape_curation_status: SitemapImportCurationStatusEnum (ENUM)
    sitemap_import_status: SitemapImportProcessStatusEnum (ENUM)

    # Sitemap Metadata (populated after import)
    url_count: Integer (nullable)
    last_modified: DateTime (nullable)
    file_size: Integer (nullable)

    # Timestamps
    created_at: DateTime (required)
    updated_at: DateTime (required)
    user_id: UUID (nullable)
```

**✅ VERIFIED:** Model structure confirmed via SYSTEM_MAP.md and verification report

### ENUM Dependencies (CRITICAL - ADR-005)

**✅ VERIFIED from src/models/sitemap.py:**
```python
class SitemapImportCurationStatusEnum(enum.Enum):
    """Curation status for sitemap import."""
    New = "New"
    Selected = "Selected"
    Maybe = "Maybe"
    Not_a_Fit = "Not a Fit"
    Archived = "Archived"

class SitemapImportProcessStatusEnum(enum.Enum):
    """Processing status for sitemap import."""
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
```

**Status Field Names:**
- Curation: `deep_scrape_curation_status`
- Processing: `sitemap_import_status`

---

## Field Dependencies & Constraints

### Required Fields (Direct Submission)
1. ✅ `id` - UUID generation
2. ✅ `url` - User-provided sitemap URL (must validate)
3. ✅ `sitemap_type` - Set to "STANDARD" (nullable=False constraint)
4. ✅ `deep_scrape_curation_status` - Set based on `auto_import` flag
5. ✅ `sitemap_import_status` - Set based on `auto_import` flag
6. ✅ `created_at` - `datetime.utcnow()`
7. ✅ `user_id` - From JWT token

### Fields Requiring Get-or-Create Logic
1. ✅ `domain_id` - **MUST be populated** (nullable=False constraint)
   - Extract domain from sitemap URL using domain extraction utility
   - Get existing domain by name OR create new domain
   - Auto-created domains have `tenant_id=DEFAULT_TENANT_ID` and `local_business_id=NULL`

### Optional Fields
1. ✅ `url_count` - NULL initially (populated after import)
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

### RESOLVED: Domain ID Constraint (Critical)

**Original Risk:** Assumed `domain_id` could be NULL for direct submissions

**Ground Truth:** `domain_id` has `nullable=False` constraint (verified via SYSTEM_MAP.md Critical Constraints and WO-009-011_CRITICAL_VERIFICATION_REPORT.md)

**Solution: Get-or-Create Domain Pattern**
```python
# Extract domain from sitemap URL
from urllib.parse import urlparse

def extract_domain_from_sitemap_url(url: str) -> str:
    """Extract domain from sitemap URL (e.g., 'example.com' from 'https://www.example.com/sitemap.xml')."""
    parsed = urlparse(url)
    domain = parsed.netloc
    # Remove 'www.' prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

# Get or create domain
domain_name = extract_domain_from_sitemap_url(sitemap_url_str)
result = await session.execute(
    select(Domain).where(Domain.domain == domain_name)
)
domain = result.scalar_one_or_none()

if not domain:
    domain = Domain(
        id=uuid.uuid4(),
        domain=domain_name,
        tenant_id=uuid.UUID(DEFAULT_TENANT_ID),  # REQUIRED (nullable=False)
        local_business_id=None,  # NULL OK here (nullable=True)
        sitemap_curation_status=SitemapCurationStatusEnum.New,
        sitemap_analysis_status=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(domain)
    await session.flush()  # Get domain.id before using it

# Now create sitemap file with valid domain_id
sitemap_file.domain_id = domain.id  # NOT NULL ✅
sitemap_file.sitemap_type = "STANDARD"  # REQUIRED (nullable=False)
```

**Impact:** Maintains referential integrity, enables domain-sitemap analytics, no database migration needed

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

### Phase 0: Critical Pre-Verification ✅ COMPLETE

**✅ VERIFICATION COMPLETED** via WO-009-011_CRITICAL_VERIFICATION_REPORT.md and SYSTEM_MAP.md

**VERIFIED MODEL STRUCTURE:**
```
- Class name: SitemapFile (src/models/sitemap.py)
- Status field 1: deep_scrape_curation_status (SitemapImportCurationStatusEnum)
- Status field 2: sitemap_import_status (SitemapImportProcessStatusEnum)
- ENUM 1 values: New, Selected, Maybe, Not_a_Fit, Archived
- ENUM 2 values: Queued, Processing, Complete, Error
- domain_id nullable: NO (nullable=False) ⚠️ CRITICAL
- Unique constraint: url (unique=True)
```

**VERIFIED CONSTRAINTS:**
```sql
-- From SYSTEM_MAP.md Critical Constraints section:
domain_id = Column(PGUUID, ForeignKey("domains.id"), nullable=False, index=True)
```

**WF5 Scheduler Compatibility:** ✅ Compatible (filters on sitemap_import_status, not domain_id)

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
from src.models.sitemap import (
    SitemapFile,
    SitemapImportCurationStatusEnum,
    SitemapImportProcessStatusEnum
)
from src.models.domain import Domain, SitemapCurationStatusEnum
from src.models.tenant import DEFAULT_TENANT_ID
from src.schemas.sitemaps_direct_submission_schemas import (
    DirectSitemapSubmissionRequest,
    DirectSitemapSubmissionResponse
)
from urllib.parse import urlparse

router = APIRouter(
    prefix="/api/v3/sitemaps",
    tags=["V3 - Sitemaps Direct Submission"]
)


def extract_domain_from_sitemap_url(url: str) -> str:
    """
    Extract domain name from sitemap URL.

    Examples:
        'https://www.example.com/sitemap.xml' -> 'example.com'
        'https://example.com/sitemaps/index.xml' -> 'example.com'
        'http://subdomain.site.org/sitemap.xml' -> 'subdomain.site.org'
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    # Remove 'www.' prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


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

    **Domain Handling:**
    - Extracts domain from sitemap URL (e.g., 'example.com' from 'https://example.com/sitemap.xml')
    - Creates domain record if doesn't exist
    - Links sitemap to domain (maintains referential integrity)

    **Constraints:**
    - Maximum 50 sitemap URLs per request
    - URLs must end with .xml or contain 'sitemap'
    - Duplicate URLs are rejected with 409 Conflict
    - Requires authentication

    **Status Initialization:**
    - `deep_scrape_curation_status`: "Selected" if auto_import, else "New"
    - `sitemap_import_status`: "Queued" if auto_import, else NULL
    - `domain_id`: Auto-created via get-or-create pattern (REQUIRED)
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

            # CRITICAL: Get or create domain (domain_id has nullable=False constraint)
            domain_name = extract_domain_from_sitemap_url(url_str)
            domain_result = await session.execute(
                select(Domain).where(Domain.domain == domain_name)
            )
            domain = domain_result.scalar_one_or_none()

            if not domain:
                # Auto-create domain for direct submission
                domain = Domain(
                    id=uuid.uuid4(),
                    domain=domain_name,
                    tenant_id=uuid.UUID(DEFAULT_TENANT_ID),  # REQUIRED (nullable=False)
                    local_business_id=None,  # NULL OK (nullable=True per SYSTEM_MAP.md)
                    sitemap_curation_status=SitemapCurationStatusEnum.New,
                    sitemap_analysis_status=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(domain)
                await session.flush()  # Get domain.id before using it

            # Create sitemap file with proper status initialization
            sitemap_file = SitemapFile(
                id=uuid.uuid4(),
                url=url_str,

                # Foreign key
                domain_id=domain.id,  # REQUIRED (nullable=False per SYSTEM_MAP.md)

                # DUAL-STATUS PATTERN (CRITICAL)
                deep_scrape_curation_status=(
                    SitemapImportCurationStatusEnum.Selected if request.auto_import
                    else SitemapImportCurationStatusEnum.New
                ),
                sitemap_import_status=(
                    SitemapImportProcessStatusEnum.Queued if request.auto_import
                    else None
                ),

                # Required fields
                sitemap_type="STANDARD",  # REQUIRED (nullable=False) - default for direct submissions

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
SELECT sf.id, sf.url, sf.deep_scrape_curation_status, sf.sitemap_import_status, sf.domain_id, d.domain
FROM sitemap_files sf
LEFT JOIN domains d ON sf.domain_id = d.id
WHERE sf.url = 'https://example.com/sitemap.xml';

-- Expected:
-- deep_scrape_curation_status = 'New'
-- sitemap_import_status = NULL
-- domain_id = <valid UUID>
-- domain = 'example.com' (auto-created)

-- Verify domain was auto-created
SELECT id, domain, local_business_id, sitemap_curation_status
FROM domains
WHERE domain = 'example.com';

-- Expected:
-- local_business_id = NULL (direct submission domain)
-- sitemap_curation_status = 'New'
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
```python
# Comment out:
# app.include_router(sitemaps_direct_router)
```

2. **Delete created sitemaps and auto-created domains**
```sql
-- Delete sitemap files from direct submissions
DELETE FROM sitemap_files
WHERE created_at > '2025-11-17 00:00:00'
AND user_id = '<test_user_id>';  -- Use specific user ID for safety

-- Optionally delete auto-created test domains
-- (Only if they have no other sitemaps/pages and were created during testing)
DELETE FROM domains
WHERE local_business_id IS NULL
AND created_at > '2025-11-17 00:00:00'
AND NOT EXISTS (SELECT 1 FROM sitemap_files WHERE sitemap_files.domain_id = domains.id)
AND NOT EXISTS (SELECT 1 FROM pages WHERE pages.domain_id = domains.id);
```

3. **Remove new files**
```bash
rm src/routers/v3/sitemaps_direct_submission_router.py
rm src/schemas/sitemaps_direct_submission_schemas.py
```

4. **Restart application**
```bash
docker compose restart app
```

**Time to rollback:** < 5 minutes

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

## ✅ All Questions Resolved

1. **What is the exact SitemapFile model structure?**
   - ✅ Verified: SitemapFile class with fields documented in Phase 0

2. **What are the exact ENUM definitions and values?**
   - ✅ Verified: SitemapImportCurationStatusEnum and SitemapImportProcessStatusEnum documented above

3. **Is NULL domain_id allowed?**
   - ✅ NO - domain_id has nullable=False constraint, get-or-create pattern implemented

4. **Should we auto-create domains if user provides domain in sitemap URL?**
   - ✅ YES - Implemented via get-or-create pattern to satisfy nullable=False constraint

---

## Related Work

- **ADR-003:** Dual-Status Workflow Pattern
- **ADR-005:** ENUM Catastrophe (verify ENUMs first!)
- **EXTENSIBILITY_PATTERNS.md:** Original design
- **WO-009:** Direct Page Submission (similar pattern)
- **WO-010:** Direct Domain Submission (similar pattern)

---

**Status:** ✅ READY FOR IMPLEMENTATION
**Blocked By:** None (Phase 0 verification complete)
**Blocking:** None
