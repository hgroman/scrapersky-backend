# Peer Review: WF7 Page Curation Refactor

**Author**: Gemini AI  
**Date**: 2025-09-19
**Status**: PROPOSED

## 1. Objective

This document outlines a proposed refactor to the `PageCurationService` to align with the strategic goal of minimizing ScraperAPI costs and to correctly handle all scraping failure scenarios. The current implementation attempts to use the expensive ScraperAPI first and incorrectly marks pages as `Complete` even when all scraping attempts fail.

This proposal details two main changes:
1.  Invert the scraping logic to use a robust, direct `aiohttp` connection as the primary method, only falling back to ScraperAPI when necessary.
2.  Fix a blocking (synchronous) call in the `ScraperAPIClient` to improve application performance and stability.

## 2. Files to be Modified

1.  `src/services/WF7_V2_L4_1of2_PageCurationService.py`
2.  `src/utils/scraper_api.py`

---

## 3. Proposed Changes

### 3.1. `PageCurationService.py` - Logic Inversion and Hardening

**Location**: `src/services/WF7_V2_L4_1of2_PageCurationService.py`

#### Change 1: Replace `process_single_page_for_curation` Method

*   **Lines to be Replaced**: 23-220
*   **Summary**: The entire body of the `process_single_page_for_curation` method will be replaced with a new, more robust implementation that reflects the "try cheap first" strategy.

**New Logic Breakdown:**

1.  **Primary Method (Direct Fetch)**: The code will first attempt to scrape the URL directly using `aiohttp`. This attempt is hardened:
    *   It uses a full set of browser-like `headers` to avoid basic bot detection.
    *   It is wrapped in a `for` loop to retry up to 3 times on transient network errors (like `Connection reset by peer`) or `5xx` status codes.
    *   It uses exponential backoff between retries to avoid overwhelming the target server.

2.  **Fallback Method (ScraperAPI)**: If all 3 direct attempts fail, the `except` block will trigger and make a single attempt using the expensive `ScraperAPIClient` as a last resort.

3.  **Final Failure Handling**: If the ScraperAPI fallback also fails to retrieve content, the `html_content` will be empty. A final check is performed:
    *   If `html_content` is empty, the page's `page_processing_status` is set to `PageProcessingStatus.Error`.
    *   The function then returns `False`, ensuring the job is marked as failed in the `run_job_loop` and can be investigated or retried later.

4.  **Success Handling**: If either the direct fetch or the ScraperAPI fallback succeeds, the function proceeds with the existing contact extraction logic and marks the page as `Complete` on success.

#### Change 2: Clean up Imports

*   **Line to be Removed**: 217 (`from src.models.enums import PageProcessingStatus`)
*   **Summary**: The local import at the end of the function will be removed and a single `from src.models.enums import PageProcessingStatus` line will be added to the main import block at the top of the file (around line 14) for better code style and clarity.

---

### 3.2. `scraper_api.py` - Fix Blocking Call

**Location**: `src/utils/scraper_api.py`

*   **Line to be Modified**: 281
*   **Summary**: The synchronous call `response = self._sdk_client.get(url=api_url)` blocks the entire asyncio event loop, which can cause major performance degradation and timeouts across the whole application.

**Proposed Change:**

This line will be wrapped in `loop.run_in_executor` to run it in a separate thread pool, preventing it from blocking the main event loop.

*   **Before**:
    ```python
    response = self._sdk_client.get(url=api_url)
    ```
*   **After**:
    ```python
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None, self._sdk_client.get, url=api_url
    )
    ```
This requires adding `import asyncio` at the top of the file.

---

## 4. Call for Review

This document outlines the complete plan to refactor the WF7 page curation logic. The goal is to create a more robust, cost-effective, and correct process that properly handles all failure modes.

Constructive criticism and feedback on this proposal are welcome. Please review the proposed logic and implementation details before the changes are applied.
