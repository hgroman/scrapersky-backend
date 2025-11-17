# Work Order 002: Development Token Production Restriction

**ID:** WO-002
**Created:** 2025-11-16
**Priority:** 🔴 CRITICAL
**Status:** OPEN
**Estimated Time:** 10 minutes
**Assignee:** TBD

---

## Issue Summary

**CRITICAL SECURITY VULNERABILITY:** The hardcoded development authentication bypass token `"scraper_sky_2024"` works in ALL environments including production, providing full admin access to anyone who knows this token.

---

## Severity Classification

**Level:** 🔴 CRITICAL

**Risk:** Anyone with knowledge of the `scraper_sky_2024` token can:
- Bypass all JWT authentication in production
- Gain full admin access to the API
- Access all protected endpoints
- Impersonate the system user (UUID: `5905e9fe-6c61-4694-b09a-6602017b000a`)
- Execute operations as an authenticated user without valid credentials

**Exposure:** The token is documented in multiple locations:
- Source code at `src/auth/jwt_auth.py`
- Historical documentation files
- This work order

---

## Current State (Vulnerable Code)

**File:** `src/auth/jwt_auth.py`
**Lines:** 122-147

### Vulnerable Implementation

```python
# Lines 91-147
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current user from JWT token.
    """
    # Remove Bearer prefix if present
    if token.startswith("Bearer "):
        token = token[7:]  # Remove "Bearer " prefix

    # ================================================================
    # IMMUTABLE PRODUCTION CRITICAL CODE - DO NOT MODIFY
    # ================================================================
    # This internal token is NOT a security vulnerability.
    # It is a REQUIRED operational mechanism for:
    #   - Background job authentication
    #   - Service-to-service communication
    #   - Sitemap scanner operations
    #   - Database maintenance tasks
    #
    # [... extensive comment block ...]
    # ================================================================
    if token == "scraper_sky_2024":  # ⚠️ NO ENVIRONMENT CHECK
        logger.debug("Internal token authorized for authentication bypass")
    # ================================================================
    # END OF IMMUTABLE BLOCK
    # ================================================================

        dev_user_uuid = (
            "5905e9fe-6c61-4694-b09a-6602017b000a"  # From 10-TEST_USER_INFORMATION.md
        )
        return {
            "user_id": dev_user_uuid,
            "id": dev_user_uuid,
            "sub": dev_user_uuid,
            "tenant_id": DEFAULT_TENANT_ID,
            "exp": datetime.utcnow() + timedelta(days=30),
        }

    payload = decode_token(token)
    # ... rest of function
```

### The Problem

**Missing Environment Check:** The token works in development, staging, AND production environments.

**Intent vs. Reality:**
- **Comment claims:** "REQUIRED operational mechanism for background jobs"
- **Reality:** No production operational requirement - background jobs can use proper service accounts
- **Comment warns:** "DO NOT MODIFY" with extensive violation history
- **Truth:** This IS a security vulnerability that must be restricted

---

## Required Fix

### Solution

Add environment check to restrict the bypass token to development environments only.

### Implementation Options

#### Option 1: Environment Variable Check (Recommended)

```python
import os

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current user from JWT token.
    """
    # Remove Bearer prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    # Development bypass token - ONLY in development environment
    if token == "scraper_sky_2024":
        # ✅ ADD THIS ENVIRONMENT CHECK
        current_env = os.getenv("ENV", "production").lower()
        if current_env not in ["development", "dev", "local"]:
            # Reject bypass token in production/staging
            logger.warning(
                f"Attempted use of development bypass token in {current_env} environment. Rejecting."
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"Development bypass token authorized in {current_env} environment")
        dev_user_uuid = "5905e9fe-6c61-4694-b09a-6602017b000a"
        return {
            "user_id": dev_user_uuid,
            "id": dev_user_uuid,
            "sub": dev_user_uuid,
            "tenant_id": DEFAULT_TENANT_ID,
            "exp": datetime.utcnow() + timedelta(days=30),
        }

    # Standard JWT validation
    payload = decode_token(token)
    # ... rest of function
```

#### Option 2: Feature Flag Check (Alternative)

```python
# In settings.py
ALLOW_DEV_TOKEN: bool = os.getenv("ALLOW_DEV_TOKEN", "false").lower() == "true"

# In jwt_auth.py
if token == "scraper_sky_2024":
    if not settings.ALLOW_DEV_TOKEN:
        logger.warning("Development bypass token rejected (disabled)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # ... rest of bypass logic
```

---

## Implementation Checklist

### Step 1: Choose Implementation Strategy
- [ ] **Option 1 (Recommended):** Environment variable check (`ENV != production`)
- [ ] **Option 2:** Feature flag check (`ALLOW_DEV_TOKEN=true`)

### Step 2: Code Changes

- [ ] Add environment check before token bypass logic (line 122)
- [ ] Add logging for rejected bypass attempts
- [ ] Raise proper HTTPException when bypass is rejected
- [ ] Update comments to reflect environment restriction

### Step 3: Environment Configuration

- [ ] Set `ENV=development` in local `.env`
- [ ] Set `ENV=production` in production deployment
- [ ] Set `ENV=staging` in staging deployment (bypass disabled)
- [ ] Document environment variable in `.env.example`

### Step 4: Update Documentation

- [ ] Update comment block (lines 92-121) to reflect environment restriction
- [ ] Remove or soften "DO NOT MODIFY" language
- [ ] Add clear statement: "Only works in development environment"
- [ ] Update CLAUDE.md if it references this pattern

### Step 5: Verification

- [ ] **Local (development):** Verify bypass token still works
  ```bash
  curl -X GET http://localhost:8000/api/v3/domains \
    -H "Authorization: Bearer scraper_sky_2024"
  # Should succeed in development
  ```

- [ ] **Production:** Verify bypass token is REJECTED
  ```bash
  curl -X GET https://production-api.com/api/v3/domains \
    -H "Authorization: Bearer scraper_sky_2024"
  # Should return 401 Unauthorized
  ```

- [ ] Check logs for rejection warnings in production
- [ ] Verify background jobs still work (they should use proper service accounts)

---

## Background Jobs Consideration

### Claim vs. Reality

**Comment Claims:** "Background jobs require this token"

**Investigation Required:**
- [ ] Audit all background schedulers for token usage
- [ ] Check if schedulers actually use this token
- [ ] Verify schedulers work without bypass token

**Expected Finding:** Background schedulers likely do NOT use this token. They run server-side and can use:
- Internal service accounts with proper JWT tokens
- Direct database access (no API authentication needed)

### If Background Jobs DO Use This Token

**Alternative Solutions:**
1. Create a proper service account with long-lived JWT
2. Use internal API calls that bypass authentication (mark as internal-only)
3. Allow background jobs to access services directly without router authentication

---

## Testing Strategy

### Unit Tests

Create `tests/auth/test_dev_token_restriction.py`:

```python
import os
import pytest
from src.auth.jwt_auth import get_current_user

async def test_dev_token_works_in_development():
    """Verify bypass token works in development"""
    os.environ["ENV"] = "development"

    user = await get_current_user(token="scraper_sky_2024")
    assert user["user_id"] == "5905e9fe-6c61-4694-b09a-6602017b000a"

async def test_dev_token_rejected_in_production():
    """Verify bypass token is rejected in production"""
    os.environ["ENV"] = "production"

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="scraper_sky_2024")

    assert exc_info.value.status_code == 401

async def test_dev_token_rejected_in_staging():
    """Verify bypass token is rejected in staging"""
    os.environ["ENV"] = "staging"

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="scraper_sky_2024")

    assert exc_info.value.status_code == 401
```

### Integration Tests

```python
async def test_production_rejects_bypass_token_on_protected_endpoint():
    """End-to-end test: production API rejects bypass token"""
    os.environ["ENV"] = "production"

    headers = {"Authorization": "Bearer scraper_sky_2024"}
    response = await client.get("/api/v3/domains", headers=headers)

    assert response.status_code == 401
    assert "Invalid authentication" in response.json()["detail"]
```

---

## Risk Assessment

### Before Fix
- **Exploit Difficulty:** Trivial (token is documented)
- **Access Level:** Full admin access in production
- **Impact:** CRITICAL

### After Fix
- **Exploit Difficulty:** N/A (token disabled in production)
- **Access Level:** Development only
- **Impact:** Mitigated

---

## Migration Plan

### Phase 1: Add Environment Check (This Work Order)
- Add environment check to reject bypass in production
- Deploy to production
- Monitor logs for rejection attempts

### Phase 2: Audit Background Jobs (Follow-up)
- Verify all background jobs work without bypass token
- Create proper service accounts if needed
- Document authentication patterns for background jobs

### Phase 3: Consider Token Rotation (Future)
- Change the bypass token value in development
- Update documentation
- Ensure old token no longer works anywhere

---

## Deployment Considerations

### Pre-Deployment Verification

**CRITICAL:** Before deploying to production, verify:
- [ ] Background schedulers are running correctly in staging
- [ ] No background jobs depend on the bypass token
- [ ] Environment variable `ENV=production` is set correctly

### Deployment Steps

1. **Deploy to staging first**
   - Set `ENV=staging`
   - Verify bypass token is rejected
   - Run for 24 hours, monitor for issues

2. **Deploy to production**
   - Set `ENV=production`
   - Verify bypass token is rejected
   - Monitor background jobs for authentication failures

3. **Rollback trigger**
   - If background jobs fail due to authentication, rollback immediately
   - Investigate proper service account solution
   - Redeploy with fix

---

## Rollback Plan

If issues arise after deployment:

1. **Immediate:** Revert commit to restore unrestricted bypass token
2. **Alternative:** Set environment variable `ALLOW_DEV_TOKEN=true` temporarily
3. **Investigation:**
   - Identify which background jobs failed
   - Determine proper authentication method
   - Implement service account solution
4. **Redeploy:** Re-enable restriction after fixing background job auth

---

## Success Criteria

- ✅ Bypass token works in development environment (`ENV=development`)
- ✅ Bypass token is REJECTED in production environment (`ENV=production`)
- ✅ Bypass token is REJECTED in staging environment (`ENV=staging`)
- ✅ Proper error message returned when bypass is rejected
- ✅ Rejection attempts are logged with warnings
- ✅ All background jobs continue to function correctly
- ✅ No regression in legitimate authentication flows
- ✅ Tests pass

---

## Related Documents

- **STATE_OF_THE_NATION_2025-11-16.md** - Issue identification
- **src/auth/jwt_auth.py** - Authentication implementation
- **CLAUDE.md** - Authentication patterns
- **.env.example** - Environment variable documentation

---

## Comment Block Revision

### Current Comment (Lines 92-121)

The extensive "IMMUTABLE PRODUCTION CRITICAL CODE" comment block should be updated to:

```python
# ================================================================
# DEVELOPMENT BYPASS TOKEN - RESTRICTED TO DEVELOPMENT ONLY
# ================================================================
# This bypass token is for LOCAL DEVELOPMENT convenience only.
# It allows testing without setting up full JWT authentication.
#
# IMPORTANT: This token is DISABLED in production and staging.
# Background jobs and service-to-service communication should use
# proper service accounts with valid JWT tokens.
#
# Environment Check: Only works when ENV=development
# ================================================================
```

---

## Notes

- The original comment block's claims about "production critical" and "background job requirement" should be verified
- This restriction may reveal background jobs that incorrectly use the bypass token
- Consider this a forcing function to implement proper service account authentication
- The bypass token is useful for development but is a liability in production
- After this fix, consider rotating the token value to invalidate any exposed copies

---

**Created by:** Claude (AI Assistant)
**Validation Date:** 2025-11-16
**Related Issue:** CRITICAL security vulnerability - Dev Token in production
