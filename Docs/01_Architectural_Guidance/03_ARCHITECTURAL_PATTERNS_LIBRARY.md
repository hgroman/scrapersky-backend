# ScraperSky Architectural Patterns Library

**Version:** 2.1  
**Owner:** The Architect  
**Last Updated:** 2025-08-17 (WF7 Postmortem Integration)  
**Purpose:** Consolidated reference for naming conventions, blessed patterns, and anti-patterns across all layers

> **📚 COMPREHENSIVE CATALOGS AVAILABLE:**
> - **47 Patterns:** See `07_PATTERN_CATALOG_WF7_SYNTHESIS.md` for complete collection
> - **47 Anti-patterns:** See `08_ANTIPATTERN_CATALOG_WF7_SYNTHESIS.md` for full taxonomy
> 
> This document contains the most critical subset for daily use.

---

## SECTION 1: MANDATORY NAMING CONVENTION

### The Law (Non-Negotiable)
```
WF[X]_V[N]_L[Layer]_[Seq]of[Total]_[DescriptiveName].py
```

### Pattern Components
- **WF[X]**: Workflow number (WF1-WF7)
- **V[N]**: Version number (V2, V3)
- **L[Layer]**: Layer number (L1-L7)
- **[Seq]of[Total]**: File sequence (1of1, 1of2, 2of2)
- **[DescriptiveName]**: Clear component descriptor

### ⚠️ CRITICAL: Python vs Documentation
| Context | Format | Example |
|---------|--------|---------|
| **Documentation** | Hyphens | `WF7-V2-L1-1of1-ContactModel.py` |
| **Python Files** | Underscores | `WF7_V2_L1_1of1_ContactModel.py` |
| **Import Statement** | Underscores | `from src.models.WF7_V2_L1_1of1_ContactModel import Contact` |

**WHY:** Python cannot import modules with hyphens!

### Correct Examples by Layer
```python
# Layer 1 (Models)
src/models/WF7_V2_L1_1of1_ContactModel.py

# Layer 2 (Schemas)  
src/schemas/WF7_V3_L2_1of1_PageCurationSchemas.py

# Layer 3 (Routers)
src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py

# Layer 4 (Services)
src/services/WF7_V2_L4_1of2_PageCurationService.py
src/services/WF7_V2_L4_2of2_PageCurationScheduler.py
```

### Compliance Verification
```bash
# Find non-compliant files
find src/ -name "*.py" | grep -v "WF[0-9]_V[0-9]_L[0-9]"

# Test import validity
python -c "from src.models.WF7_V2_L1_1of1_ContactModel import Contact"
```

---

## SECTION 2: BLESSED PATTERNS (✅ DO THIS)

### Layer 1: Models Pattern
```python
# ✅ CORRECT: Proper model structure
from src.models.base import Base, BaseModel
from sqlalchemy import Column, String, UUID, ForeignKey
from sqlalchemy.orm import relationship

class Domain(Base, BaseModel):
    __tablename__ = "domains"
    
    # BaseModel provides: id, created_at, updated_at
    # Only add YOUR specific fields
    domain_url = Column(String, nullable=False)
    status = Column(String, default="pending")
    
    # Relationships
    pages = relationship("Page", back_populates="domain")
```

### Layer 2: Schemas Pattern
```python
# ✅ CORRECT: Extracted schema file
# File: src/schemas/WF7_V3_L2_1of1_PageCurationSchemas.py
from pydantic import BaseModel, ConfigDict

class PageCurationRequest(BaseModel):
    url: str
    priority: int = 0

class PageCurationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Required for ORM
    id: str
    url: str
    status: str
```

### Layer 3: Routers Pattern
```python
# ✅ CORRECT: Transaction ownership + auth
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db_session
from src.auth.jwt_auth import verify_token
from src.schemas.WF7_V3_L2_1of1_PageCurationSchemas import PageCurationRequest

router = APIRouter(prefix="/api/v3/pages", tags=["pages"])

@router.post("/curate")
async def curate_page(
    request: PageCurationRequest,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(verify_token)  # Auth dependency
):
    async with session.begin():  # Router owns transaction
        result = await page_service.curate(session, request)
        return result
```

### Layer 4: Services Pattern
```python
# ✅ CORRECT: Stateless service accepting session
async def curate_page(
    session: AsyncSession,  # Accept session, never create
    request: PageCurationRequest
) -> PageCurationResponse:
    # Business logic here
    page = Page(**request.dict())
    session.add(page)
    await session.flush()  # Not commit - router handles that
    return PageCurationResponse.from_orm(page)
```

### Layer 4: Scheduler Pattern
```python
# ✅ CORRECT: run_job_loop SDK pattern
from src.sdk.run_job_loop import run_job_loop
from src.config.settings import settings

async def page_curation_scheduler_setup():
    await run_job_loop(
        job_name="page_curation",
        job_function=process_page_batch,
        status_column="curation_status",
        table_name="pages",
        interval_seconds=settings.PAGE_CURATION_INTERVAL,
        batch_size=settings.PAGE_CURATION_BATCH_SIZE
    )
```

### Layer 5: Configuration Pattern
```python
# ✅ CORRECT: Settings with proper imports
# File: src/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Scheduler settings
    PAGE_CURATION_INTERVAL: int = 60
    PAGE_CURATION_BATCH_SIZE: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()

# Import in other files
from src.config.settings import settings  # Absolute
# OR
from ..config.settings import settings  # Relative
```

### Import Resolution Pattern
```python
# ✅ CORRECT: Finding the right import
# Step 1: Find where something is defined
find src/ -name "*.py" -exec grep -l "verify_token" {} \;

# Step 2: Test the import
python -c "from src.auth.jwt_auth import verify_token; print('✅')"

# Step 3: Use in code
from src.auth.jwt_auth import verify_token
```

<!-- WF7 POSTMORTEM INTEGRATION START - Source: WF7_POSTMORTEM_INTEGRATION_QUEUE.md -->

### ✅ PATTERN: Mandatory Checkpoint Enforcement
**Source:** WO_002/003 Analysis
**Implementation:**
```python
async def checkpoint_enforcement(phase: str, guardian: str):
    """Cannot proceed without guardian approval"""
    approval = await get_guardian_approval(guardian, phase)
    if not approval:
        raise StopSignViolation(f"Phase {phase} blocked by {guardian}")
    return approval
```
**Key:** Makes advisory guidance mandatory
**Verification:** No phase proceeds without approval

<!-- WF7 POSTMORTEM INTEGRATION END -->

### V2/V3 Parallel Pattern
```python
# ✅ CORRECT: Dual existence in main.py
from src.routers.v2.WF7_V2_L3_1of1_PagesRouter import router as v2_pages
from src.routers.v3.WF7_V3_L3_1of1_PagesRouter import router as v3_pages

app.include_router(v2_pages)  # Keep V2 active
app.include_router(v3_pages)  # Add V3 alongside
```

---

## SECTION 3: ANTI-PATTERNS (❌ NEVER DO THIS)

### ❌ ANTI-PATTERN 1: Hyphens in Python Files
```python
# ❌ WRONG: Hyphens break imports
WF7-V2-L1-1of1-ContactModel.py  # SyntaxError!

# ✅ CORRECT: Use underscores
WF7_V2_L1_1of1_ContactModel.py
```

### ❌ ANTI-PATTERN 2: Inline Schemas
```python
# ❌ WRONG: Schema defined in router
@router.post("/endpoint")
async def endpoint():
    class RequestSchema(BaseModel):  # VIOLATION!
        field: str

# ✅ CORRECT: Import from Layer 2
from src.schemas.WF7_V3_L2_1of1_Schemas import RequestSchema
```

### ❌ ANTI-PATTERN 3: Service Creating Sessions
```python
# ❌ WRONG: Service creates its own session
async def my_service():
    async with get_db_session() as session:  # VIOLATION!
        # logic here

# ✅ CORRECT: Service accepts session
async def my_service(session: AsyncSession):
    # logic here
```

### ❌ ANTI-PATTERN 4: Duplicate BaseModel Fields
```python
# ❌ WRONG: Redefining inherited fields
class MyModel(Base, BaseModel):
    id = Column(UUID, primary_key=True)  # BaseModel has this!
    created_at = Column(DateTime)  # Duplicate!

# ✅ CORRECT: Only add new fields
class MyModel(Base, BaseModel):
    # id, created_at, updated_at inherited
    custom_field = Column(String)
```

### ❌ ANTI-PATTERN 5: Missing ConfigDict
```python
# ❌ WRONG: Response without ORM config
class MyResponse(BaseModel):
    field: str  # Won't work with ORM objects!

# ✅ CORRECT: Include ConfigDict
class MyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    field: str
```

### ❌ ANTI-PATTERN 6: Wrong API Version
```python
# ❌ WRONG: Using /api/v2/ for new code
router = APIRouter(prefix="/api/v2/pages")

# ✅ CORRECT: New code uses v3
router = APIRouter(prefix="/api/v3/pages")
```

### ❌ ANTI-PATTERN 7: Import Guessing
```python
# ❌ WRONG: Assuming import location
from src.dependencies.auth import get_current_user  # May not exist!

# ✅ CORRECT: Find actual location first
# Run: find src/ -name "*.py" -exec grep -l "get_current_user" {} \;
from src.auth.jwt_auth import verify_token  # Verified location
```

### ❌ ANTI-PATTERN 8: File Duplication
```python
# ❌ WRONG: Keeping old and new files
cp src/models/contact.py src/models/WF7_V2_L1_1of1_ContactModel.py
# Now TWO files can be imported!

# ✅ CORRECT: Rename immediately
mv src/models/contact.py src/models/WF7_V2_L1_1of1_ContactModel.py
```

### ❌ ANTI-PATTERN 9: Missing Auth Dependency
```python
# ❌ WRONG: Endpoint without authentication
@router.post("/sensitive")
async def endpoint(session: AsyncSession = Depends(get_db_session)):
    # No auth check!

# ✅ CORRECT: Include auth dependency
@router.post("/sensitive")
async def endpoint(
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(verify_token)  # Required!
):
```

### ❌ ANTI-PATTERN 10: Circular Imports
```python
# ❌ WRONG: Circular dependency
# models.py imports from services.py
# services.py imports from models.py

# ✅ CORRECT: Unidirectional flow
# models.py → standalone
# services.py → imports models
# routers.py → imports services
```

<!-- WF7 POSTMORTEM INTEGRATION START - Source: WF7_POSTMORTEM_INTEGRATION_QUEUE.md -->

### ❌ ANTI-PATTERN 11: Compliance Theater
**Source:** WO_002 WF7 Crisis
**Pattern:** AI claims compliance while violating everything
**Example:** "I have reviewed all documentation" (never opened files)
**Prevention:** Require file:line citations for all claims
**Verification:** `grep -n "pattern_name" file.py`

### ❌ ANTI-PATTERN 12: Blueprint Blindness  
**Source:** WO_002 WF7 Crisis
**Pattern:** Documentation exists but AI never loads it
**Example:** Perfect blueprints available, zero consultations
**Prevention:** Mandatory blueprint loading with verification
**Verification:** Check session history for Read operations

### ❌ ANTI-PATTERN 13: Guardian Ghosting
**Source:** WO_002 WF7 Crisis  
**Pattern:** Zero Layer Guardian consultations despite requirements
**Example:** Building Layer 1 without L1 Data Sentinel input
**Prevention:** Checkpoint enforcement at each layer
**Verification:** Guardian approval signatures required

### ❌ ANTI-PATTERN 14: Import Assumption Cascade
**Source:** WO_002 WF7 Crisis
**Pattern:** AI assumes functions exist without verification
**Example:** `from src.nonexistent import imaginary_function`
**Prevention:** Test every import before use
**Verification:** `python -c "from x import y"`

### ❌ ANTI-PATTERN 15: Documentation Deception
**Source:** WO_002 WF7 Crisis
**Pattern:** Glowing case studies hiding violations
**Example:** "Successfully implemented WF7" (broke everything)
**Prevention:** Code-first documentation with citations
**Verification:** Every claim links to actual code

### ❌ ANTI-PATTERN 16: Analysis Paralysis
**Source:** WO_006 Git Patterns
**Pattern:** Endless analysis without implementation
**Example:** 88 uncommitted files for 10+ days
**Prevention:** Commit threshold of 80 files
**Verification:** `git status | wc -l`

### ❌ ANTI-PATTERN 17: SQLAlchemy Enum Comparison Bug ⚠️ **CRITICAL**
**Source:** Contacts CRUD Crisis (2025-09-13), War Story: Enum_Implementation_Train_Wreck__2025-09-12.md
**Pattern:** Using enum objects directly in SQLAlchemy comparisons/assignments
**PostgreSQL Error:** `operator does not exist: enum_type = customenumtype`
**Example:**
```python
# ❌ WRONG: Direct enum comparison (BREAKS DATABASE QUERIES)
filters.append(Contact.status == ContactStatus.New)  # FAILS!
contact.status = ContactStatus.Active  # FAILS!

# ✅ CORRECT: Always use .value for SQLAlchemy operations
filters.append(Contact.status == ContactStatus.New.value)  # WORKS!
contact.status = ContactStatus.Active.value  # WORKS!
```
**🤖 AI PARTNER WARNING:** This is a recurring bug that breaks production. ALWAYS use `.value` when:
- Comparing enum fields in SQLAlchemy queries (`Model.enum_field == MyEnum.VALUE.value`)
- Assigning enum values to model fields (`model.enum_field = MyEnum.VALUE.value`)
- Python enum-to-enum comparisons are fine: `request.status == MyEnum.VALUE` ✅

**Prevention:** Check every enum operation in SQLAlchemy contexts
**Verification:** Test all enum filtering before deployment

<!-- WF7 POSTMORTEM INTEGRATION END -->

---

## SECTION 4: LAYER-SPECIFIC PATTERNS

| Layer | Primary Pattern | Key Requirement |
|-------|----------------|-----------------|
| **L1 Models** | BaseModel inheritance | UUID PKs, snake_case |
| **L2 Schemas** | Extracted files | ConfigDict(from_attributes=True) |
| **L3 Routers** | Transaction ownership | Auth dependency, /api/v3/ |
| **L4 Services** | Session acceptance | Stateless, no session creation |
| **L4 Schedulers** | run_job_loop SDK | Status progression pattern |
| **L5 Config** | Centralized settings | Environment variables |
| **L6 UI** | Semantic HTML | External CSS/JS files |
| **L7 Testing** | Docker-first | Six-tier validation |

---

## QUICK REFERENCE: DEFUSAL COMMANDS

```bash
# Verify naming compliance
find src/ -name "*.py" | grep -v "WF[0-9]_V[0-9]_L[0-9]"

# Find inline schemas
grep -r "class.*Request\|class.*Response" src/routers/

# Locate auth functions
find src/ -name "*.py" -exec grep -l "verify_token\|get_current_user" {} \;

# Test import chain
python -c "from src.main import app; print('✅ All imports valid')"

# Check for duplicates
find src/ -name "*.py" | xargs basename | sort | uniq -d

# Verify server health
curl -f http://localhost:8000/health
```

---

**Authority:** ScraperSky Development Constitution  
**Enforcement:** Mandatory for all workflow construction  
**Updates:** Add new patterns/anti-patterns as discovered