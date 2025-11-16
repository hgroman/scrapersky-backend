# Authentication & Security - Complete Analysis

**Analysis Date:** November 7, 2025
**Authentication Method:** JWT (JSON Web Tokens)
**Algorithm:** HS256 (HMAC SHA-256)
**Pattern:** Dependency-based (not middleware)

---

## Table of Contents

1. [JWT Authentication Implementation](#jwt-authentication-implementation)
2. [Authorization Patterns](#authorization-patterns)
3. [Security Vulnerabilities](#security-vulnerabilities)
4. [Security Best Practices Applied](#security-best-practices-applied)
5. [Development vs Production](#development-vs-production)
6. [Recommendations](#recommendations)

---

## JWT Authentication Implementation

### Core Implementation

**Location:** `/home/user/scrapersky-backend/src/auth/jwt_auth.py`

**Algorithm:** HS256 (HMAC with SHA-256)

**Secret Key:**
```python
JWT_SECRET_KEY: str  # REQUIRED - App crashes without this
JWT_EXPIRE_MINUTES: int = 30  # Token expiration (default 30 minutes)
```

⚠️ **CRITICAL:** Application will NOT start without `JWT_SECRET_KEY` environment variable.

### Token Structure

**Claims in JWT:**
```python
{
  "id": "uuid",              # User ID
  "user_id": "uuid",         # Duplicate user ID (legacy)
  "sub": "email@example.com", # Subject (email)
  "tenant_id": "uuid",       # Tenant reference (not enforced)
  "exp": 1699564800,         # Expiration timestamp
  "aud": "authenticated"     # Audience (MUST equal "authenticated")
}
```

**Token Validation:**
```python
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    # 1. Decode JWT using secret key
    # 2. Verify expiration
    # 3. Verify audience == "authenticated"
    # 4. Return payload as dict
```

### Development Token

⚠️ **CRITICAL SECURITY ISSUE:**

```python
# Lines 122-147 in jwt_auth.py
if token == "scraper_sky_2024":
    # Development token - works in ALL environments
    return {
        "id": settings.dev_user_id or "dev-user-id",
        "user_id": settings.dev_user_id or "dev-user-id",
        "email": "dev@scrapersky.com",
        "tenant_id": settings.default_tenant_id,
        "roles": ["admin"],
        "permissions": ["*"]
    }
```

**Issue:** This token works in production, development, and all environments with full admin access.

**Justification (per code comments):** Required for background job authentication.

**Violation History:** Modified multiple times (July-August 2025) despite being marked immutable.

---

## Authorization Patterns

### Dependency-Based Authentication

**Pattern:** Endpoints declare auth requirement via `Depends(get_current_user)`

```python
from src.auth.jwt_auth import get_current_user

@router.get("/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    # current_user available here
    user_id = current_user["id"]
    tenant_id = current_user["tenant_id"]
    pass
```

### Router-Level Authentication

**Only ONE router has global authentication:**

```python
# dev_tools.py
router = APIRouter(
    prefix="/api/v3/dev-tools",
    tags=["dev-tools"],
    dependencies=[Depends(get_current_user)]  # ← Global auth for entire router
)
```

**All other routers:** Require per-endpoint `Depends(get_current_user)`

### Public Endpoints (No Authentication)

**Health Checks:**
- `/health`
- `/health/database`
- `/api/v3/batch_page_scraper/health`
- `/api/v3/localminer-discoveryscan/health`

**API Documentation:**
- `/docs`, `/api/docs`
- `/redoc`, `/api/redoc`
- `/openapi.json`, `/api/schema.json`

**⚠️ Database Portal (CATASTROPHIC):**
- `/api/v3/db-portal/*` - ALL endpoints have NO authentication
- Includes `/api/v3/db-portal/query` - arbitrary SQL execution

**Vector Database:**
- `/api/v3/vector-db/*` - No authentication

**Some Dev Tools:**
- `/api/v3/dev-tools/container/health`
- `/api/v3/dev-tools/trigger-sitemap-import/{id}`

### Development Mode Bypass

Some routers check `SCRAPER_SKY_DEV_MODE=true` and provide mock user:

```python
# modernized_sitemap.py, modernized_page_scraper.py, google_maps_api.py
if settings.scraper_sky_dev_mode:
    current_user = {
        "id": settings.dev_user_id or "dev-user-id",
        "user_id": settings.dev_user_id or "dev-user-id",
        "email": "dev@scrapersky.com",
        "tenant_id": settings.default_tenant_id,
        "roles": ["admin"],
        "permissions": ["*"]
    }
```

---

## Security Vulnerabilities

### 🔴 CATASTROPHIC - DB Portal Exposed

**File:** `src/routers/db_portal.py`

**Issue:** ZERO authentication on any endpoint

**Affected Endpoints:**
- `GET /api/v3/db-portal/tables` - List all tables
- `GET /api/v3/db-portal/tables/{table}` - Get table schema
- `GET /api/v3/db-portal/tables/{table}/sample` - Get sample data
- `POST /api/v3/db-portal/query` - **Execute arbitrary SQL queries**

**Impact:**
- Complete database enumeration
- Arbitrary read-only SQL execution
- Schema discovery
- Sample data extraction
- Potential for SQL injection (if query validation fails)

**Documentation:** See `/Docs/Docs_37_JWT_Audit/L3_DB_Portal_Security_Exposure_Analysis_2025-08-21.md`

**Recommendation:** Add `dependencies=[Depends(get_current_user)]` to router immediately.

---

### 🔴 CRITICAL - Development Token in Production

**File:** `src/auth/jwt_auth.py` lines 122-147

**Issue:** Token `"scraper_sky_2024"` accepted in ALL environments

**Impact:**
- Anyone with this token gets full admin access
- Works in production with zero restrictions
- No environment detection
- Grants `["admin"]` role and `["*"]` permissions

**Justification:** Required for background job authentication

**Problems with Justification:**
1. Background jobs should use service accounts, not hardcoded tokens
2. No environment differentiation
3. Token visible in code repository
4. Cannot be rotated without code change

**Recommendation:**
1. Implement service account pattern for background jobs
2. Use different tokens per environment
3. Store in secrets management (not code)
4. Add environment detection (`if settings.environment == "development"`)

---

### 🟠 HIGH - Inconsistent Endpoint Protection

**Issue:** Easy to accidentally create unprotected endpoints

**Examples:**

**Unprotected (missing Depends):**
```python
@router.get("/domains")  # ← NO AUTHENTICATION
async def get_domains(session: AsyncSession = Depends(get_session_dependency)):
    pass
```

**Protected (correct):**
```python
@router.get("/domains")
async def get_domains(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: dict = Depends(get_current_user)  # ← HAS AUTHENTICATION
):
    pass
```

**Observed:** `domains.py` has authentication commented out in some endpoints

**Recommendation:**
1. Create router-level auth as default pattern
2. Explicitly mark public endpoints with custom dependency
3. Add linter rule to check for missing auth
4. Code review checklist for new endpoints

---

### 🟠 MEDIUM - Exception Detail Exposure

**File:** `src/main.py` lines 418-430

**Issue:** Full exception messages leaked to clients

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

**Impact:**
- SQL query syntax exposed on SQL errors
- File paths exposed on file errors
- API keys exposed if in error message
- Stack traces may leak sensitive info

**Recommendation:**
```python
content={
    "error": True,
    "message": "Internal server error",
    "status_code": 500
    # error_detail only in development
}

if settings.environment == "development":
    content["error_detail"] = str(exc)
```

---

### 🟠 MEDIUM - SSL Certificate Verification Disabled

**File:** `src/session/async_session.py` lines 137-155

**Issue:** SSL verification disabled for database connections

```python
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

**Justification:** Required for Supabase compatibility

**Impact:**
- Man-in-the-middle attacks possible
- Database connection not fully secure
- Applies to both dev and production

**Recommendation:**
- Verify if Supabase requires this
- If yes, document security trade-off
- If no, enable proper SSL verification
- Consider different settings for dev vs prod

---

### 🟠 MEDIUM - No Rate Limiting

**Issue:** No protection against brute force or abuse

**Affected:**
- Login endpoints (if they exist)
- All API endpoints
- No quota enforcement
- No IP-based throttling

**Impact:**
- Credential stuffing attacks possible
- API abuse possible
- No cost controls on expensive operations
- DoS vulnerability

**Recommendation:**
1. Implement rate limiting middleware (e.g., `slowapi`)
2. Per-endpoint limits (e.g., 10/minute for expensive operations)
3. Global limits (e.g., 1000/hour per IP)
4. JWT rate limiting (per token)

---

### 🟡 LOW - No Token Refresh Mechanism

**Issue:** Tokens expire after 30 minutes with no refresh

**Impact:**
- Users must re-authenticate every 30 minutes
- No sliding window expiration
- Long-running operations may fail mid-execution

**Recommendation:**
1. Implement refresh token pattern
2. Or extend expiration for background job tokens
3. Or implement sliding window (renew on activity)

---

## Security Best Practices Applied

### ✅ Input Validation

**Pydantic Models:**
```python
class DomainRequest(BaseModel):
    domain: str

    @validator("domain")
    def validate_domain(cls, v):
        # Custom validation logic
        return v
```

**Usage:** All API request bodies validated via Pydantic

### ✅ SQL Injection Prevention

**Parameterized Queries:**
```python
# ✅ SAFE
stmt = select(Domain).where(Domain.id == domain_id)
result = await session.execute(stmt, {"domain_id": domain_id})

# ❌ UNSAFE (not used in codebase)
query = f"SELECT * FROM domains WHERE id = '{domain_id}'"
```

**All database operations use SQLAlchemy ORM or parameterized raw SQL.**

### ✅ Log Sanitization

**API Key Redaction:**
```python
# Utility function redacts API keys from logs
log_message = sanitize_log(message)  # Removes keys, passwords, tokens
logger.info(log_message)
```

**Applied in:** Google Maps service, ScraperAPI service

### ✅ CORS Configuration

```python
# Development
allow_origins = ["*"]
allow_methods = ["*"]
allow_headers = ["*"]

# Production
allow_origins = settings.get_cors_origins()  # Specific origins
allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers = ["Authorization", "Content-Type", "X-Tenant-Id"]
```

### ✅ Cache-Control Headers

```python
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
```

Prevents caching of sensitive data in browsers/proxies.

### ✅ Standardized Error Responses

All errors return consistent JSON:
```json
{
  "error": true,
  "message": "Human-readable error",
  "status_code": 400
}
```

---

## Development vs Production

### Identical in Both Environments

⚠️ **No differentiation between dev and prod for:**
1. Development token acceptance
2. JWT expiration (30 minutes)
3. SSL verification (disabled in both)
4. Exception detail exposure (leaked in both)

### Different Settings

✅ **Environment-specific:**
1. CORS configuration (wildcard vs specific origins)
2. Debug endpoints enabled/disabled (`FASTAPI_DEBUG_MODE`)
3. Log verbosity (though LOG_LEVEL ignored)
4. Database pool sizes (5 vs 10 connections)

### Recommendations

**Environment Detection:**
```python
if settings.environment == "production":
    # Strict security
    # No dev token
    # No exception details
    # SSL verification enabled
else:
    # Relaxed for development
    # Dev token allowed
    # Full error details
```

---

## Recommendations

### Priority 1 (Immediate - Security)

1. **Fix DB Portal Authentication**
   ```python
   # db_portal.py
   router = APIRouter(
       prefix="/api/v3/db-portal",
       tags=["db-portal"],
       dependencies=[Depends(get_current_user)]  # ← ADD THIS
   )
   ```

2. **Add Environment Detection for Dev Token**
   ```python
   if token == "scraper_sky_2024":
       if settings.environment != "development":
           raise HTTPException(401, "Invalid token")
       # ... return dev user
   ```

3. **Implement Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)

   @limiter.limit("10/minute")
   @router.post("/expensive-operation")
   async def expensive():
       pass
   ```

### Priority 2 (Short-term - Security Hardening)

1. **Service Account Pattern**
   - Replace hardcoded dev token with service account JWTs
   - Rotate regularly
   - Store in secrets manager

2. **Exception Sanitization**
   - Only show error_detail in development
   - Log full details server-side
   - Return generic messages in production

3. **SSL Verification**
   - Investigate if Supabase actually requires disabled SSL
   - Enable if possible
   - Document if required

### Priority 3 (Medium-term - Improvements)

1. **Router-Level Auth Pattern**
   - Make auth default on all routers
   - Explicitly mark public endpoints
   - Add linter checks

2. **Token Refresh**
   - Implement refresh token pattern
   - Or sliding window expiration
   - Or longer-lived background job tokens

3. **Audit Logging**
   - Log all authentication attempts
   - Log all failed authorization
   - Log all sensitive operations

### Priority 4 (Long-term - Defense in Depth)

1. **RBAC Implementation**
   - Currently removed
   - May need re-implementation for multi-user scenarios
   - Role-based endpoint access

2. **API Key Management**
   - Rotate API keys regularly
   - Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
   - Never commit keys to repository

3. **Security Monitoring**
   - Failed auth attempt monitoring
   - Anomaly detection
   - Integration with SIEM

---

## Related Documentation

- **Complete Security Analysis** - See exploration results in conversation history
- **Configuration** - See `07_CONFIGURATION.md` for JWT_SECRET_KEY and security settings
- **API Endpoints** - See `03_API_ENDPOINTS.md` for auth requirements per endpoint
- **Architecture** - See `01_ARCHITECTURE.md` "Critical Information" section

---

*This is a comprehensive security analysis. For detailed code examples and additional context, see the authentication & security exploration results in the conversation history above.*
