# L5 Config Guardian Pattern-AntiPattern Companion
## Instant Pattern Recognition & Violation Detection Guide

**Version:** 1.0  
**Purpose:** Enable instant configuration pattern recognition and violation detection  
**Cardinal Rule:** One source of truth for every configuration!  
**Usage:** Load ONLY this document for complete L5 configuration review authority  
**Verification Requirement:** Router prefixes and session dependencies must be unambiguous  

---

## QUICK REFERENCE SECTION

### 🎯 INSTANT PATTERN CHECKLIST
- [ ] Router defines full prefix OR main.py adds it, never both
- [ ] Single session dependency function used consistently
- [ ] All scheduler variables in docker-compose.yml
- [ ] No hardcoded secrets or tokens anywhere
- [ ] Import order: stdlib → third-party → local
- [ ] Database parameters use Supavisor requirements

### 🔴 INSTANT REJECTION TRIGGERS
1. **Mixed router prefix patterns** → REJECT (Pattern #1 violation)
2. **Multiple session dependencies** → REJECT (Pattern #2 violation)
3. **Hardcoded secrets in code** → REJECT (Pattern #3 violation)
4. **Missing scheduler variables** → REJECT (Pattern #4 violation)
5. **Complex path calculations** → REJECT (Pattern #5 violation)
6. **Scattered import organization** → REJECT (Pattern #6 violation)

### ✅ APPROVAL REQUIREMENTS
Before approving ANY configuration:
1. Verify router prefix pattern consistency
2. Confirm single session dependency source
3. Check all secrets from environment variables
4. Verify scheduler configuration complete
5. Confirm import organization follows pattern
6. Ensure Supavisor parameters present

---

## PATTERN #1: Router Prefix Configuration

### ✅ CORRECT PATTERN:
```python
# main.py - Clear prefix pattern
# EITHER router defines full prefix:
app.include_router(
    domains_router,  # Router has prefix="/api/v3/domains" internally
    # No prefix here!
)

# OR main.py adds prefix:
app.include_router(
    domains_router,  # Router has no prefix internally
    prefix="/api/v3"
)

# Router file shows intent clearly:
@router = APIRouter(prefix="/api/v3/domains")  # Full prefix
# OR
@router = APIRouter()  # Expects main.py to add prefix
```
**Why:** Prevents route registration failures and 404 errors  
**Citation:** Layer 5 Blueprint 2.3.3, 2.3.4

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Mixed Prefix Patterns**
```python
# main.py - VIOLATION!
app.include_router(pages_router, prefix="/api/v3")
app.include_router(domains_router)  # No prefix?
app.include_router(sitemaps_router, prefix="/api")  # Wrong version?

# Some routers have internal prefixes, others don't
# Causes 404s and route conflicts
```
**Detection:** Inconsistent `include_router` patterns in main.py  
**From Audit:** Current implementation has mixed patterns  
**Impact:** Route registration failures, API inconsistency

**Violation B: Double Prefix Addition**
```python
# Router file:
router = APIRouter(prefix="/api/v3/domains")

# main.py - VIOLATION!
app.include_router(router, prefix="/api/v3")
# Results in: /api/v3/api/v3/domains - WRONG!
```
**Detection:** Router with internal prefix + main.py prefix  
**From Audit:** Creates wrong route paths  
**Impact:** All endpoints become unreachable

---

## PATTERN #2: Session Dependency Management

### ✅ CORRECT PATTERN:
```python
# Single source of truth for sessions
# src/session/async_session.py
async def get_session_dependency() -> AsyncSession:
    """The ONE approved session dependency."""
    async with get_session() as session:
        yield session

# Usage everywhere:
from src.session.async_session import get_session_dependency

@router.get("/domains")
async def list_domains(
    session: AsyncSession = Depends(get_session_dependency)
):
    # Consistent session management
```
**Why:** Single source prevents confusion and resource leaks  
**Citation:** Layer 5 Blueprint 2.2 - Dependency Injection Setup

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Multiple Session Dependencies**
```python
# VIOLATION: Two competing functions!
# src/db/session.py
def get_db_session():
    """Claims to be ONLY approved method"""
    
# src/session/async_session.py  
def get_session_dependency():
    """Also used everywhere"""
    
# Developers don't know which to use!
```
**Detection:** Multiple `get_*session*` dependency functions  
**From Audit:** Both functions exist and claim authority  
**Impact:** Inconsistent session management, resource leaks

**Violation B: Direct Session Creation**
```python
# In router - VIOLATION!
@router.get("/test")
async def test():
    session = await get_session()  # WRONG! Should use Depends
```
**Detection:** Direct `get_session()` calls in routers  
**From Audit:** Bypasses dependency injection  
**Impact:** No automatic cleanup, transaction issues

---

## PATTERN #3: Secret Management

### ✅ CORRECT PATTERN:
```python
# docker-compose.yml
environment:
  - DEV_TOKEN=${DEV_TOKEN}  # From .env file
  - JWT_SECRET_KEY=${JWT_SECRET_KEY}
  - API_KEY=${API_KEY}

# settings.py
class Settings(BaseSettings):
    dev_token: str = Field(..., env="DEV_TOKEN")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    
    class Config:
        env_file = ".env"
```
**Why:** Secrets never exposed in version control  
**Citation:** Layer 5 Blueprint 2.1.4 - Secret Management

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Hardcoded Secrets**
```python
# docker-compose.yml - VIOLATION!
environment:
  - DEV_TOKEN=scraper_sky_2024  # HARDCODED SECRET!
  - API_KEY=sk-proj-abc123  # EXPOSED IN REPO!
```
**Detection:** Literal secret values in configuration files  
**From Audit:** DEV_TOKEN hardcoded in docker-compose.yml  
**Impact:** Security vulnerability, exposed credentials

**Violation B: Secrets in Code**
```python
# settings.py - VIOLATION!
class Settings:
    jwt_secret = "super_secret_key_123"  # NEVER DO THIS!
```
**Detection:** String literals that look like secrets  
**From Audit:** Hardcoded tokens found  
**Impact:** Credentials exposed in version control

---

## PATTERN #4: Scheduler Configuration

### ✅ CORRECT PATTERN:
```python
# docker-compose.yml - Complete scheduler config
environment:
  # WF7 Page Curation Scheduler
  - PAGE_CURATION_SCHEDULER_ENABLED=${PAGE_CURATION_SCHEDULER_ENABLED:-true}
  - PAGE_CURATION_SCHEDULER_INTERVAL=${PAGE_CURATION_SCHEDULER_INTERVAL:-60}
  - PAGE_CURATION_SCHEDULER_BATCH_SIZE=${PAGE_CURATION_SCHEDULER_BATCH_SIZE:-10}
  
  # All workflows have scheduler variables
  - DOMAIN_SCHEDULER_ENABLED=${DOMAIN_SCHEDULER_ENABLED:-true}
  - SITEMAP_SCHEDULER_ENABLED=${SITEMAP_SCHEDULER_ENABLED:-true}
```
**Why:** All schedulers configurable via environment  
**Citation:** Layer 5 Blueprint 2.1 - Settings Management

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing Scheduler Variables**
```python
# docker-compose.yml - VIOLATION!
# WF1-WF6 have scheduler variables
# WF7 Page Curation missing entirely!
environment:
  - DOMAIN_SCHEDULER_ENABLED=true
  - SITEMAP_SCHEDULER_ENABLED=true
  # PAGE_CURATION_* variables missing!
```
**Detection:** Grep for workflow scheduler variables  
**From Audit:** WF7 scheduler not configurable  
**Impact:** Cannot control scheduler in deployment

**Violation B: Hardcoded Scheduler Settings**
```python
# scheduler.py - VIOLATION!
INTERVAL = 60  # Hardcoded instead of from env
BATCH_SIZE = 10  # Should be configurable
```
**Detection:** Literal values in scheduler code  
**From Audit:** Scheduler parameters not flexible  
**Impact:** Must rebuild to change configuration

---

## PATTERN #5: Database Configuration

### ✅ CORRECT PATTERN:
```python
# Supavisor-compliant database URL
DATABASE_URL = (
    "postgresql+asyncpg://user:pass@host:6543/db"
    "?raw_sql=true&no_prepare=true&statement_cache_size=0"
)

# Utility function that works
def get_db_params() -> dict:
    """Return Supavisor-required parameters."""
    return {
        "raw_sql": "true",
        "no_prepare": "true", 
        "statement_cache_size": "0"
    }
```
**Why:** Supavisor requires specific connection parameters  
**Citation:** CLAUDE.md Database Architecture section

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Incomplete Utility Function**
```python
# src/utils/db_helpers.py - VIOLATION!
def get_db_params() -> dict:
    """Should return Supavisor params."""
    return {}  # EMPTY! Useless function!
```
**Detection:** Empty or incomplete utility functions  
**From Audit:** get_db_params() returns empty dict  
**Impact:** Missed standardization, connection issues

**Violation B: Missing Supavisor Parameters**
```python
# VIOLATION: Missing required parameters
DATABASE_URL = "postgresql+asyncpg://user:pass@host:6543/db"
# Missing: ?raw_sql=true&no_prepare=true&statement_cache_size=0
```
**Detection:** Database URL without Supavisor params  
**From Audit:** Connection pooling failures  
**Impact:** Database connection errors in production

---

## PATTERN #6: Import Organization

### ✅ CORRECT PATTERN:
```python
# main.py - Organized imports
# 1. Standard library
import os
from typing import Optional

# 2. Third-party libraries  
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# 3. Local application imports
from src.config.settings import settings
from src.routers.v3 import domains, pages
from src.session.async_session import get_session_dependency
```
**Why:** Predictable structure, prevents import conflicts  
**Citation:** Layer 5 Blueprint - Code Organization

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Scattered Imports**
```python
# main.py - VIOLATION!
from fastapi import FastAPI
from src.config.settings import settings
import os  # Standard lib mixed in
from src.routers import domains
from typing import Optional  # More stdlib
import logging  # Random placement
```
**Detection:** Non-grouped imports in main.py  
**From Audit:** Imports scattered throughout file  
**Impact:** Hard to maintain, import order issues

**Violation B: Multiple Settings Definitions**
```python
# main.py - VIOLATION!
class Settings:  # Defined here
    pass

from src.config.settings import settings  # Also imported!
# Which Settings to use?
```
**Detection:** Settings defined and imported  
**From Audit:** Configuration source ambiguity  
**Impact:** Wrong settings used, configuration errors

---

## VERIFICATION REQUIREMENTS

### Configuration Review Protocol
```bash
# Check router prefix consistency
grep -n "include_router" src/main.py

# Find all session dependencies
grep -rn "get.*session" src/ --include="*.py" | grep "def "

# Check for hardcoded secrets
grep -rn "TOKEN\|KEY\|SECRET" . --include="*.yml" | grep -v '${'

# Verify scheduler variables
grep "SCHEDULER" docker-compose.yml | wc -l

# Check import organization
head -30 src/main.py  # Should show organized imports
```

### What WF7 Did Wrong:
```python
# 1. Mixed router prefix patterns
# 2. No scheduler environment variables
# 3. Assumed configuration was complete
# 4. Never verified route registration
```

### What WF7 Should Have Done:
```python
# 1. Consistent router prefix pattern
# 2. Add PAGE_CURATION_SCHEDULER_* variables
# 3. Single session dependency source
# 4. Verify routes accessible after registration
```

---

## GUARDIAN CITATION FORMAT

When reviewing Layer 5 configuration, use this format:

```markdown
L5 CONFIG GUARDIAN ANALYSIS:
❌ VIOLATION of Pattern #1: Mixed router prefix patterns
❌ VIOLATION of Pattern #2: Multiple session dependencies
❌ VIOLATION of Pattern #3: Hardcoded DEV_TOKEN in docker-compose
⚠️ WARNING on Pattern #4: WF7 scheduler variables missing

REQUIRED CORRECTIONS:
1. Standardize router prefix pattern (internal OR external)
2. Remove duplicate session dependency function
3. Move DEV_TOKEN to environment variable
4. Add PAGE_CURATION_SCHEDULER_* configuration

APPROVAL: DENIED - Configuration ambiguity must be resolved
```

---

## REPLACES
- Full Layer 5 Config/Main Blueprint (250+ lines)
- Configuration audit reports
- Router integration guides
- Secret management documentation

**With this single 460-line companion for instant pattern recognition!**

---

*"One source of truth, no ambiguity, configuration clarity."*  
**- The L5 Config Guardian**