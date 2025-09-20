# Work Order: WF7 Page Curation Scraping Logic Inversion

**Priority**: HIGH
**Type**: Refactor / Strategy Implementation
**Component**: `WF7_V2_L4_1of2_PageCurationService`
**Created**: 2025-09-19

## 1. Problem Statement

The current page curation service (`PageCurationService`) attempts to use the expensive ScraperAPI for all initial page fetches. A fallback to direct, non-proxied HTTP requests (`aiohttp`) exists but is implemented incorrectly and fails to trigger, leading to silent failures where pages are marked `Complete` even if content is never fetched.

The strategic business goal is to **minimize ScraperAPI costs**. Therefore, the default scraping method should be the low-cost, direct `aiohttp` approach. The expensive ScraperAPI should only be used as a last-resort fallback when the direct method fails.

This work order outlines the plan to **invert the current scraping logic** to align with this strategy.

## 2. Current State Analysis

*   **Inverted Logic**: The service currently tries the most expensive method (`ScraperAPIClient`) first. This is contrary to the cost-saving objective.
*   **Broken Fallback**: The existing fallback mechanism (which attempts to use `aiohttp` after a ScraperAPI failure) is non-functional and appears to be skipped during execution.
*   **Incorrect Failure Handling**: When all fetch attempts fail, the page's `page_processing_status` is incorrectly set to `Complete`, and `contact_scrape_status` is set to `NoContactFound`. This prevents the system from ever retrying the failed page, leading to permanent data loss for that URL.

## 3. Proposed Implementation Strategy: Invert and Simplify

The core of this refactor is to reverse the fetching logic to **"try cheap first, then expensive."**

### 3.1. Step 1: Prioritize Direct `aiohttp` Scraping

The `process_single_page_for_curation` method will be modified to attempt a direct, "scrappy" `aiohttp` GET request as its primary strategy.

*   A standard `User-Agent` will be used to mimic a real browser.
*   The request will have a reasonable timeout (e.g., 30 seconds).
*   **Success Condition**: An HTTP `200 OK` response with non-empty, meaningful HTML content.
*   **Failure Conditions**:
    *   Specific HTTP error codes indicating blocking or temporary issues (`403 Forbidden`, `429 Too Many Requests`, `5xx` server errors).
    *   Network errors (e.g., `aiohttp.ClientError`).
    *   Timeouts (`asyncio.TimeoutError`).
    *   Receiving empty or minimal content (which we will treat as a soft failure to trigger the fallback).

### 3.2. Step 2: Use ScraperAPI as the Fallback

The call to `ScraperAPIClient` will be moved into the `except` block that catches the failure of the primary `aiohttp` attempt.

*   This ensures ScraperAPI is only engaged when the direct approach fails, minimizing cost.
*   The ScraperAPI call should be configured for the lowest cost (e.g., `render_js=False`, `premium=False`).

### 3.3. Step 3: Implement Correct Final Failure Handling

This is the most critical part of the fix.

*   If the primary `aiohttp` call fails, **AND** the fallback `ScraperAPIClient` call also fails, the `html_content` will be empty.
*   In this scenario, the function will **set the `page_processing_status` to `Failed`**.
*   The function will then terminate processing for that page and return `False`.

This change ensures that failed pages are correctly recorded and can be re-queued for processing by the `run_job_loop` scheduler.

## 4. Acceptance Criteria

1.  ✅ On initial processing of a page, production logs clearly show an "Attempting direct HTTP fetch" message.
2.  ✅ For a URL that is accessible without a proxy, the direct `aiohttp` fetch succeeds, and **no call is made to ScraperAPI**.
3.  ✅ For a URL that blocks direct requests, logs show the direct fetch failing, followed by an "Attempting ScraperAPI fallback" message.
4.  ✅ If both the direct fetch and the ScraperAPI fallback fail, the page's `page_processing_status` in the database is updated to `Failed`.
5.  ✅ If a URL returns a `404 Not Found` on the direct fetch, processing stops, no fallback is attempted, and the page is marked `Complete` with `NoContactFound`.
6.  ✅ The synchronous `_sdk_client.get()` call in `scraper_api.py` is addressed to prevent it from blocking the event loop.

## 5. Implementation Plan

### Phase 1: Restructure `PageCurationService` (2-3 hours)
1.  Modify `process_single_page_for_curation` to move the existing `aiohttp` logic into the main `try` block.
2.  Move the `ScraperAPIClient` call into the `except` block that follows.
3.  Define the specific exceptions to be caught from the `aiohttp` attempt to trigger the fallback.

### Phase 2: Implement Robust Failure Logic (1-2 hours)
1.  Add the final check for `html_content`.
2.  Implement the logic to set `page_processing_status` to `Failed` if `html_content` is empty after all attempts.
3.  Ensure the `PageProcessingStatus` enum supports a `Failed` state.
4.  Refine logging to clearly show the execution path (direct attempt -> fallback attempt -> final status).

### Phase 3: Address Blocking Call (1 hour)
1.  Modify `src/utils/scraper_api.py`.
2.  Wrap the synchronous `self._sdk_client.get()` call in `loop.run_in_executor` to make it non-blocking.

### Phase 4: Testing and Deployment (1 hour)
1.  Test with a known-good URL to verify `aiohttp` success.
2.  Test with a URL known to block requests (e.g., by pointing to a local server that returns 403) to verify the ScraperAPI fallback is triggered.
3.  Test a complete failure scenario to verify the `Failed` status is set correctly.
4.  Deploy and monitor logs.

## 6. Files to be Modified

*   `src/services/WF7_V2_L4_1of2_PageCurationService.py` (Primary changes)
*   `src/utils/scraper_api.py` (To fix the blocking SDK call)
*   `src/models/enums.py` (To ensure `PageProcessingStatus` has a `Failed` member, if it doesn't already)

## 7. Risk Assessment

*   **Low Risk**: The change is logical and contained within a single service. The dependencies (`aiohttp`, `scraperapi-sdk`) are already in use.
*   **Medium Risk**: Direct scraping may lead to a higher rate of IP blocking from target sites. This is an expected trade-off for cost savings. The ScraperAPI fallback is the mitigation for this.
