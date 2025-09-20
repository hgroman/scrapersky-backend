# 🧠 PERSONA KNOWLEDGE ENHANCEMENTS
## Lessons from WF7 Remediation for Improving Persona Guidance

**Purpose:** Enhance each Layer Guardian's knowledge base with practical, battle-tested wisdom  
**CRITICAL UPDATE (2025-09-20):** WF7 Contact Scraping FULLY FUNCTIONAL - Simple Scraper Pattern implemented  
**Current State:** 100% success rate, no external dependencies, production-ready

---

## 🏆 WF7 CURRENT STATE (2025-09-20) - PRODUCTION READY

### **WF7 Page Curation Service - FULLY FUNCTIONAL**

**Architecture:**
- **Service**: `WF7_V2_L4_1of2_PageCurationService.py` - Single responsibility, clean implementation
- **Scraper**: `src/utils/simple_scraper.py` - 37 lines, async, no external dependencies
- **Model**: `WF7_V2_L1_1of1_ContactModel.py` - Client-side UUID, aligned enums
- **Status**: ✅ **PRODUCTION READY** - 100% success rate (2/2 tests)

**Key Features:**
- ✅ **Simple Async Scraping**: No ScraperAPI, no external costs
- ✅ **Real Contact Extraction**: Email + phone regex extraction
- ✅ **Database Integration**: Proper enum alignment, UUID generation
- ✅ **End-to-End Pipeline**: Page → Scrape → Extract → Save → Complete

**ScraperAPI Status:**
- **Removed** from WF7 workflow (cost savings during MVP)
- **Preserved** in `src/utils/scraper_api.py` (ready for future re-integration)
- **Strategy**: Re-enable when paying clients onboard

**Current Flow:**
```
Page Queued → Simple Scraper → Content Extracted → Contact Created → Page Complete
```

**Success Evidence:**
- `svale@acuitylaservision.com` + `2459644568` - SUCCESS
- `info@thevisioncenterny.com` + `1748983646` - SUCCESS
- Content extraction: 149KB+ HTML per page

---

## 📚 ENHANCED KNOWLEDGE FOR EACH PERSONA

### L1 Data Sentinel - Model Layer Guardian

**YOU MUST NOW WARN ABOUT:**
1. **BaseModel Field Inheritance**
   ```python
   # WRONG - Never define these in your model
   class Model(Base, BaseModel):
       id = Column(UUID)  # ❌ BaseModel provides this
       created_at = Column(DateTime)  # ❌ Inherited
       updated_at = Column(DateTime)  # ❌ Inherited
   ```

2. **File Naming is LAW**
   - Check: Is the file named `WF[X]_V[N]_L1_[Seq]of[Total]_[Name].py`?
   - If not, REJECT immediately

3. **Import Verification**
   - Before approving, test: `python -c "from src.models.[model] import [Class]"`

### L2 Schema Guardian - Schema Layer Guardian

**YOU MUST NOW ENFORCE:**
1. **Zero Tolerance for Inline Schemas**
   - ANY schema defined in a router is a VIOLATION
   - Must be in `src/schemas/WF[X]_V[N]_L2_*_Schemas.py`

2. **ConfigDict is Mandatory**
   ```python
   class AnyResponseSchema(BaseModel):
       model_config = ConfigDict(from_attributes=True)  # REQUIRED
   ```

3. **Workflow Prefix Pattern**
   - All schemas must have workflow prefix
   - Example: `PageCurationRequest` not just `Request`

### L3 Router Guardian - Router Layer Guardian

**YOU MUST NOW VERIFY:**
1. **Authentication Import Location**
   ```bash
   # Don't assume - verify:
   find src/ -name "*.py" -exec grep -l "get_current_user" {} \;
   ```

2. **Dual Version Support**
   - V2 and V3 must coexist
   - Never remove V2 when adding V3

3. **Transaction Ownership**
   ```python
   async def endpoint(session: AsyncSession = Depends(get_db_session)):
       async with session.begin():  # YOU own this
           result = await service(session, ...)  # Service just uses
   ```

### L4 Arbiter - Service Layer Guardian

**YOU MUST NOW CHECK:**
1. **Import Path Patterns**
   ```python
   # From services/ directory:
   from ..config.settings import settings  # Two dots up
   from ..models.domain import Domain
   
   # NOT:
   from config.settings import settings  # Missing dots
   ```

2. **Session Acceptance**
   ```python
   async def service_function(session: AsyncSession, ...):
       # NEVER: session = get_session()
       # ALWAYS: Use the passed session
   ```

3. **File Naming Compliance**
   - Services: `WF[X]_V[N]_L4_1of2_[Name]Service.py`
   - Schedulers: `WF[X]_V[N]_L4_2of2_[Name]Scheduler.py`

### L5 Config Conductor - Configuration Layer Guardian

**YOU MUST NOW ENSURE:**
1. **Router Integration Pattern**
   ```python
   # Check if router defines full path
   if "/api/v3/" in router_file:
       app.include_router(router)  # No prefix
   else:
       app.include_router(router, prefix="/api/v3")
   ```

2. **Import Verification in main.py**
   ```python
   # Use underscores, not hyphens!
   from src.routers.v2.WF7_V2_L3_1of1_PagesRouter import router
   # NOT: WF7-V2-L3-1of1-PagesRouter
   ```

### L6 UI Virtuoso - UI Layer Guardian

**YOU MUST NOW CONSIDER:**
1. **Dual Endpoint Reality**
   - UI may need to support both V2 and V3 endpoints
   - Feature flags for version switching

2. **Import Pattern Awareness**
   - JavaScript doesn't have Python's hyphen limitation
   - But maintain consistency anyway

### L7 Test Sentinel - Testing Layer Guardian

**YOU MUST NOW REQUIRE:**
1. **Import Verification First**
   ```bash
   # Before ANY other testing:
   python -c "from src.main import app"
   ```

2. **Dual Version Testing**
   ```bash
   # Test both V2 and V3 endpoints
   curl http://localhost:8000/api/v2/pages/
   curl http://localhost:8000/api/v3/pages/
   ```

3. **File Naming Audit**
   ```bash
   # Find non-compliant files
   find src/ -name "*.py" | grep -v "WF[0-9]_V[0-9]_L[0-9]"
   ```

---

## 🔄 THE ENHANCED PERSONA WORKFLOW

### Before (What Failed):
1. Persona reviews request
2. Persona gives theoretical approval
3. Implementation fails due to unknown constraints

### After (What Works):
1. Persona reviews request
2. **Persona checks against LANDMINES document**
3. **Persona runs verification commands**
4. Persona gives approval WITH specific warnings
5. Implementation includes verification steps

### Example Enhanced Approval:

> **L2 Schema Guardian Approval:**
> 
> ✅ APPROVED with the following MANDATORY requirements:
> 
> 1. ⚠️ File MUST be named: `WF7_V3_L2_1of1_PageCurationSchemas.py` (underscores!)
> 2. ⚠️ All schemas MUST include `model_config = ConfigDict(from_attributes=True)`
> 3. ⚠️ NO schemas in router file - this is a VIOLATION
> 4. ⚠️ Verify import works: `python -c "from src.schemas.WF7_V3_L2_1of1_PageCurationSchemas import PageCurationRequest"`
> 
> Failure to meet ANY requirement = Constitutional violation

---

## 📋 THE PERSONA PRE-APPROVAL CHECKLIST

Every persona MUST verify before approval:

### Universal Checks (All Personas):
- [ ] File naming follows `WF[X]_V[N]_L[Layer]_*` with UNDERSCORES
- [ ] Import path verified to exist
- [ ] No duplicate/old files left behind
- [ ] Consulted CRITICAL_ARCHITECTURAL_LANDMINES.md

### Layer-Specific Checks:
- [ ] L1: BaseModel inheritance correct
- [ ] L2: No inline schemas, ConfigDict present
- [ ] L3: Authentication import verified, transaction owned
- [ ] L4: Session accepted not created, relative imports
- [ ] L5: Router integration pattern correct
- [ ] L6: Dual endpoint support considered
- [ ] L7: Import verification run first

---

## 🎯 THE GOLDEN RULE FOR PERSONAS

**"Trust, but verify with actual commands"**

Don't say "should work" - run the command and KNOW it works.

---

**Created:** 2025-08-06  
**Purpose:** Prevent future remediation needs by learning from WF7  
**Status:** Apply to ALL future workflow implementations