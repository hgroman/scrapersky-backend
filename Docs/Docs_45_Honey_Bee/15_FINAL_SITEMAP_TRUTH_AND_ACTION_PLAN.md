# Final Sitemap Truth & Action Plan

**Date:** September 9, 2025  
**Purpose:** To serve as the single, definitive source of truth regarding the sitemap processing pipeline issues and to outline the strategic plan to resolve them permanently.

---

## 1. Executive Summary

A series of cascading, difficult-to-diagnose failures in the sitemap processing pipeline has been occurring. After a lengthy and reactive debugging process, the true root cause has been identified: an architectural conflict between **two separate, overlapping sitemap processing systems**. One is a legacy, job-based system, and the other is a modern, SDK-based system.

These two systems have been running concurrently, causing unpredictable behavior, race conditions, and a series of seemingly unrelated bugs (TypeErrors, data mismatches, HTTP errors, and session failures). Patching one system would only reveal a new failure in the other.

This document provides a full analysis of this conflict and presents a clear strategic action plan. The plan is to **disable the legacy system entirely** and perform a single, holistic fix of the modern system.

---

## 2. Proposed Strategic Solution (The Action Plan)

To permanently resolve the instability, we must stop patching symptoms and fix the root architectural conflict.

**Recommendation:** We must standardize on **System B (the "Modern" SDK-based workflow)** and completely disable the legacy workflow.

**Action Plan:**

1.  **Disable the Legacy System:** Modify `src/services/sitemap_scheduler.py` to **stop** processing jobs of type "sitemap". This will immediately halt the entire legacy workflow and all errors originating from it.
2.  **Holistically Fix the Modern System:** Apply the required fixes we have identified exclusively to the files associated with **System B** (`src/common/curation_sdk/scheduler_loop.py` and `src/services/sitemap_import_service.py`). The required fixes are:
    *   Ensure database `COMMIT` occurs immediately after updating a job's status to `Processing`.
    *   Ensure all string-based IDs are properly cast to `UUID` objects before database operations.
    *   Implement robust `try/except/rollback/raise` blocks for all database transactions to prevent cascading session failures.
3.  **Verify:** With the legacy system disabled and the modern system properly fixed, perform a clean, end-to-end test to verify that the pipeline runs stably and correctly.

---

## 3. Holistic Analysis of the Sitemap Processing Pipeline

#### System A: The "Legacy" Job-Based Workflow

This system uses a generic `jobs` table to manage work.

*   **Workflow:** `sitemap_scheduler.py` -> `job_service.py` -> `sitemap/processing_service.py`
*   **The Flaw:** This is the source of the `403 Forbidden` errors (due to a bad User-Agent in `sitemap_analyzer.py`) and the `badly formed hexadecimal UUID string` errors (due to passing an integer `job.id` instead of a UUID `job.job_id`).

#### System B: The "Modern" SDK-Based Workflow

This system uses the standardized `run_job_loop` SDK.

*   **Workflow:** `sitemap_import_scheduler.py` -> `run_job_loop.py` -> `sitemap_import_service.py`
*   **The Flaw:** This system was failing due to a `TypeError` (missing UUID hint) and a race condition (stale data reads), which initially prevented it from running at all.

#### The Root Cause: Systemic Conflict

We were applying fixes reactively across both systems without realizing they were separate. Fixing System B allowed it to start running, which then revealed new failures caused by the still-running System A. This architectural conflict is the true source of the instability.

---

## 4. Appendix: Detailed Debugging & Fixing Timeline

1.  **The Scheduler Crash (TypeError):** Caused by a missing `uuid.UUID` type hint in `sitemap_import_service.py`. Fixed by restoring the hint.
2.  **The Race Condition (Stale Data):** Caused by the processing function reading data before the `Processing` status update was committed. Tentatively fixed with `session.refresh()`.
3.  **HTTP 403 Forbidden Errors:** Caused by a default `aiohttp` User-Agent in `sitemap_analyzer.py`. Fixed by adding a browser User-Agent.
4.  **Invalid UUID Errors:** Caused by the legacy scheduler passing an `int` ID instead of a `UUID`. Fixed by changing `job.id` to `job.job_id`.
5.  **Data Type Mismatch (`priority_value`):** Caused by inserting a `string` into a `REAL` column. Fixed by casting the value to a `float`.
6.  **Recurring Indentation Errors:** Caused by tooling issues when applying automated patches. Fixed manually.

---

## 5. Appendix: Supporting Details

*   **Key Files (Legacy):** `sitemap_scheduler.py`, `sitemap/processing_service.py`, `sitemap_analyzer.py`
*   **Key Files (Modern):** `sitemap_import_scheduler.py`, `sitemap_import_service.py`, `common/curation_sdk/scheduler_loop.py`
*   **Test Record:** `01934199-aec7-7ea8-8b31-39cc9dd4b12c` (https://corningwinebar.com/page-sitemap.xml)
