# PRD: Page Endpoint `page_type` Filter

**Author:** Gemini
**Date:** September 11, 2025
**Status:** Proposed

## 1. Overview & Problem Statement

### 1.1. Overview
This document outlines the requirements for enhancing the primary page-listing endpoint (`GET /api/v3/pages`) to support filtering by the `page_type` field. This field is populated by the Honeybee URL categorization system and contains values like `contact_root`, `legal_root`, and `unknown`.

### 1.2. Problem Statement
The user interface for Workflow 7 (WF7) Curation needs to be able to display specific categories of pages to streamline the manual review process. Currently, the API supports filtering by status but not by the page's semantic category. This makes it difficult for a user to, for example, isolate all uncategorized (`New`) pages that Honeybee has identified as high-value `contact_root` pages. Adding this capability is a critical step in leveraging the intelligence provided by the Honeybee system.

## 2. Goals & Objectives

*   **Primary Goal:** Enable API clients to filter the `GET /api/v3/pages` endpoint by the `page_type` field.
*   **Objective 1:** Improve the efficiency of the WF7 manual curation workflow by allowing users to focus on specific page categories.
*   **Objective 2:** Support compound filtering, allowing queries that combine `page_type` with existing filters like `page_curation_status`.
*   **Objective 3:** Ensure the implementation follows all existing architectural patterns for the ScraperSky backend.

## 3. Scope & Requirements

### 3.1. Endpoint Modification
The scope of this work is limited to a single endpoint:
*   **Endpoint:** `GET /api/v3/pages`
*   **File:** `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py`
*   **Function:** `get_pages`

### 3.2. Functional Requirements
1.  **New Query Parameter:** The `get_pages` function must be updated to accept a new optional query parameter named `page_type` of type `string`.
2.  **Filtering Logic:** When the `page_type` parameter is provided in an API request, the endpoint must add a `WHERE` clause to its database query to filter the results, returning only `Page` records where the `page_type` column exactly matches the provided string.
3.  **Compound Filtering:** The new filter must work in conjunction with existing filters (`page_curation_status`, `page_processing_status`, `url_contains`).
4.  **Response Body:** The JSON response object must be updated to include the `page_type` parameter in the `filters_applied` dictionary, consistent with existing filters.

## 4. Out of Scope

*   This PRD does not cover any UI/frontend changes. It only enables the backend capability.
*   No changes will be made to the Honeybee categorization logic or any other service.
*   No new endpoints will be created.
*   No changes will be made to the database schema; the `page_type` field already exists.

## 5. Success Metrics

The enhancement will be considered successful when the following criteria are met:
1.  A `GET` request to `/api/v3/pages?page_type=contact_root` returns a `200 OK` status and a list containing only pages where `page_type` is 'contact_root'.
2.  A `GET` request to `/api/v3/pages?page_curation_status=New&page_type=contact_root` returns a `200 OK` status and a list containing only pages that satisfy both conditions.
3.  In both of the above cases, the `filters_applied` object in the response correctly reflects the `page_type` that was passed in the query.
4.  A `GET` request to `/api/v3/pages` without the `page_type` parameter continues to function as it currently does.

## 6. Proposed Technical Implementation

The implementation will follow the established patterns in `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py`:

1.  **Modify Function Signature:** Add `page_type: Optional[str] = Query(None, ...)` to the `get_pages` function definition.
2.  **Update Filter Logic:** Append a new condition to the `filters` list: `if page_type: filters.append(Page.page_type == page_type)`.
3.  **Update Response:** Add `'page_type': page_type` to the `filters_applied` dictionary in the function's return statement.
