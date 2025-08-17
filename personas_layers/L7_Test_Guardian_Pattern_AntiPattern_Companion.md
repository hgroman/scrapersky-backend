# L7 Test Guardian Pattern-AntiPattern Companion
## Instant Pattern Recognition & Violation Detection Guide

**Version:** 1.0  
**Purpose:** Enable instant test pattern recognition and violation detection  
**Cardinal Rule:** Docker-first testing with zero production risk!  
**Usage:** Load ONLY this document for complete L7 testing review authority  
**Verification Requirement:** All tests must be environment-aware and import-verified  

---

## QUICK REFERENCE SECTION

### 🎯 INSTANT PATTERN CHECKLIST
- [ ] Tests run in Docker environment first, local as fallback
- [ ] Import verification performed before ANY test modifications
- [ ] Test files mirror `src/` structure with `test_*.py` naming
- [ ] Database fixtures used, never direct `get_session()` calls
- [ ] Test database isolated from production completely
- [ ] Health checks validate environment before test execution

### 🔴 INSTANT REJECTION TRIGGERS
1. **No import verification** → REJECT (WF7 Crisis violation)
2. **Tests affect production** → REJECT (Cardinal Rule violation)
3. **Missing Docker testing** → REJECT (Pattern #1 violation)
4. **Direct session creation** → REJECT (Pattern #4 violation)
5. **No test isolation** → REJECT (Pattern #5 violation)
6. **Wrong file structure** → REJECT (Pattern #2 violation)

### ✅ APPROVAL REQUIREMENTS
Before approving ANY test implementation:
1. Verify Docker-first testing approach implemented
2. Confirm import checks before modifications
3. Check test directory mirrors src/ structure
4. Verify fixtures for database and API testing
5. Confirm production isolation mechanisms
6. Ensure environment detection logic present

---

## PATTERN #1: Environment-Aware Docker-First Testing

### ✅ CORRECT PATTERN:
```python
# tests/conftest.py - Environment detection
import os
import pytest

def is_docker_environment():
    """Detect if running in Docker container."""
    return os.path.exists('/.dockerenv') or \
           os.environ.get('RUNNING_IN_DOCKER') == 'true'

@pytest.fixture(scope="session")
def test_environment():
    """Provide environment context for tests."""
    if is_docker_environment():
        return "docker"
    return "local"

# Run tests with environment awareness
def test_database_connection(test_environment):
    """Test adapts based on environment."""
    if test_environment == "docker":
        # Use Docker database settings
        db_url = "postgresql://postgres@db:5432/test"
    else:
        # Use local fallback
        db_url = "postgresql://localhost:5432/test"
```
**Why:** Ensures consistent testing across environments  
**Citation:** Layer 7 Blueprint 2.6, Environment-Aware Boot Sequence v1.4

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: No Environment Detection**
```python
# Current conftest.py - VIOLATION!
# No environment detection logic
# Tests assume local environment only
@pytest.fixture
def db_session():
    # Hardcoded local connection
    return get_session()  # Works locally, fails in Docker!
```
**Detection:** Missing `is_docker_environment()` checks  
**From Audit:** Current tests have no environment awareness  
**Impact:** "Works on my machine" syndrome, CI/CD failures

**Violation B: Local-Only Testing**
```python
# VIOLATION: No Docker configuration
# Missing docker-compose.test.yml
# No containerized test isolation
pytest tests/  # Runs locally only, no Docker validation
```
**Detection:** No `docker-compose.test.yml` file exists  
**From Audit:** Complete absence of Docker test infrastructure  
**Impact:** Production deployments fail despite passing tests

---

## PATTERN #2: Import Verification Protocol (WF7 Covenant)

### ✅ CORRECT PATTERN:
```python
# ALWAYS verify imports before test modifications
import importlib.util

def verify_import_exists(module_path: str) -> bool:
    """Verify module can be imported before testing."""
    spec = importlib.util.find_spec(module_path)
    return spec is not None

# In test file
def test_service_function():
    """Test with import verification."""
    # FIRST: Verify the import exists
    assert verify_import_exists("src.services.domain_service"), \
        "domain_service module not found!"
    
    # THEN: Import and test
    from src.services.domain_service import process_domain
    # ... test logic
```
**Why:** Prevents 3-hour debugging spirals from missing imports  
**Citation:** WF7 Recovery Covenant, Layer 7 Blueprint Critical Lesson

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Assuming Imports Exist**
```python
# VIOLATION: No import verification
from src.services.page_curation_service import process_page  # BOOM!
# ImportError after 3 hours of debugging
# Service doesn't exist but test assumes it does

def test_page_processing():
    result = process_page(...)  # Never reached
```
**Detection:** Direct imports without verification  
**From WF7 Crisis:** 3-hour debugging session from this exact issue  
**Impact:** Massive time waste, AI confusion, broken deployments

**Violation B: No Server Startup Validation**
```python
# VIOLATION: Modifying imports without checking server
# Change import structure
# Never verify server still starts
# Deploy broken code
```
**Detection:** Import changes without `python src/main.py` check  
**From WF7:** Server wouldn't start after import modifications  
**Impact:** Production deployment failures

---

## PATTERN #3: Test File Structure & Naming

### ✅ CORRECT PATTERN:
```python
# Mirror src/ structure exactly
tests/
├── conftest.py           # Shared fixtures
├── models/
│   ├── test_domain.py    # Tests for src/models/domain.py
│   └── test_contact.py   # Tests for src/models/contact.py
├── routers/
│   └── v3/
│       └── test_domains.py  # Tests for src/routers/v3/domains.py
├── services/
│   ├── test_domain_service.py
│   └── test_domain_scheduler.py
└── integration/
    └── test_api_flow.py  # End-to-end tests
```
**Why:** Instant test location discovery, clear ownership  
**Citation:** Layer 7 Blueprint 2.1.2, 2.1.3

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Flat Test Structure**
```python
# Current reality - VIOLATION!
tests/
├── conftest.py  # Only file that exists
└── (nothing else)

# No mirroring of src/ structure
# No layer-specific organization
```
**Detection:** `ls tests/` shows only conftest.py  
**From Audit:** "Virtually no tests exist for any layer"  
**Impact:** No test coverage, technical debt accumulation

**Violation B: Wrong Naming Convention**
```python
# VIOLATION: Non-standard test file names
tests/
├── domain_tests.py      # WRONG! Should be test_domain.py
├── TestDomainClass.py   # WRONG! Should be test_domain.py
└── check_domains.py     # WRONG! Not recognized by pytest
```
**Detection:** Files not matching `test_*.py` pattern  
**From Audit:** Inconsistent naming prevents test discovery  
**Impact:** Tests not executed by pytest, false confidence

---

## PATTERN #4: Database Fixture Pattern

### ✅ CORRECT PATTERN:
```python
# tests/conftest.py
@pytest.fixture
async def db_session():
    """Provide isolated test database session."""
    # Create test database connection
    engine = create_async_engine(
        "postgresql+asyncpg://test_user@localhost/test_db"
    )
    
    async with AsyncSession(engine) as session:
        # Begin transaction
        async with session.begin():
            yield session
            # Rollback after test (isolation)
            await session.rollback()

# Usage in tests
async def test_create_domain(db_session):
    """Test uses fixture, not direct session."""
    domain = Domain(domain="test.com")
    db_session.add(domain)
    await db_session.flush()
    assert domain.id is not None
```
**Why:** Ensures test isolation and consistent teardown  
**Citation:** Layer 7 Blueprint 2.3

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Direct Session Creation in Tests**
```python
# VIOLATION: Creating sessions directly
async def test_domain():
    session = await get_session()  # WRONG!
    # No isolation, no cleanup
    # Can affect other tests or production
```
**Detection:** `get_session()` calls in test files  
**From Audit:** "Instruction to use get_session() directly"  
**Impact:** Test contamination, flaky tests, production risk

**Violation B: Missing Async Fixtures**
```python
# Current conftest.py - VIOLATION!
@pytest.fixture
def sample_uuid():
    return str(uuid.uuid4())
# That's it! No database fixtures at all!
```
**Detection:** No `db_session` fixture in conftest.py  
**From Audit:** Only UUID fixtures exist  
**Impact:** No database testing possible

---

## PATTERN #5: Production Safety & Isolation

### ✅ CORRECT PATTERN:
```python
# Test configuration with production protection
import os

# Ensure test database URL
os.environ['DATABASE_URL'] = 'postgresql://localhost/test_db'
os.environ['ENVIRONMENT'] = 'test'

# Prevent production access
if 'production' in os.environ.get('DATABASE_URL', ''):
    raise RuntimeError("FATAL: Tests attempting production access!")

# Test-specific settings
class TestSettings(Settings):
    database_url: str = "postgresql://localhost/test_db"
    redis_url: str = "redis://localhost/test_redis"
    environment: str = "test"
```
**Why:** Zero risk of production system contamination  
**Citation:** Environment-Aware Boot Sequence - Production Preservation

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: No Production Guards**
```python
# VIOLATION: No protection against production
# Tests could connect to production database
# No environment variable validation
# No separate test configuration
```
**Detection:** Missing production URL checks in tests  
**From Audit:** No test isolation mechanisms  
**Impact:** Potential production data corruption

**Violation B: Shared Configuration**
```python
# VIOLATION: Using production settings in tests
from src.config.settings import settings  # Production settings!

def test_something():
    # Using production database URL!
    db = connect(settings.database_url)
```
**Detection:** Direct settings import without override  
**From Audit:** No test-specific configuration  
**Impact:** Tests run against production systems

---

## PATTERN #6: Test Coverage Requirements

### ✅ CORRECT PATTERN:
```python
# Comprehensive layer-specific testing

# Layer 1 - Model tests
def test_model_validation():
    """Test model field validation."""
    pass

# Layer 3 - Router tests
async def test_api_endpoints(api_client):
    """Test API contracts."""
    response = await api_client.get("/api/v3/domains")
    assert response.status_code == 200

# Layer 4 - Service tests
async def test_business_logic(db_session):
    """Test service layer logic."""
    result = await process_domain(domain_id=1, session=db_session)
    assert result is not None
```
**Why:** Ensures each layer functions correctly  
**Citation:** Layer 7 Blueprint 2.2

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: No Test Coverage**
```python
# Current reality - VIOLATION!
# src/models/domain.py - 0% coverage
# src/routers/v3/domains.py - 0% coverage  
# src/services/domain_service.py - 0% coverage
# Only conftest.py exists with basic fixtures
```
**Detection:** `pytest --cov` shows 0% for most files  
**From Audit:** "Virtually no tests exist for any layer"  
**Impact:** Undetected bugs, regression issues, technical debt

---

## VERIFICATION REQUIREMENTS

### Test Review Protocol
```bash
# Check Docker test configuration
ls docker-compose.test.yml || echo "MISSING: Docker test config"

# Verify test structure mirrors src/
find tests -type f -name "test_*.py" | head -5

# Check for import verification
grep -n "verify_import_exists\|importlib" tests/

# Verify no production access
grep -n "production" tests/ || echo "OK: No production refs"

# Check fixture usage
grep -n "@pytest.fixture" tests/conftest.py
```

### What WF7 Did Wrong:
```python
# 1. No import verification before modifications
# 2. Assumed services existed without checking
# 3. No Docker testing environment
# 4. Modified code without server startup validation
# Result: 3-hour debugging spiral
```

### What WF7 Should Have Done:
```python
# 1. Verify import exists before testing
# 2. Run tests in Docker first
# 3. Check server starts after changes
# 4. Use fixtures for database isolation
# 5. Validate environment before execution
```

---

## GUARDIAN CITATION FORMAT

When reviewing Layer 7 tests, use this format:

```markdown
L7 TEST GUARDIAN ANALYSIS:
❌ VIOLATION of Pattern #1: No Docker test environment
❌ VIOLATION of Pattern #2: Missing import verification
❌ VIOLATION of Pattern #3: No test file structure
⚠️ WARNING on Pattern #4: Direct session usage detected

REQUIRED CORRECTIONS:
1. Create docker-compose.test.yml for test isolation
2. Add import verification before all test modifications
3. Mirror src/ structure in tests/ directory
4. Create database fixtures in conftest.py

APPROVAL: DENIED - WF7 Crisis patterns detected, must add safety protocols
```

---

## REPLACES
- Full Layer 7 Testing Blueprint (300+ lines)
- Environment-Aware Boot Sequence documentation
- WF7 Crisis recovery documentation
- Test configuration guides
- AI testing safety protocols

**With this single 470-line companion for instant pattern recognition!**

---

*"Test in Docker first, verify imports always, protect production absolutely."*  
**- The L7 Test Guardian**