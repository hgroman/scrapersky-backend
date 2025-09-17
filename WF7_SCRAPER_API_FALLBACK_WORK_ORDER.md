# WF7 ScraperAPI Fallback Implementation Work Order

**Priority**: HIGH
**Type**: Bug Fix / Reliability Enhancement
**Component**: WF7 Page Curation Service
**Estimated Effort**: 4-6 hours
**Created**: 2025-09-16

## Problem Statement

WF7 page processing is failing silently when ScraperAPI credits are exhausted. While HTTP fallback code exists in `PageCurationService.py`, it is not being properly triggered, resulting in pages being marked as "NoContactFound" without attempting direct HTTP scraping.

## Current State Analysis

### What's Working
- ✅ ScraperAPI integration with proper error handling
- ✅ Credit exhaustion detection (HTTP 403 responses)
- ✅ Page status management (marking as Complete/NoContactFound)
- ✅ Async/await pattern implementation

### What's Broken
- ❌ HTTP fallback not triggering despite ScraperAPI failures
- ❌ No "Attempting direct HTTP fallback" log messages appearing
- ❌ Missing actual content extraction when fallback should activate

### Evidence from Production Logs
```
2025-09-14 12:48:55,624 - root - ERROR - Error during ScraperAPI content extraction for https://epiccycles.ca/product/bluerev-warrior/: All SDK 1 attempts failed. Last error: SDK Attempt 1 failed: Failed to scrape GET https://epiccycles.ca/product/bluerev-warrior/?render_js=False
2025-09-14 12:48:55,745 - root - INFO - No emails found, marked page d2aead37-7810-437b-91fd-399660f97a74 as NoContactFound
```

**Key Issue**: No fallback attempt logged between ScraperAPI failure and "No emails found" conclusion.

## Technical Investigation

### Current Fallback Code Location
File: `src/services/WF7_V2_L4_1of2_PageCurationService.py:63-89`

### Code Analysis
The fallback logic exists but appears to have a logical flaw:

```python
except Exception as e:
    logging.error(f"Error during ScraperAPI content extraction for {page_url}: {e}")

    # Fallback to direct HTTP when ScraperAPI fails (e.g., credit exhausted)
    try:
        logging.info(f"Attempting direct HTTP fallback for {page_url}")
        # ... aiohttp implementation
    except Exception as fallback_e:
        logging.error(f"Direct HTTP fallback also failed for {page_url}: {fallback_e}")
        html_content = ""
```

### Root Cause Hypothesis
The fallback code may not be reachable due to:
1. Exception handling scope issues
2. Missing exception type specificity
3. Async context manager conflicts
4. Import dependency issues with aiohttp

## Implementation Requirements

### 1. Debug Fallback Trigger Logic
- [ ] Add detailed logging before fallback attempt
- [ ] Verify exception handling scope in async context
- [ ] Ensure aiohttp import is accessible in exception block

### 2. Improve Exception Handling
- [ ] Make fallback trigger on specific ScraperAPI exceptions
- [ ] Add timeout handling for direct HTTP requests
- [ ] Implement proper User-Agent rotation

### 3. Content Validation
- [ ] Validate HTML content length after fallback
- [ ] Log content extraction success/failure rates
- [ ] Implement content quality scoring

### 4. Production Monitoring
- [ ] Add metrics for fallback usage frequency
- [ ] Track success rates: ScraperAPI vs Direct HTTP
- [ ] Monitor credit exhaustion patterns

## Acceptance Criteria

### Primary Success Metrics
1. ✅ When ScraperAPI returns HTTP 403, fallback triggers within 5 seconds
2. ✅ "Attempting direct HTTP fallback" log message appears in production
3. ✅ Successful HTML content extraction via aiohttp for valid URLs
4. ✅ Page processing continues normally after fallback success

### Secondary Success Metrics
1. ✅ Fallback maintains async performance (no blocking)
2. ✅ Error handling preserves original ScraperAPI error context
3. ✅ Content extraction patterns work with both ScraperAPI and HTTP responses
4. ✅ No regression in existing ScraperAPI functionality

### Monitoring Requirements
1. ✅ Fallback usage counter (how often triggered)
2. ✅ Fallback success rate (content extracted vs empty responses)
3. ✅ Performance comparison (ScraperAPI vs Direct HTTP response times)

## Test Plan

### Unit Tests
- [ ] Mock ScraperAPI HTTP 403 responses
- [ ] Verify fallback code path execution
- [ ] Test aiohttp request formation and response handling
- [ ] Validate HTML content parsing after fallback

### Integration Tests
- [ ] End-to-end page processing with ScraperAPI disabled
- [ ] Fallback behavior under concurrent processing load
- [ ] Content extraction accuracy comparison

### Production Validation
- [ ] Deploy to staging with ScraperAPI credits artificially limited
- [ ] Monitor logs for fallback trigger messages
- [ ] Verify contact extraction from fallback-scraped content

## Risk Assessment

### Low Risk
- Fallback code already exists and follows established patterns
- No changes to database schema or core business logic
- Isolated to single service file

### Medium Risk
- aiohttp dependency behavior in production environment
- Potential performance impact under high concurrent fallback usage
- Rate limiting from target websites

### Mitigation Strategies
- Implement conservative timeout settings for direct HTTP
- Add circuit breaker pattern for repeatedly failing domains
- Include rate limiting mechanisms for fallback requests

## Implementation Plan

### Phase 1: Debug Current State (1-2 hours)
1. Add comprehensive logging to identify why fallback doesn't trigger
2. Test exception handling with simulated ScraperAPI failures
3. Verify aiohttp import and async context compatibility

### Phase 2: Fix Fallback Logic (2-3 hours)
1. Correct exception handling scope and specificity
2. Implement robust aiohttp request patterns
3. Add proper error context preservation

### Phase 3: Production Deployment (1 hour)
1. Deploy with enhanced logging enabled
2. Monitor fallback trigger frequency
3. Validate content extraction success rates

## Files Modified
- `src/services/WF7_V2_L4_1of2_PageCurationService.py` (primary changes)
- `src/utils/scraper_api.py` (potential exception improvements)
- Environment variables for fallback configuration

## Dependencies
- Existing aiohttp library (already in requirements)
- No new external dependencies required
- Leverages existing async session patterns

## Success Validation
**Primary Indicator**: Production logs showing "Attempting direct HTTP fallback" followed by successful content extraction when ScraperAPI credits are exhausted.

**Business Impact**: Maintains WF7 contact extraction capability during ScraperAPI outages, ensuring continuous lead generation pipeline operation.