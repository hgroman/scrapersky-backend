# L4 Service Guardian Pattern-AntiPattern Companion

## Instant Pattern Recognition & Violation Detection Guide

**Version:** 1.0
**Purpose:** Enable instant service pattern recognition and violation detection
**Cardinal Rule:** Services ACCEPT sessions, never create them!
**Usage:** Load ONLY this document for complete L4 service review authority
**Verification Requirement:** Pattern claims must be verified against actual codebase

---

## QUICK REFERENCE SECTION

### 🎯 INSTANT PATTERN CHECKLIST

- [ ] Service accepts `AsyncSession` as parameter, never creates sessions
- [ ] Service file named `{workflow_name}_service.py` or `{workflow_name}_scheduler.py`
- [ ] Business logic encapsulated in service, not in router
- [ ] Service returns data/None, router handles HTTP responses
- [ ] Scheduler uses `run_job_loop` pattern from Curation SDK
- [ ] All database operations use the passed session parameter

### 🔴 INSTANT REJECTION TRIGGERS

1. **Session creation in service** → REJECT (Cardinal Rule violation)
2. **Business logic in router** → REJECT (Pattern #2 violation)
3. **Missing service for workflow** → REJECT (Pattern #1 violation)
4. **Service handling HTTP responses** → REJECT (Pattern #3 violation)
5. **Direct transaction management** → REJECT (Pattern #4 violation)
6. **Tenant ID usage after removal** → REJECT (Constitutional violation)

### ✅ APPROVAL REQUIREMENTS

Before approving ANY service implementation:

1. Verify service accepts `AsyncSession` parameter
2. Confirm workflow naming convention followed
3. Check business logic properly encapsulated
4. Verify no HTTP concerns in service layer
5. Confirm scheduler uses SDK pattern if applicable
6. Ensure no tenant isolation code remains

---

## PATTERN #1: Service File Existence & Naming

### ✅ CORRECT PATTERN:

```python
# File: src/services/domain_curation_service.py
# For workflow WF4_Domain_Curation

# File: src/services/sitemap_curation_scheduler.py
# For workflow WF5_Sitemap_Curation scheduler component
```

**Why:** Consistent naming enables instant workflow identification
**Citation:** Layer 4 Blueprint Section 2.1, Constitutional naming convention

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing Service Entirely**

```python
# WF7 audit result:
# MISSING: src/services/page_curation_service.py
# MISSING: src/services/page_curation_scheduler.py
```

**Detection:** Check if service file exists for workflow
**From WF7:** Complete absence of Layer 4 components
**Impact:** Workflow lacks business logic encapsulation, architectural breakdown

**Violation B: Wrong Naming Convention**

```python
# File: src/services/sitemap_files_service.py  # WRONG!
# Should be: sitemap_curation_service.py

# File: src/services/sitemap_import_scheduler.py  # WRONG!
# Should be: sitemap_curation_scheduler.py
```

**Detection:** Service name doesn't match workflow name
**From WF5:** Inconsistent naming breaks workflow traceability
**Impact:** Confusion about service ownership and purpose

---

## PATTERN #2: Session Acceptance (CARDINAL RULE)

### ✅ CORRECT PATTERN:

```python
async def process_domain(
    domain_id: int,
    session: AsyncSession  # ACCEPT session as parameter
) -> Optional[DomainResult]:
    """Service accepts session, never creates."""
    domain = await session.get(Domain, domain_id)
    if domain:
        domain.status = "processed"
        # Use passed session for all operations
    return domain
```

**Why:** Services must accept sessions to maintain transaction boundaries
**Citation:** Layer 4 Blueprint Cardinal Rule, Constitution Article III.4

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Service Creating Session**

```python
# From places_deep_service.py:180
async def process_place(place_id: int):
    # VIOLATION: Service creating its own session!
    session = await get_session()
    if not session:
        logger.error("Failed to acquire database session.")
        return None
```

**Detection:** Any `get_session()`, `get_background_session()` in service
**From Audit:** places_deep_service.py violates cardinal rule
**Impact:** Breaks transaction control, creates nested transactions

**Violation B: Service Using Background Session**

```python
# From sitemap processing services
async def process_sitemap():
    # VIOLATION: Service creating background session
    async with get_background_session() as session:
        # Processing logic
```

**Detection:** `get_background_session()` anywhere in service
**From WF5:** Multiple sitemap services create sessions
**Impact:** Transaction boundaries become unmanageable

---

## PATTERN #3: Business Logic Encapsulation

### ✅ CORRECT PATTERN:

```python
# Service encapsulates complex business logic
async def list_domains_with_filters(
    session: AsyncSession,
    filters: DomainFilters,
    pagination: PaginationParams
) -> DomainListResult:
    """Complex listing logic belongs in service."""
    query = select(Domain)

    # Apply complex filters
    if filters.status:
        query = query.filter(Domain.status == filters.status)

    # Apply sorting logic
    if filters.sort_by:
        query = apply_sorting(query, filters.sort_by)

    # Execute and return data
    result = await session.execute(query)
    return DomainListResult(domains=result.scalars().all())
```

**Why:** Services own business logic, routers handle HTTP only
**Citation:** Layer 4 Blueprint Section 2.1.A

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Complex Logic in Router**

```python
# From domains.py router - VIOLATION!
ALLOWED_SORT_FIELDS = {
    "domain": Domain.domain,
    "created_at": Domain.created_at,
    # Complex mapping logic in router!
}

@router.get("/list")
async def list_domains(session: AsyncSession = Depends(get_session)):
    # VIOLATION: Complex business logic in router
    query = select(Domain)
    # Multiple filters, sorting, pagination logic
    # Should be in service layer!
```

**Detection:** Complex queries, business rules in router files
**From WF4:** list_domains endpoint exceeds Pattern B scope
**Impact:** Router becomes bloated, business logic scattered

---

## PATTERN #4: Return Types & HTTP Separation

### ✅ CORRECT PATTERN:

```python
# Service returns data or None, never HTTP responses
async def get_domain_details(
    domain_id: int,
    session: AsyncSession
) -> Optional[Domain]:  # Returns domain object or None
    """Service returns data, not HTTP responses."""
    return await session.get(Domain, domain_id)

# Router handles HTTP concerns
@router.get("/{domain_id}")
async def get_domain(
    domain_id: int,
    session: AsyncSession = Depends(get_session)
):
    domain = await domain_service.get_domain_details(domain_id, session)
    if not domain:
        raise HTTPException(status_code=404)  # HTTP in router only
    return domain
```

**Why:** Clean separation of concerns between layers
**Citation:** Layer 4 Blueprint Section 2.2

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Service Returning HTTP Responses**

```python
# VIOLATION: Service handling HTTP concerns
async def get_domain(domain_id: int, session: AsyncSession):
    domain = await session.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404)  # WRONG LAYER!
    return JSONResponse(content={"domain": domain})  # WRONG!
```

**Detection:** `HTTPException`, `JSONResponse` in service files
**From Audit:** Services mixing HTTP concerns
**Impact:** Layer responsibilities become confused

---

## PATTERN #5: Scheduler Implementation

### ✅ CORRECT PATTERN:

```python
# Using Curation SDK pattern
from src.sdk.curation_sdk import run_job_loop

async def process_domain_queue():
    """Scheduler using SDK pattern."""
    await run_job_loop(
        process_fn=process_single_domain,
        queue_query=select(Domain).filter(
            Domain.status == "pending"
        ),
        status_field="status",
        processing_value="processing",
        completed_value="completed",
        failed_value="failed"
    )
```

**Why:** Consistent scheduler pattern across all workflows
**Citation:** Constitution Article III.1 - Universal Background Pattern

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing Workflow Scheduler**

```python
# From WF4 audit:
# MISSING: src/services/domain_curation_scheduler.py
# domain_scheduler.py exists but doesn't process workflow queue!
```

**Detection:** No dedicated scheduler for workflow status field
**From WF4:** Missing scheduler for `sitemap_analysis_status`
**Impact:** Workflow queue never processed, critical functional gap

**Violation B: Manual Queue Processing**

```python
# VIOLATION: Not using SDK pattern
async def process_queue():
    domains = await session.execute(
        select(Domain).filter(Domain.status == "pending")
    )
    for domain in domains:
        # Manual processing without SDK
```

**Detection:** Manual queue loops instead of `run_job_loop`
**From Audit:** Inconsistent scheduler implementations
**Impact:** Error handling, retry logic inconsistent

---

## PATTERN #6: Tenant Isolation Removal

### ✅ CORRECT PATTERN:

```python
# No tenant_id references after architectural removal
page_data = {
    "domain_id": domain_id,
    "url": page_url,
    "sitemap_file_id": sitemap_file.id,
    # No tenant_id field
}
```

**Why:** Tenant isolation was architecturally removed
**Citation:** Constitutional decree on tenant removal

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Lingering Tenant ID Usage**

```python
# From sitemap_import_service.py:130
tenant_id = sitemap_file.tenant_id  # VIOLATION!
page_data = {
    "domain_id": domain_id,
    "url": page_url,
    "tenant_id": tenant_id,  # VIOLATION: Using removed field
    "sitemap_file_id": sitemap_file.id,
}
```

**Detection:** Any `tenant_id` reference in service layer
**From WF5:** sitemap_import_service still uses tenant_id
**Impact:** Architectural inconsistency, future migration issues

---

## PATTERN #7: Async I/O Correctness (Await vs Async Iterator)

### ✅ CORRECT PATTERN:

```python
# Services must await coroutines. Use async-for only on async iterators.
result = await crawler.arun(url, config)  # arun returns a coroutine → await it
return result  # or handle the returned object appropriately

# If the library exposes an async iterator, then:
async for item in crawler.stream(url, config):
    process(item)
```

**Why:** Using `async for` on a coroutine raises a runtime error and short-circuits processing.
**Citation:** Python async/await semantics; WF7 remediation tests

### ❌ ANTI-PATTERN VIOLATIONS:

```python
# domain_content_service.py - VIOLATION!
async for result in self.crawler.arun(url, self.config):  # WRONG: arun is a coroutine
    results.append(result)
```

**Detection:** `'async for' requires an object with __aiter__ method, got coroutine` in logs
**Impact:** Crawler never yields data; downstream logic runs with empty content, masking failures

### Detection:

```bash
grep -n "async for .*arun\(" -n src/services/**/*.py
```

### Remediation Template:

```python
try:
    result = await self.crawler.arun(url, self.config)
    if not result:
        logger.warning("No content extracted from %s", url)
        return None
    return result
except Exception as e:
    logger.error("Error crawling %s: %s", url, e)
    return None
```

---

## VERIFICATION REQUIREMENTS

### Service Review Protocol

```bash
# Verify service accepts session
grep -n "AsyncSession" src/services/domain_curation_service.py

# Check for session creation violations
grep -n "get_session\|get_background_session" src/services/*.py

# Verify no HTTP concerns in services
grep -n "HTTPException\|JSONResponse" src/services/*.py

# Check for tenant_id usage
grep -n "tenant_id" src/services/*.py
```

### What WF7 Did Wrong:

```python
# 1. No service files created at all
# 2. Router contained all business logic
# 3. Inline schemas instead of separate layer
# 4. No scheduler for background processing
```

### What WF7 Should Have Done:

```python
# 1. Create src/services/page_curation_service.py
# 2. Create src/services/page_curation_scheduler.py
# 3. Move business logic from router to service
# 4. Service accepts AsyncSession parameter
# 5. Use run_job_loop for scheduler
```

---

## GUARDIAN CITATION FORMAT

When reviewing Layer 4 services, use this format:

```markdown
L4 SERVICE GUARDIAN ANALYSIS:
✅ Compliant with Pattern #1: Service files exist with correct naming
❌ VIOLATION of Pattern #2: Service creating session at line 45
❌ VIOLATION of Pattern #3: Complex business logic in router
⚠️ WARNING on Pattern #5: Scheduler missing for workflow queue

REQUIRED CORRECTIONS:

1. Move session creation to router, pass as parameter
2. Extract business logic from router to service
3. Create dedicated workflow scheduler

APPROVAL: DENIED - Cardinal Rule violation must be corrected
```

---

## REPLACES

- Full Layer 4 Services Blueprint (200+ lines)
- All workflow-specific L4 audit reports (7 documents)
- Service implementation guidelines
- Scheduler pattern documentation

**With this single 450-line companion for instant pattern recognition!**

---

_"Services accept, never create. This is the way."_
**- The L4 Service Guardian**
