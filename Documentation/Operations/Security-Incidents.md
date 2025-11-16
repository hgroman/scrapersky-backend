# Security Incidents and Vulnerabilities

**Purpose:** Document known security issues, their severity, and remediation status.

**Status:** As of November 2025 comprehensive security audit

---

## Table of Contents

1. [Critical Vulnerabilities](#critical-vulnerabilities)
2. [High Priority Issues](#high-priority-issues)
3. [Medium Priority Issues](#medium-priority-issues)
4. [Remediation Guidance](#remediation-guidance)
5. [Security Best Practices](#security-best-practices)

---

## Critical Vulnerabilities

### 🔴 CATASTROPHIC: DB Portal Completely Exposed

**Severity:** CATASTROPHIC
**Status:** ⚠️ UNRESOLVED (as of Nov 2025 audit)
**Impact:** Complete database access without authentication

#### Details

**File:** `src/routers/db_portal.py`

**Issue:** ZERO authentication on all DB Portal endpoints

**Affected Endpoints:**
- `POST /api/v3/db-portal/query` - **Execute arbitrary SQL queries**
- `GET /api/v3/db-portal/tables` - List all database tables
- `GET /api/v3/db-portal/tables/{table}` - Get table schema
- `GET /api/v3/db-portal/tables/{table}/sample` - Extract sample data

**Current Code:**
```python
# VULNERABLE - NO AUTHENTICATION
router = APIRouter(
    prefix="/api/v3/db-portal",
    tags=["Database Portal"],
    # MISSING: dependencies=[Depends(get_current_user)]
)
```

**Attack Vector:**
```bash
# Anyone can execute arbitrary SQL
curl -X POST http://your-server/api/v3/db-portal/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users"}'
```

**Business Impact:**
- Complete database enumeration
- Arbitrary read-only SQL execution
- Schema discovery
- Sample data extraction
- Potential SQL injection (if query validation fails)
- Regulatory compliance violations (GDPR, CCPA)

#### Remediation

**Fix Time:** 5 minutes

**Solution:**
```python
# Add authentication to router
from src.auth.jwt_auth import get_current_user

router = APIRouter(
    prefix="/api/v3/db-portal",
    tags=["Database Portal"],
    dependencies=[Depends(get_current_user)],  # ← ADD THIS LINE
    responses={404: {"description": "Not found"}},
)
```

**Testing:**
```bash
# After fix - should return 401 without auth token
curl -X POST http://your-server/api/v3/db-portal/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT 1"}'
# Expected: 401 Unauthorized

# With auth token - should work
curl -X POST http://your-server/api/v3/db-portal/query \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT 1"}'
# Expected: 200 OK with results
```

#### References
- **Detailed Analysis:** `Docs/Docs_37_JWT_Audit/L3_DB_Portal_Security_Exposure_Analysis_2025-08-21.md`
- **Comprehensive Security Analysis:** `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/06_AUTHENTICATION_SECURITY.md`

---

### 🔴 CRITICAL: Development Token Works in Production

**Severity:** CRITICAL
**Status:** ⚠️ UNRESOLVED (as of Nov 2025 audit)
**Impact:** Hardcoded admin token works in ALL environments

#### Details

**File:** `src/auth/jwt_auth.py` lines 122-147

**Issue:** Hardcoded token `"scraper_sky_2024"` accepted in production with full admin access

**Current Code:**
```python
# Lines 122-147 in jwt_auth.py
if token == "scraper_sky_2024":
    # Development token - works in ALL environments (DANGEROUS)
    return {
        "id": settings.dev_user_id or "dev-user-id",
        "user_id": settings.dev_user_id or "dev-user-id",
        "email": "dev@scrapersky.com",
        "tenant_id": settings.default_tenant_id,
        "roles": ["admin"],
        "permissions": ["*"]  # Full permissions
    }
```

**Attack Vector:**
```bash
# Anyone with this token gets full admin access
curl -X GET http://your-server/api/v3/domains \
  -H "Authorization: Bearer scraper_sky_2024"
# Returns all domains with admin access
```

**Business Impact:**
- Anyone with knowledge of this token has full admin access
- Works in production, development, and all environments
- Cannot be rotated without code change
- Token visible in codebase (if repository exposed)
- No environment differentiation

**Justification (from code comments):** Required for background job authentication

**Problems with Justification:**
1. Background jobs should use service accounts, not hardcoded tokens
2. No environment detection (works in prod)
3. Token in code repository (security by obscurity)
4. Cannot rotate without code deployment

#### Remediation

**Fix Time:** 10 minutes

**Solution:**
```python
# Add environment check
if token == "scraper_sky_2024":
    # Only allow in development environment
    if settings.environment != "development":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    # Development environment only
    return {
        "id": settings.dev_user_id or "dev-user-id",
        # ... rest of dev user
    }
```

**Better Solution (Long-term):**
1. Implement service account pattern for background jobs
2. Use different tokens per environment
3. Store tokens in secrets management (not code)
4. Add token rotation capability

#### References
- **Comprehensive Security Analysis:** `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/06_AUTHENTICATION_SECURITY.md` (lines 61-213)

---

## High Priority Issues

### 🟠 HIGH: No Rate Limiting

**Severity:** HIGH
**Status:** ⚠️ UNRESOLVED
**Impact:** No protection against brute force or API abuse

#### Details

**Issue:** Zero rate limiting on any endpoint

**Affected:**
- All API endpoints
- Login/authentication endpoints (if they exist)
- No IP-based throttling
- No quota enforcement

**Business Impact:**
- Credential stuffing attacks possible
- API abuse possible (unlimited requests)
- No cost controls on expensive operations
- DoS vulnerability (overwhelm server with requests)

#### Remediation

**Fix Time:** 2 hours

**Solution:**
```python
# Install slowapi
pip install slowapi

# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to expensive endpoints
@limiter.limit("10/minute")
@router.post("/expensive-operation")
async def expensive_operation():
    pass

# Global limit
@limiter.limit("1000/hour")
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    response = await call_next(request)
    return response
```

---

### 🟠 HIGH: Inconsistent Endpoint Protection

**Severity:** HIGH
**Status:** ⚠️ ONGOING RISK
**Impact:** Easy to forget authentication on new endpoints

#### Details

**Issue:** Authentication is opt-in per endpoint, not default

**Pattern makes it easy to accidentally create unprotected endpoints:**

```python
# WRONG - Missing authentication (easy to forget)
@router.get("/domains")
async def get_domains(session: AsyncSession = Depends(get_session_dependency)):
    # NO authentication check
    pass

# CORRECT - Authentication added (must remember)
@router.get("/domains")
async def get_domains(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)  # ← Easy to forget
):
    pass
```

**Observed:** Some routers have authentication commented out in some endpoints

#### Remediation

**Solution 1: Router-Level Authentication (Recommended)**
```python
# Add auth at router level (like dev_tools.py)
router = APIRouter(
    prefix="/api/v3/domains",
    tags=["domains"],
    dependencies=[Depends(get_current_user)]  # ← All endpoints protected
)

# Endpoints automatically authenticated
@router.get("/")  # Protected by router-level dependency
async def get_domains():
    pass
```

**Solution 2: Linter Rule**
```bash
# Add to ruff or custom linter
# Check for @router without Depends(get_current_user)
```

**Solution 3: Code Review Checklist**
- All new endpoints must have authentication
- Router-level auth preferred over endpoint-level
- Explicitly mark public endpoints

---

## Medium Priority Issues

### 🟡 MEDIUM: Exception Details Leaked to Clients

**Severity:** MEDIUM
**Status:** ⚠️ UNRESOLVED
**Impact:** Full exception messages exposed in API responses

#### Details

**File:** `src/main.py` lines 418-430

**Issue:** Exception messages include sensitive information

**Current Code:**
```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "error_detail": str(exc),  # ← Leaks full exception
            "status_code": 500
        }
    )
```

**What Gets Leaked:**
- SQL query syntax (on database errors)
- File paths (on file errors)
- API keys (if in error messages)
- Stack traces (may include sensitive info)

#### Remediation

**Fix Time:** 30 minutes

**Solution:**
```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log full error server-side
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return sanitized error to client
    content = {
        "error": True,
        "message": "Internal server error",
        "status_code": 500
    }

    # Only include details in development
    if settings.environment == "development":
        content["error_detail"] = str(exc)

    return JSONResponse(status_code=500, content=content)
```

---

### 🟡 MEDIUM: SSL Certificate Verification Disabled

**Severity:** MEDIUM
**Status:** ⚠️ BY DESIGN (Supabase requirement?)
**Impact:** Database connection not fully secure

#### Details

**File:** `src/session/async_session.py` lines 137-155

**Issue:** SSL verification disabled for database connections

**Current Code:**
```python
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

**Justification:** Required for Supabase compatibility

**Business Impact:**
- Man-in-the-middle attacks possible on database connection
- Connection still encrypted but not verified
- Applies to both dev and production

#### Remediation

**Action Required:**
1. Verify if Supabase actually requires this
2. If yes, document security trade-off in code comments
3. If no, enable proper SSL verification
4. Consider different settings for dev vs prod

---

### 🟡 MEDIUM: No Token Refresh Mechanism

**Severity:** MEDIUM
**Status:** ⚠️ BY DESIGN
**Impact:** Users must re-authenticate every 30 minutes

#### Details

**Issue:** JWT tokens expire after 30 minutes with no refresh

**Business Impact:**
- Users re-authenticate every 30 minutes
- No sliding window expiration
- Long-running operations may fail mid-execution

#### Remediation

**Options:**
1. Implement refresh token pattern (separate short-lived + long-lived tokens)
2. Extend expiration for background job tokens
3. Implement sliding window (renew token on activity)

---

## Remediation Guidance

### Immediate Actions (This Week)

**Priority 1: Stop the Bleeding**

1. **Add auth to DB Portal** (5 minutes)
   ```python
   # src/routers/db_portal.py
   router = APIRouter(..., dependencies=[Depends(get_current_user)])
   ```

2. **Add environment check to dev token** (10 minutes)
   ```python
   # src/auth/jwt_auth.py
   if token == "scraper_sky_2024":
       if settings.environment != "development":
           raise HTTPException(401, "Invalid token")
   ```

3. **Implement basic rate limiting** (2 hours)
   - Install slowapi
   - Add global rate limit (1000/hour per IP)
   - Add per-endpoint limits for expensive operations

**Total Time:** ~2.5 hours
**Risk Reduction:** Eliminates catastrophic vulnerabilities

### Short-Term Actions (This Month)

**Priority 2: Security Hardening**

1. **Service account pattern** for background jobs
2. **Exception sanitization** (dev vs prod)
3. **SSL verification** investigation
4. **Router-level auth pattern** as default

**Total Time:** ~1 week
**Risk Reduction:** Hardens security posture

### Long-Term Actions (This Quarter)

**Priority 3: Defense in Depth**

1. **Token refresh mechanism**
2. **Audit logging** (all auth attempts, sensitive operations)
3. **RBAC re-implementation** (if multi-user needed)
4. **Security monitoring** and alerting

---

## Security Best Practices

### For All New Code

✅ **Always add authentication:**
```python
# Router-level (preferred)
router = APIRouter(..., dependencies=[Depends(get_current_user)])

# Or endpoint-level
@router.get("/")
async def endpoint(current_user: dict = Depends(get_current_user)):
    pass
```

✅ **Never hardcode secrets:**
```python
# WRONG
if token == "hardcoded_secret":

# RIGHT
if token == os.getenv("SERVICE_ACCOUNT_TOKEN"):
```

✅ **Sanitize error messages:**
```python
# Log full error server-side
logger.error(f"Error: {exc}", exc_info=True)

# Return generic message to client
return {"error": "Internal server error"}  # No details
```

✅ **Implement rate limiting on expensive operations:**
```python
@limiter.limit("10/minute")
@router.post("/expensive")
async def expensive_operation():
    pass
```

---

## References

- **Comprehensive Security Analysis:** `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/06_AUTHENTICATION_SECURITY.md`
- **JWT Audit:** `Docs/Docs_37_JWT_Audit/`
- **DB Portal Analysis:** `Docs/Docs_37_JWT_Audit/L3_DB_Portal_Security_Exposure_Analysis_2025-08-21.md`
- **Work Order:** `Docs/Docs_37_JWT_Audit/WORK_ORDER_001_PRODUCTION_AUTH_CRITICAL.md`

---

## Summary: Critical Security Issues

**Must fix immediately:**
1. 🔴 DB Portal: Add `dependencies=[Depends(get_current_user)]` to router
2. 🔴 Dev Token: Add `if settings.environment != "development": raise 401`
3. 🟠 Rate Limiting: Implement slowapi with basic limits

**Total Time:** ~2.5 hours
**Impact:** Eliminates catastrophic security vulnerabilities

**Remember:** Security is not optional. Fix critical issues before deploying to production.
