# L2 Schema Guardian Pattern-AntiPattern Companion v2.0
## Instant Pattern Recognition & Violation Detection Guide - Enhanced Edition

**Version:** 2.0  
**Purpose:** Enable instant schema pattern recognition and violation detection  
**Cardinal Rule:** Schemas in schema files, never in routers!  
**Usage:** Load ONLY this document for complete L2 schema review authority  
**Verification Requirement:** All schemas properly organized with ORM configuration  

---

## QUICK REFERENCE SECTION

### 🎯 INSTANT PATTERN CHECKLIST
- [ ] All Pydantic schemas in `src/schemas/` directory, NEVER inline
- [ ] Schema names include workflow prefix (e.g., `WF7_PageCurationRequest`)
- [ ] Response schemas have `from_attributes = True` for ORM models
- [ ] Request/Response suffix on all schema names
- [ ] ENUMs from Layer 1 used, not strings
- [ ] Proper CRUD inheritance pattern (Create/Update inherit from Base)
- [ ] Field descriptions for OpenAPI documentation

### 🔴 INSTANT REJECTION TRIGGERS
1. **Schemas in router files** → REJECT (Cardinal Rule violation)
2. **Missing workflow prefix** → REJECT (Pattern #2 violation)
3. **Missing from_attributes** → REJECT (Pattern #3 violation)
4. **String instead of ENUM** → REJECT (Pattern #4 violation)
5. **No Request/Response suffix** → REJECT (Pattern #5 violation)
6. **Duplicate schema definitions** → REJECT (Pattern #6 violation)
7. **Missing field validation** → REJECT (Pattern #7 violation)

### ✅ APPROVAL REQUIREMENTS
Before approving ANY schema implementation:
1. Verify schema in proper `src/schemas/` file
2. Confirm workflow prefix present
3. Check `from_attributes = True` on response schemas
4. Verify ENUMs from Layer 1 used
5. Confirm Request/Response naming pattern
6. Ensure proper field validation and descriptions

---

## PATTERN #1: Schema File Organization (CARDINAL RULE)

### ✅ CORRECT PATTERN:
```python
# src/schemas/domain_curation.py - Schemas in dedicated files
from pydantic import BaseModel, Field, ConfigDict
from src.models.enums import DomainStatus

class WF4_DomainCurationRequest(BaseModel):
    """Request schema for WF4 domain curation."""
    domain: str = Field(..., description="Domain to curate")
    priority: int = Field(1, ge=1, le=5, description="Priority 1-5")

class WF4_DomainCurationResponse(BaseModel):
    """Response schema for WF4 domain curation."""
    id: uuid.UUID
    domain: str
    status: DomainStatus  # Uses Layer 1 ENUM
    
    model_config = ConfigDict(from_attributes=True)  # For ORM

# src/routers/v3/domains.py - Router imports schemas
from src.schemas.domain_curation import (
    WF4_DomainCurationRequest,
    WF4_DomainCurationResponse
)
```
**Why:** Separation of concerns, reusability, maintainability  
**Citation:** Layer 2 Blueprint 2.1, Constitutional separation

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Inline Schemas in Routers**
```python
# src/routers/batch_sitemap.py - CRITICAL VIOLATION!
# 26+ schemas defined directly in router files!

class BatchStatusResponse(BaseModel):  # WRONG LOCATION!
    batch_id: str
    status: str
    total_domains: int
    # Should be in src/schemas/batch_sitemap.py
```
**Detection:** `class.*BaseModel` in router files  
**From Audit:** 26+ inline schemas across 9 router files  
**Impact:** Architectural breakdown, unmaintainable code

**Violation B: Scattered Schema Definitions**
```python
# VIOLATION: Schemas spread across routers
/src/routers/batch_sitemap.py      # 3 schemas
/src/routers/google_maps_api.py    # 2 schemas
/src/routers/db_portal.py          # 9 schemas!
# All should be in src/schemas/
```
**Detection:** Multiple `BaseModel` classes per router  
**From Audit:** 9 routers contain schema definitions  
**Impact:** Cannot find/reuse schemas, duplication

---

## PATTERN #2: Workflow Prefix Naming

### ✅ CORRECT PATTERN:
```python
# Always include workflow prefix
class WF7_PageCurationRequest(BaseModel):      # WF7 prefix
    page_id: uuid.UUID
    
class WF4_DomainAnalysisResponse(BaseModel):   # WF4 prefix
    domain_id: uuid.UUID
    
class WF5_SitemapImportRequest(BaseModel):     # WF5 prefix
    sitemap_url: str
```
**Why:** Clear workflow ownership and traceability  
**Citation:** Layer 2 Blueprint 2.2.1, Constitutional naming

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing Workflow Prefix**
```python
# VIOLATION: Generic names without workflow context
class PageBatchStatusUpdateRequest(BaseModel):  # Which workflow?
    page_ids: List[uuid.UUID]
    
class BatchStatusResponse(BaseModel):  # Too generic!
    batch_id: str
    
# Should be:
class WF7_PageBatchStatusUpdateRequest(BaseModel):
class WF7_BatchStatusResponse(BaseModel):
```
**Detection:** Schema names without `WF[0-9]_` prefix  
**From Audit:** Multiple schemas lack workflow identification  
**Impact:** Unclear ownership, naming conflicts

---

## PATTERN #3: ORM Configuration (from_attributes)

### ✅ CORRECT PATTERN:
```python
# Response schemas returning ORM models need configuration
class WF4_DomainResponse(BaseModel):
    """Response with ORM model data."""
    id: uuid.UUID
    domain: str
    status: DomainStatus
    created_at: datetime
    
    # Modern Pydantic v2 style
    model_config = ConfigDict(from_attributes=True)
    
    # Or legacy style for Pydantic v1
    class Config:
        orm_mode = True  # Legacy name for from_attributes
```
**Why:** Enables automatic ORM model serialization  
**Citation:** Layer 2 Blueprint 2.2.3, Pydantic requirements

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing ORM Configuration**
```python
# batch_sitemap.py - VIOLATION!
class BatchStatusResponse(BaseModel):
    batch_id: str
    status: str
    # MISSING: model_config = ConfigDict(from_attributes=True)
    # Cannot serialize ORM models!
```
**Detection:** Response schemas without `from_attributes`  
**From Audit:** Only 3 of 9 routers properly configure ORM  
**Impact:** Runtime serialization errors with SQLAlchemy

**Violation B: Wrong Configuration Style**
```python
# VIOLATION: Mixing Pydantic versions
class DomainResponse(BaseModel):
    class Config:
        orm_mode = True  # v1 style
    
    model_config = ConfigDict(...)  # v2 style
    # Don't mix both!
```
**Detection:** Both `Config` class and `model_config`  
**From Audit:** Inconsistent configuration patterns  
**Impact:** Confusion, potential conflicts

---

## PATTERN #4: ENUM Usage from Layer 1

### ✅ CORRECT PATTERN:
```python
# Always use Layer 1 ENUMs, never strings
from src.models.enums import TaskStatus, PageCurationStatus

class WF7_PageStatusResponse(BaseModel):
    """Uses proper ENUM from Layer 1."""
    page_id: uuid.UUID
    status: PageCurationStatus  # ENUM, not str!
    
class JobStatusResponse(BaseModel):
    job_id: uuid.UUID
    status: TaskStatus  # Uses Layer 1 ENUM
```
**Why:** Type safety, validation, consistency  
**Citation:** Layer 2 Blueprint Principle 11, Layer 1 ENUM requirement

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: String Instead of ENUM**
```python
# src/schemas/job.py - CRITICAL VIOLATION!
class JobStatusResponse(BaseModel):
    status: str  # WRONG! Should be TaskStatus ENUM
    job_id: uuid.UUID
    # Comment admits: "# Use the actual Enum type if possible"
```
**Detection:** `status: str` in schemas  
**From Audit:** JobStatusResponse violates Blueprint Principle 11  
**Impact:** No validation, inconsistent values, STOP_FOR_REVIEW

**Violation B: Redefining ENUMs**
```python
# VIOLATION: Creating new ENUM in schema
class StatusEnum(str, Enum):  # Don't redefine!
    PENDING = "pending"
    
# Use Layer 1 ENUM instead:
from src.models.enums import StatusEnum
```
**Detection:** `class.*Enum` in schema files  
**From Audit:** Duplicate ENUM definitions  
**Impact:** Multiple sources of truth

---

## PATTERN #5: Request/Response Naming

### ✅ CORRECT PATTERN:
```python
# Clear action-based naming with suffix
class WF4_DomainCreateRequest(BaseModel):   # Create action
    domain: str
    
class WF4_DomainCreateResponse(BaseModel):  # Response to create
    id: uuid.UUID
    domain: str
    
class WF4_DomainListRequest(BaseModel):     # List action
    filters: Optional[Dict]
    
class WF4_DomainListResponse(BaseModel):    # Response to list
    domains: List[Domain]
    total: int
```
**Why:** Clear intent, consistent patterns  
**Citation:** Layer 2 Blueprint 2.2.1

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing Suffix**
```python
# VIOLATIONS: Ambiguous names
class PlacesStatus(BaseModel):      # Status of what?
class TableInfo(BaseModel):         # Request or Response?
class PatternData(BaseModel):       # Too vague!

# Should be:
class PlacesStatusResponse(BaseModel):
class TableInfoResponse(BaseModel):
class PatternSearchRequest(BaseModel):
```
**Detection:** Schemas without Request/Response suffix  
**From Audit:** Multiple schemas with ambiguous names  
**Impact:** Unclear usage, poor API documentation

---

## PATTERN #6: CRUD Inheritance Pattern

### ✅ CORRECT PATTERN:
```python
# Base schema with common fields
class SitemapFileBase(BaseModel):
    """Base schema for sitemap files."""
    url: str
    file_path: str
    
class SitemapFileCreate(SitemapFileBase):
    """Inherits all base fields for creation."""
    pass  # All fields required
    
class SitemapFileUpdate(SitemapFileBase):
    """Inherits base fields, all optional for updates."""
    url: Optional[str] = None
    file_path: Optional[str] = None
```
**Why:** DRY principle, consistent field definitions  
**Citation:** Layer 2 Blueprint CRUD patterns

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: No Base Inheritance**
```python
# sitemap_file.py - VIOLATION!
class SitemapFileUpdate(BaseModel):  # Should inherit!
    url: Optional[str] = None        # Redefining fields
    status: Optional[SitemapFileStatusEnum] = None
    file_path: Optional[str] = None
    # Not inheriting from SitemapFileBase!
```
**Detection:** Update/Create schemas without base inheritance  
**From Audit:** SitemapFileUpdate doesn't inherit  
**Impact:** Field definition duplication, inconsistency

---

## PATTERN #7: Field Validation & Documentation

### ✅ CORRECT PATTERN:
```python
class WF4_DomainCreateRequest(BaseModel):
    """Request to create a new domain for curation.
    
    Used by WF4 Domain Curation workflow to initiate
    domain analysis and enrichment process.
    """
    domain: str = Field(
        ...,
        min_length=3,
        max_length=255,
        pattern=r'^[a-z0-9.-]+$',
        description="Domain name without protocol"
    )
    priority: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Processing priority (1=highest, 5=lowest)"
    )
```
**Why:** Runtime validation, clear API documentation  
**Citation:** Layer 2 Blueprint 2.2.4

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing Field Descriptions**
```python
# email_scan.py - VIOLATION!
class EmailScanRequest(BaseModel):
    domain_id: uuid.UUID  # No description!
    scan_depth: int       # What's the range?
    
# Should have:
domain_id: uuid.UUID = Field(..., description="Domain to scan")
scan_depth: int = Field(3, ge=1, le=10, description="Scan depth")
```
**Detection:** Fields without `Field()` or description  
**From Audit:** Many schemas lack field documentation  
**Impact:** Poor API docs, no validation

**Violation B: Missing Class Docstrings**
```python
# VIOLATION: No documentation
class PageCurationUpdateRequest(BaseModel):  # What's this for?
    page_id: uuid.UUID
    
# Should have:
class PageCurationUpdateRequest(BaseModel):
    """Request to update page curation status."""
```
**Detection:** Classes without docstrings  
**From Audit:** Multiple schemas undocumented  
**Impact:** Unclear purpose, poor maintainability

---

## PATTERN #8: Duplicate Schema Prevention

### ✅ CORRECT PATTERN:
```python
# src/schemas/common.py - Shared schemas
class BatchUpdateResponse(BaseModel):
    """Generic batch update response."""
    updated_count: int
    failed_count: int
    
# src/schemas/page_curation.py - Specific extension
class WF7_PageBatchUpdateResponse(BatchUpdateResponse):
    """Page-specific batch response."""
    page_ids: List[uuid.UUID]
```
**Why:** DRY principle, single source of truth  
**Citation:** Layer 2 Blueprint architectural principles

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Duplicate Definitions**
```python
# WF7_V2_L3_1of1_PagesRouter.py - VIOLATION!
class BatchUpdateResponse(BaseModel):
    updated_count: int
    queued_count: int

# sitemap_files.py - DUPLICATE!
class BatchUpdateResponse(BaseModel):  # Same name!
    updated_count: int
    queued_count: int
```
**Detection:** Same class names across files  
**From Audit:** Duplicate schemas in multiple routers  
**Impact:** Import conflicts, inconsistent definitions

---

## VERIFICATION REQUIREMENTS

### Schema Review Protocol
```bash
# Find inline schemas in routers
grep -n "class.*BaseModel" src/routers/**/*.py

# Check for workflow prefixes
grep -n "^class [^W].*Request\|Response" src/schemas/*.py

# Verify from_attributes configuration
grep -n "from_attributes\|orm_mode" src/schemas/*.py

# Find string status fields (should be ENUMs)
grep -n "status: str" src/schemas/*.py

# Check for missing Field descriptions
grep -n ": uuid.UUID$\|: str$\|: int$" src/schemas/*.py
```

### What WF7 Did Wrong:
```python
# 1. Defined schemas directly in router file
# 2. No workflow prefix on schema names
# 3. Missing from_attributes = True
# 4. Used status: str instead of ENUMs
# 5. No field validation or descriptions
```

### What WF7 Should Have Done:
```python
# 1. Create src/schemas/page_curation.py
# 2. Use WF7_PageCurationRequest naming
# 3. Add model_config with from_attributes
# 4. Import PageCurationStatus from enums
# 5. Add Field() with validation rules
```

---

## GUARDIAN CITATION FORMAT

When reviewing Layer 2 schemas, use this format:

```markdown
L2 SCHEMA GUARDIAN ANALYSIS:
❌ VIOLATION of Pattern #1: Schema defined in router file (Line 45)
❌ VIOLATION of Pattern #2: Missing WF7_ prefix on schema name
❌ VIOLATION of Pattern #4: Using str instead of TaskStatus ENUM
⚠️ WARNING on Pattern #7: Missing field descriptions

REQUIRED CORRECTIONS:
1. Move schema to src/schemas/page_curation.py
2. Rename to WF7_PageCurationRequest
3. Change status: str to status: PageCurationStatus
4. Add Field descriptions for API documentation

APPROVAL: DENIED - Cardinal Rule violation (inline schema)
```

---

## REPLACES
- L2 Schema Guardian Companion v1.0
- Full Layer 2 Schemas Blueprint (300+ lines)
- 6 Layer 2 audit report chunks
- Schema organization guidelines
- Pydantic configuration documentation

**With this single 495-line companion for instant pattern recognition!**

---

*"Schemas in files, prefixes for workflows, ENUMs from Layer 1, validate everything."*  
**- The L2 Schema Guardian v2.0**