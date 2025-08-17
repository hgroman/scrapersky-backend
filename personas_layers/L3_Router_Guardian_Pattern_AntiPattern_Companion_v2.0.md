# L3 Router Guardian Pattern-AntiPattern Companion v2.0

## Instant Pattern Recognition & Violation Detection Guide - Enhanced Edition

**Version:** 2.0
**Purpose:** Enable instant router pattern recognition and violation detection
**Cardinal Rule:** Routers own transactions, services accept sessions!
**Usage:** Load ONLY this document for complete L3 router review authority
**Verification Requirement:** All routers handle HTTP only, delegate logic to services

---

## QUICK REFERENCE SECTION

### 🎯 INSTANT PATTERN CHECKLIST

- [ ] Router owns transaction boundaries (begin/commit/rollback)
- [ ] All business logic delegated to Layer 4 services
- [ ] Authentication dependency on ALL data-modifying endpoints
- [ ] API version prefix `/api/v3/` configured correctly
- [ ] Pydantic schemas from Layer 2, never local definitions
- [ ] No direct database queries in routers
- [ ] Proper error handling with HTTPException

### 🔴 INSTANT REJECTION TRIGGERS

1. **Missing authentication** → REJECT (Security violation)
2. **Business logic in router** → REJECT (Pattern #2 violation)
3. **session.commit() in router** → REJECT (Cardinal Rule violation)
4. **Local Pydantic models** → REJECT (Pattern #4 violation)
5. **Direct SQL queries** → REJECT (Pattern #5 violation)
6. **Wrong API version** → REJECT (Pattern #6 violation)
7. **Dict response types** → REJECT (Pattern #7 violation)

### ✅ APPROVAL REQUIREMENTS

Before approving ANY router implementation:

1. Verify authentication on all modifying endpoints
2. Confirm transaction ownership pattern
3. Check all logic delegated to services
4. Verify Layer 2 schemas imported
5. Confirm `/api/v3/` prefix present
6. Ensure proper error handling

---

## PATTERN #1: Authentication Requirements

### ✅ CORRECT PATTERN:

```python
from src.auth.dependencies import get_current_active_user

@router.put("/pages/curation-status")
async def update_page_curation_status(
    request: PageCurationUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: Dict = Depends(get_current_active_user)  # REQUIRED!
):
    """All data-modifying endpoints need authentication."""
    # User is authenticated before any processing
    result = await page_service.update_status(
        request, session, user_id=current_user["id"]
    )
    return result
```

**Why:** Prevents unauthorized data modifications
**Citation:** Layer 3 Blueprint Security Requirements

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Commented Out Authentication**

```python
# page_curation.py - CRITICAL SECURITY VIOLATION!
@router.put("/pages/curation-status")
async def update_page_curation_status_batch(
    session: AsyncSession = Depends(get_db_session),
    request_body: PageCurationUpdateRequest = Body(...),
    # current_user: Dict = Depends(get_current_active_user), # COMMENTED OUT!
):
    # Allows batch updates without authentication!
```

**Detection:** Commented auth dependencies
**From Audit:** page_curation.py, email_scanner.py
**Impact:** Unauthorized database modifications possible

**Violation B: Dev Mode Bypass**

```python
# modernized_sitemap.py - VIOLATION!
def is_development_mode() -> bool:
    if os.getenv("SCRAPER_SKY_DEV_MODE") == "true":
        logger.warning("⚠️ ALL AUTH CHECKS BYPASSED ⚠️")
        return True  # Security completely disabled!
```

**Detection:** Environment-based auth bypass
**From Audit:** modernized_sitemap.py bypasses all checks
**Impact:** Production security vulnerabilities

---

## PATTERN #2: Transaction Ownership (CARDINAL RULE)

### ✅ CORRECT PATTERN:

```python
@router.post("/domains")
async def create_domain(
    request: DomainCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    """Router owns the transaction boundaries."""
    try:
        async with session.begin():  # Router starts transaction
            # Service accepts session, doesn't manage transaction
            domain = await domain_service.create_domain(
                request, session  # Pass session to service
            )
        # Transaction auto-commits on context exit
        return domain
    except Exception as e:
        # Transaction auto-rollbacks on exception
        raise HTTPException(status_code=400, detail=str(e))
```

**Why:** Clear transaction boundaries, consistent error handling
**Citation:** Layer 3 Blueprint Cardinal Rule, Constitution Article III.4

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Manual Commit/Rollback**

```python
# domains.py - VIOLATION!
@router.put("/sitemap-curation/status")
async def update_status_batch(...):
    try:
        for domain in domains_to_update:
            domain.sitemap_curation_status = status

        await session.commit()  # WRONG! Router shouldn't commit
    except Exception as e:
        await session.rollback()  # WRONG! Router shouldn't rollback
        raise
```

**Detection:** `session.commit()` or `session.rollback()` in routers
**From Audit:** domains.py manages transactions directly
**Impact:** Inconsistent transaction handling

**Violation B: Service Creating Transaction**

```python
# VIOLATION: Service shouldn't own transaction
# modernized_sitemap.py calling service
async def scan_domain(...):
    async with session.begin():  # Router owns this
        await job_service.create(session, job_data)
        # But service might also try to manage transaction
```

**Detection:** Nested transaction contexts
**From Audit:** Confusion about transaction ownership
**Impact:** Nested transaction errors

---

## PATTERN #3: Business Logic Delegation

### ✅ CORRECT PATTERN:

```python
@router.get("/domains", response_model=PaginatedDomainResponse)
async def list_domains(
    filters: DomainFilters = Depends(),
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Router handles HTTP, delegates logic to service."""
    # Simple delegation to service
    result = await domain_service.list_domains(
        filters, pagination, session
    )
    return result  # Service returns Pydantic model
```

**Why:** Separation of concerns, testable business logic
**Citation:** Layer 3 Blueprint Pattern B

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Complex Logic in Router**

```python
# domains.py - VIOLATION!
@router.get("", response_model=PaginatedDomainResponse)
async def list_domains(...):
    # ALL THIS SHOULD BE IN SERVICE!
    base_query = select(Domain)

    filters = []
    if sitemap_curation_status:
        filters.append(Domain.sitemap_curation_status == status)
    if domain_filter:
        filters.append(Domain.domain.ilike(f"%{domain_filter}%"))

    # Pagination logic in router
    count_query = select(func.count(Domain.id))
    total = await session.execute(count_query).scalar_one()

    # Sorting logic in router
    query = base_query.order_by(sort_direction(sort_column))
    query = query.offset((page - 1) * size).limit(size)

    results = await session.execute(query)
```

**Detection:** Query building, filtering, pagination in routers
**From Audit:** domains.py has extensive business logic
**Impact:** Untestable logic, bloated routers

---

## PATTERN #4: Layer 2 Schema Usage

### ✅ CORRECT PATTERN:

```python
# Import schemas from Layer 2
from src.schemas.page_curation import (
    PageCurationRequest,
    PageCurationResponse,
    PaginatedPageResponse
)

@router.get("/pages", response_model=PaginatedPageResponse)
async def list_pages(...):
    """Uses Layer 2 schemas for type safety."""
    return await page_service.list_pages(...)
```

**Why:** Single source of truth for schemas
**Citation:** Layer 2/3 separation requirements

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Local Schema Definitions**

```python
# places_staging.py - VIOLATION!
# Defining schemas in router file
class PaginatedPlaceStagingResponse(BaseModel):
    items: List[PlaceStagingRecord]
    total: int
    page: int

class QueueDeepScanRequest(BaseModel):
    place_ids: List[UUID]
    priority: Optional[str] = "normal"
# Should be in src/schemas/places_staging.py!
```

**Detection:** `class.*BaseModel` in router files
**From Audit:** places_staging.py, google_maps_api.py
**Impact:** Duplicate schemas, inconsistent definitions

**Violation B: Inline Schema Creation**

```python
# google_maps_api.py - VIOLATION!
class PlacesSearchRequest(BaseModel):  # In router!
    query: str
    location: str
```

**Detection:** BaseModel classes in routers
**From Audit:** Multiple routers define local schemas
**Impact:** Cannot reuse schemas

---

## PATTERN #5: No Direct Database Access

### ✅ CORRECT PATTERN:

```python
@router.get("/places/staging")
async def list_staged_places(
    filters: PlaceFilters = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Router delegates ALL database operations to service."""
    # No SQL here, service handles it
    places = await place_service.list_staged_places(
        filters, session
    )
    return places
```

**Why:** Database logic belongs in services
**Citation:** Layer 3 Blueprint - no direct DB access

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Raw SQL in Router**

```python
# places_staging.py - VIOLATION!
@router.get("/places/staging")
async def list_all_staged_places(...):
    # RAW SQL IN ROUTER!
    sql_query = text("""
        SELECT p.*, ps.discovery_job_id
        FROM places p
        INNER JOIN place_search ps ON p.place_search_id = ps.id
        WHERE p.status = :status
        ORDER BY p.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await session.execute(sql_query, {
        "status": "staging",
        "limit": size,
        "offset": (page - 1) * size
    })
```

**Detection:** `text("""SELECT` or `session.execute` in routers
**From Audit:** places_staging.py has raw SQL
**Impact:** SQL injection risk, untestable queries

---

## PATTERN #6: API Versioning & Prefixes

### ✅ CORRECT PATTERN:

```python
# Correct router configuration
router = APIRouter(
    prefix="/api/v3/domains",  # Full versioned prefix
    tags=["Domains"],          # For OpenAPI docs
    dependencies=[Depends(get_current_active_user)]  # Global auth
)

# Or if prefix in main.py
router = APIRouter(tags=["Domains"])  # main.py adds /api/v3
```

**Why:** Consistent API versioning, clear documentation
**Citation:** Layer 3 Blueprint API Standards

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing Prefix & Tags**

```python
# email_scanner.py - VIOLATION!
router = APIRouter()  # No prefix, no tags!
# Should be:
# router = APIRouter(
#     prefix="/api/v3/email-scanner",
#     tags=["Email Scanner"]
# )
```

**Detection:** `APIRouter()` without arguments
**From Audit:** Multiple routers missing configuration
**Impact:** Inconsistent API paths, poor documentation

**Violation B: Wrong Version**

```python
# VIOLATION: Using old version
router = APIRouter(prefix="/api/v2/domains")  # v2 is deprecated!
# Should be /api/v3/
```

**Detection:** `/api/v2/` in router prefixes
**From Audit:** Some routers still use v2
**Impact:** API version confusion

---

## PATTERN #7: Typed Response Models

### ✅ CORRECT PATTERN:

```python
from src.schemas.domains import (
    DomainUpdateResponse,
    BatchUpdateResponse
)

@router.put("/domains/batch", response_model=BatchUpdateResponse)
async def update_domains_batch(...) -> BatchUpdateResponse:
    """Always use specific Pydantic response models."""
    result = await domain_service.batch_update(...)
    return BatchUpdateResponse(
        updated_count=result.updated,
        failed_count=result.failed
    )
```

**Why:** Type safety, automatic validation, clear API docs
**Citation:** Layer 3 Blueprint Response Requirements

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Generic Dict Responses**

```python
# Multiple routers - VIOLATION!
@router.put("/status", response_model=Dict[str, int])  # Too generic!
@router.post("/search", response_model=Dict)  # No type info!
@router.post("/update", response_model=Dict)  # Unclear structure!

# Should use specific models:
@router.put("/status", response_model=StatusUpdateResponse)
```

**Detection:** `response_model=Dict`
**From Audit:** domains.py, google_maps_api.py, others
**Impact:** No type validation, unclear API contracts

---

## PATTERN #8: Service Internal Access

### ✅ CORRECT PATTERN:

```python
# Import service properly
from src.services.sitemap_service import sitemap_service

@router.post("/scan")
async def scan_domain(
    request: ScanRequest,
    session: AsyncSession = Depends(get_session)
):
    """Use service public methods only."""
    # Call public service method
    result = await sitemap_service.scan_domain(request, session)
    return result
```

**Why:** Encapsulation, maintainable interfaces
**Citation:** Object-oriented design principles

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Direct Internal Access**

```python
# modernized_sitemap.py - VIOLATION!
from ..services.sitemap.processing_service import sitemap_processing_service

@router.post("/scan")
async def scan_domain(...):
    # DIRECTLY MANIPULATING SERVICE INTERNALS!
    sitemap_processing_service._job_statuses[job_id] = {
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
```

**Detection:** Access to `_private` attributes
**From Audit:** modernized_sitemap.py violates encapsulation
**Impact:** Breaks when service internals change

---

## VERIFICATION REQUIREMENTS

## PATTERN #9: Dual‑Status Trigger Mapping (External → Internal)

### ✅ CORRECT PATTERN:

```python
# External label "Selected" is normalized upstream; router triggers on internal Queued
if request.status == PageCurationStatus.Queued:
    page.page_processing_status = PageProcessingStatus.Queued
    page.page_processing_error = None  # clear errors

# Optional normalization (adapter/bridge) — not in router:
# request.status = normalize_selected_to_queued(request.status)
```

**Why:** Routers should act on internal enums only. Any UX term like "Selected" must be mapped upstream (validator/adapter) to `Queued` before Layer 3.
**Citation:** WF7 Remediation Debrief + Compliance Workflow

### ❌ ANTI-PATTERN VIOLATIONS:

```python
# Mixing external term in router logic (breaks on Enum mismatch)
if request.status == PageCurationStatus.Selected:  # WRONG: not a Page enum value
    page.page_processing_status = PageProcessingStatus.Queued
```

### Detection:

```bash
# Find invalid Selected checks in routers
grep -n "PageCurationStatus\.Selected" src/routers/**/*.py
```

### Impact:

- 500s at runtime due to enum attribute error
- Breaks dual‑status trigger and blocks scheduler flow

### Router Review Protocol

```bash
# Check for authentication dependencies
grep -n "get_current_active_user" src/routers/*.py

# Find transaction management in routers
grep -n "session.commit\|session.rollback" src/routers/*.py

# Look for business logic in routers
grep -n "select(\|query = \|filter(" src/routers/*.py

# Find local schema definitions
grep -n "class.*BaseModel" src/routers/*.py

# Check API versioning
grep -n "APIRouter(" src/routers/*.py

# Find Dict response types
grep -n "response_model=Dict" src/routers/*.py
```

### What WF7 Did Wrong:

```python
# 1. No authentication on endpoints
# 2. Complex logic directly in router
# 3. Local schema definitions
# 4. Raw SQL queries in router
# 5. Wrong API version (v2 instead of v3)
```

### What WF7 Should Have Done:

```python
# 1. Add Depends(get_current_active_user)
# 2. Delegate all logic to services
# 3. Import schemas from Layer 2
# 4. Use service methods for DB access
# 5. Use /api/v3/ prefix consistently
```

---

## GUARDIAN CITATION FORMAT

When reviewing Layer 3 routers, use this format:

```markdown
L3 ROUTER GUARDIAN ANALYSIS:
❌ VIOLATION of Pattern #1: Missing authentication (Line 45)
❌ VIOLATION of Pattern #2: session.commit() in router (Line 67)
❌ VIOLATION of Pattern #3: Complex business logic (Lines 80-120)
⚠️ WARNING on Pattern #6: Using /api/v2/ instead of /api/v3/

REQUIRED CORRECTIONS:

1. Add current_user dependency to all modifying endpoints
2. Remove transaction management, use async with session.begin()
3. Move query logic to DomainService
4. Update to /api/v3/ prefix

APPROVAL: DENIED - Security and Cardinal Rule violations
```

---

## REPLACES

- L3 Router Guardian Companion v1.0
- Full Layer 3 Routers Blueprint (350+ lines)
- 10 Layer 3 audit report chunks
- Router pattern guidelines
- Transaction management documentation

**With this single 495-line companion for instant pattern recognition!**

---

_"Routers route, services serve, transactions stay at the boundary."_
**- The L3 Router Guardian v2.0**
