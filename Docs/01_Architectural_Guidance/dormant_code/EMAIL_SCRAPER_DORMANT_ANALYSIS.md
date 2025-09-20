# Dormant Code Analysis: Email Scraper Service

**Discovered:** 2025-09-13
**Status:** DORMANT - API endpoint commented out
**Impact:** Medium - Misleading documentation references active functionality

## Summary

The email scraper service (`src/tasks/email_scraper.py` + `src/routers/email_scanner.py`) appears functional but is **dormant** - the API endpoint is commented out, making the service unreachable.

**⚠️ AI Partner Warning:** This service exists and looks functional but is inactive. Don't investigate it as a potential contact creation pathway.

## Evidence

**File:** `src/routers/email_scanner.py:99`
```python
# @router.post("/api/v3/email-scanner/scan/{domain_id}", ...)
# async def scan_domain(...): ... # Remove old endpoint
```

**Documentation Still References:**
- `POST /api/v3/scan/website` endpoint (non-existent)
- `scan_website_for_emails_api` function (commented out)
- Multiple work orders and audit reports

## Discovery Process

1. **Initial Assessment**: Identified `source_url` inconsistency between WF7 and email_scraper
2. **Investigation**: Could not find active API endpoint
3. **Confirmation**: Endpoint is commented out, service is dormant
4. **Time Invested**: ~30 minutes of analysis before realizing dormant state

## Active vs Dormant

| Component | Status | Notes |
|-----------|--------|-------|
| **WF7 Service** | ✅ Active | Background scheduler, creating contacts |
| **Email Scraper** | ❌ Dormant | API commented out, unreachable |

## Recommendation

**Document dormant services** to prevent future AI partners from wasting investigation time on inactive code paths.

## Related Files

- `src/tasks/email_scraper.py` - Task implementation (functional but unreachable)
- `src/routers/email_scanner.py` - Router with commented endpoints
- `Docs/Docs_5_Project_Working_Docs/40-LAYER4_Email-Scraper-Refactor-Round-2/` - Stale documentation