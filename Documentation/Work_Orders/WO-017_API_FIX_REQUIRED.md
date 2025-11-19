# WO-017: DeBounce API Fix Required

**Date:** 2025-11-19  
**Priority:** 🔴 **CRITICAL - BLOCKS PHASE 1**  
**Assigned To:** Online Claude  
**Status:** ⏳ **WAITING FOR FIX**

---

## Problem Summary

The DeBounce service is using a **non-existent bulk API endpoint**. After reviewing the official DeBounce API documentation, there is **no bulk validation endpoint** for real-time API calls.

**Current (Wrong):**
```
POST https://api.debounce.io/v1/validate/bulk
→ HTTP 404 Not Found
```

**Correct:**
```
GET https://api.debounce.io/v1/?api={API_KEY}&email={EMAIL}
→ Single email validation only
```

---

## DeBounce API Facts

### What DeBounce Provides ✅
1. **Real-Time Lookup API** - Single email validation via GET
2. **Dashboard Bulk Upload** - Upload CSV, validate via dashboard (not API)

### What DeBounce Does NOT Provide ❌
1. ❌ No `/validate/bulk` endpoint
2. ❌ No bulk validation via API
3. ❌ No POST method for validation

### Authentication Method
- **NOT via headers** ❌
- **Via query parameter** ✅: `?api=YOUR_API_KEY`

### Rate Limiting
- **Maximum 5 concurrent calls** (parallel connections)
- If exceeded: HTTP 429 "Maximum concurrent calls reached"
- **Recommendation:** Process emails sequentially or with max 5 parallel

---

## Required Changes

### File to Fix
`src/services/email_validation/debounce_service.py`

### Current Implementation (WRONG)
```python
async def _call_debounce_bulk_api(self, emails: List[str]) -> List[dict]:
    """
    Call DeBounce.io bulk validation API.
    
    ❌ PROBLEM: This endpoint doesn't exist!
    """
    headers = {
        "Authorization": f"api-key {self.api_key}",  # ❌ Wrong auth method
        "Content-Type": "application/json",
    }
    
    payload = {"emails": emails}  # ❌ No bulk payload
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(  # ❌ Wrong method (should be GET)
            f"{self.base_url}/validate/bulk",  # ❌ Endpoint doesn't exist
            headers=headers,
            json=payload,
        )
        
        if response.status_code != 200:
            logger.error(f"DeBounce API failed (HTTP {response.status_code}): {response.text}")
            response.raise_for_status()
        
        data = response.json()
        return data.get("results", [])  # ❌ Wrong response format
```

### Correct Implementation (FIXED)
```python
async def _call_debounce_api(self, emails: List[str]) -> List[dict]:
    """
    Call DeBounce.io real-time lookup API for each email.
    
    DeBounce does NOT have a bulk endpoint. We validate emails sequentially
    to respect the 5 concurrent call limit.
    
    Args:
        emails: List of email addresses to validate
    
    Returns:
        List of validation results in standardized format
    
    Raises:
        httpx.HTTPStatusError: If API call fails
    """
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for email in emails:
            try:
                # DeBounce API uses query parameters for auth and email
                params = {
                    "api": self.api_key,  # ✅ Auth via query param
                    "email": email
                }
                
                # GET request (not POST)
                response = await client.get(
                    self.base_url,  # ✅ Just the base URL (no /validate/bulk)
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(
                        f"DeBounce API failed for {email} (HTTP {response.status_code}): {response.text}"
                    )
                    response.raise_for_status()
                
                data = response.json()
                
                # Check if request was successful
                if data.get("success") == "1":
                    debounce_data = data.get("debounce", {})
                    
                    # Map DeBounce response to our format
                    result = {
                        "email": email,
                        "result": self._map_debounce_result(debounce_data.get("result")),
                        "score": self._calculate_score(debounce_data),
                        "reason": debounce_data.get("reason", ""),
                        "did_you_mean": debounce_data.get("did_you_mean", ""),
                        "code": debounce_data.get("code"),
                        "role": debounce_data.get("role") == "true",
                        "free_email": debounce_data.get("free_email") == "true",
                        "send_transactional": debounce_data.get("send_transactional") == "1"
                    }
                    results.append(result)
                    logger.info(f"✅ Validated {email}: {result['result']}")
                else:
                    # API returned success=0
                    error_msg = data.get("debounce", {}).get("error", "Unknown error")
                    logger.error(f"❌ DeBounce API error for {email}: {error_msg}")
                    results.append({
                        "email": email,
                        "error": error_msg
                    })
                
            except Exception as e:
                logger.error(f"❌ Failed to validate {email}: {e}")
                results.append({
                    "email": email,
                    "error": str(e)
                })
    
    return results

def _map_debounce_result(self, debounce_result: str) -> str:
    """
    Map DeBounce result strings to our standardized format.
    
    DeBounce Results:
    - "Safe to Send" → "valid"
    - "Deliverable" → "valid"
    - "Invalid" → "invalid"
    - "Risky" → "catch-all" or "unknown"
    - "Unknown" → "unknown"
    """
    result_lower = (debounce_result or "").lower()
    
    if "safe" in result_lower or "deliverable" in result_lower:
        return "valid"
    elif "invalid" in result_lower:
        return "invalid"
    elif "risky" in result_lower:
        return "catch-all"
    elif "disposable" in result_lower:
        return "disposable"
    else:
        return "unknown"

def _calculate_score(self, debounce_data: dict) -> int:
    """
    Calculate a 0-100 score from DeBounce data.
    
    DeBounce provides a "code" (0-5) and other indicators.
    We convert this to a 0-100 scale.
    
    Code meanings:
    - 5: Safe to Send (100)
    - 4: Deliverable (90)
    - 3: Risky (50)
    - 2: Unknown (30)
    - 1: Invalid (10)
    - 0: Invalid (0)
    """
    code = int(debounce_data.get("code", 0))
    
    score_map = {
        5: 100,  # Safe to Send
        4: 90,   # Deliverable
        3: 50,   # Risky
        2: 30,   # Unknown
        1: 10,   # Invalid
        0: 0     # Invalid
    }
    
    return score_map.get(code, 0)
```

---

## Response Format Changes

### DeBounce API Response Format
```json
{
   "debounce": {
      "email": "mohsen@gmail.com",
      "code": "5",
      "role": "false",
      "free_email": "true",
      "result": "Safe to Send",
      "reason": "Deliverable",
      "send_transactional": "1",
      "did_you_mean": ""
   },
   "success": "1",
   "balance": "1725935"
}
```

### Our Standardized Format
```python
{
    "email": "mohsen@gmail.com",
    "result": "valid",  # Mapped from "Safe to Send"
    "score": 100,       # Calculated from code=5
    "reason": "Deliverable",
    "did_you_mean": "",
    "code": "5",
    "role": False,
    "free_email": True,
    "send_transactional": True
}
```

---

## Update Method Calls

### In `_validate_contact_batch` method

**Current (line ~123):**
```python
results = await self._call_debounce_bulk_api(emails)
```

**Change to:**
```python
results = await self._call_debounce_api(emails)
```

---

## Configuration Updates

### Update `.env` (Already Correct)
```bash
# DeBounce API Configuration
DEBOUNCE_API_KEY=691d38cd78602
DEBOUNCE_API_BASE_URL=https://api.debounce.io/v1  # ✅ Correct base URL
```

**Note:** The base URL is correct. We just append query parameters, not paths.

---

## Rate Limiting Considerations

### DeBounce Limits
- **5 concurrent calls maximum**
- **429 error** if exceeded

### Our Implementation
**Current:** Sequential processing (safe, but slow)
```python
for email in emails:
    result = await client.get(...)  # One at a time
```

**Future Optimization (Phase 2):**
```python
# Process up to 5 emails in parallel
import asyncio

async def _call_debounce_api_parallel(self, emails: List[str]) -> List[dict]:
    """Process up to 5 emails in parallel."""
    results = []
    
    # Process in batches of 5
    for i in range(0, len(emails), 5):
        batch = emails[i:i+5]
        batch_results = await asyncio.gather(
            *[self._validate_single_email(email) for email in batch],
            return_exceptions=True
        )
        results.extend(batch_results)
    
    return results
```

**Recommendation:** Start with sequential, optimize later if needed.

---

## Testing After Fix

### Test Command
```bash
python test_manual_debounce.py \
  8ef2449f-d3eb-4831-b85e-a385332b6475 \
  f1bae019-a2a4-4caf-aeb6-43c1d8464fd6 \
  bc5de95f-de77-4993-94a5-a2230349809b
```

### Expected Output
```
2025-11-19 XX:XX:XX - INFO - 📧 Preparing to validate 3 contact(s)
2025-11-19 XX:XX:XX - INFO - 🚀 Starting DeBounce validation for 3 contacts
2025-11-19 XX:XX:XX - INFO - 📧 Validating 3 emails via DeBounce API
2025-11-19 XX:XX:XX - INFO - HTTP Request: GET https://api.debounce.io/v1/?api=691d38cd78602&email=test.valid.email@gmail.com "HTTP/1.1 200 OK"
2025-11-19 XX:XX:XX - INFO - ✅ Validated test.valid.email@gmail.com: valid (score: 100)
2025-11-19 XX:XX:XX - INFO - HTTP Request: GET https://api.debounce.io/v1/?api=691d38cd78602&email=test@invaliddomain12345.com "HTTP/1.1 200 OK"
2025-11-19 XX:XX:XX - INFO - ✅ Validated test@invaliddomain12345.com: invalid (score: 0)
2025-11-19 XX:XX:XX - INFO - HTTP Request: GET https://api.debounce.io/v1/?api=691d38cd78602&email=test@mailinator.com "HTTP/1.1 200 OK"
2025-11-19 XX:XX:XX - INFO - ✅ Validated test@mailinator.com: disposable (score: 10)
2025-11-19 XX:XX:XX - INFO - ✅ VALIDATION COMPLETED SUCCESSFULLY!
```

### Database Verification
```sql
SELECT 
    email,
    debounce_validation_status,
    debounce_processing_status,
    debounce_result,
    debounce_score,
    debounce_reason,
    debounce_validated_at
FROM contacts 
WHERE id IN (
    '8ef2449f-d3eb-4831-b85e-a385332b6475',
    'f1bae019-a2a4-4caf-aeb6-43c1d8464fd6',
    'bc5de95f-de77-4993-94a5-a2230349809b'
);
```

**Expected Results:**
| Email | Status | Result | Score | Reason |
|-------|--------|--------|-------|--------|
| test.valid.email@gmail.com | Complete | valid | 90-100 | Deliverable |
| test@invaliddomain12345.com | Complete | invalid | 0-10 | Invalid domain |
| test@mailinator.com | Complete | disposable | 10-30 | Disposable email |

---

## Error Handling

### Handle API Errors
```python
# HTTP 401: Invalid API key
if response.status_code == 401:
    logger.error("❌ Invalid DeBounce API key")
    raise ValueError("Invalid DeBounce API key")

# HTTP 402: No credits
if response.status_code == 402:
    logger.error("❌ DeBounce credits exhausted")
    raise ValueError("DeBounce validation credits finished")

# HTTP 429: Rate limit
if response.status_code == 429:
    logger.warning("⚠️ DeBounce rate limit exceeded - will retry")
    # Let retry logic handle it
```

### Handle Per-Email Errors
```python
# If an email fails, don't fail the entire batch
for result in results:
    if "error" in result:
        contact = email_to_contact[result["email"]]
        contact.debounce_processing_status = "Error"
        contact.debounce_processing_error = result["error"]
    else:
        # Success path...
```

---

## Summary

### What Needs to Change
1. ✅ **Method name:** `_call_debounce_bulk_api` → `_call_debounce_api`
2. ✅ **HTTP method:** POST → GET
3. ✅ **Endpoint:** `/validate/bulk` → base URL with query params
4. ✅ **Authentication:** Header → Query parameter `?api=KEY`
5. ✅ **Request format:** JSON payload → Query parameters
6. ✅ **Processing:** Bulk → Sequential (one email at a time)
7. ✅ **Response mapping:** Add helper methods for result mapping
8. ✅ **Score calculation:** Add helper method for code → score

### Files to Modify
- `src/services/email_validation/debounce_service.py`
  - Line ~190: Rename method
  - Line ~206-227: Rewrite API call logic
  - Add: `_map_debounce_result()` helper
  - Add: `_calculate_score()` helper

### Testing
- Run `python test_manual_debounce.py` with 3 test contacts
- Verify all 3 emails validate successfully
- Check database for correct results
- Verify auto-CRM queue logic (if enabled)

---

**Priority:** 🔴 **CRITICAL**  
**Estimated Time:** 30-45 minutes  
**Blocks:** WO-017 Phase 1 completion  
**Next:** After fix, Local Claude will re-test and proceed to Phase 2 (scheduler)
