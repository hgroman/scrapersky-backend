# ScraperSky Executable Fix Cheat Sheet

## CONTEXT
You are fixing **critical technical debt** identified by comprehensive 7-layer audit reports. Each fix below has been verified as necessary and comes with **specific audit report references**. 

**Your Mission**: Execute these fixes systematically while building knowledge patterns for similar issues.

**Good Code Examples to Follow**:
- `src/models/page.py` - Proper enum naming and BaseModel inheritance
- `src/routers/google_maps_api.py` - Correct transaction management
- `src/services/page_curation_service.py` - Service layer template (if exists)

## CRITICAL-SECURITY (Fix First - 30 minutes)

### 1. Remove Hardcoded JWT Tokens (Implemented)
**Files**: `static/js/domain-curation-tab.js`, `static/js/sitemap-curation-tab.js`
**Audit Reference**: Layer 6 UI Components Audit - CRITICAL security findings
**Status**: **Implemented.** Hardcoded JWT tokens have been removed and replaced with `getJwtToken()` calls.
**Related DART Tasks**: `avPIASSf4qI7`, `F4vjy2ifcaj9`
**Pattern**: JWT tokens must NEVER be hardcoded - always use centralized token retrieval

### 2. Add Missing Authentication (Implemented)
**Files**: `src/routers/page_curation.py`, `src/routers/email_scanner.py`
**Audit Reference**: Layer 3 Routers Audit - CRITICAL auth gaps
**Status**: **Implemented.** Authentication (`Depends(get_current_user)`) has been added to relevant endpoint decorators.
**Related DART Tasks**: `vas6TTZsXsCU`, `ildO8Gz1EtoV`
**Pattern**: All database-modifying endpoints require authentication

## CRITICAL-ARCHITECTURE (Fix Second - 2 hours)

### 3. Create Missing Service Files
**Files to CREATE**: 
- `src/services/staging_editor_service.py`
- `src/services/local_business_curation_service.py` 
- `src/services/domain_curation_service.py`
- `src/services/page_curation_service.py` (if missing)

**Audit Reference**: Layer 4 Services Audit - Missing service files across workflows
**Template**: Copy structure from any existing `*_service.py` file
**Pattern**: Every workflow MUST have dedicated service file with `process_single_{entity}_for_{workflow}` function

### 4. Fix BaseModel Inheritance
**Files**: `src/models/local_business.py`, `src/models/place.py`, others identified in Layer 1 audit
**Audit Reference**: Layer 1 Models Audit - BaseModel inheritance violations
**Problem**: Models inherit only `Base` instead of `Base, BaseModel`
**Fix**: Change `class LocalBusiness(Base):` to `class LocalBusiness(Base, BaseModel):`
**Pattern**: ALL models must inherit from both Base and BaseModel

### 5. Remove Tenant ID Usage (Partially Implemented)
**Files**: Search entire codebase for `tenant_id`
**Audit Reference**: Multiple layers - Tenant isolation removal project
**Status**: **Partially Implemented.** `tenant_id` parameters and filtering logic have been removed from `src/services/places/places_service.py`. Further work is needed to remove all instances across the codebase (e.g., `src/routers/places_staging.py`).
**Related DART Task**: `IrbfKAD8XaO7`
**Pattern**: NO tenant filtering anywhere - system is single-tenant now

## HIGH-STANDARDS (Fix Third - 1 hour)

### 6. Standardize Enum Naming
**Files**: All `*StatusEnum` classes in `src/models/`
**Audit Reference**: Layer 1 Models Audit - Enum standardization
**Problem**: Enums named `PageCurationStatusEnum` with `(enum.Enum)` base
**Fix**: Rename to `PageCurationStatus`, change base to `(str, Enum)`
**Pattern**: No "Enum" suffix, always `(str, Enum)` base class

### 7. Fix UI Data Refresh
**Files**: All curation tab JavaScript files
**Audit Reference**: Layer 6 UI Audit - Data refresh after batch updates  
**Problem**: UI doesn't refresh after batch operations
**Fix**: Add `fetchData()` call in success callback of batch update functions
**Pattern**: Always refresh data view after successful modifications

### 8. Move Local Pydantic Models
**Files**: Any Pydantic models defined in router files
**Audit Reference**: Layer 2 Schemas Audit - Model location violations
**Problem**: Request/response models defined locally in routers
**Fix**: Move to appropriate `src/schemas/{workflow_name}.py` file
**Pattern**: All Pydantic models belong in Layer 2 schemas directory

### 9. Add API Versioning
**Files**: Routers missing `/api/v3/` prefix
**Audit Reference**: Layer 3 Routers Audit - Missing API versioning
**Problem**: Some routers don't use standard API prefix
**Fix**: Add `prefix="/api/v3/{router-name}"` to APIRouter initialization
**Pattern**: ALL API endpoints must use `/api/v3/` prefix

## VERIFICATION STEPS
After each fix:
1. **Code compiles** without import errors
2. **Basic functionality works** (can start server, load UI)
3. **No obvious regressions** introduced
4. **Pattern documented** for future similar fixes

## REFERENCE DOCUMENTS
If you need detailed context:
- **Remediation Executor Persona** - Your operational identity and procedures
- **Layer 1 Models Audit** - Detailed model inheritance and enum issues
- **Layer 3 Routers Audit** - Authentication and API versioning problems  
- **Layer 4 Services Audit** - Missing services and architecture violations
- **Layer 6 UI Audit** - JavaScript security and functionality issues

## SUCCESS METRICS
- **Security**: No hardcoded tokens, all sensitive endpoints authenticated
- **Architecture**: All workflows have service files, clean separation of concerns
- **Standards**: Consistent naming, proper inheritance, API versioning
- **Functionality**: UI works correctly, data refreshes properly

**Remember**: Each fix should follow established patterns and contribute to overall architectural health. Document any new patterns you discover.
