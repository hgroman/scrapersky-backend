# WO-010: Direct Domain Submission Endpoint
**Created:** November 17, 2025
**Priority:** MEDIUM
**Estimated Effort:** 2-3 hours
**Risk Level:** LOW (early in workflow chain)

---

## Objective

Implement `/api/v3/domains/direct-submit` endpoint to allow users to submit domain URLs directly, bypassing WF1→WF2 (Google Maps → Deep Scan).

**Entry Point:** WF3 (Domain Extraction)
**Bypass:** WF1 (Google Maps Search), WF2 (Place Details)
**Benefit:** Enables domain-based scraping without Google Maps API dependency

---

## Background

**Current Flow:**
```
WF1 (Google Maps Search) → WF2 (Deep Scan) → WF3 (Domain Extraction) →
WF4 (Sitemap Discovery) → WF5 (Sitemap Import) → WF7 (Page Curation)
```

**New Flow:**
```
Direct API Call → Domain Record Created → WF4 (Sitemap Discovery) → ...
```

**Use Case:** User has list of company domains to scrape (e.g., competitor list, industry directory) without needing Google Maps data.

---

## Technical Analysis

### Layer 1: Model Analysis (Domain)

**File:** `src/models/domain.py`

**Critical Fields:**
```python
class Domain(Base):
    __tablename__ = "domains"

    # Primary Key
    id: UUID (required)

    # Core Fields
    domain: String (required, unique)
    local_business_id: UUID (optional - NULL for direct submission)

    # DUAL-STATUS PATTERN (CRITICAL)
    sitemap_curation_status: SitemapCurationStatusEnum (ENUM)
    sitemap_analysis_status: SitemapAnalysisStatusEnum (ENUM)

    # Metadata (optional)
    site_title: String (nullable)
    site_description: String (nullable)

    # Timestamps
    created_at: DateTime (required)
    updated_at: DateTime (required)
    user_id: UUID (nullable)
```

### ENUM Dependencies (CRITICAL - ADR-005)

**SitemapCurationStatusEnum (Layer 1):**
```python
# File: src/models/domain.py
class SitemapCurationStatusEnum(str, Enum):
    New = "New"
    Selected = "Selected"
    Rejected = "Rejected"
```

**SitemapAnalysisStatusEnum (Layer 1):**
```python
# File: src/models/domain.py
class SitemapAnalysisStatusEnum(str, Enum):
    queued = "queued"
    submitted = "submitted"
    failed = "failed"
```

**⚠️ ENUM NAMING INCONSISTENCY:**
- Curation status: PascalCase values ("New", "Selected")
- Analysis status: lowercase values ("queued", "submitted")

**This is EXISTING CODE - do NOT change to maintain backward compatibility**

**Schema Layer (Layer 2):**
```python
# File: src/schemas/domain_schemas.py (if exists)
# Must import from Layer 1
from src.models.domain import SitemapCurationStatusEnum, SitemapAnalysisStatusEnum
```

---

## Field Dependencies & Constraints

### Required Fields (Direct Submission)
1. ✅ `id` - UUID generation
2. ✅ `domain` - User-provided domain (must validate format)
3. ✅ `sitemap_curation_status` - Set based on `auto_queue` flag
4. ✅ `sitemap_analysis_status` - Set based on `auto_queue` flag
5. ✅ `created_at` - `datetime.utcnow()`
6. ✅ `user_id` - From JWT token

### Optional Fields (Can be NULL)
1. ⚠️ `local_business_id` - NULL for direct submission (not from WF2 flow)
2. ✅ `site_title` - NULL initially (no metadata extraction on submission)
3. ✅ `site_description` - NULL initially

### Domain Validation Requirements
```python
# Must validate domain format
import re
from urllib.parse import urlparse

def validate_domain(domain_str: str) -> str:
    """
    Validate and normalize domain.

    Accepts:
    - "example.com"
    - "www.example.com"
    - "https://example.com"
    - "https://www.example.com/path" (extracts domain)

    Returns: Normalized domain (e.g., "example.com")
    """
    # Remove protocol if present
    if "://" in domain_str:
        parsed = urlparse(domain_str)
        domain_str = parsed.netloc or parsed.path

    # Remove www. prefix
    domain_str = domain_str.replace("www.", "")

    # Remove trailing slashes
    domain_str = domain_str.rstrip("/")

    # Validate format
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    if not re.match(domain_pattern, domain_str):
        raise ValueError(f"Invalid domain format: {domain_str}")

    return domain_str.lower()
```

### Constraints to Verify
```sql
-- Check unique constraint
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'domains'::regclass;

-- Expected: UNIQUE constraint on domain
```

---

## Risk Assessment

### LOW RISK: Existing Workflow Interference

**Risk:** Direct submission domains might conflict with WF3-extracted domains

**Scenarios:**
1. User submits "example.com" directly
2. Later, WF3 extracts same domain from Google Maps business
3. **Potential Conflict:** Duplicate domain or constraint violation

**Mitigation:**
```python
# Check if domain already exists
existing_domain = await session.execute(
    select(Domain).where(Domain.domain == normalized_domain)
)
if existing_domain.scalar_one_or_none():
    raise HTTPException(409, "Domain already exists")
```

### LOW RISK: Missing local_business_id

**Risk:** Domains without `local_business_id` might break business-based queries

**Impact:** Minimal - most queries are domain-centric, not business-centric

**Verification:**
```bash
# Find queries that assume local_business_id exists
grep -r "local_business_id IS NOT NULL" src/
grep -r "JOIN local_business" src/services/
```

**Mitigation:** Use LEFT JOIN in queries (likely already done)

### VERY LOW RISK: Scheduler Compatibility

**Risk:** WF4 scheduler might not handle NULL local_business_id

**Likelihood:** Very low - scheduler filters on `sitemap_analysis_status`, not `local_business_id`

**Verification:**
```bash
# Check scheduler query
cat src/services/domain_sitemap_submission_scheduler.py | grep -A 10 "WHERE"
```

---

## Implementation Plan

### Phase 1: Pre-Implementation Verification (15 min)

**Task 1.1: Verify Database Constraints**
```sql
-- Check unique constraints
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'domains'::regclass;

-- Check NULL handling
SELECT COUNT(*) FROM domains WHERE local_business_id IS NULL;
```

**Expected Results:**
- Unique constraint on `domain` only
- Some domains may already have NULL `local_business_id`

**Task 1.2: Verify WF4 Scheduler Query**
```bash
# Ensure scheduler doesn't filter on local_business_id
grep -A 20 "def " src/services/domain_sitemap_submission_scheduler.py
```

**Expected:** Filters on `sitemap_analysis_status = 'queued'`, not local_business_id

**✅ CHECKPOINT:** All verifications pass before proceeding

---

### Phase 2: Layer 2 - Schema Creation (20 min)

**File:** `src/schemas/domains_direct_submission_schemas.py` (NEW)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID
import re
from urllib.parse import urlparse


class DirectDomainSubmissionRequest(BaseModel):
    """Request schema for direct domain submission."""

    domains: list[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="List of domain names or URLs to submit"
    )

    auto_queue: bool = Field(
        default=False,
        description="If True, auto-queue for WF4 sitemap discovery"
    )

    @validator('domains', each_item=True)
    def validate_domain_format(cls, domain_str: str) -> str:
        """Validate and normalize domain."""
        # Remove protocol if present
        if "://" in domain_str:
            parsed = urlparse(domain_str)
            domain_str = parsed.netloc or parsed.path

        # Remove www. prefix
        domain_str = domain_str.replace("www.", "")

        # Remove trailing slashes and paths
        domain_str = domain_str.split("/")[0].rstrip("/")

        # Validate format
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, domain_str):
            raise ValueError(f"Invalid domain format: {domain_str}")

        return domain_str.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "domains": [
                    "example.com",
                    "https://www.another-example.org",
                    "third-example.net"
                ],
                "auto_queue": True
            }
        }


class DirectDomainSubmissionResponse(BaseModel):
    """Response schema for direct domain submission."""

    submitted_count: int
    domain_ids: list[UUID]
    auto_queued: bool
    normalized_domains: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "submitted_count": 3,
                "domain_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001",
                    "123e4567-e89b-12d3-a456-426614174002"
                ],
                "auto_queued": True,
                "normalized_domains": [
                    "example.com",
                    "another-example.org",
                    "third-example.net"
                ]
            }
        }
```

**✅ CHECKPOINT:** Schema validation tests pass

---

### Phase 3: Layer 3 - Router Implementation (40 min)

**File:** `src/routers/v3/domains_direct_submission_router.py` (NEW)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from src.db.session import get_db_session
from src.auth.dependencies import get_current_user
from src.models.domain import Domain, SitemapCurationStatusEnum, SitemapAnalysisStatusEnum
from src.schemas.domains_direct_submission_schemas import (
    DirectDomainSubmissionRequest,
    DirectDomainSubmissionResponse
)

router = APIRouter(
    prefix="/api/v3/domains",
    tags=["V3 - Domains Direct Submission"]
)


@router.post("/direct-submit", response_model=DirectDomainSubmissionResponse)
async def submit_domains_directly(
    request: DirectDomainSubmissionRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit domain names directly for sitemap discovery, bypassing WF1-WF2.

    **Use Case:**
    - User has list of domains to analyze
    - Bypass Google Maps search and place details
    - Direct entry to WF4 (Sitemap Discovery)

    **Auto-Queue Behavior:**
    - `auto_queue=True`: Sets status to Selected + queued (WF4 picks up immediately)
    - `auto_queue=False`: Sets status to New + NULL (requires manual curation)

    **Domain Format:**
    Accepts any of these formats (all normalized to "example.com"):
    - "example.com"
    - "www.example.com"
    - "https://example.com"
    - "https://www.example.com/path"

    **Constraints:**
    - Maximum 100 domains per request
    - Duplicate domains are rejected with 409 Conflict
    - Requires authentication

    **Status Initialization:**
    - `sitemap_curation_status`: "Selected" if auto_queue, else "New"
    - `sitemap_analysis_status`: "queued" if auto_queue, else NULL
    - `local_business_id`: NULL (not from Google Maps workflow)
    """
    domain_ids = []
    normalized_domains = []

    # Domains are already validated and normalized by pydantic
    normalized_domains = request.domains

    async with session.begin():
        for domain_str in normalized_domains:

            # Check for duplicates
            existing_check = await session.execute(
                select(Domain).where(Domain.domain == domain_str)
            )
            existing_domain = existing_check.scalar_one_or_none()

            if existing_domain:
                raise HTTPException(
                    status_code=409,
                    detail=f"Domain already exists: {domain_str} (ID: {existing_domain.id})"
                )

            # Create domain with proper status initialization
            domain = Domain(
                id=uuid.uuid4(),
                domain=domain_str,

                # NULL foreign key (not from WF2 flow)
                local_business_id=None,

                # DUAL-STATUS PATTERN (CRITICAL)
                # Note: ENUM values have inconsistent casing (this is existing code behavior)
                sitemap_curation_status=(
                    SitemapCurationStatusEnum.Selected if request.auto_queue
                    else SitemapCurationStatusEnum.New
                ),
                sitemap_analysis_status=(
                    SitemapAnalysisStatusEnum.queued if request.auto_queue
                    else None
                ),

                # Metadata (NULL for direct submission)
                site_title=None,
                site_description=None,

                # Timestamps
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                user_id=current_user.get("user_id"),
            )

            session.add(domain)
            domain_ids.append(domain.id)

    return DirectDomainSubmissionResponse(
        submitted_count=len(domain_ids),
        domain_ids=domain_ids,
        auto_queued=request.auto_queue,
        normalized_domains=normalized_domains
    )
```

**✅ CHECKPOINT:** Router passes unit tests

---

### Phase 4: Integration with main.py (5 min)

**File:** `src/main.py`

```python
# Add import
from src.routers.v3.domains_direct_submission_router import router as domains_direct_router

# Add router inclusion
app.include_router(domains_direct_router)  # No prefix needed
```

**✅ CHECKPOINT:** Application starts without errors

---

### Phase 5: Testing (30 min)

**Test 1: Basic Submission (auto_queue=False)**
```bash
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": ["example.com"],
    "auto_queue": false
  }'
```

**Expected Result:**
```json
{
  "submitted_count": 1,
  "domain_ids": ["uuid-here"],
  "auto_queued": false,
  "normalized_domains": ["example.com"]
}
```

**Verification:**
```sql
SELECT id, domain, sitemap_curation_status, sitemap_analysis_status, local_business_id
FROM domains
WHERE domain = 'example.com';

-- Expected:
-- sitemap_curation_status = 'New'
-- sitemap_analysis_status = NULL
-- local_business_id = NULL
```

---

**Test 2: Auto-Queue Submission (auto_queue=True)**
```bash
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": ["test-domain.com"],
    "auto_queue": true
  }'
```

**Verification:**
```sql
SELECT id, domain, sitemap_curation_status, sitemap_analysis_status
FROM domains
WHERE domain = 'test-domain.com';

-- Expected:
-- sitemap_curation_status = 'Selected'
-- sitemap_analysis_status = 'queued'
```

**Wait 1 minute (WF4 scheduler interval), then check:**
```sql
SELECT d.domain, d.sitemap_analysis_status, COUNT(sf.id) as sitemap_count
FROM domains d
LEFT JOIN sitemap_files sf ON sf.domain_id = d.id
WHERE d.domain = 'test-domain.com'
GROUP BY d.domain, d.sitemap_analysis_status;

-- Expected:
-- sitemap_analysis_status = 'submitted'
-- sitemap_count > 0 (if domain has sitemaps)
```

**✅ CHECKPOINT:** WF4 scheduler picks up and processes auto-queued domain

---

**Test 3: Domain Normalization**
```bash
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": [
      "example.com",
      "https://www.example.org",
      "HTTP://UPPERCASE.COM/path/to/page"
    ],
    "auto_queue": false
  }'
```

**Expected Result:**
```json
{
  "submitted_count": 3,
  "normalized_domains": [
    "example.com",
    "example.org",
    "uppercase.com"
  ]
}
```

---

**Test 4: Duplicate Detection**
```bash
# Submit same domain twice
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": ["example.com"],
    "auto_queue": false
  }'
```

**Expected Result:**
```json
{
  "detail": "Domain already exists: example.com (ID: ...)"
}
```

**Status Code:** 409 Conflict

---

**Test 5: Invalid Domain Format**
```bash
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": ["invalid domain with spaces"],
    "auto_queue": false
  }'
```

**Expected Result:**
```json
{
  "detail": [
    {
      "loc": ["body", "domains", 0],
      "msg": "Invalid domain format: invalid domain with spaces",
      "type": "value_error"
    }
  ]
}
```

**Status Code:** 422 Unprocessable Entity

**✅ CHECKPOINT:** All tests pass

---

## Rollback Plan

**If implementation fails:**

1. **Remove router from main.py**
```python
# Comment out:
# app.include_router(domains_direct_router)
```

2. **Delete created domains**
```sql
DELETE FROM domains
WHERE local_business_id IS NULL
AND created_at > '2025-11-17 00:00:00';
```

3. **Remove new files**
```bash
rm src/routers/v3/domains_direct_submission_router.py
rm src/schemas/domains_direct_submission_schemas.py
```

4. **Restart application**

**Time to rollback:** < 5 minutes

---

## Success Criteria

- ✅ Direct domain submission creates valid Domain records
- ✅ Domain normalization works correctly (removes www, protocol, paths)
- ✅ Auto-queue flag properly sets dual-status fields
- ✅ WF4 scheduler picks up auto-queued domains
- ✅ Duplicate domains are rejected with 409
- ✅ Invalid domain formats are rejected with 422
- ✅ Existing /api/v3/domains queries work unchanged
- ✅ No errors in application logs

---

## Documentation Updates

**After successful implementation:**

1. Update `Documentation/Context_Reconstruction/EXTENSIBILITY_PATTERNS.md`
   - Mark Pattern 2 as "✅ IMPLEMENTED"

2. Update `Documentation/Workflows/README.md`
   - Add note about direct domain submission option

---

## Related Work

- **ADR-003:** Dual-Status Workflow Pattern
- **ADR-004:** Transaction Boundaries
- **ADR-005:** ENUM Catastrophe (note inconsistent ENUM casing)
- **EXTENSIBILITY_PATTERNS.md:** Original design
- **WO-009:** Direct Page Submission (similar pattern)

---

**Status:** READY FOR REVIEW
**Depends On:** None
**Blocks:** None
